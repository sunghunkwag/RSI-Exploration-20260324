# RSI-Exploration Daily Log

## 2026-03-24

**Source:** [DreamCoder: bootstrapping inductive program synthesis with wake-sleep library learning](https://github.com/mlb2251/dreamcoder) (Ellis et al., PLDI 2021; compression/refactoring algorithm)

**Mechanism:** Library Learning — extracting frequently occurring subtrees from elite programs in the MAP-Elites archive and promoting them to new primitive operations in the vocabulary.

**Integration:** Added `LibraryLearner` class to main.py. The learner:
1. Scans all elite trees in the archive for subtrees of depth >= `min_subtree_depth`
2. Groups by structural fingerprint, filters by frequency >= `min_frequency`
3. Ranks by `frequency * depth` (compression value heuristic)
4. Converts top candidates into new `PrimitiveOp` entries with correct arity detection (unary if subtree contains `input_x`, nullary otherwise)
5. Registers them in the vocabulary with discounted cost

Integrated into `MetaGrammarLayer.expand_design_space()` — library learning fires with 50% probability when elite trees are available, alongside existing meta-rules.

Updated `build_rsi_system()` factory with `use_library_learning`, `library_min_depth`, `library_min_freq`, `library_max_additions` parameters.

**New capability:** The system can now break its own depth ceiling. Previously, with `max_depth=D`, the system could only express computations requiring at most `D` levels of nesting. After library learning extracts a depth-K subtree as a single primitive, a depth-D tree using that primitive can express what previously required depth `D+K`. This is a genuine expansion of F_theo — the set of representable functions grows strictly larger after each library learning step, unlike `_meta_compose_new_op` which only randomly chains unary ops.

**Tests:** 45/45 pass (38 existing + 7 new)
- `test_extract_from_repeated_subtrees` — verifies extraction triggers on shared subtrees
- `test_extracted_op_computes_correctly` — verifies semantic correctness of extracted ops
- `test_no_extraction_below_frequency_threshold` — verifies frequency filter
- `test_no_duplicate_extraction` — verifies idempotency
- `test_depth_amplification` — **critical**: demonstrates depth ceiling bypass
- `test_library_learning_with_engine_integration` — full engine integration smoke test
- `test_constant_subtree_extraction` — verifies arity-0 extraction for constant subtrees

**Branch:** `upgrade/20260324-library-learning`

---

## 2026-03-25 — Session 1: Domain A (Mathematics & Formal Foundations)

### Baseline
- 49/49 tests pass
- CAGE snapshot: no changes since last session (library learning integrated on main)
- Architectural ceiling: ExprNode trees are NOT Turing-complete — specifically cannot express: self-reference, adaptive grammar rules, simultaneous induction-recursion
- Today's domain: A (Mathematics & Formal Foundations)
- Previous sessions completed: none (this is Session 1)

### Monitoring
- arxiv: 38 scanned, 12 relevant, 12 deeper_read
- GitHub: 25 scanned, 4 relevant
- Cumulative: arxiv 38, GitHub 25

### Domain investigation
- Sub-topics investigated: 7
- Full formal extractions completed: 7
- STRUCTURAL_EXPANSION verdicts: 6 (A.1 Universe Polymorphism/IR, A.2 Kan Extensions, A.3 Adaptive Grammars, A.4 VW Two-Level Grammars, A.5 Univalence, A.7 Diagonal Lemma)
- COMBINATORIAL_RECOMBINATION verdicts: 1 (A.6 Priority Arguments)
- Remaining incomplete: 0

### Key findings from Domain A

**Strongest cage-breaking candidates (Layer 3 / FORMAT_CHANGE):**

1. **A.3 Adaptive Grammars (Shutt)** — Rule set becomes dynamic semantic object modified during evaluation. Layer 3.
2. **A.4 Van Wijngaarden Two-Level Grammars** — Metarules + hyperrules generate infinite concrete grammar from finite specification. Layer 3 -> Layer 2.
3. **A.7 Diagonal Lemma (Self-Reference)** — Trees that can reference their own encoding. FORMAT_CHANGE.
4. **A.1 Induction-Recursion** — Simultaneous definition of codes + interpretation. Layer 3 + FORMAT_CHANGE.

### Session assessment
COMPLETE — All 7 sub-topics. Domain A report written to docs/domains/domain-A-mathematics.md.

---

## 2026-03-25 — Session 2: Domain B (Physics, Cosmology & Fundamental Theory)

### Baseline
- 49/49 tests pass
- CAGE snapshot: no changes since Session 1 (same day)
- Today's domain: B (Physics, Cosmology & Fundamental Theory)

### Monitoring
- arxiv: 19 scanned, 8 relevant (incremental)
- Cumulative: arxiv 57, GitHub 25

### Domain investigation
- Sub-topics investigated: 9
- Full formal extractions completed: 9
- STRUCTURAL_EXPANSION verdicts: 4 (B.1 Higgs, B.3 Wilson RG, B.7 M-theory, B.8 Electroweak)
- COMBINATORIAL_RECOMBINATION verdicts: 5 (B.2 Landau, B.4 T-duality, B.5 S-duality, B.6 AdS/CFT, B.9 Nucleosynthesis)
- Remaining incomplete: 0

### Key findings from Domain B

**Critical pattern: dualities are isomorphisms, not expansions.** T-duality, S-duality, AdS/CFT all preserve F_theo.

1. **Symmetry breaking** (B.1, B.8) — vacuum selection creates new mass eigenstates. FORMAT_CHANGE.
2. **Wilson RG** (B.3) — **KEY INSIGHT: Wilson RG IS structurally identical to LibraryLearner.** Formal, not metaphorical.
3. **M-theory unification** (B.7) — meta-format subsuming multiple representations.

### Session assessment
COMPLETE — All 9 sub-topics. Domain B report written to docs/domains/domain-B-physics.md.

---

## 2026-03-25 — Session 3: Domain C (Ancient Texts, Manuscripts & Historical Linguistics)

### Baseline
- 49/49 tests pass
- Today's domain: C (Ancient Texts, Manuscripts & Historical Linguistics)

### Domain investigation
- Sub-topics investigated: 8
- Full formal extractions completed: 8
- STRUCTURAL_EXPANSION verdicts: 5 (C.1b Paribhasa, C.1c Karaka, C.3 Aramaic polysemy, C.4 Cuneiform evolution, C.5 DSS variants)
- COMBINATORIAL_RECOMBINATION verdicts: 2 (C.1a Pratyahara, C.2 Hebrew binyanim)
- Mixed: 1 (C.6 Script evolution)

### Key findings from Domain C

**Dominant pattern: context-dependent evaluation is the primary expansion mechanism.** Three independent sub-topics converge on making evaluation context-dependent.

1. **Context-dependent evaluation** (C.3 + C.4 + C.1c) — Polymorphic PrimitiveOps with context threading. FORMAT_CHANGE.
2. **Paribhasa conflict resolution** (C.1b) — Replace random rule selection with specificity-based deterministic resolution.
3. **Bidirectional abstraction** (C.6) — Fine-graining = inverse of B.3 Wilson RG / LibraryLearner.

### Session assessment
COMPLETE — All 8 sub-topics. Domain C report written to docs/domains/domain-C-linguistics.md.

---

## 2026-03-25 — Session 4: Domain D (Computer Science & Computation Theory)

### Baseline
- 49/49 tests pass
- Today's domain: D (Computer Science & Computation Theory)

### Domain investigation
- Sub-topics investigated: 8
- Full formal extractions completed: 8
- STRUCTURAL_EXPANSION verdicts: 5 (D.1 Quines/Kleene, D.5 Type Systems, D.6 Automata/TAG, D.7 Godel Machines, D.8 Continuations/Effects)
- COMBINATORIAL_RECOMBINATION verdicts: 3 (D.2 GGGP/GE, D.3 DreamCoder, D.4 Reflection)

### Key findings from Domain D

**Self-reference is the master cage-breaking mechanism.** D.1->D.4->D.7 progression.

1. **Godel Machine** (D.7) — system rewrites its own evaluation mechanism; ultimate cage-breaking.
2. **Quines / self-reference** (D.1) — trees referencing own encoding. = A.7.
3. **Continuations / algebraic effects** (D.8) — adds entire control flow dimension.
4. **TAG adjunction** (D.6) — moves ExprNode to mildly context-sensitive.
5. **Dependent types** (D.5) — type-indexed composition rules.

### Session assessment
COMPLETE — All 8 sub-topics. Domain D report written to docs/domains/domain-D-cs.md.

---

## 2026-03-25 — Session 5: Domain E (Music, Acoustics & Compositional Theory)

### Baseline
- 49/49 tests pass
- Today's domain: E (Music, Acoustics & Compositional Theory)

### Domain investigation
- Sub-topics: 6 investigated, 6 complete
- STRUCTURAL_EXPANSION: 4 (E.1 Schenkerian, E.3 Spectral, E.4 GTTM, E.6 Microtonality)
- COMBINATORIAL_RECOMBINATION: 2 (E.2 Serialism, E.5 L-Systems)

### Key findings from Domain E

**Cross-domain convergence dominates.** E.3=B.1/B.8 (continuous primitives), E.4=C.1b (preference rules), E.2=B.4-B.6 (symmetry=recombination).

### Session assessment
COMPLETE — All 6 sub-topics. Domain E report written to docs/domains/domain-E-music.md.

---

## 2026-03-25 — Session 6: Domain F (Architecture, Engineering & Design)

### Baseline
- 49/49 tests pass
- Today's domain: F (Architecture, Engineering & Design)

### Domain investigation
- Sub-topics: 7 investigated, 7 complete
- STRUCTURAL_EXPANSION: 2 (F.5 Topology Optimization, F.6 Origami Mathematics)
- COMBINATORIAL_RECOMBINATION: 4 (F.1 Shape Grammars, F.2 Parametric Design, F.3 Tensegrity, F.7 Co-evolutionary Design)
- NO_STRUCTURE_FOUND: 1 (F.4 Pattern Language)

### Key findings from Domain F

**Architecture/design primarily about search efficiency, not expressibility.** Only 2/7 STRUCTURAL_EXPANSION.

1. **Topology optimization** (F.5) — discrete->continuous FORMAT_CHANGE (=E.3=B.1/B.8, now 4 domains).
2. **Origami algebraic tower** (F.6) — quadratic->cubic field extension. New Galois-theoretic expansion.

### Session assessment
COMPLETE — All 7 sub-topics. Domain F report written to docs/domains/domain-F-architecture.md.

---

## 2026-03-25 — Session 7: Domain G (Philosophy of Mathematics & Formal Epistemology)

### Baseline
- 49/49 tests pass
- Today's domain: G (Philosophy of Mathematics & Formal Epistemology)

### Domain investigation
- Sub-topics: 7 investigated, 7 complete
- STRUCTURAL_EXPANSION: 2 (G.1 Intuitionism/Constructive Math, G.6 Topos Theory)
- COMBINATORIAL_RECOMBINATION: 3 (G.2 Lakatos, G.3 Structuralism, G.5 Forcing)
- NO_STRUCTURE_FOUND: 2 (G.4 Reverse Mathematics, G.7 Incompleteness)

### Key findings from Domain G

**Fewer expansions but deeper foundations.** Two genuine STRUCTURAL_EXPANSION providing mathematical grounding for other domains.

1. **Constructive proofs-as-programs** (G.1) — Curry-Howard: expansion via restriction. New pattern.
2. **Topos-internal evaluation** (G.6) — Mathematical foundation for C.3/C.4 context-dependent eval.

### Session assessment
COMPLETE — All 7 sub-topics. Domain G report written to docs/domains/domain-G-philosophy.md.

---

## 2026-03-25 — Session 8: Domain H (Representation Theory & Algebraic Structures)

### Baseline
- 49/49 tests pass
- CAGE snapshot: no changes since Session 7 (same day)
- Architectural ceiling: unchanged from Session 1
- Today's domain: H (Representation Theory & Algebraic Structures)
- Previous sessions completed: Sessions 1-7 (Domains A-G)

### Monitoring
- arxiv: 0 incremental (8th session same day)
- GitHub: 0 incremental
- Cumulative: arxiv 57, GitHub 25

### Domain investigation
- Sub-topics investigated: 8
- Full formal extractions completed: 8
- STRUCTURAL_EXPANSION verdicts: 5 (H.2 Quiver Representations, H.3 Crystal Bases, H.4 Geometric Rep Theory, H.5 Categorification, H.8 Operads)
- COMBINATORIAL_RECOMBINATION verdicts: 3 (H.1 Young Tableaux, H.6 Fusion Categories, H.7 Langlands Program)
- NO_STRUCTURE_FOUND: 0
- Remaining incomplete: 0

### Key findings from Domain H

**Representation theory is the richest domain for structural expansion.** 5/8 sub-topics yield STRUCTURAL_EXPANSION — the highest ratio of any domain. Root cause: representation theory studies *how structures represent other structures*, which is exactly what the RSI system needs for cage-breaking.

**Strongest candidates:**
1. **Operads as meta-grammar** (H.8) — Grammar for grammars. Directly formalizes MetaGrammarLayer. Koszul duality auto-generates dual rule systems.
2. **Categorification** (H.5) — Systematic format lifting (int->vector space, polynomial->chain complex). Functorial information gain.
3. **Crystal bases** (H.3) — Expansion via dimensional reduction (q->0). Paradoxical expansion via restriction (matches G.1).
4. **Geometric rep theory** (H.4) — Sheaf-theoretic methods reveal algebraically invisible structure.
5. **Quiver root classification** (H.2) — Dynkin diagrams organize representation types.

**Cross-domain:** H.8=A.3/A.4 (meta-grammar), H.5=B/E/F (format lifting), H.3=G.1 (expansion via restriction), H.4=G.6 (geometric methods), H.7=B.4-B.6 (duality=recombination).

### Session assessment
COMPLETE — All 8 sub-topics. Domain H report written to docs/domains/domain-H-representation.md.

---

## 2026-03-25 — Session 9: Synthesis (Cross-Domain Analysis)

### Baseline
- 49/49 tests pass (no code changes in this session)
- Previous sessions completed: Sessions 1-8 (Domains A-H)

### Synthesis results

**Aggregate across 8 domains:** 60 extractions total. 33 STRUCTURAL_EXPANSION (55%), 23 COMBINATORIAL_RECOMBINATION (38%), 3 NO_STRUCTURE_FOUND (5%), 1 Mixed (2%).

**Highest expansion-rate domains:** A-Mathematics (86%), E-Music (67%), C-Linguistics (63%), D-CS (63%), H-Representation (63%).

**7 converged mechanism families identified:**

1. **Self-Reference** (Master Cage-Breaker) — A.7, D.1, D.7. Trees encoding their own structure. Unlocks fixed-point computations. Priority: HIGHEST.
2. **Context-Dependent Evaluation** — C.1c, C.3, C.4, G.6, D.4. eval(T,x) becomes eval(T,x,ctx). Polymorphic dispatch. Priority: HIGH.
3. **Adaptive Grammar / Meta-Grammar Formalization** — A.3, A.4, H.8, D.6. Rule sets as first-class dynamic objects. Operadic composition. Priority: HIGH.
4. **Discrete->Continuous FORMAT_CHANGE** — B.1, B.8, E.3, E.6, F.5, F.6. Continuous primitives strictly expand F_theo. Priority: MEDIUM.
5. **Preference-Based Rule Selection** — C.1b, E.4, D.5. Deterministic conflict resolution replacing random selection. Priority: MEDIUM.
6. **Categorification / Systematic Format Lifting** — H.5, H.4, A.2, A.1. Functorial lifting preserving structure. Priority: MEDIUM.
7. **Bidirectional Abstraction** — B.3, C.6, H.2. Inverse of LibraryLearner: fine-graining. Priority: LOW.

**Implementation roadmap:**
- Tier 1 (Maximum Impact, Implementable Now): Mechanisms 1 + 2
- Tier 2 (High Impact, Requires Architecture Work): Mechanisms 3 + 5
- Tier 3 (Valuable, Longer Horizon): Mechanisms 4 + 6 + 7

### Session assessment
COMPLETE — Synthesis report written to docs/synthesis.md.

---

## 2026-03-25 — Session 10: Build (Tier 1 Implementation)

### Baseline
- 49/49 tests pass (pre-build)
- Previous sessions completed: Sessions 1-9

### Implementation: Mechanism 1 — Self-Reference

**What was built:**
- `self_encode` built-in op in `_eval_tree`: when a node's op is `"self_encode"`, it reads `ctx.self_fingerprint`, converts the first 8 hex chars to a float in [0,1), and returns it. Without context, returns 0.0 (backward compatible).
- All 4 fitness functions (`symbolic_regression_fitness`, `sine_approximation_fitness`, `absolute_value_fitness`, `cubic_fitness`) updated to accept optional `ctx: EvalContext = None` and auto-populate `self_fingerprint` from `tree.fingerprint()`.

**F_theo expansion proof:** Self-referential trees can compute fixed-point functions of their own structure — e.g., `add(input_x, self_encode)` computes `f(x) = x + h(T)` where `h(T)` depends on the tree's identity. Non-self-referential trees cannot distinguish themselves from structurally different trees computing the same function. The self_encode op makes each tree's computation dependent on its own identity, strictly expanding the space of representable input-output mappings.

### Implementation: Mechanism 2 — Context-Dependent Evaluation

**What was built:**
- `EvalContext` dataclass: `niche_id`, `generation`, `env_tag`, `self_fingerprint`, `custom` dict. Method `context_key() -> int` hashes `(niche_id, env_tag)` to range [0,3].
- `PolymorphicOp` dataclass: `dispatch_table: Dict[int, Callable]` maps context keys to different implementations. Falls back to `default_fn` when no context or key not in table.
- `_eval_tree` updated: signature `_eval_tree(node, vocab, x, ctx=None)`. Handles `self_encode` special case. For `PolymorphicOp` instances, passes `ctx` to dispatch.
- `CostGroundingLoop.evaluate_with_cost` accepts optional `ctx` parameter.

**F_theo expansion proof:** A context-free tree with n ops computes a fixed function. A context-dependent tree with the same n ops and k=4 context states can compute up to 4 different functions per polymorphic node. For any tree containing at least one PolymorphicOp, F_theo strictly increases.

### Tests added
- `TestSelfReference`: 5 tests (determinism, differentiation, composition, no-context fallback, fixed-point property)
- `TestContextDependentEvaluation`: 8 tests (context creation, key range, polymorphic dispatch, default behavior, eval_tree integration, F_theo proof-of-concept, backward compatibility, fitness function integration)
- **62/62 tests pass** (49 existing + 13 new)

### Files modified
- `main.py` — EvalContext, PolymorphicOp, _eval_tree update, fitness function updates (~+120 lines)
- `test_main.py` — 13 new tests in 2 test classes (~+145 lines)

### Commits
- `31a2d48` — main.py with Mechanism 1 + 2 implementation
- `7cf9aeb` — test_main.py with 13 new tests

### Session assessment
COMPLETE — Tier 1 mechanisms (Self-Reference + Context-Dependent Evaluation) implemented, tested, and pushed.

---

---

## 2026-03-26 — Session 11: V4/V5 Verification + Integration Fix

### Baseline
- 142/142 tests pass (after fixing main.py broken by commit 7d44af1)
- CAGE snapshot: Omega VM backend added (commits 9a21a24, 4ff6b68, 7d44af1)
- Fix applied: restored full architecture from 154f9e7, added omega_backend wiring on top
- Architectural ceiling: unchanged — ExprNode trees NOT Turing-complete

### Monitoring
- arxiv: 22 scanned, 7 relevant
- GitHub: 12 scanned, 3 relevant
- Cumulative: arxiv 79, GitHub 37
- Key finding: NO papers/repos claiming runtime representation FORMAT expansion. Darwin Gödel Machine, Gödel Agent, DéjàQ, OpenEvolve all modify content within fixed formats.

### V4 — End-to-End Evolution Test (CRITICAL)

**Initial V4 result: DEAD_CODE for both Tier 1 mechanisms.**

Root causes identified:
1. **self_encode not registered in VocabularyLayer.** It was handled as a special case in `_eval_tree` but never added to the vocabulary. Grammar's `random_tree` and `mutate` only use registered ops. self_encode was unreachable: 0/1000 random trees, 0/1000 mutations, 0/104 elites across 5 seeds.
2. **MetaGrammarLayer cannot generate PolymorphicOps.** `_get_hyper_rule_templates()` explicitly filters out PolymorphicOps. No meta-rule creates them. 0/100 meta-expansions produced PolymorphicOps. 0/104 elites contained them.

**Fixes applied:**
1. Registered `self_encode` as PrimitiveOp(arity=0, cost=0.5) in `VocabularyLayer._register_defaults()`. Returns 0.0 from vocab; actual fingerprint-dependent value computed in `_eval_tree` via EvalContext.
2. Added `_meta_create_polymorphic_op` meta-rule to MetaGrammarLayer. Takes 2-4 unary ops, bundles into PolymorphicOp dispatching on `topo_key()`. Fires when vocab_size >= 12 and coverage < 0.6.
3. Added `accepts_child_type`, `input_types`, `output_type` to PolymorphicOp dataclass for refinement type compatibility.

**V4 re-run results (5 seeds × 200 generations):**

| Seed | Best Fitness | self_encode in elites | PolymorphicOps in elites |
|------|-------------|----------------------|--------------------------||
| 42   | 0.4995      | 13/22 (59%)          | 7/22 (32%)               |
| 123  | 0.9998      | 4/19 (21%)           | 5/19 (26%)               |
| 456  | 0.9998      | 9/21 (43%)           | 0/21 (0%)                |
| 789  | 0.9998      | 9/20 (45%)           | 0/20 (0%)                |
| 1024 | 0.7183      | 8/21 (38%)           | 0/21 (0%)                |
| **Total** | | **43/103 (42%)** | **12/103 (12%)** |

**V4 VERDICT: USED — Both mechanisms active in evolutionary loop.**

### V5 — Format Isomorphism Test

**Mechanism 1 (Self-Reference / self_encode):**
- |F_theo(baseline, depth=1)| = 14 distinct functions
- |F_theo(+self_encode, depth=1)| = 42 distinct functions
- 28 NEW functions expressible only with self-reference
- Example: `add(x, self_encode)` computes `x + h(T)` where h depends on tree identity. Two structurally different trees compute provably different functions.
- **VERDICT: NON-ISOMORPHIC → GENUINE_F_THEO_EXPANSION**

**Mechanism 2 (Context-Dependent / PolymorphicOp):**
- PolymorphicOp with k variants = syntactic sugar for k base ops selected by position
- At unlimited depth with all base ops available: `F_theo(+poly) = F_theo(base)`
- Any position-dependent dispatch can be replicated by using the k base ops directly
- **VERDICT: ISOMORPHIC at unlimited resources → F_EFF_GAIN_UNDER_CONSTRAINT**
- Reclassification: Mechanism 2 is not a cage-breaking expansion but a search efficiency improvement under depth constraints.

### Verification Summary Table

```
V1 F_theo changed:        YES (Mechanism 1), NO (Mechanism 2)
V2 Prior work:            YES — Kleene recursion theorem (1938), quines
V3 Self-expansion:        EXTERNAL (agent registered self_encode + poly meta-rule)
V4 Evolution loop:        USED — 42% elites use self_encode, 12% use PolymorphicOps
V5 Format isomorphism:    NON-ISOMORPHIC (M1), ISOMORPHIC (M2)

FINAL VERDICT:
  Mechanism 1 (Self-Reference): GENUINE_F_THEO_EXPANSION + REIMPLEMENTATION + EXTERNAL_INJECTION
  Mechanism 2 (Context-Dependent): F_EFF_GAIN_UNDER_CONSTRAINT + EXTERNAL_INJECTION
```

**Honest assessment:** Mechanism 1 genuinely expands F_theo but is a reimplementation of well-known self-reference (Kleene 1938). It was externally injected (agent wrote the code). The evolutionary loop uses it but could not have discovered it on its own — the system cannot add new PrimitiveOps to its own vocabulary without meta-grammar intervention. Mechanism 2 is an efficiency gain, not an expansion.

### Tests added
- `TestV4SelfEncodeEvolutionIntegration`: 3 tests (vocab registration, random tree appearance, elite usage)
- `TestV4PolymorphicOpEvolutionIntegration`: 3 tests (meta-grammar creation, type compat, evolved population)
- `TestV5FormatIsomorphism`: 2 tests (self_encode F_theo expansion, PolymorphicOp F_eff)
- **150/150 tests pass** (94 main + 56 omega_backend)

### Files modified
- `main.py` — self_encode PrimitiveOp registration, _meta_create_polymorphic_op rule, PolymorphicOp type compatibility (~+70 lines)
- `test_main.py` — 8 new V4/V5 tests (~+100 lines)
- `docs/monitoring-log.md` — 2026-03-26 scan results
- `docs/session-tracker.md` — Session 11 entry
- `docs/daily-log.md` — This entry

### Session assessment
COMPLETE — V4 and V5 verification performed. Critical DEAD_CODE issue found and fixed. Both mechanisms now active in evolutionary loop. Mechanism 1 confirmed as genuine F_theo expansion. Mechanism 2 reclassified as F_eff gain.

---

## Protocol Summary: Design Space Escape Protocol v4

**Total sessions:** 11 (8 domain + 1 synthesis + 1 build + 1 verification)
**Total extractions:** 60 across 8 domains
**STRUCTURAL_EXPANSION rate:** 55% (33/60)
**Mechanism families identified:** 7
**Mechanisms implemented:** 2 (Tier 1: Self-Reference + Context-Dependent Evaluation)
**V4/V5 verified:** YES — Mechanism 1 = GENUINE_F_THEO_EXPANSION, Mechanism 2 = F_EFF_GAIN
**Final test count:** 150/150 pass
**Architectural ceilings addressed:** #1 (self-reference) via self_encode, #2 (adaptive grammar) partially via PolymorphicOp context dispatch
