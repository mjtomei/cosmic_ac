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

**The Oral Questions cell is not Question Period, and reading its flags
individually says more than the rate does.** The 120–360-word filter retains
95.2% of SO31 segments but only a small fraction of Oral Questions, because
QP utterances are short. What survives is the long tail: procedural and
ceremonial business filed under the QP rubric rather than question-and-answer
exchange.

Not one of the five flagged segments is spontaneous exchange.[^r43] Two are
**eulogies** for a former member. One is a **question of privilege**
responding to a matter raised the previous day. One is a **unanimous-consent
motion** — text negotiated between parties beforehand and read verbatim, the
most pre-written thing that happens in the chamber. The fifth is a backbench
question of the routinely staff-written kind. The genre claim therefore holds
segment by segment and not only in aggregate: within the genre nominated as
unscripted, the flags land exactly on the parts that were written in advance.

This makes the 8.3% a **mislabelled row rather than a wrong one**. It is not
an estimate of Question Period; it is an estimate of long-tail business
carrying the QP heading, and the true rate for genuine exchange is lower —
possibly zero.

**One flag type has no control, and it should not be leaned on.** Two of the
five are tributes, both at `fraction_ai` 1.0, and **no pre-AI tribute exists
anywhere in the control set**. Tribute register — elevated, cadenced, parallel
construction, abstract virtue nouns — is exactly what a detector keys on. Those
two are either strong evidence of drafting or the most interesting false
positive in the study, and nothing here separates the two readings. What the
controls do establish is that formal prepared *procedural* speech does not trip
the detector: the six pre-AI privilege and Business-of-the-House segments among
the CA-FED controls all read Human, inside the 1,260/1,260 overall.

[^r43]: `python genre_oq_audit.py`, which prints the five flags with their
    order-of-business headings, the control composition, and the unmet tribute
    control. It also retires an argument this section previously made — that
    the length floor leaves "prepared ministerial answers", the sub-population
    "most likely to be machine-drafted". Both halves are false: ministerial and
    parliamentary-secretary segments flag **0 of 28**, all five flags coming
    from non-ministers, and the floor selects *away* from ministers rather than
    toward them (ministerial share of Oral Questions falls 46.3% → 36.1% across
    the filter; median ministerial utterance 89 words against 95). The
    conclusion that the cell is biased upward survives; that mechanism does
    not.

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

Pooled alignment effect **+0.42** [6.7 sd above the estimator's own null].[^r47]
The shift is largest at the preference stage, which is what makes §4.5 more
than a coincidence of direction: the thing RLHF selects for is something humans
were already drifting toward.

[^r47]: Ladder stages: `python olmo_ladder.py` (end-to-end base→instruct
    **+1.2420**). The pooled **+0.42** is a *separate* experiment on two other
    model families — `python rlhf_pref_analyze.py`, which prints
    `EXCESS +0.4214, p < 0.001` (Qwen3-8B **+0.47** [+0.34, +0.59], Mistral-7B
    **+0.16** [+0.05, +0.27]; 668 and 788 prompt pairs, Kobak style words
    against frequency-matched controls). It is not a pooling of the three OLMo
    stages, and it is not produced by `align_ratio.py report`, which prints the
    Hansard-drift arm instead. Recorded here because looking for it in the
    wrong script is how it came to be mistaken for an unsourced figure.

    **This figure was +0.88 until 2026-08-12 and the old value should not be
    quoted.** The control pool was asymmetric: candidates were drawn only from
    words the base model had emitted, so a control absent from base output was
    impossible, while 57 of the 212 style words (27%) are absent from base
    output and carry mean preference +1.45. Controls were also bucketed on the
    ratio's own denominator, dragging the control median to −0.45 where a
    symmetric control sits at ~0. Fed 30 random frequency-matched word lists,
    the old procedure returned **+0.45** — a pedestal for lists with no special
    property. The corrected estimator returns +0.003 on the same nulls.

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
this gets **22.5%** of targets past it: **9.8×**.[^r49a] Against Pangram's
clean-conditions false-negative rate of 0.34%, it is 65×.

That is the finding. The detector is not weak — its specificity is 0 in 1,260
(§4.1), and a single "make this sound human" prompt makes text *more*
detectable, not less. But the gap between a purpose-built evasion product and
a frontier model told to try again is an order of magnitude in the frontier
model's favour, and it will not narrow in the detector's direction.

One asymmetry to keep visible: the 2.31% is a **one-shot** rate, while 22.5%
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
| **pooled** | **461** | **39 = 8.5%** [4.0, 13.4] | **37 = 8.0%** [3.6, 12.9] |

Restricted to unambiguously AI-seeded originals the rate is unchanged: 34/400
= 8.5% [3.5, 14.2] by label, 32/400 = 8.0% strict. This is the right number
when the claim is about the *detector*, and it is deliberately harsh on
ourselves: it keeps two superseded searches in the denominator, including the
badly-seeded run that produced nothing.

**The intervals are clustered on text, and they are wide.** The 461 variants
are up to eighteen rewrites of each of 92 originals, and success is strongly
clustered by original — which is what this arm's own band analysis asserts,
that evadability is a property of the text rather than of the rewrite. Treating
each rewrite as an independent trial gives a Wilson interval of [6.3, 11.4],
about half the width it should be: the cluster-robust standard error is 2.44
percentage points against a naive 1.30, a **design effect of 3.55**, so the
effective sample is about 130 variants and not 461. Quoted above is a
non-parametric cluster bootstrap over texts, 20,000 draws. The per-target
figures below need no such correction — they already carry one observation per
text.

**The operational figure — 22.5% per target, best method only.** An adversary
does not care how many drafts they discard; they care whether the speech they
wanted through got through. Taking only the **final search in each chamber**
and asking on what fraction of *targets* at least one variant reached a clean
Human verdict:

| | searched | zero-yield | ≥1 Human | ≥1 at `fraction_ai = 0.0` |
|---|---|---|---|---|
| NB v3 contrastive | 40 | 2 | 10 = 25.0% | 10 = 25.0% |
| GO all-31 uniform | 31 | 4 | 6 = 19.4% | 5 = 16.1% |
| **pooled** | **71** | **6** | **16 = 22.5%** [14.4, 33.5] | **15 = 21.1%** [13.2, 32.0] |

**Roughly one flagged speech in five can be walked past the detector**, at a
budget of six rounds and three variants per round. This is the figure a fresh
study replicating our best method should expect to reproduce, and the more
honest description of the exposure a chamber actually faces.

**The denominator is targets searched, not targets that yielded a variant.**
The search submits a rewrite to Pangram only when its Opus proxy score drops
below 50, and six of these 71 targets ran four to six full rounds without ever
producing one. Those are attack failures — an adversary who cannot produce a
candidate their own proxy will submit has not got that speech past anything —
so they belong in the denominator. Counting only targets that yielded makes
the rate conditional on the attack having already half-succeeded, and gave
24.6% where the answer is 22.5%.

Those six are not evidence that the text cannot be disguised. They establish
that *this* search, at this budget, did not manage it — and the search had
converged, so further draws from the same process would probably not have
helped either. Whether a **different method** would is a separate question and
an untested one: better contrastive exemplars, a rewriter fine-tuned against
the detector, or a human editor are all outside what was tried.

The two chambers agree closely (25.0% and 19.4%) **despite contradicting each
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
| *this study, per target* | *22.5%* | *induced, ≤18 attempts — 9.8× the humanizers* |
| Rice 2026, Australian Hansard | ~8% | **false *positive* rate**, n = 50 |

**Only the per-variant row is commensurable with the vendor rows**, which are
one-shot document-level rates on known-AI text. And the comparison is a
comparison of point estimates: once the per-variant interval is clustered on
text it runs [4.0, 13.4], so the adversarial vendor figures at 2.31–2.86% sit
below our estimate but not far below its lower bound. The ordering is not in
doubt; its margin is less certain than the point estimates suggest. The per-target row is
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
targets (45%) cleared it. So 8.5% and 22.5% bound what two days and four
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
stage 3 is 38 New Brunswick pairs, stage 4 is 25 Government Orders pairs.
Within-text pairing holds content, speaker and occasion fixed by construction,
so these are the raw paired differences — the design's own estimand, needing
no covariate. **Every dimension is null on both.**[^r49b]

| dimension | stage 3 (n=38) | stage 4 (n=25) |
|---|---|---|
| justification | +0.05 (t +0.6) | +0.16 (t +1.7) |
| common_good | −0.05 (t −0.8) | 0.00 (t 0.0) |
| respect_groups | −0.08 (t −1.8) | +0.04 (t +1.0) |
| respect_demands | −0.08 (t −0.6) | 0.00 (t 0.0) |
| respect_counterargs | +0.33 (t +1.8) | +0.12 (t +1.0) |
| constructive | 0.00 (t 0.0) | −0.12 (t −1.8) |
| evidence | +0.03 (t +0.4) | +0.08 (t +0.7) |

**On length, which we do not adjust away — and which does not replicate.**
Stage 4's rewrites run about 29 words longer than their originals; stage 3's do
not (mean −1.3). Within stage 4, justification does move with length, at
**r = +0.33**. That is the largest correlation on the board and it points the
way the length story predicts.

It does not survive the other stage. In stage 3 the same correlation is
**r = −0.24** — longer rewrites justify *less* — and stage 3 is where the
estimate is better identified, its word deltas running both directions with sd
38 against stage 4's one-sided 14. Neither reaches significance (p = 0.11 and
p = 0.15). **A relationship that changes sign between two arms of the same
design is not a relationship**, and the tidy explanation that justification's
stage-4 drift "was length" fails on the data rather than on the statistics.

We report the correlation rather than removing it, because length is not a
confound here in any case. On this rubric a longer passage genuinely has room
to justify more, and a member with a longer slot could earn the same points the
same way. Adding justification by adding words is a real strategy, not an
artifact of one; partialling it out would treat a route to quality as a
nuisance parameter.[^r49c]

[^r49c]: An earlier version of this section reported a *length-adjusted*
    column instead and used it to conclude that justification's apparent gain
    "was length". That column is the regression intercept at a word delta of
    zero, and 24 of the 25 stage-4 deltas are strictly positive — a zero delta
    sits 2.1 sd outside the sample with one observation there, giving an
    intercept VIF of 5.43 and inflating the standard error 2.3×. The +0.16 →
    −0.173 sign flip was extrapolation. The column has been removed from the
    script rather than repaired: the design is within-text paired, so content,
    speaker and occasion are already fixed by construction and there was
    nothing for a covariate to control.

**What this means for the prevalence number.** Evasion is real, clears the
detector on roughly one flagged speech in five under directed search, and is free
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
    `results_stage34.json`, which now also caches `r_words` per dimension.
    Grading transcripts live on the second machine (stage 3 run
    `wf_b9bbcff8-1a7`, stage 4 `wf_7516f16c-386`); the script needs a run
    directory, so pass one. Quoted column is the **raw paired difference**,
    humanized − original, within text. `-1` (inapplicable) pairs are excluded,
    which is why the two sentinel dimensions have smaller n (12 and 12 in
    stage 3; 18 and 16 in stage 4).

---

## 5. Limits

- **Prevalence is a floor.** Detectors see undisguised machine text. A
  directed search clears the detector on 8.5% of variants and **22.5% of
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
- **This study measures register, not substance.** Whether machine assistance
  changes *what* is argued, which evidence is cited, or which framings are
  reached for is not measured anywhere in §4, and the frequency instrument
  cannot measure it — the Kobak style/content split is PubMed's content and
  does not transfer to a legislature. The quality arm (§4.9) is the closest
  thing here, and it grades form rather than position. A domain-native
  substance arm is buildable from materials we already hold (§8.6 item 1);
  until it exists, no claim in this study should be read as being about the
  content of legislative argument.
- **Cohort mechanism is unidentified.** Three exposure tests null, and the
  informative next evidence is a different kind rather than a fourth
  operationalisation of the same kind (§8.6 items 2–4).
- **No chamber requires AI disclosure**, so no ground truth exists anywhere;
  every number rests on detector calibration rather than admission.
- **Single detector.** Specificity is measured, but Pangram 4 is one vendor.
- **Specificity is measured on the genres the controls happen to contain.**
  1,260/1,260 is strong, but no tribute or eulogy is among them, and tributes
  produced two of the five Oral Questions flags at maximal confidence (§4.3).
  Until a pre-AI tribute control exists (§8.6 item 4a), the specificity claim
  does not extend to that register.
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

## 8. Discussion: detection as a norms instrument, and what to measure instead

§4.9 is usually read as a result about one detector. It is better read as an
instance of a general limit, and the generalisation changes what the rest of
the study is for.

### 8.1 The limit

Point a general-purpose model at its own output, tell it to try again, and it
will defeat any check you can put in front of it. This is not a claim about
Pangram. It follows from the check being a fixed function and the attacker
being an optimiser with a quality constraint the optimiser itself can satisfy.

Our own numbers are the *weak* instance. The search never queried the detector
it was evading: it optimised against an Opus proxy, tested on Pangram only at
the end, used roughly eighteen attempts per target, and involved no
fine-tuning, no gradients, and no detector access of any kind. 22.5% of
targets cleared is what that buys. An adversary who can query the check
directly is hill-climbing the actual objective, and there is no reason to
expect the ceiling to be near where we stopped.

**Two scoping notes, because the argument can be overextended.** Inferring
*future* checks is weaker than defeating present ones — you cannot optimise
against features you cannot anticipate. And the limit applies to **post-hoc
statistical detection of unmarked text**, which is a different problem from
provenance asserted at generation time.

### 8.2 Where the norms argument actually lands

Detection fails against adversaries and works against everyone else. That is
not a small residual: the 12.4% in §4.2 exists precisely because nobody
currently bothers to evade, or the undisguised register signature would not be
there to find. **Detection is a norms instrument, not a security instrument** —
locks, not vaults. It raises the cost of casual undisclosed use and does
nothing against motivated use, and that is a coherent thing for a chamber to
want. It is also what lets 12.4% stand as a measurement of disclosed-by-default
behaviour while conceding the limit above entirely.

The better version of the norms instrument is not a sharper detector but a
**signature the generator puts there on purpose**. Anthropic began embedding
"an imperceptible watermark directly into the text itself" for Claude models
launched on or after **2 August 2026**, with retrofitting of existing models in
progress, across all its products and its AWS, Google Cloud and Microsoft
distribution; generated image files additionally carry C2PA-signed provenance
metadata. Detection is not yet public — the company says it is "working to
enable users and other third parties to detect Claude's embedded watermarks",
with technical documentation forthcoming. Google DeepMind's SynthID-Text
(Dathathri et al., *Nature* 2024) is the deployed precedent.

**The durable argument for hiddenness is not robustness — it is minimal
interference with the content.** This is worth stating carefully, because the
obvious argument is the wrong one. One could say a secret-keyed mark cannot be
hill-climbed without query access to the verifier, which is exactly the
situation our search was in and the reason it needed eighteen tries. True, but
fragile: it erodes the moment the detector is released, and released detectors
are the whole point of a transparency measure. Anthropic's own documentation
concedes the robustness half — marks may not survive text that is "heavily
edited, paraphrased, translated, or mixed", and short passages may carry no
reliable signal.

The property that never goes away is that an invisible mark **costs the reader
nothing even after the detector is public**. A visible disclosure label
degrades the artifact, invites removal, and is trivially stripped; an
imperceptible one imposes no cost on the text and survives ordinary copying
between applications. Image watermarking is the settled analogy: easy to crop
or inpaint away, universally deployed anyway, and useful precisely as a norm
rather than a lock.

**Bypassability is therefore not a defect here — it is the category.** Zhang
et al., *Watermarks in the Sand*, give an impossibility result for strong
watermarking against an attacker with a quality oracle and a perturbation
budget, close to the setting we ran; paraphrase degrades token-level marks
(Sadasivan et al. 2023, with Kirchenbauer et al. 2023b making survival a
function of marked-token count). None of that refutes the instrument. It
establishes that a watermark is a norms instrument and not a security
primitive, which is the same thing §4.9 establishes about detection, and both
are still worth having for the same reason locks are.

Two limits that do bite, and neither is about robustness:

- **It requires the generator to cooperate.** Open-weight models will not mark
  their output, so this prices casual frontier-API use and does nothing about a
  local model.
- **A mark attests presence, never absence.** Unmarked text proves nothing,
  which means watermarking can support a disclosure norm but can never
  underwrite an accusation.

### 8.3 The substitution, and why our null is the argument for it

If provenance is the wrong thing to spend effort on, the question is what to
spend it on instead. The answer available from this study is: **check the work
directly.**

The case rests on the §4.9 quality null, which is usually read as bad news.
Evasion cost nothing on any of seven DQI dimensions across 63 paired grades.
Read as a detection result, that is a failure. Read as a substitution result it
is the entire argument: **quality assessment is orthogonal to provenance, not a
proxy for it.** Had DQI tracked authorship, it would merely be a worse
detector. Because it does not, it measures the thing anyone actually wanted to
know.

And it is now cheap in a way it has not been before. The instrument reproduces
at or above the published human inter-coder bar across accounts and machines
(Appendix C.1), on a rubric with published human codings as anchors. Twenty
years ago the Discourse Quality Index required trained coders and bounded any
study to a few hundred speeches. We graded 1,522 in the main arms without
trained coders. That capability arrived with the same technology that broke
detection, which is the substitution in one sentence: the machine that made
provenance unmeasurable made quality measurable.

### 8.4 Where text is a proxy for a person's internal state

Deliberation is judged on the artifact, so §8.3 suffices. Education is not:
there the text is a proxy for what is in someone's head, and a proxy that can
be generated is no proxy at all. That case needs a **more rigorous proof of
understanding**, and machine intelligence supplies the means as well as the
problem — adaptive examination against a person's *entire* corpus of work, with
provenance and time-on-task as evidence rather than the text alone.

Two costs to state plainly. Process and timing data are themselves spoofable,
so this is an escalation and not a resolution. And "analyse the student's
entire corpus" is a surveillance instrument before it is an assessment
instrument; the version worth building is the one that is legible to the person
being assessed.

### 8.5 Measuring the human contribution against an automated counterpart

The most promising direction, and the least developed. Generate what a fully
automated system would produce given the same task and context; the human
contribution is the residual. This is the marginal-product definition done
properly, and it is measurable today.

**The baseline must move.** The obvious objection is that the residual shrinks
as models improve, and the obvious fix — freeze a model vintage — is wrong. It
reproduces the error the current debate already makes, where contributions
relative to dumb computers are treated as obviously legitimate and anything
touching an LLM as obviously suspect. **The goalpost should move by
construction, always incorporating the latest technology**, because that is
what contribution means: what you added over the best available alternative. A
shrinking residual is correct measurement, not measurement decay. Nobody
credits long division done by hand.

The one thing worth recording is *which* baseline a given measurement was taken
against — metadata that keeps an old measurement interpretable, not a fixed
target. This is the same quantity S17 measures as the imitation lag, and the
same reason it is collapsing.

### 8.6 Future work

Grouped by what they would settle. Several were designed during the study and
deferred rather than invented here; where a design was set aside deliberately,
that is recorded.

**A. The measurement this study does not make.**

1. **The substance channel.** §4 measures *register*. Whether machine
   assistance changes what legislators argue, which evidence they cite, and
   which framings they reach for is unmeasured, and the Kobak instrument cannot
   answer it — its style/content split is PubMed's content, not a legislature's,
   and does not transfer. The materials for a domain-native version already
   exist: the base-versus-instruct generation that produced §4.7's +0.42 yields
   an empirically derived list of what post-training adds *to legislative text
   specifically*. Split that list into register-like and substance-like by an
   independent rule and run both through the frozen protocol as separate arms,
   giving "did the register shift" and "did the substance shift" as two
   measurements instead of one. Estimated at a few hours. This is the single
   most valuable unrun item, and it is also a limit on the present study rather
   than merely an extension (§5).

**B. Getting outside the parliamentary archive.** Three versions of one move.
§4.6's mechanism is unidentified and three exposure tests inside the archive
returned null (Appendix A); the informative next evidence is a different *kind*,
not a fourth operationalisation of the same kind.

2. **Cross-country onset timing.** Within-country geography is exhausted — by
   2006 everywhere in Canada and the US was past the inflection, leaving about
   five points of spread. If the climb tracks immersion it should *start later*
   in late-adopting countries; Poland, Romania, Brazil and Mexico lag the UK by
   five to ten years, which is a difference-in-differences on onset with far
   more leverage. The language barrier is now surmountable with our own method:
   generate paired base/instruct output in the target language and take the
   words post-training adds — the same procedure behind §4.7. ParlaMint is the
   corpus vehicle. **Deferred by Matthew during the study** in favour of
   staying with the existing English word list; recorded here because the
   English fallbacks it was traded against have all since been run.
3. **A population-wide, age-stratified corpus outside politics.** The
   generational-language-change rival predicts the same shift in *any*
   age-stratified corpus, with politics incidental. The within-legislature leg
   of that test was run — birth decade survives occupation and education, both
   of which run the wrong way — but the external leg has never been attempted
   and no such corpus has been named.
4. **The same people's non-parliamentary writing before they entered
   politics.** Directly tests whether the register is acquired before political
   life. Not reachable from parliamentary archives, which is why it was set
   aside; it remains the cleanest available test of the cohort story.

**C. Corpora and arms already within reach.**

4a. **A pre-AI tribute control — the one specificity gap we know about.** Every
   chamber bought a 60-segment pre-2022 control, and 1,260 of 1,260 read Human,
   including six ceremonial and procedural CA-FED segments. But **no tribute or
   eulogy is in any of them**, and two of the five Oral Questions flags are
   eulogies at `fraction_ai` 1.0 (§4.3). Tribute register is elevated,
   cadenced and heavy on parallel construction — the surface features a
   detector keys on — so it is the one genre where a false positive could hide
   behind our specificity claim. Score ~40 pre-2022 tributes from the same
   chamber. Same design as every control already bought, roughly $5, and it
   either closes the gap or produces the most interesting result in the arm.

5. **The written arm of the US Congressional Record.** Extensions of Remarks
   is separable from floor speech and is currently dropped at extraction
   (`us/us_extract.py`). It mirrors the closest prior work directly — Suvanto
   et al. studied *written* parliamentary text and explicitly avoided
   transcribed speech — so running it turns a contrast of methods into a
   head-to-head on comparable material.
6. **NSW Written Community Recognition Statements**, currently excluded to keep
   the corpus spoken-only. Short, formulaic, offline-drafted text is exactly
   where machine writing should surface first, and the section grew from 4.7%
   of raw words in 2018 to 29–32% in 2025-26 — an uncollected datum in its own
   right. Recoverable from the same PDFs as a separate stream.
7. **Genre-resolved US prevalence.** Canada and the provinces carry genre
   metadata and the US does not, which is why the US sits out §4.3. Recovering
   One Minute Speeches, Special Orders and Morning Business needs re-extraction
   against CREC granule metadata.
8. **Coverage gaps that need a non-English instrument**: 199k words of
   French-original New Brunswick debate, never scored by anything; Quebec,
   dropped from the province gradient for the same reason; and New Zealand,
   ranked as tractable but never built. All three are first customers for the
   build-the-instrument-in-any-language method in item 2.

**D. Rivals for the register trend that remain live.**

9. **Staff age as the exposure measure.** Members read what staff write, so a
   70-year-old member with 24-year-old staff has young exposure — which is why
   the member-age design is not the right one. Legislative staff are young and
   short-tenured, so office exposure tracks the cohort entering staff work, and
   that cohort turned computer-native in the mid-2000s, where the UK curve
   starts climbing. Data is thin but two routes exist: Legistorm's US
   congressional staff records (paid) and House Statements of Disbursements
   (names, salaries, tenure and salary as seniority proxies). Neither has been
   pursued. This is also the natural companion to S15.
10. **A role-controlled UK specification.** The two UK specs fail in opposite
    directions — the full corpus has a composition problem, and the
    within-speaker subset has a role problem, since those MPs lived through a
    change of government and frontbench speech is more formal and more scripted
    by function. The fix is a formality set defined by function rather than
    hand-picked (words that rise with frontbench status *in the pre-period
    only*), restricted to MPs whose frontbench status did not change. Related:
    `arrival_premium.py` shows the arrival premium exists in every era at about
    +0.8 and *grows*, so the level component is real and currently unattributed
    between tenure and role.
11. **Candidate selection for media performance**, named as a compositional
    rival and never given a test or a data source. And the
    **professionalised-communications** rival — message discipline and
    clip-ready speech over the same years — has only ever been tested
    indirectly, through its prediction of uniform rather than gradiented drift.
    Since the gradient tests returned null, that indirect test cannot
    distinguish it from the exposure story. It is live and unmeasured.

**E. The detector and evasion arm.**

12. **Does the counterfactual residual behave?** Take the §4.9 pairs, generate
    the automated counterpart for each, and check whether the residual
    separates segments we have independent reason to think were human-drafted.
    We already hold the pairs and the labels.
13. **Do watermarks survive our search?** The v3 contrastive attack targeted
    structural features — rhythm, tricolons, anticlimactic endings — and
    Anthropic's own stated limit is that marks may not survive text "heavily
    edited, paraphrased, translated, or mixed". Our rewrites are exactly that,
    with a plausibility gate keeping them usable as floor speech, so this is a
    sharper test than generic paraphrase. **Blocked until third-party detection
    publishes**; no query access to the verifier is what makes it the honest
    threat model when it does.
14. **Detector access as a variable.** Re-run the search with Pangram in the
    loop rather than an Opus proxy. Our 22.5% is a floor on adversary
    capability and the gap is unmeasured.
15. **The below-threshold residual sample** — roughly 150 segments, 33–54k
    words, about $5. It bounds what the *screen* misses, which is a different
    quantity from what Pangram misses on edited text, and worth having stated
    as its own number.
16. **Human-coded DQI subsample**, still the real validation of §8.3's claim
    that the instrument is cheap *and* sound (§5).
17. **Does anyone actually evade?** The norms argument in §8.2 rests on current
    prevalence being undisguised. A chamber-level test — whether flagged text
    clusters away from the evasion signature — would turn that assumption into
    a measurement.

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
| NB v3 contrastive | 40 | same pool, contrastive exemplars added | outcome |
| GO Opus-selected | 35 | top 48 of 600 **by Opus score**, then Pangram-AI | **selection** |
| GO all-31 uniform | 31 | every Pangram positive in the uniform GO draws | outcome |

The seed column is targets **searched**. An earlier version listed 38, 25 and
27 — the counts that produced at least one variant clearing the submission
gate — which understated the attack surface, most severely for the
Opus-selected run where 10 of 35 targets yielded nothing.

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
| `rlhf_pref_analyze.py` | §4.7 pooled **+0.42**, with null calibration (not `align_ratio.py`) |
| `align_ratio.py` | §4.7 Hansard-drift arm |
| `word_context_delta.py` | §4.8 in-context permeation |
| `bypass_report.py` | §4.9 bypass, all four runs pooled |
| `go_reflip_fractions.json` + `nb_`/`bp_` | strict re-scores behind the 8.0% |
| `quality_expansion/` | §4.9, self-contained (`RUNME.md`) |
| `BYPASS_METHODOLOGY.md` | §4.9 selection filters, per sample |
| `PRIOR_ART.md`, `ai_policy_scan.md` | §6, §7 |

Cost: $158.00 API + 8,962 dashboard credits.
