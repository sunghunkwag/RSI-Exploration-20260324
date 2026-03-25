# Domain C — Ancient Texts, Manuscripts & Historical Linguistics

**Session 3 | Date: 2026-03-25 | Status: COMPLETE**

---

## C.1 — Pāṇinian Grammar: Pratyāhāra, Paribhāṣā & Kāraka

### SOURCE
Pāṇini, *Aṣṭādhyāyī* (~4th century BCE), ~4000 sūtras.
Rajpopat (2022), "In Pāṇini We Trust: Discovering the Algorithm for Rule Conflict Resolution in the Aṣṭādhyāyī," PhD thesis, Cambridge.
Kiparsky (1979), "Pāṇini as a Variationist."
Staal (1962), "A Method of Linguistic Description."

### FORMAL STRUCTURE EXTRACTION

#### C.1a — Pratyāhāra (Interval-Indexed Phoneme Classes)

**Old format:** Explicit enumeration of phoneme classes. Each rule that references a set of phonemes must list them individually. No compression mechanism. If a rule applies to {a, i, u, ṛ, ḷ}, it must name all five. Phoneme set descriptions are O(n) in set size.

**New format:** The Śiva-sūtras define a linear ordering of phonemes with embedded *anubandha* (index markers): `a i u Ṇ | ṛ ḷ K | e o Ṅ | ai au C | ...`. A pratyāhāra is a pair (start_phoneme, end_marker) denoting the interval — e.g., "aC" = {a, i, u, ṛ, ḷ, e, o, ai, au}. Any contiguous subset in the Śiva-sūtra ordering can be named in O(1) by a two-symbol code.

**Transition op:** (1) Fix a linear ordering of all phonemes with strategically placed index markers. (2) For any phoneme set S, find the minimal interval [p, M] in the ordering such that S ⊆ interval(p, M). (3) Replace enumerated set with pratyāhāra code "pM". The ordering is optimized so that linguistically natural classes align with contiguous intervals (this is the key design achievement — 14 Śiva-sūtras compress ~300 phoneme-class references across 4000 rules).

**Became expressible:** O(1) reference to any phoneme class that aligns with a contiguous interval. Cross-rule consistency enforced by shared ordering. Novel: classes that are *supersets* of intended groups are also nameable, enabling controlled over-generation for productivity. Previously inexpressible: implicit phoneme class relationships (if aC ⊃ aṆ, the containment is visible from the ordering).

**Computable:** YES — Interval lookup is O(1). Ordering construction is a finite combinatorial optimization (NP-hard in general but the Śiva-sūtra ordering is fixed and small).

#### C.1b — Paribhāṣā (Meta-Rules for Conflict Resolution)

**Old format:** Flat, unordered rule set. When multiple rules match the same input, conflict is resolved ad hoc or by arbitrary convention. Rule interaction is unpredictable as the grammar grows.

**New format:** Hierarchical rule system with explicit meta-rules (paribhāṣās) that determine which rule fires when multiple rules match. Key paribhāṣā types: (1) *vipratiṣedhe paraṁ kāryam* (1.4.2) — "in conflict, the later rule prevails" (default specificity ordering), (2) Rajpopat's 2022 discovery: the *actual* Pāṇinian algorithm selects the rule whose *operand* (right-hand side trigger) is more specific (SOI — Scope of the Operand over DOI — Scope of the Operator), yielding deterministic derivation with <1% exception rate across all 4000 sūtras.

**Transition op:** (1) Index all rules by their triggering context. (2) When conflict arises between rules R₁ and R₂, compute scope of operand for each. (3) Select the rule with the narrower operand scope. (4) Apply selected rule; continue derivation. The meta-rule system transforms a non-deterministic grammar into a deterministic one without modifying any individual rule.

**Became expressible:** Deterministic derivation from non-deterministic specification. Predictable rule interaction without per-case patches. Modular rule addition (new rules inherit conflict resolution automatically). The meta-rule system makes the grammar *compositional* in a way the flat rule set is not.

**Computable:** YES — Operand scope comparison is syntactic (decidable). Rajpopat's algorithm is O(k) where k = number of conflicting rules at a derivation step.

#### C.1c — Kāraka (Semantic Role Abstraction Layer)

**Old format:** Direct surface-form to meaning mapping. Each morphological form maps directly to a semantic interpretation. No intermediate representation.

**New format:** Six kāraka roles (Apādāna, Sampradāna, Karaṇa, Adhikaraṇa, Karma, Kartṛ) form an intermediate semantic layer between surface syntax and meaning. Surface forms map to kārakas; kārakas map to semantic roles. The kāraka layer provides a stable interface that decouples syntax from semantics.

**Transition op:** (1) Parse surface form to identify case markers. (2) Map case markers to kāraka roles via vibhakti rules. (3) Map kāraka roles to semantic interpretation via kāraka-to-meaning rules. The two-stage mapping allows many-to-many relationships: one surface form can express multiple kārakas (contextually), and one kāraka can be realized by multiple surface forms.

**Became expressible:** Context-dependent interpretation (same surface form → different meaning via different kāraka assignment). Cross-linguistic semantic transfer (kārakas abstract over language-specific morphology). Compositional semantics with intermediate abstraction.

**Computable:** YES — Both mapping stages are finite table lookups with contextual disambiguation rules.

### CAGE DIAGNOSIS

**Layer affected:** Layer 2 (Grammar) — pratyāhāra compresses vocabulary addressing; paribhāṣā adds deterministic conflict resolution to GrammarLayer; kāraka adds intermediate representation layer.
**Within-format:** Pratyāhāra = COMBINATORIAL_RECOMBINATION (compression, not expansion). Paribhāṣā = STRUCTURAL_EXPANSION (transforms non-deterministic rule application into deterministic — this changes which derivations are reachable). Kāraka = STRUCTURAL_EXPANSION (intermediate abstraction layer enables compositions unreachable by direct surface-to-meaning mapping).

### TRANSPLANT SKETCH

**Pratyāhāra → ExprNode:** Define a canonical ordering on PrimitiveOps with index markers. Grammar rules reference operator classes via interval codes rather than explicit sets. Reduces rule proliferation in MetaGrammarLayer. Implementation: `VocabularyLayer.pratyahara_ordering` + `PrimitiveOp.class_code(start, marker)`.

**Paribhāṣā → ExprNode:** When multiple GrammarLayer rules match during tree construction, resolve via operand-specificity: the rule whose triggering context is more specific (narrower type signature) wins. Currently, MetaGrammarLayer selects rules randomly (50% probability each). Replace with: `GrammarLayer.resolve_conflict(rules, context) → rule` using operand scope comparison. This makes expansion deterministic and compositional.

**Kāraka → ExprNode:** Add an intermediate "semantic role" layer between ExprNode structure and evaluation. Each subtree is assigned a kāraka-like role tag (e.g., SOURCE, TARGET, INSTRUMENT, LOCUS) that mediates between structural position and computational interpretation. This decouples tree structure from evaluation semantics, enabling the same structural pattern to compute differently based on role assignment.

### VERDICT: STRUCTURAL_EXPANSION (paribhāṣā, kāraka) + COMBINATORIAL_RECOMBINATION (pratyāhāra)

---

## C.2 — Hebrew Binyanim: Morphological Operator Algebra

### SOURCE
Gesenius, *Hebrew Grammar* (Kautzsch edition, 1910).
Waltke & O'Connor, *An Introduction to Biblical Hebrew Syntax* (1990).
Aronoff (1994), *Morphology by Itself*.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Single verb root (typically triconsonantal, e.g., k-t-b "write") with one voice/valence interpretation. Each root has a fixed argument structure. No systematic mechanism to derive causative, reflexive, intensive, or passive variants.

**New format:** Seven binyanim (Qal, Niph'al, Pi'el, Pu'al, Hiph'il, Hoph'al, Hithpa'el) as morphological operators applied to consonantal roots. Each binyanim is a fixed vowel-pattern + prefix/suffix template that transforms argument structure:
- Qal: base (transitive or intransitive)
- Niph'al: passive/reflexive of Qal
- Pi'el: intensive/causative
- Pu'al: passive of Pi'el
- Hiph'il: causative
- Hoph'al: passive of Hiph'il
- Hithpa'el: reflexive/reciprocal

The system is a finite algebra: 7 operators × root inventory = verb lexicon.

**Transition op:** Apply binyan template B to root R: (1) Extract consonantal skeleton from R. (2) Interleave with B's vowel pattern and affixes. (3) Assign B's argument-structure transformation to the result. Example: root k-t-b + Hiph'il template → hiktīb "caused to write" (added causer argument).

**Became expressible:** Systematic derivation of causative, passive, reflexive, intensive, and reciprocal forms from any root. Predictable argument-structure transformations. Previously: each derived form would require a separate lexical entry.

**Computable:** YES — Template application is string interleaving (O(n) in root length). Argument structure transformation is a fixed finite map.

### CAGE DIAGNOSIS

**Layer affected:** Layer 1 (Vocabulary) — expands verb inventory via fixed operators.
**Within-format:** YES — The binyanim are a closed, non-composing set. Critically: **binyanim do not compose with each other.** You cannot apply Hiph'il to a Pi'el form to get a "causative-intensive." The system is flat, not recursive. This is unlike ExprNode composition, which is recursive and unbounded. The binyanim system is a finite expansion of Layer 1 that does not change the compositional structure.

**Additional note:** Fossilized traces of higher-layer activity exist (Pilpel, Polel — reduplicated forms suggesting historical productivity beyond the 7-binyan system), but these are lexicalized fossils, not active compositional mechanisms.

### TRANSPLANT SKETCH

Define 7 fixed "morphological operators" in VocabularyLayer, each a unary transformation on PrimitiveOp semantics: `PASSIVE(op)`, `CAUSATIVE(op)`, `INTENSIVE(op)`, `REFLEXIVE(op)`, etc. These produce new PrimitiveOps from existing ones with predictable semantic transformations. Unlike MetaGrammarLayer's random composition, binyan operators have fixed, interpretable semantics. Implementation: `VocabularyLayer.apply_binyan(op, binyan_type) → PrimitiveOp`.

Useful for vocabulary enrichment but does not expand F_theo (the resulting operators are expressible as explicit unary wrappers in the current system).

### VERDICT: COMBINATORIAL_RECOMBINATION

---

## C.3 — Aramaic Polysemy: Context-Dependent Type Resolution

### SOURCE
Sokoloff, *A Dictionary of Jewish Palestinian Aramaic* (2002).
Jastrow, *A Dictionary of the Targumim, the Talmud Babli and Yerushalmi* (1903).
Cook, "Aramaic Language and the Study of the New Testament," *JGRCHJ* (2008).

### FORMAL STRUCTURE EXTRACTION

**Old format:** Monomorphic word-to-meaning binding. Each lexical item has a single type. Word W maps to meaning M₁. If W also means M₂ in different context, this is handled by listing W twice as separate lexical entries (homonymy approach) — no systematic mechanism for context-dependent resolution.

**New format:** Polymorphic lexical entries with context-dependent type resolution. Word W maps to a function set {f₁: Context₁ → M₁, f₂: Context₂ → M₂, ...}. A dispatcher selects the appropriate function based on contextual features (syntactic frame, semantic domain, register, discourse position). The word is a single entry with multiple typed facets.

**Transition op:** (1) Collect all attested meanings {M₁, ..., Mₖ} of polysemous word W across corpus. (2) For each meaning Mᵢ, identify the contextual feature set Cᵢ that selects it. (3) Construct dispatcher D: Context → {1, ..., k} that maps context features to meaning index. (4) Replace monomorphic entry W → M with polymorphic entry W → {(C₁, M₁), ..., (Cₖ, Mₖ)} + D.

**Became expressible:** Single lexical entry serving multiple type roles. Dynamic meaning selection based on compositional context. Semantic coercion (context forces meaning shift). Previously: required separate entries for each meaning, losing the systematic relationship between senses.

**Computable:** YES — Dispatcher is a finite decision function over enumerated contextual features. Context feature extraction is syntactic (parseable). In practice, Aramaic lexicography uses this exact structure.

### CAGE DIAGNOSIS

**Layer affected:** Layer 1 (Vocabulary) + FORMAT_CHANGE
**Within-format:** NO — ExprNode currently evaluates PrimitiveOps as fixed functions (each op has one `func` attribute). Context-dependent dispatch requires: (1) a function set per op (not single function), (2) a dispatcher mechanism, (3) context threading through evaluation. None of these exist in the current format. This is a genuine format change.

### TRANSPLANT SKETCH

Extend PrimitiveOp to hold a function set rather than a single function:
```python
class PolymorphicOp(PrimitiveOp):
    func_set: Dict[ContextType, Callable]
    dispatcher: Callable[[EvalContext], ContextType]
```

During `_eval_tree`, thread an `EvalContext` object that accumulates contextual information (parent node type, sibling types, depth, archive statistics). When evaluating a PolymorphicOp, the dispatcher selects the appropriate function from func_set based on EvalContext.

This enables:
- Same primitive computing differently based on position in tree (kāraka-like)
- Adaptive behavior without tree modification
- Context-sensitive evaluation expanding F_theo: a tree with polymorphic ops can express functions that require different behavior at different call sites — impossible with current monomorphic PrimitiveOps

### VERDICT: STRUCTURAL_EXPANSION

---

## C.4 — Cuneiform Sign Evolution: Monomorphic-to-Polymorphic Transition

### SOURCE
Nissen, Damerow & Englund, *Archaic Bookkeeping* (1993).
Schmandt-Besserat, *Before Writing* (1992).
Civil (2008), "The Early Dynastic Practical Vocabulary A."
Taylor (2015), "Sumerian Writing," in *The Oxford Handbook of Cuneiform Culture*.

### FORMAL STRUCTURE EXTRACTION

**Old format:** Proto-cuneiform archaic signs (~3400 BCE). One sign = one concept (monomorphic). The sign for "sheep" means only "sheep." No phonetic values, no polyvalence. The system is logographic: sign inventory = concept inventory. Adding a new concept requires inventing a new sign.

**New format:** Mature cuneiform (~2600 BCE onward). Each sign carries multiple values: (1) logographic (SHEEP = "sheep"), (2) syllabic (SHEEP = /lu/ in phonetic context), (3) determinative (SHEEP as classifier prefix, e.g., before animal names). Signs become polymorphic: one sign maps to {logographic_value, syllabic_values[], determinative_role}. Context (position, adjacent signs, determinative markers) selects the active value.

**Transition op:** The *rebus principle* drives the transition: (1) Observe that sign for concept C₁ is pronounced /p/. (2) Reuse sign for concept C₁ to represent sound /p/ in writing concept C₂ (which contains /p/ in its pronunciation). (3) The sign now has both logographic value C₁ and syllabic value /p/. (4) Add determinative signs (semantic classifiers) to disambiguate: determinative + sign = logographic reading; no determinative + sign = syllabic reading.

**Became expressible:** Phonetic representation (sounds, not just concepts). Abstract and grammatical words (which have no pictographic representation). Foreign words and names. Previously inexpressible grammatical morphemes (case markers, verb tenses). The sign inventory becomes finite while the expressible language becomes infinite (via phonetic combination).

**Computable:** YES — Rebus transfer is a finite mapping. Determinative classification is a lookup table. The key insight: the transition from finite-concept to infinite-expression system is achieved by adding a second interpretation layer (phonetic), not by expanding the sign inventory.

### CAGE DIAGNOSIS

**Layer affected:** Layer 1 (Vocabulary) + Layer 2 (Grammar) + FORMAT_CHANGE
**Within-format:** NO — The format changes fundamentally: from {sign → concept} to {sign → {concept, sound, classifier}}. The monomorphic system cannot express phonetic combinations regardless of how many signs are added. The addition of the phonetic interpretation layer is a genuine format change that makes the system compositionally productive.

### TRANSPLANT SKETCH

The cuneiform evolution parallels the C.3 polysemy transplant but adds a crucial element: **determinatives as type annotations**. In ExprNode terms:

1. Allow PrimitiveOps to carry multiple interpretation functions (as in C.3 polysemy).
2. Add "determinative" nodes — lightweight type-annotation nodes that don't compute but constrain interpretation of adjacent nodes.
3. During `_eval_tree`, determinative nodes set the interpretation mode for their subtree.

Implementation:
```python
class DeterminativeNode(ExprNode):
    """Type annotation node — selects interpretation mode for children."""
    mode: str  # e.g., "numeric", "symbolic", "structural"
```

This combines with C.3 to form a complete context-dependent evaluation system. The cuneiform lesson: the transition from finite to infinite expressibility comes from adding an interpretation layer, not from expanding the primitive inventory.

### VERDICT: STRUCTURAL_EXPANSION

---

## C.5 — Dead Sea Scrolls: Textual Variation as Multi-Layer Mutation

### SOURCE
Tov, *Textual Criticism of the Hebrew Bible* (4th ed., 2022).
Ulrich, *The Dead Sea Scrolls and the Origins of the Bible* (1999).
Cross, "The Evolution of a Theory of Local Texts," *Qumran and the History of the Biblical Text* (1975).

### FORMAL STRUCTURE EXTRACTION

**Old format:** Single textual tradition (e.g., Masoretic Text as "the" Hebrew Bible). Variations treated as errors to be corrected. No systematic framework for understanding variant relationships.

**New format:** Multiple parallel textual traditions (MT, LXX Vorlage, Samaritan Pentateuch, Qumran sectarian texts) understood as a population of variants with classified mutation types:

- **Layer 1 mutations (Vocabulary):** Lexical substitution (synonym replacement), vocabulary loss/gain. Example: Isaiah 53:11 — 1QIsaᵃ adds אור ("light") absent from MT. Single-primitive change.
- **Layer 2 mutations (Grammar):** Word boundary resegmentation, syntactic reanalysis. Example: 1 Samuel 14:30 — consonantal text אף כי allows two parsings: "how much more" (MT) vs. "indeed" (4QSamᵃ), yielding different clause structures from identical character sequence.
- **Layer 3 mutations (Meta-Grammar):** Interpretive framework shifts. Example: 1QS (Community Rule) — "Teacher of Righteousness" passages reframe prophetic texts within an eschatological interpretive grammar, changing which derivations are licensed from the base text.

**Transition op:** Each mutation type has a distinct transition operation:
- L1: lexical substitution σ: word → word (preserves syntax)
- L2: resegmentation ρ: character_sequence → parse_tree (same characters, different structure)
- L3: framework shift φ: interpretive_grammar → interpretive_grammar (same text, different licensed derivations)

**Became expressible:** L1: new semantic content (אור in Isa 53:11). L2: alternative syntactic structures from identical input (genuine ambiguity formalization). L3: new interpretive derivations from unchanged source material. The DSS demonstrate that all three CAGE layers can be independently mutated, and that L2 and L3 mutations can expand expressibility without changing the base vocabulary.

**Computable:** YES — L1 substitution is trivially computable. L2 resegmentation requires exhaustive parse over character sequence (exponential in worst case, polynomial for natural language with bounded ambiguity). L3 framework shift is a grammar replacement operation.

### CAGE DIAGNOSIS

**Layer affected:** All three layers demonstrated independently.
**Within-format:** L1 = YES (vocabulary substitution is within-format). L2 = BORDERLINE (resegmentation reveals latent structure in existing representation — the characters were already there, but the grammar couldn't see the alternative parse). L3 = NO (framework shift changes which derivations are possible — this is a meta-grammar change).

### TRANSPLANT SKETCH

The DSS classification of mutation types maps directly to the CAGE layer framework, providing concrete mutation operators for each layer:

**L1 (Vocabulary mutation):** Already implemented — `VocabularyLayer.add_operation()` adds new primitives. Library learning extracts new ops from subtrees.

**L2 (Resegmentation / reparse):** NEW — Given an ExprNode tree, re-parse its serialized form under alternative grammar rules to discover alternative tree structures encoding the same "character sequence" (primitive sequence at leaves). Implementation: `GrammarLayer.resegment(tree) → [alternative_trees]`. This is a genuine expansion: it finds trees that were latent in the existing representation but invisible under the current parse.

**L3 (Framework shift):** Partially implemented via MetaGrammarLayer rule addition. Full transplant: `MetaGrammarLayer.shift_framework(old_rules, archive_state) → new_rules` — wholesale replacement of active grammar rules based on population characteristics (connects to A.3 Adaptive Grammars).

### VERDICT: STRUCTURAL_EXPANSION (L2 resegmentation, L3 framework shift) + COMBINATORIAL_RECOMBINATION (L1 vocabulary mutation)

---

## C.6 — Script Evolution: Logographic → Syllabic → Alphabetic Transitions

### SOURCE
Daniels & Bright, *The World's Writing Systems* (1996).
Gelb, *A Study of Writing* (1952, revised 1963).
Sampson, *Writing Systems* (2nd ed., 2015).
Gnanadesikan, *The Writing Revolution* (2009).

### FORMAL STRUCTURE EXTRACTION

**Old format (Logographic):** Each sign represents one morpheme/word. Sign inventory ≈ morpheme inventory. System is expressively complete (can represent any word) but has combinatorial explosion: thousands of signs required, each independently learned.

**New format (Alphabetic):** Each sign represents one phoneme (~20-30 signs). Words are composed by concatenation. Sign inventory is minimal; expressibility is achieved compositionally. Intermediate stage (Syllabic): each sign represents one syllable (~50-200 signs).

**Transition operations (three historical transitions):**

1. **Logographic → Syllabic (Rebus principle):** Same as C.4. Signs are reinterpreted as sound-units rather than meaning-units. Key: this is a *re-interpretation* of existing signs, not creation of new ones. The sign inventory stays the same; the interpretation grammar changes.

2. **Syllabic → Alphabetic (Decomposition):** Syllable signs CV are analyzed into onset C + nucleus V. The consonantal alphabet (abjad) emerges by extracting the onset: {CV₁, CV₂, ...} → {C}. Vowels are initially unwritten (abjad stage: Phoenician, Hebrew, Arabic) then optionally or mandatorily added (alphabet stage: Greek, Latin). Transition: for each syllabic sign, extract the initial consonant; merge all signs sharing the same initial consonant into one alphabetic sign.

3. **Abjad ↔ Alphabet (Vowel projection/extension):** Abjad (consonants only) → Alphabet (consonants + vowels) by: (a) repurposing unused consonant signs as vowel signs (Greek used Phoenician signs for sounds absent in Greek as vowel letters), or (b) adding diacritics (Hebrew niqqud, Arabic ḥarakāt). Reverse: Alphabet → Abjad by projection (drop vowel information).

**Became expressible at each stage:**
- Logographic → Syllabic: phonetic representation, grammatical morphemes, foreign words (as in C.4). Expressibility transitions from finite to infinite.
- Syllabic → Alphabetic: phonemic distinctions (minimal pairs), more efficient encoding, easier learnability. Not strictly more expressive, but exponentially more *efficient* — any syllabary-expressible word is alphabet-expressible, but the alphabet achieves this with 20-30 signs instead of 200.
- Abjad → Alphabet: vowel distinctions become explicit. Some distinctions expressible in speech but ambiguous in abjad become unambiguous.

**Computable:** YES — All transitions are finite mappings (reinterpretation, decomposition, projection). Each is reversible or partially reversible.

### CAGE DIAGNOSIS

**Layer affected:** Transition 1 (logo→syllabic): FORMAT_CHANGE (Layer 1+2). Transition 2 (syllabic→alphabetic): Layer 1 compression (COMBINATORIAL_RECOMBINATION in expressibility, major efficiency gain). Transition 3 (abjad↔alphabet): Layer 1 extension/projection.

**Within-format:** Transition 1 = NO (fundamental reinterpretation of sign semantics). Transition 2 = YES for expressibility (same F_theo, much better F_eff). Transition 3 = BORDERLINE (abjad→alphabet adds explicit vowel distinctions, marginal F_theo expansion).

### TRANSPLANT SKETCH

**Meta-pattern: each script transition trades economy for compositionality/transparency.** The alphabetic principle is: decompose complex units into minimal compositional atoms, accept longer representations in exchange for smaller inventory and greater compositionality.

Applied to ExprNode:

1. **Rebus/reinterpretation (Transition 1):** Allow existing PrimitiveOps to be reinterpreted in new contexts (connects to C.3 polysemy, C.4 cuneiform). The "phonetic" interpretation of a PrimitiveOp is its structural role in composition, not its standalone semantics.

2. **Decomposition (Transition 2):** Analyze compound PrimitiveOps into sub-atomic components. Currently, LibraryLearner *composes* subtrees into new primitives (coarse-graining / Wilson RG direction). The reverse operation — *decomposing* primitives into smaller reusable atoms — is the alphabetic transition. Implementation: `VocabularyLayer.decompose(op) → [sub_ops]` where sub_ops are more atomic and more reusable. This is the inverse of library learning.

3. **Projection/Extension (Transition 3):** Define projection operators that strip information from ExprNode representations (lossy compression) and extension operators that add information channels. Example: project a tree to its shape (ignore leaf values) or extend a tree with type annotations.

**Key insight for RSI:** The system currently only moves in the coarse-graining direction (library learning / Wilson RG). The alphabetic decomposition provides the reverse direction: fine-graining. A system that can both coarse-grain AND fine-grain can navigate the abstraction hierarchy bidirectionally. This is a genuine capability expansion.

### VERDICT: STRUCTURAL_EXPANSION (Transition 1 reinterpretation) + COMBINATORIAL_RECOMBINATION (Transition 2 decomposition for F_eff, not F_theo) + BORDERLINE (Transition 3)

---

## Cross-Domain Patterns (Domain C)

### Pattern 1: Context-Dependent Evaluation is the Dominant Expansion Mechanism
C.1c (kāraka), C.3 (Aramaic polysemy), and C.4 (cuneiform polyvalence) all point to the same structural expansion: **making evaluation context-dependent**. Current ExprNode evaluation is context-free — each node computes the same function regardless of position. Adding context threading + polymorphic ops + determinative type annotations would be a single coherent FORMAT_CHANGE with high impact across all three sub-topics.

### Pattern 2: Bidirectional Abstraction (Coarse-Graining + Fine-Graining)
C.6 (script evolution) reveals that the RSI system currently only moves in one direction on the abstraction hierarchy (coarse-graining via library learning). The alphabetic decomposition principle provides the reverse: fine-graining compound operators into reusable atoms. A bidirectional system can navigate the full abstraction landscape.

### Pattern 3: Deterministic Conflict Resolution Enables Compositional Growth
C.1b (paribhāṣā) shows that deterministic conflict resolution is prerequisite for compositional growth. Random rule selection (current MetaGrammarLayer behavior) prevents reliable composition. Specificity-based resolution would make grammar expansion deterministic and predictable.

### Pattern 4: Resegmentation as Latent Structure Discovery
C.5 (DSS Layer 2 mutations) demonstrates that re-parsing existing representations under alternative grammars can reveal latent structure. This is a "zero-cost" expansion: no new primitives or rules needed, just alternative parsing of existing trees.

---

## Summary Statistics

| Sub-topic | Verdict | Layers | Format Change |
|-----------|---------|--------|---------------|
| C.1a Pratyāhāra | COMBINATORIAL_RECOMBINATION | L2 | No |
| C.1b Paribhāṣā | STRUCTURAL_EXPANSION | L2 | No |
| C.1c Kāraka | STRUCTURAL_EXPANSION | L2 | Partial |
| C.2 Binyanim | COMBINATORIAL_RECOMBINATION | L1 | No |
| C.3 Aramaic polysemy | STRUCTURAL_EXPANSION | L1+FORMAT | Yes |
| C.4 Cuneiform evolution | STRUCTURAL_EXPANSION | L1+L2+FORMAT | Yes |
| C.5 DSS variants | STRUCTURAL_EXPANSION (L2,L3) | L1+L2+L3 | Partial |
| C.6 Script evolution | STRUCTURAL_EXPANSION (T1) | L1+L2+FORMAT | Partial |

**Totals:** 8 sub-topics investigated, 8 formal extractions completed.
- STRUCTURAL_EXPANSION: 5 (C.1b, C.1c, C.3, C.4, C.5)
- Mixed (STRUCTURAL + COMBINATORIAL): 1 (C.6)
- COMBINATORIAL_RECOMBINATION: 2 (C.1a, C.2)
- NO_STRUCTURE_FOUND: 0

**Strongest cage-breaking candidates:**
1. **Context-dependent evaluation** (C.3 + C.4 + C.1c combined) — unified FORMAT_CHANGE adding polymorphic ops, context threading, and determinative type annotations
2. **Resegmentation** (C.5 L2) — re-parsing existing trees under alternative grammars to discover latent structure
3. **Paribhāṣā conflict resolution** (C.1b) — deterministic specificity-based rule selection replacing random expansion
4. **Bidirectional abstraction** (C.6) — adding fine-graining (decomposition) as inverse of library learning (coarse-graining)
