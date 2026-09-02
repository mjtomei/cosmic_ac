# Review round 2 — prose/structure pass: morning report (2026-09-02)

## Bottom line

The multi-model writing pass ran overnight — a §4.6 trial first, then the whole
paper. It works end-to-end. A seven-lab panel (Anthropic, OpenAI, Google, xAI,
Moonshot, Alibaba, DeepSeek) plus two Fable generators proposed changes; a
ground-truth faithfulness gate screened them for data integrity; the blind,
self-excluded panel voted on each with a multi-factor ballot. **Nothing was
applied — every change is yours to gate.**

**Read this first:** `analysis/s10/REWRITES-round2/round2-all.md` (whole paper).
It opens with a composite-ranked triage index, then lists every change in
document order with current/proposed text, the faithfulness verdict, and all
seven ballots. The trial is `round2-4.6.md`. Raw data: `*.proposals.json`,
`*.votes.json`, `*.result.json`.

## What the full pass produced

- 63 proposals → 63 candidates → 62 passed the data-faithfulness gate, **1
  dropped** → **60 accepted** (majority keep), 2 rejected on the vote.
- Coverage: Abstract, §1 (10 changes), §§2–9, appendices. **45 prose rewrites +
  15 structural reorganizations.**
- The 15 structural moves are the holistic value-add you asked for (cross-section
  reorg a per-section pass can't see), e.g.:
  - move §6 (norms scan) to after §8.2;
  - move Related Work (§7) to after §4 Results;
  - relocate §8.6 Future Work to a standalone appendix so Discussion closes on §8.5;
  - split §4.9 into a Quality arm and a Detector arm;
  - move §4.8 Permeation up to after §4.6b.

### Per-seat: proposed vs accepted (full pass)

| seat | proposed | accepted | faith-dropped | vote-rejected |
|---|--:|--:|--:|--:|
| xAI grok-4.6 | 12 | 12 | 0 | 0 |
| OpenAI gpt-5.6-sol-high | 12 | 11 | 0 | 1 |
| Alibaba qwen3.8-max | 10 | 10 | 0 | 0 |
| Fable gen-prose | 10 | 10 | 0 | 0 |
| Anthropic fable-5 (panel seat) | 8 | 7 | 0 | 1 |
| Fable gen-dataviz | 6 | 6 | 0 | 0 |
| DeepSeek v4-pro | 4 | 3 | 1 | 0 |
| Google gemini-3.1-pro | 1 | 1 | 0 | 0 |
| Moonshot kimi-k3 | 0 | 0 | 0 | 0 |
| **total** | **63** | **60** | **1** | **2** |

Trial (§4.6) for comparison — Kimi worked there: grok 7/7, alibaba 7/6,
anthropic-seat 6/6, openai 6/5, **kimi 5/5**, gen-prose 5/5, gen-dataviz 5/4,
deepseek 3/1, gemini 1/0. Total 45 proposed, 40 accepted.

## How to read the verdicts

- **Faithfulness (data) is the hard gate**, and I made it read the actual
  manuscript as ground truth rather than trusting the proposer's quoted text. It
  caught 1 in the full pass — C44 deleted a recorded finding ("the best-performing
  form is a folk category") while preserving the numbers — and 4 in the trial
  (dropping a "short of significance" qualifier, deleting an "and found"
  confirmation, adding an unverifiable per-cohort count). Per your steer it
  protects data only; interpretation, framing, and hedging were free to change.
- **Keep-rate is high (95%) — be aware.** Proposals are pre-constrained to
  faithful presentation improvements, which are usually net-positive, so the
  binary keep vote is a low bar. But the panel does discriminate: composites span
  12.3–16.7 (mean 14.6), it rejected 2, and the ballots are substantive (e.g.
  "collapses a doubled, self-contradictory caveat into one plain statement";
  "all counts 13/35, 5/35 survive intact"). Treat "accepted" as *surfaced with
  panel support*, use the composite ranking to prioritize, and make the call.
  **A single round cannot separate the two explanations** — "the draft had that
  much slack" and "the panel is generous" predict the same 95%. The discriminating
  test is iteration: re-run the pass on the revised text and watch the proposal
  rate. If it decays, the slack was real and got spent; if proposals keep arriving
  at the same rate indefinitely, that is churn, and the generosity reading wins.
- Every prose diff is anchored to verbatim draft text (60/63; the 3 exceptions
  are structural gists, correctly flagged), so accepted prose changes apply cleanly.

### If we required unanimity

Of the 62 candidates that reached a vote, raising the bar costs less than the 95%
keep-rate suggests — the votes are concentrated at the top:

| bar | accepted |
|---|--:|
| majority (≥4/6) — what the report uses | 60 |
| supermajority (≥5/6) | 56 |
| **unanimous (6/6)** | **51** |

All 51 unanimous winners had a full six-voter panel, so none is unanimity-by-
small-n. **14 of the 15 structural reorganizations are unanimous** — the
cross-section moves were the least contested work in the pass. Of the 9 changes
unanimity would drop, 8 are prose (the ninth is C25, below), and they score lower
on the independent multi-factor scale too (mean composite 13.6 vs 14.9), so the
binary and the factors agree about which changes are marginal. Unanimity would also zero out
Gemini's contribution: its single proposal (C21, a §1 move) went 5/6.

Unanimity rate by proposing family: Alibaba 10/10, Fable 22/24, xAI 10/12,
OpenAI 8/12, DeepSeek 1/3, Google 0/1.

The triage index in `round2-all.md` now marks unanimous rows, so you can skim at
whichever bar you prefer.

**Correction — a backstop that was wrong, now removed (2026-09-02).** The
original `decide()` let any single voter's `faithfulness: fail` kill a change
outright, and my structural rubric told voters to fail a move that would "strand
a reference." That combination rejected **C25** — a §4.2 findings-first
reorganization approved 5/6 — because OpenAI judged it would strand two "below"
references to the chamber table. That is the wrong rule twice over: the other
five voters checked and found nothing stranded (DeepSeek: "no data dependency or
cross-reference is stranded"), and even where a reference *would* strand, the
remedy is to update the reference or move the table, not to reject the
reorganization. Per Matthew: a companion edit is a dependency to carry out, not a
disqualifier.

Fixed in `round2_prose.js`: the voter field is now `data_faithful` (data only),
stranded references and figure relocation go in a new `dependencies` field that
is explicitly never a reason to reject, and the acceptance rule no longer treats
a voter's self-report as a hard gate — the ground-truth faithfulness stage
remains the authoritative data check. Applied to this run's data, that restores
C25 and moves the totals from 59 to **60 accepted** (trial: 39 to 40). Any
companion edits voters noted now render on the change entry instead of silently
killing it.
