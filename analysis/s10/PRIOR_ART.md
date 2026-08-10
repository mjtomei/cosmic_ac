# S10 prior art — detector studies of legislative speech

Surfaced 2026-08-09 by the AI-policy scan. **None of it is verified against
primary sources yet.** Figures below are as reported by the scanning agent;
pin them before any of this enters the paper.

## The two comparators

| | Rice | Pimlico Journal |
|---|---|---|
| Corpus | Australian federal Hansard, 124,734 speeches (64,642 post-ChatGPT scored) | UK House of Commons |
| Instrument | Binoculars + Fast-DetectGPT + an LLM scoring pass (0–10) | z-score excess-vocabulary analysis |
| Result | **No significant post-ChatGPT increase** | Increase detected |
| Reported FPR | ~8%, exceeding the corpus detection rate | not reported |

Neither used a calibrated commercial detector. Both predate S10 on chambers
that are in our corpus, so both must be engaged with directly.

## How S10 answers Rice

Not by impugning the detectors. Binoculars (Hans et al. 2024) and
Fast-DetectGPT (Bao et al. 2024) are published methods, and dismissing them
would not survive review.

The answer is calibration. **A reported 8% false-positive rate exceeding the
detection rate makes the null uninformative rather than negative** — at that
specificity a true prevalence of a few percent cannot be distinguished from
noise, so the study is not powered to find what S10 measures. This is an
argument about what the instrument can resolve, not about whether the authors
did their work properly.

S10's corresponding number is measured, not assumed: **423/423 specificity**
across four chambers, plus 2,400 pre-LLM segments in the Opus band screen
with zero flags, and every new chamber in the expansion buys its own 60-segment
pre-AI control rather than borrowing one. A chamber's false-positive rate
depends on its own editorial register, so specificity is not transferable.

## Why Pimlico's agreement is not corroboration

Pimlico's z-score method is the same family as S10's Kobak-lexicon arm, which
**we demoted from inferential to descriptive** after an in-time placebo showed
it carries no trend control (`in_time_placebo.py`). A method that agrees with
us while sharing the defect we found in our own version of it is weak support.
Treat it as a third result to explain, not as a second vote.

## The complication both studies run into

S10's permeation result — human speech drifting toward LLM register
independent of drafting — predicts exactly this split:

- **lexical z-score methods fire** on a real effect that is not machine
  drafting (Pimlico's positive)
- **detector methods get ambiguous**, because the human baseline is itself
  moving toward the thing being detected (part of Rice's null)

So the two prior studies may both be measuring something real and different.
The honest framing is not "we are right and Rice is wrong" but that
prevalence and permeation are separate quantities requiring separate
instruments, which is why S10 runs a calibrated detector for the first and
detector-independent tests for the second.

## Also flagged: transcript provenance

Several chambers now use AI/ASR in producing the record itself — reported for
NSW and WA Hansard, an approved Oireachtas use case for AI-drafted Journal
proceedings, and plenary transcription as the most common parliamentary AI
application in the EU (27 of 34 chambers). This confounds *any* detector study
of Hansard, prior or ours.

Measured locally rather than taken on report (`transcript_regime_check.py`):
NSW and WA are flat across 2006–2026 on sentence segmentation and contraction
density, so whatever they procured has not visibly changed the text.
**Tasmania is the chamber that actually moved** — contraction density 3.4 →
15.9 per 1,000 words across the windows, +364% — and its step falls between
the control and prevalence windows, so no pre-AI text exists in the current
regime to calibrate against. The corpus evidence and the procurement reports
point at different chambers.

## To verify before citing

1. Rice — author, venue, date, the 8% FPR and how it was derived, and whether
   "no significant increase" is a null result or an underpowered one in the
   authors' own words.
2. Pimlico Journal — author, date, method detail, whether the z-score baseline
   has any trend control.
3. The Sejm/EU survey claim that Oireachtas AI guidelines cover "members of
   parliament", which the Oireachtas's own documents do not support. Do not
   cite without the underlying document.
