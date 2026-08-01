# S10 pilot — pipeline, throughput, and first scores


Executed 2026-07-29 per `plans/S10-legislative-ai-detection.md` (Tasks 2 and 4,
plus the pre-2022 control pull). Environment: NVIDIA GB10 (aarch64, 119 GB
unified), torch 2.13.0+cu130 (SBSA wheel, `--index-url .../whl/cu130`),
transformers 5.14.1. **Caveat: the GPU ran clock-capped at 513 MHz of
3,003 MHz max (P0, no throttle reason, ~15 W; needs root to investigate) —
all measured throughput below is a floor, ~5.9× headroom if unlocked.**

## Pipeline (run in this order)

| Script | What it does |
|---|---|
| `extract.py` | pdfplumber column-aware extraction → `paragraphs*.jsonl`. Splits the two parallel columns, language-IDs each paragraph, pairs L/R by vertical overlap, tags `orig` (left column = language as spoken; validated: anglophone members 94–99% orig-EN, francophone 20–22%). |
| `segment.py` | chronological EN stream → speaker turns (bold-lead + colon) → windows ≤360 words, min 50 (`segments*.jsonl`). Section metadata is noisy (headers vs stage directions) — auxiliary only. |
| `tier1_regex.py` | prompt-leakage sweep (assistant framing, instruction echoes, self-ID, placeholders, markdown). Output `tier1_report.txt`, `tier1_hits.jsonl`. |
| `bench_binoculars.py` | batched Binoculars port (math follows github.com/ahans30/Binoculars; score math in fp32). Sweep mode (`--budgets`) or full scoring (`--full --scores-out`). Stats append to `throughput_runs.jsonl`. |
| `analyze_scores.py` | score distributions by year / orig-vs-translation, naive-threshold counts (uncalibrated — NOT an AI rate), extremes for eyeballing. |

## Data

- `pdfs/` — 38 sittings, 61st Legislature 2nd Session (Oct 2025 – May 2026).
  **Six PDFs are served truncated by legnb.ca** (their content-length matches
  the truncated bytes): 09, 14, 15, 28, 30, 33. Recovered locally with pikepdf
  (page streams intact; xref rebuilt). This also explains why the earlier word
  count (1.60M bilingual) undershot this extraction (1.89M).
- `pdfs_control/` — 6 sittings from 2019 (59th Legislature, sessions 2–3),
  pre-ChatGPT control. Listings for 59/1–59/3 (60 sittings 2018–2020) are in
  the scraper output; URL pattern `legnb.ca/content/house_business/{leg}/{ses}/hansard/`.
- `segments.jsonl` / `segments_control.jsonl` / `segments_all.jsonl` —
  scoring units with date, speaker, section, `orig_frac`, `scoreable`.
- `scores_falcon.csv`, `scores_qwen1.7.csv` — per-segment Binoculars scores.
- `throughput_runs.jsonl` — every timed run: budget, real/padded tokens,
  per-stage seconds, end-to-end tok/s, peak memory.
- `projections.csv` — wall-clock projections to Task-3 corpus scales, with
  assumptions inline.

## Conventions honored

Every number in the memo traces to a CSV/JSONL here (analysis/ convention).
Scores are *uncorrected instrument readings*; the plan's "Do not" rules apply
— no AI-rate claims without the in-domain Se/Sp correction (S10 estimator).

## Pangram web-app adjudication route (established 2026-08-01)

**Billing:** web-app scans draw the Pro plan's monthly word allowance, NOT the
$200 API credit — verified: plan balance held at $167.10 across four web scans
(~5.3k words), August API usage 0 credits / 0 requests. The "500 scans/month"
badge is the *image* detection limit. Text is priced 1 credit / 100 words
against the web allowance.

**Mechanism:** `.txt` is rejected; the uploader takes PDF/DOCX/RTF/CSV, up to
**100 files per batch**. One RTF per segment gives one verdict per segment —
no bundling, no attribution ambiguity. `pangram_rtf/` holds 643 files
(one per >=50 Opus-screened segment), `pangram_rtf_manifest.json` maps
filename -> seg_id/date/speaker/screen score. Results appear in a Result
panel that `get_page_text` extracts as `file / credits / words / verdict`.

**Per-document metadata** (from the history detail view, also extractable):
document-level AI %, AI/Assisted/Human word split, "signs of humanization"
flag, model version, and a per-segment breakdown with classification,
confidence, word count and segment text.

**Also noted for the multi-legislature campaign:** the API has a *Bulk*
endpoint at a 20% discount that accepts per-item `id` fields for row
mapping — the right tool if we ever return to API-based scanning.
