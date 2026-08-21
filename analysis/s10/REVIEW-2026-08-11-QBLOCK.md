# Q block — the quality-arm findings of the 2026-08-11 adversarial review

*This file is for Matthew's review. Below the status block is the ORIGINAL
consolidated presentation of all twelve Q items, extracted verbatim from the
session transcript (pre-compaction, 2026-08-17); each item was verified with
confirmatory runs before that presentation. Nothing in the verbatim section
has been edited.*

## Correction, 2026-08-19 (Matthew's catch)

The apparatus preamble below says "five gradings exist." That count was
correct **at review time** and is now stale: **stage 5** (successful-evasion
grading, pre-registered, all-null, 39 variants / 15 targets) was added
2026-08-16 — five days after the review — so there are now SIX gradings plus
the D.1 judge-leakage control. Stage 5 is fully recomputable
(`stage5_scores.json`, `workflows/stage5_grade.js` committed), so Q12's
"three of five cannot be recomputed" reads today as three of six.
METHODOLOGY §7 was two generations stale on all of this and was rewritten
2026-08-19; draft §4.9 was already current.

## Status as of 2026-08-19

| item | status |
|---|---|
| Q7 | **CLOSED** — `analyze_stage2.py` committed (6481d8d), reproduces the column |
| Q3, Q5, Q6, Q11 | disclosure edits, will be applied as described unless vetoed |
| **Q1** | **OPEN — ruling needed**: report the applicability collapse as its own finding? (recommended: yes, both claims) |
| **Q4 + Q10** | **OPEN — ruling needed**: units row + per-sd figures; pooled genre means 1.10/2.09? (recommended: fix both) |
| **Q9** | **OPEN — ruling needed**: drop the star on stage-1 respect-groups, carry the conjunct on stage 2? (recommended: yes) |
| **Q2 + Q8 + Q12** | **OPEN — ruling needed**: one schema fix (segment IDs + word counts + per-grade records) unblocks all three; then run the length control and speaker clustering? (recommended: fix + run) |

---

## FULL BRIEFS FOR THE OPEN ITEMS (added 2026-08-21; self-contained, no prior knowledge assumed)

### Q9 — one starred result fails multiple-testing correction

**Context, from zero.** One arm of the study asks whether machine-drafted
legislative speech is better or worse *quality* than the rest. Quality is
scored by an LLM judge against the Discourse Quality Index (DQI), a standard
political-science rubric with seven dimensions; the three that matter here
are *justification* (are arguments reasoned), *common_good* (appeals beyond
self-interest), and *respect_groups* (does the speaker say anything
explicitly positive about the people the policy under discussion would
help — scored 0/1/2). Two independent gradings exist: **stage 1** (840
segments from federal Canada, balanced across speech genres, regressed on a
0–100 "how machine-like" score from the study's own Opus-based screen, with
genre and era fixed effects) and **stage 2** (682 segments across all 22
chambers, regressed on the binary verdict of Pangram, a commercial AI-text
detector, with chamber fixed effects). The paper's headline is that
AI-flagged speech scores HIGHER on those three form dimensions in both
stages; the results table stars every cell whose |t| exceeds 1.96 — six
stars across the two stages.

**The problem.** Fourteen cells were tested (7 dimensions x 2 stages).
Testing many cells at the 1.96 bar means some stars arise by chance;
the standard repair is the Benjamini-Hochberg (BH) procedure, which adjusts
each cell's p-value for how many tests were run. Applying BH across all 14
cells: five of the six starred cells survive easily (q < 0.003). **The
sixth — stage-1 respect_groups, t 2.0 — fails, at q = 0.106.** It is the
weakest star and the only one that does not survive correction.

**Three independent strikes against the same cell, accumulated since the
review.** (1) The judge also reports its own guess at whether each text is
AI ("judge_ai"); re-running stage 1 with that guess controlled — a harsh
diagnostic, not an estimator — flips this one dimension's sign (+0.29 to
−0.14) while the other starred cells survive, so in stage 1 this cell
cannot be separated from the judge reading AI-likeness as warmth. (2) With
standard errors clustered on speaker (840 segments come from 418 speakers;
run 2026-08-20 after the grading records were recovered), the cell drops to
t 1.8 — below the 1.96 bar on its own. (3) In stage 6 (machine continuations
no human ever reviewed, graded blind), NO machine arm at any capability
tier scores elevated respect_groups — evidence that the wild lift on this
dimension comes from what members ask drafting tools for, and that the
judge does not award warmth to text it believes is machine.

**Why nothing is lost.** The same dimension is stage 2's STRONGEST cell:
+0.220 at t 6.1, q < 0.0001, on an independent segment pool with an
external label (Pangram decides what is AI, not the judge), surviving
speaker clustering (t 5.8) and completely length-free (+0.220 raw, +0.222
with a length control). The respect-groups conjunct of the headline is
already carried by better evidence.

**The decision.** Recommended: drop the star from stage-1 respect_groups,
add one sentence noting it fails BH and is quarantined in stage 1, and
attribute the conjunct to stage 2. Alternatives: keep the star with a BH
footnote (leaves a star the correction kills — a reviewer's free shot), or
drop the conjunct from the headline entirely (overkill: stage 2's version
is bulletproof).

### Q10 — two quoted "genre means" are actually era-subset cells

**Context, from zero.** In Canada's House of Commons, "SO31" (Standing
Order 31) statements are short prepared member statements — a genre. The
paper's genre argument says: machine drafting concentrates in SO31; SO31
happens to be the genre with the LOWEST justification scores; therefore,
pooled across genres, the machine-vs-human justification difference looks
like nothing, while within any single genre it is strongly positive (a
"suppression effect"). To make that point the draft quotes two numbers:
SO31's mean justification **1.14** against government business's **2.01**.

**The problem (confirmed by recomputation).** Those two numbers are not the
full-sample genre means — they are the means computed on the post-2023
subset only (1.136 and 2.014). The full-sample genre means are **1.096 and
2.089**. The mislabeling is real; the substance is untouched — the pooled
gap is WIDER, i.e., marginally more favourable to the paper's own argument,
and SO31 also carries the highest mean machine-score of any genre (17.9,
against 9.8 for oral questions and 11.6 for debate).

**The decision.** Quote the pooled figures, 1.10 vs 2.09, labelled as
full-sample genre means. Pure figure hygiene at zero risk: a referee
recomputing genre means from the released data gets the pooled numbers and
would otherwise flag the mismatch.

### Q11 — a docstring motivates a control with the wrong stage's numbers

**Context, from zero.** Stages 3 and 4 are paired designs: a flagged
segment against its own detector-evading rewrite, graded blind, 38 and 25
pairs — the test of whether the evasion edit changes quality (it does not,
on any dimension). The analysis script for these stages includes a
word-count covariate, and its docstring justifies it by saying the rewrites
run "~30 words longer at the median."

**The problem.** That fact belongs to stage 4, whose rewrites do run ~29
words longer. Stage 3's PAIRED length shift — the only thing a paired model
sees — is approximately zero: median +4 words, mean −1.3, with 42% of
rewrites shorter than their originals. The stated motivation describes the
wrong stage. The covariate itself is still worth keeping in stage 3 — not
against bias (there is no length shift to de-bias) but for PRECISION:
within-pair word counts vary a lot (sd ~38 words), and absorbing that noise
tightens the standard errors.

**The decision.** A one-line documentation fix: state that stage 3's paired
shift is ~0 and the covariate is retained for precision; the ~30-words
figure moves to stage 4 where it is true. No number changes anywhere.

---

## Part 1 — My verified summaries (from the session transcript, verbatim)

All confirmed. Here's the full Q block. **Shared context first**, since every item refers to the same apparatus.

**The quality arm** grades legislative speech against the **DQI** (Discourse Quality Index — Steenbergen et al. 2003), a deliberation rubric scoring seven dimensions: *justification*, *common_good*, *respect_groups*, *respect_demands*, *respect_counterargs*, *constructive*, *evidence*. Two of those can be **inapplicable** — you can't score "respect toward others' demands" if nobody made one — and are coded **−1** and excluded from means.

Five gradings exist. **Stage 1** (840 segments, federal Canada, genre-balanced) regresses DQI on the *Opus screen's continuous 0–100 score*. **Stage 2** (682 segments, cross-chamber) regresses on the *Pangram binary verdict* with chamber fixed effects. **Stages 3 and 4** are within-text paired designs (38 and 25 pairs) comparing a segment against its detector-evading rewrite. **Appendix C.1** is a cross-account reliability replication.

The headline: **AI-flagged speech is better-formed and shows no engagement penalty once genre or chamber is held fixed** — which retired the earlier "form up, deliberation down."

---

**Q1 — applicability is an outcome, and it moves.** *PARTIAL, but the substance is real.* Excluding the −1 cells conditions on something the treatment affects. **I measured it:** applicability collapses at high screen scores — respect_demands **61.4% → 63.0% → 31.1%** across ai<10 / 10–49 / ≥50, respect_counterargs **50.8% → 51.2% → 28.9%**. AI-flagged speech is about **half as likely to contain anything to engage with**. The review's own adjudication notes the composite coding (−1 = 0) is null in all four cells, so the *total* engagement effect is still zero — but that's a different claim. **Fix:** report P(applicable) by condition, and distinguish "engages worse when there is something to engage" (null) from "less likely to have anything to engage with" (not null).

**Q2 — stage-2 length imbalance, uncontrolled.** *PARTIAL.* AI/Mixed segments run +29.4 words longer within chamber (t +5.4), and length predicts justification, so it could account for ~half the +0.290. **I verified the blocker:** `results_stage2.json` has no `n_words` and no segment id, so the control **cannot be run at all**. Note length is plausibly a *channel* rather than a confound — longer speeches having more room to justify is part of "better-formed" — and respect_groups, the strongest conjunct (t +6.1), has a length slope of −0.018, so at least one conjunct isn't length. **Fix:** report the imbalance, name length as a channel, add segment ids.

**Q3 — the paired nulls are underpowered.** *PARTIAL.* Stages 3/4 can only exclude effects of 0.12–0.26 (stage 3) and 0.59–1.00 (stage 4's adjusted column). Twenty-eight tests, no multiplicity note. But the review concedes its MDEs are reconstructed from a rounded cache, gets one scale wrong, and the imprecision is mostly M2's already-retired length-adjustment artifact. Also: for a *null*, multiplicity cuts the other way — 0 of 28 significant is harder without correction. **Fix:** state what the paired arms can and cannot exclude; don't lean on stage 4's adjusted column.

**Q4 — stage 1 and stage 2 aren't the same quantity.** *PARTIAL.* **Verified:** the stage-1 regressor is the screen's 0–100 score, but its observed max is **70**, sd **15.3**, IQR **18**, with **59% of values below 10**. So +1.134 is a fitted 0→100 difference on a variable that never reaches 100. Rescaled: **+0.173 per sd, +0.204 per IQR** — right next to stage 2's binary +0.290. The 4× ratio in the table is a units artifact. The text never claims a magnitude difference, but the table invites one. **Fix:** units row plus per-sd figures.

**Q5 — reliability presented as validity.** *PARTIAL, mostly refuted.* Three sub-claims; the adjudicator kills two — the Spearmans are compared to the *human inter-coder* bar of 0.716, which all seven exceed, and the "anomalously low" evidence cites the wrong transcripts. What survives is real though: same-model cross-account agreement is **reliability**, and a judge that reads AI register as justification would reproduce perfectly, so high self-agreement is *predicted by* the leakage hypothesis. **Fix:** one sentence — qualify §8.3's "quality assessment is orthogonal to provenance."

**Q6 — the self-contradiction argument rests on n = 5.** *PARTIAL.* **Verified:** the candidate gap is **−0.356, Welch t −1.47, n = 20 vs 32**; the uniform gap rests on 5 applicable AI segments. Two noisy nulls disagreeing in sign is the expected outcome, not proof of instrument failure — and the write-up ranks it *first* among three observations. The retirement of "deliberation down" is carried by the genre control, which is sound. **Fix:** give n and t; don't rank this above the genre control.

**Q7 — the stage-2 column has no committed script.** *PARTIAL, but a convention violation.* No `.py` in `quality_expansion/` puts chamber in a design matrix, and the documented command produces different numbers. The specification *is* stated in words and reproduces from that sentence, and dropping Mixed barely moves it (+0.263/+0.283/+0.231) — but this breaks the study's **one-script-per-claim** rule, the same class of defect as L1 and L9. **Fix:** add a `--chamber-fe` path; state the Mixed coding at the table.

**Q8 — SEs aren't clustered on speaker.** *PARTIAL.* HC1 is correctly implemented but has no cluster dimension. Stage 1 draws 840 segments from 418 speakers; a design effect of 1.2–1.4 would take stage-1 respect_groups (t 2.01) below significance. Stage 2 is nearly inert (mean cluster 1.28). **Blocked by the same missing segment id as Q2.**

**Q9 — stage-1 respect_groups fails multiplicity.** ***CONFIRMED, and I reproduced it exactly.*** Benjamini-Hochberg across all 14 reported cells:

| cell | t | q |
|---|---|---|
| s2 respect_groups | 6.1 | 0.0000 |
| s2 common_good | 4.5 | 0.0000 |
| s2 justification | 4.4 | 0.0001 |
| s1 justification | 4.1 | 0.0001 |
| s1 common_good | 3.3 | 0.0027 |
| **s1 respect_groups** | **2.0** | **0.106 — fails** |

It's the only nominally-significant cell that fails, and it's also the one that flips sign under the judge_ai control (+0.29 → −0.14). **Fix is clean rather than costly:** drop the star and attribute the conjunct to **stage 2**, where the same dimension is the strongest cell in the table (t +6.1, q < 0.0001) on an independent pool with an external label.

**Q10 — two "genre means" are era cells.** ***CONFIRMED.*** **Verified:** the draft's 1.14 vs 2.01 are the **post-era** cells (1.136, 2.014). Pooled they're **1.096 vs 2.089** — marginally *more* favourable to the argument. The substantive point holds: SO31 is the lowest-justification genre and carries the highest mean screen score (**17.9** vs OQ 9.8, DEBATE 11.6). **Fix:** quote 1.10 vs 2.09.

**Q11 — the stage-3 length motivation describes stage 4.** *PARTIAL.* The docstring's "~30 words longer at the median" is true of group medians but the *paired* shift — the only thing the model uses — is ~0 (median +4, mean −1.3, 42% shorter). That figure belongs to stage 4. The covariate is still warranted, for **precision** (within-pair sd is 37.9 words). **Fix:** say the paired shift is ~0 and the covariate is there for precision.

**Q12 — three of five gradings can't be recomputed.** ***CONFIRMED.*** Stages 3/4 survive only as a rounded summary; Appendix C.1 has no cached output, so footnote r49b's reproduce line **cannot be executed**. The review's own headline overstates ("none of the five") — stages 1 and 2 do cache per-segment grades. **Fix:** commit per-grade records for all five stages.

---

**One consolidation worth acting on:** **Q2, Q8 and Q12 are the same defect** — the results files lack segment ids and word counts. Adding those two fields unblocks the length control, the speaker clustering, and the reproducibility gap in one change rather than three.

**And the honest count:** two CONFIRMED with real content (Q9, Q12), one CONFIRMED and trivial (Q10), Q1 substantive despite being PARTIAL, and the rest disclosure or units. Q9 is the only one that removes a claim — and it survives, just carried by better evidence.

---

## Part 2 — The review's own findings, verbatim (REVIEW-2026-08-11.md §2.4, Quality / DQI arm)


#### Quality / DQI arm

**Q1. Applicability is an outcome, it moves with AI status after the fixed effects, and it
is never reported.** *PARTIAL.* Two dimensions carry a −1 inapplicable code excluded from
means. With genre and era FE, P(respect_demands applicable) falls −0.492 per unit screen
score (t −3.6) and P(respect_counterargs applicable) −0.319 (t −2.3); with chamber FE,
stage-2 respect_demands applicability is −0.141 (t −3.9) for AI/Mixed. That is the monologic
property the exclusion rule was written to avoid "manufacturing", and it survives the
control that retired "deliberation down". Excluding −1 conditions on a post-treatment
variable and drops 40–50% of stage-1 rows. `analyze.py`'s own comment says the
applicable-rate "is reported instead"; no script or table reports it. *Accurate version:*
the composite coding (−1 = 0) is null in all four cells (stage 1 −0.272 t −1.6 and −0.251
t −1.2; stage 2 −0.094 t −1.6 and +0.009 t +0.1), so the *total* engagement effect is
indistinguishable from zero after genre or chamber — which is what the write-up claims. The
headline applicability coefficients also carry Q4's unit problem (−0.492 is per 100 points
of a 1–70 regressor, i.e. −7.5pp per sd); only the stage-2 −0.141 is on a binary contrast.
The exclusion rule is the original run's documented convention, not an ad-hoc choice.
*Fix:* report P(applicable) by condition with FE, add the composite row as a sensitivity,
and distinguish "engages worse when there is something to engage" (null) from "is less
likely to have anything to engage with".

**Q2. Stage 2 has a large unreported length imbalance and no length control.** *PARTIAL.*
AI/Mixed segments run +29.4 words longer than Human within chamber (t +5.4). The
length-quality slope on this study's own 241-segment v2 pool with group FE is +0.481
justification points per 100 words (t +7.0) and +0.204 common_good, so the imbalance could
account for about half the reported +0.290 justification effect. It cannot be tested
because `results_stage2.json` carries no segment id and no word count. *Accurate version:*
length is plausibly a *channel* of the treatment (AI drafting producing longer speeches is
part of "better-formed"), and the study's claim is descriptive, so conditioning on it would
answer a different question. The alleged inconsistency with stages 3/4 is not one — those
are within-text paired designs. The transported slope is an upper bound: the v2 pool has no
genre field, so it is uncontrolled for the variation driving both length and justification.
And respect_groups, the strongest stage-2 conjunct at t +6.1, has a length slope of −0.018
(t −0.5), so at least one conjunct cannot be length. *Fix:* report the +29-word imbalance
and name length as a plausible channel; add the segment id to the results files so the
control can be run at all.

**Q3. The stage-3/4 null is underpowered where it matters most.** *PARTIAL.* MDEs (80%
power, two-sided .05) back-solved from the cached estimate/t pairs: stage 3's five
non-sentinel dimensions are informative at 0.12–0.26; stage 3's two sentinel dimensions
(n = 12) are 0.38–0.59; stage 4's *quoted* column is 0.59–0.68 for justification, 0.59–1.00
for common_good, 0.93–1.57 for evidence. Twenty-eight tests with no multiplicity note.
*Accurate version:* the MDEs are reconstructed from a cache rounded to 2–3 dp with t to 1
dp, yielding ranges as wide as [0.93, 1.57] and leaving four cells unidentified; the scale
column is wrong for two cells (`dqi_judge_v2b.js` sets respect_counterargs to max 3, not 2);
and the imprecision is entirely M2's length-adjustment artifact — stage 4's *raw* MDEs are
0.19–0.36 and the raw column is in the artifact, so this partly double-counts M2. The
multiplicity complaint also cuts the wrong way for a null: 0 of 28 cells significant is
harder to obtain without correction, not easier. *Fix:* state what effect sizes the paired
arms can and cannot exclude, and do not lean on stage 4's adjusted column for a
"nothing here" claim.

**Q4. Stage-1 and stage-2 coefficients are not the same kind of quantity.** *PARTIAL.*
Stage 1 regresses on the screen's continuous 0–100 `ai_guess`/100, so +1.134 is the fitted
difference between ai_guess = 0 and 100 on a variable whose observed maximum is 70, sd 15.3,
with 59% of values below 10. Per sd it is +0.173; over the IQR +0.204. Stage 2's +0.290 is a
binary contrast. Presented in one table with no units row, the 4× ratio reads as a
substantive difference. *Accurate version:* the mechanics are right and the fix is a units
row, but the finding supplies the misreadings and then attributes them — the write-up's
claim at that table is "Different populations, different label sources, same answer", which
is about agreement in direction and significance pattern, not magnitude. Nowhere does the
study call the federal effect four times larger or read +1.134 as 38% of the scale. *Fix:*
report per-sd or per-IQR effects, add a units row, give the observed range in the caption.

**Q5. Appendix C.1 reports test-retest reliability and §8.3 converts it into validity.**
*PARTIAL.* Three sub-claims. (a) Five of the seven Spearmans (0.781–0.923) fall *inside*
the stated 0.68–0.91 band rather than above it. (b) The 0.30 "shifted" flag is larger than
every stage-2 effect it is being used to protect. (c) Same-model cross-account agreement is
reliability; a judge that reads AI register as DQI justification reproduces perfectly, so
high self-agreement is *predicted by* the leakage hypothesis. *Accurate version:* (a) is
refuted — "at or above" means inside or above, which is `compare_replication.py`'s own
criterion, and §8.3's comparison is to the *human inter-coder* bar of r = 0.716, which all
seven values exceed. (b) is weakened — the 0.30 flag is a coarse check on group *levels*,
and C.1 separately reports the sign test (12/14 gaps keep sign, including every
claim-bearing one) and the per-segment Spearmans. (c) is real but disclosed in §5.
Additionally, the two 2026-07-31 transcripts offered as evidence that the cross-account run
is anomalously low do not support it: `wf_0aa63dc2` is the run that *produced*
`fable_judge_v2_scores.csv`, so its 0.94–0.98 is self-comparison, and `wf_e2fe0a4b` is the
retired 6-dimension paraphrase. *Fix:* one sentence — cut or qualify §8.3's "quality
assessment is orthogonal to provenance", which sits in tension with §4.9's own gaps. See
**X4**.

**Q6. The self-contradiction argument, ranked first, rests on n = 5.** *PARTIAL.* Both gaps
reproduce (cand −0.356, uniform +0.650) and neither is distinguishable from zero: the
+0.650 rests on 5 applicable AI segments against 60 (Welch t = +1.30); the −0.356 is
t = −1.47 on 20 vs 32. Two noisy nulls disagreeing in sign is the expected outcome, not
evidence of instrument failure, and neither n nor t appears in the write-up. *Accurate
version:* the write-up's assertion is literally true and the inference drawn is the modest
one — the two pairs *did* disagree in sign, and the point is the fragility of the original
finding, which two mutually-opposed nulls demonstrate. It is also explicitly corroborative:
the retirement of "deliberation down" is carried by the genre control, which the finding
concedes is sound. *Reproduce:* recompute both gaps and Welch t from
`fable_judge_v2_scores.csv`. *Fix:* give n and t for both gaps and do not rank the
observation above the genre control.

**Q7. The stage-2 column has no committed script and an undisclosed coding.** *PARTIAL.* No
`.py` in `quality_expansion/` puts chamber in a design matrix; the documented command
(`python analyze.py --key key2.json`) regresses on the *screen's* ai_guess and produces
different numbers. The published column is recoverable only under "AI or Mixed = 1,
Human = 0" with 21 chamber dummies. Mixed pooling is stated once in §5 and never at the
table. *Accurate version:* the traceability defect is real and is a violation of the
study's one-script-per-claim convention, but three specifics are wrong: the specification
*is* stated in words at the table ("labelled by Pangram verdict, with chamber fixed
effects"), and reproduces exactly from that sentence alone; `key2.json` does carry genre for
the 82 federal-Canadian rows, so the claim that all fixed effects collapse to nothing is
false; and the quoted alternative numbers do not reproduce. Dropping Mixed gives +0.263 /
+0.283 / +0.231, so the substance is unaffected. *Fix:* add a `--chamber-fe` path or a
stage-2 script, note it in Appendix C.5, and state the Mixed coding at the table with the
drop-Mixed sensitivity.

**Q8. Standard errors are not clustered on speaker.** *PARTIAL.* HC1 is correctly
implemented (validated to 1.1e-15 against a numpy reference) but has no cluster dimension.
Stage 1 draws 840 segments from 418 speakers with 26% from speakers contributing ≥ 5; a
design effect of 1.2–1.4 takes stage-1 respect_groups (t = 2.01) below significance. It
cannot be recomputed because the results files omit the segment id. *Accurate version:*
stage 2 draws 682 from 532 speakers (mean cluster 1.28, only 1.6% from speakers with ≥ 5),
so clustering is nearly inert there — and all three headline conjuncts replicate in stage 2
at t +4.4, +4.5 and +6.1. The only reachable cell is stage-1 respect_groups, which is
carried by stage 2. *Fix:* add the segment id to the results files and report
speaker-clustered SEs alongside HC1.

**Q9. Stage-1 respect_groups does not survive multiplicity.** *CONFIRMED.* Fourteen
coefficients are reported and starred at nominal .05 with no adjustment. Benjamini-Hochberg
across the 14 leaves five of the six nominally significant cells at q ≤ 0.0031 and puts
stage-1 respect_groups at q = 0.104. It is also the cell that flips sign under the
judge_ai control. *Reproduce:* exact two-sided normal p-values and BH q-values for all 14
cells (`/tmp/s10_quality_review.py` section H). *Fix:* drop the star and attribute the
conjunct to stage 2, where it is the strongest cell in the table (t +6.1, q < 0.0001) on an
independent pool with an external label.

**Q10. Two "genre means" are era cells.** *CONFIRMED.* §4.9 line 447 says "SO31 has the
lowest justification of any genre (1.14, against 2.01 for government business)". 1.136 and
2.014 are the *post-era* cells; the genre means pooled over era are 1.096 and 2.089. The
substantive point is unaffected — SO31 really is the lowest-justification genre and carries
the highest mean screen score (17.9 vs 9.8 and 11.6) — and the pooled figures are marginally
*more* favourable to the argument. *Reproduce:* mean `justification` by genre and by
(genre, era) from `results_stage1.json`. *Fix:* quote 1.10 against 2.09, or label the
figures as the 2025–26 cells.

**Q11. The stage-3 length motivation is a difference of medians.** *PARTIAL.*
`analyze_stage3.py`'s docstring says "Humanized versions run ~30 words longer at the median
(200 vs 168)"; the *paired* difference — the only quantity the model uses — has median +4
and mean −1.3, with 42% of pairs shorter after rewriting. The claim is true of stage 4
(paired median +24, mean +29) and was imported into the stage-3 docstring. *Accurate
version:* the docstring is not false (the group medians really are 168 and 200, "at the
median"), and the conclusion drawn from the nuance fails: adjusted and raw do *not* agree on
every stage-3 dimension (respect_demands −0.08 vs −0.144; respect_counterargs +0.33 t 1.8 vs
+0.236 t 1.3), and within-pair length varies with sd 37.9 words, which is the variation
identifying the slope and which tightens stage-3 evidence MDEs from 0.19–0.25 to 0.15–0.20.
The covariate is warranted in stage 3 for precision. *Fix:* say the paired shift is ~0 and
that the covariate is there for precision, not to correct a mean imbalance.

**Q12. Three of the five gradings cannot be recomputed from the repository.** *CONFIRMED.*
No workflow directory on this machine (all 129 searched, using both `analyze.py`'s and
`analyze_stage3.py`'s own harvest functions) contains H-, G-, Q- or R-prefixed grades.
Stages 3/4 survive only as the rounded summary in `results_stage34.json` (2–3 dp estimates,
1 dp t, several cells with t = 0.0 or 0.1 leaving the SE unidentifiable); Appendix C.1's
cross-account run has no cached output at all, so its table is unverifiable, and footnote
r49b's reproduce line cannot be executed. *Two corrections:* the finding's own headline
("none of the five") is contradicted three sentences later — stages 1 and 2 cache
per-segment grades and reproduce exactly — and the 2026-07-31 transcripts it characterises
as an independent pass are not (see Q5). *Fix:* commit the per-grade records for all five
stages (id, condition, seven scores, ai_guess, n_words), as `results_stage1/2.json` nearly
does, and add the segment id to the stage-1/2 files.

---

---

## Part 3 — The paper text under review: draft §4.9, verbatim


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
3. **The two independent AI-guesses correlate** (screen vs grading judge,
   r = +0.758) — a shared style signal across two different models, which is a
   caveat on reading either judge's `ai_guess` as ground truth, not on the DQI
   scores. Its bearing on the quality claim is tested in Appendix D and does
   not overturn the external-label result; the genre/era fixed effects in the
   table above control confounds between cells, which is a separate matter from
   leakage within a text.

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
