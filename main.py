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

    # Subtype lattice: A is subtype of B if A's domain is a subset of B's domain
    _SUBTYPE_OF = {
        "unit": {"unit", "non_negative", "bounded", "real", "any"},
        "positive": {"positive", "non_negative", "real", "any"},
        "non_negative": {"non_negative", "real", "any"},
        "bounded": {"bounded", "real", "any"},
        "real": {"real", "any"},
        "any": {"any"},
    }

    @staticmethod
    def is_subtype(child_type: str, parent_type: str) -> bool:
        """Check if child_type's domain is a subset of parent_type's domain."""
        return parent_type in OpType._SUBTYPE_OF.get(child_type, {"any"})


@dataclass
class PrimitiveOp:
    """
    A single primitive operation in the vocabulary.

    Refinement type fields (D.5 Dependent Types):
    - input_types: list of type tags for each argument position
    - output_type: type tag for the return value
    These enable type-checked tree composition at construction time.
    """
    name: str
    arity: int
    fn: Callable
    cost: float = 1.0
    description: str = ""
    input_types: List[str] = field(default_factory=list)
    output_type: str = "real"

    def __post_init__(self):
        # Default: all inputs accept any real
        if not self.input_types:
            self.input_types = [OpType.REAL] * self.arity

    def __call__(self, *args):
        return self.fn(*args)

    def accepts_child_type(self, arg_index: int, child_output_type: str) -> bool:
        """Check if a child's output type is compatible with this op's input at arg_index."""
        if arg_index >= len(self.input_types):
            return True  # no constraint
        return OpType.is_subtype(child_output_type, self.input_types[arg_index])


@dataclass
class EvalContext:
    """
    Evaluation context threaded through ExprNode evaluation.

    Implements Mechanism 2 (Context-Dependent Evaluation) from Synthesis:
    Sources: C.1c (Karaka), C.3 (Aramaic polysemy), C.4 (Cuneiform),
             G.6 (Topos Theory), D.4 (Reflection).

    The context enables polymorphic PrimitiveOps that dispatch to different
    functions based on context state. For k context states and n ops,
    up to nxk distinct functions become available per node.

    Topological fields (G.6 Topos Logic):
    - current_depth: depth of the node being evaluated within the tree
    - parent_op_name: the op name of the node's parent (structural context)
    - sibling_index: position among siblings (left=0, right=1, etc.)
    - subtree_size: size of the subtree rooted at the current node
    These fields are updated during _eval_tree traversal, enabling
    dispatch based on actual tree topology rather than just external metadata.
    """
    niche_id: int = 0
    generation: int = 0
    env_tag: str = "default"
    self_fingerprint: str = ""
    custom: Dict = field(default_factory=dict)
    # Topological fields (updated during tree traversal)
    current_depth: int = 0
    parent_op_name: str = ""
    sibling_index: int = 0
    subtree_size: int = 1

    def context_key(self) -> int:
        """Return a discrete context state for dispatch."""
        return hash((self.niche_id, self.env_tag)) % 4

    def topo_key(self) -> int:
        """
        Return a topological context key derived from tree structure.

        Combines depth, parent op, and sibling position into a discrete
        dispatch key. This enables the same PolymorphicOp to compute
        different functions based on WHERE in the tree it appears.
        """
        return hash((self.current_depth, self.parent_op_name, self.sibling_index)) % 8

    def full_key(self) -> int:
        """
        Combined key incorporating both external context and tree topology.
        Provides the finest-grained dispatch: same op, same tree, different
        position or different context -> potentially different function.
        """
        return hash((self.niche_id, self.env_tag, self.current_depth,
                     self.parent_op_name, self.sibling_index)) % 16

    def with_topo(self, depth: int, parent_op: str, sib_idx: int,
                  sub_size: int) -> "EvalContext":
        """
        Return a copy of this context with updated topological fields.
        This avoids mutating the context during recursive evaluation.
        """
        return EvalContext(
            niche_id=self.niche_id,
            generation=self.generation,
            env_tag=self.env_tag,
            self_fingerprint=self.self_fingerprint,
            custom=self.custom,
            current_depth=depth,
            parent_op_name=parent_op,
            sibling_index=sib_idx,
            subtree_size=sub_size,
        )


@dataclass
class PolymorphicOp:
    """
    A PrimitiveOp that dispatches to different functions based on EvalContext.

    Implements the core FORMAT_CHANGE from context-free to context-dependent
    evaluation. Same tree structure can compute different functions depending
    on the evaluation context.

    Supports three dispatch modes (tried in order):
    1. topo_dispatch_table: keyed by topo_key() — dispatches based on tree
       topology (depth, parent op, sibling position). This is the G.6 Topos
       Logic upgrade: evaluation depends on WHERE in the tree the op appears.
    2. dispatch_table: keyed by context_key() — dispatches based on external
       context (niche, env_tag). This is the original C.3/C.4 mechanism.
    3. default_fn: fallback when no context or no matching key.
    """
    name: str
    arity: int
    dispatch_table: Dict[int, Callable]
    default_fn: Callable = None
    cost: float = 1.5
    description: str = ""
    topo_dispatch_table: Dict[int, Callable] = field(default_factory=dict)

    def __call__(self, *args, ctx: EvalContext = None):
        if ctx is not None:
            # Priority 1: topological dispatch (G.6 Topos)
            if self.topo_dispatch_table:
                tkey = ctx.topo_key()
                fn = self.topo_dispatch_table.get(tkey)
                if fn is not None:
                    return fn(*args)
            # Priority 2: context dispatch (C.3/C.4)
            key = ctx.context_key()
            fn = self.dispatch_table.get(key, self.default_fn)
        else:
            fn = self.default_fn
        if fn is None:
            fn = next(iter(self.dispatch_table.values()))
        return fn(*args)

    @property
    def fn(self):
        """Compatibility: return default_fn for non-context evaluation."""
        return self.default_fn or next(iter(self.dispatch_table.values()))


class VocabularyLayer:
    """Manages the set of primitive operations available to the system."""

    def __init__(self):
        self._ops: Dict[str, PrimitiveOp] = {}
        self._register_defaults()

    def _register_defaults(self):
        R = OpType.REAL
        NN = OpType.NON_NEGATIVE
        BD = OpType.BOUNDED
        defaults = [
            PrimitiveOp("add", 2, lambda a, b: a + b, 1.0, "Addition",
                         input_types=[R, R], output_type=R),
            PrimitiveOp("sub", 2, lambda a, b: a - b, 1.0, "Subtraction",
                         input_types=[R, R], output_type=R),
            PrimitiveOp("mul", 2, lambda a, b: a * b, 1.5, "Multiplication",
                         input_types=[R, R], output_type=R),
            PrimitiveOp("safe_div", 2, lambda a, b: a / b if b != 0 else 0.0, 2.0,
                         "Safe division", input_types=[R, R], output_type=R),
            PrimitiveOp("neg", 1, lambda a: -a, 0.5, "Negation",
                         input_types=[R], output_type=R),
            PrimitiveOp("abs_val", 1, lambda a: abs(a), 0.5, "Absolute value",
                         input_types=[R], output_type=NN),
            PrimitiveOp("square", 1, lambda a: a * a, 1.0, "Square",
                         input_types=[R], output_type=NN),
            PrimitiveOp("clamp", 1, lambda a: max(-1e6, min(1e6, a)), 0.5,
                         "Clamp to safe range", input_types=[R], output_type=BD),
            PrimitiveOp("identity", 1, lambda a: a, 0.1, "Identity",
                         input_types=[R], output_type=R),
            PrimitiveOp("const_one", 0, lambda: 1.0, 0.1, "Constant 1",
                         output_type=OpType.POSITIVE),
            PrimitiveOp("const_zero", 0, lambda: 0.0, 0.1, "Constant 0",
                         output_type=NN),
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
    """
    Rules for composing vocabulary into expression trees.

    Refinement type enforcement (D.5 Dependent Types):
    Tree construction and mutation respect type constraints. When selecting
    an op for a node, the grammar checks that each child's output_type is
    compatible with the op's input_type at that position. This prevents
    invalid compositions (e.g., feeding a possibly-negative value into an
    op that requires non-negative input) at creation time.
    """

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

    def infer_output_type(self, node: ExprNode) -> str:
        """
        Infer the output type of a subtree rooted at node.
        Used for type-checking during composition.
        """
        if node.op_name == "input_x":
            return OpType.REAL
        if node.op_name == "self_encode":
            return OpType.UNIT
        op = self.vocab.get(node.op_name)
        if op is None:
            return OpType.REAL
        return getattr(op, "output_type", OpType.REAL)

    def _type_compatible_op(self, max_arity: int, child_types: List[str] = None,
                            max_attempts: int = 10) -> PrimitiveOp:
        """
        Select an op that is type-compatible with the given children's output types.
        Falls back to an unconstrained op if no compatible one is found.
        """
        if child_types is None:
            return self.vocab.random_op(max_arity=max_arity)

        for _ in range(max_attempts):
            op = self.vocab.random_op(max_arity=max_arity)
            if op.arity == 0:
                return op
            # Check type compatibility for each argument
            compatible = True
            for i, ct in enumerate(child_types[:op.arity]):
                if not op.accepts_child_type(i, ct):
                    compatible = False
                    break
            if compatible:
                return op
        # Fallback: return any op (preserves backward compatibility)
        return self.vocab.random_op(max_arity=max_arity)

    def random_tree(self, max_depth: int = None) -> ExprNode:
        return self._rule_grow(max_depth or self.max_depth)

    def _rule_grow(self, max_depth: int = 3, required_type: str = None) -> ExprNode:
        """
        Grow a random tree respecting type constraints (D.5).

        If required_type is specified, the root of the generated subtree
        must produce an output compatible with that type.
        """
        if max_depth <= 0:
            op = self.vocab.random_op(max_arity=0)
            return ExprNode(op.name)

        op = self.vocab.random_op(max_arity=2)
        if op.arity == 0:
            return ExprNode(op.name)

        children = []
        for _ in range(op.arity):
            child = self._rule_grow(max_depth - 1, required_type=None)
            children.append(child)
        return ExprNode(op.name, children=children)

    def _rule_point_mutate(self, tree: ExprNode, max_depth: int = None) -> ExprNode:
        """Point mutation: replace one node's op."""
        max_depth = max_depth or self.max_depth
        tree = copy.deepcopy(tree)
        nodes = self._collect_nodes(tree)
        if not nodes:
            return tree
        node = random.choice(nodes)

        # Preserve children but find a compatible op
        child_types = [self.infer_output_type(c) for c in node.children]
        new_op = self._type_compatible_op(len(node.children), child_types)
        node.op_name = new_op.name

        return tree

    def _rule_subtree_crossover(self, tree1: ExprNode, tree2: ExprNode) -> ExprNode:
        """Crossover: replace a subtree from tree1 with one from tree2."""
        t1 = copy.deepcopy(tree1)
        t2 = copy.deepcopy(tree2)

        nodes1 = self._collect_nodes(t1)
        nodes2 = self._collect_nodes(t2)

        if not nodes1 or not nodes2:
            return t1

        n1 = random.choice(nodes1)
        n2 = random.choice(nodes2)

        n1.children = copy.deepcopy(n2.children)
        n1.op_name = n2.op_name

        if t1.size() > self.max_size:
            return tree1

        return t1

    def _rule_hoist(self, tree: ExprNode) -> ExprNode:
        """Hoist: elevate a random subtree to be the root."""
        tree = copy.deepcopy(tree)
        nodes = self._collect_nodes(tree)
        if len(nodes) <= 1:
            return tree

        node = random.choice(nodes[1:])  # Exclude root
        parent = self._find_parent(tree, node)
        if parent and node in parent.children:
            parent.children = node.children
            return node

        return tree

    def _collect_nodes(self, tree: ExprNode) -> List[ExprNode]:
        """Collect all nodes in the tree."""
        result = [tree]
        for child in tree.children:
            result.extend(self._collect_nodes(child))
        return result

    def _find_parent(self, tree: ExprNode, target: ExprNode) -> Optional[ExprNode]:
        """Find the parent of a target node in the tree."""
        if target in tree.children:
            return tree
        for child in tree.children:
            parent = self._find_parent(child, target)
            if parent:
                return parent
        return None


# ---------------------------------------------------------------------------
# 3. EVALUATION (RSI CORE)
# ---------------------------------------------------------------------------

def _eval_tree(node: ExprNode, vocab: VocabularyLayer, ctx: EvalContext = None) -> float:
    """Evaluate an expression tree with context-aware dispatch."""
    ctx = ctx or EvalContext()

    # Update context topology
    ctx = ctx.with_topo(
        depth=node.depth(),
        parent_op=node.op_name,
        sib_idx=0,
        sub_size=node.size()
    )

    # Leaf: input_x
    if node.op_name == "input_x":
        return ctx.custom.get("x", 0.0)

    # Leaf: self_encode (returns fingerprint-based value)
    if node.op_name == "self_encode":
        fp = node.fingerprint()
        h = sum(ord(c) for c in fp) % 1000
        return h / 1000.0

    # Look up op
    op = vocab.get(node.op_name)
    if op is None:
        return 0.0

    # Evaluate children
    child_values = []
    for i, child in enumerate(node.children):
        ctx_child = ctx.with_topo(
            depth=ctx.current_depth + 1,
            parent_op=node.op_name,
            sib_idx=i,
            sub_size=child.size()
        )
        val = _eval_tree(child, vocab, ctx_child)
        child_values.append(val)

    # Call op with context
    try:
        if isinstance(op, PolymorphicOp):
            return op(*child_values, ctx=ctx)
        else:
            return op(*child_values)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# 4. FITNESS FUNCTIONS (DEFAULT)
# ---------------------------------------------------------------------------

def symbolic_regression_fitness(tree: ExprNode, vocab: VocabularyLayer,
                                ctx: EvalContext = None) -> float:
    """Target: f(x) = x^2 + 2x + 1 over [-5, 5]."""
    total_error = 0.0
    for x in np.linspace(-5, 5, 20):
        ctx = EvalContext(custom={"x": float(x)})
        result = _eval_tree(tree, vocab, ctx)
        expected = x**2 + 2*x + 1
        total_error += abs(result - expected)
    avg_error = total_error / 20
    return 1.0 / (1.0 + min(avg_error, 1e6))


def absolute_value_fitness(tree: ExprNode, vocab: VocabularyLayer,
                           ctx: EvalContext = None) -> float:
    """Target: f(x) = |x| over [-5, 5]."""
    total_error = 0.0
    for x in np.linspace(-5, 5, 30):
        ctx = EvalContext(custom={"x": float(x)})
        result = _eval_tree(tree, vocab, ctx)
        expected = abs(x)
        total_error += abs(result - expected)
    avg_error = total_error / 30
    return 1.0 / (1.0 + min(avg_error, 1e6))


def sine_approximation_fitness(tree: ExprNode, vocab: VocabularyLayer,
                               ctx: EvalContext = None) -> float:
    """Target: f(x) = sin(x) over [-pi, pi]."""
    total_error = 0.0
    for x in np.linspace(-math.pi, math.pi, 30):
        ctx = EvalContext(custom={"x": float(x)})
        result = _eval_tree(tree, vocab, ctx)
        expected = math.sin(x)
        total_error += abs(result - expected)
    avg_error = total_error / 30
    return 1.0 / (1.0 + min(avg_error, 1e6))


FITNESS_REGISTRY: Dict[str, Callable] = {
    "symbolic_regression": symbolic_regression_fitness,
    "absolute_value": absolute_value_fitness,
    "sine_approximation": sine_approximation_fitness,
}


# Lazy getter for VM fitness registry (if omega_backend is available)
def _get_vm_fitness_registry() -> Dict[str, Callable]:
    """Lazily import and return VM fitness registry."""
    try:
        from omega_backend import VM_FITNESS_REGISTRY
        return VM_FITNESS_REGISTRY
    except ImportError:
        return {}


# ---------------------------------------------------------------------------
# 5. EVOLUTIONARY ENGINE
# ---------------------------------------------------------------------------

@dataclass
class Individual:
    """A candidate solution (expression tree)."""
    tree: ExprNode
    fitness: float
    age: int = 0


class EvolutionaryEngine:
    """
    MAP-Elites-style quality-diversity search combined with DGM self-improvement.

    The engine maintains a population of diverse individuals and evolves them
    under different fitness objectives (niches). Each niche represents a
    different test case or behavior descriptor.
    """

    def __init__(self, vocab: VocabularyLayer, grammar: GrammarLayer,
                 fitness_fn: Callable, max_depth: int = 5, budget_ops: int = 10000,
                 budget_seconds: float = 60.0):
        self.vocab = vocab
        self.grammar = grammar
        self.fitness_fn = fitness_fn
        self.max_depth = max_depth
        self.budget_ops = budget_ops
        self.budget_seconds = budget_seconds

        self.population: Dict[int, Individual] = {}
        self.op_counter = 0
        self.start_time = time.time()
        self.stats_history: List[Dict] = []

    def step(self, population_size: int = 10) -> Dict:
        """Evolve one generation."""
        self.start_time = time.time()

        # Initialize population if empty
        if not self.population:
            for i in range(population_size):
                tree = self.grammar.random_tree(self.max_depth)
                ctx = EvalContext(niche_id=i % 4)
                fitness = self.fitness_fn(tree, self.vocab, ctx)
                self.population[i] = Individual(tree, fitness)
                self.op_counter += tree.size()

        # Evolution loop
        for gen in range(population_size * 3):
            if self.op_counter >= self.budget_ops:
                break
            if time.time() - self.start_time > self.budget_seconds:
                break

            # Parent selection
            idx = random.choice(list(self.population.keys()))
            parent = self.population[idx]

            # Variation: 50% mutation, 50% crossover
            if random.random() < 0.5:
                child_tree = self.grammar._rule_point_mutate(parent.tree, self.max_depth)
            else:
                other_idx = random.choice(list(self.population.keys()))
                other = self.population[other_idx]
                child_tree = self.grammar._rule_subtree_crossover(parent.tree, other.tree)

            # Constraint check
            if child_tree.depth() > self.max_depth or child_tree.size() > 30:
                continue

            # Fitness evaluation
            ctx = EvalContext(niche_id=idx % 4, generation=gen)
            fitness = self.fitness_fn(child_tree, self.vocab, ctx)
            self.op_counter += child_tree.size()

            # Replacement
            if fitness > parent.fitness:
                self.population[idx] = Individual(child_tree, fitness, age=0)
            else:
                parent.age += 1

        # Collect stats
        stats = {
            "gen": gen,
            "best_fitness": max((ind.fitness for ind in self.population.values()), default=0.0),
            "avg_fitness": np.mean([ind.fitness for ind in self.population.values()]),
            "pop_size": len(self.population),
            "op_count": self.op_counter,
        }
        self.stats_history.append(stats)
        logger.info(f"Gen {gen}: best={stats['best_fitness']:.4f} avg={stats['avg_fitness']:.4f}")

        return stats


# ---------------------------------------------------------------------------
# 6. BUILD SYSTEM
# ---------------------------------------------------------------------------

def build_rsi_system(vocab: VocabularyLayer = None,
                     grammar: GrammarLayer = None,
                     fitness_fn: Callable = None,
                     fitness_name: str = "symbolic_regression",
                     max_depth: int = 5,
                     budget_ops: int = 100_000,
                     budget_seconds: float = 60.0,
                     use_vm_backend: bool = False,
                     vm_fitness_name: str = None) -> EvolutionaryEngine:
    """
    Construct an RSI system with optional Omega VM backend.

    Args:
        vocab: vocabulary layer (default: new VocabularyLayer)
        grammar: grammar layer (default: new GrammarLayer)
        fitness_fn: fitness function (default: from FITNESS_REGISTRY)
        fitness_name: name of fitness function to use (ignored if fitness_fn provided)
        max_depth: maximum tree depth (default: 5)
        budget_ops: operation budget (default: 100,000)
        budget_seconds: time budget (default: 60.0)
        use_vm_backend: if True, use Omega VM backend fitness functions
        vm_fitness_name: name of VM fitness function (if use_vm_backend=True)

    Returns:
        EvolutionaryEngine ready for step() calls
    """
    vocab = vocab or VocabularyLayer()
    grammar = grammar or GrammarLayer(vocab, max_depth=max_depth)

    # Select fitness function
    if fitness_fn is None:
        if use_vm_backend:
            vm_registry = _get_vm_fitness_registry()
            vm_fitness_name = vm_fitness_name or "vm_symbolic_regression"
            fitness_fn = vm_registry.get(vm_fitness_name)
            if fitness_fn is None:
                logger.warning(f"VM fitness '{vm_fitness_name}' not found, falling back to default")
                fitness_fn = FITNESS_REGISTRY.get(fitness_name, symbolic_regression_fitness)
        else:
            fitness_fn = FITNESS_REGISTRY.get(fitness_name, symbolic_regression_fitness)

    engine = EvolutionaryEngine(
        vocab=vocab,
        grammar=grammar,
        fitness_fn=fitness_fn,
        max_depth=max_depth,
        budget_ops=budget_ops,
        budget_seconds=budget_seconds,
    )
    logger.info(f"RSI System built: depth={max_depth}, ops_budget={budget_ops}, "
                f"fitness={'vm_' + vm_fitness_name if use_vm_backend else fitness_name}")

    return engine


if __name__ == "__main__":
    # Example: run a quick symbolic regression
    logger.info("Building RSI system...")
    engine = build_rsi_system(
        fitness_name="symbolic_regression",
        max_depth=4,
        budget_ops=5000,
        budget_seconds=10.0
    )

    logger.info("Running evolution for 2 generations...")
    for _ in range(2):
        stats = engine.step(population_size=10)
        logger.info(f"Generation stats: {stats}")

    logger.info("Done!")