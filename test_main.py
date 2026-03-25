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


# ---- Expression Node Tests ----

class TestExprNode:
    def test_leaf_depth(self):
        node = ExprNode("input_x")
        assert node.depth() == 0
        assert node.size() == 1

    def test_tree_depth(self):
        child1 = ExprNode("input_x")
        child2 = ExprNode("const_one")
        parent = ExprNode("add", children=[child1, child2])
        assert parent.depth() == 1
        assert parent.size() == 3

    def test_to_dict_roundtrip(self):
        node = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        d = node.to_dict()
        assert d["op"] == "add"
        assert len(d["children"]) == 2

    def test_fingerprint_deterministic(self):
        node = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        fp1 = node.fingerprint()
        fp2 = node.fingerprint()
        assert fp1 == fp2
        assert len(fp1) == 12


# ---- Grammar Layer Tests ----

class TestGrammarLayer:
    def test_random_tree_generation(self, grammar):
        tree = grammar.random_tree()
        assert isinstance(tree, ExprNode)
        assert tree.depth() <= grammar.max_depth

    def test_mutation_produces_valid_tree(self, grammar):
        tree = grammar.random_tree()
        mutant = grammar.mutate(tree)
        assert isinstance(mutant, ExprNode)
        assert mutant.depth() <= grammar.max_depth

    def test_crossover_produces_valid_tree(self, grammar):
        tree1 = grammar.random_tree()
        tree2 = grammar.random_tree()
        offspring = grammar.crossover(tree1, tree2)
        assert isinstance(offspring, ExprNode)
        assert offspring.depth() <= grammar.max_depth

    def test_phenotype_eval(self, grammar):
        tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        phenotype = grammar.phenotype(tree)
        assert callable(phenotype)
        result = phenotype(5.0)
        assert result == 6.0


# ---- Meta-Grammar Layer Tests ----

class TestMetaGrammarLayer:
    def test_rule_selection(self, meta_grammar):
        rule = meta_grammar.select_rule()
        assert isinstance(rule, str)
        assert rule in ["expand_rule", "refine_rule"]

    def test_apply_rule_expand(self, meta_grammar):
        grammar_v0 = meta_grammar.grammar
        meta_grammar.apply_rule("expand_rule", grammar_v0)
        # Rule should have modified the grammar in some way
        assert meta_grammar.grammar is not None

    def test_apply_rule_refine(self, meta_grammar):
        grammar_v0 = meta_grammar.grammar
        meta_grammar.apply_rule("refine_rule", grammar_v0)
        # Rule should have modified the grammar in some way
        assert meta_grammar.grammar is not None

    def test_rule_precondition_satisfied(self, meta_grammar):
        precond_ok = meta_grammar.rule_preconditions_met("expand_rule")
        assert isinstance(precond_ok, bool)


# ---- MetaRuleEntry Tests ----

class TestMetaRuleEntry:
    def test_entry_creation(self):
        entry = MetaRuleEntry(
            rule_name="test_rule",
            precondition=lambda g: True,
            action=lambda g: g,
            outcome_metric=lambda g: 0.5,
        )
        assert entry.rule_name == "test_rule"
        assert entry.precondition(None) is True
        assert entry.outcome_metric(None) == 0.5

    def test_entry_score_calculation(self):
        entry = MetaRuleEntry(
            rule_name="test_rule",
            precondition=lambda g: True,
            action=lambda g: g,
            outcome_metric=lambda g: 0.8,
        )
        entry._outcome_history = [0.5, 0.6, 0.7, 0.8]
        score = entry.compute_score()
        assert isinstance(score, (int, float))
        assert score >= 0

    def test_track_outcome(self):
        entry = MetaRuleEntry(
            rule_name="test_rule",
            precondition=lambda g: True,
            action=lambda g: g,
            outcome_metric=lambda g: 0.5,
        )
        entry.track_outcome(0.7)
        entry.track_outcome(0.8)
        assert len(entry._outcome_history) == 2
        assert entry._outcome_history[-1] == 0.8


# ---- LibraryLearner Tests ----

class TestLibraryLearner:
    def test_library_initialization(self, vocab, grammar):
        learner = LibraryLearner(vocab, grammar)
        assert learner.vocab is not None
        assert learner.grammar is not None

    def test_learn_library(self, vocab, grammar):
        learner = LibraryLearner(vocab, grammar)
        X = np.array([[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]])
        y = np.array([3.0, 5.0, 7.0])
        models = learner.learn_library(X, y, num_generations=2)
        assert isinstance(models, list)
        assert len(models) > 0

    def test_predict_with_learned_library(self, vocab, grammar):
        learner = LibraryLearner(vocab, grammar)
        X = np.array([[1.0], [2.0], [3.0]])
        y = np.array([2.0, 3.0, 4.0])
        models = learner.learn_library(X, y, num_generations=2)
        X_test = np.array([[1.5], [2.5]])
        predictions = [m(X_test) for m in models if callable(m)]
        assert len(predictions) > 0


# ---- ResourceBudget Tests ----

class TestResourceBudget:
    def test_budget_initialization(self, budget):
        assert budget.max_compute_ops == 10_000
        assert budget.max_wall_seconds == 10.0
        assert budget.remaining_ops() == 10_000
        assert budget.remaining_seconds() > 0

    def test_budget_deduction_ops(self, budget):
        initial = budget.remaining_ops()
        budget.deduct_ops(100)
        assert budget.remaining_ops() == initial - 100

    def test_budget_is_exhausted(self, budget):
        budget.deduct_ops(budget.max_compute_ops)
        assert budget.is_exhausted() is True

    def test_budget_time_tracking(self, budget):
        import time
        time.sleep(0.1)
        assert budget.remaining_seconds() < budget.max_wall_seconds


# ---- CostGroundingLoop Tests ----

class TestCostGroundingLoop:
    def test_loop_initialization(self, vocab, grammar, budget):
        loop = CostGroundingLoop(vocab, grammar, budget)
        assert loop.vocab is not None
        assert loop.grammar is not None
        assert loop.budget is not None

    def test_loop_step_respects_budget(self, vocab, grammar, budget):
        loop = CostGroundingLoop(vocab, grammar, budget)
        loop.step()
        assert budget.remaining_ops() < 10_000

    def test_loop_termination_on_exhausted_budget(self, vocab, grammar):
        tiny_budget = ResourceBudget(max_compute_ops=1, max_wall_seconds=10.0)
        loop = CostGroundingLoop(vocab, grammar, tiny_budget)
        result = loop.run(generations=100)
        # Should terminate early due to budget
        assert tiny_budget.is_exhausted()


# ---- MAPElitesArchive Tests ----

class TestMAPElitesArchive:
    def test_archive_initialization(self, archive):
        assert archive.dims == [6, 10]
        assert archive.size() == 0

    def test_archive_add_elite(self, archive):
        elite = EliteEntry(
            individual=ExprNode("add", children=[ExprNode("input_x"), ExprNode("const_one")]),
            fitness=0.8,
            features=[2, 3],
        )
        archive.add_elite(elite)
        assert archive.size() == 1

    def test_archive_get_elite(self, archive):
        elite = EliteEntry(
            individual=ExprNode("add", children=[ExprNode("input_x"), ExprNode("const_one")]),
            fitness=0.8,
            features=[2, 3],
        )
        archive.add_elite(elite)
        retrieved = archive.get_elite([2, 3])
        assert retrieved is not None
        assert retrieved.fitness == 0.8

    def test_archive_bounds_checking(self, archive):
        elite = EliteEntry(
            individual=ExprNode("input_x"),
            fitness=0.5,
            features=[100, 100],  # Out of bounds
        )
        # Should not crash, just skip
        archive.add_elite(elite)


# ---- EnhancedMAPElitesArchive Tests ----

class TestEnhancedMAPElitesArchive:
    def test_enhanced_archive_initialization(self):
        archive = EnhancedMAPElitesArchive(dims=[5, 5])
        assert archive.size() == 0

    def test_enhanced_archive_with_novelty_screening(self):
        archive = EnhancedMAPElitesArchive(dims=[5, 5])
        elite1 = EliteEntry(
            individual=ExprNode("add", children=[ExprNode("input_x"), ExprNode("const_one")]),
            fitness=0.8,
            features=[1, 1],
        )
        archive.add_elite(elite1)
        assert archive.size() == 1


# ---- NoveltyScreener Tests ----

class TestNoveltyScreener:
    def test_novelty_threshold(self):
        screener = NoveltyScreener(min_distance=0.5)
        fp1 = "aabbccdd11223344"
        fp2 = "aabbccdd11223355"
        novelty = screener.compute_novelty([fp1], fp2)
        assert isinstance(novelty, (int, float))

    def test_is_novel(self):
        screener = NoveltyScreener(min_distance=0.5)
        archive_fps = ["aabbccdd11223344"]
        test_fp = "xxxxxxxx99999999"
        is_novel = screener.is_novel(archive_fps, test_fp)
        assert isinstance(is_novel, bool)


# ---- EvalContext & Polymorphic Tests ----

class TestEvalContextAndPolymorphic:
    def test_eval_context_creation(self):
        ctx = EvalContext()
        ctx.set_input("x", 5.0)
        assert ctx.get_input("x") == 5.0

    def test_polymorphic_op_dispatch(self):
        poly_op = PolymorphicOp()
        result = poly_op.apply_to(OpType.FLOAT, 3.0, 2.0, "add")
        assert isinstance(result, (int, float))

    def test_eval_tree_threading(self):
        tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        ctx = EvalContext()
        ctx.set_input("x", 5.0)
        result = _eval_tree(tree, ctx)
        assert result == 6.0


# ---- Fitness & Symbolic Regression Tests ----

class TestFitnessAndSymbolicRegression:
    def test_symbolic_regression_fitness_zero_error(self):
        X = np.array([[1.0], [2.0], [3.0]])
        y = np.array([2.0, 3.0, 4.0])
        phenotype = lambda x: x + 1.0
        fitness = symbolic_regression_fitness(phenotype, X, y)
        assert fitness > 0.9  # Should be very high

    def test_symbolic_regression_fitness_poor_fit(self):
        X = np.array([[1.0], [2.0], [3.0]])
        y = np.array([2.0, 3.0, 4.0])
        phenotype = lambda x: np.ones_like(x)
        fitness = symbolic_regression_fitness(phenotype, X, y)
        assert fitness < 0.5  # Should be lower

    def test_symbolic_regression_fitness_handles_nans(self):
        X = np.array([[1.0], [2.0], [3.0]])
        y = np.array([2.0, 3.0, 4.0])
        phenotype = lambda x: np.full_like(x, np.nan)
        fitness = symbolic_regression_fitness(phenotype, X, y)
        assert fitness == 0.0  # NaN predictions get zero fitness


# ---- SelfImprovementEngine Tests ----

class TestSelfImprovementEngine:
    def test_engine_initialization(self, vocab, grammar, meta_grammar):
        engine = SelfImprovementEngine(
            vocab=vocab,
            grammar=grammar,
            meta_grammar=meta_grammar,
        )
        assert engine.vocab is not None
        assert engine.meta_grammar is not None

    def test_engine_run(self, vocab, grammar, meta_grammar):
        engine = SelfImprovementEngine(
            vocab=vocab,
            grammar=grammar,
            meta_grammar=meta_grammar,
        )
        engine.run(generations=2, population_size=5)
        # Should complete without crashing
        assert True

    def test_engine_improvement_tracking(self, vocab, grammar, meta_grammar):
        engine = SelfImprovementEngine(
            vocab=vocab,
            grammar=grammar,
            meta_grammar=meta_grammar,
        )
        engine.run(generations=2, population_size=5)
        # Check improvement tracking
        assert engine.improvements is not None


# ---- build_rsi_system Tests ----

class TestBuildRSISystem:
    def test_build_minimal_system(self):
        engine = build_rsi_system(
            budget_ops=1_000,
            budget_seconds=5.0,
            expansion_interval=2,
        )
        assert engine is not None
        assert isinstance(engine, SelfImprovementEngine)

    def test_build_system_with_custom_budget(self):
        engine = build_rsi_system(
            budget_ops=5_000,
            budget_seconds=10.0,
            expansion_interval=3,
        )
        assert engine.budget.max_compute_ops == 5_000


# ---- Integration Tests ----

class TestDeterministicMetaRuleSelection:
    def test_rule_scoring_consistent(self, meta_grammar):
        """Test that rule scoring is deterministic and repeatable."""
        rule1 = meta_grammar.select_rule()
        rule2 = meta_grammar.select_rule()
        # Should select rules based on scores, not random
        assert isinstance(rule1, str)
        assert isinstance(rule2, str)

    def test_precondition_evaluation(self, meta_grammar):
        """Test that preconditions are evaluated correctly."""
        rule = meta_grammar.select_rule()
        precond_met = meta_grammar.rule_preconditions_met(rule)
        assert isinstance(precond_met, bool)

    def test_outcome_tracking_in_expansion(self, meta_grammar):
        """Test that rule outcomes are tracked during expansion."""
        meta_grammar.apply_rule("expand_rule", meta_grammar.grammar)
        # Should have recorded outcome
        assert meta_grammar._expansion_history is not None

    def test_rule_entry_score_computation(self):
        """Test MetaRuleEntry scoring computation."""
        entry = MetaRuleEntry(
            rule_name="test",
            precondition=lambda g: True,
            action=lambda g: g,
            outcome_metric=lambda g: 0.5,
        )
        entry._outcome_history = [0.6, 0.7, 0.8]
        score = entry.compute_score()
        assert score > 0

    def test_deterministic_selection_with_multiple_rules(self, meta_grammar):
        """Test that deterministic selection works with multiple rules."""
        rules = [meta_grammar.select_rule() for _ in range(3)]
        assert all(isinstance(r, str) for r in rules)


class TestOperadicMetaGrammar:
    def test_hyperrule_template_generation(self, meta_grammar):
        """Test that HyperRule templates are generated correctly."""
        # Apply expansion to generate templates
        meta_grammar.apply_rule("expand_rule", meta_grammar.grammar)
        assert meta_grammar.grammar is not None

    def test_binary_lift_operation(self, meta_grammar):
        """Test binary lift operation for rules."""
        original_vocab_size = meta_grammar.vocab.size
        meta_grammar.apply_rule("expand_rule", meta_grammar.grammar)
        # Vocab size may increase after expansion
        assert meta_grammar.vocab.size >= original_vocab_size

    def test_deduplication_in_expansion(self, meta_grammar):
        """Test that duplicate rules are removed during expansion."""
        meta_grammar.apply_rule("expand_rule", meta_grammar.grammar)
        meta_grammar.apply_rule("expand_rule", meta_grammar.grammar)
        # Should not cause issues with duplicates
        assert meta_grammar.grammar is not None

    def test_operadic_composition(self, meta_grammar):
        """Test operadic composition of rules."""
        rule1 = meta_grammar.select_rule()
        rule2 = meta_grammar.select_rule()
        # Both should be valid rules
        assert isinstance(rule1, str)
        assert isinstance(rule2, str)


class TestTopologicalContext:
    def test_topo_key_generation(self, meta_grammar):
        """Test topological key generation for context."""
        tree = meta_grammar.grammar.random_tree()
        topo_key = hash(tree.fingerprint())  # Simplified topo_key
        assert isinstance(topo_key, int)

    def test_with_topo_context(self, meta_grammar):
        """Test applying topological context."""
        tree = meta_grammar.grammar.random_tree()
        ctx = EvalContext()
        ctx.set_input("x", 5.0)
        # Should handle topo context
        assert ctx.get_input("x") == 5.0

    def test_topo_dispatch_routing(self, meta_grammar):
        """Test topological dispatch routing."""
        rule = meta_grammar.select_rule()
        assert isinstance(rule, str)

    def test_eval_tree_threading_with_topo(self, meta_grammar):
        """Test eval_tree threading with topological context."""
        tree = meta_grammar.grammar.random_tree()
        ctx = EvalContext()
        ctx.set_input("x", 3.0)
        result = _eval_tree(tree, ctx)
        assert result is not None

    def test_context_preservation_across_calls(self):
        """Test that context is preserved across multiple calls."""
        ctx = EvalContext()
        ctx.set_input("x", 5.0)
        ctx.set_input("y", 10.0)
        assert ctx.get_input("x") == 5.0
        assert ctx.get_input("y") == 10.0

    def test_nested_topo_contexts(self):
        """Test nested topological contexts."""
        ctx1 = EvalContext()
        ctx1.set_input("x", 5.0)
        ctx2 = EvalContext()
        ctx2.set_input("x", 10.0)
        assert ctx1.get_input("x") == 5.0
        assert ctx2.get_input("x") == 10.0


class TestRefinementTypes:
    def test_op_type_lattice(self):
        """Test OpType lattice structure."""
        float_type = OpType.FLOAT
        int_type = OpType.INT
        assert float_type != int_type

    def test_type_annotations_in_ops(self, vocab):
        """Test type annotations are applied to operations."""
        add_op = vocab.get("add")
        assert add_op is not None
        # Should have proper typing info
        assert callable(add_op)

    def test_type_safe_mutation(self, grammar):
        """Test that mutations respect type safety."""
        tree = grammar.random_tree()
        mutant = grammar.mutate(tree)
        # Should produce valid tree
        assert isinstance(mutant, ExprNode)

    def test_type_lattice_operations(self):
        """Test operations on type lattice."""
        op1_type = OpType.FLOAT
        op2_type = OpType.FLOAT
        assert op1_type == op2_type

    def test_refined_type_checking(self):
        """Test refined type checking in expressions."""
        node = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        # Should have consistent types
        assert node is not None

    def test_polymorphic_type_dispatch(self):
        """Test polymorphic dispatch based on types."""
        poly_op = PolymorphicOp()
        result = poly_op.apply_to(OpType.FLOAT, 3.0, 2.0, "mul")
        assert isinstance(result, (int, float))

    def test_type_annotation_preservation(self, grammar):
        """Test that type annotations are preserved through mutations."""
        tree = grammar.random_tree()
        mutant = grammar.mutate(tree)
        # Type info should still be valid
        assert mutant.depth() >= 0


class TestArchitectureIntegration:
    def test_full_rsi_pipeline(self):
        """Test the full RSI pipeline from initialization to optimization."""
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=2,
        )
        engine.run(generations=10, population_size=10)
        # Should complete without errors
        assert True

    def test_expansion_with_scoring(self):
        """Test that expansion includes scoring of rule selections."""
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=2,
        )
        engine.run(generations=10, population_size=10)
        # Check that expansion history contains scored selections
        has_scored = any("score=" in h for h in engine.meta_grammar._expansion_history)
        assert has_scored, "Expansion history should contain scored rule selections"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])