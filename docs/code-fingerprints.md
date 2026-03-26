# Code Fingerprints

## Format
[YYYY-MM-DD] filename.py
  Classes: [list]
  Key methods: [list]
  Core structures: [list]
  Search mechanism: [type]
  F_theo claim: [description]
  Verdict: [GENUINE_NEW / VARIANT_OF_BXX / REJECTED_DUPLICATE]

## Entries

[2026-03-24] main.py (LibraryLearner)
  Classes: LibraryLearner
  Key methods: extract_library, _subtree_fingerprint, _extract_subtrees
  Core structures: ExprNode tree, subtree frequency table, PrimitiveOp vocabulary
  Search mechanism: Frequency-based subtree extraction (DreamCoder-style)
  F_theo claim: Depth ceiling bypass — extracted depth-K subtree as single primitive allows depth-D tree to express depth D+K computations
  Verdict: GENUINE_NEW

[2026-03-25] main.py (Self-Reference / self_encode)
  Classes: EvalContext (dataclass)
  Key methods: _eval_tree (self_encode branch), fingerprint()
  Core structures: ExprNode with self_encode PrimitiveOp, EvalContext.self_fingerprint
  Search mechanism: Fixed-point self-reference (Kleene recursion theorem)
  F_theo claim: GENUINE_F_THEO_EXPANSION — trees compute functions of their own identity
  Verdict: GENUINE_NEW (but reimplementation of known theory)

[2026-03-25] main.py (Context-Dependent / PolymorphicOp)
  Classes: PolymorphicOp (dataclass), EvalContext
  Key methods: _eval_tree (PolymorphicOp dispatch), context_key(), _meta_create_polymorphic_op
  Core structures: dispatch_table Dict[int, Callable], context key hashing
  Search mechanism: Context-dependent dispatch on niche_id/env_tag
  F_theo claim: F_EFF_GAIN_UNDER_CONSTRAINT (isomorphic at unlimited resources)
  Verdict: GENUINE_NEW (efficiency gain, not expansion)

[2026-03-26] main.py (Tier 2 — Adaptive Grammar + Learned Specificity)
  Classes: ConditionalGrammarRule, GrammarRuleComposer, RuleInteractionTracker
  Key methods: _meta_compose_grammar_rule, apply_conditional_rule, compose_sequential/depth_filtered/intensity_adaptive
  Core structures: Precondition functions, EMA success tracking, pairwise rule interaction history
  Search mechanism: Operadic grammar composition + adaptive meta-rule selection
  F_theo claim: F_EFF_GAIN_UNDER_CONSTRAINT (grammar rules are search operators, not expressibility limiters)
  Verdict: GENUINE_NEW (efficiency gain, not expansion)
