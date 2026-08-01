# Reading this work: what S10 claims, and what it does not

**Read this before the data files.** This directory contains a measurement of
how much machine-generated text appears in New Brunswick legislative Hansard,
including per-segment detector outputs with speaker names attached. That data is
easy to misread, and the misreading is the opposite of the finding.

## What this is

An observation about **the presence of machine intelligence in a legislature** —
one instance of a substitution happening across institutions generally. The
speech analysed is public speech by public officials in their official capacity,
taken from the official published record (Hansard). Nothing here involves
private communications, and nothing was obtained by any means other than
downloading the public record.

The forward-looking work this supports is constructive: how to build systems
that incorporate machine intelligence *without* the decay of societal
institutions. The quality arm — measuring deliberative quality alongside
provenance — exists because measurement is the precondition for optimising
toward that goal rather than away from it. If machine intelligence is entering
institutional speech (it is), the useful questions are what it does to the
quality of that speech and how to aim it deliberately.

## What this is NOT

**It is not an allegation of wrongdoing, and no finding here should be reported
as one.** Legislative speech has always been drafted by others — staffers,
speechwriters, party researchers, committee analysts. That is the ordinary,
disclosed, entirely legitimate operation of a legislature. "Machine-drafted" and
"not personally written by the speaker" are *different claims*, and only the
first is measured here. A member whose remarks were drafted with a model has
done nothing that a member whose remarks were drafted by a staffer has not done.

The argument this evidence serves depends on that distinction rather than being
damaged by it: the point is that **an office is a socket**. What plugs into a
figurehead's role has always been variable, so machine intelligence in that slot
is a substitution the system already performs routinely and does not find
strange. Reporting the data as a scandal about individuals inverts the finding.

## What the numbers support, and at what confidence

The study's power is in the **rate**, not in any individual verdict.

- **Aggregate (strong).** Corrected prevalence τ̂ ≈ 8.3% of 2025–26 segments
  [95% CI 4.6–14.6], via Rogan-Gladen with sensitivity and specificity both
  measured **in-domain** (40/40 synthetic legislative speech; 60/60 pre-2022
  control) rather than assumed from published benchmarks. Supporting evidence:
  a pre-2022 negative control establishing the false-positive floor, a placebo
  lexicon battery, a register control, clustered bootstrap, an independent
  instrument (Kobak rare-style subset, placebo p = 0.001), and a blinded
  Fable-5 judge cross-validating Pangram at AUC 0.936.
- **Per-segment (weaker — treat as indicative).** A classification on a single
  passage carries materially more uncertainty than the aggregate. In-domain
  Se/Sp of 1.0 were measured on modest samples; the honest reading of any one
  row is "this segment scored as machine-generated under these detectors," not
  "this person used AI." Rows are published for reproducibility and audit, which
  requires that they be checkable, and that is the only reason they are here.
- **Known limits, all stated in `PILOT.md` and the progress report.** Hansard is
  lightly edited by professional editors, which may normalise prose toward the
  flagged register. Bilingual chambers carry professional translation, scored
  separately or excluded. Edited-AI text is substantially invisible to zero-shot
  detectors, which is why the corrected estimate rests on adjudication rather
  than on the free detectors alone. One originating case (the clip that prompted
  the study) still awaits its **primary Hansard record**; until that arrives it
  is cited as a clip, not as the official record.

## If you are quoting this

Quote the rate and the method. If you name an individual, you are making a
claim the per-segment confidence does not support on its own — get the primary
record, and carry the staffer distinction in the same sentence. The study was
designed to measure an institutional trend, and it answers that question well;
it was not designed to adjudicate any particular person's authorship, and it
should not be used to.

Method, environment notes, and full results: `PILOT.md`,
`PROGRESS-REPORT-20260731.md`, and the plan in
`../../plans/S10-legislative-ai-detection.md`.
