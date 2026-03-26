# RSI Verification Report: Does Recursive Self-Improvement Actually Work?

**Date**: 2026-03-26
**System**: MAP-Elites + DreamCoder-inspired Library Learning + OpFitnessTracker
**Repository**: github.com/sunghunkwag/RSI-Exploration-20260324

---

## Executive Summary

After multiple rounds of testing and honest failure analysis, **library learning
produces genuine recursive self-improvement on tasks that require depth
amplification**. On the original sin(x) target, the effect is neutral (both
conditions already saturate). No trial mechanism, no exploration bonus, no
library-insert mutation — these were all removed as unnecessary scaffolding.

---

## Methodology

### What Was Changed (Legitimate Fixes Only)

1. **Depth Enforcement** (bug fix): Mutations that produce trees exceeding
   `max_depth` are now rejected. Without this, crossover/mutation routinely
   exceeded the depth limit, making the depth constraint meaningless and
   library learning's depth amplification invisible.

2. **Adaptive min_frequency** (sparse-archive heuristic): When the archive has
   fewer than 20 elites, `min_frequency` for subtree extraction is lowered
   from 2 to 1. This allows library learning to bootstrap from small archives
   where identical subtrees rarely recur across different elites.

3. **OpFitnessTracker** (credit assignment): Tracks per-op fitness contribution
   (mean fitness of elites WITH op vs WITHOUT). Used for fitness-driven
   sampling weights and pruning of harmful ops.

4. **Fitness-weighted extraction**: Library extraction scores candidates by
   elite fitness, not just raw frequency. Only elites above median fitness
   contribute subtrees.

### What Was Removed (Shown Unnecessary or Harmful)

- **Trial mechanism** (`_generate_trial_trees`): Hand-designed compositions
  tested immediately after extraction. Empirically shown to be unnecessary —
  library extraction alone achieves the same or better results. Removed.
- **Library-insert mutation** (`_rule_library_insert`): Directed mutation that
  forces library op insertion. Not needed. Removed.
- **Exploration bonus** (3x weight for new ops): Reverted to default weight.

### Experimental Design

Three conditions tested on each target:

| Condition | Library Learning | OpFitnessTracker | Expansion |
|-----------|-----------------|------------------|----------|
| A) FROZEN | OFF | OFF | Never |
| B) LIB-ONLY | ON | OFF | Every 10 gen |
| C) LIB+TRACKER | ON | ON | Every 10 gen |

All conditions use depth enforcement (bug fix applied equally).

Parameters: 10 seeds × {200 or 100} generations × 30 population size.

---

## Results

### Test 1: x⁵ (quintic) at max_depth=2

The base vocabulary can reach polynomial degree 4 at depth 2. x⁵ is
unreachable without depth amplification.

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.4778 | 0.0105 | — |
| B) LIB-ONLY | 0.6585 | 0.2737 | 8/10 |
| C) LIB+TRACKER | 0.8003 | 0.2587 | 9/10 |

**Library extraction effect (B-A): +0.1808**
**Full RSI effect (C-A): +0.3226**
**Tracker added value (C-B): +0.1418**

### Test 2: x⁷ (septic) at max_depth=2

Even harder — degree 7 is far beyond the depth-2 ceiling of degree 4.

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.2569 | 0.0389 | — |
| B) LIB-ONLY | 0.8814 | 0.2116 | 9/10 |
| C) LIB+TRACKER | 0.7493 | 0.2653 | 8/10 |

**Library extraction effect (B-A): +0.6245**
**Full RSI effect (C-A): +0.4924**
**Tracker added value (C-B): −0.1321** (tracker hurts here)

### Test 3: sin(x) (original) at max_depth=3

The original target. Both FROZEN and RSI already saturate near 0.999.

| Condition | Mean Fitness | Std | Wins vs FROZEN |
|-----------|-------------|-----|----------------|
| A) FROZEN | 0.9858 | 0.0411 | — |
| B) LIB-ONLY | 0.9761 | 0.0711 | 1/10 |
| C) LIB+TRACKER | 0.9997 | 0.0002 | 1/10 |

**Library extraction effect (B-A): −0.0097** (slight regression)
**Full RSI effect (C-A): +0.0140** (neutral)

---

## Mechanism: How RSI Works

The verified chain of self-improvement on x⁵:

```
Generation  10: Elite = mul(identity(x), square(x)) = x³  [fitness 0.47]
                Library extracts x³ subtree → lib_x3 (depth 0)
Generation  40: Evolution creates mul(lib_x3(x), square(x)) = x⁵ [fitness 0.99]
                Library extracts x⁵ subtree → lib_x5 (depth 0)
Generation  50: lib_x5(x) = x⁵ at depth 1 [fitness 0.9998]
```

This is genuine depth amplification:
- Round 1: depth-2 subtree (x³) compressed to depth-0 op
- Round 2: depth-2 composition (x³ × x²) compressed again
- Result: x⁵ reachable at depth 1, which was impossible with base vocabulary

---

## Honest Assessment

### What Works
- Library extraction + depth amplification is a **real mechanism** that
  genuinely expands the reachable design space under depth constraints.
- On problems where depth is the bottleneck (x⁵, x⁷ at depth 2), RSI
  provides a large, consistent advantage.
- The recursive chain (extract → compose → extract again) is verified.

### What Doesn't Work (or Is Ambiguous)
- **OpFitnessTracker**: Mixed results. Helps on x⁵ (+0.14), hurts on x⁷
  (−0.13), neutral on sin(x). The tracker's credit assignment may be too
  noisy with small archives. Net contribution is uncertain.
- **High variance**: LIB-ONLY and LIB+TRACKER have high std (0.21–0.27),
  meaning some seeds fail to extract the right building block. This is a
  stochastic search — not every run succeeds.
- **sin(x)**: No improvement. The problem is too easy for depth-3 search;
  library learning adds nothing when the base vocabulary suffices.
- **LIB-ONLY sometimes beats LIB+TRACKER**: On x⁷, pure frequency-based
  extraction outperforms fitness-weighted extraction. The tracker's sampling
  bias may interfere with diversity.

### Limitations
- The test problems are synthetic. Real-world symbolic regression has
  different structure.
- The ExprNode representation is NOT Turing-complete (no loops, conditionals).
  This bounds the class of problems where RSI can help.
- Depth amplification is the ONLY verified RSI mechanism. The system does not
  discover new algorithms, control structures, or representations.
- The adaptive min_frequency=1 heuristic is necessary for bootstrapping but
  may extract poor building blocks in some seeds (explaining the high variance).

### What Was NOT Hardcoded
- No target-specific logic in extraction or mutation
- No hand-crafted compositions — the system discovers mul(lib_x3, square)
  through normal evolutionary search
- The same code works on both x⁵ and x⁷ without modification
- The trial mechanism was shown unnecessary and removed

---

## Conclusion

**RSI works, specifically and narrowly, as depth amplification via library
learning.** When the depth constraint is the bottleneck, extracting subtrees
from elites and reusing them as building blocks genuinely enables solutions
that were previously unreachable. The recursive chain (extract → compose →
extract) is verified on multiple targets.

The effect is **absent** when the problem is already solvable within the depth
limit (sin(x) at depth 3). RSI is not a universal performance booster — it
helps only when the search space is depth-constrained and the target requires
compositions beyond what base primitives can reach at the allowed depth.
