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
| Canada Commons | 338 | 1,097 | 20.1M / 11.1M | confirmatory, complete |
| UK Commons | 650 | 1,137 | 47.2M / 24.2M | confirmatory, complete |

All four are complete. Each chamber is also run in a **within-speaker**
specification (members present before and after that chamber's election),
since the UK, Ireland and Canada all held general elections inside the
post-window.

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

**Raw mean-logFC values are NOT comparable across chambers.** Each corpus
has its own baseline for what frequency-matched random vocabulary did over
the same window, and those baselines differ substantially (placebo medians
range −0.141 to −0.245). Canada makes this unmissable: its raw primary is
*negative* (−0.0138) yet p < 0.001, because its placebo baseline is lower
still. The comparable effect size is each instrument's **excess over its own
placebo median**.

| chamber | seats | raw primary | **excess** | p | vs formality control |
|---|---|---|---|---|---|
| New Brunswick *(discovery)* | 49 | +0.3791 | **+0.554** | < 0.001 | +0.377 |
| Dáil Éireann | 160 | +0.0647 | **+0.224** | < 0.001 | +0.052 |
| Dáil *(within-speaker)* | 160 | +0.0722 | **+0.244** | < 0.001 | +0.153 |
| Canada Commons | 338 | −0.0138 | **+0.218** | < 0.001 | +0.090 |
| Canada *(within-speaker)* | 338 | +0.0122 | **+0.257** | < 0.001 | +0.241 |
| UK Commons | 650 | +0.1155 | **+0.257** | < 0.001 | +0.088 |
| UK *(within-speaker)* | 650 | +0.0776 | **+0.272** | < 0.001 | +0.119 |

**Fisher over the three confirmatory chambers: X² = 41.4, df = 6,
p = 2.4 × 10⁻⁷.**

The three confirmatory chambers span **0.218–0.272**, and **0.244–0.272** on
the like-for-like within-speaker runs — much tighter agreement than the raw
figures suggested.

**Two revisions since 2026-07-31.** (a) That report led with New Brunswick's
~3× rise. NB was selected *because* a signal was visible there — the origin
was a viral clip of a member reading an AI framing sentence aloud — which
selects on the outcome even though instrument and protocol are external.
NB is now quoted as **discovery-inflated, an upper bound**; on the
normalised metric it is ~2× the others, not ~5×. (b) Cross-chamber
comparisons of the raw statistic were mistaken and are corrected above.

**A phrasing constraint that must survive into the paper.** In Canada the
*absolute* volume of AI-style vocabulary **fell** (clustered bootstrap CIs
0.925 and 0.916, both below 1.0). It fell markedly less than comparable
vocabulary did, which is what the significant result measures. So the
defensible claim is **"AI-preferred vocabulary rises relative to comparable
vocabulary"** — not "rises". That holds in all four chambers; the stronger
absolute claim does not.

A hypothesis was killed along the way: effect size is **not** monotone in
chamber size. On the normalised metric the confirmatory chambers are
statistically indistinguishable from one another (0.218–0.272 across
49→650 seats), so chamber size predicts nothing. Ireland was chosen
specifically to separate chamber size from corpus size and it falsified the
ordering; Canada confirmed the null.

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
  `<FloorLanguage>` markers (26% of its "English" record is translated
  French — translator-authored text that would otherwise have been scored as
  members' own).

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

Open, in priority order: per-chamber Pangram calibration
outside NB (prevalence is currently a one-chamber number); a human-coded DQI
subsample to make the quality arm paper-grade; the below-threshold residual
sample that would close NB's 7.2%-vs-8.3% gap; and a role-controlled UK
specification to separate frontbench churn from behaviour change.
