# Remaining evidence-gap evaluations — the reviewable plan

The evidence-standards survey (`EVIDENCE-STANDARDS-SURVEY.md`, nine
adjacent-literature reviews) produced a recommendation list; the
measure-centered items and everything zero-cost are done and in the paper.
This document is the decision sheet for what remains: per item, the exact
result in the paper it concerns, the gap in plain terms, what the
evaluation would concretely be, what changes in the text under each
outcome, and the effort or spend. Items are ordered by my suggested
priority; the last three are gated on spends and are independent of the
rest.

---

## 1. The cohort claim's identification package (survey rec 6)

**The results concerned.** §4.6's headline bullet — birth **+0.88 per
1,000 words per decade** (t 15.7 clustered) net of spoken year — and the
claim that the gradient **steepens as drift-formed cohorts arrive**; also
the within-member **+0.51σ/decade** and the era figure.

**The gap, plainly.** Age, period, and cohort satisfy age = year − birth,
so no data can identify all three slopes; only two combinations are
identified, and the +0.88 is one point on a line of equally-fitting
(age, period, cohort) combinations. The paper *names* the limit but still
quotes the point as if estimated. The steepening claim — the half that
ties the gradient to the drift — is currently read off a figure, not
tested. And the live rival is career-stage age-grading: juniors may write
differently because they are junior-in-career, not because of when they
were born; the test that separates these sits in a footnote.

**The evaluation.**
(a) *Publish the solution line*: tabulate the implied period and cohort
slopes across the plausible range of age slopes — one small table, pure
arithmetic on the committed fit.
(b) *Bound it with the pre-drift Senate cell*: US senators born 1917–1964
observed 1994–2004 are a cell where the cohort effect is ~zero by
construction (all pre-drift cohorts), so their age slope is directly
estimable (≈ −1.05/decade on current data) and caps the line.
(c) *APC-I (Luo & Hodges)*: the **nonlinear** inter-cohort deviations are
identified with no assumptions at all; fit them on member-year cells and
test the post-1985 cohort deviations — this is the formal version of the
steepening claim, which is exactly a nonlinearity claim.
(d) *Promote the tenure test*: within (birth × year × chamber) cells,
regress rate on tenure — net of all three clocks simultaneously; this is
the one regression that discriminates career-stage from cohort, and it
currently lives in footnote r46a.

**Outcomes.** If the bounded line keeps the cohort slope positive and
APC-I confirms the post-1985 deviations, the claim upgrades from
"identified via an assumption we name" to "bounded and nonlinearly
confirmed." If the tenure test carries the load instead, the honest
rescope is "a juniority gradient — cohort or career clock — steepened in
the drift era," which is still the paper's story. Either way the +0.88
sentence gains a "one point on this line" companion.

**Effort.** Held data only. (a)+(b) half a day; (c)+(d) 3–5 days.

---

## 2. Member-panel decomposition, ported to three arms (survey rec 8, remainder)

**The results concerned.**
(i) Permeation's pre-LLM delta (§4.8: the detector-independent +0.01-range
in-context shift, and the pre-LLM window parity);
(ii) chase-and-flight's "**the peak does not migrate**" (§4.6b) — which
footnote r46cls concedes is adjudicated by an aggregation choice
(member-year aggregation *would* show migration; member-level does not);
(iii) the unexplained factor-of-two between the between-member cohort
gradient (+1.25/decade, member-year panel) and the within-member drift
(+0.51/decade).

**The gap, plainly.** Every arm with a time dimension faces the same
question — is the aggregate movement *people changing* or *people being
replaced*? — and the study has answered it properly exactly once (§4.6's
within-member fixed-effects drift). The other arms either don't split it
(permeation: the era contrast pools sitting members with turnover, and
§4.6's own cohort result says turnover is large), or split it informally
(the peak-migration "40%" replacement share has no SE and the two
aggregations disagree).

**The evaluation.** One asset serves all three: the member × word × year
cache (already built for the flight work, `flight_member_cache.json.gz`,
extended panel-wide).
(i) Recompute the permeation era contrast on the balanced sub-panel
(members present in both windows) with member fixed effects; decompose the
aggregate delta into within-member change, entrant-minus-leaver
composition, and interaction.
(ii) Run the Firebaugh decomposition of the peak's movement with proper
SEs — report both components as *the* result instead of choosing an
aggregation; add per-word lead–lag (fit each word's tier crossing dates;
does the top's date precede the bottom's?), which is the direction-of-
diffusion evidence the fashion literature runs on.
(iii) Reconcile 1.25 vs 0.51 explicitly: the gap *is* the composition
share, and one paragraph can say so with the decomposition's numbers.

**Outcomes.** Permeation: if the within-member component survives, the
diffusion claim strengthens sharply (it is currently vulnerable to "it's
all turnover"); if it's all composition, the claim rescopes to
cohort-borne diffusion — still real, differently worded. Peak migration:
the result becomes aggregation-proof either way. Lead–lag: top-first
supports the cycle's direction; simultaneous take-off supports a common
external source (also informative — it points at the tools).

**Effort.** Held data; ~1 week. The cache exists; the analyses are new
scripts.

---

## 3. The ruler audit: per-word decomposition and trend-matched donors (survey rec 7)

**The results concerned.** The paper's second headline: the register
**rise begins 1994–96** and the marker list "predates the models by
decades" (§4.5); also permeation's lack of a control word set (its
footnote admits "no placebo word list").

**The gap, plainly.** The 407 markers were selected because they jumped
after 2022, then run backwards thirty years. Words that jumped post-2022
could disproportionately be words that were *already rising* — selection
on the endpoint of a trending series. The committed placebos match
frequency and dispersion but **not pre-period trend**, which is the one
dimension this objection travels through. Separately, the 30-year rise is
only ever shown as a pooled aggregate — no reader can see whether it is
broad (many words drifting) or narrow (a few words exploding).

**The evaluation.**
(a) *Per-word decomposition*: 1994–2026 slope for every marker; fraction
positive; the aggregate recomputed with the ten largest contributors
removed; a types-per-speech breadth series.
(b) *Trend-matched donors*: rebuild the placebo pool matched on frequency,
dispersion **and pre-2010 slope**; report the register series minus the
donor series (a difference-in-differences against selection).
(c) *The second marker set*: the study already holds the Wikipedia-control
set — test whether the 1994–96 onset appears on it too (currently the two
sets are only compared post-2023).
(d) For permeation: a donor word set matched on frequency decile, length
and part-of-speech, rescored through the committed pipeline — its missing
control.

**Outcomes.** Onset survives trend-matched donors and shows breadth → the
endogeneity objection is answered in its own coin, and "predates" gains
its strongest support. Donors show the same 1994 rise → the onset is
generic vocabulary drift and the claim rescopes to "the register rides a
broader drift the models then amplified" — a real finding, differently
framed.

**Effort.** Held data; (a)–(c) CPU only, 2–3 days; (d) needs GPU
rescoring, ~1–2 days more.

---

## 4. Post-training: from data claim to attribution (survey rec 2)

**The results concerned.** §4.7: base→instruct **+1.24** on the OLMo
ladder; SFT and DPO indistinguishable; **RLVR ≈ 0**; the cross-family
preference compile **+0.387**; and the abstract's sentence "installed by
the stages tuned toward human demonstrations and preferences, and not by
the stage tuned toward verifiable correctness."

**The gap, plainly.** On the OLMo/Tulu ladder, SFT and DPO train on chat
data while RLVR trains on math and code — so "the RLVR *objective* doesn't
install it" is confounded with "the RLVR *data* isn't chat." The sentence
as written is an objective claim; the design supports a data claim. And
the +1.24 is confounded with the chat template and decoding regime.

**The evaluation.**
(a) *Score the preference data itself*: register excess on chosen-vs-
rejected pairs in the public Tulu-3 preference mixture — within-pair
deltas, length-residualised. If the preference data prefers the register,
the mechanism is located in the data without any training run.
(b) *Length control*: truncate generations to common within-pair length
and re-run every stage delta.
(c) *Base-prompting arm* (URIAL-style): base model with a 3-shot stylistic
prefix vs instruct with and without template — what share of the +1.24 is
weights vs surface conditioning.

**Outcomes.** Preference pairs positive → upgrade: "the human-preference
data itself prefers the register" (a stronger and cleaner claim than the
stage attribution). Base-prompting recovers a large share → the +1.24
softens to a conditioning result, which the honest sentence absorbs.

**Effort.** Public data + inference on models already run; a few days.

---

## 5. Genre and scriptedness labels, panel-wide (survey rec 9)

**The results concerned.** Four at once: the prevalence spread and its
year comparison (§4.2), the 30-year register series and its 1994–96 onset
(§4.5), permeation's window contrasts (§4.8), and the flight test's
interpretation (status display vs drafting practice).

**The gap, plainly.** §4.3 shows a **3.29×** genre gradient — and genre is
labelled in exactly one of 22 chambers. Any rate compared across time,
chamber, or group is exposed to composition drift in the one dimension the
study has proven matters most.

**The evaluation.** Three tiers, cheapest first: (a) post-stratify each
chamber-year to a fixed segment-length distribution (a measurable proxy);
(b) parse order-of-business and debate-title headings from the raw
transcripts into a coarse 3–5-way rubric and reweight; (c) the scoped LLM
genre classifier (already registered as future-work item 12) over held
text. Then re-run: the 30-year series and onset under fixed composition;
the permeation contrast within genre; the chamber spread
direct-standardised; and the flight correlation split
scripted/unscripted — a discriminating test, since status display predicts
flight strongest in the most-monitored speech and drafting practice
predicts the opposite.

**Outcomes.** Series robust → the standing "informalization" rival and the
composition confound close together. Onset moves → major, honest rescope.
The flight split adjudicates between two readings the paper currently
cannot separate.

**Effort.** Held text; new labels. Tier (a) a day; (b) ~3 days; (c) an
LLM-classifier run over the corpus (compute spend, bounded).

---

## 6. Instrument breadth for the evasion and quality arms (survey rec 4)

**The results concerned.** §4.9: "**roughly one flagged speech in five**
can be walked past the detector" (19.4–22.5%), "**~10× the commercial
evasion baseline**", and every quality number's single-judge provenance.

**The gap, plainly.** One target detector (every accepted evasion paper
attacks 4–12); the 10× compares our measurement on our corpus against
Pangram's self-reported benchmarks on other corpora; and the attacker and
both graders are the same model family.

**The evaluation.** (a) Rescore all 341 variants + 71 originals with
Binoculars and Fast-DetectGPT (computable from held log-probs; a bench
script exists) plus one open supervised detector — a per-detector evasion
table and a transfer statement (did evading Pangram evade the others?).
(b) Run 2–4 commercial humanizers over the same 71 targets, scored by
Pangram — converts the 10× into a within-experiment ratio with an
interval. (c) Re-grade both quality pools with two non-Anthropic judges on
the frozen rubric; report headline contrasts as a range across judges.

**Outcomes.** Transfer high → the evasion claim generalises beyond one
vendor. Humanizers land near Pangram's tables → the 10× stands on our own
data. Judge range tight → the quality claims shed the family-circularity
objection.

**Effort.** ~$100–300 of subscriptions/API + ~1 week.

---

## 7. Known-α recovery and fraction calibration (survey rec 10, trimmed by held assets)

**The results concerned.** The headline **9.03%** — specifically two of
its joints: the pipeline has never been shown to recover a *known*
prevalence end-to-end, and the fraction-weighting (12.03% → 9.03%) rides
the vendor's `fraction_ai`, which has never been calibrated against known
mixtures.

**The gap, plainly.** The strongest comparator works all show an
estimator-recovery exhibit: seed a corpus at known α, run the unmodified
pipeline, plot α̂ against α. We show calibration of the *negative* class
(1,260/1,260) but nothing on recovery of a positive rate.

**The evaluation.** Build one synthetic asset and spend it twice:
machine speeches generated the way an office would prompt them, spliced
into pre-2022 control segments (your point stands and trims the work — the
study's known-authorship continuations already supply machine text for
part of this). (a) Pseudo-chambers at α ∈ {0, 2.5, 5, 10, 15, 20}%,
unmodified pipeline, α̂-vs-α curve with the 45° line. (b) ~400 segments
spliced at known word-fraction p; regress reported `fraction_ai` on true
p; re-report the headline under raw / calibrated / binary weightings.

**Outcomes.** Recovery clean → the 9.03% gains the exhibit its literature
leads with. Fraction mis-calibrated → the paper switches its headline
weighting with a stated correction — better now than in review.

**Effort.** Generation spend (low hundreds of dollars) + ~1 week.

---

## 8. GATED: the stage-2 human-comparator grading census

**The result concerned.** The composite-weighting check: factor-weighted
AI-vs-human contrast **+0.076 (t 1.71)** — direction survives,
significance doesn't — beside the equal-weight +0.195 (t 5.65).

**The evaluation.** Every Pangram hit is already graded; the margin is
human comparators (341 graded of 2,051 in the pool). Grade the remaining
~1,710 under the frozen rubric with the **census endpoint pre-committed**
(the whole pool — a principled stopping rule, not grade-until-significant).
Projected t at the current point estimate: ≈ 2.1.

**Outcomes.** Clears → the qualifying sentence reverts. Doesn't → the
current sentence was the true one. **Gated on your grading spend.**

---

## 9. GATED: the detector-side selection placebo (cheapest high-value quality test)

**The result concerned.** The entire quality arm's design: treatment =
Pangram verdict, outcome = textual form — and detectors key on form. If
Pangram preferentially flags well-formed text, the **justification +0.29**
could be partly selection, not machine assistance.

**The evaluation.** Grade the 1,260 pre-2022 controls (all human by
construction) on the frozen rubric; regress each DQI dimension on the
continuous Pangram and screen scores with genre and chamber fixed
effects. Any form–score association among pure humans is the selection
effect, measured; subtract it from the headline.

**Outcomes.** Null → the first objection every referee raises is
pre-answered. Positive → the honest correction is applied, sized. API
cost only (~1,260 gradings); no human time. **Gated on your grading
spend.**

---

## 10. GATED: the human DQI gold subsample

**The result concerned.** Every quality number in the paper is
LLM-judged; there is no human-coded DQI anywhere.

**The evaluation.** Two trained human coders, 150–200 segments,
stratified probability sample (verdict × genre × chamber) with logged
inclusion probabilities; then DSL/PPI re-estimation of the headline
contrasts on the surrogate labels — the standard correction for
LLM-labelled outcomes. The sampling rule must be a recorded random draw,
designed before grading.

**Why it can't be substituted.** This is the survey's one blocking gap
with no computational alternative: judge reliability statistics cannot
distinguish a consistent judge from a consistently biased one; only human
anchors can. **Gated on recruiting coders.**

---

*Also outstanding, from the blind review rather than the survey: CC6–CC11
(commit-the-script/refresh-the-number mechanics in the class sections,
including the stale crossover meta and the stale "+1.01 citable figure"),
awaiting rulings.*
