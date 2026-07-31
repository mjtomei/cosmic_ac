# Speech/argumentation quality vs AI status — methodology design

**Goal:** compare the *quality* of AI-flagged vs human legislative speech
(Pangram verdicts as ground truth) without the comparison collapsing into
re-detecting AI style. Version 1, 2026-07-30.

## The two traps, designed against

1. **Circularity.** Most "quality" surface metrics (lexical diversity,
   sentence rhythm, formality) are exactly the features detectors and
   lexicons use. Any difference found on them is *style*, not quality.
   Every measure below carries a circularity grade: **[C-low]** (measure
   is about propositional content, not diction), **[C-med]**, **[C-high]**
   (style-adjacent — descriptive only, never a quality claim). For the
   LLM judge, we additionally *measure* the leak: the judge separately
   guesses "was this AI-assisted?", and quality scores are compared
   with that guess controlled (if judged-quality differences vanish
   conditional on the judge's AI-guess, the judge was smelling style).
2. **Genre confound.** AI-flagged segments concentrate in prepared
   ceremonial/statement genres; spontaneous crosstalk is nearly all
   human. Naive comparison measures genre, not AI. Design: compare
   **within selection-matched pools** — the Pangram-scored candidate
   strata contain both AI-verdict and Human-verdict segments that passed
   the *same* selection filters; primary comparisons are within-stratum,
   within a 100–360-word band, original-English, non-chair speakers.
   The unbiased-but-small B-sample comparison (10 AI vs 110 human) and
   the 2019 control anchor are reported alongside. Full genre labels
   (prepared vs spontaneous) remain an S10 open item; until then this is
   a pilot with the confound stated, not solved.

## Tier Q1 — computable, model-free (`quality_lexical.py`)

| measure | what it proxies | circularity |
|---|---|---|
| numerals + currency + percent per 100w | concrete evidence density | C-low |
| mid-sentence capitalized tokens per 100w | named entities (people, places, programs) | C-low |
| NB place/riding lexicon hits per 100w | constituency grounding — is it about the actual place | C-low |
| first-person-singular rate | personal witness vs generic voice | C-med |
| repeated-bigram share within segment | boilerplate / padding | C-med |
| argument connectives (because/therefore/however/but) per 100w | explicit reasoning moves | C-med |
| mean sentence length, Flesch | descriptive only | C-high |

## Tier Q2 — LLM-judged DQI-lite (`quality_judge.py`, pilot)

Anchor: the Discourse Quality Index (Steenbergen, Bächtiger, Spörndli &
Steiner 2003), the standard deliberation-quality instrument for
parliamentary debate; LLM automation of DQI recently validated at
human-comparable reliability (JPIPE 2025 prompt-engineering framework;
DelibAnalysis for Canadian territorial legislatures). Rubric per segment
(blinded, shuffled order, no metadata shown):

- justification level 0–3 (DQI: none → qualified justification with
  reasons and linkage)
- common-good orientation 0–2
- respect toward other positions 0–2 (where applicable)
- constructiveness 0–2 (proposals vs pure positioning)
- evidence specificity 0–3 (checkable facts, named sources, quantities)
- **judge probe:** P(this text was AI-assisted) 0–100 — used ONLY to
  measure and control judge-side circularity, never as a detector

Judge: local Qwen3-8B for the pilot (validity caveat: an 8B judge is a
screening instrument; the paper-grade run uses a frontier judge with
25–50 in-context examples per the JPIPE recipe, plus a human-coded
reliability subsample). Two passes with shuffled order; report
intra-judge agreement.

## Tier Q3 — behavioral/uptake (designed, not yet run)

- Chamber reaction: interjections and recorded reactions following the
  speech (Hansard marks them) per speech. C-low but engagement ≠ quality.
- Uptake: does the next speaker engage the content (lexical overlap of
  response beyond baseline)? Discursive influence.
- QP responsiveness: for question–answer pairs, judged answer-to-question
  relevance — the genre where quality is least confounded by preparation.

## Comparison sets

1. Primary: candidate-strata AI/Mixed (n≈90) vs candidate-strata Human
   (n≈150), within-stratum weights, 100–360w, orig_frac ≥ 0.5.
2. Unbiased check: B-sample AI (10) vs B-sample Human (110).
3. Anchor: 2019 control (60) — the pre-AI baseline for every metric.
Cluster bootstrap by speech for all CIs; report effect sizes, not just p.

## Pilot results (2026-07-30)

Q1: AI-flagged speech has **~3× less first-person singular** (CI-separated,
replicates in the unbiased sample), directionally fewer numerals (−33%)
and named entities, longer sentences, lower Flesch. Q2 (blinded Qwen3-8B
DQI-lite, 241 segments): **no meaningful judged-quality gap** — AI a hair
higher on justification/structure (2.47 vs 2.33), a hair lower on
evidence (1.53 vs 1.60); the ai_guess probe returned ~10 for every group
(no circularity leak, and no detection ability — expected at 8B).
Synthesis: **AI raises the floor of argumentative form while thinning the
content anchors** — formally competent, experientially hollow. Pronoun
corollary (Pennebaker/Kacewicz status work; Newman deception work): low
"I" classically reads as status or distance; here it is authorship
displacement — the drafting voice has no experience to reference. Any
pronoun-based psychological inference on post-2023 institutional text
silently breaks; the remaining "I rise today" is a simulated first person.

## Fable-5 workflow judge (2026-07-31, wf_e2fe0a4b, 31 agents, blinded)

- **Blind cross-validation of Pangram: AUC 0.936** — Fable-5's ai_guess,
  from text alone, reproduces Pangram's verdicts (mean 44 on AI-verdict
  candidates vs 9.7 on random-human, 7.3 on 2019 control). Two unrelated
  frontier systems agree on which segments are AI.
- Quality by verdict (unconditional): AI higher justification (2.13 vs
  1.89), evidence equal, **lower respect (1.00 vs 1.08) and
  constructiveness (0.89 vs 1.06)**. Conditional on the judge NOT
  smelling AI (ai_guess ≤ 25, n = 9 vs 46), the form advantage vanishes
  (justification 1.44 vs 1.78) — the "argues better" signal lives in the
  segments that read most AI. Collider caveat: conditioning selects
  atypical segments; directional only.
- **Blinded time comparison (2019 control vs 2025–26 random):**
  justification and evidence flat, **constructiveness −0.36 (1.23 →
  0.87)**, respect −0.14. The chamber's speech commits to less, and the
  judge cannot see dates.
- Reliability: 60-segment second pass — exact agreement 80–97% per
  dimension, 100% within one point; ai_guess mean|Δ| 5.7. Inter-judge vs
  the Qwen3-8B pilot: ρ 0.43–0.61 (pilot directionally right,
  compressed).

## Anchored v2 (2026-07-31, wf_0aa63dc2 — strict DQI + Commons anchors)

- **Anchoring effect, measured**: rank-order stable on well-defined
  dimensions (evidence ρ=0.90, ai_guess ρ=0.94, justification ρ=0.75)
  but calibration moved hard where the worked examples bite —
  justification mean 2.12→1.73 (anchors raise the "complete inference"
  bar), constructive 0.99→0.25 (strict "mediating proposal" almost never
  occurs, matching Steenbergen's own all-zeros Commons finding).
  Reproduces the JPIPE anchoring claim on our corpus.
- **Repeat-pass reliability at the published human bar**: justification
  r=0.83 (their inter-coder r=0.716), respect_demands 0.87, evidence
  0.91, counterarguments 0.75 (their κ was 0.559). Caveat: self-agreement
  ≠ inter-coder agreement; the human-coded subsample remains the true
  validation.
- **AUC vs Pangram unchanged: 0.936** (property of the text, not the rubric).
- **Blinded 2019 vs 2025-26 under strict DQI**: justification +0.21 and
  evidence +0.19 UP; respect toward others' demands **−0.36**
  (0.96→0.60) and constructive politics **−0.30** (0.54→0.24) DOWN.
  The deliberation-theory phrasing of the whole quality result: the
  chamber argues more completely and cites more, but engages opposing
  demands less and almost never mediates. Form up, deliberation down.
- AI-verdict vs human-verdict under v2: justification 1.77 vs 1.52,
  respect_demands 0.55 vs 0.91 — AI-flagged speech is better-formed and
  worse-engaged, the same scissors at the discourse level.
