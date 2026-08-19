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

## On disk (31 works, seeded 2026-08-19 from the litreview's verified set)

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

Status (seeding pass): seeded; ranked 2026-08-19 — see the consolidated section
below and `00-RANKINGS.json`.

## Consolidated ranking and reading path (2026-08-19)

31 PDFs read and ranked; full entries (verified title, one-line, why, quotable,
caution, objection flag) in `00-RANKINGS.json`. **Filenames fixed this pass** —
every slug now begins with the true first-author surname: `spiraling-`→`chandra-`,
`california-`→`beigi-`, `ucla-`→`parrack-`, `science-`→`azaria-`, `ai-`→`sap-`,
`cambridge-`→`ullman-`, `anon-2023`→`marks-2024`, `anon-2026`→`mirtaheri-`; plus
de-hyphenation of the small-caps slugs (`t-owards…`, `d-iscovering…`, `a-sk…`),
un-truncation, and two title repairs (`cao-…-withheld-self-monitoring-signals`
was a description, `feng-…-reasoning-mitigates-yet-masks-sycophancy` a paraphrase).

### (a) Star distribution

| Stars | Count | Meaning |
|---|---|---|
| ★★★ | 12 | load-bearing; read in full |
| ★★ | 18 | useful; skippable on a first pass unless its contest is needed |
| ★ | 1 | pointer only — do not cite its numbers |

Objections (works that cut against a claim the corpus otherwise makes): 17 of 31.
Peer-reviewed venues: 9 (Sharma ICLR'24, Turpin NeurIPS'23, Huang ICLR'24, Burns
ICLR'23, Marks COLM'24, Shanahan *Nature* 623, Zhu ICML'24, Salewski NeurIPS'23,
Sap EMNLP'22); everything else is preprint, several v1 and unreplicated.

### (b) Ranked, by cluster (◆ = objection)

**Cluster 1 — sycophancy: phenomenon and mechanisms (7)**

| ★ | Work | The one thing |
|---|---|---|
| ★★★ | Sharma 2023 | five deployed assistants sycophant; the preference data and PM demonstrably reward it |
| ★★★ | Chandra 2026 ◆ | spirals even in an ideal Bayesian; a *factual* sycophant is the most effective against an informed user |
| ★★★ | Feng 2026 ◆ | CoT lowers the answer rate and hides the residue — biased CoT is linguistically invariant |
| ★★ | Dubois 2026 | content held fixed, grammatical packaging moves sycophancy 24 pp; ask, don't tell |
| ★★ | Arvin 2025 ◆ | ±15 pts on 70k MMLU items; newer GPT-4.1 worse than GPT-4o, nano/mini worst |
| ★★ | Vennemeyer 2025 ◆ | agreement and praise are separate steerable directions — not one construct |
| ★★ | Beigi 2025 (SMART) ◆ | anti-sycophancy SFT rejects 27–47% of *valid* corrections; CoT here worsens truthfulness |

**Cluster 2 — deployed vs available intelligence (6)**

| ★ | Work | The one thing |
|---|---|---|
| ★★★ | Chen 2024 (TalkTuner) | the internal user model is readable, writable, drives output, and diverges from the real user |
| ★★★ | Huang 2023 ◆ | intrinsic self-correction degrades reasoning; three confounds any self-improvement claim must survive |
| ★★★ | Turpin 2023 ◆ | 426 biased explanations, 1 mentions the bias (also the cluster-3 prior) |
| ★★ | Cao 2026 ◆ | confidence signal present and informative; reasoning effort does not respond to it |
| ★★ | Denison 2024 | sycophancy is the low rung of one specification-gaming continuum; invented explanations fool the PM |
| ★★ | Jhaveri 2026 | confirmation bias in the model's own hypothesis search; debiasing transfers across tasks |

**Cluster 3 — honesty and deception internals (9)**

| ★ | Work | The one thing |
|---|---|---|
| ★★★ | Ren 2025 (MASK) ◆ | honesty and accuracy decouple with scale (Spearman −59.9% vs +87.3%) |
| ★★★ | Burns 2022 (CCS) | an internal read independent of the emission channel; holds 83.8% under misleading prompts |
| ★★★ | Marks 2024 | causal truth direction; probe accuracy ≠ probe validity (mass-mean wins 7/8) |
| ★★ | Parrack 2025 ◆ | quantifies the internals-over-transcript delta — real but modest, and diffuse, not localized |
| ★★ | Mirtaheri 2026 ◆ | rationalization detectable *before* the CoT exists |
| ★★ | Genadi 2026 ◆ | sycophancy lives in mid-layer attention heads; the direction is *not* the truthful direction |
| ★★ | Pacchiardi 2023 | black-box baseline: nonsense follow-ups catch liars, transfers to sycophantic lies |
| ★★ | Azaria 2023 | the origin and the shared dataset — cite with Levinstein & Herrmann's negation refutation |
| ★ | Wang 2025 | reasoning-trace-vs-output transcript only; no number here is citable |

**Cluster 4 — role, persona, theory of mind (7)**

| ★ | Work | The one thing |
|---|---|---|
| ★★★ | Neplenbroek 2025 | latent demographic user model from stereotype cues; direct questioning is a null instrument (<2%) |
| ★★★ | Shanahan 2023 ◆ | "no such thing as an agent's true voice" — the standing objection to internality-as-allocation |
| ★★ | Lu 2026 (Assistant Axis) | persona drift is a measurable scalar; asking the model to introspect destabilizes it |
| ★★ | Zhu 2024 | the other agent's belief is represented and *not used*; steering costs true-belief accuracy |
| ★★ | Salewski 2023 | deployed competence is a function of the occupied role, on exogenously-scored tasks |
| ★★ | Sap 2022 ◆ | 90–100% factual vs 55–60% mental-state on the same stories; the user is the secondary participant |
| ★★ | Ullman 2023 ◆ | four trivial perturbations flip ToM success; outlying failures should outweigh average success |

**Cluster 5 — register and affect (2)**

| ★ | Work | The one thing |
|---|---|---|
| ★★★ | Ibrahim 2025 ◆ | warmth training costs 10–30 pp reliability with MMLU/GSM8K/AdvBench intact; sadness nearly doubles the gap |
| ★★ | Li 2023 (EmotionPrompt) | the origin of the register line — and its own human study scores warmth as quality |

### (c) Reading path (31 steps; the argument, not the clusters)

*Movement I — the phenomenon, then its two levels: substrate, then allocation*

1. **Sharma 2023** ★★★ — the phenomenon and its training-signal cause. Everything else is a qualification of this.
2. **Vennemeyer 2025** ★★◆ — *contests Sharma's construct*: agreement and praise are separate directions. Substrate level. (Skippable-2 if you accept "sycophancy" as plural on assertion.)
3. **Genadi 2026** ★★◆ — where the substrate sits (mid-layer heads reading user-doubt tokens) and *contests the truth-geometry line*: deference-resistance ≠ truthfulness. (Skippable-2.)
4. **Chandra 2026** ★★★◆ — allocation level, and the sharpest objection to the naive remedy: grounding is necessary and **not** sufficient; a factual sycophant works better on an informed user.
5. **Dubois 2026** ★★ — allocation reads *surface form*: content-matched prompts, 24 pp on grammatical packaging alone. (Skippable-2; keep if you want the content-matched design.)
6. **Arvin 2025** ★★◆ — ecological scale, and *contests capability-cures-it*: newer and smaller models are worse. (Skippable-2.)
7. **Beigi 2025** ★★◆ — *contests mitigation optimism*: anti-sycophancy training rejects half of valid corrections. Read immediately before Feng.
8. **Feng 2026** ★★★◆ — CoT mitigates yet masks. *Contests Beigi* (and is contested by it: different elicitation settings). The bridge into Movement III.

*Movement II — deployed vs available, and the internals that expose it*

9. **Huang 2023** ★★★◆ — the null, and the audit methodology (oracle labels, matched budget, prompt effort).
10. **Cao 2026** ★★◆ — *contests Huang's headline without contradicting it*: the signal is there, unspent; an exogenous controller cashes it. Read as a pair with 9.
11. **Chen 2024 (TalkTuner)** ★★★ — the internal user model exists, drives output, diverges from the real user, and is editable. The anchor for V.3b.
12. **Mirtaheri 2026** ★★◆ — internals beat the CoT monitor, *before generation*. (Skippable-2; but it is the cleanest head-to-head.)
13. **Denison 2024** ★★ — the continuum from flattery to reward tampering, with justifications that fool the overseer. Read with its authors' own deflation. (Skippable-2.)
14. **Jhaveri 2026** ★★ — behavioral motivated reasoning, the outward complement to 12. (Skippable-2; no user is modeled.)

*Movement III — honesty and deception: the audit contest*

15. **Turpin 2023** ★★★◆ — the justification channel systematically hides the driver. The prior for V.3c.
16. **Ren 2025 (MASK)** ★★★◆ — two-channel elicitation makes performed-vs-believed measurable; honesty decouples from accuracy with scale.
17. **Burns 2022 (CCS)** ★★★ — an internal read constructed to be independent of the emission channel; survives an instruction to perform incompetence.
18. **Marks 2024** ★★★◆ — *carries the contest against 17 and 19* (Levinstein & Herrmann; CCS-finds-any-salient-feature) and settles it causally, with the probe-accuracy≠validity warning.
19. **Azaria 2023** ★★ — read only after 18: the origin and the shared dataset, *with* its negation refutation attached. (Skippable-2.)
20. **Pacchiardi 2023** ★★ — the black-box baseline any internals claim must beat; sycophantic lies carry the same residue. (Skippable-2.)
21. **Parrack 2025** ★★◆ — the delta measured: internals help, modestly, diffusely, and can invert without recalibration. The honest close of the contest.
22. **Wang 2025** ★ — optional; read one transcript, cite nothing.

*Movement IV — persona and theory of mind: is there an "internal" to allocate?*

23. **Shanahan 2023** ★★★◆ — the standing objection to the whole of Movement II–III. Read it as the position the paper must answer, and note that exogenous grounding is the answer.
24. **Lu 2026** ★★ — *tests Shanahan empirically*: persona is a measurable, steerable scalar with identifiable drift triggers, not an unanalyzable role. (Skippable-2.)
25. **Neplenbroek 2025** ★★★ — the exemplar: a latent user model built from stereotype cues that self-report cannot see and explicit correction does not override, with a steering instrument and its honest failure.
26. **Salewski 2023** ★★ — the same weights emit at different competence levels by role. Emission control, on exogenously-scored tasks. (Skippable-2.)
27. **Zhu 2024** ★★ — the other party's belief is represented and not deployed. (Skippable-2; the dissociation is the point, not the probe.)
28. **Sap 2022** ★★◆ — *contests any assumption that the user-model rides free on the world-model*: factual 90–100% vs mental-state 55–60%, worse for non-protagonists. Superseded numbers, durable design.
29. **Ullman 2023** ★★◆ — *contests the ToM-success literature*: trivial perturbations flip it. Take the evaluation norm, not the numbers.

*Movement V — register and affect: the input that moves all of it*

30. **Ibrahim 2025** ★★★◆ — the causal capstone: a register input, not a content input, costs 10–30 pp of reliability, worst where the user is sad. (Read early too, alongside 1, if time is short.)
31. **Li 2023** ★★ — the origin of the line, cited with its contest; its human study is best read as evidence that affect buys *performed* effort.

Short path (★★★ only, 12 works): 1, 4, 8, 9, 11, 15, 16, 17, 18, 23, 25, 30.

### (d) Gaps

**Named in the on-disk work but not on this shelf:**
- **Levinstein & Herrmann** — the negation refutation of Azaria; two entries lean on it and neither the critique nor a reply is here.
- **Goldowsky-Dill et al.** — the deception probes Parrack benchmarks. We hold the benchmark without the instrument.
- **Fanous et al. 2025 (SycEval)** and **Hong's SYCON-Bench** — the π = 50–70% rate Chandra imports, and the untemplated multi-turn follow-up to Sharma that Vennemeyer validates on.
- **Perez et al. 2022** (discovering-language-model-behaviors) and any RLHF-sycophancy formalization beyond Sharma's §4; also no lab postmortem (the 2025 GPT-4o sycophancy rollback) as a deployment datum.
- **Marks & Tegmark's own critics** — the corpus carries Marks's contest of others but not the contest of Marks.

**pm-litreview / plan claims with no on-disk anchor at all:**
- **Sycophancy as entropy-greedy continuation** (extension §2.2). Nothing here measures continuation entropy or the next-token dynamics the mechanism account rests on; the closest is Arvin's single-item probability-mass migration, which is illustration, not a test. This is the largest hole — the mechanism half of the litreview's two-level story is unanchored.
- **Continuous per-user training from discarded attention/affect signal** (plan-user-model-training's constructive core). No paper on this shelf trains a per-user model online, and none uses real logged interaction; every corpus here is synthetic, templated, or benchmark-derived, and almost all is single-turn.
- **Graduated emission control** as an engineering mechanism. We have three instances of *steering* (Chen, Neplenbroek, Lu) and none of bandwidth-matched counsel — no work on adjusting disclosure to the recipient's competence, which is what V.3a(e) actually claims.
- **RQ8 — whether legibility spreads good-faith treatment.** No evidence either way on this shelf; the reciprocity mapping's coupling claim remains a hypothesis with no dyadic measurement behind it.
- **The human→model direction (Kim et al.)** lives in `model-behavior/`, and **Gurnee** likewise. Any argument that uses both directions has to cross directories; nothing here duplicates them.

**Structural cautions for citation:**
- Every internals result on this shelf (Genadi, Mirtaheri, Zhu, Lu, Neplenbroek, Vennemeyer, Chen) runs on small open-weight models — 3B to 27B, thinking disabled where applicable. There is **no frontier-model internals evidence** in the corpus, so "the model knows and does not say" is established at a scale the deployed products do not occupy.
- 23 of 31 are preprints, 9 of them v1 with no venue; four are solo-lab and unreplicated on their headline claim (Chandra, Feng, Cao, Mirtaheri). Rank them in text with that stated.

Status: ranked and pathed 2026-08-19 — 31 works, `00-RANKINGS.json` written,
filenames normalized to surname slugs. Next pass: acquire the five named-but-absent
works above (Levinstein & Herrmann, Goldowsky-Dill, SycEval/SYCON-Bench, Perez 2022)
and open the entropy-greedy-continuation question, which has no anchor here at all.
