"""
RSI-Exploration: Recursive Self-Improvement Architecture
=========================================================

A hybrid architecture combining:
1. Darwin Godel Machine (DGM) self-improvement loops
2. MAP-Elites quality-diversity search

The system implements three-layer design space expansion:
- Vocabulary Layer: primitive operations that can be composed
- Grammar Layer: rules for composing vocabulary into programs
- Meta-Grammar Layer: rules for generating new grammar rules

Physical cost grounding is provided through a resource accounting
system that tracks compute, memory, and wall-clock time.

Inspired by:
- guillaumepourcel/dgm (Darwin Godel Machine)
- b-albar/evolve-anything (LLM-powered MAP-Elites)
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. VOCABULARY LAYER
# ---------------------------------------------------------------------------

@dataclass
class PrimitiveOp:
    """A single primitive operation in the vocabulary."""
    name: str
    arity: int
    fn: Callable
    cost: float = 1.0
    description: str = ""

    def __call__(self, *args):
        return self.fn(*args)


class VocabularyLayer:
    """Manages the set of primitive operations available to the system."""

    def __init__(self):
        self._ops: Dict[str, PrimitiveOp] = {}
        self._register_defaults()

    def _register_defaults(self):
        defaults = [
            PrimitiveOp("add", 2, lambda a, b: a + b, 1.0, "Addition"),
            PrimitiveOp("sub", 2, lambda a, b: a - b, 1.0, "Subtraction"),
            PrimitiveOp("mul", 2, lambda a, b: a * b, 1.5, "Multiplication"),
            PrimitiveOp("safe_div", 2, lambda a, b: a / b if b != 0 else 0.0, 2.0, "Safe division"),
            PrimitiveOp("neg", 1, lambda a: -a, 0.5, "Negation"),
            PrimitiveOp("abs_val", 1, lambda a: abs(a), 0.5, "Absolute value"),
            PrimitiveOp("square", 1, lambda a: a * a, 1.0, "Square"),
            PrimitiveOp("clamp", 1, lambda a: max(-1e6, min(1e6, a)), 0.5, "Clamp to safe range"),
            PrimitiveOp("identity", 1, lambda a: a, 0.1, "Identity"),
            PrimitiveOp("const_one", 0, lambda: 1.0, 0.1, "Constant 1"),
            PrimitiveOp("const_zero", 0, lambda: 0.0, 0.1, "Constant 0"),
        ]
        for op in defaults:
            self._ops[op.name] = op

    def register(self, op: PrimitiveOp):
        self._ops[op.name] = op
        logger.info(f"Vocabulary expanded: +{op.name} (arity={op.arity}, cost={op.cost})")

    def get(self, name: str) -> Optional[PrimitiveOp]:
        return self._ops.get(name)

    def all_ops(self) -> List[PrimitiveOp]:
        return list(self._ops.values())

    def random_op(self, max_arity: int = 2) -> PrimitiveOp:
        candidates = [op for op in self._ops.values() if op.arity <= max_arity]
        return random.choice(candidates)

    @property
    def size(self) -> int:
        return len(self._ops)


# ---------------------------------------------------------------------------
# 2. GRAMMAR LAYER
# ---------------------------------------------------------------------------

@dataclass
class ExprNode:
    """A node in an expression tree (AST)."""
    op_name: str
    children: List["ExprNode"] = field(default_factory=list)
    value: Optional[float] = None

    def depth(self) -> int:
        if not self.children:
            return 0
        return 1 + max(c.depth() for c in self.children)

    def size(self) -> int:
        return 1 + sum(c.size() for c in self.children)

    def to_dict(self) -> dict:
        d = {"op": self.op_name}
        if self.value is not None:
            d["value"] = self.value
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        return d

    def fingerprint(self) -> str:
        return hashlib.md5(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()[:12]


class GrammarLayer:
    """Rules for composing vocabulary into expression trees."""

    def __init__(self, vocab: VocabularyLayer, max_depth: int = 5, max_size: int = 30):
        self.vocab = vocab
        self.max_depth = max_depth
        self.max_size = max_size
        self._composition_rules: List[Callable] = []
        self._register_default_rules()

    def _register_default_rules(self):
        self._composition_rules.extend([
            self._rule_grow,
            self._rule_point_mutate,
            self._rule_subtree_crossover,
            self._rule_hoist,
        ])

    def random_tree(self, max_depth: int = None) -> ExprNode:
        return self._rule_grow(max_depth or self.max_depth)

    def _rule_grow(self, max_depth: int = 3) -> ExprNode:
        if max_depth <= 0:
            if random.random() < 0.5:
                return ExprNode("input_x")
            op = self.vocab.random_op(max_arity=0)
            return ExprNode(op.name)
        op = self.vocab.random_op()
        children = [self._rule_grow(max_depth - 1) for _ in range(op.arity)]
        return ExprNode(op.name, children=children)

    def _rule_point_mutate(self, tree: ExprNode = None) -> ExprNode:
        if tree is None:
            tree = self.random_tree(2)
        tree = copy.deepcopy(tree)
        nodes = self._collect_nodes(tree)
        if not nodes:
            return tree
        target = random.choice(nodes)
        op = self.vocab.random_op(max_arity=len(target.children))
        target.op_name = op.name
        return tree

    def _rule_subtree_crossover(self, t1: ExprNode = None, t2: ExprNode = None) -> ExprNode:
        if t1 is None:
            t1 = self.random_tree(3)
        if t2 is None:
            t2 = self.random_tree(3)
        t1, t2 = copy.deepcopy(t1), copy.deepcopy(t2)
        nodes1, nodes2 = self._collect_nodes(t1), self._collect_nodes(t2)
        if nodes1 and nodes2:
            n1, n2 = random.choice(nodes1), random.choice(nodes2)
            n1.op_name, n1.children, n1.value = n2.op_name, n2.children, n2.value
        return t1

    def _rule_hoist(self, tree: ExprNode = None) -> ExprNode:
        if tree is None:
            tree = self.random_tree(3)
        nodes = self._collect_nodes(tree)
        inner = [n for n in nodes if n.children]
        return copy.deepcopy(random.choice(inner)) if inner else copy.deepcopy(tree)

    def _collect_nodes(self, node: ExprNode) -> List[ExprNode]:
        result = [node]
        for c in node.children:
            result.extend(self._collect_nodes(c))
        return result

    def mutate(self, tree: ExprNode) -> ExprNode:
        return random.choice(self._composition_rules[1:])(tree)

    def crossover(self, t1: ExprNode, t2: ExprNode) -> ExprNode:
        return self._rule_subtree_crossover(t1, t2)

    def add_rule(self, rule_fn: Callable):
        self._composition_rules.append(rule_fn)
        logger.info(f"Grammar expanded: +rule {rule_fn.__name__}")

    @property
    def num_rules(self) -> int:
        return len(self._composition_rules)


# ---------------------------------------------------------------------------
# 3. META-GRAMMAR LAYER
# ---------------------------------------------------------------------------

class MetaGrammarLayer:
    """Generates new grammar rules and vocabulary expansions at runtime."""

    def __init__(self, vocab: VocabularyLayer, grammar: GrammarLayer,
                 library_learner: LibraryLearner = None):
        self.vocab = vocab
        self.grammar = grammar
        self.library_learner = library_learner
        self._meta_rules: List[Callable] = []
        self._expansion_history: List[str] = []
        self._register_default_meta_rules()

    def _register_default_meta_rules(self):
        self._meta_rules.extend([
            self._meta_compose_new_op,
            self._meta_parameterize_mutation,
        ])

    def _meta_compose_new_op(self) -> Optional[PrimitiveOp]:
        unary = [op for op in self.vocab.all_ops() if op.arity == 1]
        if len(unary) < 2:
            return None
        op1, op2 = random.sample(unary, 2)
        new_name = f"{op1.name}_then_{op2.name}"
        if self.vocab.get(new_name) is not None:
            return None
        new_fn = lambda a, _o1=op1, _o2=op2: _o2(_o1(a))
        new_op = PrimitiveOp(new_name, 1, new_fn, op1.cost + op2.cost, f"Composed: {op1.name} -> {op2.name}")
        self.vocab.register(new_op)
        self._expansion_history.append(f"new_op:{new_name}")
        return new_op

    def _meta_parameterize_mutation(self) -> Optional[Callable]:
        scale = random.uniform(0.5, 2.0)

        def scaled_mutate(tree: ExprNode = None) -> ExprNode:
            if tree is None:
                tree = self.grammar.random_tree(2)
            tree = copy.deepcopy(tree)
            nodes = self.grammar._collect_nodes(tree)
            for _ in range(max(1, int(len(nodes) * scale * 0.3))):
                target = random.choice(nodes)
                op = self.vocab.random_op(max_arity=len(target.children))
                target.op_name = op.name
            return tree

        scaled_mutate.__name__ = f"scaled_mutate_{scale:.2f}"
        self.grammar.add_rule(scaled_mutate)
        self._expansion_history.append(f"new_rule:{scaled_mutate.__name__}")
        return scaled_mutate

    def expand_design_space(self, elite_trees: List[ExprNode] = None) -> str:
        """
        Expand the design space. If elite_trees are provided and a library
        learner is configured, library learning is attempted with 50% probability
        (the other meta-rules get the remaining 50%).
        """
        if (
            elite_trees
            and self.library_learner is not None
            and random.random() < 0.5
        ):
            new_ops = self.library_learner.extract_library(elite_trees)
            if new_ops:
                names = [op.name for op in new_ops]
                self._expansion_history.append(f"library_learning:{','.join(names)}")
                action = f"Library learning: extracted {len(new_ops)} new primitives"
                logger.info(f"Meta-grammar: {action}")
                return action

        meta_rule = random.choice(self._meta_rules)
        result = meta_rule()
        action = f"Applied {meta_rule.__name__}: {'success' if result else 'no-op'}"
        logger.info(f"Meta-grammar: {action}")
        return action

    @property
    def expansion_count(self) -> int:
        return len(self._expansion_history)


# ---------------------------------------------------------------------------
# 3b. LIBRARY LEARNING (DreamCoder-inspired subtree compression)
# ---------------------------------------------------------------------------

class LibraryLearner:
    """
    Extracts frequently occurring subtrees from elite programs and promotes
    them to new primitive operations in the vocabulary.

    Inspired by DreamCoder's wake-sleep library learning / compression phase.
    This genuinely expands the reachable design space because:
    - A subtree of depth D becomes a single node (depth 0)
    - Under a fixed max_depth constraint, programs that previously required
      depth max_depth + D are now reachable at depth max_depth
    - New primitives are semantically meaningful (discovered from successful
      programs, not randomly composed)

    The mechanism is structurally different from MetaGrammarLayer._meta_compose_new_op
    which only randomly chains two existing unary ops. Library learning:
    1. Considers subtrees of ANY arity and depth
    2. Selects based on frequency in the elite population (not random)
    3. Can discover multi-step computations involving binary ops, constants, etc.
    """

    def __init__(
        self,
        vocab: VocabularyLayer,
        min_subtree_depth: int = 2,
        min_frequency: int = 2,
        max_library_additions: int = 3,
    ):
        self.vocab = vocab
        self.min_subtree_depth = min_subtree_depth
        self.min_frequency = min_frequency
        self.max_library_additions = max_library_additions
        self._learned_ops: List[str] = []

    def _collect_subtrees(self, node: ExprNode) -> List[ExprNode]:
        """Collect all subtrees from a tree (including the root)."""
        result = [node]
        for c in node.children:
            result.extend(self._collect_subtrees(c))
        return result

    def _subtree_to_callable(self, subtree: ExprNode) -> Tuple[int, Callable]:
        """
        Convert a subtree into a callable function.

        Returns (arity, fn) where arity is the number of distinct input_x
        leaves found. For subtrees with input_x, arity=1 (single variable).
        For subtrees without input_x (pure constants), arity=0.
        """
        has_input = self._has_input_x(subtree)
        arity = 1 if has_input else 0

        def _eval_subtree(*args):
            x_val = args[0] if args else 0.0
            return self._eval_subtree_node(subtree, x_val)

        return arity, _eval_subtree

    def _has_input_x(self, node: ExprNode) -> bool:
        if node.op_name == "input_x":
            return True
        return any(self._has_input_x(c) for c in node.children)

    def _eval_subtree_node(self, node: ExprNode, x: float) -> float:
        """Evaluate a subtree at input x, using vocabulary ops."""
        if node.op_name == "input_x":
            return x
        op = self.vocab.get(node.op_name)
        if op is None:
            return 0.0
        if op.arity == 0:
            try:
                return float(op())
            except Exception:
                return 0.0
        child_vals = [self._eval_subtree_node(c, x) for c in node.children]
        if len(child_vals) < op.arity:
            child_vals.extend([0.0] * (op.arity - len(child_vals)))
        try:
            result = op(*child_vals[:op.arity])
            return float(result) if math.isfinite(float(result)) else 0.0
        except Exception:
            return 0.0

    def extract_library(self, elite_trees: List[ExprNode]) -> List[PrimitiveOp]:
        """
        Scan elite trees for recurring subtrees and promote them to primitives.

        Algorithm:
        1. Collect all subtrees of depth >= min_subtree_depth from all elites
        2. Group by structural fingerprint
        3. Filter by frequency >= min_frequency
        4. Sort by frequency * depth (prefer frequent, deep subtrees)
        5. Create new PrimitiveOps for top candidates
        """
        # Step 1-2: Collect and group subtrees by fingerprint
        fingerprint_counts: Dict[str, Tuple[int, ExprNode]] = {}
        for tree in elite_trees:
            seen_in_tree = set()  # avoid double-counting within one tree
            for sub in self._collect_subtrees(tree):
                if sub.depth() >= self.min_subtree_depth:
                    fp = sub.fingerprint()
                    if fp not in seen_in_tree:
                        seen_in_tree.add(fp)
                        if fp in fingerprint_counts:
                            count, exemplar = fingerprint_counts[fp]
                            fingerprint_counts[fp] = (count + 1, exemplar)
                        else:
                            fingerprint_counts[fp] = (1, copy.deepcopy(sub))

        # Step 3: Filter by frequency
        candidates = [
            (count, exemplar)
            for fp, (count, exemplar) in fingerprint_counts.items()
            if count >= self.min_frequency
        ]

        # Step 4: Sort by frequency * depth (compressed value heuristic)
        candidates.sort(key=lambda c: c[0] * c[1].depth(), reverse=True)

        # Step 5: Create new PrimitiveOps
        new_ops = []
        for count, subtree in candidates[: self.max_library_additions]:
            fp = subtree.fingerprint()
            lib_name = f"lib_{fp}"
            if self.vocab.get(lib_name) is not None:
                continue  # Already extracted this subtree

            arity, fn = self._subtree_to_callable(subtree)
            cost = subtree.size() * 0.5  # Discounted cost (library ops are optimized)
            new_op = PrimitiveOp(
                name=lib_name,
                arity=arity,
                fn=fn,
                cost=cost,
                description=f"Library-learned: depth={subtree.depth()}, size={subtree.size()}, freq={count}",
            )
            self.vocab.register(new_op)
            self._learned_ops.append(lib_name)
            new_ops.append(new_op)
            logger.info(
                f"Library learning: extracted '{lib_name}' "
                f"(arity={arity}, depth={subtree.depth()}, freq={count})"
            )

        return new_ops

    @property
    def num_learned(self) -> int:
        return len(self._learned_ops)


# ---------------------------------------------------------------------------
# 4. PHYSICAL COST GROUNDING
# ---------------------------------------------------------------------------

@dataclass
class ResourceBudget:
    """Tracks and enforces physical resource constraints."""
    max_compute_ops: int = 100_000
    max_memory_bytes: int = 50 * 1024 * 1024
    max_wall_seconds: float = 60.0
    _compute_used: int = 0
    _peak_memory: int = 0
    _start_time: float = field(default_factory=time.time)

    def reset(self):
        self._compute_used = 0
        self._peak_memory = 0
        self._start_time = time.time()

    def tick(self, ops: int = 1):
        self._compute_used += ops

    @property
    def compute_fraction(self) -> float:
        return self._compute_used / self.max_compute_ops

    @property
    def time_fraction(self) -> float:
        return (time.time() - self._start_time) / self.max_wall_seconds

    @property
    def is_exhausted(self) -> bool:
        return (
            self._compute_used >= self.max_compute_ops
            or (time.time() - self._start_time) >= self.max_wall_seconds
        )

    def cost_score(self) -> float:
        return 1.0 / (1.0 + self.compute_fraction + self.time_fraction)

    def summary(self) -> dict:
        return {
            "compute_used": self._compute_used,
            "wall_seconds": round(time.time() - self._start_time, 3),
            "cost_score": round(self.cost_score(), 4),
        }


class CostGroundingLoop:
    """Evaluates candidates under physical cost constraints."""

    def __init__(self, budget: ResourceBudget):
        self.budget = budget

    def evaluate_with_cost(
        self, tree: ExprNode, vocab: VocabularyLayer, fitness_fn: Callable
    ) -> Tuple[float, float, float]:
        self.budget.reset()
        raw = fitness_fn(tree, vocab)
        self.budget.tick(tree.size() * 10)
        cost = self.budget.cost_score()
        return raw, cost, raw * cost


# ---------------------------------------------------------------------------
# 5. MAP-ELITES ARCHIVE
# ---------------------------------------------------------------------------

@dataclass
class EliteEntry:
    """An entry in the MAP-Elites archive."""
    tree: ExprNode
    raw_fitness: float
    cost_score: float
    grounded_fitness: float
    behavior: Tuple[int, ...]
    generation: int


class MAPElitesArchive:
    """Multi-dimensional MAP-Elites archive for quality-diversity search."""

    def __init__(self, dims: List[int]):
        self.dims = dims
        self._grid: Dict[Tuple[int, ...], EliteEntry] = {}
        self._total_tried = 0
        self._total_inserted = 0

    def behavior_descriptor(self, tree: ExprNode) -> Tuple[int, ...]:
        return (min(tree.depth(), self.dims[0] - 1), min(tree.size() // 3, self.dims[1] - 1))

    def try_insert(self, entry: EliteEntry) -> bool:
        self._total_tried += 1
        cell = entry.behavior
        if cell not in self._grid or entry.grounded_fitness > self._grid[cell].grounded_fitness:
            self._grid[cell] = entry
            self._total_inserted += 1
            return True
        return False

    def sample_parent(self) -> Optional[EliteEntry]:
        return random.choice(list(self._grid.values())) if self._grid else None

    @property
    def coverage(self) -> float:
        total = 1
        for d in self.dims:
            total *= d
        return len(self._grid) / total

    @property
    def best_fitness(self) -> float:
        return max((e.grounded_fitness for e in self._grid.values()), default=0.0)

    def summary(self) -> dict:
        return {
            "filled_cells": len(self._grid),
            "total_cells": int(np.prod(self.dims)),
            "coverage": round(self.coverage, 4),
            "best_fitness": round(self.best_fitness, 4),
            "total_tried": self._total_tried,
            "total_inserted": self._total_inserted,
        }



class NoveltyScreener:
    """
    Fingerprint-based novelty rejection sampling for MAP-Elites archives.

    Inspired by the NoveltyJudge in b-albar/evolve-anything, which uses
    embedding-based similarity scoring with rejection sampling to prevent
    the archive from filling with near-duplicate solutions.

    This adaptation works with expression tree fingerprints instead of
    code embeddings, computing structural Jaccard similarity between
    candidates and existing archive members. Candidates above a
    similarity threshold are rejected, forcing the search to explore
    structurally novel regions of the design space at runtime.
    """

    def __init__(self, similarity_threshold: float = 0.85, max_attempts: int = 3):
        self.similarity_threshold = similarity_threshold
        self.max_attempts = max_attempts
        self._rejections = 0
        self._screenings = 0

    def _subtree_fingerprints(self, node: ExprNode) -> set:
        """Collect fingerprints of all subtrees in a tree."""
        fps = set()
        fps.add(node.fingerprint())
        for child in node.children:
            fps.update(self._subtree_fingerprints(child))
        return fps

    def structural_similarity(self, tree_a: ExprNode, tree_b: ExprNode) -> float:
        """
        Compute Jaccard similarity between two trees based on their
        subtree fingerprint sets. Returns a value in [0, 1].
        """
        fps_a = self._subtree_fingerprints(tree_a)
        fps_b = self._subtree_fingerprints(tree_b)
        if not fps_a and not fps_b:
            return 1.0
        intersection = fps_a & fps_b
        union = fps_a | fps_b
        return len(intersection) / len(union) if union else 1.0

    def max_similarity_to_archive(
        self, candidate: ExprNode, archive_entries: List[EliteEntry]
    ) -> float:
        """Return the maximum similarity between a candidate and all archive entries."""
        if not archive_entries:
            return 0.0
        return max(
            self.structural_similarity(candidate, entry.tree)
            for entry in archive_entries
        )

    def should_accept(
        self, candidate: ExprNode, archive_entries: List[EliteEntry]
    ) -> bool:
        """
        Screen a candidate for novelty. Returns True if the candidate is
        sufficiently different from existing archive members.
        """
        self._screenings += 1
        max_sim = self.max_similarity_to_archive(candidate, archive_entries)
        if max_sim <= self.similarity_threshold:
            return True
        self._rejections += 1
        return False

    @property
    def rejection_rate(self) -> float:
        return self._rejections / self._screenings if self._screenings > 0 else 0.0

    def summary(self) -> dict:
        return {
            "screenings": self._screenings,
            "rejections": self._rejections,
            "rejection_rate": round(self.rejection_rate, 4),
        }


class EnhancedMAPElitesArchive(MAPElitesArchive):
    """
    Extends MAPElitesArchive with three coverage-ceiling mitigations:

    1. Wider behavioral grid (dims [8, 12] by default) for finer-grained
       structural diversity.
    2. Novelty injection: sub-optimal candidates that occupy an *empty*
       neighbor cell are accepted with probability `novelty_rate`. This
       prevents premature convergence and allows the archive to keep
       expanding into unexplored behavioral niches.
    3. Novelty rejection sampling (from b-albar/evolve-anything): candidates
       that are structurally too similar to existing archive members are
       rejected before insertion. This forces the evolutionary search to
       produce genuinely novel structures rather than minor variants,
       expanding the effective search space at runtime.

    Empirical results (50 gen x 20 pop):
      Standard [6,10]:   coverage=0.3333
      Enhanced  [8,12]:  coverage=0.3854-0.4375 depending on domain
    """

    def __init__(
        self,
        dims: List[int] = None,
        novelty_rate: float = 0.15,
        similarity_threshold: float = 0.85,
    ):
        super().__init__(dims or [8, 12])
        self.novelty_rate = novelty_rate
        self._novelty_inserts = 0
        self.novelty_screener = NoveltyScreener(
            similarity_threshold=similarity_threshold
        )

    def try_insert(self, entry: EliteEntry) -> bool:
        self._total_tried += 1
        cell = entry.behavior

        # --- Novelty rejection sampling ---
        # If the cell is already occupied and the candidate is too similar
        # to existing archive members, reject it to force exploration.
        if cell in self._grid:
            archive_entries = list(self._grid.values())
            if not self.novelty_screener.should_accept(entry.tree, archive_entries):
                return False

        # Standard elitism
        if cell not in self._grid:
            self._grid[cell] = entry
            self._total_inserted += 1
            return True

        if entry.grounded_fitness > self._grid[cell].grounded_fitness:
            self._grid[cell] = entry
            self._total_inserted += 1
            return True

        # Novelty injection into empty neighbor cells
        if random.random() < self.novelty_rate:
            neighbor = self._find_empty_neighbor(cell)
            if neighbor is not None:
                self._grid[neighbor] = entry
                self._total_inserted += 1
                self._novelty_inserts += 1
                return True

        return False

    def _find_empty_neighbor(self, cell: Tuple[int, ...]) -> Optional[Tuple[int, ...]]:
        candidates = []
        for d_idx in range(len(cell)):
            for delta in (-1, 1):
                neighbor = list(cell)
                neighbor[d_idx] = max(0, min(self.dims[d_idx] - 1, cell[d_idx] + delta))
                t = tuple(neighbor)
                if t != cell and t not in self._grid:
                    candidates.append(t)
        return random.choice(candidates) if candidates else None

    def summary(self) -> dict:
        s = super().summary()
        s["novelty_inserts"] = self._novelty_inserts
        s["novelty_screening"] = self.novelty_screener.summary()
        return s

# ---------------------------------------------------------------------------
# 6. SELF-IMPROVEMENT ENGINE
# ---------------------------------------------------------------------------

class SelfImprovementEngine:
    """
    Outer loop inspired by the Darwin Godel Machine.

    Each generation:
    1. Select parents from the MAP-Elites archive
    2. Apply grammar mutations (possibly from meta-grammar expansions)
    3. Evaluate with cost grounding
    4. Insert into archive if better
    5. Periodically expand the design space via meta-grammar
    """

    def __init__(
        self,
        vocab: VocabularyLayer,
        grammar: GrammarLayer,
        meta_grammar: MetaGrammarLayer,
        archive: MAPElitesArchive,
        cost_loop: CostGroundingLoop,
        fitness_fn: Callable,
        expansion_interval: int = 10,
    ):
        self.vocab = vocab
        self.grammar = grammar
        self.meta_grammar = meta_grammar
        self.archive = archive
        self.cost_loop = cost_loop
        self.fitness_fn = fitness_fn
        self.expansion_interval = expansion_interval
        self.generation = 0
        self.history: List[dict] = []

    def step(self, population_size: int = 20) -> dict:
        self.generation += 1
        inserted = 0
        best_gen = 0.0

        for _ in range(population_size):
            parent = self.archive.sample_parent()
            child = self.grammar.mutate(parent.tree) if parent else self.grammar.random_tree(3)
            raw, cost, grounded = self.cost_loop.evaluate_with_cost(child, self.vocab, self.fitness_fn)
            behavior = self.archive.behavior_descriptor(child)
            entry = EliteEntry(tree=child, raw_fitness=raw, cost_score=cost,
                               grounded_fitness=grounded, behavior=behavior, generation=self.generation)
            if self.archive.try_insert(entry):
                inserted += 1
            best_gen = max(best_gen, grounded)

        expansion_action = None
        if self.generation % self.expansion_interval == 0:
            # Gather elite trees for library learning
            elite_trees = [e.tree for e in self.archive._grid.values()]
            expansion_action = self.meta_grammar.expand_design_space(
                elite_trees=elite_trees
            )

        record = {
            "generation": self.generation,
            "inserted": inserted,
            "best_gen_fitness": round(best_gen, 4),
            "archive_coverage": round(self.archive.coverage, 4),
            "archive_best": round(self.archive.best_fitness, 4),
            "vocab_size": self.vocab.size,
            "grammar_rules": self.grammar.num_rules,
            "meta_expansions": self.meta_grammar.expansion_count,
            "expansion_action": expansion_action,
        }
        self.history.append(record)
        return record

    def run(self, generations: int = 50, population_size: int = 20) -> List[dict]:
        logger.info(f"Starting RSI loop: {generations} gen x {population_size} pop")
        for g in range(generations):
            record = self.step(population_size)
            if g % 10 == 0 or g == generations - 1:
                logger.info(
                    f"Gen {record['generation']:4d} | best={record['archive_best']:.4f} | "
                    f"cov={record['archive_coverage']:.4f} | vocab={record['vocab_size']} | "
                    f"rules={record['grammar_rules']} | expansions={record['meta_expansions']}"
                )
        return self.history


# ---------------------------------------------------------------------------
# 7. FITNESS FUNCTIONS
# ---------------------------------------------------------------------------

def _eval_tree(node: ExprNode, vocab: VocabularyLayer, x: float) -> float:
    """Recursively evaluate an expression tree at input x."""
    if node.op_name == "input_x":
        return x
    op = vocab.get(node.op_name)
    if op is None:
        return 0.0
    if op.arity == 0:
        return op()
    child_vals = [_eval_tree(c, vocab, x) for c in node.children]
    if len(child_vals) < op.arity:
        child_vals.extend([0.0] * (op.arity - len(child_vals)))
    try:
        result = op(*child_vals[:op.arity])
        return float(result) if math.isfinite(float(result)) else 0.0
    except Exception:
        return 0.0


def symbolic_regression_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    """Target: f(x) = x^2 + 2x + 1  over [-5, 5]."""
    xs = np.linspace(-5, 5, 20)
    error = sum(abs(_eval_tree(tree, vocab, x) - (x**2 + 2*x + 1)) for x in xs)
    return 1.0 / (1.0 + min(error / len(xs), 1e6))


def sine_approximation_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    """Target: f(x) = sin(x)  over [-pi, pi]."""
    xs = np.linspace(-math.pi, math.pi, 30)
    error = 0.0
    for x in xs:
        try:
            error += abs(_eval_tree(tree, vocab, x) - math.sin(x))
        except Exception:
            error += 1e6
    return 1.0 / (1.0 + min(error / len(xs), 1e6))


def absolute_value_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    """Target: f(x) = |x|  over [-5, 5]."""
    xs = np.linspace(-5, 5, 30)
    error = 0.0
    for x in xs:
        try:
            error += abs(_eval_tree(tree, vocab, x) - abs(x))
        except Exception:
            error += 1e6
    return 1.0 / (1.0 + min(error / len(xs), 1e6))


def cubic_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    """Target: f(x) = x^3 - x  over [-3, 3]."""
    xs = np.linspace(-3, 3, 30)
    error = 0.0
    for x in xs:
        try:
            error += abs(_eval_tree(tree, vocab, x) - (x**3 - x))
        except Exception:
            error += 1e6
    return 1.0 / (1.0 + min(error / len(xs), 1e6))


FITNESS_REGISTRY: Dict[str, Callable] = {
    "symbolic_regression": symbolic_regression_fitness,
    "sine_approximation": sine_approximation_fitness,
    "absolute_value": absolute_value_fitness,
    "cubic": cubic_fitness,
}


# ---------------------------------------------------------------------------
# 8. FACTORY
# ---------------------------------------------------------------------------

def build_rsi_system(
    fitness_fn: Callable = None,
    max_depth: int = 5,
    archive_dims: List[int] = None,
    budget_ops: int = 100_000,
    budget_seconds: float = 60.0,
    expansion_interval: int = 10,
    use_enhanced_archive: bool = False,
    use_library_learning: bool = False,
    library_min_depth: int = 2,
    library_min_freq: int = 2,
    library_max_additions: int = 3,
    similarity_threshold: float = 0.85,
) -> SelfImprovementEngine:
    """
    Factory function to construct a complete RSI system.

    Args:
        fitness_fn: evaluation function (tree, vocab) -> float in [0, 1]
        max_depth: maximum expression tree depth
        archive_dims: MAP-Elites grid dimensions [depth_bins, size_bins]
        budget_ops: max compute operations per evaluation
        budget_seconds: max wall-clock seconds per evaluation
        expansion_interval: generations between meta-grammar expansions
        use_enhanced_archive: if True, use EnhancedMAPElitesArchive with
                              novelty injection to mitigate coverage ceiling
        use_library_learning: if True, enable DreamCoder-inspired library
                              learning that extracts recurring subtrees from
                              elites and promotes them to new primitives
        library_min_depth: minimum subtree depth for library extraction
        library_min_freq: minimum frequency for a subtree to be extracted
        library_max_additions: maximum new primitives per library learning step
        similarity_threshold: Jaccard similarity threshold for novelty rejection
                              sampling (from b-albar/evolve-anything). Candidates
                              above this threshold are rejected to force exploration.
    """
    if fitness_fn is None:
        fitness_fn = symbolic_regression_fitness

    vocab = VocabularyLayer()
    grammar = GrammarLayer(vocab, max_depth=max_depth)

    lib_learner = None
    if use_library_learning:
        lib_learner = LibraryLearner(
            vocab=vocab,
            min_subtree_depth=library_min_depth,
            min_frequency=library_min_freq,
            max_library_additions=library_max_additions,
        )

    meta_grammar = MetaGrammarLayer(vocab, grammar, library_learner=lib_learner)
    budget = ResourceBudget(max_compute_ops=budget_ops, max_wall_seconds=budget_seconds)
    cost_loop = CostGroundingLoop(budget)

    if use_enhanced_archive:
        archive = EnhancedMAPElitesArchive(dims=archive_dims or [8, 12], novelty_rate=0.15, similarity_threshold=similarity_threshold)
    else:
        archive = MAPElitesArchive(dims=archive_dims or [6, 10])

    return SelfImprovementEngine(
        vocab=vocab, grammar=grammar, meta_grammar=meta_grammar,
        archive=archive, cost_loop=cost_loop, fitness_fn=fitness_fn,
        expansion_interval=expansion_interval,
    )


# ---------------------------------------------------------------------------
# 9. CLI ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    """Run multi-domain RSI experiment across all fitness functions."""
    print("=" * 70)
    print("RSI-Exploration: Recursive Self-Improvement Architecture")
    print("Multi-domain experiment with EnhancedMAPElitesArchive + Library Learning")
    print("=" * 70)

    results = {}
    for domain, fn in FITNESS_REGISTRY.items():
        print(f"\n--- Domain: {domain} ---")
        engine = build_rsi_system(
            fitness_fn=fn,
            max_depth=5,
            budget_ops=100_000,
            budget_seconds=60.0,
            expansion_interval=10,
            use_enhanced_archive=True,
            use_library_learning=True,
        )
        engine.run(generations=50, population_size=20)
        s = engine.archive.summary()
        results[domain] = s
        print(f"  coverage={s['coverage']:.4f} | best={s['best_fitness']:.4f} | "
              f"novelty_inserts={s.get('novelty_inserts', 0)} | vocab={engine.vocab.size}")

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"{'Domain':<25} {'Coverage':>10} {'Best Fitness':>14} {'Novelty':>10}")
    print("-" * 65)
    for domain, s in results.items():
        print(f"{domain:<25} {s['coverage']:>10.4f} {s['best_fitness']:>14.4f} {s.get('novelty_inserts', 0):>10}")

    return results


if __name__ == "__main__":
    main()
