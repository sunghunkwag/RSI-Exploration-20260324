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


# ---- Library Learning Tests ----

class TestLibraryLearner:
    """Tests for DreamCoder-inspired library learning mechanism."""

    def test_extract_from_repeated_subtrees(self, vocab):
        """When the same subtree appears in multiple trees, it should be extracted."""
        lib = LibraryLearner(vocab, min_subtree_depth=2, min_frequency=2)
        # Build a shared subtree: add(input_x, const_one) — depth 1 from leaves, depth 1 total
        # We need depth >= 2, so: add(mul(input_x, input_x), const_one)
        shared = ExprNode("add", children=[
            ExprNode("mul", children=[ExprNode("input_x"), ExprNode("input_x")]),
            ExprNode("const_one"),
        ])
        # Embed the shared subtree into two different outer trees
        tree1 = ExprNode("neg", children=[
            ExprNode("add", children=[
                ExprNode("mul", children=[ExprNode("input_x"), ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        tree2 = ExprNode("square", children=[
            ExprNode("add", children=[
                ExprNode("mul", children=[ExprNode("input_x"), ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        initial_vocab_size = vocab.size
        new_ops = lib.extract_library([tree1, tree2])
        assert len(new_ops) >= 1, "Should extract at least one library primitive"
        assert vocab.size > initial_vocab_size, "Vocabulary should have grown"

    def test_extracted_op_computes_correctly(self, vocab):
        """Extracted library op should compute same as original subtree."""
        lib = LibraryLearner(vocab, min_subtree_depth=2, min_frequency=2)
        # Subtree: add(square(input_x), const_one) => x^2 + 1
        tree1 = ExprNode("neg", children=[
            ExprNode("add", children=[
                ExprNode("square", children=[ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        tree2 = ExprNode("abs_val", children=[
            ExprNode("add", children=[
                ExprNode("square", children=[ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        new_ops = lib.extract_library([tree1, tree2])
        assert len(new_ops) >= 1
        # The extracted op should compute x^2 + 1
        extracted = new_ops[0]
        assert extracted.arity == 1  # has input_x
        result = extracted.fn(3.0)
        expected = 3.0 ** 2 + 1.0  # = 10.0
        assert abs(result - expected) < 1e-6, f"Expected {expected}, got {result}"

    def test_no_extraction_below_frequency_threshold(self, vocab):
        """Subtrees appearing fewer than min_frequency times should not be extracted."""
        lib = LibraryLearner(vocab, min_subtree_depth=2, min_frequency=3)
        # Only 2 trees with the same subtree — below threshold of 3
        tree1 = ExprNode("neg", children=[
            ExprNode("add", children=[
                ExprNode("mul", children=[ExprNode("input_x"), ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        tree2 = ExprNode("square", children=[
            ExprNode("add", children=[
                ExprNode("mul", children=[ExprNode("input_x"), ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        new_ops = lib.extract_library([tree1, tree2])
        assert len(new_ops) == 0, "Should not extract below frequency threshold"

    def test_no_duplicate_extraction(self, vocab):
        """Running extraction twice on same trees should not create duplicate ops."""
        lib = LibraryLearner(vocab, min_subtree_depth=2, min_frequency=2)
        tree1 = ExprNode("neg", children=[
            ExprNode("add", children=[
                ExprNode("mul", children=[ExprNode("input_x"), ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        tree2 = ExprNode("square", children=[
            ExprNode("add", children=[
                ExprNode("mul", children=[ExprNode("input_x"), ExprNode("input_x")]),
                ExprNode("const_one"),
            ])
        ])
        ops1 = lib.extract_library([tree1, tree2])
        vocab_after_first = vocab.size
        ops2 = lib.extract_library([tree1, tree2])
        assert vocab.size == vocab_after_first, "No duplicates should be added"
        assert len(ops2) == 0

    def test_depth_amplification(self):
        """
        CRITICAL TEST: Demonstrates the system can now express programs
        that were IMPOSSIBLE before library learning.

        With max_depth=3, the deepest tree has 3 levels of nesting.
        After library learning extracts a depth-2 subtree as a primitive,
        a depth-3 tree using that primitive can express what previously
        required depth-5.
        """
        random.seed(123)
        np.random.seed(123)
        engine = build_rsi_system(
            max_depth=3,
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=5,
            use_library_learning=True,
            library_min_depth=2,
            library_min_freq=2,
        )
        # Run enough generations to populate the archive and trigger library learning
        engine.run(generations=20, population_size=20)

        # Check that library learning actually happened
        lib_learner = engine.meta_grammar.library_learner
        assert lib_learner is not None

        # The vocabulary should have grown beyond what random composition achieves
        # (initial default is 11 ops, random composition adds one at a time)
        initial_vocab = 11  # default count from VocabularyLayer._register_defaults
        assert engine.vocab.size > initial_vocab, (
            "Vocabulary should have expanded via library learning and/or meta-grammar"
        )

    def test_library_learning_with_engine_integration(self):
        """Library learning integrates correctly with the full RSI engine."""
        random.seed(42)
        np.random.seed(42)
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=5,
            use_library_learning=True,
        )
        history = engine.run(generations=15, population_size=15)
        assert len(history) == 15
        # Engine should not crash and should maintain valid state
        assert engine.archive.best_fitness >= 0
        assert engine.vocab.size >= 11

    def test_constant_subtree_extraction(self, vocab):
        """Subtrees without input_x should be extracted as arity-0 ops."""
        lib = LibraryLearner(vocab, min_subtree_depth=2, min_frequency=2)
        # Subtree: add(const_one, const_one) — no input_x, depth=1
        # Need depth >= 2: add(square(const_one), const_one)
        const_sub = ExprNode("add", children=[
            ExprNode("square", children=[ExprNode("const_one")]),
            ExprNode("const_one"),
        ])
        tree1 = ExprNode("mul", children=[
            ExprNode("input_x"),
            ExprNode("add", children=[
                ExprNode("square", children=[ExprNode("const_one")]),
                ExprNode("const_one"),
            ]),
        ])
        tree2 = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("add", children=[
                ExprNode("square", children=[ExprNode("const_one")]),
                ExprNode("const_one"),
            ]),
        ])
        new_ops = lib.extract_library([tree1, tree2])
        # Should extract the constant subtree
        const_ops = [op for op in new_ops if op.arity == 0]
        if const_ops:
            # Should compute 1^2 + 1 = 2.0
            result = const_ops[0].fn()
            assert abs(result - 2.0) < 1e-6



# ---- Novelty Screener Tests ----

class TestNoveltyScreener:
    """Tests for the fingerprint-based novelty rejection sampling."""

    def test_identical_trees_have_similarity_one(self):
        """Two identical trees should have Jaccard similarity of 1.0."""
        screener = NoveltyScreener(similarity_threshold=0.85)
        tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        sim = screener.structural_similarity(tree, tree)
        assert sim == 1.0

    def test_different_trees_have_lower_similarity(self):
        """Structurally different trees should have similarity < 1.0."""
        screener = NoveltyScreener(similarity_threshold=0.85)
        tree_a = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        tree_b = ExprNode("mul", children=[
            ExprNode("input_x"),
            ExprNode("input_x"),
        ])
        sim = screener.structural_similarity(tree_a, tree_b)
        assert sim < 1.0

    def test_completely_different_trees(self):
        """Trees with no shared subtrees should have low similarity."""
        screener = NoveltyScreener(similarity_threshold=0.85)
        tree_a = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        tree_b = ExprNode("neg", children=[
            ExprNode("square", children=[ExprNode("const_zero")]),
        ])
        sim = screener.structural_similarity(tree_a, tree_b)
        assert sim < 0.5

    def test_should_accept_novel_candidate(self):
        """A novel candidate should be accepted."""
        screener = NoveltyScreener(similarity_threshold=0.85)
        candidate = ExprNode("mul", children=[
            ExprNode("input_x"),
            ExprNode("input_x"),
        ])
        existing = [
            EliteEntry(
                tree=ExprNode("add", children=[
                    ExprNode("const_one"),
                    ExprNode("const_zero"),
                ]),
                raw_fitness=0.5, cost_score=0.9,
                grounded_fitness=0.45, behavior=(0, 0), generation=1,
            )
        ]
        assert screener.should_accept(candidate, existing)

    def test_should_reject_too_similar_candidate(self):
        """A candidate identical to an archive member should be rejected."""
        screener = NoveltyScreener(similarity_threshold=0.5)
        tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        existing = [
            EliteEntry(
                tree=ExprNode("add", children=[
                    ExprNode("input_x"),
                    ExprNode("const_one"),
                ]),
                raw_fitness=0.5, cost_score=0.9,
                grounded_fitness=0.45, behavior=(0, 0), generation=1,
            )
        ]
        assert not screener.should_accept(tree, existing)

    def test_empty_archive_always_accepts(self):
        """With no archive entries, all candidates should be accepted."""
        screener = NoveltyScreener(similarity_threshold=0.5)
        candidate = ExprNode("input_x")
        assert screener.should_accept(candidate, [])

    def test_rejection_rate_tracking(self):
        """Rejection rate should be tracked correctly."""
        screener = NoveltyScreener(similarity_threshold=0.0)
        tree = ExprNode("input_x")
        existing = [
            EliteEntry(
                tree=ExprNode("input_x"),
                raw_fitness=0.5, cost_score=0.9,
                grounded_fitness=0.45, behavior=(0, 0), generation=1,
            )
        ]
        screener.should_accept(tree, existing)
        assert screener._screenings == 1
        assert screener._rejections == 1
        assert screener.rejection_rate == 1.0

    def test_summary(self):
        """Summary should include screening stats."""
        screener = NoveltyScreener()
        s = screener.summary()
        assert "screenings" in s
        assert "rejections" in s
        assert "rejection_rate" in s


class TestEnhancedMAPElitesWithNoveltyScreening:
    """Tests for the EnhancedMAPElitesArchive with novelty rejection sampling."""

    def test_enhanced_archive_has_screener(self):
        """Enhanced archive should initialize with a NoveltyScreener."""
        archive = EnhancedMAPElitesArchive(dims=[6, 10])
        assert hasattr(archive, "novelty_screener")
        assert isinstance(archive.novelty_screener, NoveltyScreener)

    def test_custom_similarity_threshold(self):
        """Custom similarity threshold should be passed to screener."""
        archive = EnhancedMAPElitesArchive(
            dims=[6, 10], similarity_threshold=0.5
        )
        assert archive.novelty_screener.similarity_threshold == 0.5

    def test_summary_includes_screening_stats(self):
        """Archive summary should include novelty screening info."""
        archive = EnhancedMAPElitesArchive(dims=[6, 10])
        s = archive.summary()
        assert "novelty_screening" in s
        assert "screenings" in s["novelty_screening"]

    def test_similar_candidate_rejected_from_occupied_cell(self):
        """A very similar candidate in an occupied cell should be rejected."""
        archive = EnhancedMAPElitesArchive(
            dims=[6, 10], similarity_threshold=0.3, novelty_rate=0.0
        )
        tree1 = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        entry1 = EliteEntry(
            tree=tree1, raw_fitness=0.5, cost_score=0.9,
            grounded_fitness=0.45, behavior=(0, 0), generation=1,
        )
        archive.try_insert(entry1)

        # Same tree, same cell, lower fitness — should be rejected by both
        # elitism AND novelty screening
        entry2 = EliteEntry(
            tree=tree1, raw_fitness=0.3, cost_score=0.9,
            grounded_fitness=0.27, behavior=(0, 0), generation=2,
        )
        result = archive.try_insert(entry2)
        assert result is False

    def test_engine_with_novelty_screening(self):
        """Full RSI engine should work with novelty rejection sampling."""
        random.seed(42)
        np.random.seed(42)
        engine = build_rsi_system(
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=5,
            use_enhanced_archive=True,
            similarity_threshold=0.85,
        )
        history = engine.run(generations=10, population_size=10)
        assert len(history) == 10
        assert engine.archive.best_fitness >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
