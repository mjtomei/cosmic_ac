# Data-presentation principles (distilled) — the workaround corpus

We do not have Tufte, Cleveland, Few, or Wilkinson on disk (copyrighted
books). This is the legitimate substitute: a distillation from the canon's
in-weights knowledge plus **freely-published downstream works** that carry
it forward, for priming the data-presentation generator. Sources named per
item; this is our own synthesis, not reproduced text.

## Free downstream references (fetchable, canonical)
- **Claus Wilke, *Fundamentals of Data Visualization*** — clauswilke.com/dataviz
  (full book, free). Modern operationalisation of Tufte/Cleveland. Fetched
  and distilled 2026-09-01 (below).
- **Kieran Healy, *Data Visualization: A Practical Introduction*** — socviz.co
  (full book, free). Complementary, more workflow-oriented.
- **Cleveland & McGill graphical-perception ranking**, replicated openly by
  **Heer & Bostock, "Crowdsourcing Graphical Perception" (CHI 2010)** — the
  empirical ordering of how accurately readers decode visual encodings.
- **The bundled `dataviz` skill** (loadable on demand) — a validated,
  actionable house reference: form choice, mark specs, colour validation,
  the anti-pattern catalogue.

## Checklist (Wilke, with Tufte/Cleveland lineage noted)
1. **Proportional ink** (Tufte's data-ink → Wilke ch.17): the amount of ink
   must be proportional to the quantity — no truncated bars, no distorted
   areas.
2. **Encoding by decodability** (Cleveland–McGill / Heer–Bostock): prefer
   position and length over angle, area, and colour-intensity, which readers
   decode less accurately. Reserve the weaker channels for the less precise
   comparisons.
3. **Right form for the data's job** (Wilke ch.5–16): amounts, distributions,
   proportions, relationships, and trends each have appropriate forms; pick
   by the comparison you want the reader to make, and consider whether the
   answer is a chart at all (sometimes a number or a small table wins).
4. **Beat overplotting** (ch.18): transparency, jitter, 2-D histograms or
   contours when points collide — every datum must remain interpretable.
5. **Direct labels over legends** (ch.20): label series in place; a legend
   is a lookup tax. Redundant coding (colour + label) lowers cognitive load.
6. **Colour with intent** (ch.4,19): sequential = one hue light→dark;
   diverging = two hues + neutral midpoint; categorical = a fixed, ordered,
   CVD-safe set — never a rainbow, never colour as the only cue.
7. **Small multiples** (Tufte → ch.21): repeat one design across a facet to
   compare many series without clutter, rather than overloading one panel.
8. **Honest, readable axes** (ch.3,23–24): zero-baseline where the encoding
   implies it (bars); adequate tick/label sizes; state units.
9. **Minimise non-data ink / chartjunk** (Tufte): recessive gridlines and
   frames; no decoration that carries no information.
10. **Show the story, and the uncertainty** (ch.29): guide the eye to the
    finding; show error/interval rather than implying false precision.

## For THIS paper specifically (the review's job)
Apply the above to the study's committed tables and figures: are the
class/era panels, the tenure-profile curves, the altitude U, and the
prevalence tables using the most-decodable encodings? Do tables mix
estimands in one column (a flagged defect)? Are quintile/level bins and
CIs shown honestly? Proposals target these, under the same faithfulness
gate (no number/claim may change — only its presentation).
