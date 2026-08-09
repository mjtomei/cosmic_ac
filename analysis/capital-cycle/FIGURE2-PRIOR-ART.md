# Figure 2 (embargo natural experiment) — prior-art and data check

2026-08-08 Opus agent pass, prompted by the flag in `NONRIVALRY-ANCHORS.md`.
Bears on the **existing published paper**, not the Cosmic AC material.

## The data checks out exactly — cite it more precisely

Stanford AI Index 2025, Ch. 2.1, verbatim: "On the LMSYS Chatbot Arena, the top
U.S. model outperformed the best Chinese model by **9.26% in January 2024**. By
**February 2025**, this gap had narrowed to just **1.70%** (Figure 2.1.36)."
AI Index 2026: "as of **March 2026** the top U.S. model leads by **2.7%**."
So the paper's 9.3 / 1.7 / 2.7 series is correct and fully citable, and
`build/fig_embargo.py` already attributes it correctly. Three fixes:

1. **Pin the citation to Figure 2.1.36.** AI Index 2025 uses "1.70%" for *two*
   different gaps — the US–China Arena gap AND (in Top Takeaway #2) the
   closed-vs-open-weight gap ("8.04% in early January 2024… narrowed to 1.70%").
   A checking reader can easily land on the wrong one.
2. **Date fix: "March 2026," not "early 2026."**
3. **Metric caveat worth stating:** these are percentage differences in *Elo*,
   an interval scale with an arbitrary zero, so percent-of-Elo is a soft
   normalization. Epoch's ECI time-lag metric gives a less triumphant reading of
   the same underlying data: Chinese models lag the US frontier by **~7 months
   on average (range 4–14) since 2023**, never at the frontier. Naming both
   costs the argument nothing — 7 months is still ≪ the 4-year hardware lead.

## The inference is already published — cite Miller, don't assert it fresh

**Chris Miller, "How US Export Controls Have (and Haven't) Curbed Chinese AI,"
AI Frontiers / HKS GrowthPolicy, 2025-07-08** states the paper's exact narrow
inference a year earlier: controls *did* work on chipmaking capacity (no EUV for
SMIC; Huawei ~200k chips in 2025 vs ~1M Nvidia legally imported in 2024), but
**"chip export controls have not seriously slowed improvements in Chinese model
quality"** — citing the AI Index benchmark evidence. High-credibility author,
same claim. Corroboration: Gupta, Walker & Reddie, "Whack-a-Chip: The Futility
of Hardware-Centric Export Controls," arXiv:2411.14425 (Tencent Hunyuan-Large
reaching SOTA on unrestricted H20s). The ~4-year hardware-lead figure is Erdil
(Epoch, 2024-12-06), who adds a point the paper should use: "the US has
essentially no lead when it comes to *serving* those models to users," because
controls bit arithmetic throughput rather than memory/network bandwidth.

**Recommended recast of the caption:** "drawn from Stanford AI Index 2025
(Fig. 2.1.36) and 2026, and Epoch AI; the inference follows Miller (2025)" —
strictly stronger than asserting it fresh, and exactly what the no-novelty rule
wants.

## Jin et al. is ADJACENT, not SAME — and is a useful ally

arXiv:2606.15999 = Jin, Kunievsky, Lou, Sun & Evans, **"U.S. Policies
Unintentionally Accelerated China's Open AI Ecosystems"** (2026-06-14). Event
study around four policy shocks (CHIPS Act 2022-08-09; Commerce controls
2022-10-07; expanded controls 2023-10-17; EAR revision 2024-12-02). Outcomes are
**ecosystem response, not capability**: GitHub ForkEvents, open-model release
counts, arXiv efficiency-topic paper counts, USPTO mentions. Full-text grep
returns **no** instance of Arena, LMSYS, Elo, or MMLU. Finding: Chinese
developers increased engagement with open LLM repos far more than US developers
after the shocks; Chinese open models then diffused through open-source and
scientific channels while remaining near-absent from US patent disclosures.
Weakness: region assigned by a **time-zone proxy on event hour**. Authors
self-limit to "descriptive and quasi-experimental."
**Use it in §2.2 as the published event-study supplying the *mechanism* the
figure only implies** — substitution toward open ecosystems rather than
capability suppression.

## Strengthen the confounders — two upgrades

1. **Replace "stockpiled chips" with a number.** Epoch AI, Juniewicz,
   "Diversion and resale: estimating compute smuggling to China" (2026-04-29):
   Monte Carlo estimate **290k–1.6M H100-equivalents smuggled through 2025,
   median ~660k ≈ one-third of China's total AI compute**. This goes to
   *treatment validity* — "chips were restricted" is partly counterfactual.
2. **Name the best opposing case, which the figure cannot absorb.** Epoch via
   AI Index 2025: the top 10 Chinese models by training compute scaled at
   **~3×/year since late 2021 against ~5×/year for the rest of the world since
   2018**. That is a measured divergence in exactly the input the controls
   targeted, contemporaneous with the Arena convergence. Also Heim & Huang,
   "The Rise of DeepSeek: What the Headlines Miss" (2025-01-25) — attacks the
   *measurement*: real restrictions only began Oct 2023; firms spend **60–80% of
   compute on deployment** so controls hit ecosystems more than individual
   training runs; public benchmarks understate US capability because leading labs
   hold capabilities private; DeepSeek's founder conceded a **4× compute
   disadvantage** and built on Asia's first 10,000-A100 cluster. Amodei (Jan
   2025) is op-ed and temporal (controls target the 2026–27 scale jump). CSIS
   Harithas (Dec 2024): ~14.31M US accelerators vs ~4.8M Chinese by end-2025.

## Also found

A cluster of DiD/PSM-DiD econometrics estimates export-control effects on
Chinese **firm** R&D, innovation, productivity and export complexity (Research
Policy Nov 2025; IRFA Oct 2024; The World Economy 10.1111/twec.13570; PLOS ONE;
IJOPM) — all finding controls *stimulated* Chinese R&D. **None uses model
capability as an outcome, and no study uses the Arena series as a regression
outcome variable.**
