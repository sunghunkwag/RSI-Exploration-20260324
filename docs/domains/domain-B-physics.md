# Domain B — Physics, Cosmology & Fundamental Theory

**Session 2 | Date: 2026-03-25 | Status: COMPLETE**

---

## B.1 — Spontaneous Symmetry Breaking: Higgs Mechanism

### SOURCE
Peskin & Schroeder, "An Introduction to Quantum Field Theory," Ch. 20.
Weinberg, "The Quantum Theory of Fields," Vol. 2.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Lagrangian L_sym with gauge symmetry group G = SU(2)_L × U(1)_Y. Four massless gauge bosons (W¹, W², W³, B). Scalar field φ in symmetric vacuum ⟨φ⟩ = 0. All fields in irreducible representations of G. Mass terms for gauge bosons forbidden by gauge invariance.

**New format:** Effective Lagrangian L_eff after vacuum selection. Scalar acquires VEV: φ₀ = (0, v/√2)ᵀ. Residual symmetry H = U(1)_EM ⊂ G. Physical field h(x) = φ(x) - φ₀. Three Goldstone bosons eaten by gauge bosons → W±, Z acquire mass. Photon γ remains massless. Mass terms explicitly present: M_W = gv/2, M_Z = gv/(2cos θ_W).

**Transition op:** (1) Minimize potential V(φ) = λ(|φ|² - v²/2)² → vacuum φ₀ = v/√2, (2) Expand φ(x) = φ₀ + h(x) around minimum, (3) Substitute into L, collect terms by power of h, (4) Compute mass matrix M²_ab from Hessian ∂²V/∂φ_i∂φ_j|φ₀, (5) Diagonalize to find mass eigenstates via rotation R(θ_W). Output: {M_W, M_Z, M_γ=0, mass eigenstates, residual U(1)_EM}.

**Became expressible:** Massive gauge bosons (W±, Z) — these CANNOT exist in the symmetric representation because explicit mass terms violate gauge invariance. The Higgs mechanism generates them through vacuum interaction, not by hand. Longitudinal polarization states (3rd polarization) for W±, Z. Coupling hierarchy proportional to v.

**Computable:** YES — symbolic computation (FeynCalc, MadGraph). Steps: minimize polynomial, compute Hessian, diagonalize matrix, extract eigenvalues. All algebraic.

### CAGE DIAGNOSIS

**Layer affected:** FORMAT_CHANGE (Layer 3)
**Within-format:** NO — Symmetric and broken representations are structurally distinct. New mass eigenstates are linear combinations of original fields — they do not exist in the symmetric basis. Between-format change.

### TRANSPLANT SKETCH

The Higgs mechanism maps to a "vacuum selection" operation on ExprNode trees: given a space of possible tree configurations (analogous to field space), select a "vacuum" configuration v (the best-performing tree structure), then expand all future trees as perturbations around v. The "mass" of a perturbation direction = its fitness cost. Directions with zero cost (massless) remain free exploration axes; directions with high cost (massive) constrain exploration. This maps to adaptive grammar: GrammarLayer.set_vacuum(best_tree) fixes structural template, then mutations are perturbations around it.

### VERDICT: STRUCTURAL_EXPANSION

---

## B.2 — Phase Transitions: Landau Theory

### SOURCE
Landau & Lifshitz, "Statistical Physics," Vol. 5.
Arovas, "Thermodynamics and Statistical Mechanics," Ch. 7 (LibreTexts).

### FORMAL STRUCTURE EXTRACTION

**Old format:** Free energy F(η, T>T_c) = F₀ + a(T)η² + b(T)η⁴ where a(T) = α(T - T_c) > 0. Single stable minimum at η* = 0 (symmetric/disordered phase). Order parameter η identically zero in equilibrium.

**New format:** Free energy F(η, T<T_c) with a(T) < 0. Landscape bifurcates: unstable saddle at η = 0, two stable minima at η* = ±√(-a/2b) = ±√(α(T_c - T)/2b). Broken Z₂ symmetry. Order parameter acquires spontaneous nonzero value.

**Transition op:** Control parameter T crosses threshold T_c → coefficient a(T_c) = 0 → pitchfork bifurcation. Procedure: (1) Compute dF/dη = 2a(T)η + 4b(T)η³ = 0, (2) Solve: η* = 0 or η* = ±√(-a/2b), (3) Evaluate d²F/dη² at each root to classify stability, (4) For T < T_c: η = 0 is unstable (d²F/dη² < 0), η = ±η₀ are stable. (5) New observable: spontaneous magnetization, bistability, susceptibility divergence χ → ∞ at T_c.

**Became expressible:** Spontaneous ordering, bistability, hysteresis, domain formation, critical exponents (β = 1/2 in mean-field). These are INEXPRESSIBLE in the T > T_c representation because the free energy landscape has only one minimum there.

**Computable:** YES — polynomial root finding, Hessian evaluation. Standard numerical/algebraic procedure.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar) — topology of solution space changes
**Within-format:** YES — same free energy functional, same order parameter space. The representation FORMAT (polynomial in η) is unchanged; what changes is the CONTENT (which solutions are stable). This is within-format bifurcation.

### TRANSPLANT SKETCH

Landau theory maps to fitness landscape analysis in MAP-Elites: as a control parameter (e.g., generation count, mutation rate) crosses a threshold, the fitness landscape bifurcates — new stable optima appear that were not present before. The "order parameter" is archive coverage or structural diversity. Phase transition = transition from exploration-dominated to exploitation-dominated regime. Practical: detect landscape bifurcation by monitoring second derivative of fitness vs. control parameter. When it crosses zero, trigger design-space expansion.

### VERDICT: COMBINATORIAL_RECOMBINATION

Rationale: Landau theory describes bifurcation within a FIXED representation format. The free energy functional form is unchanged. New stable states emerge, but the representational grammar is the same. This is a within-format phenomenon — valuable for detecting WHEN to expand, but not itself a format change.

---

## B.3 — Wilson Renormalization Group

### SOURCE
Wilson & Kogut (1974), "The renormalization group and the ε expansion," Physics Reports 12(2), 75-200.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Bare Lagrangian L(Λ) with UV cutoff Λ, containing operators {O_i} with couplings {g_i(Λ)}. Theory formulated at single scale. All modes up to cutoff included.

**New format:** Effective Lagrangian L_eff(Λ') at lower scale Λ' = Λ/b (b > 1), containing SAME operators with renormalized couplings {g_i(Λ')} PLUS potentially NEW operators {O_j^(new)} with couplings {c_j(Λ')} generated by integration. Operator basis has EXPANDED.

**Transition op:** (1) Separate fields into high-energy (Λ/b < k < Λ) and low-energy (k < Λ/b) modes: φ = φ_h + φ_l. (2) Functional integral over φ_h: Z_eff = ∫Dφ_l exp(-S_eff[φ_l]) where S_eff = -log(∫Dφ_h exp(-S[φ_h + φ_l])). (3) Rescale momenta k → k·b and fields φ → φ·b^(d-2+η)/2. (4) Read off new couplings and new operators from S_eff. (5) Iterate. Flow equation: dg_i/d(ln b) = β_i({g}).

**Became expressible:** New effective operators at lower energy scales. These encode collective phenomena, bound states, and emergent properties ABSENT from the UV Lagrangian. Example: four-fermion operators generated from gauge boson exchange. The β-function itself — the rate of coupling evolution — is a new expressible quantity that describes how the theory changes with scale.

**Computable:** PARTIALLY — perturbative RG (loop expansion) is computable order-by-order. Lattice RG and tensor network RG provide numerical approximations. Exact functional RG requires solving infinite-dimensional flow equations (not generally tractable). ε-expansion (Wilson-Kogut innovation) gives explicit perturbative formulas near d=4.

### CAGE DIAGNOSIS

**Layer affected:** Layer 1 (Vocabulary) + Layer 2 (Grammar)
**Within-format:** NO — new operators genuinely appear that were NOT in the original Lagrangian. The operator basis (vocabulary) expands. Between-format: UV and IR representations have different operator content.

### TRANSPLANT SKETCH

Wilson RG maps directly to library learning in the RSI system: (1) "High-energy modes" = fine-grained tree structure details, (2) "Integrate out" = extract common subtrees as primitives (exactly what LibraryLearner does), (3) "New operators" = extracted library primitives, (4) "Effective Lagrangian" = reduced vocabulary + library primitives that encode complex sub-computations. The β-function analog is the rate at which library extraction generates new primitives as a function of generation number. The current LibraryLearner IS a Wilson RG step on expression trees. To make it more rigorous: define a formal "cutoff" (tree depth), integrate out sub-trees deeper than cutoff, extract effective primitives.

### VERDICT: STRUCTURAL_EXPANSION

---

## B.4 — T-duality

### SOURCE
Polchinski, "String Theory," Vol. 1, Ch. 8.
Tong, "String Theory" Cambridge lectures, Ch. 8.

### FORMAL STRUCTURE EXTRACTION

**Old format:** String theory compactified on circle of radius R. Spectrum: M² = (n/R)² + (wR/α')² + oscillators, where n = momentum quantum number, w = winding number. At large R: momentum modes light (n/R small), winding modes heavy (wR/α' large). Perturbation theory organized around momentum modes.

**New format:** Dual theory with R̃ = α'/R. Same spectrum: M² = (w/R̃)² + (nR̃/α')² + oscillators. Quantum numbers exchanged: n ↔ w. At small R (= large R̃): winding modes light, momentum modes heavy. Perturbation theory organized around winding modes.

**Transition op:** R → α'/R, (n, w) → (w, n). On worldsheet: Fourier transform of compact coordinate zero-mode sector. Formally an O(1,1;ℤ) transformation on the (momentum, winding) lattice. The mass spectrum, partition function, and all scattering amplitudes are INVARIANT under this map.

**Became expressible:** Nothing genuinely new. The SAME physics is re-expressed with different "simple" degrees of freedom. Winding-dominated phenomena (intractable at large R) become perturbatively accessible at small R, and vice versa. F_theo is IDENTICAL in both descriptions.

**Computable:** YES — fully algorithmic. Worldsheet Fourier transform on zero-mode sector (finite-dimensional Gaussian integral). Quantum number relabeling is a discrete bijection on ℤ².

### CAGE DIAGNOSIS

**Layer affected:** None (isomorphism)
**Within-format:** YES — both representations describe the same theory with the same expressible content. Bijection on solution space. No cage-breaking.

### TRANSPLANT SKETCH

T-duality as ExprNode analog: define two representations of the same computation — one organized by "frequency" (how often a sub-pattern appears), another by "locality" (how deep in the tree it lives). Duality: frequent-but-deep ↔ rare-but-shallow after library extraction. This is a reparameterization of the search space, not an expansion. Potentially useful for search efficiency but does not change F_theo.

### VERDICT: COMBINATORIAL_RECOMBINATION

Rationale: T-duality is a proven isomorphism. F_theo(A) = F_theo(B). No new expressibility. Within-format reparameterization.

---

## B.5 — S-duality

### SOURCE
Montonen & Olive (1977). Sen (1994), "Strong-weak coupling duality in four-dimensional string theory."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Type IIB string theory at weak coupling g_s ≪ 1. Perturbative states (F-strings, gravitons) light, M ∝ g_s⁰. Non-perturbative states (D-branes, monopoles) heavy, M ∝ 1/g_s. Perturbation theory converges. Feynman diagrams with fundamental strings dominate.

**New format:** Same theory at strong coupling, described via dual with coupling 1/g_s ≪ 1. D-branes now light, F-strings heavy. Perturbation theory in 1/g_s converges. Feynman diagrams organized around D-brane degrees of freedom.

**Transition op:** SL(2,ℤ) modular transformation on axio-dilaton τ = C₀ + ie^{-φ}. S-transformation: τ → -1/τ, equivalently g_s → 1/g_s. F-string ↔ D1-brane. BPS mass formula M_BPS = √(p² + q²)·(2π/α') is invariant under (p,q) → (q,-p).

**Became expressible:** Strong-coupling observables become COMPUTABLE via weak-coupling perturbation theory in the dual. For BPS-protected quantities, exact computation is possible. However, F_theo is unchanged — same theory, same spectrum, same physics. The gain is computational accessibility, not representational expansion.

**Computable:** PARTIALLY — BPS sector: exactly computable. Non-BPS sector: requires D-brane perturbation theory, which is systematically harder. Not a simple algorithmic inversion like T-duality.

### CAGE DIAGNOSIS

**Layer affected:** None (same F_theo)
**Within-format:** YES — same Type IIB theory. Computational regime inverts but representational content is identical. No cage-breaking.

### TRANSPLANT SKETCH

S-duality analog for ExprNode: if evolutionary search at "weak coupling" (low mutation rate) cannot find solutions requiring large structural changes, switch to "strong coupling" (high mutation rate, aggressive restructuring) where those solutions become accessible. The duality asserts that the same solution space is searchable from both regimes. Practical: adaptive mutation rate scheduling as a "coupling inversion." Does not change F_theo but may improve F_eff.

### VERDICT: COMBINATORIAL_RECOMBINATION

Rationale: S-duality is a computational bridge, not a structural expansion. F_theo(weak) = F_theo(strong). Same physics, different computational accessibility. Valuable for search strategy but not cage-breaking.

---

## B.6 — AdS/CFT Correspondence

### SOURCE
Maldacena (1997), "The large N limit of superconformal field theories and supergravity."
Gubser, Klebanov, Polyakov (1998); Witten (1998) — GKPW relation.

### FORMAL STRUCTURE EXTRACTION

**Old format:** d-dimensional conformal field theory (CFT) on boundary. Operators O_i with scaling dimensions Δ_i. Correlation functions computed via CFT path integral. No geometric/gravitational content. Strongly coupled (large 't Hooft coupling λ) → perturbation theory fails.

**New format:** (d+1)-dimensional gravity on Anti-de Sitter space (AdS_{d+1}). Bulk fields φ with masses m² = Δ(Δ-d). Classical Einstein equations + matter. Boundary conditions encode CFT sources. Same physics encoded geometrically in higher-dimensional space.

**Transition op:** GKPW relation: ⟨exp(∫ φ₀ O)⟩_CFT = Z_gravity[φ|_boundary = φ₀]. Procedure: (1) Specify CFT source φ₀ on boundary, (2) Solve bulk Einstein + matter equations with boundary condition φ → φ₀, (3) Evaluate on-shell gravitational action S[φ_bulk], (4) log Z_CFT = -S[φ_bulk]/ℏ. Dictionary: CFT dimension Δ ↔ bulk mass m, CFT temperature ↔ black hole horizon, CFT entanglement entropy ↔ bulk minimal surface area (Ryu-Takayanagi).

**Became expressible:** Entanglement entropy as geometric area (Ryu-Takayanagi). Black hole thermodynamics as CFT thermal state. Non-perturbative strongly-coupled CFT observables via classical gravity computation. These are computable in NEITHER representation alone — the duality provides computational access that both descriptions individually lack.

**Computable:** PARTIALLY — classical gravity (large N limit) reduces to PDEs, numerically solvable. Exact analytic solutions for symmetric cases. Quantum gravity corrections (1/N) require loop computations in bulk.

### CAGE DIAGNOSIS

**Layer affected:** FORMAT_CHANGE
**Within-format:** NO — two fundamentally different geometric settings (boundary QFT vs. bulk gravity) encode the same Hilbert space. Neither is a rewriting of the other within a single formalism. True between-format duality.

### TRANSPLANT SKETCH

AdS/CFT as ExprNode analog: define a "boundary" representation (flat tree structure, operator composition) and a "bulk" representation (hierarchical tree with depth = extra dimension). The "holographic dictionary" maps: tree depth ↔ energy scale (RG flow), tree width at depth d ↔ number of effective operators at scale d. Ryu-Takayanagi analog: entanglement between two sub-trees measured by the minimal cut separating them (min-cut = min-surface). This reframes tree structural analysis as a geometric problem. Practical but does not change F_theo — it's a different VIEW of the same tree, not a new tree format.

### VERDICT: COMBINATORIAL_RECOMBINATION

Rationale: AdS/CFT is a proven duality (Hilbert space isomorphism). F_theo(CFT) = F_theo(gravity). Same expressible content in both representations. The duality provides computational access (strong coupling ↔ classical gravity) but does not expand what is expressible. Within our CAGE framework: no cage-breaking, only cage-viewing-from-different-angle.

---

## B.7 — M-theory Unification

### SOURCE
Witten (1995), "String theory dynamics in various dimensions."
Hořava & Witten (1996), heterotic M-theory.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Five separate 10-dimensional string theories (Type IIA, IIB, Heterotic SO(32), Heterotic E₈×E₈, Type I). Each with distinct spectrum, coupling, moduli space. No known relation between them.

**New format:** Single 11-dimensional M-theory. Each string theory is a compactification limit: Type IIA = M-theory on S¹ (R₁₁ → 0), Heterotic E₈×E₈ = M-theory on S¹/Z₂ (Hořava-Witten). Unified moduli space. U-duality = S-duality + T-duality unified. Fundamental objects: M2-branes, M5-branes.

**Transition op:** Dimensional reduction/compactification. For Type IIA: (1) Start with 11D supergravity action, (2) Compactify 11th dimension on S¹ of radius R₁₁, (3) Kaluza-Klein reduce: ∫d¹¹x → ∫d¹⁰x ∫dy, (4) Identify g_s = (R₁₁/l_Planck)^{3/2}, (5) Read off 10D Type IIA spectrum and couplings. For Heterotic: same but with S¹/Z₂ orbifold and E₈ gauge fields on boundary branes.

**Became expressible:** Strong-coupling dynamics of each string theory — previously inaccessible — becomes computable via 11D supergravity (which becomes classical at large R₁₁). Unified duality structure (U-duality). Non-perturbative brane spectrum. Moduli space transitions between string theories.

**Computable:** PARTIALLY — dimensional reduction is formulaic (systematic KK reduction). U-duality transformations are linear algebra on moduli for toroidal compactifications. Full 11D dynamics not solvable in general.

### CAGE DIAGNOSIS

**Layer affected:** FORMAT_CHANGE (unification)
**Within-format:** NO — embeds five separate formats into one higher-dimensional framework. Between-format: 10D → 11D lift is a genuine format change.

### TRANSPLANT SKETCH

M-theory unification as ExprNode analog: if multiple seemingly different tree grammars (e.g., prefix notation, postfix notation, S-expressions, graph-based) all turn out to be "compactification limits" of a single higher-dimensional representation, then the search should operate in the unified representation and project down to specific formats as needed. Practical: define a "meta-tree" format that subsumes ExprNode trees, stack-based programs (PushGP), and graph-based programs — then evolve in the meta-format. This IS the architectural question posed in standing rule #12: "is ExprNode tree itself the cage wall?" M-theory's answer: yes, each specific format is a limit of a more general structure.

### VERDICT: STRUCTURAL_EXPANSION

Rationale: M-theory genuinely reveals structure invisible in any single string theory — unified duality group, 11D brane spectrum, strong-coupling access. While each individual duality (T, S) is an isomorphism, the UNIFICATION into a single framework creates new computational access and reveals structural relationships. The format change (10D → 11D) is genuine.

---

## B.8 — Gauge Symmetry Breaking (Electroweak)

### SOURCE
Weinberg, "The Quantum Theory of Fields," Vol. 2.
DAMTP Cambridge Standard Model lectures.

### FORMAL STRUCTURE EXTRACTION

**Old format:** SU(2)_L × U(1)_Y gauge theory. 4 massless gauge bosons: W¹, W², W³, B. Covariant derivative D_μ = ∂_μ + i(g/2)W^a_μ σ^a + i(g'/2)B_μ Y. Couplings g (SU(2)), g' (U(1)). All bosons in adjoint representation. No mass hierarchy.

**New format:** U(1)_EM residual symmetry. Physical bosons: W± = (W¹ ∓ iW²)/√2 (massive, M_W = gv/2), Z⁰ = cos θ_W W³ - sin θ_W B (massive, M_Z = gv/(2cos θ_W)), γ = sin θ_W W³ + cos θ_W B (massless). Weinberg angle: tan θ_W = g'/g. Coset: SU(2)×U(1)/U(1)_EM ≅ S² parameterizes 3 broken generators.

**Transition op:** (1) Higgs doublet acquires VEV: ⟨φ⟩ = (0, v/√2)ᵀ, (2) Identify unbroken generator: Q = T³ + Y (electric charge), (3) Rotate (W³, B) → (Z, γ) by angle θ_W = arctan(g'/g), (4) Compute mass matrix M² in gauge boson space, (5) Diagonalize: 3 massive + 1 massless eigenstate. Goldstone counting: dim(G/H) = (3+1)-1 = 3 broken generators → 3 eaten Goldstones → 3 massive gauge bosons.

**Became expressible:** Z⁰ boson (mixture of W³ and B — undefined without vacuum selection). W± as charge eigenstates. Neutral weak current (Z-mediated). The mixing angle θ_W is ONLY defined after symmetry breaking — it parameterizes which combination remains massless.

**Computable:** YES — matrix diagonalization, eigenvalue computation, all algebraic.

### CAGE DIAGNOSIS

**Layer affected:** FORMAT_CHANGE (Layer 3)
**Within-format:** NO — mass eigenstates are linear combinations that don't exist in the symmetric basis. Between-format.

### TRANSPLANT SKETCH

Electroweak breaking as ExprNode analog: the system has multiple "symmetry groups" of tree transformations (e.g., commutativity of add, associativity). "Breaking" one symmetry (e.g., fixing evaluation order) creates new distinguished operators (like Z being a specific mixture of W³ and B). The "mixing angle" determines which combination of abstract operators becomes the "physical" one used in evaluation. Practical: introduce an explicit "symmetry breaking" step in MetaGrammarLayer that selects specific operator compositions from a symmetric space of possibilities, creating new named primitives.

### VERDICT: STRUCTURAL_EXPANSION

---

## B.9 — Stellar Nucleosynthesis: Vocabulary Expansion Through Energy Thresholds

### SOURCE
Burbidge, Burbidge, Fowler & Hoyle (B²FH, 1957), "Synthesis of the Elements in Stars," Reviews of Modern Physics 29(4), 547-650.

### FORMAL STRUCTURE EXTRACTION

**Old format:** At temperature T_n, vocabulary V_n = {elements up to Z_max(T_n)}. Reaction rules R_n = {A + B → C + γ : kT_n ≥ E_Coulomb(A,B)}. Below Coulomb barrier threshold, fusion reactions are forbidden. Observable: element abundances up to Z_max.

**New format:** At higher temperature T_{n+1}, vocabulary V_{n+1} = V_n ∪ {new elements}. New reaction pathways R_{n+1} = R_n ∪ {newly accessible reactions}. Thresholds: T₁ ≈ 4×10⁶ K (pp-chain: H→He), T₂ ≈ 10⁸ K (triple-alpha: He→C), T₃ ≈ 6×10⁸ K (C-burning: C→Ne,Mg), T₄ ≈ 10⁹ K (O-burning), T₅ ≈ 1.5×10¹⁰ K (Si-burning: →Fe-peak).

**Transition op:** Threshold activation function ξ_ij(T) = 1 if kT ≥ E_Coulomb(i,j), else 0. Procedure: (1) Increase T past threshold, (2) Activate new reactions: ξ_ij flips 0→1, (3) Compute new reaction rates Γ_ij(T) = σ_ij(E) × ξ_ij(T) × ρ, (4) Integrate rate equations dY_A/dt = Σ(production) - Σ(consumption), (5) Read off new vocabulary V_{n+1} = {A : Y_A > ε}.

**Became expressible:** Heavier elements (C, O, Ne, Mg, Si, Fe...) — literally nonexistent below their formation threshold. New reaction pathways (triple-alpha, CNO cycle, r-process, s-process). The periodic table as a progressive vocabulary expansion.

**Computable:** YES — stellar nuclear reaction networks are solved numerically. Systems of coupled ODEs for 300+ species. Implemented in XNet, NuGrid, Kepler stellar evolution codes.

### CAGE DIAGNOSIS

**Layer affected:** Layer 1 (Vocabulary) + Layer 2 (Grammar/reaction rules)
**Within-format:** YES (with nuance) — the underlying nuclear physics (strong force, Coulomb interaction) is unchanged. The FORMAT (nuclear reaction grammar) is the same at all temperatures. What changes is which reactions are KINETICALLY ACCESSIBLE. The vocabulary expansion is real but occurs within a fixed representational framework. The "hidden" elements were always possible in principle; temperature just enables their formation.

### TRANSPLANT SKETCH

Direct transplant to RSI system: define "energy thresholds" for meta-grammar operations. Currently, `expand_design_space()` fires probabilistically. Instead: define a "computational temperature" T_comp (function of archive coverage, fitness plateau duration, generation count). At each T_comp threshold, unlock new expansion operations: T₁ → vocabulary composition (current _meta_compose_new_op), T₂ → library learning (current LibraryLearner), T₃ → grammar rule parameterization, T₄ → adaptive grammar activation, T₅ → format change operations. Lower thresholds = simpler expansions; higher thresholds = more disruptive changes. This creates a staged expansion protocol analogous to stellar burning stages.

### VERDICT: COMBINATORIAL_RECOMBINATION

Rationale: Nucleosynthesis occurs within a FIXED physical framework (nuclear forces unchanged). The vocabulary expansion is real but does not change the underlying representational format. Elements were always "expressible" in principle (the nuclear force grammar permits them) — the threshold merely enables kinetic access. This is within-format, threshold-gated combinatorial expansion. Valuable for designing staged expansion protocols but not cage-breaking.

---

## Session Summary

| Sub-topic | Formal Extractions | Verdict |
|-----------|-------------------|--------|
| B.1 Higgs Mechanism | Complete | STRUCTURAL_EXPANSION |
| B.2 Landau Phase Transitions | Complete | COMBINATORIAL_RECOMBINATION |
| B.3 Wilson Renormalization Group | Complete | STRUCTURAL_EXPANSION |
| B.4 T-duality | Complete | COMBINATORIAL_RECOMBINATION |
| B.5 S-duality | Complete | COMBINATORIAL_RECOMBINATION |
| B.6 AdS/CFT Correspondence | Complete | COMBINATORIAL_RECOMBINATION |
| B.7 M-theory Unification | Complete | STRUCTURAL_EXPANSION |
| B.8 Electroweak Symmetry Breaking | Complete | STRUCTURAL_EXPANSION |
| B.9 Stellar Nucleosynthesis | Complete | COMBINATORIAL_RECOMBINATION |

**Sub-topics investigated:** 9
**Full formal extractions completed:** 9
**STRUCTURAL_EXPANSION verdicts:** 4 (B.1 Higgs, B.3 Wilson RG, B.7 M-theory, B.8 Electroweak)
**COMBINATORIAL_RECOMBINATION verdicts:** 5 (B.2 Landau, B.4 T-duality, B.5 S-duality, B.6 AdS/CFT, B.9 Nucleosynthesis)
**NO_STRUCTURE_FOUND:** 0
**Remaining incomplete:** 0

### Critical observation

The physics domain reveals a clear pattern: **dualities are isomorphisms, not expansions.** T-duality, S-duality, and AdS/CFT all preserve F_theo — they provide computational access to different regimes but do not expand what is expressible. The genuine expansions come from **symmetry breaking** (Higgs, electroweak) and **coarse-graining** (Wilson RG), which generate new representational content (mass eigenstates, effective operators) absent from the original formulation. M-theory is intermediate: a unification that reveals structure invisible in any single component theory.

The strongest transplant insight from Domain B: **Wilson RG IS library learning.** The RSI system's LibraryLearner already implements the core RG operation (integrate out fine structure → extract effective primitives). The formal connection is not metaphorical — it is structural.
