# S10 venue review — where adjacent work landed, and what format each implies

*2026-08-18. All venue placements below web-verified today. Purpose (Matthew):
review venues where this type of work might be submitted, and format the paper
similarly to adjacent works.*

## Where the directly adjacent work published

| work | venue | what it is |
|---|---|---|
| Kobak et al., "Delving into LLM-assisted writing in biomedical publications through excess vocabulary" | **Science Advances** 11, eadt3813 (2025) | The study's methodological parent (excess-vocabulary method; ≥13.5% of 2024 PubMed abstracts). Research-article format, compact main text + large supplement, code on GitHub. |
| Liang et al., "Monitoring AI-Modified Content at Scale" (peer reviews) | **ICML 2024** (PMLR v235) | Distributional ML estimator of LLM share; conference format. |
| Liang et al., "Mapping the Increasing Use of LLMs in Scientific Papers" | **COLM 2024** | Same family, ~950k papers; conference format. |
| Koniaris et al., ParliaBench (LLM-generated parliamentary speech benchmark) | **LREC 2026** | Generation/evaluation benchmark, not prevalence measurement. |
| Suvanto, McGlinchey, Barclay & Wahde, "Detecting undisclosed LLM-generated content in parliamentary texts" | **arXiv 2606.14209** (June 2026; publication venue TBD) | **Closest competitor.** UK + Sweden, glass-box classifier trained on pre-2022 text vs LLM rewrites, finds "steady increase from 2022 onwards." Prevalence only — no covariates, no quality arm, no register/cohort/occupation analysis per the abstract. |
| Pimlico Journal UK Commons word analysis (press, not peer-reviewed) | blog/press (TechRound coverage) | 2007–2025 Commons marker words ("underscores", "streamline"); public attention exists. |

**Competitor read:** 2606.14209 confirms the phenomenon in two chambers with a
different detector family and stops at prevalence. S10's differentiators — 22
chambers, calibration (Rogan-Gladen), genre/concentration structure, the
pre-machine register with cohort/class/occupation covariates, the quality arm,
the pre-registered occupational study — are all outside its scope. It should be
cited in §7 related work; it also means the prevalence-alone claim is no longer
novel, which strengthens the case for submitting the integrated study rather
than slicing it.

## Candidate venues, in rough order of fit

1. **Science Advances** — the parent paper's home; multi-arm computational
   studies with heavy supplements are normal there; open access; no strict
   length cap once SM is used. Format implication: distill a ~5,000-word main
   text (prevalence + register + occupational headline), push the arms and
   appendices into SM — our appendix structure already maps onto that.
2. **Journal of Quantitative Description: Digital Media** — founded (Guess,
   Hargittai, Munger) explicitly because comprehensive descriptive work is
   undersupplied; fee-free OA; Letter-of-Inquiry model (cheap to test fit);
   no causal-claims framing — matches the study's careful non-causal voice.
   The philosophical fit with the anti-salami meta point is exact. Scope
   question (parliamentary records as "digital media") is answerable with a
   one-page LOI.
3. **PNAS / PNAS Nexus** — standard computational-social-science home; short
   main + SI format similar to Sci Adv.
4. **Political-science field journals** — *Legislative Studies Quarterly*,
   *British Journal of Political Science*, *Political Communication* (the
   audience whose institutions are being measured); *Political Analysis* if
   the submission is re-centred on the measurement/calibration methodology.
   Format: 8–12k words, heavier theory framing, slower.
5. **ML/NLP conferences** (ACL/EMNLP CSS tracks, COLM) — fits the detection
   and calibration machinery; wrong home for the sociology; consider only for
   a methods-focused companion if one is ever wanted (which the anti-salami
   point argues against).

## Formatting takeaways to apply regardless of venue

- Compact main text + everything-reproducible supplement is the format of
  every adjacent success (Kobak's SM + public repo is the model; our
  analysis/ scripts + appendices already have that shape).
- Public code/data repository at submission (Kobak precedent; our convention
  already matches).
- Cite 2606.14209 and ParliaBench in §7 now, before any submission.
- The two-instrument structure (detector + register) should be the main-text
  spine, matching how Kobak leads with the method-anyone-can-rerun.
