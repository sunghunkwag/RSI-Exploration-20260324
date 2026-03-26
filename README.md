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
| `test_main.py` | 175 tests — all core mechanisms including V4/V5, library learning, OpFitnessTracker |
| `test_omega_backend.py` | 56 tests — VM, compiler, CFG, fitness, integration |
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

**Test 1: x⁵ (quintic) at max_depth=2** — requires depth amplification (base vocab caps at degree 4)

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.4778 | 0.0105 | — |
| B) LIB-ONLY | 0.6585 | 0.2737 | 8/10 |
| C) LIB+TRACKER | 0.8003 | 0.2587 | 9/10 |

**Test 2: x⁷ (septic) at max_depth=2** — far beyond the depth-2 ceiling

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.2569 | 0.0389 | — |
| B) LIB-ONLY | 0.8814 | 0.2116 | 9/10 |
| C) LIB+TRACKER | 0.7493 | 0.2653 | 8/10 |

**Test 3: sin(x) at max_depth=3** — solvable without library learning (ceiling effect)

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.9858 | 0.0411 | — |
| B) LIB-ONLY | 0.9761 | 0.0711 | 1/10 |
| C) LIB+TRACKER | 0.9997 | 0.0002 | 1/10 |

### Verified RSI Mechanism

```
Gen 10:  Elite = mul(identity(x), square(x)) = x³  [fitness 0.47]
         Library extracts x³ subtree → lib_x3 (depth 0)
Gen 40:  Evolution creates mul(lib_x3(x), square(x)) = x⁵  [fitness 0.99]
         Library extracts x⁵ subtree → lib_x5 (depth 0)
Gen 50:  lib_x5(x) = x⁵ at depth 1  [fitness 0.9998]
```

### Verdict

**RSI works, specifically and narrowly, as depth amplification via library learning.** When the depth constraint is the bottleneck, extracting subtrees from elites and compressing them into single ops genuinely enables solutions that were previously unreachable. The recursive chain (extract → compose → extract) is verified on multiple targets.

The effect is **absent** when the problem is already solvable within the depth limit. RSI is not a universal performance booster — it helps only when the search space is depth-constrained and the target requires compositions beyond what base primitives can reach.

See [`docs/rsi-verification-report.md`](docs/rsi-verification-report.md) for full methodology, honest limitations, and what was removed as unnecessary scaffolding.

## Usage

```bash
pip install numpy pytest
python main.py                          # Run multi-domain experiment (interpreter + VM backends)
pytest test_main.py test_omega_backend.py -v  # 150 tests (core + VM)
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
