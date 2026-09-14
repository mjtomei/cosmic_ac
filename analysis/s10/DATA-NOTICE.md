# Notice for the parliamentary material in this directory

Four files let the detector arms be checked rather than taken on trust. Two
carry text; two carry pointers to it.

| file | rows | what it holds |
|---|---|---|
| `detector_bench_input.jsonl` | 406 | **text** — 341 machine-rewritten **variants** plus the 65 unmodified segments they derive from, all from NB and CA-FED |
| `detector_bench_scored_input.jsonl` | 406 | **text** — the same set as submitted for scoring |
| `detector_bench_controls.jsonl` | 1,255 | **pointers** — pre-2022 human controls across twenty chambers, as `text_sha256` + `n_chars` |
| `flagged_hits_pool.json` | 316 | **pointers** — the estimator's flagged hits, same form |

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

## The two that do carry text

`detector_bench_input.jsonl` and `detector_bench_scored_input.jsonl` hold text
because no committed script can regenerate it: `bypass_rewrite.py` seeds only
its choice of in-context examples, not the model's sampling, so re-running it
yields different strings — nobody, including us, can reproduce these. A hash
would point at something no reader could obtain.

Both draw only on the **House of Commons of Canada** and the **Legislative
Assembly of New Brunswick**. Canada's Speaker's Permission allows reproduction
"in whole or in part and in any medium ... provided that the reproduction is
accurate and is not presented as official", excluding commercial use; New
Brunswick permits reproduction "for educational purposes, private study,
research, reporting ... without charge or request for permission".

**These reproductions are not official.** They are not published under the
authority of any House, and the absolute privilege attaching to proceedings
does not extend to them. They are reproduced for **non-commercial academic
research**. Where a chamber's own record differs, that record governs.

### The variants are adaptations, not reproductions

341 of the 406 rows in each file are text a language model **rewrote**. Every
one is a modification of a real speech and must not be read, quoted, or cited
as anything a member said. They are marked `"kind": "variant"`, carry a run
label (`nb_v3`, `go_all`), and their `seg_id` ends in a variant suffix
(`...|r1v3`) distinguishing them from the segment they came from. The remaining
65 rows are marked `"kind": "original"` and are unmodified.

Measured against their sources, the variants retain a median 56.9% of the
original wording, and 94 of 180 keep a verbatim run of 20 words or more (max
111). They are close paraphrases, not fresh compositions — which is why the
reproduction permissions above, both of which condition on accuracy, are not
the instrument that covers them; that rests on fair dealing for research.

## What is not here

The corpora themselves. What is here is the sample the published detector
results were computed on, in the least redistributive form that still lets a
reader check them.

See `SOURCE-LICENCES.md` for each publisher's terms, chamber by chamber, and
`REPRODUCTION-PURGED.md` for rebuilding anything held back.
