# Machine-drafted speech in legislatures: prevalence, concentration, and a register that predates the machines

**S10 — draft write-up, 2026-08-11; §4.6a and Appendix A extended
2026-08-13.** All arms complete, including the detector-bypass study and both
prior-art comparators. Everything is reproducible from `analysis/s10/`.

**The 2026-08-13 additions carry UNVERIFIED citations.** §4.6a places its
result against Labov, Simmel, Veblen, Jhering, Bourdieu and Lieberson, none of
which has been checked against a primary text — one fetched entry was already
wrong on both year and publisher. See `CLASS-REGISTER-LITERATURE.md`. That
subsection also reports standard errors that are not clustered on member,
which the study has been bitten by three times; both are flagged in place.

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
- **prevalence** — segments dated 2025-01-01 or later, sampled uniformly at
  random with no detector-screen stratification.

Segments are member-authored, English-original, non-chair, and 50 words or
longer — the whole of the record Pangram will read. Sampling is at a uniform
rate across segment lengths, so the sample reproduces the corpus's own length
mix and the pooled estimate needs no length weights. Sampling is seeded per cell
and reproducible (`build_pangram_expansion.py`, `build_shortband.py`).

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

### 4.2 Prevalence: 9.0% of words, with an elevenfold spread

**Pooled 9.03% of words [8.00%, 10.08%]** — 65,795 machine-written words of
728,998 across 3,519 segments in 20 chambers, excluding regime-flagged TAS.

Every figure below is the share of *what was said* that is machine-drafted,
over the whole of the record Pangram will read.

*Weighted by words, because a segment is not a natural unit.* `segment.py`
packs speaker turns into windows of at most 360 words, so a long speech becomes
three segments and a short interjection becomes one. A rate over segments is
partly a measurement of our packer; a rate over words is invariant to how the
text was cut up.

*Weighted by AI fraction, because a flagged segment is not uniformly flagged.*
A Mixed verdict is Pangram reporting that part of the segment is human, so
counting all of its words as machine over-states the rate by a third —
**12.03% against 9.03%**. Every flagged segment is weighted by its own AI
share: recorded directly for the API-scored rows, and read off the dashboard
result by result for all 132 Mixed segments the API did not cover. Mixed
segments average **0.435** machine (n=132, sd 0.219, range 0.11–1.00); AI
verdicts are effectively a constant at 0.9965. Human verdicts are 0.0 in every
one of the 1,246 recorded cases.[^r42f]

| chamber | rate | 95% CI | | chamber | rate | 95% CI |
|---|---|---|---|---|---|---|
| NSW | **19.8%** | [13.2, 26.9] | | IE | 7.5% | [3.6, 12.2] |
| CA-FED | 18.5% | [12.5, 24.6] | | VIC | 7.3% | [3.5, 11.7] |
| QLD | 15.8% | [9.9, 22.1] | | SA | 6.8% | [2.9, 11.3] |
| BC | 14.2% | [8.3, 20.4] | | WA | 4.9% | [1.4, 9.1] |
| MB | 13.1% | [8.1, 18.6] | | WAL | 4.9% | [1.6, 8.9] |
| NI | 13.1% | [8.1, 18.6] | | SK | 4.1% | [1.3, 7.5] |
| **US House** | **12.1%** | [7.0, 17.7] | | SCO | 3.9% | [1.0, 7.4] |
| ON | 11.1% | [6.1, 16.8] | | NL | 3.3% | [0.8, 6.6] |
| NS | 10.0% | [5.4, 15.2] | | UK | 2.5% | [0.7, 4.8] |
| AB | 7.8% | [3.9, 12.2] | | **US Senate** | **1.8%** | [0.1, 4.1] |

Intervals are cluster bootstraps over segments, not Wilson intervals: the
estimator is a ratio of two random sums whose numerator and denominator move
together, so a chamber whose one flagged segment happens to run 900 words
should read as less certain than one whose flag is 130 words, and a binomial on
segment counts cannot express that.[^r42]

The spread is the finding, not noise around a mean. **US House 12.1% vs US
Senate 1.8%** is the sharpest contrast available: two chambers of one
legislature, near-identical AI policies, differing sevenfold.

**Federal Canada's row comes from its own uniform draw**, not from the
genre-stratified sample that answers §4.3. The genre arm takes 60 segments
each from Statements by Members, Government Orders and Oral Questions, which
imposes a genre mix rather than observing one and leaves 25.6% of the chamber's
in-band record — Private Members' Business, Adjournment Proceedings, Routine
Proceedings, the Throne Speech reply — in no stratum at all. Read as a chamber
rate it gives 16.5%; the uniform draw of 120 prevalence segments gives **18.5%**,
and the uniform draw is what the table reports. Dropping CA-FED entirely leaves
the pool at 8.50% against 9.03%, so the chamber contributes about half a point
to the headline and neither makes nor breaks it.[^r42ca]

[^r42ca]: `pangram_ch_verdicts.csv`, rows `caprev*`/`cactl*`. Its short band
    already matched this draw: 120 × 15,236/18,029 = 101, and 101 short
    segments were scored at the matched rate. Seven controls dated after the
    2022-06-30 cutoff — one of them after ChatGPT shipped — were replaced on
    2026-08-13 from the same 2018–2022 window the survivors occupy
    (`build_cafed_ctl_redraw.py`); all seven replacements scored Human, as had
    all seven originals, so specificity is unchanged at 60/60 and only the
    design claim is repaired.

**UK Commons and Dáil Éireann are scored entirely on Pangram 4**, verified
rather than assumed: all 360 of their segments from the four-chamber arm, which
recorded no model version, were rescored through the dashboard and agree with
the original verdicts **360 out of 360**. That agreement is itself the largest
Pangram 3-versus-4 comparison in the study (§3.2).

**Manitoba's 13.1% depends on a repaired extractor**, and without it the
chamber reads 5.3%. The original extraction lost 42% of the record: from
mid-2018 the Manitoba Hansard export splits a speaker's name across several bold runs
around inserted table-of-contents anchors, the extractor's prefix pattern
matched only the first run, and the speech accreted to the previous turn — the
Speaker's — where it was discarded as chair voice. Chair share of page text ran
4% in 2011–13 against 37–40% in 2020–24.

The loss was **not neutral**, which is why it matters so much. A frame missing
42% of text at random would leave the rate roughly unchanged. What was
missing were the formatted, anchor-bearing speeches — the prepared ones — and
prepared business is exactly where drafting concentrates (§4.3). The extractor
was preferentially deleting the machine-drafted half of the chamber's record.

The controls are the check that this is a frame effect and not the detector
behaving differently: they were clean before the fix and remain clean after,
**0 of 18,342 words**. 275 segments were redrawn from the corrected extraction
and rescored, restricted to the original year windows so that the frame is the
only thing that changed.[^r42mb]

[^r42mb]: `python build_mb_redraw.py`, then `pangram_mb_redraw_verdicts.csv`.
    The redraw deliberately excludes the years backfilled in August 2026: a
    first draw from the corrected frame pulled 30 of its 90 controls from
    2011–14 and 2020–22, years no other chamber can draw from, which would have
    confounded the frame repair with a change of window. The superseded
    extraction is kept at `provinces/superseded/` so the pre-fix verdicts stay
    reproducible — 135 of the old 278 seg_ids do not exist in the corrected
    file, because re-extraction shifts turn indices.

[^r42f]: Fractions live in `fraction_ai_harvested.json` (151 harvested
    individually) and in the `fraction_ai` column of
    `pangram_p4_verdicts.csv` (1,431 recorded by the API). The 154 AI verdicts
    not harvested individually are carried at the measured constant; two
    independent samples put it at 0.9965 (n=148) and 1.0000 (n=19), and the
    lowest AI value anywhere is 0.81, so clicking them would move the pooled
    figure by under 0.01pp.

    **This is a correction, not a refinement.** Every rate this study reported
    before 2026-08-13 counted a Mixed segment as wholly machine-written. The
    error is a factor of 1.33 on the headline and is not uniform across the
    study: it is largest where Mixed verdicts cluster, which is the
    mixed-format business in the middle of §4.3's genre ladder.

[^r42]: `python -c "import banded_prevalence as B; B.table(B.load())"`.

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

| genre, 2025–26 | flagged words | 95% CI |
|---|---|---|
| **SO31** — one-minute scripted set-pieces | **32.3%** | [21.0, 44.1] |
| Government Orders — mixed prepared and spontaneous | 19.9% | [10.4, 30.3] |
| **Oral Questions** — not on notice | **9.8%** | [2.3, 19.2] |
| all three pre-AI controls | **0.0%** | [0.0, 0.0] |

**SO31 vs OQ: 3.29×, +22.5pp, permutation p = 0.0025.**

Word-weighted and fraction-weighted, like every other rate here. **Weighting
by the AI share widened this ladder rather than flattening it**, which was not
the expected direction: Mixed verdicts are commoner in the mixed-format
Government Orders than in the scripted SO31 set pieces, so counting Mixed
segments as wholly machine had been flattering the middle rung. On binary
counting the three read 35.8% / 25.7% / 11.8% and a 3.03× ratio.

The word-weighting choice matters more in this table than anywhere else in the
study: the genres differ sharply in how long
their segments are — SO31 is a one-minute set piece, a Government Orders slot
runs twenty — so a segment-weighted comparison measures the packer's behaviour
across genres alongside the drafting. On segments the same data reads 36.7% /
23.3% / 8.3% and a 4.40× ratio; word- and fraction-weighted the ordering is
unchanged and **the gap settles at 3.29×**. The test is a label permutation rather than
Fisher exact, because Fisher takes segment counts and the estimator is a ratio
of summed words.[^r43w]

[^r43w]: `python prevalence_report.py` for the rates and bootstrap intervals;
    the SO31-vs-OQ permutation is 50,000 label shuffles of the pooled
    prevalence segments. Reported here rather than the old Fisher p = 0.00034,
    which tested a quantity the study no longer reports.

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

### 4.5a The climb is everywhere except the United States

Running the same series on every chamber turns the thirty-year drift into a
comparison. The instrument and the 200 matched placebo sets are built once, on
UK Commons 2010–12, and applied unchanged everywhere, so the chambers are
measured with the same ruler.[^r45a]

| chamber | gap per 100k, first year | last year | change | |
|---|---|---|---|---|
| UK Commons | 380 (1994) | **1,444** (2026) | **×3.80** | rises |
| Ireland | 1,603 (2018) | **1,975** (2026) | ×1.23 | rises |
| CA federal | 1,865 (2015) | 1,735 (2026) | ×0.93 | flat |
| **US House** | **1,515** (1994) | **1,709** (2026) | **×1.13** | **flat** |
| **US Senate** | **1,314** (1994) | **1,562** (2026) | **×1.19** | **flat** |

The US chambers are flat across thirty-two years, and they start *above* where
the UK still sits two decades later: US House 1,515 in 1994 against the UK's
1,444 in 2026. So the picture is not a common shift. It is everyone else
converging upward on a level the United States already held before the consumer
web, while the United States does not move.

The US series reaches back to 1994 only as of 2026-08-13. The Congressional
Record is on GovInfo from 1994, which the study had not used: the original
download began at 2006 because that was where the state-exposure design needed
it. Extending it was the decisive test, because a US series starting in 2006
cannot distinguish "the United States was always there" from "the United States
got there first and stopped". The 1994 values settle it.[^r45c]

**They caught up; they did not pass.** A single recent year appears to
contradict that: in 2026 the Canadian provinces, Ireland, the Australian states
and federal Canada all sit above US House. The comparison does not survive
contact with the variance. US House swings between 1,660 and 2,074 across the
series — a 25% range, the widest here — and 2026 catches it at 1,709, near its
own floor. On 2020–26 means, with each series' standard deviation alongside:

| | mean | sd | vs US House |
|---|---|---|---|
| CA provinces | 2,054 | 61 | **+155 (+1.28 sd)** |
| Ireland | 1,901 | 52 | +2 (+0.02 sd) |
| **US House** | **1,899** | **121** | — |
| AUS states | 1,861 | 36 | −39 (−0.32 sd) |
| CA federal | 1,816 | 134 | −84 (−0.69 sd) |
| US Senate | 1,591 | 60 | −309 (−2.55 sd) |
| UK Commons | 1,415 | 61 | −484 (−4.00 sd) |

Only the Canadian provinces are meaningfully above, and they are a standing
exception this study does not explain. Ireland is at parity to within a
fiftieth of a standard deviation; the Australian states and federal Canada are
below. Three of the four apparent overshoots are US House having a low year.

**Exported machine text does not account for the rest, and cuts the wrong
way.** The natural rescue — that AI drafting, American-inflected, is pushing
the others past — fails on the arithmetic: US House is **14.3% machine by
instrument occurrences** against Ireland's 9.0% and the Australian states'
11.3%, so removing machine text lowers the American benchmark by more than it
lowers the challengers. Federal Canada is the one case it does explain, at
21.7% the most machine-written chamber in the study, dropping from
apparently-above to clearly-below once corrected.[^r45f]

[^r45f]: `python convergence_check.py`, with shares from
    `ai_share_of_instrument.py`. Machine-written text carries the instrument at
    4,231 occurrences per 100k words against human text's 3,470, a ratio of
    1.22×, so a chamber that is 9.0% machine by words is 10.6% machine by
    occurrences. Note this is an overlap between two instruments and not a
    causal decomposition: a high instrument rate inside flagged text is part of
    why the detector flagged it. The correction also applies only to 2025–26,
    the detector's window, so it is anachronistically absent from 2023–24 where
    some machine text certainly exists unmeasured.

**A caveat that constrains how this can be read.** The instrument is Kobak et
al.'s list, derived from PubMed abstracts — American scientific English. Chamber
*levels* are therefore partly definitional: a US-derived yardstick will score US
speech high whatever is happening. The defensible comparison is the *within*-chamber
trend, and that is where the finding sits.

**What post-training does resembles what already distinguished American
usage.** If the two processes select for the same thing, the vocabulary shift
instruct-tuning induces should line up with the difference that already
separated American from British legislative speech before any model existed.
Measured on 4,823 words in a 2006–10 window, it does, weakly and
specifically:[^r45b]

| contrast | Spearman | partial, holding frequency |
|---|---|---|
| post-training preference vs log(US/UK) | **+0.081** | **+0.086** |
| vs log(Canada/UK) | +0.012 | +0.012 |
| vs log(Australia/UK) | +0.018 | +0.004 |
| vs log(US/Canada) | +0.083 | +0.088 |

Permutation p < 0.005. The **discrimination** carries more than the coefficient:
Canada and Australia are anglophone parliamentary democracies too, and
post-training moves models toward none of what distinguishes *them* from
Westminster. It is not drift away from British usage; it is drift toward
American usage specifically, and Canada — nearest neighbour to the United
States — shows nothing.

The effect is small: r = 0.081 is under one percent of variance. And the design
establishes compatibility, not cause. A shared cause predicts the same
correlation — both the models and the global drift could be downstream of an
American-dominated written corpus, with no common optimization involved. §8.6
names the instrument that would separate those two.

[^r45a]: `python occurrence_trends.py --build --report`. Word-weighted, pooled
    into fixed-composition panels; a pooled line whose membership changes
    between years is a picture of the download schedule, not a trend. Chamber
    coverage and every gap are tabulated in the output. 2023 is missing from
    most chambers because the study design excluded it as a washout year
    between the 2018–22 and 2024–26 windows.

[^r45c]: `python us/fetch_us_hist.py --years 1994-2005,2023 --per-year 60
    --tag US_DEEP_DONE`, then re-extract with `us/us_extract.py zips
    segments_us.jsonl` and rebuild. 780 sitting-day zips at 60 days/year;
    both chambers are now unbroken 1994-2026 with no missing year. The
    extraction nearly doubled the US corpus — House 66.0M to 108.2M words,
    Senate 74.4M to 144.7M. Rates are per 100k words, so uniform within-year
    sampling costs precision and not validity.

[^r45b]: `python alignment_vs_american.py`. Three families at 1,600 prompts;
    reference corpora US 37.6M, UK 44.2M, CA 74.8M, AU 88.8M words over
    2006–10 — pre-transformer, and early enough that the UK's own climb has
    barely begun, so the ratio compares two human traditions rather than two
    stages of one drift. Reported on all words. US/UK spelling pairs and
    one-word orthographic forms (`percent` for "per cent") are reported as a
    separate stratum, along with two harsher filters, as robustness only.

### 4.6 Cohort replacement, not incumbent conversion

- Arrivals bring **+1.87 per 1,000** more than incumbents (15/16 chambers). †[^r46a]
- Birth decade predicts at **t ≈ 12**; coarse occupation and post-secondary
  controls run the wrong way, *strengthening* the cohort term. Finer measures
  of both do predict the register (§4.6a) and still leave cohort intact. †[^r46b]
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
tests failed to identify it (Appendix A). Cohort is not the whole of who uses
the register, though — §4.6a adds three predictors that survive it — but none
of them identifies the cohort mechanism either.

### 4.6a Class and the register: jointly significant, individually noisy — and education is not it

The arc of this section is a correction applied twice, recorded because both
applications were the study's own committed checks. On the eight provinces,
class, education and prominence appeared to predict the register at t = 3–4.
Clustering by member and replication then removed every INDIVIDUAL certainty
— and an over-hasty first rewrite of this section called that a reversal. The
joint tests say otherwise:

**Clustering the standard errors by member** (the study's third encounter
with unclustered inference flattering a result) leaves the provincial point
estimates untouched and doubles to triples their errors: class II falls from
t = 3.40 to 1.48, IVab from 3.51 to 1.49, VIIab from −4.04 to −1.84, the
education ladder from 2.96 to 0.78. Member-years are not independent draws,
and treating them as such had manufactured the significance.

**Replication on the tier-1 panel** (US House, US Senate, UK Commons, federal
Canada, Dáil Éireann — 18,178 member-years, 2,742 members, clustered) finds
the same qualitative shape at smaller magnitude — II +0.24 and IVab +0.28
above class I, VIIab −0.51 below — with nothing individually significant
except class III, which is significant with the OPPOSITE sign to its
provincial estimate, i.e. noise behaving like noise.

The final specification — one observation per legislator at equal weight,
register z-scored within each legislature against its full member
population, HC1 errors, joint Wald beside every table
(`member_level_estimation.py`; the reasoning for each choice is in its
docstring) — settles the section:

**Class is a monotone gradient, strongest at the bottom.** At member level
(n = 3,413, joint **p = 0.0001**): VIIab **−0.306σ (t = −3.12)**, V/VI
−0.184σ (t = −2.32), IVc −0.184σ (t = −1.97), IVab −0.078, class I baseline,
II +0.054 above it. The panel specification agrees jointly (Wald p = 0.029
pooled, p ≈ 0.078 in each independent panel). Manual and farm members use
distinctly less of the register than the service classes, about a third of a
within-chamber standard deviation at the extreme.

**The II-over-I crossover is established, by the test that needs no
normalization at all.** Comparing class II to class I WITHIN each chamber —
each legislature its own control, cohort-adjusted, equal member weights —
the contrast is positive in 9 of 12 chambers, individually significant in
each of the three with the power to detect it (UK +0.68, t = 2.48; US House
+0.82, t = 2.10; Manitoba +2.26, t = 2.21), and the inverse-variance
meta-analysis across chambers gives **+0.59 per 1,000, z = 3.50**. One
regression variant (full-population z-scoring) reads +0.054σ at t = 1.57 — a
diluted positive, not a contrary result: same sign as every other view,
within 1.2 se of its sibling regression, short of the threshold because that
scaling down-weights exactly the large low-variance chambers where the
contrast is largest. Under heterogeneous per-chamber effects, differently
weighted estimators answer differently weighted questions; no specification
at any point estimated the contrast negative. (The within-chamber meta was
computed after the variants diverged; it corroborates rather than
adjudicates.) Teachers, nurses and journalists out-use lawyers, physicians and
professors, within their own chambers, on both sides of the Atlantic —
Labov's crossover, in this register. The exact location of any peak remains
a non-claim: under a chase-and-flight cycle the peak SHOULD migrate downward
as the top tier's abandonment propagates, so peak location is dynamics, not
structure (an era-resolved peak test is future work).

**Education matters, with the same top-end structure.** Joint p = 0.0002 at
member level; the academic ladder runs **+0.065σ/rung (t = 3.42)**; a
professional degree sits below bachelor's in every specification (−0.449,
t = −2.22 raw; −0.065, ns, z-scored). The earlier "education is dead"
verdict was an artifact of raw cross-chamber pooling, where the US chambers
— nearly universal degree-holding, so almost no covariate variance — swamp
the estimate; putting chambers on their own scales recovers it.

**Origin is null, and robustly so.** Parental class, 704 members, tested
under both the panel and member-level specifications: joint p = 0.53–0.59,
group means within 0.1σ of each other. **The register tracks class
destination, not class origin** — what a legislator did, not where they came
from — which favours occupational practice over inherited-status accounts of
the gradient, stated as interpretation.

**Cohort towers over all of it.** Birth decade is **+1.01 (t = 10.96)** in
the member-year panel with year fixed effects — the citable figure, since
career-level specifications absorb era of service into the cohort term — and
survives every covariate this study has measured, in three countries and 22
chambers. For scale: the whole class gradient spans ~0.36σ; cohort covers
that in about thirteen years of birth date.

#### Class: the provincial estimates (retained as the discovery record; see the panel result above)

Coding each member's pre-political occupation into the
Erikson–Goldthorpe–Portocarero schema — two independent Claude passes over a
shared rubric, blind to each other, 96.4% raw agreement, disagreements
adjudicated (`provinces/OCCUPATION_CODING.md`) — gives 897 members and 5,294
member-years, 57.5% of the words that reach a named non-chair speaker in the
eight Canadian provinces.

Register rate against EGP class, year and province fixed effects, weighted by
words, baseline class I:

| class | | vs I | t | members |
|---|---|---|---|---|
| III | routine non-manual | **+2.00** | 4.98 | 29 |
| II | lower service | **+0.84** | 4.23 | 435 |
| IVab | petty bourgeoisie | **+0.80** | 3.24 | 180 |
| I | higher service | — | — | 186 |
| V/VI | skilled manual | +0.21 | 0.34 | 45 |
| IVc | farmers | −0.24 | −0.58 | 53 |
| VIIab | semi- and unskilled manual | **−1.66** | −4.22 | 16 |

**The peak sits one to two rungs below the top.** Teachers, nurses,
journalists, clerks and shopkeepers use the register more than lawyers,
physicians and professors do, and the manual classes use it least. Lawyers are
the single largest occupation in the corpus (40 members) and they sit *below*
teachers.

**The standard three-class collapse destroys this result**, which is worth
stating because that collapse is the conventional reporting unit. NS-SEC pools
III with IVc and V/VI with VIIab; the opposite signs cancel and the table reads
professional 35.5 / intermediate 35.3 / working 34.9 — a null. The
seven-class schema is not a refinement here, it is the difference between a
finding and nothing.[^r46d]

#### Education: the provincial ladder (did not replicate; see above)

Education behaves the same way once the ladder is separated from the
professional track. On the academic rungs alone — secondary, college,
bachelor, graduate — register rises **+0.366 per rung** (t = 3.30), and
**+0.315** with birth cohort controlled (t = 2.96). Treating a professional
degree as a rung above a master's zeroes the linear term entirely, because
law and medicine sit **−0.785 below bachelor's** (t = −3.49). A professional
degree outranks a bachelor's on any ordering, so that dip cannot be attainment;
it is the same class-I effect arriving through a second instrument.

#### The shape has a name — held now as hypothesis, not finding

The second-highest status group exceeding the highest is Labov's crossover
pattern, and the middle tier's described disposition matches his linguistic
insecurity. After clustering, the crossover here is a recurring direction in
two panels rather than a demonstrated effect, so the parallel is a hypothesis
the enlarged panel failed to confirm at conventional thresholds — not a
replication of Labov. It stays because the shape recurred independently and
because the flight result below is measured on pooled text rather than
member-level inference, but nothing in this subsection should be cited as
established.

#### Flight: class I avoids the words that became common

What distinguishes class I is *which* words it avoids. Across style words with
enough volume in 2023–26, the correlation between a word's post/pre lift and
class I's relative use of it against class II is negative at every volume
threshold and strengthens monotonically with volume: ρ = −0.13 at 100+
occurrences, −0.22 at 300+, **−0.42 at 800+ (p = 0.004)**, −0.46 at 1,500+.
Class I under-uses `primary` (2.35× lift), `advocating` (1.85×), `advocates`
(1.57×), `outcomes` (1.54×); it over-uses `remarkable`, `individuals`,
`broader`, `ultimately` — words that barely moved.

That is chase-and-flight: a marker loses value as it is copied, so the group
that holds it abandons the most conspicuous forms first. Jhering stated it in
1883 — fashion, once universally adopted, "condemned by its very nature to
renew itself continuously" — and Veblen and Simmel gave it its standard form.
Lieberson is the closest parallel to our case, because his markers are discrete
lexical items: first names diffuse down the status ladder and are abandoned by
higher-status parents once they become common.[^r46e]

#### Prominence: the same direction, a different variable (not yet re-tested)

The result below is provincial and its errors are NOT clustered by member;
given what clustering did to the class and education arms, treat it as
unconfirmed until the panel re-run includes it.

Each member's Wikipedia article length — fetched from the MediaWiki API through
their Wikidata identifier, so it is a measured page property and not a
judgement (`wiki_depth.py`, 1,354 of 1,396 members resolved, median 8,924
bytes, range 1,478 to 136,048) — predicts the register **negatively**. Members
with longer articles use less of it.

On the 4,437 member-years carrying class, depth and birth year together:

| | alone | with class | + cohort and volume |
|---|---|---|---|
| log article length | −0.607 (t −4.9) | −0.590 (t −4.6) | **−0.747** (t −6.2) |
| class II vs I | +0.654 (t 3.1) | +0.464 (t 2.2) | +0.416 (t 2.1) |
| class IVab vs I | +0.793 (t 3.0) | +0.541 (t 2.0) | +0.570 (t 2.2) |
| class VIIab vs I | −1.563 (t −3.9) | −2.002 (t −4.9) | −2.176 (t −5.8) |
| birth decade | | | **+1.400** (t 16.3) |
| log words spoken | | | −0.461 (t −4.0) |

Each absorbs about a quarter of the other and both survive. So the study has
three partially independent predictors, and the two new ones point the same
way: **the more established the speaker, the less of this register they use** —
at the level of occupational class, and again at the level of individual
prominence within a class. Volume runs the same direction; members who speak
more use it less.

WP:NPOL gives essentially every elected member an article, so existence
discriminates nothing and depth is the usable instrument. It was collected as a
control on notability bias in the education covariate — members whose education
we know have **1.80× the median article length** of those we do not, so that
bias is real and measured — and it turned out to be a result in its own right.

#### Word mix: the effects live in rate, not vocabulary — and machine text sits outside the geometry

A composition check (`vector_analysis.py`, methodology and full results in
`VECTOR-ANALYSIS.md`): normalising each member's style-word vector to its own
sum and z-scoring across 1,356 members, there are no prior-free clusters
(silhouettes fall monotonically in k; PC1 carries 71% of variance), and class,
education and cohort correlate with the mix at |r| ≤ 0.20 — **the standing
effects above are about how much register a member uses, not which words**.
Machine-flagged speech resembles no class tier (peak z-cosine +0.12 against a
human control's +0.47), and in the one clean base/instruct pair available,
post-training moves the model's mix **out of the human class geometry**:
Sonnet 5, Opus 5 and Fable 5 traces are negative against every human class
and education centroid and are the only text sets positively similar to the
machine-flagged legislature pool. qwen3's move *up* (class II/bachelor to
I/graduate) is the outlier among five measurable families. Extending the
comparison to the older Claude versions still serving (Sonnet 4.5, Opus 4.1,
Opus 4; 300 audited continuations each) sharpens this into a **family
signature**: all six Claude models are positive against the flagged pool
(+0.016 to +0.186) and all five open-model sets negative (−0.024 to −0.063),
stable across three model generations. Within-family ordering is not
interpretable at these sample sizes, but the family split is clean — the
flagged text shares distinctive vocabulary with one lineage and not the
other. This is register lineage, not attribution (§8.6 A.1b). Register
*rate* is also a lineage property: Opus sits at base-model rate across three
generations (2,696–2,837 per 100k), Sonnet runs hot in both versions
(4,639–5,116), and Fable 5, at 3,369, is the first model measured that lands
inside the human class range at all. Scored AI use itself runs *highest* in class I
(11.3% vs II's 5.7%, 27-segment cell, suggestive only). Interpretation,
recorded as such in VECTOR-ANALYSIS.md: because register and prevalence can
now be measured explicitly, a legislature with a stated goal of fair
representation can control for them — a fairness mechanism independent of the
social dynamics this section documents, which are expected to persist.

#### Limits, and they are real

Article length is measured once, in 2026, and applied to every year of a
member's career. A backbencher who later became premier carries their eventual
prominence backwards through the series. That biases toward finding nothing
rather than something, since it adds noise to the regressor, but it means the
coefficient is not a clean within-career estimate.

Class III's premium is a cohort effect and should not be read as class.
Controlling birth year alone moves it from +1.03 to −0.32, and the mechanism
is compositional: III's median birth year is 1974 against 1956–1960 for every
other class — routine non-manual members are the chamber's young class, by
sixteen years. The rest of the curve is age-robust on the same subsample: II
and IVab strengthen slightly under the control (+0.68, +0.91), VIIab holds at
−1.51, so the peak sits at IVab/II rather than III and the crossover reading
is unchanged.

Classes III and VIIab rest on 29 and 16 members. Their standard errors treat
repeated years of the same person as independent, so the true intervals are
wider than shown and those two rows should not be quoted as significant. II and
IVab, at 435 and 180 members, carry the finding.

The chase-and-flight correlation strengthens as the volume cut rises, and that
cut was chosen before the pattern was seen but not pre-registered. Two readings
are consistent with the monotonicity — flight genuinely concentrates on the
common forms, as the theory says, or low-volume words are noisier and
attenuate the correlation — and this data cannot separate them. What argues
against an artifact is that the sign is negative at all six thresholds,
including the widest and least significant.

Both effects leave cohort intact. Birth decade runs **+1.20 to +1.36 per
decade** in every specification here, larger than any class or education
contrast.

[^r46d]: `python covariate_study.py`, `python class_origin.py --dist`. Coding
    workflow and rubric ambiguities in `provinces/OCCUPATION_CODING.md`; the
    adjudicators' fifteen flagged ambiguities cluster on exactly the I/II and
    service/manual cuts the schema turns on, which is a caveat on the coding
    and not on the register measurement.

[^r46e]: `python class_markedness.py`, `build_class_word_year.py`. An earlier
    version of this test used the *most-risen* words rather than the
    *most-used* ones and found nothing; the theory predicts flight from gross
    forms, so rare risers are the wrong test set. A separate cross-sectional
    result — class I holding the lowest share of marked words overall — did
    not survive a year control and is not reported. **Citations in this
    subsection are UNVERIFIED**: gathered from reference pages, not primary
    texts, and one fetched entry was already wrong on year and publisher. See
    `CLASS-REGISTER-LITERATURE.md`. None should reach a published version
    before the books are opened.

### 4.7 The register is a post-training artifact

OLMo-2 ladder, same prompts across the post-training stages. The stage values
are bias-corrected: the estimator as first shipped carried a per-transition
pedestal (the M3 defect, per stage — null calibration on random word lists
returns +0.45/+0.56/+0.31, largest at DPO only because DPO's generations are
longest), and three independent corrected routes agree on the picture below
(exact stratified estimator shown; audit values in the 2026-08-11 review, M9):

| stage | register shift (corrected) | shipped, superseded |
|---|---|---|
| SFT | +0.32 | +0.76 |
| DPO | +0.27 | +0.86 |
| RLVR | **+0.06** (CI straddles 0) | +0.37 |

Pooled alignment effect **+0.387** on the scaled generation — three model
families, 1,600 prompt pairs each, 1.19M base words.[^r47] SFT and DPO
contribute **indistinguishably** (paired bootstrap over 800 shared prompts:
DPO − SFT = −0.08, 95% CI [−0.31, +0.15]), so no stage ordering is supported —
an earlier version leaned on "largest at the preference stage," and that
ordering was the pedestal, not the data (Appendix B). What remains true, and
is kept as a datapoint rather than a load-bearing link: the register is
installed by the stages tuned toward human demonstrations and preferences, and
not by the stage tuned toward verifiable correctness. That is consistent with
§4.5's reading that alignment concentrates something humans already favoured —
an association, not an identified mechanism, and the section's argument no
longer rests on it. The correction
STRENGTHENS the arm's design claim: **RLVR was the pre-registered placebo** —
tuning on verifiable math/code correctness should not install a speech
register — and corrected it behaves exactly as the placebo it was designed to
be, where the shipped +0.37 (p = 0.000) had it failing its own manipulation
check. Post-training as a whole installs the register; base→instruct
end-to-end (+1.24) is untouched.

**Quote the well-measured figure, not the pooled one.** The same run reports
+0.6311 pooled over every style word present and +0.3872 restricted to the 82
words with at least 20 base occurrences. Doubling the data separates them: the
well-measured estimate is flat (+0.3881 → +0.3903, a move of +0.0022 from 800
to 1,600 prompts on the same families) while the pooled estimate keeps climbing
(+0.6074 → +0.6235, and on Qwen3 alone +0.6776 → +0.7481 from 1,600 to 3,200).
A quantity that grows with sample size is not converging on anything. The
pooled figure includes style words with zero or near-zero base occurrences,
where the 0.5 pseudocount sets the value, and more data keeps pulling in more
of them.

**All four families are positive on their own** — +0.356 to +0.749 pooled —
which matters more than the pool, since it is four independent replications
rather than one estimate. The 30B mixture-of-experts model is the weakest at
+0.067 well-measured, but it is also the only family whose instruct side never
passed 800 prompts, with just 37 style words clearing 20 occurrences. That is
an unresolved flag, not a counter-result.

[^r47]: Ladder stages: `python olmo_ladder.py` (end-to-end base→instruct
    **+1.2420**). The **+0.387** is a *separate* experiment on other model
    families: `python rlhf_pref_compile.py`, reading the generation built by
    `rlhf_pref_scale.py` at 400 new tokens over 3 families at 1,600 prompt
    pairs each and 1.19M base words. It is not a pooling of the three OLMo
    stages, and it is not produced by `align_ratio.py report`, which prints the
    Hansard-drift arm instead.

    Controls are drawn from the union of the base and instruct vocabularies and
    bucketed on the combined count. Both details are load-bearing. Drawing only
    from words the base model emitted makes a control absent from base output
    impossible while 27% of the style words are exactly that, and bucketing on
    the base count alone selects controls on the ratio's own denominator. An
    estimator with either flaw returns **+0.45** on 30 random
    frequency-matched word lists — a pedestal for lists with no special
    property at all. The estimator used here returns +0.003 on those same
    nulls, so the +0.387 sits on nothing.

    The run stopped at 1,600 prompts rather than its planned 6,400. The 30B MoE
    pair cost about six times its estimate, because a mixture-of-experts model's
    active-parameter advantage does not survive batching — at batch 48 the
    sequences route to different experts and the union touched per step
    approaches the whole model. Active-parameter arithmetic describes batch 1.

### 4.7a Coverage: post-training moves the model's vocabulary onto Hansard's

§4.7's excess runs over Kobak's 407 style words, and only about half appear in
the generated corpus. The standing answer was a presence count — real Hansard
covers barely more of the list at the same volume, so the list is partly
out-of-domain and 407 is the wrong denominator. That is a summary of a
distribution, and the distribution says something the summary hides.

At matched volume, style words by number of occurrences:[^r47a]

| corpus | **0** | 1–2 | 3–5 | 6–10 | 11–20 | 21–50 | 51+ |
|---|---|---|---|---|---|---|---|
| generated base | **158** | 82 | 32 | 24 | 29 | 29 | 53 |
| generated instruct | **118** | 60 | 40 | 33 | 31 | 46 | 79 |
| Hansard pre-2023 | **86** | 80 | 55 | 39 | 42 | 39 | 66 |
| Hansard 2025–26 | **85** | 82 | 47 | 40 | 37 | 49 | 67 |

The shapes differ, so the defence only half holds: at equal volume the
generated corpus has by far the fatter zero bin, and part of the missing
coverage is a property of the generation rather than of the word list.

**The overlap is the result, because it says which words are missing rather
than how many.** Partitioning the 407 against Hansard 2025–26:

| | absent from both | absent from generated only | absent from Hansard only | present in both |
|---|---|---|---|---|
| base | 72 | **86** | 13 | 236 |
| instruct | 63 | **55** | 22 | **267** |

Only **72 words are absent from both** — that is the genuine out-of-domain
share, well under what a presence count implied. And post-training moves the
model onto Hansard's vocabulary: the words real legislators use that the model
does not fall from **86 to 55**, and the words both use rise from 236 to 267.

This is §4.7's claim arriving by a different route. It needs no control
matching, no frequency bucketing and no pseudocount — it is a count of which
words appear — so it is not exposed to the estimator defect that cost §4.7 its
original +0.88. Two measurements of the same shift, one of which cannot fail in
the way the other did.

**What the models never produce is the reason to be careful.** The words
present in 2025–26 Hansard and absent from our generations are the archetypal
ones: *transformative, unlocking, enhances, groundbreaking, leveraging,
pioneering, pivotal, amid*. Our 8B open models do not emit that register;
whatever is putting it in the record is not them. So the base-versus-instruct
contrast is a **directional proxy for what post-training does**, not a model of
the register actually appearing in Hansard, and §4.7 should not be read as
reproducing the thing §4.2 detects.

[^r47a]: `python style_word_frequency.py`. Three families at 1,600 prompts;
    every corpus truncated to 1,187,489 words, base and instruct counted
    separately — pooling them doubles the generated volume against a
    volume-matched human corpus and manufactures parity, which an earlier
    version of `style_coverage.py` did.

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
member can defeat the detector cheaply, 9.0% is a floor and detection-based
prevalence is a dead end. Four search runs across two chambers, **461 rewritten
variants of 92 distinct originals** — 106 were attacked, and the two New
Brunswick searches re-attack the same 40 texts — each variant scored by
Pangram.
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
allows up to eighteen attempts. Like-for-like on single detector submissions
the multiple is **3.7×** (8.5% against 2.31%). One point of transparency about
that 8.5%: it is the rate per variant *submitted to the detector*, and the
search generates several Opus rewrites per submission, screening them on
Opus's own AI-score and plausibility before spending a detector query on the
survivors (≈461 submitted of ≈1,830 generated; §methodology). This is the
attacker's actual flow, not a distortion of it — the Opus self-score is free
and available before any detector call, so a real adversary screens exactly
this way rather than submitting every draft. The number to read it against is
therefore per detector submission, which is what the vendor rows also are. (An
unconditional per-generated-rewrite rate would be ≈2.1%, but that counts drafts
no attacker would submit, so it understates the operational threat.) The
tenfold per-target figure is unaffected either way — discarding candidates can
only lose targets, never gain them, so 22.5% per target is conservative
regardless.

**Two rates, and both belong here.** They answer different questions and the
gap between them is threefold, so quoting either alone misleads.

**The per-variant figure — 8.5%, all four runs.** How often a variant
submitted to the detector defeats it, in a search that pre-screens Opus
rewrites on Opus's own score before submitting (§methodology gives the
generated:submitted ratio). This is the realistic per-detector-query rate; it
is not a per-Opus-generation rate.

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
| **this study, per detector submission** | **8.5%** | **induced FNR under an iterative search that self-screens rewrites before submitting — 3.7× the humanizers** |
| *this study, per target* | *22.5%* | *induced, ≤18 attempts — 9.8× the humanizers* |
| Rice 2026, Australian Hansard | ~8% | **false *positive* rate**, n = 50 |

**The per-detector-submission row is the one commensurable with the vendor
rows**, which are also document-level FNRs per submission on adversarially
prepared text. The difference is method, not accounting: our submissions are
the survivors of an Opus self-screen, i.e. a stronger attack than a single
humanizer pass, which is why 8.5% exceeds the 2.31% commercial rate. Read as a
comparison of point estimates; clustered on text the per-variant interval runs
[4.0, 13.4], so the vendor figures sit below our estimate but within its lower
tail — the ordering is secure, its margin less so. And the comparison is a
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

**Evasion-directed rewriting does not measurably change deliberative
quality.** Two paired arms, 63 within-text pairs, blinded and interleaved,
graded on the same v2b DQI rubric: stage 3 is 38 New Brunswick pairs (the v3
ladder variants), stage 4 is 25 Government Orders pairs from the **GO
Opus-selected run** — not the GO all-31 arm of the bypass section above, with
which it shares no segments. Named precisely because of what the verdicts
show: **61 of the 63 graded rewrites did not clear the detector** (stage 3:
AI 29 / Mixed 7 / Human 2; stage 4: AI 23 / Mixed 2). What is measured is the
effect of rewriting *under an evasion instruction*, not of successful evasion
— the selection was by the Opus proxy, not the Pangram outcome, so this graded
set is not conditioned on failure. The complementary arm, graded ON the
Pangram outcome (the successful reversals), is stage 5 below. Within-text pairing holds content, speaker and occasion fixed by
construction, so these are the raw paired differences — the design's own
estimand, needing no covariate. **Every dimension is null on both.**[^r49b]

| dimension | stage 3 (n=38) | stage 4 (n=25) |
|---|---|---|
| justification | +0.05 (t +0.6) | +0.16 (t +1.7) |
| common_good | −0.05 (t −0.8) | 0.00 (t 0.0) |
| respect_groups | −0.08 (t −1.8) | +0.04 (t +1.0) |
| respect_demands | −0.08 (t −0.6) | 0.00 (t 0.0) |
| respect_counterargs | +0.33 (t +1.8) | +0.12 (t +1.0) |
| constructive | 0.00 (t 0.0) | −0.12 (t −1.8) |
| evidence | +0.03 (t +0.4) | +0.08 (t +0.7) |

**Stage 5 grades the successful evasions themselves, and finds the same
null.** Conditioning on the outcome — the complement of stages 3/4 — every
rewrite that reached a Human verdict (39 variants across 15 targets, one
target's original text unavailable and dropped) was graded blind against its
original on the same v2b rubric, two independent passes (inter-pass exact
agreement 79–100%). No dimension moves at either level:

| dimension | variant (n=35) | target (n=15) |
|---|---|---|
| justification | −0.14 (t −1.7) | −0.03 (t −0.2) |
| common_good | +0.01 (t +0.3) | +0.03 (t +0.4) |
| respect_groups | +0.04 (t +1.0) | +0.10 (t +1.2) |
| respect_demands | −0.01 (t −0.6) | 0.00 (t 0.0) |
| respect_counterargs | +0.11 (t +0.9) | +0.10 (t +0.4) |
| constructive | +0.03 (t +1.0) | +0.07 (t +1.0) |
| evidence | −0.01 (t −0.2) | +0.04 (t +0.3) |

The lone lean — justification at variant level (t −1.7) — collapses on
aggregation to targets (t −0.2), a within-target artifact of multiply-graded
targets, not a cost. So the two arms bracket the claim: **evasion-directed
rewriting is null (stages 3/4) and evasion-ACHIEVING rewriting is null (stage
5).** (A note the DQI judge's own `ai_guess` adds: it rated the successful
evaders 36/100 against 40 for the human originals — barely less AI-like — so
the two detectors disagree on this set even as neither finds a quality
difference. `stage5_scores.json`, `PREREG-stage5-successful-evasion.md`.)

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
in deliberative-quality terms — so 9.0% is a floor, and the honest reading is
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
  targets** (§4.9), so 9.0% is a lower bound. How much of a lower bound is
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
not a small residual: the 9.0% in §4.2 exists precisely because nobody
currently bothers to evade, or the undisguised register signature would not be
there to find. **Detection is a norms instrument, not a security instrument** —
locks, not vaults. It raises the cost of casual undisclosed use and does
nothing against motivated use, and that is a coherent thing for a chamber to
want. It is also what lets 9.0% stand as a measurement of disclosed-by-default
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

And the fallback people reach for when a detector is unavailable — their own
sense of whether text "reads like a person" — is worse than unreliable on
adversarial input; it is anti-correlated with the truth. Asked to judge
AI-likeness by register, a frontier reader flagged 13 of 35 genuine human
floor speeches and only 5 of 35 machine rewrites that had been optimised
against a detector (§4.9 stage 5): adversarial optimisation removes exactly the
tells gut judgment keys on, so the errors of a vibes-based adjudicator
concentrate on the *unoptimised* — ordinary speakers who ran their words
through nothing. As machine-assisted text spreads, register ceases to carry
authorship information at all, and any institution still adjudicating
authenticity by feel will manufacture false accusations that fall hardest on
the people least equipped to contest them. (One unblinded, lineage-correlated
judge on 35 texts; illustrative, not a measured effect — see the future-work
item below.)

### 8.3 The substitution, and why our null is the argument for it

If provenance is the wrong thing to spend effort on, the question is what to
spend it on instead. The answer available from this study is: **check the work
directly.**

The case rests on §4.9's primary finding, and it is independent of evasion:
machine-assisted text grades **better-formed, not worse-engaged** on the DQI —
so policing authorship does not protect quality, because the authorship
detection would flag is not where the quality deficit is. That is the whole
argument: **quality assessment is orthogonal to provenance, not a proxy for
it.** Had DQI tracked authorship, it would merely be a worse detector; because
it does not, it measures the thing anyone actually wanted to know. The paired
evasion arms add a separate, secondary reassurance for anyone worried about
the arms race specifically: rewriting under evasion pressure did not move any
of the seven dimensions across 63 within-text pairs, and neither did the 39
rewrites that actually cleared the detector when graded on their own (§4.9
stage 5), so a body that measures quality directly need not fear that evasion
— attempted or achieved — degrades the metric it watches.

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
   exist: the base-versus-instruct generation that produced §4.7's +0.387 yields
   an empirically derived list of what post-training adds *to legislative text
   specifically*. Split that list into register-like and substance-like by an
   independent rule and run both through the frozen protocol as separate arms,
   giving "did the register shift" and "did the substance shift" as two
   measurements instead of one. Estimated at a few hours. This is the single
   most valuable unrun item, and it is also a limit on the present study rather
   than merely an extension (§5).

1a. **A register-feature instrument, and the test that would settle §4.5a.**
   Every arm in this study measures register through a *word list*, which is
   why §4.5a's American result can be read two ways: the correlation is carried
   partly by managerial and topical vocabulary, and a word list cannot separate
   "models adopt American subject matter" from "models adopt the American way
   of arguing". The features that would are syntactic and stance-bearing, not
   lexical: hedge and modal density (*may, might, tends to, somewhat*),
   first-person plural rate, concessive construction (*while X, nonetheless
   Y*), agentless passives, subordination depth, and a balance marker for
   on-the-one-hand structure. None of them can be carried by *senator* or
   *dollars*.

   Run that instrument on two contrasts at once — base against instruct, and
   US against UK in the pre-transformer window — and the thesis behind §4.5a
   becomes falsifiable. **If both contrasts move the same features in the same
   direction, alignment and the American public tradition are selecting for the
   same thing.** If post-training raises hedging and inclusiveness while the
   US–UK difference sits somewhere else entirely, the lexical correlation was
   subject matter and the soft-power reading fails. Either outcome is
   informative, which the present measurement is not.

1b. **Vendor attribution for the family signature.** §4.6a's vector result —
   every Claude model positive against the flagged legislature pool, every
   open model negative, across three Claude generations — is *consistent
   with* Claude drafting but cannot attribute, because the discriminative
   controls are missing: no GPT, Gemini or Llama-instruct-served traces exist
   on the same prompt pool. The design is already fixed and cheap: the same
   800-prompt continuation protocol (45-word Hansard openings, ~300 words,
   no styling instructions, thinking off), run through each major vendor's
   API, audited for uniqueness and degeneracy before entering any table
   (the audit is not optional — two of nine Claude trace sets failed it in
   ways that specifically corrupt this measurement). If the flagged pool's
   similarity peaks on one vendor's family and is flat or negative on the
   others, the signature becomes evidence *about* usage rather than
   consistency with it; if several vendors' models all match, the signature
   is a frontier-register commons and attribution is off the table — which
   would itself bear on §4.5a's homogenization reading. Two caveats bound
   even the positive outcome: models train on one another's output, so
   lineage blurs with each generation, and the flagged pool (126 segments,
   1,495 instrument occurrences) should be enlarged first — the §4.2 sample
   grows it mechanically as more chambers are scored.

   This pairs directly with §8.5. A register-feature profile is a measurable
   *automated counterpart*: it says what an aligned model's stance profile
   looks like on the same task, so a speaker's distance from it is the residual
   §8.5 asks for — and unlike a detector score it decomposes into named
   features rather than one number. It also gives §8.6.1's register/substance
   split a principled rule, since the two lists are constructed by different
   criteria rather than by splitting one list in half.

1c. **The anti-correlation of gut judgment, measured properly.** §8.2's
   sharpest claim — that register-based human judgment of authorship is
   anti-correlated with the truth on adversarial text, flagging real humans
   more than optimised machine rewrites — currently rests on one unblinded,
   lineage-correlated judge (the DQI grader shares a family with the search's
   own Opus proxy) over 35 texts, where the paired effect is directional but
   not significant (−4 points, t = −1.15). The confirmatory design is cheap
   and pre-registerable: recruit human raters (or at minimum a
   non-Claude-family model, so the judge is independent of the optimisation
   target), give them a balanced blind mix of genuine floor speech, ordinary
   machine drafts, and detector-optimised rewrites, and record whether the
   false-positive rate on real humans exceeds the miss rate on optimised text.
   If it does, "detection cannot underwrite an accusation" strengthens from a
   statement about detectors to a statement about human judgment itself, with
   a measured false-accusation rate attached — the number a disclosure-norm
   policy would actually need.

1d. **A search that targets the human judge, to measure the vulnerability's
   ceiling.** The bypass arm (§4.9) optimises rewrites against a *statistical*
   detector; 1c shows human register-judgment is already anti-correlated with
   truth on that output as a side effect. The complement is a search whose
   objective IS a model of the human reviewer — rewrite to minimise a
   held-out human-proxy's AI-likeness rating (and, in the strong form, to
   maximise its rated authenticity above the genuine-human baseline). This
   measures how far "more human than human" can be pushed when it is the
   explicit target rather than a by-product, i.e. the ceiling of the
   false-accusation problem a disclosure regime would face. Framed and run as
   MEASUREMENT of an adversary's reachable frontier, not as a deployable
   deception tool: the deliverable is the reachable rating gap and what text
   features drive it (pairing with the §8.6.1a register-feature instrument, so
   the output is named features rather than a black-box rewrite), reported so
   that reviewers and disclosure policies can be built against the ceiling
   rather than the current floor. The obvious dual-use tension is real and is
   the reason to publish the ceiling openly rather than leave it to be found
   privately.

1e. **The detection game — 1c and 1d as one self-generating instrument.**
   Human and AI participants each continue a shared prompt (legislative, or an
   Apples-to-Apples card for reach); humans rate each submission's
   LLM-likelihood under a proper scoring rule, blind to the human:AI mix. The
   independent variable is how much human-review feedback each AI generator
   sees — none / own aggregate / others' games only / full transcripts — a
   dose-response ladder for the value of human-review signal to an adversary.
   One apparatus yields three curves: human detection accuracy over rounds
   (does it fall as models adapt?), the AI pass-rate ceiling by condition (1d,
   under consent), and the false-accusation rate on real humans (1c, at scale
   and with real raters rather than the single lineage-correlated judge behind
   §8.2). The game frame is what makes it practical — participation is
   intrinsic — and it is the ethical form of 1d, since the human-targeting
   search runs inside a disclosed, consented frame. Design detail in
   `plans/S10-detection-game.md`.

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
8. **Provincial AI prevalence** — the Canadian provinces average 9.1% machine
   by words against US House 12.1%, so removing machine text *widens* the gap
   they were supposed to explain. Wrong sign, not merely small.
9. **Skilled-immigration share** — ρ = +0.26 on levels, +0.09 on growth, n = 6.
10. **Province-level post-secondary share** — ρ = −0.04 on levels, +0.11 on
    growth, n = 7. Note this is the *aggregate* null; the member-level
    education ladder in §4.6a does predict, which is the difference between
    seven data points and three thousand.
11. **Graduate/professional as a binary** — null in every province (BC −0.25,
    MB −0.26, NL −0.24, ON −0.30, SK +0.23, none significant; PE +2.19 on 87
    member-years is one hit in six). The binary fails because it pools a
    graduate degree (+0.01) with a professional one (−0.79); the ordered
    ladder in §4.6a is what recovers the effect.
12. **Cross-province education composition** — ρ = 0.00 against graduate
    share, and ρ = 0.00 against source tier. Not usable in any case: coverage
    runs 5% to 81% across provinces and the two best-covered provinces are the
    two sourced from Wikipedia, so a province-level regression would be
    fitting a source dummy.
13. **Markedness as pre-AI rarity** — null. Rare-word share of instrument use
    is 0.22–0.25% in every class, differences within ±0.02pp. The class effect
    is a uniform scaling of the instrument, not a re-weighting, when
    "conspicuous" is defined as rare *before* the machines. Defining it
    instead as *risen* and *common* is what produces §4.6a's result.
14. **Class I avoiding marked words, cross-sectionally** — did not survive a
    year control. Pooled, class I held the lowest share of the most-risen
    words (−1.76pp against VIIab); within era it is level with class II
    (1.48% vs 1.49% in 2023–26) and higher in 2020–22. The pooled table was
    class I's year distribution. **Recorded because it was reported before the
    control was run** — the third time in this study that unclustered or
    uncontrolled inference produced a flattering result.
15. **Wikipedia article depth as a confounder of the education effect** — null,
    and only in that narrow sense. The notability selection is real: members
    whose education is known have 1.80× the median article length of those
    whose is not. But controlling for depth moves the education coefficients by
    0.00 to 0.11, so the education results are not artifacts of who has a long
    article. Depth's own strong negative effect on the register is **not** a
    null and is reported in §4.6a.

16. **Class origin (parental EGP) against register** — first measurement,
    704 members with a coded parental class across thirteen chambers:
    intermediate-origin +0.09, working-origin +0.12 against
    professional-origin, t ≈ 0.2. Nothing.
17. **The education ladder at panel scale** — provincial +0.32/rung fell to
    +0.26 (t = 0.78) under member clustering and to −0.13 (t = −1.4) on the
    tier-1 chambers. The §4.6a provincial ladder was unclustered inference.
18. **Class contrasts at panel scale** — every §4.6a class coefficient loses
    conventional significance under clustering except VIIab (−0.79,
    t = −1.99). Point estimates keep their signs in both panels; magnitudes
    halve out of sample.

Together these say the cohort effect is real and its **mechanism is not
exposure as we can measure it.** Items 9–12 say the same of composition at the
*chamber* level: nothing about who a legislature recruits explains why it
climbs. What does carry is measured on individuals, not on chambers.

## Appendix B — Superseded analyses

0a. **§4.7's stage ordering** — "the shift is largest at the preference
   stage" rested on a per-transition estimator pedestal (M9; the M3 defect
   per stage). Corrected by three agreeing routes: SFT ≈ DPO, RLVR ≈ 0. The
   §4.5 connection is DE-EMPHASIZED rather than withdrawn (Matthew): the
   preference-and-demonstration stages installing the register while the
   correctness stage does not remains an interesting association, but the
   text no longer relies on any stage ordering, and the RLVR placebo now
   passes its own manipulation check.

0. **§4.6a, twice** — first written as "standing predicts the register
   downward" at t = 3–4 (unclustered provincial estimates, the study's third
   unclustered-inference incident); then over-corrected to "did not survive
   its own checks" on per-term t-tests alone. The joint Wald (p = 0.029
   pooled) and the cross-panel shape replication showed the over-correction
   wrong within a day (Matthew caught it from the preserved ordering). The
   standing version reports all three layers: jointly significant class,
   dead education/origin, dominant cohort. Both superseded framings are part
   of the record.

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
| `covariate_study.py` | §4.6a class and education, member level (`--build-cache` first, ~10 min) |
| `class_origin.py` | §4.6a EGP/NS-SEC arithmetic over the checked-in coding |
| `class_markedness.py`, `build_class_word_year.py` | §4.6a chase-and-flight |
| `build_member_vectors.py`, `vector_analysis.py` | §4.6a word-mix geometry; VECTOR-ANALYSIS.md is the full log |
| `claude_gen/`, `claude_gen_old/`, `rlhf_gen_180/` | generated traces behind the family-signature table (audited) |
| `provinces/occupation_coding.json` + `OCCUPATION_CODING.md` | the coding itself, with its 96.4% agreement rate |
| `wiki_depth.py` | article length via Wikidata QID → MediaWiki, the notability control |
| `build_allsource_merge.py` | rebuilds `member_allsource.json` from the workflow journal |
| `CLASS-REGISTER-LITERATURE.md` | §4.6a citations, **unverified**, with the suspect entries flagged |
| `band_coverage_check.py` | standing check that every length band is sampled at its chamber's own rate |
| `olmo_ladder.py` | §4.7 ladder stages |
| `rlhf_pref_compile.py` | §4.7 **+0.387** well-measured, 3 families at 1,600 prompts |
| `rlhf_pref_analyze.py` | the superseded +0.42 run, with null calibration (not `align_ratio.py`) |
| `align_ratio.py` | §4.7 Hansard-drift arm |
| `word_context_delta.py` | §4.8 in-context permeation |
| `bypass_report.py` | §4.9 bypass, all four runs pooled |
| `go_reflip_fractions.json` + `nb_`/`bp_` | strict re-scores behind the 8.0% |
| `quality_expansion/` | §4.9, self-contained (`RUNME.md`) |
| `BYPASS_METHODOLOGY.md` | §4.9 selection filters, per sample |
| `PRIOR_ART.md`, `ai_policy_scan.md` | §6, §7 |

**What this was run on.** Three resources, and the commercial detector is the
smallest of them.

*Pangram*, a commercial detector, for all 4,258 verdicts — the prevalence,
calibration, genre and bypass-outcome numbers.

*A frontier-model subscription* (Claude Code) for everything that needed a
frontier model rather than a detector. Which model did what matters here and is
not interchangeable:

| arm | model | effort |
|---|---|---|
| Corpus-wide screen (§4.4), effort A/B | Claude Opus | low, and max in the A/B |
| Bypass search: scoring / rewriting / hypotheses (§4.9) | Claude Opus | low / medium / high |
| DQI grading, all four stages (§4.9) | **Claude Fable 5** | default |
| Synthetic in-domain sensitivity corpus (§3.1) | Claude Opus | default |
| Analysis, verification, adversarial review | Claude Opus | varies |

The screen/grader split is load-bearing rather than incidental. §4.9 reports
that the screen's `ai_guess` and the grading judge's independent `ai_guess`
correlate at r = +0.758, and treats that as a leakage problem. It is one — but
it is a correlation between **two different models**, which makes it a fact
about the shared style signal rather than an artifact of one model agreeing
with itself.

*An NVIDIA DGX Spark (GB10)* for the open-weight work: the six-detector survey
that established the free instruments do not work on this register, the OLMo-2
post-training ladder, the paired base-versus-instruct generation behind §4.7,
the in-context permeation scoring in §4.8, and the open-model band screens.

Only the first is metered per document. The other two are the larger share of
the work and are not substitutable by spending more with the detector vendor.
Anyone holding all three can repeat the study; a Pangram subscription alone
reproduces the prevalence arm and nothing else.
