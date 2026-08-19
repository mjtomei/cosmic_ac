# B block — the bypass-arm findings of the 2026-08-11 adversarial review

*Self-contained review file for Matthew: apparatus context, then the review's
eight findings verbatim, then the paper text they target. **Status: none of
the B items has been adjudicated or independently verified yet** — the
verdict labels (CONFIRMED/PARTIAL) are the review's own; I will run
confirmations per item as you review, the same flow as the Q block.*

## The apparatus these refer to

The **bypass arm** asks how evadable the study's detection is under directed
effort. Flagged segments were rewritten by a frontier model with the explicit
goal of preserving content while clearing **Pangram** (the commercial AI-text
detector the study calibrates against); the study reports that the directed
search clears the detector on **8.5% of rewrite variants and 22.5% of
targets** (a target = an original flagged segment, attacked with multiple
variants), across **four runs over two days**. This is why the 9.0% headline
prevalence is presented as a floor. Supporting documents: draft §4.9 (the
"evadable under effort" half), `BYPASS_METHODOLOGY.md` (the arm's own methods
file), and per-run scripts. The eight findings below concern pooling across
the four runs, denominators, what "no detector access" means, in-sample
replication claims, power, and missing scripts.

---

## Part 1 — The review's findings, verbatim (REVIEW-2026-08-11.md §2.4, Bypass arm)

#### Bypass arm

**B1. The four runs do not share a common rate, and the pooling weight is endogenous.**
*PARTIAL.* Run rates 1/40 (2.5%), 29/212 (13.7%), 0/80 (0%), 9/129 (7.0%); Pearson χ² =
17.05 on 3 df, p = 0.0007. Each run's weight in the pool is the number of variants that
passed the Opus gate, and gate-passing measures how well the search went, so the most
successful search gets the largest weight. The unweighted mean of run rates is 5.8%, not
8.5%. *Accurate version:* heterogeneity is real and a Wilson interval on the mixture is not
a clean estimand — but none of it is hidden. The per-run rows are printed side by side in
both primary documents, `bypass_report.py` names the estimand descriptively, and the
write-up says the pooled figure "keeps two superseded searches in the denominator, including
the badly-seeded run that produced nothing". The proposed alternative is not obviously
better: the unweighted mean gives the 40-variant v2 row (per-target bests, 19 of 40 failing
the gate) equal weight to the 212-variant v3 row. And v3's larger share comes from a
protocol change, not from the search having gone well. *Fix:* report the four run rates and
the heterogeneity test; if one number is required, say it is a variant-weighted average
over four incomparable designs.

**B2. "No detector access of any kind" is false.** *PARTIAL.* The contrastive search —
responsible for 29 of 39 variant reversals and 10 of 16 target reversals — was built on
Pangram's own labels: its exemplars are, in the script's words, "the two highest-scoring
genuine Pangram-Human segments that still score BELOW it", and all 41 exemplars across the
three contrast files are labelled Human in `pangram_p4_verdicts.csv`. *Accurate version:*
Pangram's role is as a genuine-human *filter*, not a style oracle — the matching is entirely
on Opus (median gap 3 for NB, 10 for GO) — and given this study's own 0/1,260 specificity,
"Pangram says Human" among genuine Hansard is close to "is genuine human text", a property
obtainable without any detector (e.g. pre-2022 Hansard). The load-bearing threat-model claim
survives exactly: the search never queried the detector on the text it was attacking, no
gradients, no fine-tuning, tested on Pangram only at the end. *Reproduce:* cross-reference
every exemplar `seg_id` in `bypass_contrast.json`, `gov_contrast_all.json`,
`gov_contrast.json` against `pangram_p4_verdicts.csv`. *Fix:* "no query access to the
detector on the text under attack", plus one clause on the exemplar labels.

**B3. The effort paragraph switches the definition of success.** *CONFIRMED.* "The blind v2
search flipped 10% of variants; the contrastive v3 search 28%" are *moved-off-AI* rates
(Mixed or Human): 4/40 and 59/212. The comparable Human-reversal rates are 2.5% and 13.7%.
Placed three lines after the 8.5% headline and framed as "both rates move with effort", the
sentence invites a reader to take 28% as the per-variant reversal rate of the best search —
a 2× overstatement. "flip" occurs exactly once in the bypass section and is never defined
there, while the next sentence's "If 'soften off AI' rather than 'reach Human' is the bar"
actively implies the preceding numbers were on the reach-Human bar.
`BYPASS_METHODOLOGY.md`:84–91 itself warns the two are different events. *Mitigations:* the
numbers are correct under the term as defined in BYPASS_METHODOLOGY, the comparison is
internally like-for-like, and on the reach-Human definition the effort multiple is *larger*
(5.5× vs 2.8×). *Reproduce:* tabulate verdicts per run from `bypass_report.load()`. *Fix:*
state both quantities explicitly.

**B4. Each headline is computed on a different subset.** *PARTIAL.* 8.5% is all four runs;
24.6% is the final search per chamber only. The internally consistent alternatives are
final-two-run per-variant 11.1%, all-four per-target 12.3%, distinct-text 17.4%; on the
final two runs the gap between the two rates is 2.3×, not threefold. *Accurate version:*
"the asymmetry is not disclosed" does not hold — both subsets are named in the bold headings
themselves ("8.5% per variant, all four runs"; "24.6% per target, best method only") with
the rationale in the same sentences. And the charge of convenient subsetting is contradicted
where it can be tested: the one place the subsets are combined into a ratio is the "3.7×"
line, and the same-subset version is 11.1%/2.31% = **4.8×** — the study reported the number
that makes its own instrument look *worse*. *Fix:* print all four cells of the
(subset × estimand) table, and compute any single multiple on one subset.

**B5. Half the pooled per-target estimate is in-sample for the replication claim.**
*PARTIAL.* "This is the figure a fresh study replicating our best method should expect to
reproduce" is said of 24.6%, but v3's design was derived from watching v2 fail on the same
40 New Brunswick texts (`gov_bypass_all.js:15-35` lists three changes "each fixing a
measured defect", one justified by "All four Pangram flips observed so far came from
variants scoring under 34"). Only GO all-31 is a clean out-of-sample application.
*Accurate version:* none of the three changes is fitted per text — contrastive exemplars and
noise-aware early stopping are tuned on the Opus proxy, and keeping all sub-50 variants is a
submission-budget change a replicating study would also make. The empirical answer is in the
data: the clean out-of-sample run returns 22.2% against NB v3's 26.3% (19.4% vs 25.0%
corrected), which is not what overfitting looks like. Appendix C.4 already calls GO all-31
"an exploratory replication rather than an independent rate estimate". *Fix:* name GO
all-31 as the only out-of-sample estimate and quote it (19–22%, wide interval) as the
replication expectation; keep the pooled figure as a summary of what was achieved.

**B6. "The two chambers agree closely" is a comparison with no power.** *PARTIAL.* The
difference is 4.1pp with a 95% CI of [−16.9, +25.1]pp; the data are equally consistent with
the GO rate being half or double the NB rate. *Accurate version:* the concordance is
evidence about a question the pooled interval does not address — the interval quantifies
sampling error *under an assumed common rate*, and says nothing about whether one exists, so
the sentence is not double-counting. It is also paired with a genuinely independent point:
the two chambers' derived humanising hypotheses flatly contradict each other, which is what
makes "the rate transfers; the playbook does not" more than a restatement. *Fix:* soften
"more trustworthy than its interval suggests" to "consistent across two chambers, though
with intervals too wide to establish that they agree".

**B7. Two of the four runs and the band tables have no script.** *PARTIAL.*
`BYPASS_METHODOLOGY.md:5` says "Everything is reproducible from analysis/s10/". The New
Brunswick v2 and v3 search scripts are absent (only `gov_bypass_v3.js` and
`gov_bypass_all.js` exist), so the run contributing 29 of 39 variant reversals cannot be
re-executed or inspected for its gate parameters; and the contrast-pair builders that
produced `bypass_contrast.json` and `gov_contrast_all.json` exist nowhere. *Accurate
version:* the third sub-claim — that the band tables are unreproducible — is wrong, and it
is the one called "the entire basis of the organising hypothesis". The New Brunswick band
table regenerates exactly from stored artifacts in about ten lines (join `opus_orig3x` from
`pangram_bypass_key.json` onto `pangram_v3_key.json` and `bypass_v3_pangram.json`, then
band): 46/54/56/56 variants with flip 57%/30%/23%/7% and clean Human 43%/7%/9%/0%, every
cell to the digit. The missing-script gaps are also partly mitigated:
`BYPASS_METHODOLOGY.md:242-244` records that the GO script was copied from the NB script and
differs only in paths, seed count and one field name, verified by structural diff.
*Reproduce:* `ls *.js && grep -rl 'human_exemplars' . && grep -n 'band' bypass_report.py`.
*Fix:* commit the NB search scripts and the contrast-pair builders, or state in §4.9 and
C.4 that two of the four runs are documented by their outputs only; add the band computation
to `bypass_report.py`.

**B8. BYPASS_METHODOLOGY and the write-up disagree about the zero-success run.** *PARTIAL.*
BYPASS_METHODOLOGY calls "zero clean Human verdicts in 80 attempts at any band" the
"strongest single fact in the arm"; Appendix C.4 says the same run's "zero successes test
nothing about the band hypothesis". *Accurate version:* they are not opposite claims. The
methodology document says, in order, "This sample does not replicate the gradient" → "The
sample is range-restricted … A sample that cannot contain the effect cannot test it" → then
the narrower high-band claim. It concedes the write-up's point two sentences earlier. And
the write-up's blunt "test nothing" is the looser statement: against the arm's own 8.5%
pooled rate, 0 successes in 80 has probability 0.915^80 ≈ 0.0009, so the run does
discriminate the band hypothesis from a flat-rate alternative. *Sub-point that stands:* "80
attempts" is 80 gate-passing variants out of ~513 generated across 35 seeds, 10 of which
yielded nothing — the same denominator issue as **M12**. *Fix:* align the two passages and
state the 80 as 80 of ~513.

---

---

## Part 2 — The paper text under review: draft §4.9, verbatim
*(the bypass content lives in the same section as the quality arm; included in
the Q-block file too — repeated here so this file stands alone)*

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
