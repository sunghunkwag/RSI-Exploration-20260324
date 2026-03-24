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

import abc
import copy
import hashlib
import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 1. VOCABULARY LAYER - primitive operations
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
# 2. GRAMMAR LAYER - composition rules (expression trees)
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
        md = max_depth or self.max_depth
        return self._rule_grow(md)

    def _rule_grow(self, max_depth: int = 3) -> ExprNode:
        if max_depth <= 0:
            if random.random() < 0.5:
                return ExprNode("input_x", value=None)
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
        t1 = copy.deepcopy(t1)
        t2 = copy.deepcopy(t2)
        nodes1 = self._collect_nodes(t1)
        nodes2 = self._collect_nodes(t2)
        if nodes1 and nodes2:
            n1 = random.choice(nodes1)
            n2 = random.choice(nodes2)
            n1.op_name = n2.op_name
            n1.children = n2.children
            n1.value = n2.value
        return t1

    def _rule_hoist(self, tree: ExprNode = None) -> ExprNode:
        if tree is None:
            tree = self.random_tree(3)
        nodes = self._collect_nodes(tree)
        inner = [n for n in nodes if n.children]
        if inner:
            return copy.deepcopy(random.choice(inner))
        return copy.deepcopy(tree)

    def _collect_nodes(self, node: ExprNode) -> List[ExprNode]:
        result = [node]
        for c in node.children:
            result.extend(self._collect_nodes(c))
        return result

    def mutate(self, tree: ExprNode) -> ExprNode:
        rule = random.choice(self._composition_rules[1:])
        return rule(tree)

    def crossover(self, t1: ExprNode, t2: ExprNode) -> ExprNode:
        return self._rule_subtree_crossover(t1, t2)

    def add_rule(self, rule_fn: Callable):
        self._composition_rules.append(rule_fn)
        logger.info(f"Grammar expanded: +rule {rule_fn.__name__}")

    @property
    def num_rules(self) -> int:
        return len(self._composition_rules)


# ---------------------------------------------------------------------------
# 3. META-GRAMMAR LAYER - rules for generating new rules
# ---------------------------------------------------------------------------

class MetaGrammarLayer:
    """Generates new grammar rules and vocabulary expansions."""

    def __init__(self, vocab: VocabularyLayer, grammar: GrammarLayer):
        self.vocab = vocab
        self.grammar = grammar
        self._meta_rules: List[Callable] = []
        self._expansion_history: List[str] = []
        self._register_default_meta_rules()

    def _register_default_meta_rules(self):
        self._meta_rules.extend([
            self._meta_compose_new_op,
            self._meta_parameterize_mutation,
        ])

    def _meta_compose_new_op(self) -> Optional[PrimitiveOp]:
        ops = self.vocab.all_ops()
        unary = [op for op in ops if op.arity == 1]
        if len(unary) < 2:
            return None
        op1, op2 = random.sample(unary, 2)
        new_name = f"{op1.name}_then_{op2.name}"
        if self.vocab.get(new_name) is not None:
            return None
        new_fn = lambda a, _o1=op1, _o2=op2: _o2(_o1(a))
        new_cost = op1.cost + op2.cost
        new_op = PrimitiveOp(new_name, 1, new_fn, new_cost, f"Composed: {op1.name} -> {op2.name}")
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
            num_mutations = max(1, int(len(nodes) * scale * 0.3))
            for _ in range(min(num_mutations, len(nodes))):
                target = random.choice(nodes)
                op = self.vocab.random_op(max_arity=len(target.children))
                target.op_name = op.name
            return tree

        scaled_mutate.__name__ = f"scaled_mutate_{scale:.2f}"
        self.grammar.add_rule(scaled_mutate)
        self._expansion_history.append(f"new_rule:{scaled_mutate.__name__}")
        return scaled_mutate

    def expand_design_space(self) -> str:
        meta_rule = random.choice(self._meta_rules)
        result = meta_rule()
        action = f"Applied {meta_rule.__name__}: {'success' if result else 'no-op'}"
        logger.info(f"Meta-grammar: {action}")
        return action

    @property
    def expansion_count(self) -> int:
        return len(self._expansion_history)


# ---------------------------------------------------------------------------
# 4. PHYSICAL COST GROUNDING - resource tracking
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

    def check_memory(self, current_bytes: int):
        self._peak_memory = max(self._peak_memory, current_bytes)

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
        c = self.compute_fraction
        t = self.time_fraction
        return 1.0 / (1.0 + c + t)

    def summary(self) -> dict:
        return {
            "compute_used": self._compute_used,
            "compute_max": self.max_compute_ops,
            "wall_seconds": round(time.time() - self._start_time, 3),
            "wall_max": self.max_wall_seconds,
            "cost_score": round(self.cost_score(), 4),
        }


class CostGroundingLoop:
    """Evaluates candidates with physical cost awareness."""

    def __init__(self, budget: ResourceBudget):
        self.budget = budget

    def evaluate_with_cost(
        self,
        tree: ExprNode,
        vocab: VocabularyLayer,
        fitness_fn: Callable,
    ) -> Tuple[float, float, float]:
        self.budget.reset()
        raw_fitness = fitness_fn(tree, vocab)
        self.budget.tick(tree.size() * 10)
        cost = self.budget.cost_score()
        grounded_fitness = raw_fitness * cost
        return raw_fitness, cost, grounded_fitness


# ---------------------------------------------------------------------------
# 5. MAP-ELITES ARCHIVE - quality-diversity container
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
    """Multi-dimensional MAP-Elites archive for quality-diversity."""

    def __init__(self, dims: List[int]):
        self.dims = dims
        self._grid: Dict[Tuple[int, ...], EliteEntry] = {}
        self._total_tried = 0
        self._total_inserted = 0

    def behavior_descriptor(self, tree: ExprNode) -> Tuple[int, ...]:
        depth_bin = min(tree.depth(), self.dims[0] - 1)
        size_bin = min(tree.size() // 3, self.dims[1] - 1)
        return (depth_bin, size_bin)

    def try_insert(self, entry: EliteEntry) -> bool:
        self._total_tried += 1
        cell = entry.behavior
        if cell not in self._grid or entry.grounded_fitness > self._grid[cell].grounded_fitness:
            self._grid[cell] = entry
            self._total_inserted += 1
            return True
        return False

    def sample_parent(self) -> Optional[EliteEntry]:
        if not self._grid:
            return None
        return random.choice(list(self._grid.values()))

    @property
    def coverage(self) -> float:
        total_cells = 1
        for d in self.dims:
            total_cells *= d
        return len(self._grid) / total_cells

    @property
    def best_fitness(self) -> float:
        if not self._grid:
            return 0.0
        return max(e.grounded_fitness for e in self._grid.values())

    def summary(self) -> dict:
        return {
            "filled_cells": len(self._grid),
            "total_cells": int(np.prod(self.dims)),
            "coverage": round(self.coverage, 4),
            "best_fitness": round(self.best_fitness, 4),
            "total_tried": self._total_tried,
            "total_inserted": self._total_inserted,
        }


# ---------------------------------------------------------------------------
# 6. SELF-IMPROVEMENT ENGINE - the DGM-inspired outer loop
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
        best_gen_fitness = 0.0

        for _ in range(population_size):
            parent = self.archive.sample_parent()
            if parent is not None:
                child_tree = self.grammar.mutate(parent.tree)
            else:
                child_tree = self.grammar.random_tree(3)

            raw, cost, grounded = self.cost_loop.evaluate_with_cost(
                child_tree, self.vocab, self.fitness_fn
            )

            behavior = self.archive.behavior_descriptor(child_tree)
            entry = EliteEntry(
                tree=child_tree,
                raw_fitness=raw,
                cost_score=cost,
                grounded_fitness=grounded,
                behavior=behavior,
                generation=self.generation,
            )

            if self.archive.try_insert(entry):
                inserted += 1
            best_gen_fitness = max(best_gen_fitness, grounded)

        expansion_action = None
        if self.generation % self.expansion_interval == 0:
            expansion_action = self.meta_grammar.expand_design_space()

        record = {
            "generation": self.generation,
            "population_size": population_size,
            "inserted": inserted,
            "best_gen_fitness": round(best_gen_fitness, 4),
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
        logger.info(f"Starting RSI loop: {generations} generations x {population_size} pop")
        for g in range(generations):
            record = self.step(population_size)
            if g % 10 == 0 or g == generations - 1:
                logger.info(
                    f"Gen {record['generation']:4d} | "
                    f"best={record['archive_best']:.4f} | "
                    f"cov={record['archive_coverage']:.4f} | "
                    f"vocab={record['vocab_size']} | "
                    f"rules={record['grammar_rules']} | "
                    f"expansions={record['meta_expansions']}"
                )
        return self.history


# ---------------------------------------------------------------------------
# 7. EXAMPLE FITNESS FUNCTIONS
# ---------------------------------------------------------------------------

def symbolic_regression_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    """
    Fitness: how well does the expression tree approximate f(x) = x^2 + 2x + 1?
    """
    test_points = np.linspace(-5, 5, 20)
    target_fn = lambda x: x ** 2 + 2 * x + 1
    total_error = 0.0

    for x in test_points:
        try:
            predicted = _eval_tree(tree, vocab, x)
            target = target_fn(x)
            total_error += abs(predicted - target)
        except Exception:
            total_error += 1e6

    max_error = 1e6
    normalized_error = min(total_error / len(test_points), max_error)
    fitness = 1.0 / (1.0 + normalized_error)
    return fitness


def _eval_tree(node: ExprNode, vocab: VocabularyLayer, x: float) -> float:
    """Recursively evaluate an expression tree."""
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
        if isinstance(result, (int, float)) and not math.isfinite(result):
            return 0.0
        return float(result)
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# 8. FACTORY - convenient construction
# ---------------------------------------------------------------------------

def build_rsi_system(
    fitness_fn: Callable = None,
    max_depth: int = 5,
    archive_dims: List[int] = None,
    budget_ops: int = 100_000,
    budget_seconds: float = 60.0,
    expansion_interval: int = 10,
) -> SelfImprovementEngine:
    """Factory function to build a complete RSI system."""
    if fitness_fn is None:
        fitness_fn = symbolic_regression_fitness
    if archive_dims is None:
        archive_dims = [6, 10]

    vocab = VocabularyLayer()
    grammar = GrammarLayer(vocab, max_depth=max_depth)
    meta_grammar = MetaGrammarLayer(vocab, grammar)
    archive = MAPElitesArchive(dims=archive_dims)
    budget = ResourceBudget(max_compute_ops=budget_ops, max_wall_seconds=budget_seconds)
    cost_loop = CostGroundingLoop(budget)

    return SelfImprovementEngine(
        vocab=vocab,
        grammar=grammar,
        meta_grammar=meta_grammar,
        archive=archive,
        cost_loop=cost_loop,
        fitness_fn=fitness_fn,
        expansion_interval=expansion_interval,
    )


# ---------------------------------------------------------------------------
# 9. CLI ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    """Run the RSI exploration system."""
    print("=" * 70)
    print("RSI-Exploration: Recursive Self-Improvement Architecture")
    print("Hybrid DGM + MAP-Elites with Design Space Self-Expansion")
    print("=" * 70)

    engine = build_rsi_system(
        fitness_fn=symbolic_regression_fitness,
        max_depth=5,
        archive_dims=[6, 10],
        budget_ops=100_000,
        budget_seconds=60.0,
        expansion_interval=10,
    )

    history = engine.run(generations=50, population_size=20)

    print("\\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Archive: {json.dumps(engine.archive.summary(), indent=2)}")
    print(f"Vocabulary size: {engine.vocab.size}")
    print(f"Grammar rules: {engine.grammar.num_rules}")
    print(f"Design space expansions: {engine.meta_grammar.expansion_count}")
    print(f"Best grounded fitness: {engine.archive.best_fitness:.4f}")

    return engine


if __name__ == "__main__":
    main()

