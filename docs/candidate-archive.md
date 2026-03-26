# Candidate Archive

## Format
Each entry: mechanism name, source, formal extraction, V1 status, date added.

## Entries

### Candidate 1: Self-Reference (self_encode)
- **Source:** A.7 Diagonal Lemma, D.1 Quines/Kleene, D.7 Gödel Machines
- **Old format:** ExprNode trees with fixed vocabulary
- **New format:** ExprNode trees with self_encode op accessing own fingerprint
- **Became expressible:** Fixed-point functions of tree identity
- **Computable:** YES (implemented)
- **V1:** GENUINE_F_THEO_EXPANSION
- **V5:** NON-ISOMORPHIC
- **Status:** IMPLEMENTED (Session 10-11), VERIFIED
- **Date:** 2026-03-25

### Candidate 2: Context-Dependent Evaluation (PolymorphicOp)
- **Source:** C.1c Karaka, C.3 Aramaic polysemy, G.6 Topos Theory
- **Old format:** eval(T, x) → float
- **New format:** eval(T, x, ctx) → float with dispatch
- **Became expressible:** Multiple behaviors per tree structure
- **Computable:** YES (implemented)
- **V1:** NO (F_EFF_GAIN_UNDER_CONSTRAINT, isomorphic at unlimited resources)
- **V5:** ISOMORPHIC
- **Status:** IMPLEMENTED (Session 10-11), RECLASSIFIED
- **Date:** 2026-03-25

### Candidate 3: Adaptive Grammar (ConditionalGrammarRule + GrammarRuleComposer)
- **Source:** A.3 Shutt Adaptive Grammars, H.8 Operads
- **V1:** NO (F_EFF_GAIN — grammar rules are search operators)
- **Status:** IMPLEMENTED (Session 12), VERIFIED as F_eff only
- **Date:** 2026-03-26

### Candidate 4: Learned Specificity (Enhanced MetaRuleEntry)
- **Source:** C.1b Paribhasa, E.4 GTTM preference rules
- **V1:** NO (F_EFF_GAIN — changes selection order, not what rules produce)
- **Status:** IMPLEMENTED (Session 12), VERIFIED as F_eff only
- **Date:** 2026-03-26

## Unimplemented candidates from synthesis (Session 9)

### Candidate 5: Discrete→Continuous FORMAT_CHANGE
- **Source:** B.1 Higgs, E.3 Spectral, F.5 Topology Optimization
- **V1 potential:** YES — continuous primitives strictly expand F_theo
- **Status:** NOT_IMPLEMENTED — requires replacing ExprNode discrete ops with continuous-valued ops
- **Date:** 2026-03-25

### Candidate 6: Categorification / Systematic Format Lifting
- **Source:** H.5, H.4, A.2 Kan Extensions, A.1 Induction-Recursion
- **V1 potential:** UNCLEAR — functorial lifting may be isomorphic at unlimited resources
- **Status:** NOT_IMPLEMENTED
- **Date:** 2026-03-25

### Candidate 7: Bidirectional Abstraction (Fine-graining)
- **Source:** B.3 Wilson RG, C.6 Script evolution, H.2 Quiver roots
- **V1 potential:** LOW — inverse of LibraryLearner, likely F_eff
- **Status:** NOT_IMPLEMENTED
- **Date:** 2026-03-25

### Candidate 8: First-Class Meta-Level Parameters (from Bounded Universe Levels)
- **Source:** arxiv:2502.20485 (Chan et al., TTBFL), related to A.1 Induction-Recursion
- **Old format:** ExprNode trees with max_depth as fixed integer parameter
- **New format:** ExprNode trees where depth/meta-level is a first-class computable expression within the tree language
- **Became expressible:** Recursive definitions with depth-varying recursive calls; trees that compute their own depth bounds contextually
- **Transition op:** Internalize max_depth from external parameter to first-class bounded type (Depth < k) within tree expressions
- **Computable:** YES in principle (TTBFL has explicit syntax, Agda mechanization exists via IR)
- **V1 potential:** ~~MEDIUM~~ → **LOW (F_EFF only in current format)**
- **Blacklist check:** CLEAR — not a variant of B01-B14
- **Date:** 2026-03-26
- **Isomorphism analysis (2026-03-26 Day 3):**
  TTBFL's first-class levels are genuinely more expressive than prenex polymorphism IN TYPE THEORY because type theories support recursive definitions with level-varying recursive calls (e.g., incr k (succ n) = incr n [k+1]). Monomorphization provably fails for such definitions.
  However, ExprNode trees are FINITE expression trees, not recursive programs. A tree that "computes its own depth" still produces a fixed finite depth value. Without recursion in the tree language, every first-class-depth tree is equivalent to some fixed-depth tree — the depth computation just selects which fixed depth to use.
  Therefore: first-class depth in the CURRENT ExprNode format is ISOMORPHIC to unbounded fixed depth at unlimited resources. The FORMAT_CHANGE from TTBFL is only genuine when the language supports recursive definitions, which ExprNode trees do not.
  **COROLLARY:** To make first-class depth genuinely expand F_theo, the system would FIRST need recursive tree evaluation (trees calling themselves). This is Candidate 1 (self_encode) extended with depth-varying recursion. The combination self_encode + first-class depth could be genuinely new — a self-referential tree that adjusts its recursion depth based on its own structure. This is noted as a potential Candidate 8b.
- **Status:** RECLASSIFIED as F_EFF_GAIN_UNDER_CONSTRAINT. Not worth implementing alone. Revisit if recursive tree evaluation (self_encode with explicit recursion depth) is developed.
- **V5 verdict:** ISOMORPHIC (at unlimited resources, equivalent to unbounded fixed depth)
