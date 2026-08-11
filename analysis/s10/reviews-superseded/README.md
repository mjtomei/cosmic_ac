# Superseded reviews — v1.0 / v1.1 protocol era

**These review a version of S10 that no longer exists. Do not read them as
current criticism, and do not cite their findings.** Archived 2026-08-11 so
that a fresh review can be run against the study as it now stands.

| file | what it is |
|---|---|
| `METHODOLOGY-REVIEW.md` | round-1 adversarial review, written against `METHODOLOGY.md` as of 2026-08-02 |
| `METHODOLOGY-REVIEW-2.md` | round-2, written against `METHODOLOGY.md` as of 2026-08-03, after the round-1 fixes |
| `REVIEW-RESPONSES.md` | our responses to both rounds |
| `REVIEW-RESPONSES.pdf` | render of the above |
| `REVIEW-RESPONSES-root-copy.pdf` | an earlier render that had been sitting loose in the repo root (differs from the one above; kept only so nothing is silently discarded) |

## Why they are stale

They target the **frequency/lexicon arm run under protocol v1.0–v1.1** — the
Kobak-style excess-vocabulary estimator — at a time when that arm carried
inferential weight. Since then:

- The lexicon arm was **demoted from inferential to descriptive** after
  `in_time_placebo.py` showed it has no trend control (§3.3 of the write-up).
  Most of round 2's severity ratings concern an arm that no longer makes the
  claims being attacked.
- The study's headline moved to a **calibrated commercial detector** (Pangram 4)
  with per-chamber pre-AI controls — 1,260/1,260 specificity — which did not
  exist in the reviewed version.
- Whole arms were added afterwards and are unreviewed: the genre ladder, the
  Opus screen and its effort A/B, the cohort decomposition, the OLMo
  post-training ladder, the quality arm across four stages, and the bypass
  study.
- Numbers quoted throughout (e.g. the 7.5% New Brunswick prevalence) predate
  the Pangram model-tier fix of 2026-08-09 and the corpus expansion to 19
  chambers.

## What is still worth carrying forward

Not everything here is obsolete, and a fresh review should not have to
rediscover these:

- **Frequency × dispersion matching.** Round 1 found the word-level
  AI-preference score was largely a Hansard-rarity index; dispersion-matched
  placebos were the fix and are now standard in the frequency arm.
- **The p-hacking discipline** — importing an external word list rather than
  choosing one after looking at the data — survived and is still the design.
- **`p = 0` means resolution-limited, not measured.** Adopted, and the
  write-up states it that way.
- **The Kobak content list is PubMed's content** and only 105 of 462 words
  appear in legislative text. This observation is the origin of the substance
  channel item now in §8.6.

## Current documents

`../METHODOLOGY.md` is the live methodology write-up. The study write-up is
`../S10-WRITEUP-DRAFT.md`; prior-art verification is `../PRIOR_ART.md`.
