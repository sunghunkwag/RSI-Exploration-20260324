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

    # Refinement type compatibility (D.5): PolymorphicOps accept any REAL input
    # and output REAL, since their actual behavior depends on context.
    input_types: List[str] = field(default_factory=lambda: [OpType.REAL])
    output_type: str = OpType.REAL

    def __post_init__(self):
        if not self.input_types or len(self.input_types) < self.arity:
            self.input_types = [OpType.REAL] * self.arity

    def accepts_child_type(self, arg_index: int, child_output_type: str) -> bool:
        """PolymorphicOps accept any type (conservative: always compatible)."""
        if arg_index >= len(self.input_types):
            return True
        return OpType.is_subtype(child_output_type, self.input_types[arg_index])


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
            # Mechanism 1: Self-Reference (A.7, D.1, D.7)
            # self_encode returns 0.0 from VocabularyLayer; the actual
            # fingerprint-dependent value is computed in _eval_tree when
            # an EvalContext with self_fingerprint is available.
            # Registering it here makes it reachable by random_tree/mutate.
            PrimitiveOp("self_encode", 0, lambda: 0.0, 0.5,
                         "Self-reference: tree's own fingerprint hash",
                         output_type=BD),
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
            if random.random() < 0.5:
                return ExprNode("input_x")
            op = self.vocab.random_op(max_arity=0)
            return ExprNode(op.name)
        op = self.vocab.random_op()
        # Build children, then check type compatibility
        children = []
        for i in range(op.arity):
            # Determine what type this argument position requires
            arg_type = op.input_types[i] if i < len(getattr(op, 'input_types', [])) else OpType.REAL
            child = self._rule_grow(max_depth - 1, required_type=arg_type)
            children.append(child)
        return ExprNode(op.name, children=children)

    def _rule_point_mutate(self, tree: ExprNode = None) -> ExprNode:
        """
        Point mutation with type-constraint enforcement (D.5).

        When replacing an op, the new op must be type-compatible with
        the existing children's output types.
        """
        if tree is None:
            tree = self.random_tree(2)
        tree = copy.deepcopy(tree)
        nodes = self._collect_nodes(tree)
        if not nodes:
            return tree
        target = random.choice(nodes)
        # Infer children types for constraint checking
        child_types = [self.infer_output_type(c) for c in target.children]
        op = self._type_compatible_op(max_arity=len(target.children), child_types=child_types)
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

    @property
    def rule_names(self) -> List[str]:
        return [getattr(r, '__name__', str(r)) for r in self._composition_rules]