# Stage 6 — DQI on machine continuations that no human ever reviewed

*Planned 2026-08-19 (Matthew). Motivated by review item Q1 and testable with
assets already in the repo. Self-contained.*

## The hypothesis this tests (Matthew, from the Q1 result)

Q1 found that AI-flagged speech is about half as likely to contain anything
to engage with, and separately the study finds AI-flagged speech
better-formed. One explanation nobody has excluded: **the AI-flagged human
submissions went through MORE stringent human review than ordinary speech —
members worried about the ethics of machine drafting vetted the output
harder.** Under that account the form-lift is a selection effect of worried
humans, not a property of machine text.

The test: grade machine text that **no human ever reviewed** — the study's
own cached generations. If raw, unvetted machine output shows the same
form-lift (and the same applicability collapse), the vetting explanation
loses; if the lift vanishes without a human curator, it gains.

## Assets, already on disk

`rlhf_gen/prompts.json`: 800 prompts = 45-word openings of real PRE-2023
segments (IE/UK/CA, scoreable, untranslated, ≥120 words) — pre-machine by
construction. Continuations cached for eight models
(`rlhf_gen/{llama31,mistral,qwen3,qwen3_a3b}_{base,instruct}.json`) and the
four OLMo ladder stages (`olmo_ladder/*_gen.json`). None was ever seen by a
human before caching.

**The human twin exists for every prompt**: the source segment's own words
from word 46 on — the member's actual continuation, recovered by matching
the 45-word opening back to the source jsonl (deterministic; the
`build_prompts` filter is reproducible from `rlhf_pref_generate.py:65`).

## Design

Paired, blind, same rubric as stages 1–5 (v2b DQI + ai_guess + the −1
applicability sentinels), two independent passes, stage-5 workflow pattern.

- Sample **60 prompts** (seeded). Arms per prompt: HUMAN (the real
  continuation, words 46+, truncated to the generation length), MISTRAL-I
  and QWEN3-I (instruct — the register carriers), MISTRAL-B (base contrast).
  240 texts, 480 gradings across two passes.
- All texts enter one shuffled blind pool keyed by content hash; the judge
  never sees arm, model, or pairing.
- Primary contrasts, pre-stated: instruct − human on the three form
  dimensions (justification, common_good, respect_groups) and on
  **P(applicable)** for the two sentinel dimensions (the Q1 quantity).
  Secondary: base vs instruct (does post-training create the lift, matching
  §4.7's register result); OLMo ladder stages as a dose-response follow-up
  if the primary shows anything.
- Length: generations are token-capped; the human twin is truncated to the
  same word count so length is matched by construction, and the Q2 ruling
  applies — length is a channel, not a nuisance (Matthew, 2026-08-19: if
  LLMs put in more effort and provide longer texts with higher
  justification, that is a valid quality increase; report raw beside any
  adjusted figure, never adjusted alone).

## What it cannot show, stated now

These are continuations under a bare prompt, not speeches a member chose to
submit — so a null form-lift here would not prove the lift in the wild is
vetting; it would show machine text alone does not carry it, which makes
human curation (of some kind) the remaining channel. And the models are
open-weight 2024–25 vintages, not whatever tool members actually use.

## Order of execution

1. Recover human twins (match prompts to source segments); build the blind
   pool + key. 2. Grade via the stage-5 workflow pattern, two passes.
   3. Paired analysis + applicability rates; write into §4.9 as stage 6.
