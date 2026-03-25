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
2. **A.4 Van Wijngaarden Two-Level Grammars** — Metarules + hyperrules generate infinite concrete grammar from finite specification. Layer 3 → Layer 2.
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
- STRUCTURAL_EXPANSION verdicts: 5 (C.1b Paribhāṣā, C.1c Kāraka, C.3 Aramaic polysemy, C.4 Cuneiform evolution, C.5 DSS variants)
- COMBINATORIAL_RECOMBINATION verdicts: 2 (C.1a Pratyāhāra, C.2 Hebrew binyanim)
- Mixed: 1 (C.6 Script evolution)

### Key findings from Domain C

**Dominant pattern: context-dependent evaluation is the primary expansion mechanism.** Three independent sub-topics converge on making evaluation context-dependent.

1. **Context-dependent evaluation** (C.3 + C.4 + C.1c) — Polymorphic PrimitiveOps with context threading. FORMAT_CHANGE.
2. **Paribhāṣā conflict resolution** (C.1b) — Replace random rule selection with specificity-based deterministic resolution.
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
- STRUCTURAL_EXPANSION verdicts: 5 (D.1 Quines/Kleene, D.5 Type Systems, D.6 Automata/TAG, D.7 Gödel Machines, D.8 Continuations/Effects)
- COMBINATORIAL_RECOMBINATION verdicts: 3 (D.2 GGGP/GE, D.3 DreamCoder, D.4 Reflection)

### Key findings from Domain D

**Self-reference is the master cage-breaking mechanism.** D.1→D.4→D.7 progression.

1. **Gödel Machine** (D.7) — system rewrites its own evaluation mechanism; ultimate cage-breaking.
2. **Quines / self-reference** (D.1) — trees referencing own encoding. ≡ A.7.
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

1. **Topology optimization** (F.5) — discrete→continuous FORMAT_CHANGE (=E.3=B.1/B.8, now 4 domains).
2. **Origami algebraic tower** (F.6) — quadratic→cubic field extension. New Galois-theoretic expansion.

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
2. **Categorification** (H.5) — Systematic format lifting (int→vector space, polynomial→chain complex). Functorial information gain.
3. **Crystal bases** (H.3) — Expansion via dimensional reduction (q→0). Paradoxical expansion via restriction (matches G.1).
4. **Geometric rep theory** (H.4) — Sheaf-theoretic methods reveal algebraically invisible structure.
5. **Quiver root classification** (H.2) — Dynkin diagrams organize representation types.

**Cross-domain:** H.8=A.3/A.4 (meta-grammar), H.5=B/E/F (format lifting), H.3=G.1 (expansion via restriction), H.4=G.6 (geometric methods), H.7=B.4-B.6 (duality=recombination).

### Session assessment
COMPLETE — All 8 sub-topics. Domain H report written to docs/domains/domain-H-representation.md.
