# Source licences, and how we decide what may be committed

Two questions this answers: under what terms each corpus was collected, and
why the pre-push guard blocks what it blocks. Written 2026-09-13 because the
rules existed only as patterns in `.githooks/pre-push` and `.gitignore`, with
the reasoning spread across commit messages.

**Not legal advice.** This records what each publisher's own notice says, with
the date it was read. Where the answer turns on more than a published
permission, that is said plainly rather than resolved.

## The rule the guard implements

Three classes, and the test for each.

| class | committed? | test |
|---|---|---|
| **Our own code and derived results** | yes | carries no source text: scripts, scores, verdicts, counts, codings, ids. This is nearly everything. |
| **Our own model output** | yes | text a model produced *from a prompt*, not *from a passage* — `claude_gen/`, `rlhf_gen*/`. 34 files, explicitly exempted in the hook. |
| **Source text, and anything embedding it** | no | verbatim transcripts, extracted-speech pools, and close paraphrases that retain the original's expression. Held locally, rebuildable — see `REPRODUCTION-PURGED.md`. |

The guard enforces this three ways, because no single test catches everything:
a **path rule** (corpus directories), a **size gate** (10 MB any file, 2 MB for
text formats), and a **content backstop** (20+ prose runs of 300+ characters in
any added text file over 100 KB). The backstop exists because extracted-speech
pools kept appearing under new names below the size gate.

The permissive half matters as much: extraction scripts under `us/` and
`provinces/` are allowlisted *past* the corpus path rule, because without them
a recorded `seg_id` cannot be resolved back to the transcript it names and 17
of 21 chambers stop being reproducible.

## What the publishers say

Verified by reading each publisher's own notice on the date shown. Chambers
without a date have **not** been checked; do not rely on the guess column.

| chamber | terms | verified |
|---|---|---|
| CA-FED (House of Commons) | Speaker's Permission: "Reproduction of the proceedings of the House of Commons and its Committees, in whole or in part and in any medium, is hereby permitted provided that the reproduction is accurate and is not presented as official." Excludes "reproduction, distribution or use for commercial purpose of financial gain." Parliamentary privilege reserved; a permitted reproduction is not a publication under the authority of the House. | 2026-09-13 |
| NB (Legislative Assembly) | Site disclaimer: "Content herein may be reproduced for educational purposes, private study, research, reporting, or in order to prepare a newspaper summary, without charge or request for permission." Content is "strictly as is"; printed Bills take precedence. | 2026-09-13 |
| AB, BC, MB, NL, NS, ON, SK | not checked | — |
| NSW, QLD, SA, TAS, VIC, WA | not checked | — |
| NI, SCO, WAL | not checked | — |
| US-HOUSE, US-SENATE | not checked. The Congressional Record is a US Government work; §105 puts federal government works outside copyright, which is why the corpus was collected from GovInfo without a permission step. Confirm before relying on it in print. | — |
| O\*NET-SOC 30.3 (occupation anchors) | CC-BY 4.0. Redistributable with attribution, which the pre-registration and METHODOLOGY carry. This is why `market_anchors/occupation_titles.txt` and `onet_occupation_data.csv` are committed despite tripping the prose backstop — a standing false positive. | 2026-08-21 |

Both verified permissions cover our use: non-commercial academic research. Both
are permissions to **reproduce**, and neither is a licence to redistribute a
whole corpus, which is the separate reason the segment stores stay out.

## The case the permissions do not settle

The bypass **variants** (`detector_bench_input.jsonl`,
`detector_bench_scored_input.jsonl`, `bypass_text/`) are model rewrites of
specific NB and CA-FED segments. Measured against their sources across the 180
variants that pair: median similarity **56.9%** (max 91.7%), median longest
verbatim run **20 words** (max 111), and **94 of 180 carry a 20+ word verbatim
stretch**. They are not clean model output; they embed the source.

Two things follow, and the second is the reason they stay out:

1. Canada's Speaker's Permission conditions reproduction on being **accurate**.
   A paraphrase is not an accurate reproduction, so the permission is not
   obviously the instrument that covers a modified version — that is an
   adaptation question, not a reproduction one. NB's wording ("reproduced for
   ... research") is broader but has the same shape.
2. The fallback in Canada is **fair dealing**, which is not the US
   "transformative use" test. Fair dealing asks first whether the purpose is
   one of the enumerated ones — research and private study are — and then
   whether the dealing is fair on the *CCH* factors: purpose, character, amount,
   alternatives, nature of the work, and effect on the market. "Transformative"
   is a US fair-use concept and does not map onto those factors directly.
   Research use weighs well on purpose; publishing 341 near-copies of specific
   speeches weighs less well on character and amount.

Nothing is lost by holding them: `detector_transfer.py` reads only the scores
CSVs, which keep every `seg_id` and all four detector metrics, so the arm
reproduces exactly. Private copies are kept off-repo so a future detector can
still be run against the same strings.

## If this becomes load-bearing

Getting a definite answer means reading each remaining chamber's notice, and
for the variants, deciding whether to publish adaptations at all rather than
reasoning from the reproduction permissions. Until then the conservative rule
stands: derived results in, source text and anything embedding it out.
