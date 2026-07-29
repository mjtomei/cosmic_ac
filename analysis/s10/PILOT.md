# S10 pilot memo — throughput, pipeline shakeout, first scores

**Date:** 2026-07-29 · **Box:** NVIDIA GB10 (DGX-Spark-class, aarch64, 119 GB
unified LPDDR5x), Ubuntu 24.04, torch 2.13.0+cu130, transformers 5.14.1.
**Scope:** plan Tasks 2 and 4 (pilot + throughput), Tier-1 sweep, and the
pre-2022 control pull. Task 1 (detector survey) and the `Se` reference corpus
remain open.

## TL;DR

1. **Pipeline proven end to end** on all 38 sittings + a 6-sitting 2019
   control: extraction, EN/FR split, original-vs-translation tagging
   (a real discovery — see below), speaker segmentation, Tier-1 regex,
   batched Binoculars scoring.
2. **Throughput (measured, on a clock-capped GPU):** Falcon-7B pair
   **509 tok/s** end-to-end (full corpus in 40 min); Qwen3-1.7B pair
   **1,347 tok/s** (15 min; forward 2,042). The GPU is stuck at 513/3,003
   MHz (root needed to fix); unlocked estimates are ~5.9× higher. Even
   unlocked, the 7B pair lands *below* the plan's 5k–50k bracket — the
   small-pair / iterate-freely branch is the operative one on this box,
   and it agrees with the 7B pair well enough to stratify (ρ = 0.73,
   bottom-decile overlap 54% vs 10% chance).
3. **First scores:** raw flag rates 2025–26 sit *below* the 2019
   pre-ChatGPT control's false-positive floor (2.85% vs 5.64% at the
   accuracy threshold; 0.53% vs 1.03% at low-FPR). Rogan–Gladen point
   estimate: **0** at any plausible Se; rough upper bound **≤ ~0.5%** true
   prevalence (assumptions below). **No detectable machine share via this
   instrument** — and the null is informative about the *instrument* too
   (a 2023-era zero-shot detector may simply have low Se on 2026 text; the
   planned Se corpus measures exactly that).
4. **Design-level finding:** the whole score distribution drifts between
   eras — 2019 reads *more* AI-like than 2025–26 (median 0.986 vs 1.000) —
   **and the drift replicates on a second architecture** (Qwen3-1.7B pair,
   same direction), so it is a property of the record, not the detector.
   Cross-era threshold/Sp transport is therefore not automatic, which
   sharpens the plan's own "measure Se/Sp in-domain" stance into: measure
   them **per era**, and add within-era human anchors (spontaneous
   question-period crosstalk is the closest thing to guaranteed-human 2026
   text).
5. **Tier-1 prompt leakage: 0 hits in 992,587 words** (both corpora) — the
   hard floor is zero *in the edited record*; the unpublished Bill Oliver
   sitting (leakage observed on video captions) is the direct test of
   whether editing strips it. Request to the Hansard Office still worth it.

## Environment: three findings that gate all timing on this box

1. **torch install.** Use
   `pip install torch --index-url https://download.pytorch.org/whl/cu130`
   (aarch64 SBSA wheel; 2.13.0+cu130 today). Verify
   `torch.cuda.get_device_capability() == (12, 1)`.
2. **No sm_121 kernels in the wheel** (`get_arch_list()` tops out at
   sm_120) → every kernel is PTX-JIT-compiled at first use, and the default
   1 GB JIT cache (`~/.nv/ComputeCache`) was full → processes evicted each
   other and recompiled forever (one CPU core pegged, GPU idle, looked like
   a hang). **Fix (no root):** `CUDA_CACHE_MAXSIZE=17179869184` +
   `CUDA_CACHE_PATH=~/.nv/ComputeCache_s121`. First run pays JIT once.
3. **GPU clock-capped at 513 of 3,003 MHz** in P0 under sustained load
   (~13–15 W, 96% util, no throttle reason; `nvidia-smi -lgc` denied
   non-root). Sustained bf16 matmul: **23.6 TFLOPS** ≈ est. max-clock rate ÷
   (3003/513). All numbers here are a **floor for this box as configured**;
   ~5.9× headroom. To try (root): `sudo nvidia-smi -lgc 3003,3003`
   (reset `-rgc`); check DGX OS/firmware updates for GB10 clock behavior.

## Corpus + pipeline

- 38 sittings (61st Leg., 2nd Sess., Oct 2025 – May 2026). **Six PDFs are
  truncated on the server** (content-length confirms; sittings 09, 14, 15,
  28, 30, 33); recovered with pikepdf. Explains the earlier 1.60M-word
  undercount → true total **1.89M words bilingual**.
- **869k EN words**; the two-column record puts the **language as spoken in
  the left column** (translation right). Validated per speaker: anglophones
  94–99% original-EN by words; francophones 20–22%. The study can therefore
  score *speaker-authored* English only (**709k words**), excluding
  translator-authored English — a structural advantage of bilingual
  Hansards that the plan didn't anticipate.
- Segmentation: 3,206 speaker turns → 4,509 windows (≤360 words, min 50),
  3,998 scoreable. Section labels noisy (stage directions) — auxiliary only.
- **2019 control** (59th Leg.): 6 sittings, 585 scoreable windows, 132k
  words, processed identically; orig-EN validation reproduces (Cardy/Carr/
  Austin 99–100%, K. Chiasson 11%). Full 59th listing (60 sittings,
  2018–2020) archived in `analysis/hansard-nb/nb-hansard-59th-index.json`.

## Throughput (measured; clock-capped floor)

| run | budget (padded tok) | real tok | pad eff | tok/s e2e | tok/s fwd | peak GiB | load s |
|---|---|---|---|---|---|---|---|
| falcon sweep | 8,192 | 35k | 0.88 | 439 | 466 | 32.7 | 267 |
| falcon sweep | 16,384 | 35k | 0.81 | 397 | 418 | 34.6 | — |
| falcon sweep | 32,768 | 35k | 0.69 | 329 | 346 | 39.2 | — |
| **falcon FULL corpus** | 16,384 | **1,209,804** | **0.988** | **508.6** | 536.7 | 34.7 | 234 |
| qwen1.7 sweep | 16,384 | 36k | 0.81 | 1,098 | 1,700 | 26.4 | 77 |
| qwen1.7 sweep | 32,768 | 36k | 0.69 | 949 | 1,445 | 35.1 | — |
| qwen1.7 sweep | 65,536 | 36k | 0.55 | 753 | 1,137 | 54.0 | — |
| **qwen1.7 FULL corpus** | 32,768 | **1,198,695** | **0.975** | **1,346.5** | 2,041.7 | 36.5 | 76 |

Readings:
- **Padded-token throughput is flat across budgets** (~500–530/s for the
  Falcon pair): the capped GPU saturates at ~8k-token batches; bigger
  budgets only help via packing. On the full sorted corpus, packing hits
  0.988 and the whole 1.21M-token corpus+control scored in **39.6 min**.
- The plan's "sort by length before batching" note is confirmed load-bearing
  (sweep-subset pad efficiencies of 0.69–0.88 vs 0.988 at scale).
- Qwen pair: score-math (softmax over the 151k vocab) now costs ≈ a full
  forward pass (11.4s vs 10.4s per stage in the sweep) — the e2e/forward gap
  is optimization headroom (bf16 softmax + fused xent), not model cost.
- Model-load overhead: ~4 min (7B pair) / ~1.3 min (1.7B pair) per job —
  use long-running jobs, not per-file invocations.
- Two-pass scoring (all segments through observer, then performer) proved
  unnecessary: both 7B models + score math peak at 34.7 GiB of 119.

## Projections to Task-3 scales

See `projections.csv` (measured full-run rates; capped-clock measurements +
unlocked ÷5.85 estimates, flagged as estimates). The plan asked which end of
the 5k–50k tok/s bracket we are on for a 260M-token sweep ("14 h vs 1.5 h"):
the measured answer is **below the bracket** —

| corpus | falcon pair (capped → unlocked-est) | qwen1.7 pair |
|---|---|---|
| NB this corpus (1.2M tok) | 40 min → ~7 min | 15 min → ~3 min |
| Canadian Parliament, 1 yr (54M) | 29 h → ~5 h | 11 h → ~2 h |
| 10 legislatures × 5 yr (270M) | **147 h (~6 d) → ~25 h** | **56 h (~2.3 d) → ~9.5 h** |

Full sweeps are *feasible but overnight-to-days scale*; the two-phase design
(free detector sweeps everything as stratifier, paid detector samples)
survives contact with the hardware. Score-math optimization (the Qwen pair
spends a third of wall time on 151k-vocab softmax) and the clock fix are the
two levers before buying more compute.

## First scores (uncorrected instrument readings — NOT AI rates)

Falcon pair, reference thresholds (uncalibrated for this register):

| stratum | n | median | < acc thr (0.902) | < low-FPR thr (0.854) |
|---|---|---|---|---|
| 2019 control (pre-ChatGPT) | 585 | 0.986 | **5.64%** [4.0, 7.8] | **1.03%** [0.5, 2.2] |
| 2025–26 corpus | 3,998 | 1.000 | **2.85%** [2.4, 3.4] | **0.53%** [0.3, 0.8] |
| 2025–26 original-EN only | 2,994 | 1.001 | 2.67% | 0.50% |
| 2025–26 translated-EN | 473 | 1.000 | 2.96% | 0.63% |

(Wilson 95% intervals; full table + Rogan–Gladen sensitivity in
`flag_rates.csv`.)

- **The 2025–26 corpus flags *below* the pre-ChatGPT floor.** Rogan–Gladen
  point estimate is 0 for any Se; the rough upper bound (Wilson-extreme,
  low-FPR threshold) is **0.35–0.48%** true prevalence at Se 0.95→0.70.
  Assumption flagged: Sp measured in 2019 applied to 2025–26 — which the
  observed era drift itself questions. Treat as illustrative, exactly per
  the plan's "report the interval, never the truncated point alone."
- **Era drift is the real finding:** the entire 2019 distribution sits lower
  (more "AI-like") than 2025–26. Candidate causes: Hansard editing/house-
  style changes between legislatures, register drift, and Falcon's training
  data placement. Consequence for the full study: thresholds and Sp must be
  estimated per era; add within-era human anchors (spontaneous crosstalk);
  keep a second instrument (Pangram tier) whose error structure differs.
- **Translation is a nothing-burger for this detector** (2.67% vs 2.96%):
  good news — but keep scoring them separately on principle.
- **Eyeballing the extremes:** the lowest scores in *both eras* are
  ceremonial formula — festival greetings, condolence motions, award
  recognitions, procedural rulings. This is the register detectors over-flag,
  live in our own data. No smoking-gun segment surfaced; the two lowest
  2025-era segments (a Diwali statement, an InnovateNB response) are exactly
  the prepared-ceremonial genre the 2019 control also flags.

### Second detector pair (Qwen3-1.7B-Base / Qwen3-1.7B) — replication

- **The era drift replicates on a different architecture and vintage:**
  the Qwen pair also reads 2019 as more AI-like than 2025–26 (median 0.972
  vs 0.983; flags 11.6% vs 9.3% at the Falcon acc-threshold, 3.1% vs 2.6%
  at low-FPR — absolute rates meaningless under transplanted thresholds,
  the *direction* is the point). This is a property of the record, not a
  Falcon quirk.
- **Detector agreement** (`detector_agreement.py`): Pearson r = 0.741,
  Spearman ρ = 0.726, bottom-decile overlap 54.4% (chance 10%) across 4,583
  shared segments. Strong enough for Phase-1 stratification — the 2.6×
  faster small pair can sweep, with the 7B pair or Pangram reserved for
  the sampled phase.
- One divergence worth keeping: the Qwen pair flags translated-EN notably
  more than original-EN (12.3% vs 8.0%) — it reads translationese as
  AI-like; Falcon shows no such gap (3.0% vs 2.7%). Another reason the
  original-vs-translation split stays in the design.

## Verdict

**The pilot justifies the full study, with a sharpened design.** The
pipeline is real, cheap, and validated; the corpus expands naturally
(59th-Leg. listing already captured; ParlaMint et al. still to survey); and
the instrument-calibration problem is now *measured*, not hypothesized:
era drift means naive flag-rate deltas would have produced a confidently
wrong number in either direction — the 2019 control just paid for itself.

What the full study needs that the pilot didn't produce:
1. **Se, in-domain and per-era** — generate known-AI legislative speech
   (prompt with real bill text + speaking role, plausible-vintage models)
   and score it. Without this, a null via a 2023 detector on 2026 text is
   weak evidence of absence. (This is the single highest-value next step.)
2. **Detector survey (plan Task 1)** — unchanged, and now with a concrete
   question: anything published 2025–26 with measured Se on frontier-model
   text in formal registers?
3. **Pangram tier** on a stratified sample (score × era × prepared/
   spontaneous), n≈2,000 (~$120 or inside one $65 Professional month) —
   the second instrument the era-drift finding demands.
4. **Hansard Office request** for the unpublished Bill Oliver sitting — the
   only direct test of whether editing strips Tier-1 leakage.
5. Prepared-vs-spontaneous labels (the noisy section tracker needs a pass;
   likely the dominant stratifier).

Throughput answer for the plan: on this box today, **free local scoring of
everything we can download is feasible but overnight-scale per legislature-
year with a 7B pair, and comfortable with a 1.7B pair** — and 5.9× better
if the clock cap is lifted. The two-phase design stands.

---

# Addendum (2026-07-29, later): detector trials, in-domain Se, authorship

## In-domain Se (pilot grade) — and the "bigger models?" answer

40 synthetic legislative speeches (Mistral-7B-Instruct-v0.3, prompted with
real 2025–26 NB business + speaking roles; family-neutral to all detector
pairs; `gen_se_corpus.py`, vintage caveat there). Se at thresholds
calibrated on the 2019 control (`se_results.csv`):

| detector | Se @5% FPR | Se @1% FPR | synthetic median (ctl median) |
|---|---|---|---|
| **Falcon-7B pair** | **1.000** | **0.975** | 0.691 (0.986) |
| Qwen3-8B pair | 0.825 | 0.250 | 0.823 (0.995) |
| Qwen3-1.7B pair | 0.675 | 0.250 | 0.842 (0.972) |
| HC3-RoBERTa (classifier) | 0.675 | 0.150 | 0.998 (0.028) |
| RADAR (classifier) | 0.200 | 0.025 | 0.983 (0.091) |
| GPT-2-era detector (classifier) | 0.350 | 0.075 | 0.232 (0.001) |

**Bigger ≠ better.** Within the Qwen family, 8B beats 1.7B at the loose
threshold only; both collapse at the strict one. The 2023-vintage Falcon
pair dominates the same-size 2025-vintage Qwen3-8B outright — consistent
with Mireshghallah et al. (EACL 2024): smaller/older scoring models detect
better, plausibly because assistant-register prose saturates newer models'
training data and stops looking anomalous. Se here is against ONE 2024
7B generator; frontier-generator Se is still unmeasured (Pangram stratum D
+ a future API-generated reference).

**Consequence for the null:** the sweep instrument (Falcon pair) has
Se ≈ 0.97–1.0 on this generator class while the 2025–26 corpus flags BELOW
its false-positive floor. Rogan–Gladen with measured Se 0.975: upper bound
≈ **0.3–0.4%** unedited Mistral-class AI text. The null is not detector
blindness — for that class. Edited/paraphrased AI remains undetectable by
design (all zero-shot detectors are paraphrase-fragile).

## Six-detector consensus

3-way Binoculars consensus (control-calibrated): errors stay ~100×
correlated vs independence; 2025–26 all-agree 0.90% vs control floor 1.54%
(at 5% calib) — consensus shrinks lists but never separates the eras
(`consensus.csv`). Classifiers agree: all three flag 2025–26 at/below
their calibrated floors. **Eight statistics** (3 Binoculars, Fast-DetectGPT,
LRR, 3 classifiers) once `scores_multistat.csv` lands; none shows an
elevation so far.

## Authorship (Burrows' Delta, `authorship_delta.py`)

- Closed-set attribution: **54.5% over 43 speakers (chance 2.3%)** on
  1,000-word chunks — authorship signal robustly survives Hansard editing.
- Cross-era self-match (3 speakers in both 2019 and 2025–26): Coon and
  Mitton rank 1 to their own six-years-later profiles; **Austin ranks
  34/43** — a live changepoint specimen (he also changed party/role between
  eras: confound and use-case in one). Design note: spontaneous crosstalk
  should track the *speaker* while prepared text tracks the *office* —
  splitting those is the validation lever, and documented staff changes
  (GNB directory snapshots via Wayback, Public Accounts salary lists,
  news-reported chief-of-staff moves; reconstructible for ministers'
  offices, mostly not for backbenchers) are candidate ground truth.

## Pangram batch (ready to submit)

`pangram_batch.jsonl`: **265 segments, 52,577 words** — A: 45 consensus
hits (2025–26 + control), B: 120 decile-stratified 2025–26, C: 60 control
(Pangram's in-domain FPR), D: 40 synthetic (Pangram's in-domain Se). Fits
a single $65 Professional month with ~1.44M words to spare (enough to
sweep the full original-EN corpus afterward), or a month of free tier.
