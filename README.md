# RSI-Exploration-20260324

## Recursive Self-Improvement Architecture with Design Space Self-Expansion

A hybrid architecture combining **Darwin Godel Machine (DGM)** self-improvement loops with **MAP-Elites** quality-diversity search, featuring three-layer design space expansion and physical cost grounding.

---

## Research Context

This repository was auto-generated as part of an exploration into Recursive Self-Improvement (RSI) architectures. It was informed by analysis of 5 open-source repositories in the open-ended evolution space:

| Repository | Core Mechanism | F_theo vs F_eff | Cost Grounding |
|---|---|---|---|
| amahury/OEE-metric | Omega metric via attractor dynamics in RBNs | Measures F_theo (open-endedness metric) | No real-world grounding |
| b-albar/evolve-anything | LLM + MAP-Elites evolutionary code optimization | Expands F_eff via LLM mutations | Sandboxed execution cost |
| DesmondForward/open-ended-evolution-agency-si | Multi-scenario agency emergence simulator | Models F_theo via SDE dynamics | Simulated environment difficulty |
| guillaumepourcel/dgm | Darwin Godel Machine - self-modifying code agent | Expands F_theo via recursive self-improvement | Benchmark-grounded evaluation |
| calvarez0/fashiOEn | Open-ended evolution of fashion designs | Fixed F_eff search | No cost grounding |

### Most Promising: DGM + Evolve-Anything

The two most promising repos are **guillaumepourcel/dgm** (genuine recursive self-improvement with empirical validation) and **b-albar/evolve-anything** (LLM-driven evolutionary search with MAP-Elites for quality-diversity). This hybrid architecture combines their core mechanisms.

---

## Architecture Overview

### Three-Layer Design Space Expansion

The system operates across three layers that enable the search space itself to grow over time:

**Layer 1: Vocabulary** - A registry of primitive operations (add, mul, neg, square, etc.) that serve as the atomic building blocks. New primitives can be composed from existing ones at runtime.

**Layer 2: Grammar** - Composition rules that combine vocabulary primitives into expression trees (ASTs). Includes point mutation, subtree crossover, and hoisting. New mutation strategies can be added dynamically.

**Layer 3: Meta-Grammar** - Rules for generating new grammar rules and vocabulary items. This is what enables genuine design space expansion (F_theo growth), not just better search within a fixed space (F_eff).

### Physical Cost Grounding Loop

Every candidate solution is evaluated with a resource budget that tracks:
- Compute operations consumed
- Wall-clock time elapsed
- Memory usage

The final fitness is: `grounded_fitness = raw_fitness * cost_score`

This prevents bloat and ensures that solutions are parsimonious - they must be both correct and efficient.

### MAP-Elites Quality-Diversity Archive

Instead of maintaining a single best solution, the system uses a MAP-Elites grid indexed by behavioral descriptors (tree depth, tree size). This ensures diversity of solutions across different structural niches, preventing premature convergence.

### DGM-Inspired Outer Loop

The self-improvement engine runs generational evolution:
1. Sample parents from the MAP-Elites archive
2. Apply grammar mutations (including meta-grammar-expanded mutations)
3. Evaluate with cost grounding
4. Insert into archive if the new solution dominates its cell
5. Periodically expand the design space via meta-grammar

---

## Installation

```bash
git clone https://github.com/sunghunkwag/RSI-Exploration-20260324.git
cd RSI-Exploration-20260324
pip install -r requirements.txt
```

## Usage

### Run the system

```bash
python main.py
```

This runs 50 generations of evolutionary search on a symbolic regression task (approximating f(x) = x^2 + 2x + 1), with design space expansion every 10 generations.

### Run tests

```bash
pytest test_main.py -v
```

### Use as a library

```python
from main import build_rsi_system, symbolic_regression_fitness

# Build with custom parameters
engine = build_rsi_system(
    fitness_fn=symbolic_regression_fitness,
    max_depth=5,
    archive_dims=[6, 10],
    expansion_interval=10,
)

# Run evolution
history = engine.run(generations=100, population_size=30)

# Inspect results
print(f"Best fitness: {engine.archive.best_fitness:.4f}")
print(f"Archive coverage: {engine.archive.coverage:.4f}")
print(f"Vocabulary size: {engine.vocab.size}")
print(f"Grammar rules: {engine.grammar.num_rules}")
```

### Custom fitness function

```python
from main import build_rsi_system, ExprNode, VocabularyLayer, _eval_tree
import numpy as np

def my_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    # Define your own target and evaluation
    xs = np.linspace(0, 10, 50)
    error = sum(abs(_eval_tree(tree, vocab, x) - np.sin(x)) for x in xs)
    return 1.0 / (1.0 + error / len(xs))

engine = build_rsi_system(fitness_fn=my_fitness)
engine.run(generations=200)
```

---

## File Structure

| File | Description |
|---|---|
| `main.py` | Core architecture: Vocabulary, Grammar, Meta-Grammar, Cost Grounding, MAP-Elites, Self-Improvement Engine |
| `test_main.py` | Comprehensive pytest test suite covering all components |
| `requirements.txt` | Python dependencies (numpy, pytest, pytest-cov) |
| `README.md` | This documentation |

---

## Key Concepts

**F_theo (Theoretical Design Space)**: The full space of possible designs. Systems that expand F_theo can discover fundamentally new types of solutions.

**F_eff (Effective Design Space)**: The subset of F_theo actually reachable by the search algorithm. MAP-Elites and LLM-guided search expand F_eff within a given F_theo.

**Design Space Escape**: When the meta-grammar layer creates new vocabulary or grammar rules, the system escapes its previous design space into a larger one.

**Cost Grounding**: Physical resource constraints prevent unbounded complexity growth and ensure solutions remain practical.

---

## License

MIT
