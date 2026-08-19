# X block — the cross-cutting findings of the 2026-08-11 adversarial review

*Self-contained review file for Matthew: what "cross-cutting" means, the
review's twelve findings verbatim, then every paper section they target,
verbatim. **Status: none of the X items has been adjudicated or independently
verified yet** — verdict labels are the review's own; confirmations will run
per item as you review, same flow as the Q block.*

## What these refer to

The **cross-cutting block** collects findings that span sections rather than
attacking one arm: consistency between the write-up and its own METHODOLOGY /
work-log / register documents, the framing of §5 (Limits), §6 (Policy
context), §7 (Related work), and §8.5 (the moving-baseline proposal), plus
benchmark attributions and comparator coverage. Several are
documentation-consistency findings (two documents asserting different
things); a few are missing-caveat or selective-citation findings. Note X1
duplicates P1 (the Se corpus), which was **RESOLVED 2026-08-16** — the Se
number was removed entirely, so X1 should be checked against the current
text rather than the text the review saw.

---

## Part 1 — The review's findings, verbatim (REVIEW-2026-08-11.md §2.4, Cross-cutting)

#### Cross-cutting

**X1. The Se identity rests on a corpus the primary documents say was deleted, and §5 has no
sensitivity bullet.** *PARTIAL.* Duplicate of **P1**, raised independently by the
cross-cutting reviewer with two additions: `gen_se_corpus.py`'s own docstring says "treat
the resulting Se as a *pilot mechanism check*, not the study's Se", and `METHODOLOGY.md`
712–741 sets out the correct treatment (a one-sided floor with 1/Se an unknown multiplier,
tabulated 7.5% → 10.0% at Se = 0.75 and 25.0% at Se = 0.30) while naming the unmeasured
class — aide-drafted, member-revised, Hansard-edited — as the one that "actually dominates
Hansard". §5 Limits contains no sensitivity bullet at all, attributing the floor entirely to
evasion. *Accurate version:* because Sp = 1 is measured, τ = π/Se and Se ≤ 1 always, so
Se = 1.000 yields the *smallest* possible calibrated prevalence; at METHODOLOGY's own
replacement anchor (Se = 0.993) the figure is 12.5% against the reported 12.4%. Also, §3.4
line 164 ("Mistral synthetic control corpus | deleted | replaced by in-domain synthetic Se")
is self-contradictory, since the in-domain synthetic Se *is* that corpus. *Fix:* re-source
Se to the published anchors METHODOLOGY already names, and add the §5 bullet naming detector
sensitivity to edited text as the study's largest unmeasured quantity.

**X2. Two vendor rows are attributed to the wrong benchmark.** *PARTIAL.* In the Pangram 4
report, 2.86% (17/594) is Pangram 4's document-level FNR on the **Epoch AI Style Imitation**
benchmark (Table 23) and 9.09% is Originality.ai's on the same; the **Perkins** benchmark is
Table 22, reported as three-method mean accuracy (Pangram 4: 100.0% baseline, 94.1%
manipulated, i.e. ~5.9% miss; next best Copyleaks, not Originality.ai). Both
`S10-WRITEUP-DRAFT.md`:546 and `PRIOR_ART.md`:163-164 label them Perkins, in a table whose
stated purpose is naming quantities precisely. *Accurate version:* 2.86% is a correct
Pangram 4 vendor-reported FNR; only the benchmark name is wrong, and no claim changes. With
the real Perkins figure substituted the ordering is unchanged (0.34%, 0.43%, 2.31%, 2.86%,
5.9% all below 8.5%), and S10 never computes a multiple against Perkins — both multiples are
explicitly anchored to 2.31%. The "1.44×" replacement comparison is itself an unlicensed
unit conversion (mean accuracy → FNR). *Secondary point that stands:* 2.31% is
1 − (AI recall 97.69%), i.e. it counts Mixed as a miss, whereas S10 counts only Human as
success; the strictly matched vendor rate is 1 − 98.83% = 1.17%, which runs in the study's
favour. *Reproduce:* `pdftotext -layout` on arXiv:2607.27183, Tables 14, 22, 23. *Fix:*
relabel both rows, add the real Perkins row, and footnote the Mixed asymmetry.

**X3. The peer-review benchmark claim is selective.** *PARTIAL.* §7 says both Binoculars and
Fast-DetectGPT "fall to roughly 6% true-positive rate at 1% FPR" on "peer-review benchmarks"
(plural). Only one benchmark gives that: Sem-Detect (Table 27). On the Saha benchmark
(Table 28) Fast-DetectGPT scores 100.0/100.0/97.5 on the easy subset and 72.1/68.2/63.1 on
the hard subset, and `PRIOR_ART.md`:96 cites Saha's Binoculars numbers while omitting
Fast-DetectGPT's. *Accurate version:* two of the three sub-points fail. "Reproduced in the
Pangram 4 report" is natural English for "reprinted in", which is what Table 27's note
describes, and PRIOR_ART separately flags all Pangram rows as vendor-reported. And the claim
that non-commercial detectors match the commercial one collapses on the table's own
footnote: EditLens, Sem-Detect and Anchor all carry a dagger marking them as *tuned on
peer-review data*; among untuned detectors only Pangram clears 95. The conclusion also
holds — the claim is scoped to 1% FPR, which Table 28 does not report; MELD-eval gives
Binoculars 0.6% and Fast-DetectGPT 17.0% at that operating point; and Rice's primary
statistical detector is Binoculars, weak on both peer-review benchmarks. *Fix:* name
Sem-Detect, state the Saha split for Fast-DetectGPT, and keep the argument on Binoculars.

**X4. "Quality assessment is orthogonal to provenance" is contradicted by the paper it sits
in.** *PARTIAL.* §8.3 draws the substitution result from 63 pairs in which *both* members
are machine-touched text; the contrast that bears on provenance is §4.9 stages 1–2, which
shows DQI tracking authorship on three of seven dimensions (t up to +6.1). *Accurate
version:* the word "orthogonal" is too strong and should go, but everything built on the
charge fails. The stage-2 effects are tiny — respect_groups at t +6.1 over n = 682 is
d ≈ 0.23, an AUC around 0.55–0.60 against this study's Opus screen at 0.951 — so "merely a
worse detector" is an accurate description; part of the association is the r = +0.758
leakage the study discloses; and the sign is positive, so nobody could operate DQI as a
detector without flagging the best speeches in the chamber. The power objection is also
inverted: the three dimensions where DQI tracks the label have stage-3 MDEs of 0.224, 0.185
and 0.123, all *below* the effects they would have to miss; the wide cells are on dimensions
with no association to detect. *Fix:* replace "orthogonal" with "not a usable provenance
proxy", quote the CIs, and add a power bullet to §5.

**X5. §7 omits the work the study's own documents call closest.** *PARTIAL.* `PILOT.md`:437
records Suvanto, McGlinchey, Barclay & Wahde (arXiv:2606.14209) as "the closest work" — UK
Parliament + Swedish Riksdag, an interpretable classifier with an FP rate measured on a
2021–mid-2022 holdout, finding "a steady increase in undisclosed LLM use … from 2022
onwards" — and §8.6 item 5 calls it "the closest prior work", while §7 names only Rice and
Pimlico and emphasises that both are not peer-reviewed. Also dropped: the Mexican Congress
result and NCSL RELACS 2026's finding that 55% of US legislative staff use generative AI.
*Accurate version:* §7's scope sentence is "Two prior efforts ran comparable designs **on
chambers in this corpus** and reached **opposite** conclusions", and Suvanto fails all three
conjuncts — written parliamentary text with transcribed speech explicitly avoided, the
Riksdag absent from the corpus, and a conclusion that *agrees* with S10. "Omits" is also
false at document level: lines 970–974 cite it by name and propose a head-to-head. *Fix:*
name Suvanto in §7 even to distinguish it, and use the NCSL 55% figure in §6 as an external
plausibility anchor.

**X6. Neither prior comparator's chamber carries an S10 prevalence estimate.** *PARTIAL.*
Rice's corpus is the Australian *Commonwealth* Parliament; S10 holds six Australian *state*
chambers and the policy scan lists federal Australia as out-of-scope background. Pimlico's
is the UK House of Commons, which appears in §2's table but has no row in §4.2. *Accurate
version:* right about Rice, wrong about Pimlico. UK Commons carries §4.5's descriptive
series back to 1985, the same lexical-frequency method family as Pimlico's z-scores, so for
Pimlico the comparator is matched on chamber *and* method; absence from the prevalence panel
is irrelevant because Pimlico reports no prevalence estimate. Note also that §7's answer to
Rice never rests on chamber matching — it is an instrument argument — and PRIOR_ART already
states the non-comparability outright. *Fix:* say Rice measures a chamber S10 does not
cover; fix the "Nineteen chambers" sentence (see **P8**).

**X7. §5 states one direction of bias when the study has measured a downward one.**
*PARTIAL.* Limits offers only "Prevalence is a floor", while METHODOLOGY §5.0a documents the
length-band overstatement. See **M7** for the full treatment. *Accurate version and
magnitude:* the 1.7× is Canada's *segment*-weighted correction; for "what share of the
record", the word-weighted correction is 17.5 → 14.0, i.e. 1.25×. Inside the panel the
pattern is a step, not a gradient — 8.3% at 120–199, 14.6% at 200–279, 14.3% at 280–360 —
saturating above 200 words, so extrapolation to the unmeasured sub-120 band rests on one
pilot chamber. METHODOLOGY also records that New Brunswick "needed no such correction", so
the Canadian 1.7× is not a corpus constant. *Fix:* add a §5 bullet stating that the 120-word
floor selects toward longer, more-flagged segments, that the one chamber where the excluded
band was measured implies a 1.25–1.7× downward correction, and that this runs against the
evasion floor. State the unit: 12.4% is a share of *segments*.

**X8. The register drops a caveat the work log mandates.** *PARTIAL.*
`studies-and-work-log.md`:462 says "state this whenever the 10x is used"; the register
bullet at 160–165 puts both rates in one sentence followed by a single multiple, with no
such statement. *Accurate version:* the bullet disambiguates arithmetically (24.6/2.31 =
10.65 vs 8.5/2.31 = 3.68), both operands are present, and the register's own Artifacts line
points at the write-up, which carries the caveat twice in its sharpest form. Documentation
hygiene in an internal index. *Fix:* put the multiple next to the rate it belongs to.

**X9. The register says "refuting" where the write-up says "run the wrong way".** *PARTIAL.*
Register: "Occupation and education both run the *wrong* way, refuting professionalisation
and educational expansion." A cohort coefficient surviving two crude categorical controls
fails to explain the rivals away; it does not refute them, and §8.6 item 11 records the
professionalised-communications rival as "live and unmeasured". *Accurate version:*
"refuting" is a one-word overreach, but the alleged contradiction conflates two rivals.
`formation_window.py` names *compositional* rivals (occupational selection, educational
expansion), which are tested; §8.6 item 11's live rival is an *era-wide* norm change
affecting all members regardless of background, which no compositional control can address
and which §8.6 correctly labels unmeasured. The result is also directionally stronger than
the finding allows: postsecondary is −0.499 and communications-PR-journalism −0.646, i.e.
both rivals predict the wrong sign on their own key coefficients. *Fix:* match the register
wording to footnote r46b.

**X10. §6 mischaracterises its own policy scan, in both directions.** *PARTIAL.* Four
mismatches were alleged; one holds. **Holds:** "Saskatchewan is the one solid null" is
contradicted by `ai_policy_scan.md`, which says in the same breath that Nova Scotia and
Newfoundland & Labrador are equivalent and lists thirteen chambers at High confidence, six
of them no-policy-found after exhaustive searches (NL: "25 published policies + Management
Commission papers (~125k words): zero AI mentions"). **Does not hold:** "figures unverified
against primary sources" is a conservative posture, not a contradiction; §6 says "a
22-chamber scan", not "of the S10 corpus", so the PEI-for-NB substitution is a defect in the
scan's title; and §6's actual words are "requiring AI-drafted text to be disclosed **in the
record**", which is precisely the narrow claim the scan supports. The Sejm 4-of-9 EU
disclaimer datapoint is a reasonable addition but is not a usable route to ground truth
without the non-English instrument §8.6 item 8 already names. *Fix:* correct "the one solid
null" to name the six.

**X11. §8.5's moving-baseline proposal does not price its own costs, and equates two
different quantities.** *PARTIAL.* Four sub-points: non-comparability across a moving
baseline; non-reproducibility of a deprecating, access-gated baseline (with §3.2's silent
model substitution as the in-study demonstration); task/context specification being human
contribution absorbed into the counterfactual; and the claim that this is "the same quantity
S17 measures as the imitation lag". *Accurate version:* the first sub-point misquotes the
text, which claims interpretability under a label, not comparability. The second and third
are legitimate but are addressed to a proposal the section explicitly flags as "the most
promising direction, and the least developed", and the §3.2 anecdote cuts the other way —
what bit the study was a *silent* substitution, exactly what recording the baseline
prevents. **The fourth holds:** S17 measures a *duration* (months until an imitator reaches
frontier capability, λ = 1/L), while §8.5's residual is a capability gap between a person
and a machine. *Fix:* replace "the same quantity S17 measures" with "moves for the same
reason as S17's imitation lag".

**X12. §5's limits list omits five standard referee objections — of which two are worth
adding.** *PARTIAL.* Alleged: no clustering, equal-weight-per-chamber pooling, no
multiplicity, a two-point design precluding any trend, and single-scan specificity; plus a
wording issue on the repeat-pass band. *Accurate version:* (i) Clustering — the arithmetic
reproduces (deff 1.296, [10.8, 13.9]) but answers a different estimand:
`build_pangram_expansion.py` draws `rng.sample(...)`, a simple random sample of *segments*,
for which the design-based variance carries no clustering term. (ii) **Pooling weights — this
one stands and should be added:** 120 segments per chamber means 12.4% is the average
chamber's rate, not a population rate; disclosed in §2 but worth a clause. (iii)
Multiplicity — the heterogeneity claim survives an omnibus test needing no correction (χ² =
88.1 on 17 df, p = 1.4e-11) and NSW vs US Senate at p = 5.0e-6 clears Bonferroni over all
171 pairs; **reporting the omnibus test would make the spread claim multiplicity-proof on
its face, and is worth adding.** (iv) Two time points — the evidentiary claim misreads
Appendix B item 7, which retires the estimates that *predated* the per-year series, not the
series; and 0/1,260 pre-AI against 12.4% post is itself a change measurement against a
measured zero. (v) Single-scan specificity — 243 NB controls were scored on both Pangram 3
and 4 with 60/60 both times, and 2,400 pre-LLM segments passed the Opus band screen with
zero flags; the "11% instability" is 1 change across 39 rescans of texts deliberately chosen
*at* the boundary. (vi) The 0.716 anchor is dimension-matched in `quality_methods.md`
(justification: their 0.716 against this study's 0.83), so §5's sentence is defensible;
METHODOLOGY:1407's one-line summary is the loose one. *Fix:* add the equal-allocation clause
and the omnibus heterogeneity test.

---

---

## Part 2 — The paper text under review, verbatim

### Draft §5 — Limits (current text, post-2026-08-18 edits)

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
- **Tasmania is uninterpretable** and excluded. All twenty pooled chambers
  are now screened (the diagnostic previously globbed only the provinces;
  CA-FED, US House and US Senate were added — CA-FED flat, the two US chambers
  a gradual multi-decade climb with no discrete step). Nineteen pass; Tasmania
  is the sole exclusion. The diagnostic uses two convention-tracking markers,
  not all of them.
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
  r = +0.758. Controlling the judge's own `ai_guess` (Appendix D) leaves the
  largest external-label conjuncts standing but over-attenuates others; the
  only clean fixes are a human-coded subsample or grading style-normalised
  text, neither yet done.
- **Genre cells are not equally representative.** The length filter retains
  95% of SO31 but 6% of Oral Questions (§4.3). Flag rate also rises with
  segment length within a chamber, so the filter — which keeps the longer
  tail of each cell — works in the same conservative direction for the
  reported gradient, but it means the OQ figure is not an estimate of
  Question Period as a whole.
- **The quality arm is LLM-graded.** Repeat-pass and cross-account agreement
  both sit at or above the published human inter-coder bar, but
  self-agreement is not inter-coder agreement; the human-coded subsample
  remains the real validation and is not done.
- **The covariate effects are small, and small is what this kind of work
  finds.** In the field's common currency the study's member-level effects
  are correlations of r ≈ .07 (the insulation delta), r ≈ .10 (the class
  block), r ≈ .14 (cohort in current speech), with a class-II era contrast
  of d ≈ 0.2. Against empirical benchmarks for individual-differences
  research — Gignac & Szodorai's pool of 708 meta-analytically derived
  correlations puts the 25th/50th/75th percentiles at r = .10/.20/.30
  (*Personality and Individual Differences* 102, 2016) — these sit at or
  below the typical published effect. Funder & Ozer's guidelines read the
  same numbers forward: r = .05 is "very small" for single events "but
  potentially consequential in the not-very long run," r = .10 "small…
  but potentially more ultimately consequential," r = .20 "medium"
  (*Advances in Methods and Practices in Psychological Science* 2, 2019).
  Three things keep the small sizes honest rather than damning. They are
  reliably estimated — at n ≈ 3,600–4,800 the delta carries t ≈ 4 and holds
  in 100% of covariate specifications, which is the "critical
  consideration" Funder & Ozer's guidance is conditioned on. They are
  floors, not ceilings — the register index is one thin lexical probe of
  the behavior, and measurement error in a single index attenuates every
  correlation toward zero. And the study's real claim is structural, not
  variance-explained: the same peak-below-the-summit shape appears in
  class, in education, and in two occupational ladders built by
  semi-independent processes, with the occupational gradient nesting inside
  the class rungs — replication across instruments of the kind
  variance-share statistics do not measure. One benchmark cuts against us
  and is kept: Funder & Ozer flag r ≥ .40 as "likely to be a gross
  overestimate," and our career-outcome cohort estimate (R ≈ .39) was
  exactly that — period mixing inflated it, and the era-restricted r ≈ .14
  is the defensible number. Individual style is dominated by idiolect;
  roughly five-sixths of within-chamber member variation stays unexplained
  by everything we measure, which is the expected result in stylistic
  variation, not a defect of the instrument.

---

### Draft §6 — Policy context

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

### Draft §7 — Related work

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

### Draft §8.5 — the moving-baseline proposal

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
