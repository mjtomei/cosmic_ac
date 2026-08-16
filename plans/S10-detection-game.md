# S10 future work: the detection game — a self-generating instrument for 1c/1d

**Idea: Matthew, 2026-08-16.** A game with human and AI participants that
produces, in one loop, the two things future-work items 1c and 1d call for:
the false-accusation rate of human authorship-judgment (1c), and the reachable
"more human than human" ceiling when a model optimises against human reviewers
(1d). The game framing is not decoration — it solves the recruitment and
incentive problem that makes standalone human-rating studies impractical.

Prior art to VERIFY before writing (not web-checked, budget): AI21's "Human or
Not" (2023) social Turing game (largest of its kind) is the closest precedent;
the mechanic here differs in the adaptive-feedback conditions and the
continuation/Apples-to-Apples generation step. Also check the LLM-as-judge and
Turing-test-tournament literature.

## Mechanic

Each round: a shared prompt (a legislative-speech opening, to stay commensurable
with the study's corpus — or a general Apples-to-Apples-style card to widen
appeal). Every participant, human and AI, submits a continuation. Human
participants then rate each submission's probability of being LLM-generated.
Blind-mixed: raters never know the human:AI ratio or which is which.

## The independent variable: information conditions (dose-response ladder)

How much human-review signal each AI generator receives:

- **none** — generates blind, never sees ratings. The control: with humans
  improving round over round and this AI static, it isolates HUMAN learning.
- **own aggregate** — sees how its own past outputs scored.
- **others' games only** — sees the human-review signal from games it was not
  in (tests transfer/generalisation vs. personalisation).
- **full transcripts** — sees which specific submissions drew "AI" votes and
  which passed (the strong 1d form: optimise against named human tells).

## Two decisions that make or break the measurement

1. **Proper scoring rule for raters.** Score/rank raters by Brier or log score
   on their AI-probability judgments, so honest belief is the optimal strategy.
   Without this, ratings are strategic and the 1c false-accusation rate is
   contaminated. This is the single most important design knob.
2. **Blind-mixed generator pool.** Humans and AIs both generate; raters never
   know the ratio. A rater's "AI" vote on a genuine human submission is then a
   true false accusation — exactly the 1c quantity — and an AI submission
   rated "human" is a true pass — the 1d quantity.

## Outcomes (three curves from one apparatus)

- **Human detection accuracy over rounds** — does it fall as feedback-enabled
  AIs adapt? (the arms-race / equalizer-dynamics question)
- **AI pass-rate ceiling by information condition** — the 1d frontier, measured
  under consent; the gap between the `full transcripts` and `none` conditions
  is the value of human-review signal to an adversary.
- **False-accusation rate on real humans** — the 1c number, and whether it
  concentrates on any identifiable subgroup of human writers.

## Why this is the ethical form of 1d

1d ("a search that targets the human judge") has a real dual-use edge. Running
it inside a consented game resolves it: participants opt in, no one is deceived
outside a disclosed game frame, and the deliverable is the measured ceiling and
its driving features (pair with the §8.6.1a register-feature instrument so the
output is named features, not a black-box rewriter) — built for defenders, not
deployment.

## Connections back to the study

- Directly instruments §8.2's anti-correlation claim (currently one
  lineage-correlated judge, n=35, t=−1.15) with real humans at scale.
- The co-adaptation curve tests the equalizer/chase-and-flight dynamics: if
  human detection collapses under feedback, register has stopped carrying
  authorship information in real time, observably.
- Legislative-prompt variant keeps it commensurable with the corpus; the
  Apples-to-Apples variant trades commensurability for participation and reach.

## Open design questions (before any build)

- Human-subjects consent / IRB, since it is human-subjects research with a
  disclosed-deception frame; required if published.
- Separating AI-improvement from human-improvement rigorously (the `none`
  condition is the lever; may need a frozen human panel as a second control).
- Whether raters also generate (role leakage) or the roles are disjoint.
- Incentive to generate well vs. to generate human-passably — these differ,
  and the payoff structure has to name which is being rewarded.
