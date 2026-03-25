# Domain A — Mathematics & Formal Foundations

**Session 1 | Date: 2026-03-25 | Status: COMPLETE**

---

## A.1 — Type Theory: Universe Polymorphism & Induction-Recursion

### SOURCE
Dybjer & Setzer (1999), "A Finite Axiomatization of Inductive-Recursive Definitions," TLCA. Springer LNCS 1581.
Sozeau & Tabareau, "Universe Polymorphism in Coq."
Palmgren, "On Universes in Type Theory," Uppsala University.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Fixed stratified universe hierarchy U₀ : U₁ : U₂ : ... with monomorphic definitions. Each definition must be written separately at each universe level. No abstraction mechanism over universe levels. Universes are external, atomic type formers.

**New format:** Parametric universe polymorphism (level variables ℓ with successor/supremum operations, unification-based constraint solver) combined with inductive-recursive definitions: simultaneous declaration of a TYPE (set of codes U) and a RECURSIVE FUNCTION (interpretation El : U → Type). Universes become internally definable via Tarski-style (U, El) pairs.

**Transition op:** The Dybjer-Setzer axiomatization performs a *schema-to-type-former lift*: (1) Parse the pattern of simultaneous induction-recursion in user declaration, (2) Extract the positivity class (half-positive conditions on B), (3) Generate formation/introduction/elimination rules parametrized by universe level ℓ, (4) Type-check against positivity constraints (decidable in linear time), (5) Solve universe constraints via unification over level expressions. The result is a single polymorphic IR definition that instantiates at multiple universe levels.

**Became expressible:** Internal universe hierarchies (universes as data, not postulates), generic polymorphic definitions across universe levels, large inductive types (universes themselves as data), Mahlo universe analogues. Previously: each universe level required separate axioms; now a single IR definition covers all levels. Universe self-extension becomes expressible.

**Computable:** YES — Positivity checking is O(n) on constructor syntax. Universe level unification is first-order decidable. Rule generation is template instantiation. Type checking IR-definitions is decidable and implemented in Agda/Coq.

### CAGE DIAGNOSIS

**Layer affected:** Layer 3 (Meta-Grammar) + FORMAT_CHANGE
**Within-format:** NO — Moves from external universe hierarchy (separate syntactic objects) to internal inductive-recursive universe (single U with decoding El). Old system cannot express IR universes. Candidate for cage-breaking.

### TRANSPLANT SKETCH

Each IR-definition becomes a compound ExprNode with type `InductiveRecursive(codes: ExprNode, decode: ExprNode→ExprNode)`. Positivity checking maps to a tree traversal labeling positions as +/- polarity. Universe polymorphism maps to level-parameterized templates in MetaGrammarLayer. The key transplantable insight: a vocabulary layer that can define new primitives *simultaneously with their interpretation function* — currently, `_meta_compose_new_op` creates primitives without simultaneous type/interpretation constraints.

### VERDICT: STRUCTURAL_EXPANSION

---

## A.2 — Category Theory: Kan Extensions

### SOURCE
Mac Lane, "Categories for the Working Mathematician," Ch. X.
Lehner, "All Concepts are Kan Extensions," Harvard senior thesis.
nLab, "Kan extension."

### FORMAL STRUCTURE EXTRACTION

**Old format:** A functor F: C → D defined only on subcategory C ⊆ C'. No values on objects or morphisms outside C. Domain-restricted.

**New format:** Extended functor Lan_i(F): C' → D where inclusion i: C → C' lifts F to larger domain C'. Total on C', preserves F on restriction (Lan_i(F) ∘ i ≅ F).

**Transition op:** Pointwise left Kan extension formula:

```
(Lan_i F)(c') = colim_{(c, f: i(c) → c')} F(c)
```

Colimit taken over comma category (i ↓ c'). Equivalently via coend: `(Lan_i F)(c') = ∫^c Hom(i(c), c') · F(c)`. For each target c' ∈ C': (1) enumerate all pairs (c ∈ C, f: i(c) → c'), (2) pull back F(c) values, (3) compute colimit of that diagram in D.

**Became expressible:** Values at objects in C' \ C (outside original domain). Colimits and limits as special cases. Adjoint functors (right Kan extension of identity along F gives left adjoint). Universal properties depending on relationships between i(C) and new objects.

**Computable:** YES, conditionally — if D admits relevant colimits, the construction is algorithmic. For finite categories, fully computable. For infinite categories, requires termination conditions on comma category enumeration.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar) — extends domain of composition
**Within-format:** NO — Transforms partial (domain-restricted) to total (universally extended). Between-format change.

### TRANSPLANT SKETCH

A partial evaluation function eval: SimpleExpr → Value (defined only on leaves/simple expressions) could be Kan-extended to eval': AllExpr → Value by computing each compound expression's value as a colimit over its sub-expression decompositions. This is analogous to what `_eval_tree` already does recursively, but the Kan extension framework provides a *universal* guarantee: the extension is optimal among all possible extensions. Practical transplant: define a "comma category" of all ways to decompose a complex expression into known sub-expressions, then compute the colimit. This would formalize the current ad-hoc recursive evaluation.

### VERDICT: STRUCTURAL_EXPANSION

---

## A.3 — Formal Language Theory: Adaptive Grammars (Shutt 2001)

### SOURCE
Shutt (2001), "What is an Adaptive Grammar?" WPI Technical Report.
Shutt, "Recursive Adaptive Grammars," Semantic Scholar.
Christiansen, "Adaptable Grammars."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Context-free grammar with fixed production rules N → α. Rule set determined at definition time, immutable during parsing.

**New format:** Grammar with explicit rule set manipulation. Base grammar + rule manipulation predicates (add_rule, remove_rule) + synthesized/inherited attributes that compute which rules are active at parse time. The rule set itself becomes a first-class semantic value.

**Transition op:** Synthesized attribute evaluation with rule set propagation: (1) Bottom-up attribute propagation during parse tree construction, (2) Attributes computed in one subtree determine which rules are available for parsing sibling/subsequent subtrees, (3) Grammar dynamically instantiates or removes rules based on attribute values. Formal: at each parse tree position p, the active rule set R(p) is a function of the synthesized attributes of previously parsed subtrees.

**Became expressible:** Context-sensitive and Turing-recognizable languages. Context-sensitive agreement constraints, identifier scope rules, parametric constructs that vary based on semantic values — all expressed *within* the grammar, not via external semantic passes. Well-behaved recursive adaptive grammars (RAGs) are Turing-powerful.

**Computable:** YES (well-behaved subset) — restricted to strongly stepwise decidable and strongly answer-encapsulated grammars. Unrestricted RAGs can express undecidable languages.

### CAGE DIAGNOSIS

**Layer affected:** Layer 3 (Meta-Grammar)
**Within-format:** NO — The rule set becomes a dynamic semantic object, not a static specification. Between-format for imperative adaptive grammars. Candidate for cage-breaking.

### TRANSPLANT SKETCH

Direct mapping to GrammarLayer/MetaGrammarLayer: (1) GrammarLayer maintains base production rules, (2) MetaGrammarLayer computes synthesized attributes from elite archive population, (3) Active rule set R(generation) varies per generation based on attributes. The current `expand_design_space()` method already does a crude version of this (probabilistically adding rules). A formal adaptive grammar transplant would make rule activation *conditional on population attributes* (e.g., coverage, fitness plateau detection) rather than random. Specific implementation: `GrammarLayer.active_rules(attributes: Dict) → List[Rule]` where attributes are computed from archive state.

### VERDICT: STRUCTURAL_EXPANSION

---

## A.4 — Formal Language Theory: Van Wijngaarden Two-Level Grammars

### SOURCE
Van Wijngaarden, "Revised Report on the Algorithmic Language ALGOL 68."
Augenstein, "The van Wijngaarden Grammars: A Syntax Primer with Decidable Restrictions."
Sintzoff, "Existence of a van Wijngaarden syntax for every recursively enumerable set."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Context-free grammar requiring infinite explicit enumeration of rules to express parametric/context-sensitive constraints (e.g., separate rules for every type combination).

**New format:** Two-level grammar: (Level 1) metarules — context-free productions defining possible values for metanotions (abstract parameters); (Level 2) hyperrules — production templates with metanotions as placeholders. Finite specification generates infinite object-level grammar via consistent substitution.

**Transition op:** Consistent (uniform) substitution procedure: (1) Parse metagrammar (finite CFG) to determine all values for each metanotion, (2) For each hyperrule, enumerate all possible metanotion assignments, (3) Replace each metanotion occurrence consistently with the same value throughout a hyperrule, (4) Output: infinite set of concrete context-free production rules. Formally: `instantiate(hyperrule, binding: metanotion → value) → concrete_rule`. Applied over all consistent bindings.

**Became expressible:** Non-context-free constraints within a finite specification. ALGOL 68's type consistency, parametric language features, syntactic orthogonality. A single hyperrule with MODE metanotion covers all type-specific variants. Unrestricted W-grammars generate all recursively enumerable languages.

**Computable:** YES (restricted variants) — Membership problem is undecidable for unrestricted W-grammars (Type 0 equivalent). Restricted variants (Bracketed Two-Level Grammars, Extended Affix Grammars) are parseable in polynomial time. ALGOL 68 uses decidable restricted variants. Algorithm: lazy substitution (on-demand instantiation, not exhaustive enumeration).

### CAGE DIAGNOSIS

**Layer affected:** Layer 3 (Meta-Grammar) → generates Layer 2 (Grammar)
**Within-format:** NO — Explicit format transition from two-level specification to object-level CFG. Between-format change.

### TRANSPLANT SKETCH

MetaGrammarLayer already has metanotions (implicitly: the types of operations, arity constraints). Making this explicit: define `MetaRule(metanotion: str, values: List[str])` and `HyperRule(template: str, metanotions: List[str])`. The `expand_design_space()` method would instantiate hyperrules via consistent substitution over metanotion values, generating concrete grammar rules. This would replace the current random rule generation with systematic parametric expansion. Example metanotion: `ARITY → {0, 1, 2}`, hyperrule: `compose_ARITY(args) → tree_node(op, args[:ARITY])`.

### VERDICT: STRUCTURAL_EXPANSION

---

## A.5 — Homotopy Type Theory: Univalence Axiom

### SOURCE
HoTT Book, Ch. 2.10 (Voevodsky et al., "Homotopy Type Theory: Univalent Foundations of Mathematics").
Voevodsky, "The Univalence Axiom in Homotopy Type Theory," AMS Notices 2013.
1Lab, "Univalence."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Martin-Löf type theory without univalence. Identity A =_U B defined only via reflexivity constructor and path induction (J-eliminator). Equivalences A ≃ B exist as separate mathematical objects. No formal mechanism to identify equivalent structures as identical types. Theorems proven about one representation cannot automatically transfer to an isomorphic one.

**New format:** HoTT with univalence. The canonical map `idtoequiv : (A =_U B) → (A ≃ B)` is promoted to a full equivalence. Inverse map `ua : (A ≃ B) → (A =_U B)` converts equivalences to identities. Computation rule: `transport(ua(f), x) = f(x)`.

**Transition op:** The `ua` map: given equivalence (f, inv, sec, ret) representing a type isomorphism, produce a path (identity proof) between types. This is asserted axiomatically, not computed. In cubical type theory (Cohen et al. 2015), a computational interpretation exists via explicit path types (1-dimensional cubes) with Cartesian cubical semantics.

**Became expressible:** (1) Structure Identity Principle: isomorphic structures are identical — theorems lift automatically across representations. (2) Function extensionality (derived). (3) Transport of properties along equivalences. (4) Quotient type construction. (5) Representation independence: theorems for one data structure encoding automatically hold for any isomorphic encoding.

**Computable:** NO as axiom in standard MLTT — breaks canonicity. PARTIALLY YES via cubical type theory (Agda --cubical) which provides computational content to `ua`. Open problem: combining full univalence + full canonicity in single formalization.

### CAGE DIAGNOSIS

**Layer affected:** FORMAT_CHANGE
**Within-format:** NO — Redefines what "identity" means at the foundational level. Between-format: bridges syntactic identity and semantic equivalence.

### TRANSPLANT SKETCH

Apply to ExprNode trees: if two trees are structurally equivalent (same algebraic content, different syntax), treat them as *identical* via a quotient. Define equivalence relation on ExprNode trees (structural isomorphism modulo commutativity of add/mul, etc.). Build transport operation that lifts fitness/properties from one encoding to the isomorphic one without re-evaluation. Practical: `ExprNode.canonical_form() → ExprNode` that normalizes structurally equivalent trees to a single representative, then archive deduplication via canonical forms rather than fingerprints. This would collapse the search space by identifying equivalent regions. **Limitation:** univalence itself is not computable as an axiom; the transplant uses only the *principle* (equivalence-as-identity) not the full type-theoretic machinery.

### VERDICT: STRUCTURAL_EXPANSION (with caveat: computability requires cubical interpretation)

---

## A.6 — Computability: Friedberg-Muchnik Theorem (Priority Arguments)

### SOURCE
Friedberg (1957), "Two recursively enumerable sets of incomparable degrees of unsolvability."
Muchnik (1956), "On the unsolvability of the problem of reducibility in the theory of algorithms."
Soare, "Recursively Enumerable Sets and Degrees," Ch. VII.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Single c.e. set construction via iterative enumeration. Approximations S₀ ⊆ S₁ ⊆ S₂ ⊆ ... where Sₛ contains elements enumerated by stage s. Cannot control conflicts between multiple competing objectives (requirements).

**New format:** Priority method for simultaneous satisfaction of infinitely many requirements. Requirements R₀, R₁, R₂, ... enumerated and assigned priorities (lower index = higher priority). Stage-by-stage construction with injury management: higher-priority requirements can "injure" (undo progress of) lower-priority ones. Each requirement injured only finitely often.

**Transition op:** Priority argument procedure: (1) Enumerate requirements {Rᵢ}. (2) At each stage s, scan requirements in priority order. (3) For each unsatisfied, uninjured Rᵢ, take action (e.g., enumerate element into A). (4) If higher-priority Rⱼ action conflicts, mark Rᵢ as injured. (5) Repeat. Invariant: each requirement injured finitely often → all eventually satisfied.

**Became expressible:** Incomparable c.e. degrees (A and B neither Turing-reduces to the other). Minimal pairs. Dense c.e. ideals. Infinite antichains. The priority method is the fundamental tool for constructing c.e. sets with specified relative properties — none of which are expressible via single-set construction.

**Computable:** PARTIALLY — the enumeration procedure is computable. The final sets A, B are c.e. (limit-computable). The total function "which requirements survive without injury" is computable in the limit but not in real-time.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar) — adds conflict resolution structure to composition
**Within-format:** YES — still produces c.e. sets, just with more sophisticated construction. Within-format enhancement of construction method, not format change.

### TRANSPLANT SKETCH

Priority-driven conflict resolution maps to MetaGrammarLayer: instead of random selection among meta-rules, assign priorities to competing design-space expansion strategies. When expanding vocabulary (Layer 1) conflicts with grammar modification (Layer 2), higher-priority requirement wins. Lower-priority requirements can be "injured" (rolled back) if they conflict. This formalizes the current random `expand_design_space()` into a principled multi-objective expansion strategy. Specific: `MetaGrammarLayer.expand_with_priorities(requirements: List[Requirement]) → action`.

### VERDICT: COMBINATORIAL_RECOMBINATION

Rationale: Priority arguments produce more sophisticated constructions within the SAME format (c.e. sets). The representational format is unchanged. The method is a within-format compositional technique, not a format change. Valuable for implementation but not cage-breaking.

---

## A.7 — Gödel Incompleteness as Generation (Diagonal Lemma)

### SOURCE
Gödel (1931), "Über formal unentscheidbare Sätze."
Boolos, "The Logic of Provability," Ch. 2.
Smullyan, "Diagonalization and Self-Reference."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Formulas as syntactic strings. No mechanism for a formula to reference its own encoding. Self-reference was informal/conceptual.

**New format:** Gödel numbering (formula ↔ natural number bijection) + substitution function sub(n, m) + diagonal construction. A formula can now formally reference its own encoding.

**Transition op:** Diagonal lemma construction (computable procedure): Given formula φ(x) with one free variable: (1) Define ψ(x) := φ(sub(x, x)), (2) Compute n = ⌜ψ⌝ (Gödel number of ψ), (3) Define σ := ψ(⌜n⌝) = φ(sub(⌜ψ⌝, ⌜ψ⌝)), (4) Result: T ⊢ σ ↔ φ(⌜σ⌝). The sentence σ claims property φ of its own Gödel number.

**Became expressible:** Self-referential sentences (undecidable Gödel sentences, Tarski undefinability, Löb's theorem). Programs that output their own source (quines). Any property can be turned into a self-referential claim. The diagonal lemma is a *generator* of new sentences not in the original enumeration.

**Computable:** YES — fully computable. Gödel numbering (prime encoding or Cantor pairing), substitution (decode, replace, re-encode), diagonal construction (compose above). Every step uses primitive recursive functions.

### CAGE DIAGNOSIS

**Layer affected:** FORMAT_CHANGE
**Within-format:** NO — Adds a reflexive capacity (self-reference) that the old format fundamentally lacks. A formula system with self-reference is strictly more expressive (can express its own consistency, provability, etc.) than one without.

### TRANSPLANT SKETCH

ExprNode trees already have `fingerprint()` (encoding) and `to_dict()` (serialization). The diagonal construction transplants as: (1) Encoding: tree → fingerprint (exists), (2) Decoding: fingerprint → tree (requires cache/lookup table — add to VocabularyLayer), (3) Self-reference: special operator `self_ref` that evaluates to the fingerprint of its containing tree, (4) Diagonal lemma analog: given property P on trees, construct tree T such that eval(T) = P(fingerprint(T)). This enables *reflective* trees that can inspect and reason about their own structure during evaluation. Implementation: add `PrimitiveOp("self_encode", 0, lambda: current_tree_fingerprint)` where `current_tree_fingerprint` is set during evaluation via a context variable. This would be a genuine F_theo expansion: trees with self-reference can express fixed-point computations that trees without self-reference cannot.

### VERDICT: STRUCTURAL_EXPANSION

---

## Session Summary

| Sub-topic | Formal Extractions | Verdict |
|-----------|-------------------|--------|
| A.1 Type Theory (Universe Polymorphism + IR) | Complete | STRUCTURAL_EXPANSION |
| A.2 Category Theory (Kan Extensions) | Complete | STRUCTURAL_EXPANSION |
| A.3 Adaptive Grammars (Shutt 2001) | Complete | STRUCTURAL_EXPANSION |
| A.4 Van Wijngaarden Two-Level Grammars | Complete | STRUCTURAL_EXPANSION |
| A.5 HoTT (Univalence Axiom) | Complete | STRUCTURAL_EXPANSION |
| A.6 Friedberg-Muchnik (Priority Arguments) | Complete | COMBINATORIAL_RECOMBINATION |
| A.7 Gödel Incompleteness (Diagonal Lemma) | Complete | STRUCTURAL_EXPANSION |

**Sub-topics investigated:** 7
**Full formal extractions completed:** 7
**STRUCTURAL_EXPANSION verdicts:** 6
**COMBINATORIAL_RECOMBINATION verdicts:** 1
**NO_STRUCTURE_FOUND:** 0
**Remaining incomplete:** 0
