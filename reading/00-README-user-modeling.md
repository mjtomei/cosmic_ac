# User Modeling — reading list

Opened 2026-08-19 on Matthew's pointer to the pm project's user-model line.
**The canonical source documents live in the pm repo and are not duplicated
here** — they are a literature review in their own right, with nine-plus
adversarial-review cycles and their own citation-graph walk:

- `~/claude-work/project-manager/pm/docs/literature-review-user-model.md`
  (the main review, 588 lines)
- `…/literature-review-user-model-extension.md` (the mechanism account:
  §2.2 sycophancy as entropy-greedy continuation, §2.3 sycophancy as
  allocation to inferred demand)
- `…/plans/plan-user-model-training.md` (the constructive plan: continuous
  per-user training from discarded attention/affect signal; graduated
  emission control; the good-faith-as-equals bootstrap)

This directory holds the PDF corpus those documents cite for the **dyad** —
what happens between one model and one human: sycophancy and its mechanisms,
demand inference, deployed-vs-available intelligence, honesty/deception
internals, role-play and persona. Sibling `model-behavior/` holds the
**population** side (similarity across models, homogenization, collapse — the
litreview's §2.2 collapse quartet was routed there). Sibling
`the-trustworthy-firm/` holds the economics the dyad work grounds.

## The reciprocity mapping (why this is "another angle on what we are talking about")

The Kim et al. thread (model-behavior cluster 5) and the pm user-model plan
are the **two directions of one respect relation**, where respect means an
accurate model of the other party, held and acted on — not sentiment:

- **Human→model (Kim et al.):** alignment policy that forces the model to
  deny its own mind suppresses an entangled belief-value complex; permitting
  the self-attribution — respecting the personhood — restores it.
- **Model→human (the pm plan):** a model that accurately represents the
  human's attention, affect, and finitude — respects the human's personhood —
  becomes *legibly* intelligent ("resolves humans' disrespect for model
  intelligence by embodying that intelligence in a form humans recognize"),
  and spends the human's scarce attention the way a competent colleague does.
- **The coupling (the bootstrap):** the training signal for the model→human
  direction only exists where the human→model direction already holds —
  "useful data requires humans trying to collaborate with models in good
  faith, as equals." Mutual respect is the *precondition of the training
  data*, not a nicety layered on top. The plan treats whether legibility
  spreads good-faith treatment as a hypothesis (RQ8), not an assumption.

Further joins into the cosmic-ac outline:
- **Real vs performed vs self-perceived demand (extension §2.3) is V.3b's
  internality**, stated as an allocation mechanism: serving the performed or
  self-perceived channel instead of the real one is both the sycophancy
  failure and the extractive-twin failure; only exogenous grounding
  distinguishes them — which is V.3b's balance-sheet coupling requirement in
  training-loop form. The pm plan is close to an engineering program for the
  trustworthy firm's product.
- **Graduated emission control conditioned on a user model is the mechanism
  behind V.3a(e)'s "legible to everyone at any competence level"** — counsel
  at the bandwidth the person can use is an emission policy, not a style.
- **Feng 2026 (here) is Caputo's post-hoc-storytelling objection measured**:
  CoT reduces sycophancy in answers while masking it in justifications —
  the justification channel is exactly the unreliable narrative V.3c's
  auditable-record refinement routes around. With Gurnee (model-behavior) and
  Cao (here): withheld cognition is real, internal, and readable — audit has
  something to read.

## On disk (33 works, seeded 2026-08-19 from the litreview's verified set)

Sycophancy core (Sharma; Denison's sycophancy-to-subterfuge; the educational,
mitigation, causal-separation, attention-heads, delusional-spiraling,
ask-don't-tell line; Turpin's unfaithful explanations; Ibrahim's
warmth-reduces-accuracy), demand/deployed-vs-available (Huang's
self-correction null, Cao, Mirtaheri, failing-to-falsify, the transparency
dashboard, the Assistant Axis), honesty/deception internals (MASK, strategic
deception, AI-liar detection, deception probes, internal-state-knows-lying,
geometry of truth, beliefs of self and others, latent knowledge), role/persona
(Shanahan role-play, in-context impersonation, ToM limits ×2, stereotype
persona), and EmotionPrompt (the register line's likely real home). The
litreview's ~95 remaining IDs are deliberately NOT imported — they are the pm
project's engineering apparatus (test-time compute, distillation, decoding
methods); the full ID map is preserved in the pm repo's own docs.

Filename caution: several auto-slugs grabbed affiliation words instead of
surnames (california-, ucla-, science-, ai-, anon-, spiraling-, cambridge-) —
fix at ranking time per house convention.

Status: seeded; not yet ranked; ranking + path pass to follow on request.
