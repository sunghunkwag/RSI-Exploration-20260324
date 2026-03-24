# RSI-Exploration: Recursive Self-Improvement via Design Space Self-Expansion

A hybrid architecture that combines **Darwin Godel Machine (DGM)** self-improvement loops with **MAP-Elites** quality-diversity search to implement a three-layer design space expansion system with physical cost grounding.

> **Core thesis**: Genuine recursive self-improvement requires not just better search within a fixed space (*F_eff* expansion), but the ability to expand the space of possible designs itself (*F_theo* expansion). This system implements both.

---

## Motivation

Most evolutionary and meta-learning systems operate within a fixed design space — they improve *how* they search, but not *what* they can search over. This limits their ability to discover qualitatively new solutions.

This work addresses the following question:

> *Can a self-improving system autonomously expand its own design vocabulary and composition rules, and does this lead to qualitatively better solutions than fixed-space search?*

The architecture is grounded in two empirically validated open-source systems:
- **[guillaumepourcel/dgm](https://github.com/guillaumepourcel/dgm)** — Darwin Godel Machine: genuine recursive self-improvement with benchmark-grounded evaluation
- **[b-albar/evolve-anything](https://github.com/b-albar/evolve-anything)** — LLM-driven MAP-Elites evolutionary code optimization

This repository synthesizes their core mechanisms into a unified, dependency-minimal Python implementation.

---

## Key Concepts

### F_theo vs F_eff

| Concept | Definition | How This System Addresses It |
|---|---|---|
| **F_eff** (Effective Design Space) | The subset of all possible designs reachable by the current search algorithm | Expanded via MAP-Elites quality-diversity archive |
| **F_theo** (Theoretical Design Space) | The full space of designs the system is *capable* of representing | Expanded via Meta-Grammar layer at runtime |

**Design Space Escape** occurs when the Meta-Grammar layer synthesizes new vocabulary primitives or composition rules, pushing F_theo beyond its previous boundaries.

### Physical Cost Grounding

Every candidate is evaluated under a hard resource budget:

```
grounded_fitness = raw_fitness × cost_score
cost_score = 1 / (1 + compute_fraction + time_fraction)
```

This prevents bloat and rewards parsimonious solutions — a solution must be both correct *and* efficient to dominate the archive.

---

## Architecture

The system operates across three self-expanding layers:

```
┌─────────────────────────────────────────────────┐
│  Layer 3: Meta-Grammar                          │
│  Generates new grammar rules & vocab primitives │
│  → expands F_theo at runtime                    │
├─────────────────────────────────────────────────┤
│  Layer 2: Grammar                               │
│  Composition rules: mutation, crossover, hoist  │
│  → defines how vocabulary is combined           │
├─────────────────────────────────────────────────┤
│  Layer 1: Vocabulary                            │
│  Primitive operations: add, mul, square, ...    │
│  → atomic building blocks                       │
└─────────────────────────────────────────────────┘
```

### Self-Improvement Loop (DGM-inspired)

Each generation:
1. Sample parent from MAP-Elites archive
2. Apply grammar mutation (including meta-grammar-expanded rules)
3. Evaluate under physical cost budget
4. Insert into archive if the candidate dominates its behavioral cell
5. Every N generations: expand design space via meta-grammar

### MAP-Elites Archive

Instead of a single best solution, the archive maintains a grid indexed by behavioral descriptors (expression depth × expression size). This preserves structural diversity and prevents premature convergence to a single local optimum.

---

## Results

Running 50 generations × 20 population on symbolic regression (target: *f(x) = x² + 2x + 1*):

| Metric | Gen 1 | Gen 50 |
|---|---|---|
| Best grounded fitness | 0.0955 | **0.9996** |
| Archive coverage | 8.3% | 33.3% |
| Vocabulary size | 11 | 13 (+2 auto-synthesized) |
| Grammar rules | 4 | 7 (+3 auto-generated) |
| Design space expansions | 0 | 5 |

The system autonomously synthesized 2 new vocabulary primitives and 3 new mutation strategies during the run — without any external intervention.

---

## Installation

```bash
git clone https://github.com/sunghunkwag/RSI-Exploration-20260324.git
cd RSI-Exploration-20260324
pip install -r requirements.txt
```

**Requirements**: Python 3.8+, numpy, pytest (no ML framework dependencies)

---

## Usage

### Run default experiment

```bash
python main.py
```

### Run test suite

```bash
pytest test_main.py -v
```

### Custom fitness function

```python
from main import build_rsi_system, ExprNode, VocabularyLayer, _eval_tree
import numpy as np

def my_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    xs = np.linspace(0, 10, 50)
    error = sum(abs(_eval_tree(tree, vocab, x) - np.sin(x)) for x in xs)
    return 1.0 / (1.0 + error / len(xs))

engine = build_rsi_system(fitness_fn=my_fitness)
history = engine.run(generations=200, population_size=30)
print(f"Best fitness: {engine.archive.best_fitness:.4f}")
print(f"Vocab expanded to: {engine.vocab.size} primitives")
```

---

## File Structure

| File | Description |
|---|---|
| `main.py` | Core architecture: all layers, cost grounding, MAP-Elites, self-improvement engine |
| `test_main.py` | Pytest test suite covering all components |
| `requirements.txt` | Minimal dependencies (numpy, pytest) |

---

## Limitations and Open Questions

This is an early-stage prototype. Known limitations:

- **Coverage ceiling**: Archive coverage stabilizes at ~33% after Gen 21. The meta-grammar expansion does not yet sufficiently diversify behavioral descriptors.
- **Single domain**: Results are demonstrated on symbolic regression only. Generalization across domains remains to be tested.
- **Shallow self-modification**: The system modifies its *operators* and *rules*, but not its own learning algorithm. True Godel Machine-level self-modification (modifying the search procedure itself) is a natural next step.

---

## Related Work

- Lehman & Stanley (2011) — *Abandoning Objectives: Evolution Through the Search for Novelty Alone*
- Clune et al. (2019) — *AI-GAs: AI-generating algorithms*
- Kirsh (2024) — *Darwin Godel Machine*
- Mouret & Clune (2015) — *Illuminating search spaces by mapping elites*

---

## License

MIT
