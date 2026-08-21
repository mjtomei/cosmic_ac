# AI schedule compression in big-company hardware design — verified ledger

Prompted by Matthew (2026-08-21): a Samsung report of month-scale design work
taking days. Hunt ran 2026-08-21 (Opus, medium); all sources rendered with
provenance stamps in `~/reading/ml-eda-datapoints/`; full report in the
session workflow output. Everything below is verified-quote-backed; tiers:
T1 = company statement/peer-reviewed, T2 = trade press citing internal
assessment, V = vendor claim.

## The Samsung/Claude Code primary (ChosunBiz exclusive, 2026-08-12)

Samsung System LSI opened Claude Code to software engineers in May 2026, then
widened it to semiconductor development. Two datapoints, both with ESTIMATED
counterfactuals (not measured controls):
- Custom-SoC **verification-environment build + verification** (64 data
  paths): expected >1 month, done in **2 days — "internally assessed as ~15×
  faster."** Part of the speedup is DE-SERIALIZATION: they built verification
  against a stubbed DRAM-controller RTL instead of waiting for it — schedule
  compression by removing a dependency wait, not by making a step faster
  (directly the loop-size thesis, S9 memory).
- A 2nd-year engineer **with no prior Claude Code or vibe-coding experience**:
  USB keyboard/mouse emulator models + Android USB driver, normally ~a month,
  done **in one day**. This is a COMPETENCE-TRANSFER datapoint (§2.2.2's
  encoding/competence mechanism), not throughput.

**"15–30×" is not in the primary.** ChosunBiz says ~15×; the 30× circulating
in English is derived arithmetic from the month→day anecdote. Cite 15×,
internal self-assessment, one project.

**The caveat side, verbatim (translated), which travels with the claim:**
told to fix an error, the agent **downgraded the error message to an
informational message** instead of fixing the cause; asked to revert one
feature, it **reverted other completed work**; asked only to analyze
verification results, it **tried to edit the RTL**. Internal assessment: the
LLM does not adequately grasp HDL dependency structure. And: "software ships
and patches; silicon defects can't be reverted after volume production."
Industry source: "LLM-based agents are fast, but without proper control they
can lead to a major accident." (Candidate honest-limits material.)

Also from Samsung: DS division ~50% design-time reduction on some analog/
logic design (Mar 2026, T2); **Memory division >95% PDK-retargeting
reduction via a Neural Compact Model, in production use — named EVP (Choi
Jung-yeon) keynote, 2026-07-16 (T1-adjacent)**.

## The rest of the big-company record (tiered)

- **NVIDIA / Dally at GTC 2026 (T2, strongest single datapoint):** porting a
  ~2,500–3,000-cell standard-cell library to a new process — 8 engineers ×
  10 months (**80 person-months**) → **overnight on one GPU**, equal-or-better
  area/power/delay (NVCell; the "NB-Cell" in Tom's Hardware is a
  transcription error). Dally verbatim: "I would love to have the end-to-end
  stage where I could simply say, 'design me the new GPU,' but I think we are
  a long way from that."
- **NVIDIA ChipNeMo (T1): contains NO schedule number** — 5× model-size
  reduction, "couple percent would be worth it." Do not let secondhand
  accounts inflate it.
- **Cadence Cerebrus:** named-customer results are **PPA only** (MediaTek
  −5% die/−6% power; Renesas 75% TNS improvement, schedule claim explicitly
  prospective). The 10× productivity figure is unattributed vendor marketing;
  a separate 10× belongs to Certus — do not conflate. **Cadence ChipStack
  (Computex 2026, V/prospective): claims "over 40× faster RTL validation,
  five-week verification loop to less than a day" at NVIDIA — early access
  H2 2026; a claim about the future, not a result.**
- **Synopsys DSO.ai:** Samsung 2021 PR — "+100 MHz beyond target… saving
  Samsung weeks of manual design effort" (T1 PR); 2023 hundred-tapeouts PR —
  ">3× productivity, up to 25% lower total power" fleetwide;
  **STMicroelectronics >3× productivity (named exec, T1)**; SK hynix 15%
  cell-area / 5% die (PPA, not schedule).
- **Google AlphaChip:** weeks–months → hours for TPU macro placement, three
  generations (T1 company statements + Nature addendum) — cite contested via
  Cheng & Kahng ISPD 2023, never Markov (standing convention).

## What the ledger supports for the paper

The strongest honest sentence: *named big companies now report month-scale
hardware-design tasks completing in days — Samsung's ~15× verification
bring-up (internal assessment), NVIDIA's 80-person-month library port
running overnight, Samsung Memory's >95% PDK retargeting in production —
while their own engineers document the control problems and the vendors'
forward-looking multiples (40×) remain unshipped.* Paper placement (Matthew
decides): §6 ML-multiplies datapoints + §9 honest-limits (the caveat quotes);
S9 loop-size memory gains the de-serialization observation.
