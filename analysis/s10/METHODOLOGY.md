# S10 methodology — every method, every number, and why

**Written to be readable by someone who has not done this kind of analysis
before.** Each section says what we were trying to learn, what could have
fooled us, what we did about it, and what the resulting number actually
licenses you to claim. Numbers are as of 2026-08-02.

---

## 0. The problem, and why it is harder than it sounds

We want to know how much legislative speech is now drafted with AI help.

The naive approach — run an AI-detector over Hansard and report the
percentage — fails for four independent reasons:

1. **Detectors are uncalibrated on this register.** They were validated on
   student essays and news. Formal prepared oratory is exactly the register
   they over-flag. A detector reporting "8% AI" might report the same 8% on
   1998 text.
2. **There is no ground truth.** Nobody discloses. We can never build a
   labelled set of "AI legislative speech" from the real world.
3. **Hansard is professionally edited.** Editors normalise prose, which can
   erase the token-level statistical fingerprints detectors rely on.
4. **Prepared speeches were always ghost-written.** "Not written by the
   member" has been true for a century. Only *machine*-drafted is new, and
   the two are easy to conflate.

Everything below is machinery for getting a defensible number despite these.

---

## 1. Corpora

Four parliaments, chosen to vary in size, country and record format:

| chamber | seats | sittings | source format | words (pre / post) |
|---|---|---|---|---|
| New Brunswick | 49 | 364 | bilingual two-column PDF | 4.4M / 2.5M |
| Dáil Éireann | 160 | 748 | Akoma Ntoso XML (API) | 36.7M / 18.7M |
| Canada Commons | 338 | 1,097 | ourcommons.ca XML | 20.1M / 11.1M |
| UK Commons | 650 | 1,137 | ParlParse XML (rsync) | 47.2M / 24.2M |
| US House | 435 | 1,554 | GovInfo CREC zips | 22.4M / 11.3M |
| US Senate | 100 | 1,554 | GovInfo CREC zips | 24.4M / 10.9M |

**Time windows are fixed by protocol**: pre = 2018-01-01 to 2022-12-31,
post = 2024-01-01 onward, **2023 excluded entirely** as the transition year.
The 2018 floor is set by the shallowest source (NB) and every deeper archive
is truncated to it, so effect sizes stay comparable
(`replication_protocol.md`, Clarification 1).

### 1.1 What per-corpus work actually consists of

Almost all of it is *excluding text that is not the member's own English*.
This is where studies quietly go wrong, so each case is documented:

- **New Brunswick** prints English and French in parallel columns, with the
  language *as spoken* on the left and the translation on the right. We
  split by word x-coordinate, language-ID each paragraph, and pair columns
  by vertical overlap. Validated per speaker: anglophone members come out
  94–99% original-English, francophones 20–22%. Result: 709k words of
  member-authored English out of 869k English words.
- **Canada** is worse, because the English edition *translates* French floor
  speech. `<FloorLanguage language="FR">[Translation]` marks where. **26% of
  scoreable "English" segments are translator-authored** and are excluded.
  Miss this and a quarter of your corpus is a professional translator's
  register.
- **Ireland** records Irish as Irish (1.0% of segments, excluded). Deputies
  often open in Irish and continue in English; those segments are correctly
  scored as majority-English.
- **UK** is monolingual, but ParlParse ships several revisions per sitting
  (2,937 files for 1,137 dates); we keep the one marked `latest="yes"`.
- **Chair and procedural speech** is excluded everywhere — by role attribute
  where the format provides one (Ireland, Canada), by name pattern otherwise.

Six New Brunswick PDFs were **truncated on the server itself** (the
content-length matched the truncated bytes); recovered with pikepdf. That is
why an early word count of 1.60M was wrong and the true figure is 1.89M.

### 1.2 Segmentation — the unit everything is measured on

1. Extract paragraphs with speaker attribution.
2. Group consecutive paragraphs into **speaker turns**.
3. Within a turn, pack paragraphs into **windows of ≤360 words, minimum 50**.

The 360 ceiling exists because Binoculars truncates at 512 tokens; the 50
floor because no instrument can score a one-line interjection. Every
downstream number is per-window, and the *turn* is retained as the
clustering unit for all bootstrap statistics (segments within one speech are
not independent observations).

NB produced 37,801 scoreable windows; UK 447,210; Ireland 251,298;
Canada 353,339.

---

## 2. The lexicon method — the core of the study

This is what produces the p-values. It uses **no AI detector at all**.

### 2.1 The instrument, and why it must be external

We count how often a fixed list of "AI-preferred" words appears, before
versus after. The obvious danger: if we pick the word list ourselves after
looking at the data, we will find whatever we picked. So the instrument is
**Kobak, González-Márquez, Horvát & Lause (arXiv:2406.07016)** — the
style-annotated subset of their excess-vocabulary list, 407 words.

Why this list is trustworthy for our purpose:
- It was derived from **15 million PubMed abstracts**, not from parliaments.
- It was built by an **excess-mortality-style design**: fit each word's
  pre-2023 frequency trend, extrapolate, flag words whose 2024 usage exceeds
  their own counterfactual. Nothing about it is hand-chosen for rhetoric.
- It was **published before** we touched any parliamentary corpus.
- Its authors hand-annotated **style vs content**; we use the style subset
  only, so biomedical topic words cannot leak in. (Their content list is
  PubMed's topic vocabulary — *lachnospiraceae*, *tocilizumab* — so it is not
  usable as a control here: whether biomedical jargon moved in a parliament is
  a fact about parliamentary topics, orthogonal to whether our style
  measurement is picking up AI. The frequency-and-dispersion-matched placebo
  already controls for in-domain churn, using words that occur in the domain.)

A second instrument — Wikipedia's *Signs of AI writing* (WikiProject AI
Cleanup) — is used descriptively. It is a hand-built editorial field guide,
so it is weaker evidence, but it is independent of Kobak and moves the same
way, which is worth something.

### 2.2 The statistic, and why this one

For each word *w* we compute a **log fold-change**: the log ratio of its
rate after to its rate before, with +0.5 smoothing so zero counts don't
explode:

```
logFC(w) = log[ (k_post(w) + 0.5)/W_post  ÷  (k_pre(w) + 0.5)/W_pre ]
```

The primary statistic is the **equal-weight mean** of logFC across all 407
words — every word gets one vote.

Why equal-weight rather than pooling all the counts together? Because
pooling is frequency-weighted, so a handful of common words dominate and
drown out the signal. Concretely: on the full Kobak list the *pooled* ratio
in NB is 1.09 (p = 0.48, nothing), while the equal-weight statistic is
+0.379 (p < 10⁻⁵). Same data, same words. The equal-weight version matches
the hypothesis being tested — "LLMs shifted usage across their preferred
vocabulary" — and, critically, it involves **no analyst choices at all**: no
threshold, no subsetting. That matters for the p-hacking objection (§6).

### 2.3 The placebo null — why not a t-test

A textbook significance test would ask "did this rate change more than
sampling noise?" With tens of millions of words, *everything* is significant
by that standard. It is the wrong question.

The right question is: **is this rise unusual for words like these?**
Political vocabulary churns enormously — topics arrive, phrases go in and
out of fashion, a bill dominates a session. So we measure that churn instead
of assuming it:

1. Build **1,000 placebo instruments**. Each is a random word set the same
   size as the real one, where every placebo word is drawn from the **same
   pre-period frequency band** (same log₂ bucket) as its real counterpart.
   Function words, the instrument's own words, short and non-alphabetic
   tokens are excluded.
2. Run the identical statistic on each.
3. Those 1,000 values **are** the null distribution — they embody exactly how
   much matched-rarity vocabulary drifts over these same years in this same
   chamber, for every non-AI reason there is.
4. **p = the fraction of placebos that match or beat the real instrument.**

Two things this buys you. It needs no distributional assumptions. And the
null is *not* centred on zero — placebo sets drift by −0.14 to −0.25
depending on the chamber, which is real background vocabulary churn that a
naive test would have mistaken for signal.

### 2.4 What "p < 0.001" means here

It means zero of 1,000 placebos reached the observed value, so the p-value
is bounded by the resolution of the simulation, not measured. Where we ran
100,000 draws (NB) the bound is p < 10⁻⁵, and there the real value was **4×
the most extreme excursion in 100,000 draws**.

### 2.5 The cross-corpus normalisation (a correction)

**Raw statistics are not comparable between chambers.** Each corpus has its
own placebo baseline, and they differ a lot. Canada makes this unmissable:
its raw primary is **negative** (−0.0138) yet p < 0.001, because its placebo
baseline is −0.231. Canada's AI vocabulary *declined* — but far less than
comparable vocabulary declined.

So the comparable effect size is **excess over the corpus's own placebo
median**. Earlier drafts of this project compared raw values across chambers
and were wrong to. On the corrected metric:

| chamber | raw primary | **excess** | p |
|---|---|---|---|
| New Brunswick *(discovery)* | +0.3791 | **+0.554** | < 0.001 |
| Dáil Éireann | +0.0647 | **+0.224** | < 0.001 |
| Dáil within-speaker | +0.0722 | **+0.244** | < 0.001 |
| Canada Commons | −0.0138 | **+0.218** | < 0.001 |
| Canada within-speaker | +0.0122 | **+0.257** | < 0.001 |
| UK Commons | +0.1155 | **+0.257** | < 0.001 |
| UK within-speaker | +0.0776 | **+0.272** | < 0.001 |

**Fisher's method** combines independent p-values: X² = −2·Σln(pᵢ) on
2k degrees of freedom. Over the three confirmatory chambers:
**X² = 41.4, df = 6, p = 2.4 × 10⁻⁷.** New Brunswick is reported separately
because it is the discovery corpus (§6).

### 2.6 Protocol v1.1 — what the effect looks like with the null repaired

Adversarial review found two defects in v1.0's null, both real, both fixed in
`run_protocol_v11.py`. v1.0 is not withdrawn; both are reported, because the
difference between them is itself the honest measure of how much the
headline depended on the artifacts.

**Fix 1 — present-in-both.** v1.0 scores all 407 words, including words
appearing in *neither* period. Under +0.5 smoothing each such word
contributes a constant positive term, since W_pre ≈ 2·W_post. That is an
artifact of the denominators, not a fact about language.

**Fix 2 — dispersion-matched placebos.** v1.0 matches placebo words to
instrument words on pre-period frequency alone. Corpus linguistics treats
dispersion — how many distinct sittings a word appears in — as co-equal with
frequency (Gries 2008; Egbert & Biber 2019), because a pool of bursty topic
words decays faster between windows, depressing the placebo median and
inflating every excess. v1.1 matches on both axes. **The study already knew
this**: the same filter was written for the formality control (§3.1) after it
returned place names, and was never ported to the placebo pool.

| chamber | pre words | v1.0 excess | **v1.1 excess** | v1.1 p |
|---|---|---|---|---|
| New Brunswick *(discovery)* | 4.2M | +0.554 | **+0.278** | < 0.001 |
| UK Commons | 47.2M | +0.257 | **+0.121** | < 0.001 |
| Dáil Éireann | 36.7M | +0.224 | **+0.080** | 0.002 |
| US House | 22.4M | +0.299 | **+0.104** | < 0.001 |
| Canada Commons | 20.1M | +0.218 | **+0.029** | **0.132 — n.s.** |
| US Senate | 24.4M | +0.151 | **−0.036** | **0.910 — n.s.** |

**Fisher over the five confirmatory chambers: X² = 44.3, df = 10,
p = 2.9 × 10⁻⁶.** The combined result stands. **Two of five chambers do not
reach significance individually.** Effect sizes roughly halve against v1.0.
Any claim of "consistent magnitude across parliaments" is dead; the
defensible range among confirmatory chambers is −0.03 to +0.12.

The US is now the **complete record** for both windows — 1,554 sitting days,
71M words — so both US rows are adequately powered and directly comparable to
the other chambers. (The earlier 330-day sample gave ~3M words per chamber and
inflated excesses, because sampling thins per-word counts and drags the
placebo baseline down; those numbers are superseded.)

**The two nulls are now real nulls, and one of them is the most useful
comparison in the study.** The US House (+0.104, p < 0.001) and the US Senate
(−0.036, p = 0.910) sit in the same country, the same era, the same published
Record, under the same national media environment — and differ completely.
Whatever separates them is institutional, not national. That is a
within-country contrast no cross-country comparison can give, and it is the
sharpest evidence in the study that the effect is not some artifact of
Anglophone parliamentary drift.

The Senate null is not the instrument failing to work there — its style arm
behaves like the others, it simply does not move.

### 2.6b THE NULL DOES NOT CONTROL FOR TREND — read this before quoting any p-value

**Every significance claim in this section is currently unsupported.** The
frequency-and-dispersion-matched placebo has now been run on windows where the
effect *cannot* exist, and it fails.

Take window pairs entirely before ChatGPT and run the identical v1.1 protocol:

| chamber | REAL 2018–22 vs 2024–26 | 2018–19 vs 2021–22 | 2018 vs 2020 | 2019 vs 2021 | estimator check |
|---|---|---|---|---|---|
| UK Commons | +0.120 | **+0.123** | **+0.130** | **+0.165** | +0.011 *(p=0.26)* |
| Dáil Éireann | +0.083 | **+0.112** | **+0.102** | **+0.094** | +0.030 *(p=0.06)* |
| Canada Commons | +0.033 *(n.s.)* | +0.037 | +0.072 | +0.087 | +0.008 *(p=0.36)* |
| New Brunswick | +0.236 | +0.137 | +0.204 | +0.060 | +0.066 *(p=0.01)* |

Pre-LLM windows return excesses **as large as or larger than the real
comparison**, at p < 0.001, in three of four chambers.

**The estimator is not the problem.** Splitting the *same* period into
interleaved halves by alternating sitting date — identical time span, differing
only by sampling — returns ~0 (+0.011, +0.030, +0.008). So the machinery is
near-unbiased and the in-time placebos are detecting a **real secular trend**:
this vocabulary has been rising in parliamentary English since at least 2018.

**Why the null cannot catch it.** A frequency-and-dispersion-matched placebo
controls a word's *level* and its *burstiness*. It does not control *trend* —
matched words do not share the instrument's drift. So "the instrument rose more
than matched words did" is exactly what a already-rising vocabulary produces,
with or without LLMs.

**The diagnosis: we imported Kobak's word list but not Kobak's estimator, and
the estimator was doing the work.** Their design fits each word's own pre-trend
and measures the *break* from it —
`q = p₋₂ + 2·max{p₋₂ − p₋₃, 0}`, floored so it can never predict a decline —
which is a trend control by construction. We replaced it with a two-window
level contrast plus a placebo, and a placebo cannot recover what the
extrapolation was doing.

**What this invalidates:** every lexicon p-value, the Fisher combination, and
the cross-chamber effect-size comparisons. New Brunswick is the only chamber
whose real effect clearly exceeds its own in-time placebos, and it is the
discovery corpus.

**What it leaves untouched:** the prevalence arm (§5 — Pangram verdicts and
specificity calibration involve no time-series contrast), the base-versus-
instruct result (§6.1 — a property of model outputs, not of Hansard over time),
and the detector-side permeation evidence (§5.2a).

**The fix is a rebuild, not a patch**: replace the two-window primary with a
trend-aware counterfactual in the manner of Kobak's extrapolation, and re-run
every chamber. Until that exists, the tables above and in §2.5–2.6 should be
read as descriptive, not inferential.

### 2.6a The per-year series — the pooled ratio was hiding two things

Pooling 2024–2026 into one number assumes the effect is stable inside the post
window. It is not. Each post year scored against the same 2018–22 baseline,
under v1.1, with its own placebo null:

| chamber | 2024 | 2025 | 2026 |
|---|---|---|---|
| New Brunswick | +0.112 | **+0.266** | +0.105 |
| Dáil Éireann | +0.050 | **+0.106** | +0.096 |
| Canada Commons | **−0.019** *(n.s.)* | **+0.068** | **+0.058** |
| UK Commons | +0.102 | **+0.127** | +0.036 *(n.s.)* |
| US House | **+0.159** | +0.034 *(n.s.)* | +0.038 *(n.s.)* |
| US Senate | +0.051 | **−0.062** | −0.054 |

**First: Canada's pooled null was a mixture artifact, exactly as the review
said.** Canada is 49% 2024 by words, and 2024 is its only null year. Scored
per year it is positive and significant in **both 2025 (+0.068) and 2026
(+0.058)**. The pooled Canada figure should not be read as "no effect in
Canada" — it is "no effect in the half of Canada's window that is 2024".

**Second, and more awkward: the series is not a rising ramp.** Four of six
chambers **peak and then decline**, and the US Senate goes negative. A
narrative of steady acceleration — which an earlier progress report asserted —
is not supported.

**The most likely explanation is that the instrument is decaying, not the
behaviour.** Kobak's list was derived from 2024 data, and Geng & Trotta show
individual markers collapsing once they become notorious (*delve* fell sharply
through 2024 while other ChatGPT-favoured words kept rising). If writers and
models both drifted off the 2024 tells, the lexicon signal falls while actual
use does not.

The detector evidence supports that reading, because the two instruments
**diverge in exactly the direction instrument-decay predicts**:

| chamber | lexicon 2025 → 2026 | Pangram AI rate 2025 → 2026 |
|---|---|---|
| UK Commons | +0.127 → **+0.036** | 1.0% → **1.6%** |
| Dáil Éireann | +0.106 → +0.096 | 3.3% → 4.4% |
| Canada Commons | +0.068 → +0.058 | 13.8% → 13.7% |
| New Brunswick | +0.266 → +0.105 | 4.3% → **13.6%** |

New Brunswick is the clearest case: its lexicon excess more than halves while
its measured prevalence **triples**. A word list frozen in 2024 cannot be
assumed to track behaviour in 2026, and any claim about the *trajectory* of AI
use should rest on the calibrated detector, not on the lexicon. The lexicon's
job is establishing that a shift happened at all, against a defensible null —
not measuring how fast it is growing.

### 2.7 Does the lexicon predict an independent detector?

The obvious challenge to any word-list instrument is that it might be
measuring nothing in particular. The test that bears on this is not whether
some other word list moved — it is whether **lexicon density predicts what a
calibrated detector says, segment by segment**.

Two detectors are available and neither has any connection to Kobak's list:
Pangram (calibrated in-domain, 423/423 specificity, but expensive so only ~120
unbiased segments) and the Opus screen (AUC 0.951 against Pangram, run over
all 37,801 NB segments).

**The list is specific.** Per-segment density predicts the Opus score at
ρ = +0.252, while **frequency-and-dispersion-matched random word sets predict
essentially nothing**:

| era | Kobak list | matched random sets | placebos beating Kobak |
|---|---|---|---|
| 2025–26 (n = 7,218) | **+0.252** | +0.024 *(−0.072 to +0.116)* | 0 of 30 |
| pre-2023 (n = 20,329) | **+0.250** | +0.004 *(−0.103 to +0.121)* | 0 of 30 |

So this is not "passages with more mid-frequency abstract words look AI-ish to
everything." The list carries particular information an independent detector
recognises. Pangram agrees: within the unbiased random stratum, density
separates its verdicts at AUC 0.680 (p = 0.031), matching the Opus figure of
0.691 on 60× the data.

**But the association is the same size before AI existed**, and that is the
important qualification. What the two instruments agree about is a
**register** — a recognisable way of writing that predates these tools and
that LLMs amplified rather than invented. Their agreement validates Kobak's
list as an instrument *for that register*; it does **not** establish that
either detects AI at the segment level. Per-segment claims of the form "this
speech is machine-drafted because it is lexicon-dense" are not supported.

**The levels are what carry the signal, and they move very differently:**

| | pre-2023 | 2025–26 | change |
|---|---|---|---|
| lexicon density (per 1,000 words) | 32.13 | 35.98 | +12% |
| Opus AI score | 8.18 | 18.03 | **+120%** |

**And the detector's rise is not the lexicon's rise.** Matching segments on
*absolute* density in 2.0-wide calipers — so the two eras agree on mean density
to two decimal places within each bin — the score shift persists at every
level, +5.3 at the lowest to +17.3 at the highest:

| | pre-2023 | 2025–26 | shift |
|---|---|---|---|
| density-matched weighted mean score | 8.68 | 18.86 | **+10.18** |
| unmatched overall | 8.18 | 18.03 | +9.85 |

Conditioning on density **does not shrink the gap; it slightly widens it.** If
the two instruments were measuring one thing, matching on density would absorb
the detector's rise. It absorbs none of it, so the lexicon's +12% explains
essentially none of the detector's +120%.

(An earlier version of this test binned by density *decile*. That is not an
adequate control: the density distribution shifted right, so within any decile
the post-period segments sit higher in the bin than the pre-period ones, and
part of the apparent shift is residual density. Absolute-density calipers fix
it, and the result survives.)

Three things follow. The **lexicon understates the change** (12% against
120%), so its effect sizes are conservative. The two arms measure **different
quantities** — register shift versus drafting prevalence — and should be
reported separately rather than treated as cross-validating. And the detector
sees structural change the 407 words miss, which is why the prevalence arm
is not redundant with the lexicon arm.

*Caveat: the Opus screen's threshold is well calibrated (0.0% flag rate across
20,329 pre-2023 segments, Pangram-confirmed 243/243 human), but its continuous
score is not anchored the same way, and Opus was trained on data that includes
AI-influenced recent text. The decile shifts are large enough that this is
unlikely to explain them, but it cannot be ruled out here.*

---

## 3. Controls — what each one kills

A result is only as good as the alternative explanations it excludes.

| control | the alternative it kills | result |
|---|---|---|
| **Pre-2023 window** | "detectors/lexicons just flag formal oratory" | every chamber's own pre-AI baseline |
| **Placebo null** | "all vocabulary drifts like this" | every placebo draw negative, instrument positive, in all four chambers |
| **Formal-register control** | "this is just pomposity inflation" | NB 0.808, Ireland 0.990, Canada 0.987, UK 0.998 |
| **Data-defined formality axis** | "you hand-picked a control that passes" | instrument leads it everywhere (§3.1) |
| **Within-speaker restriction** | "the chamber's membership changed" | survives in all three chambers that held elections |
| **Absent-word check** | "smoothing manufactures the gap" | present-only restriction *widens* NB/UK gap |
| **Translation exclusion** | "you're measuring translators" | NB columns, Canada FloorLanguage, Ireland language-ID |
| **Speech-clustered bootstrap** | "a few speeches drive it" | resample whole turns, not words |

### 3.0 One assumption worth stating, because we measure its violation

Most causal designs assume **no interference** (SUTVA): one unit's treatment
does not affect another unit's outcome. Here that would mean AI-assisted
writing does not change how *non-AI* text is written. **We know it does** —
that is the permeation result in §5.2, and it is the study's most interesting
finding rather than a nuisance.

The consequence is worth writing down because it runs in our favour. The
placebo pool has no semantic exclusion, and the formality control is built to
be maximally register-similar — so both are partly *treated*. Contaminated
controls make the comparison too conservative, biasing every reported effect
**toward the null**. Whatever the true shift is, the numbers here are a floor,
not a ceiling.

### 3.1 The data-defined formality control (worth understanding)

The hand-picked register list invites the objection "you chose words you
knew would behave". So we built one from data instead:

```
formality score(w) = log[ rate(w | long pre-period speeches ≥300w)
                        ÷ rate(w | short interventions ≤120w) ]
```

Long speeches are overwhelmingly prepared, short interventions
overwhelmingly spontaneous, so words scoring high mark the prepared
register. Take the top scorers, frequency-match them bucket-for-bucket to
the instrument, require zero overlap with it, and use **pre-period data
only** so nothing about the outcome leaks in.

**The first attempt failed, instructively.** It returned *hessle, mcdonagh,
broxbourne, smokers, circuses* — place names and bill topics. Long speeches
differ from short ones by *topic*, not just register. Two filters fixed it:
a dispersion floor (a word must appear in at least as many sittings as the
median instrument word) and a proper-noun filter (excluded if capitalised
mid-sentence >25% of the time). The axis then returns real register
vocabulary: *amends, movingly, poignant, deficiencies, discourse,
practicable*.

**A third filter was needed and the review found it (F7).** The candidate
floor was a pre-period count of 200, which sits above log2 bucket 7 — but 227
of the instrument's 407 words live in buckets 0–3, so those quotas could never
fill. The realised control was 67 words in New Brunswick against the
instrument's 407, and was therefore systematically **more common** than the
thing it controls — reintroducing the exact flaw it exists to remove. Lowering
the floor to 20 and borrowing from neighbouring buckets when one still cannot
fill:

| chamber | control words filled | instrument − control |
|---|---|---|
| New Brunswick | 407 / 407 | **+0.392** |
| UK Commons | 362 / 407 | **+0.092** |
| Dáil Éireann | 371 / 407 | **+0.077** |
| Canada Commons | 381 / 407 | **+0.074** |

The instrument leads the control in every chamber, as before, and the gaps
barely move — so the earlier numbers were not *wrong*, they were
under-evidenced. What changed is that the control is now actually matched.

One honest weakness remains. The control vocabulary looks like register in the
three large chambers (*whilst, amends, movingly, poignant*; *consisting,
pleaded, nowadays*; *thereafter, ramifications, illustrate*) but topical in
New Brunswick (*drainage, plantations, asphalt*). NB has only 169 pre-period
sittings, so its dispersion filter is coarse — the fix that worked at scale
degrades on the shallowest corpus, which is another reason NB is quoted as the
discovery corpus rather than as evidence.

---

## 4. Detectors — three tiers, and why the first two failed

### 4.1 Statistical / zero-shot (all failed)

Eight instruments: three **Binoculars** pairs (Falcon-7B, Qwen3-1.7B,
Qwen3-8B), **Fast-DetectGPT**, **log-rank ratio**, and three supervised
classifiers (HC3-RoBERTa, RADAR, the GPT-2-era OpenAI detector). Each
calibrated on the 2019 control so its threshold means the same thing.

Binoculars scores the ratio of a text's perplexity under one model to its
cross-perplexity under a closely related model — machine text is
"unsurprising to a machine" in a specific way. It is a good method. It found
nothing: **2025–26 flag rates sat *below* the pre-ChatGPT false-positive
floor** (2.85% vs 5.64%). Fast-DetectGPT and the classifiers agreed.

**That null is about the detectors, not the text, and real data shows it.**
The obvious worry is that "eight detectors found nothing" might just mean
zero-shot detectors do not work on transcribed parliamentary speech. It does
not, because *other* instruments find plenty in the very same corpus: Pangram
individually confirmed **576 of 643** tail segments as AI or Mixed (89.6%),
and a frontier LLM screen separates its verdicts at AUC 0.951 while open-weight
models manage 0.55–0.72 (§4.2).

So the same segments that eight statistical detectors rate unremarkable are
adjudicated AI by a calibrated commercial classifier and recovered by a
frontier model. The null is a property of the *method* — perplexity-based
detection — not evidence that the record is clean. That is the scissors: the
vocabulary channel and the commercial/frontier detectors both move, while
token-level statistics do not.

*This argument previously rested on measuring sensitivity against 40 synthetic
speeches generated by Mistral-7B-Instruct. That corpus has been removed from
the study entirely: it was a single 7B open-weight model nobody's office uses,
too small to carry variance (39 of its 89 usable words occurred exactly once),
and it is not needed — the case above is made on real adjudicated text rather
than on our guess at what machine legislative speech looks like.*

### 4.2 Prompt-based detection, and the capability finding

Same blinded pool, same question, six configurations:

| detector | AUC vs Pangram |
|---|---|
| Claude Opus 5 (low effort) | **0.951** |
| Claude Fable 5 (high effort) | 0.936 |
| Qwen3-32B (thinking) | 0.721 |
| gpt-oss-120b (high reasoning) | 0.672 |
| gpt-oss-120b (low reasoning) | 0.657 |
| Qwen3-32B (no thinking) | 0.549 |

Reasoning effort helps the open models somewhat but never closes a ~0.25 AUC
gap. **Detecting edited AI in this register is frontier-capability-bound** —
which retro-explains why the statistical detectors failed, and is itself a
finding.

### 4.3 Calibration — the part that makes a percentage meaningful

A detector's output is worthless without knowing its error rates. Two
parameters:

- **Specificity (Sp)** = P(not flagged | actually human). **Measured here**,
  in-domain, on pre-2023 segments that predate the tools.
- **Sensitivity (Se)** = P(flagged | actually AI). **Taken from the published
  literature**, because no study — including this one — can measure it for
  the text that matters.

**Specificity: 423 pre-LLM segments, zero false positives.** New Brunswick
243/243, then 60/60 independently in each of Ireland, Canada and the UK. The
NB figure includes the three pre-2023 segments an LLM screen rated *most*
AI-like, all of which came back Human — a specificity test chosen
adversarially rather than at random. This is the half of the calibration that
had to be done in-domain, because a detector's false-positive rate on formal
parliamentary oratory is exactly what no vendor benchmark covers.

**Sensitivity: cite, don't generate.** Pangram's catch rate on machine text
is far better established publicly than anything 40 speeches of ours could
show: 99.3% on the RAID benchmark across domains (Dugan et al., COLING shared
task); never below 99.8% in independent testing at Chicago Booth; the only
one of four tools to detect reliably in a peer-reviewed Vrije Universiteit
Brussel evaluation; 1.4% false-negative rate self-reported in the Pangram
technical report (Emi & Spero, arXiv:2402.14873). Pangram also trains against
19 humanizer tools as augmentation, which bounds how badly light editing
should hurt.

*An earlier version estimated Se from 40 synthetic speeches generated by
Mistral-7B-Instruct (Se = 40/40). **That corpus has been removed from the
study.** It was weaker evidence than the published evaluations it duplicated,
and it rested on a single 7B open-weight model nobody's office uses — the
wrong generator for asking what share of real speech is machine-drafted.
Nothing now depends on it.*

**What nobody has measured, and why it cannot be fixed by generating more
text.** Every published figure above is for machine text as emitted, or
perturbed by automated humanizers. The class this study argues actually
dominates Hansard is different: drafted by an aide with a model, revised by
the member, then normalised by a professional Hansard editor. To measure Se
on *that*, you would have to generate it — which means deciding what a
member's edit looks like. That is an unvalidatable modelling assumption, and
it would yield a confident-looking sensitivity figure resting entirely on a
guess. Reporting the floor honestly is better than manufacturing an interval.

**Rogan–Gladen correction.** An imperfect test's observed flag rate π relates
to true prevalence τ by

```
    π  =  τ·Se  +  (1 − τ)(1 − Sp)          so      τ̂ = (π̂ + Sp − 1)/(Se + Sp − 1)
          ↑ caught      ↑ falsely flagged
```

Because **Sp = 1 is measured**, the false-positive term vanishes and this
collapses to

```
    τ̂  =  π̂ / Se           and since Se ≤ 1 always,   τ̂ ≥ π̂
```

So the correction contributes no number — it tells us the *shape* of the
remaining uncertainty. It is **one-sided and upward**, with 1/Se as the
unknown multiplier. Every observed rate in §5 is therefore a floor, and the
only thing that could move it is evidence about sensitivity on edited
in-register text, which does not exist.

The denominator (Se + Sp − 1) is how much better than chance the test is; as
it approaches zero the estimate explodes, which is why a mediocre detector
cannot produce a prevalence figure at any sample size. Ours is dominated by
the measured Sp = 1, which is the part that makes the floor meaningful.

### 4.4 Two-phase sampling (why the design is affordable)

Adjudicating a whole corpus with a paid detector is unaffordable. Two-phase
sampling solves it: a cheap instrument scores everything and defines strata,
then the expensive instrument is spent only where it is informative. **The
cheap instrument does not need to be accurate — only correlated with truth —
because stratum weights are known exactly from the full corpus.**

In practice a lean Claude Opus screen (low effort, detection-only prompt)
scored all 37,801 NB segments for ~17M tokens, at AUC 0.951 against Pangram.
Its precision is monotone in score — 100% at 90+, 83% at 50–59 — which is
what a well-behaved stratifier looks like.

---

## 5. The prevalence numbers

- **Design-based random sample**: 120 segments drawn 12-per-decile of the
  **Falcon/Binoculars** score. Result **9 AI + 1 Mixed of 120**: **7.5% AI**
  [4.0–13.6], **8.3% AI-or-Mixed** [4.6–14.6]. Report which of the two you
  mean — Pangram returns three verdicts, not two, and the AI-only and
  AI-or-Mixed rates diverge sharply in other chambers (Canada: 17.5% vs
  26.7%).

  **Two corrections a reviewer would otherwise make first (review F4).**

  *The reference population is five sitting months, not the corpus.* The
  sampling frame is 3,998 segments — 585 from 2019 plus Oct/Nov/Dec 2025 and
  Mar/May 2026 — which is **10.6% of the 37,801-segment corpus**, omits all of
  2024 and January–September 2025, and sits on the steepest part of the ramp.
  So the defensible statement is **"7.5% of New Brunswick segments in sittings
  from October 2025 to May 2026"**, not a corpus rate. The other three
  chambers use a different window again (2025-01-01 onward), which is why
  §5.0b's table is labelled 2025–26.

  *The stratifier was uninformative.* The deciles are of the Falcon score —
  the Binoculars detector §4.1 reports as having found nothing — not of the
  Opus screen. Realised AI counts by decile were 0,1,1,1,1,0,1,1,1,2: flat.
  The design therefore **degenerated to an effective simple random sample**.
  That is harmless for the point estimate under equal allocation across
  equal-sized deciles, but it must be stated, and §4.4's "precision is monotone
  in score" describes the *Opus* screen on a different pool.
- **By year**: 0% (2019–22, n=240) → 4.0% (2023) → 4.0% (2024) → 4.3% (2025)
  → **13.6% (2026)**.
- **Full tail adjudication**: all 643 segments scoring ≥50 submitted
  individually → **461 AI, 115 Mixed, 67 Human (89.6% confirmed)**.
- **Corpus-wide screen**: pre-2023 flag rate **0.0%** across 20,329
  segments; 0.5% (2023) → 1.2% (2024) → 7.0% (2025) → 11.0% (2026).

**Two numbers that must not be conflated.** 576 confirmed segments over
37,801 is a **1.5% audited floor** — it only counts what was individually
verified. 7.5% is the **estimated prevalence** from random sampling. They
measure different things.

**And 7.5% is a floor, not a point estimate (review F5).** Since Sp = 1 is
measured, τ̂ = π̂/Se (§4.3), so the only thing standing between the observed
rate and the true one is sensitivity on the text that actually dominates:
**edited** AI, in parliamentary register. Nobody has measured that — not this
study, not any published evaluation. What it would do to the number:

| Se on edited in-register AI | implied prevalence |
|---|---|
| 1.00 | 7.5% |
| 0.75 | 10.0% |
| 0.50 | 15.0% |
| 0.30 | 25.0% |

Two things bound how pessimistic to be. Against us: Dugan et al. (RAID) show
detector performance collapsing under light edits across eight detectors, and
Liang et al.'s proofreading arm found lightly-edited text yields only a
slight, non-significant rise in their estimator — both say editing hurts. For
us: those results are for detectors that do **not** train on humanized text,
whereas Pangram trains against 19 humanizer tools as augmentation, so the
most pessimistic rows are probably too pessimistic.

**This gap is not closeable by more work, which is why we stopped.** Measuring
Se on edited in-register AI means generating it, which means deciding what a
member's edit looks like — an assumption nothing can validate. The result
would be a precise-looking interval resting on a guess. The defensible
statement is the one-sided one: **at least 7.5% of New Brunswick segments in
sittings from October 2025 to May 2026, with 1/Se as a stated unknown
multiplier**, and every correction running toward more AI, never less.

### 5.0a Segment length is a confound, and it bit us

The three confirmatory chambers were first sampled with a **120-word floor**
(so that Pangram had enough text to work with). That floor is not innocent:
AI-flag rate rises steeply with segment length. In Canada, 11.1% of
120–199-word segments were flagged versus 22.6% of 280–360-word ones, and
the excluded 50–119-word band came back at **2.5%** against the long band's
17.5%. Since that band is **45.8% of Canadian segments**, the unweighted
long-band figure overstates the corpus rate by roughly 1.7×.

The fix is to measure the excluded band rather than extrapolate, then
combine with weights taken from the **full corpus** (not the sample), which
is what makes the result design-based:

| chamber | long band | short band | **segment-weighted** | **word-weighted** |
|---|---|---|---|---|
| Canada | 17.5% | 2.5% | **10.6% ± 4.3** | **14.0% ± 5.3** |

Two weightings because they answer different questions: segment-weighted is
"what share of *turns* is AI-flagged", word-weighted is "what share of the
*record* is". Quote the second only if the claim is about text volume.

New Brunswick needed no such correction — its sample was 16% short segments
against 13.9% in its pool, so it was already representative. **This is why
NB (7.5%) and Canada (10.6%) are statistically indistinguishable, and why
the uncorrected comparison — 7.5% vs 17.5% — would have been an artifact of
the sampling frame rather than a fact about Canada.**

### 5.0b Four chambers, corrected — and they genuinely differ

The three confirmatory chambers were sampled **uniformly at random** from
their post-window pools, with no screen stratification, so unlike the NB
pilot they need no weighting assumptions at all. Every one carries its own
specificity control drawn the same way from pre-2023.

| chamber | seats | specificity | long band | short band | **AI, corrected** | AI+Mixed |
|---|---|---|---|---|---|---|
| UK Commons | 650 | 60/60 | 1.7% | 0/40 | **0.8% ± 1.0** | 2.3% ± 1.8 |
| Dáil Éireann | 160 | 60/60 | 5.0% | 0/40 | **4.3% ± 3.3** | 9.9% ± 4.9 |
| New Brunswick | 49 | 243/243 | 8.9% | 0/19 | **7.5%** [4.0–13.6] | 8.3% [4.6–14.6] |
| Canada Commons | 338 | 60/60 | 17.5% | 2.5% | **10.6% ± 4.3** | 15.6% ± 4.8 |

Two things to take from this.

**Specificity replicates.** 423 pre-2023 segments across four parliaments,
zero false positives. The NB pilot's perfect specificity was not a fluke of
one corpus, which is what pins down the specificity half of the Rogan–Gladen
correction
rather than a fudge.

**The chambers really do differ.** A homogeneity test on the long band, the
one stratum sampled identically everywhere, gives **X² = 22.2, df = 3,
p = 6.0 × 10⁻⁵** — a tenfold spread from UK 1.7% to Canada 17.5% that
sampling noise does not explain.

**And prevalence does not rank chambers the way the lexicon does.** The UK
has among the largest lexicon excesses (+0.257) and the *lowest* measured
prevalence; New Brunswick has by far the largest excess (+0.554) and a
middling prevalence. So the two instruments are not two measurements of one
quantity, and the paper must not treat them as interchangeable. Three
candidate explanations, none yet tested:

1. **Editorial policy.** UK Hansard is the most heavily edited of the four —
   it reports substantially what was said, with repetition and error removed.
   Heavy editing is exactly what destroys detector signal while leaving word
   choice intact. This is the scissors (§5.1) operating at chamber level, and
   it predicts the UK's specific pattern.
2. **Register composition.** The UK has the most short-intervention-heavy
   record of the four (56,380 short vs 46,715 long segments), and short
   segments are both harder to detect and less often drafted.
3. **Genuine behavioural difference** in how members prepare.

Distinguishing these needs an editing-intensity measure the study does not
yet have. Until then the honest statement is that the **lexicon measures
register drift, including ambient permeation into human writing (§5.2),
while the detector measures drafting** — and that they diverge.

### 5.1 The scissors, and what it implies

Vocabulary rises while token statistics do not. That combination is the
signature of **edited or assimilated** AI: editing destroys the token-level
fingerprint but not the word choice. It also explains why a study designed
around detector flag rates alone would have concluded, wrongly, that nothing
was happening.

### 5.2 Permeation into human-written text

If AI register is spreading into prose people write themselves, the rise
should appear even in text a calibrated detector calls human. Testing on
segments the screen rates *least* AI-like (score <20, identical selection
rule both eras):

| era | words | Wikipedia-signs/100k | rare-Kobak/100k [95% CI] |
|---|---|---|---|
| pre-2023 | 4.08M | 11.4 | 213.7 [209.3, 218.2] |
| 2025–26 | 1.06M | 16.1 | **264.8 [255.1, 274.7]** |

Non-overlapping intervals, 1.24–1.41× higher. **Part of the corpus-level
rise is ambient** — the machine register colonising human writing — not only
direct drafting.

That test used a screen score as a human proxy, which is vulnerable to an
obvious objection: if members run drafts through a humanizer, "the detector
says human" means the detector lost, not that a person wrote it. The
permeation case therefore cannot rest on any detector, and the two tests
below are built so that it doesn't.

#### 5.2a Dose-response by speech format — the strongest evidence

Drafting and permeation make opposite predictions about *where* the shift
should sit. Drafting enters where drafting is easy and worthwhile: long
prepared statements. Permeation enters wherever people produce language,
including short spontaneous interventions nobody drafts with a model.

Segments split at 120 words, the frozen protocol run on each band
separately, and the same blinded Opus screen (n = 400 per cell) run on both:

| chamber | lexicon excess, **short** | lexicon excess, long | detected AI, short | detected AI, long |
|---|---|---|---|---|
| Dáil Éireann | **+0.378** | +0.214 | 0.0% | 0.2% |
| Canada Commons | **+0.312** | +0.221 | 0.2% | 2.8% |
| UK Commons | **+0.299** | +0.267 | 0.0% | 0.8% |

**The two columns run in opposite directions in all three chambers.**
Detected drafting concentrates in the long band; the vocabulary shift
concentrates in the short band. If drafting caused the vocabulary shift these
would track each other.

Two things make this hold up. First, the obvious objection — that the screen
just scores short text lower — is settled by the pre-2023 cells: **0 flags in
2400 pre-LLM segments**, so there is no baseline short/long gap to subtract.
Second, the argument needs only the detector's *ordering* across bands, not
its absolute accuracy, so a humanizer that defeats detection does not rescue
the drafting story unless it is being applied to seventy-word Question Period
supplementaries.

The screen also sees the permeation directly, below its own flag threshold:
mean score rises significantly pre→post in **every** short-band cell —
Ireland +1.18 [0.65, 1.75], Canada +0.95 [0.42, 1.54], UK +2.31 [1.84, 2.80]
— while almost nothing crosses the threshold. Text reading slightly more
machine-like without being machine-written is exactly what permeation looks
like.

#### 5.2b Speaker distribution — is it everyone, or a few adopters?

Adoption by a subset predicts most members unchanged with a right tail.
Permeation predicts the whole distribution translating. Per-member shift,
each against that member's own frequency-matched placebo, using the
equal-weight statistic that carries the corpus effect:

| chamber | median member | members shifting positive | top decile's share |
|---|---|---|---|
| Dáil Éireann | +0.089 | 78% | 32% |
| UK Commons | +0.071 | 69% | 33% |
| Canada Commons | +0.008 | 53% | 47% |

**A statistic-choice warning.** Measured as a *pooled* per-speaker rate this
reverses — Canada 22% positive, UK 49% — because pooling is
frequency-dominated while the effect lives in rare words. Same data, opposite
conclusion. Use equal-weight.

Deleting the most-shifted members and re-running the frozen protocol:

| corpus | baseline | −top 10% | −top 25% | −top 50% |
|---|---|---|---|---|
| Dáil Éireann | +0.246 | +0.199 | +0.166 | **+0.130** |
| Canada Commons | +0.252 | +0.155 | +0.158 | **+0.147** |

About **half** the effect is carried by the top movers and about half
survives deleting them, still at p < 0.001 with half the chamber gone. So
neither story is complete: there is real concentrated adoption *and* a
broad-based floor.

**That test is biased and the bias mattered.** Speakers were ranked by the
same quantity then measured in the remainder — selection on the outcome, which
lowers the trimmed mean even under pure permeation. The clean version ranks
members on odd-numbered sittings and measures on even ones, so ranking and
measurement use independent data:

| corpus (measured on fold B) | baseline | −top 10% | −top 25% | −top 50% |
|---|---|---|---|---|
| Canada Commons | +0.351 | +0.357 | +0.314 | **+0.325** |
| UK Commons | +0.317 | +0.278 | +0.236 | **+0.194** |
| Dáil Éireann | +0.277 | +0.233 | +0.201 | **+0.165** |

All three survive deleting half the membership, at p < 0.001. Canada is
**essentially unchanged** (7% reduction, against 42% in the biased version —
so that 42% was almost entirely the artifact). Ireland and the UK fall about
40% but remain strongly positive. **No minority of adopters can account for
the effect in any chamber.**

#### 5.2c Unscripted business — and the result that cuts the other way

Length is only a proxy for spontaneity. Parliamentary procedure gives the real
thing: business where the words cannot have been drafted, because nobody knew
what was coming. Canada's oral questions are not submitted in advance at all;
UK Topical Questions are not tabled and PMQs supplementaries are a surprise;
Ireland's Leaders' Questions and Questions on Promised Legislation are raised
without notice.

| chamber | unscripted | prepared | ratio |
|---|---|---|---|
| Dáil Éireann | **+0.362** | +0.220 | 1.65× |
| UK Commons | **+0.289** | +0.261 | 1.10× |
| Canada Commons | +0.287 | **+0.405** | **0.71×** |

**Canada reverses it, and Canada is the sharpest test.** For the UK and
Ireland the "prepared" pole is just *everything else* — a diluted mixture. In
Canada both poles are clean categories: Oral Questions against **Statements by
Members**, the 60-second set-pieces that are the most scripted text in the
chamber. There, the shift is largest exactly where drafting is easiest.

Ordering the Canadian strata by how scriptable they are makes the point:

| Canadian stratum | excess |
|---|---|
| Statements by Members (fully scripted) | **+0.405** |
| all short segments | +0.312 |
| Oral Questions (unscripted) | +0.287 |
| all long segments | +0.221 |

The purer the prepared category, the larger the shift — the long-band average
is low only because ordinary debate dilutes it. The earlier length-band
reading of Canada was an artifact of that dilution.

#### 5.2d What the permeation arm actually supports

Both mechanisms are real, and their relative weight differs by chamber in a
way that **tracks measured AI prevalence**:

| chamber | AI prevalence | unscripted/prepared | reading |
|---|---|---|---|
| UK Commons | 0.8% | 1.10× | mostly permeation |
| Dáil Éireann | 4.3% | 1.65× | mostly permeation |
| Canada Commons | 10.6% | 0.71× | drafting visible on top of it |

That coherence is itself evidence the two instruments are measuring what we
think. But the honest headline is **not** "the shift is permeation". It is:

1. **A broad-based floor exists everywhere.** It survives deleting half of
   each chamber's members under an unbiased split-half design, and it appears
   in speech that could not have been drafted. Something is changing in how
   people write and speak who are not using these tools on that text.
2. **Direct drafting sits on top of it, and is chamber-specific.** Where
   prevalence is highest, the shift concentrates in scripted formats.

Claim 1 is the mass-behaviour-change result and it is supported. Claim 2 is
not a threat to it — they are separable, and separating them is what these
tests do.

#### 5.2d-bis In-context permeation — the phrasing, not just the words (Matthew's design)

Frequency counting shows members using more of the register vocabulary. A
sharper question is whether, when they use those words, the *surrounding
phrasing* has become the assistant's phrasing — collocations and frames, not
lexicon. Measured as the per-token log-likelihood advantage of an instruct
checkpoint over its own base checkpoint, **at instrument-word positions
only**, self-normalised by each segment's full-trace delta (no placebo word
list — that construction has failed three times in this study and is not
used here).

Pre → post change in that quantity, two model families, five chambers:

| family | ie | ca | uk | ush | uss | pooled |
|---|---|---|---|---|---|---|
| Qwen3-8B | +0.017 | +0.016 | +0.011 | +0.013 | +0.002 | +0.0118 |
| Mistral-7B | +0.005 | +0.008 | +0.017 | −0.006 | +0.016 | +0.0081 |

**Two-family pooled: +0.0099, 95% CI [+0.0007, +0.0196], P(≤0) = 0.020;
9 of 10 family-chamber cells positive** (clustered bootstrap over speeches).

This is the first *contextual* permeation evidence: the phrasing around the
register words has drifted measurably toward the assistant's, in text
selected identically in both eras. It is detector-free (the humanizer
objection does not apply) and word-selection-free (self-normalised). The
magnitude is small — about a hundredth of a nat per token — and the corpus-
wide version of the same quantity is a triple-replicated null, so the drift
is confined to the neighbourhoods of the register vocabulary, which is
exactly where a diffusion-of-phrasing account puts it.

#### 5.2e Shift of the centre, or collapse toward it?

Everything above is a **mean**. A mean can move two ways with opposite
implications: everyone moves together and the distribution *translates*, or
members converge on a common register and the distribution *narrows*. The
second is the monoculture claim — individual voices becoming interchangeable
— and it is a statement about second moments, not means.

Every member is subsampled to **exactly 10,000 tokens in both eras**, and only
members present in both are used. Without that, the smaller post window would
manufacture convergence by itself, since every diversity and distance measure
is biased by sample size.

| measure | Ireland | Canada | UK |
|---|---|---|---|
| instrument rate (the mean) | +90 | −271 | −44 |
| **between-speaker SD** | **+42** | **+89** | −5 *(n.s.)* |
| **Burrows Delta between members** | **+0.079** | **+0.079** | **+0.042** |
| Shannon entropy | +0.026 | **−0.071** | +0.029 |
| distinct types | −288 (−1.2%) | **−1710 (−6.9%)** | −467 (−1.4%) |
| top-100 token share | −0.005 | **+0.005** | −0.004 |

All significant at 95% except the UK's between-speaker SD.

**On the measure that directly tests the question, it is a shift of the
centre, not a collapse.** Burrows Delta — the standard authorship-distance
statistic, z-scored profiles over the 200 most frequent words — **rises in all
three chambers**. Members became *more* distinguishable from one another, not
less. Between-speaker dispersion of the instrument rate also rises in two
chambers and is flat in the third. Nothing is converging on a common level of
use.

Delta is a *pairwise* distance, so a shift affecting everyone equally cancels
out of it exactly. A rise therefore means genuine added heterogeneity, and it
cannot be an artifact of the common drift the rest of this study measures.

**But one thing does narrow, everywhere: the size of the working vocabulary.**
Distinct types fall in all three chambers at fixed token count, and in Canada
the corpus also concentrates outright — entropy down, top-100 share up. So the
picture is:

- **individual distinctiveness: rising** — no collapse of voice
- **collective lexicon: shrinking** — fewer distinct words in use

Canada shows both at once, which is not a contradiction: Delta is computed on
function-word-dominated profiles and is topic-robust, so its members can
diverge stylistically while their shared topic vocabulary narrows.

**The honest caveat.** Type-count narrowing has an obvious non-AI explanation,
and Canada — where it is largest by five-fold — is precisely the chamber with
documented massive topic churn (bail 17.9×, corruption 6.2×, auditor 4.7×).
A narrower political agenda produces a narrower lexicon with no machine
involved. Attributing the vocabulary contraction to AI is not yet supported;
attributing the *absence of stylistic collapse* to the data is.

**And a limit on what a two-window design can see.** Early adoption should
*add* variance — some members pick it up, others don't — so widening is what
the early phase of a convergence process looks like from the outside. Collapse
would be a late signature, after everyone has converged on the same tool. This
does not refute the monoculture prediction; it dates it. Between-speaker Delta
is the series to track over time, and a single pre/post contrast cannot
substitute for that.

---

## 6. The p-hacking question, handled explicitly

Three defences, in increasing order of strength:

1. **The instrument is external and predates the study.**
2. **The primary statistic involves no choices** — no threshold, no
   subsetting, all 407 words, equal weight.

   An earlier version of this defence claimed a rare-word threshold sweep
   "shows every cutoff from <1 to <50 per 100k gives p ≤ 0.008". That was
   New Brunswick only, unlabelled, and misquoted (NB's <1 cell is 0.015).
   **The frequency-weighted secondary does not replicate**, and the full table
   is now reported rather than one chamber's:

   | chamber | <1 | <2 | <5 | <10 | <20 | <50 |
   |---|---|---|---|---|---|---|
   | New Brunswick *(discovery)* | 0.015 | 0.008 | 0.000 | 0.001 | 0.000 | 0.000 |
   | US House | 0.020 | 0.023 | 0.020 | 0.062 | 0.213 | 0.603 |
   | Dáil Éireann | 0.207 | 0.146 | 0.083 | **0.047** | 0.069 | 0.136 |
   | UK Commons | 0.143 | 0.184 | 0.148 | 0.240 | 0.130 | 0.111 |
   | Canada Commons | 0.137 | 0.332 | 0.195 | 0.274 | 0.489 | 0.916 |
   | US Senate | 0.472 | 0.945 | 0.984 | 0.964 | 0.986 | 0.992 |

   **4 of 30 confirmatory cells reach p < 0.05.** The pooled statistic is
   frequency-weighted, so a handful of common words dominate it — §2.2 shows
   it is null even in NB on the full list (ratio 1.09, p = 0.48) while the
   equal-weight statistic is +0.379. The choice of equal weighting is defended
   on the merits and follows Gray's published design; what is *not* defensible
   is letting a reader assume the two statistics agree. They do not.
3. ~~**A mechanism prediction test.**~~ **REMOVED, along with the corpus it
   depended on.** It claimed that word-level AI-preference — measured from 40
   synthetic speeches and the 2019 control — predicts which individual words
   rose (Spearman +0.548, p < 10⁻⁴). Two things killed it, and the second
   subsumes the first.

   *The statistic was a rarity index.* The 2019 control is a subset of the
   2018–22 pre-window, so each word's Hansard rarity sat inside both the
   predictor and the outcome with the same sign. It correlates **+0.923** with
   −log(2019 count) and **−0.234** with the synthetic evidence it was meant to
   encode; the partial correlation controlling pre-period frequency is
   **−0.008**; and permuting within frequency quintiles rather than globally
   gives **p = 0.24**. Rarity alone, using no AI data at all, scores **+0.568**
   — better than the published predictor.

   *The synthetic corpus is gone.* Its 6,838 words were too few to carry
   variance (39 of the 89 usable words occurred exactly once), and it came
   from a single 7B open-weight model that does not represent what anyone
   actually drafts with. Nothing in the study now depends on it.

   So this is not a defence with a correction pending — the analysis has been
   deleted. What is retained is its *design lesson*: an unpaired comparison of
   model output against a human corpus inherits that corpus's word-frequency
   structure on both sides. The replacement (§6.1) is paired by construction —
   instruct against its **own base checkpoint** on identical prompts — which
   cancels baseline frequency exactly, as in Geng & Trotta and Yakura et al.
   Defences 1 and 2 carry §6 in the meantime.


### 5.4 Where the register comes from — onset, cohort, and arrival

The lexicon arm failed as an *AI* instrument (§2.6b) but the series it
measures is real and turns out to have structure worth reporting in its own
right. Three findings, from a 16-chamber panel built for this purpose:
eight Canadian provinces, six Australian states, and the three UK devolved
legislatures, each from its own archive with its own extractor.

#### 5.4.1 The onset is 1994–96, not 2022

Extending the UK Commons series to **1985–2026** (10,006 sitting-day files)
shows the register *declining* before the consumer web and rising after:

| period | slope (gap units/yr) |
|---|---|
| 1985–1995 | **−18.97** |
| 1996–2005 | **+31.64** |
| 2006–2016 | **+42.22** |
| 2017–2026 | +28.26 |

The gap falls from 774 (1985) to a minimum of **593 (1994)**, then climbs
monotonically to 1,720 (2026). The frequency-and-dispersion-matched placebo is
flat across all 41 years (1,520–1,575), so this is not measurement drift. A
pre-existing secular trend would have been rising in 1985–94; it was falling.
**The inflection coincides with mass consumer internet adoption, and the
transformer era is the slowest-growing of the three rising periods.**

#### 5.4.2 It arrives with new members, not with changed ones

| quantity (16 chambers) | pooled | 95% CI |
|---|---|---|
| **arrival premium** (new members minus incumbents, same years) | **+1.87** | **[+1.25, +2.49]** |
| within-member change | −0.42 | [−1.32, +0.49] *(n.s.)* |
| compositional component | +2.12 | — |

Positive in **15 of 16 chambers** (sign test p ≈ 2.6 × 10⁻⁴), significant
individually in 10. Member-level bootstrap, resampling members not words.

The honest form of this is "**incumbents flat, arrivals higher**" — not
"incumbents declined". The within-member component is significantly negative
in only 4 chambers (BC, ON, QLD, SK) and significantly *positive* in 3 (NI,
SCO, WAL). Those three are all UK devolved, and two carry known
era-asymmetric instruments (Wales PDF→XML across the windows; NI's second
window truncated by the Stormont collapse), which is exactly the artifact
shape that manufactures a spurious within-member effect.

#### 5.4.3 What distinguishes arrivals is birth year

Per-member-year register rate on birth decade, province and year fixed
(3,445 member-years, 79% birth-year coverage from Wikidata/Wikipedia):

| predictor | coefficient | t |
|---|---|---|
| **birth decade** | **+0.93** | **+12.03** |
| birth decade, adding occupation + education | **+1.06** | **+13.36** |
| post-secondary attested | −0.53 | −3.31 |
| occupation: law | −1.67 | −5.83 |
| occupation: communications/PR/journalism | −0.67 | −2.02 |

Raw cohort means run 33.30 (1930s) → 33.64 (1950s) → 36.84 (1970s) → 39.60
(1990s) — flat, then climbing from the 1960s cohort.

**Candidate professionalisation and educational expansion are refuted as
explanations**: communications backgrounds use *less* of the register, as do
law and the post-secondary-educated, and controlling for both *strengthens*
the cohort coefficient.

**Cohort, not age.** With year fixed effects, birth year and age are
collinear, so the coefficient could in principle be an age effect. It is not:
mean chamber age is flat (52.2 in 2006 → 51.4 in 2019) while the register
rises +2.06. A stable-age chamber shows no trend under an age effect. Under a
cohort effect, mean birth year advanced 13.8 years, which at +0.093/yr
predicts **+1.28 of the observed +2.06 — about 60%**.

#### 5.4.4 What is still not identified — three nulls

Birth cohort is a portmanteau for everything that differs between
generations. Three attempts to isolate computer exposure specifically have
now returned null, each fixing the previous one's flaw:

| attempt | design | result |
|---|---|---|
| 1 | district adoption during **tenure** (US states; provinces) | null; −0.008 (t = −0.64) and −0.0045 [−0.0108, +0.0009] |
| 2 | cohort × **service**-province adoption | +0.09 (t = +0.97) |
| 3 | cohort × **birth**-province adoption, formative window | see below |

Attempt 3 used birthplace collected from Wikidata P19 (70% coverage) — the
right geography at last, since **34% of members serve a province other than
their birth province**, half of them foreign-born across 34 countries. Three
specifications, pre-committed in that order:

| specification | estimate | verdict |
|---|---|---|
| **A — direct**: birth-province adoption during the member's own age-15–25 window | **−0.40** (t = −1.00) | null, wrong sign, 106 people |
| B — interaction, all cohorts | +0.21 | t = +2.20 on member-year SEs, but **CI [−0.22, +0.33]** clustered on the 10 birth provinces |
| C — birth-settlement size (urbanicity) | +0.15 (t = +1.37) | null |

**B is a cautionary case worth keeping in the record.** Its regressor varies
only across birth provinces, so member-year standard errors treat 2,394
observations as independent when there are ten clusters. Correctly clustered,
23% of resamples fall at or below zero. This is the second time in this study
that unclustered inference on a province-level regressor produced a spurious
"significant" result, and both times it flattered the hypothesis.

Meanwhile **the cohort effect is unmoved by any of this**: birth decade +1.02
to +1.22, t ≈ +11–12, in every specification.

So: the register enters legislatures through generational replacement, and no
measure of technology exposure we can construct predicts which members bring
more of it. The defensible claim is **generational, mechanism unidentified**.
Ambient computing remains the leading candidate on **timing** — the onset at
1994–96 in §5.4.1 — but that is a coincidence of dates, not a dose-response,
and three dose-response tests have now failed. Further proxies are not worth
running; the informative next evidence would be a different kind, not a
fourth operationalisation of the same one.

### 5.3 The exposure-gradient tests — two nulls, and a continental replication

If ambient computer immersion drives the register drift (the strongest causal
reading of its ~2006 onset), drift intensity should gradient on local
adoption. Two designs tested this, both entirely inside pre-LLM windows
(member drift 2006–2010 → 2015–2019):

**US Congress** — drift vs home-state internet adoption (NTIA Sept-2001 CPS):
coefficient −0.008 per sd (t = −0.64), null, with demonstrated power (the
same regression finds Republicans drifting +0.093, t = +3.40). Escape hatch:
congressional drafting staff live in Washington, so home-state adoption may
never reach the drafting environment.

**Canadian provinces** — the version without the escape hatch: provincial
staff live in-province, offices are small, many members self-draft. Exposure
from StatCan 22-10-0034 (household internet use, by province; 2000 spread
43.6–58.8). Seven chambers built from their own Hansard archives, 259
name-resolved members with ≥5k words in both windows:

| province | adoption 2000 | mean drift |
|---|---|---|
| Alberta | 58.8 | +0.002 |
| BC | 55.9 | +0.042 |
| Ontario | 54.2 | +0.061 |
| Nova Scotia | 52.0 | +0.082 |
| Manitoba | 49.8 | +0.094 |
| Saskatchewan | 46.9 | +0.074 |
| Newfoundland | 45.5 | +0.062 |

Registered spec (2000 level): slope **−0.0045**, province-clustered bootstrap
CI [−0.0108, +0.0009] — wrong sign for exposure. Alternative spec (adoption
growth 2000→2003, the saturation-lag reading): **+0.0059** [−0.0062,
+0.0153] — null, and the growth column visibly fails to order the drift.

**Verdict: the register climb does not dose-respond on local computer
adoption at either margin, in either country.** The exposure mechanism in its
geographically testable form is unsupported; cultural accounts that operate
nationally (or continentally) remain open, but they are exactly the accounts
a geographic gradient cannot test.

**The finding that emerged anyway:** six of seven provinces show strong
pre-LLM register drift (+0.04 to +0.09 over nine years). The UK's secular
climb replicates across seven independent chambers with independent Hansard
offices. The register change is continental and predates the tools everywhere
examined.

*Caveats: seven clusters; Alberta is an outlier (+0.002, n = 19, PDF-era
extraction); and each province passes through a bespoke extractor with
markup-era boundaries inside the design windows (BC 2008, ON 2011, NS 2010),
so era-asymmetric extraction artifacts load directly on the cross-province
coefficient. The NULL is robust to this — no artifact pattern plausibly
creates an absent positive gradient — but the negative point estimate should
not be quoted without an era-boundary robustness pass.*

### 6.1 The alignment-register experiment — one result, one failure

A paired design was built to replace the withdrawn test and to ask a separate
question: is the register that leaked specifically the **alignment** register?
An instruct model differs from its own base model only by post-training, so
what SFT-plus-preference-optimisation adds is directly measurable. Identical
prompts (openings of real pre-2023 segments), identical decoding and seeds, no
chat template — so the only difference is the weights. Two families completed:
Qwen3-8B and Mistral-7B. Generations where the instruct model *analysed* the
prompt rather than continuing it are dropped from **both** members of the pair,
since that is instruction-following behaviour rather than register.

**The result that holds — Kobak's instrument is substantially an alignment
artifact.** Mean log(instruct/base) for the style words, against
frequency-matched controls drawn from the base model's own output:

| family | excess | 95% CI | prompt pairs |
|---|---|---|---|
| Qwen3-8B | **+1.04** | [+1.05, +1.31] | 668 |
| Mistral-7B | **+0.65** | [+0.67, +0.99] | 788 |

Pooled excess **+0.880, p < 0.001**, and it is broad rather than a few words:
**70.8% of style words are instruct-preferred against 28.2% of all other
words.** So the vocabulary Kobak derived from PubMed abstracts — with no
reference to alignment at all — is largely the vocabulary that post-training
adds. "AI register" is more precisely **assistant register**.

**The test that fails — it does not predict Hansard.** The same score, asked
whether it predicts *which words rose*, does not survive frequency
stratification:

| predictor | Spearman | partial \| freq | stratified p |
|---|---|---|---|
| alignment preference (paired) | +0.112 | +0.097 | **0.098** |
| generic model-vs-human (unpaired) | +0.044 | +0.006 | 0.581 |
| — Qwen3 alone | +0.045 | +0.034 | 0.314 |
| — Mistral alone | +0.012 | +0.031 | 0.298 |

Neither family replicates individually and the pooled value misses 0.05. **The
replacement for the withdrawn mechanism test is not delivered.** (An earlier
run gave p = 0.031; that was before the meta-commentary filter, and the
filtered number is the honest one.) The rarity check does confirm the design
works as intended — the new predictor scores +0.22 against log-rarity where
the dead one scored +0.92 — so the failure is a real null, not a repeat of the
same confound.

**What post-training actually adds** (descriptive, mean log instruct/base):

| category | value |
|---|---|
| discourse structuring — *moreover, furthermore, however, ultimately* | **+0.43** |
| significance marking — *important, crucial, vital, essential* | **+0.33** |
| constructive verbs — *ensure, foster, enhance, promote* | +0.16 |
| hedging — *perhaps, arguably, somewhat, potentially* | **−0.02** |

This refines the sycophancy hypothesis rather than confirming it. What
preference tuning adds is **scaffolding and evaluative inflation**, not
hedging or politeness — hedges are flat to slightly *down*. If the assistant
register is leaking into parliamentary speech, the leak is "moreover" and
"crucial", not "perhaps".

**Limits.** Two families, not three — Llama-3-8B-Instruct has no local weights
and is gated. The two disagree in magnitude by ~1.6×. The descriptive list
still carries some task residue (*text, speaker, context*) because the filter
only inspects each generation's opening. And an instruct-model contrast is not
the same as measuring RLHF specifically: SFT and preference optimisation are
confounded here. Separating them needs a family that ships intermediate
checkpoints — OLMo-2 publishes SFT and DPO stages separately and is the right
next step.

And the honest concession: **New Brunswick was selected because a signal was
visible there** (the origin was a clip of a member reading an AI framing
sentence aloud). That selects on the outcome even though the instrument is
external. NB is therefore labelled the **discovery** corpus, quoted as an
upper bound, and excluded from the Fisher combination.

---

## 7. Quality measurement

Instrument: the **Discourse Quality Index** (Steenbergen, Bächtiger,
Spörndli & Steiner 2003) — the standard deliberation-quality scale for
parliamentary debate, whose own worked examples come from a 1998 Commons
debate. Ten of those published codings are embedded as in-context anchors,
so the scale is the authors', not ours.

Two traps designed against. **Circularity**: most "quality" metrics are
style metrics, and AI text differs in style by construction, so every
measure carries a circularity grade and the judge separately reports
P(AI-assisted) purely to detect leakage. **Genre**: AI-flagged segments
concentrate in prepared statements, so comparisons run within
selection-matched pools.

Reliability: repeat-pass Spearman 0.68–0.91 per dimension, at or above the
published human inter-coder bar (their justification r = 0.716).

Findings: AI-flagged speech scores **higher** on formal justification, ~3×
**lower** on first-person witness, and **lower** on engaging opponents'
demands. Blinded 2019 → 2026: justification +0.21 and evidence +0.19 up,
**respect toward others' demands −0.36 (0.96 → 0.60)** and constructive
politics −0.30 (0.54 → 0.24) down. Summary: **form up, deliberation down**.

*(An earlier draft of this section gave the respect figure as 0.96 → 0.52.
The anchored-v2 run's own record, `quality_methods.md`, says 0.60; 0.52 was
a transcription error and the corrected value is above.)*

**Genre remains the unsolved confound, and recent work makes it sharper.**
The design compares within selection-matched Pangram strata, but full
prepared-vs-spontaneous labels were always an open item. We now know from the
unscripted-business analysis (§5.2c) that AI concentrates in scripted formats
— Canada's Statements by Members carry a larger shift than Oral Questions. So
"AI-flagged speech engages opponents less" may in part be "scripted speech
engages opponents less". The provincial corpora built since carry business-
rubric metadata that would let this be settled rather than stated; it has not
been done.

The pronoun result connects to a real literature — Pennebaker and
colleagues found high-status speakers use fewer first-person singulars, and
deception research found the same for fabricated accounts. Here it is
neither: it is **authorship displacement**, because the drafting voice has
no experience to reference. A corollary worth stating: pronoun-based
psychological inference on post-2023 institutional text is now unsafe.

---

## 8. What each headline number licenses you to say

| number | claim it supports | claim it does NOT support |
|---|---|---|
| p = 2.4 × 10⁻⁷ (Fisher, 3 chambers) | the vocabulary shift is real and replicable | anything about *how much* text is AI |
| excess +0.218 to +0.272 | consistent magnitude across parliaments | that it is large |
| 8.3% prevalence (NB) | ~1 in 12 recent NB segments is AI-flagged | anything about other chambers *(pending)* |
| Sp = 1.0 measured (423/423) | no inflation from false positives | that Se = 1 on *edited* AI — unmeasured, so 7.5% is a floor (§4.3) |
| 89.6% of 643 confirmed | the screen is a precise stratifier | a corpus-wide rate |
| AUC 0.951 (Opus screen) | frontier LLMs track a commercial detector | that either tracks ground truth |

**And one wording constraint.** In Canada the absolute volume of AI-style
vocabulary *fell* (bootstrap CIs 0.925 and 0.916). It fell less than
comparable vocabulary, which is what the significant result measures. The
defensible phrasing is **"rises relative to comparable vocabulary"** — not
"rises". That holds in all four chambers; the stronger claim does not.

---

## 9. Reproducing any of it

```
run_protocol.py    CORPUS_NAME OUT_PREFIX segments.jsonl   # the frozen protocol
formality_axis.py  CORPUS_NAME segments.jsonl              # data-defined control
cross_corpus.py                                            # table + Fisher + figure
```

The protocol's only per-corpus input is the corpus name, which seeds the RNG
via `sha1(name)[:8]`. Per-corpus code exists solely to map a source format
onto the shared segment schema. That separation is what makes the
cross-chamber combination legitimate rather than a fishing expedition.
