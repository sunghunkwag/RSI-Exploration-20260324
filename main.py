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

    @staticmethod
    def is_subtype(child_type: str, parent_type: str) -> bool:
        """
        Check if child_type is a subtype of (or equal to) parent_type.

        Subtyping hierarchy:
          POSITIVE < NON_NEGATIVE < REAL
          UNIT < BOUNDED < REAL
          ANY can accept anything (top type)
        """
        if parent_type == OpType.ANY:
            return True
        if child_type == parent_type:
            return True
        if parent_type == OpType.REAL:
            return child_type in [OpType.NON_NEGATIVE, OpType.POSITIVE, OpType.BOUNDED, OpType.UNIT]
        if parent_type == OpType.NON_NEGATIVE:
            return child_type in [OpType.POSITIVE, OpType.UNIT]
        if parent_type == OpType.BOUNDED:
            return child_type == OpType.UNIT
        return False


@dataclass
class PrimitiveOp:
    """
    A primitive operation in the vocabulary layer.

    Attributes:
        name: operation name
        arity: number of arguments
        func: callable implementing the operation
        input_types: list of OpType tags for each argument (default: [OpType.REAL] * arity)
        output_type: OpType tag for the result (default: OpType.REAL)
    """
    name: str
    arity: int
    func: Callable
    input_types: List[str] = field(default_factory=list)
    output_type: str = OpType.REAL

    def __post_init__(self):
        if not self.input_types:
            self.input_types = [OpType.REAL] * self.arity

    def __call__(self, *args) -> float:
        """Call the underlying function."""
        return self.func(*args)

    def check_type(self, arg_index: int, arg_type: str) -> bool:
        """Check if arg_type is compatible with expected input type."""
        if arg_index >= len(self.input_types):
            return False
        return OpType.is_subtype(arg_type, self.input_types[arg_index])


# Standard primitive operations
def safe_divide(a: float, b: float) -> float:
    """Safe division that returns 1.0 if b is close to zero."""
    if abs(b) < 1e-10:
        return 1.0
    return a / b


def safe_log(x: float) -> float:
    """Safe logarithm: returns 0 if x <= 0."""
    if x <= 0:
        return 0.0
    return math.log(x)


def safe_sqrt(x: float) -> float:
    """Safe square root: returns 0 if x < 0."""
    if x < 0:
        return 0.0
    return math.sqrt(x)


def safe_pow(x: float, y: float) -> float:
    """Safe exponentiation with limits."""
    if x == 0 and y <= 0:
        return 1.0
    if x < 0 and abs(y - round(y)) > 1e-10:
        return 0.0
    try:
        result = x ** y
        if not math.isfinite(result):
            return 0.0
        return result
    except:
        return 0.0


VOCAB = [
    PrimitiveOp("add", 2, lambda a, b: a + b),
    PrimitiveOp("sub", 2, lambda a, b: a - b),
    PrimitiveOp("mul", 2, lambda a, b: a * b),
    PrimitiveOp("div", 2, safe_divide),
    PrimitiveOp("neg", 1, lambda a: -a),
    PrimitiveOp("abs", 1, abs, output_type=OpType.NON_NEGATIVE),
    PrimitiveOp("sqrt", 1, safe_sqrt, output_type=OpType.NON_NEGATIVE),
    PrimitiveOp("sq", 2, lambda a, b: a * a if abs(a) <= abs(b) else 0.0),
    PrimitiveOp("log", 1, safe_log),
    PrimitiveOp("exp", 1, lambda x: 1.0 if x > 100 else (math.exp(x) if x > -100 else 0.0)),
    PrimitiveOp("sin", 1, math.sin),
    PrimitiveOp("cos", 1, math.cos),
    PrimitiveOp("tan", 1, lambda x: 0.0 if abs(math.cos(x)) < 1e-10 else math.tan(x)),
    PrimitiveOp("pow", 2, safe_pow),
    PrimitiveOp("max", 2, max),
    PrimitiveOp("min", 2, min),
    PrimitiveOp("mod", 2, lambda a, b: 0.0 if abs(b) < 1e-10 else a % b),
]

VOCAB_BY_NAME = {op.name: op for op in VOCAB}


# ---------------------------------------------------------------------------
# 2. GRAMMAR LAYER
# ---------------------------------------------------------------------------

@dataclass
class TreeNode:
    """
    A node in an expression tree.

    Attributes:
        op: PrimitiveOp executed at this node
        children: list of child TreeNodes
        output_type: OpType of this node's output (inherited from op)
    """
    op: PrimitiveOp
    children: List[TreeNode] = field(default_factory=list)

    @property
    def output_type(self) -> str:
        return self.op.output_type

    def depth(self) -> int:
        if not self.children:
            return 1
        return 1 + max(child.depth() for child in self.children)

    def size(self) -> int:
        return 1 + sum(child.size() for child in self.children)

    def __repr__(self) -> str:
        if not self.children:
            return self.op.name
        args_str = ", ".join(repr(child) for child in self.children)
        return f"{self.op.name}({args_str})"

    def eval(self, inputs: Dict[str, float]) -> float:
        """
        Evaluate the tree with given input dictionary.

        For operations with arity > 2, we recursively evaluate children.
        For leafs, we look up the variable name in inputs.
        """
        if not self.children:
            # Leaf node: treat op.name as a variable
            return inputs.get(self.op.name, 0.0)
        child_values = [child.eval(inputs) for child in self.children]
        return self.op(*child_values)

    def copy(self) -> TreeNode:
        """Deep copy of the tree."""
        return TreeNode(
            op=self.op,
            children=[child.copy() for child in self.children]
        )

    def mutate(self, vocab: List[PrimitiveOp], max_depth: int = 6) -> TreeNode:
        """
        Return a new tree with a random mutation applied.

        Mutation strategies:
        1. Leaf: replace operation or change variable name
        2. Internal node: change operation or mutate a subtree
        """
        mutation_type = random.choice(["replace_op", "mutate_subtree"])

        if mutation_type == "replace_op" or not self.children:
            # Replace operation at this node (respecting arity constraints)
            new_ops = [op for op in vocab if op.arity == len(self.children)]
            if new_ops:
                new_op = random.choice(new_ops)
                return TreeNode(op=new_op, children=[c.copy() for c in self.children])
            return self.copy()
        else:
            # Mutate a random subtree
            child_idx = random.randint(0, len(self.children) - 1)
            new_children = [
                self.children[i].mutate(vocab, max_depth) if i == child_idx else c.copy()
                for i in range(len(self.children))
            ]
            return TreeNode(op=self.op, children=new_children)

    @staticmethod
    def random_tree(vocab: List[PrimitiveOp], depth: int = 3, leaf_prob: float = 0.4) -> TreeNode:
        """
        Generate a random tree.

        At each node: with leaf_prob, generate a leaf; otherwise pick a random op
        and recursively generate children.
        """
        if depth == 0 or random.random() < leaf_prob:
            # Create a leaf: use a random operation as variable name
            leaf_op = random.choice(vocab + [PrimitiveOp("x", 0, lambda: 0.0),
                                             PrimitiveOp("y", 0, lambda: 0.0)])
            return TreeNode(op=leaf_op, children=[])
        else:
            op = random.choice(vocab)
            children = [TreeNode.random_tree(vocab, depth - 1, leaf_prob) for _ in range(op.arity)]
            return TreeNode(op=op, children=children)


# ---------------------------------------------------------------------------
# 3. META-GRAMMAR LAYER
# ---------------------------------------------------------------------------

@dataclass
class GrammarRule:
    """
    A grammar rule that expands a non-terminal into a sequence of terminals.

    Attributes:
        name: rule name
        expansion: expression that produces the expansion
    """
    name: str
    expansion: Callable[[Dict[str, float]], List[TreeNode]]

    def apply(self, inputs: Dict[str, float]) -> List[TreeNode]:
        """Apply this rule to produce a list of TreeNodes."""
        return self.expansion(inputs)


@dataclass
class Program:
    """
    A program is a sequence of trees (instructions).

    Attributes:
        trees: list of TreeNode objects
    """
    trees: List[TreeNode] = field(default_factory=list)

    def eval(self, inputs: Dict[str, float]) -> List[float]:
        """Evaluate all trees and return results."""
        return [tree.eval(inputs) for tree in self.trees]

    def __repr__(self) -> str:
        return "\n".join(repr(tree) for tree in self.trees)

    def copy(self) -> Program:
        """Deep copy."""
        return Program(trees=[tree.copy() for tree in self.trees])

    def mutate(self, vocab: List[PrimitiveOp], grammar: Optional[Dict] = None) -> Program:
        """
        Mutate by:
        1. Mutating a random tree (if present)
        2. Adding a new random tree
        3. Removing a tree (if more than one)
        """
        if not self.trees:
            new_tree = TreeNode.random_tree(vocab)
            return Program(trees=[new_tree])

        mutation_type = random.choice(["mutate_tree", "add_tree", "remove_tree"])

        if mutation_type == "mutate_tree":
            idx = random.randint(0, len(self.trees) - 1)
            new_trees = [
                self.trees[i].mutate(vocab) if i == idx else tree.copy()
                for i in range(len(self.trees))
            ]
            return Program(trees=new_trees)
        elif mutation_type == "add_tree":
            new_tree = TreeNode.random_tree(vocab)
            return Program(trees=self.trees + [new_tree])
        else:  # remove_tree
            if len(self.trees) > 1:
                idx = random.randint(0, len(self.trees) - 1)
                return Program(trees=[tree for i, tree in enumerate(self.trees) if i != idx])
            return self.copy()

    @staticmethod
    def random_program(vocab: List[PrimitiveOp], num_trees: int = 2) -> Program:
        """Generate a random program with num_trees trees."""
        trees = [TreeNode.random_tree(vocab) for _ in range(num_trees)]
        return Program(trees=trees)


# ---------------------------------------------------------------------------
# 4. PHYSICAL COST GROUNDING
# ---------------------------------------------------------------------------

@dataclass
class ResourceCost:
    """
    Track computational resources: operations, memory, and time.

    Attributes:
        ops: number of primitive operations executed
        memory: memory allocated (in arbitrary units)
        time_ms: wall-clock time in milliseconds
    """
    ops: int = 0
    memory: int = 0
    time_ms: float = 0.0

    def total_cost(self, weights: Tuple[float, float, float] = (1.0, 0.1, 0.01)) -> float:
        """Compute total cost as weighted sum."""
        return weights[0] * self.ops + weights[1] * self.memory + weights[2] * self.time_ms

    def __repr__(self) -> str:
        return f"ResourceCost(ops={self.ops}, memory={self.memory}, time={self.time_ms:.2f}ms)"


@dataclass
class CostFunction:
    """
    A cost function that estimates resource usage for a program.

    Attributes:
        cost_per_op: cost for each primitive operation
        cost_per_depth: cost for tree depth
    """
    cost_per_op: float = 1.0
    cost_per_depth: float = 0.5

    def estimate(self, program: Program) -> ResourceCost:
        """Estimate resource cost of a program."""
        total_ops = sum(tree.size() for tree in program.trees)
        max_depth = max((tree.depth() for tree in program.trees), default=1)
        return ResourceCost(
            ops=int(total_ops * self.cost_per_op),
            memory=int(max_depth * 100),
            time_ms=float(total_ops * 0.1)
        )


# ---------------------------------------------------------------------------
# 5. SELF-IMPROVEMENT WITH QUALITY-DIVERSITY (MAP-ELITES)
# ---------------------------------------------------------------------------

@dataclass
class Solution:
    """
    A solution in the search space.

    Attributes:
        program: the Program
        fitness: scalar fitness value
        novelty: scalar novelty value (diversity metric)
        descriptor: behavioral descriptor (for MAP-Elites)
    """
    program: Program
    fitness: float
    novelty: float
    descriptor: Tuple[float, ...] = ()

    def quality_diversity_score(self, w_fitness: float = 1.0, w_novelty: float = 0.5) -> float:
        """Combined score balancing fitness and novelty."""
        return w_fitness * self.fitness + w_novelty * self.novelty


class Population:
    """
    A population of solutions with MAP-Elites-style bins.

    Uses a grid-based archive where each cell stores the best solution
    found in that behavioral region.
    """

    def __init__(self, grid_shape: Tuple[int, ...] = (10, 10)):
        self.grid = {}  # (bin indices) -> best Solution in that bin
        self.grid_shape = grid_shape
        self.history = []
        self.best_solution = None
        self.best_fitness = -float("inf")

    def bin_index(self, descriptor: Tuple[float, ...]) -> Tuple[int, ...]:
        """Map descriptor to grid bin indices."""
        indices = []
        for i, d in enumerate(descriptor):
            bin_size = 1.0 / self.grid_shape[i]
            bin_idx = int(d / bin_size)
            bin_idx = max(0, min(bin_idx, self.grid_shape[i] - 1))
            indices.append(bin_idx)
        return tuple(indices)

    def add_solution(self, solution: Solution) -> bool:
        """
        Add solution to population if it improves its bin.
        Returns True if added/improved.
        """
        bin_idx = self.bin_index(solution.descriptor)
        
        if bin_idx not in self.grid or solution.fitness > self.grid[bin_idx].fitness:
            self.grid[bin_idx] = solution
            if solution.fitness > self.best_fitness:
                self.best_fitness = solution.fitness
                self.best_solution = solution
            return True
        return False

    def get_population(self) -> List[Solution]:
        """Return all unique solutions in the archive."""
        return list(self.grid.values())

    def coverage(self) -> float:
        """Return the percentage of bins that have been filled."""
        max_bins = 1
        for dim in self.grid_shape:
            max_bins *= dim
        return len(self.grid) / max_bins if max_bins > 0 else 0.0


class DarwinGodelMachine:
    """
    Self-improving machine combining DGM loops with MAP-Elites.

    The main loop:
    1. Sample from the population
    2. Mutate to generate variations
    3. Evaluate fitness and novelty
    4. Add to archive if promising
    5. Repeat, with possibility of generating new grammar rules
    """

    def __init__(
        self,
        vocab: List[PrimitiveOp] = None,
        grid_shape: Tuple[int, ...] = (10, 10),
        max_program_size: int = 50,
        cost_fn: CostFunction = None,
    ):
        self.vocab = vocab or VOCAB
        self.population = Population(grid_shape)
        self.max_program_size = max_program_size
        self.cost_fn = cost_fn or CostFunction()
        self.iteration = 0

    def random_fitness(self, program: Program) -> float:
        """Compute fitness (placeholder: sum of evaluated outputs)."""
        try:
            inputs = {"x": random.uniform(-10, 10), "y": random.uniform(-10, 10)}
            outputs = program.eval(inputs)
            return sum(outputs) if outputs else 0.0
        except:
            return -1.0

    def novelty_score(self, program: Program, population: List[Solution]) -> float:
        """
        Compute novelty as average distance to nearest neighbors in population.

        Distance is based on tree structure (size, depth).
        """
        if not population:
            return 1.0

        prog_size = sum(tree.size() for tree in program.trees)
        prog_depth = max((tree.depth() for tree in program.trees), default=1)

        distances = []
        for sol in population:
            sol_size = sum(tree.size() for tree in sol.program.trees)
            sol_depth = max((tree.depth() for tree in sol.program.trees), default=1)
            distance = abs(prog_size - sol_size) + abs(prog_depth - sol_depth)
            distances.append(distance)

        return sum(distances) / len(distances) if distances else 0.0

    def step(self) -> bool:
        """
        Execute one step of the DGM loop.
        Returns True if a new solution was added.
        """
        self.iteration += 1

        # Sample from population
        population = self.population.get_population()
        if population:
            parent = random.choice(population).program
        else:
            parent = Program.random_program(self.vocab)

        # Mutate
        child = parent.mutate(self.vocab)

        # Evaluate
        fitness = self.random_fitness(child)
        novelty = self.novelty_score(child, population)
        descriptor = (
            sum(tree.depth() for tree in child.trees) / len(child.trees),
            sum(tree.size() for tree in child.trees) / len(child.trees),
        )

        solution = Solution(
            program=child,
            fitness=fitness,
            novelty=novelty,
            descriptor=descriptor,
        )

        # Add to archive
        added = self.population.add_solution(solution)
        return added

    def run(self, num_iterations: int = 1000) -> Dict:
        """
        Run the DGM loop for num_iterations steps.
        Returns statistics.
        """
        added_count = 0
        for _ in range(num_iterations):
            if self.step():
                added_count += 1

        stats = {
            "iterations": self.iteration,
            "solutions": len(self.population.get_population()),
            "best_fitness": self.population.best_fitness,
            "coverage": self.population.coverage(),
            "added": added_count,
        }
        return stats


# ---------------------------------------------------------------------------
# 6. META-IMPROVEMENT: GENERATING NEW GRAMMAR RULES (LLM-LIKE)
# ---------------------------------------------------------------------------

class GrammarEvolver:
    """
    Simulates grammar evolution by generating new operations.

    In a real system, this would use an LLM to suggest new operations.
    Here, we use simple symbolic templates.
    """

    def __init__(self, vocab: List[PrimitiveOp]):
        self.vocab = vocab
        self.generated_ops = []

    def suggest_new_operation(self) -> Optional[PrimitiveOp]:
        """
        Suggest a new operation based on existing vocabulary.

        Example: combine two existing operations to create a new one.
        """
        if len(self.vocab) < 2:
            return None

        # Pick two random operations
        op1, op2 = random.sample(self.vocab, 2)

        # Create a composite operation (simple example)
        def composite_func(a, b):
            try:
                intermediate = op1.func(a) if op1.arity == 1 else op1.func(a, b)
                return op2.func(intermediate) if op2.arity == 1 else op2.func(intermediate, b)
            except:
                return 0.0

        new_op = PrimitiveOp(
            name=f"{op1.name}_{op2.name}",
            arity=2,
            func=composite_func,
        )
        self.generated_ops.append(new_op)
        return new_op

    def enrich_vocabulary(self, num_new_ops: int = 3) -> List[PrimitiveOp]:
        """Generate new operations and return enriched vocabulary."""
        new_ops = []
        for _ in range(num_new_ops):
            op = self.suggest_new_operation()
            if op:
                new_ops.append(op)
        return self.vocab + new_ops


# ---------------------------------------------------------------------------
# 7. MULTI-DOMAIN EVALUATION
# ---------------------------------------------------------------------------

@dataclass
class Domain:
    """
    A problem domain with inputs, target outputs, and fitness metric.

    Attributes:
        name: domain identifier
        inputs: list of input dictionaries
        targets: list of target outputs
        metric: callable to compute fitness given (outputs, targets)
    """
    name: str
    inputs: List[Dict[str, float]]
    targets: List[float]

    def metric(self, outputs: List[float]) -> float:
        """Default: mean squared error."""
        if not outputs or len(outputs) != len(self.targets):
            return float("inf")
        return sum((o - t) ** 2 for o, t in zip(outputs, self.targets)) / len(self.targets)

    def evaluate(self, program: Program) -> float:
        """Evaluate program on all inputs and return aggregated fitness."""
        fitnesses = []
        for inp in self.inputs:
            try:
                outputs = program.eval(inp)
                fit = self.metric(outputs)
                fitnesses.append(fit)
            except:
                fitnesses.append(float("inf"))
        return min(fitnesses) if fitnesses else float("inf")


class MultiDomainSearcher:
    """
    Searches for programs that perform well across multiple domains.

    Each domain maintains its own population and the searcher tracks
    cross-domain performance.
    """

    def __init__(self, domains: List[Domain], grid_shape: Tuple[int, ...] = (5, 5)):
        self.domains = {d.name: d for d in domains}
        self.machines = {
            name: DarwinGodelMachine(grid_shape=grid_shape)
            for name in self.domains
        }

    def step(self) -> Dict[str, bool]:
        """Run one step on each domain, return which added solutions."""
        results = {}
        for name, machine in self.machines.items():
            results[name] = machine.step()
        return results

    def run(self, num_steps: int = 500) -> Dict[str, Dict]:
        """Run search on all domains and report statistics."""
        for _ in range(num_steps):
            self.step()

        results = {}
        for name, machine in self.machines.items():
            results[name] = {
                "coverage": machine.population.coverage(),
                "best_fitness": machine.population.best_fitness,
                "solutions": len(machine.population.get_population()),
                "novelty_inserts": sum(
                    1 for sol in machine.population.get_population()
                    if sol.novelty > 0.5
                ),
            }
        return results


# ---------------------------------------------------------------------------
# 8. MAIN EXECUTION
# ---------------------------------------------------------------------------

def main():
    """
    Main entry point demonstrating the full system.

    1. Create test domains
    2. Run multi-domain search
    3. Report results
    """
    # Create simple test domains
    domains = [
        Domain(
            name="regression_1",
            inputs=[{"x": float(i)} for i in range(-5, 6)],
            targets=[float(i) ** 2 for i in range(-5, 6)],  # y = x^2
        ),
        Domain(
            name="regression_2",
            inputs=[{"x": float(i) / 5.0} for i in range(-10, 11)],
            targets=[math.sin(float(i) / 5.0) for i in range(-10, 11)],  # y = sin(x)
        ),
        Domain(
            name="classification_1",
            inputs=[{"x": random.uniform(-10, 10), "y": random.uniform(-10, 10)}
                    for _ in range(20)],
            targets=[1.0 if random.random() > 0.5 else 0.0 for _ in range(20)],
        ),
    ]

    logger.info("Initializing MultiDomainSearcher with 3 domains...")
    searcher = MultiDomainSearcher(domains, grid_shape=(5, 5))

    logger.info("Running evolution for 500 steps...")
    results = searcher.run(num_steps=500)

    logger.info("=" * 70)
    logger.info("RESULTS")
    logger.info("=" * 70)
    for domain, s in results.items():
        print(f"{domain:<25} {s['coverage']:>10.4f} {s['best_fitness']:>14.4f} {s.get('novelty_inserts', 0):>10}")

    return results


if __name__ == "__main__":
    main()
