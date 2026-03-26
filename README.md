# RSI-Exploration

> **Experimental repository.** Research prototype for recursive self-improvement via design space self-expansion.

## Overview

This system investigates whether an evolutionary architecture can autonomously expand its own representational capacity (*F_theo*), not merely optimize within a fixed design space (*F_eff*). It combines a Darwin Gödel Machine-inspired self-improvement loop with MAP-Elites quality-diversity search across a three-layer self-expanding architecture (Vocabulary → Grammar → Meta-Grammar), grounded by physical cost budgets.

The project follows a 10-session Design Space Escape Protocol spanning 8 academic domains (Mathematics, Physics, Linguistics, Computer Science, Music, Architecture, Philosophy, Representation Theory), yielding 60 formal structure extractions and 7 mechanism families for *F_theo* expansion.

## Architecture

**Three-layer design space:**

- **Layer 1 — Vocabulary**: Primitive ops (`add`, `mul`, `square`, `self_encode`, `PolymorphicOp`, ...) with refinement type annotations (`OpType` subtype lattice: unit ⊂ non_negative ⊂ real ⊂ any`).
- **Layer 2 — Grammar**: Typed composition rules (mutation, crossover, hoist) with type-checking at construction time.
- **Layer 3 — Meta-Grammar**: Paribhāṣā-inspired deterministic meta-rule selection (specificity scoring + preconditions), operadic HyperRule templates (`binary_lift`, `binary_partial`, `unary_chain`), and DreamCoder-inspired library learning.

**Evaluation paths:**

- **Tree interpreter** (`_eval_tree`): Direct recursive evaluation with topological context threading (`EvalContext.topo_key()`, `PolymorphicOp.topo_dispatch`).
- **Omega VM backend** (`omega_backend.py`): Compiles `ExprNode` trees to 8-register VM instructions via `ExprNodeCompiler`, executes on `VirtualMachine` with memory/call-stack/control-flow, and analyzes execution traces via `ControlFlowGraph` (Kosaraju SCC, canonical hashing).

**Key mechanisms implemented:** self-reference (diagonal lemma), context-dependent evaluation (topos-theoretic), refinement types (dependent types D.5), deterministic meta-rule selection (Paribhāṣā C.1b), operadic meta-grammar (H.8), library learning (Ellis et al. 2021), novelty rejection sampling, enhanced MAP-Elites with novelty injection.

## Files

| File | Description |
|---|---|
| `main.py` | Core RSI engine (~2000 lines): 3-layer architecture, MAP-Elites, OpFitnessTracker, library learning, depth enforcement |
| `omega_backend.py` | Omega VM backend (~700 lines): instruction set, VM, CFG analysis, ExprNode compiler, VM fitness |
| `test_main.py` | 153 tests — all core mechanisms including V4/V5, library learning, OpFitnessTracker, depth enforcement |
| `test_omega_backend.py` | 32 tests — VM, compiler, CFG, fitness, integration |
| `test_rsi_verification.py` | RSI verification: FROZEN vs SELF-MODIFY controlled experiment on x^2+2x+1 (5 seeds x 2 conditions x 500 gen) |
| `test_rsi.py` | RSI verification on hard targets: sin(x) approximation at depth=3 and depth=5 with convergence analysis |
| `test_v4_evolution.py` | V4 integration test: self_encode reachability, PolymorphicOp generation, elite utilization (5 seeds x 200 gen) |
| `test_v5_isomorphism.py` | V5 format isomorphism test: F_theo enumeration at depth 1, baseline vs +self_encode (14 -> 42 distinct functions) |
| `run_ablation.py` | Reproducible ablation study: FROZEN vs LIB-ONLY vs LIB+TRACKER on quintic, septic, sin(x) |
| `docs/rsi-verification-report.md` | Full RSI verification report with methodology, results, mechanism analysis, and honest limitations |
| `docs/` | Synthesis report, daily log, monitoring log, session tracker, domain investigations (A-H) |

## RSI Verification Results

### Ablation Study (March 2026)

Three conditions tested across multiple targets (10 seeds × 200 generations × 30 population):

| Condition | Library Learning | OpFitnessTracker | Op Expansion |
|-----------|-----------------|------------------|---------------|
| A) FROZEN | OFF | OFF | Never |
| B) LIB-ONLY | ON | OFF | Every 10 gen |
| C) LIB+TRACKER | ON | ON | Every 10 gen |

All conditions use depth enforcement (bug fix: `max_depth` is now enforced in `mutate()` and `crossover()`, not just `random_tree()`).

**Test 1: x⁵ (quintic) at max_depth=2** — requires depth amplification (base vocab caps at degree 4)

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.1853 | 0.0324 | — |
| B) LIB-ONLY | 0.2003 | 0.0590 | 2/10 |
| C) LIB+TRACKER | 0.1968 | 0.0431 | 2/10 |

Delta B-A: +0.0151, Delta C-A: +0.0115. **NEUTRAL** (< 0.05 threshold).

**Test 2: x⁷ (septic) at max_depth=2** — far beyond the depth-2 ceiling

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.0532 | 0.0004 | — |
| B) LIB-ONLY | 0.0548 | 0.0033 | 1/10 |
| C) LIB+TRACKER | 0.0558 | 0.0087 | 1/10 |

Delta B-A: +0.0016, Delta C-A: +0.0027. **NEUTRAL**.

**Test 3: sin(x) at max_depth=3** — solvable without library learning

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.6761 | 0.0383 | — |
| B) LIB-ONLY | 0.7014 | 0.0339 | 3/10 |
| C) LIB+TRACKER | 0.6993 | 0.0482 | 4/10 |

Delta B-A: +0.0253, Delta C-A: +0.0233. **NEUTRAL**.

### Honest Assessment

**The RSI effect is not statistically significant on any target tested.** All deltas are below the 0.05 threshold. The previous README claimed results (FROZEN 0.48, LIB-ONLY 0.66, LIB+TRACKER 0.80 on quintic) that were produced by code that lacked depth enforcement — without the depth ceiling, FROZEN could already reach high-degree polynomials via unconstrained mutation, making the comparison meaningless.

**Root cause**: Library learning correctly extracts subtrees (e.g., x³) and makes them available as single ops, but the evolutionary search fails to discover the right compositions (e.g., `mul(lib_x3, square)`) within the generation budget. With 12+ ops in the vocabulary, the probability of randomly composing the correct 2-op tree is approximately 1/(12×12) per trial, and library ops further dilute the sampling distribution.

**What works**: The depth enforcement bug fix itself is verified — FROZEN at max_depth=2 correctly caps at fitness ~0.17 on quintic (degree 4 maximum), confirming the bottleneck exists.

**What doesn't work yet**: The evolutionary search cannot reliably exploit library ops to overcome the bottleneck. Potential improvements include larger populations, more generations, or smarter op selection (the OpFitnessTracker is implemented but shows no measurable benefit at current scale).

See [`docs/rsi-verification-report.md`](docs/rsi-verification-report.md) for full methodology and limitations.

## Usage

```bash
pip install numpy pytest
python main.py                          # Run multi-domain experiment (interpreter + VM backends)
pytest test_main.py test_omega_backend.py -v  # 185 tests (core + VM)
pytest test_rsi_verification.py test_rsi.py   # RSI verification experiments
pytest test_v4_evolution.py test_v5_isomorphism.py  # V4/V5 mechanism verification
```

```python
from main import build_rsi_system

# Tree interpreter backend (default)
engine = build_rsi_system(use_enhanced_archive=True, use_library_learning=True)

# Omega VM compilation backend
engine = build_rsi_system(use_vm_backend=True, vm_fitness_name="vm_symbolic_regression")

engine.run(generations=50, population_size=20)
```

## References

Kirsh (2024) — Darwin Gödel Machine; Mouret & Clune (2015) — MAP-Elites; Ellis et al. (2021) — DreamCoder; Lehman & Stanley (2011) — Novelty Search; b-albar/evolve-anything; guillaumepourcel/dgm.

## License

MIT
