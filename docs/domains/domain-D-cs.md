# Domain D — Computer Science & Computation Theory

**Session 4 | Date: 2026-03-25 | Status: COMPLETE**

---

## D.1 — Quines and Self-Replication (Kleene's Recursion Theorem)

### SOURCE
Kleene (1952), *Introduction to Metamathematics*, Chapter XI.
Rogers (1987), *Theory of Recursive Functions and Effective Computability*, §11.
Thompson (1984), "Reflections on Trusting Trust," Turing Award Lecture.
Bratley & Millo (1972), "Turing's thesis."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Programs as opaque indices. A program φₑ is identified by its index e in an acceptable numbering, but the program itself has no access to e. No program can compute a function of its own index without being externally provided that index. The system is non-reflective: computation proceeds forward-only with no introspective capacity.

**New format:** Programs parametrized by self-index via the s-m-n theorem. Kleene's Second Recursion Theorem guarantees: for any total computable f, there exists an index e such that φₑ = φ_{f(e)}. The program at index e "knows" its own index — it can compute functions of its own encoding. Quines are the simplest instance: f = identity, so φₑ outputs e itself.

**Transition op:** The s-m-n parametrization constructs the fixed point:
1. Start with a program P(x, y) that takes its own source x and an input y.
2. Use the s-m-n theorem to construct s(e) = index of "λy. P(φₑ, y)" for each e.
3. The recursion theorem guarantees a fixed point: an e* such that φ_{e*} = φ_{s(e*)} = λy. P(φ_{e*}, y).
4. At e*, the program has access to its own encoding φ_{e*} as the first argument.

**Became expressible:** Self-replication without external data source. Self-reference without infinite regress (the fixed-point construction is finite). Self-modifying computation (program can compute transformations of its own encoding). Recursive self-improvement (program can evaluate modifications to itself). Fixed-point computations that require a program to "know itself."

**Computable:** YES — The s-m-n theorem is constructive and effective. The fixed-point index e* is computable from the program P. Complexity: O(|P|²) for the construction.

### CAGE DIAGNOSIS

**Layer affected:** Layer 3 (Meta-Grammar) + FORMAT_CHANGE
**Within-format:** NO — The current ExprNode format has no mechanism for a tree to reference its own encoding. Trees are evaluated purely structurally with no access to their own representation. Adding self-reference (tree can serialize itself, compute on its serialization, and use the result) is a genuine format change that breaks the opacity barrier.

### TRANSPLANT SKETCH

Add a `self_encode` primitive operator to VocabularyLayer:
```python
class SelfEncodeOp(PrimitiveOp):
    """Returns a numerical encoding of the tree containing this node."""
    name = "self_encode"
    arity = 0  # nullary — takes no subtree arguments
    func = lambda tree_context: tree_context.fingerprint()
```

During `_eval_tree`, when encountering a SelfEncodeOp, pass the current tree's structural fingerprint as the evaluation result. This enables:
- Trees that compute functions of their own structure (quine-like)
- Self-referential fitness: a tree can evaluate how "good" its own structure is
- Fixed-point search: find trees whose output equals their own encoding

This directly addresses the architectural ceiling identified in Session 1: "no tree can reference its own encoding."

Connection to A.7 (Diagonal Lemma): The Pāṇinian self-reference (D.1) and the Gödelian self-reference (A.7) are formally the same mechanism — Kleene's recursion theorem IS the computational version of the diagonal lemma.

### VERDICT: STRUCTURAL_EXPANSION

---

## D.2 — Grammar-Guided Genetic Programming & Grammatical Evolution

### SOURCE
Whigham (1995), "Grammatically-based Genetic Programming," *ICML Workshop on GP*.
O'Neill & Ryan (2001), "Grammatical Evolution," *IEEE Trans. Evol. Comp.*
Fenton et al. (2017), "PonyGE2: Grammatical Evolution in Python."
Medvet et al. (2020), "A Comparative Analysis of Dynamic Locality in GP and GE."

### FORMAL STRUCTURE EXTRACTION

**Old format (Static GGGP/GE):** A fixed context-free grammar G defines the search space. Programs are derived from G by applying production rules. The grammar is determined before evolution begins and never changes. The expressible function set F_theo = L(G) — the language of the grammar.

**New format (Dynamic GGGP with grammar expansion):** The grammar G_t evolves alongside the population. At generation t: (1) mine frequent subtree patterns from elite programs, (2) synthesize new production rules capturing these patterns, (3) retire low-utility rules. F_theo(t) = L(G_t) where L(G_t) ⊂ L(G_{t+1}) — the language grows monotonically.

**Transition op:** For static GGGP: map genotype (integer sequence in GE, derivation tree in GGGP) to phenotype (program) via grammar derivation. Each integer selects a production rule at a choice point. For dynamic expansion: (1) Track rule usage frequency across elite programs. (2) Identify recurring derivation subsequences. (3) Promote frequent subsequences to new non-terminals with corresponding production rules. (4) Remove rules unused for k generations.

**Became expressible:** Static GGGP: no new expressibility vs. unconstrained GP — same F_theo, different F_eff (grammar guides search, avoids invalid programs). Dynamic GGGP: genuinely new programs as L(G_t) grows. The grammar expansion mechanism is structurally identical to library learning (DreamCoder) and Wilson RG (Session 2, B.3).

**Computable:** YES — Grammar derivation is O(n) in derivation length. Rule mining is O(|archive| × max_depth). Rule synthesis is template-based.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar) for static; Layer 2+3 for dynamic.
**Within-format:** Static GGGP = YES (grammar constrains but doesn't expand F_theo). Dynamic GGGP with intelligent rule synthesis = borderline (F_theo grows as grammar grows, but this is the same mechanism as LibraryLearner — already implemented).

### TRANSPLANT SKETCH

The RSI system's GrammarLayer + MetaGrammarLayer + LibraryLearner already implement the core dynamic GGGP mechanism. The key enhancement from GGGP literature:

1. **Derivation tracking:** Record which grammar rules were used to construct each elite tree. Currently not tracked.
2. **Rule utility scoring:** Score each rule by frequency × fitness_contribution. Retire low-scoring rules.
3. **Systematic rule synthesis:** Replace random `_meta_compose_new_op` with pattern-mined rule synthesis (as in dynamic GGGP).

This is an efficiency improvement (F_eff) rather than an expressibility expansion (F_theo), since LibraryLearner already achieves the core grammar expansion.

### VERDICT: COMBINATORIAL_RECOMBINATION (static GGGP/GE isomorphic to constrained GP; dynamic GGGP mechanism already implemented as LibraryLearner)

---

## D.3 — DreamCoder: Wake-Sleep Library Learning

### SOURCE
Ellis et al. (2021), "DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning," *PLDI 2021*.
Ellis et al. (2018), "Learning Libraries of Subroutines for Neurally-Guided Bayesian Program Induction," *NeurIPS 2018*.

### FORMAL STRUCTURE EXTRACTION

**Old format (RSI LibraryLearner as currently implemented):** Frequency-based subtree extraction. The LibraryLearner scans elite trees, groups by structural fingerprint, filters by frequency ≥ min_frequency, ranks by frequency × depth, and promotes top candidates to new PrimitiveOps. Selection criterion: frequency × depth (compression value heuristic).

**New format (Full DreamCoder):** Three-phase wake-sleep cycle:
1. **Wake phase:** Neural recognition model proposes programs for tasks. The recognition model is trained on (task, program) pairs from previous solutions.
2. **Sleep phase (dreaming):** Sample programs from the current library, generate synthetic tasks they solve, train the recognition model on these pairs.
3. **Compression phase:** Bayesian model selection over library refactorings. For each candidate abstraction λ, compute compression gain = Σ_tasks log P(solution | library ∪ {λ}) - log P(solution | library) - description_length(λ). Accept λ if compression gain > 0.

**What DreamCoder has that RSI LibraryLearner lacks:**
- **Neural recognition model:** Amortized inference — learns to propose likely programs without enumeration. RSI uses random generation.
- **Bayesian compression criterion:** Principled library selection based on minimum description length. RSI uses frequency × depth heuristic.
- **Dream phase:** Self-generated training data to prevent catastrophic forgetting. RSI has no equivalent.
- **Task-conditioned extraction:** Abstractions are selected based on how much they compress solutions to SPECIFIC tasks. RSI extracts based on global frequency.

**Became expressible:** The compression phase does NOT expand F_theo beyond what LibraryLearner already achieves (both promote subtrees to primitives, enabling depth ceiling bypass). The neural recognition model and dream phase improve F_eff (search efficiency) dramatically but don't change what's theoretically expressible.

**Computable:** YES — All phases are effective. Compression phase is NP-hard in general but tractable with beam search approximation.

### CAGE DIAGNOSIS

**Layer affected:** Layer 1 (Vocabulary) + Layer 2 (Grammar) — same layers as LibraryLearner.
**Within-format:** YES for F_theo (DreamCoder's library learning expands F_theo the same way LibraryLearner does — depth ceiling bypass via subtree promotion). The Bayesian compression criterion is more principled but achieves the same structural expansion.

### TRANSPLANT SKETCH

**High-value transplant (compression gain criterion):**
Replace LibraryLearner's `frequency × depth` heuristic with compression gain:
```python
def compression_gain(subtree, archive):
    """Bayesian compression: how much shorter are elite programs with this primitive?"""
    gain = 0
    for tree in archive.elites():
        occurrences = count_occurrences(subtree, tree)
        gain += occurrences * (subtree.depth - 1)  # depth saved per occurrence
    cost = description_length(subtree)  # cost of adding to library
    return gain - cost
```

**Lower-priority transplant (recognition model):**
Train a lightweight neural model to predict which grammar rules to apply given a target fitness profile. This replaces random tree generation with guided synthesis. Significant engineering effort; improves F_eff, not F_theo.

### VERDICT: COMBINATORIAL_RECOMBINATION (DreamCoder's core F_theo expansion mechanism = LibraryLearner, already implemented; Bayesian criterion and neural guidance improve F_eff)

---

## D.4 — Reflection and Meta-Programming

### SOURCE
Smith (1982), "Procedural Reflection in Programming Languages," PhD thesis, MIT (3-Lisp).
Wand & Friedman (1988), "The Mystery of the Tower Revealed."
Kiczales et al. (1991), *The Art of the Metaobject Protocol*.
Maes (1987), "Concepts and Experiments in Computational Reflection."

### FORMAL STRUCTURE EXTRACTION

**Old format:** Non-reflective computation. Programs execute forward-only on data. The interpreter/evaluator is a fixed black box — programs cannot inspect or modify their evaluation mechanism. The execution environment (stack, bindings, control flow) is invisible to the program.

**New format (Reflective tower — 3-Lisp):** Programs have access to their own execution state via *reification* (making implicit execution state explicit as data) and *reflection* (modifying execution by modifying reified state). Smith's 3-Lisp provides three levels:
1. **Object level:** The program computes on data.
2. **Meta level:** The program can inspect its own execution (bindings, continuation, environment).
3. **Meta-meta level:** The program can inspect/modify the meta-level interpreter.

The reflective tower extends infinitely: each level is interpreted by the level above. In practice, implemented via a "tower of interpreters" with level-shifting operators.

**Transition op:** Two key operations:
1. **Reify (↑):** Convert implicit execution state to explicit data object. E.g., reify the current continuation → a function object representing "the rest of the computation."
2. **Reflect (↓):** Install a data object as execution state. E.g., reflect a modified continuation → computation resumes with altered control flow.

**Became expressible:** Programs that inspect their own bindings, modify their evaluation strategy at runtime, implement custom control flow, create self-optimizing interpreters, debug themselves. Meta-circular evaluation (interpreter for the language written in the language, with ability to modify interpretation).

**Computable:** YES — Reification/reflection are implemented operations (3-Lisp, CLOS MOP, Smalltalk metaclasses). The reflective tower requires care with termination but is effective for finite levels.

### CAGE DIAGNOSIS

**Layer affected:** Layer 3 (Meta-Grammar) + FORMAT_CHANGE
**Within-format:** NO — Current ExprNode evaluation is completely non-reflective. Trees cannot inspect their evaluation mechanism, cannot access the GrammarLayer rules that constructed them, cannot modify the VocabularyLayer during evaluation. Adding reflection requires: (1) reification of evaluation context as ExprNode-accessible data, (2) reflection operators that modify evaluation behavior. This is a FORMAT_CHANGE.

**However, for F_theo specifically:** Reflection enables programs to modify their *evaluation strategy* but not (in general) to compute functions that a non-reflective program with the same primitives cannot. The Church-Turing thesis ensures that a reflective system and a non-reflective system with equivalent primitives compute the same class of functions. Reflection expands *pragmatic* expressibility (what's convenient to express) rather than *theoretical* expressibility (what's possible to express).

**Critical nuance:** Reflection combined with self-modification (D.7) DOES expand F_theo — the tree can inspect itself AND modify itself based on what it finds. Reflection alone is COMBINATORIAL_RECOMBINATION; reflection + self-modification is STRUCTURAL_EXPANSION.

### TRANSPLANT SKETCH

**Reification (read-only reflection):**
```python
class ReifyOp(PrimitiveOp):
    """Returns information about the current evaluation context."""
    name = "reify_depth"  # or reify_parent, reify_siblings, etc.
    arity = 0
    func = lambda ctx: ctx.current_depth  # access evaluation context
```

Thread an `EvalContext` through `_eval_tree` that accumulates: current depth, parent op, sibling results, evaluation count, archive statistics. Reification operators read from this context.

**Connection to Domain C:** This is exactly the "context-dependent evaluation" identified in C.3 (Aramaic polysemy), C.4 (cuneiform), and C.1c (kāraka). Reification is the CS formalization of the linguistic context-threading mechanism.

### VERDICT: COMBINATORIAL_RECOMBINATION (reflection alone does not expand F_theo; it expands pragmatic expressibility and F_eff)

---

## D.5 — Type Systems: Dependent Types and Refinement Types

### SOURCE
Martin-Löf (1984), *Intuitionistic Type Theory*.
Xi & Pfenning (1999), "Dependent Types in Practical Programming," *POPL*.
Rondon et al. (2008), "Liquid Types," *PLDI*.
Vazou et al. (2014), "Refinement Types for Haskell," *ICFP*.
Siek & Taha (2006), "Gradual Typing for Functional Languages," *Scheme Workshop*.

### FORMAL STRUCTURE EXTRACTION

#### D.5a — Dependent Types

**Old format (Simply typed):** Types are independent of values. Function type A → B says nothing about the relationship between input and output values. A vector of length 5 and a vector of length 10 have the same type (Vec). Type checking cannot enforce length invariants.

**New format (Dependently typed):** Types can depend on values. Π(n: Nat). Vec(n) → Vec(n) types a function that takes a natural number n and a vector of length n, returning a vector of the same length n. The type system enforces length preservation at compile time.

**Transition op:** Replace simple type formers (→, ×) with dependent type formers (Π, Σ). Π(x:A).B(x) generalizes A → B (when B doesn't depend on x). Σ(x:A).B(x) generalizes A × B. Type checking becomes undecidable in general (requires evaluation to check type equality) but decidable for well-founded programs.

**Became expressible:** Types that encode program specifications (length-preserving, sorted, balanced). Proofs as programs (Curry-Howard correspondence extends to predicate logic). Programs that are verified correct by construction. Previously: specifications were external comments; now they're machine-checked types.

**Computable:** YES for type checking of well-founded programs (decidable). NO in general (type checking dependently-typed programs can require arbitrary computation).

#### D.5b — Refinement Types

**Old format:** Base types (Int, Bool, Float) with no logical constraints. Any integer is an Int, including negative numbers, even when the program requires positive numbers.

**New format:** Base types refined with logical predicates. {x: Int | x > 0} is the type of positive integers. {xs: List | sorted(xs)} is the type of sorted lists. Type checking verifies that refinement predicates are satisfied at every usage point, typically via SMT solver.

**Transition op:** (1) Annotate types with logical predicates drawn from a decidable logic (e.g., linear arithmetic). (2) At each program point, generate verification conditions (VCs) expressing that the refinement holds. (3) Discharge VCs via SMT solver. (4) If all VCs are satisfied, the program is type-safe with respect to refinements.

**Became expressible:** Specification-level guarantees within the type system: preconditions, postconditions, invariants. Programs that cannot violate their specifications (caught at compile time). Properties like "array index within bounds" become type errors rather than runtime errors.

**Computable:** YES — Liquid types restrict refinements to a decidable logic, making type inference fully automatic via SMT.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar) — type system constrains which compositions are valid.
**Within-format (Dependent types):** STRUCTURAL_EXPANSION — Dependent types don't just constrain; they enable new compositions that are only valid when type indices match. A function Π(n: Nat). Vec(n) → Vec(n+1) requires dependent typing to express the n+1 relationship. In ExprNode terms: enabling type-indexed composition rules where rule applicability depends on computed values.

**Within-format (Refinement types):** STRUCTURAL_EXPANSION for F_eff (eliminates invalid programs from search space); BORDERLINE for F_theo (same programs are expressible, but refinement types enable the *system* to verify correctness, which is new capability).

### TRANSPLANT SKETCH

**Refinement types for ExprNode (high priority):**
Add type annotations to PrimitiveOps specifying input/output domains:
```python
class TypedPrimitiveOp(PrimitiveOp):
    input_type: RefinementType  # e.g., {x: float | -10 < x < 10}
    output_type: RefinementType  # e.g., {y: float | y >= 0}
```

During tree construction, GrammarLayer checks type compatibility: only compose ops whose output type refines the next op's input type. This eliminates invalid compositions (e.g., applying sqrt to a potentially negative input).

**Dependent types for ExprNode (lower priority):**
Enable composition rules that depend on runtime values. E.g., a rule that says "this binary op can only be applied to subtrees of matching depth." Implementation: `GrammarRule.applicability(left_subtree, right_subtree) → bool` with access to computed properties of subtrees.

### VERDICT: STRUCTURAL_EXPANSION (dependent types add type-indexed compositions; refinement types expand F_eff dramatically and add verification capability)

---

## D.6 — Automata Theory: Beyond Context-Free

### SOURCE
Aho (1968), "Indexed Grammars — An Extension of Context-Free Grammars," *JACM*.
Joshi (1985), "Tree Adjoining Grammars," in *Natural Language Parsing*.
Weir (1988), "Characterizing Mildly Context-Sensitive Grammar Formalisms," PhD thesis, UPenn.
Vijay-Shanker et al. (1987), "Some Computational Properties of TAGs," *ACL*.

### FORMAL STRUCTURE EXTRACTION

#### D.6a — Indexed Grammars (Aho 1968)

**Old format (CFG):** Productions A → α where A is a non-terminal and α is a string of terminals and non-terminals. Each non-terminal generates independently — no information passes between sibling derivations. Language class: CFL (context-free languages).

**New format (Indexed Grammar):** Each non-terminal carries a stack of indices: A[f₁f₂...fₙ]. Productions can:
1. Push index onto stack: A[σ] → B[fσ] (adds f to stack)
2. Pop index from stack: A[fσ] → B[σ] C[σ] (removes f, copies remaining to children)
3. Copy stack to children: A[σ] → B[σ] C[σ] (both children inherit full stack)

The index stack carries context from parent to children, enabling non-local dependencies. Language class: indexed languages (properly contains CFL).

**Transition op:** Augment each non-terminal with an index stack. Productions are parameterized by stack operations (push, pop, copy). The key addition: information flows from parent to child via the stack, creating cross-serial dependencies impossible in CFGs.

**Became expressible:** Cross-serial dependencies (e.g., {aⁿbⁿcⁿ | n ≥ 0} — not context-free). Copy language {ww | w ∈ {a,b}*}. Swiss-German word order (cross-serial verb dependencies). Duplication patterns requiring unbounded counting across derivation branches.

**Computable:** YES — Indexed grammar membership is decidable (though PSPACE-complete vs. O(n³) for CFGs). Parsing is polynomial for bounded index stack depth.

#### D.6b — Tree-Adjoining Grammars (Joshi 1985)

**Old format (CFG tree):** Derivation trees where each internal node applies exactly one production. Trees grow only by substitution (replacing a leaf non-terminal with a derived tree).

**New format (TAG tree):** Two tree operations:
1. **Substitution:** Same as CFG — replace a leaf with a derived tree.
2. **Adjunction:** Insert an "auxiliary tree" into the middle of an existing tree. An auxiliary tree has a "foot node" of the same type as its root; adjunction splices the auxiliary tree at an internal node, moving the original subtree below to the foot node.

**Transition op:** Adjunction is the key new operation. Given a tree T with internal node n of type A, and an auxiliary tree β with root and foot of type A: adjunction at n removes the subtree below n, replaces it with β, and attaches the removed subtree at β's foot node. This enables tree-internal insertion — modifying the structure of an existing tree without rebuilding it.

**Became expressible:** Mildly context-sensitive languages (properly contains CFL, properly contained in indexed languages). Nested dependencies that cross over each other. Crucially for ExprNode: **modular tree composition** — adjunction allows inserting a "wrapper" around any subtree without changing the subtree itself.

**Computable:** YES — TAG parsing is O(n⁶) — polynomial. TAG generation is polynomial.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar) — both indexed grammars and TAGs expand the grammar's generative power.
**Within-format:** NO — Both expand the class of generable trees beyond CFG:
- Indexed grammars add context propagation via stacks (ExprNode trees currently have no context propagation between siblings).
- TAGs add adjunction (ExprNode trees currently only grow by substitution/composition, not by internal insertion).

### TRANSPLANT SKETCH

**Indexed grammar → ExprNode (stack-based context):**
Add an index stack to each node during tree construction:
```python
class IndexedExprNode(ExprNode):
    index_stack: List[str]  # context passed from parent
```

Grammar rules parameterized by stack operations:
- Push rule: when constructing subtree, push a context marker onto the stack
- Pop rule: when encountering a marker, select grammar rule based on marker
- Copy rule: both children of a binary node inherit the parent's stack

This enables cross-serial dependencies: a composition rule at depth d can constrain behavior at depth d+k via the shared stack. Currently impossible in ExprNode.

**TAG adjunction → ExprNode:**
Add an `adjoin` mutation operator to the evolutionary system:
```python
def adjoin(tree, node, auxiliary_tree):
    """Insert auxiliary_tree at node, moving node's subtree to foot."""
    original_subtree = node.children
    node.children = auxiliary_tree
    auxiliary_tree.foot_node.children = original_subtree
```

This is a new mutation operator for MAP-Elites that modifies tree INTERNALS without changing the leaves (primitives at the boundary). Current mutations only modify at leaves or rebuild from scratch.

**Where ExprNode sits in Chomsky hierarchy:** The current GrammarLayer generates trees equivalent to a regular tree grammar (Type-3 in the tree language hierarchy). Adding indexed stacks moves it to Type-2+ (indexed tree grammar). Adding adjunction moves it to mildly context-sensitive (TAG-equivalent).

### VERDICT: STRUCTURAL_EXPANSION

---

## D.7 — Self-Modifying Code and Gödel Machines

### SOURCE
Schmidhuber (2006), "Gödel Machines: Fully Self-Referential Optimal Universal Self-Improvers," in *Artificial General Intelligence*.
Schmidhuber (2007), "Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements," arXiv cs/0309048.
Clune (2019), "AI-Generating Algorithms (AI-GAs)."
Hu et al. (2025), "The Darwin Gödel Machine," arXiv 2505.22954.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Fixed evaluation mechanism. The SelfImprovementEngine can modify its vocabulary (Layer 1) and grammar rules (Layers 2-3) but cannot modify the `_eval_tree` function, the `_generate_tree` function, the fitness function, or the engine's own search strategy. The evaluation mechanism is a fixed black box that interprets ExprNode trees.

**New format (Gödel Machine):** The entire system — including evaluation, search strategy, and proof system — is encoded as data that the system can inspect and modify. A modification is applied if and only if the system's proof searcher finds a proof that the modification improves expected future performance according to a utility function. The "global optimality theorem" guarantees: if a provably beneficial self-modification exists, the Gödel Machine will eventually find and apply it.

**Darwin Gödel Machine (2025):** Relaxes the formal proof requirement. Instead of mathematical proofs, uses empirical validation: (1) propose a code modification, (2) test it on a held-out benchmark, (3) accept if performance improves. This makes the system practical (proofs are intractable for real code) while sacrificing formal guarantees.

**Transition op:**
1. **Encode** the system's own source code as data accessible to the system.
2. **Search** for modifications to the code that provably (Gödel) or empirically (Darwin) improve performance.
3. **Verify** the modification: formal proof (Gödel) or benchmark test (Darwin).
4. **Apply** the modification: replace the active code with the modified version.

**Became expressible:** Self-modification of the evaluation mechanism itself. Modification of the search strategy (not just the search space). Optimization of the optimization algorithm. This is a qualitative leap: the system can rewrite ANY part of itself, not just the vocabulary/grammar.

**Computable:** YES (construction is effective). Practical limitations: proof search for Gödel Machine is intractable for non-trivial systems. Darwin Gödel Machine sidesteps this via empirical validation (benchmarking).

### CAGE DIAGNOSIS

**Layer affected:** ALL layers + FORMAT_CHANGE (cage-breaking)
**Within-format:** NO — This is the ultimate cage-breaking mechanism. The system doesn't just expand its vocabulary, grammar, or meta-grammar — it can rewrite the rules for how those layers operate. A Gödel Machine with ExprNode trees could: change the evaluation function, modify the fitness function, alter the search strategy, redesign the archive structure. None of these are possible in the current fixed-evaluation architecture.

### TRANSPLANT SKETCH

**Darwin Gödel Machine approach (practical):**
```python
class DarwinGM:
    def propose_modification(self, engine):
        """Propose a modification to the engine's code/parameters."""
        # Sample from space of modifications:
        # - change max_depth, mutation_rate, selection_pressure
        # - swap evaluation strategy
        # - modify fitness function weights
        return Modification(target, old_value, new_value)

    def validate(self, modification, benchmark_tasks):
        """Empirically validate the modification."""
        baseline = engine.run(benchmark_tasks)
        engine.apply(modification)
        modified = engine.run(benchmark_tasks)
        if modified.score > baseline.score:
            return ACCEPT
        else:
            engine.revert(modification)
            return REJECT
```

**Scope of self-modification for ExprNode RSI:**
1. **Parameter tuning** (minimal): mutation rates, selection pressure, archive size — doesn't change F_theo.
2. **Evaluation strategy** (moderate): change `_eval_tree` to context-dependent evaluation — changes F_theo.
3. **Representation change** (maximal): switch from ExprNode trees to graph programs, stack machines, or hybrid — changes F_theo fundamentally.

The Darwin Gödel Machine provides the framework for all three levels. Level 2 connects to C.3/C.4 (context-dependent evaluation). Level 3 connects to B.7 (M-theory unification).

### VERDICT: STRUCTURAL_EXPANSION (cage-breaking — system can modify its own evaluation mechanism)

---

## D.8 — Lambda Calculus Extensions: Delimited Continuations and Algebraic Effects

### SOURCE
Danvy & Filinski (1990), "Abstracting Control," *LFP*.
Felleisen (1988), "The Theory and Practice of First-Class Prompts," *POPL*.
Plotkin & Power (2001), "Adequacy for Algebraic Effects," *FOSSACS*.
Pretnar (2015), "An Introduction to Algebraic Effects and Handlers," *ENTCS*.

### FORMAL STRUCTURE EXTRACTION

#### D.8a — Delimited Continuations (shift/reset)

**Old format (Pure tree evaluation):** ExprNode trees are evaluated bottom-up. Each node computes a value from its children's values. There is no notion of "the rest of the computation" — evaluation at each node is local. Control flow is strictly tree-recursive.

**New format (shift/reset):** Two new operators:
- **reset** (⟨...⟩): Delimits a continuation. Marks a boundary in the computation.
- **shift** (S(k, ...)): Captures the continuation up to the nearest reset as a first-class function k, then computes with k available.

The continuation k represents "what would have happened after this point" — it's the computation context reified as a callable function.

**Transition op:** (1) During evaluation, maintain a continuation stack. (2) When encountering `reset`, push a delimiter on the stack. (3) When encountering `shift`, capture everything between the current point and the nearest delimiter as function k. (4) Evaluate the shift body with k available as a callable. (5) The result of the shift body replaces the entire delimited computation.

**Became expressible:** Non-local control flow within tree evaluation: early exit (evaluate shift body, discard k), backtracking (call k multiple times with different values), coroutines (yield via shift, resume via calling k). Exception-like behavior without special mechanisms. Composable control operators (shift/reset compose, unlike undelimited call/cc).

**Computable:** YES — shift/reset is implementable as a source-to-source CPS transformation. The transformation is mechanical and preserves semantics.

#### D.8b — Algebraic Effects and Handlers

**Old format:** Side effects (I/O, state, exceptions, nondeterminism) are hardcoded into the evaluation mechanism. Each effect requires special-case handling in the evaluator.

**New format:** Effects are declared as algebraic operations (op: A → B) with no built-in semantics. Handlers provide semantics for effects, and handlers compose:
```
handler H {
    op(x, resume) → ... resume(v) ...  // handle effect op
    return(x) → x                       // handle return value
}
```

When an effect op is invoked during evaluation, control transfers to the nearest enclosing handler for op. The handler receives the argument AND the continuation (resume). The handler decides whether/how to resume.

**Transition op:** (1) Replace hardcoded effects with algebraic operation declarations. (2) Wrap computations in handlers that define effect semantics. (3) Handlers compose by nesting. (4) Different handlers for the same effect produce different behaviors (e.g., a nondeterminism effect can be handled by backtracking, random choice, or enumeration).

**Became expressible:** Modular side effects — same computation, different behaviors depending on handler. Stackable handlers (compose state + exception + nondeterminism). User-defined control flow effects. Meta-programming of evaluation semantics.

**Computable:** YES — Algebraic effects have clean denotational semantics and are implemented in Eff, Koka, OCaml 5, etc.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar — new composition operators) + FORMAT_CHANGE
**Within-format:** NO for both:
- **Continuations:** ExprNode evaluation currently cannot capture "the rest of the computation." Adding shift/reset requires a continuation-passing evaluation mode. This is a genuine format change.
- **Algebraic effects:** ExprNode evaluation currently has no effect system. Adding effects + handlers requires: (1) effect operation primitives, (2) handler composition during evaluation, (3) continuation capture for each effect invocation. Format change.

**F_theo analysis:** Delimited continuations add expressiveness equivalent to adding control operators — strictly more expressive than pure tree evaluation. Algebraic effects don't increase F_theo beyond delimited continuations (effects are encodable with continuations) but provide modular decomposition.

### TRANSPLANT SKETCH

**Delimited continuations for ExprNode:**
Add `shift` and `reset` as special ExprNode operators:
```python
class ResetNode(ExprNode):
    """Delimits a continuation boundary."""
    child: ExprNode  # the delimited computation

class ShiftNode(ExprNode):
    """Captures continuation to nearest reset as function k."""
    body: ExprNode  # evaluated with k bound to captured continuation
```

Modify `_eval_tree` to maintain a continuation stack. When evaluating ShiftNode, capture the current continuation (computation context between shift and nearest reset), make it available as a callable PrimitiveOp, and evaluate the body.

**Algebraic effects for ExprNode:**
Define effect operations as PrimitiveOps that "perform" an effect:
```python
class EffectOp(PrimitiveOp):
    effect_name: str  # e.g., "choose", "fail", "state_get"
```

Wrap trees in HandlerNodes that define semantics for effects:
```python
class HandlerNode(ExprNode):
    handlers: Dict[str, Callable]  # effect_name → handler function
    body: ExprNode  # the computation being handled
```

This enables: trees that express nondeterministic computation (choose effect), trees with mutable state (state effect), trees with early exit (fail effect) — all composable via handler stacking.

### VERDICT: STRUCTURAL_EXPANSION (continuations add genuinely new control flow; effects add modular decomposition of evaluation semantics)

---

## Cross-Domain Patterns (Domain D)

### Pattern 1: Self-Reference is the Master Cage-Breaking Mechanism
D.1 (quines/Kleene), D.4 (reflection), and D.7 (Gödel Machines) form a progression: quines enable self-reference at the data level, reflection enables self-inspection at the evaluation level, Gödel Machines enable self-modification at the system level. The progression directly addresses the three identified ceilings: no self-reference → quines; static evaluation → reflection; fixed evaluation mechanism → Gödel Machine.

### Pattern 2: LibraryLearner is Already the Core Mechanism
D.2 (dynamic GGGP) and D.3 (DreamCoder) both reduce to the same mechanism already implemented as LibraryLearner: extract frequent subtrees, promote to primitives. DreamCoder's Bayesian compression criterion is more principled but achieves the same structural expansion. The RSI system has already implemented the core F_theo expansion mechanism from program synthesis.

### Pattern 3: Control Flow is the Missing Dimension
D.8 (continuations + effects) reveals that ExprNode evaluation has no control flow beyond bottom-up tree recursion. Adding continuations enables non-local jumps, backtracking, and coroutines — a dimension of expressiveness entirely absent from the current system.

### Pattern 4: Type Constraints Reduce Wasted Search
D.5 (type systems) shows that adding type constraints to ExprNode composition would dramatically reduce the fraction of invalid trees generated during evolution. This is primarily an F_eff improvement but with F_theo implications for dependent types (type-indexed compositions).

### Pattern 5: Hierarchy Position Matters
D.6 (automata theory) places ExprNode trees at the regular tree grammar level — the weakest in the tree language hierarchy. Moving to indexed tree grammars (via stack-based context) or TAG-equivalent (via adjunction) would expand both the class of generable trees and the functions they can express.

---

## Summary Statistics

| Sub-topic | Verdict | Layers | Format Change |
|-----------|---------|--------|---------------|
| D.1 Quines/Kleene | STRUCTURAL_EXPANSION | L3+FORMAT | Yes |
| D.2 GGGP/GE | COMBINATORIAL_RECOMBINATION | L2+L3 | No |
| D.3 DreamCoder | COMBINATORIAL_RECOMBINATION | L1+L2 | No |
| D.4 Reflection | COMBINATORIAL_RECOMBINATION | L3 | Partial |
| D.5 Type Systems | STRUCTURAL_EXPANSION | L2 | Yes |
| D.6 Automata/TAG | STRUCTURAL_EXPANSION | L2+FORMAT | Yes |
| D.7 Gödel Machines | STRUCTURAL_EXPANSION | ALL+FORMAT | Yes (cage-breaking) |
| D.8 Continuations/Effects | STRUCTURAL_EXPANSION | L2+FORMAT | Yes |

**Totals:** 8 sub-topics investigated, 8 formal extractions completed.
- STRUCTURAL_EXPANSION: 5 (D.1, D.5, D.6, D.7, D.8)
- COMBINATORIAL_RECOMBINATION: 3 (D.2, D.3, D.4)
- NO_STRUCTURE_FOUND: 0

**Strongest cage-breaking candidates:**
1. **Gödel Machine / self-modification** (D.7) — system can rewrite its own evaluation mechanism; ultimate cage-breaking
2. **Quines / self-reference** (D.1) — trees that can reference their own encoding; addresses core architectural ceiling
3. **Continuations / algebraic effects** (D.8) — adds control flow dimension entirely absent from current system
4. **Indexed grammars / TAG adjunction** (D.6) — moves ExprNode from regular tree grammar to mildly context-sensitive
5. **Dependent / refinement types** (D.5) — type-indexed composition rules with verification capability