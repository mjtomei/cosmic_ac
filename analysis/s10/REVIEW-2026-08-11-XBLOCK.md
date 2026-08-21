# X block — the cross-cutting findings of the 2026-08-11 adversarial review

*Self-contained review file for Matthew. The 2026-08-11 adversarial review of the S10
write-up produced twelve cross-cutting findings (X1–X12) — items spanning sections
rather than attacking one arm: consistency between the write-up and its own
METHODOLOGY / work-log / register documents, the framing of §5 (Limits), §6 (Policy
context), §7 (Related work), §8.5 (the moving-baseline proposal), plus benchmark
attributions and comparator coverage. Each section below is complete on its own: the
context a cold reader needs, the current text under challenge quoted verbatim with
file:line references (checked 2026-08-21 at commit c5562bf; the draft is under active
edit, so line numbers may drift by a few — the quoted text is the anchor), the review's
finding verbatim, a staleness assessment, and the decision left to make. Verdict labels inside the verbatim findings
(*CONFIRMED / PARTIAL*) are the review's own. Much has changed since the review ran —
the 2026-08-13 word-weighted prevalence rebuild (pooled headline now 9.0% of words
across 20 chambers, was 12.4% of segments across 19), the 2026-08-16 removal of the
sensitivity number (P1), and the 2026-08-18/19 §5 and Q-block edits — so several items
are wholly or partly moot and each section says exactly which parts.*

## Status at a glance (2026-08-21)

| item | one-line summary | status |
|---|---|---|
| X1 | Se identity rested on a corpus the documents say was deleted; §5 had no sensitivity bullet | **already-resolved** in core (P1 fix, 2026-08-16); residue: §5 bullet choice + one stale Appendix C.4 row |
| X2 | 2.86% (and 9.09%) attributed to the Perkins benchmark; they are Epoch AI Style Imitation numbers | **live — unadjudicated** (draft:1652; PRIOR_ART:163–164) |
| X3 | "peer-review benchmarks" (plural) claim is selective; only Sem-Detect gives ~6%, Saha split omitted | **live — unadjudicated** (unchanged since review) |
| X4 | §8.3's "quality assessment is orthogonal to provenance" vs the paper's own stage-1/2 authorship tracking | **live in wording** — passage re-founded 2026-08-19 (Q5) but "orthogonal" retained |
| X5 | §7 omits Suvanto (the documents' own "closest work"), ParliaBench, NCSL 55% | **live — unadjudicated**; reinforced by VENUES.md (2026-08-18) |
| X6 | Neither prior comparator's chamber carries an S10 prevalence estimate | **split**: Pimlico half **moot** (UK now has a §4.2 row); Rice half + "Nineteen chambers" **live** |
| X7 | §5 states only the upward bias while a downward length-band bias was measured | **moot** — superseded by the 2026-08-13 word-weighted / 50-word-floor redesign; 12.4% no longer exists |
| X8 | Register bullet drops the mandated one-shot-vs-18-attempts caveat on the 10× | **live** — and the bullet's numbers (24.6%, 10.6×, 12.4%) are now stale outright |
| X9 | Register says "refuting" where the write-up says "run the wrong way" | **live — unadjudicated** (one-word fix) |
| X10 | "Saskatchewan is the one solid null" contradicts the scan's own text | **live — unadjudicated** (one-sentence fix) |
| X11 | §8.5 equates its residual with the "same quantity" S17 measures | **live — unadjudicated** (one-phrase fix) |
| X12 | Five standard referee objections missing from §5 | **split**: (ii) pooling weights + (iii) omnibus test **live**; (i) superseded by the redesign; (iv)(v) rejected by the review itself; (vi) resolved |

Reader's key, used throughout: **S10** is the study — measuring machine-drafted speech
in 20+ legislative chambers by scoring official transcripts (Hansard, the Congressional
Record) with a calibrated commercial AI-text detector, plus a detector-independent
lexical instrument. **Pangram** (version 4) is that commercial detector; **Se/Sp** are
its sensitivity (share of true machine text it flags) and specificity (share of true
human text it correctly passes). **The register** is the study's lexical style measure —
the rate of AI-associated words in speech. **The work log / study register** is
`studies-and-work-log.md` at the repo root, the project's running record of studies,
with a per-study findings summary (the "register") and dated log entries. **The review**
is `REVIEW-2026-08-11.md`, a multi-agent adversarial review whose findings are grouped
in lettered blocks (P prevalence, M methods, Q quality, B bypass, X cross-cutting), each
independently verified before presentation.

---

## X1 — The Se identity and the deleted synthetic corpus

**Context, from zero:** S10 reports what share of recent legislative speech is
machine-drafted, using Pangram, a commercial AI-text detector. Converting a detector's
observed flag rate π into true prevalence τ requires its error rates via the
Rogan–Gladen identity τ = (π − (1−Sp))/(Se − (1−Sp)), where Sp (specificity) is the
probability human text passes and Se (sensitivity) the probability machine text is
caught. At review time the pipeline divided by Se = 1.000, a value computed from 40
synthetic New Brunswick speeches generated by the open-weight model Mistral-7B — a
corpus the study's own methods document (`METHODOLOGY.md`) said had been deleted, and
whose generator script's docstring disclaimed it as a pilot mechanism check. The review
raised this as P1 (in the prevalence block) and again here as X1, adding that §5
(Limits, the paper's list of caveats) contained no bullet about sensitivity at all —
the floor framing was attributed entirely to evasion (members deliberately disguising
machine text), not to the detector's unmeasured blindness to edited machine text.

**The paper/document text under challenge (current):** The Se number is gone
everywhere. `S10-WRITEUP-DRAFT.md`:124–128 (§3.1):

> When `Sp = 1` this collapses to `τ = π/Se`. **`Se` is not estimated.** Since a
> detector's sensitivity cannot exceed 1, `τ = π/Se ≥ π`, so with `Sp = 1`
> measured (§4.1) the observed flag rate is a conservative floor on true
> prevalence — every prevalence figure below is thus conservative with respect
> to machine text the detector misses.

`S10-WRITEUP-DRAFT.md`:188–192 (§4.1): "Sensitivity is not estimated: with `Sp = 1` and
any real detector's `Se ≤ 1`, the observed flag rate is a **conservative floor** on true
prevalence, so every §4.2 figure is if anything an underestimate of machine text."

The §3.4 retired-instruments row the review called self-contradictory now reads
(`S10-WRITEUP-DRAFT.md`:180):

```
| Mistral synthetic sensitivity corpus | deleted | too few words to carry variance; sensitivity not estimated |
```

§5's floor bullet (`S10-WRITEUP-DRAFT.md`:1940–1944):

> - **Prevalence is a floor.** Detectors see undisguised machine text. A
>   directed search clears the detector on 8.5% of variants and **22.5% of
>   targets** (§4.9), so 9.0% is a lower bound. How much of a lower bound is
>   not estimable from this design: we can measure how often evasion succeeds
>   when attempted, not how often it is attempted.

`METHODOLOGY.md`:604 heads a section "**Sensitivity: cite, don't generate.**";
`METHODOLOGY.md`:614–616: "*Sensitivity is not estimated (see the calibration note
above): prevalence is reported as a floor, τ ≥ π, since Sp = 1 and Se ≤ 1. Nothing in
the study depends on a sensitivity number.*"; `METHODOLOGY.md`:618–626 names the
unmeasured class the review pointed at: "The class this study argues actually dominates
Hansard is different: drafted by an aide with a model, revised by the member, then
normalised by a professional Hansard editor. To measure Se on *that*, you would have to
generate it … Reporting the floor honestly is better than manufacturing an interval."
The scenario table the review cited as "the correct treatment" survives at
`METHODOLOGY.md`:708–718 (New Brunswick pilot section): Se 1.00 → 7.5%, 0.75 → 10.0%,
0.50 → 15.0%, 0.30 → 25.0%, "with 1/Se as a stated unknown multiplier."

One loose end: the Appendix C.4 model inventory still lists the corpus with a pointer
to a section that no longer describes it (`S10-WRITEUP-DRAFT.md`:3063):

```
| Synthetic in-domain sensitivity corpus (§3.1) | Claude Opus | default |
```

**The review's finding (verbatim):**

> **X1. The Se identity rests on a corpus the primary documents say was deleted, and §5 has no
> sensitivity bullet.** *PARTIAL.* Duplicate of **P1**, raised independently by the
> cross-cutting reviewer with two additions: `gen_se_corpus.py`'s own docstring says "treat
> the resulting Se as a *pilot mechanism check*, not the study's Se", and `METHODOLOGY.md`
> 712–741 sets out the correct treatment (a one-sided floor with 1/Se an unknown multiplier,
> tabulated 7.5% → 10.0% at Se = 0.75 and 25.0% at Se = 0.30) while naming the unmeasured
> class — aide-drafted, member-revised, Hansard-edited — as the one that "actually dominates
> Hansard". §5 Limits contains no sensitivity bullet at all, attributing the floor entirely to
> evasion. *Accurate version:* because Sp = 1 is measured, τ = π/Se and Se ≤ 1 always, so
> Se = 1.000 yields the *smallest* possible calibrated prevalence; at METHODOLOGY's own
> replacement anchor (Se = 0.993) the figure is 12.5% against the reported 12.4%. Also, §3.4
> line 164 ("Mistral synthetic control corpus | deleted | replaced by in-domain synthetic Se")
> is self-contradictory, since the in-domain synthetic Se *is* that corpus. *Fix:* re-source
> Se to the published anchors METHODOLOGY already names, and add the §5 bullet naming detector
> sensitivity to edited text as the study's largest unmeasured quantity.

**Status and staleness:** Resolved in its core, five days after the review. Commit
9ecc8d9 (2026-08-16, "S10 P1: remove the Se sensitivity number entirely; reframe
prevalence as a floor") took the second of P1's two offered fixes: no Se is computed
anywhere, `prevalence_report.py` no longer contains the computation, and §3.1/§4.1/
METHODOLOGY all carry the one-sided floor with 1/Se as the named unknown — the exact
treatment the reviewer said METHODOLOGY already set out. The resolution is recorded
inline at `REVIEW-2026-08-11.md`:720 ("[RESOLVED 2026-08-16] … The contradiction is
gone because the claim is gone."). The review-quoted §3.4 row ("replaced by in-domain
synthetic Se") no longer exists; the current row is honest. The reported figure also
changed independently: the headline is now 9.0% of words (2026-08-13 rebuild), so the
review's 12.4%/12.5% arithmetic has no referent. Two residues: (1) §5 still has no
dedicated sensitivity bullet — the floor bullet's opening clause "Detectors see
undisguised machine text" gestures at edited-text blindness, but the bullet then
discusses only evasion, so the review's specific request (name Se-on-edited-text as the
study's largest unmeasured quantity, in Limits) is at best half-met; (2) the Appendix
C.4 inventory row at draft:3063 still points to §3.1 for a corpus §3.4 says was cut.

**The decision to make:** The headline fix is done; decide the residue. Either add the
one-sentence §5 bullet the review asked for (drawing on METHODOLOGY:618–626's
aide-drafted/member-revised/Hansard-edited class), or rule the floor bullet's current
first clause sufficient; and fix or delete the stale C.4 row either way.

---

## X2 — Two vendor rows attributed to the wrong benchmark

**Context, from zero:** S10's bypass arm measures how often a directed rewrite search
gets flagged machine text past Pangram (the study's commercial AI-text detector): 8.5%
of submitted variants and 22.5% of targets succeed. To give those numbers context, §4.9
carries a table of published false-negative rates (FNR — the share of machine text a
detector misses), most of them vendor-reported in Pangram's own technical report
(arXiv:2607.27183). That report contains several third-party benchmark suites; two
matter here: the **Perkins benchmark** (its Table 22, reported as *mean accuracy* over
three manipulation methods — Pangram 4: 100.0% baseline, 94.1% manipulated) and the
**Epoch AI Style Imitation benchmark** (its Table 23, reported as document-level FNR —
Pangram 4: 2.86% = 17/594; Originality.ai, a rival commercial detector: 9.09%). The
review found that S10's tables took the Table 23 numbers but labeled them "Perkins."
The comparison anchor for S10's own multiples (3.7×, 9.8×) is a different row entirely
— the 2.31% FNR of 13 commercial "humanizer" evasion services — so no computed claim
depends on the mislabeled rows.

**The paper/document text under challenge (current):** `S10-WRITEUP-DRAFT.md`:1648–1655
(the §4.9 comparison table; the review cited this table at its then-location, line 546):

```
| measurement | rate | what it is |
|---|---|---|
| Pangram 4, clean | 0.34% | FNR, known-AI text, vendor-reported |
| Pangram 4, 13 humanizer services | 2.31% | FNR under commercial evasion, vendor |
| Pangram 4, BLADER de-AI agent | 0.43% | FNR under agentic evasion, vendor |
| Pangram 4, Perkins benchmark | 2.86% | FNR, doc-level, adversarial, vendor |
| **this study, per detector submission** | **8.5%** | **induced FNR under an iterative search that self-screens rewrites before submitting — 3.7× the humanizers** |
| *this study, per target* | *22.5%* | *induced, ≤18 attempts — 9.8× the humanizers* |
| Rice 2026, Australian Hansard | ~8% | **false *positive* rate**, n = 50 |
```

and the follow-on sentence at `S10-WRITEUP-DRAFT.md`:1665–1668: "…once the per-variant
interval is clustered on text it runs [4.0, 13.4], so the adversarial vendor figures at
2.31–2.86% sit below our estimate but not far below its lower bound." (Note in passing:
draft:1660–1668 says this same thing twice in slightly different words — an editing
leftover worth cleaning whenever this passage is touched.)

`PRIOR_ART.md`:158–166 (the source table the draft row was taken from):

```
| Pangram 4 report, clean | 0.34% | FNR, known-AI |
| Pangram 4 report, 13 humanizer services | 2.31% | FNR under commercial evasion |
| Pangram 4 report, BLADER de-AI agent | 0.43% | FNR under agentic evasion |
| Pangram 4 report, Perkins benchmark | 2.86% | FNR, doc-level adversarial |
| Originality.ai, Perkins | 9.09% | FNR, doc-level adversarial |
| GPTZero / Originality.ai, humanizer split | 55.7% / 71.5% | FNR at 1% FPR |
| Binoculars / Fast-DetectGPT, peer review | ~93.8% | FNR at 1% FPR |
```

**The review's finding (verbatim):**

> **X2. Two vendor rows are attributed to the wrong benchmark.** *PARTIAL.* In the Pangram 4
> report, 2.86% (17/594) is Pangram 4's document-level FNR on the **Epoch AI Style Imitation**
> benchmark (Table 23) and 9.09% is Originality.ai's on the same; the **Perkins** benchmark is
> Table 22, reported as three-method mean accuracy (Pangram 4: 100.0% baseline, 94.1%
> manipulated, i.e. ~5.9% miss; next best Copyleaks, not Originality.ai). Both
> `S10-WRITEUP-DRAFT.md`:546 and `PRIOR_ART.md`:163-164 label them Perkins, in a table whose
> stated purpose is naming quantities precisely. *Accurate version:* 2.86% is a correct
> Pangram 4 vendor-reported FNR; only the benchmark name is wrong, and no claim changes. With
> the real Perkins figure substituted the ordering is unchanged (0.34%, 0.43%, 2.31%, 2.86%,
> 5.9% all below 8.5%), and S10 never computes a multiple against Perkins — both multiples are
> explicitly anchored to 2.31%. The "1.44×" replacement comparison is itself an unlicensed
> unit conversion (mean accuracy → FNR). *Secondary point that stands:* 2.31% is
> 1 − (AI recall 97.69%), i.e. it counts Mixed as a miss, whereas S10 counts only Human as
> success; the strictly matched vendor rate is 1 − 98.83% = 1.17%, which runs in the study's
> favour. *Reproduce:* `pdftotext -layout` on arXiv:2607.27183, Tables 14, 22, 23. *Fix:*
> relabel both rows, add the real Perkins row, and footnote the Mixed asymmetry.

**Status and staleness:** Still live in both files; nothing about it has been fixed. The
draft's row moved (line 546 at review time → 1652 now, the draft having roughly doubled)
but still says "Perkins benchmark" for the 2.86% figure; PRIOR_ART.md:163–164 still
carries both mislabeled rows. One narrowing since review: the draft's table no longer
includes the Originality.ai 9.09% row at all (it survives only in PRIOR_ART), so in the
draft exactly one row needs relabeling. The multiples remain anchored to 2.31% (draft
rows at 1653–1654, prose at 1532 and 1543), as the review said, so no computed claim
moves. The Mixed-asymmetry footnote (Pangram's vendor 2.31% counts its own "Mixed"
verdict as a miss, while S10 counts only clean "Human" verdicts as evasion success —
the strictly matched vendor rate would be 1.17%, which would make S10's multiple larger,
not smaller) has not been added.

**The decision to make:** Apply the review's relabel — "Epoch AI Style Imitation
benchmark" on draft:1650 and PRIOR_ART:163–164 — and decide the two optional additions:
a true Perkins row (flagged as mean accuracy, a different unit, per the review's own
warning against converting it to an FNR) and the Mixed-asymmetry footnote, which runs in
the study's favour. The minimal alternative is to relabel and do nothing else, since no
claim depends on the row.

---

## X3 — The peer-review benchmark claim is selective

**Context, from zero:** §7 (Related work) answers Rice 2026 — a Substack analysis of the
Australian federal Parliament that found *no* post-ChatGPT inflection using Binoculars
and Fast-DetectGPT, two published open-source "zero-shot" AI-text detectors that score
text by token statistics rather than training on labeled data. S10's answer is that
those instruments are near-blind on formal institutional prose, so Rice's null is
uninformative. The supporting evidence is drawn from benchmark tables reprinted in
Pangram's technical report: on **Sem-Detect** (a peer-review benchmark; the report's
Table 27) both methods collapse to roughly 6% true-positive rate (TPR — share of machine
text caught) at 1% false-positive rate; but on the **Saha** peer-review benchmark (Table
28) Fast-DetectGPT does well on the easy subset (100.0/100.0/97.5) and moderately on the
hard one (72.1/68.2/63.1). The review's charge: the draft says "peer-review benchmarks"
(plural) fall to ~6% when only one benchmark shows that, and `PRIOR_ART.md` (the study's
comparator-verification document) quotes Saha's Binoculars numbers while omitting
Fast-DetectGPT's much better ones.

**The paper/document text under challenge (current):** `S10-WRITEUP-DRAFT.md`:2081–2089
(§7):

> The substantive answer to Rice is therefore about **sensitivity, not
> specificity**, and it generalises beyond his study. Binoculars (Hans et al.
> 2024) and Fast-DetectGPT (Bao et al. 2024) are sound published methods that
> degrade severely on formal institutional prose: on peer-review benchmarks
> reproduced in the Pangram 4 report, both fall to roughly 6% true-positive rate
> at 1% FPR — false-negative rates above 90% — where a calibrated commercial
> detector holds above 95%. Hansard is the same kind of register. A null
> recovered with those instruments on this genre is close to uninformative, and
> Rice's own numbers (Binoculars flagging 0.4% of everything) look like exactly
> that.

`PRIOR_ART.md`:93–96: "On peer-review benchmarks reproduced in the Pangram 4 technical
report (arXiv:2607.27183), at 1% FPR both Binoculars and Fast-DetectGPT reach ~6%
true-positive rate — FNR above 90% — where a calibrated commercial detector holds above
95%. On the harder Saha subset Binoculars runs 14–22% TPR." (Saha's Fast-DetectGPT
numbers are still absent.) `PRIOR_ART.md`:166: "| Binoculars / Fast-DetectGPT, peer
review | ~93.8% | FNR at 1% FPR |".

**The review's finding (verbatim):**

> **X3. The peer-review benchmark claim is selective.** *PARTIAL.* §7 says both Binoculars and
> Fast-DetectGPT "fall to roughly 6% true-positive rate at 1% FPR" on "peer-review benchmarks"
> (plural). Only one benchmark gives that: Sem-Detect (Table 27). On the Saha benchmark
> (Table 28) Fast-DetectGPT scores 100.0/100.0/97.5 on the easy subset and 72.1/68.2/63.1 on
> the hard subset, and `PRIOR_ART.md`:96 cites Saha's Binoculars numbers while omitting
> Fast-DetectGPT's. *Accurate version:* two of the three sub-points fail. "Reproduced in the
> Pangram 4 report" is natural English for "reprinted in", which is what Table 27's note
> describes, and PRIOR_ART separately flags all Pangram rows as vendor-reported. And the claim
> that non-commercial detectors match the commercial one collapses on the table's own
> footnote: EditLens, Sem-Detect and Anchor all carry a dagger marking them as *tuned on
> peer-review data*; among untuned detectors only Pangram clears 95. The conclusion also
> holds — the claim is scoped to 1% FPR, which Table 28 does not report; MELD-eval gives
> Binoculars 0.6% and Fast-DetectGPT 17.0% at that operating point; and Rice's primary
> statistical detector is Binoculars, weak on both peer-review benchmarks. *Fix:* name
> Sem-Detect, state the Saha split for Fast-DetectGPT, and keep the argument on Binoculars.

**Status and staleness:** Still live and entirely unchanged: both the §7 paragraph and
the PRIOR_ART passage read today exactly as the review saw them (only the draft line
number moved). Note the review's own verification cuts the charge down considerably —
the ~6%-at-1%-FPR claim survives as scoped (Saha's table does not report the 1% FPR
operating point, and MELD-eval numbers at that point are consistent with the sentence),
and Rice's primary statistical detector, Binoculars, is weak on both benchmarks. What
stands is the plural "benchmarks" implying breadth that one benchmark carries, and
PRIOR_ART's asymmetric quoting of Saha.

**The decision to make:** Adopt the review's fix — name Sem-Detect as the ~6% source,
add Fast-DetectGPT's Saha split alongside Binoculars' in PRIOR_ART, and keep §7's
argument centered on Binoculars — or, minimally, change "peer-review benchmarks" to the
singular and cite the benchmark by name. Doing nothing leaves a selectivity charge a
referee can re-derive from the vendor report's own tables.

---

## X4 — "Quality assessment is orthogonal to provenance"

**Context, from zero:** S10's quality arm grades speeches against the Discourse Quality
Index (DQI; Steenbergen, Bächtiger, Spörndli & Steiner 2003), a seven-dimension rubric
for deliberative quality (justification, common-good framing, three respect dimensions,
constructiveness, evidence), applied here by an LLM judge anchored on the instrument
authors' own published codings. §8.3 argues the study's "substitution": since detection
is a dead end, institutions should assess quality directly — and claims quality
measurement is *orthogonal* to provenance (i.e., carries no information about whether a
machine wrote the text). The review's charge: the paper's own §4.9 stages 1–2 show DQI
scores *do* track authorship labels on three of seven dimensions (stage 1: 840 segments
labeled by a blinded LLM screen; stage 2: 682 segments labeled by Pangram verdict, with
chamber fixed effects; t up to +6.1), so "orthogonal" is contradicted in-house; while
the 63-pair evidence §8.3 leans on compares machine-touched text to machine-touched
text and cannot speak to provenance. Relevant since the review: review item Q5 (same
review, quality block) attacked the *reliability* support for the same passage, and its
closure on 2026-08-19 (commit 4db96d7) rewrote §8.3's support onto validity evidence —
but kept the word.

**The paper/document text under challenge (current):** `S10-WRITEUP-DRAFT.md`:2215–2234
(§8.3, as revised for Q5):

> The case rests on §4.9's primary finding, and it is independent of evasion:
> machine-assisted text grades **better-formed, not worse-engaged** on the DQI —
> so policing authorship does not protect quality, because the authorship
> detection would flag is not where the quality deficit is. That is the whole
> argument: **quality assessment is orthogonal to provenance, not a proxy for
> it.** Had DQI tracked authorship, it would merely be a worse detector; because
> it does not, it measures the thing anyone actually wanted to know. The
> reliability statistics cannot carry this claim by themselves — a consistently
> biased judge would also reproduce itself perfectly (review item Q5); what
> carries it is validity evidence: the rubric's calibration anchors are the
> instrument authors' own published codings, so the scale is theirs rather than
> the judge's; the one dimension
> where judge-suspicion moves the result is identified and quarantined rather
> than averaged in (respect_groups; Appendix D.1, §4.9), and across stages the
> judge's AI-guess and its quality scores move independently in both
> directions — higher form under suspicion in the wild pools, lower for weak
> models and higher for frontier ones in stage 6.

Against it, the paper's own stage-1/2 table (`S10-WRITEUP-DRAFT.md`:1442–1450) shows
three dimensions tracking the AI label in *both* stages:

```
| dimension | stage 1, per 0→100 score | stage 1, per sd of score | stage 2, AI vs Human verdict |
| justification | **+1.134** (t +4.1) ✱ | +0.173 | **+0.290** (t +4.4) ✱ |
| common_good | **+0.583** (t +3.3) ✱ | +0.089 | **+0.229** (t +4.5) ✱ |
| respect_groups | **+0.287** (t +2.0) ✱[^r49m] | +0.044 | **+0.220** (t +6.1) ✱ |
```

(the `[^r49m]` marker is new — see Status below) and the revised §4.9 claim
(draft:1459–1462): "AI-assisted legislative speech is
better-formed — more justified, more common-good framed, more positive toward the
groups a policy would help — and shows no engagement penalty once genre or chamber is
held fixed." The power statement the review asked for now exists in §4.9 rather than
§5 (draft:1731–1736, added for review item Q3): "detectable effects run roughly
±0.12–0.26 per dimension for stage 3 — commensurate with the study's own headline
effects (+0.22 to +0.29, stage 2)". §5 (Limits) still has no power bullet.

**The review's finding (verbatim):**

> **X4. "Quality assessment is orthogonal to provenance" is contradicted by the paper it sits
> in.** *PARTIAL.* §8.3 draws the substitution result from 63 pairs in which *both* members
> are machine-touched text; the contrast that bears on provenance is §4.9 stages 1–2, which
> shows DQI tracking authorship on three of seven dimensions (t up to +6.1). *Accurate
> version:* the word "orthogonal" is too strong and should go, but everything built on the
> charge fails. The stage-2 effects are tiny — respect_groups at t +6.1 over n = 682 is
> d ≈ 0.23, an AUC around 0.55–0.60 against this study's Opus screen at 0.951 — so "merely a
> worse detector" is an accurate description; part of the association is the r = +0.758
> leakage the study discloses; and the sign is positive, so nobody could operate DQI as a
> detector without flagging the best speeches in the chamber. The power objection is also
> inverted: the three dimensions where DQI tracks the label have stage-3 MDEs of 0.224, 0.185
> and 0.123, all *below* the effects they would have to miss; the wide cells are on dimensions
> with no association to detect. *Fix:* replace "orthogonal" with "not a usable provenance
> proxy", quote the CIs, and add a power bullet to §5.

**Status and staleness:** Live in its narrow wording point; the passage has changed
around it. The 2026-08-19 Q5 closure rewrote §8.3's *support* — from repeat-pass
reliability statistics to validity evidence (published-coding anchors, the
respect_groups quarantine, the AI-guess/quality dissociation) — and §8.3 also now
cites the paired evasion arms only as "a separate, secondary reassurance," resting the
case on stages 1–2 plus 5–6 (the M10 fix, 2026-08-16). But the two sentences X4 targets
survive verbatim: "quality assessment is orthogonal to provenance" and "Had DQI tracked
authorship, it would merely be a worse detector; because it does not, it measures the
thing anyone actually wanted to know" — and "because it does not" still shares the
paper with a table showing that on three of seven dimensions it does, weakly and
positively. The review's own verification defangs the deep version of the charge (the
associations are d ≈ 0.23, partly judge leakage, positive-signed — a detector built on
them would flag the chamber's best speeches; and the power objection inverts), so what
remains is exactly the one-word overclaim the review conceded. The proposed §5 power
bullet was not added, though the MDE-vs-headline-effect calibration now lives in §4.9.
One further same-day development (2026-08-21, commit c5562bf, Q9 closed per Matthew):
the stage-1 respect_groups cell now carries footnote r49m disclosing that it is the one
starred cell failing Benjamini–Hochberg correction (q = 0.106 across the table's
fourteen cells, every other starred cell q < 0.003, stage 2's version q < 0.0001) —
which sharpens the picture X4 argues over: the weakest stage-1 association is now
flagged in place while the stage-2 external-label associations stand untouched.

**The decision to make:** Either soften the sentence to the review's formulation —
"not a usable provenance proxy" (the associations are too weak, partly leakage, and
positive-signed) — or keep "orthogonal" as a deliberate strong claim now re-founded on
validity evidence, accepting that a referee holding the stage-2 table can call it
literally false. Separately: add the §5 power bullet or rule §4.9's Q3 statement
sufficient.

---

## X5 — §7 omits the work the study's own documents call closest

**Context, from zero:** §7 (Related work) currently discusses exactly two comparators:
Rice 2026 (Substack, Australian federal Parliament, found no post-ChatGPT inflection)
and Pimlico Journal 2025 (pseudonymous magazine piece, UK Commons, asserted an
increase). But the study's own documents name a third, closer effort: Suvanto,
McGlinchey, Barclay & Wahde (arXiv:2606.14209, June 2026) — UK Parliament *written
statements* plus Swedish Riksdag *motions* (written text; they deliberately avoided
transcribed speech), an interpretable n-gram classifier ("ICON") with its false-positive
rate measured on a pre-LLM holdout, finding "a steady increase in undisclosed LLM use …
from 2022 onwards." The pilot memo (`PILOT.md`) calls it "the closest work"; the
write-up's own future-work list mirrors it. Also absent from the draft: ParliaBench
(Koniaris et al., LREC 2026, an LLM-generated-parliamentary-speech benchmark), a
Mexican Congress result, and NCSL RELACS 2026's survey finding that 55% of US
legislative staff use generative AI (NCSL = the US National Conference of State
Legislatures). `VENUES.md` is a venue survey Matthew commissioned on 2026-08-18 —
a week *after* the review — which independently reached the same conclusion.

**The paper/document text under challenge (current):** §7's scope sentence,
`S10-WRITEUP-DRAFT.md`:2050–2054:

> Two prior efforts ran comparable designs on chambers in this corpus and
> reached opposite conclusions. **Neither used a calibrated commercial
> detector, and neither is peer-reviewed** — one is a Substack post, the other a
> pseudonymous magazine piece. Details and primary-source verification in
> `PRIOR_ART.md`.

Suvanto appears in the draft only in future work, `S10-WRITEUP-DRAFT.md`:2473–2479
(§8.6 item 5): "**The written arm of the US Congressional Record.** Extensions of
Remarks is separable from floor speech and is currently dropped at extraction
(`us/us_extract.py`). It mirrors the closest prior work directly — Suvanto et al.
studied *written* parliamentary text and explicitly avoided transcribed speech — so
running it turns a contrast of methods into a head-to-head on comparable material."
Neither "ParliaBench" nor "NCSL" appears anywhere in the draft; §6 (draft:2029–2044)
carries no staff-adoption figure. The supporting documents: `PILOT.md`:438–439
("**Suvanto, McGlinchey, Barclay & Wahde, arXiv:2606.14209 (June 2026)** — the closest
work…"), `PILOT.md`:455 ("NCSL RELACS 2026: 55% of US legislative staff use genAI."),
and `VENUES.md`:15 (table row calling 2606.14209 "**Closest competitor.**"),
`VENUES.md`:18–25 ("**Competitor read:** 2606.14209 confirms the phenomenon in two
chambers with a different detector family and stops at prevalence… It should be cited
in §7 related work; it also means the prevalence-alone claim is no longer novel, which
strengthens the case for submitting the integrated study rather than slicing it."),
and `VENUES.md`:60 ("Cite 2606.14209 and ParliaBench in §7 now, before any
submission.").

**The review's finding (verbatim):**

> **X5. §7 omits the work the study's own documents call closest.** *PARTIAL.* `PILOT.md`:437
> records Suvanto, McGlinchey, Barclay & Wahde (arXiv:2606.14209) as "the closest work" — UK
> Parliament + Swedish Riksdag, an interpretable classifier with an FP rate measured on a
> 2021–mid-2022 holdout, finding "a steady increase in undisclosed LLM use … from 2022
> onwards" — and §8.6 item 5 calls it "the closest prior work", while §7 names only Rice and
> Pimlico and emphasises that both are not peer-reviewed. Also dropped: the Mexican Congress
> result and NCSL RELACS 2026's finding that 55% of US legislative staff use generative AI.
> *Accurate version:* §7's scope sentence is "Two prior efforts ran comparable designs **on
> chambers in this corpus** and reached **opposite** conclusions", and Suvanto fails all three
> conjuncts — written parliamentary text with transcribed speech explicitly avoided, the
> Riksdag absent from the corpus, and a conclusion that *agrees* with S10. "Omits" is also
> false at document level: lines 970–974 cite it by name and propose a head-to-head. *Fix:*
> name Suvanto in §7 even to distinguish it, and use the NCSL 55% figure in §6 as an external
> plausibility anchor.

**Status and staleness:** Still live and now externally reinforced. §7 is unchanged
since the review: Rice and Pimlico only, no Suvanto, no ParliaBench, no NCSL. The
review's mitigation — §7's scope sentence is honestly scoped and Suvanto fails all
three of its conjuncts, and the draft does cite Suvanto in future work (the passage the
review saw at lines 970–974 is today's §8.6 item 5 at 2473–2479) — still holds. What
changed is the pressure: VENUES.md, written 2026-08-18 for submission planning,
flatly instructs citing both 2606.14209 and ParliaBench in §7 before any submission,
and adds a strategic reason (Suvanto makes prevalence-alone non-novel, which argues for
the integrated submission). So the review and the venue survey independently converge
on the same edit.

**The decision to make:** Add Suvanto (and ParliaBench) to §7 — cited to be
distinguished: written text vs transcribed speech, different chambers, agreeing
conclusion — which likely means widening or splitting §7's scope sentence; and decide
separately whether NCSL's 55% staff-adoption figure enters §6 as an external
plausibility anchor. The alternative of leaving §7 as-is contradicts the project's own
build-on-published-work convention and VENUES.md's pre-submission checklist.

---

## X6 — Neither prior comparator's chamber carries an S10 prevalence estimate

**Context, from zero:** The two prior efforts §7 answers are Rice 2026, who measured
the Australian *Commonwealth* (federal) Parliament, and Pimlico Journal 2025, who
measured the UK House of Commons. S10's corpus contains six Australian *state* chambers
(NSW, QLD, SA, TAS, VIC, WA — no federal Australia) and, at review time, ran its
prevalence panel (§4.2, the per-chamber machine-share table) over 19 chambers that did
not include the UK Commons — the UK appeared only in §2's corpus table and in §4.5's
long-run register series (a descriptive lexical time series back to 1985, the same
method family as Pimlico's z-scores). The review asked whether S10 can claim to answer
either author on their own chamber. Since the review, the prevalence panel was rebuilt
(2026-08-13): it now covers 20 chambers *including* the UK Commons. A related finding,
P8, flagged §2's "Nineteen chambers" sentence sitting over a table whose rows sum to
22; X6's fix defers to P8 for that sentence.

**The paper/document text under challenge (current):** `S10-WRITEUP-DRAFT.md`:46 (§2,
still unchanged): "Nineteen chambers across four countries, extracted from official
Hansard and the Congressional Record:" — above a table whose rows sum to 22 (9 Canada +
6 Australia + 5 UK/Ireland + 2 US). §7's comparator table (draft:2056–2061) is headed:

```
| | Rice 2026 (Australian federal) | Pimlico Journal 2025 (UK Commons) |
| corpus | 124,734 speeches, 2018– | UK Commons |
```

The current §4.2 panel (draft:211–212): "**Pooled 9.03% of words [8.00%, 10.08%]** —
65,795 machine-written words of 728,998 across 3,519 segments in 20 chambers, excluding
regime-flagged TAS." Its table now carries a UK row (draft:248): "| NS | 10.0% | [5.4,
15.2] | | UK | 2.5% | [0.7, 4.8] |" — the review-quoted predicate "has no row in §4.2"
no longer exists. §4.5 (draft:511) still opens: "Descriptive series (§3.3), UK Commons
extended back to 1985." Federal Australia still appears nowhere in §4.2, and §7 nowhere
says Rice's chamber is outside the corpus.

**The review's finding (verbatim):**

> **X6. Neither prior comparator's chamber carries an S10 prevalence estimate.** *PARTIAL.*
> Rice's corpus is the Australian *Commonwealth* Parliament; S10 holds six Australian *state*
> chambers and the policy scan lists federal Australia as out-of-scope background. Pimlico's
> is the UK House of Commons, which appears in §2's table but has no row in §4.2. *Accurate
> version:* right about Rice, wrong about Pimlico. UK Commons carries §4.5's descriptive
> series back to 1985, the same lexical-frequency method family as Pimlico's z-scores, so for
> Pimlico the comparator is matched on chamber *and* method; absence from the prevalence panel
> is irrelevant because Pimlico reports no prevalence estimate. Note also that §7's answer to
> Rice never rests on chamber matching — it is an instrument argument — and PRIOR_ART already
> states the non-comparability outright. *Fix:* say Rice measures a chamber S10 does not
> cover; fix the "Nineteen chambers" sentence (see **P8**).

**Status and staleness:** Split. The Pimlico half is doubly moot: the review already
rejected it (matched on chamber and method via §4.5, and Pimlico reports no prevalence
estimate to compare against), and the 2026-08-13 panel expansion has since given the UK
Commons an actual §4.2 prevalence row (2.5% [0.7, 4.8]) — scored end-to-end on Pangram
4 and verified 360/360 against the earlier arm. The Rice half is still live: no federal
Australian estimate exists anywhere in the study, and §7 still does not say so
(PRIOR_ART states the non-comparability, but the paper itself is silent). The
cross-referenced P8 fix is also still unapplied, and staler than at review time: §2's
"Nineteen chambers" (draft:46) now sits over a 22-row corpus table *and* disagrees with
§4.2's "20 chambers" pooled panel.

**The decision to make:** One clause in §7 stating that Rice's chamber — federal
Australia — is not in S10's corpus, so the answer to him is an instrument argument, not
a re-measurement; and repair §2's chamber-count sentence to the current design (P8's
fix). The Pimlico side needs nothing.

---

## X7 — §5 states an upward bias while a downward one was measured

**Context, from zero:** At review time S10's headline prevalence (12.4%) was a share of
*segments* — text windows the study's own packer cuts speeches into — sampled with a
120-word minimum so the detector had enough text. That floor is not innocent: Pangram's
flag rate rises steeply with segment length, and in the one chamber where the excluded
50–119-word band was measured (federal Canada) it came back at 2.5% against the long
band's 17.5%, implying the long-band figure overstated the corpus rate by ~1.7×
segment-weighted (~1.25× word-weighted). METHODOLOGY §5.0a documented this ("Segment
length is a confound, and it bit us"), but §5 (Limits) stated only the opposite
direction — "Prevalence is a floor," i.e. the truth can only be higher. M7 is the
methods-block review item with the full treatment. Between 2026-08-12 and 2026-08-13,
after the review, the study rebuilt the estimate: word-weighted became the primary and
only measure, the sampling floor dropped to 50 words (Pangram's own minimum readable
length) with all bands sampled at a uniform rate, and Mixed verdicts weighted by their
measured AI fraction.

**The paper/document text under challenge (current):** §5's floor bullet is unchanged in
direction (`S10-WRITEUP-DRAFT.md`:1940–1944, quoted in full under X1). But the design it
described is gone. `S10-WRITEUP-DRAFT.md`:209–221 (§4.2):

> ### 4.2 Prevalence: 9.0% of words, with an elevenfold spread
>
> **Pooled 9.03% of words [8.00%, 10.08%]** — 65,795 machine-written words of
> 728,998 across 3,519 segments in 20 chambers, excluding regime-flagged TAS.
>
> Every figure below is the share of *what was said* that is machine-drafted,
> over the whole of the record Pangram will read.
>
> *Weighted by words, because a segment is not a natural unit.* …

`S10-WRITEUP-DRAFT.md`:65–68 (§2): "Segments are member-authored, English-original,
non-chair, and 50 words or longer — the whole of the record Pangram will read. Sampling
is at a uniform rate across segment lengths, so the sample reproduces the corpus's own
length mix and the pooled estimate needs no length weights." `METHODOLOGY.md`:884–892
(§5.0a): "**Superseded 2026-08-13.** This table is the 2026-08-02 four-chamber arm …
The study now samples the short and over-360 bands at the SAME rate as the long band,
so the combined sample is self-weighting and needs no reweighting constants at all
(`build_shortband.py`, `banded_prevalence.py`). … The segment-weighted column that
stood here has been removed rather than updated: the study reports one weighting."
`METHODOLOGY.md`:896–899 retains the New Brunswick contrast ("New Brunswick needed no
such correction — its sample was 16% short segments against 13.9% in its pool…"). The
remaining truly unreachable text is bounded at `METHODOLOGY.md`:823–827: "A
word-weighted rate `r` measured on the reachable 94.7% bounds the true corpus rate to
`[0.947r, 0.947r + 0.053]` … At r = 9.03% that is **[8.6%, 13.8%]**."

**The review's finding (verbatim):**

> **X7. §5 states one direction of bias when the study has measured a downward one.**
> *PARTIAL.* Limits offers only "Prevalence is a floor", while METHODOLOGY §5.0a documents the
> length-band overstatement. See **M7** for the full treatment. *Accurate version and
> magnitude:* the 1.7× is Canada's *segment*-weighted correction; for "what share of the
> record", the word-weighted correction is 17.5 → 14.0, i.e. 1.25×. Inside the panel the
> pattern is a step, not a gradient — 8.3% at 120–199, 14.6% at 200–279, 14.3% at 280–360 —
> saturating above 200 words, so extrapolation to the unmeasured sub-120 band rests on one
> pilot chamber. METHODOLOGY also records that New Brunswick "needed no such correction", so
> the Canadian 1.7× is not a corpus constant. *Fix:* add a §5 bullet stating that the 120-word
> floor selects toward longer, more-flagged segments, that the one chamber where the excluded
> band was measured implies a 1.25–1.7× downward correction, and that this runs against the
> evasion floor. State the unit: 12.4% is a share of *segments*.

**Status and staleness:** Moot — superseded by redesign rather than by a caveat. Every
element of the proposed fix was answered structurally: the 120-word floor no longer
exists (sampling now runs to Pangram's own 50-word minimum, at a uniform rate across
lengths, so the sample is self-weighting and the "excluded band" is measured rather
than extrapolated); the unit is words and is stated in the section title itself
("9.0% of words"); and the review's preferred word-weighted number *is* now the
headline. The review-quoted sentence "12.4% is a share of *segments*" has no referent
left: 12.4% appears nowhere in the current draft (it survives only in the stale work-log
register — see X8). What remains excluded is text Pangram cannot read at all (sub-50-word
plus translated plus over-360 remnants, 5.3% of words), and that residual is bounded
explicitly in METHODOLOGY ([8.6%, 13.8%] at the 9.03% point estimate) — a different and
smaller point than the one X7 raised. §5 carries no bullet pointing at that bracket.

**The decision to make:** Nothing is required on the review's own terms. The one
optional carry-forward: a single §5 line noting that the pooled figure covers the
94.7% of words Pangram can read, with METHODOLOGY's [8.6%, 13.8%] bracket, so Limits
states both directions of residual uncertainty in one place.

---

## X8 — The register drops a caveat the work log mandates

**Context, from zero:** `studies-and-work-log.md` (repo root) is the project's study
register and dated work log: each study has a findings summary ("the register") that
sessions read as ground truth, plus dated log entries recording work as it happened.
S10's bypass arm measured detector evasion two ways: per detector submission (8.5% of
variants clear Pangram) and per target (a speech walked past the detector within ≤18
attempts). Against the 2.31% one-shot rate of 13 commercial "humanizer" evasion
services in Pangram's own report, the per-target rate gives the "~10×" headline. Because
the two quantities differ (one-shot vs 18 attempts), the dated log entry that first
reported the result mandated: "state this whenever the 10× is used." The review found
the register's own findings bullet violates the mandate. Since the review, the numbers
themselves moved twice in the draft: the per-target denominator was corrected on
2026-08-12 (review item M4: 24.6% → 22.5%, 10.6× → 9.8×), and the prevalence headline
was rebuilt on 2026-08-13 (12.4% of segments → 9.0% of words). The register was never
updated for either.

**The paper/document text under challenge (current):** `studies-and-work-log.md`:165–172
(the S10 register bullet, unchanged since the review):

> - **The detector is evadable under effort.** An off-the-shelf model in a
>   rewrite loop — no fine-tuning, no detector access — clears Pangram on
>   **8.5% of variants** and **24.6% of targets**, about **10.6×** the 2.31%
>   that 13 commercial humanizer services achieve. Evasion costs **nothing** in
>   deliberative quality (7 DQI dimensions null across 63 paired grades), but it
>   is not cheap: a single "sound human" prompt *raises* the score.
> - So 12.4% is a **floor**, and detection is a norms instrument rather than a
>   security one.

The mandate, inside the dated 2026-08-10 entry (`studies-and-work-log.md`:525): "…
Like-for-like on single attempts the multiple is 3.7× (2.31% is one-shot, 24.6% allows
≤18 attempts — state this whenever the 10× is used)." The correction the register never
absorbed, dated 2026-08-12 (`studies-and-work-log.md`:532): "**22.5%, not 24.6%; 9.8×,
not 10.6×.** The denominator counted targets that produced a variant clearing the
search's own submission gate … §8's argument is untouched; 9.8× is still an order of
magnitude." The write-up itself carries the caveat prominently
(`S10-WRITEUP-DRAFT.md`:1541–1543): "One asymmetry to keep visible: the 2.31% is a
**one-shot** rate, while 22.5% allows up to eighteen attempts. Like-for-like on single
detector submissions the multiple is **3.7×** (8.5% against 2.31%)."

**The review's finding (verbatim):**

> **X8. The register drops a caveat the work log mandates.** *PARTIAL.*
> `studies-and-work-log.md`:462 says "state this whenever the 10x is used"; the register
> bullet at 160–165 puts both rates in one sentence followed by a single multiple, with no
> such statement. *Accurate version:* the bullet disambiguates arithmetically (24.6/2.31 =
> 10.65 vs 8.5/2.31 = 3.68), both operands are present, and the register's own Artifacts line
> points at the write-up, which carries the caveat twice in its sharpest form. Documentation
> hygiene in an internal index. *Fix:* put the multiple next to the rate it belongs to.

**Status and staleness:** Still live, and the situation has worsened from
missing-caveat to stale-numbers. The review's charge (the bullet pairs one multiple
with two rates and omits the mandated one-shot-vs-18-attempts statement) still holds of
lines 165–170, but the bullet's numbers are now also simply wrong by the project's own
record: 24.6% and 10.6× were corrected to 22.5% and 9.8× in the draft on 2026-08-12
(the entry at line 532 records the correction — the register bullet above it was never
touched), and "12.4%" (line 171) was replaced by the 9.0%-of-words headline on
2026-08-13. The staleness is register-wide, not local: the same S10 findings block
still says "Pooled 12.4% [11.1, 13.8] across 19 chambers", "A sevenfold spread … US
House **15.0%** … NSW 23.3%" (lines ~130–137) against today's 9.03%, elevenfold,
US House 12.1%, NSW 19.8%. The review's mitigation (the Artifacts line at ~174 points
at the write-up, which is correct and carries the caveat) still applies.

**The decision to make:** Rewrite the register's S10 findings block to the current
numbers with the caveat inline (9.0% of words, elevenfold 1.8–19.8%, 22.5% per target /
9.8× with "≤18 attempts vs one-shot" stated, 3.7× like-for-like), or explicitly stamp
the block as a dated snapshot that defers to the write-up. The review's minimal fix —
put each multiple next to the rate it belongs to — is now insufficient on its own,
because the rates themselves are superseded.

---

## X9 — "Refuting" in the register vs "run the wrong way" in the write-up

**Context, from zero:** One of S10's register-arm findings is a generational gradient:
members born later use more of the AI-associated register, at +1.05 per 1,000 words per
decade of birth (t ≈ 8.5, clustered on member), *net of* calendar period. Two rival
explanations are compositional: professionalisation (chambers filling with
communications/PR/law professionals) and educational expansion (more postsecondary
degrees). `formation_window.py` tests these by adding occupation and education controls
to the cohort regression; both controls carry negative coefficients (postsecondary
−0.499, communications-PR-journalism −0.646) and adding them *strengthens* the cohort
term (+1.05 → +1.14) — the opposite of what a selection story predicts. The study
register (`studies-and-work-log.md`, the project's per-study findings summary)
compressed this to "refuting professionalisation and educational expansion," while the
write-up's future-work list separately keeps a *different, era-wide* version of the
professionalisation rival — message discipline changing all members' speech regardless
of background — explicitly "live and unmeasured" (§8.6 item 11). The review objected to
"refuting"; its verification found the alleged self-contradiction conflates the two
rivals but conceded the word.

**The paper/document text under challenge (current):** `studies-and-work-log.md`:144–150
(register bullet; the challenged words at 149–150):

> - The rise is **generational as well as period-wide**: regressing the
>   member-year register rate on spoken year and birth year together (chamber
>   FE, 13 chambers, 46,515 member-years), birth cohort predicts **+0.95 per
>   1,000 per decade (t 28)** net of calendar period (+1.24/decade), and is the
>   stronger organiser in 10 of 13 chambers. Within province and year the
>   gradient is +1.05/decade (t ≈ 8.5, clustered). Occupation and education run
>   the *wrong* way, refuting professionalisation and educational expansion.

The write-up's own calibrated wording, which the review's fix says the register should
match — `S10-WRITEUP-DRAFT.md`:673–674: "**The gradient holds within year and province
at +1.05 per 1,000 per decade** (t ≈ 8.5, clustered on member), unmoved by occupation
and education controls, which *strengthen* it rather than explain it away (§4.6a)." —
and footnote r46b (`S10-WRITEUP-DRAFT.md`:701–708): "…birth-decade coefficient +1.05
per 1,000 words per decade, t = +8.46 unadjusted and +9.23 with occupation and
education controls. The controls *strengthen* the cohort term (coefficient +1.05 →
+1.14), which is why they are reported as running the wrong way for a selection
story." The still-live rival, `S10-WRITEUP-DRAFT.md`:2512–2518 (§8.6 item 11): "…the
**professionalised-communications** rival — message discipline and clip-ready speech
over the same years — has only ever been tested indirectly … It is live and
unmeasured."

**The review's finding (verbatim):**

> **X9. The register says "refuting" where the write-up says "run the wrong way".** *PARTIAL.*
> Register: "Occupation and education both run the *wrong* way, refuting professionalisation
> and educational expansion." A cohort coefficient surviving two crude categorical controls
> fails to explain the rivals away; it does not refute them, and §8.6 item 11 records the
> professionalised-communications rival as "live and unmeasured". *Accurate version:*
> "refuting" is a one-word overreach, but the alleged contradiction conflates two rivals.
> `formation_window.py` names *compositional* rivals (occupational selection, educational
> expansion), which are tested; §8.6 item 11's live rival is an *era-wide* norm change
> affecting all members regardless of background, which no compositional control can address
> and which §8.6 correctly labels unmeasured. The result is also directionally stronger than
> the finding allows: postsecondary is −0.499 and communications-PR-journalism −0.646, i.e.
> both rivals predict the wrong sign on their own key coefficients. *Fix:* match the register
> wording to footnote r46b.

**Status and staleness:** Still live, unchanged on both sides: the register still says
"refuting" (work log:150), and the write-up's calibrated versions (draft:673–674,
r46b at 701–708, §8.6 item 11 at 2512–2518) still read as the review described, so the
one-word register fix remains the entire item. A dated log entry (work log:489,
2026-08-07) also uses "refuted"; dated entries are the historical record and arguably
should stand as written. Note the review's verification cuts *for* the study on
substance — both rivals' own coefficients carry the wrong sign, so the compositional
versions are genuinely disconfirmed; the overreach is only that "refuting" reads as
covering the era-wide variant that §8.6 keeps open.

**The decision to make:** Change the register bullet's "refuting professionalisation
and educational expansion" to r46b's formulation — the controls run the wrong way for a
selection story and strengthen the cohort term — leaving the era-wide
professionalised-communications rival visibly live; leave dated log entries as record.

---

## X10 — §6 and its own policy scan disagree about the null

**Context, from zero:** §6 (Policy context) summarizes `ai_policy_scan.md`, an
August-2026 scan of AI-usage rules across 22 legislative chambers, which recorded for
each chamber whether any instrument governs AI-drafted speech, at what confidence
(High = primary documents retrieved and searched; partial = coverage gaps). The scan
found no chamber anywhere requiring disclosure of AI-drafted text in the record. §6
compresses the scan's confidence tiers into one sentence naming Saskatchewan as "the
one solid null" — but the scan itself says Nova Scotia and Newfoundland & Labrador are
equivalent nulls (exhaustive primary-document searches, zero AI mentions) and lists
thirteen chambers at High confidence, six of them no-policy-found. The review alleged
four §6-vs-scan mismatches; its verification upheld exactly this one. (The Sejm is the
Polish parliament — an EU-disclaimer datapoint the reviewer floated as an addition;
§8.6 item 8 is the future-work item on non-English instruments that would be needed to
use it.)

**The paper/document text under challenge (current):** `S10-WRITEUP-DRAFT.md`:2029–2044
(§6 in full):

> A 22-chamber scan found **zero chambers requiring AI-drafted text to be
> disclosed in the record, and none forbidding AI drafting.** Where rules
> exist they are IT-security instruments issued by Clerks and CIOs, not rules
> of authorship. The structural pattern: **where a Clerk governs staff, rules
> are detailed; where members govern themselves, there is nothing.**
>
> Strictest is the US House (HITPOL 8). The UK is the only chamber to address
> the question directly, and resolves it permissively — AI-generated content in
> proceedings is the member's own, "protected by privilege regardless of the
> tools used to produce that material." The only Speaker's ruling anywhere in
> scope is Alberta, 2 December 2025: asked to extend the anti-staff-written-
> speeches rule to AI, Speaker Cooper ruled **"ChatGPT is not staff."**
>
> Coverage is partial for NI, Manitoba, PEI and South Australia — absence of
> evidence, not evidence of absence. Saskatchewan is the one solid null.
> (`ai_policy_scan.md`; figures unverified against primary sources.)

The scan's own text: `ai_policy_scan.md`:76–78: "**Loosest: Saskatchewan, and the
Canadian provinces generally.** Saskatchewan has no instrument, no [debate, no
accusation] … Nova Scotia and Newfoundland and Labrador are equivalent.";
`ai_policy_scan.md`:180: "**Saskatchewan — the clean null.** No instrument, no debate,
no accusation, no mention."; the no-policy-found table rows at lines 43/46/47
(Saskatchewan: "All 21 BOIE Directives: zero AI mentions"; Nova Scotia: "HAMC policies,
annotated regulations and 5 sets of minutes: zero AI mentions"; Newfoundland &
Labrador: "25 published policies + Management Commission papers (~125k words): zero AI
mentions"); and the High-confidence list of thirteen chambers at line 242.

**The review's finding (verbatim):**

> **X10. §6 mischaracterises its own policy scan, in both directions.** *PARTIAL.* Four
> mismatches were alleged; one holds. **Holds:** "Saskatchewan is the one solid null" is
> contradicted by `ai_policy_scan.md`, which says in the same breath that Nova Scotia and
> Newfoundland & Labrador are equivalent and lists thirteen chambers at High confidence, six
> of them no-policy-found after exhaustive searches (NL: "25 published policies + Management
> Commission papers (~125k words): zero AI mentions"). **Does not hold:** "figures unverified
> against primary sources" is a conservative posture, not a contradiction; §6 says "a
> 22-chamber scan", not "of the S10 corpus", so the PEI-for-NB substitution is a defect in the
> scan's title; and §6's actual words are "requiring AI-drafted text to be disclosed **in the
> record**", which is precisely the narrow claim the scan supports. The Sejm 4-of-9 EU
> disclaimer datapoint is a reasonable addition but is not a usable route to ground truth
> without the non-English instrument §8.6 item 8 already names. *Fix:* correct "the one solid
> null" to name the six.

**Status and staleness:** Still live and unchanged: §6 reads today exactly as reviewed
(the sentence sits at draft:2043), and the scan's contradicting passages are likewise
unchanged. This is a one-sentence understatement of the study's own evidence — the scan
supports a stronger claim (at least three exhaustively-searched clean nulls, six
no-policy-found at High confidence) than §6 makes. The three rejected sub-points stay
rejected on the review's own verification.

**The decision to make:** Replace "Saskatchewan is the one solid null" with a sentence
matching the scan — e.g. naming Saskatchewan, Nova Scotia and Newfoundland & Labrador
as equivalent solid nulls among six High-confidence no-policy-found chambers. The only
alternative is deliberate conservatism, but here the conservative reading contradicts
the cited source document rather than hedging it.

---

## X11 — §8.5 equates its residual with S17's imitation lag

**Context, from zero:** §8.5 is a discussion-section proposal, flagged in its own first
line as "the most promising direction, and the least developed": instead of policing
provenance, measure the *human contribution* to a text as the residual over what a
fully automated system would produce given the same task and context — with the
baseline deliberately moving as models improve, recording only *which* baseline each
measurement used. Its closing sentence ties that to S17, a separate study in this
project (the Nordhaus capture-ratio work) which measures the **imitation lag** — the
*duration*, in months, until an imitator reproduces a frontier AI capability (rate
λ = 1/L) — and finds it collapsing. The review ran four objections at §8.5; its
verification rejected three (one misquote, two addressed to a proposal already flagged
as undeveloped, with the study's own §3.2 silent-model-substitution incident actually
*supporting* baseline-recording) and upheld the fourth: a person-vs-machine capability
gap at a moment is not the same *quantity* as a duration, however related their causes.

**The paper/document text under challenge (current):** `S10-WRITEUP-DRAFT.md`:2263–2283
(§8.5 in full — unchanged since the review):

> ### 8.5 Measuring the human contribution against an automated counterpart
>
> The most promising direction, and the least developed. Generate what a fully
> automated system would produce given the same task and context; the human
> contribution is the residual. This is the marginal-product definition done
> properly, and it is measurable today.
>
> **The baseline must move.** The obvious objection is that the residual shrinks
> as models improve, and the obvious fix — freeze a model vintage — is wrong. It
> reproduces the error the current debate already makes, where contributions
> relative to dumb computers are treated as obviously legitimate and anything
> touching an LLM as obviously suspect. **The goalpost should move by
> construction, always incorporating the latest technology**, because that is
> what contribution means: what you added over the best available alternative. A
> shrinking residual is correct measurement, not measurement decay. Nobody
> credits long division done by hand.
>
> The one thing worth recording is *which* baseline a given measurement was taken
> against — metadata that keeps an old measurement interpretable, not a fixed
> target. This is the same quantity S17 measures as the imitation lag, and the
> same reason it is collapsing.

**The review's finding (verbatim):**

> **X11. §8.5's moving-baseline proposal does not price its own costs, and equates two
> different quantities.** *PARTIAL.* Four sub-points: non-comparability across a moving
> baseline; non-reproducibility of a deprecating, access-gated baseline (with §3.2's silent
> model substitution as the in-study demonstration); task/context specification being human
> contribution absorbed into the counterfactual; and the claim that this is "the same quantity
> S17 measures as the imitation lag". *Accurate version:* the first sub-point misquotes the
> text, which claims interpretability under a label, not comparability. The second and third
> are legitimate but are addressed to a proposal the section explicitly flags as "the most
> promising direction, and the least developed", and the §3.2 anecdote cuts the other way —
> what bit the study was a *silent* substitution, exactly what recording the baseline
> prevents. **The fourth holds:** S17 measures a *duration* (months until an imitator reaches
> frontier capability, λ = 1/L), while §8.5's residual is a capability gap between a person
> and a machine. *Fix:* replace "the same quantity S17 measures" with "moves for the same
> reason as S17's imitation lag".

**Status and staleness:** Still live and unchanged: §8.5's text is byte-identical to
what the review saw, including the challenged final sentence at draft:2281–2282. The
upheld defect is a category error in one phrase — "the same quantity" — between a gap
and a duration; the sentence's second half ("the same reason it is collapsing") is the
part the review endorses.

**The decision to make:** Apply the review's one-phrase fix — "This moves for the same
reason as S17's imitation lag, and is collapsing for the same reason" or equivalent —
or cut the S17 sentence entirely; keeping "the same quantity" invites the correction
from any reader who knows S17.

---

## X12 — Five standard referee objections, and which §5 still lacks

**Context, from zero:** §5 (Limits) is the write-up's caveat list. The review checked it
against five objections a statistics referee raises by default: (i) **clustering** —
whether confidence intervals account for correlated observations; (ii) **pooling
weights** — a pooled rate built from roughly equal per-chamber draws is the *average
chamber's* rate, not a population rate over all speech; (iii) **multiplicity** — a
"spread" claim across many chambers invites a correction for multiple comparisons,
answerable with one omnibus heterogeneity test; (iv) a **two-point design** — no trend
claim from just pre/post; (v) **single-scan specificity** — a zero-false-positive
result measured once. Plus (vi) a wording issue: §5 anchors the LLM judge's reliability
to "the published human inter-coder bar," a 0.716 correlation, and the review checked
whether that anchor is dimension-matched. Context on what changed after the review: the
prevalence arm was rebuilt 2026-08-13 (word-weighted 9.03% over 20 chambers, cluster
bootstrap intervals, replacing the segment-weighted 12.4% over 19 with Wilson
intervals), and §5 gained a long effect-size calibration bullet (2026-08-18, commit
c82d999 — Gignac-Szodorai and Funder-Ozer benchmarks for the covariate effects) that is
unrelated to these five.

**The paper/document text under challenge (current):** §5's bullet list
(draft:1938–2027) today contains bullets on: prevalence-is-a-floor, evasion effort,
Tasmania, Mixed pooling, permeation, register-not-substance, cohort mechanism, no
ground truth, single detector, control-genre coverage, judge leakage, genre-cell
representativeness, LLM-graded quality, and covariate effect sizes. None of the five
objections has a bullet. Per sub-point:

(i) Clustering — superseded in the design itself. `S10-WRITEUP-DRAFT.md`:251–255:
"Intervals are cluster bootstraps over segments, not Wilson intervals: the estimator is
a ratio of two random sums whose numerator and denominator move together…" and the
bypass arm now states its clustering correction outright (draft:1580–1592: "…the
cluster-robust standard error is 2.44 percentage points against a naive 1.30, a
**design effect of 3.55**, so the effective sample is about 130 variants and not 461").

(ii) Pooling weights — still absent, and *less* disclosed than at review time: §2
(draft:57–68) no longer states the per-chamber draw size at all (the old "60 / 120 per
chamber" design line is gone; 120 survives only in a CA-FED footnote, draft:274), and
no sentence says the pooled 9.03% weights chambers roughly equally regardless of how
much speech each produces.

(iii) Multiplicity — still absent. The spread claim is now draft:257–259: "The spread
is the finding, not noise around a mean: chamber rates run from 1.8% to 19.8%, an
elevenfold range." No omnibus test is reported anywhere (no χ², no heterogeneity
statistic in the draft).

(iv) Two time points — the review rejected this one; the text it defends is unchanged:
Appendix B item 7 (draft:2901–2902): "**Pre-per-year prevalence point estimates** —
superseded by the per-year series and then by the 19-chamber panel." — retiring what
predated the per-year series, not the series.

(v) Single-scan specificity — the review rejected this one too; the defense is still in
§4.1 (draft:193–207): the New Brunswick rescore table, 60/60 pre-AI controls clean on
both Pangram 3 and Pangram 4.

(vi) The 0.716 anchor — now dimension-matched in both places:
`S10-WRITEUP-DRAFT.md`:1431–1433: "The rubric's repeat-pass reliability sits at
Spearman 0.68–0.91 per dimension, at or above the instrument's own published
inter-coder bar (justification r = 0.716)…" and `METHODOLOGY.md`:1967–1968 (§7,
rewritten 2026-08-19): "repeat-pass Spearman 0.68–0.91 per dimension, at or above the
published human inter-coder bar (their justification r = 0.716)".

**The review's finding (verbatim):**

> **X12. §5's limits list omits five standard referee objections — of which two are worth
> adding.** *PARTIAL.* Alleged: no clustering, equal-weight-per-chamber pooling, no
> multiplicity, a two-point design precluding any trend, and single-scan specificity; plus a
> wording issue on the repeat-pass band. *Accurate version:* (i) Clustering — the arithmetic
> reproduces (deff 1.296, [10.8, 13.9]) but answers a different estimand:
> `build_pangram_expansion.py` draws `rng.sample(...)`, a simple random sample of *segments*,
> for which the design-based variance carries no clustering term. (ii) **Pooling weights — this
> one stands and should be added:** 120 segments per chamber means 12.4% is the average
> chamber's rate, not a population rate; disclosed in §2 but worth a clause. (iii)
> Multiplicity — the heterogeneity claim survives an omnibus test needing no correction (χ² =
> 88.1 on 17 df, p = 1.4e-11) and NSW vs US Senate at p = 5.0e-6 clears Bonferroni over all
> 171 pairs; **reporting the omnibus test would make the spread claim multiplicity-proof on
> its face, and is worth adding.** (iv) Two time points — the evidentiary claim misreads
> Appendix B item 7, which retires the estimates that *predated* the per-year series, not the
> series; and 0/1,260 pre-AI against 12.4% post is itself a change measurement against a
> measured zero. (v) Single-scan specificity — 243 NB controls were scored on both Pangram 3
> and 4 with 60/60 both times, and 2,400 pre-LLM segments passed the Opus band screen with
> zero flags; the "11% instability" is 1 change across 39 rescans of texts deliberately chosen
> *at* the boundary. (vi) The 0.716 anchor is dimension-matched in `quality_methods.md`
> (justification: their 0.716 against this study's 0.83), so §5's sentence is defensible;
> METHODOLOGY:1407's one-line summary is the loose one. *Fix:* add the equal-allocation clause
> and the omnibus heterogeneity test.

**Status and staleness:** Split three ways, and the review's supporting numbers are now
stale throughout. Of the five alleged omissions: **(ii) pooling weights — still live**,
the equal-allocation clause was never added and §2's partial disclosure the review
credited has since disappeared; **(iii) multiplicity — still live in spirit**, no
omnibus test is reported, but the review's specific statistics (χ² = 88.1 on 17 df,
p = 1.4e-11; NSW vs US Senate p = 5.0e-6 over 171 pairs; deff 1.296 and [10.8, 13.9])
were all computed on the retired segment-weighted 19-chamber design — the panel is now
20 chambers, word-weighted, with different rates (NSW 23.3% → 19.8%, US Senate 3.3% →
1.8%), so the test would have to be recomputed under the new estimator before it could
be reported; **(i) clustering — superseded**: the review rejected it against the old
simple-random-sample design, and the rebuilt design now clusters anyway (bootstrap over
segments; bypass deff 3.55 stated in text); **(iv) and (v) — moot**, rejected by the
review's own verification, with the defending text (Appendix B item 7; the §4.1 NB
dual-scan) unchanged; **(vi) — resolved**: the draft was already dimension-matched and
METHODOLOGY's loose one-liner was eliminated in the 2026-08-19 §7 rewrite (dce04fe).
The §5 changes since the review (the effect-size calibration bullet added 2026-08-18;
reworded evasion bullets) touch none of the five.

**The decision to make:** Two additions if adopted, both small: a one-clause
equal-allocation disclosure (the pooled 9.03% averages near-equal per-chamber draws —
an average-chamber rate, not a speech-volume-weighted population rate), and an omnibus
heterogeneity test recomputed under the word-weighted estimator to make the elevenfold
spread claim multiplicity-proof on its face. The other three sub-points need nothing.
