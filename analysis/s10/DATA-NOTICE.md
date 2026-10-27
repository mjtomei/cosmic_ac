# Notice for the parliamentary material in this directory

Fourteen files carry the text, or pointers to the text, behind the detector and
grading arms. Two are pointer-only; eleven carry text; one is synthetic.

| file | rows | what it holds |
|---|---|---|
| `detector_bench_input.jsonl` | 406 | **text** — 341 machine-rewritten **variants** plus the 65 unmodified segments they derive from, all from NB and CA-FED |
| `detector_bench_scored_input.jsonl` | 406 | **text** — the same set as submitted for scoring |
| `detector_bench_controls.jsonl` | 1,255 | **pointers** — pre-2022 human controls across twenty chambers, as `text_sha256` + `n_chars` |
| `flagged_hits_pool.json` | 316 | **pointers** — the estimator's flagged hits, same form |
| `pangram_gov_seeds.csv` | 48 | **text, verbatim** — the CA-FED segments that seeded the `go_all` run |
| `pangram_gov_all_b0.csv` | 100 | **text** — CA-FED variants, batch 0 |
| `pangram_gov_all_b1.csv` | 29 | **text** — CA-FED variants, batch 1 |
| `pangram_v3_b0.csv` | 100 | **text** — NB variants, batch 0 |
| `pangram_v3_b1.csv` | 100 | **text** — NB variants, batch 1 |
| `pangram_bypass.csv` | 40 | **text** — NB variants from the earlier bypass run |
| `stage5_evasion_pairs.json` | 35 pairs | **text** — original and variant side by side (26 NB, 9 CA-FED) |
| `stage5_grade_items.json` | 70 | **text** — the blinded grading subset drawn from those pairs |
| `se_segments.jsonl` | 40 | **text, synthetic** — no parliamentary source; see below |
| `wp_extracts.json` | 58 | **text** — full Wikipedia articles, not parliamentary material; see below |

The bottom ten rows were published in `9dff5ba` and `891a4e4` (2026-08-14 and
-16) and went undocumented here until 2026-10-27, when a rewrite of the push
guard's content backstop surfaced them. Every row was then audited: the 369
rows in the four `pangram_*_b*.csv` batches each match a known variant, so they
are model rewrites with no originals among them; `pangram_bypass.csv`'s 40 rows
match no segment in any of the 112 local corpus files, consistent with being
variants; `pangram_gov_seeds.csv` is verbatim, one row traced to
`ca/xml/451_048.xml`. All parliamentary rows are NB or CA-FED. **No row comes
from a restrictive chamber.**

## Why two of them are pointers

The control and flagged pools draw on all twenty chambers, and the terms differ
by chamber. British Columbia permits reproduction "other than personal use"
only with the Speaker's express written consent; Victoria publishes no general
reuse grant for Hansard; Queensland reserves it to the Clerk; and four more
chambers publish no terms at all. Republishing those rows was not ours to do.

So each row carries the SHA-256 of the exact string that was scored instead of
the string. A replicator fetches the segment from the chamber's own archive,
hashes it, and gets a yes/no answer on whether they hold the same text we
scored — a stricter check than comparing against a copy we supply, and one that
needs no licence from anyone. `build_text_pointers.py --check` re-verifies the
hashes against local text; `build_flagged_hits_pool.py` emits pointers by
default.

Earlier revisions of this repository carried those rows as text. They were
removed from the published history on 2026-09-13.

## The files that carry text

`detector_bench_input.jsonl` and `detector_bench_scored_input.jsonl` hold text
because no committed script can regenerate it: `bypass_rewrite.py` seeds only
its choice of in-context examples, not the model's sampling, so re-running it
yields different strings — nobody, including us, can reproduce these. A hash
would point at something no reader could obtain. The same is true of the
`pangram_*` batches and the stage-5 pools: they are the exact submissions the
detector scored, and the scores are meaningless without the strings that
produced them.

All of them draw only on the **House of Commons of Canada** and the
**Legislative Assembly of New Brunswick**. Canada's Speaker's Permission allows
reproduction "in whole or in part and in any medium ... provided that the
reproduction is accurate and is not presented as official", excluding
commercial use; New Brunswick permits reproduction "for educational purposes,
private study, research, reporting ... without charge or request for
permission".

**These reproductions are not official.** They are not published under the
authority of any House, and the absolute privilege attaching to proceedings
does not extend to them. They are reproduced for **non-commercial academic
research**. Where a chamber's own record differs, that record governs.

### The variants are adaptations, not reproductions

341 of the 406 rows in each detector-bench file are text a language model
**rewrote**, as are all 369 rows across the four `pangram_*_b*.csv` batches,
all 40 in `pangram_bypass.csv`, and the `variant` side of every stage-5 pair.
Every one is a modification of a real speech and must not be read, quoted, or
cited as anything a member said. In the detector-bench files they are marked
`"kind": "variant"`, carry a run label (`nb_v3`, `go_all`), and their `seg_id`
ends in a variant suffix (`...|r1v3`) distinguishing them from the segment they
came from; in the `pangram_*` batches the whole file is variants, and in
`stage5_evasion_pairs.json` the two are in separate fields. The unmodified
rows are the 65 marked `"kind": "original"`, the 48 in `pangram_gov_seeds.csv`,
and the `original` field of each stage-5 pair.

Measured against their sources, the variants retain a median 56.9% of the
original wording, and 94 of 180 keep a verbatim run of 20 words or more (max
111). They are close paraphrases, not fresh compositions — which is why the
reproduction permissions above, both of which condition on accuracy, are not
the instrument that covers them; that rests on fair dealing for research.

### `se_segments.jsonl` is synthetic

Its 40 rows were generated by `mistralai/Mistral-7B-Instruct-v0.3`, carry
`"speaker": "SYNTHETIC"` and `"date": "synthetic-2026"`, and reproduce no
chamber's record. The `SE#` seg_id prefix marks the synthetic set; it is not a
chamber code. Nothing in this file is parliamentary material and no
parliamentary licence applies to it.

### `wp_extracts.json` is Wikipedia, under CC BY-SA

58 full article extracts (178 KB) supporting the member-covariate coding, one
per member, each keyed `CHAMBER|surname` with its character count. English
Wikipedia text is licensed **CC BY-SA 4.0**. Reusing it obliges us to credit
the authors, name the licence, state that the text was modified where it was,
and license adaptations alike — conditions, not courtesies: fail them and the
licence does not apply.

Accordingly: each extract is from the English Wikipedia article named in its
own `title` field, written by that article's contributors and licensed CC BY-SA
4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Article histories at
`https://en.wikipedia.org/wiki/<title>?action=history` list the authors. Each
row records the article's `title` and the `chars` count of the stored text.

The text is a plain-text extract: section headings survive as `== Heading ==`,
and markup, references and infoboxes are gone. The prose itself is unmodified.
Retrieval date is not recorded in the file; it is on or before the 2026-08-14
commit that published it. **No committed script builds this file** — it was
made ad hoc, and the two tracked Wikipedia scripts (`wiki_depth.py`,
`build_t1_wiki_depth.py`) call `prop=info` for article length, not the extract
endpoint, so neither reproduces it. Treat the stored extracts as a snapshot of
articles that have since moved on. The derived codings in
`provinces/member_bios.json` and `provinces/member_allsource.json` record
short attributed quotations and the structured fields read off them.

## What is not here

The corpora themselves. What is here is the sample the published detector
results were computed on, in the least redistributive form that still lets a
reader check them.

Two caches are held back for size rather than licence — `vocab_year_counts
.json.gz` and `member_cache_panel.json.gz`, counts with no prose. Rebuild them
with `build_word_year_counts.py` and `build_member_cache_panel.py`; their
downstream results are all tracked.

See `SOURCE-LICENCES.md` for each publisher's terms, chamber by chamber.
