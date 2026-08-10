# S10 quality expansion — genre-controlled DQI grading

**Self-contained.** Everything needed is in this directory. No context from the
session that produced it is required.

## What this settles

The quality arm of S10 found that AI-flagged legislative speech is
**better-formed and worse-engaged** than human speech — higher on formal
justification, lower on engaging opponents' demands. "Form up, deliberation
down."

Its unsolved confound is **genre**. AI concentrates in scripted formats
(Canada's Statements by Members shift more than Oral Questions), so the
finding may partly be *"scripted speech engages opponents less"* — a fact
about parliamentary procedure rather than about machine drafting.

This grades a pool balanced by construction so genre can be held fixed:

| | 2018–19 | 2025–26 |
|---|---|---|
| **SO31** — Statements by Members (60-second scripted set-pieces) | 140 | 140 |
| **OQ** — Oral Questions (not submitted in advance; unscripted) | 140 | 140 |
| **DEBATE** — Government Orders (prepared debate) | 140 | 140 |

840 Canadian House of Commons segments, 159,344 words, 120–360 words each,
English-original, non-chair speakers.

## How to run it

Two steps. The workflow is the expensive one.

```bash
# 1. grade  (Claude Code, in a session with Workflow available)
#    Point the Workflow tool at the script:
#      Workflow({ scriptPath: "<abs path>/grade_workflow.js" })
#    It runs 18 screen agents (low effort) + 84 grading agents (high effort).

# 2. analyse
python3 analyze.py                      # finds the newest run automatically
python3 analyze.py <workflow_run_dir>   # or point at one explicitly
```

`analyze.py` needs only Python 3 — no packages.

### Notes for whoever runs it

- **The grading phase wants a strong model at high effort.** The rubric is
  strict and the anchors exist to stop judges inflating scores; a weak judge
  produces the null we already have from an 8B pilot. The screen phase is
  deliberately low effort — it only needs to be correlated with truth.
- **~102 agents total.** The screen is 18 batches of 48; grading is 84
  batches of 10. Grading is small-batch on purpose: six ordinal judgements
  per segment degrade when batched large.
- If the run dies partway, `analyze.py` works on whatever completed — it
  harvests per-agent results from the transcripts and reports the counts it
  found. Below ~200 grades it refuses to analyse.

## Files

| file | what it is |
|---|---|
| `pool.json` | **blinded** — segment ID → text. No date, genre, speaker or era. This is what the judges read. |
| `key.json` | the unblinding key: ID → genre, era, date, speaker, seg_id, word count |
| `grade_workflow.js` | the workflow: blinded AI screen, then anchored DQI grading |
| `analyze.py` | descriptive tables, the genre-confound test, the leakage probe |
| `results.json` | written by `analyze.py` — per-segment grades joined to metadata |

## The rubric

Discourse Quality Index (Steenbergen, Bächtiger, Spörndli & Steiner 2003) —
the standard deliberation-quality scale for parliamentary debate, whose own
worked examples come from a 1998 House of Commons debate. Six dimensions:
justification (0–3), common good (0–2), respect toward others' demands (0–2),
counterarguments (0–2), constructive politics (0–2), evidence (0–3).

**The anchors in the prompt are load-bearing.** Measured on this corpus,
adding them moved constructive politics from 0.99 to 0.25 — matching
Steenbergen's own finding that a real Commons debate scores essentially zero
on mediating proposals. Without anchors, judges inflate justification and
constructive politics badly. Do not simplify the rubric text.

`ai_guess` is scored by the grading judge **as well as** by the separate
screen. That is deliberate: it is a leakage probe. If the quality differences
vanish once the judge's own AI-guess is controlled, the judge was detecting
style rather than measuring quality.

## Reading the output

`analyze.py` prints three sections in this order:

1. **DQI by genre and era** — establishes that the genres actually differ,
   which is the premise of the confound. If they don't differ, the confound
   was never real.
2. **The confound test** — the AI-quality association, first alone, then with
   genre and era fixed effects. **The second column is the one to quote.** If
   the association survives, the original finding stands; if it collapses,
   it was genre all along.
3. **Leakage probe** — correlation between the two independent AI guesses.

## Stage 2 — cross-chamber, after the Pangram batches return

`build_stage2.py` builds a second pool once Pangram verdicts exist for the
expansion chambers (US House, US Senate, federal Canada by genre, and the
provincial/Australian/UK-devolved chambers as their batches complete).

**What stage 2 adds:** an AI-versus-human quality comparison at scale, using
Pangram verdicts as the label rather than an LLM screen, across every chamber
with verdicts. It brings in a fourth country, the US House/Senate contrast,
and enough AI-labelled text to fix the power problem — the existing unbiased
comparison rests on **8 AI segments against 82 human**.

**What stage 2 cannot do:** control genre. Federal Canada is the only corpus
with a business rubric. The US Congressional Record's section field turned out
to be bill-text fragments and vote tallies (197 usable genre markers in 28,002
segments), and the sixteen other corpora were extracted with the core schema
only. Adding US genre would need re-extraction against CREC's granule
metadata — worth doing, not done.

**The design point is selection matching.** AI-verdict and Human-verdict
segments come from the *same* uniformly sampled prevalence stratum, so they
passed identical filters. New Brunswick's 576 confirmed-AI tail segments are
deliberately excluded despite being the richest AI-labelled source we have:
they were selected by screen score, so comparing them against random human
text would measure selection, not AI status.

Run: `python build_stage2.py`, then point `grade_workflow.js` at `pool2.json`
(the script prints the exact edits) and analyse with
`python analyze.py --key key2.json`.

## What this does *not* do

The **human-coded subsample** remains the true validation and is not part of
this. Repeat-pass reliability on the existing runs sits at or above the
published human inter-coder bar (justification r = 0.83 against their 0.716),
but self-agreement is not inter-coder agreement, and no amount of LLM grading
substitutes for a trained human coding a subsample against the same rubric.

This is also **one chamber**. Canada was chosen because its Hansard carries
the business rubric (`Statements by Members` / `Oral Questions` /
`Government Orders`) that makes the genre control possible at all. Provincial
corpora built later carry similar metadata if a replication is wanted.

## Provenance

Pool built 2026-08-09 from `analysis/s10/ca/segments_ca2.jsonl` (Canadian
House of Commons Hansard, ourcommons.ca XML, re-extracted with the
`OrderOfBusinessTitle` rubric). Cell sampling is seeded per cell
(`sha1(genre+era+"qx")`), so the pool is reproducible.
