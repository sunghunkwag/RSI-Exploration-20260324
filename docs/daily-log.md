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
- Architectural ceiling: ExprNode trees are NOT Turing-complete — specifically cannot express: self-reference (no tree can reference its own encoding), adaptive grammar rules (rule set is static during evaluation), simultaneous induction-recursion (no type/interpretation co-definition)
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
- NO_STRUCTURE_FOUND: 0
- Remaining incomplete: 0

### Key findings from Domain A

**Strongest cage-breaking candidates (Layer 3 / FORMAT_CHANGE):**

1. **A.3 Adaptive Grammars (Shutt)** — Rule set becomes a dynamic semantic object modified during evaluation. Direct transplant: `GrammarLayer.active_rules(attributes)` where attributes are computed from archive state. Makes rule activation conditional on population characteristics rather than random. Layer 3.

2. **A.4 Van Wijngaarden Two-Level Grammars** — Metarules + hyperrules generate infinite concrete grammar from finite specification via consistent substitution. Transplant: parameterize grammar rules with metanotions (ARITY, TYPE, etc.) and systematically instantiate. Replaces random rule generation with parametric expansion. Layer 3 → Layer 2.

3. **A.7 Diagonal Lemma (Self-Reference)** — Trees that can reference their own encoding. Transplant: add `self_encode` primitive operator + tree-fingerprint context variable during evaluation. Enables reflective trees that inspect/modify their own structure. FORMAT_CHANGE: adds reflexive capacity absent from current format. F_theo expansion: self-referential trees can express fixed-point computations that non-self-referential trees cannot.

4. **A.1 Induction-Recursion** — Simultaneous definition of codes + interpretation. Transplant: vocabulary entries defined simultaneously with their semantics (currently, `_meta_compose_new_op` creates primitives without interpretation constraints). Layer 3 + FORMAT_CHANGE.

**Within-format (not cage-breaking):**

5. **A.6 Priority Arguments** — Conflict resolution for multi-objective expansion. Useful for implementation (principled MetaGrammarLayer expansion ordering) but does not change F_theo. COMBINATORIAL_RECOMBINATION.

**High value but computability concerns:**

6. **A.5 Univalence** — Quotient ExprNode space by structural equivalence. Valuable for search efficiency (collapse equivalent representations) but univalence itself is not computable as axiom. Cubical interpretation partially resolves this. Transplant: `ExprNode.canonical_form()` for archive deduplication.

### Session assessment
COMPLETE — All 7 sub-topics have full formal structure extractions with old/new format, transition operation, expressibility analysis, computability assessment, CAGE diagnosis, and transplant sketch. Domain A report written to docs/domains/domain-A-mathematics.md.

---

## 2026-03-25 — Session 2: Domain B (Physics, Cosmology & Fundamental Theory)

### Baseline
- 49/49 tests pass
- CAGE snapshot: no changes since Session 1 (same day)
- Architectural ceiling: unchanged from Session 1
- Today's domain: B (Physics, Cosmology & Fundamental Theory)
- Previous sessions completed: Session 1 (Domain A)

### Monitoring
- arxiv: 19 scanned, 8 relevant, 8 deeper_read (incremental)
- GitHub: 0 incremental (reused Session 1 scan)
- Cumulative: arxiv 57, GitHub 25

### Domain investigation
- Sub-topics investigated: 9
- Full formal extractions completed: 9
- STRUCTURAL_EXPANSION verdicts: 4 (B.1 Higgs, B.3 Wilson RG, B.7 M-theory, B.8 Electroweak)
- COMBINATORIAL_RECOMBINATION verdicts: 5 (B.2 Landau, B.4 T-duality, B.5 S-duality, B.6 AdS/CFT, B.9 Nucleosynthesis)
- NO_STRUCTURE_FOUND: 0
- Remaining incomplete: 0

### Key findings from Domain B

**Critical pattern discovered: dualities are isomorphisms, not expansions.** T-duality, S-duality, and AdS/CFT all preserve F_theo. They provide computational access to different regimes but do not expand expressibility. This is an important diagnostic: any proposed "expansion" that is actually a duality/isomorphism should be immediately reclassified as COMBINATORIAL_RECOMBINATION.

**Genuine expansions in physics come from two mechanisms:**

1. **Symmetry breaking** (B.1 Higgs, B.8 Electroweak) — vacuum selection creates new mass eigenstates (linear combinations) inexpressible in the symmetric representation. FORMAT_CHANGE. Transplant: "vacuum selection" on ExprNode trees = fixing a structural template and expanding as perturbations around it.

2. **Coarse-graining / RG** (B.3 Wilson) — integrating out fine structure generates new effective operators absent from original Lagrangian. Layer 1+2 expansion. **KEY INSIGHT: Wilson RG IS structurally identical to LibraryLearner.** The RSI system already implements the core RG operation. The connection is not metaphorical — it is formal.

3. **Unification** (B.7 M-theory) — embedding multiple formats into a higher-dimensional framework reveals structure invisible in any single component. Transplant: define a meta-format subsuming ExprNode trees + stack-based + graph-based programs, evolve in meta-format. Directly addresses standing rule #12 (architectural question).

**Within-format but useful for implementation:**

4. **Threshold-gated expansion** (B.9 Nucleosynthesis) — staged unlocking of progressively disruptive operations based on "computational temperature." Transplant: define T_comp thresholds for MetaGrammarLayer operations.

5. **Landscape bifurcation detection** (B.2 Landau) — monitor second derivative of fitness vs. control parameter to detect phase transitions in the evolutionary search. Trigger expansion at bifurcation points.

### Session assessment
COMPLETE — All 9 sub-topics have full formal structure extractions. Domain B report written to docs/domains/domain-B-physics.md. Key insight: Wilson RG = LibraryLearner (structural, not metaphorical). Pattern: dualities preserve F_theo; symmetry breaking and coarse-graining expand it.

---

## 2026-03-25 — Session 3: Domain C (Ancient Texts, Manuscripts & Historical Linguistics)

### Baseline
- 49/49 tests pass
- CAGE snapshot: no changes since Session 2 (same day)
- Architectural ceiling: unchanged from Session 1
- Today's domain: C (Ancient Texts, Manuscripts & Historical Linguistics)
- Previous sessions completed: Session 1 (Domain A), Session 2 (Domain B)

### Monitoring
- arxiv: 0 incremental (3rd session same day, reused prior scans)
- GitHub: 0 incremental
- Cumulative: arxiv 57, GitHub 25

### Domain investigation
- Sub-topics investigated: 8
- Full formal extractions completed: 8
- STRUCTURAL_EXPANSION verdicts: 5 (C.1b Paribhāṣā, C.1c Kāraka, C.3 Aramaic polysemy, C.4 Cuneiform evolution, C.5 DSS variants)
- Mixed (STRUCTURAL + COMBINATORIAL): 1 (C.6 Script evolution)
- COMBINATORIAL_RECOMBINATION verdicts: 2 (C.1a Pratyāhāra, C.2 Hebrew binyanim)
- NO_STRUCTURE_FOUND: 0
- Remaining incomplete: 0

### Key findings from Domain C

**Dominant pattern: context-dependent evaluation is the primary expansion mechanism.** Three independent sub-topics (C.1c kāraka, C.3 Aramaic polysemy, C.4 cuneiform polyvalence) converge on the same structural expansion: making evaluation context-dependent. Current ExprNode evaluation is context-free. Adding context threading + polymorphic ops + determinative type annotations is a single coherent FORMAT_CHANGE.

**Strongest cage-breaking candidates:**

1. **Context-dependent evaluation** (C.3 + C.4 + C.1c) — Polymorphic PrimitiveOps with function sets, dispatchers, and context threading through evaluation. FORMAT_CHANGE. Extends F_theo: same tree structure can compute different functions based on evaluation context.

2. **Resegmentation / latent structure discovery** (C.5 L2) — Re-parsing existing trees under alternative grammars reveals structure invisible to current parse. Zero-cost expansion (no new primitives needed).

3. **Paribhāṣā conflict resolution** (C.1b) — Replace random rule selection in MetaGrammarLayer with operand-specificity-based deterministic resolution. Makes grammar expansion compositional and predictable.

4. **Bidirectional abstraction** (C.6) — Library learning only coarse-grains (subtrees → primitives). The alphabetic decomposition principle adds fine-graining (primitives → sub-atomic components). Bidirectional movement across abstraction hierarchy.

**Cross-domain connection:** C.6's fine-graining is the exact inverse of B.3 Wilson RG / LibraryLearner. The RSI system currently only moves in the RG direction; adding the reverse (decomposition) would enable full abstraction navigation.

### Session assessment
COMPLETE — All 8 sub-topics have full formal structure extractions. Domain C report written to docs/domains/domain-C-linguistics.md. Key insight: context-dependent evaluation is the dominant expansion mechanism (convergent across 3 independent sub-topics). Cross-domain: fine-graining (C.6) is inverse of coarse-graining (B.3/LibraryLearner).

---

## 2026-03-25 — Session 4: Domain D (Computer Science & Computation Theory)

### Baseline
- 49/49 tests pass
- CAGE snapshot: no changes since Session 3 (same day)
- Architectural ceiling: unchanged from Session 1
- Today's domain: D (Computer Science & Computation Theory)
- Previous sessions completed: Sessions 1-3 (Domains A, B, C)

### Monitoring
- arxiv: 0 incremental (4th session same day)
- GitHub: 0 incremental
- Cumulative: arxiv 57, GitHub 25

### Domain investigation
- Sub-topics investigated: 8
- Full formal extractions completed: 8
- STRUCTURAL_EXPANSION verdicts: 5 (D.1 Quines/Kleene, D.5 Type Systems, D.6 Automata/TAG, D.7 Gödel Machines, D.8 Continuations/Effects)
- COMBINATORIAL_RECOMBINATION verdicts: 3 (D.2 GGGP/GE, D.3 DreamCoder, D.4 Reflection)
- NO_STRUCTURE_FOUND: 0
- Remaining incomplete: 0

### Key findings from Domain D

**Self-reference is the master cage-breaking mechanism.** D.1 (quines), D.4 (reflection), and D.7 (Gödel Machines) form a progression addressing the three architectural ceilings.

**Strongest cage-breaking candidates:**

1. **Gödel Machine / self-modification** (D.7) — system rewrites its own evaluation mechanism; ultimate cage-breaking.
2. **Quines / self-reference** (D.1) — trees referencing own encoding. Same mechanism as A.7 (Diagonal Lemma).
3. **Continuations / algebraic effects** (D.8) — adds entire control flow dimension absent from current system.
4. **Indexed grammars / TAG adjunction** (D.6) — moves ExprNode from regular tree grammar to mildly context-sensitive.
5. **Dependent / refinement types** (D.5) — type-indexed composition rules + verification.

**Cross-domain connections:** D.1≡A.7, D.4≡C.3/C.4, D.7⊃B.3.

### Session assessment
COMPLETE — All 8 sub-topics have full formal structure extractions. Domain D report written to docs/domains/domain-D-cs.md. Key insight: self-reference is the master cage-breaking mechanism (D.1→D.4→D.7 progression). LibraryLearner already implements core program synthesis mechanism (D.2, D.3 = COMBINATORIAL_RECOMBINATION).

---

## 2026-03-25 — Session 5: Domain E (Music, Acoustics & Compositional Theory)

### Baseline
- 49/49 tests pass
- CAGE snapshot: no changes since Session 4 (same day)
- Architectural ceiling: unchanged from Session 1
- Today's domain: E (Music, Acoustics & Compositional Theory)
- Previous sessions completed: Sessions 1-4 (Domains A, B, C, D)

### Monitoring
- arxiv: 0 incremental (5th session same day)
- GitHub: 0 incremental
- Cumulative: arxiv 57, GitHub 25

### Domain investigation
- Sub-topics investigated: 6
- Full formal extractions completed: 6
- STRUCTURAL_EXPANSION verdicts: 4 (E.1 Schenkerian Analysis, E.3 Spectral Music, E.4 GTTM, E.6 Microtonality/JI)
- COMBINATORIAL_RECOMBINATION verdicts: 2 (E.2 Serialism, E.5 L-Systems)
- NO_STRUCTURE_FOUND: 0
- Remaining incomplete: 0

### Key findings from Domain E

**Cross-domain convergence dominates this domain.** Four of five cross-domain patterns connect to previously identified mechanisms.

**Strongest cage-breaking candidates:**

1. **Spectral / continuous primitives** (E.3) — FORMAT_CHANGE from discrete scalar to continuous vector. Same structural expansion as B.1/B.8 (physics). Transplant: extend PrimitiveOp to output vectors (SpectralOp), add spectral composition rules. Layer 1 + FORMAT_CHANGE.

2. **Preference-based rule selection** (E.4 GTTM) — Replace random rule selection with preference-ranked selection. Converges with C.1b (paribhāṣā) — three domains now independently identify this mechanism. Transplant: multi-component hierarchy with cross-constraints. Layer 2.

3. **Structure-preserving composition** (E.1 Schenkerian) — Multi-level prolongation preserving structural tones of higher levels. New composition mode absent from ExprNode. Connects to D.6 (TAG adjunction). Layer 2 + FORMAT_CHANGE.

4. **Lattice-structured vocabulary** (E.6 JI/Microtonality) — Infinite lattice with geometric consonance constraints. Genuinely expands vocabulary with structured relationships. Layer 1 + FORMAT_CHANGE.

**Within-format (not cage-breaking):**

5. **Group symmetry operations** (E.2 Serialism) — Bijections on same set. Confirms B.4-B.6 pattern: symmetry-preserving transformations = COMBINATORIAL_RECOMBINATION.

6. **Parallel rewriting** (E.5 L-systems) — Exponential compactness but same F_theo. Useful as MetaGrammarLayer strategy.

**Key cross-domain patterns:**
- E.3 = B.1/B.8 (continuous primitives are recurring FORMAT_CHANGE)
- E.4 = C.1b (preference rules replace random selection — 3 independent domains)
- E.2 confirms B.4-B.6 (group symmetry = recombination)
- E.1 connects to D.6 (structure-preserving hierarchical composition)

### Session assessment
COMPLETE — All 6 sub-topics have full formal structure extractions. Domain E report written to docs/domains/domain-E-music.md. Key insight: cross-domain convergence is the dominant finding — continuous primitives (E.3=B.1/B.8), preference rules (E.4=C.1b), group symmetry as recombination (E.2=B.4-B.6). No fundamentally new cage-breaking mechanism discovered; rather, Domain E reinforces and validates patterns from Domains A-D.
