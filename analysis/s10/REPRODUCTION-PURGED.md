# What the push guard flagged, and where each thing ended up

The pre-push guard stopped seven files on 2026-09-13. This records what
happened to each and how to rebuild or resolve anything not committed.

*(The filename says "purged" because that was the expected outcome when this
was written. It is not what happened to most of them — four ship. The name is
kept because other files and commit messages point at it.)*

| outcome | files |
|---|---|
| **kept as-is** — false positive | `market_anchors/occupation_titles.txt` |
| **purged, rebuildable** | `vocab_year_counts.json.gz`, `member_cache_panel.json.gz` |
| **committed as text** | `detector_bench_input.jsonl`, `detector_bench_scored_input.jsonl` |
| **committed as pointers** | `detector_bench_controls.jsonl`, `flagged_hits_pool.json` |

The chain everything here sits in:

    public parliamentary archive            118 tracked extractor scripts under
      (official sites + Wayback)            analysis/s10/{provinces,us}/*.py
            |
            v
    segments_*.jsonl                        gitignored: licensed source text,
      (per chamber)                         never redistributed from this repo
            |
            v
    caches and pools                        some committed, some rebuildable
            |
            v
    committed results                       tracked, and what the paper cites

**No committed result depends on anything held back.** Every consumer script
and every result file it writes is tracked. The manuscript cites the two purged
caches as rebuild COMMANDS rather than as artifacts to open (footnotes `rfhk`
and `r41cs`), and neither appears in the artifact table at D.7.

## Kept — not a corpus file

`market_anchors/occupation_titles.txt` is O\*NET-SOC 30.3: CC-BY 4.0,
redistributable with the attribution the pre-registration and METHODOLOGY
carry. Same ruling as `onet_occupation_data.csv` on 2026-08-21. The guard's
prose heuristic fires on the occupation *descriptions* — a standing false
positive, allowlisted by name.

## Purged — derived counts, rebuildable

| file | rebuild | source of truth | results that survive |
|---|---|---|---|
| `vocab_year_counts.json.gz` (56 MB) | `python build_word_year_counts.py` | every `segments_*.jsonl`; the file's own `_meta.sources` names each store it read, per chamber | `kobak_excess_words.csv` (tracked) via `donor_series.py` |
| `member_cache_panel.json.gz` (14 MB) | `python build_member_cache_panel.py` | `provinces/segments_*.jsonl`, `us/segments_us_{house,senate}.jsonl`, `uk/segments_uk_deep.jsonl` + `uk/segments_uk_2023.jsonl`, `ie/segments_ie_en.jsonl`, `ca/segments_ca2.jsonl` — the script's header lists the exclusions and why | `peak_gap_series.csv`, `permeation_components.csv`, `leadlag_words.csv` (all tracked) |

Both hold counts, not prose. They went for size alone (against a 10 MB gate),
and 56 MB would be a poor thing to put in a public repo regardless. Copies at
`~/s10_private_artifacts` so nobody has to re-run the scans.

## Committed as pointers — resolve, don't rebuild

`detector_bench_controls.jsonl` (1,255 rows) and `flagged_hits_pool.json` (316)
carry `text_sha256` and `n_chars` in place of the text, because between them
they span twenty chambers including three that reserve Hansard reuse (BC, VIC,
QLD) and four that publish no terms. See `SOURCE-LICENCES.md`.

To resolve one: take the row's `seg_id`, fetch that turn from the chamber's
archive using its extractor under `provinces/` or `us/`, and compare the
SHA-256. A match proves you hold the string that was scored — a stricter check
than comparing against a copy we could have supplied.

`build_text_pointers.py --check` re-verifies committed hashes against local
text. `build_flagged_hits_pool.py` emits pointers by default; `--with-text`
produces a local inspection copy that must stay untracked.

Neither file is an input to any analysis: `flagged_hits_bound.py` never reads
the text field, and `detector_transfer.py` reads only the scores CSVs.

## Committed as text — the part nothing can regenerate

`detector_bench_input.jsonl` and `detector_bench_scored_input.jsonl` (406 rows
each: 341 bypass variants plus the 65 unmodified segments they derive from)
carry text. `bypass_rewrite.py` seeds only its choice of in-context examples,
not the model's sampling, so re-running yields different strings — nobody,
including us, can reproduce the variants, and a hash of them would point at
nothing a reader could obtain. Both draw only on NB and CA-FED, whose terms
permit research reproduction. Conditions and the adaptation warning are in
`DATA-NOTICE.md`.

The `bypass_text/` working store stays gitignored: it is the unpublished
remainder, not part of the scored sample.

## Re-deriving text from a seg_id

Ids are `CHAMBER + DATE#tTURNwWINDOW` (`SAHA2007-03-07#t112w0` = South
Australia, 2007-03-07, turn 112, word-window 0) or, for New Brunswick,
`DATE#tTURNwWINDOW`. Given the chamber's extractor and its public source, the
id resolves to a turn in a published transcript. That is why the extraction
scripts are allowlisted past the corpus guard: without them 17 of 21 chambers
are unreproducible, and with them a reader who fetches the archive gets the
same segments.
