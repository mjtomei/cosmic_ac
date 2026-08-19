# Q block — the quality-arm findings of the 2026-08-11 adversarial review

*This file is for Matthew's review. Below the status block is the ORIGINAL
consolidated presentation of all twelve Q items, extracted verbatim from the
session transcript (pre-compaction, 2026-08-17); each item was verified with
confirmatory runs before that presentation. Nothing in the verbatim section
has been edited.*

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

## The original presentation, verbatim from the transcript

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