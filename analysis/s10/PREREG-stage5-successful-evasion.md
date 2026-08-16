# Pre-registration: DQI of SUCCESSFUL evasions (stage 5)

**Frozen 2026-08-16, before grading.** Complements §4.9's attempted-evasion
arm (stages 3/4, where 61/63 graded rewrites did NOT clear the detector).
This arm conditions ON the Pangram outcome: it grades only rewrites that
reached a Human verdict — the complement Matthew requested.

## Sample
39 Human-verdict variants across 16 targets (NB v2, NB v3, GO all-31).
35 pairs / 15 targets are gradeable; one target (seg_id 2025-12-04#t1466w0,
4 variants) is dropped — its original text is absent from the corpus dumps.
Recorded as a coverage gap, not a result.

## Design
Each pair = (original segment, its evading rewrite). Both texts graded
blinded, opaque ids, interleaved (originals and variants non-adjacent),
arm hidden from the judge. Rubric: dqi_judge_v2b.js VERBATIM (the frozen
v2b DQI, seven dimensions + ai_guess). Two independent grading passes for
inter-pass reliability.

## Analysis, fixed
- Primary: paired difference (variant − original) per DQI dimension,
  variant level (n=35) and collapsed to target level (n=15, mean within
  target). Paired t and sign test per dimension.
- This ARM CONDITIONS ON THE OUTCOME by construction; it answers "given a
  rewrite that evaded, is its quality changed?" — NOT a per-attempt rate.
- Reported beside the attempted-evasion arm so both are visible: attempted
  (stages 3/4, mostly non-evading) and successful (this arm).
- ai_guess recorded but not used to select or adjudicate.

## What counts
Null on all dimensions in BOTH arms = evasion, attempted or achieved, does
not measurably change DQI. Any dimension moving only in this arm = a cost
that appears specifically when evasion succeeds — reported as such.
