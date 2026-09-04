# Applying structural changes — the protocol

Prose rewrites replace a quoted `current` passage with `proposed`, located by
locus and quote together rather than by exact match. Structural changes cannot — they
are natural-language instructions ("move to after §Y", "split before
'<quote>'"), so an agent executes them by judgment. This file is that agent's
brief, and the Apply phase of `workflows/round2_iter_all.js` points it at the
selected changes and the manuscript.

**Model:** run this on a strong model. The 2026-09-02 pass ran on
`claude-opus-5` and applied 10 reorganizations with no prose lost.

## How a run is executed (constraint, 2026-09-02)

**One workflow does the whole iteration.** `workflows/round2_iter_all.js` runs
Scope -> Propose -> Faithfulness -> Vote -> Synthesize -> Apply -> Verify, and is
invoked directly from a `claude-mixed` session. There is no runner script, no
tmux orchestration, and no hand-assembled second stage; earlier rounds had all
three and each was a place for the pipeline to drift out of sync with the draft.

Consequences worth knowing when you edit this protocol:

- **The section tiling is derived, never stored.** The Scope phase reads the
  draft's own headings and packs them into contiguous groups that each fit one
  read, then asserts the tiling covers every line with no gaps. The old
  hand-maintained `section_groups.json` went stale the moment a reorganization
  renumbered the paper, and iteration 1's agents were handed scopes naming a
  section that no longer existed. Do not reintroduce a stored copy.
- **Prose applies by judgment from the locus and the quote together.** The
  quoted `current` may be re-wrapped or drawn from a slightly earlier state of
  the draft, so it is read as a pointer to the passage rather than matched
  character by character. What must not move is the content: no number,
  statistic, sample size, interval or finding changes to make anything fit. Where
  the target is genuinely ambiguous, the change is skipped and reported.
- **No standing tooling in the loop.** There is no runner, no stored section
  map, no applier and no checker script. The integrity checks live in the Verify
  prompt and the agent re-checks until a full pass is clean. Prompts say what
  must hold, not which tool to reach for.
- **Which changes land is decided in the workflow script**, not by a separate
  tool: unanimity among whoever voted on that change, then best-composite wins
  among rival takes on the same passage or reorganization.
- **Models are named in the workflow, not in agent frontmatter.** Frontmatter
  only accepts names ending in `claude-*`; `agent()`'s `model` option takes the
  router's real names. Every workflow worker runs on the work subscription.

## Cuts, and the appendix that receives them

A cut is a **move**, never a delete. The material leaves the main text and
lands in `## Appendix F — Cut for length`, which is created on first use with a
one-line framing sentence and otherwise looks like the other appendices.

Executing one:

1. Remove the passage from the body.
2. Add its entry to Appendix F, carrying **every** number, interval, sample
   size and finding out of the removed passage verbatim, plus the proposal's
   one-sentence note on what it is and why it left.
3. Repair what the removal disturbs — a `§N` reference into the cut passage now
   points at Appendix F, a footnote defined inside it moves with it, and a
   transition sentence that leaned on it needs its seam closed.
4. If the proposal did not supply the receiving text, **skip it and say so**. A
   cut without its appendix half is a deletion wearing a cut's name, and the
   data gate should already have caught it.

Appendix F is not a graveyard for weak results. A result that did not survive
belongs in Appendix A, one that was superseded in Appendix B. F is for sound
material that does not earn its place in the reader's path — and the reader is
told where it went.

## Order: prose first, then structural

Not a convenience — the two steps fail differently, so the order is load-bearing.

Mechanical prose application depends on locating `current` **verbatim**.
Structural changes renumber sections, and renumbering rewrites the `§N`
references that sit *inside* prose passages. Run structural first and every
prose anchor containing a section reference stops matching, so those changes
silently fail to land. Agent-executed structural moves have the opposite
property: they locate blocks by content and judgment, so they tolerate prose
that has already changed underneath them.

**Run the brittle exact-match step first, the tolerant judgment step second.**

A consequence to expect: by the time the structural agent runs, the text no
longer matches what the panel saw, so a change's quoted locus may be slightly
stale. That is why the agent locates blocks rather than string-matching, and
skips anything it cannot identify unambiguously.

## Selection, before anything is applied

1. **Unanimous only**, and only changes that cleared the data-faithfulness gate.
2. **Highest scoring first.** Rival takes on one reorganization — same
   (section, action) — collapse to the best composite; the losers go to the
   review queue. Different actions on one section may be complementary (a move
   another proposal's split builds on), so those survive and the applier skips
   any residual conflict it meets.
3. Apply **in dependency order**, and one at a time.

## The agent's hard rules

- **Content is preserved verbatim.** These are moves, splits, and extractions.
  Never reword, condense, or "improve" a sentence while relocating it. Never
  drop a footnote, table, figure block, or code fence.
- **Never alter data**: no number, statistic, CI, p-value, or claim.
- **Cross-references must keep resolving.** Renumbering is part of the job.
- If a change is ambiguous, would lose content, or conflicts with one already
  applied, **skip it and say so**. A skipped change is fine; a corrupted
  manuscript is not.

## Final hygiene pass (added 2026-09-02 — do not skip)

A reorganization silently breaks things that live *outside* the moved text.
After the moves, sweep for all of it:

- **The LaTeX label map.** The PDF must never hard-code a section or appendix
  number: `latex/reformat.py` strips baked-in numbers, attaches semantic labels
  (`sec:prevalence`, `app:null`), and rewrites `§N` to `\cref{}` and
  `Appendix X` to `Appendix~\ref{}`. That map is keyed by the markdown's
  numeric prefixes, so **every renumbering desynchronizes it**. Re-walk every
  numbered heading and appendix and confirm its label is present and
  semantically correct — after the 2026-09-02 pass, §4.7 and §4.8 had their
  labels *swapped*, twelve headings had none, and three top-level sections
  pointed at the wrong content. Check the `[A-D]`-style regexes still cover the
  appendix range. Keep existing label names stable where the content is
  unchanged, so existing `\cref` targets keep working.
- **In-text references to moved material**: artifact tables, front-matter
  notes, and "see §N" asides that name a section by number.
- **Titles that describe content that moved out** of their section.
- **Pronouns orphaned by a split** — the new section's opening sentence may
  refer to an antecedent left behind. Repair minimally; name the referent.
- **Footnote definitions** stranded in a different section from their call
  sites (renders fine, but move them when clean).

## Building figures the panel asked for

A proposal may ask for a figure. It must NOT insert a reference to a file that
does not exist — the propose prompt now forbids that — but when a change argues
for a figure in its rationale, **building it is part of integration**. On
2026-09-02 two accepted changes (C59, C60) inserted `![](...)` references to
figures nobody had made, plus bracketed build notes addressed to the author;
the data gate passed them because no datum changed, and six voters approved the
described figure without anyone checking the file existed.

How to build one here:

1. **Plot only values that are already committed.** These figures render
   numbers the manuscript already reports; they are not new analysis. If a
   figure would need a value the paper does not have, stop and say so.
2. **Parse the numbers from the manuscript itself** rather than transcribing
   them, so the figure can never drift from the table beside it. See
   `plot_manuscript_figures.py`, which reads the tables out of the draft and
   asserts the expected row counts.
3. **Match the repo's figure style**: `matplotlib` with the `Agg` backend,
   direct labels over legends, a colourblind-safe palette (grey for context,
   `#D55E00` and `#0072B2` for the emphasised series), recessive grid, axes
   starting at zero where the quantity is a share, `dpi=150`.
4. **Render it and LOOK at it before calling it done.** The first slopegraph
   here passed every assertion and was still unusable: names collided at the
   left edge, values overlapped at the right, the subtitle sat on the title, and
   a de-collision fix then pushed labels outside the axes. Check label
   collisions, overflow, and geometry by eye, every time.
5. **Strip any build note or instruction to the author** that came in with the
   proposal. Those are not manuscript text.

## Wiring a figure into LaTeX — references must resolve, never be hard-coded

The PDF numbers figures itself; the markdown must never say "the figure below"
or name a figure number, because floats drift. For each new figure:

- Add the filename to **`FIGLABEL`** in `latex/reformat.py` with a semantic
  label (`chamber_prevalence_dotplot.png` -> `fig:prevalence-dots`). Without an
  entry the image is left as a bare `\includegraphics` — no float, no caption,
  no label — and the build prints `WARN: figure not found`.
- Put the caption in the markdown as an **italic paragraph immediately after
  the image**. `wrap_figures` looks for exactly that and warns `no caption
  after <file>` if it is missing, so the figure loses its caption silently.
- Give it a **`\cref` anchor in `figure_ref_anchors`** so the prose actually
  references it, keyed on a phrase that exists in the text. An unreferenced
  float has nothing tying it to its argument, and `figure_ref_anchors` warns
  when a keyed phrase does not match exactly once — treat that warning as an
  error, since it means the anchor silently did nothing.
- Verify in the generated `body.tex`: the figure appears inside
  `\begin{figure}` with a `\caption` and its `\label`, and at least one
  `\cref` points at that label.

## Iterate until clean

After applying, check the draft's integrity: every §N and Appendix reference
resolves to something that exists, every footnote use is defined, no heading or
section number is duplicated, every referenced image is on disk, every figure is
wired into the LaTeX transform, every numbered heading and appendix letter has a
label there, and the transform's appendix ranges still span the letters in use.
There is no checker script and deliberately so — write whatever throwaway checks
you need.

**Fix, re-run, repeat until it reports clean** — a fix can expose or create the
next problem, so a single pass is not enough. Escalate to the author only what
genuinely needs a judgment call (e.g. whether an appendix cascade is acceptable),
and say plainly what you left alone and why.
