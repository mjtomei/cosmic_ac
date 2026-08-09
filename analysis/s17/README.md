# S17 — The Mansfield ratio, recomputed

Study register: `studies-and-work-log.md` (S17). Handoff/plan:
`plans/S17-appropriability-and-externality-pricing.md`. Proposed paper text
(staged, Matthew decides): `plans/S17-proposed-text.md`. Reading notes:
`reading/notes/nordhaus-2004.md`.

**Question.** How far has the imitation lag for frontier capability fallen
since Mansfield, Schwartz & Wagner measured it (EJ 1981), and what does the
measured lag do to Nordhaus's 2.2% innovator-capture ratio (NBER WP 10433)?

**Headline.** Holding Nordhaus's appropriability ratio fixed at α = 0.07 and
re-solving his capture equation at measured AI imitation lags, the innovator
capture ratio falls from his postwar 2.2% to ~0.15–0.19% at the 2023–2026
Epoch ECI lags (3–4 months) — an 11–15× collapse. Even the conservative
23-month GPT-3→OPT-175B lag halves it. The uncaptured share rises from 97.8%
to ~99.8%. Nordhaus predicted the direction in the same paper (WP 10433 §V:
new-economy profit durability falls because information is cheap to imitate);
this measures the size.

## Artifacts

| File | What it is |
|---|---|
| `nordhaus_recompute.py` | The model. Capture equation derived in the docstring (the paper never prints its formula — the derived form gives 1.81% at his parameters vs his published 2.2%; a normalized column anchors his headline, and the fold-drop is invariant to the anchoring). Every non-derived number sourced in the header. |
| `capture_ratio_grid.csv` | Output grid: 5 lag scenarios × 5 α values, raw + normalized + half-life-reading columns, fold-drop vs baseline. |
| `imitation_lag.csv` | The measured lag series, per-row source and metric: Epoch ECI (primary), benchmark parity (OPT/BLOOM), LM Arena ranks, Artificial Analysis index gap, consumer-GPU lag. Two ECI-independent metrics included so the result does not rest on ECI alone. Source-quality column flags the one secondary-sourced row (DeepSeek-R1 Arena debut — pull the primary lmarena post before publication). |
| `imitation_cost_ratio.csv` | The sparse Mansfield cost-analogue: DeepSeek-V3 vs GPT-4 (~0.07–0.14 vs Mansfield's 0.65), R1's RL stage, Sky-T1/s1 distillation rows (those are distillation cost, the analogue only if the base model is ambient), Mansfield 1981 baseline row. Include/exclude caveats per row. |
| `build_figure.py` → `s17-capture-collapse.png` | The figure: capture ratio at measured lags vs the Nordhaus baseline, direct-labeled, one axis. The rising-social-value half of the handoff's "wedge" is conceptual and deliberately not drawn as a curve; it lives in the caption. |
| `negative_control.md` | Imitation lags where machine intelligence is not the imitation mechanism: pharma flat at 12–14 yr over 25 years, leading-edge fab flat at ~4 yr pre- and post-export-controls, and the reportable absence — Mansfield's survey never rerun in 45 years. |
| `externality_anchor_verification.md` | The externality-pricing half's anchor set, verified: SCC $51/$190 (with the mandatory not-only-discounting framing), SO2 CEMS 7%-of-compliance-cost quote, Sherwin AMT 2024, CRS IF12072 (title corrected), EPA sensor guidebook. Vendor methane figures did not survive; no peer-reviewed $-per-estimate series exists. |
| `v2_anchor_verification.md` | **v2 (2026-08-06):** anchors for the four-leg argument (`plans/S17-proposed-text.md`) — social-vs-private returns, *Patent Failure*'s negative ledger, quinolones DWL, NPE costs, Eldred brief (Arrow signed), Machlup, CNW (framing corrected), publishing capture, Merton/Dasgupta-David, Shapley (phrasing corrected), ASCAP sampling→census, Epoch 9–900×/yr. |

## Method notes

- **λ from lag:** λ = 1/L (lag as mean lifetime of the lead). Half-life reading
  λ = ln2/L reported as a sensitivity column; it shifts levels, not the story.
- **Why normalization is legitimate:** λ enters capture only through the common
  (r − g + λ) factor, so "capture falls K-fold" is identical in the raw and
  normalized columns. Both are reported.
- **α is swept, not asserted** (0.104 → 0.01): appropriation migrates to
  complements (Teece — distribution, integration, trust, data, supply chain).
  The claim is about the artifact, not the firm.

## Honest limits (state with any use of the result)

1. Benchmark parity ≠ economic substitutability. A 4-month ECI lag is not a
   4-month lag in enterprise willingness-to-pay. Direction: overstates decay.
2. Epoch's own caveats run opposite: open models score worse on private
   benchmarks, and labs withhold their best models, so measured lag
   understates the true capability lag. We report a λ range, not a point.
3. The 2025→2026 3→4-month move is a widening. Short, noisy series; no
   exponential fit anywhere in the study.
4. Bessen & Maskin 2009: with sequential, complementary innovation, imitation
   can raise total innovation — so the finding is "unprofitable to sell,"
   never "unproduced."
5. Nordhaus's method measures US appropriation of US productivity growth;
   the AI sector is far more internationally porous (his own p.18 caveat,
   amplified here).

## Relation to the rest of the repo

Matched pair with `assets-rents-socialized-buildout-2e.pdf` (IV.3): the report
concludes the AI valuations require durable moats; this study measures the
moat depreciation rate directly and finds it 15× the postwar rate. Same claim,
two sides. Third matched pair alongside Arrow-pressure/Samuelson-machine.
