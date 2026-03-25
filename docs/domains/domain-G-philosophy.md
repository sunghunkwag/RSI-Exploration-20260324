# Domain G — Philosophy of Mathematics & Formal Epistemology

**Session 7 | Date: 2026-03-25 | Status: COMPLETE**

---

## G.1 — Intuitionism & Constructive Mathematics (Brouwer, Martin-Löf)

### SOURCE
Brouwer (1908), "The Unreliability of the Logical Principles."
Martin-Löf (1984), *Intuitionistic Type Theory*, Bibliopolis.
Howard (1980), "The Formulae-as-Types Notion of Construction."
Troelstra & Van Dalen (1988), *Constructivism in Mathematics*, North-Holland.

### FORMAL STRUCTURE EXTRACTION

**Old format (Classical logic):** Excluded middle (LEM) assumed. Proof = abstract truth-justification. Existence proofs via contradiction (no constructive witness). Non-constructive: "∃x.P(x)" proven without providing x.

**New format (Constructive type theory):** No LEM. BHK interpretation: proof of ∃x.P(x) must provide explicit witness a + proof P(a). Curry-Howard isomorphism: propositions are types, proofs are programs. Martin-Löf Type Theory: dependent types, proof terms are executable.

**Transition op:** For each classical proof schema, identify algorithmic content. Transform negation-based existence proofs into explicit witness computation. Type-check in MLTT. Compile proof to executable term.

**Became expressible:** Program synthesis from proofs (a proof of ∃x.P(x) IS a program computing x). Computational content recovery from classical proofs. Dependent types for program verification. Every constructive proof computes in finite time.

**Computable:** YES — Type checking MLTT decidable. Proof terms are executable programs.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 2 + FORMAT_CHANGE
**Within-format:** NO — Classical proofs are abstract truth-justifications; constructive proofs are syntactic programs. Curry-Howard creates proof-to-program synthesis functor absent from classical logic. New dimension: algorithmic content.

### TRANSPLANT SKETCH
ProofWitness primitive type: every expression satisfying a property carries its verification. Constructive grammar rules: mutations must preserve proof witnesses. Reject compositions requiring non-constructive justification. Connects to D.5 (dependent types).

### VERDICT: STRUCTURAL_EXPANSION

---

## G.2 — Lakatos's Proofs and Refutations (Dialectical Method)

### SOURCE
Lakatos (1976), *Proofs and Refutations: The Logic of Mathematical Discovery*, Cambridge.
Koetsier (1991), "Lakatos' Philosophy of Mathematics: A Historical Approach."

### FORMAL STRUCTURE EXTRACTION

**Old format (Classical proof verification):** Proof as fixed artifact — valid or invalid (binary). Counterexample invalidates theorem entirely.

**New format (Dialectical evolution):** Proof as evolving sequence: conjecture C₀ → proof P₀ → counterexample → revised C₁, P₁ → ... Counterexample taxonomy: global (falsifies conjecture), local (violates lemma), monster (edge case, tightens proof). Successive approximation to robust truth.

**Transition op:** Initial conjecture → proof sketch → counterexample search → classify counterexample type → revise conjecture/proof accordingly → iterate until robust.

**Became expressible:** Conjecture refinement via falsification. Proof robustification via lemma accumulation. Minimal conditions for truth discovered dynamically.

**Computable:** NO in general (detecting all counterexamples undecidable). YES in restricted finite search spaces.

### CAGE DIAGNOSIS
**Layer affected:** Layer 3 (MetaGrammarLayer)
**Within-format:** YES — Dialectical proof is a sequence of classical proofs + counterexamples. Same formal objects, better search process. Analogous to co-evolution (F.7).

### TRANSPLANT SKETCH
Counterexample-driven refinement: when expression fails test case, classify failure type (global vs local), refine accordingly. Track expression lineages. Stopping criterion: no new counterexamples in N generations.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## G.3 — Structuralism in Philosophy of Mathematics (Resnik, Shapiro)

### SOURCE
Resnik (1997), *Mathematics as a Science of Patterns*, Oxford.
Shapiro (1997), *Philosophy of Mathematics: Structure and Ontology*, Oxford.
Hellman (1989), *Mathematics Without Numbers*, Oxford.

### FORMAL STRUCTURE EXTRACTION

**Old format (Platonism / intrinsic objects):** Mathematical objects exist independently with intrinsic properties. ℕ₁ and ℕ₂ (different constructions of naturals) are different objects even if isomorphic.

**New format (Structuralism):** Mathematical objects are positions in abstract structures. Identity = role in structure, not intrinsic properties. Isomorphic realizations treated as the same structure. Theorems about structure transfer automatically via isomorphism.

**Transition op:** Given isomorphic objects A ≅ B, quotient: [A] ~ [B]. Extract canonical form. All theorems proven about A transfer to B via isomorphism φ.

**Became expressible:** Representation independence. Structural invariance. Canonical form reduction (deduplicate isomorphic representations).

**Computable:** YES for finite structures (graph isomorphism, decidable but hard). PARTIAL for infinite structures.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 2
**Within-format:** YES — Quotient construction achievable in classical set theory. Same theorems expressible, more efficiently organized. Essentially A.5 (Univalence) at philosophical level.

### TRANSPLANT SKETCH
Structural equivalence on ExprNode trees: deduplicate by behavioral equivalence (same output for all inputs). Quotient archive by equivalence classes. Transfer proofs across isomorphs. Reduces archive redundancy.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## G.4 — Reverse Mathematics (Simpson, Friedman)

### SOURCE
Simpson (1999), *Subsystems of Second-Order Arithmetic*, Springer.
Friedman (1975), "Some Systems of Second Order Arithmetic and their Use."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Multiple foundational systems (ZFC, PA, constructive logic). No principled way to determine weakest axiom system sufficient for a given theorem.

**New format:** Fix base system RCA₀. For each theorem T, determine minimum additional axioms A such that RCA₀ + A ⊢ T. "Big Five" hierarchy: RCA₀ ⊂ WKL₀ ⊂ ACA₀ ⊂ ATR₀ ⊂ Π¹₁-CA₀. ~90% of ordinary mathematics falls into one of these five levels.

**Transition op:** Encode theorem T in second-order arithmetic. Attempt derivation from RCA₀. If fails, find minimal A with RCA₀ + A ⊢ T. Verify reverse direction: T ⊢ A over RCA₀.

**Became expressible:** Minimal axiom identification. Calibrated foundationalism. Computational complexity stratification of provability.

**Computable:** Semi-decidable (search for derivations). No algorithm for determining which Big Five level a theorem belongs to.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 (vocabulary classification)
**Within-format:** YES — Classification within fixed format (second-order arithmetic). No new logic or proof system introduced.

### TRANSPLANT SKETCH
Vocabulary stratification: assign each primitive an axiom level. Partition archive by axiom level. Optimize: find expressions achieving target coverage with minimum axiom level. Value is organizational, not expressive.

### VERDICT: NO_STRUCTURE_FOUND

---

## G.5 — Forcing and Independence (Cohen)

### SOURCE
Cohen (1963), "The Independence of the Continuum Hypothesis."
Kunen (1980), *Set Theory*.
Jech (2003), *Set Theory*.

### FORMAL STRUCTURE EXTRACTION

**Old format:** MetaGrammarLayer rewrites rules with no guarantee that rewritten system preserves invariants. Syntactic modification only.

**New format:** Extend vocabulary V with generic object G via constrained poset P. M[G] ⊨ ZF iff G respects forcing conditions. Rule rewrite + invariant certification.

**Transition op:** GenericExtension(P, M): given poset P of forcing conditions, generate filter G ⊆ P such that closure of M ∪ {G} preserves designated invariants.

**Became expressible:** Primitives added only if they satisfy forcing conditions (compatibility with existing system). Safe vocabulary extension with invariant preservation.

**Computable:** YES for finite posets (enumerate conditions, check filter). Undecidable in full higher-order logic.

### CAGE DIAGNOSIS
**Layer affected:** Layer 3 (MetaGrammarLayer)
**Within-format:** YES — Forcing is a consistency-preserving rewrite strategy, not a new capability. It disciplines extension, doesn't expand it.

### TRANSPLANT SKETCH
Before LibraryLearner commits new primitive P, construct poset of compatibility conditions ("P does not unify with reserved symbols," "P does not induce infinite regress"). Check if generic filter exists. Only commit if yes. Effect: safer primitive induction.

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## G.6 — Topos Theory as Alternative Foundations (Lawvere, Tierney)

### SOURCE
Lawvere & Tierney (1970), *Elementary Theory of the Category of Sets*.
Mac Lane & Moerdijk (1992), *Sheaves in Geometry and Logic*.
Goldblatt (1984), *Topoi: The Categorical Analysis of Logic*.

### FORMAL STRUCTURE EXTRACTION

**Old format (Boolean evaluation):** Each ExprNode expression evaluates to true or false. Primitive judgments are bivalent. Evaluation is context-free (same result regardless of where/when evaluated).

**New format (Topos-internal logic):** Replace {T, F} with subobject classifier Ω of a topos τ. Elements of Ω are open sets in a Heyting algebra. Truth is multi-valued and context-dependent. Expressions whose truth is partial or local (defined in region U but not V).

**Transition op:** Revalue(τ, e): interpret expression e in internal logic of topos τ. Each subexpression evaluates to element of Ω(τ). Composition respects sheaf conditions (locality + gluing).

**Became expressible:** Context-dependent truth (primitive valid in domain U but undefined in V). Locality and coverage as first-class. Non-Boolean evaluation where intermediate truth values carry geometric meaning.

**Computable:** Undecidable in general (Ω can be uncountable). Semi-decidable for finite posets or effective topoi.

### CAGE DIAGNOSIS
**Layer affected:** Layer 1 + Layer 2 + FORMAT_CHANGE
**Within-format:** NO — Replacing Boolean with Heyting-algebra-valued truth changes the semantic domain. This is the same structural pattern as C.3/C.4 (context-dependent evaluation) but with stronger mathematical foundations.

### TRANSPLANT SKETCH
Primitives carry spatial/contextual metadata ("valid in domain U"). Composition: P₁ (valid in U) composed with P₂ (valid in V) → result valid in U ∩ V. Implement via domain annotations + intersection checks. Connects directly to C.3/C.4 context-dependent evaluation transplant.

### VERDICT: STRUCTURAL_EXPANSION

---

## G.7 — Computability & Incompleteness Applied (Gödel, Turing, Chaitin)

### SOURCE
Gödel (1931), "Über formal unentscheidbare Sätze."
Turing (1936), "On Computable Numbers."
Chaitin (1974-2000), *Algorithmic Information Theory*.

### FORMAL STRUCTURE EXTRACTION

**Old format (Implicit completeness assumption):** Assume all expressible properties of ExprNode trees are decidable (type-check, termination, reachability).

**New format (Incompleteness ceiling):** Gödel I: any consistent system encoding arithmetic is incomplete. Turing: halting undecidable. Chaitin: Omega (halting probability) is algorithmically random, uncomputable. These are absolute ceilings, not implementation limitations.

**Transition op:** Recognize(S): given RSI system S, identify undecidable properties. Map to Omega(S) (fraction of randomly-generated programs that halt). Use as complexity index.

**Became expressible:** Nothing new. Awareness of what cannot be decided within S, even with unlimited resources. Undecidable predicates expressible as oracle queries but not computable.

**Computable:** By definition, the boundary properties are NOT computable. Approximations exist but never converge.

### CAGE DIAGNOSIS
**Layer affected:** Meta-level (system boundaries)
**Within-format:** N/A — These are foundational theorems about what no system can do, not rules within RSI.

### TRANSPLANT SKETCH
Identify candidate properties (termination, type safety). For each, assess decidability. For undecidable properties, provide semi-decision procedures (bounded model-check). Document Omega_RSI as complexity index. Value: epistemic — avoid false claims of decidability. RSI's "immune system," not its substrate.

### VERDICT: NO_STRUCTURE_FOUND

---

## Cross-Domain Patterns (Domain G)

### Pattern 1: Constructive Restriction Adds Computational Content
G.1 (intuitionism): dropping LEM RESTRICTS provable theorems but ADDS algorithmic content via Curry-Howard. Paradoxical expansion via restriction. New pattern not seen in A-F.

### Pattern 2: Dialectical Refinement = Better Search, Not Expansion
G.2 (Lakatos) confirms F.7 (co-evolution), E.5 (L-systems): process improvements to search methodology do not expand F_theo.

### Pattern 3: Structural Quotient = Archive Efficiency
G.3 (structuralism) = A.5 (univalence): quotienting by structural equivalence reduces redundancy. COMBINATORIAL_RECOMBINATION.

### Pattern 4: Topos-Internal Logic = Context-Dependent Evaluation
G.6 (topos theory) provides mathematical foundations for C.3/C.4 (context-dependent evaluation). Heyting-algebra-valued truth = formally grounded version of polymorphic PrimitiveOps with domain annotations. Now 4 independent domains identify context-dependent evaluation (C.3, C.4, C.1c, G.6).

### Pattern 5: Incompleteness Defines Boundaries, Not Mechanisms
G.7 (Gödel/Turing/Chaitin) and G.4 (reverse mathematics) are epistemic tools — they characterize what's possible/impossible, but provide no transplantable structure.

---

## Summary Statistics

| Sub-topic | Verdict | Layers | Format Change |
|-----------|---------|--------|---------------|
| G.1 Intuitionism | STRUCTURAL_EXPANSION | L1+L2+FORMAT | Yes |
| G.2 Lakatos | COMBINATORIAL_RECOMBINATION | L3 | No |
| G.3 Structuralism | COMBINATORIAL_RECOMBINATION | L1+L2 | No |
| G.4 Reverse Math | NO_STRUCTURE_FOUND | L1 | No |
| G.5 Forcing | COMBINATORIAL_RECOMBINATION | L3 | No |
| G.6 Topos Theory | STRUCTURAL_EXPANSION | L1+L2+FORMAT | Yes |
| G.7 Incompleteness | NO_STRUCTURE_FOUND | Meta | N/A |

**Totals:** 7 sub-topics, 7 extractions. STRUCTURAL_EXPANSION: 2. COMBINATORIAL_RECOMBINATION: 3. NO_STRUCTURE_FOUND: 2.

**Strongest candidates:**
1. **Constructive proofs-as-programs** (G.1) — Curry-Howard adds program synthesis dimension; paradoxical expansion via restriction
2. **Topos-internal context-dependent evaluation** (G.6) — mathematical foundation for C.3/C.4 pattern; Heyting algebra truth values
