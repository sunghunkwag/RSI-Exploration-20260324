"""Tests for the RSI-Exploration architecture."""

import random
import pytest
import numpy as np

from main import (
    PrimitiveOp,
    OpType,
    VocabularyLayer,
    ExprNode,
    GrammarLayer,
    MetaGrammarLayer,
    MetaRuleEntry,
    LibraryLearner,
    ResourceBudget,
    CostGroundingLoop,
    MAPElitesArchive,
    EnhancedMAPElitesArchive,
    NoveltyScreener,
    EliteEntry,
    SelfImprovementEngine,
    build_rsi_system,
    symbolic_regression_fitness,
    _eval_tree,
    EvalContext,
    PolymorphicOp,
    # Session 12 — Tier 2 imports
    ConditionalGrammarRule,
    GrammarRuleComposer,
    RuleInteractionTracker,
)


# ---- Fixtures ----

@pytest.fixture
def vocab():
    return VocabularyLayer()


@pytest.fixture
def grammar(vocab):
    return GrammarLayer(vocab, max_depth=4)


@pytest.fixture
def meta_grammar(vocab, grammar):
    return MetaGrammarLayer(vocab, grammar)


@pytest.fixture
def archive():
    return MAPElitesArchive(dims=[6, 10])


@pytest.fixture
def budget():
    return ResourceBudget(max_compute_ops=10_000, max_wall_seconds=10.0)


# ---- Vocabulary Layer Tests ----

class TestVocabularyLayer:
    def test_default_ops_registered(self, vocab):
        assert vocab.size >= 10
        assert vocab.get("add") is not None
        assert vocab.get("mul") is not None

    def test_register_new_op(self, vocab):
        initial_size = vocab.size
        new_op = PrimitiveOp("cube", 1, lambda a: a ** 3, 2.0, "Cube")
        vocab.register(new_op)
        assert vocab.size == initial_size + 1
        assert vocab.get("cube") is not None

    def test_random_op_respects_arity(self, vocab):
        for _ in range(20):
            op = vocab.random_op(max_arity=0)
            assert op.arity == 0

    def test_primitive_op_callable(self, vocab):
        add_op = vocab.get("add")
        assert add_op(3, 4) == 7

    def test_safe_div_by_zero(self, vocab):
        div_op = vocab.get("safe_div")
        assert div_op(5, 0) == 0.0


# ---- ExprNode Tests ----

class TestExprNode:
    def test_leaf_node_creation(self, vocab):
        leaf = ExprNode(vocab.get("x"), [])
        assert leaf.op.name == "x"
        assert leaf.arity == 0
        assert len(leaf.children) == 0

    def test_internal_node_creation(self, vocab):
        leaf1 = ExprNode(vocab.get("x"), [])
        leaf2 = ExprNode(vocab.get("y"), [])
        internal = ExprNode(vocab.get("add"), [leaf1, leaf2])
        assert internal.op.name == "add"
        assert internal.arity == 2
        assert len(internal.children) == 2

    def test_depth_property(self, vocab):
        x = ExprNode(vocab.get("x"), [])
        y = ExprNode(vocab.get("y"), [])
        add = ExprNode(vocab.get("add"), [x, y])
        mul = ExprNode(vocab.get("mul"), [add, x])
        assert x.depth == 0
        assert add.depth == 1
        assert mul.depth == 2

    def test_size_property(self, vocab):
        x = ExprNode(vocab.get("x"), [])
        y = ExprNode(vocab.get("y"), [])
        add = ExprNode(vocab.get("add"), [x, y])
        assert x.size == 1
        assert add.size == 3

    def test_subtree_generation(self, vocab):
        for _ in range(10):
            node = ExprNode.random(vocab, max_depth=3)
            assert node is not None
            assert node.depth <= 3


# ---- Grammar Layer Tests ----

class TestGrammarLayer:
    def test_basic_derivation(self, grammar):
        rule = grammar.rules["E"]
        assert rule is not None
        assert len(rule) > 0

    def test_derivation_generates_expr(self, grammar):
        for _ in range(10):
            node = grammar.derive()
            assert isinstance(node, ExprNode)
            assert node.depth <= grammar.max_depth

    def test_depth_limit_enforced(self, grammar):
        for _ in range(20):
            node = grammar.derive()
            assert node.depth <= grammar.max_depth


# ---- Meta-Grammar Tests ----

class TestMetaGrammarLayer:
    def test_meta_rule_entry_creation(self, vocab, grammar):
        meta_rule = MetaRuleEntry(
            rule_name="E",
            production_rule=grammar.rules["E"][0],
            fitness=0.5,
            usage_count=10
        )
        assert meta_rule.rule_name == "E"
        assert meta_rule.fitness == 0.5
        assert meta_rule.usage_count == 10

    def test_meta_grammar_maintains_rules(self, meta_grammar):
        assert len(meta_grammar.meta_rules) > 0

    def test_meta_grammar_selection(self, meta_grammar):
        # The meta grammar should be able to select high-fitness rules
        rule = meta_grammar.select_rule()
        assert rule is not None


# ---- Library Learner Tests ----

class TestLibraryLearner:
    def test_library_initialization(self, vocab):
        learner = LibraryLearner(vocab, max_library_size=100)
        assert learner.max_library_size == 100
        assert len(learner.library) == 0

    def test_library_addition(self, vocab):
        learner = LibraryLearner(vocab, max_library_size=100)
        x = ExprNode(vocab.get("x"), [])
        y = ExprNode(vocab.get("y"), [])
        node = ExprNode(vocab.get("add"), [x, y])
        learner.add_to_library(node, fitness=1.0)
        assert len(learner.library) == 1

    def test_library_size_limit(self, vocab):
        learner = LibraryLearner(vocab, max_library_size=5)
        for i in range(10):
            node = ExprNode(vocab.get("const"), [])
            learner.add_to_library(node, fitness=i * 0.1)
        assert len(learner.library) <= learner.max_library_size


# ---- Resource Budget Tests ----

class TestResourceBudget:
    def test_budget_initialization(self, budget):
        assert budget.max_compute_ops == 10_000
        assert budget.max_wall_seconds == 10.0
        assert budget.remaining_ops == 10_000

    def test_budget_decrement(self, budget):
        initial = budget.remaining_ops
        budget.spend(100)
        assert budget.remaining_ops == initial - 100

    def test_budget_exhaustion(self, budget):
        budget.spend(5_000)
        assert budget.remaining_ops == 5_000
        assert not budget.is_exhausted()
        budget.spend(5_000)
        assert budget.is_exhausted()


# ---- Cost Grounding Loop Tests ----

class TestCostGroundingLoop:
    def test_cgl_initialization(self, vocab, grammar, budget):
        cgl = CostGroundingLoop(vocab, grammar, budget)
        assert cgl.vocab is vocab
        assert cgl.grammar is grammar
        assert cgl.budget is budget

    def test_cgl_cost_estimation(self, vocab, grammar, budget):
        cgl = CostGroundingLoop(vocab, grammar, budget)
        node = ExprNode(vocab.get("x"), [])
        cost = cgl.estimate_cost(node)
        assert cost >= 0


# ---- MAP-Elites Archive Tests ----

class TestMAPElitesArchive:
    def test_archive_initialization(self, archive):
        assert archive.dims == [6, 10]
        assert len(archive.cells) == 0

    def test_archive_add_elite(self, archive, vocab):
        x = ExprNode(vocab.get("x"), [])
        elite = EliteEntry(
            expr=x,
            fitness=0.9,
            bc=[3, 5]
        )
        archive.add_elite(elite)
        assert archive.cells.get((3, 5)) is not None
        assert archive.cells[(3, 5)].fitness == 0.9

    def test_archive_replacement(self, archive, vocab):
        x = ExprNode(vocab.get("x"), [])
        elite1 = EliteEntry(expr=x, fitness=0.5, bc=[2, 3])
        elite2 = EliteEntry(expr=x, fitness=0.8, bc=[2, 3])
        archive.add_elite(elite1)
        archive.add_elite(elite2)
        assert archive.cells[(2, 3)].fitness == 0.8

    def test_archive_random_elite(self, archive, vocab):
        for i in range(5):
            x = ExprNode(vocab.get("x"), [])
            elite = EliteEntry(expr=x, fitness=0.1 * i, bc=[i % 6, i % 10])
            archive.add_elite(elite)
        sampled = archive.random_elite()
        assert sampled is not None


# ---- Enhanced MAP-Elites Archive Tests ----

class TestEnhancedMAPElitesArchive:
    def test_enhanced_archive_initialization(self):
        archive = EnhancedMAPElitesArchive(dims=[4, 4])
        assert archive.dims == [4, 4]
        assert len(archive.cells) == 0

    def test_enhanced_archive_tracks_history(self, vocab):
        archive = EnhancedMAPElitesArchive(dims=[4, 4])
        x = ExprNode(vocab.get("x"), [])
        elite = EliteEntry(expr=x, fitness=0.7, bc=[1, 1])
        archive.add_elite(elite)
        history = archive.get_history()
        assert len(history) > 0


# ---- Novelty Screener Tests ----

class TestNoveltyScreener:
    def test_novelty_screener_initialization(self):
        screener = NoveltyScreener(k=5, threshold=0.3)
        assert screener.k == 5
        assert screener.threshold == 0.3

    def test_novelty_calculation(self, vocab):
        screener = NoveltyScreener(k=3, threshold=0.3)
        x = ExprNode(vocab.get("x"), [])
        y = ExprNode(vocab.get("y"), [])
        add = ExprNode(vocab.get("add"), [x, y])
        # Add some archive entries
        screener.archive_population.append(x)
        screener.archive_population.append(y)
        novelty = screener.calculate_novelty(add)
        assert novelty >= 0


# ---- Symbolic Regression Fitness Tests ----

class TestSymbolicRegressionFitness:
    def test_fitness_evaluation(self):
        # Create simple target: y = 2*x
        x_vals = np.array([0.0, 1.0, 2.0, 3.0])
        y_target = 2.0 * x_vals
        
        # Create evaluation context
        ctx = EvalContext(vars={"x": 0.0})
        
        # Create simple expression: x + x
        vocab = VocabularyLayer()
        x = ExprNode(vocab.get("x"), [])
        expr = ExprNode(vocab.get("add"), [x, x])
        
        # Evaluate fitness
        fitness = symbolic_regression_fitness(
            expr=expr,
            x_vals=x_vals,
            y_target=y_target,
            ctx=ctx
        )
        assert 0 <= fitness <= 1

    def test_fitness_perfect_match(self):
        # Create target: y = x
        x_vals = np.array([0.0, 1.0, 2.0, 3.0])
        y_target = x_vals
        
        ctx = EvalContext(vars={"x": 0.0})
        vocab = VocabularyLayer()
        x = ExprNode(vocab.get("x"), [])
        
        # Evaluate fitness
        fitness = symbolic_regression_fitness(
            expr=x,
            x_vals=x_vals,
            y_target=y_target,
            ctx=ctx
        )
        assert fitness == 1.0


# ---- Expression Evaluation Tests ----

class TestEvalTree:
    def test_eval_leaf_variable(self):
        vocab = VocabularyLayer()
        x = ExprNode(vocab.get("x"), [])
        ctx = EvalContext(vars={"x": 5.0})
        result = _eval_tree(x, ctx)
        assert result == 5.0

    def test_eval_leaf_constant(self):
        vocab = VocabularyLayer()
        const = ExprNode(vocab.get("const"), [])
        ctx = EvalContext(vars={})
        result = _eval_tree(const, ctx)
        assert isinstance(result, (int, float))

    def test_eval_binary_op(self):
        vocab = VocabularyLayer()
        x = ExprNode(vocab.get("x"), [])
        y = ExprNode(vocab.get("y"), [])
        add = ExprNode(vocab.get("add"), [x, y])
        ctx = EvalContext(vars={"x": 3.0, "y": 4.0})
        result = _eval_tree(add, ctx)
        assert result == 7.0

    def test_eval_complex_tree(self):
        vocab = VocabularyLayer()
        x = ExprNode(vocab.get("x"), [])
        y = ExprNode(vocab.get("y"), [])
        add_xy = ExprNode(vocab.get("add"), [x, y])
        mul = ExprNode(vocab.get("mul"), [add_xy, x])
        ctx = EvalContext(vars={"x": 2.0, "y": 3.0})
        # (2.0 + 3.0) * 2.0 = 10.0
        result = _eval_tree(mul, ctx)
        assert result == 10.0


# ---- Integration Tests ----

class TestRSISystemIntegration:
    def test_build_rsi_system(self):
        system = build_rsi_system()
        assert system is not None
        assert hasattr(system, 'vocab')
        assert hasattr(system, 'grammar')
        assert hasattr(system, 'meta_grammar')
        assert hasattr(system, 'archive')
        assert hasattr(system, 'budget')

    def test_rsi_system_derivation(self):
        system = build_rsi_system()
        for _ in range(5):
            expr = system['grammar'].derive()
            assert isinstance(expr, ExprNode)
            assert expr.depth <= system['grammar'].max_depth

    def test_rsi_system_fitness_evaluation(self):
        system = build_rsi_system()
        x_vals = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        y_target = 2.0 * x_vals + 1.0
        
        expr = system['grammar'].derive()
        ctx = EvalContext(vars={"x": 0.0})
        
        fitness = symbolic_regression_fitness(
            expr=expr,
            x_vals=x_vals,
            y_target=y_target,
            ctx=ctx
        )
        assert 0 <= fitness <= 1


# ---- Polymorphic Op Tests ----

class TestPolymorphicOp:
    def test_polymorphic_op_creation(self):
        def impl1(a, b):
            return a + b
        def impl2(a, b):
            return a - b
        
        poly_op = PolymorphicOp("flex_op", 2, [impl1, impl2], 1.0, "Flexible operator")
        assert poly_op.name == "flex_op"
        assert poly_op.arity == 2
        assert len(poly_op.implementations) == 2

    def test_polymorphic_op_call(self):
        def impl1(a, b):
            return a + b
        def impl2(a, b):
            return a - b
        
        poly_op = PolymorphicOp("flex_op", 2, [impl1, impl2], 1.0, "Flexible operator")
        # Should call first implementation by default
        result = poly_op(3, 2)
        assert result in [5, 1]  # Could be either implementation


# ---- Session 12 — Tier 2 Tests ----

class TestConditionalGrammarRule:
    def test_conditional_rule_creation(self, vocab):
        rule = ConditionalGrammarRule(
            name="TestRule",
            condition=lambda context: context.get("depth", 0) < 2,
            production_rule=lambda vocab: ExprNode(vocab.get("x"), [])
        )
        assert rule.name == "TestRule"
        assert callable(rule.condition)
        assert callable(rule.production_rule)

    def test_conditional_rule_satisfaction(self, vocab):
        rule = ConditionalGrammarRule(
            name="TestRule",
            condition=lambda context: context.get("depth", 0) < 2,
            production_rule=lambda vocab: ExprNode(vocab.get("x"), [])
        )
        # Should be satisfied with shallow depth
        assert rule.is_satisfied({"depth": 0})
        assert rule.is_satisfied({"depth": 1})
        assert not rule.is_satisfied({"depth": 2})

    def test_conditional_rule_generation(self, vocab):
        rule = ConditionalGrammarRule(
            name="TestRule",
            condition=lambda context: context.get("depth", 0) < 3,
            production_rule=lambda vocab: ExprNode(vocab.get("x"), [])
        )
        expr = rule.generate(vocab, {"depth": 1})
        assert isinstance(expr, ExprNode)


class TestGrammarRuleComposer:
    def test_rule_composition(self, vocab):
        rule1 = ConditionalGrammarRule(
            name="Rule1",
            condition=lambda ctx: True,
            production_rule=lambda v: ExprNode(v.get("x"), [])
        )
        rule2 = ConditionalGrammarRule(
            name="Rule2",
            condition=lambda ctx: True,
            production_rule=lambda v: ExprNode(v.get("y"), [])
        )
        
        composer = GrammarRuleComposer([rule1, rule2])
        assert len(composer.rules) == 2

    def test_rule_composition_selection(self, vocab):
        rule1 = ConditionalGrammarRule(
            name="Rule1",
            condition=lambda ctx: ctx.get("depth", 0) == 0,
            production_rule=lambda v: ExprNode(v.get("x"), [])
        )
        rule2 = ConditionalGrammarRule(
            name="Rule2",
            condition=lambda ctx: ctx.get("depth", 0) == 1,
            production_rule=lambda v: ExprNode(v.get("y"), [])
        )
        
        composer = GrammarRuleComposer([rule1, rule2])
        available = composer.get_applicable_rules({"depth": 0})
        assert len(available) > 0


class TestRuleInteractionTracker:
    def test_tracker_initialization(self):
        tracker = RuleInteractionTracker()
        assert len(tracker.interaction_graph) == 0

    def test_track_rule_interaction(self):
        tracker = RuleInteractionTracker()
        tracker.record_interaction("RuleA", "RuleB", interaction_type="composition")
        assert ("RuleA", "RuleB") in tracker.interaction_graph

    def test_query_interactions(self):
        tracker = RuleInteractionTracker()
        tracker.record_interaction("RuleA", "RuleB", interaction_type="composition")
        tracker.record_interaction("RuleB", "RuleC", interaction_type="conflict")
        
        interactions = tracker.get_interactions_for("RuleA")
        assert len(interactions) > 0


# ---- Self-Improvement Engine Tests ----

class TestSelfImprovementEngine:
    def test_engine_initialization(self, vocab, grammar, archive, budget):
        engine = SelfImprovementEngine(
            vocab=vocab,
            grammar=grammar,
            archive=archive,
            budget=budget
        )
        assert engine.vocab is vocab
        assert engine.grammar is grammar
        assert engine.archive is archive

    def test_engine_step(self, vocab, grammar, archive, budget):
        engine = SelfImprovementEngine(
            vocab=vocab,
            grammar=grammar,
            archive=archive,
            budget=budget
        )
        x_vals = np.array([0.0, 1.0, 2.0])
        y_target = np.array([0.0, 1.0, 4.0])
        
        initial_size = len(engine.archive.cells)
        engine.step(x_vals, y_target)
        # Archive may or may not grow, but should not raise an error


# ---- Edge Cases and Stress Tests ----

class TestEdgeCases:
    def test_empty_vocabulary_behavior(self):
        # This should still work with defaults
        vocab = VocabularyLayer()
        assert vocab.size > 0

    def test_very_deep_tree(self, vocab):
        # Create a very deep tree
        node = ExprNode(vocab.get("x"), [])
        for _ in range(100):
            node = ExprNode(vocab.get("neg"), [node])
        # Should not crash
        assert node.depth == 100

    def test_large_constant_pool(self, vocab):
        # Should handle many constants
        for _ in range(1000):
            ExprNode(vocab.get("const"), [])
        # Should not crash

    def test_eval_with_nan(self):
        vocab = VocabularyLayer()
        div_op = vocab.get("safe_div")
        result = div_op(0.0, 0.0)
        assert result == 0.0

    def test_eval_with_large_numbers(self):
        vocab = VocabularyLayer()
        add_op = vocab.get("add")
        result = add_op(1e100, 1e100)
        assert result == 2e100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])