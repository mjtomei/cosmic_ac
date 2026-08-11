# S10 — adversarial review, with responses

**Updated 2026-08-03.** Twelve findings from the adversarial methodology
review, each with the attack stated plainly, our response, and what has been
done. Terms of art are marked with a dagger† on first use and defined in §5.

Three findings were re-derived independently from the raw data before being
accepted, because a review reporting 48 of 49 findings surviving its own
verification is itself a thing to be suspicious of. All three reproduced.

**Since the first version of this document, two findings have been obviated
rather than fixed** — the analyses they attacked have been removed from the
study. That is the cleaner outcome where it is available, and §2 says why.

---

## 1. Status

| # | Finding | Severity | Status |
|---|---|---|---|
| F1 | The word-level mechanism test is a rarity index, not an AI-preference score | Fatal | **OBVIATED** — analysis and its corpus deleted |
| F3 | Kobak's content words were never run, and v1.0 fails them | Major | **OBVIATED** — control cut as orthogonal |
| F5a | Sensitivity measured on one 7B generator | Major | **OBVIATED** — replaced by published evaluations |
| F2 | Placebo pool† matched on frequency but not dispersion† | Major | **Applied** (protocol v1.1) |
| F4 | The NB prevalence figure is a five-month window; §5 names the wrong stratifier† | Major | **Applied** |
| F6 | The frequency-weighted secondary does not replicate; the sweep claim is misquoted | Major | **Applied** — full table now printed |
| F7 | The formality control is not actually frequency-matched | Major | **Applied** — buckets now fill |
| F8 | One ratio pooled over 2024–26 is not a stable estimand† | Major | **Applied** — and it exposed instrument decay |
| F9 | Zero-count smoothing† is asymmetric between instrument and placebo | Minor | **Applied** — now load-bearing (see below) |
| F11 | Instrument citation wrong (fourth author is Lause, not Berens) | Minor | **Applied** |
| F12 | No-interference† assumption never stated | Minor | **Applied** |
| F5b | Sensitivity on *edited* text is unmeasured by anyone | Major | **Stands — unfixable; stated as a floor** |
| F10 | Estimand departs from Kobak's, forfeiting the prevalence reading | Minor | **OUTSTANDING** |

**Net effect on the headline.** Effect sizes roughly halve under v1.1. The
combined p-value moves from 2.4 × 10⁻⁷ to 2.9 × 10⁻⁶ across five confirmatory
chambers (two of which are individually null). Prevalence becomes a floor over
a five-month window rather than a corpus rate. **Nothing reverses direction.**

**One dependency shifted.** F9 was originally reported as "subsumed by F3."
With the content-word control removed, F9 stands alone as the justification
for v1.1's present-in-both restriction — and it is sufficient on its own:
words absent from both periods contribute a constant +0.58 to +0.68 from the
smoothing, worth 11% of New Brunswick's raw primary and 31% of the UK's.

---

## 2. Findings obviated by removing an analysis

### F1 — the mechanism test, and the corpus under it

**The attack.** §6's strongest anti-p-hacking† defence claimed that a word's
"AI preference" — measured from 40 synthetic speeches and a 2019 control —
predicts which words later rose in Hansard, at Spearman† +0.548, permutation
p† < 10⁻⁴. But the 2019 control is a *subset* of the 2018–22 pre-window, so
each word's rarity sat inside both the predictor and the outcome with the
same sign.

**Independently verified, and the mechanism is a variance problem.** The
predictor was

```
                  ( syn_n(w) + 0.5 )              ( ctl_n(w) + 0.5 )
ai_pref(w) = log ────────────────────  −  log  ────────────────────
                        6,838                        703,905
                  └ rate in AI text ┘          └ rate in 2019 humans ┘
```

The synthetic corpus was 6,838 words, so **39 of the 89 usable words occurred
exactly once** — seventeen distinct values in total, against control counts
spanning 0 to 7,759. The variance is 0.758 in the numerator term against 4.390
in the denominator term, so the predictor collapsed into its denominator: it
correlates **+0.914** with the control term and **−0.211** with the synthetic
term.

| quantity | Spearman |
|---|---|
| published predictor vs the Hansard shift | +0.548 |
| **rarity alone: −log(2019 count), no AI data at all** | **+0.568** |
| AI evidence alone: log(synthetic count) | −0.219 |
| partial correlation† controlling log(pre count) | **−0.008** |
| permutation within frequency strata† | **p = 0.24** |

Rarity alone beats the published predictor. The synthetic corpus contributed
nothing and slightly hurt.

**Response: obviated.** The corpus has been removed from the study, so the
analysis no longer exists — this is not a defence awaiting correction. What is
retained is the design lesson: **an unpaired† comparison of model output
against a human corpus inherits that corpus's frequency structure on both
sides.** The replacement is paired by construction — an instruct model against
its *own base checkpoint* on identical prompts, which cancels baseline
frequency exactly (Geng & Trotta; Yakura et al.).

### F3 — the content-word control

**The attack.** Kobak's team annotated all 900 excess words content-versus-style
blinded to year; the 462 content words are the field's canonical topic-churn
control; no script in the study touched them; and run under v1.0 the primary
statistic **cannot tell them apart from the style list** (Canada +0.282 content
vs +0.210 style).

**Response: obviated, on a ground the review did not consider.** Kobak's
"content" list is *PubMed's* content — *lachnospiraceae, carbapenemase,
tocilizumab, clostridioides, retrosigmoid*. Only 105 of 462 appear in
legislative text at all. **Whether biomedical jargon moved in a parliament is
a fact about parliamentary topics, orthogonal to whether our style measurement
is picking up AI here.** The frequency-and-dispersion-matched placebo already
controls for in-domain churn, using words that actually occur in the domain,
and does it better.

Two things found on the way to that conclusion are worth recording. Under
v1.1 the control appears to pass decisively (style − content +0.23 to +0.48),
but that is **the pandemic leaving our pre-window**: the steepest declines are
*coronavirus* (−4.63), *quarantine* (−4.58), *omicron* (−4.03), *lockdown*
(−3.00), and removing just 24% of the list moves Ireland from −0.358 to
−0.011. A control that passes because COVID ended is not evidence. And
instruct models prefer Kobak's **content** words too (+0.488 against matched
controls), so content was never a clean null — differencing it away removes
real signal.

**What replaces it** is the validation that actually bears on the instrument:
does lexicon density predict an independent detector, segment by segment?
See §4.

### F5a — sensitivity measured on a single 7B generator

**Response: obviated.** Pangram's catch rate on machine text is far better
established publicly than 40 speeches of ours could show — 99.3% on RAID
across domains (Dugan et al.), never below 99.8% at Chicago Booth, the only
one of four tools to detect reliably in a peer-reviewed VUB evaluation, 1.4%
self-reported FNR (Emi & Spero, arXiv:2402.14873), and training against 19
humanizer tools. Citing that is shorter *and* stronger than reproducing a
weaker version with a generator nobody's office uses.

**The one claim the corpus was carrying** — that the eight-detector null means
"little unedited paste" rather than "these detectors don't work here" — now
rests on real adjudicated text instead: the same segments those detectors rate
unremarkable were confirmed by Pangram as **576 AI-or-Mixed of 643**, and a
frontier LLM screen separates its verdicts at AUC† 0.951 while open-weight
models manage 0.55–0.72. The null is a property of perplexity-based detection,
not of the record.

---

## 3. Findings applied

**F2 — dispersion.** Placebos were matched to instrument words on pre-period
frequency only. Corpus linguistics treats **dispersion**† as co-equal (Gries
2008; Egbert & Biber 2019) — a pool of bursty topic words decays faster
between windows, depressing the placebo median and inflating every excess. We
had written this exact filter for the formality control and never ported it.
v1.1 matches on both axes; costs 12–44% of each effect size.

**F4 — reference population and stratifier.** The NB prevalence frame is 3,998
segments from five sitting months (Oct–Dec 2025, Mar/May 2026) — 10.6% of the
corpus, on the steepest part of the ramp. Restated as **"7.5% of New Brunswick
segments in sittings from October 2025 to May 2026."** The deciles were of the
**Falcon/Binoculars** score, not the Opus screen, and realised AI counts across
them were 0,1,1,1,1,0,1,1,1,2 — flat, so the design degenerated to an effective
simple random sample. Harmless for the point estimate under equal allocation;
it must be said.

**F6 — the frequency-weighted secondary.** The claim "every cutoff from <1 to
<50 per 100k gives p ≤ 0.008" was New Brunswick only, unlabelled, and
misquoted (NB's <1 cell is 0.015). Full table now printed: **4 of 30
confirmatory cells reach p < 0.05.** The equal-weight choice is defended on
the merits and is Gray's published design; letting a reader assume the two
statistics agree is not defensible.

**F7 — formality control.** The candidate floor of 200 sat above log₂ bucket 7,
but 227 of the instrument's 407 words live in buckets 0–3, so those quotas
could never fill: New Brunswick's control was **67 words against 407**, hence
systematically *more common* than what it controls. Floor lowered to 20 with
neighbour-borrowing; controls now fill 362–407. Gaps barely move (+0.07 to
+0.39), so the earlier numbers were under-evidenced rather than wrong.

**F8 — the pooled 2024–26 ratio.** Chambers weight the post years very
differently (Canada is 49% 2024; Ireland 31%), and the markers are
non-stationary† inside the window. Per-year series now reported. **Canada's
pooled null was a mixture artifact** — it is positive and significant in both
2025 (+0.068) and 2026 (+0.058). See §4 for what else the series revealed.

**F9 — smoothing asymmetry.** Because the pre-window is 2–3× the post-window,
a word absent from *both* periods scores a constant +0.58 to +0.68. The
genuinely new part is the placebo side: the pool is built from pre-period
counts, so its lowest bucket holds words with count 1, whose expected logFC is
about −0.43 — a structural ~1.1 log-unit gap **before any AI exists.** Fixed by
the present-in-both restriction, which F9 now justifies on its own.

**F11 — citation.** Fourth author is **Jan Lause**, not Berens (Berens is the
lab, hence the `berenslab` GitHub org). Web-verified: Kobak D,
González-Márquez R, Horvát E-Á, Lause J, *Science Advances* 11(27):eadt3813
(2025). Fixed in the methodology and the frozen protocol; **still wrong in the
project `CLAUDE.md`** and should be corrected there before it reaches the paper.

**F12 — no-interference.** **SUTVA**† is nowhere in our documents even though
§5.2 measures its violation directly. Stating it is free strengthening:
contaminated controls bias toward the null, so every reported effect is a
floor.

---

## 4. Issues the review did not find

These emerged from working through the findings and are, in our judgement,
more serious than anything left in the review.

**The lexicon is largely a register meter.** Per-segment density predicts the
Opus detector at ρ = +0.252 while frequency-and-dispersion-matched random word
sets predict +0.024 (0 of 30 beat Kobak) — so the list is genuinely specific.
But the association is **the same size before AI existed** (+0.250 pre-2023,
n = 20,329). What the two instruments agree about is a register that predates
these tools. That validates Kobak's list *for that register*; it does **not**
support segment-level claims of the form "this speech is machine-drafted
because it is lexicon-dense."

**The detector sees change the lexicon misses.** Lexicon density rose 12%
pre→post; the Opus score rose 120%. Matching segments on **absolute** density
in fine calipers† — the two eras agreeing on mean density to two decimal places
within each bin — the score gap is **+10.18**, slightly *larger* than the
unmatched +9.85. Conditioning on density absorbs none of the detector's rise.
So the two arms measure different quantities (register shift vs drafting
prevalence) and our lexicon effect sizes are conservative.

**The instrument decays.** Four of six chambers peak and decline across the
per-year series, and the US Senate goes negative. Kobak's list was derived
from 2024 data, and Geng & Trotta document individual markers collapsing once
they become notorious. New Brunswick's lexicon excess more than halves from
2025 to 2026 (+0.266 → +0.105) while its measured Pangram prevalence
**triples** (4.3% → 13.6%). **Trajectory claims must rest on the detector, not
the word list.**

**F1's replacement has not landed.** The paired base-vs-instruct predictor does
not survive frequency stratification (pooled p = 0.098; neither family
replicates alone). The design is sound — its rarity check is +0.22 against
log-frequency where the dead test scored +0.92 — so this is a real null, not
the same confound returning. There is still no word-level mechanism evidence.

**The likelihood-ratio arm is weak and possibly confounded.** Scoring Hansard
under instruct-vs-base checkpoints gives small, inconsistent movements (two
chambers positive, two null, US Senate significantly negative), against base
log-probability changes 3× larger. Instruct models may simply be more robust to
unfamiliar post-2023 content, which would produce the same pattern with no
register drift.

**What did land**, and it is worth stating as a contribution: instruct models
over-produce Kobak's style words relative to their own base checkpoints at
**+0.88, p < 0.001**, with 70.8% of style words instruct-preferred against
28.2% of all other words. Kobak inferred LLM causation from a temporal pattern
in human text, explicitly avoiding labelled model output; this measures it from
the weights, by the route they set out to avoid needing.

---

## 5. Glossary

For a reader comfortable with probability and measurement but not with the
conventions of empirical social science.

### Testing and inference

**Null hypothesis.** The boring explanation you are trying to rule out. Here
it is never "nothing changed" but "this changed no more than comparable
vocabulary changed anyway."

**p-value.** Probability of a result at least this extreme *if the null were
true*. Not the probability the null is true. Think of it as a false-alarm rate
for a detector thresholded at the observed value.

**Permutation / placebo test.** Rather than assume a null distribution, build
it: re-draw the thing you are measuring many times under conditions where the
effect cannot exist, and see where the real value falls. Ours draws 1,000
matched random word sets. It is the empirical-noise-floor approach — measure
the noise instead of modelling it.

**p < 0.001 as a bound.** With 1,000 draws the smallest observable p is 1/1000.
"p < 0.001" means zero draws beat the real value — the resolution limit of the
simulation, not a measurement.

**Stratified permutation.** Shuffling only *within* groups sharing a nuisance
property (here word frequency), so that structure is preserved and cannot
masquerade as signal. A global shuffle destroys it — which is how F1's
confound went unseen.

**Confound.** A third variable driving both things you are relating, producing
a correlation that means nothing. In F1 it was the word's own rarity.

**Partial correlation.** What remains between two variables once a third is
removed from both — the residuals correlated against each other. Raw +0.55
with a partial of −0.01 means the third variable did all the work.

**Spearman (rank) correlation.** Pearson correlation computed on *ranks*. Sort
the items by each measurement and ask whether the orderings agree. Robust to
outliers and to non-linear-but-monotone relationships. Being a within-group
quantity, it says nothing about whether the *levels* moved — two instruments
can both drift upward while their internal ordering is unchanged.

**AUC.** Probability that a randomly chosen positive scores above a randomly
chosen negative. 0.5 is chance, 1.0 perfect. Threshold-free, so it compares
detectors whose score scales differ.

**Caliper matching.** Comparing groups only within narrow bands of a
confounding variable, so the comparison holds it near-constant. Finer than
binning by quantile: if a distribution has shifted, one group sits
systematically higher *within* each quantile bin, and the comparison is still
confounded.

**Fisher's method.** Combines independent p-values: X² = −2·Σln(pᵢ) on 2k
degrees of freedom. Asks whether a pattern is unlikely taken together.

**Effect size vs significance.** Significance says an effect is unlikely to be
noise; effect size says how big. With tens of millions of words everything is
significant, so effect size is the only interesting quantity.

**Power.** Probability of detecting an effect that is really there. A null from
a small corpus is weak evidence of absence — which is why the US Senate null on
24M words means something and the earlier 3M-word version did not.

**p-hacking / researcher degrees of freedom.** Trying many analyses and
reporting the one that worked. Defences: fix the analysis before seeing the
data, use an instrument someone else built for another purpose, and have no
tunable choices in the primary statistic.

**Discovery vs confirmatory corpus.** The dataset where you *found* an effect
cannot also be evidence for it, because you selected on the outcome. New
Brunswick is our discovery corpus, quoted separately and as an upper bound.

**SUTVA / no-interference.** The assumption that one unit's treatment does not
affect another's outcome. Violated here in an interesting way — AI writing
changes how non-AI text is written — so our controls are partly treated, and
every effect is biased toward the null.

### Measurement and correction

**Sensitivity (Se)** = P(flag | actually AI). **Specificity (Sp)** = P(no flag
| actually human). Properties of a detector *on your data*, not universal
constants.

**Rogan–Gladen correction.** π = τ·Se + (1−τ)(1−Sp), so
τ̂ = (π̂ + Sp − 1)/(Se + Sp − 1). With Sp measured at 1, this collapses to
**τ̂ = π̂/Se**, and since Se ≤ 1, τ̂ ≥ π̂. It contributes no number here — it
tells us the *shape* of the uncertainty: one-sided, upward, with 1/Se as the
unknown multiplier.

**Clopper–Pearson / Wilson intervals.** Confidence intervals for a proportion;
Clopper–Pearson exact and conservative, Wilson better-behaved near 0 and 1.

**Rule of three.** Zero events in n trials bounds the rate at about 3/n. Zero
flags in 2,400 pre-LLM segments bounds the false-positive rate near 0.125%.

**Two-phase / double sampling.** A cheap instrument scores everything and
defines strata; the expensive one is spent where informative. The cheap one
need not be accurate, only correlated with truth, because stratum weights are
known from the full corpus.

**Stratifier.** The variable used to divide a population before sampling. If
uninformative, the design degenerates to simple random sampling — not fatal,
but it must be disclosed (F4).

**Clustered bootstrap.** Resampling whole clusters (here, whole speeches)
rather than individual observations, because words within a speech are not
independent.

**Selection on the outcome.** Choosing units by the quantity you then measure
in the remainder. Guaranteed to bias, because you removed the upper tail of a
noisy distribution. Fixed by **split-half**: rank on one half of the data,
measure on the other.

### Corpus statistics

**Log fold-change.** log(rate after ÷ rate before). Symmetric around zero and
additive, which is why count ratios are analysed in logs.

**Smoothing / pseudocount.** Adding a constant (0.5) so zeros do not produce
infinities. Not innocent: when the two denominators differ, an absent word
gets a systematic non-zero score (F9).

**Equal-weight vs pooled.** Equal-weight gives each word one vote; pooled sums
counts, so common words dominate. They can point opposite ways on the same
data — as they do here (F6).

**Dispersion.** How evenly a word spreads across documents or sittings, as
distinct from how often it occurs. 500 occurrences in one debate is frequent
but badly dispersed. Ignoring it selects bursty topic words.

**Frequency matching.** Choosing controls with the same baseline frequency as
each instrument word — the analogue of matching impedance before comparing two
measurements.

**Placebo / donor pool.** The set controls are drawn from. Its construction
determines what the null represents.

**Non-stationary.** A process whose statistics change over time. Our markers
are non-stationary inside the post-window — some collapsed after 2024, others
kept rising — so one pooled ratio over 2.5 years is not a stable quantity.

**Paired vs unpaired design.** Paired compares two conditions on the *same*
units, so unit-level nuisance variation cancels exactly. Base-versus-instruct
on identical prompts is paired; model-output-versus-human-corpus is not, and
that difference is what killed F1.

**Document containment.** Kobak's estimand: the fraction of *documents*
containing at least one group word, rather than a token rate. It is what
licenses a prevalence reading ("at least 13.5%"); a token-rate mean has none.
Adding it as a parallel primary is F10, the one outstanding item.
