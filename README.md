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

This repository synthesizes their core mechanisms into a unified, dependency-minimal Python implementation, augmented with mechanisms discovered through a 10-session cross-domain Design Space Escape Protocol.

---

## Key Concepts

### F_theo vs F_eff

| Concept | Definition | How This System Addresses It |
|---|---|---|
| **F_eff** (Effective Design Space) | The subset of all possible designs reachable by the current search algorithm | Expanded via MAP-Elites quality-diversity archive + novelty rejection sampling |
| **F_theo** (Theoretical Design Space) | The full space of designs the system is *capable* of representing | Expanded via Meta-Grammar layer, Library Learning, Self-Reference, and Context-Dependent Evaluation at runtime |

**Design Space Escape** occurs when the system synthesizes new vocabulary primitives, composition rules, or evaluation mechanisms, pushing F_theo beyond its previous boundaries.

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
│  + Library Learning (DreamCoder-inspired)        │
│  → expands F_theo at runtime                    │
├─────────────────────────────────────────────────┤
│  Layer 2: Grammar                               │
│  Composition rules: mutation, crossover, hoist  │
│  → defines how vocabulary is combined           │
├─────────────────────────────────────────────────┤
│  Layer 1: Vocabulary                            │
│  Primitive operations: add, mul, square, ...    │
│  + self_encode, PolymorphicOps                  │
│  → atomic building blocks                       │
└─────────────────────────────────────────────────┘
```

### Self-Improvement Loop (DGM-inspired)

Each generation:

1. Sample parent from MAP-Elites archive
2. Apply grammar mutation (including meta-grammar-expanded rules)
3. Evaluate under physical cost budget with optional evaluation context
4. Insert into archive if the candidate dominates its behavioral cell (subject to novelty screening)
5. Every N generations: expand design space via meta-grammar and/or library learning

### MAP-Elites Archive

Instead of a single best solution, the archive maintains a grid indexed by behavioral descriptors (expression depth × expression size). This preserves structural diversity and prevents premature convergence to a single local optimum. The `EnhancedMAPElitesArchive` adds novelty injection into empty neighbor cells and fingerprint-based novelty rejection sampling to further mitigate coverage ceilings.

---

## F_theo Expansion Mechanisms

Through a 10-session cross-domain Design Space Escape Protocol spanning 8 academic domains (Mathematics, Physics, Linguistics, Computer Science, Music, Architecture, Philosophy, Representation Theory), 60 formal structure extractions were performed, yielding 7 distinct mechanism families for genuine F_theo expansion. Two Tier-1 mechanisms have been implemented:

### Mechanism 1: Self-Reference

**Sources:** Diagonal Lemma (A.7), Quines/Kleene (D.1), Gödel Machines (D.7)

The `self_encode` built-in op allows expression trees to reference their own structural encoding. When evaluated with an `EvalContext`, `self_encode` returns a deterministic float derived from the tree's fingerprint, enabling fixed-point computations where `T(⌜T⌝) = T`. Non-self-referential trees cannot compute functions that depend on their own identity, so this strictly expands F_theo.

### Mechanism 2: Context-Dependent Evaluation

**Sources:** Kāraka (C.1c), Aramaic polysemy (C.3), Cuneiform (C.4), Topos Theory (G.6), Reflection (D.4)

`EvalContext` threads niche, generation, and environment information through evaluation. `PolymorphicOp` dispatches to different functions based on context state (up to 4 context keys). A context-free tree with n ops computes a fixed function per node; a context-dependent tree can compute up to n×k functions per node, strictly expanding F_theo for k > 1.

### Library Learning (DreamCoder-inspired)

**Source:** Ellis et al. (PLDI 2021) — DreamCoder wake-sleep library learning

The `LibraryLearner` scans elite trees for frequently recurring subtrees, extracts them as new primitive operations, and registers them in the vocabulary. This breaks the depth ceiling: a depth-K subtree promoted to a single primitive allows a depth-D tree to express computations previously requiring depth D+K. Unlike random meta-grammar composition, library learning discovers semantically meaningful multi-step computations from successful programs.

### Novelty Rejection Sampling

**Source:** b-albar/evolve-anything (NoveltyJudge)

The `NoveltyScreener` computes structural Jaccard similarity between candidate trees and archive members using subtree fingerprint sets. Candidates above a similarity threshold are rejected before archive insertion, forcing the evolutionary search to produce genuinely novel structures.

---

## Results

### Multi-Domain Experiment

Running 50 generations × 20 population with `EnhancedMAPElitesArchive` + Library Learning across 4 fitness domains:

| Domain | Target Function | Coverage | Best Fitness |
|---|---|---|---|
| Symbolic Regression | f(x) = x² + 2x + 1 | ~39-44% | ~0.999 |
| Sine Approximation | f(x) = sin(x) | ~39-44% | varies |
| Absolute Value | f(x) = \|x\| | ~39-44% | varies |
| Cubic | f(x) = x³ - x | ~39-44% | varies |

### Single-Domain Baseline (Symbolic Regression)

| Metric | Gen 1 | Gen 50 |
|---|---|---|
| Best grounded fitness | 0.0955 | **0.9996** |
| Archive coverage (standard) | 8.3% | 33.3% |
| Archive coverage (enhanced) | — | 38.5–43.8% |
| Vocabulary size | 11 | 13+ (auto-synthesized + library-learned) |
| Grammar rules | 4 | 7+ (auto-generated) |
| Design space expansions | 0 | 5+ |

The `EnhancedMAPElitesArchive` with novelty injection and rejection sampling raises the coverage ceiling from ~33% to ~39-44% compared to the standard archive.

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

### Run multi-domain experiment

```bash
python main.py
```

This runs all 4 fitness domains (symbolic regression, sine approximation, absolute value, cubic) with the enhanced archive and library learning enabled.

### Run test suite

```bash
pytest test_main.py -v
```

62 tests covering all components including self-reference, context-dependent evaluation, library learning, novelty screening, and enhanced archive integration.

### Custom fitness function

```python
from main import build_rsi_system, ExprNode, VocabularyLayer, _eval_tree
import numpy as np

def my_fitness(tree: ExprNode, vocab: VocabularyLayer) -> float:
    xs = np.linspace(0, 10, 50)
    error = sum(abs(_eval_tree(tree, vocab, x) - np.sin(x)) for x in xs)
    return 1.0 / (1.0 + error / len(xs))

engine = build_rsi_system(
    fitness_fn=my_fitness,
    use_enhanced_archive=True,
    use_library_learning=True,
)
history = engine.run(generations=200, population_size=30)
print(f"Best fitness: {engine.archive.best_fitness:.4f}")
print(f"Vocab expanded to: {engine.vocab.size} primitives")
```

### Factory parameters

`build_rsi_system()` accepts configuration for all subsystems:

| Parameter | Default | Description |
|---|---|---|
| `fitness_fn` | symbolic_regression | Evaluation function (tree, vocab) → float in [0, 1] |
| `max_depth` | 5 | Maximum expression tree depth |
| `archive_dims` | [6, 10] or [8, 12] | MAP-Elites grid dimensions |
| `use_enhanced_archive` | False | Use EnhancedMAPElitesArchive with novelty injection |
| `use_library_learning` | False | Enable DreamCoder-inspired library learning |
| `similarity_threshold` | 0.85 | Jaccard threshold for novelty rejection sampling |
| `expansion_interval` | 10 | Generations between meta-grammar expansions |

---

## File Structure

| File / Directory | Description |
|---|---|
| `main.py` | Core architecture: vocabulary, grammar, meta-grammar, library learner, cost grounding, MAP-Elites (standard + enhanced), novelty screener, self-improvement engine, fitness functions, factory |
| `test_main.py` | 62 pytest tests covering all components |
| `requirements.txt` | Minimal dependencies (numpy, pytest) |
| `docs/synthesis.md` | Cross-domain synthesis: 7 mechanism families from 60 extractions |
| `docs/daily-log.md` | Session-by-session development log (Sessions 1–10) |
| `docs/session-tracker.md` | Session completion status tracker |
| `docs/monitoring-log.md` | Literature monitoring log |
| `docs/domains/` | 8 domain investigation reports (A–H) |

---

## Design Space Escape Protocol

This project followed a structured 10-session research protocol:

| Session | Domain | Extractions | STRUCTURAL | Key Finding |
|---|---|---|---|---|
| 1 | Mathematics | 7 | 6 | Self-reference is the master cage-breaker |
| 2 | Physics | 9 | 4 | Dualities are isomorphisms, not expansions |
| 3 | Linguistics | 8 | 5 | Context-dependent evaluation from ancient texts |
| 4 | Computer Science | 8 | 5 | Quines → Gödel Machines progression |
| 5 | Music | 6 | 4 | Cross-domain convergence dominates |
| 6 | Architecture | 7 | 2 | Search efficiency ≠ expressibility |
| 7 | Philosophy | 7 | 2 | Topos theory grounds context-dependent eval |
| 8 | Representation Theory | 8 | 5 | Richest domain (operads, categorification) |
| 9 | Synthesis | — | — | 7 mechanism families identified |
| 10 | Build | — | — | Tier 1 mechanisms implemented (62/62 tests) |

**Aggregate:** 60 extractions, 33 STRUCTURAL_EXPANSION (55%), 23 COMBINATORIAL_RECOMBINATION (38%), 3 NO_STRUCTURE (5%). Full details in `docs/synthesis.md`.

---

## Limitations and Open Questions

This is an early-stage prototype. Known limitations:

- **Coverage ceiling (mitigated)**: Standard archive coverage stabilizes at ~33%. The `EnhancedMAPElitesArchive` raises this to ~39-44%, but further improvement requires richer behavioral descriptors.
- **Shallow self-modification**: The system modifies its *operators*, *rules*, and *evaluation context*, but not its own learning algorithm. True Gödel Machine-level self-modification (modifying the search procedure itself) remains a natural next step.
- **Tier 2+ mechanisms not yet implemented**: Operadic meta-grammar formalization (Mechanism 3), preference-based rule selection (Mechanism 5), continuous primitives (Mechanism 4), categorification (Mechanism 6), and bidirectional abstraction (Mechanism 7) are identified but not yet built.
- **Approximate F_theo expansion results**: The multi-domain results are stochastic; exact coverage and fitness vary by random seed.

---

## Related Work

- Lehman & Stanley (2011) — *Abandoning Objectives: Evolution Through the Search for Novelty Alone*
- Clune et al. (2019) — *AI-GAs: AI-generating algorithms*
- Kirsh (2024) — *Darwin Godel Machine*
- Mouret & Clune (2015) — *Illuminating search spaces by mapping elites*
- Ellis et al. (2021) — *DreamCoder: bootstrapping inductive program synthesis with wake-sleep library learning*
- Shutt (1993) — *Adaptive grammars*

---

## License

MIT
