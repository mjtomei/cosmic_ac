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
| **Source text, and anything embedding it** | no, with one named exception | verbatim transcripts and extracted-speech pools stay out, rebuildable — see `REPRODUCTION-PURGED.md`. The exception is the **reproduction substrate**: the four files a replicator needs to check our scoring, allowlisted by name and covered by `DATA-NOTICE.md`. |

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

| chamber | terms | status | verified |
|---|---|---|---|
| **CA-FED** (House of Commons) | Speaker's Permission: "Reproduction of the proceedings of the House of Commons and its Committees, in whole or in part and in any medium, is hereby permitted provided that the reproduction is accurate and is not presented as official." Excludes "reproduction, distribution or use for commercial purpose of financial gain." Privilege reserved; a permitted reproduction is not published under the authority of the House. | permissive | 2026-09-13 |
| **NB** (Legislative Assembly) | Site disclaimer: "Content herein may be reproduced for educational purposes, private study, research, reporting, or in order to prepare a newspaper summary, without charge or request for permission." | permissive | 2026-09-13 |
| **SCO** (Scottish Parliament) | Scottish Parliament Copyright Licence, aligned to OGL v3.0. Commercial use permitted. Attribution: "Contains information licensed under the Scottish Parliament Copyright Licence". Must not be used for party political purposes or advertising endorsement, or in a way suggesting official status or SPCB endorsement. | permissive | 2026-09-13 |
| **NI** (NI Assembly) | Official Report re-use permitted under the Open Government Licence v3.0 unless otherwise stated. | permissive | 2026-09-13 |
| **US-HOUSE, US-SENATE** | 17 U.S.C. §105: "Copyright protection under this title is not available for any work of the United States Government." GovInfo recommends "customary credit should be given". Caveat: a government publication may contain third-party copyrighted material, which §105 does not release. | public domain | 2026-09-13 |
| **ON** (Legislative Assembly of Ontario) | The Speaker permits display, print, reproduction and use of **excerpts** without charge, provided the use is "reasonable, fair and non-commercial" and credits the Assembly; subject to parliamentary privilege; not an acknowledgement of use under the Assembly's authority. | permissive for excerpts | 2026-09-13 |
| **NSW** (Parliament of NSW) | May copy, distribute, display and download, provided the use is not for "advertising, satire or ridicule, or to misrepresent members of Parliament", and provided the notice "© State of New South Wales through the Parliament of New South Wales" is included. **Permission is required to charge for access, or to modify the material.** | conditional — notice required | 2026-09-13 |
| **VIC** (Parliament of Victoria) | The Creative Commons licence covers only Library research publications. "All other material on the Parliament of Victoria website is copyright." No general reuse grant found for Hansard. | not clearly permitted | 2026-09-13 |
| **BC** (Legislative Assembly of BC) | "The copyright in all material contained herein is claimed by the Legislative Assembly and the King's Printer ... and rests with His Majesty the King in Right of the Province of British Columbia." Reproduction "by any means for financial gain, or other than **personal use**" requires "the express written consent of the Speaker". | **restrictive** | 2026-09-13 |
| MB | Manitoba publishes a copyright page (gov.mb.ca/legislature/copyright.html) that reads as the BC-style Speaker-consent model. **Not read directly — do not rely on this row.** | unverified | — |
| AB, NL, NS, SK | not checked | unverified | — |
| QLD, SA, TAS, WA | not checked. Queensland publishes a copyright page but it refused automated fetch; read it by hand. | unverified | — |
| WAL (Senedd Cymru) | not checked; the copyright page moved and was not located. UK-wide practice is OGL, but that is an assumption, not a reading. | unverified | — |
| **O\*NET-SOC 30.3** (occupation anchors) | CC-BY 4.0, redistributable with attribution, which the pre-registration and METHODOLOGY carry. This is why `market_anchors/occupation_titles.txt` and `onet_occupation_data.csv` are committed despite tripping the prose backstop — a standing false positive. | permissive | 2026-08-21 |

### What this means for what we published

The **variants** — the files this was really about — draw only on NB and CA-FED,
both permissive. That half is sound.

The **verbatim** files are the problem, and it is the reverse of where I
expected it. `detector_bench_controls.jsonl` carries 60 segments from each of
twenty chambers and `flagged_hits_pool.json` another 316 across the same
spread, so they include **60 + 20 rows of British Columbia Hansard**, whose
terms permit personal use only absent the Speaker's written consent, and
**35 + 14 rows of Victoria**, which publishes no general reuse grant. NSW rows
are permitted but require a copyright notice we do not yet carry.

Most of these cover non-commercial academic research. All are permissions to
**reproduce**, and none is a licence to redistribute a whole corpus, which is
the separate reason the segment stores stay out. Two — BC and VIC — do not
clearly permit republication at all, and NSW permits it only with an
attribution notice.

## The variants: adaptations, published deliberately

The bypass **variants** (`detector_bench_input.jsonl`,
`detector_bench_scored_input.jsonl`) are model rewrites of specific NB and
CA-FED segments. Measured across the 180 that pair with a source: median
similarity **56.9%** (max 91.7%), median longest verbatim run **20 words** (max
111), and **94 of 180 carry a 20+ word verbatim stretch**. They embed the
source rather than replacing it.

**Decision, 2026-09-13 (Matthew): they ship.** They are required to reproduce
the result. `bypass_rewrite.py` seeds only its choice of in-context examples,
not the model's sampling, so re-running produces different strings — nobody,
including us, can regenerate them. Without them a reader can recompute our
numbers from the scores CSVs but cannot check that those scores belong to that
text, which is trust rather than replication. The same reasoning admits
`detector_bench_controls.jsonl` and `flagged_hits_pool.json`: recoverable in
principle from their `seg_id`s, but only by someone who has rebuilt all twenty
corpora, and the flagged pool's builder additionally reads gitignored RTF
submissions.

Note which half is the harder case, because it is the reverse of the intuition.
The **verbatim** rows are the easy ones: accurate, non-official, non-commercial
reproduction is exactly what the Canadian Speaker's Permission and the NB
research clause describe. The **modified** rows are the ones those permissions
do not obviously reach, since both condition on reproduction being *accurate*,
and a paraphrase is not — that is an adaptation question.

The fallback there is Canadian **fair dealing**, which is not the US
"transformative use" test. Fair dealing asks first whether the purpose is
enumerated — research and private study are — and then whether the dealing is
fair on the *CCH* factors: purpose, character, amount, alternatives, nature of
the work, and effect on the market. Research purpose weighs well; 341
near-copies of identifiable speeches weigh least well on amount and character.
What reduces the exposure is that the set is a bounded research sample rather
than a corpus, that it competes with nothing (the chambers give the originals
away), and that every row is labelled an adaptation and marked not-official in
`DATA-NOTICE.md`, so no reader can mistake a rewrite for something a member
said.

This is a considered call, not a settled legal answer. If it ever needs to be
firm, the route is a written application to the Office of the Speaker, which
the Canadian notice provides for.

## If this becomes load-bearing

Getting a definite answer means reading each remaining chamber's notice, and
for the variants, deciding whether to publish adaptations at all rather than
reasoning from the reproduction permissions. Until then the conservative rule
stands: derived results in, source text and anything embedding it out.
