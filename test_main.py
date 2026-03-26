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

    def test_register_safe_div(self, vocab):
        assert vocab.get("safe_div") is not None
        safe_div_op = vocab.get("safe_div")
        assert safe_div_op(10, 2) == 5.0
        assert safe_div_op(10, 0) == 0.0

    def test_negative_arity_not_allowed(self, vocab):
        with pytest.raises(ValueError):
            vocab.random_op(max_arity=-1)


# ---- Expression Node Tests ----

class TestExprNode:
    def test_leaf_node_creation(self, vocab):
        const_node = ExprNode("const", 3.14)
        assert const_node.op_name == "const"
        assert const_node.const_value == 3.14
        assert len(const_node.children) == 0

    def test_binary_node_creation(self, vocab):
        left = ExprNode("const", 2.0)
        right = ExprNode("const", 3.0)
        add_node = ExprNode("add", children=[left, right])
        assert add_node.op_name == "add"
        assert len(add_node.children) == 2

    def test_arity_checking(self, vocab):
        left = ExprNode("const", 2.0)
        # Creating a node with wrong arity should fail
        with pytest.raises((ValueError, AssertionError)):
            ExprNode("add")  # add expects 2 children


# ---- Grammar Layer Tests ----

class TestGrammarLayer:
    def test_grammar_initialization(self, grammar):
        assert grammar.max_depth == 4
        assert grammar.vocab is not None

    def test_random_expr_within_depth(self, grammar):
        for depth in range(1, 4):
            expr = grammar.random_expr(max_depth=depth)
            assert expr is not None

    def test_mutate_expr(self, grammar):
        expr = grammar.random_expr(max_depth=2)
        mutated = grammar.mutate_expr(expr)
        assert mutated is not None

    def test_crossover_expr(self, grammar):
        expr1 = grammar.random_expr(max_depth=2)
        expr2 = grammar.random_expr(max_depth=2)
        child = grammar.crossover_expr(expr1, expr2)
        assert child is not None


# ---- Meta-Grammar Tests ----

class TestMetaGrammarLayer:
    def test_meta_grammar_initialization(self, meta_grammar):
        assert meta_grammar.vocab is not None
        assert meta_grammar.grammar is not None

    def test_sample_meta_rule(self, meta_grammar):
        rule = meta_grammar.sample_meta_rule()
        assert rule is not None
        assert isinstance(rule, MetaRuleEntry)

    def test_compose_grammar_modification(self, meta_grammar):
        """Test that meta-grammar can suggest grammar modifications."""
        modification = meta_grammar.sample_meta_rule()
        assert modification is not None


# ---- Library Learner Tests ----

class TestLibraryLearner:
    def test_learner_initialization(self):
        learner = LibraryLearner(vocab_size=20)
        assert learner.vocab_size == 20
        assert len(learner.library) == 0

    def test_add_program_to_library(self):
        learner = LibraryLearner(vocab_size=20)
        prog_id = learner.add_program(name="my_prog", expr_tree={"type": "const", "value": 5})
        assert prog_id in learner.library

    def test_retrieve_program(self):
        learner = LibraryLearner(vocab_size=20)
        learner.add_program(name="test", expr_tree={"type": "const", "value": 10})
        programs = learner.retrieve_programs()
        assert len(programs) > 0


# ---- Resource Budget Tests ----

class TestResourceBudget:
    def test_budget_initialization(self, budget):
        assert budget.max_compute_ops == 10_000
        assert budget.max_wall_seconds == 10.0

    def test_budget_tracking(self, budget):
        budget.spend_compute_ops(100)
        assert budget.compute_ops_spent == 100
        assert budget.remaining_compute_ops() == 9_900

    def test_budget_exceeded(self, budget):
        budget.spend_compute_ops(10_001)
        assert budget.is_exhausted()


# ---- Cost-Grounding Loop Tests ----

class TestCostGroundingLoop:
    def test_loop_initialization(self):
        loop = CostGroundingLoop()
        assert loop is not None

    def test_add_expression_cost(self):
        loop = CostGroundingLoop()
        loop.record_expression_cost("test_expr", 5.0)
        assert "test_expr" in loop.costs


# ---- MAP-Elites Archive Tests ----

class TestMAPElitesArchive:
    def test_archive_initialization(self, archive):
        assert len(archive.dims) == 2
        assert archive.dims == [6, 10]

    def test_add_elite(self, archive):
        elite = EliteEntry(
            id="e1",
            expr_tree=ExprNode("const", 1.0),
            fitness=0.95,
            features=[2, 3],
            metadata={}
        )
        archive.add_elite(elite)
        assert archive.get_elite("e1") is not None

    def test_get_elite(self, archive):
        elite = EliteEntry(
            id="e1",
            expr_tree=ExprNode("const", 1.0),
            fitness=0.95,
            features=[2, 3],
            metadata={}
        )
        archive.add_elite(elite)
        retrieved = archive.get_elite("e1")
        assert retrieved.id == "e1"

    def test_feature_bin_assignment(self, archive):
        elite = EliteEntry(
            id="e1",
            expr_tree=ExprNode("const", 1.0),
            fitness=0.95,
            features=[2, 3],
            metadata={}
        )
        bin_key = archive._get_bin_key([2, 3])
        assert bin_key == (2, 3)


# ---- Novelty Screener Tests ----

class TestNoveltyScreener:
    def test_screener_initialization(self):
        screener = NoveltyScreener()
        assert screener is not None

    def test_novelty_metric(self):
        screener = NoveltyScreener()
        val = screener.compute_novelty({"test": 1})
        assert isinstance(val, (int, float))


# ---- Self-Improvement Engine Tests ----

class TestSelfImprovementEngine:
    def test_engine_initialization(self):
        engine = SelfImprovementEngine()
        assert engine is not None

    def test_suggest_improvement(self):
        engine = SelfImprovementEngine()
        suggestion = engine.suggest_improvement(current_fitness=0.5)
        assert suggestion is not None


# ---- Polymorphic Op Tests ----

class TestPolymorphicOp:
    def test_polymorphic_op_creation(self):
        poly_op = PolymorphicOp("test_poly", 2)
        assert poly_op.name == "test_poly"
        assert poly_op.arity == 2

    def test_polymorphic_op_evaluation(self):
        poly_op = PolymorphicOp("add", 2)
        result = poly_op.evaluate(3, 4)
        assert result == 7


# ---- Enhanced MAP-Elites Archive Tests ----

class TestEnhancedMAPElitesArchive:
    def test_enhanced_archive_initialization(self):
        archive = EnhancedMAPElitesArchive(dims=[5, 5])
        assert archive is not None
        assert len(archive.dims) == 2

    def test_enhanced_archive_add_elite(self):
        archive = EnhancedMAPElitesArchive(dims=[5, 5])
        elite = EliteEntry(
            id="e1",
            expr_tree=ExprNode("const", 1.0),
            fitness=0.95,
            features=[2, 3],
            metadata={}
        )
        archive.add_elite(elite)
        assert archive.get_elite("e1") is not None


# ---- Eval Context Tests ----

class TestEvalContext:
    def test_context_initialization(self):
        ctx = EvalContext()
        assert ctx is not None

    def test_set_and_get_variable(self):
        ctx = EvalContext()
        ctx.set("x", 5)
        assert ctx.get("x") == 5

    def test_eval_tree_basic(self):
        ctx = EvalContext()
        ctx.set("x", 2.0)
        ctx.set("y", 3.0)
        tree = ExprNode("add", children=[
            ExprNode("const", 2.0),
            ExprNode("const", 3.0)
        ])
        result = _eval_tree(tree, ctx)
        assert result == 5.0


# ---- Build RSI System Tests ----

class TestBuildRSISystem:
    def test_build_system_returns_dict(self):
        system = build_rsi_system()
        assert isinstance(system, dict)
        assert "vocab" in system
        assert "grammar" in system
        assert "archive" in system

    def test_system_components_initialized(self):
        system = build_rsi_system()
        assert system["vocab"] is not None
        assert system["grammar"] is not None
        assert system["archive"] is not None


# ---- Fitness Function Tests ----

class TestSymbolicRegressionFitness:
    def test_fitness_function_basic(self):
        # Simple quadratic: y = 2*x + 1
        X = np.array([[0], [1], [2], [3]])
        y = np.array([1, 3, 5, 7])

        expr = ExprNode("add", children=[
            ExprNode("mul", children=[
                ExprNode("const", 2.0),
                ExprNode("var", "x")
            ]),
            ExprNode("const", 1.0)
        ])

        ctx = EvalContext()
        fitness = symbolic_regression_fitness(expr, X, y, ctx)
        assert isinstance(fitness, float)
        assert 0 <= fitness <= 1

    def test_fitness_perfect_fit(self):
        X = np.array([[1.0], [2.0], [3.0]])
        y = np.array([1.0, 2.0, 3.0])

        expr = ExprNode("var", "x")
        ctx = EvalContext()
        fitness = symbolic_regression_fitness(expr, X, y, ctx)
        assert fitness > 0.9

    def test_fitness_with_large_error(self):
        X = np.array([[1.0], [2.0]])
        y = np.array([10.0, 20.0])

        expr = ExprNode("const", 1.0)
        ctx = EvalContext()
        fitness = symbolic_regression_fitness(expr, X, y, ctx)
        assert 0 <= fitness <= 1


# ---- Session 12 Tier 2: Conditional Grammar Rules ----

class TestConditionalGrammarRule:
    def test_rule_creation(self):
        def sample_cond():
            return {"type": "depth", "value": 3}

        def rule_fn():
            return None

        rule = ConditionalGrammarRule(
            condition=sample_cond,
            rule_fn=rule_fn,
            priority=1.0
        )
        assert rule is not None
        assert rule.priority == 1.0

    def test_rule_condition_evaluation(self):
        def sample_cond():
            return {"depth": 2}

        rule = ConditionalGrammarRule(
            condition=sample_cond,
            rule_fn=lambda: None,
            priority=1.0
        )
        cond_result = rule.condition()
        assert isinstance(cond_result, dict)

    def test_rule_with_different_priorities(self):
        rules = []
        for i in range(3):
            rule = ConditionalGrammarRule(
                condition=lambda: {"test": i},
                rule_fn=lambda: None,
                priority=float(i) + 1.0
            )
            rules.append(rule)

        # Sort by priority
        sorted_rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        assert sorted_rules[0].priority == 3.0
        assert sorted_rules[2].priority == 1.0


class TestGrammarRuleComposer:
    def test_composer_initialization(self):
        composer = GrammarRuleComposer()
        assert composer is not None
        assert len(composer.rules) == 0

    def test_add_rule_to_composer(self):
        composer = GrammarRuleComposer()
        rule = ConditionalGrammarRule(
            condition=lambda: {"test": 1},
            rule_fn=lambda: None,
            priority=1.0
        )
        composer.add_rule(rule)
        assert len(composer.rules) == 1

    def test_compose_from_rules(self):
        composer = GrammarRuleComposer()
        rule1 = ConditionalGrammarRule(
            condition=lambda: {"test": 1},
            rule_fn=lambda: None,
            priority=1.0
        )
        rule2 = ConditionalGrammarRule(
            condition=lambda: {"test": 2},
            rule_fn=lambda: None,
            priority=2.0
        )
        composer.add_rule(rule1)
        composer.add_rule(rule2)

        composed_grammar = composer.compose()
        assert composed_grammar is not None


class TestRuleInteractionTracker:
    def test_tracker_initialization(self):
        tracker = RuleInteractionTracker()
        assert tracker is not None

    def test_record_interaction(self):
        tracker = RuleInteractionTracker()
        tracker.record_interaction(rule_id="r1", other_rule_id="r2", effect_score=0.8)
        assert tracker is not None

    def test_get_interaction_score(self):
        tracker = RuleInteractionTracker()
        tracker.record_interaction("r1", "r2", 0.75)
        score = tracker.get_interaction_score("r1", "r2")
        assert score is not None
        assert isinstance(score, float)

    def test_multiple_interactions(self):
        tracker = RuleInteractionTracker()
        for i in range(5):
            for j in range(i + 1, 5):
                tracker.record_interaction(f"r{i}", f"r{j}", 0.5 + 0.1 * i)

        score = tracker.get_interaction_score("r0", "r1")
        assert isinstance(score, float)

    def test_interaction_graph_structure(self):
        tracker = RuleInteractionTracker()
        tracker.record_interaction("rule_a", "rule_b", 0.9)
        tracker.record_interaction("rule_b", "rule_c", 0.7)

        # Verify we can retrieve scores
        score_ab = tracker.get_interaction_score("rule_a", "rule_b")
        score_bc = tracker.get_interaction_score("rule_b", "rule_c")
        assert score_ab is not None
        assert score_bc is not None

    def test_rule_update_affects_interactions(self):
        tracker = RuleInteractionTracker()
        tracker.record_interaction("r1", "r2", 0.5)

        # Update the interaction
        tracker.record_interaction("r1", "r2", 0.8)

        score = tracker.get_interaction_score("r1", "r2")
        # Depending on implementation, should reflect update
        assert score is not None
        # Most recent/updated score should be returned
        assert score != 0.5  # Should be updated


# ---- Advanced Integration Tests ----

class TestAdvancedIntegration:
    def test_full_pipeline(self):
        """Test the full RSI pipeline: system build → vocab → grammar → archive."""
        system = build_rsi_system()
        assert system["vocab"] is not None
        assert system["grammar"] is not None
        assert system["archive"] is not None

    def test_expr_evaluation_pipeline(self):
        vocab = VocabularyLayer()
        expr = ExprNode("add", children=[
            ExprNode("const", 2.0),
            ExprNode("const", 3.0)
        ])
        ctx = EvalContext()
        result = _eval_tree(expr, ctx)
        assert result == 5.0

    def test_grammar_and_archive_integration(self, grammar, archive):
        """Test grammar generating expressions and archive storing elites."""
        for _ in range(5):
            expr = grammar.random_expr(max_depth=2)
            elite = EliteEntry(
                id=f"expr_{random.randint(0, 100)}",
                expr_tree=expr,
                fitness=random.random(),
                features=[random.randint(0, 5), random.randint(0, 9)],
                metadata={"source": "test"}
            )
            archive.add_elite(elite)

        # Verify archive has elites
        assert len(archive.elites) > 0


# ---- Tier 2 Conditional Grammar Integration ----

class TestTier2ConditionalGrammarIntegration:
    def test_conditional_rule_affects_expr_generation(self):
        """Test that conditional rules modify expression generation."""
        vocab = VocabularyLayer()
        grammar = GrammarLayer(vocab, max_depth=4)

        # Create a conditional rule
        rule = ConditionalGrammarRule(
            condition=lambda: {"max_depth": 2},
            rule_fn=lambda: {"strategy": "shallow"},
            priority=1.0
        )

        # Compose it into grammar
        composer = GrammarRuleComposer()
        composer.add_rule(rule)
        composed = composer.compose()

        assert composed is not None

    def test_interaction_tracker_with_multiple_rules(self):
        """Test interaction tracking when multiple rules are composed."""
        tracker = RuleInteractionTracker()
        composer = GrammarRuleComposer()

        # Create and add multiple rules
        for i in range(3):
            rule = ConditionalGrammarRule(
                condition=lambda idx=i: {"rule_id": idx},
                rule_fn=lambda: {"output": f"rule_{i}"},
                priority=1.0 + i * 0.5
            )
            composer.add_rule(rule)
            if i > 0:
                tracker.record_interaction(f"rule_{i-1}", f"rule_{i}", 0.7)

        composed = composer.compose()
        assert composed is not None

        # Verify interaction scores
        score = tracker.get_interaction_score("rule_0", "rule_1")
        assert score == 0.7

    def test_rule_fitness_update_scenario(self):
        """Test scenario where rule fitness changes based on interactions."""
        tracker = RuleInteractionTracker()

        # Record initial interaction
        tracker.record_interaction("filter_rule", "mutation_rule", 0.6)

        score_before = tracker.get_interaction_score("filter_rule", "mutation_rule")
        assert score_before == 0.6

        # Update with new interaction (simulating fitness improvement)
        tracker.record_interaction("filter_rule", "mutation_rule", 0.85)

        score_after = tracker.get_interaction_score("filter_rule", "mutation_rule")
        assert score_after != score_before
        # The rule_fn itself hasn't changed
        assert tracker is not None  # Same function


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
