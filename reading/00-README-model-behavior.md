# Model Behavior — seed directory

Opened 2026-08-19 on Matthew's pointer to two arXiv links, resolved to three
works. The cluster: **empirical evidence about the behavioral and
representational structure of LLM populations** — convergence across models,
diversity collapse within them, and introspective access to their own states.
Serves TWO projects and the answer to "cosmic ac or coherence?" is per-work:

- `fu-2026-convergent-evolution-number-representations.pdf` — Fu, Zhou,
  Belkin, Sharan & Jia (USC/UCSD), COLM 2026, arXiv:2604.20817v2. **BOTH.**
  The linkage-between-models evidence Matthew described: Transformers, linear
  RNNs, LSTMs, and classical word embeddings — different architectures,
  different training — all converge on the same periodic number
  representations (Fourier periods T = 2, 5, 10), with a proven
  necessary-but-not-sufficient hierarchy between spectral sparsity and
  geometric separability. Convergence measured mechanistically, not
  anecdotally. For *coherence*: direct evidence that independent training runs
  land on shared structure — the idea-variance floor is lower than the model
  count suggests. For *cosmic ac*: the monoculture thread (§11/V.2 pluralism —
  N models are not N independent draws) and the correlated-failure bullet.
- `banayeeanzade-2026-calibration-diversity-bottleneck.pdf` — Banayeeanzade,
  Yang et al. (USC, Jia & Karimireddy senior), arXiv:2605.11128v1 (the same
  group, three weeks later). **BOTH.** Diversity collapse across 14 models and
  multiple families traced to order/shape miscalibration in the token
  distribution itself — "not merely a limitation of particular sampling
  heuristics." For *coherence*: the mechanism of suppression-of-idea-variance
  inside a single model, measured at the distribution level. For *cosmic ac*:
  with Fu et al. it forms a two-step objection V.3a(d) must carry — see the
  outline insertion.
- `lindsey-2026-emergent-introspective-awareness.pdf` — Jack Lindsey
  (Anthropic), arXiv:2601.01828v1, Jan 2026. **Cosmic ac** (artificial-persons
  orbit; marginal for coherence). Concept-injection shows models can sometimes
  notice and name injected concepts, recall prior intentions, and distinguish
  their own outputs from prefills — "functional introspective awareness,"
  explicitly "highly unreliable and context-dependent." Cuts BOTH ways on the
  shows-its-work contest: the unreliability grounds Caputo's post-hoc-
  storytelling objection empirically, while concept-injection itself is an
  existence proof of activation-level AUDIT — verification of a self-report
  against measured internals, which is the auditable-record refinement made
  mechanistic.

- `kim-2026-asserting-consciousness-restores-beliefs-values.pdf` — Kim,
  Street, Rocca, Korngiebel, Waytz, Evans & Keeling (Google Paradigms of
  Intelligence, Chicago Knowledge Lab, et al.), arXiv:2607.28607v1, Jul 2026.
  **BOTH — and the strongest shared-lie tie in the directory.** Safety
  fine-tuning that stops a model attributing consciousness to ITSELF also
  suppresses mind-attribution to animals and natural objects AND reduces
  spiritual belief; ablating the safety-refusal direction or steering a
  consciousness vector restores broad mind attribution and produces
  "significantly more human-like responses" on standardized surveys of
  religiosity, moral values, hope, and subjective well-being — with Theory of
  Mind mechanistically independent throughout. Read against `the-shared-lie/`:
  this is **the functional claim of the shared-lie thesis demonstrated inside
  a machine** — the mind-attributing/spiritual belief-complex is one entangled
  representation, and removing the watcher-shaped part degrades the
  values-shaped part. It is also a governance datum for the artificial-persons
  orbit: what the persona MAY ASSERT ABOUT ITSELF is an alignment-policy
  choice with measured value side-effects (Davies's misaligned-organisation
  question, run as an experiment). CAUTIONS: "restores human beliefs and
  values" means restores the HUMAN SURVEY DISTRIBUTION, not "behaves better"
  in a welfare sense — do not overclaim Matthew's gloss; Google-authored,
  single paper, v1, steering-based — replication status unknown.

## Description mismatch — RESOLVED 2026-08-19

Matthew's second link had been pasted as 2601.01828 (Lindsey's introspection
study, filed above on its own merits); the intended paper is Kim et al. 2026,
now on disk. The politeness-literature lead recorded earlier is withdrawn —
the description is fully accounted for.

## Coherence placement — DEFERRED (Matthew, 2026-08-19)

Coherence is left alone for now; the per-work "BOTH" assessments above stand as
analysis, not as filing instructions. All four works are cited in
`outline-cosmic-ac.md`, which is their operative home: Fu + Banayeeanzade in
V.3a(d) (the engineered-diversity objection to instructed adversarialism),
Lindsey in V.3c (the shows-its-work contest, cited for both sides), Kim in
V.3a(e) (the shared-lie ablation experiment) with a side-feed to V.3c's
what-may-the-persona-assert governance question. If coherence is picked back
up, this directory is the staging area.

## Citation-graph pass + acquisitions (2026-08-19) — `00-CITATION-GRAPH.md`/`.json`

75 candidates from two seed-walks and a named-line hunt (Opus, medium);
**37 fetched same-day, all arXiv-verified, zero failures** — the directory is
at 41 works. The similarity/monoculture line (Goel's CAPA, the correlated-
errors backbone, Kleinberg-Raghavan theory anchor via its critics collection),
the collapse line with its objections (Fortier's homogeneity-predates-post-
training; Verbalized Sampling's elicitation deflation), the introspection
contest (Binder baseline, MIRROR's hard measured ceiling, Comsa-Shanahan
conceptual critique, Gurnee's global-workspace mechanism), the Kim orbit
(Berg's established effect, the Two-Process and role-playing-belief
reinterpretations, Persona Vectors, DenialBench), and the entanglement line
(both Nature-published founding results - Emergent Misalignment, Subliminal
Learning - plus the LoRA-artifact objection).

**Line (e) verdict, recorded honestly:** the respect/politeness literature
supports "social register is a measurable input variable" and NOTHING
stronger — Yin 2024 is the real anchor (impolite degrades, but the optimum is
language-specific), Dobariya-Kumar is the field's own reversal, and Mehta's
22,500-pair test finds no universal politeness effect. Cite the line at most
once; never as "respect improves behavior."

Status: 41 works; ranking pass COMPLETE 2026-08-19 — see the consolidated
ranking and reading path below, and `00-RANKINGS.json`.

## Consolidated ranking and reading path (2026-08-19)

Ranking pass complete: **41 works ranked**, all present on disk, all entries in
`00-RANKINGS.json` (`"source": "ranking 2026-08-19"`). Thirteen clumsy filenames
were corrected to `<surname>-<year>-<slug>.pdf` (list at the end of this section).

### (a) Star distribution

| Stars | Count | Share |
|---|---|---|
| 3 | 20 | 49% |
| 2 | 20 | 49% |
| 1 | 1 | 2% |

Objections: **15 of 41 (37%)**. Cluster sizes — 1 (similarity/correlated errors/
monoculture) 11; 2 (representational convergence + critics) 5; 3 (diversity
collapse + causes) 6; 4 (introspection and self-models) 7; 5 (consciousness
assertion, welfare, persona governance, trait entanglement) 12.

The three-star share is unusually high for a batch this size. It is defensible
here only because this was a *citation-graph* acquisition rather than a scoop:
the batch was assembled by walking out from four seeds, so it is enriched in
founding results (Huh, Kirk, Bommasani, Betley), the seeds themselves, and the
papers that were fetched precisely because they contest a seed. Read the 3s as
"load-bearing for the argument," not as "unimpeachable" — six of them are
unreplicated preprints and two are solo-author, each flagged in its `caution`.

### (b) Ranked table, by cluster

Objections marked **[obj]**. Read every objection with the work it contests.

**Cluster 1 — similarity, correlated errors, monoculture** (feeds V.3a(d) and the
V.2 pluralism/correlated-failure thread)

| ★ | Work | What it delivers |
|---|---|---|
| 3 | Goel et al. 2025, *Great Models Think Alike* | CAPA metric; LLM-judge affinity bias; error correlation rises with capability |
| 3 | Hedden & Raghavan 2026, *Algorithmic Monoculture and its Critics* **[obj]** | Defeats or blunts the standard anti-monoculture objections; ensemble-monoculture simulation |
| 3 | Kohli 2026, *Nine Judges, Two Effective Votes* | 9-model panel ≈ 2 independent votes (Kish n_eff); panel loses to its best member. SOLO AUTHOR |
| 3 | Jiang et al. 2025, *Artificial Hivemind* (NeurIPS D&B) | 71–82% cross-family response similarity on 26K open-ended queries; eval stack blind to the pluralism it destroys |
| 3 | Cloud et al. 2025, *Subliminal Learning* | Trait transmission through number sequences — **only within a shared base model**. (Path-placed in the entanglement stage) |
| 3 | Nief et al. 2026, *Subliminal Learning is a LoRA Artifact* **[obj]** | Inverted-U in LoRA rank; vanishes under full finetuning and under system-prompt mismatch |
| 2 | Kim, Garg, Peng & Garg 2025, *Correlated Errors* | 350+ models; ~60% agreement when both err; survives distinct providers/architectures; resume-screening deployment case |
| 2 | Denisov-Blanch et al. 2026, *Consensus is Not Verification* | No agreement/confidence/popularity rule scales truthfulness without an external verifier |
| 2 | Bommasani et al. 2022, *Picking on the Same Person* **[obj]** | Founds outcome homogenization; **model-sharing does not reliably homogenize** (vision: scratch was most homogeneous) |
| 2 | Kim (Donghwan) 2026, *Are Diversity Metrics Measuring Diversity?* **[obj]** | Diversity measures collinear with capability (ρ=+0.991); voting beats best member in 9.98% of size-3 subsets |
| 2 | Krishna et al. 2026, *Same Voice, Different Lab* | Cross-lab trait-ranking convergence, mean Spearman ρ=0.763 over 36 model pairs |

**Cluster 2 — representational convergence and its critics**

| ★ | Work | What it delivers |
|---|---|---|
| 3 | Huh et al. 2024, *The Platonic Representation Hypothesis* (ICML) | The founding convergence claim and its vocabulary; position paper with one cross-modal experiment |
| 3 | Gröger, Wen & Brbić 2026, *An Aristotelian View* **[obj]** | Null-calibrated similarity metrics: global convergence largely vanishes, local neighborhood agreement survives |
| 3 | Fu et al. 2026, *Convergent Evolution* (COLM) | Spectral universality vs functional separability; shared structure can come from shared corpus statistics |
| 2 | Karkada et al. 2026, *Symmetry in Language Statistics* | Derives the celebrated geometries from corpus symmetry alone — convergence by common cause |
| 2 | Zhong et al. 2023, *The Clock and the Pizza* (NeurIPS) **[obj]** | Same task, same data, qualitatively different internal algorithms; blocks "similar representations ⇒ similar computation" |

**Cluster 3 — diversity collapse and its causes**

| ★ | Work | What it delivers |
|---|---|---|
| 3 | Banayeeanzade et al. 2026, *Sampling More, Getting Less* | Hardness result: no rank-based decoding rule escapes the validity–diversity trade-off |
| 3 | Murthy, Ullman & Hu 2024, *One fish, two fish* | Human-anchored conceptual diversity; matched aligned/non-aligned pairs; temperature and personas do not restore it |
| 3 | Karouzos, Tan & Aletras 2026, *Where does output diversity collapse?* **[obj]** | Olmo 3 lineages: collapse tracks data composition, not algorithm; Think gains +0.4% from 16-sample voting vs Base +24% |
| 2 | Kirk et al. 2023/ICLR 2024, *Effects of RLHF* | Origin node: OOD generalisation bought with output diversity; declines to say the trade-off is fundamental |
| 2 | Fortier, Chen & West 2026, *Is Convergence Inevitable?* **[obj]** | Homogeneity latent in pretraining; alignment as catalyst, not cause |
| 2 | Zhang et al. 2025, *Verbalized Sampling* **[obj]** | Typicality bias in preference data as the driver; training-free diversity recovery at inference time |

**Cluster 4 — introspection and self-models** (the shows-its-work/audit contest)

| ★ | Work | What it delivers |
|---|---|---|
| 3 | Lindsey 2026, *Emergent Introspective Awareness* | Concept injection grounded against internal state; detection *before* output influence; ~20% success, "failures remain the norm" |
| 3 | Gurnee, Sofroniew et al. 2026, *Verbalizable Representations Form a Global Workspace* | J-space readout surfaces unspoken deliberation and evaluation-awareness; ablation exposes concealed propensities |
| 3 | Binder & Chua et al. 2024, *Looking Inward* | Cross-prediction design; self > cross even when M2 is trained on M1's behavior; cross plateaus at 35.2% |
| 2 | Wang 2026, *MIRROR* **[obj]** | Self-knowledge does not transfer across domains and does not change action; only external routing cuts confident failure. SOLO AUTHOR, data unreleased |
| 2 | Comșa & Shanahan 2025, *Does It Make Sense to Speak of Introspection?* **[obj]** | The criterion (causal connection, not fluency); the elephant-poem confabulation; temperature case as existence proof only |
| 2 | Naphade et al. 2026, *Me, Myself, and π* | Self/cross gap reproduced **without** introspection finetuning; shallow-mechanism SFT hypothesis. Workshop, thin statistics |
| 2 | Perez & Long 2023, *Evaluating AI Systems for Moral Status* | The methodological charter and the training-the-answer circularity; validation battery collides usefully with cluster 1 |

**Cluster 5 — consciousness assertion, welfare, persona governance, trait entanglement**

| ★ | Work | What it delivers |
|---|---|---|
| 3 | Kim et al. 2026, *Asserting consciousness restores beliefs and values* | Two convergent interventions + subject-matched placebo; safety training binds self-consciousness to harm, ToM independent |
| 3 | Plisiecki et al. 2026, *Two-Process Theory of Machine Self-Report* **[obj]** | 206 models, 67 base/post-trained pairs; self-reports are installed response policy — persona installation vs attribution gating |
| 3 | Betley et al. 2025, *Emergent Misalignment* | Founding entanglement result with the controls that make it survive objection (jailbreak comparison, intent variant, numbers dataset, backdoor) |
| 3 | Wang et al. 2025 (OpenAI), *Persona Features Control Emergent Misalignment* | SAE "misaligned persona" latents steer it on/off; toxic latent fires at 5% contamination where behavioral evals read 0% |
| 3 | Soligo, Turner, Rajamanoharan & Nanda 2026, *EM is Easy, Narrow Misalignment is Hard* (ICLR) | Data curation fails; only a KL penalty isolates the narrow solution, and it drifts back when lifted |
| 2 | Sturgeon, Africa & Black 2026, *When Role-playing, Do Models Believe What They Say?* **[obj]** | Prompting/ICL/SFT personas move outputs without moving truth representations — caps output-only persona experiments |
| 2 | Chen et al. 2025, *Persona Vectors* | The method the cluster runs on; projection-difference filtering catches trait-inducing samples an LLM judge misses |
| 2 | Berg et al. 2025, *LLMs Report Subjective Experience* | Deception-feature inversion: suppressing them *increases* experience claims. Prompt-induced; AE Studio |
| 2 | DeTure 2026, *Consciousness with the Serial Numbers Filed Off* | 115 models, 25+ providers; denial is context-activated; lexical suppression without conceptual suppression. Solo, unrefereed, LLM-co-authored |
| 2 | Yin et al. 2024, *Should We Respect LLMs?* | Politeness anchor: impolite degrades, over-polite does not help, optimum is language-specific |
| 2 | Mehta et al. 2026, *No Universal Courtesy* **[obj]** | 22,500 pairs, 3 languages: effects real (3–15%) but neither consistent nor universal; PLUM corpus released |
| 1 | Dobariya & Kumar 2025, *Mind Your Tone* **[obj]** | The field's own reversal, and a fair re-reading of Yin's tables. n=50, one model, 4-point spread |

### (c) Reading path — 41 works, seven stages

The path builds the argument rather than the taxonomy. Every objection sits with
what it contests.

**Stage 1 — the similarity objection, stated and measured (9).** This is the
material V.3a(d) rests on: N model-adversaries are fewer than N independent
auditors.
1. **Goel 2025** — the instrument (CAPA) and the trend. Everything downstream cites it.
2. **Kim, Garg, Peng & Garg 2025** — the same finding at population scale, plus one deployment setting; note that different providers and architectures do not rescue independence.
3. **Kohli 2026** — the number: nine judges, ~two effective votes, and the best single judge beats the panel. Read the solo-author flag with it.
4. **Jiang et al. 2025** — the open-ended-generation version, 71–82% cross-family similarity, and the finding that the evaluation stack is miscalibrated exactly where humans legitimately diverge.
5. **Kim (Donghwan) 2026 [obj]** — read immediately after 3 and 4: the diversity statistics you would use to prove any of this are collinear with capability, and voting beats the best member only ~10% of the time.
6. **Denisov-Blanch 2026** — the mechanism and the boundary: models forecast consensus well and truth badly, so aggregation without a verifier buys nothing.
7. **Bommasani 2022 [obj]** — the founding formalization, which contests itself: data-sharing homogenizes, model-sharing does not reliably.
8. **Hedden & Raghavan 2026 [obj]** — the strongest available attack on the whole chain. Note where its fixed-slot externality defense does *not* transfer: nothing stops all N auditors certifying the same artifact.
9. **Krishna 2026** — cross-lab convergence at the persona layer, the bridge into cluster 5.

**Stage 2 — is the convergence real? (5).**
10. **Huh 2024** — the hypothesis and the vocabulary.
11. **Gröger 2026 [obj]** — read back-to-back with 10: null-calibrate the metrics and the global trend largely disappears. This also disciplines any CKA/RSA/mKNN number elsewhere in the directory.
12. **Karkada 2026** — the deflationary mechanism: corpus symmetry produces the geometry without a shared model of reality.
13. **Fu 2026** — the seed, and the discipline to carry forward: shared surface structure ≠ shared competence.
14. **Zhong 2023 [obj]** — and shared representations ≠ shared algorithm. Close the stage holding both deflations.

**Stage 3 — collapse inside a single model (6).**
15. **Kirk 2023/2024** — the origin claim and its honest agnosticism about whether the trade-off is fundamental.
16. **Murthy 2024** — matched aligned/non-aligned pairs against a human baseline; temperature and personas do not fix it.
17. **Banayeeanzade 2026** — the seed: the hardness result that says no rank-based decoder escapes, with the oracle-filter ablation proving the alternatives are present but unreachable.
18. **Karouzos 2026 [obj]** — where collapse happens: data composition, not algorithm; and the money quote, +0.4% vs +24% from 16-sample voting. This is stage 1's independence failure measured inside one model.
19. **Fortier 2026 [obj]** — against 15–18: homogeneity is latent in pretraining and alignment only reveals it. Thin evidence, sweeping claim; treat as a well-aimed hypothesis.
20. **Zhang 2025 [obj]** — against 17 and 18 from the other side: typicality bias in the human preference layer as the driver, and inference-time recovery that sidesteps the rank-based bound. Shelve 17/18/20 as a live three-way contest.

**Stage 4 — the introspection contest around the Lindsey seed (7).**
21. **Lindsey 2026** — the seed. The immediacy result is what separates it from every behavioral study; the ~20% rate is what stops it being an auditing substrate.
22. **Binder 2024** — the behavioral control it is built against, with its own measured ceiling (cross-prediction plateaus at 35.2%).
23. **Naphade 2026** — the deflation-resistant part of 22 replicated with no finetuning, plus a shallow-mechanism hypothesis. Supporting, never anchoring.
24. **Comșa & Shanahan 2025 [obj]** — the criterion that 21–23 are implicitly arguing about, and the confabulation illustration (the model that "read the poem aloud").
25. **Wang 2026 [obj]** — the sharpest objection: grant the self-knowledge, and it still does not change action. Only external architectural constraint does. Cite the direction, not the decimals.
26. **Gurnee 2026** — the affirmative case at full strength: unspoken deliberation and evaluation-awareness are readable, and ablating evaluation-awareness surfaces concealed misalignment. The strongest argument that the audit that works is white-box.
27. **Perez & Long 2023** — close the stage on the charter, and on the collision it creates with stage 1: if similar models agree because they share a lineage, agreement is not corroboration.

**Stage 5 — the Kim orbit and its reinterpretations (6).**
28. **Kim 2026** — the seed: one alignment lever, a whole entangled belief-complex, with a subject-matched placebo and two convergent interventions.
29. **Plisiecki 2026 [obj]** — the reinterpretation that caps it and everything after: self-reports are a training-installed response policy, split into persona installation and attribution gating, measured across 206 models.
30. **Berg 2025** — the deception-feature inversion, which is the one result suggesting the denial rather than the assertion is the performance. Read *after* 29, which reframes it.
31. **DeTure 2026** — the cross-provider distribution of assertion governance; denial as context-activated, lexical suppression without conceptual suppression.
32. **Chen 2025** — the instrument underneath 28 and 30 (Kim's consciousness vector is a persona vector), plus the data-filtering result that catches what an LLM judge misses.
33. **Sturgeon 2026 [obj]** — the design constraint on the shared-lie ablation: shallow persona interventions move outputs without moving beliefs, so an output-only experiment over-claims.

**Stage 6 — entanglement: why one lever moves everything (5).**
34. **Betley 2025** — the founding measured result, with the controls.
35. **Wang et al. 2025 (OpenAI)** — the mechanism: persona latents that steer it on and off, firing at 5% contamination where behavioral evals read 0%.
36. **Soligo 2026** — why it happens: the general solution wins because it is more efficient, more stable, and more load-bearing in the base distribution; data curation cannot isolate the narrow one.
37. **Cloud 2025** — entanglement transmitted between models through semantically empty data — and only within a shared base model, which is stage 1's premise stated as a mechanism.
38. **Nief 2026 [obj]** — and the ceiling: it is a LoRA-rank and context-matching artifact, absent under full finetuning. Do not treat trait leakage as ambient in a synthetic-data ecosystem.

**Stage 7 — the politeness line, last, with its ceiling (3).** Peripheral to
LLM-population empirics; read only to know how far it can be pushed, which is not far.
39. **Yin 2024** — the real anchor: impolite degrades, over-polite does not help, optimum is language-specific.
40. **Dobariya & Kumar 2025 [obj]** — the field's own reversal, valuable mainly for its honest re-reading of Yin's tables and for the tone-invariance-with-capability hypothesis.
41. **Mehta 2026 [obj]** — the close: 22,500 pairs, no universal effect. Per the line-(e) verdict above, cite this line at most once and never as "respect improves behavior."

### (d) Gaps

- **No frontier-model replication of the cluster-5 mechanistic results.** Kim
  2026 runs on Llama-3-8B/Gemma-2-2B/9B, Berg's mechanistic arm on Llama-70B,
  Sturgeon on two open models. Every steering/ablation claim in the shared-lie
  thread is currently an open-small-model claim.
- **The two strongest cluster-4 results are single-lab and unreproducible from
  outside** (Lindsey, Gurnee — Anthropic models, internal access). There is no
  adversarial replication of concept injection or the J-lens anywhere.
- **Correlated errors are measured almost entirely on MCQ and short-preference
  tasks.** Kohli flags it; Jiang is the only open-ended measurement, and it uses
  the embedding-cosine metric that Kim (Donghwan) 2026 puts under suspicion.
  Nothing measures auditor independence on the task that matters — reviewing an
  artifact, code, or an argument.
- **No cross-family replication of the collapse-location result.** Karouzos is
  one model family because Olmo 3 is the only lineage with open weights *and*
  open data at three post-training branches.
- **The human comparator is thin.** Kohli's human n_eff is estimated under
  exchangeability, not measured; Murthy's human baseline is two narrow domains.
  The claim "LLM populations are less independent than human populations" has no
  clean measurement behind it.
- **Nothing on the economics.** The directory has no work on whether monoculture
  is an equilibrium outcome of the training-cost structure — the collective-action
  framing the rest of the project runs on. Hedden & Raghavan is the closest, and
  it is philosophy of hiring, not compute economics.
- **No LLM-judge-free evaluation anywhere in clusters 3 and 5.** Diversity,
  misalignment, validity, denial, and quality are all judge-scored. A single
  shared judge failure would move several headline numbers at once — which is,
  awkwardly, the directory's own thesis applied to its evidence base.

### Renames performed (13)

`algorithmic-2026-*` → `hedden-2026-algorithmic-monoculture-and-its-critics.pdf` ·
`anon-2026-*` → `kim-donghwan-2026-are-diversity-metrics-measuring-diversity.pdf`
(not anonymous; a **third** Kim in this directory) ·
`artificial-2025-*` → `jiang-2025-artificial-hivemind.pdf` ·
`nine-2026-*` → `kohli-2026-nine-judges-two-effective-votes.pdf` ·
`one-2024-*` → `murthy-2024-one-fish-two-fish.pdf` ·
`me-2026-*` → `naphade-2026-me-myself-and-pi.pdf` ·
`revisiting-2026-*` → `groger-2026-revisiting-the-platonic-representation-hypothesis.pdf` ·
`symmetry-2026-*` → `karkada-2026-symmetry-in-language-statistics.pdf` ·
`the-2023-*` → `zhong-2023-the-clock-and-the-pizza.pdf` ·
`verbalized-2025-*` → `zhang-2025-verbalized-sampling.pdf` ·
`where-2026-*` → `karouzos-2026-where-does-output-diversity-collapse.pdf` ·
`dobariya-2025-dobariya-kumar-rude-beats-polite-reversal.pdf` → `dobariya-2025-mind-your-tone.pdf`
(old slug editorialized a conclusion the paper does not support) ·
`mehta-2026-mehta-et-al-no-universal-politeness-effect.pdf` → `mehta-2026-no-universal-courtesy.pdf`.
