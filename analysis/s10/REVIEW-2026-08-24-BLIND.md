# S10 — blind review, 2026-08-24 (open findings first; method, progress and resolved items at the end)

---

## MAJOR — CONFIRMED

### AL1. [argument-logic] §2.13 Permeation

> The register is permeating human speech independently of drafting: +0.0099, positive in 9 of 10 cells, permutation p = 0.017.

**Problem.** The 'independently of drafting' clause is unsupported: the era samples behind this arm are drawn uniformly within (chamber, era) cells with no filtering of machine-drafted text, so the post-2023 cells contain the very machine-drafted text §2.2 measures at ~9% of words (higher in some of these chambers). A small pooled shift of +0.0099 in assistant-likeness at instrument-word positions is exactly what a ~9% admixture of strongly assistant-like drafted text would produce with zero change in human speech. Detector-independence of the instrument is precisely what prevents it from excluding drafting as the source.

**Reviewer's check.** Read align_ratio.py (item selection: 'uniform at random within each (chamber, era) cell', era = pre if date ≤ 2022-12-31 else post; no Pangram/human filter) and word_context_delta.py (scores those same items); confirmed METHODOLOGY §5.2d-bis and the draft make no exclusion or sensitivity analysis for drafted-text contamination.

**Refuter's verification.** Quote verbatim in §2.13. Verified in code: align_ratio/items.json holds 1,500 segments per (chamber, era) cell drawn 'uniform at random within each (chamber, era) cell' (align_ratio.py), with fields {chamber, era, seg_id, turn_id, date, n_words, text} — no Pangram field, no flag exclusion — and word_context_delta.py consumes those items unfiltered. METHODOLOGY §5.2d-bis says only 'text selected identically in both eras'; neither it nor §2.13 claims drafted text was removed or bounded. The post-era cells therefore contain machine-drafted text at the chambers' measured prevalences (ca ~18.5%, ush 12.1%), and contamination of that size times a plausible per-position likelihood advantage for machine text can carry a material share of +0.0099, so 'independently of drafting' does not follow from detector-independence. The strongest defeater I found — the UK cell (2.5% machine) is positive on both scorers (+0.011, +0.017), arguing against 'wholly' carried by contamination — is an argument the paper never makes and does not bound the pooled headline; §5.2d's 'speech that could not have been drafted' claim belongs to the other (lexicon/unscripted) permeation arms, not this one. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Either restrict the post-era sample to segments Pangram scores Human (reporting the detector-dependence honestly as a robustness check), or bound the contamination arithmetically (show +0.0099 exceeds what the measured prevalence × the flagged-text delta could produce), or weaken the claim to 'the record is drifting' rather than 'human speech independently of drafting'.

### AL2. [argument-logic] §2.2 / Table 2 / §5.1

> A chamber's false-positive rate depends on its own editorial register, so specificity is not transferable — each chamber buys its own 60-segment pre-AI control.

**Problem.** Internal contradiction between the calibration premise and the per-chamber conclusions. If specificity is chamber-specific (the stated reason for per-chamber controls), then each chamber's specificity is known only from its own 60/60, whose Wilson lower bound is ~94% — so a chamber-level false-positive rate of several percent cannot be excluded, and the low-end rows of Table 2 (US Senate 1.8%, UK 2.5%, SCO 3.9%, SK 4.1%) are not distinguishable from calibration error under the paper's own premise. The elevenfold-spread headline's denominator inherits this. The quoted pooled interval [99.7%, 100%] is only usable per-chamber by transferring specificity across chambers — exactly what §5.1 says cannot be done.

**Reviewer's check.** Computed Wilson lower bound for 60/60 ≈ 94.0%; confirmed Table 2's per-chamber CIs are cluster bootstraps of the flag rate that carry no specificity uncertainty; confirmed §2.1 quotes the [99.7, 100] interval only for the pooled 1,260.

**Refuter's verification.** Recomputed the Wilson lower bound for a 60/60 control: 93.98% — under the paper's own no-transfer premise (§5.1's quoted sentence), a chamber-level FPR up to ~6% is not excluded by that chamber's own control. Table 2's intervals are cluster bootstraps over prevalence segments carrying zero specificity uncertainty; Rogan–Gladen is applied with Sp fixed at 1. US Senate 1.8%, UK 2.5%, SCO 3.9%, SK 4.1% all sit below the per-chamber calibration slack, so those rows and the elevenfold ratio's denominator are not calibration-exact under the stated premise. No caveat near Table 2 or in the Limits addresses per-chamber specificity uncertainty; the only rescue (pooling specificity across chambers) is exactly what §5.1 disclaims.

**Suggested fix.** Either argue explicitly that specificity partially transfers (softening §5.1) and propagate a pooled-specificity term into per-chamber intervals, or add per-chamber specificity uncertainty to Table 2 and stop quoting low-end chamber rates and the elevenfold ratio as if calibration-exact.

### AL3. [argument-logic] §2.14 Bypass study (headline)

> The headline: asking a general-purpose model to rework a speech in a loop beats the commercial evasion industry by about tenfold. ... which get 2.31% of documents past it, this search gets 22.5% of targets past it: 9.8×.

**Problem.** The paper's own Table 23 note declares this exact comparison invalid: 'The per-target row is italicised because it allows up to eighteen attempts per document, and no published benchmark grants that; it is ... the wrong number for a detector comparison.' The commensurable comparison the paper itself identifies is per-variant 11.1% vs 2.31% ≈ 4.8×, not 'about tenfold'; the 66× against clean FNR compounds the same mismatch. The headline leads with a ratio the paper later proves is between incommensurable quantities.

**Reviewer's check.** Compared the headline paragraph against Table 23 and its accompanying text within the same section; recomputed the commensurable ratio (11.1/2.31 = 4.8).

**Refuter's verification.** Quote verbatim in §2.14. Recomputed: 22.5/2.31 = 9.7×, 11.1/2.31 = 4.8× — both match, and Table 23 itself prints '4.8× the humanizers' on the per-variant row and '9.8× the humanizers' on the italicised per-target row. The same subsection's commensurability note reads: 'The per-variant row is the one commensurable with the vendor rows, which are also document-level FNRs on one adversarially prepared submission... The per-target row is italicised because it allows up to eighteen attempts per document, and no published benchmark grants that; it is the right number for exposure, the wrong number for a detector comparison.' The bolded headline compares against the humanizers' single-submission 2.31% using the ≤18-attempt per-target rate — exactly the comparison the section's own rule disqualifies. Best defense — reading the headline as an attack-pipeline (exposure) comparison — fails because the humanizer figure contains no retries, so the ratio is inflated by the retry budget regardless of framing; the paper's own text says per-variant exceeds 2.31% 'because... a stronger attack,' making 4.8× the internally consistent headline. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Make ~5× (per-variant vs humanizers) the headline ratio, and present 22.5% only as the exposure number it is defined to be.

### AL4. [argument-logic] §2.6 (Other chambers converge on the level the United States already held)

> So the picture is not a common shift. It is chambers converging upward on a level the United States already held before the consumer web, while the United States barely moves.

**Problem.** The section's own caveat destroys its headline: 'Chamber levels are therefore partly definitional: a US-derived yardstick will score US speech high whatever is happening. The defensible comparison is the within-chamber trend.' The convergence-toward-the-US-level story (Tables 7–8, 'They caught up; they did not pass') is a cross-chamber level comparison — the exact comparison the caveat rules indefensible. If the US sits high by construction of the Kobak instrument, 'other chambers converging on the US level' is partly an artifact of the ruler, and the Americanization reading built on it (feeding Table 9's interpretation) is not established.

**Reviewer's check.** Compared the section's headline and Tables 7–8 against its own instrument caveat paragraph; confirmed no US-independent level instrument is used anywhere in the section.

**Refuter's verification.** Quote verbatim in §2.6. Read the section end-to-end: Tables 6–8, the 1994-values-settle-it paragraph, and 'They caught up; they did not pass' are all cross-chamber level comparisons on a US-derived (PubMed/Kobak) yardstick, and the section's own caveat then states: 'Chamber levels are therefore partly definitional: a US-derived yardstick will score US speech high whatever is happening. The defensible comparison is the within-chamber trend, and that is where the finding sits.' The headline's distinctive content — 'a level the United States already held' — is irreducibly a level claim, so the caveat names the artifact the headline relies on, and the caveat's closing sentence is false of the section's actual finding. Best defense — the within-chamber trends (US flat since 1994, UK climbing 4%/yr) are unconfounded and carry part of the picture — supports a downgraded reading ('consistent with a US ceiling') but cannot carry 'on a level the US already held,' which requires exactly the cross-chamber level comparability the section disclaims. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Restate the section's conclusion in within-chamber terms (US flat, others rising) and explicitly mark the 'level the US already held' framing as unresolvable with a US-derived word list, deferring the level claim to the §3.8 1a register-feature instrument.

### AL5. [argument-logic] §2.6 / Table 6 (constant-window trend)

> on that single ruler the pattern is convergence: the lower a chamber started, the faster it climbed (Spearman between 2006 level and growth −0.56, n = 19).

**Problem.** Regression-to-the-mean coupling: growth is computed as (gap2026/gap2006)^(1/20), so the noisy 2006 endpoint enters the level positively and the growth negatively, mechanically inducing a negative correlation with no true convergence. Endpoint values rest on one sampled year per chamber, so this noise is material. Additionally the 19 chambers are treated as independent while the four fastest climbers are exactly the four UK-family chambers — one polity cluster (and the polity the placebo sets were built on), so a single shared-country factor is an unexamined alternative to convergence.

**Reviewer's check.** Verified from footnote 12 and constant_window_trend.py's description that both variables are computed from the same 2006 endpoint; verified no split-sample or independent-baseline check (e.g., 2006–08 mean level vs later growth) is reported; noted the country clustering of the top four rows in Table 6.

**Refuter's verification.** Quote verbatim in §2.6. Footnote 12 confirms growth is the geometric rate between the 2006 and 2026 endpoint values, so the −0.56 correlates growth against its own 2006 denominator — the classic Friedman/regression-to-the-mean coupling: endpoint noise enters level and growth with opposite signs, biasing the correlation negative. Endpoint values are single-year gaps estimated from sampled sitting days (Table 8's series sds run 36–134 on multi-year means, so single-year noise is nontrivial). Searched the section: no acknowledgment, no placebo (2006-level vs 2026-level), no split-sample baseline. Best defense — the four lowest starters (UK, SCO, NI, WAL at 605–1,276 vs 1,276–1,811) sit hundreds of points below the rest, far beyond plausible endpoint noise, so the qualitative convergence likely survives — shows the bias probably does not produce −0.56 entirely, but the finding claims bias-plus-no-acknowledgment, not fabrication, and both halves are accurate; the paper states the four-lowest-starters fact without framing it as robustness to the coupling. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Recompute with the baseline estimated from years disjoint from those defining growth (e.g., 2006–08 mean level vs 2010–2026 growth), report the correlation with country-cluster-robust inference, and soften 'the pattern is convergence' accordingly.

*Also flagged by: CB4, ST11.*

### AL6. [argument-logic] §2.13 Permeation

> Small, but it is the only permeation evidence that does not route through a detector, and it survives the failure mode that demoted the lexicon arm.

**Problem.** The failure mode that demoted the lexicon arm (§5.3) was the absence of a trend control — the estimator fires on pre-LLM periods. No equivalent test (an in-time placebo on pre-LLM era pairs) is reported for the word-context instrument; its self-normalisation controls segment-global drift, not register-specific drift. And the paper's own §2.5 finding — human register moving toward what instruct-tuning later selected for, for thirty years — predicts a positive pre-vs-post contrast in exactly this quantity with no post-2022 cause. The survival claim is asserted, not demonstrated.

**Reviewer's check.** Searched METHODOLOGY.md §5.2d-bis and word_context_delta.py for any pre-LLM window-pair placebo of this instrument — none exists; confirmed the permutation test shuffles era labels (testing for any era difference, not for excess over the standing trend).

**Refuter's verification.** Read word_context_delta.py in full: the pooled inference is a raw pre-vs-post era contrast (pre 2018–22, post 2024–26); the permutation shuffles era labels within chamber×family cells — testing for ANY era difference, not excess over a standing trend; self-normalisation cancels only segment-global drift. No in-time placebo on pre-LLM era pairs exists for this instrument (in_time_placebo.py serves the lexicon arm; the matched placebo words are recorded and deliberately unused). §5.3's demotion standard was precisely that the lexicon estimator fires on pre-LLM pairs, and the paper's own thirty-year-drift reading predicts a positive pre/post contrast here with no post-2022 cause. 'Survives the failure mode' is asserted, never demonstrated.

**Suggested fix.** Run the in-time placebo the demotion standard requires (e.g., 2015-vs-2019 era pairs through the identical pipeline); until then state that the instrument shares the lexicon arm's exposure to the pre-existing drift rather than claiming it survives that failure mode.

### AL7. [argument-logic] Abstract (and §1)

> This machine-drafted speech is not degraded: once genre is held fixed, AI-flagged contributions are better-formed and no less engaged.

**Problem.** The abstract states only the favorable half of a pair §2.14 says must be 'stated separately': the engagement null holds only conditional on there being something to engage with, and 'separately, AI-flagged speech is about half as likely to contain anything to engage with — a real difference, not a null' (applicability falls from ~61–63% to ~31% at high screen scores). 'No less engaged' as an unconditional abstract-level claim contradicts the paper's own conceded engagement-opportunity deficit.

**Reviewer's check.** Compared the abstract and §1's 'no quality penalty' against §2.14's applicability paragraph, which explicitly separates the two claims and calls the collapse 'a real difference, not a null'.

**Refuter's verification.** Quote verbatim in the abstract; §3.3 echoes it ('better-formed, not worse-engaged on the DQI'). §2.14 states the null is conditional and insists the two claims 'are stated separately (review item Q1)': applicability collapses at high screen scores (61.4%/63.0% vs 31.1% for respect demands), and 'AI-flagged speech is about half as likely to contain anything to engage with — a real difference, not a null.' Stage 6 additionally finds 'every machine arm sits below the human 2.07 on checkable specifics.' The abstract drops exactly the conditional the body establishes as required. Best defense — stage 6c attributes the collapse to weak tools rather than machine text as such — reframes the mechanism but does not undo the wild-text fact, and the abstract's unconditional conjunct remains contradicted by the body's own applicability finding. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Carry the conditional into the abstract: 'no less engaged where there is something to engage with, though flagged speech is about half as likely to contain anything to engage with'.

*Also flagged by: CE1.*

### AL8. [argument-logic] §2.14 (closing paragraph, 'What this means for the prevalence number')

> Evasion is real, clears the detector on roughly one flagged speech in five under directed search, and is free in deliberative-quality terms — so 9.0% is a floor

**Problem.** 'Free in deliberative-quality terms' overstates the paper's own stated power: the same section says the paired nulls have detectable-effect bounds of ±0.12–0.26 per dimension, 'commensurate with the study's own headline effects (+0.22 to +0.29)', so 'these nulls say the evasion edit produces nothing dramatic, not that it produces nothing at the scale the study elsewhere reports.' Stage 5's target-level n is 15. A conclusion of 'free' does not follow from nulls the section concedes cannot exclude headline-scale effects; §3.3 then compounds it ('need not fear that evasion ... degrades the metric it watches').

**Reviewer's check.** Compared the closing claim against the section's own review-item-Q3 power statement and stage-5 sample sizes.

**Refuter's verification.** The same section's power statement bounds detectable effects at ±0.12–0.26 per dimension and calls that commensurate with the study's own headline effects (+0.22 to +0.29); stage 5 aggregates to n=15 targets. The closing paragraph qualifies 'free' only on effort, never on power, and §3.3 mirrors the unqualified form. A set of nulls whose conceded detectable-effect floor sits at the study's own headline effect sizes cannot support 'free'.

**Suggested fix.** Replace 'free in deliberative-quality terms' with 'shows no detectable quality cost at the arms' power, which cannot exclude effects at the study's headline scale', and mirror that bound in §3.3.

### AL10. [argument-logic] §3.3 (The substitution)

> machine-assisted text grades better-formed, not worse-engaged on the DQI — so policing authorship does not protect quality, because the authorship detection would flag is not where the quality deficit is.

**Problem.** The premise 'not where the quality deficit is' is contradicted by two quality deficits the paper itself locates in machine/flagged text: the applicability collapse (flagged speech about half as likely to contain anything to engage with, §2.14) and the evidence channel (stage 6: 'every machine arm sits below the human 2.07 on checkable specifics'; the wild evidence lift is 'entirely length'). Given those, authorship is associated with real quality deficits on at least two dimensions, and the argument that authorship policing has no quality-protective content does not go through as stated.

**Reviewer's check.** Traced the §3.3 premise against §2.14's applicability paragraph and the stage-6 evidence result within the compiled text.

**Refuter's verification.** Traced both cited deficits: §2.14's Q1 paragraph states 'AI-flagged speech is about half as likely to contain anything to engage with — a real difference, not a null' (applicability 61.4/63.0 → 31.1 at screen ≥50), and stage 6 puts every machine arm below the human 2.07 on checkable specifics with the wild evidence lift 'entirely length'. §3.3's 'not worse-engaged' silently drops the paper's own conjunct split, and 'not where the quality deficit is' is contradicted by the paper's own located deficits.

**Suggested fix.** Qualify the substitution argument: detection is a poor proxy for quality on formation dimensions, but the measured machine-side deficits (engagement opportunity, checkable specifics) are exactly what a direct quality check must weight — which strengthens the 'check the work' proposal without the false 'no deficit where authorship is' premise.

### AL11. [argument-logic] §3.2 (gut judgment anti-correlation)

> Asked to judge AI-likeness by register, a frontier reader flagged 13 of 35 genuine human floor speeches and only 5 of 35 machine rewrites that had been optimised against a detector (§2.14 stage 5)

**Problem.** Near-circular evidence presented ahead of a strong unconditional conclusion ('any institution still adjudicating authenticity by feel will manufacture false accusations'). The rewrites were the surviving output of a search that optimised against an Opus self-screen, and the 'frontier reader' is an Opus-family judge — so a low flag rate on the rewrites is close to guaranteed by construction, and the comparison shows only that optimisation removed the tells this correlated judge keys on, not that human gut judgment is 'anti-correlated with the truth'. §3.8 1c concedes the paired effect is not significant (t = −1.15). The parenthetical flags the sample but the assertion and its policy conclusion are stated as established.

**Reviewer's check.** Cross-checked the optimisation target (Opus self-screen, §2.14 threat model) against the judge's lineage (Table 33; §3.8 1c calls it 'lineage-correlated' with the search's own proxy) and the conceded t-statistic.

**Refuter's verification.** Verified the lineage circle (the search self-screens on Opus's own score; the stage-5 grader is Fable — Table 33) and recomputed the counts from stage5_scores.json: originals 13/35 at ai_guess≥50 (exact), variants 7/35 (paper says 5). Strengthened the defect: per the stage-5 prereg, the '35 genuine human floor speeches' are the stage-5 ORIGINALS — Pangram-flagged attack targets the study itself counts as machine-drafted — so the 13 flags are not demonstrably false accusations on ordinary speakers. The 'illustrative' parenthetical hedges the evidence but leaves the declaratives unconditioned.

**Suggested fix.** Move the claim fully to hypothesis status ('one lineage-correlated judge suggests...'), and let the §3.8 1c design carry it; delete or condition the 'any institution ... will manufacture false accusations' sentence until an independent judge measures it.

*Also flagged by: SL2.*

### CP1. [calibration+prevalence] 4.2 (flagged-segment composition)

> of the 364 flagged prevalence segments, **217 are full AI verdicts and 147 (40%) are Mixed**

**Problem.** These counts do not describe the sample behind the 9.03% headline. The committed estimator (banded_prevalence.load()) contains 316 flagged prevalence segments: 182 AI and 134 Mixed (42%). The 364/217/147 set is a different population — it includes the CA-FED genre-arm rows (217 AI / 146 Mixed = 363 when TAS is excluded but the genre arm included), which §4.2 itself says are excluded from the chamber/pooled prevalence. Meanwhile the 12.03%-vs-9.03% comparison in the same paragraph IS computed on the estimator's 316-segment set, so the paragraph mixes two populations.

**Reviewer's check.** Ran banded_prevalence.py (prints 316 flagged of 3,519 prev segments); replicated load()'s exact filters over the five verdict CSVs to get the verdict split (182 AI / 134 Mixed); relaxing only the CA-FED genre exclusion reproduces 217 AI / 146 Mixed = 363; reproduced 12.031% as the full-weight rate on the estimator's own sample.

**Refuter's verification.** Quote verbatim in S10-WRITEUP-DRAFT.md (§4.2) and the render. The committed estimator (banded_prevalence.py) prints 316 flagged of 3,519 prevalence segments; replicating load() with verdicts kept gives 182 AI / 134 Mixed. The 12.03%-vs-9.03% comparison in the same paragraph reproduces exactly on that 316-flag sample, so the paragraph does mix two populations. One correction to the reviewer's diagnosis: relaxing only the CA-FED genre exclusion gives 357 (212 AI / 145 Mixed), not 363; the writeup's 364 = 217 AI + 147 Mixed reproduces exactly only when the genre arm is included AND Manitoba is double-counted (superseded draw plus redraw) — an even less defensible population than the reviewer supposed. The defect as stated survives fully.

**Suggested fix.** Quote the estimator's sample: 316 flagged segments, 182 AI and 134 Mixed (42%), or state explicitly that the 364 count spans the genre arm too and reconcile the residual off-by-one on Mixed.

### CP2. [calibration+prevalence] 2. Data (control window) / 3.1

> **control** — 60 segments dated on or before **2022-06-30**. Not 2022-12-31: ChatGPT shipped 2022-11-30, and a "pre-AI" control dated December 2022 is not pre-AI.

**Problem.** Seven control segments loaded into the pooled control set violate the stated cutoff: pangram_ch_p4_verdicts.csv rows ch055–ch059 (Dáil, 2022-09-21 to 2022-11-17) and ch238–ch239 (UK Commons, 2022-09-08 and 2022-10-27). All are still pre-ChatGPT and all scored Human, so no number moves, but the design claim is false as written for the UK/IE arm — the same defect footnote r42ca says was repaired for CA-FED was left in place for UK and Ireland.

**Reviewer's check.** Loaded banded_prevalence.load() with its META side table and listed every ctl row dated after 2022-06-30: exactly the 7 UK/IE rows above; all other files (p4 expansion, CA uniform ctl incl. cafedctl2*, shortband, MB redraw) have zero violations.

**Refuter's verification.** Quote verbatim in the Data section. Loading banded_prevalence.load() with its META side table lists exactly seven control rows dated after 2022-06-30, all in pangram_ch_p4_verdicts.csv: IE ch055–ch059 (2022-09-21 to 2022-11-17) and UK ch238/ch239 (2022-09-08, 2022-10-27). All seven scored Human and all predate ChatGPT, so no number moves, but the stated design rule is violated for the UK/IE arm and nothing in the draft discloses it — while footnote r42ca documents that the identical defect in CA-FED was found and repaired on 2026-08-13. No other loaded file has violations.

**Suggested fix.** Either replace/floor the seven UK/IE controls as was done for CA-FED, or amend the Data section to state the UK/IE long-band controls run to 2022-11-17 (pre-ChatGPT) and disclose the exception.

### CP3. [calibration+prevalence] 4.2 (word-weighting rationale, X12)

> the longest quartile of segments runs 9.4% against 5.8% for the shortest (review item X12). Segment-weighting would therefore understate the rate by about 0.6 points

**Problem.** Neither figure reproduces on the committed pooled sample. Across the pooled prevalence sample the longest/shortest quartiles run 15.2%/1.0% (binary segment rates) or 11.3%/0.7% (word-weighted); the long band alone gives 14.8%/5.8% — the quoted 5.8% matches the long band only, so the numbers were computed on a different scope than the text states. And segment-weighting understates by 0.05 points (8.98% vs 9.03% binary) or 2.19 points (fraction-weighted segment mean 6.83%), not "about 0.6 points". The direction of the argument survives — the specific figures are wrong.

**Reviewer's check.** Computed quartile rates (binary and word-weighted) and segment- vs word-weighted rates on banded_prevalence.load()'s prevalence rows, for all bands and for the long band alone; compared with banded_prevalence.py's own printed seg-wtd 8.98% vs word-wtd 9.03%.

**Refuter's verification.** Quote verbatim. On the committed pooled prevalence sample the quartile contrast is 15.2%/1.0% (binary segment rates) or 11.3%/0.7% (word-weighted); the long band alone gives 14.8%/5.8% binary — so the quoted 5.8% matches only the long band, and 9.4% reproduces nowhere on current data. The understatement is 0.05 points (seg-wtd binary 8.98% vs word-wtd 9.03%, both printed by banded_prevalence.py) or 2.2 points against the fraction-weighted segment mean (6.83%); nothing gives 0.6. The argument's direction (longer segments more machine-drafted, so segment-weighting understates) does survive — the specific figures do not.

**Suggested fix.** Recompute the quartile contrast and the understatement on the current pooled sample and state which sample (all bands) it is computed on; commit the computation.

### CP4. [calibration+prevalence] 4.2 (per-chamber CI table) / Results intro

> every number reproduces from a committed script

**Problem.** The per-chamber bootstrap CIs do not reproduce: banded_prevalence.table() seeds each chamber's bootstrap with abs(hash(ch)) % 10000, and Python string hashing is randomized per process, so every run yields different CI bounds (e.g. NSW [13.17, 26.89] one run, [13.21, 26.79] the next). The table's printed bounds match the writeup only to within this jitter, and MB and NI carry the identical interval [8.1, 18.6] in the writeup, which no run I produced reproduces for NI. prevalence_report.py's wboot seeds (abs(hash(c)) % 9999) have the same defect.

**Reviewer's check.** Ran the table twice in separate processes and diffed the CI bounds; read boot_ci()/wboot() seeding code; confirmed the pooled CI (seed=7) is deterministic and matches [8.00, 10.08] exactly.

**Refuter's verification.** Quote verbatim (Results intro, draft line 286 / render line 111). boot_ci() is seeded with abs(hash(ch)) % 10000 and Python string hashing is per-process randomized, so the per-chamber CI bounds differ on every run (NSW [13.20, 27.02] then [13.15, 26.86] in consecutive processes); even PYTHONHASHSEED=0 does not recover the writeup's MB [8.1, 18.6] (gives [8.0, 18.8]). prevalence_report.py's wboot seeds (abs(hash(c)) % 9999) share the defect. The pooled CI uses seed=7, is deterministic, and matches the writeup's [8.00, 10.08] exactly — the defect is confined to the per-chamber (and per-genre) intervals.

**Suggested fix.** Seed with a deterministic function of the chamber name (e.g. int(hashlib.sha1(ch.encode()).hexdigest(),16) % 10000) or a fixed map, rerun, and repaste the CI columns.

### CE1. [claims-vs-evidence] Abstract (repeated in Introduction and §3.3)

> This machine-drafted speech is not degraded: once genre is held fixed, AI-flagged contributions are better-formed and no less engaged.

**Problem.** The Results section explicitly splits this claim in two and the abstract merges them back. §2.14 states: "the engagement null below means engages no worse when there is something to engage with; separately, AI-flagged speech is about half as likely to contain anything to engage with — a real difference, not a null" (respect_demands applicability 61.4% at screen <10 vs 31.1% at ≥50; respect_counterargs 50.8% vs 28.9%). "No less engaged" is the unconditional claim the body says would "manufacture" a wrong reading; the measured unconditional picture includes a real engagement-opportunity deficit. The Introduction ("no quality penalty ... better-formed and no less engaged") and §3.3 ("grades better-formed, not worse-engaged on the DQI") repeat the merged form.

**Reviewer's check.** Compared the abstract/intro/§3.3 sentences against §2.14's applicability-by-band paragraph and its explicitly separated two-claim statement.

**Refuter's verification.** Quote verbatim in the abstract; merged forms also verified in the Introduction ("no quality penalty ... better-formed and no less engaged") and §3.3 ("grades better-formed, not worse-engaged on the DQI"). §2.14 states, as review item Q1, that "the two claims are stated separately" and gives the applicability collapse (respect_demands 61.4%/63.0% applicable below screen 50 vs 31.1% at ≥50; respect_counterargs 50.8%/51.2% vs 28.9%), calling the halved engagement-opportunity "a real difference, not a null." My best attack fails: the applicability figures come from the genre-balanced stage-1 pool (n=498/297/45 sums to the 840 stage-1 segments), so the abstract's "once genre is held fixed" clause does not cover the deficit — genre-fixing rescues the DQI engagement null but not the something-to-engage-with gap. Stage 6c's attribution of the collapse to weaker tools mitigates interpretation but is equally absent from all three merged statements. The defect survives.

**Suggested fix.** In Abstract, Introduction, and §3.3, state both halves: e.g. "better-formed, and no worse-engaged where there is something to engage with — though flagged speech is about half as likely to contain anything to engage with, a difference §2.14 traces to weaker tools."

*Also flagged by: AL7.*

### CE2. [claims-vs-evidence] Discussion, §3 opening paragraph

> two instruments that fail differently — a detector calibrated to zero false positives ... and a transparent lexical register run against placebo-matched counterfactuals — agree that at least 9.0% of words in current legislative speech are machine-drafted, spread elevenfold

**Problem.** The register instrument never produces a prevalence estimate. The Results assign the roles explicitly: Pangram "answers the prevalence question"; the register "carries the historical and social results" (§2 intro). The 9.0% and the elevenfold spread come from Pangram alone (Table 2). The only place the two instruments demonstrably agree is the genre ladder (§2.3: "the one place where the lexicon arm's inference is confirmed by an independent instrument"), and §5.3 demotes the register's frequency arm to "descriptive, not inferential." Attributing the headline count to two-instrument agreement claims corroboration the body does not deliver.

**Reviewer's check.** Searched the Results for any register-instrument prevalence estimate (none exists); confirmed §2's role assignment, §2.3's "one place" statement, and §5.3's demotion of the frequency arm.

**Refuter's verification.** Quote verbatim at the §3 Discussion opening. I searched the entire Results for any register-arm prevalence estimate: the register instrument only ever produces per-100k gap levels and trend series (Tables 6–8), never a machine-drafted share; §5.3 explicitly demotes its frequency arm to "descriptive, not inferential" because it fires on pre-LLM placebo windows. The 9.03% and the 1.8%–19.8% elevenfold range come solely from Pangram (Table 2), and §2's opening assigns the roles: Pangram "answers the prevalence question," the register "carries the historical and social results." Demonstrated cross-instrument agreement is the genre ladder (§2.3: "the one place where the lexicon arm's inference is confirmed by an independent instrument") and the qualitative §2.7 level test. The sentence's grammar attributes all three conjuncts — 9.0%, elevenfold spread, genre concentration — to joint agreement; only the third has two-instrument support. No defeating context found.

**Suggested fix.** Rewrite to attribute the 9.0% and elevenfold spread to the calibrated detector alone, and credit the register instrument only for the genre-concentration corroboration and the historical/social results.

### CC1. [cohort+class] 4.6, first bullet + footnote r46a

> birth **+0.88 per 1,000 words per decade** (t = 33.8) against spoken year **+1.25 per decade** (t = 29.2)

**Problem.** The cited invocation cannot produce these numbers. `python cohort_vs_period.py` always fits spoken+entry+birth: it prints birth +0.687 (t 19.4), spoken +0.851 (t 11.4), n=37,548 (default), or birth +0.629, spoken +0.678 on n=61,312 with --censor 0. The +0.88/+1.25 pair comes from a spoken+birth-only regression that exists nowhere in the committed script — and the script's own richer APC spec attenuates birth from +0.88 to +0.63 by absorbing entry-cohort, which the text never mentions. The t=33.8 is also unclustered member-year HC inference, the exact pattern the study flags three times (the identical provincial gradient falls t 17.7→8.5 when clustered).

**Reviewer's check.** Ran `python3 cohort_vs_period.py` (default and --censor 0); reimplemented the two-stamp spoken+birth WLS with chamber FE on the 61,312 birth-known rows using the script's own functions — it reproduces +1.254 (t 29.2) / +0.876 (t 33.8) exactly, confirming the printed spec is an uncommitted variant.

**Refuter's verification.** Quote is verbatim in §2.8/fn17. I ran the cited `cohort_vs_period.py`: it always fits spoken+entry+birth and prints birth +0.687 (t 19.43), spoken +0.851 (t 11.41) on n=37,548 (default) and birth +0.629, spoken +0.678 on n=61,312 (--censor 0) — never the printed pair. Reimplementing a two-stamp spoken+birth WLS with chamber FE on the 61,312 birth-known rows using the script's own load/_wls functions reproduces spoken +1.254 (t +29.23) and birth +0.876 (t +33.80) exactly, so the printed numbers come from an uncommitted variant; the committed richer spec attenuates birth to +0.63–0.69 (entry-cohort absorption the text never mentions), and the t=33.8 is unclustered member-year HC inference, the pattern the study flags three times elsewhere. The supplementary claim 'Everything is reproducible from analysis/s10/' makes this a live defect. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Either commit the two-stamp specification (e.g. a --no-entry flag) and cluster its SEs by member, or quote the script's actual three-stamp output and discuss the entry-year attenuation explicitly.

### CC2. [cohort+class] 4.6a, era figure + text

> class II sits above class I in all seven half-decades, and the manual-and-farm tail stays at the floor throughout.

**Problem.** The second clause is contradicted by the study's own table: in 2025–26 the pooled manual+farm cell is +0.021, nominally ABOVE class I (−0.061) and IVab (−0.102) — it is not at the floor. The figure's title ('manual and farm below both') is likewise false for the last period, and in the unpooled CSV V/VI is +0.166 in 2025–26, second only to III. The II-over-I half of the sentence checks out in all seven bins.

**Reviewer's check.** Read class_by_era_grouped.csv and class_by_era.csv row by row; compared each half-decade's manual+farm mean_z against I and IVab.

**Refuter's verification.** Read both CSVs row by row. II > I holds in all seven half-decades. But in 2025–26 the pooled manual+farm cell is +0.021, nominally above class I (−0.061) and IVab (−0.102) — not at the floor — and in the unpooled class_by_era.csv V/VI is +0.166 in 2025–26, second only to III. The figure title in plot_class_by_era_grouped.py ('manual and farm below both') is likewise false for the last period. The caption's noise caveat covers class III only, not manual+farm; the +0.021 (se 0.086) cell is statistically indistinguishable from the floor, so a qualified claim would survive, but the categorical claim as written is contradicted by the study's own table. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Qualify the claim (e.g. 'at or near the floor in six of seven half-decades, with a noisy 2025–26 excursion, se 0.086') and fix the figure title, or show the 2025–26 cell is statistically indistinguishable from the floor.

### CC3. [cohort+class] 4.6a, 'All four predictors at once' + footnote r46joint

> | **education** (block Wald) | p = 0.0025 | **p = 0.2150** |

**Problem.** Running the cited `python joint_predictors.py` gives materially different numbers for half the table: education alone Wald p=0.0000 (not 0.0025), joint p=0.1179 (not 0.2150), class II alone +0.122 (t 3.63) not +0.093 (t 3.02), prominence alone +0.037 (t 3.59) not +0.035 (t 3.08), cohort alone +0.276 (t 27.7) not +0.280 (t 24.3). The printed table was computed under an uncommitted variant (education as 4 level dummies rather than the script's ladder+professional; 'alone' fits including cohort rather than the script's cohort-free ones) — I reproduced the printed joint column exactly only under that variant.

**Reviewer's check.** Ran `python3 joint_predictors.py`; then refit the joint model with education level dummies and the alone fits with cohort using the script's own functions — the level-dummy variant reproduces the printed joint column exactly (edu p=0.2150, II +0.072 t 2.10, prominence +0.020 t 2.05).

**Refuter's verification.** Ran the cited `joint_predictors.py`: it prints education alone Wald p=0.0000 (not 0.0025), joint p=0.1179 (not 0.2150), class II alone +0.122 (t 3.63) not +0.093 (t 3.02), prominence alone +0.037 (t 3.59) not +0.035 (t 3.08), cohort alone +0.276 (t 27.69) not +0.280 (t 24.3) — half the printed table does not match the committed script (its 'alone' fits are cohort-free and education enters as ladder+professional). Refitting with education level dummies and cohort included in the 'alone' fits moves every number to or near the printed values (class alone II +0.091 t 2.95 ≈ printed +0.093 t 3.02; joint II +0.073 t 2.11 ≈ +0.072 t 2.10; prominence joint +0.020 t 2.07 ≈ +0.020 t 2.05; edu-levels alone p=0.0032 ≈ 0.0025), corroborating that the table was computed under an uncommitted variant. My variant refit gave edu joint p=0.2828 rather than the reviewer's exact 0.2150, so their exact-reproduction detail did not replicate for me, but the core defect — the printed table is not producible from the committed script — is directly verified. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Update joint_predictors.py to the specification the table actually uses (or regenerate the table from the committed script) and say in the footnote what 'alone' includes.

### CC4. [cohort+class] Appendix D.4

> | **non-office only** | **+1.31** | **+17.9** |

**Problem.** office_split.py computes HC (sandwich) SEs on word-weighted member-year cells with NO clustering by member, so the printed t = +18.4/+17.9/+4.9 are the same unclustered-inference pattern the study itself flags three times; on the identical provincial panel, formation_window.py's same gradient falls from t 17.7 (HC1) to 8.5 (CR1), so these t's are roughly 2× inflated. D.4 presents them without any clustering caveat while §4.6a's headline correction is precisely about this.

**Reviewer's check.** Ran `python3 office_split.py` (reproduces all printed values exactly) and read its _wls: weights are words, meat is per-observation, no cluster sums; compared with formation_window.py's HC1-vs-CR1 ratio on the same panel.

**Refuter's verification.** Ran `office_split.py`: it reproduces the D.4 table exactly (+1.194 t +18.39 / +1.309 t +17.97 / +0.617 t +4.94). Its _wls computes an HC sandwich with per-observation meat (w[i]**2 * resid[i]**2) and no cluster sums, i.e. unclustered member-year inference. On the same provincial birth panel, formation_window.py's gradient falls t +17.72 (HC1) → +8.46 (CR1), so ~2× inflation is a fair estimate. D.4 carries no clustering caveat (its 'per member-year rather than per member' note is about group assignment, not SEs), and the study's unclustered-inference flags (fn19, §2.9, Appendix A item 3, supplementary note) all point at other subsections. The conclusion likely survives clustering, but the presentation defect is real. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Add CR1 member-clustered SEs to office_split.py (the conclusion survives: even halved, non-office t≈9 and office-only t≈2.3), or flag the t's as unclustered in the table.

### CC5. [cohort+class] 4.6a, 'Flight' + footnote r46e

> ρ = −0.13 at 100+ occurrences, −0.22 at 300+, **−0.42 at 800+ (p = 0.004)**, −0.46 at 1,500+

**Problem.** No committed script computes this correlation. The cited `class_markedness.py` computes a different test (rare-word share of each class's instrument use — the cross-sectional result the same footnote says is 'not reported'), and `build_class_word_year.py` only writes the (class, year, word) count cache. The flight result — the subsection's headline — is therefore not reproducible from the repository as cited.

**Reviewer's check.** Ran `python3 class_markedness.py` (prints only the rare/mid/common share table), read both scripts end to end, and grepped every .py for a lift-vs-relative-use correlation; none exists.

**Refuter's verification.** Ran the cited `class_markedness.py`: it prints only the rare/mid/common share table (the separate cross-sectional test the same footnote says is not reported). Read `build_class_word_year.py` end to end: it only writes the (class, year, style-word) count cache, and a repo-wide grep shows the only code referencing class_word_year.json is its own builder. No committed script computes a post/pre-lift vs class-relative-use correlation, so the subsection's headline flight result is not reproducible from the repository as cited. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Commit the script that reads class_word_year.json and computes the post/pre-lift vs class-I-relative-use Spearman series, and cite it.

### CC6. [cohort+class] 4.6a, 'Class: the provincial estimates' + footnote r46d

> [^r46d]: `python covariate_study.py`, `python class_origin.py --dist`. Coding workflow and rubric ambiguities in `provinces/OCCUPATION_CODING.md`

**Problem.** Neither cited script produces the provincial EGP regression table (III +2.00 t 4.98, II +0.84 t 4.23, …, VIIab −1.66 t −4.22). covariate_study.py outputs a different analysis (occupation-category means by province, grad-vs-not education); class_origin.py --dist prints only the coding distribution. The table's regression, and the sample statement '897 members and 5,294 member-years', have no committed source (class_origin --dist shows 944 EGP-coded members; formation_window prints 5,860 member-years / 891 people).

**Reviewer's check.** Ran both cited scripts and compared their full output to the table; grepped all committed .py files for a year+province-FE EGP regression — none exists.

**Refuter's verification.** Ran both cited scripts in full. covariate_study.py outputs occupation-category means by province, grad-vs-not education contrasts, and a notability check — no EGP regression. class_origin.py --dist prints only the coding distribution (944 EGP-coded members: I 186, II 435, III 29, IVab 180, IVc 53, V/VI 45, VIIab 16 — which is where the table's members column comes from, but not its coefficients). No committed script produces the Table 13 regression (III +2.00 t 4.98, II +0.84 t 4.23, ..., VIIab −1.66 t −4.22): I checked panel_estimation.py, member_level_estimation.py, formation_window.py (prints 5,860 member-years / 891 people, not 5,294/897), and prereg_covariate_strength.py. The '897 members and 5,294 member-years' statement matches no committed artifact. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Commit the provincial EGP regression script (or an --egp mode in panel_estimation restricted to the 8 provinces) and reconcile the 897/5,294 sample statement with the committed artifacts.

### CB1. [comparability] §2.14 Bypass study (headline paragraph) and Table 23

> beats the commercial evasion industry by about tenfold. Against the 13 commercial "humanizer" services benchmarked in Pangram's own technical report, which get 2.31% of documents past it, this search gets 22.5% of targets past it: 9.8×.

**Problem.** The headline ratio compares a per-target rate under ≤18 query-and-retry attempts (22.5%) against vendors' per-document single-submission FNRs (2.31%). The paper's own Table 23 note concedes 'the per-target row is... the wrong number for a detector comparison' and that only the per-variant row (11.1%, i.e. 4.8×) is commensurable — yet the section headline, the 9.8× figure, and the 66× against the clean 0.34% FNR are all built on the incommensurable per-target number. The commensurable claim is ~5×, not ~10× (and not 66×).

**Reviewer's check.** Traced each rate to its definition: 22.5% = fraction of 71 targets with ≥1 Human verdict across up to 18 submitted variants; vendor 2.31% and 0.34% = document-level FNR on one submission. Cross-checked against the paper's own commensurability ruling in the Table 23 discussion, which contradicts the headline's arithmetic.

**Refuter's verification.** Quote verbatim at paper lines 1469-1471. The 22.5% is per-target under ≤18 query-and-retry submissions (Table 22); the 2.31% and 0.34% vendor figures are single-submission document-level FNRs. The paper's own Table 23 discussion rules 'the per-variant row is the one commensurable with the vendor rows' and calls the per-target row 'the right number for exposure, the wrong number for a detector comparison', and prints the commensurable multiplier itself (11.1% — 4.8× the humanizers). The headline 'about tenfold', the 9.8× and the 66× against the clean 0.34% all use the number the paper itself disqualifies for that comparison. The disclosure elsewhere mitigates but does not defeat the finding: the headline arithmetic contradicts the paper's own commensurability ruling, and the commensurable claim is ≈4.8×.

**Suggested fix.** Headline the commensurable comparison (11.1% vs 2.31%, ≈4.8×, 'about fivefold'); present 22.5% only as the exposure number, and drop or reframe the 66× line, which compounds multi-attempt adversarial vs clean single-document.

### CB2. [comparability] §2.14 Bypass study, flip-vs-success paragraph

> the blind first attempt flipped 10% of variants (4/40) and reached Human on 2.5% (1/40); the contrastive search flipped 28% (59/212) and reached Human on 13.7% (29/212). Effort raised both bars, and by more on the flip bar (2.8×) than on the success bar (5.5×).

**Problem.** The sentence states the opposite of its own numbers: 28/10 = 2.8× (flip) and 13.7/2.5 = 5.5× (success), so effort raised the success bar by more, not the flip bar. As written the comparison of the two effort multipliers is backwards.

**Reviewer's check.** Recomputed both ratios from the quoted counts (4/40→59/212 and 1/40→29/212) and compared with the sentence's ordering claim.

**Refuter's verification.** Quote verbatim at lines 1605-1608; counts verified against bypass_v3_pangram.json (212 variants: 153 AI / 30 Mixed / 29 Human). 28/10 = 2.8× is the flip multiplier and 13.7/2.5 = 5.5× the success multiplier, so on the multiplicative scale the sentence quotes, effort raised the success bar by more — the ordering clause is backwards as written. The only defense (reading 'more' as percentage points: +18.0pp flip vs +11.2pp success) is defeated by the parentheticals, which attach the ratios as the compared quantities. No downstream inference rests on the ordering, so the fix is a one-clause reversal.

**Suggested fix.** Reverse the clause: 'by more on the success bar (5.5×) than on the flip bar (2.8×)' — and reconcile the subsequent inference if any rests on the ordering.

### CB3. [comparability] §2.3 Drafting concentrates in scripted business

> The monotone trend across all three rungs is the ladder's proper test, and it holds: a Cochran–Armitage trend test on the segment counts (5, 14 and 22 flags of 60) gives z = 3.70, p = 2.2 × 10−4.

**Problem.** The section first rules segment-weighted cross-genre rates invalid — 'a segment-weighted comparison measures the packer's behaviour across genres alongside the drafting' (segments give 4.40× vs the word-weighted 3.29×, i.e. segment units exaggerate the ladder) — then designates as the ladder's 'proper test' a trend test computed on exactly those segment counts. The headline p-value therefore carries the packer confound the paper disavows, and in the direction that widens the gradient.

**Reviewer's check.** Compared the unit of the Cochran–Armitage input (per-genre segment flag counts, 5/14/22 of 60) against the section's own argument for word- and fraction-weighting, and against the reported segment-vs-word ratio gap (4.40× vs 3.29×).

**Refuter's verification.** Quote verbatim at lines 304-305. The same section rules that 'a segment-weighted comparison measures the packer's behaviour across genres alongside the drafting' and reports that segment units widen the ladder (4.40× vs the word-weighted 3.29×), yet designates as the 'proper test' a CA test on exactly those segment counts (5/14/22 of 60 = the segment rates 8.3/23.3/36.7%). The defect survives attack: a word-weighted permutation trend test was available (the paper already uses that machinery for SO31-vs-OQ, p = 0.0025) and CA's binary-count requirement does not excuse calling the segment-unit statistic the proper test. Mitigating context (not defeating): the ordering is unchanged word-weighted and the endpoint contrast holds at p = 0.0025 in the preferred unit, so the ladder itself is not threatened — only the headline trend p carries the disavowed unit.

**Suggested fix.** Run the trend test on the word/fraction-weighted estimand (e.g., a permutation trend test on summed AI-weighted words, matching the SO31-vs-OQ permutation), or present the segment-count trend explicitly as a secondary, packer-confounded check.

### XC1. [cross-cutting] Table 28 (Materials and methods §4) vs Table 6 (§2.6), §3.7, Appendix A item 10

> Canada federal House of Commons, AB, BC, MB, NB, NL, NS, ON, SK

**Problem.** The paper's official 22-chamber roster (Table 28) includes New Brunswick and excludes Prince Edward Island, yet PEI appears throughout as a study chamber: it is one of Table 6's 'nineteen chambers' (1,589 -> 1,523), one of the 'only three chambers [that] decline at all', in the 22-chamber policy scan ('Coverage is partial for NI, Manitoba, PEI and South Australia'), and in Appendix A item 10 ('PE +2.19 on 87 member-years'). Meanwhile NB — the densest-sampled corpus — is absent from Table 6, and §2.6's footnote names only SA, Ireland and federal Canada as exclusions, so its 19+3=22 bookkeeping only works if PEI replaces NB. The paper thus uses two different 22-chamber sets (23 distinct chambers in total).

**Reviewer's check.** Enumerated every chamber named anywhere in the paper; summed Table 6's 19 rows plus the footnote's three named exclusions against Table 28's roster; grepped all PEI/PE and New Brunswick mentions.

**Refuter's verification.** Table 28's roster (9 Canada + 6 Australia + 5 UK/Ireland + 2 US = 22) includes NB and excludes PEI, yet PEI appears as a study chamber in Table 6 (one of the 19 rows), in the only-three-decliners sentence, in the §3.7 policy scan, and in Appendix A item 10 (PE +2.19 on 87 member-years). Table 6's footnote names only SA, Ireland and federal Canada as exclusions (19+3=22 only if PEI replaces NB), and NB's absence is never explained there. The data files settle it: occurrence_trends.json contains exactly 22 chamber keys including PE and excluding NB, and covariate_study.py's eight Canadian provinces are AB BC MB NL NS ON PE SK — PE in, NB out — while Table 28 claims 'the covariate arms use all 22' with NB listed and no PE. Two different 22-chamber sets, 23 distinct chambers, exactly as stated. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** State the true roster once (if PEI is a 23rd, partially-covered chamber, say so and fix every '22 chambers' count); either add NB to Table 6 or name it among that table's exclusions with the reason.

*Also flagged by: IC1.*

### XC2. [cross-cutting] Appendix D.1 Table 34 vs §2.14 Table 19 (stage 2)

> justification +1.13 (t 4.1) → +0.83 (t 2.2) +0.75 (t 4.1) → +1.17 (t 3.6)

**Problem.** Table 34's stage-2 baseline coefficients contradict Table 19's stage-2 column for the same associations: justification +0.75 (t 4.1) vs +0.290 (t 4.4); common good +0.89 (t 7.0) vs +0.229 (t 4.5); respect groups +0.64 (t 6.2) vs +0.220 (t 6.1); respect counterargs even flips sign (−0.14 vs +0.073). D.1's header says the regressor is 'the screen ai guess + genre/era fixed effects', which contradicts the column label 'stage 2 (external)' (Table 19's stage-2 regressor is the binary Pangram verdict with chamber fixed effects). No reconciliation is given.

**Reviewer's check.** Matched every dimension row of Table 34 against Table 19; stage-1 baselines match Table 19 exactly, stage-2 baselines do not, confirming the discrepancy is specific to the stage-2 column.

**Refuter's verification.** Reproduced Table 34's stage-2 column exactly from results_stage2.json: the baselines (+0.749 t 4.1, +0.887 t 7.0, +0.635 t 6.2, −0.142) come from regressing DQI on the SCREEN's continuous ai_guess/100 (with degenerate genre FE — 600 of 682 rows are genre 'n/a'), not on the binary Pangram verdict with chamber FE that produces Table 19's stage-2 column (+0.290, +0.229, +0.220, +0.073). analyze_stage2.py's own docstring records that 'analyze.py --key key2.json regresses on the SCREEN's continuous ai_guess instead and returns different numbers.' So the two tables' 'stage 2' columns are different regressions on the same 682 segments; D.1's prose nonetheless calls it 'the stage-2 external label' and no reconciliation with Table 19 is given at the table. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** State Table 34's stage-2 regressor and fixed effects explicitly, and if they differ from Table 19's (score vs binary verdict, era/genre vs chamber FE) say so at the table; otherwise recompute so the baselines agree.

### XC3. [cross-cutting] §2.14 (bypass, per-target chamber comparison)

> The two chambers give 25.0% (n = 40) and 19.4% (n = 31) — consistent, but with intervals far too wide to establish that they agree: the 4.1-point gap carries a 95% interval of roughly [−17, +25] points

**Problem.** 25.0% − 19.4% = 5.6 points, not 4.1. The quoted gap matches neither the ≥1-Human rates nor the fraction-ai=0.0 rates (25.0 vs 16.1 = 8.9); it appears to be a stale number from an earlier version of the table.

**Reviewer's check.** Recomputed 10/40 − 6/31 = 5.65 points; checked the alternative (strict) column too.

**Refuter's verification.** 10/40 − 6/31 = 5.65 points, not 4.1. The staleness is documented in the repo itself: REVIEW-2026-08-11-BBLOCK.md's B6 entry records that the 4.1pp difference and its [−16.9, +25.1] interval were the review's computation on the OLD per-chamber figures (26.3% and 22.2%, before the M4 fix in commit 487f313 updated them to 25.0/19.4), and states explicitly 'on the current figures the difference is 5.6pp.' The paper adopted the softened B6 language but carried the stale gap and interval. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Change to the 5.6-point gap (and reconfirm the bootstrap interval was computed on the current rates).

### XC4. [cross-cutting] §3.8 item 4 (and §2.3)

> the House runs far more one-minute floor speeches, the SO31-type format §2.3 measures at ˜37% machine

**Problem.** §2.3's reported SO31 rate is 32.3% (Table 3, word- and fraction-weighted — the weighting the paper declares canonical for every rate); ~37% is the segment-weighted 36.7% the paper itself deprecates as 'a measurement of our packer'. The same slip occurs inside §2.3: 'This makes the 8.3% a mislabelled row rather than a wrong one' calls 8.3% a row when Table 3's Oral Questions row reads 9.8% (8.3% is the segment-weighted figure that appears in no table).

**Reviewer's check.** Compared both quoted values against Table 3 and against §2.3's own list of segment-weighted alternatives (36.7% / 23.3% / 8.3%).

**Refuter's verification.** Table 3's SO31 rate is 32.3% [21.0, 44.1], word- and fraction-weighted — the weighting §2.2 declares applies to 'every rate in this study'; ~37% matches only the segment-weighted 36.7% that §2.3 itself deprecates as partly 'a measurement of our packer' (binary counting gives 35.8%, also not the canonical figure). The companion slip also verifies: §2.3's 'This makes the 8.3% a mislabelled row rather than a wrong one' calls 8.3% a row when Table 3's Oral Questions row reads 9.8%; 8.3% is the segment-weighted figure appearing only in the prose list 36.7/23.3/8.3, in no table. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Quote 32.3% (or '˜32%') in §3.8, and in §2.3 refer to 'the Oral Questions estimate' or the 9.8% row rather than the untabled segment-weighted 8.3%.

### GS1. [genre+screen] 4.3 Drafting concentrates in scripted business

> Not one of the five flagged segments is spontaneous exchange.[^r43] Two are **eulogies** for a former member.

**Problem.** The categorical claim is contradicted by the writeup's own fifth item. I read all five flagged segment texts: the eulogies, the privilege response, and the unanimous-consent motion check out, but the fifth (Connie Cody, 'The Economy', 124w) is an ordinary QP supplementary question addressed to the Prime Minister mid-exchange — i.e., it IS spontaneous exchange on its face, excluded only by the unsourced assertion that backbench questions are 'routinely staff-written'. genre_oq_audit.py itself tags it (and the two eulogies and the UC motion) 'exchange?'. The follow-on claim 'the flags land exactly on the parts that were written in advance' is demonstrated for 4/5, asserted for the fifth.

**Reviewer's check.** Ran genre_oq_audit.py (its NOT_EXCHANGE classifier marks only 1/5); extracted the five flagged seg_ids from pangram_p4_verdicts.csv and read their full texts in ca/segments_ca2.jsonl.

**Refuter's verification.** Reproduced fully. The fifth flag (Connie Cody, 'The Economy', 124w, 2025-12-04) is a mid-exchange QP supplementary addressed to the Prime Minister — facially question-and-answer exchange — and its exclusion rests solely on the writeup's unsourced 'routinely staff-written' characterization; genre_oq_audit.py's own NOT_EXCHANGE classifier tags it (and the two eulogies and the UC motion, whose section headers don't match the regex) 'exchange?', marking only the Privilege segment NOT-exchange. The writeup claims 'The genre claim therefore holds segment by segment' and 'the flags land exactly on the parts that were written in advance', but that is demonstrated for 4/5 (I read all five texts: two eulogies, a prepared privilege response, a verbatim unanimous-consent motion) and merely asserted for the fifth. The writeup does disclose the fifth's nature transparently, so 'contradicted' is rhetorically strong — but the categorical sentence and 'exactly' overclaim what was shown, and that defect survives.

**Suggested fix.** Soften to 'four of the five are demonstrably pre-written text (two eulogies, a prepared privilege response, a negotiated unanimous-consent motion); the fifth is a backbench question, a category plausibly but not demonstrably staff-written', and drop 'exactly'.

### GS2. [genre+screen] 4.4 The Opus screen tracks Pangram

> A blinded LLM screen over the full corpus (37,801 segments, date-blind) separates Pangram's classes cleanly on the 618-segment overlap

**Problem.** 'The full corpus' is the New Brunswick corpus only, not the study's 22-chamber corpus, and §4.4 never says so. opus_screen_full.js is named 'opus-screen-nb-full' with description 'Lean Opus screening of the full NB corpus', and opus_screen_auc.py's docstring says 'run over all 37,801 NB segments'. Nothing between §4.3 (federal Canada) and this sentence scopes 'the corpus' to NB, so a reader will take the screen — and its 'cheap stratifier' claim — as covering the whole multi-chamber study.

**Reviewer's check.** Read opus_screen_full.js meta and opus_screen_auc.py docstring; counted opus_screen_scores.csv (37,801 scored rows); inspected screen_batches/ (blinded NB text); grepped the writeup for any NB scoping before line 585 — none.

**Refuter's verification.** Verified: opus_screen_scores.csv holds 37,801 NB-format seg_ids (no chamber prefix, e.g. '2025-12-04#t1558w3'); opus_screen_full.js is named 'opus-screen-nb-full' ('Lean Opus screening of the full NB corpus'); opus_screen_auc.py's docstring says 'all 37,801 NB segments'. §2 defines 'the corpus' as 22 chambers across five countries, and I grepped the entire draft: the only mentions of the screen are lines 583-640 and no NB scoping appears anywhere in §4.4, before it, or in the appendices. A reader will take the screen and its 'cheap stratifier for future work' claim as covering the multi-chamber study corpus. No defeating context found.

**Suggested fix.** Say 'over the full New Brunswick corpus (37,801 segments, date-blind)' here and at 'the run over all 37,801 segments'.

### GS3. [genre+screen] 4.3 Drafting concentrates in scripted business

> Mixed verdicts are commoner in the mixed-format Government Orders than in the scripted SO31 set pieces, so counting Mixed segments as wholly machine had been flattering the middle rung.

**Problem.** False as written: both 60-segment cells contain exactly 5 Mixed verdicts (SO31 5/60, Government Orders 5/60). The middle rung deflates most under fraction-weighting (25.7%→19.9%) because GO's Mixed segments carry much lower fraction_ai (mean ~0.38 vs ~0.61 for SO31's), not because Mixed verdicts are commoner there. Only as a share of flagged segments (5/14 vs 5/22) is Mixed 'commoner' in GO, which the sentence does not say. The same wrong mechanism appears in prevalence_report.py's wrate() docstring.

**Reviewer's check.** Counted verdicts per genre and per-segment fraction_ai values from pangram_p4_verdicts.csv; recomputed binary vs fraction-weighted rates (35.8/25.7/11.8 vs 32.3/19.9/9.8, both reproduce).

**Refuter's verification.** Recomputed from pangram_p4_verdicts.csv: SO31 has exactly 5 Mixed of 60 and Government Orders (DEBATE) exactly 5 Mixed of 60 — equal counts, so 'commoner' is false as written. The middle rung deflates most under fraction-weighting (25.7%→19.9% vs SO31 35.8%→32.3%, both pairs reproduce) because GO's Mixed segments carry lower AI fractions (mean 0.381 vs 0.607 for SO31), i.e. dilution, not frequency. Only as a share of flagged segments (5/14 vs 5/22) is Mixed relatively commoner in GO, which the sentence does not say. prevalence_report.py's wrate() docstring repeats the same wrong mechanism verbatim ('Mixed is commoner in the mixed-format Government Orders').

**Suggested fix.** State the actual driver: GO's Mixed segments are more diluted (lower AI fractions), and/or say 'Mixed is a larger share of the flags in Government Orders'.

### IC1. [internal-consistency] §4 Data, Table 28 (and Abstract, §2.6 Table 6, §2.8, Appendix A)

> Canada federal House of Commons, AB, BC, MB, NB, NL, NS, ON, SK

**Problem.** The roster of 'The 22 chambers' contradicts the study's own tables. Table 6 has a Prince Edward Island row, Table 8's 'CA provinces' group includes it, and Appendix A items 9-11 report PE results (e.g. 'PE +2.19 on 87 member-years') — yet PEI is absent from Table 28 and never introduced in Data. The covariate panel's '22 chambers' includes PEI and excludes New Brunswick, while Table 28's 22 includes NB and excludes PEI, so the study actually spans 23 distinct chambers and 'all 22' names two different sets in different sections. The caption also promises 'the arms that use each' but the table has no arms column.

**Reviewer's check.** Counted Table 6's 19 rows and reconciled against the footnote's three exclusions (SA, IE, CA-FED): 19+3=22 with PEI and without NB. Enumerated chambers in prereg_member_table.json: 22 chambers including PE (68 members), excluding NB. Table 28 sums to 22 only with NB and without PEI. occurrence_trends.json likewise contains PE and no NB.

**Refuter's verification.** Verified in full. Table 28's 22 (line 2526 of the render) includes NB and omits PE. Footnote 12 excludes SA, IE and CA-FED from Table 6's 19 rows, reconciling to a different 22 that includes PE and omits NB. prereg_member_table.json enumerates exactly 22 chambers including PE (68 members) and no NB; occurrence_trends.json likewise carries PE and no NB. Appendix A reports 'PE +2.19 on 87 member-years' (line 2690), yet PE never appears in the Data section. So the study spans 23 distinct chambers and 'all 22' names two different sets. The caption promises 'the arms that use each' but the table has only group/chambers columns; the arms statement lives in the prose above it, and that prose ('the covariate arms use all 22') is itself wrong for the PE/NB swap.

**Suggested fix.** Add PEI to the roster, state the true chamber count (23 distinct chambers), and specify per arm which chambers it covers (prevalence 20; trend/covariate 22 incl. PEI, excl. NB); add the promised arms column or reword the caption.

*Also flagged by: XC1.*

### IC3. [internal-consistency] §2.14 Stage 6 vs Table 33 (Materials)

> blind, length-matched within prompt, frozen v2b rubric, two passes, judge pinned to the stage-1/2 model.

**Problem.** Table 33 says stages 1-5 were graded by Claude Fable 5 and stage 6 by Claude Opus (medium); the stage-6 discussion itself says 'the judge is Opus grading its own family blind'. So the stage-6 judge was NOT pinned to the stage-1/2 model, contradicting the comparability claim on which stage 6's link to the stage-1/2 results partly rests.

**Reviewer's check.** Compared the §2.14 sentence with Table 33's rows and the stage-6 favoritism paragraph; verified in artifacts that workflows/stage6_grade.js sets model:'opus',effort:'medium' while quality_expansion/grade_workflow.js's provenance comment records fable-5 grading for the earlier stages.

**Refuter's verification.** Quote at line 1706. Table 33 (line 2999) states DQI grading stages 1-5 ran on Claude Fable 5 and stage 6 on Claude Opus (medium); the same §2.14 passage admits 'the judge is Opus grading its own family blind' (line 1753). Verified in artifacts: workflows/stage6_grade.js sets model:'opus', effort:'medium', and its own comment ('stages 1-5 were graded in Opus sessions') is contradicted by quality_expansion/grade_workflow.js's recovered provenance comment (stages 3-4 graded by claude-fable-5) and by Table 33. Whichever provenance is factually right, the paper simultaneously asserts the stage-6 judge is pinned to the stage-1/2 model and that it is a different model, and never states whether cross-judge comparability is assumed or tested.

**Suggested fix.** Correct the sentence (the stage-6 judge is Opus, not the stage-1/2 Fable judge), and state explicitly whether cross-judge comparability between stage 6 and stages 1/2 is assumed or tested.

### IC4. [internal-consistency] Appendix D.1 Table 34 vs §2.14 Table 19

> On the stage-2 external label, the two largest conjuncts — justification and common good — survive the control (t 3.6, t 3.2); the headline is not an artifact of the judge smelling AI.

**Problem.** Table 34's stage-2 'AI+FE' baselines (justification +0.75 t 4.1; common good +0.89 t 7.0; respect groups +0.64 t 6.2) do not match Table 19's stage-2 estimates (+0.290 t 4.4; +0.229 t 4.5; +0.220 t 6.1) with no explanation. The generating script regresses DQI on the SCREEN's ai_guess/100 with genre/era fixed effects for every pool — not on the Pangram verdict with chamber FE — so the column labelled 'stage 2 (external)' is neither the external label nor the main-text specification, and the robustness conclusion is drawn against a different regression than the one it defends.

**Reviewer's check.** Compared the two tables cell by cell; read quality_expansion/analyze.py §3b: r['ai'] = screen.get(sid).get('ai_guess') for all pools, regressed as ai/100 with genre/era FE.

**Refuter's verification.** Quote at lines 3045-3047. Read analyze.py §3b: for every pool it sets r['ai'] = screen ai_guess and regresses each DQI dimension on ai/100 + genre/era FE (+judge_ai) — for the stage-2 pool key2.json carries chamber+verdict and genre is mostly None, so the genre/era FE are degenerate and there is no chamber FE. Table 34's stage-2 baselines (+0.75 t 4.1, +0.89 t 7.0, +0.64 t 6.2) do not match Table 19's stage-2 estimates (+0.290 t 4.4, +0.229 t 4.5, +0.220 t 6.1) and no reconciliation is offered. D.1's opening sentence does disclose the screen-ai_guess regressor, but the conclusion sentence attributes the robustness to 'the stage-2 external label', which is neither the regressor used nor the main-text specification the control is defending.

**Suggested fix.** Rerun the leakage control on the actual stage-2 specification (Pangram verdict, chamber FE) or relabel the column and rewrite D.1's conclusion to match what was estimated.

### IC5. [internal-consistency] §2.9 vs §2.9.4

> The II-over-I crossover is established, by the test that needs no normalization at all.

**Problem.** Two subsections give incompatible verdicts on the same claim. §2.9 calls the crossover 'established' (within-chamber meta-analysis +0.59, z = 3.50); §2.9.4 says 'the crossover here is a recurring direction in two panels rather than a demonstrated effect ... nothing in this subsection should be cited as established' and calls it 'a hypothesis the enlarged panel failed to confirm at conventional thresholds' — while z = 3.50 is well past conventional thresholds.

**Reviewer's check.** Read the two passages side by side; confirmed both refer to the II-over-I crossover, and that the meta-analytic z printed in §2.9 contradicts §2.9.4's 'failed to confirm at conventional thresholds'.

**Refuter's verification.** Quote at line 749. §2.9 asserts 'established' backed by the within-chamber meta (+0.59 per 1,000, z = 3.50), member-level contrast (+0.073, t 2.49), chamber-FE (+0.650, t 5.17) and the joint model (t 2.10). §2.9.4 (lines 903-907) says of the same quantity 'the crossover here is a recurring direction in two panels rather than a demonstrated effect', 'a hypothesis the enlarged panel failed to confirm at conventional thresholds', and 'nothing in this subsection should be cited as established' — while z = 3.50 and the post-expansion joint t 2.10 are past conventional thresholds. The 'failed to confirm' language appears to be stale text from before the nine-chamber expansion (§2.9.1 records the pre-expansion joint test failing at t 1.26). The disclaimer sentence speaks of 'the crossover here', not only the Labov parallel, so it cannot be read as scoped to the interpretation alone. Both verdicts stand in the printed text.

**Suggested fix.** Pick one verdict: either §2.9.4 should scope its disclaimer to the Labov-parallel interpretation (not the crossover's existence), or §2.9 should drop 'established'; state explicitly what the z = 3.50 meta does and does not license.

### IC6. [internal-consistency] §3 Discussion (opening paragraph)

> agree that at least 9.0% of words in current legislative speech are machine-drafted, spread elevenfold across chambers and concentrated where procedure permits preparation

**Problem.** The prevalence figure is attributed to the agreement of both instruments, but by the paper's own design only the detector measures prevalence: §1 says 'Prevalence ... needs a calibrated detector', §5.3 demotes the lexical arm to 'a descriptive series, not ... evidence of LLM causation', and §2.3 identifies the genre ladder as 'the one place' the lexicon arm is confirmed by an independent instrument. The register arm neither produces nor corroborates the 9.0% or the elevenfold spread.

**Reviewer's check.** Compared the Discussion sentence against §1's prevalence/permeation split, §5.3's demotion of the frequency arm, and §2.2's derivation of 9.03% from Pangram alone.

**Refuter's verification.** Quote at lines 1800-1802, attributed to the agreement of both instruments. By the paper's own design only Pangram measures prevalence: §1 states 'Prevalence... needs a calibrated detector'; §2.2 derives 9.03% and the elevenfold spread (Table 2) from Pangram alone; §5.3 demotes the lexical arm to 'a descriptive series, not... evidence of LLM causation' (it fires on pre-LLM placebo windows); and §2.3 identifies the genre ladder as 'the one place where the lexicon arm's inference is confirmed by an independent instrument'. Of the three conjuncts, only the genre concentration is two-instrument; the 9.0% and the spread are carried by the detector alone. The register arm — whose whole finding is that the register predates the machines — cannot corroborate a machine-drafting share.

**Suggested fix.** Rewrite so the 9.0% and the spread are carried by the calibrated detector alone, with the register instrument corroborating only the genre concentration (and the permeation/history claims).

### IC7. [internal-consistency] §3.5 Limits

> Mixed is pooled with AI throughout. Reported separately in the CSV.

**Problem.** This limits bullet contradicts the headline methodology: §2.2 states that counting Mixed at full weight 'is the single largest upward bias in the headline', that every flagged segment is weighted by its own AI share (Mixed averaging 0.435), and that 'The 9.03% headline is thus already the split-corrected figure, not an AI-or-Mixed count.' A reader of the limits section takes away the pre-2026-08-13 method the paper says it corrected.

**Reviewer's check.** Compared the bullet against §2.2's fraction-weighting paragraphs and footnote 1's 'This is a correction, not a refinement' history.

**Refuter's verification.** Quote at line 1972. §2.2 (lines 170-182) states that counting Mixed at full weight 'is the single largest upward bias in the headline' (12.03% vs 9.03%), that every flagged segment is weighted by its own AI share (Mixed averaging 0.435, n=132), and that 'The 9.03% headline is thus already the split-corrected figure, not an AI-or-Mixed count.' The limits bullet asserts the pre-correction method as a standing limitation 'throughout'. The true situation: verdict-level counts (§2.3 flag counts, the stage-2 regressor per footnote 29) pool Mixed with AI, but all word-share prevalence rates weight Mixed by its measured AI fraction. As printed, the bullet contradicts the headline methodology.

**Suggested fix.** Reword the bullet: verdict-level counts (e.g. §2.3 flag counts, stage-2 regressor) pool Mixed with AI, but all word-share rates weight Mixed by its measured AI fraction.

### OP1. [occupational-prereg] Results 4.6b / prereg refutation conditions

> One drafting generation of the registration expressed the peak claim as a linear three-profile rank; that operationalization failed its own test and the framing is retired

**Problem.** The registration's refutation clause was triggered and its mandated reading is never reported. The prereg states: 'beta(front-line) ≥ beta(corporate) — refutes the revision... the original front-line version stands. Reported as exactly that, not as a general failure.' Observed: front-line +0.047 (t 3.3) > corporate +0.029 (t 2.0), corporate-top in only 24% of 2,000 resamples (the registered load-bearing share). Neither §4.6b nor Appendix B10 states the registered conclusion that the front-line (external-service) version stands; the failure is reframed as a drafting oversight.

**Reviewer's check.** Compared prereg 'What would refute it' section against prereg_stage1_results.txt §2 (reproduced by rerunning the script); searched the writeup for any 'front-line version stands' statement (none).

**Refuter's verification.** Verified against the prereg's 'What would refute it' clause: 'beta(front-line) ≥ beta(corporate) — refutes the revision... the original front-line version stands. Reported as exactly that, not as a general failure.' Stage-1 results (reproduced) show front-line +0.047 (t 3.3) > corporate +0.029 (t 2.0), corporate-top in 24% of 2,000 resamples — the clause fired. Grep of the entire writeup finds no 'front-line version stands' statement anywhere; §4.6b calls it a failed operationalization and Appendix B10 says only 'the linear rank failed its own registered clause' before pivoting to the provenance ruling. The run commit itself (ad303ad: 'the revision is refuted, the original drone stands') recorded the mandated reading, so it was known and then dropped from the writeup. Mitigating context exists (Lattice A shows L's raw positivity dissolving under covariates, weakening the front-line story), but that could accompany the mandated report, not replace it.

**Suggested fix.** Report, per the registration's own clause, that beta(front-line) ≥ beta(corporate) refutes the corporate revision and the front-line version stands on the linear-profile test — alongside the retirement rationale.

### OP2. [occupational-prereg] Results 4.6b / registered taxonomy rung arm

> Failed registered predictions are in Appendix A (the altitude quadratic, the autonomy asymmetry, nominal-vs-effective autonomy).

**Problem.** The registered taxonomy arm ('employed middle managers are the highest of the management cells, and owner-operators sit low') is reported nowhere in the writeup, and its point estimates contradict the prediction: employed first-line +0.216 (n=59) > employed middle +0.092 (n=495), and owner-op executives +0.171 sit ABOVE employed executives −0.002. The prereg's post-run amendment even claims the run 'confirmed... the rung ordering', which the data do not show. The failed-predictions list omits this arm entirely.

**Reviewer's check.** prereg_stage1_results.txt §6 (rung x ownership means; reproduced by rerun) against the prereg's fixed-classification prediction; grepped writeup for 'rung arm', 'owner', 'employed middle', '0.216' — absent.

**Refuter's verification.** Verified: the rung × ownership arm was registered with a fixed classification and the explicit note that it 'stands even if the instrument itself disappoints,' yet grep of the writeup for 'rung'/'owner'/'ownership'/'middle manager'/'0.216' finds no occupational-arm reporting anywhere — not in §4.6b, Appendix A's failed list (items 18–21), or Appendix B. Stage-1 §6 (reproduced) shows employed first-line +0.216 (n=59) above employed middle +0.092 (n=495), and owner-op executives +0.171 above employed executives −0.002 — point estimates against both halves of the prediction ('employed middle managers are the highest of the management cells'; 'owner-operators sit low'), while the prereg's post-run amendment claims the run 'confirmed... the rung ordering.' The only softening — the contradicting cells are small and noisy (se 0.129 and 0.138), so the contradictions are not statistically significant — is already in the reviewer's own fix; the omission of a registered arm whose point estimates run against the prediction stands.

**Suggested fix.** Report the rung × ownership table, state that middle-highest holds against executives but not against first-line (noisy cell, se 0.129), and that owner-op executives run against the owner-operators-sit-low prediction; add to the failed/mixed registered predictions list.

### OP4. [occupational-prereg] Results 4.6b footnote [rnc] / Indoors conditioning

> Entered jointly with Indoors, the apex delta reads +0.033 (t +2.2) and free −0.062 (t −4.4).

**Problem.** Selective reporting of the registered-control conditioning: the same results file shows the section's peak terms are absorbed by Indoors — lvl_MIDDLE +0.010 (t +0.7), flagged 'absorbed (officeness)', and dir_middle +0.022 (t +1.5), 'marginal' — with the file's own reading 'the single-rung levels were officeness'. The footnote quotes only the two surviving terms (delta, free), so the reader is not told the headline middle-peak slopes do not survive the office marker.

**Reviewer's check.** prereg_negative_controls.txt FOLLOW-UP block vs footnote [rnc]; script reruns reproduce the txt.

**Refuter's verification.** Verified against prereg_negative_controls.txt's FOLLOW-UP block (script rerun reproduces it): six conditionings were computed, and the footnote quotes only the two survivors. lvl_MIDDLE falls to +0.010 (t +0.7, 'absorbed (officeness)'), lvl_TOP to +0.003 (t +0.2, 'absorbed'), dir_middle to +0.022 (t +1.5, 'marginal') — the headline Table-15 middle slopes do not survive the office marker, and the reader is never told. The best defense — the section's 'shape inside the office' framing and the file's own 'sharpens, does not overturn' reading, under which the surviving contrasts (delta, free-lowest) carry the claim — explains why the omission is not fatal to the section's conclusion, but it does not defeat the finding: the selective quotation is real, and reporting the absorbed rows would in fact support the section's framing, as the reviewer notes.

**Suggested fix.** Report all the Indoors conditionings, including that the single-rung middle slopes are absorbed and only the contrasts (apex delta, free-lowest) survive — which is consistent with, and sharpens, the section's own 'shape inside the office' framing.

### PT1. [posttraining+coverage+permeation] 4.7 (body and footnote r47)

> Post-training as a whole installs the register; base→instruct end-to-end (+1.24) is untouched.

**Problem.** The +1.24 end-to-end figure is computed by the same defective estimator the section supersedes (olmo_ladder.py report draws controls from the earlier checkpoint's vocabulary only and buckets on the denominator). It carries the M3 pedestal too: my null calibration on the base→instruct transition returns +0.60 on random frequency-matched lists, and the bias-free symmetric estimator gives +0.61 — about half the quoted value. The footnote's own arithmetic concedes this: corrected stages sum to ~0.65 and 'the gap closes to about 0.03', which puts the bias-free end-to-end near +0.61, not +1.24. Calling it 'untouched' is wrong; the number is inflated ~2x by the acknowledged bias. The qualitative claim (post-training installs the register) survives at +0.61.

**Reviewer's check.** Reproduced +1.2376 with the flawed estimator from olmo_ladder/*_gen.json; implemented the symmetric-control estimator (controls from union vocabulary, bucketed on combined count) giving +0.6111 for base→instruct; ran 30 random frequency-matched null lists through the flawed estimator on that transition, mean +0.6008 (symmetric: −0.0030). Corrected stage sum 0.645 minus corrected end-to-end 0.611 = 0.034, matching the footnote's 'about 0.03'.

**Refuter's verification.** olmo_ladder.py report reproduces +1.2412 via the superseded estimator (controls drawn from the earlier checkpoint's vocabulary only, bucketed on the denominator — verified in the code at lines 221-236). My independent symmetric-control implementation gives base→instruct +0.6225, and feeding 30 random frequency-matched null lists through the flawed estimator returns +0.6004 (sd 0.074) on that transition — a pedestal accounting for roughly half of +1.24. The footnote's own arithmetic concedes it: corrected stages sum to 0.65 and the gap 'closes to about 0.03' under the bias-free estimator, implying bias-free end-to-end ≈ +0.62. Calling the +1.24 'untouched' is internally inconsistent with the same footnote; the qualitative claim survives at ~+0.62.

**Suggested fix.** Replace the end-to-end figure with the bias-corrected ~+0.61 (or report both, labelling +1.24 as superseded like the stage values), and delete 'is untouched'.

### PT2. [posttraining+coverage+permeation] 4.7a (table and footnote r47a)

> every corpus truncated to 1,187,489 words, base and instruct counted separately — pooling them doubles the generated volume against a volume-matched human corpus and manufactures parity

**Problem.** The truncation claim is false for the instruct row. style_word_frequency.py matches the generated corpora by prompt count (1,600), not word volume, and truncates only the Hansard corpora; the script's own output shows generated INSTRUCT at 1,435,683 words — 21% more than the 1,187,489 every other row gets. The instruct zero bin (118), the 'absent from generated only' 55, and the 'present in both' 267 all benefit from the extra volume. At genuinely matched volume the instruct row is 126/62/37/30/36/41/75 and the partition is 64/62/21/260 — so the bolded headline '86 to 55' should be '86 to 62' and '236 to 267' should be '236 to 260'. The direction survives; the printed numbers and the stated method do not match, and this is exactly the volume-mismatch error the footnote says an earlier script made.

**Reviewer's check.** Ran style_word_frequency.py (instruct row prints 1,435,683 words); read SC.generated (no word-level truncation, only Hansard is truncated to min(gbn,gin)); recomputed the instruct histogram and overlap with the instruct stream truncated at 1,187,489 words in the same family/prompt order.

**Refuter's verification.** style_word_frequency.py matches generated corpora by prompt count (1,600) and truncates only the Hansard corpora (SC.generated has no word-level truncation; target = min(gbn, gin) happens to equal the base count). The script's own output shows generated INSTRUCT at 1,435,683 words — 21% more than every other row's 1,187,489. Recomputing the instruct row with the stream truncated to 1,187,489 words in the same family/prompt order reproduces the reviewer's values exactly: histogram 126/62/37/30/36/41/75 and partition 64/62/21/260. So the matched-volume headline should be '86 to 62' and '236 to 260', not '86 to 55' / '236 to 267'. Direction survives; the stated method and the printed numbers do not match, and it is precisely the volume-mismatch error footnote 27 attributes to the earlier style_coverage.py.

**Suggested fix.** Truncate the instruct corpus to the same word target in style_word_frequency.py and update the table and the 86→55 / 236→267 sentences to the matched-volume values (86→62, 236→260).

### PT3. [posttraining+coverage+permeation] 4.7 (well-measured/pooled paragraph, per-family paragraph, footnote r47)

> the well-measured estimate is flat (+0.3881 → +0.3903, a move of +0.0022 from 800 to 1,600 prompts on the same families) while the pooled estimate keeps climbing (+0.6074 → +0.6235

**Problem.** The cited invocation (`python rlhf_pref_compile.py`) is nondeterministic and does not produce the quoted numbers. excess_at builds its control pool from Python set iteration (allw = set(base_c) | set(inst_c)) with PYTHONHASHSEED unfixed, so the recorded random seed does not pin the control draws: two same-machine runs gave well-measured +0.3927 and +0.3900 (with PYTHONHASHSEED=0: +0.3857), pooled +0.6189/+0.6209/+0.6251 — never the quoted +0.3872/+0.6311. The per-family range printed is +0.3464..+0.7343, not the quoted '+0.356 to +0.749'; the MoE well-measured came out +0.0611 and +0.0763, not the quoted +0.067. Worst, the interpreted convergence delta '+0.0022' reproduced as −0.0060 and −0.0036 — the sign is not stable, so a specific four-decimal movement is being read from Monte-Carlo noise of ~±0.01 (the same sin §4.8 explicitly refuses to commit with its bootstrap endpoint). The qualitative claims (well-measured flat, pooled climbing at 1600→3200 on qwen3, all four families positive) all reproduce.

**Reviewer's check.** Ran rlhf_pref_compile.py three times (twice default, once PYTHONHASHSEED=0) and compared every quoted figure; inspected rlhf_pref_scale.excess_at for the source of nondeterminism.

**Refuter's verification.** Verified the nondeterminism source in rlhf_pref_scale.excess_at: the control pool is built from iteration over set(base_c) | set(inst_c) with PYTHONHASHSEED unfixed, so the recorded random seed does not pin the draws. Three runs gave 1600-checkpoint well-measured +0.3859/+0.3859/+0.3857 and pooled +0.6202/+0.6205/+0.6251 — never the quoted +0.3872/+0.6311; my PYTHONHASHSEED=0 run exactly matches the reviewer's (+0.3857, +0.6251), confirming their check. The 800→1600 well-measured delta came out −0.0071, +0.0049 and +0.0070 across runs — the sign is unstable, so the four-decimal '+0.0022' is Monte-Carlo noise (~±0.01). Per-family range reproduced as +0.3520..+0.7415 (etc.), not '+0.356 to +0.749'; MoE well-measured +0.0640, not +0.067. The qualitative claims (well-measured flat, pooled climbing, all four families positive) do all reproduce.

**Suggested fix.** Sort the candidate pool (cand = sorted(...)) or fix PYTHONHASHSEED, rerun, and quote the now-deterministic values with at most 2–3 significant figures; drop the '+0.0022' precision claim in favour of 'moves by less than the draw noise (~0.01)'.

### PT4. [posttraining+coverage+permeation] 4.7 (headline table and SFT/DPO comparison)

> three independent corrected routes agree on the picture below (exact stratified estimator shown; audit values in the 2026-08-11 review, M9)

**Problem.** No committed script produces the section's headline table (+0.32/+0.27/+0.06), the per-stage null pedestals (+0.45/+0.56/+0.31), the RLVR 'CI straddles 0' claim, or the paired bootstrap DPO−SFT = −0.08 [−0.31, +0.15]. olmo_ladder.py computes only the superseded values and its header note says the corrected rebuild is 'the pending proper fix'; the sole provenance is a review document, i.e., an unverified author claim. My independent symmetric-control implementation reproduces the stage values (+0.318/+0.263/+0.064) and the pedestals (+0.44/+0.59/+0.32), so the numbers are right — but the CI claims (RLVR straddling zero; the DPO−SFT interval) have no derivation anywhere in the repo, and the project's own convention is that every novel number gets a committed computation.

**Reviewer's check.** Grepped all .py files for the corrected estimator (only olmo_ladder.py mentions it, as pending); implemented the symmetric-control estimator on olmo_ladder/*_gen.json and matched the table and pedestals; found no computation of either CI.

**Refuter's verification.** Repo-wide grep finds no committed script producing the corrected table, the null pedestals, the RLVR CI, or the DPO−SFT paired bootstrap. olmo_ladder.py's header states the symmetric-pool rebuild is 'the pending proper fix', and commit 13b13b1 says the same. The sole recorded provenance is REVIEW-2026-08-11.md M9, whose reproduce block points at $SCRATCH/ladder.py — a scratch path not in the repository. The numbers themselves are right: my independent symmetric-control implementation reproduces the stage values (+0.319/+0.270/+0.060 ≈ the table's +0.32/+0.27/+0.06), and M9 records the CI values (DPO−SFT = −0.077 [−0.305, +0.154]) — but neither CI has a committed derivation, violating the project's own every-novel-number-gets-a-committed-computation convention.

**Suggested fix.** Commit the corrected-estimator script (the 'symmetric-pool rebuild' olmo_ladder.py promises), including the null calibration and both bootstrap CIs, and point footnote r47 at it.

### QB1. [quality+bypass] 4.9 Bypass study (headline paragraph)

> Against the 13 commercial "humanizer" services benchmarked in Pangram's own technical report, which get **2.31%** of documents past it, this search gets **22.5%** of targets past it: **9.8×**.

**Problem.** The headline tenfold claim divides the per-target rate (22.5%, attacker allowed <=18 submissions with verdict feedback) by the vendors' one-shot per-document FNR (2.31%). The same section later rules exactly this pairing out: 'The per-variant row is the one commensurable with the vendor rows' and the per-target row 'is the right number for exposure, the wrong number for a detector comparison.' The commensurable ratio the section itself endorses is 4.8x (11.1/2.31), not 9.8x. The follow-on 'Against Pangram's clean-conditions false-negative rate of 0.34%, it is 66x' has the same unit mismatch (commensurable: 33x).

**Reviewer's check.** Reproduced 22.5% (16/71) and 11.1% (38/341) by running bypass_report.py; arithmetic 22.5/2.31=9.74, 11.1/2.31=4.80, 22.5/0.34=66.2 confirmed; cross-read the section's own commensurability paragraph, which contradicts the headline's chosen numerator.

**Refuter's verification.** Quote verbatim at render line ~1470. Arithmetic reproduced from bypass_report.py: 16/71=22.5% per target, 38/341=11.1% per variant; 22.5/2.31=9.74, 11.1/2.31=4.80, 22.5/0.34=66.2. The same section's Table 23 discussion states 'The per-variant row is the one commensurable with the vendor rows' and calls the per-target row 'the right number for exposure, the wrong number for a detector comparison' — yet the headline ('beats the commercial evasion industry by about tenfold') and the 66× line are exactly that detector comparison using the per-target numerator. Best defense found: the headline does name its units ('of documents' vs 'of targets') and Table 21 two paragraphs later separates the threat models — but naming units is not flagging incommensurability, and the section's own rule endorses 4.8×/33× as the like-for-like ratios. The internal contradiction survives.

**Suggested fix.** State the headline comparison per variant (~4.8x the humanizer services, ~33x the clean FNR), or explicitly label the 9.8x as exposure-vs-benchmark and not a like-for-like detector comparison at first mention, not eight paragraphs later.

### QB2. [quality+bypass] 4.9 Stage 5 (successful evasions table)

> | respect_demands | −0.01 (t −0.6) | 0.00 (t 0.0) | | respect_counterargs | +0.11 (t +0.9) | +0.10 (t +0.4) |

**Problem.** These sentinel cells reproduce from stage5_scores.json + stage5_grade_key.json ONLY when -1 (inapplicable) is included as a literal score of -1 in the paired differences — the practice the section's opening paragraph says is never used ('excluded from means rather than scored as zero') and that footnote r49b applies to stages 3/4 ('-1 (inapplicable) pairs are excluded, which is why the two sentinel dimensions have smaller n'). Under the stated exclusion rule respect_counterargs is −0.33 (t −1.0, n=3), a sign flip, and respect_demands is 0.00 (n=8). The table also shows no reduced n for these rows, silently implying n=35.

**Reviewer's check.** Recomputed all stage-5 paired differences from the committed artifacts under both codings: excluding -1 gives −0.33 (n=3) / 0.00 (n=8); including -1 as a value gives −0.014 (t −0.6) and +0.114 (t +0.8) / +0.100 (t +0.4), matching the published table. Non-sentinel rows and the ai_guess 36-vs-40 aside reproduce under either coding.

**Refuter's verification.** Recomputed from stage5_scores.json + stage5_grade_key.json under both codings. Including -1 as a literal score: respect_demands −0.014 (t −0.6), respect_counterargs +0.114 (t +0.8), n=35 — matching the published Table 25. Excluding -1 per the declared rule ('excluded from means rather than scored as zero', render line 1312, and footnote 33's stage-3/4 practice): respect_demands 0.00 (n=8), respect_counterargs −0.33 (t −1.0, n=3) — a sign flip and drastically reduced n. Table 25's column header claims n=35 with no reduced-n note for the sentinel rows, and no footnote discloses that stage 5 folds -1 in (grep found no such disclosure). Non-sentinel rows reproduce identically under either coding, as the reviewer said. The null conclusion survives, but the two published sentinel cells are computed against the paper's own stated rule.

**Suggested fix.** Recompute the two sentinel rows with the declared exclusion rule and report their reduced n (3 and 8 applicable pairs), or disclose that the stage-5 table folds -1 in and why; the null conclusion survives either way.

### QB3. [quality+bypass] 4.9 Stage 6 / Appendix C.4 (model attribution)

> | DQI grading, stages 1-5 (§4.9) | **Claude Fable 5** | default | | DQI grading, stage 6 (§4.9) | **Claude Opus** | medium |

**Problem.** Three mutually contradictory model attributions coexist. C.4 says stages 1–5 were graded by Fable 5 and stage 6 by Opus; §4.9's stage-6 paragraph says the stage-6 judge was 'pinned to the stage-1/2 model' (false if 1/2 were Fable and 6 is Opus); workflows/stage6_grade.js's own header says 'JUDGE MODEL IS PINNED to opus: stages 1-5 were graded in Opus sessions'; quality_expansion/grade_workflow.js says it 'sets no model' and that 'stages 3 and 4 were graded by claude-fable-5'. This also undercuts C.4's claim that the r=+0.758 screen-vs-judge correlation 'is a correlation between two different models': the stage-1 screen and grade phases run in the same no-model-pinned workflow, so both inherited the same session default.

**Reviewer's check.** Read C.4's table and narrative, §4.9's stage-6 sentence, and the model-provenance comments in workflows/stage6_grade.js (lines 17–18, model:'opus') and quality_expansion/grade_workflow.js (lines 1–6, no model set). The writeup itself calls the screen/grader split 'load-bearing'.

**Refuter's verification.** All four sources verified. C.4 Table 33 (render lines 2999-3000): stages 1-5 Fable 5, stage 6 Opus. §2.14 stage-6 paragraph (line 1706): 'judge pinned to the stage-1/2 model' — false under C.4's own attribution (stage 1/2 Fable, stage 6 Opus). workflows/stage6_grade.js lines 17-18: 'JUDGE MODEL IS PINNED to opus: stages 1-5 were graded in Opus sessions' (and model:'opus' at line 92) — contradicts both C.4 and quality_expansion/grade_workflow.js's header ('sets no model... stages 3 and 4 were graded by claude-fable-5'). At least two of the three records must be wrong. The 'two different models' defense of r=+0.758 is also undercut: RUNME.md line 16 confirms the stage-1 AI label is the 'blinded LLM screen, run in the same workflow', and grade_workflow.js sets no model on either its screen (line 206) or grade (line 214) agent calls, so both phases inherited the same session default — analyze.py line 229's 'TWO DIFFERENT models' claim and C.4's repetition of it are unsupported by the code.

**Suggested fix.** Resolve the attribution from the actual grading transcripts and make §4.9, C.4, and the two workflow headers agree; if screen and grader in stage 1 were in fact the same model, retract or reword C.4's 'two different models' defense of the leakage probe.

### ST1. [series+trend+cross-chamber] 4.5b + footnote r45cc

> Fisher's method over the 47 corpus specifications combines to **p ≈ 1.3×10⁻⁸³**

**Problem.** Fisher's method requires independent p-values, but the 47 'corpus specifications' are overwhelmingly nested/overlapping subsets of five chambers (16 Dail variants, 15 Canada variants, 15 UK variants — ewtrim/sh/trim/prepared/unscripted/band cuts of the same speeches). Combining them as independent inflates the statistic astronomically; one spec per independent chamber (5 chambers, each p ≤ 1e-3) gives Fisher p ≈ 7×10⁻¹¹, ~72 orders of magnitude weaker. The qualitative claim survives, but the printed number is not a valid p-value.

**Reviewer's check.** Ran cross_corpus.py; reproduced X2=647.9, df=94, p=1.288e-83 and read the 47-corpus list it prints — the variants are trims/subsets of the same chambers. Recomputed Fisher over the five independent chamber-level specs (each p bounded at 1/1000).

**Refuter's verification.** Reran cross_corpus.py: X2=647.9, df=94, p=1.288e-83 over 47 confirmatory specs that are 2 US chambers plus 15 nested trim/sh/band/prepared/unscripted variants each of Dail, Canada HoC, and UK HoC (15/15/15+2, not the reviewer's 16/15/15 — immaterial). These are overlapping subsets of five independent legislatures, violating Fisher's independence requirement; recomputing over one spec per chamber (5 × p≤1e-3) gives X2=69.08, df=10, p=6.7e-11 ≈ the reviewer's 7×10⁻¹¹. No dependence caveat exists anywhere in the writeup or footnote r45cc, and replication_protocol.md's combination rule speaks of 'corpora' (legislatures), so prespecification does not rescue the 47-way combination. The qualitative every-chamber claim survives; the printed number is not a valid p-value.

**Suggested fix.** Combine one prespecified specification per chamber (p ≈ 7×10⁻¹¹, still decisive) or use a dependence-robust combination; report the 42 robustness variants as robustness, not as contributions to the combined p.

### ST2. [series+trend+cross-chamber] 4.5a (convergence paragraph)

> US House swings between 1,660 and 2,074 across the series — a 25% range, the widest here — and 2026 catches it at 1,709, near its own floor.

**Problem.** 'The widest here' is contradicted by the table printed directly beneath it: Canada federal's sd is 134 vs US House's 121, and CA-FED's own 2020–26 swing (1,630–2,019, 23.9%) exceeds US House's (1,709–2,074, 21.4%); over its full 2015–26 series CA-FED spans 1,624–2,019 (24.3%) in half as many years. UK's 2006–26 range is 126.8% (trend-driven, but no detrending qualifier is stated).

**Reviewer's check.** Ran convergence_check.py (reproduced the means/sd table) and computed min/max ranges per chamber from occurrence_trends.json.

**Refuter's verification.** Reproduced from occurrence_trends.json: US House 2006–26 min/max 1,659.7–2,074.3 (25.0%). But the superlative fails under every reading: the table printed directly beneath shows CA federal sd 134 > US House sd 121; over the table's own 2020–26 window CA-FED swings 1,630–2,019 (23.8%) vs US House 1,709–2,074 (21.4%); over full series CA-FED spans 24.3% in 12 years, CA provinces group 33.7%, AUS states 29.9%, UK 126.8% (trend-driven, no detrending qualifier stated). The low-2026-year argument itself survives; the superlative does not.

**Suggested fix.** Either drop the superlative ('one of the widest', or 'wide for a flat series') or say explicitly that US House has the widest variation among the chambers with no trend; the low-year argument survives without the superlative.

### ST3. [series+trend+cross-chamber] 4.5a (exported-machine-text paragraph)

> Federal Canada is the one case it does explain, at 21.7% the most machine-written chamber in the study

**Problem.** Per the cited artifact, New South Wales is more machine-written than federal Canada on both metrics: 23.1% vs 21.7% by instrument occurrences, 19.8% vs 18.5% by words (ai_share_by_chamber.json). The writeup's own §4.2 table and §8 both name NSW 19.8% as the top of the prevalence range, so the superlative contradicts the paper's own numbers.

**Reviewer's check.** Read ai_share_by_chamber.json (NSW share_occurrences 0.2315 > CA-FED 0.2165; share_words 0.1981 > 0.1848) and grepped the writeup's §4.2 table (NSW 19.8% highest).

**Refuter's verification.** ai_share_by_chamber.json: NSW share_occurrences 0.2315 > CA-FED 0.2165 and share_words 0.1981 > 0.1848, so NSW beats federal Canada on both metrics. The writeup's own §4.2 table (NSW 19.8% highest) and §8 ('US Senate 1.8% to NSW 19.8%') contradict the superlative. CA-FED is second only to NSW (next is QLD 18.6%), so 'most machine-written of the national chambers' would be accurate; 'in the study' as written is false. convergence_check.py's docstring carries the same error.

**Suggested fix.** Say 'the most machine-written of the national chambers' or 'second only to NSW'.

*Also flagged by: IC9.*

### ST4. [series+trend+cross-chamber] 4.5a (exported-machine-text paragraph)

> US House is **14.3% machine by instrument occurrences** against Ireland's 9.0% and the Australian states' 11.3%, so removing machine text lowers the American benchmark by more than it lowers the challengers.

**Problem.** The Australian states' 11.3% silently imputes 0% machine share for Tasmania: TAS is deliberately excluded from the detector estimator (ai_share_of_instrument.py drops chamber TAS), has no entry in ai_share_by_chamber.json, and convergence_check.py's share() averages with so.get(...,0) over all 5 states. Excluding TAS from the mean gives (23.1+18.6+8.8+5.9)/4 = 14.1% — essentially equal to US House's 14.3% — so for the Australian states the 'cuts the wrong way' arithmetic collapses to parity. The human-only AUS mean (1,861→1,799) inherits the same bias.

**Reviewer's check.** Read convergence_check.py's GRP/share() code and ai_share_by_chamber.json (no TAS key); recomputed the 4-state mean; confirmed the TAS exclusion in ai_share_of_instrument.py scored().

**Refuter's verification.** Verified the mechanism in code: ai_share_of_instrument.py's scored() drops TAS (and MB, which unlike TAS gets re-added via pangram_mb_redraw_verdicts.csv), so ai_share_by_chamber.json has no TAS key; convergence_check.py's share() averages the 5-state group with so.get(...,0), silently imputing 0% for TAS. Mean over the four measured states = 0.1409 (14.1%) vs the printed 11.3% (=0.5636/5). At 14.1% vs US House's 14.3% the 'cuts the wrong way' arithmetic is parity for the Australian states, and the human-only AUS mean (1,861→1,799) inherits the same bias (~1,776 corrected, still below US House's 1,824 — the ordering holds, the 'by more' claim does not). The Ireland comparison is unaffected.

**Suggested fix.** Compute the AUS-states share over the four measured states (≈14.1%) or impute a peer value for TAS, and rewrite the sentence: the argument still holds cleanly for Ireland but only at parity for the Australian states.

### ST6. [series+trend+cross-chamber] 4.5a (alignment-vs-American table + footnote r45b)

> Permutation p < 0.005. The **discrimination** carries more than the coefficient

**Problem.** The footnote presents 'two harsher filters, as robustness only' without disclosing that one of them fails: the stored 'middle 80% by US/UK skew' stratum has US/UK Spearman +0.027, partial +0.028, permutation p = 0.11 (alignment_vs_american.json) — and that filter is precisely the one built to test whether the correlation is carried by the US-skewed institutional tail (senator, congress, federal), the confound §8's item 1a later concedes. The unqualified 'p < 0.005' beside a table whose committed robustness check is null is misleading as written.

**Reviewer's check.** Read alignment_vs_american.json (all strata) and alignment_vs_american.py's stratum definitions and docstring; grepped the writeup for any mention of the failed stratum (none).

**Refuter's verification.** alignment_vs_american.json's 'robustness: middle 80% by US/UK skew' stratum has US_vs_UK Spearman +0.0273, partial +0.0276, perm_p = 0.11 — a null on exactly the filter the script's own comment says was built to test whether the correlation is carried by the US-skewed institutional tail (top_joint: senator, congress, federal…), the confound §8 item 1a concedes. The script comment even asserts 'A broad register shift survives both,' which the stored data refute for the skew trim. Footnote r45b mentions 'two harsher filters, as robustness only' without reporting that one is null; no mention of the failed stratum exists anywhere in the writeup. The other strata (spelling-removed, ≥20, ≥200) do survive at perm_p 0.0.

**Suggested fix.** Report the stratum results in the footnote: survives spelling-removal, ≥20 and ≥200 attestation (perm p < 0.005) but drops to +0.027, p = 0.11 when the most-skewed word deciles are trimmed — consistent with the two-ways reading already conceded in §8.

### SL1. [storyline] §3.8 Future work (closing paragraph)

> Collecting covariates for this study produced something with uses well outside it ... Two families of question follow, and they differ in how novel they are likely to be.

**Problem.** This paragraph is the last text of §3.8, immediately before 'Materials and methods'. Nothing follows it — the promise 'Two families of question follow' is never delivered in printed order. It is plainly the stranded introduction to block F2 (items 23–24), printed ~5 pages after the items it introduces; item 24 even opens 'The more likely to be novel, precisely because of the effort', invoking the two-families framing before the reader has seen it.

**Reviewer's check.** Read §3.8 end-to-end in the compiled text; confirmed the paragraph sits after item 29 and before the Materials and methods header, and that item 24's opening sentence presupposes the novelty framing established only in this later-printed paragraph.

**Refuter's verification.** Both sentences verbatim in §3.8's final paragraph. Verified position: it prints after item 29, immediately before the 'Materials and methods' heading, while the F2 block heading and items 23–24 — the two families it introduces (23 framed as likely replication, 24 as 'the more likely to be novel') — precede it by several pages. In printed order the paragraph's promise is never delivered; it is the F2 intro stranded at the section's end. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Move the paragraph to just before the F2 header ('What the legislator panel enables beyond the register') so it introduces items 23–24 as intended.

### SL2. [storyline] §3.2 Where the norms argument actually lands

> a frontier reader flagged 13 of 35 genuine human floor speeches and only 5 of 35 machine rewrites that had been optimised against a detector (§2.14 stage 5)

**Problem.** The cited section does not contain these numbers. §2.14's stage 5 reports only the judge's mean ai_guess (36/100 for evaders vs 40 for human originals); the 13/35 vs 5/35 flag counts appear nowhere before §3.2. A first-time reader is pointed back to a result that was never presented, and the sharpest claim of §3.2 ('anti-correlated with the truth') rests on it.

**Reviewer's check.** Re-read §2.14's stage-5 subsection and its footnotes and grepped the render for '13 of 35' and '5 of 35': the counts occur only in §3.2. Future-work item 1c quotes yet another statistic for the same judgment (−4 points, t = −1.15) also absent from §2.14.

**Refuter's verification.** §2.14's stage-5 subsection presents only the paired DQI nulls and the judge's mean ai_guess (36 vs 40) — no flag counts, no threshold; '13 of 35'/'5 of 35' appear only in §3.2, and the counts cannot be derived from the means given. The '(§2.14 stage 5)' pointer directs the reader to a result never presented there.

**Suggested fix.** Present the 13/35 and 5/35 counts (with the threshold used to call a text 'flagged') in §2.14's stage-5 subsection or an appendix, and make §3.2's pointer accurate.

*Also flagged by: AL11.*

### SL3. [storyline] §2.14 Quality (applicability paragraph) and Appendix C.2

> Stage 6c locates its source: the collapse appears in raw text from weaker models and vanishes at the frontier

**Problem.** 'Stage 6c' is never defined anywhere in the paper — the stages introduced are 1–6, and stage 6 itself is presented only many pages later ('established in two rounds the same day' hints at sub-rounds but never names 6b/6c). A load-bearing resolution of the applicability collapse is attributed to an arm the reader cannot identify. Appendix C.2 has the twin defect: 'Stage 0's comparison ... recomputed' invokes a 'Stage 0' that appears nowhere else.

**Reviewer's check.** Grepped the compiled text for '6c', '6b', 'Stage 0': 'Stage 6c' occurs once (this sentence), no stage 6b/6c is ever defined, stage 6 is presented ~400 lines later, and 'Stage 0' occurs only in C.2. Source markdown has the same 'Stage 6c' orphan.

**Refuter's verification.** Quote verbatim in §2.14's third paragraph. '6c' occurs exactly once in the render, before stages 1 and 2 are introduced (three paragraphs later) and roughly 380 lines before stage 6 itself is presented; stage 6 is described as run 'in two rounds' but no 6a/6b/6c sub-arm is ever named. Line 1385 cites 'stage 6's humans-keep-evidence result' pages before stage 6 appears, and line 1741's '(§Q1)' matches no section heading — Q1 is a review-item code. All three sub-claims verified. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Rename the reference to 'stage 6' (or define the 6a/6b/6c round structure where stage 6 is introduced), and define or rename 'Stage 0' in C.2.

### SL4. [storyline] §2.12 Coverage

> so it is not exposed to the estimator defect that cost §2.11 its original +0.88

**Problem.** §2.11 never reports a +0.88. Its superseded (shipped) figures are +0.76/+0.86/+0.37 per stage and the pooled effect is +0.387; Appendix B's entry on the defect gives no +0.88 either. Worse, +0.88 does appear prominently elsewhere — as §2.8's birth-cohort gradient (+0.88 per 1,000 words per decade) — so the reader who tries to resolve the number lands on an unrelated result.

**Reviewer's check.** Grepped the render for '0.88': occurrences are §2.8's cohort gradient (twice) and this §2.12 sentence. Checked §2.11's Table 16 (superseded column: +0.76, +0.86, +0.37), the +0.387 pooled figure, and Appendix B item 0a; none contains +0.88.

**Refuter's verification.** Quote verbatim in §2.12 (line 1266). Grep for '0.88' in the render: the only other occurrence is §2.8's unrelated birth-cohort gradient (+0.88 per 1,000 words per decade). §2.11's shipped-superseded stage values are +0.76/+0.86/+0.37 (Table 16) and Appendix C.4 names the superseded pooled run 'the superseded +0.42 run'. The +0.88 is historically real — repo file REVIEW-2026-08-11.md item M3 records 'Pooled alignment effect +0.88 … EXCESS +0.8797' — but the compiled paper never states it, so the retraction has no antecedent a reader can locate, exactly as the finding says. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Replace '+0.88' with the figure §2.11 actually retired (or state it in §2.11's superseded record so the back-reference resolves).

*Also flagged by: XC8.*


---

## MAJOR — PARTIAL

### AL9. [argument-logic] §3.1 (Any fixed check loses to an optimising attacker)

> Point a general-purpose model at its own output, tell it to try again, and it will defeat any check you can put in front of it. This is not a claim about Pangram. It follows from the check being a fixed function and the attacker being an optimiser

**Problem.** The universal claim does not follow from the premises and is contradicted twice by the paper itself. Deductively: fixed function + optimiser entails nothing without a correlated proxy the optimiser can query — and §3.2 concedes exactly this ('a secret-keyed mark cannot be hill-climbed without query access to the verifier'). Empirically: the study's own search failed on 77.5% of targets and converged at zero yield on six, so its data instantiate 'sometimes beatable', not 'will defeat any check'. The section's scoping notes narrow scope but do not repair the 'it follows' framing.

**Reviewer's check.** Compared the deductive claim against §3.2's keyed-watermark argument and against §2.14's own per-target results (16/71 cleared; six zero-yield converged targets).

**Refuter's verification.** Quote verbatim in §3.1 (continues 'with a quality constraint the optimiser itself can satisfy'). Two of the reviewer's three premises hold: the search failed on 77.5% of targets with six converged zero-yield targets (§2.14), so the paper's own numbers do not exhibit 'defeat' in the universal sense; and the deduction silently assumes a correlated proxy exists for any check — the one ingredient (the Opus proxy) that made this attack work. But the third premise fails: §3.2's secret-keyed mark is not an internal counterexample, because §3.1's own scoping note explicitly excludes it — 'the limit applies to post-hoc statistical detection of unmarked text, which is a different problem from provenance asserted at generation time' — and a keyed watermark is generation-time provenance on marked text. The scoping notes ('the argument can be overextended') also temper the universal, and read as a claim about checks-as-security-controls, 22.5% per-target without query access does support a strong weaker version. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Accurate version.** The deductive framing overclaims: 'it will defeat any check' does not follow from fixed-function + optimiser — the study's own search failed on 77.5% of targets and the argument assumes without support that a correlated proxy exists for any check. It should be an empirical scaling claim as the reviewer proposes. However, the keyed-verifier 'counterexample class' cited from §3.2 is explicitly outside §3.1's stated scope (generation-time provenance on marked text is excluded by the section's own scoping note), so the defect is overstatement relative to evidence, not internal contradiction.

**Suggested fix.** Weaken to the supportable form: any check whose output (or a correlated proxy) the attacker can score against is optimisable, and the measured 22.5% is a lower bound on that adversary class — not a defeat theorem for fixed checks generally.

### CE3. [claims-vs-evidence] Introduction, penultimate paragraph

> the register the models were tuned to speak is, on our measurement, the register of the insulated organisational middle — a weak effect, but a first quantitative trace of what Brynjolfsson (9) calls the Turing trap

**Problem.** The identity between the models' register and the insulated middle's register is contradicted at the vocabulary level by the paper's own results. §2.9.7 finds machine-flagged speech "resembles no class tier" (peak z-cosine +0.12 vs a human control's +0.47) and that "post-training moves the model's mix out of the human class geometry"; §2.12 warns that the base-vs-instruct contrast "should not be read as reproducing the thing §2.2 detects" (the archetypal words are absent from the generations). What Results support is only that both models (post-training) and insulated-middle humans are elevated on the aggregate rate of one 407-word list — a much weaker claim than "the register the models were tuned to speak is the register of the insulated middle."

**Reviewer's check.** Traced the claim's evidentiary chain through §2.10 (occupational peak), §2.11 (post-training installs the rate), §2.9.7 (mix-level dissimilarity), and §2.12 (out-of-domain caveat).

**Refuter's verification.** Quote verbatim in the Introduction. The reviewer's vocabulary-level contradiction is real: §2.9.7 finds machine-flagged speech "resembles no class tier" (peak z-cosine +0.12 vs +0.47 for a human control) and that post-training moves model mixes negative against every human class and education centroid; §2.12 warns §2.11 "should not be read as reproducing the thing §2.2 detects." But the finding under-weights two defenses: throughout the paper "the register" is the defined rate-measured construct (the Kobak 407-word rate), under which the sentence is a conjunction of two section results (§2.11: post-training installs the rate; §2.10: the rate peaks at the insulated middle), and "on our measurement" plus "a weak effect" scope the claim to that instrument. So a rate-level version is genuinely supported, and the sentence is not flatly false under the paper's own operationalization — but the "is the register of" identity phrasing invites a mix-level reading the paper's own §2.9.7 measured and rejected.

**Accurate version.** Supported only at the aggregate rate level: post-training elevates the same 407-word marker vocabulary whose human use peaks at the insulated organisational middle (§2.10, §2.11). The identity phrasing ("is the register of the insulated middle") exceeds that — §2.9.7 shows model and machine-flagged vocabulary mixes sit outside the human class geometry, and §2.12 cautions the base/instruct contrast does not model the register actually in Hansard — though the hedges "on our measurement" and "a weak effect" partly scope the claim to the paper's rate-based register construct.

**Suggested fix.** Weaken to a rate-level statement, e.g. "post-training elevates the same marker vocabulary that peaks, among humans, at the insulated organisational middle — a shared word-list rate, not a shared register mix (§2.9.7)."

### CB4. [comparability] §2.6 / Table 6, convergence claim

> the lower a chamber started, the faster it climbed (Spearman between 2006 level and growth −0.56, n = 19)

**Problem.** Growth is computed as the geometric rate between the same two endpoints (footnote: 'endpoints 2006 and 2026'), so the noisy 2006 value enters both the level and the growth. Measurement error in the 2006 endpoint mechanically induces a negative level-growth correlation (regression to the mean / Galton's fallacy in convergence regressions), and the series are shown to be noisy at exactly this scale — US House alone swings 25% between years. The −0.56 is therefore biased toward the convergence conclusion by construction.

**Reviewer's check.** Verified from footnote 12 that growth is endpoint-based on the identical 2006 value used as the level; verified from §2.6's own Table 8 discussion that single-year values swing enough to matter (US House 1,660–2,074, 2026 'near its own floor').

**Refuter's verification.** Quote verbatim at lines 498-499; footnote 12 confirms growth is the geometric rate on the identical 2006/2026 endpoints, so the shared-endpoint (Galton) bias exists and points toward convergence. But the magnitude claim fails: I re-ran the correlation from occurrence_trends.json with the reviewer's own proposed fix (level = 2004–08 mean, growth 2010–26, fully non-overlapping) and got ρ = −0.49 (n=18); level = 2006 alone with growth 2010–26 gives −0.36; OLS log-slope on all years 2008+ gives −0.24. Every non-overlapping specification stays negative. The noise scale also does not support an artifact reading: median within-chamber year-to-year sd is ~50 against a cross-chamber 2006-level spread of ~373 (the quoted US-House 25% swing is stated in the paper as the widest in the corpus, not typical), and the four lowest starters (UK chambers, 605–739 vs ~1,600+) are separated by far more than noise.

**Accurate version.** Growth shares the 2006 endpoint with the level, so the −0.56 carries some regression-to-the-mean inflation; re-computed on non-overlapping data (level = 2004–08 mean, growth 2010–26) the correlation is −0.49, and −0.24 to −0.36 under other artifact-free specifications — the coefficient is modestly inflated but the convergence conclusion survives the correction. The paper should report an artifact-free variant alongside.

**Suggested fix.** Correlate 2006 level with growth computed from non-overlapping data (e.g., level = 2004–08 mean, growth from 2010 onward), or fit the trend on all years rather than endpoints; report the endpoint-based Spearman only with the attenuation/artifact caveat.

*Also flagged by: AL5, ST11.*

### CB5. [comparability] §2.6 Other chambers converge on the level the United States already held

> Chamber levels are therefore partly definitional: a US-derived yardstick will score US speech high whatever is happening. The defensible comparison is the within-chamber trend, and that is where the finding sits.

**Problem.** The section's title and central claims are cross-chamber LEVEL comparisons — 'converging upward on a level the United States already held', Table 7's 'US chambers starting above where the UK still sits two decades later', and Table 8's sd-benchmarks against US House — but the section's own caveat concedes that levels are partly an artifact of the PubMed-derived (American scientific English) instrument and that only within-chamber trends are defensible. The caveat contradicts rather than qualifies the headline: the convergence-to-the-US-level story is precisely the comparison the caveat rules out.

**Reviewer's check.** Read the section's level-based claims (title, Table 7 US-vs-UK level contrast, Table 8) against its own instrument-provenance caveat; the 'US high on a US-derived yardstick' confound predicts exactly the observed ordering (US chambers highest in 1994).

**Refuter's verification.** Quote verbatim at lines ~556-558, and the tension is real: the section title, Table 7's US-vs-UK 1994 contrast and Table 8's US-House benchmarks are cross-chamber level claims, while the caveat demotes levels and no instrument-independent check is run (the paper itself defers that to §3.8 item 1a, explicitly 'the test that would settle §2.6'). But 'contradicts rather than qualifies' overstates it. All chambers are measured on one ruler built on UK Commons 2010–12 text, so the level facts (UK 2026 ≈ US 1994) are well-defined measurements of this register, not artifacts; the section's thesis is precisely that the register in question is American-scientific in character (Table 9's chase-and-flight discrimination supports the American-specificity reading), so US-high-on-a-US-derived-list is partly the claim rather than purely its confound; and the caveat is stated in place as a reading constraint with the falsifying instrument registered as future work.

**Accurate version.** The section's level claims are instrument-relative and its own caveat says so, locating the defensible finding in within-chamber trends while the title and Tables 7–8 frame convergence on levels; the level story should be presented as caveated (or backed by a non-US-derived word list, the check §3.8 already names) rather than as established — but the caveat is an acknowledged limitation the paper flags in place, not an unnoticed contradiction.

**Suggested fix.** Either demote the level-convergence framing to a caveated observation (title on trends, levels flagged as instrument-relative), or add an instrument-independent check (e.g., a UK-derived or domain-neutral word list) showing the US-high ordering survives a non-American yardstick.

### IC2. [internal-consistency] §2.11 Table 16 and footnote 26

> Note the three uncorrected stages sum to +1.99 against that +1.24; the gap is the per-transition control pedestal described below, and closes to about 0.03 under the bias-free estimator

**Problem.** The corrected stage values printed in Table 16 (+0.32, +0.27, +0.06) sum to +0.65, while the text says the end-to-end +1.24 'is untouched'. That leaves a corrected gap of 0.59, not 'about 0.03' — the three statements cannot all be true. Either the corrected end-to-end is ~0.68 (so '+1.24 is untouched' misleads) or the 0.03 claim is wrong. Table 16's caption also labels the correction 'Rogan–Gladen', which elsewhere (§5.1) names the detector-prevalence correction, not the ladder's pedestal-free estimator.

**Reviewer's check.** Summed Table 16's corrected column and compared with the footnote's additivity claim and the '+1.24 is untouched' sentence; confirmed the same 0.03 claim appears as a comment in olmo_ladder.py without reconciling numbers.

**Refuter's verification.** The reviewer's arithmetic is right that a reader cannot reconcile the printed numbers, but the either/or framing ('the 0.03 claim is wrong or...') is resolvable: the study's own review artifact (REVIEW-2026-08-11.md, item L8) shows the bias-free estimator gives stages summing +0.6467 against a bias-free end-to-end of +0.6182 — a residual of 0.03. So the ~0.03 claim is correct for a pair of numbers the paper never prints.

**Accurate version.** The ~0.03 gap refers to the bias-free estimator's own end-to-end (+0.618, per review artifact L8) versus the corrected stage sum (+0.647) — both consistent with Table 16's corrected column. The genuine defects: (a) '+1.24 is untouched' is misleading — under the bias-free estimator the end-to-end moves to ~0.62, and that value appears nowhere in the paper, leaving readers with an apparent unexplained 0.59 gap (1.24 vs 0.65); (b) Table 16's caption label 'Rogan–Gladen corrected' is wrong — §5.1 and the artifacts use that name exclusively for the detector-prevalence correction; the ladder correction is the exact stratified estimator.

**Suggested fix.** Print the corrected end-to-end value alongside the corrected stages, state which pair the ~0.03 gap refers to, and fix the Table 16 caption's correction label.

### OP3. [occupational-prereg] Results 4.6b / prereg prediction 3

> the register peaks at the insulated middle

**Problem.** Registered prediction 3 — 'U is the strongest single component. If any one predictor carries the result it should be upward account-giving' — fails on its natural (entered-alone) reading and is disclosed nowhere: U alone is the weakest of the four components (+0.017, t 1.3, null) against L +0.065 (t 4.8), N +0.066 (t 4.8), D +0.030 (t 2.1). U is strongest only in the joint fit (+0.073, t 4.4), a different quantity. The writeup's failed-predictions list names three items; this is a fourth.

**Reviewer's check.** prereg 'The rest, in order' item 3 against prereg_stage1_results.txt §1 (reproduced); grepped writeup for 'strongest single component' — no disclosure.

**Refuter's verification.** The numbers check out: entered alone, U is the weakest and null component (+0.017, t 1.3) against L +0.065 (t 4.8), N +0.066 (t 4.8), D +0.030 (t 2.1), and no disclosure exists in the writeup ('strongest single component' absent). But the prereg's prediction 3 is genuinely ambiguous between readings, and the joint-fit reading is not strained: the sign-pattern section immediately above it judges the components 'in the joint fit', and there U IS the strongest (+0.073, t 4.4). So calling the entered-alone reading 'natural' and the prediction 'failed' overstates; what survives is an undisclosed reading-dependence.

**Accurate version.** Prediction 3 ('U is the strongest single component') holds on the joint-fit reading the prereg uses for the sign pattern (U +0.073, t 4.4, the largest coefficient) but fails on the entered-alone reading (U is the weakest and null of the four, +0.017, t 1.3). The writeup discloses neither the ambiguity nor the entered-alone result; both readings should be reported.

**Suggested fix.** Disclose that U entered alone is the weakest and null single component, note the joint-fit reading if the authors take prediction 3 to mean the joint model, and add the item to the failed-predictions list.

### OP5. [occupational-prereg] Results 4.6b / registered negative-control rule

> planted in the element pool as a deliberately atheoretical marker of office work — carries more register per standard deviation than any single instrument component (+0.101, t +7.4)

**Problem.** The registered interpretation rule ('If these predict as well as the composite, the model has found office job rather than anything about language') fired: Indoors alone adjR² 0.0103 beats both instruments (charged 0.0087, uncharged 0.0100) and the results file records 'CONTROLS MATCH OR BEAT THE INSTRUMENT — office job concern stands'. The main text presents only the post-hoc adjudication's reading ('a restatement rather than a rival') as settled; nowhere is the reader told the rule as registered returned the opposite verdict. The check was also run 2026-08-24, six days after analysis ('had not been run at analysis time' — disclosed in the prereg but not in §4.6b's main text).

**Reviewer's check.** prereg negative-controls section and its 2026-08-24 adjudication block; prereg_negative_controls.txt verdict lines; git commits c19c36f/ba907b8 dating the check and the ruling.

**Refuter's verification.** The rule fired as the reviewer says: Indoors alone adjR² 0.0103 vs charged 0.0087 / uncharged 0.0100, the results file's verdict line reads 'CONTROLS MATCH OR BEAT THE INSTRUMENT — office job concern stands', the check ran 2026-08-24 (c19c36f), and the ruling rejecting the rule came the same evening (ba907b8). But 'nowhere is the reader told' is too strong: footnote [rnc] explicitly says the prereg 'had planted these two elements as negative controls with an office-job interpretation rule' and that a dated adjudication (2026-08-24, logged in the prereg) 'rejects that rule's implication' — a reader is told a registered rule existed and was overridden post hoc, and the prereg itself carries the full auto-verdict plus the had-not-been-run-at-analysis-time disclosure. What is genuinely missing from the writeup is the statement that the rule's registered condition was met — the text compares Indoors only against single components, never against the composite fits it matched or beat.

**Accurate version.** The writeup discloses the planted controls, the existence of the registered interpretation rule, and the dated post-hoc adjudication rejecting it (footnote [rnc]), but never states that the rule's condition was met — Indoors alone (adjR² 0.0103) matched or beat both composite instruments (0.0087, 0.0100) — reporting only the weaker single-component comparison; the fired condition should be stated in the main text before the description reading.

**Suggested fix.** State in the main text that the registered rule's condition was met (control matches/beats both instruments) and that the interpretation rule was then rejected by a dated post-hoc adjudication, before giving the description reading.


---

## MINOR — CONFIRMED

### AL12. [argument-logic] §2.9.5 (Flight)

> That is chase-and-flight: a marker loses value as it is copied, so the group that holds it abandons the most conspicuous forms first.

**Problem.** The mechanism is asserted flatly in a section whose own dynamic prediction failed: §2.9 reports the peak 'does not' migrate downward across eras, §2.9.6 concedes the era-resolved test 'does not support the cycle's dynamic half', and §2.9.4 says nothing in the vicinity should be cited as established. The rescue offered — 'a cycle already in progress before our first frame would look like this too' — renders the migration prediction unfalsifiable within the data, and §2.9.8 concedes the correlation's monotonicity-in-volume is equally consistent with noise attenuation. 'That is chase-and-flight' overstates a hypothesis the surrounding subsections carefully demote.

**Reviewer's check.** Compared §2.9.5's declarative against §2.9's era test, §2.9.4's hypothesis framing, §2.9.6's concession, and §2.9.8's dual-reading caveat.

**Refuter's verification.** Verified every cross-reference: §2.9 (the peak does not migrate), §2.9.4 (nothing should be cited as established), §2.9.6 (the era-resolved test does not support the cycle's dynamic half), §2.9.8 (monotonicity equally consistent with noise attenuation). The static correlation is real (ρ=−0.42, p=0.004) but 'That is chase-and-flight' asserts the mechanism identification the neighbouring subsections immediately demote to hypothesis.

**Suggested fix.** Rephrase as 'consistent with chase-and-flight' and point forward to the pre-1996 class-coded Commons test (§3.8) as the discriminator, matching the register of §2.9.4/2.9.6.

### CP5. [calibration+prevalence] 4.1 (specificity denominator)

> ### 4.1 The detector makes zero false positives on 1,260 pre-2022 speeches

**Problem.** The 1,260 misdescribes the control set two ways. (a) 37 of the 1,260 are dated January–June 2022, so "pre-2022" is literally false (they are pre-ChatGPT). (b) The 1,260 counts only pangram_p4_verdicts.csv controls: it includes TAS's 60 (a chamber excluded as uncalibratable) and the superseded-frame MB 60, while excluding the controls that actually calibrate the headline — UK (124), IE (71), CA-FED uniform-draw, MB-redraw (91), and all short-band controls. The estimator's own control pool is 1,699 segments, also 0 flagged, so the honest number is larger and cleaner than the one quoted.

**Reviewer's check.** Counted ctl rows by chamber and date in pangram_p4_verdicts.csv (18×60 + CA-FED 180 = 1,260; 37 dated 2022-01..06); ran banded_prevalence.py (pre-AI controls: 0/1,699 segments, 0/361,509 words) and prevalence_report.py (1260/1260 = 100.00% [99.7%, 100.0%]).

**Refuter's verification.** Quote verbatim. pangram_p4_verdicts.csv ctl rows = 1,260 (18 chambers x 60 + CA-FED 180), including TAS's 60 (a chamber excluded as regime-flagged) and the superseded Manitoba 60; 37 of them are dated 2022-02 through 2022-06, so 'pre-2022' is literally false for those (they are pre-ChatGPT). The estimator's own control pool — UK 124, IE 71, CA-FED 98, MB-redraw 91, plus short-band controls — is 1,699 segments, also 0 flagged (0/361,509 words), so the honest number is larger and cleaner. Minor because zero-false-positive is true on both denominators.

**Suggested fix.** Say "pre-ChatGPT" (or "pre-2022-07"), and either report specificity on the estimator's own control pool (0/1,699) or state precisely which controls the 1,260 covers.

### CP6. [calibration+prevalence] 4.2 (Manitoba repair)

> **Manitoba's 13.1% depends on a repaired extractor**, and without it the chamber reads 5.3%.

**Problem.** The comparison mixes estimators: 13.1% is the Mixed-fraction-corrected word rate, but 5.3% is the old frame's full-weight (Mixed-uncorrected) combined rate (computed 5.31%). The like-for-like fraction-corrected pre-fix figure is 4.33% (long band alone 5.02%). Conservative for the point being made, but the two numbers are not computed the same way.

**Reviewer's check.** Recomputed the superseded MB sample (pangram_p4_verdicts MB prev + shortband MB prev) both fraction-weighted (4.33%) and full-weight (5.31%), against the redraw's 13.13% from banded_prevalence.py.

**Refuter's verification.** Quote verbatim. Recomputed the superseded MB sample (p4 MB prev rows + shortband MB prev rows, n=188): full-weight (Mixed-uncorrected) 5.31%, fraction-corrected 4.33% (long band alone 5.02%). The 13.1% is the fraction-corrected redraw rate (13.13% from banded_prevalence.py), so the sentence compares a fraction-corrected number to an uncorrected one. Conservative for the point being made (4.33% would widen the contrast), but the estimators are mixed exactly as the reviewer states.

**Suggested fix.** Report 4.3% as the pre-fix comparator (or label 5.3% as the uncorrected rate).

### CP7. [calibration+prevalence] 4.1 (NB rescore)

> disagreements run net upward (33 segments moved out of Human, 9 the other way)

**Problem.** The cross-tab shows 11 segments moved into Human (AI→Human 9, Mixed→Human 2), not 9. The net (+22 = 33 − 11) is only consistent with 11, and matches the 122→144 change; "9" counts only the AI→Human cell.

**Reviewer's check.** Ran nb_p3_vs_p4.py; read the printed cross-tab (Human row: 14 AI + 19 Mixed = 33 out; AI→Human 9 and Mixed→Human 2 = 11 in). All other cells of the table in §4.1 (122/144, 92%, 60/60, 0% in 2020–22, 40/40 synthetic) reproduce.

**Refuter's verification.** Quote verbatim. nb_p3_vs_p4.py's cross-tab: out of Human = 14 (Human→AI) + 19 (Human→Mixed) = 33; into Human = 9 (AI→Human) + 2 (Mixed→Human) = 11, not 9. Net +22 is consistent only with 11 and matches the 122→144 flag change (114+8=122 → 118+26=144). All neighbouring figures in the section verify (92% agreement, 60/60 control, 0% in 2020–22, 40/40 synthetic). The '9' counts only the AI→Human cell.

**Suggested fix.** Change "9 the other way" to "11 the other way (9 from AI, 2 from Mixed)".

### CP8. [calibration+prevalence] 4.2 (Mixed-fraction bookkeeping, incl. footnote r42f)

> read off the dashboard result by result for all 132 Mixed segments the API did not cover. Those harvested Mixed segments average **0.435** machine (n=132, sd 0.219, range 0.11–1.00)

**Problem.** The counts are stale against the committed artifacts. The estimator consumes 135 harvested Mixed fractions (mean 0.433, sd 0.214, range 0.11–1.00), not 132/0.435/0.219; footnote r42f's "151 harvested individually" does not match fraction_ai_harvested.json (238 entries; 155 consumed by load()); and "the 154 AI verdicts not harvested individually are carried at the measured constant" does not match the estimator, which carries 163 rows at AI_CONST. (The 1,431 recorded-fraction count, the 0.9965/n=148 and 1.0000/n=19 constants, the 1,246 zero Human fractions, and the 0.81 minimum all verify.)

**Reviewer's check.** Instrumented banded_prevalence.ai_fraction() to log harvest-consumed rows (135 Mixed, 19 AI, 1 Human = 155) and rows carried at AI_CONST (163); computed mean/sd/range of the consumed Mixed fractions; counted json entries and fraction_ai-bearing CSV rows.

**Refuter's verification.** Quote verbatim. Instrumenting ai_fraction() inside load(): 135 harvested Mixed fractions are consumed during load (mean 0.433, sd 0.214), of which 134 survive into the final sample (one, cmbprev076, is discarded by the MB-redraw replacement; the kept set has mean 0.435, sd 0.213, range 0.11–1.00) — under neither reading is n=132 or sd 0.219 correct. Footnote r42f's '151 harvested individually' does not match fraction_ai_harvested.json (238 entries; 155 consumed, 154 kept), and 'the 154 AI verdicts not harvested are carried at the measured constant' does not match the estimator (163 final-sample AI rows at AI_CONST). The claims the reviewer passed do verify: 1,431 recorded fractions, 1,246 Human zeros, 0.9965 over n=148, minimum AI 0.81.

**Suggested fix.** Refresh the counts from the committed artifacts: 135 harvested Mixed (mean 0.433, sd 0.214), 238 entries in the json (155 consumed), 163 AI verdicts at the constant.

### CP9. [calibration+prevalence] 4.2 (ratio-estimator bias check)

> its finite-sample bias is nil in practice (bootstrap mean 10.30% against a plug-in 10.31%, a −0.005-point gap)

**Problem.** Neither number corresponds to any current figure: the committed pooled sample gives bootstrap mean 9.02% against plug-in 9.03% (gap −0.002 points); the long band alone is 10.29%. The quoted pair is from an earlier sample state. The qualitative claim (bias nil) does reproduce.

**Reviewer's check.** Re-ran the 20,000-draw bootstrap (seed 7) over banded_prevalence.load()'s prevalence rows and compared its mean to the plug-in ratio.

**Refuter's verification.** Quote verbatim. Re-ran the 20,000-draw seed-7 bootstrap over load()'s prevalence rows: bootstrap mean 9.024% against plug-in 9.025%, gap −0.002 points; the long band alone has plug-in 10.29%. The quoted 10.30/10.31 pair matches no current figure and is evidently from an earlier (long-band or pre-update) sample state. The qualitative claim — bias nil — reproduces; the numbers are stale.

**Suggested fix.** Replace with the current pair: bootstrap mean 9.02% vs plug-in 9.03%.

*Also flagged by: CB8, SL6, XC12.*

### CP10. [calibration+prevalence] 4.2 (word-weight concentration)

> because the word-weight is not concentrated (the longest tenth of sampled segments hold only 14% of the words)

**Problem.** On the pooled prevalence sample the longest tenth holds 17.7% of the words; 13.7% (~14%) is true only of the long band. The sentence's scope ("sampled segments", in a paragraph about the pooled estimator) does not match the sample the number was computed on.

**Reviewer's check.** Computed the top-decile-by-length word share on banded_prevalence.load()'s prevalence rows (17.7% all bands, 13.7% long band only).

**Refuter's verification.** Quote verbatim. On the pooled prevalence sample the longest tenth holds 17.7% of the words; 13.7% (≈14%) is true only of the long band alone. The sentence sits in the paragraph about the pooled estimator and says 'sampled segments', so its stated scope does not match the sample the number was computed on. Minor: the qualitative point (not concentrated) holds on either scope.

**Suggested fix.** Either quote 18% for the pooled sample or scope the sentence to the long band.

### CP11. [calibration+prevalence] 4.2 (CA-FED genre-arm comparison)

> Read as a chamber rate it gives 16.5%; the uniform draw of 120 prevalence segments gives **18.5%**, and the uniform draw is what the table reports.

**Problem.** The 16.5% is not reproducible from any committed artifact I could locate. The direct word-and-fraction-weighted rate of the genre-arm prevalence sample is 20.7% (prevalence_report.py's CA-FED row; unchanged when the cashrt short band is added), which sits ABOVE the uniform draw's 18.5% and would flip the comparison's direction. If 16.5% is a business-share reweighting of the three genre rates, no committed script computes it and the text does not say so — against the section's "every number reproduces from a committed script".

**Reviewer's check.** Ran prevalence_report.py (CA-FED 20.7%); recomputed the genre-arm rate with and without the cashrt short band (20.7% both); grepped the repo's scripts and artifacts for a source of 16.5% and found none.

**Refuter's verification.** Quote verbatim. The genre arm's direct word-and-fraction-weighted rate is 20.68% (prevalence_report.py's CA-FED row prints 20.7%; full-weight 24.8%, segment rate 22.8%) — above the uniform draw's 18.5%, flipping the comparison's stated direction. Grepped the repo's scripts and artifacts: nothing produces 16.5% (the only '16.5' hit is an unrelated style_coverage.py line), and the text does not describe any reweighting. One correction to the reviewer's check: adding the cashrt short band moves the genre-arm rate to 19.0%, not 'unchanged at 20.7%' — still above 18.5%, so the conclusion is unaffected. Against the section's own 'every number reproduces from a committed script', the 16.5% is unreproducible.

**Suggested fix.** Either commit the script that produces 16.5% and state the reweighting, or quote the unweighted genre-arm rate 20.7% and rewrite the sentence accordingly.

### CE4. [claims-vs-evidence] Abstract (also Introduction and Discussion opening)

> Run as a level series, its rise begins in 1994–96 [abstract as rewritten 2026-08-25; the original quoted sentence was replaced by the Kobak-contextualisation, but the scoping issue PERSISTS in the new wording]

**Problem.** The 1994–96 onset is measured in one chamber only. §2.5's turning point is the minimum of the UK Commons series (the only series extending before 1994 with a visible decline-then-turn); Table 7 shows the two US chambers already at 1,314–1,515 per 100k in 1994 and essentially flat (+0.4–0.5%/yr), and Table 6 shows three chambers declining 2006–26. §2.6's own summary is "chambers converging upward on a level the United States already held before the consumer web, while the United States barely moves." The generic "its rise begins in 1994–96" (Discussion: "rising since 1994–96") is broader than the single-chamber dating; "predates the models by decades" is fully supported, but the onset claim is UK-specific.

**Reviewer's check.** Read §2.5 and footnote 9 (UK-only turning point, day-clustered bootstrap) and Tables 6–8 (US flat/high since 1994, three decliners).

**Refuter's verification.** Quote verbatim in the abstract; "rising since 1994–96" repeated in the Discussion opening. Re-checked the evidence: §2.5's turning point is the minimum of the UK Commons instrument-minus-placebo series (the only series extending before 1994 with a decline-then-turn; footnote 9's day-clustered bootstrap is UK-only). Table 7 confirms US House at 1,515 and US Senate at 1,314 per 100k already in 1994, moving +0.4–0.5%/yr — no rise; Table 6 shows US House, US Senate and PEI declining 2006–26; §2.6's own summary is chambers "converging upward on a level the United States already held before the consumer web, while the United States barely moves." So the generic onset claim is dated in one chamber and is false as a description of the US series. "Predates the models by decades" survives everywhere (the US was already at the level in 1994); the unscoped onset dating does not. Minor scoping defect, but it survives attack — §2.5's section title makes the same generic claim, so no in-body scoping rescues the abstract.

**Suggested fix.** Scope the dating: "in the one series long enough to see a turn (UK Commons), the rise begins in 1994–96; the US chambers already held the destination level in 1994."

### CE6. [claims-vs-evidence] Introduction, instrument paragraph

> their agreement, not either alone, carries the study's claims.

**Problem.** The Results carry the study's main claims on one instrument each, not on agreement: prevalence, spread and the genre rates on Pangram alone; the 1994–96 onset, cohort, class, and occupational structure on the register instrument alone (whose frequency arm §5.3 itself demotes to "descriptive, not inferential"). Demonstrated agreement is limited to the genre ladder (§2.3, "the one place where the lexicon arm's inference is confirmed") and the coarse §2.7 level test. As a description of the study's evidentiary structure the sentence overstates cross-validation.

**Reviewer's check.** Mapped each headline Results claim to the instrument(s) supporting it; confirmed §2.3's "one place" phrasing and §5.3's demotion.

**Refuter's verification.** Quote verbatim in the Introduction's instrument paragraph. The Results' own opening contradicts it directly: "Two instruments, run separately, carry the results" — Pangram "answers the prevalence question," the register "carries the historical and social results." I mapped the headline claims: 9.03%, elevenfold spread, genre rates — Pangram alone (Table 2, Table 3); 1994–96 onset, cohort, class, occupational structure — register alone (with §5.3 demoting its frequency arm to descriptive); permeation (§2.13) — a third, likelihood-based instrument. Demonstrated agreement is the genre ladder (§2.3's "one place" phrasing verified) and the coarse §2.7 every-chamber level test. The best available defense — that "claims" means only the overlap region — fails against the sentence's plain reading as a description of the whole study's evidentiary structure, which the paper's own §2 opening states otherwise.

**Suggested fix.** Replace with an accurate division of labour: the detector carries prevalence, the register carries history and social structure, and they corroborate each other where both can see (the genre ladder).

### CE8. [claims-vs-evidence] Introduction, instrument paragraph

> the register is transparent, cheap at corpus scale, and robust to the light editing that defeats detectors, but coarse

**Problem.** The editing-robustness property is asserted but never tested anywhere in Results. No section runs the register instrument on edited or detector-evading text (the bypass variants were scored by Pangram and DQI-graded, not lexicon-scored); the nearest evidence, §2.5's obvious-tells-fall/rare-set-climbs contrast, concerns model-side suppression of notorious words, not robustness of the instrument to editing.

**Reviewer's check.** Grepped the compiled paper for any test of the register instrument on edited/evaded text; the phrase occurs only in the Introduction.

**Refuter's verification.** Quote verbatim in the Introduction; the phrase occurs nowhere else. I searched the paper for any test of the register instrument on edited or detector-evading text: the bypass rewrites (§2.14 stages 4–5) are scored by Pangram and DQI-graded only — no lexicon scoring of any rewrite exists; §3.8 item 15 even notes that what the screen misses "is a different quantity from what Pangram misses on edited text," still with no register-arm test. The nearest evidence actually cuts against the assertion for part of the list: §2.5 shows the conspicuous tells were "trained or edited away" (peaking 2025 then falling), i.e. targeted editing does move the lexical rate for notorious words, with only the rare Kobak set still climbing. The property may be analytically plausible for corpus-level rates under untargeted light editing, but the paper neither makes that argument nor runs the test, so the asserted-but-untested defect survives.

**Suggested fix.** Either drop "robust to the light editing that defeats detectors" or downgrade to an expectation ("and, because it counts common vocabulary rather than statistical texture, plausibly less sensitive to light editing — untested here").

### CE9. [claims-vs-evidence] Abstract, first sentence

> We measure machine-drafted speech across 22 legislative chambers in five countries with two independent instruments: a commercial AI-text detector (Pangram), calibrated against each chamber's own pre-2022 record (specificity 1,260/1,260)

**Problem.** Calibration covers 21 of the 22 chambers (1,260 = 21 × 60; §4.1: Tasmania's transcription-regime change means "no control can calibrate it"), and the prevalence measurement covers 20 (Methods: New Brunswick has no uniform prevalence sample; TAS excluded). "Each chamber's own" and the framing that machine-drafted speech is measured "across 22 chambers" overstate coverage of the prevalence/calibration arms; only the covariate arms use all 22.

**Reviewer's check.** Cross-checked the abstract against §2.2 ("20 chambers"), §4's parenthetical ("the prevalence arm covers 20 of them"), and §4.1's Tasmania finding; verified 21 × 60 = 1,260.

**Refuter's verification.** Quote verbatim as the abstract's first sentence; the same "each chamber's own... 1,260 of 1,260" formulation repeats in the Introduction. Arithmetic re-verified: §4 specifies 60 control segments per chamber, and 1,260 = 21 × 60, not 22 × 60 = 1,320. §4.1 confirms the missing chamber: Tasmania's transcription-regime step means "No pre-AI text exists in Tasmania's current regime, so no control can calibrate it. TAS is reported but excluded." §4's parenthetical confirms "the prevalence arm covers 20 of them" (NB pilot has no uniform prevalence sample; TAS excluded), matching §2.2's "3,519 segments in 20 chambers." So the machine-drafted-speech measurement runs in 20 chambers, calibration in 21, and only the covariate/register arms use 22 — the abstract's "each chamber's own" is false for Tasmania and irreconcilable with its own 1,260 figure. Minor, but no defeating context exists in the abstract or intro.

**Suggested fix.** State the arm coverage: e.g. "across 22 chambers (prevalence measured in 20; the detector calibrated on 21 chambers' own pre-2022 records, 1,260/1,260)."

### CC7. [cohort+class] 4.6, second bullet + footnote r46a

> the within-chamber, word-weighted correlation of the register rate is **+0.325 with birth year** against **+0.302 with spoken year**, and birth is the stronger of the two in 15 of the 22 chambers

**Problem.** The footnote claims 'Within-chamber correlations are on the same rows', but the committed script computes r_spoken over ALL member-years while r_birth uses only birth-known rows; its printed output shows the OPPOSITE ordering (r_spoken +0.389 > r_birth +0.376, birth stronger in only 11 of 22 with one tie). The claim is correct — I verified it reproduces exactly under the same-rows restriction — but a referee running the cited command sees it contradicted.

**Reviewer's check.** Ran `python3 cohort_vs_period.py` and counted per-chamber r_birth>r_spoken (11/22, 1 tie); reimplemented the correlation restricted to birth-known rows using the script's wcorr — reproduces +0.325/+0.302 and 15/22 exactly.

**Refuter's verification.** The committed script computes r_spoken over all member-years but r_birth only on birth-known rows; its actual output shows the opposite pooled ordering (r_spoken +0.389 > r_birth +0.376), despite fn18 claiming 'Within-chamber correlations are on the same rows.' Restricting r_spoken to the birth-known rows using the script's own wcorr reproduces the paper exactly: pooled +0.325 birth vs +0.302 spoken, birth stronger in 15 of 22 chambers (0 ties). The paper's claim is substantively correct, but the cited invocation contradicts it — a script/text mismatch, correctly graded minor. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Make the script compute r_spoken on the birth-known rows (matching the footnote), so the printed output agrees with the text.

### CC8. [cohort+class] 4.6a, 'The II-over-I crossover is established'

> the inverse-variance meta-analysis across chambers gives **+0.59 per 1,000, z = 3.50**

**Problem.** No committed script computes the within-chamber meta-analysis, and its figures are stale against the 22-chamber data the rest of the section uses: reconstructing it (per-chamber II−I contrast, cohort-adjusted, equal member weights, HC1) on current data gives 18 of 20 chambers positive, meta +0.67, z 5.8, with QLD (t 2.9) and TAS (t 2.1) also individually significant — so '9 of 12' and 'the three with the power to detect it' describe a superseded panel. The claim is conservative rather than wrong, but the bolded 'established' result rests on an ad hoc computation.

**Reviewer's check.** Reimplemented the per-chamber contrast + inverse-variance meta on the current committed data (UK +0.68, US House +0.82, MB +2.27 all match the printed per-chamber estimates); confirmed no script computes it (METHODOLOGY describes it but names no file).

**Refuter's verification.** No committed script computes it (repo-wide grep; METHODOLOGY.md describes the estimator, concedes it 'was computed AFTER the disagreement was observed', and names no file). Reimplementing it on the current committed data (per-chamber II−I contrast, cohort-adjusted, equal member weights, HC1, inverse-variance pooling) I get 20 chambers, 18 positive, meta +0.672, z +5.82, with the paper's three named per-chamber estimates matching (UK +0.683, US House +0.818, MB +2.272) and QLD (t 2.90) and TAS (t 2.12) also individually significant — so '9 of 12' and 'the three with the power to detect it' describe the superseded pre-expansion panel. The printed figure is conservative rather than wrong, but the bolded result rests on an uncommitted, stale computation. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Commit the meta-analysis script and refresh the counts to the 22-chamber panel (which strengthens the claim).

### CC9. [cohort+class] 4.6a, 'Cohort towers over all of it'

> Birth decade is **+1.01 (t = 10.96)** in the member-year panel with year fixed effects — the citable figure

**Problem.** Running panel_estimation.py on the current 22-chamber data gives birthdec +0.915 (t 12.54) in the class panel and +0.924/+0.933 in the education panels — no committed output yields +1.01 (t 10.96). The sentence invokes 'three countries and 22 chambers' but the quoted number appears to predate the 2026-08-17 nine-chamber expansion.

**Reviewer's check.** Ran `python3 panel_estimation.py` (22 chambers, 46,248 member-years) and compared every printed birthdec coefficient to the quoted figure.

**Refuter's verification.** Ran `panel_estimation.py` on the current data (46,248 member-years, 22 chambers): birthdec is +0.915 (t 12.54) in the class panel, +0.924 (t 11.45) and +0.933 (t 13.46) in the education panels, +1.064 (t 6.91) in the 704-member origin panel. No committed output yields +1.01 (t 10.96); METHODOLOGY.md repeats the same stale figure. The 'citable figure' predates the 2026-08-17 nine-chamber expansion and should be re-quoted (~+0.92, t ~12.5). [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Re-quote the citable cohort figure from the current panel run (+0.92, t 12.5) or state which panel state produced +1.01.

### CC10. [cohort+class] Appendix D.3 (and the 4.6a prominence/era tables) + footnote rpb

> [^rpb]: `python plot_class_by_era.py`-adjacent computation; per-bucket means, standard errors and counts in `prominence_buckets.csv`.

**Problem.** Neither prominence_buckets.csv nor class_by_era.csv / class_by_era_grouped.csv has a committed generating script — the plot_class_by_era*.py scripts only READ the CSVs, and the footnote itself concedes an '-adjacent computation'. The D.3 bucket table, the 4.6a quintile table, and the era figure therefore cannot be regenerated from the repository (the printed values do match the committed CSVs).

**Reviewer's check.** Grepped all .py files for writers of these CSVs (none); read both plot scripts (read-only); verified every table value and n against the CSVs (all match, including n=1,286/2,257/3,353/6,896).

**Refuter's verification.** Repo-wide grep: the only code referencing prominence_buckets.csv / class_by_era*.csv is the two plot scripts (both read-only — they open the CSVs with csv.DictReader and never write) and latex/reformat.py. No committed script generates these CSVs, and the footnote itself concedes an '-adjacent computation'. The printed D.3 bucket table and the era figure values do match the committed CSVs (spot-checked: all-22 quintiles +0.003/−0.067/−0.070/+0.023/−0.059; group ns 1,286/2,257/3,353/6,896), so the defect is regenerability, not accuracy — minor, as graded. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Commit the scripts that compute the member-level quintile means and the chamber×half-decade class means, and cite them in rpb and r46cls.

### CC11. [cohort+class] 4.6a, clustering paragraph vs provincial table

> class II falls from t = 3.40 to 1.48, IVab from 3.51 to 1.49, VIIab from −4.04 to −1.84, the education ladder from 2.96 to 0.78

**Problem.** These 'before clustering' t's do not match the unclustered provincial table printed three subsections later (II t = 4.23, IVab 3.24, VIIab −4.22), so the same subsection quotes two inconsistent unclustered baselines for the same estimates without saying the specifications differ; neither set is producible from a committed script.

**Reviewer's check.** Compared the paragraph's t's against the printed provincial table; ran covariate_study.py and class_origin.py --dist (neither outputs either set).

**Refuter's verification.** The same section's Table 13 prints unclustered provincial t's of II 4.23, IVab 3.24, VIIab −4.22 — a different unclustered baseline for the same estimates, with no statement that the specifications differ (the 2.96 education figure matches §2.9.3's cohort-controlled +0.315 t 2.96, supporting the cohort-controlled-variant reading of the paragraph's set). I ran covariate_study.py, class_origin.py --dist, formation_window.py, panel_estimation.py and member_level_estimation.py: none outputs either set, and no committed script with member clustering fits a provincial EGP regression. Two inconsistent, both-unreproducible baselines in one subsection. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** State which specification each set of t's comes from (the 3.40/3.51/−4.04 set appears to be a cohort-controlled variant), or use one baseline consistently, and commit its script.

### CC12. [cohort+class] 4.6a, education levels table

> Read as levels rather than as a ladder (22 chambers, cohort controlled, baseline bachelor)

**Problem.** The table is computed on the four-predictor complete-case subsample (per-level ns 234/371/1,194/1,271/991, summing to ~4,061), not the full education sample the label implies (4,820 members; the committed member_level_estimation.py prints different contrasts there, e.g. secondary −0.156 t −2.79 and Wald p=0.0001, not the quoted p=0.0025). On the complete-case sample I reproduce the table only approximately (secondary −0.160 t −2.58 vs printed −0.166 t −2.69), indicating the underlying covariate files have drifted since it was computed.

**Reviewer's check.** Ran member_level_estimation.py (full education sample) and refit the level-dummy contrast + Wald on the joint_predictors complete-case sample using the study's own functions; Wald p=0.0025 reproduces only on the complete-case sample.

**Refuter's verification.** Table 11's per-level ns (234/371/1,194/1,271/991) sum to ~4,061 — the four-predictor complete-case subsample, not the full education sample the label implies. The committed member_level_estimation.py on the full sample (n=4,820) prints materially different contrasts: secondary −0.156 (t −2.79), college −0.151 (t −3.22), graduate +0.017, professional −0.079 (t −2.13), Wald p=0.0001 — not the printed −0.166 (t −2.69)/−0.139/−0.008/−0.091/p=0.0025. Refitting level dummies with cohort on the joint_predictors complete-case sample gives Wald p≈0.003 and approximately (not exactly) the printed contrasts, consistent with the reviewer's drift observation. The table is mislabeled as to sample and not regenerable from a committed script. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Label the table as the complete-case sample, regenerate it from a committed script, and reconcile the per-level ns.

### CB6. [comparability] §2.6, Ireland / federal Canada aside

> Ireland and federal Canada, excluded from both tables for entering late (2018, 2015), enter high — 1,603 and 1,865 — and move like chambers already near the ceiling (+2.6%/yr and −0.7%/yr).

**Problem.** Their per-year growth rates are computed over 2018–26 and 2015–26 windows but are set beside the other chambers' 2006–26 rates as if comparable. The short windows are dominated by the post-2023 acceleration the paper itself documents (NB +23.7%/yr post-2023), so a per-year rate over 8 years is not on the same scale as one over 20; 'near the ceiling' is inferred from incomparable spans.

**Reviewer's check.** Compared the windows behind each per-year figure (footnote 12 endpoints 2006/2026 vs the stated 2018/2015 entry years) and noted the paper's own evidence that post-2023 growth is an order of magnitude above secular growth.

**Refuter's verification.** Quote verbatim at lines 521-523, and the defect survives the direct test. I ran the reviewer's fix on occurrence_trends.json: on the shared 2018–26 window Ireland's +2.6%/yr ranks 2nd of 20 chambers (above UK +1.7, Wales +2.0, most others +0.8–2.2) — on a like-for-like span Ireland moves like one of the fastest climbers, not a ceiling chamber, so the paper's inference for Ireland actually reverses under the comparable-window check (and even against Table 6's own 20-year column, +2.6%/yr would rank third). Federal Canada's ceiling reading survives (−0.7%/yr is 18th of 19 on the shared 2015–26 window). So: spans incomparable as charged; the 'near the ceiling' characterization fails for Ireland and holds only for federal Canada; the 'enter high' levels point stands.

**Suggested fix.** Quote their growth over a window shared with the comparison set (e.g., 2018–26 for all chambers side by side), or drop the per-year comparison and rest the 'enter high' point on levels alone with the level caveat.

### CB7. [comparability] §3.8 Future work, item 4 (between-chamber spread)

> The leading untested candidate is genre composition — the House runs far more one-minute floor speeches, the SO31-type format §2.3 measures at ˜37% machine

**Problem.** §2.3's word-and-fraction-weighted SO31 rate — the study's declared unit for every rate — is 32.3%; ~37% is the segment-weighted figure (36.7%) the paper disavows as measuring the packer. The deprecated unit resurfaces where it inflates the candidate explanation for the House–Senate gap.

**Reviewer's check.** Matched '~37%' against §2.3's three reported SO31 figures: 32.3% (word/fraction-weighted, Table 3), 35.8% (binary), 36.7% (segment-weighted); only the disavowed segment figure rounds to 37%.

**Refuter's verification.** Quote verbatim at lines 2224-2225. §2.3 reports three SO31 figures: 32.3% word/fraction-weighted (Table 3, the unit the study declares for every rate), 35.8% binary, and 36.7% segment-weighted — the unit §2.3 itself disavows as measuring the packer. Only 36.7% rounds to ~37% (35.8% would round to ~36%), so the deprecated segment-weighted figure resurfaces where it inflates the candidate explanation. The consistent figure is 32.3% (≈32%). No defeating context found; the fix is a one-number substitution.

**Suggested fix.** Quote 32.3% (or '≈32%'), consistent with the study's own weighting rule.

### CB9. [comparability] §2.14 Bypass study, flip-rate paragraph

> if merely "soften off AI" is the goal, 17 of 38 New Brunswick targets (45%) cleared it

**Problem.** The denominator 38 is the count of NB v3 targets that yielded a submittable variant, not the 40 searched — the exact denominator choice the paper rejects three paragraphs earlier ('The denominator is targets searched, not targets that yielded... Counting only targets that yielded makes the rate conditional on the attack having already half-succeeded'). Like-for-like with the 22.5% figure, the number is 17/40 = 42.5%.

**Reviewer's check.** Cross-referenced 38 against Table 31 and its note ('An earlier version listed 38, 25 and 27 — the counts that produced at least one variant clearing the submission gate') and against NB v3's stated 40 searched / 2 zero-yield.

**Refuter's verification.** Quote verbatim at line 1608. Verified from bypass_v3_pangram.json: exactly 38 targets produced ≥1 submitted variant (of 40 searched, 2 zero-yield per Table 22) and exactly 17 of them got ≥1 Mixed-or-Human verdict — so 38 is the yielded-targets denominator. Three paragraphs earlier the paper rules 'The denominator is targets searched, not targets that yielded... Counting only targets that yielded makes the rate conditional on the attack having already half-succeeded', and Appendix C's Table 31 note retracts exactly this denominator ('An earlier version listed 38, 25 and 27 — the counts that produced at least one variant clearing the submission gate'). Like-for-like with the 22.5% figure the number is 17/40 = 42.5%. Minor but real inconsistency with the paper's own rule.

**Suggested fix.** Report 17/40 = 42.5% for consistency with the per-target denominator rule.

*Also flagged by: IC11, QB5, XC6.*

### XC5. [cross-cutting] §2.9.2 Table 13 (provincial class estimates)

> gives 897 members and 5,294 member-years, 57.5% of the words

**Problem.** Table 13's member column sums to 944 (29+435+180+186+45+53+16), not the 897 stated in the text introducing it; no exclusion accounting for the 47-member difference is given.

**Reviewer's check.** Summed the seven class rows of Table 13 and compared with the stated total.

**Refuter's verification.** Table 13's member column sums to 29+435+180+186+45+53+16 = 944. Rerunning class_origin.py (named in the section's own footnote 22) reproduces exactly those per-class counts — 944 coded members with substantive EGP codes, out of 1,071 member records — so the table column reports coded members while the introducing sentence claims the coding 'gives 897 members'. No script in the repo prints 897 or 5,294, and neither the section nor its footnote accounts for the 47-member difference (presumably members coded but absent from the joined regression sample). [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Reconcile the counts (e.g. state which coded members are excluded from the regression and why the table counts differ), or correct whichever number is stale.

*Also flagged by: IC12.*

### XC6. [cross-cutting] §2.14 (bypass, flip-bar target rate)

> if merely ”soften off AI” is the goal, 17 of 38 New Brunswick targets (45%) cleared it

**Problem.** The NB v3 denominator is 40 targets everywhere else (Table 22; Appendix C.3 explicitly says the earlier count of 38 — targets that yielded a gate-clearing variant — 'understated the attack surface' and was corrected to targets searched). This sentence still uses the retired 38 denominator; on 40 it is 42.5%.

**Reviewer's check.** Compared against Table 22 (searched = 40) and Appendix C.3's correction note.

**Refuter's verification.** Table 22 gives NB v3 searched = 40, and §2.14's own paragraph ('The denominator is targets searched, not targets that yielded a variant... they belong in the denominator') plus Appendix C.3 ('An earlier version listed 38, 25 and 27 — the counts that produced at least one variant clearing the submission gate — which understated the attack surface') establish 40 as the corrected convention. The flip-bar sentence still uses the retired 38 with no signal that a conditional-on-yield denominator is intended; on 40 it is 42.5%. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Restate as 17 of 40 (42.5%), or explicitly say the flip count is conditional on yield if that is intended.

*Also flagged by: CB9, IC11, QB5.*

### XC8. [cross-cutting] §2.12 (coverage)

> it is not exposed to the estimator defect that cost §2.11 its original +0.88

**Problem.** No +0.88 appears in §2.11 or anywhere else in the paper: §2.11's superseded values are +0.76/+0.86/+0.37 per stage (Table 16), and the artifacts table calls the superseded preference run 'the superseded +0.42 run'. The back-reference points at a number the paper never reports.

**Reviewer's check.** Searched the full render for '0.88' and compared all superseded §2.11 figures.

**Refuter's verification.** No +0.88 for §2.11 appears anywhere in the render (the only 0.88 is §2.8's unrelated cohort coefficient); the superseded stage values are +0.76/+0.86/+0.37 (Table 16) and the artifacts table records 'the superseded +0.42 run'. The back-reference is therefore untraceable within the paper. One nuance for the fix: the number is historically genuine — the first draft (commit a04d703) reported 'Pooled alignment effect +0.88 †' — so the correct repair is to record the +0.88 in Appendix B's superseded list (or cite the history), not to substitute +0.86 or +0.42. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Name the figure that was actually retracted (+0.86? +0.42?) or cite the appendix entry that records it.

*Also flagged by: SL4.*

### XC9. [cross-cutting] §2.4 footnote 8

> The deployed screen is opus screen full.js (473 batches of 40)

**Problem.** 473 × 40 = 18,920, about half the '37,801 segments' the deployed screen is twice said to cover; 473 batches of ~80 would match (37,801/473 ≈ 79.9).

**Reviewer's check.** Multiplied the stated batch count and size and compared with the stated segment total.

**Refuter's verification.** 473 × 40 = 18,920, about half the 37,801 segments the deployed screen is twice said to cover. Counting the actual on-disk run: screen_batches/ holds 946 batch files, 40 segments each (last one 3), totaling 37,803 — so the truth is 946 batches of 40, not 473 of ~80 (the reviewer's suggested resolution guessed the wrong factor, but their arithmetic defect is real; the stale '~473 batch files x 40 segments' comment survives in opus_screen_full.js's own header). [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Correct the batch size (or count) so the product matches 37,801.

### XC10. [cross-cutting] §2.14 stage 5 vs Table 25

> every rewrite that reached a Human verdict (39 variants across 15 targets, one target's original text unavailable and dropped) was graded blind

**Problem.** Table 25 reports variant n = 35, and §3.2 relies on 35 ('flagged 13 of 35 genuine human floor speeches and only 5 of 35 machine rewrites'). If dropping the one target also dropped its variants, then it is not true that 39 variants across 15 targets were graded; the 39→35 accounting is never given.

**Reviewer's check.** Reconciled 38 final-run Human verdicts + 1 blind-run verdict = 39, 16 targets − 1 = 15, against the table's n = 35.

**Refuter's verification.** PREREG-stage5-successful-evasion.md gives the exact accounting the paper omits: '39 Human-verdict variants across 16 targets... 35 pairs / 15 targets are gradeable; one target (seg_id 2025-12-04#t1466w0, 4 variants) is dropped', and stage5_evasion_pairs.json contains 35 pairs. So the paper's parenthetical is doubly wrong: 39 variants go with 16 targets (not 15), and only 35 — not 'every' one of the 39 — were graded, matching Table 25's n=35 and §3.2's 13-of-35/5-of-35. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** State the accounting: e.g. '39 reversals; the 4 belonging to the dropped target leave 35 graded variants across 15 targets.'

*Also flagged by: CB11, IC10, QB6.*

### XC11. [cross-cutting] §2.9.8 vs §2.9.5 (chase-and-flight thresholds)

> What argues against an artifact is that the sign is negative at all six thresholds, including the widest and least significant.

**Problem.** §2.9.5 reports four volume thresholds (100+, 300+, 800+, 1,500+), not six; no other two thresholds are stated anywhere, so the robustness claim rests on cells the paper does not show.

**Reviewer's check.** Counted the thresholds listed in §2.9.5 and searched for additional threshold values.

**Refuter's verification.** §2.9.5 reports exactly four volume thresholds (ρ = −0.13 at 100+, −0.22 at 300+, −0.42 at 800+, −0.46 at 1,500+); no other thresholds appear anywhere in the render or the draft, and no committed script computes the flight correlations at all (build_class_word_year.py only builds the counts), so the two extra cells 'all six' relies on are shown nowhere the reader — or a re-runner — can check. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Either list all six thresholds with their correlations in §2.9.5, or say 'all four reported thresholds.'

### XC12. [cross-cutting] §2.2 (word-weighting / ratio estimator)

> its finite-sample bias is nil in practice (bootstrap mean 10.30% against a plug-in 10.31%, a −0.005-point gap)

**Problem.** The bias check is quoted at 10.30/10.31%, but the estimator it is defending is reported at 9.03% (and the equal-weight mean at 9.12%); 10.3% matches no figure in the paper — it appears to be the pre-Mixed-correction (or otherwise different) quantity, undermining the claim that this checks the reported estimator.

**Reviewer's check.** Compared the quoted bootstrap/plug-in values against every pooled prevalence figure reported (9.03, 9.12, 12.03, 8.50).

**Refuter's verification.** The quoted 10.30/10.31% matches no reported estimate: the headline ratio estimator is 9.03%, equal-weight mean 9.12%, Mixed-as-whole 12.03%, CA-FED-dropped 8.50%. Rerunning banded_prevalence.py identifies the likely estimand: the long-band-only word-weighted rate is 10.29% — the superseded pre-band-combination quantity — so the bias check was evidently run on a different estimand than the split-corrected 9.03% it is quoted to defend. No committed script computes the bootstrap-vs-plug-in comparison (the figures entered in commit f858dae with no artifact), so the check cannot be re-tied to the reported estimator as it stands. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Re-run (or re-quote) the bootstrap-vs-plug-in check on the split-corrected 9.03% estimator, or label which estimand the 10.3% check belongs to.

*Also flagged by: CB8, CP9, SL6.*

### GS5. [genre+screen] 4.3 (genre table)

> | **SO31** — one-minute scripted set-pieces | **32.3%** | [21.0, 44.1] |

**Problem.** The bootstrap CIs in this table are not reproducible: wboot() is seeded with abs(hash(genre+stratum)) % 9999, and Python string hashing is randomized per process, so every run prints different intervals. Two runs gave SO31 [21.4, 43.9] and [21.2, 44.0] against the quoted [21.0, 44.1]; DEBATE and OQ drift similarly (the per-chamber CIs from the same script share the defect). Differences are small, but no run can regenerate the published intervals.

**Reviewer's check.** Ran prevalence_report.py twice and compared the printed genre CIs to each other and to the writeup; read the seeding code (abs(hash(g+s)) % 9999, same pattern for chambers).

**Refuter's verification.** Reproduced: wboot() is seeded with abs(hash(genre+stratum)) % 9999 (and abs(hash(chamber)) % 9999 for the per-chamber table), and Python string hashing is salted per process. I ran prevalence_report.py twice: SO31 printed [21.3, 43.8] then [21.2, 43.9] against the published [21.0, 44.1]; DEBATE and OQ drifted the same way ([10.4,30.4]/[10.5,30.4]; [1.9,19.1]/[2.3,19.3]). The point rates, word totals and CA trend are stable, and the drift is ~0.1–0.4pp — immaterial — but no run can regenerate the published intervals, exactly as stated. build_pangram_expansion.py's stable-digest seeding shows the fix pattern already exists in the repo.

**Suggested fix.** Seed from a stable digest (e.g. int(hashlib.sha1(...).hexdigest()[:8],16), as build_pangram_expansion.py already does) or set PYTHONHASHSEED, rerun, and re-quote.

### GS6. [genre+screen] 4.4 (footnote r44dep)

> The deployed screen is `opus_screen_full.js` (473 batches of 40), distinct from the lean validation run used in the effort A/B below; the two differ in score level (mean 34.3 vs 26.5) but not in discrimination.

**Problem.** Two factual errors. (1) The means are swapped: on the shared 241-segment pool the lean run averages 34.3 and the deployed screen 26.5, while the sentence order (deployed first) implies the opposite; opus_screen_auc.py's docstring makes the same swap. (2) '473 batches of 40' is one half-run: 473×40 = 18,920 ≠ 37,801; screen_batches/ holds 946 batch files (37,803 slots) and the js itself says 'one half per run'. ('Not in discrimination' does hold: deployed AUC on the 241 pool is 0.954 vs lean 0.948.)

**Reviewer's check.** Joined opus_lean_scores.csv and opus_screen_scores.csv through the blind_id→sid map and computed both means on the 241 overlap (34.3 lean, 26.5 deployed); counted screen_batches/ files and their contents; read opus_screen_full.js header.

**Refuter's verification.** Both errors reproduce. (1) Joining opus_lean_scores.csv (blind_id→sid) to opus_screen_scores.csv on the 241-segment overlap: lean mean 34.32, deployed mean 26.52 — the footnote's order (deployed named first, then '34.3 vs 26.5') implies deployed = 34.3, i.e. swapped; opus_screen_auc.py's docstring makes the identical swap ('mean 26.5 lean vs 34.3 deployed'). (2) screen_batches/ holds 946 batch files totalling 37,803 slots against 37,801 scored rows; the js meta says '~473 batch files x 40 segments' with 'one half per run' (default args 0–473), so '473 batches of 40' (= 18,920) describes one half-run, not the deployed screen. The parity claim does hold: on the 241 pool I get deployed AUC 0.954 vs lean 0.948.

**Suggested fix.** Write '(mean 26.5 deployed vs 34.3 lean)' and '946 batch files of 40, run as two halves'.

### GS7. [genre+screen] 4.4 The Opus screen tracks Pangram

> The deployed screen — the run over all 37,801 segments — separates Pangram's AI and human classes at **AUC 0.954** [0.934, 0.971] on the 618-segment overlap

**Problem.** The positive class in that AUC is AI plus Mixed (104 = 78 + 26), not 'Pangram's AI class': opus_screen_auc.py labels 1 if verdict in (AI, Mixed). Since the table directly above lists Mixed as a separate class, 'AI and human classes' misdescribes the computation. The choice is conservative — AI-only vs Human gives 0.966 — but the reader cannot tell what was computed. The 2023+ figure (0.940) inherits the same labelling.

**Reviewer's check.** Read load_p4() in opus_screen_auc.py; recomputed both variants from opus_screen_scores.csv + pangram_p4_verdicts.csv (AI+Mixed 0.954, AI-only 0.966; n = 618 = 78+26+514 only if Mixed is included).

**Refuter's verification.** Verified in opus_screen_auc.py's load_p4(): label = 1 if verdict in ('AI','Mixed'), so the positive class is 104 = 78 AI + 26 Mixed, and n = 618 = 78+26+514 only with Mixed included. Recomputed both variants: AI+Mixed vs Human = 0.9538 (matches the published 0.954), AI-only vs Human = 0.9655 on n = 592. The table directly above the sentence lists Mixed as a separate class with its own mean (44.8), so 'AI and human classes' misdescribes the computation; the choice is conservative (AI-only is higher) and the script's printout says '104 AI / 514 human', but the prose as written does not let the reader know Mixed is folded into the positives. The 2023+ figure (0.940) uses the same labelling.

**Suggested fix.** Say 'separates Pangram's flagged (AI + Mixed) segments from its human class', or report the AI-only 0.966 alongside.

### GS9. [genre+screen] 4.4 The Opus screen tracks Pangram

> Practically, the screen can be run for about **4× fewer reasoning tokens (~2× all-in)** with no loss. (`opus_effort_ab.py`, `opus_effort_ab.csv`)

**Problem.** The 4×/2× token-cost figures are attributed to two artifacts that contain no token accounting: opus_effort_ab.csv holds only blind_id/label/three scores, opus_effort_ab.py computes AUCs and correlations only, and opus_effort_raw.json holds only per-arm score maps. The AUC parity is fully supported; the specific cost multipliers are supported by nothing on disk.

**Reviewer's check.** Read opus_effort_ab.py end to end, inspected opus_effort_ab.csv columns and opus_effort_raw.json structure, grepped the s10 tree for token counts tied to the effort A/B — none found.

**Refuter's verification.** Verified by reading all three cited/adjacent artifacts end to end: opus_effort_ab.csv holds only blind_id/label/archived_low/fresh_low/max scores; opus_effort_ab.py computes AUCs, a paired bootstrap of max−mean(low), and correlations, with no token fields anywhere (its harvest() extracts only effort tags and ai_guess scores from transcripts); opus_effort_raw.json is two {blind_id: score} maps. A grep of the s10 tree for token accounting tied to the effort A/B finds nothing — the only token mentions are unrelated (generation caps, projections). The AUC-parity half of the sentence is fully supported; the specific 4×/2× cost multipliers are supported by nothing on disk and are attributed to artifacts that cannot substantiate them.

**Suggested fix.** Record the per-arm token usage from the workflow transcripts into the CSV (or a small JSON) and cite that, or hedge the multipliers as an uncommitted observation from the run logs.

### IC8. [internal-consistency] §2.1 New Brunswick rescore, Table 1

> The model-tier defect was an undercount, not a false-positive problem — disagreements run net upward (33 segments moved out of Human, 9 the other way).

**Problem.** '9 the other way' misstates the data and breaks the arithmetic of the table beside it: 122 + 33 − 9 = 146, but Table 1 shows AI+Mixed going 122 → 144. The committed CSV shows 11 segments moved into Human (9 AI→Human plus 2 Mixed→Human), which reconciles exactly (122 + 33 − 11 = 144).

**Reviewer's check.** Recomputed the transition matrix from nb_p3_vs_p4.csv: Human→{Mixed 19, AI 14}, AI→Human 9, Mixed→Human 2, AI↔Mixed 11; agreement 91.6% ≈ '92%'.

**Refuter's verification.** Quote at lines 138-139. Recomputed the transition matrix from the committed nb_p3_vs_p4.csv (658 rows): Human→Mixed 19 + Human→AI 14 = 33 out of Human; into Human is AI→Human 9 + Mixed→Human 2 = 11. Table 1's AI+Mixed 122→144 reconciles only with 11 (122+33−11=144; the printed 9 gives 146). Exact agreement (99+503+1)/658 = 91.6% ≈ the table's 92%. The correct sentence is '11 the other way (9 from AI, 2 from Mixed)'.

**Suggested fix.** Change '9 the other way' to '11 the other way (9 from AI, 2 from Mixed)'.

### IC9. [internal-consistency] §2.6 (Table 8 discussion)

> Federal Canada is the one case it does explain, at 21.7% the most machine-written chamber in the study, dropping from apparently-above to clearly-below once corrected.

**Problem.** 'Most machine-written chamber in the study' is contradicted by Table 2 two pages earlier, where NSW (19.8% of words) exceeds CA-FED (18.5%); converting NSW to instrument occurrences by the same ~1.17-1.22× ratio puts it near 23%, above 21.7%. The 21.7% is only the highest among the aggregated units of this §2.6 comparison, where NSW is submerged in the 11.3% 'AUS states' pool.

**Reviewer's check.** Compared Table 2's chamber rates with convergence_check.py output (CA federal 21.7% by occurrences, AUS states pooled 11.3%) and applied footnote 14's words→occurrences conversion to NSW.

**Refuter's verification.** Quote at lines 555-556. The study's own committed ai_share_by_chamber.json puts NSW at 19.81% of words and 23.15% of instrument occurrences against CA-FED's 18.48% / 21.65% — NSW exceeds federal Canada on both metrics, so CA-FED is not the most machine-written chamber in the study on either unit. Table 2 two pages earlier prints NSW 19.8% above CA-FED 18.5%. The 21.7% superlative holds only among the aggregated units of the §2.6 comparison, where NSW is submerged in the 11.3% 'AUS states' pool. The proposed scoping fix is exactly right.

**Suggested fix.** Scope the superlative: 'the most machine-written of the chamber groups compared here' or 'the most machine-written national chamber'.

*Also flagged by: ST3.*

### IC10. [internal-consistency] §2.14 Stage 5

> every rewrite that reached a Human verdict (39 variants across 15 targets, one target's original text unavailable and dropped) was graded blind against its original

**Problem.** The counts do not reconcile with the tables around them: Table 22 reports 16 targets with ≥1 Human; '39 variants across 15 targets' with one target then dropped is self-inconsistent with Table 25's variant n = 35 and target n = 15 (39 across 16, minus one 4-variant target, gives 35/15). And 39 exceeds the '38 of 341' Human variants of the two final runs, silently including the superseded run's single Human without saying so.

**Reviewer's check.** Cross-checked 38 = 29 (NB v3) + 9 (GO) from §2.14, the 16-target row of Table 22, Table 25's n's, and Appendix B12's 1 Human in the superseded runs.

**Refuter's verification.** Quote at lines 1663-1664. The study's own registration file PREREG-stage5-successful-evasion.md states '39 Human-verdict variants across 16 targets (NB v2, NB v3, GO all-31)' and '35 pairs / 15 targets are gradeable; one target... unavailable' — so the paper's '39 variants across 15 targets' is wrong on the target count (39 spans 16 targets; dropping the one 4-variant target gives Table 25's n=35/15), and it is self-inconsistent (15 minus one dropped would leave 14). The 39 also silently includes the superseded NB v2 run's single Human on top of the '38 of 341' from the two final runs (line 1494-1496: 38 final + 1 superseded), without saying so. Table 22's pooled ≥1-Human row is 16 targets, matching the prereg, not the sentence.

**Suggested fix.** State '39 variants across 16 targets (38 from the final runs plus the superseded runs' one); one target's original was unavailable, leaving 35 variants over 15 targets'.

*Also flagged by: CB11, QB6, XC10.*

### IC11. [internal-consistency] §2.14 Bypass (flip-bar aside) vs Appendix C.3

> And at the target level, if merely ”soften off AI” is the goal, 17 of 38 New Brunswick targets (45%) cleared it.

**Problem.** The denominator 38 is the retired one: C.3 states 'An earlier version listed 38, 25 and 27 — the counts that produced at least one variant clearing the submission gate — which understated the attack surface', and Table 22 puts NB v3 at 40 targets searched. By the paper's own denominator rule (targets searched, argued explicitly in §2.14) this should be 17/40 = 42.5%.

**Reviewer's check.** Compared the sentence with Table 22's NB row (40 searched) and C.3's correction of the 38/25/27 counts.

**Refuter's verification.** Quote at lines 1608-1609. Table 22 and Table 31 put NB v3 at 40 targets searched; Appendix C.3 (lines 2919-2920) explicitly retires the 38/25/27 counts as 'the counts that produced at least one variant clearing the submission gate — which understated the attack surface'. §2.14 itself argues the denominator rule at length ('The denominator is targets searched, not targets that yielded a variant... Counting only targets that yielded makes the rate conditional on the attack having already half-succeeded'). By the paper's own rule the flip-goal rate is 17/40 = 42.5%; no justification is given for conditioning this one rate on the submission gate.

**Suggested fix.** Report 17 of 40 (42.5%), or justify why the flip-goal rate alone may condition on the submission gate.

*Also flagged by: CB9, QB5, XC6.*

### IC12. [internal-consistency] §2.9.2 Table 13

> gives 897 members and 5,294 member-years, 57.5% of the words that reach a named non-chair speaker in the eight Canadian provinces.

**Problem.** Table 13's members column sums to 944 (29+435+180+186+45+53+16), not the 897 stated in the sentence introducing it, and no reconciliation (dual-coded members, exclusions) is given.

**Reviewer's check.** Summed the printed member counts in Table 13 and compared with the stated total.

**Refuter's verification.** Quote at lines 858-860. Table 13's members column (29+435+180+186+45+53+16) sums to 944, not 897 — verified by direct addition. Searched the full render: '944' appears nowhere and '897' appears exactly once, so no reconciliation (dual-coded members, regression exclusions, pooled variants) is offered anywhere in the paper. A 47-member discrepancy between a stated total and the column beside it, unexplained, is an internal-consistency defect regardless of which figure is right.

**Suggested fix.** Reconcile the counts — state the 897 basis (e.g. members entering the regression) and why the per-class column sums higher, or correct whichever figure is wrong.

*Also flagged by: XC5.*

### IC13. [internal-consistency] §2.9.7 Word mix

> Sonnet 5, Opus 5 and Fable 5 traces are negative against every human class and education centroid and are the only text sets positively similar to the machine-flagged legislature pool.

**Problem.** Two sentences later the passage says 'all six Claude models are positive against the flagged pool (+0.016 to +0.186)' — so three models being 'the only text sets positively similar' to that pool is contradicted in the same paragraph once the older Claude versions are added, and the 'only' claim is left unscoped.

**Reviewer's check.** Read the two adjacent sentences; the extension paragraph explicitly adds Sonnet 4.5, Opus 4.1 and Opus 4 as positive against the same pool.

**Refuter's verification.** Quote at lines 996-998. Two sentences later the same paragraph states 'all six Claude models are positive against the flagged pool (+0.016 to +0.186)' after extending the comparison to Sonnet 4.5, Opus 4.1 and Opus 4. The 'only' claim was true within the original five-family base/instruct comparison (VECTOR-ANALYSIS.md line 130 records it in that scope, written before the extension), but the paper carried it unmodified into a paragraph whose own extension falsifies the unscoped superlative. Minor wording defect, exactly as described; the fix is to scope 'only' to the five-family comparison.

**Suggested fix.** Scope the first claim to the five-family base/instruct comparison ('the only sets among the five-family comparison...') or drop 'only'.

### OP7. [occupational-prereg] Results 4.6b (reproducibility claim)

> right-signed and nominally significant in 16 of 16 covariate specifications

**Problem.** No committed script produces this number: prereg_stage2.py's lattices contain the components and the ladder levels but not the apex delta, and prereg_covariate_strength.py prints only grand models. This contradicts the section's opening claim that 'every number below reproduces from a committed script'. The number itself is correct — independent recomputation of apex_delta × all 16 covariate masks on the n=3,594 panel gives 16/16 right-signed, 16/16 |t|>1.96 (t 3.2–4.6).

**Reviewer's check.** Grepped all prereg_*.py for an apex-delta lattice (none); recomputed the 16-spec lattice with the stage-2 estimator (HC1, same panel construction).

**Refuter's verification.** Verified both halves. No committed script produces an apex-delta covariate lattice: prereg_stage2.py's Lattice B contains only the eight ladder levels, prereg_stage1.py fits the delta in just two specs (alone, +bd), and prereg_covariate_strength.py / prereg_strength_2526.py print only grand models — contradicting the section's opening 'every number below reproduces from a committed script'. I independently recomputed the 16-mask lattice with the stage-2 estimator (HC1, same panel filter, n=3,594): 16/16 right-signed, 16/16 |t|>1.96, t range 3.23–4.63 — matching the reviewer's recomputation exactly. The number is correct; its committed source is missing.

**Suggested fix.** Add the apex-delta lattice to prereg_stage2.py (or prereg_covariate_strength.py) so the 16/16 claim has a committed source.

### OP10. [occupational-prereg] Results 4.6b (four-level table)

> the study's registered structure — **four levels, built two semi-independent ways**: the *directional ladder*

**Problem.** The directional ladder's 'middle' is algebraically the corporate profile ((+U−L+D+N)/4) — the exact instrument whose registered ordering failed — so the table's directional-column peak (+0.029, t 2.0) is the failed primary's losing slope relabeled 'middle'. The text never notes this identity, which matters for how much independent confirmation the 'two ways agree at the peak' claim carries (only the coded ladder is independent).

**Reviewer's check.** Prereg post-Stage-1 amendment gives the directional weights (middle +U−L+D+N, /4); prof_corporate and the directional middle slope are identical (+0.029, t +2.0) in stage-1/synthesis outputs.

**Refuter's verification.** The identity is exact and re-verified: the amendment defines the directional middle as (+U−L+D+N)/4, which is the corporate profile's weighting (signed mean of the standardised components under +,−,+,+), and the slopes are identical (+0.029, t +2.0) in stage-1 (prof_corporate) and the synthesis check (directional middle). The writeup never states this identity — the reader is told the ladders are 'built by different processes... agreeing at the peak to the third decimal' when the directional column's peak is the retired primary's losing profile rescored, so the independent leg of the two-way agreement is the coded ladder alone. The hedges present ('semi-independent', 'composed from the components') flag partial dependence but do not disclose that the directional middle is algebraically the corporate profile; a minor but real omission, as the reviewer rated it.

**Suggested fix.** State that the directional middle is the corporate profile rescored, so the two-way agreement rests on the coded ladder's independence.

### PT5. [posttraining+coverage+permeation] 4.7 (bias-correction parenthetical)

> null calibration on random word lists returns +0.45/+0.56/+0.31, largest at DPO only because DPO's generations are longest

**Problem.** The stated mechanism is false: DPO's generations (83,627 words over the 800 prompts) are not the longest — instruct's are (85,165), with base at 82,160. What is actually extreme about the SFT→DPO transition is that its denominator stage, SFT, is by far the shortest corpus (63,261 words), giving that transition the largest volume ratio. The pedestal ordering itself verifies (+0.44/+0.59/+0.32), the explanation attached to it does not.

**Reviewer's check.** Counted words per stage in olmo_ladder/*_gen.json with the script's own tokenizer regex; reproduced the pedestals with 30 null lists per transition.

**Refuter's verification.** Counted words per stage in olmo_ladder/*_gen.json with the script's own tokenizer regex: base 82,160, SFT 63,261, DPO 83,627, instruct 85,165. DPO's generations are not the longest — instruct's are — so the stated mechanism is factually false under any reading (if pedestal size tracked the target-side length, the RLVR transition would be largest, contradicting +0.31 being smallest). What is extreme about SFT→DPO is that SFT, the denominator side, is by far the shortest corpus (63k vs 83-85k). My null runs also reproduce SFT→DPO as the largest pedestal. The erroneous clause was copied verbatim from REVIEW-2026-08-11.md M9 line 432.

**Suggested fix.** Change the clause to attribute the largest pedestal to SFT (the transition's base side) being the shortest corpus, e.g. 'largest at SFT→DPO because SFT's generations are much the shortest'.

### PT6. [posttraining+coverage+permeation] 4.7 footnote r47 and 4.7a opening

> a control absent from base output impossible while 27% of the style words are exactly that

**Problem.** Both this 27% and §4.7a's 'only about half appear in the generated corpus' are numbers from the superseded 800-prompt/180-token run, presented as facts about the scaled run the footnote describes. On the current 3-family 1,600-prompt corpus, 61 of 310 present style words (19.7%) are absent from base output — rlhf_pref_analyze.py itself now prints '66 of 313 (21%)' — and 249/407 (61%) of the list appears in the generated base corpus (76% of the list is present in the analysis). The old rlhf_gen_180 data gives 57/212 = 26.9% and 212/407 = 52%, which is where '27%' and 'about half' come from.

**Reviewer's check.** Recomputed the absent-from-base fraction on rlhf_gen at 1600x3, 800x4, and per-family (19.7–24.4%, never 27%); recomputed on rlhf_gen_180 (26.9%); ran rlhf_pref_analyze.py (prints 21%); compared coverage counts from style_word_frequency.py output.

**Refuter's verification.** Both numbers are from the superseded 800-prompt/180-token configuration, presented as facts about the scaled run. On the scaled headline corpus (3 families, 1,600 prompts) rlhf_pref_final.json records 61 of 310 present style words (19.7%) with zero base count, and rlhf_pref_analyze.py prints '66 of 313 style words (21%) are ABSENT from base output' on its own 2-family configuration; presence is 310/407 = 76% in the analysis and 249/407 = 61% in the generated base corpus (style_word_frequency: 407−158), so '27%' and 'only about half appear' are wrong for the run being described. The old values 57/212 = 26.9% and 212/407 = 52% appear verbatim in the rlhf_pref_analyze.py docstring and METHODOLOGY.md's corrected-2026-08-12 passage — the stale source of both figures.

**Suggested fix.** Update to the scaled-run values: ~20% absent from base output, and 'about 60%' (or 'three-fifths') appearing in the generated corpus.

### PT8. [posttraining+coverage+permeation] 4.8 (headline and footnote r48)

> +0.0099, positive in 9 of 10 cells, permutation p = 0.017.

**Problem.** The point estimate and sign count reproduce exactly, but the headline p-value does not come from the documented invocation: `python word_context_delta.py pooled` at its recorded defaults (B=2,000, seed 6, 3,000 permutation draws) prints one-sided p = 0.0217 and P(<=0) = 0.020. The footnote honestly gives the cross-seed range (0.015–0.022), but the bolded headline picks a value the stated defaults do not produce. Additionally the footnote's pointer 'Per-model cell table at METHODOLOGY.md:1009' is stale — the two-family cell material now sits near METHODOLOGY.md:1142.

**Reviewer's check.** Ran word_context_delta.py pooled (reproducing +0.0099, 9/10 cells, per-family +0.0118/+0.0081, CI [+0.0009,+0.0195]); read the pooled() code to confirm defaults; grepped METHODOLOGY.md for the cell table location.

**Refuter's verification.** Re-ran `python3 word_context_delta.py pooled` at the recorded defaults (B=2,000, seed 6, 3,000 permutation draws): it reproduces +0.0099, 9/10 cells, per-family +0.0118/+0.0081, CI [+0.0009, +0.0195] — but prints one-sided p = 0.0217 and P(≤0) = 0.020, not 0.017. The bolded headline (and METHODOLOGY.md's bold summary line) quotes a value the stated default invocation does not produce; the footnote's honest cross-seed range (0.015–0.022) contains it but does not make the specific headline value reachable from the documented command. Also verified the stale pointer: METHODOLOGY.md:1009 is band-screen prose; the chamber×family cell table now sits at METHODOLOGY.md:1139-1148.

**Suggested fix.** Quote the default-seed value (p = 0.022) or the range ('p = 0.015–0.022 across seeds') in the headline, and repair the METHODOLOGY.md line pointer.

### PT9. [posttraining+coverage+permeation] 4.7 (opening of the pooled-effect paragraph)

> Pooled alignment effect **+0.387** on the scaled generation — three model families, 1,600 prompt pairs each, 1.19M base words.

**Problem.** The +0.387 is the well-measured estimate (82 words at >=20 base occurrences), not the pooled one — the section itself defines 'pooled' as the over-every-present-word figure (+0.63) two paragraphs later and instructs 'Quote the well-measured figure, not the pooled one'; Appendix C's table correctly labels +0.387 'well-measured'. Labelling it 'Pooled alignment effect' in the bolded lead invites exactly the misquotation the section warns against.

**Reviewer's check.** Compared against rlhf_pref_compile.py output columns (pooled +0.62 vs well-measured +0.39 at n=1600) and the section's own later definitions.

**Refuter's verification.** Verified against rlhf_pref_compile.py output: at n=1,600 the over-every-present-word 'pooled' column reads ~+0.62 and the well-measured column (82 words at >=20 base occurrences) reads ~+0.39 — the bolded +0.387 is the well-measured figure. The section's own next paragraph defines 'pooled' as the +0.6311 all-words estimator and bolds 'Quote the well-measured figure, not the pooled one', and Appendix C (draft line 3406) correctly labels +0.387 'well-measured'. The defense that 'pooled' here means pooled-across-families is available from the sentence's continuation, but the section has already reserved the word for the estimator it disowns, so the label contradicts its own terminology and invites the exact misquotation it warns against. Minor labeling defect; the number itself is right (to within the ±0.01 draw noise of the nondeterminism finding). [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Rename to 'Alignment effect +0.387 (well-measured)' or 'pooled across three families, restricted to well-measured words'.

*Also flagged by: XC7.*

### QB4. [quality+bypass] 4.9 Bypass study (cross-chamber consistency paragraph)

> The two chambers give 25.0% (n = 40) and 19.4% (n = 31) ... the 4.1-point gap carries a 95% interval of roughly [−17, +25] points

**Problem.** 25.0 − 19.4 = 5.6 points, not 4.1. The 4.1 figure matches the yield-conditioned per-text rates the report prints elsewhere (NB seed-AI 26.3% vs GO 22.2%, denominators 38 and 27) — exactly the conditional denominators the section's own accounting rule rejects. The CI is therefore attached to a gap computed on a different estimand than the two rates quoted beside it.

**Reviewer's check.** Arithmetic on the section's own numbers; matched 4.1 to bypass_report.py's per-text conditional block (26.3 − 22.2 = 4.1); approximate Newcombe interval for 10/40 vs 6/31 is about [−14, +25].

**Refuter's verification.** 25.0 − 19.4 = 5.6 points; the sentence calls it a 4.1-point gap. I traced the 4.1 to the yield-conditioned per-text block bypass_report.py prints (NB v3 seed-AI 10/38 = 26.3% vs GO pooled 6/27 = 22.2%; 26.3−22.2 = 4.1) — the conditional denominators the section's own accounting rule explicitly rejects ('gave 24.6% where the answer is 22.5%'). Newcombe intervals confirm the provenance: 10/38 vs 6/27 gives [−17.6, +23.6] ≈ the quoted [−17, +25], while the searched-denominator pair 10/40 vs 6/31 gives [−14.4, +23.9]. So the gap and CI are internally consistent with each other but attached to a different estimand than the two rates quoted beside them.

**Suggested fix.** Quote the 5.6-point gap with an interval computed on the searched-target denominators (roughly [−14, +25]), or say explicitly which pair of rates the 4.1 refers to.

### QB5. [quality+bypass] 4.9 Bypass study (flip vs success paragraph)

> And at the target level, if merely "soften off AI" is the goal, 17 of 38 New Brunswick targets (**45%**) cleared it.

**Problem.** The denominator 38 counts only targets that produced a submitted variant. The same subsection's own rule — 'The denominator is targets searched, not targets that yielded... Counting only targets that yielded makes the rate conditional on the attack having already half-succeeded' — requires 40, giving 42.5%. The success rates in the adjacent table correctly use 40; this flip rate silently switches denominators.

**Reviewer's check.** Recomputed from bypass_v3_pangram.json: 17 of 38 submitting targets (44.7%) had >=1 Mixed-or-Human variant; NB v3 searched 40 targets (bypass_v3.json state; 2 zero-yield), so the searched-denominator rate is 17/40 = 42.5%.

**Refuter's verification.** Recomputed from bypass_v3_pangram.json: exactly 38 submitting targets, 17 with at least one Mixed-or-Human variant (44.7%). bypass_report.py confirms NB v3 searched 40 targets with 2 zero-yield. The same subsection's rule — 'The denominator is targets searched, not targets that yielded... Counting only targets that yielded makes the rate conditional on the attack having already half-succeeded' — requires 17/40 = 42.5%. Table 22's success rates correctly use 40; this flip rate silently switches to the conditional denominator. Mitigation considered: the fraction 17/38 is printed explicitly, so an attentive reader can see the denominator — but the sentence calls them '38 New Brunswick targets' when 40 were searched, directly against the declared rule.

**Suggested fix.** Report 17/40 = 42.5% (targets searched), or flag the conditional denominator explicitly.

*Also flagged by: CB9, IC11, XC6.*

### QB6. [quality+bypass] 4.9 Stage 5 (successful evasions)

> every rewrite that reached a Human verdict (39 variants across 15 targets, one target's original text unavailable and dropped) was graded blind against its original

**Problem.** The counts are mismatched: per the frozen prereg (PREREG-stage5-successful-evasion.md) it is 39 Human-verdict variants across 16 targets, of which 35 pairs / 15 targets were gradeable after dropping the one target (4 variants) whose original is absent. '39 variants across 15 targets' is wrong on either reading; the graded set is 35/15, as the table's n confirms.

**Reviewer's check.** Read the prereg's Sample section and confirmed the key file holds exactly 35 variant items across 15 distinct seg_ids; 38 final-run Humans + 1 superseded NB v2 Human = 39 across 16 targets before the drop.

**Refuter's verification.** Verified against the frozen prereg and artifacts: stage5_humans.json holds 39 Human-verdict variants across 16 distinct targets (the dropped target 2025-12-04#t1466w0 contributes 4); stage5_grade_key.json holds exactly 35 graded variant items across 15 seg_ids, matching the table's n=35/n=15 and PREREG-stage5-successful-evasion.md's Sample section ('39 Human-verdict variants across 16 targets... 35 pairs / 15 targets are gradeable'). '39 variants across 15 targets' is wrong on either reading: 39 goes with 16 targets (pre-drop), 15 targets goes with 35 graded pairs.

**Suggested fix.** Rewrite as '39 variants across 16 targets; one target (4 variants) dropped for a missing original, leaving 35 pairs across 15 targets'.

*Also flagged by: CB11, IC10, XC10.*

### QB7. [quality+bypass] 4.9 Stage 6 (respect_groups paragraph)

> frontier arms tie the human 1.31 (fable +0.12, opus −0.12, n.s.) while every open-weight arm sits below

**Problem.** The frontier-vs-open-weight dichotomy omits claude-opus-4.1, a frontier arm at −0.24 (t −2.3) — a nominally significant deficit, larger than mistral-instruct's −0.24 (t −4.3) in magnitude and below every open-weight point estimate's neighborhood (opus-4.1 mean 1.04 vs mistral-instruct 1.07). The two arms quoted are the two that fit the 'tie' framing; the conclusion drawn (no machine arm beats human on this dimension) actually survives, but the 'frontier arms tie' half of the sentence is contradicted by one of its own frontier arms.

**Reviewer's check.** Ran quality_expansion/analyze_stage6.py: respect_groups paired diffs are fable5 +0.12 (t +1.2), opus5 −0.12 (t −1.1), opus41 −0.24 (t −2.3), opus4 +0.11 (t +0.9); human mean 1.31, opus41 mean 1.04.

**Refuter's verification.** Reproduced by running quality_expansion/analyze_stage6.py: respect_groups paired diffs are fable5 +0.12 (t +1.2), opus5 −0.12 (t −1.1), opus41 −0.24 (t −2.3), opus4 +0.11 (t +0.9); arm means human 1.31, opus41 1.04 vs mistral_instruct 1.07. claude-opus-4.1 is a frontier arm by the paper's own usage — the same paragraph says 'opus-class arms carry as much to engage with as the humans' and Table 26 leads with opus-4.1 among the arms that 'invert that at the frontier' — yet it shows a nominally significant deficit larger in point terms than any open-weight arm and a mean below mistral-instruct's. The two arms quoted are the two that fit the 'tie' framing. The paragraph's actual conclusion ('no raw-machine counterpart at any tier') survives, as the reviewer concedes, but the 'frontier arms tie' half is contradicted by the section's own data.

**Suggested fix.** Name opus-4.1's −0.24 (t −2.3) alongside the two quoted arms, e.g. 'frontier arms sit at or below the human 1.31 (fable +0.12 to opus-4.1 −0.24)'.

### ST5. [series+trend+cross-chamber] 4.5a footnote r45f

> Machine-written text carries the instrument at 4,231 occurrences per 100k words against human text's 3,470, a ratio of 1.22×, so a chamber that is 9.0% machine by words is 10.6% machine by occurrences.

**Problem.** The example is doubly wrong: per the artifact, Ireland (the 9.0% chamber in the main text) is 7.5% machine by words → 9.0% by occurrences, and a genuinely 9.0%-by-words chamber at the stated 1.22× ratio would be ≈10.8% by occurrences, not 10.6%. The footnote reuses Ireland's occurrence share as if it were a word share.

**Reviewer's check.** Read ai_share_by_chamber.json (IE share_words 0.0751, share_occurrences 0.0900, ratio 1.219) and recomputed s·r/(1−s+s·r) for s=0.09.

**Refuter's verification.** ai_share_by_chamber.json: ratio 1.219; Ireland — the main text's 9.0% chamber — is 7.5% by words (0.0751) and 9.0% by occurrences (0.0900), so the footnote treats an occurrence share as a word share. And the arithmetic is independently wrong: s·r/(1−s+s·r) at s=0.09, r=1.219 gives 10.76% ≈ 10.8%, not 10.6% (equivalently 0.09·4231/(0.09·4231+0.91·3470)=10.8%). The correct worked example is 7.5% by words → 9.0% by occurrences.

**Suggested fix.** Rewrite: 'Ireland, 7.5% machine by words, is 9.0% machine by occurrences.'

### ST7. [series+trend+cross-chamber] 4.5a (constant-window paragraph)

> The four lowest 2006 starters — UK Commons, Scotland, Northern Ireland, Wales — are the four fastest climbers

**Problem.** Literally false in the underlying data: New South Wales's 2006 gap (1,275.6) is below Wales's (1,276.4), so the four lowest starters are Scotland, UK, NI, NSW. The two are a rounding-level tie (both print as 1,276), but the sentence as written does not hold.

**Reviewer's check.** Read unrounded 2006 gaps from occurrence_trends.json (WALES 1276.44, AUS_NSW 1275.59); reproduced the table and Spearman −0.56 (n=19) via constant_window_trend.py.

**Refuter's verification.** Unrounded 2006 gaps in occurrence_trends.json: AUS_NSW 1275.59 < WALES 1276.44, so the four lowest starters are Scotland (605), UK (655), NI (739), NSW — and NSW climbs only ×1.249, not among the fastest four. The two tie at the table's printed precision (both 1,276), so this is a rounding-level miss, but the sentence as written does not hold in the data; reproduced the table and Spearman −0.56 (n=19) via constant_window_trend.py. Resting the claim on the Spearman or noting the tie fixes it.

**Suggested fix.** 'Four of the five lowest starters (Wales and NSW tie at 1,276) are the four fastest climbers', or rest the sentence on the Spearman alone.

### ST8. [series+trend+cross-chamber] 4.5a (1994 trio paragraph)

> with the US chambers *starting* above where the UK still sits two decades later, US House at 1,515 per 100k in 1994 against the UK's 1,444 in 2026

**Problem.** 1994 to 2026 is 32 years — three decades, not two. The numbers themselves check out (US House 1,515.3 in 1994; UK 1,443.9 in 2026).

**Reviewer's check.** Verified both gaps in occurrence_trends.json and the ×3.80/×1.13/×1.19 and +4.3/+0.4/+0.5%/yr figures by recomputation over 32 years.

**Refuter's verification.** Verified in occurrence_trends.json: US House 1994 gap 1,515.3, UK 2026 gap 1,443.9 — the numbers are right, but 1994→2026 is 32 years, three decades. No alternative referent for 'two decades' is available in context (the sentence is explicitly about the 1994 window). 'Three decades later' is the fix.

**Suggested fix.** 'three decades later'.

### ST9. [series+trend+cross-chamber] 4.5b

> applied against each chamber's own pre-2022 counterfactual

**Problem.** The frozen protocol's pre window is 2018-01-01 to 2022-12-31 (replication_protocol.md, Clarification 1), i.e. it includes 2022; 'pre-2022' misstates the window that every combined p-value rests on. The trend sections correctly say 'pre-2023' for the same boundary.

**Reviewer's check.** Read replication_protocol.md lines defining the pre window ('sittings on or before 2022-12-31', 'pre = 2018-01-01 to 2022-12-31').

**Refuter's verification.** replication_protocol.md defines the pre window as sittings on or before 2022-12-31 (Clarification 1: pre = 2018-01-01 to 2022-12-31), i.e., 2022 is inside the counterfactual that every combined p-value in 4.5b rests on. 'Pre-2022' misstates it; the trend sections (e.g., the ITS paragraph and Figure caption) correctly say 'pre-2023' for the same boundary. Minor wording error, confirmed.

**Suggested fix.** 'pre-2023 (through 2022) counterfactual'.

### ST10. [series+trend+cross-chamber] 4.5 footnote rits / trend figure

> The cross-chamber comparison is `python build_trend_cache.py && python plot_trend_from_cache.py`

**Problem.** plot_trend_from_cache.py writes `the-ai-lexicon-trend.png` — the same filename fig_trend.py writes and the manuscript embeds — but draws a different chart (five-chamber indexed lines, NB dropped). Following the footnote's own reproduction commands silently overwrites the manuscript figure with one that no longer matches the printed caption (NB Panels A/B).

**Reviewer's check.** Read both scripts' savefig targets; confirmed the committed PNG is the fig_trend.py NB two-panel version matching the caption (regenerated it byte-identically), and that plot_trend_from_cache.py targets the identical filename.

**Refuter's verification.** Both scripts savefig to the identical filename the-ai-lexicon-trend.png: fig_trend.py draws the two-panel NB figure (Panels A/B) matching the manuscript's embed at draft line 664 and its caption, while plot_trend_from_cache.py draws a 1×2 five-chamber indexed chart with NB explicitly dropped ('NB dropped from lines' in its code). Following the footnote's reproduction commands overwrites the manuscript figure with a chart that no longer matches the printed caption. A distinct output filename for plot_trend_from_cache.py fixes it.

**Suggested fix.** Have plot_trend_from_cache.py write a distinct filename (e.g. trend-multichamber.png) and cite that in the footnote.

### ST11. [series+trend+cross-chamber] 4.5a (convergence statistic)

> the lower a chamber started, the faster it climbed** (Spearman between 2006 level and growth −0.56, n = 19)

**Problem.** The statistic reproduces exactly, but both variables are built from the same single-year 2006 endpoint (growth = gap2026/gap2006), so sampling noise in the 2006 draw mechanically pushes the correlation negative (the standard regression-to-the-mean critique of convergence regressions), and 2026 is a partial year for several chambers. The ~400–1,000-point genuine spread between the UK-family starters and the pack means the sign almost certainly survives, but the magnitude is biased and no multi-year-endpoint robustness is reported.

**Reviewer's check.** Reproduced −0.56 (n=19) with constant_window_trend.py; inspected the script — endpoints are single years, no averaging; year-to-year gap jitter in occurrence_trends.json is roughly 40–60 per 100k against a ~1,100 cross-chamber spread.

**Refuter's verification.** The statistic reproduces exactly (−0.565, n=19). constant_window_trend.py uses single-year endpoints with growth = gap2026/gap2006, so 2006 sampling noise appears on both axes with opposite sign — the standard regression-to-the-mean bias in convergence regressions — and 2026 is a partial year; footnote r45cw reports no robustness. I ran the multi-year-endpoint check myself: 2006–08 means vs 2024–26 means gives Spearman −0.511 on the same 19 chambers, so the bias is real but modest (~0.05 of −0.56) and the sign and substance survive, exactly as the finding predicts. The defect — an unqualified biased estimator with no reported endpoint robustness — stands as a minor reporting gap.

**Suggested fix.** Recompute with multi-year endpoint means (e.g. 2006–08 vs 2024–26) and report that Spearman alongside; note the endpoint-noise bias in footnote r45cw.

*Also flagged by: AL5, CB4.*

### SL5. [storyline] §2.4 The Opus screen tracks Pangram

> Contemporary human speech is the harder class to separate — as the permeation finding predicts — so the era mix is not flattering the screen.

**Problem.** 'The permeation finding' is invoked as established, but it is presented nine subsections later (§2.13), and no section pointer is given. In printed order the reader has met 'permeation' only as a definition in the Introduction, not as a finding that can predict anything.

**Reviewer's check.** Confirmed the permeation result first appears in §2.13; 'the permeation finding' at §2.4 carries no cross-reference.

**Refuter's verification.** Quote verbatim in §2.4, with no cross-reference, and the permeation result first appears at §2.13 in printed order — both checks reproduce. One detail of the reviewer's framing is off: the abstract does not mention permeation at all; it is the Introduction that defines it ('Permeation — whether human speech is drifting toward the machine register…') — but only as a measurement target, not a finding, so a first-time reader still has no positive result to anchor 'as the permeation finding predicts'. The minor forward-reference defect survives. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Add the pointer: 'as the permeation finding (§2.13) predicts' — the paper's own no-forward-reference conventions aside, an unlabelled forward dependency is worse than a labelled one.

### SL6. [storyline] §2.2

> its finite-sample bias is nil in practice (bootstrap mean 10.30% against a plug-in 10.31%, a −0.005-point gap)

**Problem.** The bias check is quoted for an estimate of 10.30–10.31%, which matches no rate the section reports (headline 9.03%, naive AI+Mixed 12.03%, equal-weight chamber mean 9.12%). The reader cannot tell which estimator the check validated. Incidentally 10.30 vs 10.31 is a 0.01-point gap, not −0.005.

**Reviewer's check.** Compared the 10.30/10.31 pair against every rate reported in §2.2 and Table 2; none matches. Recomputed the stated gap.

**Refuter's verification.** Quote verbatim in §2.2. The pair matches no rate printed in the section (pooled 9.03%, binary 12.03%, equal-weight mean 9.12%, ex-CA-FED 8.50%). Running banded_prevalence.py identifies the actual referent: the long-band-only (120–360) pooled word-weighted rate is 10.29% — 'what the study reported' before the short-band correction — so the bias check was evidently run on the superseded long-band estimator, a quantity the compiled paper never prints. The reader cannot connect the validation to the 9.03% headline it sits beside, exactly as the finding states. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** State what the 10.3% quantity is (e.g., the pre-exclusion or binary-verdict pooled rate the check was run on) or rerun the check on the headline estimator; fix the gap arithmetic.

*Also flagged by: CB8, CP9, XC12.*

### SL7. [storyline] §2.3 Drafting concentrates in scripted business

> it is the one place where the lexicon arm's inference is confirmed by an independent instrument. Two instruments agreeing is worth more than either alone.

**Problem.** 'The lexicon arm' first appears here (the instrument has so far been called 'the register instrument'), and no lexicon-arm inference has been presented yet in printed order — the register results begin at §2.5, and none of them concerns genre. The sentence asserts a two-instrument agreement whose first half the reader has not seen and cannot locate; the terminology also drifts across 'register instrument' / 'lexicon arm' / 'frequency arm' (§5.3) with no mapping.

**Reviewer's check.** Searched the compiled text preceding §2.3 for any lexicon/register-arm result: none exists; grepped 'lexicon' — it next appears at §2.13 and §5.3. No register-instrument genre analysis appears anywhere.

**Refuter's verification.** Quote verbatim in §2.3. I searched the full render for any genre/scripted-vs-unscripted stratification of the lexicon instrument (grep for scripted/unscripted/prepared/Topical/Leaders' Questions across §2.5–2.7, §2.13, appendices): none exists — Table 3's ladder is entirely Pangram-based. The design that would supply the lexicon half exists only as uncompiled repo artifacts (analysis/s10/unscripted_strata.py, permeation_strata.py, whose docstring frames exactly this prepared-vs-unscripted register test). No reading of 'the lexicon arm's inference' rescues the sentence: any reading requires a lexicon-arm counterpart result at the ladder, which the compiled paper never delivers. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Either name the specific lexicon-arm inference being confirmed with a pointer to where it is shown, or soften to a forward-looking remark ('the register arm's post-2022 rise, §2.5, points the same way'); pick one name for the instrument and use it throughout.

### SL8. [storyline] §3.4 / §3.8 item 9

> This moves for the same reason as S17's imitation lag, and is collapsing for the same reason (review item X11) — it is not literally the same quantity S17 measures.

**Problem.** 'S17' is an internal study code with no referent anywhere in the paper (no citation, no explanation of what S17 is or found); the same applies to 'the natural companion to S15' in §3.8 item 9. A first-time reader cannot follow either sentence. (S20 in item 28, by contrast, is at least glossed as a planned study with a plan file.)

**Reviewer's check.** Grepped the render for S15/S17/S20: S17 appears only in these two adjacent sentences and S15 once, with no definition; the reference list contains no corresponding entry.

**Refuter's verification.** Quote verbatim in §3.4. 'S17' occurs nowhere else in the render (grep confirms these two lines are the only occurrences), 'imitation lag' occurs only here, and no reference-list entry corresponds to it. S17 is the project's internal study label (the Nordhaus capture-ratio re-solve in analysis/s17/), meaningless to a paper reader, yet it carries the load-bearing analogy for the moving-baseline argument. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Suggested fix.** Replace the codes with self-contained descriptions ('a companion study of AI imitation lags', with a citation if public), or cut the sentences.


---

## MINOR — PARTIAL

### CE5. [claims-vs-evidence] Abstract (also Introduction)

> with an elevenfold spread across chambers and a concentration in scripted genres

**Problem.** The genre-concentration finding rests on a single chamber: §2.3 states "Federal Canada is the only corpus carrying a business rubric, which makes the test possible at all" — a 180-segment stratified arm in one legislature. Stated in parallel with the 20-chamber spread, the abstract implies corpus-wide evidence for the genre claim that the body does not have.

**Reviewer's check.** Verified that §2.3's genre ladder (Table 3) and the OQ audit are exclusively federal-Canadian, and that no other chamber carries a genre stratification.

**Refuter's verification.** Quote verbatim in the abstract. The reviewer's core check holds: §2.3 states "Federal Canada is the only corpus carrying a business rubric, which makes the test possible at all," and no other chamber has a genre stratification — the formal ladder (Table 3) is a 180-segment single-chamber test placed in parallel with the 20-chamber spread. But "evidence for the genre claim that the body does not have" is slightly too strong: §2.2's Manitoba frame-repair is independent second-chamber evidence of the same mechanism — the extractor had preferentially dropped the formatted, prepared speeches, and restoring them moved the chamber from 5.3% to 13.1%, i.e. machine text concentrated in prepared business in Manitoba too. The scope defect in the abstract is real; the claim is not single-chamber-only in the body.

**Accurate version.** The rubric-based genre test exists in one chamber only (federal Canada, §2.3), so the abstract's unscoped parallelism with the 20-chamber spread does overstate tested scope; however, the body carries corroborating (non-rubric) evidence from a second chamber — Manitoba's frame repair, where restoring the prepared speeches nearly tripled the measured rate — so the accurate fix is a scope note ("in the one chamber whose record permits the test") rather than a claim of no supporting evidence elsewhere.

**Suggested fix.** Add scope, e.g. "a concentration in scripted genres in the one chamber whose record permits the test."

### CE7. [claims-vs-evidence] Introduction, second paragraph

> Yet a 22-chamber policy scan finds no chamber requiring machine drafting to be disclosed and none forbidding it — the record is silent exactly where the change is happening.

**Problem.** §3.7 delivers the scan but with two qualifications the intro drops: "Coverage is partial for NI, Manitoba, PEI and South Australia — absence of evidence, not evidence of absence," and the section's own flag "(ai policy scan.md; figures unverified against primary sources)." The intro's flat universal ("no chamber ... none") is more certain than the section supports.

**Reviewer's check.** Compared the intro sentence against §3.7's coverage and verification caveats.

**Refuter's verification.** Quote verbatim in the Introduction; §3.7's caveats verified verbatim ("Coverage is partial for NI, Manitoba, PEI and South Australia — absence of evidence, not evidence of absence"; "figures unverified against primary sources"). But the finding overstates the gap: the intro's first clause is phrased as a scan-report ("a policy scan finds..."), which is literally accurate even under partial coverage, and it mirrors §3.7's own unhedged topline ("A 22-chamber scan found zero chambers requiring... and none forbidding") — so the intro is a faithful compression of the section's own summary sentence, not a claim the section refuses to make. The residual defect is real but narrower: the caveats appear nowhere in the intro, and the interpretive gloss "the record is silent exactly where the change is happening" asserts silence as fact in four chambers the scan could only partially see.

**Accurate version.** The intro's scan-report clause matches §3.7's own topline and is accurate as a report of what the scan found; the genuine defect is confined to the dropped partial-coverage caveat (4 of 22 chambers) and unverified-figures flag, which the gloss "the record is silent" outruns — a hedge such as "anywhere the scan could see" would close it.

**Suggested fix.** Hedge to match §3.7: "a 22-chamber policy scan finds no disclosure requirement and no prohibition anywhere it could see (coverage partial in four chambers)."

### CB8. [comparability] §2.2 word-weighting justification

> its finite-sample bias is nil in practice (bootstrap mean 10.30% against a plug-in 10.31%, a −0.005-point gap)

**Problem.** The bias check is quoted at 10.30/10.31% — a value matching no estimate reported anywhere in §2.2 (headline 9.03%, equal-weight mean 9.12%, naive AI+Mixed 12.03%, sans-CA-FED 8.50%), and no committed script in analysis/s10 prints it. The check appears to have been run on a different quantity or corpus snapshot (plausibly pre-Mixed-correction or a different pool) yet is presented as validating the 9.03% estimator. Additionally 10.30 − 10.31 is −0.01 at the displayed precision, not −0.005.

**Reviewer's check.** Compared 10.30/10.31 against every rate in §2.2; grep of banded_prevalence.py and the full analysis/s10 tree found no script producing the pair (only incidental hits in data files).

**Refuter's verification.** Quote verbatim at line 162. Core claim confirmed: 10.30/10.31% matches no estimate in §2.2 (headline 9.03%, equal-weight 9.12%, naive 12.03%), no committed script in analysis/s10 prints the pair, and running banded_prevalence.py identifies the likely source — the long-band-only estimator is 10.29% (the pre-band-combination quantity, '1.14× the combined' 9.03%), so the check appears to have been run on the long-band pool, not on the headline estimator it is presented as validating. The arithmetic sub-complaint fails, however: unrounded values (e.g. 10.304 vs 10.309) can differ by 0.005 while displaying as 10.30/10.31, so '−0.005-point gap' is not an error at the displayed precision.

**Accurate version.** The bootstrap-vs-plug-in check was evidently computed on the long-band-only pool (10.29% per banded_prevalence.py), not on the 9.03% headline estimator, and no committed script reproduces it; it should be re-run on the exact headline estimator or its sample stated. The −0.005 vs −0.01 precision complaint does not stand.

**Suggested fix.** Re-run the bootstrap-vs-plug-in check on the exact headline estimator (fraction-weighted, TAS excluded) and quote matching numbers, or state which estimator/sample the 10.3% check was computed on.

*Also flagged by: CP9, SL6, XC12.*

### CB10. [comparability] §3.6 Related work

> The 9.0% floor itself lands where the population-level literature already points for professional prose — 6.5–17.5% (Liang et al. (3, 4), Gray (6)) — which we read as corroboration, not coincidence.

**Problem.** The 9.0% is a share of WORDS machine-drafted in transcribed speech; the Liang et al. 6.5–17.5% figures are estimated shares of sentences/text substantially AI-modified in peer reviews and scientific papers — a different unit, a different modification concept (modified vs drafted), and a different genre. Claiming the numbers 'land where the literature points' as corroboration requires the unit/domain caveat the sentence omits.

**Reviewer's check.** Compared the estimands: §2.2's word-share ratio estimator vs Liang et al.'s distributional estimates of the AI-modified fraction of sentences in review/paper corpora (as the paper's own intro describes them).

**Refuter's verification.** Quote verbatim at lines 2037-2039. The estimands do differ: §2.2's figure is the share of words machine-drafted in transcribed speech; Liang et al.'s 6.5–17.5% are distributional estimates of the fraction of sentences/texts substantially AI-modified in peer reviews and scientific papers — different unit, modification concept, and genre — so 'corroboration' overstates what range-overlap across non-commensurable estimands can deliver. But the finding's 'omits the caveat' framing is weakened by the paper itself: the introduction (lines 46-48) accurately describes the Liang estimand ('estimate the machine-modified fraction of a whole corpus distributionally... on peer reviews and scientific papers'), so the differing unit is stated in-paper, just not at the claim site.

**Accurate version.** The agreement is order-of-magnitude consistency across different units and genres — suggestive, not corroborating — and the sentence should carry that caveat locally even though the intro describes the Liang estimand correctly.

**Suggested fix.** Add the caveat: same order of magnitude across different units and genres, suggestive rather than corroborating — or convert to a comparable unit before claiming agreement.

### CB11. [comparability] §2.14 Stage 5 / bypass accounting

> every rewrite that reached a Human verdict (39 variants across 15 targets, one target's original text unavailable and dropped) was graded blind against its original

**Problem.** Three counts of the same population go unreconciled: the bypass arm reports 38 of 341 variants reaching Human (16 targets); stage 5 says 39 variants across 15 targets (after dropping a target, which should reduce, not raise, the count — unless superseded-run variants were silently added); and Table 25 then reports variant n = 35. The graded set is thus not identifiably the same sample as the bypass result it is meant to complement.

**Reviewer's check.** Traced Human-verdict counts across §2.14: 38/341 (per-variant), 16 pooled targets ≥1 Human (Table 22), stage 5's 39/15, Table 25's n=35, and §3.2's '35 machine rewrites'.

**Refuter's verification.** Quote verbatim at lines 1663-1664. The data and the frozen prereg fully reconcile the three counts, so 'not identifiably the same sample' is refuted: stage5_humans.json holds exactly 39 Human variants across 16 targets = 38 from the two final runs (29 NB v3 + 9 GO all-31, matching 38/341 and Table 22's 16 targets) + 1 from superseded NB v2; PREREG-stage5-successful-evasion.md (frozen 2026-08-16) states '39 Human-verdict variants across 16 targets (NB v2, NB v3, GO all-31). 35 pairs / 15 targets are gradeable; one target (seg_id 2025-12-04#t1466w0, 4 variants) is dropped', which I verified in the data (the dropped target carries 1 NB v2 + 3 NB v3 variants). So 39→35 and 16→15 are exact, not silent. What survives: the paper's sentence itself is garbled — 39 variants go with 16 targets and 35 with 15, so '39 variants across 15 targets' pairs a pre-drop count with a post-drop count — and the in-paper text nowhere states that stage 5 pools in the one superseded-run variant (38+1=39).

**Accurate version.** The accounting is sound and documented in the frozen prereg (39 Humans / 16 targets pooled over NB v2 + NB v3 + GO all-31; dropping the one target with unavailable original, 4 variants, leaves the graded 35 / 15 of Table 25), but the paper should state the derivation and fix '39 variants across 15 targets' to '39 across 16, 35 graded across 15'.

**Suggested fix.** State the derivation once: which runs contribute, how 38 becomes 39, and why 4 variants drop from 39 to the graded 35.

*Also flagged by: IC10, QB6, XC10.*

### CB12. [comparability] §2.1 / Table 1

> Table 1: Calibration on pre-2022 speech: specificity of Pangram 3 versus Pangram 4. ... AI + Mixed, overall 122 144 / exact agreement 92%

**Problem.** Under a caption announcing pre-2022 calibration/specificity, the last two rows report AI+Mixed verdict counts and 92% exact agreement over the full 658-segment rescore, which necessarily includes post-2022 speech (the pre-AI control is n=60 and flags nothing). Post-2022 model-comparison quantities are presented inside a pre-2022 specificity table without labeling the sample switch.

**Reviewer's check.** Compared the caption and the first two rows' sample (pre-AI control, 2020–22) against the 'overall' rows' implied sample (658 segments, byte-identical rescore including current speech, per the surrounding text).

**Refuter's verification.** Table verified at lines 129-135. The lower rows are indeed computed over the full 658-segment rescore including current speech (the pre-AI control is n=60 and flags nothing, so 122/144 AI+Mixed verdicts are necessarily post-2022), while the caption announces pre-2022 calibration/specificity — the caption's scope is wrong for those rows. But 'without labeling the sample switch' is overstated: the sentence immediately introducing the table reads 'New Brunswick rescore. 658 segments, byte-identical stored text, Pangram 3 vs Pangram 4:', and the row itself is labeled 'AI + Mixed, overall' — 'overall' marking the full-rescore sample against the 'pre-AI control (n=60)' rows above it. The switch is signposted, tersely; the caption is misscoped.

**Accurate version.** The caption covers only the first two rows; the 'overall' rows are the full 658-segment all-era rescore, as the introducing sentence states. Fix is caption scope ('...; lower rows: full 658-segment rescore, all eras') rather than an unlabeled sample switch.

**Suggested fix.** Split the table or relabel the lower rows (e.g., 'full 658-segment rescore, all eras') so the specificity caption covers only the pre-2022 rows.

### CB13. [comparability] §2.9 / Table 11 (education levels)

> secondary −0.281 234 −0.166 (t = −2.69) ... bachelor +0.042 1,194 baseline

**Problem.** The 'mean z' and 'vs bachelor' columns are different estimands mixed in one table introduced as a single cohort-controlled read: −0.281 − (+0.042) = −0.323, not the −0.166 the contrast column shows, so the means must be raw while the contrasts are cohort-adjusted (or otherwise modeled) — nothing in the table or text says which, and a reader differencing the mean column reproduces none of the printed contrasts.

**Reviewer's check.** Differenced the mean-z column against the 'vs bachelor' column for each row (secondary −0.323 vs −0.166; college −0.203 vs −0.139; professional −0.172 vs −0.091); the systematic attenuation indicates a covariate-adjusted contrast beside unadjusted means.

**Refuter's verification.** Table 11 verified at lines 786-791, and the core is confirmed: differencing the mean-z column reproduces none of the printed contrasts (−0.281 − 0.042 = −0.323 vs −0.166; college −0.203 vs −0.139; professional −0.172 vs −0.091), and member_level_estimation.py's docstring confirms the mechanism — 'Class/education coefficients here are controlled for birthdec and are the citable versions', i.e. the contrasts are cohort-adjusted while the mean-z column is raw within-chamber z-means; the table's lead-in ('22 chambers, cohort controlled, baseline bachelor') does not say which column is which. The Table 10 extension is weaker than claimed, though: Table 10's mean column is explicitly introduced as 'reading the raw within-chamber means so that every class stands on its own rather than against a baseline', so its raw-vs-adjusted split is labeled in text (the class-I contrasts in the running text are adjusted without saying so, a residue).

**Accurate version.** Table 11 mixes raw within-chamber mean-z with birthdec-adjusted contrasts and should label the columns; Table 10 already labels its mean column as raw in the introducing sentence, so only its in-text contrasts lack the 'cohort-adjusted' tag.

**Suggested fix.** Label the columns ('raw within-chamber mean' vs 'cohort-adjusted contrast'), or print means and contrasts from the same specification. The same raw-vs-adjusted mixture appears in Table 10 (class means vs class-I contrasts) and deserves the same labeling.

### XC7. [cross-cutting] §2.11 (post-training artifact)

> Pooled alignment effect +0.387 on the scaled generation — three model families, 1,600 prompt pairs each, 1.19M base words.

**Problem.** The family count is unstable within the section: the pooled effect is attributed to 'three model families, 1,600 prompt pairs each', but the same section then says 'All four families are positive on their own — +0.356 to +0.749 pooled' and discusses the 30B MoE 'whose instruct side never passed 800 prompts' (so not 1,600 each); it also quotes 'on Qwen3 alone +0.6776 → +0.7481 from 1,600 to 3,200' prompts although the run 'stopped at 1,600 prompts rather than its planned 6,400.'

**Reviewer's check.** Traced every family-count and prompt-count statement in §2.11 and the artifacts table ('3 families at 1,600 prompts').

**Refuter's verification.** Rerunning rlhf_pref_compile.py shows the design is internally coherent and mostly stated: the +0.387 pool is llama31/qwen3/mistral at n=1600 (1,187,489 base words — matching the text, footnote 26, and the artifacts table, all of which say three families at 1,600), the MoE (qwen3_a3b) sits at 800 and outside the pool, and 'all four families positive, +0.35 to +0.75' is the per-family replication at each family's own checkpoint. So the three-vs-four counts are not a contradiction: the fourth family's exclusion is inferable from '1,600 each' plus the stated 800-prompt cap. What survives is looseness, not instability of the pool's membership. [verdict carried from the first refutation pass; this dimension's second-pass refuter hit the session limit]

**Accurate version.** Two genuine slips remain: (a) 'The run stopped at 1,600 prompts rather than its planned 6,400' contradicts the Qwen3 3,200-prompt checkpoint quoted a few lines above — per-family stopping points were actually 800/1,600/1,600/3,200; (b) the section never states outright that the MoE family is excluded from the +0.387 pool for missing the 1,600 mark, leaving the reader to infer it. The pool's composition itself is stated consistently in all three places.

**Suggested fix.** State the design once: which families enter the +0.387 pool, at what prompt counts, and which family/prompt extensions (MoE at 800, Qwen3 at 3,200) sit outside it.

*Also flagged by: PT9.*

### GS4. [genre+screen] 4.3 (footnote r43w)

> `python prevalence_report.py` for the rates and bootstrap intervals; the SO31-vs-OQ permutation is 50,000 label shuffles of the pooled prevalence segments.

**Problem.** No committed script or artifact computes the headline permutation p = 0.0025, and the footnote also credits prevalence_report.py with 'adjacent-rung Fisher exacts' it does not print. The test's sidedness is unstated: my independent 50,000-shuffle reimplementation of the described test gives one-sided p ≈ 0.0015 and two-sided ≈ 0.0029, so 0.0025 is consistent only within Monte Carlo noise of the two-sided reading. (The Fisher values 0.16 and 0.043 and the Cochran–Armitage z = 3.70 do verify by independent computation.)

**Reviewer's check.** Read prevalence_report.py end to end (prints rates, bootstrap CIs, CA trend only); grepped all .py for the permutation — absent; reimplemented the word-weighted label permutation and both Fisher exacts.

**Refuter's verification.** The core claim holds: no committed script computes the headline permutation p = 0.0025 (prevalence_report.py prints rates, bootstrap CIs, the genre table and the Cochran–Armitage trend only; a grep of every .py in analysis/s10 finds no SO31-vs-OQ shuffle), and sidedness is unstated — my 50,000-shuffle reimplementation of the word-weighted label permutation gives one-sided 0.00128 and two-sided 0.00246, so 0.0025 matches only the two-sided reading within Monte Carlo noise. The Fisher (0.16, 0.043) and CA (z = 3.70, p = 2.15e-4) values do verify. But the secondary charge — that the footnote 'credits prevalence_report.py' with the Fisher exacts — over-reads the footnote: its clause says the Fishers 'are computed from the 3×2 segment table', and the script does print that table's counts ([5of60/14of60/22of60]), so the passive clause describes provenance, not a claim that the script prints the Fishers.

**Accurate version.** The headline permutation p = 0.0025 has no committed computation and its sidedness is unstated (it reproduces only as the two-sided test); the Fisher and CA values verify independently, and the footnote's Fisher clause is ambiguous provenance-language rather than a clear false attribution — though the Fishers also lack any committed script.

**Suggested fix.** Commit the permutation (and Fisher) computation to prevalence_report.py or a named script, state one- or two-sided, and re-quote the p from that run.

### GS8. [genre+screen] 4.4 The Opus screen tracks Pangram

> restricting the negatives to 2023-and-later contemporary speech only *lowers* the AUC, to **0.940** [0.915, 0.961]. Contemporary human speech is the harder class to separate — as the permeation finding predicts

**Problem.** A directional corroboration ('as the permeation finding predicts') is drawn from a 0.014 AUC difference between nested samples with heavily overlapping CIs and no paired test, in the same section that declares 'Effects below ~0.03 AUC are outside this design's resolution' for a 0.009 difference. The two comparisons differ in n, but no resolution argument is given for the 0.014, so the section applies opposite evidentiary standards to same-order effects.

**Reviewer's check.** Reproduced both AUCs and CIs via opus_screen_auc.py (0.9538 [0.934,0.971]; 0.9396 [0.915,0.961]); confirmed no paired/permutation test exists for the era restriction in any script.

**Refuter's verification.** The reviewer's facts check: both AUCs reproduce (0.9538/0.9396), no paired or permutation test for the era restriction exists in any committed script, and the writeup quotes only the 0.014 nested difference while elsewhere declaring ~0.03 the design's resolution floor. But the inconsistent-standards charge dissolves under the correct decomposition: the inference 'contemporary human speech is the harder class' corresponds to the pre-2023 vs 2023+ NEGATIVES contrast against the 104 shared positives, which I computed directly — AUC 0.9782 (pre negatives, n=189) vs 0.9396 (post negatives, n=325), a 0.039 difference whose paired bootstrap (2,000 draws, resampling each negative set with shared positives) gives 95% CI [0.022, 0.057], excluding zero and exceeding the stated 0.03 floor. So the claim is not a same-order effect held to a laxer standard; it is a larger effect that happens to be presented through the diluted 0.014 nested comparison, untested on disk.

**Accurate version.** As written the inference rests on an untested 0.014 difference between nested samples; the underlying pre-vs-post-negatives contrast is 0.039 AUC with a paired-bootstrap CI excluding zero (my computation, not in the repo), so the fix is to commit that paired test and present the contrast that actually supports the sentence, not to drop the claim.

**Suggested fix.** Report it as a robustness check only ('the era mix is not flattering the screen') and drop or test the 'harder class / permeation predicts' inference (e.g., paired bootstrap over shared positives).

### IC14. [internal-consistency] Supplementary: Provenance and reproducibility vs §2.14 footnote 31

> All arms complete, including the detector-bypass study and both prior-art comparators. Everything is reproducible from analysis/s10/.

**Problem.** Footnote 31 states the opposite for the arm that carries the largest share of the per-variant evasion rate: 'the New Brunswick searches and the contrast-pair builders were run ad hoc and survive only as their outputs ... so NB v3, the largest single contributor to the per-variant rate, is documented by its outputs and BYPASS METHODOLOGY.md, not by a re-runnable script.' A blanket 'everything is reproducible' is contradicted by the paper's own disclosed reproducibility gap.

**Reviewer's check.** Compared the provenance claim with footnote 31's 'Reproducibility gap, stated plainly' and C.3.

**Refuter's verification.** Quote at lines 2646-2648, and footnote 31 (lines 1438-1444) does name a 'Reproducibility gap, stated plainly': the New Brunswick searches and contrast-pair builders were run ad hoc and survive only as outputs. But the blanket sentence has a defensible reading the reviewer's framing skips: footnote 31 also states that bypass_report.py 'reads the verdict files and prints every figure in this subsection' from committed artifacts, so every reported number, including NB v3's, does reproduce from analysis/s10/. What cannot be re-run is the variant-generating search process itself (plus the rewritten variant text is held locally under the corpus-licence policy).

**Accurate version.** The provenance line is true for numbers-from-artifacts (every reported figure, NB v3 included, reproduces via bypass_report.py from committed verdict files) but overstates process reproducibility: the NB searches and contrast-pair builders are documented by outputs and BYPASS_METHODOLOGY.md only, a gap the paper itself labels a 'reproducibility gap' in footnote 31 — so the unqualified 'Everything is reproducible' should carry that qualifier.

**Suggested fix.** Qualify the provenance line: every reported number reproduces from committed artifacts, except the NB bypass searches, which are documented by outputs only (per footnote 31).

### OP6. [occupational-prereg] Results 4.6b (delta group form)

> Its group form — members split by relative inwardness, insulated against exposed — puts the insulated cell above the rest (t 2.1 on the gap)

**Problem.** The quoted t 2.1 is the insulated-vs-FRONT-LINE contrast (+0.082, t +2.1, from prereg_posthoc_groups.py, whose own header labels the split POST-HOC), not the insulated-vs-exposed gap the sentence names. The insulated-vs-exposed gap is +0.128 (t ≈ 2.7) with farmers and collapses to +0.016 (≈ null) once the 199 farmers are removed from the exposed cell — so the contrast the sentence describes has no surviving support at t 2.1.

**Reviewer's check.** Ran prereg_posthoc_groups.py and prereg_synthesis_check.py; computed the insulated-exposed t from the printed means/ses.

**Refuter's verification.** Reran both scripts. The t 2.1 is indeed corp-insulated − front_line (+0.082, t +2.1), the script's own header labels the split POST-HOC, and the insulated-vs-exposed contrast is +0.128 (t ≈ 2.7) with farmers, collapsing to +0.016 (insulated +0.037 vs exposed-no-farmers +0.021, null) without them — all reviewer numbers confirmed. But the sentence's claim survives better than the finding allows: 'above the rest' is true of every cell in point estimate, the quoted t 2.1 attaches to the farmer-free front-line contrast (the conservative, binding one — larger gaps exist to the other cells), and the same sentence explicitly discloses that the exposed leg is farmer-dragged ('one leg farmer-driven and reported as such: the 199 members... sit in the exposed cell and drag it'). The reviewer's 'no surviving support' conclusion holds only under the insulated-vs-exposed reading of 'the gap', which the sentence's own farmer flag partially anticipates without quantifying.

**Accurate version.** The t 2.1 belongs to the insulated-vs-front-line contrast (+0.082), not the insulated-vs-exposed gap the sentence's phrasing suggests; insulated-vs-exposed is +0.128 (t ≈ 2.7) with farmers and ≈ +0.016 (null) without them — a collapse the sentence flags qualitatively ('one leg farmer-driven') but does not quantify. The sentence should name its contrast and label the median split post-hoc (as the script header does); the claim that the insulated cell sits above every other cell, with its binding farmer-free contrast at t 2.1, is itself supported.

**Suggested fix.** Name the contrast the t belongs to (insulated vs front-line), label the split post hoc, and state the insulated-vs-exposed gap with and without farmers.

### OP8. [occupational-prereg] Results 4.6b (horse race)

> The uncharged (coded) instrument wins the registered AIC comparison narrowly (−205.0 vs −198.6)

**Problem.** ΔAIC = 6.4 is not 'narrow' by standard AIC reading (Δ>4 = considerably less support for the losing model). The registered interpretation of an uncharged win — 'hierarchy position as such carries the register and the accountability theory adds nothing' — is also never stated; the text moves directly to the (also-registered) encompassing tests, which soften but do not replace the registered reading of criterion 1.

**Reviewer's check.** prereg horse-race criterion and reading vs prereg_stage1_results.txt §4 (reproduced); Burnham–Anderson ΔAIC convention.

**Refuter's verification.** ΔAIC = 6.4 is confirmed (stage-1 §4, reproduced), and by the Burnham–Anderson convention Δ 4–7 is 'considerably less' support, so 'narrowly' is an inapt minimizer — though both AIC values are printed, so the reader can compute the gap. The second half of the finding is weaker: the registered reading of an uncharged win ('hierarchy position as such carries the register and the accountability theory adds nothing') is empirically contradicted by the also-registered criterion 3, whose encompassing tests (F 5.60 p .0002 and F 4.02 p .003, both reported in the text as 'significant in both directions — neither instrument subsumes the other') show the charged instrument does add explanatory variation; reporting criterion 3's outcome rather than restating a verbal reading criterion 3 refutes is a defensible choice, not suppression.

**Accurate version.** 'Narrowly' should be dropped or replaced with the quantity (ΔAIC 6.4, considerable under the standard AIC reading); the omission of the registered 'adds-nothing' verbal reading is defensible because the registered encompassing tests, which the text does report, contradict it.

**Suggested fix.** Drop 'narrowly' or quantify (ΔAIC 6.4), and state the registered reading of the uncharged win alongside the encompassing-test qualification.

### OP9. [occupational-prereg] Results 4.6b (instrument description)

> whose assignment to four components was itself blind-derived by three independent coding workflows over the full 295-element universe

**Problem.** One of the three workflows (anchored) showed coders the draft cells — the prereg keeps it precisely as the anchoring control, not an independent derivation — and the membership criterion was the four-cell run's unanimity plus one 2/3 element (Frequency of Decision Making) admitted on Matthew's explicit call. 'Three independent' and fully 'blind-derived' overstate the derivation for that arm and that element.

**Reviewer's check.** Prereg 'How the cells were fixed: three blind derivations' section (anchored arm saw the draft; 2-of-3 exception logged).

**Refuter's verification.** The underlying facts are confirmed from the prereg's 'three blind derivations' section: the anchored arm's coders saw the draft cells (kept precisely as the anchoring control), and Frequency of Decision Making entered at 2/3 by Matthew's explicit call, the single sub-unanimous element. But two pieces of context weaken the finding: 'blind-derived' is defensible in the sense the prereg itself uses (coders in all three arms saw element names and descriptions only — never per-occupation values, never anything about the register or hypothesis), and the section's opening names METHODOLOGY §6.1c as the method record, which states exactly what the reviewer asks for ('an anchored arm shown the draft, an unanchored control, and a four-cell arm... one 2/3 exception by Matthew's explicit call'). The membership criterion was also the blind four-cell run's unanimity, so the operative derivation was unanchored. Only the summary sentence's 'three independent' overstates.

**Accurate version.** The §4.6b summary's 'three independent... blind-derived' overstates one arm: all three workflows were blind to the register, the hypothesis, and per-occupation values, but the anchored arm saw the draft cells as the prereg's anchoring control, and one element (Frequency of Decision Making) entered at 2/3 by explicit call. The section's cited method record (METHODOLOGY §6.1c) and the prereg state this accurately; the summary sentence should say 'three coding workflows (one anchored as a control, two unanchored)' and note the single sub-unanimous element.

**Suggested fix.** Say 'three coding workflows (one anchored as a control, two unanchored)' and note the single sub-unanimous element.

### PT7. [posttraining+coverage+permeation] 4.7 footnote r47

> The estimator used here returns +0.003 on those same nulls, so the +0.387 sits on nothing.

**Problem.** The committed null calibration does not return +0.003: rlhf_pref_analyze.py prints 'null pedestal (30 random frequency-matched lists): +0.0186 sd 0.0605, 18/30 positive'. The conclusion is unaffected (+0.019 is still negligible against +0.387, 11 sd above noise per the script), but the quoted value is not what the cited machinery produces.

**Reviewer's check.** Ran rlhf_pref_analyze.py and read its null-calibration output.

**Refuter's verification.** Confirmed that +0.003 is not what the cited machinery produces for the scaled run — but two corrections to the finding. First, +0.003 is not an unnamed configuration: it has committed provenance at METHODOLOGY.md:1499, from the earlier corrected two-family 180-token run (the same passage carrying the 27% figure), so it is a stale carry-over rather than an invented number. Second, the reviewer's replacement value is itself irreproducible: rlhf_pref_analyze.py's null calibration shares the unfixed-hash-seed nondeterminism — the reviewer's run printed +0.0186 (18/30 positive) while mine printed −0.0047 sd 0.0602 (16/30 positive). The conclusion (pedestal negligible against +0.387) is unaffected in every run.

**Accurate version.** The +0.003 comes from the superseded 180-token two-family configuration (METHODOLOGY.md:1499), not the scaled run the footnote describes; the committed script's null calibration is itself nondeterministic (printing values like +0.019 or −0.005 across runs, all negligible). Fix by fixing the hash seed in the null calibration, rerunning on the scaled configuration, and quoting that value at 2 significant figures.

**Suggested fix.** Quote the script's value (+0.019, sd 0.06) or, if +0.003 came from a different configuration, name and commit it.

### QB8. [quality+bypass] 4.9 Stages 1 and 2 (main table header)

> | *segments (regressor)* | *840 (screen score; sd 15.3, max 70)* | *same fit, rescaled* | *682 (Pangram verdict, binary)* |

**Problem.** The stage-2 column is headed 'AI vs Human verdict' / 'Pangram verdict, binary', but the regressor pools the 134 Mixed verdicts with the 207 AI ones against 341 Human (disclosed only in footnote r49q). 'AI vs Human, binary' misdescribes an AI+Mixed-vs-Human contrast in the table a reader will quote; the --drop-mixed sensitivity does confirm the starred cells barely move (+0.263/+0.283/+0.231, reproduced).

**Reviewer's check.** Ran analyze_stage2.py (header prints 'Mixed pooled with AI') and analyze_stage2.py --drop-mixed; pool composition 207/134/341 from quality_expansion/RUNME.md.

**Refuter's verification.** The facts check out: the stage-2 regressor pools 134 Mixed with 207 AI against 341 Human (682 total), the header cell reads 'AI vs Human verdict' / 'Pangram verdict, binary', and the --drop-mixed sensitivity leaves the starred cells nearly unchanged (+0.263/+0.283/+0.231, quoted in the footnote). But the disclosure is stronger than 'only in a footnote' suggests: footnote 29 is anchored to the sentence that introduces the table, on the same page, and was placed there deliberately per review item Q7 ('Coding disclosed at the table per the same item'). The residual defect is real but narrow — the header cell itself carries no flag, so the cell quoted in isolation misdescribes the contrast.

**Accurate version.** The stage-2 header cell 'AI vs Human verdict / Pangram verdict, binary' misdescribes an AI+Mixed-vs-Human contrast when the cell is quoted alone; however, the pooling and the drop-mixed sensitivity are disclosed in footnote 29 anchored at the table itself (a placement chosen per review item Q7), so only the header wording — not the disclosure — needs fixing (e.g. 'AI+Mixed vs Human verdict' or a footnote marker on the cell).

**Suggested fix.** Head the column 'AI+Mixed vs Human verdict' (or footnote-mark the header cell itself), keeping the drop-mixed sensitivity note.


---

## Notes: method, blinding, and progress (moved to the end)

**Reviewed state:** commit `66b508f`. **Blinding:** run with no access to any prior review; reviewers were barred from files named REVIEW/AUDIT/RESPONSES, and in-text parentheticals like "(review item B4)" were treated as unverified author claims and audited directly.

**Method.** Thirteen blind reviewers, one dimension each: seven data dimensions reproducing numbers from the committed artifacts and reading estimator code (calibration+prevalence, genre+screen, series/trend/cross-chamber, cohort+class, occupational-prereg, post-training/coverage/permeation, quality+bypass), five narrative/argument dimensions on the compiled publication-order paper (claims-vs-evidence, internal-consistency, argument-logic, comparability, storyline), and one cross-cutting consistency reviewer. Every finding was handed to a refute-by-default adversary; only CONFIRMED and PARTIAL findings appear, PARTIAL with the corrected version stated. "Also flagged by" marks the same defect under another lens — adjudicate once, apply everywhere.

**Counts.** 138 open (0 critical, 64 major, 74 minor; 115 CONFIRMED, 23 PARTIAL); 1 refuted; 0 unresolved.

**Progress since the review ran (2026-08-24/25).** Both criticals closed by new analysis rather than rewording: (1) the floor's specificity-transfer assumption stated and bounded — a two-vote blind audit of all 316 flagged segments (277 prepared / 21 unclear / 11 both-vote spontaneous, 9 of them Mixed at fractions 0.11–0.58) puts the worst case at 9.03%→8.86% (§3.1, §4.1, Limits; flagged_hits_*). (2) The APC identification: per-legislature group-vs-individual gradients in one unit (apc_chamber_decomposition.py, new §4.6 figure) split the birth gradient into a standing juniority component (full-size among pre-drift cohorts — US Senate +105 [47,155], 1994–2004) and a cohort component (UK +30→+98, House +23→+85 as drift-formed cohorts enter); "organised generationally" retired paper-wide. Also applied: the mechanical batch (broken cross-refs, §8.6 renumbering, review-code and dagger conventions, external-table disambiguation, flip/success direction), the registration-timeline footnote, the Kobak contextualisation of the abstract, and the explanatory-power/iceberg passage at the joint model. Resolved items below; nothing deleted.


---

## RESOLVED since the review ran

- **[critical] [occupational-prereg]** Results 4.6b (headline framing): "The design intent, registered in the document's hierarchy section and throughout the pre-r..." — *adjudicated (Matthew): lead rewritten as a timeline; minute-level registration footnote added (12:04 transcript prediction → 13:05 prereg commit → 13:17 unblinding → 13:36 amendment → 17:21 ruling); meta-point on pervasive logging added*
- **[minor] [occupational-prereg]** Results 4.6b (cross-reference): "that operationalization failed its own test and the framing is retired — Appendix B8 prese..." — *fixed: duplicate of the B8→B10 pointer correction (mechanical batch)*
- **[major] [quality+bypass]** 4.9 Bypass study (flip vs success paragraph): "Effort raised both bars, and by *more* on the flip bar (2.8×) than on the success bar (5.5..." — *fixed: same direction correction*
- **[major] [internal-consistency]** §2.14 Bypass study (flip vs success bars): "Effort raised both bars, and by more on the flip bar (2.8×) than on the success bar (5.5×)..." — *fixed: duplicate of the flip/success direction correction (mechanical batch)*
- **[critical] [argument-logic]** §2.8 (Birth cohort predicts the register) and Abstract: "if it were generational, later-born members would use more of it even in the same year and..." — *resolved by new analysis per Matthew's design (apc_chamber_decomposition.py, apc_gradients.png): group vs individual gradients per legislature in one unit. The gradient splits into a standing juniority component (full-size among pre-drift cohorts, US Senate +105 [47,155], 1994-2004, births 1917-64) and a cohort component (UK +30->+98, House +23->+85 as drift-formed cohorts enter; House chamber mean flat -> ambient-culture formation). §4.6 rewritten around the two components with the identity stated and the era-stable-profile assumption named; abstract/intro/Discussion/Limits harmonized; 'organised generationally' retired.*
- **[major] [argument-logic]** §2.10 (Pre-registered occupational test) with Appendices A18–20, B10: "The registered four-level U is the result. The design intent, registered in the document's..." — *adjudicated (Matthew): same timeline footnote fix*
- **[minor] [argument-logic]** §2.1 / §5.1 (calibration and the floor claim): "with Sp = 1 and any real detector's Se ≤ 1, the observed flag rate is a conservative floor..." — *addressed per Matthew's direction: floor claim conditioned in §3.1; new §4.1 contemporary-specificity block — two-vote blind audit of all 316 hits (277 prepared / 21 unclear / 11 both-vote spontaneous, 9 of them Mixed at 0.11–0.58), worst-case bound 9.03%→8.86% (8.65% full-word); temporal-transfer bullet added to Limits; artifacts committed (flagged_hits_pool/audit/bound)*
- **[minor] [comparability]** §2.4 The Opus screen tracks Pangram: "consistent with §5.4's finding that reasoning never closes the ˜0.25 AUC frontier gap, but..." — *fixed: duplicate of the removed §5.4/~0.25-AUC cross-reference (mechanical batch)*
- **[major] [storyline]** §2.4 The Opus screen tracks Pangram: "consistent with §5.4's finding that reasoning never closes the ˜0.25 AUC frontier gap, but..." — *fixed: false cross-ref and unanchored ~0.25 AUC removed; sentence now self-contained*
- **[major] [storyline]** §3.8 Future work (item numbering) and §3.5 Limits: "All three are first customers for the build-the-instrument-in-any-language method in item ..." — *fixed: §8.6 renumbered sequentially 1–35; all item refs updated (items 8–10, 11, 8, 33)*
- **[major] [storyline]** Throughout (first use §2.2): "the longest quartile of segments runs 9.4% against 5.8% for the shortest (review item X12)..." — *fixed: review-code convention defined at first use (footnote) and in the provenance note*
- **[minor] [storyline]** §2.14 (stage 6 discussion): "wild flagged text shows the collapse (§Q1) while frontier raw text does not..." — *fixed: dangling (§Q1) replaced with a prose pointer to the applicability result*
- **[minor] [storyline]** §2.2 (first use) and §2.6 footnote: "65,795 machine-written words of 728,998 across 3,519 segments in 20 chambers, excluding re..." — *fixed: regime-flag first use now points at §2.1's diagnostic*
- **[minor] [storyline]** §2.5 (first use) / Supplementary provenance note: "human register had been moving toward what instruct-tuning later selected for, for thirty ..." — *fixed: dagger convention footnote attached at first use; full key remains in provenance*
- **[minor] [storyline]** §3.6 Related work / §2.14 footnote 32: "on the Sem-Detect peer-review benchmark reprinted in the Pangram 4 report (Table 27), both..." — *fixed: external table references disambiguated (their/its Table N)*
- **[major] [cross-cutting]** §2.14 (bypass, flip vs success rates): "Effort raised both bars, and by more on the flip bar (2.8×) than on the success bar (5.5×)..." — *fixed: direction corrected — more on the success bar (5.5×) than the flip bar (2.8×)*
- **[major] [cross-cutting]** §2.4 (Opus screen, effort A/B): "consistent with §5.4's finding that reasoning never closes the ˜0.25 AUC frontier gap..." — *fixed: same as storyline item — cross-ref removed*
- **[minor] [cross-cutting]** §2.10 (pre-registered occupational test): "that operationalization failed its own test and the framing is retired — Appendix B8 prese..." — *fixed: pointer corrected to Appendix B10*


---

## Refuted (for the record)

- [comparability] §2.11 The register is a post-training artifact: The pooled +0.387 is described as three families (so is footnote 27: 'Three families at 1,600 prompts'), but the replication claim counts four families as if from the same run. The fourth (the 30B MoE — *refuted: Both quoted fragments are verbatim (lines 1173-1174, 1218-1219), but the alleged inconsistency dissolves on the correct reading, verified against rlhf_pref_final.json. The +0.356–0.749 range is per-fa*
