# Machine-drafted speech in legislatures: prevalence, concentration, and a register that predates the machines

**S10 — draft write-up, 2026-08-11.** All arms complete, including the
detector-bypass study and both prior-art comparators. Everything is
reproducible from `analysis/s10/`.

**Numbers marked † are carried from earlier in the study.** All nine were
re-derived from their artifacts on 2026-08-11 and reproduce; footnotes on each
give the script and invocation. Two of the nine (§4.6's cohort share, §4.7's
pooled alignment effect) were briefly and wrongly recorded as unsourced — the
verification pass had looked in the wrong script — so their footnotes name the
right one explicitly. Everything unmarked was computed or re-verified on
2026-08-09/11 and names its source file.

---

## 1. The question, and why it needs two instruments

How much legislative speech is machine-drafted, and what does its arrival do
to deliberation?

The question splits in two, and conflating them is the main error available
here:

- **Prevalence** — how much text in the record was drafted by a machine. This
  needs a calibrated detector.
- **Permeation** — whether human speech is drifting toward machine register
  independent of drafting. This needs instruments that do *not* depend on a
  detector, because the human baseline is itself the thing moving.

S10 runs both, and reports them as separate claims. The prevalence arm is the
headline; the permeation arm is the more surprising result, and the weaker
one.

---

## 2. Data

Nineteen chambers across four countries, extracted from official Hansard and
the Congressional Record:

| group | chambers |
|---|---|
| Canada | federal House of Commons, AB, BC, MB, NB, NL, NS, ON, SK |
| Australia | NSW, QLD, SA, TAS, VIC, WA |
| UK/Ireland | House of Commons, Scotland, Wales, Northern Ireland, Dáil Éireann |
| US | House, Senate |

Per chamber, two strata:

- **control** — 60 segments dated on or before **2022-06-30**. Not
  2022-12-31: ChatGPT shipped 2022-11-30, and a "pre-AI" control dated
  December 2022 is not pre-AI. Every chamber had ample earlier material, so
  the tighter cutoff cost nothing.
- **prevalence** — 120 segments dated 2025-01-01 or later, sampled uniformly
  at random with no screen stratification, so the estimate needs no
  reweighting.

Segments are 120–360 words, member-authored, English-original, non-chair.
Sampling is seeded per cell and reproducible (`build_pangram_expansion.py`).

### 2.1 Two contamination hazards, both found by looking

**Invisible characters.** Manitoba's 2025-26 files carry soft hyphens
(U+00AD) in 81.6% of segments against 0.04% of tokens in 2006-19. Left in,
that is period-correlated noise a detector could latch onto with nothing to
do with drafting. Stripped at build time.

**Transcription regime.** A chamber that moved from edited Hansard to
verbatim or ASR-assisted transcription will shift on exactly the surface
features a detector reads, with nobody having drafted anything by machine.
`transcript_regime_check.py` measures two markers that track editorial
convention rather than content — words per sentence, and contraction density
(traditional Hansard expands "don't" to "do not"; verbatim transcription does
not) — random-sampled per chamber-year.

Findings, and they cut against the received story:

- The Aug-2026 policy scan named **NSW and WA** as ASR users. Both are
  **flat across 2006–2026** on both markers. Whatever they procured has not
  visibly changed the text.
- **Tasmania** — named by nobody — moved: contraction density **3.4 → 15.9
  per 1,000 words, +364%**, with the step falling *between* the control and
  prevalence windows. No pre-AI text exists in Tasmania's current regime, so
  no control can calibrate it. **TAS is reported but excluded from pooled
  estimates.**
- **NL (2016), WAL (2015), MB (2007)** step *inside* the control window.
  Their controls were floored to the current regime — still comfortably
  pre-AI, so nothing was lost.

---

## 3. Method

### 3.1 The calibration that carries the argument

Prevalence is only meaningful against a measured false-positive rate. **A
chamber's false-positive rate depends on its own editorial register, so
specificity is not transferable** — each chamber buys its own 60-segment
pre-AI control. This is the single most important design choice in the study
and the reason its result differs from published comparators (§7).

With specificity `Sp` and sensitivity `Se`, an observed flag rate `π` relates
to true prevalence `τ` by Rogan–Gladen:

```
π = τ·Se + (1−τ)(1−Sp)      ⇒     τ = (π − (1−Sp)) / (Se − (1−Sp))
```

When `Sp = 1` this collapses to `τ = π/Se`. `Se` is estimated in-domain from
synthetic AI legislative speech written to imitate the chamber's own
business, not generic essays.

### 3.2 Detector, and a defect worth recording

All verdicts are **Pangram 4**. This is not a detail. The Pangram API's
default model is **Pangram 3** (version 3.3.2), while the web dashboard runs
Pangram 4. On a 20-segment sample deliberately enriched for AI and Mixed, the
two agreed on **11/20** — the default called Human on 3 of 8 web-AI segments
and 5 of 6 web-Mixed, and never returned Mixed at all. Passing
`model: "pangram-4"` gave **20/20 exact agreement including all six Mixed**
(`api_route_check.py`).

So the API and dashboard routes are interchangeable, *but only when the model
is named*, and the failure is silent — you get verdicts, they just aren't the
same instrument. Billing corroborates it independently: the dashboard's
`ceil(words/100)` credit rule is exactly Pangram 4's $0.05-per-100-words,
while the defaulted API billed per document at Pangram 3's 1,000-word unit.

The 2026-07 New Brunswick run passed no model parameter and silently took
Pangram 3. It was rescored (§4.1).

### 3.3 Why the frequency arm is descriptive, not inferential

This belongs in methods rather than an appendix, because it explains the
framing of §4.5.

The Kobak et al. excess-vocabulary approach (arXiv:2406.07016; *Sci Adv*
11(27):eadt3813, 2025) compares observed word frequencies against a
counterfactual built from prior years. Applied naively to Hansard it produces
a large, confident-looking post-2022 signal.

**It has no trend control.** `in_time_placebo.py` runs the identical
estimator on *pre-LLM* window pairs, where the true effect is zero by
construction. It fires there too. An estimator that reports a large effect on
a period when nothing happened is measuring drift, not treatment.

The arm is therefore reported as a **descriptive series**, not as evidence of
LLM causation. This is what makes the 1994–96 onset (§4.5) interesting rather
than embarrassing: the register was already moving decades before the
machines.

### 3.4 Instruments retired, and why

Named here because a reader needs to know what was tried and dropped, not to
pad an appendix:

| instrument | outcome | why dropped |
|---|---|---|
| Zero-shot detectors (Binoculars/Falcon, Fast-DetectGPT, Qwen pairs) | 2025-26 flag rates sat **below** their own pre-LLM false-positive floors | edited AI is invisible to them; retro-explains every pilot null |
| Corpus-wide likelihood delta | triple-replicated null | no signal at corpus scale |
| Frequency-weighted secondary | fired in 4/30 cells | indistinguishable from noise |
| Content-word control | orthogonal to the claim | words rising elsewhere says nothing about here |
| Mistral synthetic control corpus | deleted | replaced by in-domain synthetic Se |

---

## 4. Results

### 4.1 Calibration: 1,260 / 1,260

**Zero false positives across every chamber's own pre-AI control.**
Specificity **100.00% [99.7%, 100.0%]** (Wilson). In-domain sensitivity
**Se = 1.000** (n=40 synthetic legislative speech), so the Rogan–Gladen
correction is the identity and **observed rate = calibrated prevalence**.
(`prevalence_report.py`)

**New Brunswick rescore.** 658 segments, byte-identical stored text, Pangram
3 vs Pangram 4:

| | Pangram 3 | Pangram 4 |
|---|---|---|
| pre-AI control (n=60) | 60/60 | 60/60 |
| 2020 / 2021 / 2022 | 0% flagged | 0% flagged |
| synthetic-AI sensitivity | 100% | 100% |
| AI + Mixed, overall | 122 | **144** |
| exact agreement | | 92% |

Specificity is **identical**. The model-tier defect was an **undercount, not
a false-positive problem** — disagreements run net upward (33 segments moved
out of Human, 9 the other way). Earlier NB conclusions stand as conservative.
(`nb_p3_vs_p4.py`)

### 4.2 Prevalence: 12.4%, with a sevenfold spread

**Pooled 275/2,220 = 12.4% [11.1%, 13.8%]**, excluding regime-flagged TAS.

| chamber | flagged | 95% CI | | chamber | flagged | 95% CI |
|---|---|---|---|---|---|---|
| NSW | **23.3%** | [16.7, 31.7] | | AB | 11.7% | [7.1, 18.6] |
| CA-FED | 22.8% | [17.3, 29.4] | | VIC | 10.8% | [6.4, 17.7] |
| QLD | 20.8% | [14.5, 28.9] | | SA | 10.0% | [5.8, 16.7] |
| NI | 20.0% | [13.8, 28.0] | | WAL | 7.5% | [4.0, 13.6] |
| BC | 16.7% | [11.1, 24.3] | | SK | 6.7% | [3.4, 12.6] |
| US House | 15.0% | [9.7, 22.5] | | WA | 5.8% | [2.9, 11.6] |
| NS | 14.2% | [9.0, 21.5] | | MB / NL / SCO | 5.0% | [2.3, 10.5] |
| ON | 14.2% | [9.0, 21.5] | | **US Senate** | **3.3%** | [1.3, 8.3] |
| *TAS (flagged)* | *11.7%* | *not pooled* | | | | |

The spread is the finding, not noise around a mean. **US House 15.0% vs US
Senate 3.3%** is the sharpest contrast available: two chambers of one
legislature, near-identical AI policies, differing 4.5-fold.

### 4.3 Genre: drafting concentrates in scripted business

Federal Canada is the only corpus carrying a business rubric, which makes
this test possible at all.

The three genres form a ladder in **how much advance preparation the
procedure permits**, which is the mechanism under test:

- **SO31 — Statements by Members.** Under Standing Order 31 a non-minister
  may address the House for up to one minute on any subject, immediately
  before Question Period. Not debatable, no reply. Written ahead and read.
- **Government Orders.** Government bills and motions. Covers both prepared
  speeches (20 minutes for early slots, 10 later) **and the spontaneous
  questions-and-comments periods that follow each one** — a genuinely mixed
  category, not pure prepared debate.
- **Oral Questions.** The 45 minutes after SO31. **Questions are not placed
  on notice**, so neither question nor answer can be fully drafted in
  advance; both sides are held to roughly 35 seconds.

| genre, 2025–26 | flagged | 95% CI |
|---|---|---|
| **SO31** — one-minute scripted set-pieces | **36.7%** | [25.6, 49.3] |
| Government Orders — mixed prepared and spontaneous | 23.3% | [14.4, 35.4] |
| **Oral Questions** — not on notice | **8.3%** | [3.6, 18.1] |
| all three pre-AI controls | **0.0%** | [0.0, 6.0] |

**SO31 vs OQ: 4.40×, Fisher exact two-sided p = 0.00034.**

The ordering is exactly what the mechanism predicts — the more preparable the
format, the more machine drafting — and it is the one place where the lexicon
arm's inference is confirmed by an independent instrument. Two instruments
agreeing is worth more than either alone.

**The sampling runs against the finding, which makes it conservative.** The
120–360-word filter retains 95.2% of SO31 segments but only **6.4% of Oral
Questions** (median QP utterance is 89 words). The OQ cell is therefore the
long tail of Question Period, which skews toward *prepared ministerial
answers* rather than rapid exchange — the sub-population most likely to be
machine-drafted. We sampled the most preparable end of the unscripted genre
and it still came in lowest. Government Orders' middle position is likewise
what a mixture of both ends would produce.

Extraction is paragraph-level throughout, so no genre loses whole speeches to
the length cap; the differential retention above is a property of natural
utterance length, not of truncation.

### 4.4 The Opus screen tracks Pangram

A blinded LLM screen over the full corpus (37,801 segments, date-blind)
separates Pangram's classes cleanly on the 618-segment overlap:

| Pangram verdict | n | mean Opus score |
|---|---|---|
| AI | 78 | 50.9 |
| Mixed | 26 | 44.8 |
| Human | 514 | **11.9** |

This matters for two reasons: it is a cheap stratifier for future work, and
the **disagreements are informative** — 45 Pangram-AI hits score below 50 on
Opus, 9 below 30. Those are naturally occurring partial bypasses and seed the
study in §4.9.

**Reasoning effort buys nothing here, and that is worth stating rather than
hiding.** The screen's headline figure — **AUC 0.951** against Pangram on the
241-segment labelled pool — was produced at `effort=low`, and low had never
been compared against anything. Re-run on the same pool with the prompt and
batching held byte-identical:

| run | AUC | 95% CI |
|---|---|---|
| archived low | 0.951 | [0.925, 0.973] |
| fresh low (replicate) | 0.942 | [0.914, 0.968] |
| **max** | **0.942** | [0.912, 0.967] |

The low-effort run was replicated precisely so the comparison has a noise
floor. |archived − fresh| = **0.009**; max − mean(low) = **−0.005**. The
effort gap is smaller than run-to-run variation, and negative. Per-segment
correlations agree: low-vs-low r = +0.976, low-vs-max +0.959 and +0.960 —
max is not scoring differently and losing, it is scoring the same way with
slightly more scatter.

Against a single low run, max would have looked like a −0.009 decline and
been tempting to report as an effect. Two low runs differ by exactly that
much. **The replicate is what makes the null readable.**

This also cuts against the pattern in the open models, measured on the same
pool: effort moved Qwen3-32B by **+0.172** and gpt-oss-120b by **+0.015**,
against **−0.005** for Opus. Reasoning closes part of the gap for weak
detectors and does nothing for a strong one — consistent with §3.4's finding
that reasoning never closes the ~0.25 AUC frontier gap, but sharper: the
frontier model is not reasoning its way to 0.951, it is recognising something
at a glance. Practically, it means the screen can be run at a fifth of the
cost with no loss. (`opus_effort_ab.py`, `opus_effort_ab.csv`)

### 4.5 The register shift starts in 1994–96, decades before the machines

Descriptive series (§3.3), UK Commons extended back to 1985. The register
*declines* through the late 1980s and turns upward around **1994–96** —
before the consumer web, and long before any language model. Whatever this
measures, LLMs did not start it.[^r45]

[^r45]: `python long_trend.py --seg uk/segments_uk_deep.jsonl`. The turning
    point is the minimum of the fitted series; it lands on 1994 exactly. The
    "1994–96" range in the text is the flat region around that minimum, not
    an interval estimate.

Read together with §4.7, the interesting reading is not "LLMs changed
parliamentary register" but that **human register had been moving toward what
instruct-tuning later selected for, for thirty years.** †

### 4.6 Cohort replacement, not incumbent conversion

- Arrivals bring **+1.87 per 1,000** more than incumbents (15/16 chambers). †[^r46a]
- Birth decade predicts at **t ≈ 12**; occupation and education both run the
  wrong way. †[^r46b]
- Cohort is separable from age: chamber age is flat while the register rises;
  cohort accounts for **~60%** of the change. †[^r46c]

[^r46a]: `python arrival_premium.py`. CI [+1.25, +2.49], clustered on member.

[^r46b]: `python formation_window.py`. t = +12.06 unadjusted, +13.22 with
    occupation and education controls — the controls *strengthen* the cohort
    term, which is why they are reported as running the wrong way for a
    selection story.

[^r46c]: Not a decomposition — an arithmetic closure. Mean birth year advances
    **13.8 years** across the window; at the fitted **+0.093 per year** that
    predicts **+1.28** of the observed **+2.06**, i.e. ~60%. Distinct from the
    within/between split in the next bullet, which asks a different question
    (`decomposition_inference.py`) and attributes essentially all of the
    change to composition: between +2.18 against within −0.42.
- **Incumbents are flat, not falling.** Pooled within-member change is −0.42,
  CI [−1.32, +0.49] — not significant. An earlier claim that sitting
  legislators' register fell was wrong; it did not survive clustering on
  member. (`decomposition_inference.py`)

Stated conclusion: **generational, mechanism unidentified.** Three exposure
tests failed to identify it (Appendix A).

### 4.7 The register is a post-training artifact

OLMo-2 ladder, same prompts across the post-training stages:

| stage | register shift |
|---|---|
| SFT | +0.76 † |
| DPO | **+0.86** † |
| RLVR | +0.37 † |

Pooled alignment effect **+0.88** †.[^r47] The shift is largest at the
preference stage, which is what makes §4.5 more than a coincidence of
direction: the thing RLHF selects for is something humans were already
drifting toward.

[^r47]: Ladder stages: `python olmo_ladder.py` (end-to-end base→instruct
    **+1.2420**). The pooled **+0.88** is a *separate* experiment on two other
    model families — `python rlhf_pref_analyze.py`, which prints
    `EXCESS +0.8797, p < 0.001` (Qwen3-8B and Mistral-7B, 668 and 788 prompt
    pairs, Kobak style words against frequency-matched controls). It is not a
    pooling of the three OLMo stages, and it is not produced by
    `align_ratio.py report`, which prints the Hansard-drift arm instead.
    Recorded here because looking for it in the wrong script is how it came to
    be mistaken for an unsourced figure.

### 4.8 Permeation: detector-independent and small but positive

In-context likelihood of the Kobak style words within Hansard traces,
self-normalised, no placebo word list, no external control:

**+0.0099, CI [+0.0007, +0.0196], positive in 9/10 cells.** †[^r48]

Small, but it is the only permeation evidence that does not route through a
detector, and it survives the failure mode that demoted the lexicon arm.

[^r48]: `python word_context_delta.py`. Per-model cell table at
    `METHODOLOGY.md:1009`; the Qwen row reproduces exactly on re-run.

### 4.9 Quality: better-formed, not worse-engaged — and evadable under effort

Graded against the Discourse Quality Index (Steenbergen, Bächtiger, Spörndli
& Steiner 2003), using the original authors' own codings of a 1998 UK Commons
debate as in-context anchors. Two of the seven dimensions carry a `-1`
inapplicable code — no other demand, or no counterargument, on the table —
which is **excluded from means rather than scored as zero**. Folding it in
would score "nothing to engage with" as worse than "engaged badly", and
manufacture an engagement penalty wherever machine text is more monologic.

Two pools were graded, 2026-08-10.

The instrument was first checked for reproducibility on a different account
before any new pool was graded: it reproduces at or above its own published
repeat-pass band, and the claim-bearing gaps keep their signs. Detail in
**Appendix C**.

**Stages 1 and 2 — the finding, and the half of it that does not survive.**
Stage 1 is 840 genre-balanced federal-Canadian segments labelled by a blinded
LLM screen; stage 2 is 682 segments across 22 chambers labelled by **Pangram
verdict**, with chamber fixed effects. Different populations, different label
sources, same answer.

| dimension | stage 1, + genre & era FE | stage 2, + chamber FE |
|---|---|---|
| justification | **+1.134** (t +4.1) ✱ | **+0.290** (t +4.4) ✱ |
| common_good | **+0.583** (t +3.3) ✱ | **+0.229** (t +4.5) ✱ |
| respect_groups | **+0.287** (t +2.0) ✱ | **+0.220** (t +6.1) ✱ |
| respect_demands | −0.179 (t −0.5) | −0.029 (t −0.4) |
| respect_counterargs | +0.143 (t +0.4) | +0.073 (t +1.0) |
| constructive | −0.015 (t −0.1) | −0.041 (t −1.0) |
| evidence | +0.350 (t +1.4) | +0.065 (t +1.1) |

**The revised claim: AI-assisted legislative speech is better-formed — more
justified, more common-good framed, more positive toward the groups a policy
would help — and shows no engagement penalty once genre or chamber is held
fixed.**

**"Deliberation down" was genre.** Uncontrolled, stage 1 gives respect_demands
−0.662 (t −2.4)✱ and respect_counterargs −0.695 (t −2.4)✱ — the original
finding. Holding genre fixed sends both to null, and counterargs flips sign.
The genre-balanced pool existed to run exactly this test, and it answers
negatively. **This supersedes "form up, deliberation down"** (Appendix B).

Three further observations, in descending order of how much they should
change a reader's confidence:

1. **The original run already contradicted itself on this dimension.** Its two
   group-pairs disagreed in sign on respect_demands: candidate-AI minus
   candidate-human = **−0.356**, but uniform-sample AI minus human =
   **+0.650**. The engagement claim rested on the first; the second, drawn
   without screen selection, pointed the other way. The genre control explains
   why.
2. **Justification is a suppression effect, not a new result.** It is null
   uncontrolled (t −0.2) and strongly positive within genre (t +4.1), because
   machine drafting concentrates in SO31 and **SO31 has the lowest
   justification of any genre** (1.14, against 2.01 for government business).
   Pooling across genres hides an effect that is plainly there inside each.
3. **Judge leakage is substantial.** The blinded screen's `ai_guess` and the
   grading judge's independent `ai_guess` correlate at **r = +0.758**. Both
   are partly reading the same style signal, so the fixed-effects columns are
   what carry the quality claim; the raw contrasts should not be quoted alone.

**Bypass study.** Prevalence counts machine text a detector can see. If a
member can defeat the detector cheaply, 12.4% is a floor and detection-based
prevalence is a dead end. Four search runs across two chambers, **461
rewritten variants of 130 flagged originals**, each variant scored by Pangram.
Selection differs between runs and the differences matter; the filter stack for
each is set out in `BYPASS_METHODOLOGY.md` and summarised in Appendix C.

**The headline: asking a general-purpose model to rework a speech in a loop
beats the commercial evasion industry by about tenfold.** No fine-tuning, no
detector access, no evasion tooling — Opus, a rewrite prompt, and six rounds
of keep-the-best. Against the 13 commercial "humanizer" services benchmarked
in Pangram's own technical report, which get **2.31%** of documents past it,
this gets **24.6%** of targets past it: **10.6×**.[^r49a] Against Pangram's
clean-conditions false-negative rate of 0.34%, it is 72×.

That is the finding. The detector is not weak — its specificity is 0 in 1,260
(§4.1), and a single "make this sound human" prompt makes text *more*
detectable, not less. But the gap between a purpose-built evasion product and
a frontier model told to try again is an order of magnitude in the frontier
model's favour, and it will not narrow in the detector's direction.

One asymmetry to keep visible: the 2.31% is a **one-shot** rate, while 24.6%
allows up to eighteen attempts. Like-for-like on single attempts the multiple
is **3.7×** (8.5% against 2.31%). The tenfold figure is the honest one for an
actor bypassing a *given* text, because discarded drafts cost them nothing;
the 3.7× is the honest one for comparing instruments. Both are below.

**Two rates, and both belong here.** They answer different questions and the
gap between them is threefold, so quoting either alone misleads.

**The conservative figure — 8.5% per variant, all four runs.** How often a
single rewrite attempt defeats the detector.

| | variants | Pangram says Human | `fraction_ai = 0.0` |
|---|---|---|---|
| NB v2 blind search | 40 | 1 | 1 |
| NB v3 contrastive | 212 | 29 | 29 |
| GO Opus-selected | 80 | 0 | 0 |
| GO all-31 uniform | 129 | 9 | 7 |
| **pooled** | **461** | **39 = 8.5%** [6.3, 11.4] | **37 = 8.0%** [5.9, 10.9] |

Restricted to unambiguously AI-seeded originals the rate is unchanged: 34/400
= 8.5% by label, 32/400 = 8.0% strict. This is the right number when the claim
is about the *detector*, and it is deliberately harsh on ourselves: it keeps
two superseded searches in the denominator, including the badly-seeded run
that produced nothing.

**The operational figure — 24.6% per target, best method only.** An adversary
does not care how many drafts they discard; they care whether the speech they
wanted through got through. Taking only the **final search in each chamber**
and asking on what fraction of *targets* at least one variant reached a clean
Human verdict:

| | targets | ≥1 Human | ≥1 at `fraction_ai = 0.0` |
|---|---|---|---|
| NB v3 contrastive | 38 | 10 = 26.3% | 10 = 26.3% |
| GO all-31 uniform | 27 | 6 = 22.2% | 5 = 18.5% |
| **pooled** | **65** | **16 = 24.6%** [16, 36] | **15 = 23.1%** [15, 35] |

**About one flagged speech in four can be walked past the detector**, at a
budget of six rounds and three variants per round. This is the figure a fresh
study replicating our best method should expect to reproduce, and the more
honest description of the exposure a chamber actually faces.

Two things make it more trustworthy than its interval suggests. The strict
criterion barely moves it — exactly one target loses its only reversal. And
the two chambers agree closely (26.3% and 22.2%) **despite contradicting each
other on which edits work**: their hypotheses agree on repetition and
unglossed idiom and flatly disagree on sentence rhythm. The rate transfers;
the playbook does not.

**Against 0 AI labels in 1,260 genuine pre-AI controls (§4.1).** That is what
makes the reversals worth reporting: they are movements *into* a class the
detector otherwise reaches zero times out of 1,260. This is not a detector
that is merely noisy at the boundary — it is one with a hard specificity floor
that a directed search nevertheless walks text across.

**Naming the quantity precisely, because the comparison is easy to get wrong.**
Ours is an **induced false-negative rate** under attack, and it is *not* the
same measurement as a vendor's published FNR, for two reasons that must travel
with the number. First, ground truth is a Pangram verdict on the *original*,
not known authorship — a "false negative" here means the detector reversed
itself on text it had flagged, not that a machine demonstrably wrote it.
Second, the variants are the surviving output of a search that optimised
against a correlated proxy, so this is a rate under adversarial pressure
rather than under clean conditions.

| measurement | rate | what it is |
|---|---|---|
| Pangram 4, clean | 0.34% | FNR, known-AI text, vendor-reported |
| Pangram 4, 13 humanizer services | 2.31% | FNR under commercial evasion, vendor |
| Pangram 4, BLADER de-AI agent | 0.43% | FNR under agentic evasion, vendor |
| Pangram 4, Perkins benchmark | 2.86% | FNR, doc-level, adversarial, vendor |
| **this study, per variant** | **8.5%** | **induced FNR, one attempt, 461 variants — 3.7× the humanizers** |
| *this study, per target* | *24.6%* | *induced, ≤18 attempts — 10.6× the humanizers* |
| Rice 2026, Australian Hansard | ~8% | **false *positive* rate**, n = 50 |

**Only the per-variant row is commensurable with the vendor rows**, which are
one-shot document-level rates on known-AI text. The per-target row is
italicised because it allows up to eighteen attempts per document, and no
published benchmark grants that; it is the right number for exposure, the
wrong number for a detector comparison. The Rice row is included because the
numeric coincidence invites a comparison that does not exist: his ~8% is a
false-positive rate on 50 pre-ChatGPT speeches, measured on an LLM judge
rather than on Pangram (§7). The vendor rows are vendor-reported on
undisclosed test data and should be read as such; independent evaluations
(RAID, Dugan et al. 2024; Weber-Wulff et al. 2023) consistently find detectors
fail toward false negatives under obfuscation, which is the direction our
result also points.

**Both rates move with effort, and that is the real caveat on each.** The
blind v2 search flipped 10% of variants; the contrastive v3 search 28%. If
"soften off AI" rather than "reach Human" is the bar, 17 of 38 New Brunswick
targets (45%) cleared it. So 8.5% and 24.6% bound what two days and four
searches achieved, not what is achievable.

**A correction to an earlier claim.** We previously reported that Pangram's own
uncertainty predicts evasion, at "22% for AI seeds against 76% for Mixed". That
figure was computed on the first 100 of 129 variants, and the two halves are
not the same statistic: it counted "not confidently AI" as success, which
scores a Mixed-seeded text that *stayed Mixed* as an evasion. Like-for-like, on
the full run, using the one outcome that is a genuine state change for both
seed types:

| seed verdict | variants | → AI | → Mixed | → Human |
|---|---|---|---|---|
| AI | 68 | 54 | 10 | 4 = 5.9% [2, 14] |
| Mixed | 61 | 17 | 39 | 5 = 8.2% [4, 18] |

Fisher exact **p = 0.735**. The per-text figures run in the same direction and
are larger (2/16 against 4/11) but rest on 27 texts. **The hypothesis that
borderline originals are the vulnerable ones remains plausible and remains
unestablished**; it should not be quoted as a finding. What is established is
that 28% of Mixed-seeded variants moved the *wrong* way, to AI — a directed
search against this detector is not monotone.

**The label and the score disagree at the boundary, and the interface hides
it.** Of the 9 Government Orders reversals, one (`ga033`) came back **Mixed at
`fraction_ai` 0.67** on re-scan rather than Human at all, and another
(`ga092`) was Human at 0.10 rather than 0.0 — about 11% verdict instability on
the same text and the same model. New Brunswick showed none: all 30 of its
Human labels re-scanned at exactly 0.0. The dashboard reports a categorical
label, so a user reads "Human" as "a person wrote this"; the continuous score
underneath sometimes says something weaker. Both numbers are therefore reported
throughout this study, and the gap between them — half a percentage point
pooled — changes no conclusion here.

**Evasion does not cost deliberative quality.** Two paired arms, 63
within-text pairs, blinded and interleaved, graded on the same v2b DQI rubric:
stage 3 is 38 New Brunswick pairs, stage 4 is 25 Government Orders pairs. Every
dimension is null on both, adjusted for length.[^r49b]

| dimension | stage 3 (n=38) | stage 4 (n=25) |
|---|---|---|
| justification | +0.05 (t +0.6) | −0.17 (t −0.8) |
| common_good | −0.05 (t −0.8) | −0.05 (t −0.2) |
| respect_groups | −0.08 (t −1.8) | +0.04 (t +0.9) |
| respect_demands | −0.14 (t −1.0) | +0.08 (t +1.0) |
| respect_counterargs | +0.24 (t +1.3) | +0.05 (t +0.5) |
| constructive | −0.00 (t −0.0) | −0.01 (t −0.1) |
| evidence | +0.02 (t +0.4) | −0.08 (t −0.2) |

Stage 4 also settles a residual worry from stage 3: justification rises +0.16
raw (t +1.7) and goes *negative* once word count enters, so the apparent gain
was length. Humanized variants run ~30 words longer at the median.

**What this means for the prevalence number.** Evasion is real, clears the
detector on about one flagged speech in four under directed search, and is free
in deliberative-quality terms — so 12.4% is a floor, and the honest reading is
that it measures *undisguised* machine drafting. But it is not free in effort:
it took a frontier model, contrastive exemplars mined from matched human text,
and a multi-round search scoring three replicates per variant. A single
"make this sound human" prompt does the opposite — instructed rewriting *raises*
Pangram's score, and human text pushed through the same ladder went from 11.7
to 60.2. The gap between "a detector can be beaten" and "a detector is easy to
beat" is the whole of that apparatus.

[^r49a]: `python bypass_report.py`, which reads the four verdict files and
    prints every figure in this subsection, including the Wilson intervals and
    the Fisher test. Strict re-scores in `nb_reflip_fractions.json`,
    `bp_reflip_fractions.json`, `go_reflip_fractions.json`. Rewritten variant
    text is held locally and excluded from the repository under the corpus
    licence policy.

[^r49b]: `cd quality_expansion && python analyze_stage3.py [RUNDIR]` and
    `python analyze_stage3.py --key4 [RUNDIR]`; values cached in
    `results_stage34.json`. Quoted column is the intercept with
    (humanized − original) word count as covariate. `-1` (inapplicable) pairs
    are excluded, which is why the two sentinel dimensions have smaller n
    (12 and 12 in stage 3; 18 and 16 in stage 4).

---

## 5. Limits

- **Prevalence is a floor.** Detectors see undisguised machine text. A
  directed search clears the detector on 8.5% of variants and **24.6% of
  targets** (§4.9), so 12.4% is a lower bound. How much of a lower bound is
  not estimable from this design: we can measure how often evasion succeeds
  when attempted, not how often it is attempted.
- **The evasion rate is an upper bound on our own effort, not on anyone's.**
  Four runs over two days with a frontier model. A staff tool refined over
  months, or a local model fine-tuned against the detector, is a different
  adversary and we did not test one.
- **Tasmania is uninterpretable** and excluded. Other chambers passed the
  regime diagnostic, but the diagnostic uses two markers, not all of them.
- **Mixed is pooled with AI** throughout. Reported separately in the CSV.
- **The permeation effect is small** and rests on one instrument.
- **Cohort mechanism is unidentified.** Three exposure tests null.
- **No chamber requires AI disclosure**, so no ground truth exists anywhere;
  every number rests on detector calibration rather than admission.
- **Single detector.** Specificity is measured, but Pangram 4 is one vendor.
- **Judge leakage.** Screen and grading-judge AI guesses correlate at
  r = +0.758, so the quality claim rests on the fixed-effects columns, not
  the raw contrasts (§4.9).
- **Genre cells are not equally representative.** The length filter retains
  95% of SO31 but 6% of Oral Questions (§4.3). The direction of that
  selection is conservative for the reported gradient, but it means the OQ
  figure is not an estimate of Question Period as a whole.
- **The quality arm is LLM-graded.** Repeat-pass and cross-account agreement
  both sit at or above the published human inter-coder bar, but
  self-agreement is not inter-coder agreement; the human-coded subsample
  remains the real validation and is not done.

---

## 6. Policy context

A 22-chamber scan found **zero chambers requiring AI-drafted text to be
disclosed in the record, and none forbidding AI drafting.** Where rules
exist they are IT-security instruments issued by Clerks and CIOs, not rules
of authorship. The structural pattern: **where a Clerk governs staff, rules
are detailed; where members govern themselves, there is nothing.**

Strictest is the US House (HITPOL 8). The UK is the only chamber to address
the question directly, and resolves it permissively — AI-generated content in
proceedings is the member's own, "protected by privilege regardless of the
tools used to produce that material." The only Speaker's ruling anywhere in
scope is Alberta, 2 December 2025: asked to extend the anti-staff-written-
speeches rule to AI, Speaker Cooper ruled **"ChatGPT is not staff."**

Coverage is partial for NI, Manitoba, PEI and South Australia — absence of
evidence, not evidence of absence. Saskatchewan is the one solid null.
(`ai_policy_scan.md`; figures unverified against primary sources.)

---

## 7. Related work

Two prior efforts ran comparable designs on chambers in this corpus and
reached opposite conclusions. **Neither used a calibrated commercial
detector, and neither is peer-reviewed** — one is a Substack post, the other a
pseudonymous magazine piece. Details and primary-source verification in
`PRIOR_ART.md`.

| | Rice 2026 (Australian federal) | Pimlico Journal 2025 (UK Commons) |
|---|---|---|
| instrument | Binoculars, Fast-DetectGPT, LLM judge, per-MP stylometry | z-score excess vocabulary |
| corpus | 124,734 speeches, 2018– | UK Commons |
| result | **no** post-ChatGPT inflection | increase asserted |
| calibration | 50 pre-ChatGPT / 50 Claude-written | none reported |

**Rice does not claim evidence of absence, and should not be cited as
though he does.** He measures his LLM judge at **20% sensitivity** against
known-AI speeches, and his own calibration script prints a verdict string for
that case — *detector blind*. His stated reading is that no threshold
separates the classes in parliamentary register, and that
"it is inconceivable that only three or four federal politicians have used AI
to draft a speech in the past three years." His null is a sensitivity failure
he diagnoses himself.

**One correction to how we previously answered him.** We wrote that his
false-positive rate exceeded his detection rate, making the null
uninformative. Rice does say this, but the two figures are measured at
different thresholds — the 8% FPR at "highly likely AI" (≥8/10), the 7.1%
corpus rate at "possibly AI" (≥6/10) — so the comparison does not hold as
stated, and we should not have repeated it. The FPR itself is real but thin:
**4 of 50**, Wilson CI [3.2%, 18.8%], and it characterises a Haiku-class judge
rather than the Sonnet-class judge behind his headline run. Our corresponding
specificity is 0 in 1,260, measured chamber by chamber.

The substantive answer to Rice is therefore about **sensitivity, not
specificity**, and it generalises beyond his study. Binoculars (Hans et al.
2024) and Fast-DetectGPT (Bao et al. 2024) are sound published methods that
degrade severely on formal institutional prose: on peer-review benchmarks
reproduced in the Pangram 4 report, both fall to roughly 6% true-positive rate
at 1% FPR — false-negative rates above 90% — where a calibrated commercial
detector holds above 95%. Hansard is the same kind of register. A null
recovered with those instruments on this genre is close to uninformative, and
Rice's own numbers (Binoculars flagging 0.4% of everything) look like exactly
that.

Pimlico's agreement is **not** corroboration. Its method is the same family as
the arm we demoted in §3.3 for lacking a trend control, it reports no
prevalence estimate, and its own author hedges the finding as
"LinkedIn-ification" rather than drafting. A method that agrees with us while
sharing the defect we found in our own version of it is weak support, and
should be treated as a third result to explain.

Both may be measuring something real and different. §4.8 predicts exactly
this split: lexical methods fire on permeation that is not drafting, while
detector methods get ambiguous because the human baseline is moving toward
the thing being detected.

---

## Appendix A — Null results

Reported because they bound what the study can claim.

1. **District technology-adoption gradient during tenure** — null.
2. **Cohort × service-province adoption** — null.
3. **Cohort × birth-province adoption** — null. Spec B initially showed
   t = +2.20; clustered on 10 birth provinces the CI is [−0.22, +0.33].
   **Unclustered inference manufactured a hypothesis-flattering result twice
   in this study; both are recorded as cautionary.**
4. **Corpus-wide likelihood delta** — triple-replicated null.
5. **Kobak counterfactual on 2024 and 2026** — null (fires on COVID 2020-21,
   validating the estimator on a known shock).
6. **Frequency-weighted secondary** — 4/30 cells.
7. **Incumbent register change** — −0.42, CI [−1.32, +0.49], not significant.

Together these say the cohort effect is real and its **mechanism is not
exposure as we can measure it.**

## Appendix B — Superseded analyses

1. **Protocol v1.0** — superseded by v1.1 (present-in-both restriction,
   frequency × dispersion-matched placebos).
2. **Pilot zero-shot detector arm** — six detectors, none lifting 2025-26
   above its own floor; bound ≤ ~0.4% at measured Se. Superseded by Pangram;
   retained because it explains why edited AI needs a commercial detector.
3. **New Brunswick on Pangram 3** — superseded by the §4.1 rescore. Kept
   because the comparison is itself a result.
4. **Deciles as frequency control** — inadequate; redone with 2.0-wide
   absolute-density calipers (conclusion survived: +10.18 matched vs +9.85
   unmatched). †
5. **"Form up, deliberation down"** — the pre-2026-08-10 headline. The
   "form up" half survives and strengthens; the "deliberation down" half was
   genre, and collapses to null under genre or chamber fixed effects (§4.9).
   Retained here because it was the operating claim for ten days and appears
   in the work log, and because *how* it failed — an artifact visible only
   once genre was balanced by construction — is the argument for having built
   the balanced pool at all.
6. **Content-word control** and **Mistral synthetic corpus** — cut (§3.4).
7. **Pre-per-year prevalence point estimates** — superseded by the per-year
   series and then by the 19-chamber panel.

## Appendix C — Replication and reproducibility

### C.1 Stage 0: does the quality instrument reproduce?

Run before any new pool was graded, because a rubric that does not reproduce
makes every downstream quality number unusable. Same 241-segment pool
(`judge_blind_pool.json`), rubric verified byte-identical to commit 19deb97,
executed on a different account and a different machine.

| dimension | Spearman vs original | exact match |
|---|---|---|
| respect_demands | 0.954 | 96% |
| evidence | 0.951 | 92% |
| justification | 0.923 | 88% |
| constructive | 0.877 | 96% |
| respect_counterargs | 0.859 | 86% |
| respect_groups | 0.812 | 92% |
| common_good | 0.781 | 88% |

All at or above the original run's own repeat-pass band (0.68–0.91). The
judge's independent `ai_guess` correlates at 0.93 with the original. Group
means moved by less than the script's 0.30 flag everywhere, several
reproducing to three decimals; the largest shift anywhere was −0.20 on
`respect_counterargs` in an 8-segment group. **The v2 numbers are a property
of the rubric, not of one run.**

12 of 14 AI-vs-human gaps kept their sign, including every gap carrying the
published claim. The two flips (+0.141 → −0.005 and +0.034 → −0.029) were on
gaps already at zero, so they are noise around a null rather than reversals.

Note that stage 0's pool is **not** genre-balanced,
and it still shows the negative respect-for-demands gap that §4.9 finds to be
a genre artifact — which is the expected signature: the gap appears wherever
genre is free to vary and vanishes when it is held fixed.

### C.2 Cross-route reproduction of the detector

Web dashboard and Bulk API agree **20/20 including all six Mixed** on
identical text when the model is named explicitly, and disagree on 9/20 when
it is not (§3.2). All 4,258 verdicts in this study are Pangram 4 by either
route, and `pangram_p4_verdicts.csv` records which.

### C.3 Independent re-analysis

Stage 0's comparison and both stages' regressions were recomputed from the
raw result files by a second party who did not run the grading, and reproduce
to the reported precision.

### C.4 Bypass sample selection

The four bypass runs are not one sample, and pooling them is defensible only
because the differences are recorded. Full stacks in `BYPASS_METHODOLOGY.md`.

| run | seeds | how the seeds were chosen | Opus's role |
|---|---|---|---|
| NB v2 blind | 40 | Pangram-AI, stratified across Opus bands | outcome |
| NB v3 contrastive | 38 | same pool, contrastive exemplars added | outcome |
| GO Opus-selected | 25 | top 48 of 600 **by Opus score**, then Pangram-AI | **selection** |
| GO all-31 uniform | 27 | every Pangram positive in the uniform GO draws | outcome |

Two consequences carried into the text. The GO Opus-selected run regresses
−10.3 points on re-scoring because every seed sits at the extreme of a noisy
distribution, and it is range-restricted — it cannot contain the low band
where New Brunswick found most of its successes, so its zero successes test
nothing about the band hypothesis. And the GO all-31 run is the cleanest
provenance in the study: exactly one selection step, the Pangram verdict
itself, with no detector, lexicon, or Opus score influencing which segments
were scanned. It is also every Government Orders positive we hold, so it is an
exploratory replication rather than an independent rate estimate.

Banding, where it appears, is always on the **mean of three independent
re-scores**, never on the single noisy measurement used to select. Banding on
the selection score manufactured a clean cross-chamber gradient that was an
artifact of differential regression, and it was briefly reported before being
caught.

### C.5 Artifacts

| artifact | what it does |
|---|---|
| `pangram_p4_verdicts.csv` | 4,258 verdicts, all Pangram 4, with metadata |
| `prevalence_report.py` | §4.1–4.3, Wilson CIs, Rogan–Gladen |
| `nb_p3_vs_p4.py` | §4.1 model-tier comparison |
| `api_route_check.py` | route/model equivalence test |
| `transcript_regime_check.py` | §2.1, writes `transcript_regime.csv` |
| `build_pangram_expansion.py` | sampling, cleaning, regime floors |
| `in_time_placebo.py` | §3.3, the test that demoted the lexicon arm |
| `long_trend.py` | §4.5 series and its 1994 trough |
| `arrival_premium.py`, `formation_window.py`, `decomposition_inference.py` | §4.6 |
| `olmo_ladder.py` | §4.7 ladder stages |
| `rlhf_pref_analyze.py` | §4.7 pooled **+0.88** (not `align_ratio.py`) |
| `align_ratio.py` | §4.7 Hansard-drift arm |
| `word_context_delta.py` | §4.8 in-context permeation |
| `bypass_report.py` | §4.9 bypass, all four runs pooled |
| `go_reflip_fractions.json` + `nb_`/`bp_` | strict re-scores behind the 8.0% |
| `quality_expansion/` | §4.9, self-contained (`RUNME.md`) |
| `BYPASS_METHODOLOGY.md` | §4.9 selection filters, per sample |
| `PRIOR_ART.md`, `ai_policy_scan.md` | §6, §7 |

Cost: $158.00 API + 8,962 dashboard credits.
