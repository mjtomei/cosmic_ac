# S10 — the original pre-execution design (2026-07-29)

**Superseded. Preserved verbatim; do not follow it.** This was the S10 study
register entry before the study ran. It is kept because it records the
reasoning behind choices that were later reversed, and because the reversals
are themselves findings.

For what S10 actually is, see the register entry in `studies-and-work-log.md`,
the write-up at `analysis/s10/S10-WRITEUP-DRAFT.md`, and the methodology at
`analysis/s10/METHODOLOGY.md`. The companion session plan of the same vintage
is `S10-legislative-ai-detection.md`.

## What the study did differently

- **Pangram went from Tier 4 to the primary instrument.** The plan below
  demotes it to "a paid cross-check on a sample" and builds the headline on
  free distributional estimation. The free tiers all failed: six zero-shot and
  supervised instruments flagged 2025-26 *below* their own pre-LLM
  false-positive floors, because edited legislative prose is exactly the
  register they over-flag. A calibrated commercial detector with per-chamber
  pre-AI controls became the only instrument that could carry the claim.
- **The Liang-based estimator was dropped** on 2026-07-29 and replaced with
  Rogan-Gladen calibration against measured per-chamber specificity.
- **The cost table below is projection, not spend.** Actual: $158.00 API plus
  8,962 dashboard credits for 4,258 Pangram 4 verdicts across 19 chambers.
- **Scope grew well past the plan.** Arms that do not appear below at all: the
  genre ladder, the Opus screen and its effort A/B, the cohort decomposition,
  the OLMo post-training ladder, the four-stage quality arm, and the bypass
  study.
- **The frequency/lexicon arm was demoted to descriptive** after an in-time
  placebo showed it has no trend control.

Two things in the plan held up exactly as written, and deserve the credit: the
insistence that a **per-chamber pre-2022 negative control** is the whole study
("without this the result is worthless"), and the warning that **"AI" and "not
written by the speaker" are different claims** and only the former is being
measured.

---

### S10. AI-generated text in legislative transcripts — **CANDIDATE, designed**
*Origin:* the Bill Oliver clip (New Brunswick, May–June 2026) in which a member
appears to read a model's framing sentence aloud mid-speech. Matthew ran the
YouTube auto-caption transcript through Pangram: **100% AI-generated**.

*Question:* what share of legislative speech is machine-generated, and how has
it moved since late 2022?

*Why it matters for the paper:* it converts V.3's "the office is a socket" from
an anecdote into a measured trend — direct evidence that substitution of machine
cognition into institutional roles is already underway and unremarked. It is the
paper's best candidate for an original empirical figure, and it is *cheap*.

*Method:*
1. Corpus: official Hansard (not auto-captions). New Brunswick's 61st Legislature
   is already downloaded — 38 sittings, 1.60M words bilingual, ~0.80M English.
   Extend to other Canadian provinces, the federal Parliament, UK, Australia,
   US states with published verbatim records.
2. Segment by speech and by speaker, keeping date, chamber, party, and whether
   the passage is prepared remarks or spontaneous debate (the distinction is
   likely to dominate the signal).
3. Score each segment with a detector (Pangram; ideally a second detector for
   agreement).
4. Report share-of-words flagged over time, per chamber and per speaker.

*The methodological crux — a negative control:* score pre-2022 transcripts from
the same chambers and speakers. Any nonzero rate there is the false-positive
floor, and the study's entire claim is the delta above it. Without this the
result is worthless, because formal prepared oratory is exactly the register
detectors over-flag.

*Other confounds to state:* Hansard is lightly edited by professional editors,
which may itself normalize prose toward the flagged register; prepared speeches
have always been staff-drafted, so "AI" and "not written by the speaker" are
different claims and only the former is being measured; bilingual chambers carry
professional translations that should be scored separately or excluded.

*Cost (Pangram, measured against the NB corpus):*

| Scope | English words | Pangram 4 API | bulk −20% |
|---|---|---|---|
| NB, one session (have it) | 0.80M | $401 | **$321** |
| NB, full legislature (~4 sessions) | 3.2M | $1,604 | $1,284 |
| One large provincial legislature, 1 yr | ~8M | $4,000 | $3,200 |
| Canadian Parliament, 1 yr | ~40M | $20,000 | $16,000 |
| 10 legislatures × 5 yrs | ~200M | $100,000 | $80,000 |

Pangram's older model is listed at 1/10th the price ($0.05/1,000 words), which
would put a full NB legislature at ~$128 — worth testing whether its accuracy
suffices, since a 10× price difference changes what is affordable by two orders
of scope. The **Professional plan ($65/mo, 1.5M words/mo + $200 API credit)**
covers roughly two NB sessions per month at no marginal cost: a slow,
subscription-paced study over a year costs ~$780 and covers ~18M words, which is
a serious corpus. *Recommended entry point: one month of Professional, NB corpus
plus a pre-2022 control, ≈$65.*

*Instrumentation — revised 2026-07-29 after Matthew asked about cheaper and
local options. The paid detector turns out to be the wrong primary instrument.*

**Tier 1 — prompt-leakage regex (free, hard lower bound).** Not "common LLM
phrases" in the stylistic sense (delve, tapestry, "it is important to note"),
which have real and drifting human base rates. The strong version searches for
**meta-discourse addressed to a requester rather than an audience** — text that
can only appear if model output was pasted without editing. The Bill Oliver line
is the type specimen: an offer to produce a revised version, read aloud in the
chamber. Categories: assistant framing ("Here's a…", "Certainly, here is…",
"I hope this helps", "Let me know if you'd like…"); instruction echoes ("in a
professional tone", "as requested", "a more natural flowing version");
self-identification ("as an AI language model"); unfilled placeholders
("[INSERT NAME]", "[Your Name]"); and markdown artifacts surviving into a
spoken or printed record. Every hit is individually verifiable and quotable, so
this yields a defensible **floor**, not an estimate — the rate will be small,
and the trend plus the specimens are the story.

**Tier 2 — distributional estimation (free, the headline number).** Built on
**Liang, Izzo, Zhang et al., "Monitoring AI-Modified Content at Scale"
(arXiv:2403.07183)**. How it actually works, from the paper:

- It never classifies a document. It models the corpus as a **mixture**: each
  document is drawn from `(1−α)·P + α·Q`, where `P` is the human token
  distribution, `Q` the AI one, and **α — the fraction of the corpus that is
  AI-generated — is the single parameter being estimated** by maximising the
  corpus log-likelihood `Σ log((1−α)P(xᵢ) + αQ(xᵢ))`.
- **The vocabulary is adjectives only.** Every calculation depends solely on
  which adjectives appear in a document; the authors report this is more stable
  than adverbs, verbs, nouns, or all tokens (alternatives in their Appendix D).
  Their headline signal is a frequency shift in ICLR 2024 reviews — *commendable*
  9.8×, *meticulous* 34.7×, *intricate* 11.2× more likely per sentence.
- **`P` and `Q` come from reference corpora**, not from a model's internals:
  `P` from historical documents known to be human-written; `Q` by taking the same
  *writing instructions* given to the humans, prompting an LLM with them, and
  collecting the output. So the AI reference is generated under the real task's
  own brief.
- Their reported cost advantage is enormous — about **seven orders of magnitude
  cheaper than per-document detectors**, while reducing estimation error 3.4×
  in-distribution and 4.6× out-of-distribution.
- They give a **sample-size bound** (Theorem I.1): the error on α̂ shrinks as
  `1/√n` with an explicit constant depending on how separated `P` and `Q` are and
  on α itself. This is the piece that matters for any sampling design — see below.
- Applied result in their case study: **6.5–16.9%** of peer-review text at four
  2023–24 AI conferences was substantially LLM-modified, with corpus-level
  trends they note are too subtle to see per document.

*Mapping onto Hansard:* `P` = pre-2022 sittings from the same chambers; `Q` =
speeches generated by prompting a model with the actual bill text and the
speaking role (the legislative analogue of their "review instructions" trick);
α estimated per session, per chamber, per party, over time. Note their adjective
choice may not transfer — legislative register has its own adjectival habits —
so run their Appendix-D alternatives and pick on stability against the pre-2022
control, not on which gives the biggest number.

**Cost: zero.**

**Tier 3 — local zero-shot detectors (free, validation).** The machine has an
NVIDIA GB10 and 119 GB of RAM, so per-document scoring is a compute question,
not a budget one. Candidates, all verified to exist:
- **Binoculars** (Hans, Schwarzschild, Cherepanova et al., arXiv:2401.12070) —
  zero-shot, contrasts two closely related models, no training required. First
  choice.
- **Fast-DetectGPT** (Bao, Zhao, Teng et al., arXiv:2310.05130) — conditional
  probability curvature; the cheap successor to DetectGPT.
- **Ghostbuster** (Verma, Fleisig, Tomlin et al., arXiv:2305.15047) — features
  from weaker models, no token-probability access needed for the target model.
Use these to score the segments Tiers 1–2 surface, not to sweep the corpus
blind. **Caveat to state in any writeup:** these were validated on essays and
news, mostly against 2023–24 models; legislative oratory is a different register
and 2026 models are harder to detect, so treat their absolute rates as
uncalibrated for this domain.

**Tier 4 — Pangram on a sample (paid, cross-check).** Demoted from the primary
instrument to an independent second opinion on a few hundred segments. At that
volume the free tier (2,000 words/day) or one month of Professional ($65) is
sufficient; the four- and five-figure corpus-sweep estimates below are no longer
the plan, and are kept only to show what the naive approach would have cost.

**Estimator — redesigned 2026-07-29 on Matthew's reframing.** He proposed
treating the question as *"what is the probability that a given piece of text is
flagged AI by Pangram?"* rather than fitting Liang's token-mixture model. That is
a better fit here, and it is standard survey sampling rather than a bespoke
likelihood.

*How Liang models the text, for the record (it is simpler than it sounds):* a
document is a **set** of adjectives, not a bag of counts (deliberately — unique
tokens grow sublinearly with length, so longer documents are not crushed;
they cite the coupon-collector intuition). Per-token occurrence rates are just
`p̂(t) = #documents containing t / #documents`, and the document likelihood is
**independent Bernoulli across the vocabulary**:
`P(x) = Π_{t∈x} p̂(t) · Π_{t∉x} (1 − p̂(t))`, and likewise `Q`. So it is naive
Bayes over adjective presence, with sentences as the unit. The independence
assumption is doing a lot of work, and the adjective vocabulary was tuned on peer
reviews — two reasons not to copy it wholesale into legislative register.

*Our estimator instead.* For a randomly drawn segment let `F = 1` if Pangram
flags it, and let `π = P(F = 1)` in some stratum. Then:

1. **`π̂ = k/n` is a binomial proportion.** Precision is exactly known — with
   n = 1,000 and a true rate near 5%, the 95% interval is about [3.8%, 6.5%];
   n = 2,000 gives [4.1%, 6.0%]. No modelling assumptions at all.
2. **`π` is instrument-dependent, so correct it.** What we want is the true rate
   `τ`, related by `π = τ·Se + (1−τ)·(1−Sp)` for detector sensitivity `Se` and
   specificity `Sp`. Inverting gives the **Rogan–Gladen prevalence estimator**,
   `τ̂ = (π̂ + Sp − 1)/(Se + Sp − 1)` — standard epidemiology for screening with
   an imperfect test (Rogan & Gladen, *Am. J. Epidemiology*, 1978 — **verify the
   handle before citing**).
3. **Both nuisance parameters are measurable in-domain, cheaply.** The pre-2022
   control *is* the estimate of `1 − Sp`, the false-positive rate on exactly this
   register — so the negative control stops being a sanity check and becomes a
   parameter. `Se` comes from generating known-AI legislative speech (Liang's `Q`
   trick: prompt with the real bill text and speaking role) and scoring it.
   Nothing here needs the vendor's published accuracy claims.
4. **Watch the correction's leverage.** Variance is amplified by
   `1/(Se + Sp − 1)`: about 1.06× at Se .95/Sp .99, 1.25× at Se .85/Sp .95. And
   when `π̂ < 1 − Sp` the point estimate goes negative — truncate at zero and
   report the interval, never the truncated point alone. At Se .90/Sp .97 a 3%
   flag rate corrects to ≈0%, which is the honest and important answer: at low
   true prevalence, a detector this good still cannot distinguish signal from its
   own error floor.

**Two-phase design — this is where Matthew's expand-from-samples idea becomes
principled.** Phase 1: run the free local detectors (Binoculars et al.) over the
*entire* corpus, giving every segment an auxiliary score. Phase 2: draw a
stratified sample on that score × year × chamber and pay for Pangram only there.
This is textbook two-phase sampling for stratification, and it has a property
worth stating plainly: **the free detector does not need to be accurate — only
correlated with the truth — to cut the variance of the paid estimate.** Its
errors bias nothing, because stratum weights are known exactly from the full
corpus. Expanding into a flagged speaker's other speeches is then the same
mechanism applied at the speaker level, which is also the only way to get
per-speaker estimates stable enough to report.

*Also handle:* segments within a speech or sitting are correlated, so use
cluster-robust variance (or the design effect `1 + (m−1)ρ`) rather than treating
segments as independent. Sample whole speeches as clusters.

*Cost at this design:* 2,000 segments of ~150 words is 300k words ≈ **$120** at
the bulk API rate, and **fits inside a single $65 Professional month**. Even
5,000 segments of 300 words (1.5M words) fits that month's allowance. The
corpus-sweep pricing below is now purely historical.

*Liang is out of the plan (decided 2026-07-29), kept as a reference only.* Its
mixture estimator is a good paper and the source of the `Q`-by-prompting trick we
still use, but running two estimators means defending two sets of assumptions,
and the corrected-sample design above is both simpler and better matched to the
instrument we actually trust.

*Session plan:* `plans/S10-legislative-ai-detection.md` — self-contained
starting point (detector survey, NB pilot, corpus search, throughput/batching).

*Pilot (2026-07-29, `analysis/s10/` + PILOT.md there):* full pipeline ran on
all 38 sittings plus a 6-sitting 2019 control. Three results. (1) Throughput:
Falcon-pair Binoculars scores the whole corpus+control (1.21M tokens) in
40 min on the GB10 — 509 tok/s end-to-end, and the GPU was discovered
clock-capped at 513/3003 MHz (fix needs root), so that is a floor with ~5.9×
headroom; Qwen3-1.7B pair runs ~2–3× faster. A 260M-token multi-legislature
sweep is overnight-to-days scale — the two-phase design stands. (2) Substance:
2025–26 raw flag rates sit BELOW the 2019 pre-ChatGPT false-positive floor
(2.85% vs 5.64% acc-threshold; 0.53% vs 1.03% low-FPR), so Rogan–Gladen gives
τ̂ = 0 at the pilot's sensitivity (bound in `analysis/s10/`); Tier-1 leakage regex: 0 hits in 993k
words (edited-record caveat). No detectable machine share via this
instrument — a null that is partly about the instrument (2023-era detector,
2026 text; Se unmeasured). (3) Design finding: the score distribution DRIFTS
between eras (2019 reads more AI-like than 2025–26), and the drift
REPLICATES across architectures (Falcon-7B and Qwen3-1.7B pairs, ρ≈0.73
agreement) — a property of the record, not the detector — so Sp/threshold
transport across eras is invalid — Se/Sp must be measured per era, add
within-era human anchors (spontaneous crosstalk), keep Pangram as the
second instrument. Bonus discovery: NB's two-column record puts language-as-
spoken in the left column, so speaker-authored English (709k words) separates
cleanly from translator-authored English — validated per speaker.

*Status:* pilot done; corpus + control archived with the pipeline in
`analysis/s10/`. Next: in-domain per-era `Se` corpus (highest value), the
detector survey (Task 1), prepared-vs-spontaneous labels, Pangram stratified
sample, Hansard Office request for the Bill Oliver sitting. Remaining
decisions unchanged: estimator code, and which model generates `Q`
(plausible-vintage, not necessarily 2026-frontier).

