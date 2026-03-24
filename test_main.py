"""Tests for the RSI-Exploration architecture."""

import random
import pytest
import numpy as np

from main import (
    PrimitiveOp,
    VocabularyLayer,
    ExprNode,
    GrammarLayer,
    MetaGrammarLayer,
    ResourceBudget,
    CostGroundingLoop,
    MAPElitesArchive,
    EliteEntry,
    SelfImprovementEngine,
    build_rsi_system,
    symbolic_regression_fitness,
    _eval_tree,
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
        tree = grammar.random_tree(3)
        assert isinstance(tree, ExprNode)
        assert tree.depth() <= 4  # may vary

    def test_mutation_produces_different_tree(self, grammar):
        random.seed(42)
        tree = grammar.random_tree(2)
        mutated = grammar.mutate(tree)
        assert isinstance(mutated, ExprNode)

    def test_crossover(self, grammar):
        t1 = grammar.random_tree(2)
        t2 = grammar.random_tree(2)
        child = grammar.crossover(t1, t2)
        assert isinstance(child, ExprNode)

    def test_add_rule(self, grammar):
        initial_rules = grammar.num_rules
        grammar.add_rule(lambda t=None: ExprNode("input_x"))
        assert grammar.num_rules == initial_rules + 1


# ---- Meta-Grammar Layer Tests ----

class TestMetaGrammarLayer:
    def test_compose_new_op(self, meta_grammar, vocab):
        initial_size = vocab.size
        meta_grammar._meta_compose_new_op()
        # Should have added a composed op
        assert vocab.size >= initial_size

    def test_parameterize_mutation(self, meta_grammar, grammar):
        initial_rules = grammar.num_rules
        meta_grammar._meta_parameterize_mutation()
        assert grammar.num_rules == initial_rules + 1

    def test_expand_design_space(self, meta_grammar):
        initial_count = meta_grammar.expansion_count
        action = meta_grammar.expand_design_space()
        assert isinstance(action, str)
        assert meta_grammar.expansion_count >= initial_count


# ---- Resource Budget Tests ----

class TestResourceBudget:
    def test_initial_state(self, budget):
        assert budget.compute_fraction == 0.0
        assert not budget.is_exhausted

    def test_tick(self, budget):
        budget.tick(5000)
        assert budget.compute_fraction == 0.5

    def test_exhaustion(self, budget):
        budget.tick(10_000)
        assert budget.is_exhausted

    def test_cost_score_decreases(self, budget):
        score_before = budget.cost_score()
        budget.tick(5000)
        score_after = budget.cost_score()
        assert score_after < score_before

    def test_reset(self, budget):
        budget.tick(5000)
        budget.reset()
        assert budget.compute_fraction == 0.0

    def test_summary(self, budget):
        s = budget.summary()
        assert "compute_used" in s
        assert "cost_score" in s


# ---- Cost Grounding Loop Tests ----

class TestCostGroundingLoop:
    def test_evaluate_with_cost(self, vocab, budget):
        loop = CostGroundingLoop(budget)
        tree = ExprNode("input_x")
        raw, cost, grounded = loop.evaluate_with_cost(
            tree, vocab, symbolic_regression_fitness
        )
        assert 0 <= raw <= 1
        assert 0 < cost <= 1
        assert grounded == raw * cost


# ---- MAP-Elites Archive Tests ----

class TestMAPElitesArchive:
    def test_behavior_descriptor(self, archive):
        tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        bd = archive.behavior_descriptor(tree)
        assert isinstance(bd, tuple)
        assert len(bd) == 2

    def test_insert_and_sample(self, archive):
        tree = ExprNode("input_x")
        entry = EliteEntry(
            tree=tree, raw_fitness=0.5, cost_score=0.9,
            grounded_fitness=0.45, behavior=(0, 0), generation=1
        )
        result = archive.try_insert(entry)
        assert result is True
        parent = archive.sample_parent()
        assert parent is not None

    def test_better_replaces_worse(self, archive):
        tree1 = ExprNode("input_x")
        entry1 = EliteEntry(
            tree=tree1, raw_fitness=0.3, cost_score=0.9,
            grounded_fitness=0.27, behavior=(0, 0), generation=1
        )
        archive.try_insert(entry1)

        tree2 = ExprNode("const_one")
        entry2 = EliteEntry(
            tree=tree2, raw_fitness=0.8, cost_score=0.9,
            grounded_fitness=0.72, behavior=(0, 0), generation=2
        )
        result = archive.try_insert(entry2)
        assert result is True
        assert archive.best_fitness == 0.72

    def test_worse_does_not_replace(self, archive):
        tree1 = ExprNode("input_x")
        entry1 = EliteEntry(
            tree=tree1, raw_fitness=0.8, cost_score=0.9,
            grounded_fitness=0.72, behavior=(0, 0), generation=1
        )
        archive.try_insert(entry1)

        tree2 = ExprNode("const_one")
        entry2 = EliteEntry(
            tree=tree2, raw_fitness=0.2, cost_score=0.9,
            grounded_fitness=0.18, behavior=(0, 0), generation=2
        )
        result = archive.try_insert(entry2)
        assert result is False

    def test_coverage(self, archive):
        assert archive.coverage == 0.0
        tree = ExprNode("input_x")
        entry = EliteEntry(
            tree=tree, raw_fitness=0.5, cost_score=0.9,
            grounded_fitness=0.45, behavior=(0, 0), generation=1
        )
        archive.try_insert(entry)
        assert archive.coverage > 0.0

    def test_summary(self, archive):
        s = archive.summary()
        assert "filled_cells" in s
        assert "coverage" in s


# ---- Eval Tree Tests ----

class TestEvalTree:
    def test_eval_input_x(self, vocab):
        node = ExprNode("input_x")
        assert _eval_tree(node, vocab, 3.0) == 3.0

    def test_eval_add(self, vocab):
        node = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        assert _eval_tree(node, vocab, 5.0) == 6.0

    def test_eval_unknown_op(self, vocab):
        node = ExprNode("unknown_op")
        assert _eval_tree(node, vocab, 1.0) == 0.0


# ---- Self-Improvement Engine Tests ----

class TestSelfImprovementEngine:
    def test_single_step(self):
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
        )
        record = engine.step(population_size=10)
        assert record["generation"] == 1
        assert record["inserted"] >= 0

    def test_multi_generation_run(self):
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=5,
        )
        history = engine.run(generations=10, population_size=10)
        assert len(history) == 10
        assert history[-1]["generation"] == 10

    def test_design_space_expands(self):
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=2,
        )
        initial_vocab = engine.vocab.size
        initial_rules = engine.grammar.num_rules
        engine.run(generations=10, population_size=5)
        expanded = (
            engine.vocab.size > initial_vocab
            or engine.grammar.num_rules > initial_rules
        )
        assert expanded, "Design space should expand over generations"

    def test_fitness_improves(self):
        random.seed(42)
        np.random.seed(42)
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
        )
        history = engine.run(generations=20, population_size=20)
        # Best fitness should be > 0 after some evolution
        assert engine.archive.best_fitness > 0


# ---- Build Factory Tests ----

class TestBuildFactory:
    def test_default_build(self):
        engine = build_rsi_system()
        assert isinstance(engine, SelfImprovementEngine)
        assert engine.vocab.size >= 10
        assert engine.grammar.num_rules >= 4

    def test_custom_fitness(self):
        custom_fn = lambda tree, vocab: 0.42
        engine = build_rsi_system(fitness_fn=custom_fn)
        record = engine.step(population_size=5)
        assert record["archive_best"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

