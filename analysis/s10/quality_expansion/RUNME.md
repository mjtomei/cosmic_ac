# Run this on the other account

Self-contained. Copy this whole folder, open Claude Code in it, and paste the
commands below. Nothing else from the originating session is needed.

## What you are running

Two independent gradings of legislative speech against the Discourse Quality
Index (Steenbergen, Bächtiger, Spörndli & Steiner 2003). They answer different
questions and neither replaces the other.

| | stage 1 | stage 2 |
|---|---|---|
| pool | `pool.json` — 840 segments | `pool2.json` — 682 segments |
| source | federal Canada only | 22 chambers, 4 countries |
| AI label | blinded LLM screen, run in the same workflow | **Pangram verdict** (207 AI / 134 Mixed / 341 Human) |
| balanced on | genre × era, 140 per cell | nothing — selection-matched only |
| settles | **the genre confound** | **the power problem** |

Stage 1 is the one that matters for the headline claim ("AI-flagged speech is
better-formed and worse-engaged"), because it can hold genre fixed. Stage 2
cannot control genre — no corpus outside federal Canada carries a business
rubric — but it replaces an 8-vs-82 comparison with 341-vs-341.

## Commands — run stage 0 FIRST

```
# stage 0 — REPLICATION of the published v2 run: 241 segments (~25 agents, cheapest)
Workflow({ scriptPath: "<abs path>/grade_workflow.js", args: { stage: 0 } })
python3 compare_replication.py

# stage 1 — genre-controlled  (~102 agents: 18 screen + 84 grade)
Workflow({ scriptPath: "<abs path to this folder>/grade_workflow.js" })
python3 analyze.py

# stage 2 — cross-chamber, Pangram-labelled  (~83 agents)
Workflow({ scriptPath: "<abs path>/grade_workflow.js", args: { stage: 2 } })
python3 analyze.py --key key2.json
```

**Do stage 0 before the others and read its output.** It re-runs the exact
published v2 measurement — same 241-segment pool (`judge_blind_pool.json`), same rubric, verified byte-identical to commit 19deb97 — so it is a replication rather than a new
result. It is also the cheapest phase. If the group means shift materially or
any AI-vs-human gap flips sign, the "form up, deliberation down" finding was a
property of one run rather than of the instrument, and stages 1 and 2 are not
worth spending on until that is understood.

`analyze.py` needs only Python 3 — no packages. It finds the newest workflow
run automatically; pass a run directory explicitly if it picks the wrong one.

## Things that will bite you if nobody says them

**Use a strong model at high effort for the Grade phase.** The rubric is
deliberately strict and the anchors exist to stop judges inflating scores. An
8B pilot produced a null on this exact pool. The Screen phase is intentionally
low effort — it only has to correlate with truth, not be right.

**Do not reword the rubric.** It is lifted verbatim from `dqi_judge_v2b.js`,
and its anchors are **the original authors' own codings** of a 1998 UK Commons
debate on women's issues — not paraphrases. An earlier version of this package
silently shipped a 6-dimension rewrite that dropped `respect_groups` and the
`-1` sentinels; anything graded with that is a different instrument and is not
comparable to the existing v2 numbers. Measured on this corpus, anchoring
moved constructive politics from 0.99 to 0.25, matching Steenbergen's own
finding that a real Commons debate scores near zero on mediating proposals.

**`-1` is a code, not missing data.** `respect_demands` and
`respect_counterargs` take -1 when no other demand or counterargument is on
the table. `analyze.py` excludes those rows from the two means rather than
averaging them in — scoring "nothing to engage with" as worse than "engaged
badly" would manufacture a quality gap wherever AI text happens to be more
monologic.

**Two dimensions have no external exemplar, for principled reasons.**
`constructive` has none because Steenbergen's coded debate contained no
mediating proposals at all (which is itself why 2 is rare), and `evidence` is
our addition rather than a DQI dimension, so no authors' coding exists.

**`ai_guess` is scored twice on purpose.** Once by the screen, once by the
grading judge. That is a leakage probe, not redundancy: if the quality
differences vanish once the judge's own AI-guess is controlled, the judge was
detecting style rather than measuring quality.

**If the run dies partway, just run `analyze.py`.** It harvests whatever
completed from the transcripts and reports the counts it found. Below ~200
grades it refuses to analyse rather than report noise.

## Reading the output

Stage 1 prints three sections. **The second column of section 2 is the one to
quote** — the AI coefficient with genre and era fixed effects. If the
association survives it, the original finding stands; if it collapses, it was
genre all along. Section 3 reports how correlated the two independent AI
guesses are.

Stage 2 prints the same structure, but its genre column is `n/a` by
construction. Read its AI-vs-human contrast, not its genre rows.

## What this deliberately does NOT do

The **human-coded subsample** is the real validation and is not part of this.
Repeat-pass reliability on the existing runs sits at or above the published
human inter-coder bar (justification r = 0.83 against their 0.716), but
self-agreement is not inter-coder agreement.

Stage 2 excludes New Brunswick's confirmed-AI tail despite it being the
richest AI-labelled text available: those segments were selected *by screen
score*, so comparing them against random human text would measure selection,
not AI status. Everything in `pool2.json` comes from the same uniformly
sampled prevalence stratum, so AI and Human rows passed identical filters.
