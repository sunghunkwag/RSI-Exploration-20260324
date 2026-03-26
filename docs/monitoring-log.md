# Monitoring Log

## 2026-03-25
- arxiv scanned: 38, relevant: 12, deeper_read: 12
- GitHub scanned: 25, relevant: 4
- Cumulative: arxiv 38, GitHub 25

### arxiv highlights
- Darwin Gödel Machine (2505.22954) — RELEVANT: code self-modification with iterative improvement
- Group-Evolving Agents (2602.04837) — RELEVANT: treats agent groups as evolutionary unit
- Test-time Recursive Thinking (2602.03094) — RELEVANT: self-improvement via strategy accumulation
- AgentFactory (2603.18000) — RELEVANT: preserves task solutions as executable code
- STOP (2310.02304) — RELEVANT: LM-infused scaffolding for recursive code improvement
- REvolution (2510.21407) — RELEVANT: evolutionary computation + LLM design strategy evolution
- Grammar-guided GP for multigrid (2412.05852) — DEEPER_READ: grammar expressibility impact
- Data types as GP frontend (2210.04826) — DEEPER_READ: type system integration for grammar expressibility
- EvoSpeak (2510.02686) — DEEPER_READ: grammar-guided GP with LLM interpretability

### GitHub highlights
- TensorNEAT (EMI-Group/tensorneat) — RELEVANT: JAX-based NEAT with topology expansion at runtime
- PGA-MAP-Elites (ollebompa/PGA-MAP-Elites) — RELEVANT: scalable quality-diversity search
- DCRL-MAP-Elites (adaptive-intelligent-robotics/DCRL-MAP-Elites) — RELEVANT: descriptor-conditioned critic for MAP-Elites
- PyTorch NEAT (ddehueck/pytorch-neat) — RELEVANT: runtime topology expansion via node/connection mutations

## 2026-03-25 (Session 2)
- arxiv scanned: 19, relevant: 8, deeper_read: 8
- GitHub scanned: 0 (reused Session 1 scan, same day)
- Cumulative: arxiv 57, GitHub 25

### arxiv highlights (Session 2 incremental)
- ShinkaEvolve (2509.19349) — DEEPER_READ: open-ended program evolution with LLM-driven framework (ICLR 2026)
- AdaEvolve (2602.20133) — RELEVANT: hierarchical adaptive optimization for LLM-driven evolution
- SymPE (2503.21985) — DEEPER_READ: symmetry breaking expanding representational power in equivariant networks
- Parameter Symmetry Breaking (2502.05300) — DEEPER_READ: symmetry dynamics as mechanism for hierarchical representation formation
- Representation theory and Langlands duality (2510.06990) — DEEPER_READ: pure math on representation theory
- Cluster structures and tropical duality (2411.11633) — DEEPER_READ: representation theory with duality perspective

## 2026-03-26 (V4/V5 Verification Session)
- arxiv scanned: 22, relevant: 7
- GitHub scanned: 12, relevant: 3
- Cumulative: arxiv 79, GitHub 37

### arxiv highlights
- Darwin Gödel Machine v2 (2505.22954, updated 2026-03-12) — DEEPER_READ: SWE-bench 20%→ 50%. Self-modifying coding agents via archive + foundation model mutation. CAGE: content modification, not format change. No formal transition structure.
- Gödel Agent (2410.04444) — RELEVANT: LLM-driven self-referential recursive improvement. Prompt-driven behavioral modification, not representational. V3: EXTERNAL_INJECTION.
- DéjàQ (2601.01931) — RELEVANT: MAP-Elites for evolving diverse RL training problems. LLM-guided mutators. Joint problem-model co-evolution. No representation format change.
- Dominated Novelty Search (2502.00593) — RELEVANT: replaces grid-based archive with dynamic fitness transformations. Search procedure change, not representation change.
- OpenEvolve/AlphaEvolve (open-source, multiple repos) — RELEVANT: MAP-Elites population + LLM mutation for algorithm discovery. Program database uses island model. No grammar evolution.
- ShinkaEvolve (SakanaAI) — RELEVANT: multi-island evolution with LLM mutation operators. Patch-based modification. No representation expansion.
- Duality viewpoint of noninvertible symmetry (2502.20435) — DEEPER_READ: noninvertible symmetry protected topological phases via duality. Condensed matter, not directly transplantable.

### GitHub highlights
- OpenEvolve (algorithmicsuperintelligence/openevolve) — RELEVANT: open-source AlphaEvolve with MAP-Elites. >10k stars. Uses island-based population model. No runtime representation expansion.
- ShinkaEvolve (SakanaAI/ShinkaEvolve) — RELEVANT: LLM-driven program evolution framework. EVOLVE-BLOCK markers for mutable regions. No grammar evolution or design space expansion.
- awesome-open-ended (jennyzzt/awesome-open-ended) — RELEVANT: curated collection of open-ended AI research. Good reference list.

### CAGE diagnostic summary
All 2026-03-26 scans: NO papers/repos claiming runtime representation FORMAT expansion. Darwin Gödel Machine and Gödel Agent modify code content within fixed agent architecture. DéjàQ evolves problem distributions, not solution representations. Quality-diversity field remains focused on search efficiency within fixed representation formats.

## 2026-03-26 (Session 12 — Tier 2 Build)
- arxiv scanned: ~30, relevant: 5
- GitHub scanned: ~10, relevant: 2
- Cumulative: arxiv ~109, GitHub ~47

### arxiv highlights
- EvoLattice (2512.13857) — DEEPER_READ: DAG-based population with multi-alternative quality-diversity graph representations. Each node stores multiple persistent alternatives; every valid path = distinct candidate. CAGE: representation change for POPULATION STRUCTURE, not program format. Programs themselves are still standard code. NOT F_theo expansion of program expressibility.
- EvoX (2602.23413) — RELEVANT: Meta-evolution framework for automated discovery. Claims to outperform AlphaEvolve, OpenEvolve, ShinkaEvolve on majority of tasks. Uses meta-learned evolutionary strategies. CAGE: search algorithm improvement, not representation expansion.
- Self-Referential Meta-Learning (2212.14392, Kirsch & Schmidhuber) — RELEVANT: Neural networks that modify their own weights via learned self-referential update rules. Eliminates meta-optimizer. CAGE: self-modification within fixed neural network format. F_eff, not F_theo.
- MR-Search (2603.11327) — RELEVANT: Meta-reinforcement learning with self-reflection for agentic search. In-context learning. CAGE: behavioral modification, not representational.
- Grammar of ML Workflows (2603.10742, Roth 2026) — RELEVANT: Formal grammar specification for machine learning pipeline composition. Potentially relevant to operadic meta-grammar formalization (H.8).

### GitHub highlights
- reubenrowe/rags — RELEVANT: Tools for recursive adaptive grammars. Prolog-based. Implements Shutt-style adaptive grammars where production rules can be added/removed during parsing. Directly relevant to Mechanism 3 investigation. Small repo, no recent activity.
- jarble/adaptive_parser — RELEVANT: Simple adaptive parser in Prolog that learns new grammar rules from input. Demonstrates the concept but limited implementation.

### CAGE diagnostic summary
Session 12 scan confirms pattern: NO papers/repos claiming runtime representation FORMAT expansion for evolutionary program synthesis. EvoLattice is the closest — it changes the population representation format (from flat to DAG), but individual program representations are unchanged. The field remains focused on search efficiency (EvoX), population diversity (EvoLattice), and meta-learning (MR-Search) within fixed program formats.

## 2026-03-26 (DAILY_PATROL Day 1)
- arxiv scanned: ~45, new: 17, relevant: 6, deeper_read: 4, skipped(already read): 5
- GitHub scanned: ~15, new: 2, relevant: 0, skipped: 5
- Staleness: ~13% (5/~45 results already in read logs)
- Query evolution: none needed (staleness well below 70%)
- Blacklist variants found: 0
- Cumulative: papers ~42 logged, repos ~11 logged

### Key new papers
- **HyperAgents (2603.19461)** — DEEPER_READ: self-referential agents with metacognitive self-modification. Meta-agent edits its own improvement procedure. DGM-H implementation. Python code rewriting by frozen LLM.
- **SGM (2510.10232)** — RELEVANT: Statistical Gödel Machine. Replaces formal proofs with statistical confidence tests (e-values). Safety layer for recursive self-modification.
- **Bounded First-Class Universe Levels (2502.20485)** — DEEPER_READ: explicit syntax for bounded first-class universe levels in dependent type theory. Relevant to A.1.
- **Mechanizing Operads with Event-B (2512.16342)** — RELEVANT: formalizing operads for component-based system composition. Relevant to H.8.
- **Hypernetworks That Evolve Themselves (2512.16406)** — RELEVANT: hypernetworks modifying their own weight-generation process.
- **Parsing as lifting problem (2212.09060)** — DEEPER_READ: CFGs as operad functors. Mathematical connection between grammars and operads.

### CAGE diagnostic summary (Day 1)
HyperAgents is the most architecturally ambitious new find: metacognitive self-modification where the meta-level is also editable. However, deep read reveals CAGE: CLOSED — the frozen LLM is the true generator, Python is the fixed format, and all modifications are within the LLM's training distribution. This matches blacklist pattern B13 (all agents are LLMs = all recombination within training distribution). The "metacognitive" label describes a content-level change (the meta-agent's Python code gets rewritten) not a format-level change. SGM provides a safety mechanism for self-modification but does not expand what is expressible. The field continues to advance search efficiency and safety within fixed representation formats, with no papers claiming runtime FORMAT expansion.

## 2026-03-26 (DAILY_PATROL Day 2)
- arxiv scanned: ~60, new: 7, relevant: 1, deeper_read: 2, not_relevant: 4, skipped(already read): ~20
- GitHub scanned: ~15, new: 0, relevant: 0, skipped: ~8
- Staleness: ~33% (~20/~60 results already in read logs)
- Query evolution: none needed (staleness below 70%)
- Blacklist variants found: 0
- Cumulative: papers 57 logged, repos 19 logged

### New papers found
- **arxiv:2603.04010** "GAT for TT with Explicit Universe Polymorphism" (Bezem, Coquand, Dybjer, Escardó, LTT 2026) — DEEPER_READ: Generalized algebraic theories as initial models for level-indexed CwFs. Directly relevant to A.1 (IR transplant feasibility). Formalizes how universe polymorphism can be captured as initial model of a GAT, with level-indexed products and internally indexed universes.
- **arxiv:2603.04014** "Non-Derivability Results in Polymorphic Dependent Type Theory" (Geuvers) — DEEPER_READ: Shows parametric quotient types not definable in λP2, stream coinduction unavailable, induction requires function extensionality. Establishes hard limits of impredicative encodings.
- **arxiv:2603.20988** "Can we automatize scientific discovery in cognitive sciences?" — RELEVANT: States explicitly that "no search procedure can discover what the representation forbids." Task grammar expressibility bounds the discovery process. Directly echoes the RSI problem formulation.
- **arxiv:2603.18073** "Continually self-improving AI" (Yang) — NOT: Synthetic data + training algorithm search within fixed LM architecture. Content modification.
- **arxiv:2508.07932** "X-evolve" — NOT: Parametric program templates with score-based search. Fixed template format, variable parameters.
- **arxiv:2602.06511** "Evolutionary Generation of Multi-Agent Systems" — NOT: Survey of agent representation choices, no format expansion mechanism.

### Deep reads completed (Day 2 main work)

#### Deep Read 1: arxiv:2502.20485 — Bounded First-Class Universe Levels (Chan et al.)
FORMAL STRUCTURE EXTRACTION:
  Old format:      Prenex level polymorphism — definitions abstract over levels at top, monomorphized at call sites
  New format:      First-class levels — Level < ℓ is a type, level expressions are terms, level quantification subsumed by dependent Π
  Transition op:   Internalize level ordering into type system via bounded level types (Level < k)
  Became express.: Recursive definitions with level-varying recursive calls (e.g., incr : ∀k<ω. ℕ → 𝖴ω where incr k (succ n) = incr n [k+1]). Previously required monomorphization which fails for recursive level variation.
  Computable:      YES — explicit syntax given (TTBFL), semantic model via CwFs mechanized in Agda using induction-recursion
CAGE DIAGNOSIS:
  Layer affected:  FORMAT_CHANGE — levels become first-class terms, not just syntactic annotations
  Within-format:   NO — genuinely new: monomorphization provably fails for recursive level variation
BLACKLIST CHECK:  CLEAR — not a variant of B01-B14
TRANSPLANT SKETCH: Making grammar rule "levels" (meta-rule nesting depth, recursion depth) into first-class computable values in the RSI system. Currently max_depth is a fixed parameter. If depth became a first-class computable expression dependent on tree structure, trees could express depth-varying recursion. Requires: (1) depth type in ExprNode, (2) bounded depth quantification in grammar rules, (3) subject reduction proof for typing.
VERDICT: STRUCTURAL_EXPANSION — genuine FORMAT_CHANGE. The mechanism of internalizing meta-level parameters as first-class computable values is a well-understood type-theoretic technique with clear formal foundations.

#### Deep Read 2: arxiv:2212.09060 — Parsing as a Lifting Problem (Melliès & Zeilberger)
FORMAL STRUCTURE EXTRACTION:
  Old format:      CFG = tuple (Σ, N, S, P) with string rewriting rules
  New format:      CFG = functor of operads p: Free[S] → W[C] from free operad on species S into operad of spliced words
  Transition op:   Reinterpret productions as operad morphisms; parsing becomes computing fiber p⁻¹(w)
  Became express.: Grammars over arbitrary categories (not just free monoids), compositional parse trees via fibrational structure, Chomsky-Schützenberger theorem generalized to arbitrary categories
  Computable:      YES — constructive (inductive characterization of parse tree sets, Proposition 2.11)
CAGE DIAGNOSIS:
  Layer affected:  Layer 3 (grammar representation itself reformulated)
  Within-format:   The paper does not address grammar SELF-modification. The operadic framework provides a richer mathematical foundation for grammars but does not describe how a grammar could extend itself at runtime. The composition of spliced words (Proposition 2.9) enables hierarchical grammar assembly but this is a static operation.
BLACKLIST CHECK:  CLEAR
TRANSPLANT SKETCH: The operadic framework could formalize the meta-grammar layer: each meta-rule is an operation in an operad, meta-rule composition is operadic composition, and grammar expansion is extending the species S with new generators. This gives formal semantics to what the GrammarRuleComposer already does informally. However, this is a FORMALIZATION of existing capability, not an expansion of F_theo.
VERDICT: NO_STRUCTURE_FOUND for F_theo expansion. The operadic framework is a mathematical reformulation of existing grammar concepts. It provides better formal foundations but does not identify a mechanism for runtime format change. The grammar remains fixed once defined; only its LANGUAGE is explored, not its own structure.

#### Deep Read 3: arxiv:2512.16406 — Hypernetworks That Evolve Themselves (Self-Referential GHNs)
FORMAL STRUCTURE EXTRACTION:
  Old format:      Hypernetwork with fixed architecture generating policy parameters
  New format:      Self-referential hypernetwork: stochastic module takes own computational graph as input, outputs delta-parameters for offspring
  Transition op:   Self-referential weight generation: GHN(own_graph) → Δparams → offspring GHN
  Became express.: Adaptive mutation rates as heritable traits, emergent exploration-exploitation cycling
  Computable:      YES (implemented, evolutionary experiments on non-stationary tasks)
CAGE DIAGNOSIS:
  Layer affected:  Layer 2 (search strategy — mutation rate adaptation)
  Within-format:   YES — architecture is explicitly fixed. Only parameter values change. The paper states "fixed architectures" for both policy and GHN. The self-referential loop modifies content (weights) not format (architecture).
BLACKLIST CHECK:  Matches P05 partially ("more layers = more power" — self-referential nesting does not expand F_theo). Also resembles B12.14392 (Self-Referential Meta-Learning) — same fundamental approach (self-referential weight modification within fixed NN format).
TRANSPLANT SKETCH: Not applicable. Fixed architecture = fixed F_theo.
VERDICT: COMBINATORIAL_RECOMBINATION — content-level self-reference within fixed architecture. Adaptive mutation rates are F_eff (search efficiency), not F_theo (expressibility).

#### Deep Read 4: arxiv:2603.04010 — GAT for TT with Explicit Universe Polymorphism (Bezem et al., LTT 2026)
FORMAL STRUCTURE EXTRACTION:
  Old format:      Martin-Löf TT with external tower of universes (fixed hierarchy U₀ : U₁ : U₂ : ...)
  New format:      Level-indexed CwF with internal universe indexing and level-indexed products
  Transition op:   Initial model characterization — the type theory IS the initial model of its GAT. Universe polymorphism captured via level-indexed Π types.
  Became express.: Polymorphic definitions that quantify over universe levels internally, enabling uniform proofs across all levels without duplication
  Computable:      YES — Agda mechanization exists (referenced from Kovács' TTFL work using IR)
CAGE DIAGNOSIS:
  Layer affected:  FORMAT_CHANGE — the relationship between type theory and its models is formalized as an initial algebra, making the format itself algebraically characterizable
  Within-format:   The initial model characterization is a meta-level result about the type theory, not a mechanism within it. It tells us WHAT the type theory is (the initial model of a specific GAT) but does not provide a runtime mechanism for extending it.
BLACKLIST CHECK:  CLEAR — purely mathematical, no implementation variant
TRANSPLANT SKETCH: If the RSI system's grammar were characterized as the initial model of a GAT, then grammar extensions would correspond to GAT extensions (adding new sorts, operators, equations). This would formalize design space expansion as moving between initial models of progressively richer GATs. However, this is a mathematical characterization, not a computable procedure for generating the next GAT.
VERDICT: NO_STRUCTURE_FOUND for direct F_theo expansion mechanism. The paper provides deep mathematical foundations (initial model semantics for universe-polymorphic type theories) but does not identify a computable procedure for self-extension. The key insight — type theories AS initial models — is relevant for formalizing what "design space expansion" means mathematically, but does not provide the expansion operation itself.

### CAGE diagnostic summary (Day 2)
Day 2 deep reads confirm a pattern: the mathematical foundations for understanding representation FORMAT change are well-developed (first-class universe levels, operadic grammar semantics, initial model characterizations) but none provide a COMPUTABLE PROCEDURE for a system to extend its own format from within. The closest is Chan et al.'s TTBFL, where making levels first-class allows expressions that were previously inexpressible (recursive level variation). This is a genuine FORMAT_CHANGE in the type-theoretic sense. The transplant to the RSI system would involve making depth/meta-level parameters into first-class computable values rather than fixed integers. This is added to the candidate archive for future synthesis consideration.

Hypernetworks That Evolve Themselves (2512.16406) is confirmed CAGE: CLOSED — fixed architecture, content-only self-modification.

No new STRUCTURAL_EXPANSION candidates surviving all filters.

## 2026-03-26 (DAILY_PATROL Day 3)
- arxiv scanned: ~40, new: 5, relevant: 0, deeper_read: 4, not_relevant: 1, skipped(already read): ~15
- GitHub scanned: ~10, new: 0, relevant: 0, skipped: ~6
- Staleness: ~38% (~15/~40 results already in read logs)
- Query evolution: Evolved queries to follow citation chains (Kovács → TTBFL → BCDE → Dybjer/Setzer IR). Author-name searches productive.
- Blacklist variants found: 0
- Cumulative: papers 62 logged, repos 19 logged

### New papers found (citation chain following)
- **arxiv:2103.00223** "Generalized Universe Hierarchies and First-Class Universe Levels" (Kovács 2021) — DEEPER_READ: The PRIMARY SOURCE for first-class universe levels. IR used for transfinite hierarchies. Levels as first-class types subject to internal reasoning. Generalizes both Coq bounded polymorphism and Agda internal level computations.
- **arxiv:2212.03284** "Type Theory with Explicit Universe Polymorphism" (BCDE, revised) — DEEPER_READ: Precursor to 2603.04010. Higher-rank level polymorphism with level constraints. Subject reduction failure identified (fixed in TTBFL by bounded types).
- **arxiv:2402.15074** "Interpretation of Inaccessible Sets in MLTT with Mahlo Universe" — DEEPER_READ: Demonstrates Setzer's Mahlo universe suffices (without extra universe above) for interpreting CZF + inaccessible sets. Agda formalization. Accessibility predicate as substitute.
- **Dybjer-Setzer 1999** "A Finite Axiomatization of Inductive-Recursive Definitions" (TLCA) — DEEPER_READ (PRIMARY SOURCE): IR definitions modeled as initial algebras in slice categories. Generic formation, introduction, elimination, equality rules. The finite axiomatization demonstrates IR can be captured by finitely many schematic rules. Key for understanding whether IR provides a computable grammar extension procedure.
- **arxiv:2506.10943** "Self-Adapting Language Models" — NOT: Weight updates from agent interactions, content modification within fixed LM format.

### Deep reads completed (Day 3 main work)

#### Deep Read 1: arxiv:2603.04014 — Non-Derivability in Polymorphic Dependent Type Theory (Geuvers)
FORMAL STRUCTURE EXTRACTION:
  Old format:      λP2 (polymorphic second-order dependent type theory) with impredicative encodings
  New format:      λP2 + Sigma-types + identity types + function extensionality
  Transition op:   Adding structural axioms (Sigma, Id, funext) to enable induction
  Became express.: Natural number induction, stream coinduction, parametric quotient types with induction
  Computable:      YES (standard extensions, implemented in proof assistants)
CAGE DIAGNOSIS:
  Layer affected:  FORMAT_CHANGE — each extension adds genuinely new derivation power
  Within-format:   NO — proven non-derivable in base system. No encoding trick can substitute.
BLACKLIST CHECK:  CLEAR
KEY INSIGHT FOR RSI: Geuvers proves that ENCODING cannot substitute for STRUCTURAL EXTENSION. Induction is not derivable from impredicativity alone. This directly parallels the RSI problem: you cannot encode design space expansion within a fixed grammar — you need structural grammar extensions. This confirms the theoretical foundation of the Protocol: content modification within fixed format cannot achieve what format extension achieves.
TRANSPLANT SKETCH: Not directly transplantable as a mechanism. Instead, it validates the theoretical framework: the RSI system's grammar IS the "type system," and adding new grammar rules (meta-rules) IS the analogue of adding Sigma/Id/funext to λP2. The question is whether the meta-grammar layer can generate the RIGHT extensions — not whether extensions help (they provably do).
VERDICT: NO_STRUCTURE_FOUND for a new mechanism, but CONFIRMS the theoretical framework. Non-derivability results provide formal backing for why content modification within fixed format is insufficient.

#### Deep Read 2: Kovács 2021 — Generalized Universe Hierarchies (arxiv:2103.00223)
Key contribution: IR is the semantic machinery for transfinite universe hierarchies. First-class levels enable arbitrary internal reasoning about universe membership. The relationship: IR provides the MODEL THEORY, first-class levels provide the SYNTAX.
For RSI: Kovács shows that IR-based models can support arbitrarily large hierarchies without ad-hoc extensions. The model grows by IR construction, not by external fiat. However, the GROWTH PROCEDURE is fixed at the meta-level (the IR schema is chosen once). The system does not modify its own IR schema.
VERDICT: FORMALIZATION — deep mathematical foundations, no self-extension mechanism.

#### Deep Read 3: Dybjer-Setzer 1999 — Finite Axiomatization of IR
Key contribution: IR definitions can be captured by finitely many schematic rules. The axiomatization has:
  - Formation rule: how to form a new IR type from codes
  - Introduction rule: how to construct elements
  - Elimination rule: how to pattern-match
  - Equality rule: computation behavior
These are GENERIC — they work for any IR definition, not just specific ones.
For RSI: The finite axiomatization means that if the RSI system could internalize the IR schema, it would have a GENERIC mechanism for creating new types (new grammar rules with mutual dependencies). However:
  (a) The IR schema itself is fixed — you choose it once
  (b) The system would need a meta-meta-level to modify the IR schema
  (c) This is exactly the infinite regress problem: who modifies the modifier?
VERDICT: NO_STRUCTURE_FOUND for self-extension. The finite axiomatization is powerful but static. It does not provide a procedure for a system to extend its own axiomatization.

### Isomorphism analysis: Candidate 8 (First-Class Depth)
RESULT: **ISOMORPHIC** at unlimited resources.
Reasoning: ExprNode trees are FINITE expression trees, not recursive programs. First-class depth in a non-recursive language just selects which fixed depth to use — every such tree is equivalent to some fixed-depth tree. The FORMAT_CHANGE from TTBFL is only genuine when the language supports recursive definitions with level-varying calls. ExprNode trees lack recursion.
COROLLARY: First-class depth becomes genuinely new ONLY when combined with recursive evaluation (self_encode + depth-varying recursion). This combination is noted as potential Candidate 8b.
Candidate 8 reclassified: F_EFF_GAIN_UNDER_CONSTRAINT → ISOMORPHIC.

### CAGE diagnostic summary (Day 3)
Day 3 establishes a critical theoretical result via Geuvers' non-derivability theorem: encoding within a fixed format PROVABLY cannot substitute for structural extension. This validates the Protocol's core premise. The IR literature (Kovács, Dybjer-Setzer) provides the mathematical tools for understanding grammar extension as type formation, but none of these tools provide a SELF-EXTENSION mechanism — they all require external choice of the IR schema.

The infinite regress problem remains: any meta-level that can modify the grammar is itself a fixed level. Modifying the meta-level requires a meta-meta-level, ad infinitum. This is consistent with the theoretical prediction that genuine F_theo expansion from within a closed system may be impossible.

Candidate 8 is reclassified as ISOMORPHIC. No new candidates added. The field of type theory provides formal confirmation of WHY the problem is hard, but not a solution.
