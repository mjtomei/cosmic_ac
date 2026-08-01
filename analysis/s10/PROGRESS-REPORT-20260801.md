# S10 progress report — machine-drafted text in legislative speech
**2026-08-01 · for external collaborators · artifacts in `analysis/s10/` (repo: performance_commons)**

*Supersedes the 2026-07-31 report. The headline effect size has been revised
**down** after replication; see §2.*

---

## 1. What is being measured

Whether, and how much, the speech recorded in legislative Hansards is now
drafted with LLM assistance — measured as a rate, over time, against
pre-ChatGPT controls from the same chambers.

Four corpora, all in one shared segment schema (≤360-word windows within
speaker turns), all analysed by the same frozen code:

| chamber | seats | sittings | words (pre / post) | status |
|---|---|---|---|---|
| New Brunswick | 49 | 364 | 4.4M / 2.5M | discovery, complete |
| Dáil Éireann | 160 | 748 | 36.7M / 18.7M | confirmatory, complete |
| UK Commons | 650 | 1,137 | 47.2M / 24.2M | confirmatory, complete |
| Canada Commons | 338 | ~1,300 | in progress | confirmatory, running |

Protocol windows are fixed: pre ≤ 2022-12-31, post ≥ 2024-01-01, 2023
excluded as the transition year. `replication_protocol.md` froze the
instrument, statistic, windows, placebo construction and RNG seeding
**before** any corpus beyond NB was touched; `run_protocol.py` is that
protocol as executable code, and the only per-corpus input is the corpus
name (which seeds the RNG). Per-corpus code exists only to map each
source format onto the shared schema.

## 2. Headline result — and an honest downward revision

The instrument is the **style-annotated subset of Kobak et al.'s
excess-vocabulary list** (arXiv:2406.07016), derived from 15M PubMed
abstracts with no contact with any parliamentary corpus. Primary statistic
is choice-free: equal-word-weight mean log fold-change across all 407 words.
The null is 1,000 frequency-matched placebo instruments.

| chamber | primary | p | vs formality control |
|---|---|---|---|
| New Brunswick *(discovery)* | +0.3791 | < 0.001 | +0.3766 |
| Dáil Éireann | +0.0647 | < 0.001 | +0.0516 |
| UK Commons | +0.1155 | < 0.001 | +0.0884 |
| UK Commons *(within-speaker)* | +0.0776 | < 0.001 | +0.1188 |

**Fisher over the two completed confirmatory corpora: X² = 27.6, df = 4,
p = 1.5 × 10⁻⁵.**

**The revision.** The 2026-07-31 report led with New Brunswick's ~3× rise.
Replication shows NB is an outlier: the two independent chambers agree with
each other (+0.065 and +0.078 like-for-like) and sit ~5× below it. NB was
selected *because* a signal was visible there — the origin was a viral clip
of a member reading an AI framing sentence aloud — which selects on the
outcome even though instrument and protocol are external. **NB's magnitude
is now quoted as discovery-inflated, an upper bound. The replicable effect
is ~+0.06 to +0.08 mean logFC, on two chambers and 127M words.**

A hypothesis was also killed: effect size is **not** monotone in chamber
size. Ireland (160 seats) sits *below* the UK (650). Ireland was chosen
specifically to separate chamber size from corpus size, and it falsified the
ordering.

## 3. Controls, and what they rule out

- **Placebo null.** 1,000 frequency-matched random word sets per corpus. In
  every chamber, *every* placebo draw is negative while the instrument is
  positive.
- **Data-defined formality control.** A hand-picked register list invites
  "you chose it to pass", and did fail on one UK specification. So the
  control is now built from data — words marking long prepared speeches over
  short interventions, **pre-period only**, frequency-matched to the
  instrument, zero overlap with it. Two filters proved necessary and were
  found by failure: without a dispersion floor and a proper-noun filter the
  axis returned place names and bill topics. The instrument leads this
  control in every chamber.
- **Absent-word artifact.** The +0.5 smoothing gives words absent from both
  periods a constant positive contribution. Restricting to words present in
  both leaves estimates essentially unchanged and *widens* the NB/UK gap.
- **Composition vs behaviour.** The UK post-window spans the July 2024
  election. Restricted to the 416 MPs speaking in both periods, the effect
  survives (+0.0776, p < 0.001) — so it is not purely compositional.
- **Translation contamination.** Excluded by construction in each bilingual
  chamber: NB by column position, Ireland by language ID, Canada by
  `<FloorLanguage>` markers (25% of its "English" record is translated
  French).

## 4. Prevalence and per-segment adjudication (New Brunswick only)

Detector work has so far been done only on the discovery corpus.

- **Pangram calibrated in-domain: Se = 40/40** on synthetic AI legislative
  speech, **Sp = 243/243** on pre-2023 segments — including the three
  segments an LLM screen rated *most* AI-like in the pre-LLM era, all of
  which came back Human.
- **Prevalence, design-based random sample: 8.3%** of 2025–26 segments
  [4.6–14.6]; by year 0% (2019–22) → 4.0% (2023) → 4.0% (2024) → 4.3%
  (2025) → **13.6% (2026)**.
- **Full tail adjudication:** all 643 segments scoring ≥50 on a
  corpus-wide Claude Opus screen were submitted individually — **461 AI,
  115 Mixed, 67 Human (89.6% confirmed)**. Screen precision is monotone in
  score (100% at 90+, 83% at 50–59).
- **Corpus-wide screen** of all 37,801 segments: pre-2023 flag rate **0.0%**
  across 20,329 segments; 0.5% (2023) → 1.2% (2024) → 7.0% (2025) → 11.0%
  (2026), corroborating the sampled curve at full coverage.

## 5. Mechanism: the scissors

Eight statistical/zero-shot detectors (three Binoculars pairs,
Fast-DetectGPT, LRR, three supervised classifiers), each calibrated on the
2019 control, show **no elevation** — while the lexicon rises. Edited or
assimilated AI keeps its vocabulary and loses its token statistics.
Frontier LLMs reproduce Pangram's verdicts blind (Opus 5 low-effort
AUC 0.951; Fable 5 high AUC 0.936) but open-weight models cannot
(gpt-oss-120b 0.66–0.67 regardless of reasoning effort; Qwen3-32B 0.55–0.72),
so detection of *edited* AI appears frontier-capability-bound.

## 6. Consequence: form up, deliberation down

Blinded Discourse Quality Index coding (Steenbergen et al. 2003, with the
original authors' worked Commons examples as anchors; repeat-pass
reliability at/above their published human inter-coder bar): AI-flagged
speech scores **higher on formal justification**, ~3× **lower on
first-person witness**, and lower on engaging opponents' demands. Blinded
2019 → 2026: justification and evidence up; respect toward others' demands
0.96 → 0.52.

## 7. Positioning and limits

Closest prior work (Suvanto et al., arXiv:2606.14209) covers UK and Swedish
*written* parliamentary texts with a trained classifier; this study measures
the **transcribed spoken record they explicitly avoided**, adds calibrated
commercial adjudication, placebo-based inference, and quality effects.

Open, in priority order: Canada in flight; per-chamber Pangram calibration
outside NB (prevalence is currently a one-chamber number); a human-coded DQI
subsample to make the quality arm paper-grade; the below-threshold residual
sample that would close NB's 7.2%-vs-8.3% gap; and a role-controlled UK
specification to separate frontbench churn from behaviour change.
