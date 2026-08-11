# S10 — adversarial methodology review

Written against `METHODOLOGY.md` (2026-08-02), the frozen protocol scripts, and the
published literature on LLM-vocabulary detection. Every number quoted below was
recomputed from the study's own data files; where a claim did not reproduce, it was
dropped. Findings are grouped by whether they survive the study's own defences.

---

## 1. Verdict

The central result survives. AI-style vocabulary rose relative to frequency-matched
comparison vocabulary in four parliaments, the effect is present under every
specification that removes a known artifact, and the corpus engineering — translation
exclusion, chair-speech exclusion, within-speaker restriction, speech-clustered
bootstrap — is better than anything in the published literature on this question. But
the paper is **not defensible as written**, for three reasons that need action before it
goes anywhere near a reviewer. First, §6's "mechanism prediction test" — the defence
the document itself calls the strongest — is dead: the word-level AI-preference score is
93% a Hansard-rarity index, and once the word's own pre-period frequency is partialled
out the correlation is −0.008. Delete it or rebuild it on paired data. Second, and this
is the single biggest exposure, the primary statistic **cannot distinguish the Kobak
style list from Kobak's own biomedical *content* list** in two of three confirmatory
chambers (Canada +0.282 content vs +0.210 style). That control is the canonical
topic-churn negative control in this field, the study has the file, and it never runs
it. The cause is benign — zero-count smoothing — and the fix (restrict to words present
in both periods) makes the specificity story *stronger*, with content words going
sharply negative everywhere. But a hostile reviewer who runs it first will conclude the
instrument is not an instrument, and they will be entitled to. Third, the headline
effect sizes shrink under the corrected specifications: "+0.218 to +0.272, consistent
magnitude across parliaments" becomes roughly +0.10 to +0.19, and the 7.5% New Brunswick
prevalence is a lower bound over a five-month window, not a corpus rate. None of that
reverses a conclusion. All of it changes what the paper is allowed to say.

---

## 2. How this compares to published practice

| Methodological choice | What S10 does | Closest published practice | Assessment |
|---|---|---|---|
| **Instrument source** | Imports Kobak's 407 style-annotated words wholesale; external, pre-registered by publication date | Kobak, González-Márquez, Horvát & Lause (*Sci Adv* 11(27):eadt3813, 2025) derive theirs from 15M PubMed abstracts by excess-mortality-style extrapolation; Liang et al. (COLM 2024) deliberately *learn* the vocabulary per venue "to minimise design biases stemming from vocabulary selection" | **Better than average.** Importing is the stronger anti-p-hacking move. But cite it correctly (§4, F11) and disclose that these 407 are the 2013–24 annotation, not the 2024 excess list |
| **Estimand** | Equal-weight mean of per-token log fold-change | Kobak's unit is *document containment*: p(w) = (#abstracts containing w + 1)/(#abstracts + 1), aggregated as Δ_G = observed − expected fraction of abstracts containing ≥1 group word. Gray (arXiv:2403.16887) uses the equal-weight mean of fold-changes S10 actually uses | **Defensible but mis-lineaged.** The design is Gray's, not Kobak's — credit him. Kobak's estimand is what licenses "13.5% is a lower bound"; a token-rate mean has no prevalence reading, which is why §8 can claim consistency but not magnitude |
| **Pseudocount** | +0.5 on both numerator and denominator, but with *different* denominators (W_pre ≈ 2×W_post) | Kobak's +1 sits on a common denominator, so a word absent in both periods contributes exactly 0. His counterfactual is additionally floored at q ≥ p₋₂ to stay conservative | **Anti-conservative in the direction of the hypothesis.** Worth up to 31% of the UK's raw primary and it is what breaks the content-word control |
| **Null distribution** | 1,000 frequency-matched random placebo instruments drawn from raw corpus vocabulary | Yakura et al. (arXiv:2409.01754) build the synthetic-control donor pool deliberately — top-50k word2vec vocabulary minus the K=20 nearest semantic neighbours, restricted to the central band of the GPT score — and report four alternative donor specifications, in the tradition of Abadie, Diamond & Hainmueller (*JASA* 2010). Gray and Matsui hand-build control sets | **The best-designed part of the study, but under-specified.** Nobody else draws controls at random from the whole type inventory. Frequency matching is a real advance on Gray; dispersion matching is the missing second axis (F2) |
| **Dispersion** | Not controlled in the placebo pool (it *is* controlled in the formality axis) | Corpus linguistics treats dispersion as co-equal with frequency in keyness: Gries (*IJCL* 2008), Egbert & Biber (*Corpora* 2019) show frequency-only keyness selects bursty topic words | **Real gap.** The study knows the fix — it wrote it for the formality control and did not port it |
| **Frequency-dependence of the effect measure** | Log fold-change, unregularised; rare words get the largest swings | Monroe, Colaresi & Quinn (*Political Analysis* 16(4), 2008) is the canonical treatment: raw log-odds is dominated by low-frequency variance, hence their informative-Dirichlet z-score. Gray concedes his markers are "more volatile given the smaller numbers involved" | **The known failure mode of this statistic.** It is why F1's predictor is a rarity index and why F4's absent words behave the way they do |
| **Significance** | Placebo permutation, p < 0.001 in each chamber, combined by Fisher to 2.4 × 10⁻⁷ | Kobak reports **no** p-values, CIs or permutation tests at all. Yakura reports rank-based placebo p's (0.010 for *delve*) and states the donor-pool resolution. Gray reports none | **S10 is the only study here leading with a 10⁻⁷.** §2.4 discloses the bound honestly; §8 then quotes it to two significant figures. Report the standardised effect instead |
| **Time resolution** | One ratio pooled over 2024–2026 | Geng & Trotta (arXiv:2502.09606) show *delve* collapsing from early 2024 while other ChatGPT-favoured words keep rising; Kobak fixes a single target year; Yakura fits monthly trajectories with change-points | **No published study pools 2.5 post-years.** With Canada's post window 49% 2024 and Ireland's 31%, the cross-chamber comparison is across different mixtures (F8) |
| **Detector calibration** | Se = 40/40 on unedited Mistral-7B output, Sp = 243/243 + 60/60 × 3 chambers; Rogan–Gladen (*Am J Epidemiol* 1978) correction | Liang et al. (ICML 2024) validate the estimator on whole placebo corpora at ground-truth α = 0 and quote the resulting error band (<1.8% in-distribution, <2.4% OOD) as the margin of error; they also ran the proofreading arm and found lightly-edited text yields only a slight, non-significant α rise. Dugan et al. (RAID, ACL 2024) show detector performance collapsing under light adversarial edits | **Specificity work is exemplary and exceeds published practice. Sensitivity work does not exist for the class of text the study argues dominates.** Published evidence says Se on edited text is materially lower |
| **Prevalence framing** | "7.5% of the corpus" | Liang et al. make the reference population explicit and venue-and-window specific by construction | **Overclaimed.** The frame is 3,998 segments from five sitting months on the steep part of the ramp (F4) |
| **Interference / SUTVA** | Never stated | Standard requirement since Rubin (1980); Hudgens & Halloran (*JASA* 2008) for partial interference. §5.2 measures the violation directly | **Two sentences missing.** The direction is conservative, so writing it down is free strengthening (F12) |
| **Measurement validation** | Multiple independent instruments, adversarially-chosen specificity set, blinded quality codings anchored on Steenbergen et al. (2003) | Grimmer & Stewart (*Political Analysis* 2013): "validate, validate, validate" | **Above field standard.** This is the part of the study that should be foregrounded |

---

## 3. Findings that stand

Ordered by severity. Each was reproduced from the study's own files.

### F1 — FATAL. §6's mechanism prediction test is a shared-denominator artifact

**The attack.** `ai_pref_prediction.py` line 78 computes the predictor as
`pref = log[(syn+0.5)/syn_w ÷ (ctl+0.5)/ctl_w]` — the word's rate in a 6,837-word
synthetic corpus against its rate in the 2019 Hansard control — and line 79 computes the
outcome as `shift = log[(post+0.5)/post_w ÷ (pre+0.5)/pre_w]`. The 2019 control is a
*subset* of the 2018–22 pre window. So the word's Hansard rarity is inside both the
predictor and the outcome, with the same sign, and the correlation is mostly that.

**Reproduced (n = 89, from `ai_pref_prediction.csv`):**

| quantity | Spearman |
|---|---|
| `ai_pref` vs `shift` (the published claim) | **+0.548** |
| `ai_pref` vs −log(2019 control count) | **+0.9233** |
| `ai_pref` vs actual synthetic-corpus count | **−0.2337** |
| `shift` vs −log(pre count) | +0.6122 |
| log(2019 ctl count) vs log(pre count) | +0.9803 |
| **partial `ai_pref` vs `shift`, controlling log(pre count)** | **−0.0082** |

("Partial correlation" = the correlation that remains after the shared driver is
statistically removed from both variables.) The predictor correlates *negatively* with
the actual synthetic evidence it is supposed to encode. The permutation test at lines
89–91 shuffles globally, which destroys the frequency structure and therefore cannot see
the confound; shuffling *within* pre-frequency quintiles over 10,000 draws gives
p = 0.262.

**Published anchor.** Geng & Trotta (arXiv:2404.08627) measure the per-word AI-induced
change rate on **paired** data — the same real abstracts before and after a GPT-3.5
rewrite — so baseline frequency cancels. Yakura et al. do the same: their GPT score is a
median word-level log-odds ratio between human texts and *their own* GPT-edited
counterparts. Monroe, Colaresi & Quinn (2008) is the general statement of why unpaired
log-odds on rare words measures rarity.

**What it threatens.** §6 defence 3 in full — the only word-level mechanism evidence in
the study, and the defence §6 explicitly ranks strongest. It threatens nothing else: the
§2.5 placebo primary is independently frequency-matched and is untouched.

**Cheapest fix.** Take ~200 real pre-2023 segments, have the generator rewrite them, and
score `log[rate in rewrite / rate in the same original]`. Baseline cancels, as in Geng &
Trotta. One rewrite pass. Until then, delete the claim — reporting +0.548 alongside a
partial of −0.008 is not a defence, it is an admission.

---

### F2 — MAJOR. The placebo pool is frequency-matched but not dispersion-matched

**The attack.** `run_protocol.py` lines 71–76 build the placebo pool from raw
`pre_c.items()` with only length, alphabetic and top-120-frequency filters.
`formality_axis.py` lines 101–104 apply a sitting-date dispersion floor and a
proper-noun filter — the study documented that unfiltered parliamentary word draws return
*hessle, mcdonagh, broxbourne, smokers, circuses*, and fixed it **for the formality
control only**. A pool full of bursty topic words decays faster than general vocabulary
between the pre and post windows, which lowers the placebo median and inflates every
excess.

**Reproduced.** Matching dispersion word-for-word the way frequency already is
(log₂-sittings bin × log₂-frequency bucket, nearest-cell fallback):

| chamber | excess as published | excess, dispersion-matched | p |
|---|---|---|---|
| New Brunswick | +0.554 | **+0.490** | 0/1000 |
| UK Commons | +0.257 | **+0.187** | 0/1000 |
| Dáil Éireann | +0.224 | **+0.150** | 0/1000 |
| Canada Commons | +0.218 | **+0.123** | 0/1000 |

**All four remain p = 0/1000.** (A cruder version of this fix — importing
`formality_axis.py`'s floor, which is the *median of the instrument's own* dispersion —
drops Canada to p = 0.051, but that filter over-corrects: it would make every placebo
word more topic-general than half the instrument's words. It exists in the formality
axis because the long-vs-short criterion actively selects topic words; a random
frequency-band draw does not.)

**Published anchor.** Gries (*IJCL* 2008) and Egbert & Biber (*Corpora* 2019) on
dispersion in keyness; Yakura's four alternative donor specifications as the model for
reporting more than one null.

**What it threatens.** §8's "excess +0.218 to +0.272 → consistent magnitude across
parliaments" must become roughly **+0.12 to +0.19**. Significance is untouched.

**Cheapest fix.** Add dispersion as a second matching axis in `run_protocol.py`, rerun
four chambers (~10 min each), report both nulls side by side.

---

### F3 — MAJOR. Kobak's content words — the field's canonical negative control — are never run, and the primary fails them

**The attack.** §2.1 says "we use style only, so biomedical topic words cannot leak in."
That is an argument, not a test. Kobak's team hand-annotated all 900 excess words
content-vs-style **blinded to year**, precisely so the two could be separated; their own
validation is that 2020–22 excess vocabulary was almost entirely content (*coronavirus*,
*lockdown*) while 2024's was almost entirely style. The 462 content rows are sitting in
`kobak_excess_words.csv`. No script in `analysis/s10/` touches `type == "content"`.

**Reproduced — full-list primary, content words against their own frequency-matched
placebos:**

| chamber | style excess | **content excess** | content p |
|---|---|---|---|
| UK | +0.2531 | **+0.2720** | 0/1000 |
| Canada | +0.2102 | **+0.2816** | 0/1000 |
| Ireland | +0.2170 | +0.2027 | 0/1000 |
| New Brunswick | +0.5543 | +0.3966 | 0/1000 |

As specified, the primary statistic cannot distinguish LLM style vocabulary from
PubMed's 2024 *content* vocabulary in a Canadian legislature.

**Why it happens, and why the fix strengthens the paper.** Content words are biomedical
jargon largely absent from Hansard — only 142 of 462 appear in both New Brunswick
periods — and each absent word draws the constant positive smoothing artifact of F4.
Restrict both sides to words present in both periods (placebo pool likewise restricted)
and the instrument discriminates decisively:

| chamber | style excess | style p | **content excess** | content p |
|---|---|---|---|---|
| New Brunswick | +0.2989 | 0/1000 | −0.0766 | 910/1000 |
| UK | +0.1724 | 0/1000 | −0.3175 | 1000/1000 |
| Ireland | +0.1261 | 0/1000 | −0.4132 | 1000/1000 |
| Canada | +0.0963 | 3/1000 | −0.5942 | 1000/1000 |

That is a clean specificity result and it is currently unpublished.

**What it threatens.** The credibility of the instrument, if a reviewer runs it first.

**Cheapest fix.** Make present-in-both the **primary** specification, not §3's side
check, and report the content list as a pre-registered negative control in every
chamber. The numbers already exist.

---

### F4 — MAJOR. The New Brunswick prevalence figure is not a corpus rate, and §5 names the wrong stratifier

**The attack.** Two separate errors in one sentence of §5.

*Frame.* `make_pangram_batch.py` line 42 reads `segments_all.jsonl`, which holds 4,583
scoreable segments: 585 from 2019 plus exactly 2025-10 (828), 2025-11 (820), 2025-12
(791), 2026-03 (816), 2026-05 (743) = 3,998 — matching `flag_rates.csv`'s "114/3998".
That is 10.6% of the 37,801-segment corpus, omits all of 2024 and January–September
2025, and sits on the steepest part of the ramp the document itself reports (1.2% in
2024 → 7.0% in 2025 → 11.0% in 2026).

*Stratifier.* Lines 59–63 read `fal = dets.get("falcon")` and rank by it — the Binoculars
detector §4.1 reports as having found nothing — and exclude segments already claimed by
the consensus stratum. §5 says "12-per-decile of the screen score." The realised verdicts
confirm the stratifier was flat: deciles 0–9 returned 0, 1, 1, 1, 1, 0, 1, 1, 1, 2 AI,
plus one Mixed in decile 0. So §4.4's "precision is monotone in score" describes a
different pool from the one the prevalence number came from.

**Published anchor.** Liang et al. (ICML 2024) make the reference population explicit and
validate on whole placebo corpora at α = 0, quoting the error band as the margin.

**Mitigating.** `PILOT.md` gets this right — "120 random 2025–26 segments, 12 per falcon-
score decile" — so this is a summarising regression in `METHODOLOGY.md`, and the point
estimate is unaffected by equal allocation over equal-sized deciles.

**Cheapest fix.** Restate as "7.5% [4.0–13.6] of New Brunswick segments in sittings from
October 2025 to May 2026"; correct §5 to say Falcon deciles; note that the decile design
degenerated to an effective simple random sample because the stratifier was uninformative.
Check §5.0b's cross-chamber table too — `ch_prevalence.py` samples the other three from
`POST_MIN = 2025-01-01`, a different window again. No new adjudication needed.

---

### F5 — MAJOR. Sensitivity was measured on exactly the class of text §4.1 concludes is absent

**The attack.** `se_segments.jsonl` is 40 texts, 6,837 words, median 181.5 words, from a
single generator (Mistral-7B-Instruct) at a single sampling config, unedited. §4.1
concludes the record contains "very little unedited paste." §5.1 says the vocabulary/
token-statistic scissors is "the signature of **edited or assimilated** AI." §8 row 4
then says the prevalence figure "needs no correction" while conceding in the adjacent
column that Pangram may not catch edited AI. Those three statements cannot all be true.

**Reproduced.** One-sided 95% Clopper-Pearson lower bounds ("the worst true rate
consistent with 40/40") are Se ≥ 0.9278 and Sp ≥ 0.9877. Propagating them individually
moves τ̂ from 7.50% to 8.08% and 6.35%; jointly, 6.98%. The reported [4.0–13.6] is the
binomial interval on 9/120 and propagates none of it. The one-sided risk is much larger:
at Se = 0.5, τ̂ = 15.0%; at Se = 0.3, τ̂ = 25.0%.

**Published anchor.** Liang et al. (ICML 2024) ran the identical robustness check and
published the answer — reviews merely *proofread* by ChatGPT yield only a slight,
non-significant rise in the estimate, i.e. the estimator undercounts light editing.
Dugan et al. (RAID, ACL 2024) show the same collapse under light edits across eight
detectors. This is direct published evidence that Se on the text S10 argues dominates
Hansard is below the Se it measured.

**What it threatens.** Not the direction — every correction runs toward *more* AI. It
threatens the framing: 7.5% has a defensible lower bound and no upper bound at all.

**Cheapest fix.** Delete "the correction is the identity" from §4.3 and rewrite §8 row 4
as "7.5% is a lower bound at Pangram's operating point, conditional on unmeasured
sensitivity to edited AI." Widen to roughly [3.0%, 14.8%] to include Se/Sp sampling
error. Properly: generate a light-edit tier of the same 40 speeches, à la Liang's
proofreading arm, and report Se separately for raw, edited and outline-expanded text.

---

### F6 — MAJOR. The frequency-weighted secondary does not replicate, and §6's sweep claim is wrong

**The attack.** §6 defence 2 says "a threshold sweep showing every cutoff from <1 to <50
per 100k gives p ≤ 0.008." That is a New Brunswick-only result, presented without a
chamber label, and misquoted: NB's <1/100k cell is **p = 0.015**. The sweep exists for
every chamber in the protocol JSONs and is reported for none of them.

**Reproduced, pooled-ratio p at <1 / <2 / <5 / <10 / <20 / <50 per 100k:**

| chamber | | | | | | |
|---|---|---|---|---|---|---|
| UK | 0.143 | 0.184 | 0.148 | 0.240 | 0.130 | 0.111 |
| Ireland | 0.207 | 0.146 | 0.083 | **0.047** | 0.069 | 0.136 |
| Canada | 0.137 | 0.332 | 0.195 | 0.274 | 0.489 | 0.916 |

One of eighteen confirmatory-chamber cells clears 0.05. Canada's <50/100k pooled ratio is
0.9385 — the AI-style vocabulary declined and the frequency-weighted null says that is
unremarkable. (Ireland's within-speaker run does better: 0.029, 0.024, 0.038.)

**Published anchor.** The frequency-weighted set-level aggregate is the *standard* here,
not the exception — Kobak's Δ_G is a document-prevalence aggregate, Liang's MLE pools
across the whole vocabulary. Gray's equal-weight mean is the one design whose own author
flags the markers as "more volatile given the smaller numbers involved."

**Mitigating.** §2.2 already tells the reader the pooled statistic is null in NB
("the *pooled* ratio in NB is 1.09 (p = 0.48, nothing)") and argues on the merits why
equal weighting matches the hypothesis. The design choice is defended; the sweep claim is
not.

**Cheapest fix.** Correct the NB figure to 0.015, label it New Brunswick, print the sweep
table for all four chambers, and state plainly that the frequency-weighted secondary does
not replicate — then make the Gray argument for equal weighting explicitly, rather than
letting the reader assume the two statistics agree.

---

### F7 — MAJOR. The data-defined formality control is not frequency-matched, and §3.1's vocabulary is a UK cherry-pick

**The attack.** §3.1 says "frequency-match them bucket-for-bucket to the instrument" and
never reports the realised sizes. `formality_axis.py` line 99 discards any candidate with
pre count < 200 — everything below log₂ bucket 7 — so the buckets holding most of the
instrument cannot be filled. Realised control sizes against the instrument's 407:

| run | n_control |
|---|---|
| New Brunswick | **67** |
| Canada within-speaker | 121 |
| Canada | 164 |
| Ireland within-speaker | 192 |
| Ireland | 201 |
| UK within-speaker | 187 |
| UK | 211 |

NB's instrument has exactly 67 words in buckets ≥ 7; buckets 0–3 hold 227 of 407. So the
control is systematically **more common** than the thing it controls — reintroducing
precisely the flaw Gray acknowledges and S10 claims to have fixed.

Two further problems. The showcased register vocabulary — *amends, movingly, poignant,
deficiencies, discourse, practicable* — is UK-only, and spans two UK runs (*practicable*
is UK-within-speaker). Ireland returns *dirty, terribly, visual, drove, toilet,
respondents, bread, inserts, peers, idir, bheith* (two untagged Irish-language tokens);
Canada *unceded, remiss, proponents, prima, facie, argued, artificial…*; NB *forests,
legislators, expertise, covered, constituency, argue*. The documented fix worked in one
chamber. And the study carries two mutually inconsistent baselines: formality-control
mean logFCs are +0.0271 (UK), +0.0131 (IE), +0.0025 (NB), −0.1035 (CA), so under that
baseline the cross-chamber effects are +0.088 / +0.052 / +0.090 — not +0.218 to +0.272.
§2.5's headline uses the more favourable one.

**Mitigating.** Both baselines are reported — §3.1's gap table and the progress report's
"vs formality control" column carry the smaller numbers. Nothing is hidden. What is
missing is the realised match table, the other chambers' words, and any reconciliation.

**Cheapest fix.** Lower the candidate floor to pre count ≥ 20, or sample within bucket
with replacement until each quota fills, so n_control = 407 everywhere; print the realised
bucket-match table; show all four chambers' top control words; pick one baseline for the
headline excess or report both columns.

---

### F8 — MAJOR. A single ratio pooled over 2024–2026 is not a stable estimand

**The attack.** The marker set is known to be non-stationary inside that window, and the
chambers weight the post years very differently. Post-period word counts by year:

| chamber | 2024 | 2025 | 2026 | 2024 share |
|---|---|---|---|---|
| Canada | 5.46M | 2.94M | 2.73M | **49%** |
| UK | 8.34M | 10.11M | 5.70M | 35% |
| Ireland | 5.85M | 7.39M | 5.42M | 31% |
| New Brunswick | 0.86M | 1.25M | 0.34M | 35% (2026 only 14%) |

**Reproduced — per-year primary against each chamber's own 2018–22 baseline:**

| chamber | 2024 | 2025 | 2026 |
|---|---|---|---|
| Canada | **−0.0361** | +0.0987 | +0.0896 |
| Ireland | +0.1664 | +0.1711 | +0.1789 |
| UK | +0.1954 | +0.1959 | +0.1613 |

Canada is the weakest chamber substantially because half its post words are 2024. That is
a sufficient alternative to any national explanation, and §8 row 2 rests the cross-chamber
comparison on a quantity computed over different mixtures.

**Published anchor.** Geng & Trotta (arXiv:2502.09606) show *delve* dropping sharply from
early 2024 once the press named it, while other ChatGPT-favoured words keep rising. Kobak
fixes a single target year; Yakura fits monthly trajectories with change-points. No
published study in this area pools 2.5 post-years into one ratio.

**Qualification.** The effect is present in every post year in three of four chambers, so
the "extreme markers decaying while ambient ones rise" story is not doing much work here.
And per-year splits mechanically inflate later years through the zero-count term (smaller
W_post) — see F9.

**Cheapest fix.** Report the primary as a per-year series in every chamber (the code
produces it almost free) and disclose the post-year mixture in the cross-corpus table.

---

### F9 — MINOR. Zero-count smoothing is asymmetric between instrument and placebo

**The attack.** Because W_pre ≈ 2 × W_post everywhere, a word absent from *both* periods
still scores a positive constant: +0.5803 (NB), +0.5923 (Canada), +0.6706 (UK), +0.6760
(Ireland). Instrument words absent from both: 30 NB, 22 UK, 19 IE, 8 CA — contributing
11% of NB's +0.3791 raw primary and 31% of the UK's +0.1155.

**Mitigating — the study already checks this.** `PILOT.md` has it under "Robustness:
absent-word smoothing does not drive the cross-corpus gap," with the same table, and
§3 summarises it. Two gaps remain. It covers 2 of 4 chambers. And "essentially unchanged"
holds for the raw primary but not the excess (NB +0.554 → +0.299, UK +0.253 → +0.172).

**The genuinely new part.** The *placebo-side* asymmetry is uncovered. `run_protocol.py`
line 73 iterates `pre_c.items()`, so bucket 0 is empty by construction and `pool_for(0)`
falls through to bucket 1 — placebo words with pre count 1, whose expected logFC is about
−0.43 in the UK. The per-word gap between an absent instrument word and its matched
placebo is therefore ~1.1 log units, structurally, before any AI exists. This is the
mechanism behind F3.

**Published anchor.** Kobak's pseudocount sits on a common denominator, so an absent word
contributes exactly zero; his counterfactual is additionally floored to stay conservative.

**Cheapest fix.** Subsumed by F3: make present-in-both primary. Report the absent-word
count per chamber either way, and extend the PILOT check to all four.

---

### F10 — MINOR. The estimand silently departs from Kobak's, forfeiting the lower-bound reading

**The attack.** Kobak's unit is document containment, and Δ_G — observed minus expected
fraction of abstracts containing ≥1 group word — is what licenses "13.5% is a lower
bound." An equal-weight mean of per-token logFC has no prevalence interpretation at all,
which is why §8 can support "consistent magnitude" but not "that it is large." Adding
the Kobak estimand as a parallel primary (fraction of *turns* containing ≥1 style word,
observed minus placebo-expected) is cheap and yields a number a reader can act on.
Separately, credit Gray for the equal-weight-mean design and Matsui for the control-set
idea, and position the frequency-matched placebo as the extension of both.

**What does *not* stand in this attack.** §2.1 is titled "The instrument, and why it must
be external" and claims Kobak only for the word list; §2.2 justifies equal weighting on
independent grounds and never attributes it to Kobak — so "silently changes the estimand"
overstates. "One verbose member repeating *crucial* forty times" is what the
speech-clustered bootstrap exists for. And "declines to produce a percentage" is simply
false: §5 produces prevalence percentages and §5.0b explicitly warns against fusing them
with the lexicon.

---

### F11 — MINOR. The instrument citation is wrong in both the methodology and the frozen protocol

**Verified externally.** The fourth author is **Jan Lause**, not Berens — Berens is the
lab (`github.com/berenslab/llm-excess-vocab`), which is where the name appears to have
come from. The published version is **Kobak D, González-Márquez R, Horvát E-Á, Lause J,
*Science Advances* 11(27):eadt3813 (2025)**, and it is not cited. Both §2.1 and
`replication_protocol.md` carry the error, so it will propagate.

**Scope.** The repository README describes `results/excess_words.csv` as "the 900 excess
words that we identified from 2013 to 2024," and the local copy has exactly 900 rows
(462 content, 407 style, 24 content/style, 4 other, 2 style/content, 1 style/count). The
407 style words are therefore the **full 2013–24 annotation**, not the 2024 excess-style
list (379 items / 343 lemmas). §2.1's "flag words whose 2024 usage exceeds their own
counterfactual" describes the 2024 subset, not what is being used.

**Where the attack overreaches.** This is bibliographic, not substantive. Kobak's design
flags a *break* from an extrapolated trend, not a steady rise, so a style word flagged
excess in 2013–17 has its break priced into the 2018–22 pre-window, and one flagged in
2018–22 raises the pre baseline and *shrinks* the measured logFC. The contamination
direction is mostly conservative.

**Cheapest fix.** Correct the citation everywhere; add one sentence on scope; run the
2024-only subset as a robustness check. A larger effect there would be a strengthening.

---

### F12 — MINOR. No-interference is never stated, even though §5.2 measures the violation

**The attack.** Grep across `METHODOLOGY.md`, `PILOT.md` and `replication_protocol.md`
returns no occurrence of SUTVA, interference, spillover or no-anticipation. ("SUTVA" =
the assumption that one unit's treatment does not affect another unit's outcome — here,
that AI writing does not change how *non-AI* words are used.) The placebo pool has no
semantic exclusion at all: only the instrument's own words, the top 120 frequency words,
and length/alpha filters. Meanwhile §5.2 measures the violation directly — rare-Kobak
per 100k rising 213.7 → 264.8 in text the screen rates *least* AI-like — and the
formality control is built to be maximally register-similar, i.e. maximally exposed.

**Why writing it down helps.** Treated controls bias the estimate *toward* the null, so
every reported effect is conservative under permeation. Stating that converts an unstated
vulnerability into a strengthening, in one paragraph. Optionally add a semantic-neighbour
exclusion to the placebo pool, as Yakura does with K = 20 word2vec neighbours.

---

## 4. Attacks that failed

Answer these in review; they are already covered.

**"Canada's significance is an artifact of placebo contamination."** No. Under
like-for-like dispersion matching Canada stays at p = 0/1000 (excess +0.123). The version
that drops Canada to p = 0.051 imposes the *instrument's median* dispersion on the
placebo pool, which makes every placebo word more topic-general than half the
instrument's own words — the mirror image of the bias being alleged. F2 is about effect
size, not significance.

**"The primary statistic can't tell LLM style from biomedical topic churn, so the whole
study is topic drift."** Only under the smoothing-contaminated specification. Restricted
to words present in both periods, content words go to −0.077 (NB, p = 910/1000), −0.318
(UK), −0.413 (IE), −0.594 (CA, p = 1000/1000) while style stays positive at p ≤ 0.003
everywhere. The specificity result is strong; it just isn't published yet.

**"p = 2.4 × 10⁻⁷ is arithmetic, not data."** Mostly wrong, and the document already
concedes the part that is right. `cross_corpus.py` line 60 does substitute
`1.0 / n_placebo` for zero counts, so X² = 41.4465 comes from three copies of 0.001, and
10,000 draws would give 4.10 × 10⁻¹⁰ while 100 would give 1.10 × 10⁻⁴. But §2.4 is
titled "What 'p < 0.001' means here" and says exactly this; `fisher()`'s docstring says
"ps may contain conservative bounds"; §2.5's table reports every chamber as "< 0.001."
And *which* chambers hit the resolution floor, and that NB's real value is 4× the most
extreme of 100,000 draws, are facts about the data. Residual: §8 should not quote a
bounded quantity to two significant figures. Report the standardised effect — real minus
placebo median, in placebo SDs — as the headline and let the p-value be a footnote.

**"Smoothing manufactures the gap."** Already checked in `PILOT.md`; the present-only
restriction *widens* the NB and UK raw gaps. Only the placebo-side half of F9 is new.

**"The equal-weight statistic is the wrong choice / an analyst degree of freedom."**
§2.2 defends it on the merits and it is Gray's published design. The real problem is
F6 — that the frequency-weighted alternative disagrees and this is not reported — not
the choice itself.

**"A few verbose speakers drive the result."** Covered by the speech-clustered bootstrap
(resampling whole turns), with per-chamber CIs in the protocol JSONs.

**"The study never produces a prevalence percentage."** False. §5 does, from a calibrated
detector, and §5.0b explicitly refuses to fuse it with the lexicon.

**"The 2013–24 instrument scope inflates the effect."** Wrong direction. Words whose
excess break falls inside the 2018–22 pre-window raise the pre baseline and shrink the
measured logFC.

**"Prevalence sampling was botched."** The design is sound and `PILOT.md` describes it
correctly; F4 is a summarising error in `METHODOLOGY.md` plus an over-broad estimand
label, not a sampling defect. The point estimate stands for its actual window.

---

## 5. What a reviewer would demand before publication

Prioritised. Items 1–4 are blocking.

1. **Delete or rebuild §6 defence 3.** A paired-rewrite preference score (~200 segments,
   one generator pass) or nothing. Reporting +0.548 without the −0.008 partial is not
   survivable.
2. **Make present-in-both the primary specification and publish the content-word negative
   control in all four chambers.** This is the single highest-value change in the list:
   it removes the smoothing artifact, defeats the topic-churn objection outright, and
   costs one rerun.
3. **Add dispersion matching to the placebo pool** and restate §8's magnitude claim as
   roughly +0.12 to +0.19. Report both nulls.
4. **Relabel the prevalence numbers.** "7.5% of New Brunswick segments in sittings from
   October 2025 to May 2026, a lower bound at Pangram's operating point." Fix "screen
   score" → "Falcon deciles." Delete "the correction is the identity" from §4.3 and
   rewrite §8 row 4. Widen the interval to include Se/Sp sampling error.
5. **Report the primary as a per-year series** (2024 / 2025 / 2026) in every chamber and
   disclose the post-year word mixture in the cross-corpus table.
6. **Publish the pooled-ratio sweep for all four chambers**, correct NB's <1/100k cell to
   p = 0.015, and state that the frequency-weighted secondary does not replicate.
7. **Fix the formality control:** lower the candidate floor so n_control = 407, print the
   realised bucket-match table, show all four chambers' top control words, and reconcile
   the two baselines.
8. **Correct the Kobak citation** (Lause, not Berens; *Sci Adv* 11(27):eadt3813) in
   `METHODOLOGY.md` and `replication_protocol.md`; note the 2013–24 scope; run the
   2024-only subset as a robustness check.
9. **Add the Kobak document-prevalence estimand as a parallel primary** — fraction of
   turns containing ≥1 style word, observed minus placebo-expected — so the study has one
   number with a lower-bound interpretation.
10. **Write down the no-interference assumption** and note that §5.2's permeation result
    makes every estimate conservative.
11. **Replace the Fisher headline** with a standardised effect (real minus placebo median,
    in placebo SDs) and demote the p-value.
12. **Credit Gray (arXiv:2403.16887) for the equal-weight-mean design and Matsui for the
    control-set idea**, positioning the frequency-matched, dispersion-matched placebo as
    the extension of both. The paper's own convention is to build on published work rather
    than argue novelty, and here the extension is genuinely an improvement on both.
