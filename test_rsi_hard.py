"""
RSI 검증 테스트 #2: 어려운 타겟에서의 재귀적 자가 개선
=====================================================

이전 테스트에서 x²+2x+1은 기본 op으로 이미 해결 가능하여
자가 개선 이점이 드러나지 않았음.

이번 테스트:
1. 타겟: sin(x) — 기본 op(add, mul, square)으로 정확히 표현 불가
   → 자가 수정이 Taylor 급수 항을 합성하여 근사해야 함
2. max_depth=3 — 얌은 트리 강제 → library learning의 depth amplification 필수
3. 500 generations × 5 seeds × 2 conditions
"""

import random
import numpy as np
import math
import logging
import sys
import time

sys.path.insert(0, '/sessions/blissful-determined-brahmagupta/RSI-Exploration')
logging.disable(logging.INFO)

from main import (
    VocabularyLayer, GrammarLayer, MetaGrammarLayer,
    LibraryLearner, ResourceBudget, CostGroundingLoop,
    MAPElitesArchive, EliteEntry, SelfImprovementEngine,
    build_rsi_system, sine_approximation_fitness,
    _eval_tree, EvalContext, PolymorphicOp, ExprNode
)


def _collect_ops(node, ops_set):
    ops_set.add(node.op_name)
    for c in node.children:
        _collect_ops(c, ops_set)


def run_hard_experiment(seed, generations, pop_size, expansion_interval,
                        max_depth, fitness_fn, label):
    random.seed(seed)
    np.random.seed(seed)

    engine = build_rsi_system(
        fitness_fn=fitness_fn,
        max_depth=max_depth,
        budget_ops=100_000,
        budget_seconds=60.0,
        expansion_interval=expansion_interval,
        use_library_learning=True,
        library_min_depth=2,
        library_min_freq=2,
        library_max_additions=3,
    )

    base_ops = {op.name for op in engine.vocab.all_ops()}
    trajectory = []
    best_at = {0.2: None, 0.3: None, 0.4: None, 0.5: None, 0.6: None, 0.7: None}

    for gen in range(generations):
        record = engine.step(pop_size)

        current_ops = {op.name for op in engine.vocab.all_ops()}
        generated_ops = current_ops - base_ops
        poly_ops = {op.name for op in engine.vocab.all_ops()
                    if isinstance(op, PolymorphicOp)}

        elites = list(engine.archive._grid.values())
        elites_using_gen = sum(1 for e in elites
                              if _get_tree_ops(e.tree) & generated_ops)

        # 수렴 속도 추적
        for thresh in best_at:
            if best_at[thresh] is None and record["archive_best"] >= thresh:
                best_at[thresh] = gen + 1

        if (gen + 1) % 50 == 0 or gen == 0:
            trajectory.append({
                "gen": gen + 1,
                "best": record["archive_best"],
                "coverage": record["archive_coverage"],
                "vocab": record["vocab_size"],
                "gen_ops": len(generated_ops),
                "poly": len(poly_ops),
                "util": elites_using_gen / max(len(elites), 1),
                "rules": record["grammar_rules"],
            })

    return {
        "label": label,
        "seed": seed,
        "trajectory": trajectory,
        "best_at": best_at,
        "final_best": trajectory[-1]["best"],
        "final_vocab": trajectory[-1]["vocab"],
        "final_gen_ops": trajectory[-1]["gen_ops"],
        "final_util": trajectory[-1]["util"],
    }


def _get_tree_ops(tree):
    ops = set()
    _collect_ops(tree, ops)
    return ops


def main():
    print("=" * 80)
    print("  RSI 검증 #2: 어려운 타겟 (sin(x), depth=3)")
    print("  Harder Target: sin(x) approximation with shallow trees")
    print("=" * 80)

    SEEDS = [42, 123, 456, 789, 1024]
    GENERATIONS = 500
    POP_SIZE = 20
    MAX_DEPTH = 3  # 얌은 트리 → library learning 필수

    # ===================================================================
    # Test 1: sin(x) with depth=3
    # ===================================================================
    print(f"\n▶ Target: sin(x), max_depth={MAX_DEPTH}")
    print(f"  sin(x)는 add/mul/square로 정확히 표현 불가.")
    print(f"  depth=3은 Taylor 급수 항을 직접 구성하기에 불충분.")
    print(f"  → Library learning이 깊은 서브트리를 하나의 op으로 압축하여")
    print(f"    effective depth를 확장해야 함.\n")

    # Condition A: FROZEN
    print("  Condition A: FROZEN")
    frozen = []
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        r = run_hard_experiment(seed, GENERATIONS, POP_SIZE, 999999,
                               MAX_DEPTH, sine_approximation_fitness,
                               f"FROZEN_sin_d{MAX_DEPTH}")
        elapsed = time.time() - t0
        print(f"    Seed {seed}: best={r['final_best']:.4f} vocab={r['final_vocab']} "
              f"time={elapsed:.1f}s")
        frozen.append(r)

    # Condition B: SELF-MODIFY
    print("\n  Condition B: SELF-MODIFY (expansion every 5 gen)")
    modify = []
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        r = run_hard_experiment(seed, GENERATIONS, POP_SIZE, 5,
                               MAX_DEPTH, sine_approximation_fitness,
                               f"MODIFY_sin_d{MAX_DEPTH}")
        elapsed = time.time() - t0
        print(f"    Seed {seed}: best={r['final_best']:.4f} vocab={r['final_vocab']} "
              f"gen_ops={r['final_gen_ops']} util={r['final_util']*100:.0f}% "
              f"time={elapsed:.1f}s")
        modify.append(r)

    # ===================================================================
    # Test 2: sin(x) with depth=5 (control — easier for library learning)
    # ===================================================================
    print(f"\n▶ Control: sin(x), max_depth=5")

    print("  Condition A: FROZEN (depth=5)")
    frozen5 = []
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        r = run_hard_experiment(seed, GENERATIONS, POP_SIZE, 999999,
                               5, sine_approximation_fitness,
                               f"FROZEN_sin_d5")
        elapsed = time.time() - t0
        print(f"    Seed {seed}: best={r['final_best']:.4f} time={elapsed:.1f}s")
        frozen5.append(r)

    print("\n  Condition B: SELF-MODIFY (depth=5)")
    modify5 = []
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        r = run_hard_experiment(seed, GENERATIONS, POP_SIZE, 5,
                               5, sine_approximation_fitness,
                               f"MODIFY_sin_d5")
        elapsed = time.time() - t0
        print(f"    Seed {seed}: best={r['final_best']:.4f} vocab={r['final_vocab']} "
              f"gen_ops={r['final_gen_ops']} util={r['final_util']*100:.0f}% "
              f"time={elapsed:.1f}s")
        modify5.append(r)

    # ===================================================================
    # 분석
    # ===================================================================
    print("\n" + "=" * 80)
    print("  분석 결과")
    print("=" * 80)

    for test_name, fr, mo, depth in [
        ("sin(x), depth=3", frozen, modify, 3),
        ("sin(x), depth=5", frozen5, modify5, 5)
    ]:
        fb = [r["final_best"] for r in fr]
        mb = [r["final_best"] for r in mo]
        delta = np.mean(mb) - np.mean(fb)

        print(f"\n  ▶ {test_name}")
        print(f"    FROZEN:      {np.mean(fb):.4f} ± {np.std(fb):.4f}  {fb}")
        print(f"    SELF-MODIFY: {np.mean(mb):.4f} ± {np.std(mb):.4f}  {mb}")
        print(f"    Δ = {delta:+.4f}")

        if delta > 0.01:
            print(f"    ✓ 자가 수정이 fitness를 개선함 (+{delta:.4f})")
        elif delta > 0.001:
            print(f"    ~ 미미한 개선 (+{delta:.4f})")
        else:
            print(f"    ✗ 개선 없음 (Δ = {delta:+.4f})")

        # 수렴 속도
        print(f"\n    수렴 속도:")
        for thresh in [0.3, 0.4, 0.5]:
            fr_gen = [r["best_at"].get(thresh, None) for r in fr]
            mo_gen = [r["best_at"].get(thresh, None) for r in mo]
            fr_avg = np.mean([g for g in fr_gen if g is not None]) if any(g is not None for g in fr_gen) else float('inf')
            mo_avg = np.mean([g for g in mo_gen if g is not None]) if any(g is not None for g in mo_gen) else float('inf')
            print(f"      → {thresh:.1f} fitness: FROZEN={fr_avg:.0f}gen, MODIFY={mo_avg:.0f}gen "
                  f"(faster by {fr_avg-mo_avg:.0f} gen)")

        # 궤적
        print(f"\n    Fitness 궤적 (FROZEN vs SELF-MODIFY):")
        print(f"    {'Gen':>5}  {'FROZEN':>8}  {'MODIFY':>8}  {'Δ':>8}  {'Util%':>6}")
        fr_traj_avg = {}
        mo_traj_avg = {}
        mo_util_avg = {}
        for r in fr:
            for t in r["trajectory"]:
                fr_traj_avg.setdefault(t["gen"], []).append(t["best"])
        for r in mo:
            for t in r["trajectory"]:
                mo_traj_avg.setdefault(t["gen"], []).append(t["best"])
                mo_util_avg.setdefault(t["gen"], []).append(t["util"])

        for gen in sorted(fr_traj_avg.keys()):
            if gen in mo_traj_avg:
                fa = np.mean(fr_traj_avg[gen])
                ma = np.mean(mo_traj_avg[gen])
                ua = np.mean(mo_util_avg.get(gen, [0]))
                print(f"    {gen:5d}  {fa:8.4f}  {ma:8.4f}  {ma-fa:+8.4f}  {ua*100:5.1f}%")

    # ===================================================================
    # 최종 판정
    # ===================================================================
    print("\n" + "=" * 80)
    print("  최종 판정")
    print("=" * 80)

    d3_delta = np.mean([r["final_best"] for r in modify]) - np.mean([r["final_best"] for r in frozen])
    d5_delta = np.mean([r["final_best"] for r in modify5]) - np.mean([r["final_best"] for r in frozen5])
    d3_util = np.mean([r["final_util"] for r in modify])
    d5_util = np.mean([r["final_util"] for r in modify5])

    print(f"\n  sin(x) depth=3: Δ = {d3_delta:+.4f}, util = {d3_util*100:.1f}%")
    print(f"  sin(x) depth=5: Δ = {d5_delta:+.4f}, util = {d5_util*100:.1f}%")

    if d3_delta > 0.01 or d5_delta > 0.01:
        print(f"\n  VERDICT: RECURSIVE_SELF_IMPROVEMENT_CONFIRMED")
        print(f"  자가 수정이 어려운 타겟에서 측정 가능한 개선을 제공함.")
        if d3_delta > d5_delta:
            print(f"  depth=3에서 효과가 더 큼 → depth amplification이 핵심 메커니즘.")
    elif d3_delta > 0.001 or d5_delta > 0.001:
        print(f"\n  VERDICT: MARGINAL_IMPROVEMENT")
        print(f"  미미한 개선. 재귀 메커니즘은 작동하지만 효과가 작음.")
    else:
        print(f"\n  VERDICT: SELF_MODIFICATION_WITHOUT_IMPROVEMENT")
        print(f"  어려운 타겟에서도 자가 수정이 개선으로 이어지지 않음.")
        print(f"  가능한 원인:")
        print(f"  1. 메타-그래머가 'useful' op을 만들지 못함 (random composition)")
        print(f"  2. 500 세대가 부족함 (더 긴 실행 필요)")
        print(f"  3. Library learning의 subtree 추출이 sin 근사에 필요한")
        print(f"     Taylor 급수 계수를 발견하기 어려움")


if __name__ == "__main__":
    main()
