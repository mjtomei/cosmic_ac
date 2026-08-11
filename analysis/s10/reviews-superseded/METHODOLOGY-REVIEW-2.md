# S10 — round-2 adversarial review

**Written against `METHODOLOGY.md` as of 2026-08-03, after the round-1 fixes.**
Round-1 findings and the responses to them are not re-litigated; everything
below is either new, or is a round-1 fix that created a new problem. Every
number quoted was re-derived from the study's own data and scripts by an
independent verification pass; where the verification disagreed with the
attack, the review says so and the attack is downgraded or moved to §4.

Findings are numbered R2-1 … R2-18.

---

## 1. Verdict

**The lexicon arm is not yet defensible, and the reason is that the repaired
null has never been tested on data where the effect cannot exist.** Run the
v1.1 protocol unchanged on pre-LLM windows and it returns UK +0.127, Dáil
+0.117, New Brunswick +0.130 at p ≤ 0.001 — against real v1.1 effects of
+0.121, +0.080 and +0.278. A frequency-and-dispersion-matched placebo controls
for level and burstiness and controls for nothing about *trend*, and this
vocabulary has a secular upward trend in parliamentary English. Until that is
answered, §2.6's heading — "what the effect looks like with the null repaired"
— is the sentence that invites a referee to run the test that ends the arm.
The permeation arm is in worse shape for a duller reason: it was never re-run
under v1.1 at all, and when it is, its three headline claims invert. The
prevalence arm is in good order and is now the strongest part of the study;
§4.3's refusal to manufacture a sensitivity figure is exactly right and should
be kept verbatim. The document's honesty conventions are working — every fatal
finding below was findable *because* the document reports its own corrections
— but the corrections were applied to six of forty-nine protocol invocations
and the study is now a mixture of two protocols with no version labels.

---

## 2. Defects introduced by the round-1 fixes

There are seven, and they share one cause. The v1.1 protocol was written as a
new script rather than as a change to the frozen one, and then wired into two
places. `grep -oh "run_protocol[a-z0-9_]*\.py" *.sh` returns **43 calls to
`run_protocol.py` and 2 to `run_protocol_v11.py`**. Everything in §5.2, §6 and
§3 is still v1.0 output sitting in a document whose §2.6 says v1.0's null was
defective. A reader cannot tell which table is which, because no table carries
a protocol label except §2.6's.

| # | fix | defect it introduced | severity |
|---|---|---|---|
| R2-2 | v1.1 (both fixes) applied to 6 chamber runs only | the permeation arm is v1.0; under v1.1 its three headline claims invert | fatal |
| R2-4 | F8's per-year series | year cells are size-confounded and 2026 is a partial year in all six chambers | major |
| R2-5 | v1.1 dropped v1.0's clustered bootstrap | no v1.1 effect size in the document has an interval on it, and §2.6 states a range anyway | major |
| R2-6 | F5a obviated by deleting its corpus | §8 still licenses "the prevalence figure needs no correction" from the deleted corpus's Se = 40/40 | major |
| R2-11 | F8's per-year series | written as a separate script with a *different* corpus filter, so §2.6 and §2.6a are different experiments in NB | minor |
| R2-13 | fix 1 (present-in-both) | the realised instrument is now corpus-dependent (335–384 of 407 words), which is the property §9 sells as the guarantee against fishing | minor |
| R2-15 | fix 2 (dispersion) | NB's placebo median flips from −0.175 to **+0.116**, falsifying §3's "every placebo draw negative" and §2.5's "the null is not centred on zero — placebo sets drift by −0.14 to −0.25" | minor |

Two more are bookkeeping rather than defects but belong in the same list: the
v1.0→v1.1 fix-cost is computed across a changing chamber set (R2-7), and v1.1
made a third, undeclared change to the placebo pool (R2-16). Both are in §3.

The pattern worth naming: **fixing by deletion leaves dangling citations, and
fixing by new script leaves protocol mixtures.** Round 1 used both. The
cheapest structural repair is to make `run_protocol_v11.py` *the* protocol,
re-run all 49 invocations, and version-label every table in the document.

---

## 3. Findings that stand

### FATAL

#### R2-1 — the repaired null has never been run in time, and it fails when it is

**Attack.** §2.3's placebo matches each instrument word to a random word in
the same pre-period frequency band and (since v1.1) the same dispersion band.
That controls level and burstiness. It does not control *trend*: if the Kobak
style vocabulary has been drifting up in parliamentary English since before
ChatGPT existed, every matched placebo will under-shoot it and the excess will
be positive with a small p, forever. The standard test for exactly this is an
**in-time placebo** — run the identical estimator on a pre-treatment window
pair, where the treatment effect is known to be zero (Bertrand, Duflo &
Mullainathan, QJE 119(1), 2004, §V). Grepping `METHODOLOGY.md` and
`REVIEW-RESPONSES.md` for `falsif`, `pre-AI`, `placebo-in-time` returns only
detector-specificity rows. The lexicon arm has no such test anywhere.

**What it returns.** Verified against an independent reimplementation of v1.1
that reproduces `v11_ca_v11.json` to five decimal places:

| window pair | NB | UK | Dáil | Canada | US House | US Senate |
|---|---|---|---|---|---|---|
| pre 2018-19 / post 2021-22 | **+0.130** *(p<0.001)* | **+0.127** *(p<0.001)* | **+0.117** *(p=0.001)* | +0.044 n.s. | +0.000 n.s. | +0.019 n.s. |
| pre 2018 / post 2022 | **+0.165** | **+0.086** *(p=0.001)* | **+0.145** *(p<0.001)* | +0.017 n.s. | +0.008 n.s. | **+0.100** *(p=0.002)* |
| **real v1.1 (2018-22 / 2024-26)** | **+0.278** | **+0.121** | **+0.080** | +0.029 n.s. | **+0.104** | −0.036 n.s. |

Ireland's real effect is *smaller* than both of its own pre-LLM baselines. The
UK's real effect is 95% of one of them. NB's is 1.7–2.1× its baselines. Only
the US House shows a real effect against a pre-LLM baseline of essentially
zero, and the US Senate is the only chamber that moved in the pre-LLM window
and then stopped.

**This is not an estimator artifact.** An odd/even split of sitting dates
*within* 2018–22 — same era, no time gap, so any excess is pure estimator bias
— gives UK +0.011 (p=0.242), Dáil +0.029 (p=0.058), Canada +0.006, US House
−0.020, US Senate +0.024. Bias in the large chambers is 0.01–0.03. The
+0.09–+0.17 excesses above are mostly real secular trend. (New Brunswick is
the exception: +0.093 with no gap, which is its own separate problem — see
R2-12.)

**What it threatens.** Every p-value in §2.5 and §2.6, the Fisher combination,
the per-year series in §2.6a, the formality control in §3.1, and the permeation
strata in §5.2 — all of them are the same statistic against the same null.

**What it does *not* establish.** The attack's "net of baseline, only the US
House survives" arithmetic is not valid. The placebo windows are 1–2 years
against the real design's 5-year pre and 2.5-year post, window size
demonstrably moves this statistic (R2-5), and both placebo post-windows sit on
the COVID peak, which the study elsewhere shows moves this vocabulary hard
(REVIEW-RESPONSES F3: *coronavirus* −4.63, *quarantine* −4.58). The honest
statement is that the null is unvalidated in the one direction that matters,
not that the effects are zero.

**Cheapest fix.** Adopt Kobak's own counterfactual instead of a matched
placebo: q = p₋₂ + 2·max{p₋₂ − p₋₃, 0}, computed on a rolling baseline
(Sci. Adv. 11(27):eadt3813, §4.2–4.3 — "q was always at least as large as
p₋₂ … resulting in conservative estimates"). By construction it cannot score a
rising pre-trend as excess, and it is the design the instrument was built
under. Failing that, add trend as a third matching axis (match each placebo
word on its own 2018→2022 logFC as well as frequency and dispersion) and
report every chamber net of its own in-time placebo. **Either way, publish the
in-time placebo table.** A referee will run it in fifteen lines, and a study
that reports it first is in a completely different position from one that
didn't.

---

#### R2-2 — the entire permeation arm is v1.0, and it inverts under v1.1

**Attack.** `permeation_run.sh`, `unscripted_run.sh`, `trim_ew_run.sh`,
`split_half_run.sh` and `speaker_shift_run.sh` all invoke `run_protocol.py`.
Only `us_full_pipeline.sh` invokes v1.1. So §5.2a, §5.2b and §5.2c are computed
under the null §2.6 says was defective, in a document that reports both.

**What v1.1 returns.** Re-run on the study's own stratum files (every figure
reproduces the v1.0 numbers to within 0.003 before the switch, so this is the
same pipeline):

| stratum | v1.0 | **v1.1** | v1.1 p |
|---|---|---|---|
| Canada unscripted (Oral Questions) | +0.287 | **−0.058** | 0.900 |
| UK unscripted | +0.289 | **−0.046** | 0.892 |
| Ireland unscripted | +0.362 | **+0.037** | 0.147 |
| Canada short | +0.312 | **−0.027** | 0.768 |
| Canada long | +0.221 | +0.041 | 0.066 |
| Canada prepared (Statements by Members) | +0.405 | +0.081 | 0.013 |
| UK short | +0.299 | +0.072 | 0.005 |
| UK long | +0.267 | **+0.128** | — |
| Ireland short | +0.378 | +0.060 | 0.034 |
| Ireland long | +0.214 | **+0.080** | — |

**Three claims die.** (a) §5.2d Claim 1 — "it appears in speech that could not
have been drafted" — **no unscripted stratum is significant under v1.1 and two
are negative.** (b) §5.2a's headline, "the two columns run in opposite
directions in all three chambers," **inverts in all three**: long now exceeds
short everywhere (UK +0.128 vs +0.072, Ireland +0.080 vs +0.060, Canada +0.041
vs −0.027). (c) §5.2c's Canadian ladder becomes **monotone in scriptability**
— prepared +0.081 > long +0.041 > short −0.027 > unscripted −0.058 — which is
the drafting story, cleanly, in the chamber the document itself calls "the
sharpest test."

**What it threatens.** §3.0's framing of SUTVA violation as "the study's most
interesting finding"; §5.2d's two-mechanism synthesis; §5.2's entire
dose-response argument. §5.2b's split-half result is untouched in kind but is
also v1.0 and must be re-run.

**Cheapest fix.** Re-run the five shell scripts against `run_protocol_v11.py`
and rewrite §5.2 from the output. Be ready for the answer to be "the
permeation arm does not survive the corrected null, and what survives is a
drafting gradient" — which is a publishable result, just not the one currently
written. **Deletion of §5.2a and §5.2c as currently written is on the table
and is defensible.** §5.2e (Burrows Delta, monoculture) does not use this
protocol and is unaffected.

---

#### R2-3 — Canada's unscripted strata violate the frozen pre-window

**Attack.** `unscripted_strata.py` line 55 reads `ca/segments_ca2.jsonl`.
`permeation_strata.py`, `trim_equalweight.py`, `split_half_trim.py` and
`build_band_screen_pool.py` all read `ca/segments_ca_en.jsonl`. Neither
`run_protocol.py` nor `run_protocol_v11.py` has a lower date bound — the filter
is `if d <= PRE_MAX`, with no `PRE_MIN`. So the ca2 extraction's older sittings
flow straight into the pre-window.

**Measured on the stratum files:**

| file | min date | pre-window words before 2018 | pre-sittings | W_pre/W_post |
|---|---|---|---|---|
| `ca_prepared.jsonl` | **2015-12-07** | 501,104 / 1,404,542 (**35.7%**) | 693 | **2.62** |
| `ca_unscripted.jsonl` | **2015-12-07** | 1,225,923 / 3,448,805 (**35.5%**) | 694 | **2.59** |
| `ca_short.jsonl` | 2018-01-29 | 0 | 464 | 1.62 |
| `ca_long.jsonl` | 2018-01-29 | 0 | 465 | 1.86 |

Irish and UK strata are clean (min dates 2018-01-16 and 2018-01-08, zero
pre-2018 words). This is Canada-specific — and Canada is the row §5.2c calls
"the sharpest test" and the one it uses to overturn the length-band reading.

**What it threatens.** §1 line 48 states the 2018 floor as protocol
("`replication_protocol.md`, Clarification 1"), so this is a documented
protocol violation, not a judgement call. The knock-on is quantitative:
W_pre/W_post of 2.6 against 1.6 in the clean bands is a 60% larger multiplier
on the smoothing constant, which is precisely the F9 artifact the round-1
review found — reintroduced in the strata used to make the argument that
survived it.

**Cheapest fix.** Point `unscripted_strata.py` at `segments_ca_en.jsonl`, add a
`PRE_MIN = 2018-01-01` guard and an `assert` to both protocol scripts, and
re-run. Do this before R2-2's re-run, since it changes the same numbers.

---

### MAJOR

#### R2-4 — the per-year series is size-confounded and every 2026 cell is a partial year

**Attack.** §2.6a scores each post year against the same 2018–22 baseline with
its own placebo null, but a small post window thins per-word counts and
deflates the statistic mechanically. Subsampling NB's later post years down to
2026's token count (291,479 words) and re-running the identical v1.1 statistic
three times:

| NB year | as reported | matched-size draws | mean |
|---|---|---|---|
| 2025 | +0.265 | +0.171 / +0.202 / +0.161 | **+0.178** (−33%) |
| 2024 | +0.112 | +0.088 / +0.127 / +0.065 | +0.093 |

And the last sitting date in each segment file: **NB 2026-05-14, Canada
2026-06-18, Ireland 2026-07-16, UK 2026-07-16, US House 2026-07-23, US Senate
2026-07-30.** Every "2026" column is 4.5–7 months against 12, and the word
"partial" appears nowhere near §2.6a.

**What it threatens.** The instrument-decay claim, which is the round-1
rebuild's headline new insight and which §2.6a uses to move all trajectory
claims onto the detector. At matched size NB's 2025→2026 fall is **−43%, not
−61%**, so "more than halves" is wrong as written. UK 2026 (+0.036, p=0.121)
is inside the size-induced deflation of its own 2025. The decline does not
vanish — it is real in NB and probably real in the UK — but "four of six
chambers peak and then decline" is read off an uncorrected column.

**Cheapest fix.** Report every year at a common subsampled token count with
three or more draws and the spread (≈20 lines on top of `per_year_series.py`),
and label 2026 as partial with its cut-off date in every table that shows it.
Then restate the NB fall as ~43%.

---

#### R2-5 — no v1.1 effect size has an interval, and §2.6 states a range anyway

**Attack.** `run_protocol_v11.py` computes no bootstrap. v1.0's clustered
bootstrap exists only in `run_protocol.py`, and only on the pooled full-list
ratio, not on the equal-weight primary. So §2.6's six effect sizes have
p-values and no uncertainty, and §2.6 nevertheless asserts "the defensible
range among confirmatory chambers is −0.03 to +0.12."

Word-level standard errors of the equal-weight mean logFC, treating words as
independent — a **lower bound**, since §1.2 itself argues the turn is the
clustering unit:

| chamber | excess | SE (lower bound) |
|---|---|---|
| New Brunswick | +0.278 | 0.0374 |
| UK | +0.121 | 0.0221 |
| Dáil | +0.080 | 0.0221 |
| US House | +0.104 | 0.0234 |
| Canada | +0.029 | 0.0237 |
| US Senate | −0.036 | 0.0232 |

UK, US House and Ireland are within ~1.3 SE of a difference of one another;
Canada and Ireland within ~1.6. The stated range spans about 3 SE end to end.

**What it threatens.** The "−0.03 to +0.12" sentence describes sampling noise
as if it were a spread of chamber effects — the same error §5.0b correctly
refuses to make about prevalence, where it *does* run a homogeneity test
(X² = 22.2, df = 3, p = 6.0 × 10⁻⁵). It also threatens §5.0b's own comparison
sentence, "the UK has among the largest lexicon excesses and the lowest
measured prevalence," which orders chambers on a quantity with no interval.

**Published anchor.** Monroe, Colaresi & Quinn, "Fightin' Words," *Political
Analysis* 16(4):372–403 (2008): log-odds-ratio variance goes as 1/count, so an
unstandardised equal-weight mean is dominated by its rarest members. Their
ζ = δ/√Var(δ) is the standardised alternative. Note their design norm, which
bears on R2-9 too: the answer to zero counts is "Bayesian shrinkage …
consistently applied across the whole of the vocabulary," explicitly not an ad
hoc filter that erases words.

**Cheapest fix.** Port the speech-clustered bootstrap into
`run_protocol_v11.py` and print a 95% CI beside every excess. If the CIs
overlap as the word-level SEs suggest, write that sentence: **"the chambers
are not distinguishable on the lexicon"** is cleaner than a range, and it is
what §2.6 is already trying to say.

---

#### R2-6 — §8's licensing table licenses three claims the rebuild killed

**Attack.** §8 is titled "What each headline number licenses you to say" and is
the table anyone quoting this study will lift. Three of its six rows are dead.

| §8 row | status |
|---|---|
| `p = 2.4 × 10⁻⁷ (Fisher, 3 chambers)` | superseded by §2.6's five-chamber 2.9 × 10⁻⁶ — and see R2-7 |
| `excess +0.218 to +0.272 → consistent magnitude across parliaments` | §2.6 line 244: "Any claim of 'consistent magnitude across parliaments' is dead." |
| `Se/Sp = 1.0 (NB, Pangram) → the prevalence figure needs no correction` | Se = 1.0 was 40/40 on the Mistral synthetic corpus that §4.3 says "has been removed from the study entirely … Nothing now depends on it." §5 says 7.5% is a floor with 1/Se as an unknown multiplier. |

**Why the third one is the worst.** The whole point of obviating an analysis
rather than defending it is that nothing downstream still cites its number.
Something does.

**Cheapest fix.** Rewrite §8 against v1.1: the excess row becomes the five
v1.1 values with CIs (R2-5) plus "chambers are not distinguishable"; the Fisher
row becomes the five-chamber v1.1 figure with the dependence caveat (R2-8);
the Se row becomes "Sp = 1.0 measured, Se unmeasured — 7.5% is a floor with
1/Se as an unknown multiplier." Then grep the whole document for
`2.4 × 10⁻⁷`, `+0.218`, `+0.272`, `Se = 1` and `four chambers`.

---

#### R2-7 — the cost of the fixes is quoted across a changing chamber set

**Attack.** §2.5 reports X² = 41.4, df = 6, p = 2.4 × 10⁻⁷ over three chambers
under v1.0. §2.6 reports X² = 44.3, df = 10, p = 2.9 × 10⁻⁶ over five chambers
under v1.1. REVIEW-RESPONSES §1 presents the move from 2.4 × 10⁻⁷ to
2.9 × 10⁻⁶ as the net effect of the fixes. It is not like-for-like: two of the
degrees of freedom and two of the chambers are new since round 1.

All six `*_protocol.json` files have `primary_p = 0.0`, i.e. all six v1.0
p-values are at the 1/1000 resolution bound. Recomputing at that bound:

| set | X² | df | p |
|---|---|---|---|
| v1.0, 3 chambers (as printed in §2.5) | 41.45 | 6 | 2.36 × 10⁻⁷ |
| **v1.0, same 5 chambers as §2.6** | **69.08** | **10** | **6.68 × 10⁻¹¹** |
| v1.1, 5 chambers (as printed in §2.6) | 44.30 | 10 | 2.91 × 10⁻⁶ |

**The honest cost of the round-1 fixes is 6.7 × 10⁻¹¹ → 2.9 × 10⁻⁶, a factor
of ~44,000, not the factor of ~12 the documents imply.** This correction runs
*against* the study, which is exactly why printing it is worth more than the
number costs.

**Cheapest fix.** Print both Fishers over the identical five-chamber set and
state the ratio. One line in `cross_corpus.py` — note it currently globs only
`**/*_protocol.json`, so it never sees the v1.1 outputs at all.

---

#### R2-8 — §5.2a and §5.2c are the same contrast in Canada and the UK, and Ireland runs the other way

**Attack.** §5.2c opens: "Length is only a proxy for spontaneity.
Parliamentary procedure gives the real thing." Measured on the study's own
stratum files, procedure and length are very nearly the same cut in two of
three chambers, and are opposed in the third:

| stratum | median words | share under the 120-word "short" cutoff |
|---|---|---|
| Canada Oral Questions ("unscripted") | 91 | **92.6% short** |
| Canada Statements by Members ("prepared") | 163 | **96.1% long** |
| UK "unscripted" | 81 | **85.0% short** |
| Ireland "unscripted" | 169 | **27.3% short** |

**What it threatens.** §5.2c is presented as an independent confirmation that
cuts against §5.2a's length reading. In Canada it is a relabelling of it — the
Canadian "ladder" in §5.2c orders the same segments the §5.2a length bands
order. And Ireland's unscripted stratum is a *long*-text stratum, so the two
sections are not measuring the same contrast across chambers at all, which is
why they appear to disagree.

**Cheapest fix.** Report the length composition of every procedural stratum in
the §5.2c table, and drop the "length is only a proxy / procedure gives the
real thing" framing — it is not what the strata are. Combine with R2-2's
re-run: under v1.1 the Canadian ladder is monotone in scriptability *and* very
nearly monotone in length, which is one finding, not two.

---

#### R2-9 — the US House / Senate "sharpest evidence" paragraph cannot carry that weight

**Attack.** §2.6 elevates the House/Senate contrast to "the sharpest evidence
in the study that the effect is not some artifact of Anglophone parliamentary
drift." Two things undercut it. First, under v1.0 both chambers were positive
and significant (House +0.299, Senate +0.151, both p < 0.001); the contrast
exists only under v1.1. Second, the Senate is the one chamber that **moved in
the pre-LLM window and stopped**: +0.100 (p = 0.002) on the 2018-vs-2022
in-time placebo, against −0.036 (p = 0.910) on the real one. A contrast between
a chamber with a zero pre-LLM baseline and a chamber with a positive one is a
statement about differing pre-existing trends, not about institutions.

Separately, **REVIEW-RESPONSES §1's "Nothing reverses direction" is wrong**:
`us_senate_protocol.json` gives +0.1512 at p ≤ 0.001 and
`us/v11_us_senate_v11.json` gives −0.03609 at p = 0.910. The point estimate
crosses zero.

**What it does *not* mean.** −0.036 at p = 0.910 is a null, not a negative
effect, and the Senate's pre-LLM movement appears in only one of the two
in-time placebo windows (+0.019, p = 0.255 on the other). "A fix changing a
number" is what a fix does; there is no manufacturing here. And the attack
misreads §2.6's sentence "its style arm behaves like the others" — that is a
claim about the instrument being realised normally in that corpus (384/407
words present, style − content +0.255), not a claim that the Senate never
moved.

**Cheapest fix.** Change "Nothing reverses direction" to "one chamber moves
from significant to null." Rewrite the §2.6 paragraph to report both chambers
against their own in-time placebo baselines, and demote "sharpest evidence in
the study" — it is a suggestive contrast whose interpretation depends entirely
on R2-1.

---

### MINOR

#### R2-10 — Fisher's method is applied to p-values the document argues are dependent

**Attack.** §2.5 and the glossary both say Fisher "combines *independent*
p-values." The five confirmatory chambers share one 407-word instrument and,
per R2-1, one common secular trend. The two US chambers share **694 of the
House's 825 sitting dates** in the same published Record — and §2.6 justifies
comparing them on exactly that ground. Under positive dependence Fisher's X²
is inflated and its nominal p is anti-conservative.

**Why it is minor in practice.** The Senate contributes −2·ln(0.910) = 0.19 to
X² = 44.3. Dropping it entirely gives X² = 44.11, df = 8, **p = 5.4 × 10⁻⁷** —
*more* significant, not less. And three of the five p-values are at the 1/1000
resolution bound, so the combined figure is already a bound rather than a
measurement.

**Cheapest fix.** One sentence of caveat, plus either dropping one US chamber
or using Brown's method (Brown, *Biometrics* 31:987–992, 1975) with the
empirical correlation between chambers' per-word logFC vectors — you have all
six vectors, so it is directly estimable.

---

#### R2-11 — New Brunswick's headline and its per-year series are computed on different corpora

**Attack.** `run_protocol.py` and `run_protocol_v11.py` filter on `scoreable`
only. `per_year_series.py` additionally drops segments flagged `translated` or
with `orig_frac <= 0.5`. In New Brunswick that filter removes **25.4% of
pre-window words and 15.6% of post-window words** — a 10-point differential in
the share of translator-authored French-origin text between the two windows,
uncontrolled in the headline. Re-running v1.1 with the filter moves NB's excess
from **+0.2776 to +0.2390**.

**Scope is narrower than it looks.** Every scoreable segment in
`ca/segments_ca_en.jsonl`, `ie/segments_ie_en.jsonl` and `uk/segments_uk.jsonl`
has `translated` false and `orig_frac > 0.5` — those files are already filtered
at extraction, which is what the `_en` suffix means. §3's "Translation
exclusion" control row is therefore honest for Canada, Ireland and the UK. The
defect is **NB-only** (6,006 of 22,851 scoreable segments in
`segments_60th.jsonl` alone carry low `orig_frac`), and NB is already quoted as
discovery-only and as an upper bound.

**Cheapest fix.** Move the filter into both protocol scripts and re-run. NB's
v1.1 excess becomes +0.239. Three lines, and it is the version §1.1 already
claims to have run.

---

#### R2-12 — the dispersion axis is an unweighted sitting count, coarsest in the chamber with the largest effect

**Attack.** `disp[w]` counts distinct pre-period sitting dates with no size
weighting, so a 200-word procedural day and a 40,000-word budget debate count
as equal parts. Pre-period sittings: **NB 169, Canada 465, Ireland 488, US
House 534, US Senate 693, UK 747** — so `int(log2(disp+1))` spans 8 bins in NB
and 10 in the UK, and NB's 407 instrument words spread [47, 54, 67, 69, 58, 41,
35, 36] across them.

**What it threatens.** §3.1 already concedes that NB's dispersion filter "is
coarse" because it has only 169 pre-period sittings, and uses that concession
to demote the NB formality control. Fix 2 imported the same coarse filter into
NB's *primary null*, in the chamber with the largest reported effect (+0.278),
without repeating the concession. R2-1's no-gap odd/even test is consistent
with this: NB shows +0.093 of pure estimator bias where the large chambers show
0.01–0.03.

**Not a citation defect.** §2.6 defines its dispersion as "how many distinct
sittings a word appears in" — range / document frequency, a standard measure —
and cites Gries 2008 for the *principle* that dispersion is co-equal with
frequency, not for DP specifically. The attack's "not the measure the cited
source specifies" is too strong.

**Cheapest fix.** A sentence in §2.6 carrying §3.1's concession forward, plus a
sensitivity run using size-weighted DP per Gries, *IJCL* 13(4):403–437 (2008)
with the Lijffijt & Gries erratum, *IJCL* 17(1):147–149 (2012) — whose whole
subject is that the equal-parts assumption breaks when parts differ in size.
A dozen lines. Then check whether NB's excess survives it.

---

#### R2-13 — present-in-both selects the word list on the outcome

**Attack.** Fix 1's filter is literally `pre_c[w] > 0 and post_c[w] > 0`, so
each corpus's realised instrument is chosen by that corpus's own post-window
counts. `n_words_present`: **NB 335, Ireland 370, UK 373, US House 382, Canada
384, US Senate 384** of 407. NB's effect is measured on 13% fewer words than
Canada's, and the words dropped are precisely the ones that fell to zero. The
filter also admits words with a single token in either window — in NB a word
with pre = 1, post = 1 scores log(4,244,863 / 2,450,195) = **+0.550** by
arithmetic alone, while the same word at post = 0 is deleted. That is an
outcome-conditioned on/off switch in the highest-variance stratum of the
vocabulary.

**What it threatens.** §9: "The protocol's only per-corpus input is the corpus
name … That separation is what makes the cross-chamber combination legitimate
rather than a fishing expedition." Under v1.1 that is no longer true — though
note §9 documents the v1.0 script list, so this is a failure to update rather
than a false claim.

**Published anchors.** Kobak et al. restrict to words with frequency above
1e-4 in *both* years — a candidate floor applied before any effect is computed,
which is outcome-independent because it is symmetric and pre-registered by
design. Evert, "Measuring Keyness" (DH2022, 202–205) recommends LRC because
"(iii) it can be applied to candidates with f2 = 0 without special precautions
… (v) it includes a reliable significance filter and does not require arbitrary
frequency thresholds," and names Hardie's 0.5 substitution as having no
mathematical justification — so v1.0's smoothing was never defensible, but
deleting zero-count words is the wrong repair.

**Cheapest fix.** Replace the `> 0` filter with a **pre-period-only frequency
floor**: outcome-independent, identical word list in every chamber, fixed
before the post window is touched. Removes the F9 smoothing artifact without
deleting anything and restores §9's claim.

---

#### R2-14 — §6's sweep table is v1.0 output presented as the secondary to a v1.1 primary

**Attack.** `run_protocol_v11.py` computes no sweep. The six-column table in §6
is exactly the `sweep` arrays in the v1.0 `*_protocol.json` files (verified: NB
0.015 / 0.008 / 0.000 / 0.001 / 0.000 / 0.000; US Senate 0.472 / 0.945 / 0.984
/ 0.964 / 0.986 / 0.992). §6 carries no protocol label. So "4 of 30
confirmatory cells reach p < 0.05" compares a v1.0 pooled secondary against a
v1.1 equal-weight primary, and the disagreement is partly the fix rather than
the weighting. The rare-word cells (<1, <2 per 100k) are exactly the stratum
present-in-both censors hardest, so a v1.1 sweep could move substantially
either way.

**Why it is minor.** The sweep is reported *against* the study's own claim, so
the mismatch cannot be inflating anything, and the honest disclosure survives
either version. The cost is that nobody knows which way a v1.1 sweep moves —
a gap to fill, not a result to retract. §6 is nonetheless the anti-p-hacking
section, which is the worst place in the document to have an unlabelled
protocol mismatch.

**Cheapest fix.** Port the sweep into `run_protocol_v11.py` (~10 lines, the
`pooled()` helper transfers unchanged) and print both tables side by side.

---

#### R2-15 — §3's control table describes a null the current protocol does not have

**Attack.** §3 row "Placebo null" reads: "every placebo draw negative,
instrument positive, in all four chambers." Under v1.1, **New Brunswick's
placebo median is +0.11613 and its placebo max is +0.22457** — placebo draws
there are strongly positive — and the per-year NB placebo medians are +0.264,
+0.227, +0.573. "Four chambers" is also stale; there are six. The same v1.0
statement props up §2.5's "the null is *not* centred on zero — placebo sets
drift by −0.14 to −0.25," which is now the wrong sign for the discovery corpus.

**Cheapest fix.** Rewrite the row and the §2.5 sentence from the v1.1 JSONs,
with per-chamber placebo medians rather than a range. Note the argument still
works — it just has to be made in both directions: the null is not centred on
zero *and its sign is chamber-specific*, which is a stronger statement about
why raw primaries are incomparable.

---

### PRESENTATIONAL

#### R2-16 — v1.1's third, undeclared change to the placebo pool

`run_protocol_v11.py` builds its donor pool excluding `set(style) | set(content)`
where `run_protocol.py` excluded only `set(style)`. §2.6 says the point of
running both protocols is "to show exactly what each fix costs," and a third
undeclared change breaks that accounting. **The consequence is negligible**:
re-running v1.1 with a style-only pool gives NB +0.27531 (vs +0.27756), UK
+0.12267 (vs +0.12074), Ireland +0.08363, Canada +0.03283, US House +0.10445,
US Senate −0.03403 — every difference ≤ 0.004, and NB moves in the opposite
direction to the one the attack predicted. One line of documentation in §2.6.

#### R2-17 — §1's corpus table gives both US chambers 1,554 sittings

The segment files contain **825 distinct House dates** (2018-01-08 to
2026-07-23) and **1,048 Senate dates** (2018-01-02 to 2026-07-30); union 1,179,
**intersection 694**. `run_protocol_v11.py` reports pre-sittings of 534 and 693.
1,554 is the number of CREC daily-issue files in `us/zips` — a fetch count, not
a per-chamber sitting count, and §2.6 repeats it as "1,554 sitting days." An
identical sittings figure for two chambers in one table is the first thing a
sceptical reader checks. Fix: print 825 and 1,048, say what 1,554 counts, and
put the 694-date overlap next to the House/Senate contrast where it belongs
(R2-9, R2-10).

#### R2-18 — the replication script argues for its own fix using a withdrawn control

`run_protocol_v11.py`'s docstring justifies present-in-both on the ground that
"because Kobak's 462 CONTENT words are mostly biomedical jargon absent from
Hansard, that artifact is large enough that v1.0 cannot distinguish the style
list from the content list," and its F3b block prints "The instrument only
means what we claim if style rises and content does not." Both rationales were
withdrawn in round 1 (REVIEW-RESPONSES F3: "OBVIATED — control cut as
orthogonal"). The script still computes the content arm, still prints
STYLE − CONTENT with that criterion attached, and still writes
`style_minus_content` into all six v11 JSONs (+0.25 to +0.48). The docstring
also numbers present-in-both as F3 where the responses document reassigns it to
F9. The script is the first artefact a replicator reads.

---

## 4. Attacks that failed

Answer these in review; each was raised and did not survive verification.

1. **"Net of its own pre-LLM baseline, only the US House survives."** Not
   established. The in-time placebo windows are 1–2 years against the real
   design's 5-year pre and 2.5-year post; window size moves this statistic by
   ~30% (R2-4); and both placebo post-windows sit on the COVID peak, whose
   departure from the pre-window the study has already shown moves this
   vocabulary hard. The baselines are a warning, not a subtraction.

2. **"v1.1 manufactured the flagship finding."** v1.1 is the corrected
   protocol. A fix changing a number is what a fix does; the same logic would
   discredit every applied round-1 finding.

3. **"The Senate reverses sign."** It goes from significant (+0.151) to null
   (−0.036, p = 0.910). A point estimate crossing zero at p = 0.91 is a null,
   not a negative effect. (REVIEW-RESPONSES still needs its wording fixed —
   R2-9.)

4. **"§2.6's sentence 'its style arm behaves like the others' is false."**
   Misreading. That sentence claims the instrument is *realised* normally in
   the Senate corpus — 384/407 words present, style − content +0.255 — not that
   the Senate never moved in any window.

5. **"The translation exclusion is never applied, so §3's control row is
   false."** True for New Brunswick only. `ca/segments_ca_en.jsonl`,
   `ie/segments_ie_en.jsonl` and `uk/segments_uk.jsonl` contain zero segments
   with `translated` true and zero with `orig_frac ≤ 0.5` — they are filtered at
   extraction. The row is honest for three of four chambers (R2-11).

6. **"§3's absent-word-check row is falsified: present-only halves NB and UK."**
   Misreading. That row is about the **raw primary**, and it still holds:
   present-only moves NB +0.3791 → +0.3882 and UK +0.1155 → +0.1066, widening
   the NB−UK gap from 0.264 to 0.282 (v1.1: +0.3937 and +0.10657, gap 0.287).
   The halving is of the **excess**, and it comes from the placebo side —
   dispersion matching moves NB's placebo median from −0.175 to +0.116 — not
   from present-in-both.

7. **"The dispersion axis is not the measure Gries specifies."** §2.6 defines
   its dispersion explicitly as sitting-range and cites Gries for the principle,
   not for DP. The residual point is about NB's coarseness, not about the
   citation (R2-12). The attack's bin arithmetic was also wrong: NB spans 8 bins
   and the UK 10, and NB's word distribution is [47, 54, 67, 69, 58, 41, 35, 36].

8. **"The undeclared pool change lowers every excess."** Wrong in magnitude and
   in sign: all six differences are ≤ 0.004 and NB moves the other way (R2-16).

9. **"`cross_corpus.py`'s `fisher()` would raise on log(0)."** It would not —
   `p = d['primary_p'] or (1.0 / d['n_placebo'])` already substitutes the
   resolution bound. The glob point is correct: it reads `**/*_protocol.json`
   and never sees the v1.1 outputs.

---

## 5. The weakest load-bearing claim

**§5.2d Claim 1 — "a broad-based floor exists everywhere … it appears in speech
that could not have been drafted."**

This is the study's most distinctive contribution. §3.0 frames the SUTVA
violation as "the study's most interesting finding rather than a nuisance,"
§5.0b uses permeation to explain why the lexicon and the detector rank chambers
differently, and the paper's use of S10 rests on mass behaviour change rather
than on a drafting-prevalence number that other people will also produce. It is
also the only claim in the document all of whose supporting analyses are still
computed under a null the document itself declares defective — and each of its
three legs fails independently when the corrected null is applied:

- **The unscripted leg is gone.** Under v1.1 no unscripted stratum is
  significant (Canada −0.058 at p = 0.900, UK −0.046 at p = 0.892, Ireland
  +0.037 at p = 0.147). The claim's own wording — "speech that could not have
  been drafted" — points at exactly the three cells that die.
- **The dose-response leg inverts.** Long now exceeds short in all three
  chambers, which is the drafting prediction, not the permeation one.
- **The sharpest-test leg is computed on a corpus that violates the frozen
  pre-window.** 35.5–35.7% of the Canadian unscripted and prepared strata's
  pre-window words predate the 2018 floor, from a different extraction, with
  W_pre/W_post inflated to 2.6.

The split-half result (§5.2b) is the one leg with a real chance of surviving,
because it is an argument about *distribution* rather than level — no minority
of adopters accounts for the effect — and that conclusion is not obviously
sensitive to the placebo baseline. It is still v1.0 and still needs re-running.

The contrast with R2-1 is worth being explicit about. The in-time placebo
problem is the more serious threat in principle — it reaches every p-value in
the lexicon arm — but its outcome is genuinely unknown until the floored
counterfactual is run, and it may well leave a smaller, defensible effect
standing. Claim 1 does not have that option: the numbers that break it are
already in hand, computed with the study's own script on the study's own
stratum files. **Re-run §5.2 under v1.1 before anything else, and be prepared
to publish the inversion.** A study that reports "our most interesting finding
did not survive our own correction, and here is what did" is more credible than
one whose most interesting finding is the only section that was never
re-derived.
