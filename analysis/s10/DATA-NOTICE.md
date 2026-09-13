# Notice for the parliamentary text in this directory

Four files carry parliamentary text so that the detector arms can be checked
rather than taken on trust:

| file | what it holds |
|---|---|
| `detector_bench_controls.jsonl` | 1,255 pre-2022 human control segments, verbatim |
| `flagged_hits_pool.json` | the estimator's 316 flagged segments, verbatim |
| `detector_bench_input.jsonl` | 341 machine-rewritten **variants** of NB and CA-FED segments |
| `detector_bench_scored_input.jsonl` | the same variants as submitted for scoring |

## Attribution and status

Source proceedings are from the legislatures named in each row's `seg_id`,
principally the **House of Commons of Canada** and the **Legislative Assembly
of New Brunswick**, with control segments drawn from the twenty chambers listed
in `SOURCE-LICENCES.md`.

**These reproductions are not official.** They are not published under the
authority of any House, and the absolute privilege attaching to proceedings
does not extend to them. They are reproduced for **non-commercial academic
research**. Where a chamber's own record differs from anything here, the
chamber's record governs.

## The variants are adaptations, not reproductions

`detector_bench_input.jsonl` and `detector_bench_scored_input.jsonl` contain
text that a language model **rewrote**. Every row in them is a modification of
a real speech and must not be read, quoted, or cited as anything a member said.
Rows are marked `"kind": "variant"` and carry a run label (`nb_v3`, `go_all`);
the `seg_id` ends in a variant suffix (`...|r1v3`) distinguishing it from the
segment it was derived from.

Measured against their sources, the variants retain a median 56.9% of the
original wording, and 94 of 180 keep a verbatim run of 20 words or more (max
111). They are close paraphrases, not fresh compositions.

## Why they are here rather than held back

They are what makes the arm checkable. `bypass_rewrite.py` seeds only its
choice of in-context examples, not the model's sampling, so re-running it
yields different strings — nobody, including us, can regenerate these. The
control and flagged pools are recoverable in principle from their `seg_id`s,
but only by someone who has rebuilt all twenty chamber corpora, and
`flagged_hits_pool.json`'s builder additionally reads the gitignored Pangram
RTF submissions. Without these four files a reader can recompute our published
numbers from the scores CSVs but cannot verify that those scores belong to that
text.

The corpora themselves remain out of this repo. What is here is the sample the
published detector results were computed on — the minimum a replicator needs.

See `SOURCE-LICENCES.md` for each publisher's terms and the reasoning behind
what is and is not committed.
