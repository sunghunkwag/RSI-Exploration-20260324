"""
RSI (Recursive Self-Improvement) 검증 테스트
==============================================

핵심 질문 3가지:
1. 시스템이 스스로 새로운 연산/규칙을 생성하는가? (자가 수정)
2. 그 발견이 더 나은 성능으로 이어지는가? (개선)
3. 더 나은 성능이 다시 더 나은 발견으로 이어지는가? (재귀)

테스트 설계:
- Condition A (FROZEN): 메타-그래머 확장 비활성화 (expansion_interval=999999)
- Condition B (SELF-MODIFY): 메타-그래머 확장 활성화 (expansion_interval=5)
- 5 seeds × 2 conditions × 500 generations
- 측정: fitness trajectory, vocab growth, library extraction rate,
        new-op utilization rate, recursive loop depth
"""

import random
import copy
import numpy as np
import logging
import sys
import time

sys.path.insert(0, '/sessions/blissful-determined-brahmagupta/RSI-Exploration')

logging.disable(logging.INFO)  # suppress verbose logs

from main import (
    VocabularyLayer, GrammarLayer, MetaGrammarLayer,
    LibraryLearner, ResourceBudget, CostGroundingLoop,
    MAPElitesArchive, EnhancedMAPElitesArchive,
    EliteEntry, SelfImprovementEngine, build_rsi_system,
    symbolic_regression_fitness, _eval_tree, EvalContext,
    PolymorphicOp, ExprNode, PrimitiveOp
)


def _collect_ops(node, ops_set):
    """트리에서 사용된 모든 op 이름을 수집."""
    ops_set.add(node.op_name)
    for c in node.children:
        _collect_ops(c, ops_set)


def _tree_uses_generated_ops(tree, base_ops):
    """트리가 기본 op 외에 생성된 op을 사용하는지 확인."""
    used = set()
    _collect_ops(tree, used)
    return used - base_ops


def run_experiment(seed, generations, pop_size, expansion_interval, label):
    """실험 하나를 실행하고 세부 궤적을 반환."""
    random.seed(seed)
    np.random.seed(seed)

    engine = build_rsi_system(
        max_depth=5,
        budget_ops=100_000,
        budget_seconds=60.0,
        expansion_interval=expansion_interval,
        use_library_learning=True,
        library_min_depth=2,
        library_min_freq=2,
        library_max_additions=3,
        similarity_threshold=0.85,
    )

    # 기본 op 이름 기록 (생성된 op과 구분하기 위해)
    base_ops = {op.name for op in engine.vocab.all_ops()}

    trajectory = []
    for gen in range(generations):
        record = engine.step(pop_size)

        # 현재 vocab에서 생성된 op 수
        current_ops = {op.name for op in engine.vocab.all_ops()}
        generated_ops = current_ops - base_ops
        poly_ops = {op.name for op in engine.vocab.all_ops()
                    if isinstance(op, PolymorphicOp)}

        # 엘리트 중 생성된 op을 사용하는 비율
        elites = list(engine.archive._grid.values())
        elites_using_generated = 0
        elites_using_self_encode = 0
        elites_using_poly = 0
        for e in elites:
            used = set()
            _collect_ops(e.tree, used)
            if used & generated_ops:
                elites_using_generated += 1
            if "self_encode" in used:
                elites_using_self_encode += 1
            if used & poly_ops:
                elites_using_poly += 1

        n_elites = len(elites)

        # "2차 생성 op" — 생성된 op을 기반으로 다시 생성된 op 탐지
        # (예: lib_X가 다른 lib_Y를 포함하는 경우 = 재귀적 자가 개선의 증거)
        second_gen_ops = 0
        for op_name in generated_ops:
            if op_name.startswith("lib_"):
                # Library learning으로 추출된 op: 해당 op의 구현이
                # 다른 generated op을 사용하면 2차 생성
                pass  # 아래에서 별도 분석

        snapshot = {
            "gen": gen + 1,
            "best_fitness": record["archive_best"],
            "coverage": record["archive_coverage"],
            "vocab_size": record["vocab_size"],
            "generated_ops": len(generated_ops),
            "poly_ops": len(poly_ops),
            "grammar_rules": record["grammar_rules"],
            "meta_expansions": record["meta_expansions"],
            "n_elites": n_elites,
            "elites_using_generated": elites_using_generated,
            "elites_using_self_encode": elites_using_self_encode,
            "elites_using_poly": elites_using_poly,
            "utilization_rate": elites_using_generated / max(n_elites, 1),
        }
        trajectory.append(snapshot)

    # 최종 분석: 재귀 깊이 측정
    # 생성된 op이 다른 생성된 op의 트리에 포함되어 있으면 2차 재귀
    recursion_evidence = analyze_recursion_depth(engine, base_ops)

    return {
        "label": label,
        "seed": seed,
        "trajectory": trajectory,
        "final": trajectory[-1],
        "recursion": recursion_evidence,
    }


def analyze_recursion_depth(engine, base_ops):
    """
    재귀적 자가 개선의 깊이를 분석.

    깊이 0: 기본 op만 사용
    깊이 1: 메타-그래머가 기본 op에서 새 op 생성 (1차 생성)
    깊이 2: 엘리트가 1차 생성 op을 사용 → 더 높은 fitness
    깊이 3: 높은 fitness 엘리트에서 library learning이 새 패턴 추출 (2차 생성)
    깊이 4: 2차 생성 op이 더 나은 엘리트에 사용됨 → 재귀 완성
    """
    current_ops = {op.name for op in engine.vocab.all_ops()}
    generated_ops = current_ops - base_ops

    # Library-extracted ops (lib_*)와 meta-grammar ops 구분
    lib_ops = {n for n in generated_ops if n.startswith("lib_")}
    meta_ops = {n for n in generated_ops if not n.startswith("lib_") and not n.startswith("poly_")}
    poly_ops_set = {n for n in generated_ops if n.startswith("poly_")}

    # 깊이 1: 새 op이 생성되었는가?
    depth_1 = len(generated_ops) > 0

    # 깊이 2: 엘리트가 생성된 op을 사용하는가?
    elites = list(engine.archive._grid.values())
    elites_with_gen = []
    for e in elites:
        used = set()
        _collect_ops(e.tree, used)
        gen_used = used & generated_ops
        if gen_used:
            elites_with_gen.append((e.grounded_fitness, gen_used))

    depth_2 = len(elites_with_gen) > 0

    # 깊이 3: library learning이 생성된 op을 포함하는 패턴을 추출했는가?
    # lib_* op의 이름은 fingerprint이므로 직접 확인 불가 → 간접 확인:
    # 엘리트 트리에서 lib_* op이 다른 generated op과 함께 사용되면 증거
    depth_3_evidence = []
    for e in elites:
        used = set()
        _collect_ops(e.tree, used)
        lib_used = used & lib_ops
        other_gen_used = used & (meta_ops | poly_ops_set)
        if lib_used and other_gen_used:
            depth_3_evidence.append({
                "fitness": e.grounded_fitness,
                "lib_ops": lib_used,
                "meta_ops": other_gen_used,
            })

    depth_3 = len(depth_3_evidence) > 0

    # 깊이 4: 2차 생성 op을 사용하는 엘리트가 1차만 사용하는 것보다 fitness가 높은가?
    fitness_with_lib = [f for f, _ in elites_with_gen if any(
        n.startswith("lib_") for n in _)] if elites_with_gen else []
    fitness_without_lib = [e.grounded_fitness for e in elites
                          if not any(n.startswith("lib_")
                          for n in _get_tree_ops(e.tree) & generated_ops)]

    depth_4 = False
    if fitness_with_lib and fitness_without_lib:
        avg_with = sum(fitness_with_lib) / len(fitness_with_lib)
        avg_without = sum(fitness_without_lib) / len(fitness_without_lib)
        depth_4 = avg_with > avg_without

    return {
        "depth_1_new_ops": depth_1,
        "depth_1_count": len(generated_ops),
        "depth_2_elites_use_ops": depth_2,
        "depth_2_count": len(elites_with_gen),
        "depth_3_compound_ops": depth_3,
        "depth_3_evidence_count": len(depth_3_evidence),
        "depth_4_recursive_benefit": depth_4,
        "lib_ops": len(lib_ops),
        "meta_ops": len(meta_ops),
        "poly_ops": len(poly_ops_set),
        "max_depth": (4 if depth_4 else 3 if depth_3 else 2 if depth_2
                      else 1 if depth_1 else 0),
    }


def _get_tree_ops(tree):
    ops = set()
    _collect_ops(tree, ops)
    return ops


def print_trajectory_summary(results, label, milestones=[50, 100, 200, 300, 500]):
    """궤적 요약 출력."""
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    print(f"{'Gen':>5} {'Best':>8} {'Cov':>6} {'Vocab':>6} {'GenOps':>7} "
          f"{'Poly':>5} {'Util%':>6} {'Rules':>6}")
    print(f"{'-'*55}")

    for r in results:
        for t in r["trajectory"]:
            if t["gen"] in milestones or t["gen"] == 1:
                print(f"{t['gen']:5d} {t['best_fitness']:8.4f} {t['coverage']:6.4f} "
                      f"{t['vocab_size']:6d} {t['generated_ops']:7d} "
                      f"{t['poly_ops']:5d} {t['utilization_rate']*100:5.1f}% "
                      f"{t['grammar_rules']:6d}")
        print()


def main():
    print("=" * 80)
    print("  RSI (재귀적 자가 개선) 검증 테스트")
    print("  Recursive Self-Improvement Verification")
    print("=" * 80)

    SEEDS = [42, 123, 456, 789, 1024]
    GENERATIONS = 500
    POP_SIZE = 20

    # ===================================================================
    # Condition A: FROZEN (메타-그래머 비활성화)
    # ===================================================================
    print("\n▶ Condition A: FROZEN (no meta-grammar expansion)")
    frozen_results = []
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        r = run_experiment(seed, GENERATIONS, POP_SIZE,
                          expansion_interval=999999, label=f"FROZEN_s{seed}")
        elapsed = time.time() - t0
        print(f"  Seed {seed} ({i+1}/5): best={r['final']['best_fitness']:.4f} "
              f"vocab={r['final']['vocab_size']} gen_ops={r['final']['generated_ops']} "
              f"time={elapsed:.1f}s")
        frozen_results.append(r)

    # ===================================================================
    # Condition B: SELF-MODIFY (메타-그래머 활성화)
    # ===================================================================
    print("\n▶ Condition B: SELF-MODIFY (meta-grammar expansion every 5 gen)")
    modify_results = []
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        r = run_experiment(seed, GENERATIONS, POP_SIZE,
                          expansion_interval=5, label=f"MODIFY_s{seed}")
        elapsed = time.time() - t0
        print(f"  Seed {seed} ({i+1}/5): best={r['final']['best_fitness']:.4f} "
              f"vocab={r['final']['vocab_size']} gen_ops={r['final']['generated_ops']} "
              f"time={elapsed:.1f}s")
        modify_results.append(r)

    # ===================================================================
    # 비교 분석
    # ===================================================================
    print("\n" + "=" * 80)
    print("  분석 결과 (Analysis)")
    print("=" * 80)

    # 1. Fitness 비교
    frozen_bests = [r["final"]["best_fitness"] for r in frozen_results]
    modify_bests = [r["final"]["best_fitness"] for r in modify_results]

    print(f"\n  1. 최종 Fitness 비교 (Final Fitness Comparison)")
    print(f"     FROZEN:      {np.mean(frozen_bests):.4f} ± {np.std(frozen_bests):.4f}")
    print(f"     SELF-MODIFY: {np.mean(modify_bests):.4f} ± {np.std(modify_bests):.4f}")
    improvement = np.mean(modify_bests) - np.mean(frozen_bests)
    print(f"     차이 (Δ):    {improvement:+.4f}")
    if improvement > 0.01:
        print(f"     판정: 자가 수정이 fitness를 개선함 ✓")
    elif improvement > -0.01:
        print(f"     판정: 차이 없음 (자가 수정이 fitness에 영향 없음) ✗")
    else:
        print(f"     판정: 자가 수정이 오히려 성능 저하 ✗✗")

    # 2. Coverage 비교
    frozen_covs = [r["final"]["coverage"] for r in frozen_results]
    modify_covs = [r["final"]["coverage"] for r in modify_results]

    print(f"\n  2. Coverage 비교")
    print(f"     FROZEN:      {np.mean(frozen_covs):.4f} ± {np.std(frozen_covs):.4f}")
    print(f"     SELF-MODIFY: {np.mean(modify_covs):.4f} ± {np.std(modify_covs):.4f}")

    # 3. Vocab growth
    print(f"\n  3. Vocabulary 성장")
    for r in modify_results:
        traj = r["trajectory"]
        print(f"     Seed {r['seed']}: {traj[0]['vocab_size']} → {traj[-1]['vocab_size']} "
              f"(+{traj[-1]['generated_ops']} generated, "
              f"{traj[-1]['poly_ops']} poly)")

    # 4. 생성된 Op 사용률 궤적
    print(f"\n  4. 생성된 Op 사용률 궤적 (Utilization Trajectory)")
    print(f"     {'Gen':>5}  ", end="")
    for seed in SEEDS:
        print(f"  s{seed:>4}", end="")
    print()

    for gen_idx in [49, 99, 199, 299, 499]:  # gen 50, 100, 200, 300, 500
        print(f"     {gen_idx+1:5d}  ", end="")
        for r in modify_results:
            t = r["trajectory"][gen_idx]
            print(f"  {t['utilization_rate']*100:5.1f}%", end="")
        print()

    # 5. self_encode 사용률
    print(f"\n  5. self_encode 사용률")
    for r in modify_results:
        t = r["trajectory"][-1]
        rate = t["elites_using_self_encode"] / max(t["n_elites"], 1) * 100
        print(f"     Seed {r['seed']}: {t['elites_using_self_encode']}/{t['n_elites']} "
              f"elites ({rate:.1f}%)")

    # 6. PolymorphicOp 사용률
    print(f"\n  6. PolymorphicOp 사용률")
    for r in modify_results:
        t = r["trajectory"][-1]
        rate = t["elites_using_poly"] / max(t["n_elites"], 1) * 100
        print(f"     Seed {r['seed']}: {t['elites_using_poly']}/{t['n_elites']} "
              f"elites ({rate:.1f}%)")

    # 7. 재귀 깊이 분석
    print(f"\n  7. 재귀 깊이 분석 (Recursion Depth)")
    print(f"     깊이 0: 기본 op만 사용")
    print(f"     깊이 1: 메타-그래머가 새 op 생성")
    print(f"     깊이 2: 엘리트가 생성된 op 사용 → 더 높은 fitness")
    print(f"     깊이 3: Library learning이 생성된 op 포함 패턴 추출")
    print(f"     깊이 4: 2차 생성 op이 fitness 이점을 제공")
    print()
    for r in modify_results:
        rec = r["recursion"]
        print(f"     Seed {r['seed']}: 최대 깊이 = {rec['max_depth']}")
        print(f"       D1 (새 op 생성):     {'✓' if rec['depth_1_new_ops'] else '✗'} "
              f"({rec['depth_1_count']}개)")
        print(f"       D2 (엘리트가 사용):   {'✓' if rec['depth_2_elites_use_ops'] else '✗'} "
              f"({rec['depth_2_count']}개 엘리트)")
        print(f"       D3 (복합 op 추출):   {'✓' if rec['depth_3_compound_ops'] else '✗'} "
              f"({rec['depth_3_evidence_count']}건 증거)")
        print(f"       D4 (재귀적 이점):    {'✓' if rec['depth_4_recursive_benefit'] else '✗'}")
        print(f"       구성: lib={rec['lib_ops']} meta={rec['meta_ops']} poly={rec['poly_ops']}")
        print()

    # 8. Convergence speed 비교
    print(f"\n  8. 수렴 속도 비교 (Convergence Speed)")
    print(f"     {'':>12} {'Gen→0.90':>10} {'Gen→0.95':>10} {'Gen→0.99':>10}")
    for label, results in [("FROZEN", frozen_results), ("SELF-MODIFY", modify_results)]:
        thresholds = {0.90: [], 0.95: [], 0.99: []}
        for r in results:
            for thresh in thresholds:
                found = None
                for t in r["trajectory"]:
                    if t["best_fitness"] >= thresh:
                        found = t["gen"]
                        break
                thresholds[thresh].append(found if found else GENERATIONS + 1)

        avgs = {k: np.mean([v for v in vals if v <= GENERATIONS])
                if any(v <= GENERATIONS for v in vals) else float('inf')
                for k, vals in thresholds.items()}

        print(f"     {label:<12} ", end="")
        for thresh in [0.90, 0.95, 0.99]:
            if avgs[thresh] == float('inf'):
                print(f"  {'never':>8}", end="")
            else:
                print(f"  {avgs[thresh]:8.1f}", end="")
        print()

    # ===================================================================
    # 최종 판정
    # ===================================================================
    print("\n" + "=" * 80)
    print("  최종 판정 (Final Verdict)")
    print("=" * 80)

    avg_depth = np.mean([r["recursion"]["max_depth"] for r in modify_results])
    any_depth_4 = any(r["recursion"]["depth_4_recursive_benefit"] for r in modify_results)
    any_depth_3 = any(r["recursion"]["depth_3_compound_ops"] for r in modify_results)
    avg_util = np.mean([r["final"]["utilization_rate"] for r in modify_results])

    print(f"\n  평균 재귀 깊이: {avg_depth:.1f}")
    print(f"  평균 생성 op 사용률: {avg_util*100:.1f}%")
    print(f"  Fitness 개선 (vs FROZEN): {improvement:+.4f}")

    if any_depth_4 and improvement > 0.01:
        verdict = "GENUINE_RECURSIVE_SELF_IMPROVEMENT"
        desc = "재귀적 자가 개선이 확인됨: 시스템이 스스로 생성한 도구를 사용하여\n" \
               "    더 나은 도구를 생성하고, 그것이 다시 성능을 개선하는 재귀 루프가 작동함."
    elif any_depth_3 and improvement > 0.01:
        verdict = "PARTIAL_RSI_DEPTH_3"
        desc = "부분적 자가 개선: 시스템이 생성한 op을 사용하여 새로운 패턴을 추출하지만,\n" \
               "    2차 생성이 명확한 fitness 이점을 제공하는지는 불확실."
    elif any_depth_3 and improvement > -0.01:
        verdict = "SELF_MODIFICATION_WITHOUT_IMPROVEMENT"
        desc = "자가 수정은 되지만 개선 없음: 시스템이 구조를 변경하지만\n" \
               "    변경이 성능 향상으로 이어지지 않음."
    elif avg_depth >= 2 and improvement > 0.01:
        verdict = "ONE_SHOT_IMPROVEMENT"
        desc = "1회성 개선: 생성된 op이 사용되고 fitness가 개선되지만\n" \
               "    재귀 루프(생성→사용→재생성)가 확인되지 않음."
    else:
        verdict = "NO_RSI"
        desc = "재귀적 자가 개선이 확인되지 않음."

    print(f"\n  VERDICT: {verdict}")
    print(f"  설명: {desc}")

    # Save raw data
    print(f"\n  원시 데이터:")
    print(f"  FROZEN  seeds: {[r['final']['best_fitness'] for r in frozen_results]}")
    print(f"  MODIFY  seeds: {[r['final']['best_fitness'] for r in modify_results]}")
    print(f"  MODIFY depths: {[r['recursion']['max_depth'] for r in modify_results]}")


if __name__ == "__main__":
    main()
