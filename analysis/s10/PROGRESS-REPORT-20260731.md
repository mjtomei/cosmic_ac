# S10 progress report — AI-generated text in the New Brunswick legislature
**2026-07-31 · for external collaborators · full artifacts in `analysis/s10/` (repo: performance_commons)**

**Corpus.** The complete digitized NB Hansard: 364 sittings, Oct 2018 – May 2026,
~8.2M scoreable English words. The bilingual record's column structure lets us
isolate speaker-authored English (~78% of original speech) from translator output.

**1. Vocabulary trend (the strongest statistical result).** Using two externally
frozen instruments — Kobak et al.'s excess-vocabulary list (arXiv:2406.07016,
derived from PubMed, no contact with our corpus) and Wikipedia's Signs-of-AI-writing
catalog — AI-preferred vocabulary is flat 2018–2022, inflects in 2023Q4 (~3 quarters
after ChatGPT), and reaches ~3× baseline by 2024–26. Primary test is choice-free
(equal-word-weight mean log fold-change over Kobak's full 407-word style list):
the observed statistic exceeds the maximum of 100,000 frequency-matched placebo
lexicons (p < 10⁻⁵). Interrupted-time-series slope change at the pre-registered
2023 break: +23.7%/yr, placebo p = 0.007. Mechanism check: word-level AI-preference
measured only from a synthetic in-domain corpus + 2019 control predicts which
individual words rose (Spearman +0.55, p < 10⁻⁴). Formal-register control set
declines (rules out formality inflation); per-speaker heterogeneity (one member
6×, others down) rules out editorial house-style drift.

**2. Prevalence (Pangram, calibrated in-domain).** Se = 40/40 on synthetic AI
legislative speech, Sp = 240/240 on pre-2023 controls across five years — zero
errors both ways. Random-sample prevalence of AI-flagged segments: 0% (2019–22),
4.0% (2023), 4.0% (2024), 4.3% (2025), **13.6% (Jan–May 2026)** — accelerating,
not plateauing (2026 CI ≈ [6%, 27%], n=44).

**3. The scissors (mechanism).** Eight statistical/zero-shot detectors (Binoculars
×3, Fast-DetectGPT, LRR, three supervised classifiers), all calibrated on the 2019
control, show *no* elevation — while the lexicon rises. Edited/assimilated AI keeps
its vocabulary but loses its token-statistics: the record's AI is human-mediated,
not pasted. Blind frontier LLMs reproduce Pangram's verdicts from text alone
(Claude Opus 5, low effort: AUC 0.951; Claude Fable 5, high: 0.936), but current
open-weight models cannot (gpt-oss-120b: 0.66–0.67 regardless of reasoning effort;
Qwen3-32B: 0.55 low, thinking-mode run in flight) — detection of edited AI appears
frontier-capability-bound, which also retro-explains result 3's nulls.

**4. Deliberative quality (DQI, Steenbergen-anchored).** A blinded LLM judge using
the strict Discourse Quality Index with the original authors' worked Commons
examples as anchors (repeat-pass reliability at/above their published human
inter-coder bar): AI-flagged speech scores *higher* on formal justification,
~3× lower on first-person witness, lower on engaging others' demands. Blind
2019→2026 comparison: justification and evidence up; respect-toward-demands
0.96 → 0.52, concentrated exactly where prevalence jumps. Summary: **form up,
deliberation down.**

**5. Attribution.** Adoption is per-office: one member's May-2023 speeches are
flagged by two independent instrument families and confirmed by Pangram at
fraction_ai = 1.00 (12+ segments); confirmed specimens include a minister's
statement and a Premier's condolence address. Catchable AI shifted from
half-assisted (2023–24) to fully generated (2025–26).

**Positioning.** Closest prior work (Suvanto et al., arXiv:2606.14209, June 2026)
covers UK/Swedish *written* parliamentary texts with a trained classifier; we
measure the transcribed spoken record they explicitly avoided, add calibrated
commercial adjudication, placebo inference, and quality effects. Replication
protocol v1.0 is frozen (instrument, statistic, windows, placebo procedure);
UK Hansard (ParlParse XML, 1918–present) is the first replication target, with
Fisher combination across chambers. Cost to date: ~$66 of a $200/mo Pangram
plan; the validated two-stage design (frontier-LLM screen → Pangram confirmation)
prices each additional legislature at $20–30.
