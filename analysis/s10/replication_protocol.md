# Frozen replication protocol — AI-lexicon shift in legislative speech

**Version 1.0, frozen 2026-07-30** (git history is the timestamp; any later
change requires a new version number and is reported as a deviation).
New Brunswick is the **discovery corpus**: its analysis sequence was partly
exploratory and is disclosed in `PILOT.md`. Every subsequent corpus runs
THIS protocol verbatim, and only these pre-specified results enter the
cross-legislature combination.

## Hypothesis

After the deployment of conversational LLMs, the usage rate of
LLM-preferred style vocabulary in a legislature's official transcript
rises relative to its own pre-deployment baseline, beyond what
frequency-matched ordinary vocabulary does over the same window.

## Instrument (fixed, external)

The **style-annotated words** of Kobak, González-Márquez, Horvát & Lause,
*Delving into LLM-assisted writing in biomedical publications through
excess vocabulary* (arXiv:2406.07016), file `results/excess_words.csv`
from github.com/berenslab/llm-excess-vocab, rows with `type == "style"`
and alphabetic `word` (n = 407 at fetch date; local copy
`kobak_excess_words.csv`, committed). Literal lowercase word forms; no
additions, deletions, or reweighting per corpus. English-language chambers
only under v1.0 (a translated instrument is a future protocol version).

## Corpus windows (fixed rule)

- Pre: all available sittings dated **on or before 2022-12-31** (use
  everything the source provides; do not select years).
- Post: sittings dated **on or after 2024-01-01**.
- 2023 is excluded everywhere (transition year; rule set from the NB
  quarterly series before this protocol was frozen).
- Unit of text: speaker turns from the official verbatim record, English
  original-language text where the record distinguishes translation.

## Primary statistic (choice-free)

Equal-word-weight mean log fold-change:

    S = (1/n) * sum_w log[ (k_post_w + 0.5)/W_post  /  ((k_pre_w + 0.5)/W_pre) ]

k = word count, W = period word count, n = instrument size. No frequency
subsetting, no thresholds.

## Null and p-value

1,000 placebo instruments (per-corpus RNG seed = integer value of
sha1(corpus name)[:8]; NB used seed 20260730 pre-protocol). Each placebo
word is drawn from the same log2 pre-frequency bucket as its real
counterpart (fallback to nearest non-empty bucket, offsets 0, ±1, ±2, ±3,
±4), excluding the instrument's words, the corpus's 120 most frequent
words, words shorter than 4 characters, and non-alphabetic tokens.
Empirical p = fraction of placebo S >= real S. Report p, the placebo
median and p99, and the real S.

## Pre-specified secondaries (reported, never substituted for the primary)

1. Pooled-ratio threshold sweep at <1, <2, <5, <10, <20, <50 per 100k
   (pre-frequency computed from the corpus's own pre period).
2. Formal-register control set (the 15 stems in `placebo_tests.py`),
   pooled ratio — expected ≈ 1.
3. Speech-clustered bootstrap 95% CI (2,000 resamples of turns) for the
   pooled ratio of the full instrument.
4. Per-year rate series for the 33-pattern Wikipedia-signs set
   (descriptive trend; instrument in `tier15_wiki_signs.py`).

## Combination across corpora

Fisher's method over the primary p-values of all corpora run under v1.0,
NB included as discovery only if flagged as such wherever combined
results are reported. Corpus inclusion rule: any legislature whose
official verbatim record spans at least two pre years and one post year
and clears the pipeline's extraction QA; no corpus may be dropped after
its p is known.

---

## Clarification 1 (2026-08-01): common pre-window

The v1.0 text says "use everything the source provides; do not select
years". In practice the sources differ enormously in depth (ParlParse
reaches 1918; ourcommons.ca reaches 2015; NB's digitised record starts
2018), so "everything available" would give each chamber a different
pre-period and make cross-corpus effect sizes non-comparable.

**Practice, applied uniformly and retroactively to every corpus:**

  pre  = sittings from 2018-01-01 to 2022-12-31
  post = sittings from 2024-01-01 onward
  2023 excluded (transition year, unchanged)

The 2018 floor is set by New Brunswick, the shallowest source. Corpora with
deeper archives (UK, Canada) are truncated to it rather than being allowed a
longer pre-period. This is a deviation from the literal v1.0 wording and is
recorded here rather than silently applied; it does not affect any
already-reported result, because NB, Ireland and the UK were all downloaded
within this window from the outset.
