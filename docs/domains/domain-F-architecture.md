# Domain F — Architecture, Engineering & Design

**Session 6 | Date: 2026-03-25 | Status: COMPLETE**

---

## F.1 — Shape Grammars

### SOURCE
Stiny & Gips (1972), "Shape Grammars and the Generative Specification of Painting and Sculpture."
Stiny (1980), *Pictorial and Formal Aspects of Shape and Shape Grammars*.
Knight (2003), "Computing with Emergence," *Environment and Planning B*.

### FORMAL STRUCTURE EXTRACTION

**Old format:** String/tree rewriting grammars. Symbolic tokens rewritten via pattern matching. Concatenation-based composition.

**New format:** Shape grammars. Geometric shapes rewritten via spatial embedding — detecting subshapes within composite shapes even when not explicitly encoded. Rules operate on algebraic point sets with spatial transformations (translation, rotation, scaling).

**Transition op:** Given shape S and rule L → R, search for ALL embeddings of L in S (subshape detection). Replace geometrically with R. Embedding is NP-hard for parametric transformations.

**Became expressible:** Spatial designs with continuous parameter variation. Self-similar recursive structures via iterated embedding. Ambiguity in shape interpretation (multiple valid embeddings). Non-string compositional semantics.

**Computable:** YES — Turing-complete (Stiny). Embedding NP-hard in general; practical systems restrict to simple shapes.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 (VocabularyLayer)
**Within-format:** YES — Both string grammars and shape grammars are Turing-complete. Embedding is a new algorithm for pattern-matching, not a new set of computable functions. The ambiguity is epistemic (multiple interpretations), not expressive (new functions).

### TRANSPLANT SKETCH
Structural embedding: map geometric embedding to tree substructure matching with commutativity tolerance. Pattern (+ a b) matches (+ b a) if + is commutative. Useful for F_eff (symmetry-aware mutation), not F_theo expansion.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## F.2 — Parametric Design & Constraint Propagation

### SOURCE
Woodbury (2010), *Elements of Parametric Design*.
Oxman (2017), "Thinking Difference: Theories and Models of Parametric Design Thinking," *Design Studies*.
Shea et al. (2005), "Towards Integrated Performance-Driven Generative Design Tools," *Automation in Construction*.

### FORMAL STRUCTURE EXTRACTION

**Old format:** DAG top-down evaluation. Parameters flow unidirectionally to geometry. Acyclic dataflow graph with topological sort evaluation.

**New format:** Bidirectional constraint propagation. Convert DAG operators to constraint predicates. Constraint hypergraph allows cycles. Simultaneous equation solving replaces sequential evaluation. Soft constraints with weights for multi-objective optimization.

**Transition op:** Convert operators to constraint predicates with slack variables. Build constraint hypergraph. Solve bidirectionally: forward (parameters → geometry), backward (geometry → parameters), simultaneous (iterate until convergence).

**Became expressible:** Interactive design feedback (dragging geometry auto-updates parameters). Automatic satisfaction of performance criteria. Overdetermined systems. Multi-objective optimization with weighted preferences. Design space exploration via solver navigation.

**Computable:** YES — Satisfiability NP-complete in general; linear systems polynomial; nonlinear systems numerically solvable.

### CAGE DIAGNOSIS
**Layer affected:** Layer 2 (GrammarLayer) + Layer 1
**Within-format:** YES — Both express same constraints. Evaluation semantics change (unidirectional → bidirectional) but the set of expressible functions is identical (both Turing-complete).

### TRANSPLANT SKETCH
Constraint-guided mutation: extend mutation rules with soft constraints (behavioral descriptor targets). Bias selection toward mutations maximizing novelty, maintaining expressiveness, minimizing depth. Useful for F_eff (better navigation), not F_theo.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## F.3 — Tensegrity & Structural Morphology

### SOURCE
Fuller (1975), *Synergetics: Explorations in the Geometry of Thinking*.
Skelton & de Oliveira (2009), *Tensegrity Systems*, Springer.
Motro (2003), *Tensegrity: Structural Systems for the Future*.

### FORMAL STRUCTURE EXTRACTION

**Old format (Forward analysis):** Given geometry G → compute stiffness matrix K(G) → solve Ku = F for displacements → extract member forces. Direction: geometry → forces.

**New format (Form-finding / inverse analysis):** Define force-density matrix Q → solve for node positions N satisfying equilibrium L·N = 0 → extract geometry G(Q). Direction: forces → geometry. Self-stressed systems require no external load.

**Transition op:** Invert the analysis direction. Force density method: q_ij · distance_ij = f_ij. Equilibrium at each node: Σ_j (q_ij / distance_ij) · (pos_j - pos_i) = 0 for self-stressed systems.

**Became expressible:** Self-supporting structures with pure internal equilibrium. Topology-independent design (same forces → infinite geometries). Continuous deformability within force constraints. Tension/compression duality (mathematically interchangeable).

**Computable:** YES — Linear force density method O(n³). Nonlinear: quadratic convergence via Newton's method. Stability analysis O(n²).

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 3
**Within-format:** YES — Forward analysis ↔ inverse analysis. Both express the same set of structural configurations. Form-finding reframes the problem for tractability but does not expand the set of discoverable structures.

### TRANSPLANT SKETCH
Self-stress as structural integrity: expression is "self-stressed" if every subexpression has a role in overall computation and removing any node breaks structure. Layer 2 mutation rule: "Only accept mutations preserving self-stress." Useful as design heuristic, not expressibility expansion.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## F.4 — Christopher Alexander's Pattern Language

### SOURCE
Alexander, Ishikawa & Silverstein (1977), *A Pattern Language: Towns, Buildings, Construction*.
Alexander (1979), *The Timeless Way of Building*.
Salingaros (2000), "The Structure of Pattern Languages," *Architectural Research Quarterly*.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Flat list of design heuristics with descriptions. Loose hierarchy or none. ~50 rules before becoming unwieldy.

**New format:** Directed graph of 253 patterns with forces. Each pattern: Problem + Solution + Invariants + References. Hierarchical composition with cross-references. Recursive compositional decomposition.

**Transition op:** Identify forces (conflicts between desired properties) → define patterns as stable resolutions → establish hierarchical composition → encode invariant structures → assess quality via pattern coherence ("quality without a name").

**Became expressible:** Hierarchical design spaces with scale-awareness. Explicit capture of design trade-offs. Recursive problem decomposition. Inter-pattern constraints.

**Computable:** UNCERTAIN — Pattern satisfaction NP-complete if formalized as CSP. "Quality without a name" (QWAN) is fundamentally qualitative. Alexander deliberately avoids formal specification.

### CAGE DIAGNOSIS
**Layer affected:** Layer 2 + Layer 3
**Within-format:** N/A — Alexander's pattern language is a design philosophy, not a formal system. It deliberately resists formalization. No formal transition operation can be defined without losing the core insight.

### TRANSPLANT SKETCH
Indirect value only: organize Layer 2 operators as pattern network instead of flat list. Each rule includes problem statement, solution, forces, cross-references. But this is methodological guidance, not formal expansion.

### VERDICT: NO_STRUCTURE_FOUND

---

## F.5 — Topology Optimization (SIMP/ESO)

### SOURCE
Bendsøe & Sigmund (2003), *Topology Optimization: Theory, Methods, and Applications*.
Xie & Steven (1997), "Evolutionary Structural Optimization," *Journal of Structural Engineering*.
Allaire et al. (2004), "Structural Optimization with FreeFEM++," *Structural and Multidisciplinary Optimization*.

### FORMAL STRUCTURE EXTRACTION

**Old format (Discrete member placement):** Design space is binary vector d ∈ {0,1}^n where d_i = 1 means member i present. Finite catalog of 2^n configurations. Combinatorial optimization (NP-hard).

**New format (Continuous density field):** Density field ρ: Ω → [0,1] on domain Ω ⊂ ℝ². SIMP constitutive law: E(x) = E₀ · ρ(x)^p. Gradient-based optimization via adjoint method. Minimize compliance C(ρ) subject to volume constraint.

**Transition op:** Mesh domain into finite elements → assign continuous density ρ_e ∈ [0,1] per element → compute stiffness K_e(ρ_e) = ρ_e^p K_e^0 → assemble global stiffness → solve Ku = F → compute sensitivities ∂C/∂ρ_e via adjoint → gradient descent → filter for manufacturability → iterate.

**Became expressible:** Smooth thickness variation (not binary on/off). Multi-scale optimization (foam-like, lattice-like, organic geometries). Sensitivity-driven search via gradient ∇C/∂ρ. Convexity properties guaranteeing global optimum convergence. Space expands from finite 2^n to uncountable [0,1]^Ω.

**Computable:** YES — FEM solve O(n^1.5), adjoint sensitivity O(1) additional solve, 50-200 iterations typical.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 2 + FORMAT_CHANGE
**Within-format:** NO — ExprNode trees with discrete PrimitiveOp composition cannot represent continuous density fields. Same recurring discrete→continuous FORMAT_CHANGE as E.3 (spectral music) and B.1/B.8 (physics). F_theo(discrete) ⊂ F_theo(continuous) strictly.

### TRANSPLANT SKETCH
New FieldPrimitiveOp type: eval_field(ρ: np.ndarray) → scalar functional. FieldGradientDescent mutation: ρ_new = ρ - α·∇C/∂ρ. MAP-Elites descriptors: compliance, material ratio, feature scale, symmetry. Connects directly to E.3 transplant (SpectralOp).

### VERDICT: STRUCTURAL_EXPANSION

---

## F.6 — Origami Mathematics & Computational Folding

### SOURCE
Lang (2011), *Origami Design Secrets: Mathematical Methods for an Ancient Art*.
Demaine & O'Rourke (2007), *Geometric Folding Algorithms: Linkages, Origami, Polyhedra*.
Hull (2006), *Project Origami: Activities for Exploring Mathematics*.
Huzita & Scimemi (1989), "The Algebra of Paper-Folding."

### FORMAL STRUCTURE EXTRACTION

**Old format (Compass-straightedge):** 4 operations: line through 2 points, circle with center and radius, intersection, copy distance. Constructible reals: quadratic field tower Q(√·). Solvable equation degrees: up to 2. Cannot solve cubics (angle trisection, cube doubling impossible).

**New format (Huzita-Hatori origami axioms):** 7 fold axioms. Axioms A5, A6 involve parabola and cubic locus intersections. Constructible reals: cubic field extensions Q(∛·). Solvable equation degrees: up to 3.

**Transition op:** Recognize that fold axioms A5 and A6 generate parabola and cubic loci. For A6: locus of points simultaneously at fixed distance ratios from P₁, P₂ and on line ℓ₁ forms cubic curve; intersection with ℓ₂ yields up to 3 solutions. Apply fold sequence; record crease pattern.

**Became expressible:** Cubic solutions (degree 3 algebraic). Angle trisection (impossible in Euclidean geometry, possible via A5/A6). Cube doubling (x³ = 2). Crease pattern as constructive proof/program. Field extension from quadratic tower to cubic tower.

**Computable:** YES — Each axiom O(1) geometric operations. Crease pattern O(n³) for n folds. Flat-foldability decidable in O(n log n).

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 2 + FORMAT_CHANGE
**Within-format:** NO — Compass-straightedge operations preserve Q(√·) (quadratic tower). Origami adds Q(∛·) (cubic tower). Galois-theoretically proven: origami group properly contains compass-straightedge group. New geometric primitives (parabola/cubic locus) fundamentally unavailable via compass-straightedge.

### TRANSPLANT SKETCH
New FoldAxiom PrimitiveOps (A1-A7). A5_FoldBiaxial: parabola with focus P, directrix ℓ₂, intersect with ℓ₁. A6_FoldBilinear: cubic locus intersection. Layer 2 composition rules: FoldSequence (insert, delete, reorder fold axioms with flatness constraint). MAP-Elites descriptors: points generated, crease complexity, algebraic degree, flat-foldability.

### VERDICT: STRUCTURAL_EXPANSION

---

## F.7 — Generative Adversarial Design / Evolutionary Co-Design

### SOURCE
Paredis (1994), "Coevolutionary Algorithms," PhD Thesis, University of Michigan.
De Jong (2006), "Coevolutionary Algorithms," in *Handbook of Evolutionary Computation*.
Goodfellow et al. (2014), "Generative Adversarial Nets," *NeurIPS*.
Lipson & Pollack (2000), "Automatic Design and Manufacture of Robotic Lifeforms," *Nature*.

### FORMAL STRUCTURE EXTRACTION

**Old format (Single-population EA):** Population of candidate designs d = {d₁, ..., d_μ}. Static fitness function f: d → ℝ. Fixed fitness landscape. Selection + variation.

**New format (Co-evolutionary / Adversarial):** Two populations: hosts (designs) and parasites (test cases). Fitness is relative: f_H(d) = avg resistance to current parasites; f_P(p) = avg exploitation of current hosts. Non-stationary fitness landscape (arms race dynamics).

**Transition op:** Initialize host and parasite populations → evaluate relative fitness → select and vary both populations → iterate arms race dynamics.

**Became expressible:** Non-stationary fitness prevents premature convergence. Arms race generates pressure to discover novel regions. Search efficiency improved 2-10× empirically. However: the set of expressible designs remains identical — all designs are still ExprNode trees.

**Computable:** YES — O(|H| × |P|) evaluations per generation. No convergence guarantee (can cycle indefinitely).

### CAGE DIAGNOSIS
**Layer affected:** Layer 2 + MAP-Elites archive
**Within-format:** YES — Designs remain ExprNode trees. Mutation/crossover unchanged. Only fitness evaluation becomes non-stationary. F_theo unchanged; F_eff improved.

### TRANSPLANT SKETCH
Adaptive fitness via parasite population: co-evolve test cases alongside designs. Non-stationary fitness signal: re-evaluate archive against current parasite population. Useful for MAP-Elites diversity maintenance. But: COMBINATORIAL_RECOMBINATION — same designs, better search.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## Cross-Domain Patterns (Domain F)

### Pattern 1: Problem Inversion is Recombination, Not Expansion
F.1 (spatial vs. symbolic), F.2 (forward vs. backward), F.3 (analysis vs. form-finding) — all involve inverting the problem direction. None expand F_theo. Confirms Domain B pattern: dualities/inversions are COMBINATORIAL_RECOMBINATION.

### Pattern 2: Continuous Primitives are a Recurring FORMAT_CHANGE
F.5 (topology optimization: discrete member → continuous density field) = same structural expansion as E.3 (spectral music), B.1/B.8 (physics). Now 4 independent domains identify this mechanism.

### Pattern 3: Algebraic Tower Extension is Genuine Expansion
F.6 (origami: quadratic → cubic field) expands constructible objects via higher-degree algebraic solutions. New pattern not previously seen — domain-specific but formally rigorous (Galois-theoretic proof).

### Pattern 4: Design Philosophy ≠ Formal System
F.4 (Alexander's pattern language) resists formalization by design. Valuable for methodology but NO_STRUCTURE_FOUND for F_theo analysis.

### Pattern 5: Co-evolution Improves Search, Not Expressibility
F.7 confirms E.5 (L-systems) and B.4-B.6 pattern: better search dynamics ≠ expanded expressibility. Important caution for literature claims.

---

## Summary Statistics

| Sub-topic | Verdict | Layers | Format Change |
|-----------|---------|--------|---------------|
| F.1 Shape Grammars | COMBINATORIAL_RECOMBINATION | L1 | No |
| F.2 Parametric Design | COMBINATORIAL_RECOMBINATION | L1+L2 | No |
| F.3 Tensegrity | COMBINATORIAL_RECOMBINATION | L1+L3 | No |
| F.4 Pattern Language | NO_STRUCTURE_FOUND | L2+L3 | N/A |
| F.5 Topology Optimization | STRUCTURAL_EXPANSION | L1+L2+FORMAT | Yes |
| F.6 Origami Mathematics | STRUCTURAL_EXPANSION | L1+L2+FORMAT | Yes |
| F.7 Co-evolutionary Design | COMBINATORIAL_RECOMBINATION | L2 | No |

**Totals:** 7 sub-topics, 7 extractions. STRUCTURAL_EXPANSION: 2. COMBINATORIAL_RECOMBINATION: 4. NO_STRUCTURE_FOUND: 1.

**Strongest candidates:**
1. **Topology optimization / continuous fields** (F.5) — recurring discrete→continuous FORMAT_CHANGE (=E.3=B.1/B.8)
2. **Origami algebraic tower** (F.6) — new pattern: higher-degree algebraic constructibility via fold axioms
