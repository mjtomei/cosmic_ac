# Rebuilding the caches kept out of the public repo

Seven files were flagged by the pre-push guard on 2026-09-13. One is a false
positive and stays; the other six are intermediates held locally. This file is
the pointer from each of those six back to a public source, so that removing
them from git costs re-running a script and nothing else.

The chain every one of them sits in:

    public parliamentary archive            118 tracked extractor scripts under
      (official sites + Wayback)            analysis/s10/{provinces,us}/*.py
            |
            v
    segments_*.jsonl                        gitignored: licensed source text,
      (per chamber)                         never redistributed from this repo
            |
            v
    the caches below                        rebuildable, not committed
            |
            v
    committed results                       tracked, and what the paper cites

**No committed result depends on a purged file.** Every consumer script and
every result file it writes is tracked; the caches are inputs to those scripts,
not outputs anyone reads. The manuscript already cites two of them as rebuild
COMMANDS rather than as artifacts to open (footnotes `rfhk` and `r41cs`), and
none of the six appears in the artifact table at D.7.

## Kept — not a corpus file

| file | why it stays |
|---|---|
| `market_anchors/occupation_titles.txt` | O\*NET-SOC codes, titles and descriptions. O\*NET 30.3 is CC-BY 4.0 and redistributable with attribution, which the pre-registration and METHODOLOGY carry. Same ruling as `onet_occupation_data.csv` on 2026-08-21. The guard's prose heuristic fires on the occupation *descriptions*; that is the false positive it was always going to have. |

## Rebuildable — derived counts, no source text

| file | rebuild | source of truth | results that survive |
|---|---|---|---|
| `vocab_year_counts.json.gz` (56 MB) | `python build_word_year_counts.py` | every `segments_*.jsonl`; the file's own `_meta.sources` names each store it read, per chamber | `kobak_excess_words.csv` (tracked) via `donor_series.py` |
| `member_cache_panel.json.gz` (14 MB) | `python build_member_cache_panel.py` | `provinces/segments_*.jsonl`, `us/segments_us_{house,senate}.jsonl`, `uk/segments_uk_deep.jsonl` + `uk/segments_uk_2023.jsonl`, `ie/segments_ie_en.jsonl`, `ca/segments_ca2.jsonl` — the script's header lists the exclusions and why | `peak_gap_series.csv`, `permeation_components.csv`, `leadlag_words.csv` (all tracked) |

Both hold counts, not prose. They are out for size alone (56 MB and 14 MB
against a 10 MB gate), and 56 MB would be a poor thing to put in a public repo
regardless of the guard.

## Rebuildable — verbatim parliamentary text

| file | rebuild | source of truth | results that survive |
|---|---|---|---|
| `flagged_hits_pool.json` | `python build_flagged_hits_pool.py` | the 316 flagged ids from `banded_prevalence.load()`, texts from the per-id RTF submissions and, for UK/IE rescore ids, from the chamber jsonls via each verdict's `seg_id` | `flagged_hits_audit.json` (tracked) via `flagged_hits_bound.py` |
| `detector_bench_controls.jsonl` | re-extract by `seg_id` from the chamber stores | every row carries its id (`ctl|SAHA2007-03-07#t112w0` = South Australia, 2007-03-07, turn 112, word-window 0) | `detector_bench_ctl_scores.csv` (tracked) |

`detector_transfer.py` — the analysis — reads **only** the two scores CSVs, never
the text. Those CSVs carry `seg_id` plus `n_tok`, `logppl`, `fastdetect_d`,
`lrr` and `binoc` for every row, so §B4.10's detector-transfer result
reproduces exactly from what is committed.

## The one real gap

| file | what is lost |
|---|---|
| `detector_bench_input.jsonl`, `detector_bench_scored_input.jsonl` | These hold the bypass **variants** (`2026-05-06#t2699w0|r1v3`, run `nb_v3`) — model-generated rewrites, not archive text. Re-running generation will not reproduce them byte for byte, so the exact strings cannot be recovered from public sources. |

What survives is the measurement: both scores CSVs keep each variant's `seg_id`
and all four detector metrics, so every number in the arm recomputes. What
cannot be redone from the repo alone is scoring *those exact variants* with a
NEW detector later.

This is the same call already made for `bypass_text/`, which is gitignored on
the reasoning that close paraphrases inherit the source's licence question
while the tracked result files keep ids, scores and hypotheses. Keep the
private copies (as with the August tarballs at `~/s10_private_artifacts`) so a
future detector can still be run against them off-repo.

## Re-deriving text from a seg_id

Ids are `CHAMBER + DATE#tTURNwWINDOW` (`SAHA2007-03-07#t112w0`) or, for New
Brunswick, `DATE#tTURNwWINDOW`. Given the chamber's extractor under
`provinces/` or `us/` and its public source, the id resolves to a turn in a
published transcript. That is why the extraction scripts are allowlisted past
the corpus guard: without them 17 of 21 chambers are unreproducible, and with
them a reader who fetches the archive gets the same segments.
