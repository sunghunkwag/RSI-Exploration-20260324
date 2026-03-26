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
- **V1 potential:** MEDIUM — genuine FORMAT_CHANGE (levels become terms), but may be isomorphic to simply using larger fixed depth at unlimited resources
- **Status:** NOT_IMPLEMENTED — requires formal analysis of whether depth-as-first-class-value expands F_theo or is isomorphic to unbounded fixed depth
- **Blacklist check:** CLEAR — not a variant of B01-B14
- **Date:** 2026-03-26
- **Flag:** NEEDS_ISOMORPHISM_ANALYSIS before implementation
