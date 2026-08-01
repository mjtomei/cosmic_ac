# The Performance Commons

Work in progress toward a paper, plus the studies, notes, and outlines behind it.

**The argument.** The gap between what computers deliver and what their silicon
could deliver is a collective-action problem within and across the computing
stack — not a limit of physics. Continuous optimization is an under-provided
public good: everyone benefits, nobody is paid to supply it, so it goes unbuilt.
Machine intelligence is inoculated against that problem, and so exposes it.

**Where it goes.** The successor in progress, *Towards the Cosmic AC*, makes the
same argument one scale up. Human societies have always preserved intelligence
outside individuals — in language, archives, offices, law, firms, markets, and
professions, institutions that survive the replacement of every person inside
them. Open source carried that inheritance into machines. Machine intelligence
is now beginning to make it active: reading the inheritance, recognising where
old techniques apply, and recombining what the commons preserves. What emerges
is not one final machine but a compute commons — a persistent system through
which intelligence inherits prior work, recruits new embodiments, and maintains
itself. The measured argument above is the first component of that account.

The prior essay in the sequence, on how a machine mind's continuity resides in
weights, records, conversations, users, and institutions rather than in any
running instance, is [coherence](https://github.com/mjtomei/coherence) — the
source of this project's inoculation and monoculture threads. It is
self-flagged as internally reviewed only.

| | |
|---|---|
| `the-performance-commons.md` / `-2col.pdf` | The paper. Nine sections plus appendix; figures and tables built by `build/build.sh`. |
| `outline-cosmic-ac.md` | Working outline for the wider successor, *Towards the Cosmic AC* — the compute commons argued at societal scope. |
| `towards-the-cosmic-ac-outline.docx` / `-v2.docx` | Structural outlines for the same, drafted in parallel with ChatGPT. |
| `drafts/` | Prose drafts of sections not yet placed. |
| `studies-and-work-log.md` | Every empirical effort behind the argument — done, committed, and candidate — with a dated log of what has actually run. |
| `analysis/` | Data, models, and scripts. Every novel number has an artifact here with its sources and assumptions. |
| `plans/` | Per-study session plans. |
| `reading/` | The three literature collections behind the argument — 219 papers, tiered, with recommended reading orders. |

Build: `bash build/build.sh` (needs `matplotlib markdown weasyprint`).
