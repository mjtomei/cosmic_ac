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

## Description mismatch, recorded per the identity-before-verdict rule

Matthew's second link (2601.01828) was described as "LLMs behaving better when
you respect their existence" — the linked paper is Lindsey's introspection
study, which is not that. A respect/politeness→behavior literature exists
(candidate: a 2024 cross-lingual prompt-politeness study, identity NOT yet
resolved — arXiv API returned empty on first probe; UNRESOLVED LEAD, hunt
before citing anything). If Matthew meant such a paper, it is not yet on disk.

## Coherence placement (not executed — sibling repo, Matthew's call)

Fu 2026 and Banayeeanzade 2026 belong in ~/coherence's evidence base (the
suppression-of-idea-variance thesis gains its first mechanistic external
anchors). This directory holds the files; coherence can reference or copy.

Status: seed; not yet ranked (3 works); grows if the respect-paper hunt or the
correlated-errors/model-similarity literature (e.g. CAPA/model-affinity line)
is pulled in.
