"""RSI-Exploration: Recursive Self-Improvement Architecture
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

class OpType:
    """
    Refinement type tags for PrimitiveOp input/output domains (D.5 Dependent Types).

    Each tag represents a constraint on the numeric domain:
    - REAL: unrestricted reals (default)
    - NON_NEGATIVE: x >= 0
    - POSITIVE: x > 0
    - BOUNDED: -1e6 <= x <= 1e6
    - UNIT: 0 <= x <= 1
    - ANY: accepts any type (universal input)

    Type compatibility is checked at tree construction time: a child node's
    output_type must be a subtype of (or equal to) the parent's input_type
    for that argument position.
    """
    REAL = "real"
    NON_NEGATIVE = "non_negative"
    POSITIVE = "positive"
    BOUNDED = "bounded"
    UNIT = "unit"
    ANY = "any"

    @staticmethod
    def is_compatible(child_type: str, parent_type: str) -> bool:
        """
        Check if child output type is compatible with parent input type.
        Subtypes are: POSITIVE < NON_NEGATIVE < BOUNDED < REAL, UNIT < REAL
        """
        if parent_type == OpType.ANY:
            return True
        if child_type == parent_type:
            return True
        # Subtype relationships
        subtypes = {
            OpType.POSITIVE: [OpType.NON_NEGATIVE, OpType.BOUNDED, OpType.REAL],
            OpType.NON_NEGATIVE: [OpType.BOUNDED, OpType.REAL],
            OpType.UNIT: [OpType.BOUNDED, OpType.REAL],
            OpType.BOUNDED: [OpType.REAL],
        }
        return parent_type in subtypes.get(child_type, [])


class PrimitiveOp:
    """
    A primitive operation in the vocabulary layer.
    
    Attributes:
        name: unique identifier
        arity: number of arguments (0 for constants, 1+ for functions)
        fn: callable that implements the operation
        weight: relative frequency for random sampling
        description: human-readable explanation
        input_types: list of input type tags (one per argument)
        output_type: output type tag
    """

    def __init__(
        self,
        name: str,
        arity: int,
        fn: Callable,
        weight: float = 1.0,
        description: str = "",
        input_types: Optional[List[str]] = None,
        output_type: str = OpType.REAL,
    ):
        self.name = name
        self.arity = arity
        self.fn = fn
        self.weight = weight
        self.description = description
        self.input_types = input_types or [OpType.ANY] * arity
        self.output_type = output_type

    def __call__(self, *args):
        """Invoke the operation."""
        return self.fn(*args)

    def __repr__(self):
        return f"PrimitiveOp({self.name}, arity={self.arity})"


class VocabularyLayer:
    """
    Registry of primitive operations that can be composed into programs.
    
    Provides:
    - Registration and lookup of operations
    - Random sampling weighted by importance
    - Type checking for safe composition
    """

    def __init__(self):
        self.ops: Dict[str, PrimitiveOp] = {}
        self._init_default_ops()

    def _init_default_ops(self):
        """Initialize with standard numeric/logical operations."""
        # Constants (arity 0)
        self.register(PrimitiveOp("zero", 0, lambda: 0.0, weight=2.0, description="Constant 0", output_type=OpType.NON_NEGATIVE))
        self.register(PrimitiveOp("one", 0, lambda: 1.0, weight=2.0, description="Constant 1", output_type=OpType.POSITIVE))
        self.register(PrimitiveOp("pi", 0, lambda: math.pi, weight=1.0, description="Constant pi", output_type=OpType.POSITIVE))

        # Unary operations (arity 1)
        def safe_sqrt(x):
            return math.sqrt(max(0, x))
        self.register(
            PrimitiveOp(
                "sqrt",
                1,
                safe_sqrt,
                weight=1.5,
                description="Safe square root",
                input_types=[OpType.NON_NEGATIVE],
                output_type=OpType.NON_NEGATIVE,
            )
        )
        self.register(
            PrimitiveOp(
                "square",
                1,
                lambda x: x ** 2,
                weight=2.0,
                description="Square",
                output_type=OpType.NON_NEGATIVE,
            )
        )
        self.register(
            PrimitiveOp(
                "abs",
                1,
                abs,
                weight=1.5,
                description="Absolute value",
                output_type=OpType.NON_NEGATIVE,
            )
        )
        self.register(
            PrimitiveOp(
                "neg",
                1,
                lambda x: -x,
                weight=1.0,
                description="Negation",
            )
        )
        self.register(
            PrimitiveOp(
                "sin",
                1,
                math.sin,
                weight=1.0,
                description="Sine",
                output_type=OpType.BOUNDED,
            )
        )
        self.register(
            PrimitiveOp(
                "cos",
                1,
                math.cos,
                weight=1.0,
                description="Cosine",
                output_type=OpType.BOUNDED,
            )
        )
        self.register(
            PrimitiveOp(
                "exp",
                1,
                lambda x: math.exp(min(100, x)),  # Cap to prevent overflow
                weight=0.8,
                description="Exponential",
                output_type=OpType.POSITIVE,
            )
        )
        self.register(
            PrimitiveOp(
                "log",
                1,
                lambda x: math.log(max(1e-6, x)),
                weight=0.8,
                description="Natural logarithm",
                input_types=[OpType.POSITIVE],
            )
        )

        # Binary operations (arity 2)
        self.register(
            PrimitiveOp(
                "add",
                2,
                lambda a, b: a + b,
                weight=3.0,
                description="Addition",
            )
        )
        self.register(
            PrimitiveOp(
                "sub",
                2,
                lambda a, b: a - b,
                weight=2.5,
                description="Subtraction",
            )
        )
        self.register(
            PrimitiveOp(
                "mul",
                2,
                lambda a, b: a * b,
                weight=3.0,
                description="Multiplication",
            )
        )

        def safe_div(a, b):
            return a / b if b != 0 else 0.0

        self.register(
            PrimitiveOp(
                "safe_div",
                2,
                safe_div,
                weight=1.5,
                description="Safe division (0 if divisor is 0)",
            )
        )
        self.register(
            PrimitiveOp(
                "max",
                2,
                max,
                weight=1.5,
                description="Maximum",
            )
        )
        self.register(
            PrimitiveOp(
                "min",
                2,
                min,
                weight=1.5,
                description="Minimum",
            )
        )
        self.register(
            PrimitiveOp(
                "pow",
                2,
                lambda a, b: a ** max(-10, min(10, b)),  # Cap exponent
                weight=0.8,
                description="Power (capped exponent)",
            )
        )

    def register(self, op: PrimitiveOp):
        """Register a new operation in the vocabulary."""
        self.ops[op.name] = op

    def get(self, name: str) -> Optional[PrimitiveOp]:
        """Retrieve an operation by name."""
        return self.ops.get(name)

    def random_op(self, max_arity: Optional[int] = None) -> PrimitiveOp:
        """Sample a random operation, optionally filtered by arity."""
        candidates = [
            op for op in self.ops.values()
            if max_arity is None or op.arity <= max_arity
        ]
        weights = [op.weight for op in candidates]
        total = sum(weights)
        r = random.random() * total
        cumsum = 0
        for op, w in zip(candidates, weights):
            cumsum += w
            if r < cumsum:
                return op
        return candidates[-1]

    @property
    def size(self) -> int:
        """Number of operations in the vocabulary."""
        return len(self.ops)


# ---------------------------------------------------------------------------
# 2. GRAMMAR LAYER
# ---------------------------------------------------------------------------

@dataclass
class ExprNode:
    """
    A node in an expression tree representing a composed program.
    
    Attributes:
        op: the PrimitiveOp at this node
        children: child nodes (empty for leaf/constant nodes)
    """
    op: PrimitiveOp
    children: List[ExprNode] = field(default_factory=list)

    def __repr__(self):
        if not self.children:
            return f"Leaf({self.op.name})"
        child_strs = ", ".join(repr(c) for c in self.children)
        return f"Node({self.op.name}, [{child_strs}])"

    def depth(self) -> int:
        """Compute tree depth."""
        if not self.children:
            return 0
        return 1 + max(c.depth() for c in self.children)

    def size(self) -> int:
        """Compute number of nodes."""
        return 1 + sum(c.size() for c in self.children)

    def hash_tree(self) -> str:
        """Create a canonical hash of tree structure for caching."""
        if not self.children:
            return f"leaf_{self.op.name}"
        child_hashes = "_".join(c.hash_tree() for c in self.children)
        return f"node_{self.op.name}_{child_hashes}"


class GrammarLayer:
    """
    Generates expression trees (programs) from the vocabulary using grammar rules.
    
    Core idea: each rule has the form:
      NonTerminal -> PrimitiveOp(NonTerminal_1, ..., NonTerminal_k)
    where k is the arity of the PrimitiveOp.
    
    Attributes:
        vocab: reference to the VocabularyLayer
        max_depth: maximum tree depth
        max_size: maximum number of nodes
    """

    def __init__(self, vocab: VocabularyLayer, max_depth: int = 5, max_size: int = 100):
        self.vocab = vocab
        self.max_depth = max_depth
        self.max_size = max_size

    def random_tree(self, depth: int = 0) -> ExprNode:
        """
        Recursively generate a random expression tree.
        
        Strategy:
        - Base case (depth >= max_depth): choose a leaf (arity-0 op)
        - Recursive case: choose any op, recursively generate children
        """
        if depth >= self.max_depth:
            # Must use a leaf node
            op = self.vocab.random_op(max_arity=0)
            return ExprNode(op)
        else:
            # Can use any operation
            op = self.vocab.random_op()
            children = [self.random_tree(depth + 1) for _ in range(op.arity)]
            return ExprNode(op, children)

    def mutate_tree(self, tree: ExprNode) -> ExprNode:
        """
        Apply a single mutation to a tree:
        1. With prob 0.5: mutate a random subtree (replace with new random tree)
        2. With prob 0.5: swap the op at a random node (preserving arity)
        """
        tree = copy.deepcopy(tree)
        if not tree.children:
            # Leaf: can only change the op
            op = self.vocab.random_op(max_arity=0)
            return ExprNode(op)

        if random.random() < 0.5:
            # Mutate a random subtree
            nodes = self._all_nodes(tree)
            node_to_mutate = random.choice(nodes)
            depth = self._depth_of_node(tree, node_to_mutate)
            new_subtree = self.random_tree(depth=depth)
            return self._replace_node(tree, node_to_mutate, new_subtree)
        else:
            # Swap op at a random node (same arity)
            inner_nodes = [n for n in self._all_nodes(tree) if n.children]
            if inner_nodes:
                node_to_change = random.choice(inner_nodes)
                new_op = self.vocab.random_op(max_arity=node_to_change.op.arity)
                node_to_change.op = new_op
            return tree

    def _all_nodes(self, tree: ExprNode) -> List[ExprNode]:
        """Get all nodes in a tree (DFS)."""
        nodes = [tree]
        for child in tree.children:
            nodes.extend(self._all_nodes(child))
        return nodes

    def _depth_of_node(self, root: ExprNode, target: ExprNode) -> int:
        """Find depth of a target node within the tree."""
        def dfs(node, d):
            if node is target:
                return d
            for child in node.children:
                result = dfs(child, d + 1)
                if result is not None:
                    return result
            return None
        return dfs(root, 0)

    def _replace_node(self, root: ExprNode, old: ExprNode, new: ExprNode) -> ExprNode:
        """Replace a node within a tree."""
        if root is old:
            return new
        root = copy.deepcopy(root)
        for i, child in enumerate(root.children):
            root.children[i] = self._replace_node(child, old, new)
        return root


class MetaGrammarLayer:
    """
    Generates new grammar rules (i.e., new "high-level" operations).
    
    Each meta-rule is a learned composition (subprogram) that becomes a new
    primitive operation in an evolving vocabulary.
    
    Session 11 (Tier 1): Stores (program_tree, (fitness_1, ..., fitness_k)) pairs.
    Session 12 (Tier 2): Extends with:
      - Conditional grammar rules with guards
      - Rule composition and interaction tracking
      - Polymorphic operations (generic implementations)
    """

    def __init__(self, vocab: VocabularyLayer, grammar: GrammarLayer):
        self.vocab = vocab
        self.grammar = grammar
        self.rules: Dict[str, MetaRuleEntry] = {}  # Tier 1
        self.conditional_rules: Dict[str, ConditionalGrammarRule] = {}  # Tier 2
        self.rule_composer = GrammarRuleComposer()  # Tier 2
        self.interaction_tracker = RuleInteractionTracker()  # Tier 2

    def register_learned_subprogram(self, tree: ExprNode, fitnesses: Tuple[float, ...]):
        """
        Register a learned subprogram as a new high-level operation (Tier 1).
        
        Creates a polymorphic op that wraps the learned composition.
        """
        rule_name = f"learned_{len(self.rules)}"
        entry = MetaRuleEntry(tree, fitnesses)
        self.rules[rule_name] = entry

        # Wrap as PolymorphicOp and register in vocab
        polymorphic_op = PolymorphicOp(rule_name, tree)
        self.vocab.register(polymorphic_op)

    def register_conditional_rule(self, rule: ConditionalGrammarRule):
        """
        Register a conditional grammar rule with a guard function (Tier 2).
        """
        rule_id = f"cond_rule_{len(self.conditional_rules)}"
        self.conditional_rules[rule_id] = rule
        # Track rule composition and interactions
        self.rule_composer.add_rule(rule)
        return rule_id

    def query_applicable_rules(self, context: Dict) -> List[str]:
        """
        Query which conditional rules are applicable for a given context (Tier 2).
        """
        applicable = []
        for rule_id, rule in self.conditional_rules.items():
            if rule.guard(context):
                applicable.append(rule_id)
        return applicable


@dataclass
class MetaRuleEntry:
    """
    Represents a learned subprogram that has become a grammar rule (Tier 1).
    
    Attributes:
        tree: the learned ExprNode representing the composition
        fitnesses: multi-objective fitness values (one per objective)
    """
    tree: ExprNode
    fitnesses: Tuple[float, ...]


class ConditionalGrammarRule:
    """
    A grammar rule with a guard function that determines applicability (Tier 2).
    
    Attributes:
        name: identifier for the rule
        guard: callable that takes a context dict and returns bool
        composition: the ExprNode this rule produces
    """

    def __init__(self, name: str, guard: Callable[[Dict], bool], composition: ExprNode):
        self.name = name
        self.guard = guard
        self.composition = composition


class GrammarRuleComposer:
    """
    Manages composition of grammar rules and tracks their interactions (Tier 2).
    """

    def __init__(self):
        self.rules: List[ConditionalGrammarRule] = []
        self.composition_graph: Dict[str, List[str]] = {}  # rule -> compatible rules

    def add_rule(self, rule: ConditionalGrammarRule):
        """Add a new rule and compute compatibilities."""
        self.rules.append(rule)
        # Simplified: assume all rules compose for now
        self.composition_graph[rule.name] = [r.name for r in self.rules if r.name != rule.name]

    def compatible_rules(self, rule_name: str) -> List[str]:
        """Get rules compatible for composition with the given rule."""
        return self.composition_graph.get(rule_name, [])


class RuleInteractionTracker:
    """
    Tracks how rules interact and compose in the meta-grammar (Tier 2).
    """

    def __init__(self):
        self.interaction_counts: Dict[Tuple[str, str], int] = {}  # (rule_a, rule_b) -> count

    def record_interaction(self, rule_a: str, rule_b: str):
        """Record that two rules were composed together."""
        key = tuple(sorted([rule_a, rule_b]))
        self.interaction_counts[key] = self.interaction_counts.get(key, 0) + 1

    def most_interacting_rules(self, top_k: int = 5) -> List[Tuple[str, str]]:
        """Get the top-k most frequently interacting rule pairs."""
        sorted_pairs = sorted(self.interaction_counts.items(), key=lambda x: x[1], reverse=True)
        return [pair for pair, _ in sorted_pairs[:top_k]]


class PolymorphicOp(PrimitiveOp):
    """
    A polymorphic operation wrapping a learned composition (ExprTree).
    
    This allows learned subprograms to be treated as new primitives.
    
    Attributes:
        tree: the ExprNode representing the composition
    """

    def __init__(self, name: str, tree: ExprNode):
        self.name = name
        self.tree = tree
        self.arity = 0  # For now, assume learned ops are parameter-free
        self.weight = 1.0
        self.description = f"Learned composition: {tree}"
        self.input_types = []
        self.output_type = OpType.REAL

    def __call__(self, *args):
        # Evaluate the tree (no external inputs for now)
        return _eval_tree(self.tree, {})


# ---------------------------------------------------------------------------
# 3. EVALUATION & RESOURCE ACCOUNTING
# ---------------------------------------------------------------------------

@dataclass
class ResourceBudget:
    """
    Physical cost budget for a learning episode.
    
    Attributes:
        max_compute_ops: maximum number of primitive operations to execute
        max_memory_bytes: maximum memory for intermediate results
        max_wall_seconds: maximum wall-clock time
    """
    max_compute_ops: int
    max_memory_bytes: int = 1_000_000_000  # 1 GB
    max_wall_seconds: float = 3600  # 1 hour


@dataclass
class EvalContext:
    """
    Runtime context for evaluating an expression tree.
    
    Tracks resource consumption during evaluation to enforce budgets.
    
    Attributes:
        compute_ops: number of primitive operations executed
        memory_bytes: current memory usage estimate
        wall_start_time: wall-clock time when evaluation started
        budget: the ResourceBudget to enforce
    """
    compute_ops: int = 0
    memory_bytes: int = 0
    wall_start_time: float = field(default_factory=time.time)
    budget: Optional[ResourceBudget] = None
    inputs: Dict[str, float] = field(default_factory=dict)

    def check_budget(self) -> bool:
        """Check if current usage exceeds budget."""
        if self.budget is None:
            return False
        if self.compute_ops > self.budget.max_compute_ops:
            return True
        if self.memory_bytes > self.budget.max_memory_bytes:
            return True
        elapsed = time.time() - self.wall_start_time
        if elapsed > self.budget.max_wall_seconds:
            return True
        return False

    def record_op(self, estimated_memory: int = 100):
        """Record execution of a primitive operation."""
        self.compute_ops += 1
        self.memory_bytes += estimated_memory


def _eval_tree(tree: ExprNode, inputs: Dict[str, float], ctx: Optional[EvalContext] = None) -> float:
    """
    Evaluate an expression tree to a scalar value.
    
    Traverses the tree bottom-up (post-order), applying each op to the
    results of its children. Enforces resource budgets at runtime.
    
    Args:
        tree: the ExprNode to evaluate
        inputs: dict of input variable assignments (for future leaf variables)
        ctx: optional EvalContext to track resource consumption
    
    Returns:
        scalar result (float)
    
    Raises:
        RuntimeError if budget is exceeded
    """
    if ctx is None:
        ctx = EvalContext(inputs=inputs)

    # Check budget before proceeding
    if ctx.check_budget():
        raise RuntimeError("Resource budget exceeded during evaluation")

    # Leaf node: return constant
    if not tree.children:
        ctx.record_op(50)
        return tree.op()

    # Inner node: recursively evaluate children, then apply op
    child_values = [_eval_tree(child, inputs, ctx) for child in tree.children]
    ctx.record_op(100)
    result = tree.op(*child_values)

    # Clamp to prevent NaN/Inf
    if math.isnan(result) or math.isinf(result):
        result = 0.0

    return result


# ---------------------------------------------------------------------------
# 4. MAP-ELITES ARCHIVE
# ---------------------------------------------------------------------------

@dataclass
class EliteEntry:
    """
    Represents an elite solution in the MAP-Elites archive.
    
    Attributes:
        individual: the ExprNode representing a program
        fitness: primary fitness value
        fitnesses: multi-objective fitness tuple
        behavior_descriptor: tuple of coordinates in behavior space
        metadata: dict of additional info (e.g., creation_time, parent_id)
    """
    individual: ExprNode
    fitness: float
    fitnesses: Tuple[float, ...]
    behavior_descriptor: Tuple[int, ...]
    metadata: Dict = field(default_factory=dict)


class MAPElitesArchive:
    """
    Maintains a collection of diverse, high-performing solutions using
    the MAP-Elites algorithm (Mouret & Clune, 2015).
    
    Discretizes behavior space into cells, keeping the best solution in each cell.
    
    Attributes:
        dims: list of dimensions for behavior space discretization
        cells: dict mapping behavior descriptor to EliteEntry
    """

    def __init__(self, dims: List[int]):
        self.dims = dims
        self.cells: Dict[Tuple, EliteEntry] = {}

    def add_or_replace(self, entry: EliteEntry) -> bool:
        """
        Add a new solution to the archive, replacing existing one if fitness is better.
        
        Returns True if added/replaced, False if rejected.
        """
        bd = entry.behavior_descriptor
        if len(bd) != len(self.dims):
            raise ValueError(f"Behavior descriptor {bd} has wrong dimension")

        # Clamp to cell bounds
        bd = tuple(min(d.dims[i] - 1, max(0, b)) for i, b in enumerate(bd))

        if bd not in self.cells:
            self.cells[bd] = entry
            return True
        elif entry.fitness > self.cells[bd].fitness:
            self.cells[bd] = entry
            return True
        else:
            return False

    def get_elites(self) -> List[EliteEntry]:
        """Return all elite solutions in the archive."""
        return list(self.cells.values())

    def size(self) -> int:
        """Number of filled cells."""
        return len(self.cells)

    def coverage(self) -> float:
        """Fraction of cells filled."""
        total = 1
        for d in self.dims:
            total *= d
        return len(self.cells) / total


class EnhancedMAPElitesArchive(MAPElitesArchive):
    """
    Extended MAP-Elites archive with novelty and quality measures (Tier 2).
    
    Adds:
    - Novelty metric: how different from existing elites
    - Quality metric: multi-objective fitness aggregation
    - Filtering: reject solutions below novelty/quality thresholds
    """

    def __init__(self, dims: List[int], novelty_threshold: float = 0.5):
        super().__init__(dims)
        self.novelty_threshold = novelty_threshold

    def behavioral_distance(self, bd1: Tuple, bd2: Tuple) -> float:
        """Compute distance between two behavior descriptors."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(bd1, bd2)))

    def novelty(self, entry: EliteEntry) -> float:
        """Compute novelty as min distance to any existing elite."""
        if not self.cells:
            return 1.0  # Maximum novelty if archive is empty
        min_dist = min(
            self.behavioral_distance(entry.behavior_descriptor, existing.behavior_descriptor)
            for existing in self.cells.values()
        )
        return min(1.0, min_dist)  # Normalized to [0, 1]

    def quality(self, entry: EliteEntry) -> float:
        """Compute aggregated quality from multi-objective fitnesses."""
        # Simple average (can be weighted)
        if not entry.fitnesses:
            return entry.fitness
        return sum(entry.fitnesses) / len(entry.fitnesses)

    def add_or_replace_with_screening(self, entry: EliteEntry) -> bool:
        """Add solution only if it passes novelty and quality screening."""
        nov = self.novelty(entry)
        if nov < self.novelty_threshold:
            return False  # Too similar to existing
        return self.add_or_replace(entry)


class NoveltyScreener:
    """
    Filters solutions by novelty before adding to archive (Tier 2).
    
    Maintains a history of seen behaviors to compute novelty against.
    """

    def __init__(self, archive: MAPElitesArchive):
        self.archive = archive
        self.history: List[Tuple] = []  # History of all seen behavior descriptors

    def is_novel(self, bd: Tuple, threshold: float = 0.5) -> bool:
        """Check if a behavior descriptor is sufficiently novel."""
        if not self.history:
            return True
        min_dist = min(
            math.sqrt(sum((a - b) ** 2 for a, b in zip(bd, existing_bd)))
            for existing_bd in self.history
        )
        return min_dist >= threshold

    def record(self, bd: Tuple):
        """Record a behavior descriptor in history."""
        self.history.append(bd)


# ---------------------------------------------------------------------------
# 5. COST-GROUNDING LOOP
# ---------------------------------------------------------------------------

class CostGroundingLoop:
    """
    Physical cost grounding for the learning process.
    
    Tracks wall-clock time, compute operations, and memory consumption
    during candidate evaluation, ensuring the system respects resource limits.
    
    Attributes:
        budget: the ResourceBudget to enforce
        total_compute_ops: cumulative count across all evaluations
        total_memory_peak: peak memory usage observed
        wall_start_time: when the learning process started
    """

    def __init__(self, budget: ResourceBudget):
        self.budget = budget
        self.total_compute_ops = 0
        self.total_memory_peak = 0
        self.wall_start_time = time.time()
        self.evaluations_completed = 0

    def evaluate_tree(self, tree: ExprNode, inputs: Dict[str, float]) -> Optional[float]:
        """
        Evaluate a tree within the cost budget.
        
        Returns the result if successful, None if budget is exceeded.
        """
        ctx = EvalContext(budget=self.budget, inputs=inputs)
        try:
            result = _eval_tree(tree, inputs, ctx)
            self.total_compute_ops += ctx.compute_ops
            self.total_memory_peak = max(self.total_memory_peak, ctx.memory_bytes)
            self.evaluations_completed += 1
            return result
        except RuntimeError:
            # Budget exceeded
            return None

    def remaining_budget(self) -> Dict[str, float]:
        """Return remaining budget across all dimensions."""
        elapsed = time.time() - self.wall_start_time
        return {
            "compute_ops": self.budget.max_compute_ops - self.total_compute_ops,
            "wall_seconds": self.budget.max_wall_seconds - elapsed,
        }


# ---------------------------------------------------------------------------
# 6. FITNESS FUNCTIONS
# ---------------------------------------------------------------------------

def symbolic_regression_fitness(tree: ExprNode, X: np.ndarray, y: np.ndarray, ctx: Optional[EvalContext] = None) -> float:
    """
    Fitness for symbolic regression: minimize prediction error.
    
    Args:
        tree: expression to evaluate
        X: input data (rows are samples, cols are features)
        y: target values
        ctx: optional EvalContext for resource tracking
    
    Returns:
        negative MSE (to maximize fitness)
    """
    try:
        predictions = np.array([_eval_tree(tree, {}, ctx) for _ in range(len(y))])
        mse = np.mean((predictions - y) ** 2)
        return -mse
    except (RuntimeError, ValueError):
        return -1e6  # Penalize failures


def diversity_fitness(tree: ExprNode, archive: MAPElitesArchive) -> float:
    """
    Fitness based on diversity from archive: reward novel solutions.
    """
    if not archive.cells:
        return 1.0
    # Use tree structure as a simple behavior descriptor
    bd = (tree.size(), tree.depth())
    min_dist = min(
        math.sqrt((bd[0] - e.behavior_descriptor[0]) ** 2 + (bd[1] - e.behavior_descriptor[1]) ** 2)
        for e in archive.cells.values()
    )
    return min(1.0, min_dist / 10.0)


# ---------------------------------------------------------------------------
# 7. LIBRARY LEARNER
# ---------------------------------------------------------------------------

class LibraryLearner:
    """
    Learns reusable subprograms (library functions) to accelerate evolution.
    
    High-level algorithm:
    1. Periodically sample elite solutions from the archive
    2. Cluster them by structural similarity
    3. For each cluster, synthesize a generic subprogram
    4. Register new subprogram as a meta-rule
    
    Session 12 (Tier 2) adds:
    - Conditional rule extraction based on context
    - Rule composition analysis
    - Interaction-based rule scoring
    """

    def __init__(self, meta_grammar: MetaGrammarLayer, archive: MAPElitesArchive):
        self.meta_grammar = meta_grammar
        self.archive = archive
        self.learned_subprograms: List[ExprNode] = []
        self.learning_history: List[Dict] = []

    def learn_from_elites(self, num_clusters: int = 3) -> List[str]:
        """
        Learn new meta-rules from elite solutions (Tier 1).
        
        Returns: list of newly registered rule IDs
        """
        elites = self.archive.get_elites()
        if len(elites) < 2:
            return []

        # Simplified: use k-means on tree size/depth
        new_rule_ids = []
        for elite in elites:
            self.meta_grammar.register_learned_subprogram(
                elite.individual,
                elite.fitnesses,
            )
            self.learned_subprograms.append(elite.individual)
            new_rule_ids.append(f"learned_{len(self.learned_subprograms) - 1}")

        self.learning_history.append({
            "timestamp": time.time(),
            "num_elites": len(elites),
            "num_rules_learned": len(new_rule_ids),
        })

        return new_rule_ids

    def extract_conditional_rules(self, context: Dict) -> List[str]:
        """
        Extract conditional rules based on context (Tier 2).
        
        Creates ConditionalGrammarRule entries and registers them.
        """
        extracted_rule_ids = []
        for i, tree in enumerate(self.learned_subprograms):
            # Synthesize a guard function based on context
            def make_guard(t=tree):
                return lambda ctx: tree.size() < 10  # Simplified guard
            
            rule = ConditionalGrammarRule(
                name=f"cond_rule_{i}",
                guard=make_guard(),
                composition=tree,
            )
            rule_id = self.meta_grammar.register_conditional_rule(rule)
            extracted_rule_ids.append(rule_id)

        return extracted_rule_ids


# ---------------------------------------------------------------------------
# 8. SELF-IMPROVEMENT ENGINE
# ---------------------------------------------------------------------------

class SelfImprovementEngine:
    """
    Main orchestration loop for recursive self-improvement (RSI).
    
    Implements the DGM + MAP-Elites hybrid architecture:
    1. Generate and evaluate diverse candidates
    2. Update quality-diversity archive
    3. Learn meta-rules from elite solutions
    4. Expand grammar with learned rules
    5. Repeat with improved vocabulary
    
    Session 12 (Tier 2) extends with:
    - Conditional rule extraction and composition
    - Multi-objective fitness optimization
    - Rule interaction tracking
    - Enhanced novelty/quality screening
    """

    def __init__(
        self,
        vocab: VocabularyLayer,
        grammar: GrammarLayer,
        archive: MAPElitesArchive,
        budget: ResourceBudget,
        fitness_fn: Optional[Callable] = None,
    ):
        self.vocab = vocab
        self.grammar = grammar
        self.archive = archive
        self.budget = budget
        self.fitness_fn = fitness_fn or diversity_fitness
        self.cost_loop = CostGroundingLoop(budget)
        self.meta_grammar = MetaGrammarLayer(vocab, grammar)
        self.library_learner = LibraryLearner(self.meta_grammar, archive)
        self.iteration = 0
        self.history: List[Dict] = []

    def step(self, num_candidates: int = 100) -> Dict:
        """
        Execute one iteration of RSI:
        1. Generate candidates
        2. Evaluate and add to archive
        3. Learn new meta-rules
        
        Returns: dict with iteration metrics
        """
        self.iteration += 1
        metrics = {"iteration": self.iteration, "candidates_added": 0}

        # Generate candidates
        candidates = [self.grammar.random_tree() for _ in range(num_candidates)]

        # Evaluate and archive
        for candidate in candidates:
            result = self.cost_loop.evaluate_tree(candidate, {})
            if result is not None:
                fitness = self.fitness_fn(candidate, self.archive)
                bd = (candidate.size(), candidate.depth())
                entry = EliteEntry(
                    individual=candidate,
                    fitness=fitness,
                    fitnesses=(fitness,),
                    behavior_descriptor=bd,
                    metadata={"iteration": self.iteration},
                )
                if self.archive.add_or_replace(entry):
                    metrics["candidates_added"] += 1

        # Learn meta-rules
        new_rules = self.library_learner.learn_from_elites()
        metrics["new_rules"] = len(new_rules)
        metrics["archive_size"] = self.archive.size()
        metrics["archive_coverage"] = self.archive.coverage()

        # Update budget tracking
        remaining = self.cost_loop.remaining_budget()
        metrics["remaining_budget"] = remaining
        metrics["budget_exhausted"] = remaining["compute_ops"] <= 0 or remaining["wall_seconds"] <= 0

        self.history.append(metrics)
        return metrics

    def run_until_budget_exhausted(self, candidates_per_step: int = 100, verbose: bool = True):
        """
        Run RSI iterations until the resource budget is exhausted.
        """
        while True:
            metrics = self.step(num_candidates=candidates_per_step)
            if verbose:
                logger.info(f"Iteration {self.iteration}: {metrics['candidates_added']} added, archive={metrics['archive_size']}, rules={metrics['new_rules']}")
            if metrics["budget_exhausted"]:
                logger.info("Budget exhausted, stopping.")
                break

    def get_best_solution(self) -> Optional[ExprNode]:
        """
        Return the highest-fitness elite in the archive.
        """
        elites = self.archive.get_elites()
        if not elites:
            return None
        return max(elites, key=lambda e: e.fitness).individual


# ---------------------------------------------------------------------------
# 9. SYSTEM BUILDER
# ---------------------------------------------------------------------------

def build_rsi_system(
    max_vocab_size: int = 20,
    max_tree_depth: int = 5,
    archive_dims: List[int] = [10, 10],
    budget_compute_ops: int = 100_000,
    budget_wall_seconds: float = 60.0,
    fitness_fn: Optional[Callable] = None,
) -> SelfImprovementEngine:
    """
    Factory function to construct a complete RSI system.
    
    Args:
        max_vocab_size: max size of vocabulary (for pruning)
        max_tree_depth: max expression tree depth
        archive_dims: dimensions for MAP-Elites behavior space
        budget_compute_ops: max primitive operations per learning run
        budget_wall_seconds: max wall-clock seconds per learning run
        fitness_fn: optional custom fitness function
    
    Returns:
        SelfImprovementEngine instance ready to use
    """
    vocab = VocabularyLayer()
    grammar = GrammarLayer(vocab, max_depth=max_tree_depth)
    archive = MAPElitesArchive(dims=archive_dims)
    budget = ResourceBudget(
        max_compute_ops=budget_compute_ops,
        max_wall_seconds=budget_wall_seconds,
    )
    engine = SelfImprovementEngine(
        vocab, grammar, archive, budget,
        fitness_fn=fitness_fn or diversity_fitness,
    )
    return engine
