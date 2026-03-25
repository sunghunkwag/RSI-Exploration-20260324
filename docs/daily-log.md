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
