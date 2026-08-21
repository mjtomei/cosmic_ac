# B block — the bypass-arm findings of the 2026-08-11 adversarial review

This file collects the eight bypass-arm findings (B1–B8) from the 2026-08-11
independent adversarial review of S10, rewritten so that **each item stands
entirely on its own**. A reader who has never seen the paper, the review, or
the study's data can read any single section below and understand what the
apparatus is, what the paper currently says, what the review objected to, what
has changed since the review ran, and what decision is open — without opening
any other file. Context is deliberately repeated across items so that no
section depends on another. **Status: none of the eight items has been
adjudicated or independently verified.** The CONFIRMED/PARTIAL labels inside
each finding are the review's own verdicts, not rulings; the review ran on the
2026-08-11 draft and the draft has been edited since (most consequentially the
M4 per-target-denominator fix of 2026-08-12 and the M12 per-detector-submission
reframe of 2026-08-16), so each item carries a staleness note.

## Status table

| item | one-line summary | review's label | status |
|---|---|---|---|
| **B1** | The four runs have significantly different flip rates, and the pool weights each run by how well its search went | PARTIAL | unadjudicated |
| **B2** | "No detector access of any kind" is literally false — the contrastive search used Pangram's own Human labels to pick exemplars | PARTIAL | unadjudicated |
| **B3** | The effort paragraph reports moved-off-AI rates (10%/28%) three lines after a reach-Human headline, inviting a 2× misread | CONFIRMED | unadjudicated |
| **B4** | The per-variant and per-target headlines are computed on different subsets of runs | PARTIAL | unadjudicated (partly stale: targets figure moved 24.6%→22.5% at M4) |
| **B5** | The per-target replication claim is made partly in-sample (v3's design was tuned on the same NB texts it is scored on) | PARTIAL | unadjudicated (figures moved at M4) |
| **B6** | "The two chambers agree closely" is a comparison the data have no power to make | PARTIAL | unadjudicated (largely moot: the "more trustworthy" sentence was deleted at M4) |
| **B7** | Two of the four run scripts and the contrast-pair builders are not in the repository | PARTIAL | unadjudicated (the pinned methodology quote does not exist in the file) |
| **B8** | The methodology file and Appendix C.4 appear to disagree about the zero-success run | PARTIAL | unadjudicated |

---

## B1 — The four runs do not share a common rate, and the pooling weight is endogenous

**Context, from zero:** The *bypass arm* of S10 measures how easily the study's
AI-text detection can be defeated by a determined author. The detector is
**Pangram**, a commercial AI-text detector that returns a categorical verdict —
**Human**, **Mixed**, or **AI** — with an underlying continuous `fraction_ai`
score (0.0 = fully human). A *target* (or *original*) is a real legislative
segment that Pangram flagged as machine-written; a *variant* is one rewrite of
a target produced by **Opus** (the frontier model used as the rewriter) and
then submitted to Pangram; a *run* (or *search*) is one search campaign that
generates variants over up to six rounds, keeping the best. The arm has **four
runs across two chambers** — the New Brunswick provincial legislature and the
federal Government Orders corpus: **NB v2 blind** (40 variants), **NB v3
contrastive** (212 variants), **GO Opus-selected** (80 variants), and **GO
all-31 uniform** (129 variants). The paper *pools* all four and reports that
**8.5% of variants (39 of 461)** reach a clean Human verdict. B1 asks whether
pooling four dissimilar runs into one 8.5% rate is legitimate, given that the
runs have visibly different success rates and that each run's weight in the pool
is the number of variants it happened to submit.

**The paper text under challenge (current):** The per-variant table and its
gloss, `S10-WRITEUP-DRAFT.md`:1565–1577:

> | | variants | Pangram says Human | `fraction_ai = 0.0` |
> |---|---|---|---|
> | NB v2 blind search | 40 | 1 | 1 |
> | NB v3 contrastive | 212 | 29 | 29 |
> | GO Opus-selected | 80 | 0 | 0 |
> | GO all-31 uniform | 129 | 9 | 7 |
> | **pooled** | **461** | **39 = 8.5%** [4.0, 13.4] | **37 = 8.0%** [3.6, 12.9] |
>
> Restricted to unambiguously AI-seeded originals the rate is unchanged: 34/400
> = 8.5% [3.5, 14.2] by label, 32/400 = 8.0% strict. This is the right number
> when the claim is about the *detector*, and it is deliberately harsh on
> ourselves: it keeps two superseded searches in the denominator, including the
> badly-seeded run that produced nothing.

The methodology file makes the same point, `BYPASS_METHODOLOGY.md`:335–336:

> The GO Opus-selected run stays in the pool despite being the badly-seeded one.
> Dropping a run *because* it produced no successes would inflate the rate.

**The review's finding (verbatim):**

> **B1. The four runs do not share a common rate, and the pooling weight is endogenous.**
> *PARTIAL.* Run rates 1/40 (2.5%), 29/212 (13.7%), 0/80 (0%), 9/129 (7.0%); Pearson χ² =
> 17.05 on 3 df, p = 0.0007. Each run's weight in the pool is the number of variants that
> passed the Opus gate, and gate-passing measures how well the search went, so the most
> successful search gets the largest weight. The unweighted mean of run rates is 5.8%, not
> 8.5%. *Accurate version:* heterogeneity is real and a Wilson interval on the mixture is not
> a clean estimand — but none of it is hidden. The per-run rows are printed side by side in
> both primary documents, `bypass_report.py` names the estimand descriptively, and the
> write-up says the pooled figure "keeps two superseded searches in the denominator, including
> the badly-seeded run that produced nothing". The proposed alternative is not obviously
> better: the unweighted mean gives the 40-variant v2 row (per-target bests, 19 of 40 failing
> the gate) equal weight to the 212-variant v3 row. And v3's larger share comes from a
> protocol change, not from the search having gone well. *Fix:* report the four run rates and
> the heterogeneity test; if one number is required, say it is a variant-weighted average
> over four incomparable designs.

**Status and staleness:** Not stale. The four per-run rows the review cites
(1/40, 29/212, 0/80, 9/129) match the current table digit-for-digit, and the
"keeps two superseded searches in the denominator, including the badly-seeded
run that produced nothing" sentence the review quotes approvingly is still
present verbatim at line 1577. No part is marked resolved in the review file.
The χ² = 17.05 (p = 0.0007) heterogeneity statistic and the 5.8% unweighted
mean are the review's own computations; they are **not yet independently
verified** and the review supplies no read-only reproduce command for them.

**The decision to make:** The review proposes reporting all four run rates plus
the heterogeneity test, and — if a single number is required — labelling 8.5% a
"variant-weighted average over four incomparable designs" rather than an
estimate of a common rate. The obvious alternative it raises and then rejects
is quoting the unweighted mean of run rates (5.8%), which it judges no better
because it would give the 40-variant v2 row equal weight to the 212-variant v3
row.

---

## B2 — "No detector access of any kind" is false

**Context, from zero:** The *bypass arm* of S10 tests how easily the study's
detector can be evaded. The detector is **Pangram**, a commercial AI-text
detector returning Human / Mixed / AI verdicts. An author's rewrites (called
*variants*) of a flagged segment (a *target*) are produced by **Opus**, a
frontier model, and only checked against Pangram at the end. A central selling
point of the arm is its *threat model*: the attack never queries the detector
while building its rewrites — it optimises against Opus's own opinion of the
text and submits to Pangram only to score the result — which is what makes the
evasion rate a clean lower bound on what a real adversary could do. The most
productive of the four runs, **NB v3 contrastive** (responsible for 29 of the
39 variant reversals), works by giving Opus *contrastive exemplars*: pairs of
real human Hansard segments matched to the target so Opus can see what
"human-sounding" looks like. B2 observes that those exemplars were themselves
chosen using Pangram's labels, so the blanket phrase "no detector access of any
kind" is literally untrue.

**The paper text under challenge (current):** `S10-WRITEUP-DRAFT.md`:1527, in
the headline paragraph:

> No fine-tuning, no detector access, no evasion tooling — Opus, a rewrite
> prompt, and six rounds of keep-the-best.

And the generalised restatement in §8.1, `S10-WRITEUP-DRAFT.md`:2106–2109:

> The search never queried the detector it was evading: it optimised against an
> Opus proxy, tested on Pangram only at the end, used roughly eighteen attempts
> per target, and involved no fine-tuning, no gradients, and no detector access
> of any kind.

The exemplar-selection rule the review quotes lives in the run script,
`gov_bypass_all.js`:20–23:

> Exemplars here are REAL Hansard: for each seed, the two highest-scoring
> genuine Pangram-Human segments that still score BELOW it (median gap 3
> points).

**The review's finding (verbatim):**

> **B2. "No detector access of any kind" is false.** *PARTIAL.* The contrastive search —
> responsible for 29 of 39 variant reversals and 10 of 16 target reversals — was built on
> Pangram's own labels: its exemplars are, in the script's words, "the two highest-scoring
> genuine Pangram-Human segments that still score BELOW it", and all 41 exemplars across the
> three contrast files are labelled Human in `pangram_p4_verdicts.csv`. *Accurate version:*
> Pangram's role is as a genuine-human *filter*, not a style oracle — the matching is entirely
> on Opus (median gap 3 for NB, 10 for GO) — and given this study's own 0/1,260 specificity,
> "Pangram says Human" among genuine Hansard is close to "is genuine human text", a property
> obtainable without any detector (e.g. pre-2022 Hansard). The load-bearing threat-model claim
> survives exactly: the search never queried the detector on the text it was attacking, no
> gradients, no fine-tuning, tested on Pangram only at the end. *Reproduce:* cross-reference
> every exemplar `seg_id` in `bypass_contrast.json`, `gov_contrast_all.json`,
> `gov_contrast.json` against `pangram_p4_verdicts.csv`. *Fix:* "no query access to the
> detector on the text under attack", plus one clause on the exemplar labels.

**Status and staleness:** Not stale. Both quoted paper phrases still stand —
"no detector access" at line 1527 and "no detector access of any kind" at line
2109 — and the exemplar rule the review quotes is present in `gov_bypass_all.js`
at lines 20–23. The three contrast files (`bypass_contrast.json`,
`gov_contrast_all.json`, `gov_contrast.json`) and `pangram_p4_verdicts.csv` all
exist in the directory. The review's cross-reference of exemplar `seg_id`s to
their Pangram labels is **not yet independently verified**; the review gives a
reproduce recipe (cross-referencing the four files) but running it is out of
scope here. No part is marked resolved.

**The decision to make:** The review proposes narrowing the phrase to "no query
access to the detector on the text under attack" and adding one clause
disclosing that the contrastive exemplars were filtered on Pangram's Human
labels. It notes the threat-model claim itself is unaffected, and that the same
human-only exemplar set is obtainable with no detector at all (e.g. pre-2022
Hansard), so the fix is a wording correction rather than a substantive
retraction.

---

## B3 — The effort paragraph switches the definition of success

**Context, from zero:** The *bypass arm* of S10 rewrites flagged legislative
segments with **Opus** (a frontier model) to defeat **Pangram** (a commercial
AI-text detector that returns Human / Mixed / AI verdicts). Two different
"success" events recur in the arm and are easy to conflate. A **flip** (or
"moved off AI") is a variant leaving the AI verdict for *either* Mixed or Human
— a weak success. A **reversal** (or "reach Human") is the stricter event of a
variant reaching a clean Human verdict — the study's actual headline event, and
the one the 8.5%-of-variants / 22.5%-of-targets figures count. Because a
Mixed-seeded text can reach Mixed without ever having been AI, and because
"soften off AI" is a lower bar than "reach Human", the two rates differ by
roughly 2×. B3 concerns a paragraph that reports the *flip* rates (10% and 28%)
immediately after the *reach-Human* headline, without flagging that it has
switched bars.

**The paper text under challenge (current):** `S10-WRITEUP-DRAFT.md`:1678–1682:

> **Both rates move with effort, and that is the real caveat on each.** The
> blind v2 search flipped 10% of variants; the contrastive v3 search 28%. If
> "soften off AI" rather than "reach Human" is the bar, 17 of 38 New Brunswick
> targets (45%) cleared it. So 8.5% and 22.5% bound what two days and four
> searches achieved, not what is achievable.

The methodology file itself warns the two events are different,
`BYPASS_METHODOLOGY.md`:85–91:

> **Terminology, since it is where the overclaim came from.** For an AI-only
> seed set, "flip" is well defined: the variant moved off AI. … The moment
> Mixed seeds enter, "flip" stops being well defined — moving off Mixed can
> mean getting *worse*. Across mixed seed types the only comparable outcome is
> reaching **Human**, and every cross-seed number must use it.

**The review's finding (verbatim):**

> **B3. The effort paragraph switches the definition of success.** *CONFIRMED.* "The blind v2
> search flipped 10% of variants; the contrastive v3 search 28%" are *moved-off-AI* rates
> (Mixed or Human): 4/40 and 59/212. The comparable Human-reversal rates are 2.5% and 13.7%.
> Placed three lines after the 8.5% headline and framed as "both rates move with effort", the
> sentence invites a reader to take 28% as the per-variant reversal rate of the best search —
> a 2× overstatement. "flip" occurs exactly once in the bypass section and is never defined
> there, while the next sentence's "If 'soften off AI' rather than 'reach Human' is the bar"
> actively implies the preceding numbers were on the reach-Human bar.
> `BYPASS_METHODOLOGY.md`:84–91 itself warns the two are different events. *Mitigations:* the
> numbers are correct under the term as defined in BYPASS_METHODOLOGY, the comparison is
> internally like-for-like, and on the reach-Human definition the effort multiple is *larger*
> (5.5× vs 2.8×). *Reproduce:* tabulate verdicts per run from `bypass_report.load()`. *Fix:*
> state both quantities explicitly.

**Status and staleness:** Not stale. The paragraph the review quotes stands
verbatim at lines 1678–1682, including "The blind v2 search flipped 10% of
variants; the contrastive v3 search 28%" and the "If 'soften off AI' rather
than 'reach Human' is the bar" sentence. The methodology warning is present at
lines 85–91 (the review cites 84–91). The review labels this one **CONFIRMED**,
its strongest verdict in the block. The underlying counts (4/40, 59/212 flips;
2.5%, 13.7% reversals) are the review's tabulation and are **not yet
independently verified**; the review points at `bypass_report.load()` as the
source. No part is marked resolved.

**The decision to make:** The review proposes stating both quantities
explicitly in the paragraph — the moved-off-AI rates (10%, 28%) and the
reach-Human rates (2.5%, 13.7%) — so the reader cannot carry the 28% number
back onto the reach-Human headline. It notes that on the reach-Human bar the
effort multiple is actually *larger* (about 5.5× versus 2.8×), so disclosure
does not weaken the effort argument.

---

## B4 — Each headline is computed on a different subset

**Context, from zero:** The *bypass arm* reports two headline evasion rates
against **Pangram** (a commercial AI-text detector, Human / Mixed / AI
verdicts). The **per-variant rate, 8.5%**, is how often a single submitted
rewrite (*variant*) reaches a clean Human verdict, computed over **all four
runs** (461 variants). The **per-target rate, 22.5%**, is the fraction of
attacked segments (*targets*) for which *at least one* variant reached Human,
computed over only the **final search in each of the two chambers** (NB v3 and
GO all-31, 71 targets). The two numbers therefore live on different slices of
the data: all four runs for one, the two best runs for the other. B4's charge
is that mixing subsets this way is a form of favourable selection, and that any
single "multiple over the vendors" computed across the two subsets is not
like-for-like.

**The paper text under challenge (current):** The "two rates" framing,
`S10-WRITEUP-DRAFT.md`:1556–1563:

> **Two rates, and both belong here.** They answer different questions and the
> gap between them is threefold, so quoting either alone misleads.
>
> **The per-variant figure — 8.5%, all four runs.** …

The per-target figure, `S10-WRITEUP-DRAFT.md`:1591–1593:

> **The operational figure — 22.5% per target, best method only.** … Taking
> only the **final search in each chamber** and asking on what fraction of
> *targets* at least one variant reached a clean Human verdict:

The single cross-subset multiple, `S10-WRITEUP-DRAFT.md`:1539–1541:

> One asymmetry to keep visible: the 2.31% is a **one-shot** rate, while 22.5%
> allows up to eighteen attempts. Like-for-like on single detector submissions
> the multiple is **3.7×** (8.5% against 2.31%).

**The review's finding (verbatim):**

> **B4. Each headline is computed on a different subset.** *PARTIAL.* 8.5% is all four runs;
> 24.6% is the final search per chamber only. The internally consistent alternatives are
> final-two-run per-variant 11.1%, all-four per-target 12.3%, distinct-text 17.4%; on the
> final two runs the gap between the two rates is 2.3×, not threefold. *Accurate version:*
> "the asymmetry is not disclosed" does not hold — both subsets are named in the bold headings
> themselves ("8.5% per variant, all four runs"; "24.6% per target, best method only") with
> the rationale in the same sentences. And the charge of convenient subsetting is contradicted
> where it can be tested: the one place the subsets are combined into a ratio is the "3.7×"
> line, and the same-subset version is 11.1%/2.31% = **4.8×** — the study reported the number
> that makes its own instrument look *worse*. *Fix:* print all four cells of the
> (subset × estimand) table, and compute any single multiple on one subset.

**Status and staleness:** Partly stale. The review's per-target headline figure
is **24.6%**, but that number was superseded on 2026-08-12 by the M4 fix
(commit `487f313`, "S10 M4: per-target denominator counts targets searched, not
targets that yielded"): the denominator changed from targets-that-yielded (65)
to targets-searched (71), moving the per-target headline from **24.6% to
22.5%**. In the current draft, 24.6% survives only as the corrected-away number
("Counting only targets that yielded … gave 24.6% where the answer is 22.5%",
line 1615). The *structure* B4 objects to is unchanged: 8.5% is still all four
runs (line 1559) and 22.5% is still "the final search in each chamber" (line
1593), so the different-subset critique still applies. The "3.7×" cross-subset
line the review discusses is still present (line 1541), and the "gap between
them is threefold" phrasing the review challenges is still at line 1557. The
review's internally-consistent alternatives (11.1%, 12.3%, 17.4%, 2.3×, 4.8×)
are its own computations and are **not yet independently verified**. No part is
marked resolved.

**The decision to make:** The review proposes printing all four cells of the
(subset × estimand) table — per-variant and per-target, each on the all-four
and final-two subsets — and computing any single vendor multiple within one
subset rather than across two. Its "accurate version" concedes that both
subsets are already named in the bold headings and that the one existing
cross-subset ratio (3.7×) understates the instrument's apparent strength
relative to the same-subset version (4.8×), so the fix is about completeness
and consistency rather than correcting a favourable error.

---

## B5 — Half the pooled per-target estimate is in-sample for the replication claim

**Context, from zero:** The *bypass arm* rewrites flagged segments with
**Opus** to defeat **Pangram** (a commercial AI-text detector). The headline
**per-target rate, 22.5%**, is the fraction of attacked segments (*targets*)
for which at least one **Opus** rewrite (*variant*) reached a clean Human
verdict, pooled over the two final runs — **NB v3 contrastive** (New Brunswick)
and **GO all-31 uniform** (Government Orders). The paper attaches a
*replication* claim to this figure: that a fresh study using the same method
should expect to reproduce it. B5's objection is that NB v3's method was
*designed by watching the earlier NB v2 search fail on the very same 40 New
Brunswick texts* — so scoring v3 on those same texts is partly in-sample, and
an in-sample number is not what a fresh, out-of-sample study would get. Only the
GO all-31 run, drawn and attacked without that tuning, is a clean out-of-sample
application.

**The paper text under challenge (current):** The replication sentence,
`S10-WRITEUP-DRAFT.md`:1603–1606:

> **Roughly one flagged speech in five can be walked past the detector**, at a
> budget of six rounds and three variants per round. This is the figure a fresh
> study replicating our best method should expect to reproduce, and the more
> honest description of the exposure a chamber actually faces.

The three v3 design changes the review cites live in the run script header,
`gov_bypass_all.js`:15–35 ("THREE CHANGES FROM v2, EACH FIXING A MEASURED
DEFECT"), one of them justified by "All four Pangram flips observed so far came
from variants scoring under 34". Appendix C.4 already scopes the GO all-31 run,
`S10-WRITEUP-DRAFT.md`:2991–2992:

> It is also every Government Orders positive we hold, so it is an exploratory
> replication rather than an independent rate estimate.

**The review's finding (verbatim):**

> **B5. Half the pooled per-target estimate is in-sample for the replication claim.**
> *PARTIAL.* "This is the figure a fresh study replicating our best method should expect to
> reproduce" is said of 24.6%, but v3's design was derived from watching v2 fail on the same
> 40 New Brunswick texts (`gov_bypass_all.js:15-35` lists three changes "each fixing a
> measured defect", one justified by "All four Pangram flips observed so far came from
> variants scoring under 34"). Only GO all-31 is a clean out-of-sample application.
> *Accurate version:* none of the three changes is fitted per text — contrastive exemplars and
> noise-aware early stopping are tuned on the Opus proxy, and keeping all sub-50 variants is a
> submission-budget change a replicating study would also make. The empirical answer is in the
> data: the clean out-of-sample run returns 22.2% against NB v3's 26.3% (19.4% vs 25.0%
> corrected), which is not what overfitting looks like. Appendix C.4 already calls GO all-31
> "an exploratory replication rather than an independent rate estimate". *Fix:* name GO
> all-31 as the only out-of-sample estimate and quote it (19–22%, wide interval) as the
> replication expectation; keep the pooled figure as a summary of what was achieved.

**Status and staleness:** Partly stale on the numbers. The review states the
replication claim "is said of 24.6%"; the per-target headline is now **22.5%**
after the M4 denominator fix (commit `487f313`, 2026-08-12), and the claim
sentence at lines 1603–1606 now sits in the 22.5% paragraph. The review's own
per-run figures anticipate this: it gives the corrected values parenthetically
("19.4% vs 25.0% corrected"), and those corrected values — NB v3 25.0%, GO
all-31 19.4% — are exactly what the current per-target table prints (lines
1599–1600). The target sentence ("This is the figure a fresh study replicating
our best method should expect to reproduce") still stands verbatim, and the
Appendix C.4 "exploratory replication rather than an independent rate estimate"
scoping still stands at lines 2991–2992. The three v3 design changes are in
`gov_bypass_all.js`:15–35 as quoted. The comparison of out-of-sample (GO,
19.4%) to in-sample-flavoured (NB v3, 25.0%) is the review's argument and is
**not yet independently verified**. No part is marked resolved.

**The decision to make:** The review proposes naming GO all-31 as the only
clean out-of-sample estimate and quoting it (roughly 19–22%, wide interval) as
the replication expectation, while keeping the pooled 22.5% as a summary of what
was achieved rather than as a forecast. Its "accurate version" argues against
overfitting on the merits — the v3 changes are tuned on the Opus proxy and on
submission budget, not fitted per text, and the out-of-sample run (19.4%) lands
close to the in-sample one (25.0%) — so the choice is between re-attributing the
replication claim to the GO run versus leaving it on the pool with a caveat.

---

## B6 — "The two chambers agree closely" is a comparison with no power

**Context, from zero:** The *bypass arm* ran its final search in two separate
chambers — the New Brunswick provincial legislature (run **NB v3 contrastive**)
and the federal Government Orders corpus (run **GO all-31 uniform**) — and
reports a *per-target* evasion rate for each: the fraction of attacked segments
where at least one **Opus** rewrite reached a clean Human verdict on **Pangram**
(the commercial detector). The paper observes that the two chambers' rates are
close and treats that concordance as reassuring. B6's objection is statistical:
each chamber's rate rests on only ~31–40 targets, so the difference between them
carries a confidence interval wide enough to accommodate one chamber's rate
being half or double the other's — meaning "they agree closely" is a claim the
data have essentially no power to support.

**The paper text under challenge (current):** `S10-WRITEUP-DRAFT.md`:1624–1627:

> The two chambers agree closely (25.0% and 19.4%) **despite contradicting each
> other on which edits work**: their hypotheses agree on repetition and
> unglossed idiom and flatly disagree on sentence rhythm. The rate transfers;
> the playbook does not.

The version the review actually saw (2026-08-11) carried an extra sentence and
different figures. From the M4 commit diff (`487f313`, 2026-08-12), the removed
text read:

> Two things make it more trustworthy than its interval suggests. … the two
> chambers agree closely (26.3% and 22.2%) **despite contradicting each other
> on which edits work**

**The review's finding (verbatim):**

> **B6. "The two chambers agree closely" is a comparison with no power.** *PARTIAL.* The
> difference is 4.1pp with a 95% CI of [−16.9, +25.1]pp; the data are equally consistent with
> the GO rate being half or double the NB rate. *Accurate version:* the concordance is
> evidence about a question the pooled interval does not address — the interval quantifies
> sampling error *under an assumed common rate*, and says nothing about whether one exists, so
> the sentence is not double-counting. It is also paired with a genuinely independent point:
> the two chambers' derived humanising hypotheses flatly contradict each other, which is what
> makes "the rate transfers; the playbook does not" more than a restatement. *Fix:* soften
> "more trustworthy than its interval suggests" to "consistent across two chambers, though
> with intervals too wide to establish that they agree".

**Status and staleness:** Largely moot. The specific sentence B6 asks to soften
— "more trustworthy than its interval suggests" — **no longer exists in the
draft**. It was removed on 2026-08-12 as part of the M4 fix (commit `487f313`),
which also updated the per-chamber figures from the review's 26.3%/22.2% to the
current **25.0% and 19.4%**. The current sentence (line 1624) reads "The two
chambers agree closely (25.0% and 19.4%) despite contradicting each other on
which edits work" — the "more trustworthy than its interval suggests"
overclaim, which is what the finding targets, is gone. What survives is the
residual phrase "agree closely," which a reader could still take as an
established agreement; the review's underlying point (the difference has a CI of
roughly [−17, +25]pp, so agreement is not established) would still apply to that
residual phrase. The 4.1pp difference and its interval are the review's
computation on the *old* figures and are **not yet independently verified**; on
the current figures the difference is 5.6pp. No part is marked resolved.

**The decision to make:** The review's proposed fix — softening "more
trustworthy than its interval suggests" to "consistent across two chambers,
though with intervals too wide to establish that they agree" — is already half
applied, since the "more trustworthy" clause was deleted at M4. The open
decision is narrower: whether the surviving "agree closely" phrasing (line
1624) still needs the "intervals too wide to establish agreement" caveat, or
whether the deletion already suffices.

---

## B7 — Two of the four runs and the band tables have no script

**Context, from zero:** The *bypass arm* comprises four search runs against
**Pangram** (a commercial AI-text detector). For the arm to be reproducible,
each run needs a committed script, and the auxiliary analyses need their
generators. B7 audits what is actually in the repository. Two artifacts matter
especially: the **contrast-pair files** (`bypass_contrast.json`,
`gov_contrast_all.json`) that feed the contrastive search its human exemplars,
and the **band tables** — the analysis that sorts flagged originals into
`fraction_ai` bands (0–29, 30–39, …) and reports the evasion rate per band,
which is "the entire basis of the organising hypothesis" that evadability is a
property of the original text rather than of the rewrite. B7 finds that the two
New Brunswick run scripts and the contrast-pair builders are missing, while
disputing the sub-claim that the band tables are unreproducible.

**The paper text under challenge (current):** B7 pins its reproducibility
charge to `BYPASS_METHODOLOGY.md`:5, which it quotes as "Everything is
reproducible from analysis/s10/". The current line 5 does **not** say that; it
reads:

> §4.9 of the write-up is conditional on the selection described here.

The mitigating note about the GO script being a copy of the NB script, which
the review cites at lines 242–244, is currently at `BYPASS_METHODOLOGY.md`:211–213:

> Verified by structural diff, not by assertion: the Government Orders script was
> copied from the NB script and differs only in file paths, the seed count, and
> `.response.text` → `.text` for the other corpus schema.

**The review's finding (verbatim):**

> **B7. Two of the four runs and the band tables have no script.** *PARTIAL.*
> `BYPASS_METHODOLOGY.md:5` says "Everything is reproducible from analysis/s10/". The New
> Brunswick v2 and v3 search scripts are absent (only `gov_bypass_v3.js` and
> `gov_bypass_all.js` exist), so the run contributing 29 of 39 variant reversals cannot be
> re-executed or inspected for its gate parameters; and the contrast-pair builders that
> produced `bypass_contrast.json` and `gov_contrast_all.json` exist nowhere. *Accurate
> version:* the third sub-claim — that the band tables are unreproducible — is wrong, and it
> is the one called "the entire basis of the organising hypothesis". The New Brunswick band
> table regenerates exactly from stored artifacts in about ten lines (join `opus_orig3x` from
> `pangram_bypass_key.json` onto `pangram_v3_key.json` and `bypass_v3_pangram.json`, then
> band): 46/54/56/56 variants with flip 57%/30%/23%/7% and clean Human 43%/7%/9%/0%, every
> cell to the digit. The missing-script gaps are also partly mitigated:
> `BYPASS_METHODOLOGY.md:242-244` records that the GO script was copied from the NB script and
> differs only in paths, seed count and one field name, verified by structural diff.
> *Reproduce:* `ls *.js && grep -rl 'human_exemplars' . && grep -n 'band' bypass_report.py`.
> *Fix:* commit the NB search scripts and the contrast-pair builders, or state in §4.9 and
> C.4 that two of the four runs are documented by their outputs only; add the band computation
> to `bypass_report.py`.

**Status and staleness:** The substance still holds, but the pinned quote does
not exist. Reading confirms only `gov_bypass_v3.js` and `gov_bypass_all.js` are
present among the bypass run scripts — no New Brunswick v2/v3 search script — so
the run contributing 29 of 39 variant reversals cannot be re-executed. A search
for the exemplar-builder marker (`grep -rl 'human_exemplars'`) turns up no
generator script (only data files), so the contrast-pair builders are indeed
absent. The mitigating GO-copied-from-NB note is present, now at lines 211–213
(the review cited 242–244 — a line-number drift, not a deletion). However, the
sentence B7 quotes as its reproducibility hook — `BYPASS_METHODOLOGY.md:5`,
"Everything is reproducible from analysis/s10/" — **appears nowhere in
`BYPASS_METHODOLOGY.md`**, at review time or now: the word "reproducible" does
not occur in that file at all, and the string is found only inside the two
review files. So the finding's opening quotation does not correspond to any text
in the file it names. The review's band-table reconstruction (the exact
46/54/56/56 counts and 57/30/23/7 flip rates) is its own computation and is
**not yet independently verified**, though the New Brunswick band table it
reproduces does appear in `BYPASS_METHODOLOGY.md`:66–71. `bypass_report.py`
contains no band computation (the only "band" occurrence is a comment at line
92). No part is marked resolved.

**The decision to make:** The review proposes either committing the missing NB
search scripts and the contrast-pair builders, or stating plainly in §4.9 and
Appendix C.4 that two of the four runs are documented by their outputs only;
and, separately, adding the band computation to `bypass_report.py` so the
organising-hypothesis table has a committed generator. Because the finding's
"Everything is reproducible" hook is not in the file, any adjudication should
first fix the misquote, then decide the two remaining sub-points on their own
terms (missing scripts; band code location).

---

## B8 — BYPASS_METHODOLOGY and the write-up disagree about the zero-success run

**Context, from zero:** One of the four bypass runs, **GO Opus-selected** (35
targets, 80 submitted variants), produced **zero clean Human verdicts** — no
successful evasion of **Pangram** (the commercial detector) at all. The arm's
organising hypothesis is that evadability is a property of the *original* text:
segments the detector already scored near its boundary (low `fraction_ai`
*band*) are vulnerable, high-band segments are not. This run was seeded entirely
from high-band, hard-to-move originals (it was "badly seeded"), so its zero
successes can be read two ways: as powerful evidence *for* the study's central
picture (high-band texts don't move), or as *uninformative* about the band
hypothesis (a sample with no low-band texts cannot test whether low-band texts
are the vulnerable ones). B8 flags that the methodology file leans the first way
and Appendix C.4 leans the second, and asks whether the two passages
contradict. A secondary point concerns the denominator "80": those are 80
gate-passing variants, not 80 raw attempts.

**The paper text under challenge (current):** The methodology file's strong
reading, `BYPASS_METHODOLOGY.md`:164–167:

> What it does establish, and this is the strongest single fact in the arm:
> **zero clean Human verdicts in 80 attempts at any band**, matching the 0/40
> observed above Opus 70 in New Brunswick.

Appendix C.4's weaker reading, `S10-WRITEUP-DRAFT.md`:2986–2988:

> it is range-restricted — it cannot contain the low band where New Brunswick
> found most of its successes, so its zero successes test nothing about the band
> hypothesis.

The "80 variants" denominator, `BYPASS_METHODOLOGY.md`:155:

> **Result: 80 variants, 18% flip, ZERO clean Human verdicts.**

**The review's finding (verbatim):**

> **B8. BYPASS_METHODOLOGY and the write-up disagree about the zero-success run.** *PARTIAL.*
> BYPASS_METHODOLOGY calls "zero clean Human verdicts in 80 attempts at any band" the
> "strongest single fact in the arm"; Appendix C.4 says the same run's "zero successes test
> nothing about the band hypothesis". *Accurate version:* they are not opposite claims. The
> methodology document says, in order, "This sample does not replicate the gradient" → "The
> sample is range-restricted … A sample that cannot contain the effect cannot test it" → then
> the narrower high-band claim. It concedes the write-up's point two sentences earlier. And
> the write-up's blunt "test nothing" is the looser statement: against the arm's own 8.5%
> pooled rate, 0 successes in 80 has probability 0.915^80 ≈ 0.0009, so the run does
> discriminate the band hypothesis from a flat-rate alternative. *Sub-point that stands:* "80
> attempts" is 80 gate-passing variants out of ~513 generated across 35 seeds, 10 of which
> yielded nothing — the same denominator issue as **M12**. *Fix:* align the two passages and
> state the 80 as 80 of ~513.

**Status and staleness:** Not stale for the two quoted passages. The
methodology file still calls the run's zero-Human result "the strongest single
fact in the arm" (lines 164–167) and Appendix C.4 still says its "zero successes
test nothing about the band hypothesis" (lines 2986–2988), so the apparent
tension the finding describes is intact. The intervening concessions the
review's "accurate version" relies on are also present in the methodology file
("This sample does not replicate the gradient", "The sample is range-restricted
… A sample that cannot contain the effect cannot test it", lines 157–162). The
secondary denominator point connects to **M12**, which was addressed elsewhere
on 2026-08-16 (commit `f7613b1`, "reframe to per-detector-submission"): the
methodology now discloses the generated-vs-submitted arithmetic in general
(lines 226–240, "roughly 461 of ~1,830 generated"), but the specific "80 of
~513" framing for this one run is not stated at line 155, where it still reads
"80 variants". The review's 0.915^80 ≈ 0.0009 power calculation is its own and
is **not yet independently verified**. No part is marked resolved.

**The decision to make:** The review proposes aligning the two passages so they
read as the same nuanced claim rather than opposite ones — the run is
uninformative about the *low-band* gradient but does discriminate the band
hypothesis from a flat-rate alternative — and restating the "80 attempts" as 80
gate-passing variants out of ~513 generated across 35 seeds. Its "accurate
version" argues the two passages do not actually contradict (the methodology
concedes the range-restriction two sentences before its strong claim), so the
fix is largely a wording alignment plus the M12-style denominator disclosure.
