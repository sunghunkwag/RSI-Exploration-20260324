# Domain H — Representation Theory & Algebraic Structures

**Session 8 | Date: 2026-03-25 | Status: COMPLETE**

---

## H.1 — Young Tableaux & Symmetric Group Representations (Young, Vershik-Okounkov)

### SOURCE
Young (1900), partition lattice and tableau enumeration.
Vershik & Okounkov (2005), "A New Approach to Representation Theory of Symmetric Groups."
Robinson-Schensted-Knuth correspondence.
Schur-Weyl duality (polynomial representations vs. highest weights).
Littlewood-Richardson rule.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Symmetric group S_n acts on n-element sets; irreducibles indexed by partitions λ ⊢ n via Young diagrams; dimension = n!/hook product.

**New format:** Tableaux as ordered sequences of cells; RSK maps permutations π ↔ pairs (P,Q) of standard Young tableaux; bijection reveals multiplicities at combinatorial level. Branching via Littlewood-Richardson coefficients.

**Transition op:** Insertion of elements into P-tableau (bumping algorithm); growth sequence of shapes λ^(0) ⊂ λ^(1) ⊂ ... ⊂ λ^(n).

**Became expressible:** Branching rules computed as tableau counts. Plethysm via skew tableaux. Character evaluation via hook-length formula. Multiplicities become enumerable combinatorial objects.

**Computable:** YES — Hook-length formula closed-form; RSK O(n log n); LR coefficients enumerated combinatorially.

### CAGE DIAGNOSIS
**Layer affected:** Layer 2 (GrammarLayer)
**Within-format:** YES — Both source (S_n actions) and target (tableaux pairs) are discrete combinatorial objects. RSK is a bijection (same F_theo). Matches B.4-B.6 duality pattern.

### TRANSPLANT SKETCH
Bumping algorithm as composition rule: insert(elem, tableau) → new tableau. Shape tracking as MAP-Elites descriptor. Useful for archive organization (partition-indexed behavioral space), not F_theo expansion.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## H.2 — Quiver Representations (Gabriel, Kac)

### SOURCE
Gabriel (1972), "Unzerlegbare Darstellungen I."
Kac (1983), "Root Systems, Representations of Quivers and Invariant Theory."
Ringel (1998), path algebras and hereditary algebras.
Assem, Simson & Skowroński (2006), *Elements of the Representation Theory of Associative Algebras*.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Quiver Q = (vertices V, arrows E). Representation ρ assigns vector spaces to vertices, linear maps to arrows. Morphism spaces via path algebra. No principled classification of indecomposables.

**New format:** Dimension vector d = (d_i) ∈ ℤ≥0^|V|. Gabriel's theorem: finite representation type ↔ Dynkin diagram (A,D,E). Indecomposables ↔ positive real roots of Gabriel form q(x) = Σ x_i² − Σ_{(i→j)} x_i x_j. Reflection functors Σ_k rotate through root system.

**Transition op:** Reflection functor Σ_k: Mod(Q) → Mod(s_k Q). Dimension vector undergoes simple reflection. Auslander-Reiten quiver extracted from Gabriel form.

**Became expressible:** Finite type classification reduced to graph-theoretic check (Dynkin). Module categories organized by root posets. Imaginary roots (Kac) extend to affine/wild types. Auslander-Reiten structure determinable from combinatorial data.

**Computable:** PARTIAL — Dimension vectors and Gabriel form computable. Full Auslander-Reiten structure requires Ext¹ calculations. Tractable for small quivers.

### CAGE DIAGNOSIS
**Layer affected:** Layer 2 (GrammarLayer)
**Within-format:** NO — Gabriel's reduction links quiver combinatorics to Lie-theoretic root systems. Reflection functors create structural bridge between module categories and Dynkin geometry. New dimension: root-system classification unavailable from path algebra alone.

### TRANSPLANT SKETCH
QuiverNode type: directed graph with vector space assignments. Reflection functor as mutation operator. Dimension vector as MAP-Elites descriptor. Gabriel form as fitness landscape topology detector (Dynkin → finite type, affine → tame, wild → undecidable). Root classification organizes search space.

### VERDICT: STRUCTURAL_EXPANSION

---

## H.3 — Crystal Bases & Canonical Bases (Kashiwara, Lusztig)

### SOURCE
Kashiwara (1990), "Crystalizing the q-Analogue of Universal Enveloping Algebras."
Lusztig (1990), "Canonical Bases Arising from Quantized Enveloping Algebras."
Nakashima & Zelevinsky, tableaux realization of crystals.
Berenstein & Zelevinsky (1992), explicit canonical basis formulas.

### FORMAL STRUCTURE EXTRACTION

**Old format (Quantum group representations):** U_q(𝔤) has basis parametrized by monomial ordering; representations deform continuously in q. Multiplication non-commutative; q-binomial coefficients required. Structure opaque at generic q.

**New format (Crystal bases):** At q→0, U_q(𝔤) degenerates to combinatorial poset of crystal paths. Kashiwara operators F_i, E_i act on crystal nodes. Crystal graph: vertices = basis elements, edges = F_i actions. Structure completely determined by Dynkin diagram. Canonical basis B(λ) has positive integer coefficients in monomial expansion.

**Transition op:** q→0 singular limit. Canonical basis B(λ) of highest-weight module V(λ) yields crystal graph. Tensor product: B(λ) ⊗ B(μ) = ⊕_ν m^{λμ}_ν B(ν) computed via crystal operator commutation.

**Became expressible:** Combinatorial skeleton of quantum group representations — multiplicities, weight spaces readable from crystal graph alone without q-arithmetic. Tensor product multiplicities from crystal tableaux. Positivity: canonical basis coefficients are positive integers. Dimension reduction: continuous q-parameter eliminated.

**Computable:** YES — Crystal graph generated by iterative F_i applications; finite for highest-weight modules. Multiplicities from crystal tableaux enumeration.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 2 + FORMAT_CHANGE
**Within-format:** NO — Transition from q-dependent continuous deformation to q→0 discrete crystal. This is the continuous→discrete direction (inverse of recurring B/E/F pattern). Crystal basis provides meta-structure unifying all U_q(𝔤) modules independent of q.

### TRANSPLANT SKETCH
CrystalOp primitives: F_i(node) → node, E_i(node) → node, weight(node) → lattice point. Crystal path = sequence of Kashiwara operators from highest weight. Composition via tensor product rule. MAP-Elites descriptors: weight vector, crystal path length, tensor multiplicity. Positivity theorem constrains search: only positive-integer combinations valid.

### VERDICT: STRUCTURAL_EXPANSION

---

## H.4 — Geometric Representation Theory (Springer, Kazhdan-Lusztig)

### SOURCE
Springer (1976), correspondence between conjugacy classes and Weyl group irreducibles.
Kazhdan & Lusztig (1979), "Representations of Coxeter Groups and Hecke Algebras."
Beilinson & Bernstein (1981), localization theorem for category O.
Mirković & Vilonen (2004), geometric Satake equivalence.
Chriss & Ginzburg (1997), *Representation Theory and Complex Geometry*.

### FORMAL STRUCTURE EXTRACTION

**Old format (Algebraic):** Representations of reductive group G defined via module structures over enveloping algebra. Characters computed via highest-weight vectors. Irreducibility checked by invariant subspace analysis. Multiplicities opaque.

**New format (Geometric):** Represent irreducibles via D-modules/perverse sheaves on geometric spaces. Springer: conjugacy classes G//G → Weyl group irreducibles via Springer fiber cohomology. Kazhdan-Lusztig: Hecke algebra irreducibles parametrized by KL polynomials P_{y,w}(q) from Schubert variety singularities. Beilinson-Bernstein: category O ≅ D-modules on flag variety G/B.

**Transition op:** Geometric realization: character ↔ intersection cohomology on variety. Localization: sheaf sections ↔ algebraic modules. Springer resolution: T*G/B → nilpotent cone N.

**Became expressible:** Singularities encode representation structure (KL positivity is purely geometric). Derived equivalences: Perv(G/B) ≅ D^b(Hecke-mod). Positivity and unimodality of KL polynomials (geometric proof). Satake: loop group representations ≅ affine Hecke modules.

**Computable:** PARTIAL — KL polynomials recursively computable (defined by positivity + initial conditions). Springer correspondence effective for small rank. Full localization requires sophisticated homological algebra.

### CAGE DIAGNOSIS
**Layer affected:** Layer 2 + Layer 3 + FORMAT_CHANGE
**Within-format:** NO — Transition from algebraic (modules, characters) to geometric (varieties, sheaves, cohomology). Singularities reveal multiplicities invisible to algebra alone. This is the most dramatic representational elevation in the H domain.

### TRANSPLANT SKETCH
CohomologyOp: computes intersection cohomology of expression-indexed varieties. KL polynomial as structural complexity measure. Localization principle: expressions that are "locally equivalent" (sheaf-theoretically) share representation structure. MAP-Elites descriptors: variety dimension, singularity type, KL polynomial degree. Connects to G.6 (topos-internal logic) — both use geometric/sheaf-theoretic methods to reveal hidden structure.

### VERDICT: STRUCTURAL_EXPANSION

---

## H.5 — Categorification & Decategorification (Khovanov, Crane-Frenkel)

### SOURCE
Khovanov (2000), "A Categorification of the Jones Polynomial."
Crane & Frenkel (1994), "Four-dimensional TQFT and Hopf Categories."
Bar-Natan (2005), "Khovanov's Homology for Tangles and Cobordisms."

### FORMAL STRUCTURE EXTRACTION

**Old format (Numerical invariants):** Polynomial invariant P(q): Link → ℤ[q, q⁻¹]. Jones polynomial as scalar encoding. Integers count components/crossings. Information compressed into single polynomial.

**New format (Categorified):** Chain complex C(L): Link → {bigraded chain complexes}. Khovanov homology H*(C(L)) recovers P(q) via Euler characteristic. Integer → graded vector space (dim = integer). Polynomial → chain complex (Euler char = polynomial). Functorial under cobordisms.

**Transition op:** LIFT: integer n → graded vector space V with dim(V) = n. DECATEGORIFY: chain complex C → polynomial via graded Euler characteristic.

**Became expressible:** Bigraded structure (quantum + homological degrees). Functoriality under cobordisms (invisible in polynomial). Torsion information absent from Jones polynomial. Spectral sequence structure. Web of categorified invariants (sl(N) → HOMFLY).

**Computable:** YES — Khovanov homology computable via Bar-Natan spectral sequences for reasonable knots.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 2 + FORMAT_CHANGE
**Within-format:** NO — Integers become vector spaces; polynomials become chain complexes. This is the discrete→richer-structure FORMAT_CHANGE. The lift adds homological dimension absent from decategorified invariant.

### TRANSPLANT SKETCH
CategorifyOp: lifts scalar PrimitiveOp outputs to graded vector spaces. ChainComplexComposition: composes via tensor product of complexes. Decategorification recovers original scalar fitness. MAP-Elites descriptors: homological degree, Betti numbers, torsion rank. Key insight: categorified expressions carry strictly more information than their decategorified projections.

### VERDICT: STRUCTURAL_EXPANSION

---

## H.6 — Tensor Categories & Fusion Categories (Turaev, Etingof)

### SOURCE
Turaev (1994), *Quantum Invariants of Knots and 3-Manifolds*.
Etingof, Gelaki, Nikshych & Ostrik (2015), *Tensor Categories*.
Rowell & Wang (2018), "Mathematics of Topological Quantum Computing."

### FORMAL STRUCTURE EXTRACTION

**Old format (Representation categories):** Rep(G) with tensor product ⊗. Multiplicity tensor m^k_{ij} as lookup table. Fusion rules: i ⊗ j = Σ_k m^k_{ij} k. No braiding or higher structure.

**New format (Fusion/modular tensor categories):** Semisimple tensor category C with simple objects {X_i}, natural associativity/unitality, braiding σ_{X,Y}: X ⊗ Y → Y ⊗ X, ribbon structure (twist θ_X, duals). Modular data: S, T matrices encoding topological order. Fusion rules enriched with braiding constraints (Yang-Baxter).

**Transition op:** TENSOR_ENRICH: fusion rules → braided ribbon tensor category. MODULARIZE: ribbon structure → TQFT via Reshetikhin-Turaev construction.

**Became expressible:** Braiding constraints (Yang-Baxter equations). Anomaly-free topological field theories. Modular data (S, T) → CFT partition functions. Quantum dimensions (non-integer). Truncated representation rings preserving fusion.

**Computable:** PARTIAL — Fusion rules and S-matrix computable for small rank. Modular closure checks NP-hard.

### CAGE DIAGNOSIS
**Layer affected:** Layer 2 (GrammarLayer)
**Within-format:** YES — Fusion categories reorganize representation theory into categorical framework. Core objects remain the same (simple objects, multiplicities). Braiding adds constraint structure but doesn't expand the set of representable objects. Modular data is derived from existing structure.

### TRANSPLANT SKETCH
BraidingConstraint on GrammarLayer: composition rules must satisfy Yang-Baxter. Quantum dimension as MAP-Elites descriptor. Modular data (S-matrix) as fitness landscape structure detector. Primarily organizational — constrains composition rather than expanding it.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## H.7 — Langlands Program & Functoriality (Langlands, Frenkel)

### SOURCE
Langlands (1967), "Letter to Weil" (original conjectures).
Frenkel (2005), "Lectures on the Langlands Program and Conformal Field Theory."
Gaitsgory & Lurie (2019), *Weil's Conjecture for Function Fields*.

### FORMAL STRUCTURE EXTRACTION

**Old format (Separate worlds):** Galois representations: Gal(Ā̄/Ā) → GL_n(ℂ). Automorphic forms: representations of GL_n(A_Q). No canonical correspondence between these two formalisms. Each computed independently in different algebro-geometric contexts.

**New format (Langlands correspondence):** L-group ^LG parametrizes both worlds. Automorphic representation π → L-parameter φ: Gal(K̄/K) → ^LG(ℂ). Functoriality: morphism G → H induces transfer π_G → π_H. Geometric Langlands: D-modules on Bun_G ↔ perverse sheaves on LocSys_{Ğ}.

**Transition op:** DUALITY_BRIDGE: Galois representations ↔ automorphic forms via L-parameter. FUNCTORIALITY: L-group morphism → automorphic transfer.

**Became expressible:** Unified framework connecting number theory and harmonic analysis. Finite Galois groups ↔ discrete automorphic series (L-packets). Functoriality equations as predictive tool. Geometric version: D-module pushforward ↔ L-parameter restriction.

**Computable:** PARTIAL — Verified for GL(n) and many small cases. General functoriality largely open. Computational approaches via automorphic test vectors exist but limited.

### CAGE DIAGNOSIS
**Layer affected:** Layer 3 (MetaGrammarLayer)
**Within-format:** YES — Langlands correspondence is a deep duality/isomorphism between two mathematical formalisms. Despite its profundity, it maps objects in one representation system to objects in another — preserving F_theo (both systems express the same mathematical truths). This is the deepest duality yet analyzed, but dualities are COMBINATORIAL_RECOMBINATION by the pattern established across B, E, F.

### TRANSPLANT SKETCH
L-parameter as cross-format bridge: define correspondence between ExprNode representations and alternative program representations (stack-based, graph-based). If both represent the same F_theo, the bridge enables translation but not expansion. Value: enables multi-representation search (evolve in one format, evaluate in another). Connects to B.7 (M-theory unification) and B.4-B.6 (dualities).

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## H.8 — Operads & Higher Algebra (May, Loday, Lurie)

### SOURCE
May (1972), *The Geometry of Iterated Loop Spaces*.
Loday & Vallette (2012), *Algebraic Operads*.
Lurie (2017), *Higher Algebra* (∞-operads formalism).

### FORMAL STRUCTURE EXTRACTION

**Old format (Specific algebras):** Algebraic structures defined by explicit relations: (a·b)·c = a·(b·c), [a,b] = −[b,a], etc. Each algebra type (associative, Lie, commutative) has its own axiom set. No unified meta-language for "what is an algebraic structure?"

**New format (Operadic):** Operad O = {O(n): symmetric sequence} with composition γ: O(m) ⊗ O(n₁) ⊗ ... ⊗ O(n_m) → O(Σn_i) and identity e ∈ O(1). Algebras over O: objects with O-actions satisfying operadic coherence. Examples: Assoc, Lie, Com, E_∞. Koszul duality: O ↔ O^! (dual operad). ∞-operads: Lurie's higher categorical enrichment.

**Transition op:** META-GRAMMAR: specific algebra relations → operad with colored operations. KOSZUL_DUALITY: operad O ↔ dual operad O^!. HIGHER_LIFT: operad O → ∞-operad via simplicial nerve.

**Became expressible:** Algebra structures as points in operadic space. Deformations: homotopy associativity (A_∞) as relaxed Assoc. Koszul duality creates shadow theories (Lie ↔ Coassociative). Functoriality: operad morphism → forgetful functor between algebra categories. Meta-composition: operads themselves compose (plethysm).

**Computable:** YES — Operad presentation, Gröbner bases for operads, ∞-operad homology computable. Koszul duality decidable for quadratic operads.

### CAGE DIAGNOSIS
**Layer affected:** Layer 3 (MetaGrammarLayer) + FORMAT_CHANGE
**Within-format:** NO — Operads are a grammar for grammars. They parametrize composition rules as first-class mathematical objects. The MetaGrammarLayer currently generates rules randomly; operads provide the formal framework for structured rule generation. Koszul duality reveals hidden complementary structures. ∞-operads extend to homotopy-coherent compositions.

### TRANSPLANT SKETCH
OperadicMetaGrammar: replace ad-hoc MetaGrammarLayer rule generation with operad-structured generation. Each GrammarLayer rule set IS an algebra over some operad. MetaGrammarLayer operations become operad morphisms. Koszul duality: for each rule system, automatically generate its dual. A_∞ relaxation: allow approximately-associative composition (homotopy coherence). MAP-Elites descriptors: operadic complexity (number of generators), coherence degree (A_∞ vs E_∞), Koszul dual complexity.

### VERDICT: STRUCTURAL_EXPANSION

---

## Cross-Domain Patterns (Domain H)

### Pattern 1: Duality Confirmation at Maximum Depth
H.1 (RSK correspondence) and H.7 (Langlands) are both dualities — the deepest dualities in mathematics. Yet by the CAGE criterion, neither expands F_theo. H.7 is particularly important: even the Langlands correspondence, which unifies number theory and harmonic analysis, is COMBINATORIAL_RECOMBINATION because it maps between equivalent representation systems. This is the strongest confirmation yet of the pattern from B.4-B.6.

### Pattern 2: Root Systems as Organizing Principle
H.2 (Gabriel's theorem) shows that root systems classify representation types. This connects to the lattice-structured vocabulary pattern from E.6 (JI microtonality) — both use algebraic lattice geometry to organize discrete objects.

### Pattern 3: Dimensional Reduction as Expansion
H.3 (crystal bases) achieves expansion by REDUCING dimension (q→0 limit). This is the inverse of the discrete→continuous FORMAT_CHANGE (B, E, F). Combined with G.1 (expansion via restriction/Curry-Howard), this establishes that dimensional reduction and logical restriction can both be expansion mechanisms — paradoxical but confirmed across multiple domains.

### Pattern 4: Geometry Reveals Hidden Structure
H.4 (geometric representation theory) uses geometric methods to extract structure invisible to algebra. This matches G.6 (topos-internal logic) — geometric/sheaf-theoretic methods as a universal expansion mechanism. Now 5+ independent sources identify geometry as a cage-breaking tool.

### Pattern 5: Meta-Grammar Formalization
H.8 (operads) provides the most rigorous formalization of the MetaGrammarLayer concept. Operads ARE the mathematical theory of composition rules. This directly addresses the RSI system's need for principled rule generation. Connects to A.3 (adaptive grammars) and A.4 (VW two-level grammars).

### Pattern 6: Categorification = Systematic Format Lifting
H.5 (categorification) makes the discrete→richer-structure pattern explicit: integers become vector spaces, polynomials become chain complexes. This is a systematic, functorial version of the FORMAT_CHANGE mechanism. Every decategorification loses information; every categorification gains a dimension.

---

## Summary Statistics

| Sub-topic | Verdict | Layers | Format Change |
|-----------|---------|--------|---------------|
| H.1 Young Tableaux | COMBINATORIAL_RECOMBINATION | L2 | No |
| H.2 Quiver Representations | STRUCTURAL_EXPANSION | L2 | Partial |
| H.3 Crystal Bases | STRUCTURAL_EXPANSION | L1+L2+FORMAT | Yes |
| H.4 Geometric Rep Theory | STRUCTURAL_EXPANSION | L2+L3+FORMAT | Yes |
| H.5 Categorification | STRUCTURAL_EXPANSION | L1+L2+FORMAT | Yes |
| H.6 Fusion Categories | COMBINATORIAL_RECOMBINATION | L2 | No |
| H.7 Langlands Program | COMBINATORIAL_RECOMBINATION | L3 | No |
| H.8 Operads | STRUCTURAL_EXPANSION | L3+FORMAT | Yes |

**Totals:** 8 sub-topics, 8 extractions. STRUCTURAL_EXPANSION: 5. COMBINATORIAL_RECOMBINATION: 3. NO_STRUCTURE_FOUND: 0.

**Strongest candidates:**
1. **Operads as meta-grammar formalization** (H.8) — grammar for grammars; directly addresses MetaGrammarLayer; Koszul duality generates dual rule systems
2. **Categorification** (H.5) — systematic FORMAT_CHANGE lifting; integers→vector spaces; functorial information gain
3. **Crystal bases** (H.3) — expansion via dimensional reduction (q→0); paradoxical expansion via restriction (matches G.1)
4. **Geometric representation theory** (H.4) — geometric methods reveal algebraically invisible structure; sheaf-theoretic unification
5. **Quiver root classification** (H.2) — Dynkin diagrams organize representation types; lattice-structured classification
