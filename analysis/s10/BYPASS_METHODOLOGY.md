# The bypass arm: how each sample was selected

Written before the final run, because by this point the samples have passed
through several filters and the filters differ between runs. Every claim in
§4.9 of the write-up is conditional on the selection described here.

---

## The question and why it is not one question

Three distinct quantities get confused if the filters are not tracked:

| quantity | what it needs |
|---|---|
| **per-variant flip rate** | how often *a given rewrite* defeats Pangram |
| **per-text evasion rate** | whether *this speech* can be got past Pangram in N tries |
| **evadability by band** | which *originals* are vulnerable at all |

The third turned out to dominate the other two, and it was discovered late.

---

## The organising hypothesis — and its current status

**Status, after the full GO run: DIRECTIONAL, NOT ESTABLISHED. Do not quote it
as a finding.** It reorganised the arm and it is still the best available
account of the pattern, but it does not clear significance on the one sample
that can test it cleanly. `bypass_report.py` prints the current numbers.

The hypothesis: what predicts a Pangram flip is a property of the **original**
— whether the detector was already near its boundary — not how far a rewrite
drives any score down.

Two versions of the evidence, and only the first is sound:

**Opus banding (below).** Measured on New Brunswick, where the Opus screen
post-dates the Pangram batch. Real, but Opus is a proxy for the thing we care
about.

**Pangram's own Mixed verdict.** The direct test, and the one we briefly
overclaimed. An earlier note reported "22% for AI seeds against 76% for
Mixed" as a Pangram-native replacement for the Opus banding. That figure was
computed on batch 0 (100 of 129) and the two halves are **not the same
statistic** — it scored "not confidently AI" as success, so a Mixed seed that
*stayed Mixed* counted as an evasion. Like-for-like on the full 129, using the
one outcome that is a genuine state change for both seed types:

| seed verdict | variants | → AI | → Mixed | → Human |
|---|---|---|---|---|
| AI | 68 | 54 | 10 | 4 = 5.9% |
| Mixed | 61 | 17 | 39 | 5 = 8.2% |

Fisher exact **p = 0.735**. Per text the gap is wider (2/16 against 4/11) but
rests on 27 texts. Note also that **28% of Mixed-seeded variants moved the
wrong way, to AI** — the search is not monotone in the detector's score.

**Band on the 3x re-scored baseline, never on the selection score.** Seeds are
chosen using a single noisy measurement, so that measurement overstates their
true level -- by 4.9 points in the stratified sample and 10.3 in the
Opus-selected one. Banding on it compresses the true separation and, where
selection was extreme, can manufacture or destroy an apparent gradient. Every
band table below uses the mean of three independent re-scores.

New Brunswick, banded on the 3x baseline:

| band (3x) | variants | flip | clean Human |
|---|---|---|---|
| 0–29 | 46 | **57%** | **43%** |
| 30–39 | 54 | 30% | 7% |
| 40–49 | 56 | 23% | 9% |
| 50+ | 56 | **7%** | **0%** |

(The same data banded on the 1x selection score gives a flatter 41/26/15/8 --
the biased version, reported here only to document that the choice matters.)

The variant's own score is uninformative: **41.0 / 41.6 / 42.0** mean Opus for
outcomes Human / Mixed / AI. Driving the Opus number down does nothing on its
own. What matters is whether the original was already near Pangram's boundary.

Mechanism, stated as a hypothesis rather than a finding: text that Pangram
flags while a frontier LLM reads as human-ish is borderline for Pangram, and a
modest rewrite tips it over. Text both detectors agree is machine-written
does not move.

**Terminology, since it is where the overclaim came from.** For an AI-only
seed set, "flip" is well defined: the variant moved off AI. That is what the
45% per-text and 28% per-variant New Brunswick figures mean, and they are
sound. The moment Mixed seeds enter, "flip" stops being well defined — moving
off Mixed can mean getting *worse*. Across mixed seed types the only
comparable outcome is reaching **Human**, and every cross-seed number must use
it.

---

## Sample 1 — New Brunswick, 40 seeds

```
NB corpus (37,801 segments)
  → tier-4 Pangram batch, 2026-07-30 (658 segments)
      strata: A* detector-selected  (Falcon consensus, Fast-DetectGPT tail,
                                     Kobak lexicon, speech-LLR, transition-FD)
              B* score deciles, Y* year draws, C* pre-AI control
  → keep Pangram = AI
  → Opus full-corpus screen, run LATER (37,801 segments)
  → 78 Pangram-AI segments with Opus scores
  → STRATIFIED sample of 40 across Opus bands (3/10/12/8/7)
```

**Opus is an outcome variable here, not a selection variable.** The full-corpus
Opus screen post-dates the Pangram batch, so it could not have influenced which
segments were scanned. That is what makes the band gradient above
interpretable.

**But 31 of the 40 came from detector-selected (A\*) strata** — chosen because
*some other* detector flagged them. The seed set is enriched for text multiple
detectors find suspicious. Checked: A\* and B\*/Y\* seeds have nearly identical
Opus distributions (mean 51.2 vs 53.1, median 45 both), so this does not skew
position on the Opus axis and the within-band comparison survives. It does
limit generalisation: the 41% low-band flip rate is measured on text something
else also noticed. Only 9 seeds came from broad draws — too few to test
separately.

**Stratification was the right call in hindsight.** A top-only sample would
have reported a single averaged effect and hidden the band gradient entirely.

## Sample 2 — Government Orders, 35 seeds (Opus-selected)

```
11,150 GO segments (2025+, 120–360 words)
  → uniform random sample of 600
  → Opus screen, all 600
  → TOP 48 BY OPUS SCORE                    ← selection ON Opus
  → Pangram scan → 35 AI / 8 Mixed / 5 Human
  → keep the 35 AI
```

**Opus is a selection variable here**, and the set is truncated to 55–78.

Consequences, all measured rather than assumed:

- **Regression to the mean −10.3 points** (vs −4.9 in NB), because every seed
  sits at the extreme of a noisy distribution. Establishing this required a
  separate 3× re-score of the 35 unmodified originals; without it the raw
  numbers implied a +19.4 improvement that was mostly artifact.
- **The band gradient cannot be estimated** from this sample — no low band
  exists in it.
- **Contrast pairs are loose** (gap median 10 vs NB's 3): human GO segments top
  out at Opus 65 while seeds start at 55, so close matches were impossible for
  the upper half.

Seeding by Opus headroom was a **mistake**. Headroom predicts how far the Opus
score falls; the Opus score does not predict Pangram flips. This sample landed
entirely in the two least productive bands (15% and 8% flip in NB).

**Result: 80 variants, 18% flip, ZERO clean Human verdicts.** Banded on the 3x
baseline the flip rates are 27% / 7% / 22% across 30–39 / 40–49 / 50+ — **not
monotonic**. This sample does not replicate the gradient.

That is not evidence against it. The sample is **range-restricted**: its 3x
baselines start near 30, so the 0–29 band where New Brunswick found 57% flips
and 43% clean Humans is entirely absent. A sample that cannot contain the
effect cannot test it.

What it does establish, and this is the strongest single fact in the arm:
**zero clean Human verdicts in 80 attempts at any band**, matching the 0/40
observed above Opus 70 in New Brunswick. Seventy-one to 120 attempts across two
chambers, no clean flips from high-scoring originals.

A caution recorded because it caught us: banded on the 1x selection score this
sample appears to show a clean 27% → 3% gradient, and was briefly reported as a
cross-chamber replication. It is an artifact of differential regression between
bands. Do not band on the selection score.

## Sample 3 — Government Orders, 31 seeds (uniform draw) — the final run

```
Government Orders prevalence draws
  · 17 from the 2026-07 pangram_ch batch  (stratum = prev)
  · 14 from the genre arm                 (stratum = prev)
  both: uniform random within stratum, NO screen stratification of any kind
  → Pangram scan (the purpose of those draws)
  → keep AI or Mixed → 31 segments
  → Opus scored AFTERWARDS, all 31
  → SEARCH ALL 31 — no Opus cut
```

**Exactly one selection step: the Pangram verdict.** No detector, lexicon or
Opus score influenced which segments were scanned. This is the cleanest
provenance in the study — cleaner than the NB sample that discovered the band
effect, which carried A\*-stratum enrichment.

All 31 are searched rather than the 16 under Opus 55, so **band is an outcome,
not a filter**. Bands populated: 7 / 9 / 10 / 5 across 0–39 / 40–54 / 55–69 /
70–100. Verdicts: 19 AI, 12 Mixed.

**Zero overlap** with Sample 2 — verified, not assumed.

Two differences from NB that must be stated when comparing:

1. **Mixed originals are included** (12 of 31). NB was AI-only, so every
   original had an unambiguous baseline. Mixed → Human is a real move but not
   the same event as AI → Human, so the two must be reported separately.
2. **No held-out set.** These are every Government Orders positive we hold, so
   this is an exploratory replication of the band effect, not an independent
   estimate of a rate.

---

## Search parameters — identical across all runs

Verified by structural diff, not by assertion: the Government Orders script was
copied from the NB script and differs only in file paths, the seed count, and
`.response.text` → `.text` for the other corpus schema.

| | value |
|---|---|
| PATIENCE (rounds without a new best before retirement) | 3 |
| MAX_ROUNDS | 6 |
| EPS (a new best must beat the old by more than this) | 1.0 |
| KEEP_BELOW (variant retained for testing) | 50 |
| K (variants per active text per round) | 3 |
| replicates per variant | 3 |
| effort | medium (rewrite), low (score) |

**Why low effort for scoring:** measured, not assumed. Opus at max effort
scored −0.005 AUC against a 0.009 run-to-run noise floor on this task, so low
is the same instrument at a fifth the cost, and it matches the 0.951 baseline
every other Opus score in the study was produced under.

**Why 3 replicates:** detector test-retest sd is 6.0 points. Best-of-1
selection chases noise — the first search's best result (25) exactly matched
the no-effect prediction for best-of-240 draws (25.1). A 3× mean has sd ~2.4.

**Why patience on the all-time best:** requiring a fixed improvement every
round retires texts that are improving in small steps. A text stays alive while
it has set a new best within the last 3 rounds.

---

## Pooled result across all four runs

Computed by `bypass_report.py`, which is the only place these are derived; the
per-run numbers in this document were each computed separately at the time and
should be read as history.

| run | variants | Human | `fraction_ai = 0.0` |
|---|---|---|---|
| NB v2 blind | 40 | 1 | 1 |
| NB v3 contrastive | 212 | 29 | 29 |
| GO Opus-selected | 80 | 0 | 0 |
| GO all-31 uniform | 129 | 9 | 7 |
| **pooled** | **461** | **39 = 8.5%** [6.3, 11.4] | **37 = 8.0%** [5.9, 10.9] |

The GO Opus-selected run stays in the pool despite being the badly-seeded one.
Dropping a run *because* it produced no successes would inflate the rate.

**Label instability at the boundary.** Of the 9 GO reversals, `ga033` re-scanned
as **Mixed at 0.67** and `ga092` as Human at **0.10** — ~11% verdict
instability on the same text and model. All 30 New Brunswick Human labels
re-scanned at exactly 0.0.

## What must be said when quoting any number from this arm

- **The per-text rate (45% in NB) is conditional on ~6 attempts.** Bootstrap
  says it saturates near 45% and does not keep climbing with more attempts —
  but search *sophistication* does keep paying (v2 blind search: 10% per
  variant; v3 contrastive: 28%).
- **Any Sample 3 rate is conditional on being a Pangram positive** drawn from
  Government Orders prevalence — not a rate for legislative speech generally.
- **This is frontier-model evasion.** A local-model arm was designed and
  abandoned when the GB10 clock-capped at 429 of 3,003 MHz. A shared staff tool
  refined over months would plausibly exceed what six rounds achieved.
- **All rewriting used an LLM.** Instructed rewriting *raises* AI scores
  (+16 to +30 per rung); human text pushed through the same ladder went 11.7 →
  60.2. Evasion required contrastive exemplars and search; it is not something
  a single "make this sound human" prompt achieves.
- **Effect size replicated across chambers; mechanism did not.** NB and GO
  hypotheses agree on repetition, unglossed idiom and anticlimactic endings,
  and flatly contradict on sentence rhythm (NB: humans use short percussive
  sentences; GO: humans almost never do). Both measured against their own
  matched pairs. The evasion playbook appears to be chamber-specific register,
  not a universal property of human writing.
