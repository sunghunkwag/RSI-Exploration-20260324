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
| `main.py` | Core RSI engine (~1600 lines): 3-layer architecture, MAP-Elites, cost grounding, fitness registry |
| `omega_backend.py` | Omega VM backend (~700 lines): instruction set, VM, CFG analysis, ExprNode compiler, VM fitness |
| `test_main.py` | 94 tests — all core mechanisms including V4/V5 verification |
| `test_omega_backend.py` | 56 tests — VM, compiler, CFG, fitness, integration |
| `test_rsi_verification.py` | RSI verification: FROZEN vs SELF-MODIFY controlled experiment on x^2+2x+1 (5 seeds x 2 conditions x 500 gen) |
| `test_rsi.py` | RSI verification on hard targets: sin(x) approximation at depth=3 and depth=5 with convergence analysis |
| `test_v4_evolution.py` | V4 integration test: self_encode reachability, PolymorphicOp generation, elite utilization (5 seeds x 200 gen) |
| `test_v5_isomorphism.py` | V5 format isomorphism test: F_theo enumeration at depth 1, baseline vs +self_encode (14 -> 42 distinct functions) |
| `docs/` | Synthesis report, daily log, monitoring log, session tracker, domain investigations (A-H) |

## RSI Verification Results

Controlled experiments comparing FROZEN (no self-modification) vs SELF-MODIFY conditions:

| Test | Target | Depth | Delta (MODIFY - FROZEN) | Verdict |
|---|---|---|---|---|
| #1 | x^2+2x+1 | 5 | +0.0002 | SELF_MODIFICATION_WITHOUT_IMPROVEMENT (target too easy) |
| #2a | sin(x) | 3 | -0.0163 | No improvement (depth too constrained) |
| #2b | sin(x) | 5 | +0.0151 | **IMPROVEMENT CONFIRMED** |

**Verdict: RECURSIVE_SELF_IMPROVEMENT_CONFIRMED (conditional)** — works on hard targets with sufficient depth. Self-modification acts as a convergence accelerator rather than a ceiling breaker.

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
