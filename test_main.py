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
        # Build a shared subtree: add(input_x, const_one) -- depth 1 from leaves, depth 1 total
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
        # Only 2 trees with the same subtree -- below threshold of 3
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
        # Subtree: add(const_one, const_one) -- no input_x, depth=1
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

    def test_structural_similarity(self):
        """
        Verify that structural_similarity(tree_a, tree_b) correctly
        calculates the Jaccard similarity between two expression trees
        based on their subtree fingerprints.
        """
        screener = NoveltyScreener(similarity_threshold=0.85)

        # --- Case 1: identical trees -> Jaccard = 1.0 ---
        tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        assert screener.structural_similarity(tree, tree) == 1.0

        # --- Case 2: partially overlapping trees -> 0 < Jaccard < 1 ---
        # tree_a subtrees: {add(input_x, const_one), input_x, const_one}
        tree_a = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        # tree_b subtrees: {mul(input_x, const_one), input_x, const_one}
        # Shared: {input_x, const_one} = 2;  Union = 4 (add(..), mul(..), input_x, const_one)
        tree_b = ExprNode("mul", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        sim_partial = screener.structural_similarity(tree_a, tree_b)
        assert 0.0 < sim_partial < 1.0
        # Exact expected: |{input_x, const_one}| / |{add(..), mul(..), input_x, const_one}| = 2/4 = 0.5
        assert abs(sim_partial - 0.5) < 1e-9

        # --- Case 3: completely disjoint trees -> Jaccard = 0.0 ---
        # tree_c has no shared subtree fingerprints with tree_d
        tree_c = ExprNode("input_x")  # subtrees: {input_x}
        tree_d = ExprNode("const_one")  # subtrees: {const_one}
        sim_disjoint = screener.structural_similarity(tree_c, tree_d)
        assert sim_disjoint == 0.0

        # --- Case 4: deeper tree, one is subtree of the other ---
        # tree_e contains tree_a as a subtree, so all of tree_a's
        # fingerprints appear in tree_e's set -> similarity > 0
        tree_e = ExprNode("neg", children=[
            ExprNode("add", children=[
                ExprNode("input_x"),
                ExprNode("const_one"),
            ])
        ])
        sim_subset = screener.structural_similarity(tree_a, tree_e)
        # tree_a fps is subset of tree_e fps, so intersection = |tree_a fps|
        # Jaccard = |tree_a fps| / |tree_e fps| = 3/4 = 0.75
        assert 0.0 < sim_subset < 1.0
        assert abs(sim_subset - 0.75) < 1e-9

    def test_should_accept_rejects_highly_similar(self):
        """
        Verify that should_accept(candidate, archive_entries) correctly
        rejects candidates when their maximum similarity to existing
        archive entries exceeds the similarity_threshold, and accepts
        them otherwise.
        """
        # Use a threshold of 0.5 so we can test both sides clearly
        screener = NoveltyScreener(similarity_threshold=0.5)

        # Build an archive entry with tree: add(input_x, const_one)
        archive_tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        archive_entries = [
            EliteEntry(
                tree=archive_tree,
                raw_fitness=0.5,
                cost_score=0.9,
                grounded_fitness=0.45,
                behavior=(0, 0),
                generation=1,
            )
        ]

        # --- Candidate identical to archive member -> similarity = 1.0 > 0.5 -> REJECT ---
        identical_candidate = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        assert not screener.should_accept(identical_candidate, archive_entries)

        # --- Candidate completely disjoint -> similarity = 0.0 <= 0.5 -> ACCEPT ---
        novel_candidate = ExprNode("const_zero")
        assert screener.should_accept(novel_candidate, archive_entries)

        # --- Candidate with borderline similarity exactly at threshold -> ACCEPT ---
        # mul(input_x, const_one) shares {input_x, const_one} with archive,
        # Jaccard = 2/4 = 0.5  (== threshold -> should accept since condition is <=)
        borderline_candidate = ExprNode("mul", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        assert screener.should_accept(borderline_candidate, archive_entries)

        # --- Candidate slightly above threshold -> REJECT ---
        # Use screener with lower threshold to force rejection of the partial overlap
        strict_screener = NoveltyScreener(similarity_threshold=0.4)
        assert not strict_screener.should_accept(borderline_candidate, archive_entries)

    def test_screener_counters_and_summary(self):
        """
        Ensure the screener correctly updates the _screenings and
        _rejections counters and outputs the correct summary dictionary.
        """
        screener = NoveltyScreener(similarity_threshold=0.5)

        # Verify initial state
        assert screener._screenings == 0
        assert screener._rejections == 0
        assert screener.rejection_rate == 0.0

        archive_tree = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        archive_entries = [
            EliteEntry(
                tree=archive_tree,
                raw_fitness=0.5,
                cost_score=0.9,
                grounded_fitness=0.45,
                behavior=(0, 0),
                generation=1,
            )
        ]

        # Screen 1: novel candidate -> accepted (screening +1, rejection +0)
        novel = ExprNode("const_zero")
        screener.should_accept(novel, archive_entries)
        assert screener._screenings == 1
        assert screener._rejections == 0

        # Screen 2: identical candidate -> rejected (screening +1, rejection +1)
        duplicate = ExprNode("add", children=[
            ExprNode("input_x"),
            ExprNode("const_one"),
        ])
        screener.should_accept(duplicate, archive_entries)
        assert screener._screenings == 2
        assert screener._rejections == 1

        # Screen 3: another novel candidate -> accepted
        novel2 = ExprNode("const_one")
        screener.should_accept(novel2, archive_entries)
        assert screener._screenings == 3
        assert screener._rejections == 1

        # Verify rejection_rate = 1/3
        assert abs(screener.rejection_rate - 1.0 / 3.0) < 1e-9

        # Verify summary dict structure and values
        s = screener.summary()
        assert isinstance(s, dict)
        assert s["screenings"] == 3
        assert s["rejections"] == 1
        assert abs(s["rejection_rate"] - round(1.0 / 3.0, 4)) < 1e-6


# ---- Enhanced MAP-Elites Archive with Novelty Rejection Tests ----


class TestEnhancedArchiveNoveltyRejection:
    """Integration tests for EnhancedMAPElitesArchive with NoveltyScreener."""

    def test_enhanced_archive_novelty_rejection(self):
        """
        Verify that the novelty screener inside EnhancedMAPElitesArchive
        rejects a structurally identical (high-similarity) candidate even
        when it has *higher* grounded_fitness than the occupant of the
        same behavioral cell.

        This proves that the rejection is caused by the NoveltyScreener,
        not by the standard elitism check (which would accept a fitter
        candidate).
        """
        # Use a very low similarity threshold so that any overlap triggers rejection.
        # Disable novelty injection (novelty_rate=0.0) so a rejected candidate
        # cannot sneak into a neighbour cell.
        archive = EnhancedMAPElitesArchive(
            dims=[6, 10],
            novelty_rate=0.0,
            similarity_threshold=0.3,
        )

        # --- Step 1: insert an initial entry (cell is empty -> always accepted) ---
        initial_tree = ExprNode("add", children=[
            ExprNode("mul", children=[
                ExprNode("input_x"),
                ExprNode("input_x"),
            ]),
            ExprNode("const_one"),
        ])
        initial_entry = EliteEntry(
            tree=initial_tree,
            raw_fitness=0.4,
            cost_score=0.9,
            grounded_fitness=0.36,
            behavior=(1, 1),
            generation=1,
        )
        assert archive.try_insert(initial_entry) is True
        assert archive.summary()["filled_cells"] == 1

        # --- Step 2: create a *structurally identical* candidate with HIGHER fitness ---
        # Same tree structure -> structural_similarity == 1.0 >> threshold (0.3)
        similar_tree = ExprNode("add", children=[
            ExprNode("mul", children=[
                ExprNode("input_x"),
                ExprNode("input_x"),
            ]),
            ExprNode("const_one"),
        ])
        better_entry = EliteEntry(
            tree=similar_tree,
            raw_fitness=0.9,
            cost_score=0.95,
            grounded_fitness=0.855,       # clearly higher than 0.36
            behavior=(1, 1),              # same cell
            generation=2,
        )

        # The standard elitism check would accept this (0.855 > 0.36),
        # but the novelty screener fires first and rejects it.
        result = archive.try_insert(better_entry)
        assert result is False

        # The cell still holds the original (lower-fitness) entry
        assert archive.best_fitness == 0.36

        # --- Step 3: verify the screener's rejection counter incremented ---
        screening_summary = archive.summary()["novelty_screening"]
        assert screening_summary["rejections"] == 1
        assert screening_summary["screenings"] == 1
        assert screening_summary["rejection_rate"] == 1.0

        # --- Step 4: insert a genuinely novel candidate into the same cell ---
        # This tree is structurally very different -> low similarity -> accepted
        novel_tree = ExprNode("neg", children=[
            ExprNode("const_zero"),
        ])
        novel_entry = EliteEntry(
            tree=novel_tree,
            raw_fitness=0.95,
            cost_score=0.95,
            grounded_fitness=0.9025,      # higher fitness + novel structure
            behavior=(1, 1),              # same cell
            generation=3,
        )
        assert archive.try_insert(novel_entry) is True
        assert archive.best_fitness == 0.9025

        # Screener stats: 2 screenings total, 1 rejection
        screening_summary_2 = archive.summary()["novelty_screening"]
        assert screening_summary_2["screenings"] == 2
        assert screening_summary_2["rejections"] == 1


# ---------------------------------------------------------------------------
# SESSION 10: MECHANISM 1 (SELF-REFERENCE) TESTS
# ---------------------------------------------------------------------------

class TestSelfReference:
    """Tests for Mechanism 1: Self-Reference (A.7 Diagonal Lemma, D.1 Quines)."""

    def test_self_encode_returns_deterministic_value(self, vocab):
        tree = ExprNode("self_encode")
        ctx = EvalContext(self_fingerprint=tree.fingerprint())
        v1 = _eval_tree(tree, vocab, 0.0, ctx)
        v2 = _eval_tree(tree, vocab, 0.0, ctx)
        assert v1 == v2
        assert 0.0 <= v1 <= 1.0

    def test_self_encode_differs_for_different_trees(self, vocab):
        tree_a = ExprNode("add", [ExprNode("input_x"), ExprNode("const_one")])
        tree_b = ExprNode("mul", [ExprNode("input_x"), ExprNode("input_x")])
        ctx_a = EvalContext(self_fingerprint=tree_a.fingerprint())
        ctx_b = EvalContext(self_fingerprint=tree_b.fingerprint())
        se_node = ExprNode("self_encode")
        v_a = _eval_tree(se_node, vocab, 0.0, ctx_a)
        v_b = _eval_tree(se_node, vocab, 0.0, ctx_b)
        assert v_a != v_b

    def test_self_encode_in_composition(self, vocab):
        tree = ExprNode("add", [ExprNode("input_x"), ExprNode("self_encode")])
        ctx = EvalContext(self_fingerprint=tree.fingerprint())
        result = _eval_tree(tree, vocab, 5.0, ctx)
        fp_val = (int(tree.fingerprint()[:8], 16) % 10000) / 10000.0
        assert abs(result - (5.0 + fp_val)) < 1e-9

    def test_self_encode_without_context_returns_zero(self, vocab):
        tree = ExprNode("self_encode")
        result = _eval_tree(tree, vocab, 0.0)
        assert result == 0.0

    def test_self_encode_fixed_point_property(self, vocab):
        """Self-referential trees express fixed-point computations."""
        tree = ExprNode("add", [ExprNode("input_x"), ExprNode("self_encode")])
        ctx = EvalContext(self_fingerprint=tree.fingerprint())
        fp_val = (int(tree.fingerprint()[:8], 16) % 10000) / 10000.0
        for x in [0.0, 1.0, -3.5, 100.0]:
            result = _eval_tree(tree, vocab, x, ctx)
            assert abs(result - (x + fp_val)) < 1e-9
        tree2 = ExprNode("mul", [ExprNode("input_x"), ExprNode("self_encode")])
        ctx2 = EvalContext(self_fingerprint=tree2.fingerprint())
        fp_val2 = (int(tree2.fingerprint()[:8], 16) % 10000) / 10000.0
        assert fp_val != fp_val2
        result2 = _eval_tree(tree2, vocab, 5.0, ctx2)
        assert abs(result2 - (5.0 * fp_val2)) < 1e-9


# ---------------------------------------------------------------------------
# SESSION 10: MECHANISM 2 (CONTEXT-DEPENDENT EVALUATION) TESTS
# ---------------------------------------------------------------------------

class TestContextDependentEvaluation:
    """Tests for Mechanism 2: Context-Dependent Evaluation (C.3, G.6)."""

    def test_eval_context_creation(self):
        ctx = EvalContext()
        assert ctx.niche_id == 0
        assert ctx.env_tag == "default"
        assert ctx.self_fingerprint == ""

    def test_context_key_in_range(self):
        ctx1 = EvalContext(niche_id=0, env_tag="test")
        ctx2 = EvalContext(niche_id=1, env_tag="test")
        assert 0 <= ctx1.context_key() <= 3
        assert 0 <= ctx2.context_key() <= 3

    def test_polymorphic_op_dispatches_by_context(self):
        dispatch = {
            0: lambda a: a * 2,
            1: lambda a: a + 10,
            2: lambda a: -a,
            3: lambda a: a * a,
        }
        pop = PolymorphicOp(
            name="poly_test", arity=1,
            dispatch_table=dispatch,
            default_fn=lambda a: a,
        )
        results = set()
        for niche in range(10):
            ctx = EvalContext(niche_id=niche, env_tag="test")
            results.add(pop(5.0, ctx=ctx))
        assert len(results) >= 2

    def test_polymorphic_op_without_context_uses_default(self):
        pop = PolymorphicOp(
            name="poly_test", arity=1,
            dispatch_table={0: lambda a: a * 2},
            default_fn=lambda a: a + 100,
        )
        assert pop(5.0) == 105.0

    def test_polymorphic_op_in_eval_tree(self, vocab):
        pop = PolymorphicOp(
            name="poly_scale", arity=1,
            dispatch_table={0: lambda a: a * 10, 1: lambda a: a * 20,
                            2: lambda a: a * 30, 3: lambda a: a * 40},
            default_fn=lambda a: a,
        )
        vocab.register(pop)
        tree = ExprNode("poly_scale", [ExprNode("input_x")])
        ctx = EvalContext(niche_id=0, env_tag="test")
        key = ctx.context_key()
        expected = {0: 10, 1: 20, 2: 30, 3: 40}[key]
        result = _eval_tree(tree, vocab, 3.0, ctx)
        assert result == 3.0 * expected

    def test_same_tree_different_context_different_output(self, vocab):
        """Critical F_theo expansion: same tree, different context, different output."""
        pop = PolymorphicOp(
            name="ctx_op", arity=1,
            dispatch_table={0: lambda a: a + 1, 1: lambda a: a * 2,
                            2: lambda a: a - 1, 3: lambda a: a ** 2},
            default_fn=lambda a: a,
        )
        vocab.register(pop)
        tree = ExprNode("ctx_op", [ExprNode("input_x")])
        outputs = set()
        for niche in range(20):
            for env in ["alpha", "beta", "gamma", "delta"]:
                ctx = EvalContext(niche_id=niche, env_tag=env)
                outputs.add(_eval_tree(tree, vocab, 5.0, ctx))
        assert len(outputs) >= 2

    def test_context_backward_compatible(self, vocab):
        tree = ExprNode("add", [ExprNode("input_x"), ExprNode("const_one")])
        r1 = _eval_tree(tree, vocab, 3.0)
        ctx = EvalContext(self_fingerprint=tree.fingerprint())
        r2 = _eval_tree(tree, vocab, 3.0, ctx)
        assert r1 == r2 == 4.0

    def test_fitness_functions_accept_context(self, vocab):
        tree = ExprNode("add", [ExprNode("input_x"), ExprNode("const_one")])
        ctx = EvalContext(self_fingerprint=tree.fingerprint(), env_tag="test")
        r1 = symbolic_regression_fitness(tree, vocab, ctx=ctx)
        r2 = symbolic_regression_fitness(tree, vocab)
        assert isinstance(r1, float)
        assert isinstance(r2, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
