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


# ---- Grammar Layer Tests ----

class TestGrammarLayer:
    def test_random_tree_respects_max_depth(self, grammar):
        for _ in range(10):
            tree = grammar.random_tree()
            assert tree.depth() <= grammar.max_depth

    def test_mutate_tree_preserves_structure(self, grammar):
        original = grammar.random_tree()
        mutated = grammar.mutate_tree(original)
        assert mutated.depth() <= grammar.max_depth
        assert mutated.size() <= 3 * original.size()  # Rough bound

    def test_expr_node_size(self, vocab):
        # Build a simple tree: add(mul(x, y), z)
        add_op = vocab.get("add")
        mul_op = vocab.get("mul")
        one_op = vocab.get("one")
        pi_op = vocab.get("pi")
        
        mul_node = ExprNode(mul_op, [ExprNode(one_op), ExprNode(pi_op)])
        add_node = ExprNode(add_op, [mul_node, ExprNode(one_op)])
        
        assert add_node.size() == 5  # add, mul, one, pi, one
        assert add_node.depth() == 2


# ---- Type System Tests ----

class TestOpType:
    def test_type_compatibility_positive_to_real(self):
        assert OpType.is_compatible(OpType.POSITIVE, OpType.REAL)

    def test_type_compatibility_any_accepts_all(self):
        assert OpType.is_compatible(OpType.POSITIVE, OpType.ANY)
        assert OpType.is_compatible(OpType.BOUNDED, OpType.ANY)

    def test_type_incompatibility(self):
        assert not OpType.is_compatible(OpType.REAL, OpType.POSITIVE)
        assert not OpType.is_compatible(OpType.UNIT, OpType.NON_NEGATIVE)  # False (but could argue)


# ---- Evaluation Tests ----

class TestEvaluation:
    def test_eval_constant_tree(self, vocab):
        tree = ExprNode(vocab.get("one"))
        result = _eval_tree(tree, {})
        assert result == 1.0

    def test_eval_add_tree(self, vocab):
        # Build: add(one, pi)
        add_op = vocab.get("add")
        tree = ExprNode(add_op, [ExprNode(vocab.get("one")), ExprNode(vocab.get("pi"))])
        result = _eval_tree(tree, {})
        assert abs(result - (1.0 + 3.141592653589793)) < 1e-6

    def test_eval_context_budget_tracking(self, vocab, budget):
        tree = ExprNode(vocab.get("one"))
        ctx = EvalContext(budget=budget)
        result = _eval_tree(tree, {}, ctx)
        assert ctx.compute_ops > 0
        assert not ctx.check_budget()  # Should still be within budget

    def test_symbolic_regression_fitness(self, vocab):
        # Simple test: constant 1.0
        tree = ExprNode(vocab.get("one"))
        X = np.zeros((10, 1))  # 10 samples, 1 feature
        y = np.ones(10)  # Target is all 1.0
        # Fitness should be close to 0 (good fit)
        fitness = symbolic_regression_fitness(tree, X, y)
        # MSE = 0, so fitness = -0 = 0
        # (predictions are always 1.0 due to tree being constant)
        # Actually, _eval_tree ignores the inputs, so prediction is 1.0 for each row
        # MSE = mean((1.0 - 1.0)^2) = 0, fitness = -0 = 0
        assert fitness == 0.0


# ---- MAP-Elites Archive Tests ----

class TestMAPElitesArchive:
    def test_archive_add_and_retrieve(self, vocab, archive):
        tree = ExprNode(vocab.get("one"))
        entry = EliteEntry(
            individual=tree,
            fitness=0.5,
            fitnesses=(0.5,),
            behavior_descriptor=(3, 2),
        )
        added = archive.add_or_replace(entry)
        assert added
        assert archive.size() == 1

    def test_archive_replacement(self, vocab, archive):
        tree1 = ExprNode(vocab.get("one"))
        entry1 = EliteEntry(
            individual=tree1,
            fitness=0.5,
            fitnesses=(0.5,),
            behavior_descriptor=(3, 2),
        )
        archive.add_or_replace(entry1)

        tree2 = ExprNode(vocab.get("pi"))
        entry2 = EliteEntry(
            individual=tree2,
            fitness=0.7,
            fitnesses=(0.7,),
            behavior_descriptor=(3, 2),
        )
        replaced = archive.add_or_replace(entry2)
        assert replaced
        assert archive.size() == 1
        assert archive.cells[(3, 2)].fitness == 0.7

    def test_archive_coverage(self, vocab, archive):
        # Archive has dims [6, 10], so 60 cells
        total_cells = 6 * 10
        for i in range(5):
            tree = ExprNode(vocab.get("one"))
            entry = EliteEntry(
                individual=tree,
                fitness=0.5,
                fitnesses=(0.5,),
                behavior_descriptor=(i, i),
            )
            archive.add_or_replace(entry)

        assert archive.coverage() == 5 / total_cells


# ---- Enhanced Archive Tests (Tier 2) ----

class TestEnhancedMAPElitesArchive:
    def test_novelty_metric(self, vocab):
        archive = EnhancedMAPElitesArchive(dims=[5, 5])
        tree = ExprNode(vocab.get("one"))
        entry = EliteEntry(
            individual=tree,
            fitness=0.5,
            fitnesses=(0.5,),
            behavior_descriptor=(2, 2),
        )
        # Empty archive: should have max novelty
        novelty = archive.novelty(entry)
        assert novelty == 1.0

    def test_quality_aggregation(self, vocab):
        archive = EnhancedMAPElitesArchive(dims=[5, 5])
        tree = ExprNode(vocab.get("one"))
        entry = EliteEntry(
            individual=tree,
            fitness=0.5,
            fitnesses=(0.3, 0.5, 0.7),  # 3 objectives
            behavior_descriptor=(2, 2),
        )
        quality = archive.quality(entry)
        assert abs(quality - 0.5) < 1e-6  # Average of [0.3, 0.5, 0.7]


# ---- Library Learner Tests ----

class TestLibraryLearner:
    def test_learn_from_elites(self, vocab, grammar):
        archive = MAPElitesArchive(dims=[5, 5])
        meta_grammar = MetaGrammarLayer(vocab, grammar)
        learner = LibraryLearner(meta_grammar, archive)

        # Add some elites
        for i in range(3):
            tree = grammar.random_tree()
            entry = EliteEntry(
                individual=tree,
                fitness=0.5 + 0.1 * i,
                fitnesses=(0.5 + 0.1 * i,),
                behavior_descriptor=(i, i),
            )
            archive.add_or_replace(entry)

        rules = learner.learn_from_elites()
        assert len(rules) == 3


# ---- Cost Grounding Tests ----

class TestCostGroundingLoop:
    def test_budget_enforcement(self, vocab, budget):
        loop = CostGroundingLoop(budget)
        # Create a tree and evaluate
        tree = ExprNode(vocab.get("one"))
        result = loop.evaluate_tree(tree, {})
        assert result == 1.0
        assert loop.evaluations_completed == 1

    def test_remaining_budget_calculation(self, vocab, budget):
        loop = CostGroundingLoop(budget)
        tree = ExprNode(vocab.get("one"))
        loop.evaluate_tree(tree, {})
        remaining = loop.remaining_budget()
        assert remaining["compute_ops"] > 0
        assert remaining["compute_ops"] < budget.max_compute_ops


# ---- Self-Improvement Engine Tests ----

class TestSelfImprovementEngine:
    def test_engine_initialization(self, vocab, grammar, archive, budget):
        engine = SelfImprovementEngine(vocab, grammar, archive, budget)
        assert engine.iteration == 0
        assert engine.archive is archive

    def test_single_step(self, vocab, grammar, archive, budget):
        engine = SelfImprovementEngine(vocab, grammar, archive, budget)
        metrics = engine.step(num_candidates=10)
        assert metrics["iteration"] == 1
        assert "candidates_added" in metrics
        assert "archive_size" in metrics

    def test_best_solution(self, vocab, grammar, archive, budget):
        engine = SelfImprovementEngine(vocab, grammar, archive, budget)
        best_before = engine.get_best_solution()
        assert best_before is None  # Empty archive

        engine.step(num_candidates=10)
        best_after = engine.get_best_solution()
        assert best_after is not None


# ---- System Builder Tests ----

class TestSystemBuilder:
    def test_build_default_system(self):
        engine = build_rsi_system()
        assert engine is not None
        assert engine.vocab.size > 10
        assert engine.archive.size() == 0  # Not yet run

    def test_build_custom_system(self):
        engine = build_rsi_system(
            max_vocab_size=15,
            max_tree_depth=3,
            archive_dims=[5, 5],
            budget_compute_ops=50_000,
        )
        assert engine is not None
        assert engine.grammar.max_depth == 3


# ---- Polymorphic Operations Tests (Tier 2) ----

class TestPolymorphicOp:
    def test_polymorphic_op_wrapping(self, vocab):
        tree = ExprNode(vocab.get("one"))
        poly_op = PolymorphicOp("learned_0", tree)
        assert poly_op.name == "learned_0"
        assert poly_op() == 1.0  # Calling the polymorphic op


# ---- Conditional Grammar Rules Tests (Tier 2) ----

class TestConditionalGrammarRule:
    def test_rule_creation_and_guard(self, vocab):
        tree = ExprNode(vocab.get("one"))
        guard_fn = lambda ctx: ctx.get("use_rule", False)
        rule = ConditionalGrammarRule("test_rule", guard_fn, tree)
        
        assert rule.guard({"use_rule": True})
        assert not rule.guard({"use_rule": False})


# ---- Grammar Rule Composer Tests (Tier 2) ----

class TestGrammarRuleComposer:
    def test_rule_composition_graph(self, vocab):
        tree = ExprNode(vocab.get("one"))
        rule1 = ConditionalGrammarRule("rule_1", lambda ctx: True, tree)
        rule2 = ConditionalGrammarRule("rule_2", lambda ctx: True, tree)
        
        composer = GrammarRuleComposer()
        composer.add_rule(rule1)
        composer.add_rule(rule2)
        
        compat = composer.compatible_rules("rule_1")
        assert "rule_2" in compat


# ---- Rule Interaction Tracker Tests (Tier 2) ----

class TestRuleInteractionTracker:
    def test_record_and_query_interactions(self):
        tracker = RuleInteractionTracker()
        tracker.record_interaction("rule_a", "rule_b")
        tracker.record_interaction("rule_a", "rule_b")
        tracker.record_interaction("rule_c", "rule_d")
        
        top = tracker.most_interacting_rules(top_k=1)
        assert len(top) == 1
        # Either (rule_a, rule_b) or (rule_b, rule_a) - order may vary
        assert set(top[0]) == {"rule_a", "rule_b"}


# ---- Novelty Screener Tests (Tier 2) ----

class TestNoveltyScreener:
    def test_novelty_screening(self, vocab, archive):
        screener = NoveltyScreener(archive)
        bd1 = (0, 0)
        bd2 = (5, 5)
        
        assert screener.is_novel(bd1)  # No history
        screener.record(bd1)
        assert screener.is_novel(bd2, threshold=0.1)  # Far enough
        assert not screener.is_novel(bd1, threshold=0.1)  # Same as recorded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
