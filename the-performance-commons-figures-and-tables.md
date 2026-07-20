# The Performance Commons — List of Figures and Tables

*Read top to bottom, the visuals carry the paper's argument on their own: **magnitude → mechanism → the same failure everywhere → the same problem, distributed → proof → destination → already underway → the program.** Each entry notes the beat it carries and whether it rests on measured data or is an argued/conceptual construct. (The defections and the diagnosis of the herd live in §2–§4; Figure 2 carries §4's measured centerpiece.)*

---

**Table 1 — The efficiency gap, quantified.**  (§1)
The measured cost of generality: ASIC 1×, CGRA ~2.8× area, FPGA ~20–35× area / ~10–14× power, GPU ~3–15× energy on regular kernels (TPU ~30× perf/W over its contemporary GPU), CPU ~100–500× energy.
*Beat: the gap is real — most code sits far below its own architecture's frontier; these ratios are the separate physical floor.* — **quantitative, sourced** (Hameed; Kuon & Rose; Prabhakar).

**Figure 1 — The general-purpose vs. custom trade-off is mostly an effort artifact.**  (§1.2)
The effort gap, concentrated on reconfigurable substrates; close it and a CGRA sits within ~2.8× of an ASIC with full flexibility.
*Beat: that gap is effort, not physics — the hardware question (Q1).* — **anchored endpoints**; finite-effort curve illustrative.

**Figure 2 — The embargo natural experiment, drawn.**  (§4)
Top-US-vs-top-Chinese Arena gap: 9.3% (Jan 2024) → 1.7% (Feb 2025) → 2.7% (2026), across export controls (Oct 2022, tightened Oct 2023) that held the training-hardware lead at ~4 years (Epoch AI).
*Beat: chips were restricted; capability parity happened anyway — the herd's effort and variance, not silicon, was binding.* — **quantitative** (Stanford AI Index 2025/2026; Epoch AI); single-metric series, leaderboard limits noted.

**Table 2 — One pattern, every layer of the stack.**  (§5)
Foundry → CAD/EDA → IP → ISA → firmware → kernels → drivers → measurement data → distributed compute, each with its open counter-trend.
*Beat: it is not one gap — the same coordination failure recurs from the foundry to the ISA.* — **qualitative + quantitative**.

**Figure 3 — Distributed computing is a collective-action problem, not a hardware limit.**  (§6)
The coordination gap by looseness of coupling; naive methods waste almost all of a loose federation's compute, while methods built for loose coupling (DiLoCo: ~500× less communication, ~90% utilization across continents) reclaim it.
*Beat: the same failure one level up — the wasted-supply side of the software question (Q2).* — **anchored to DiLoCo / OpenDiLoCo**; the underlying waste (12–18% average server utilization, up to ~30% "comatose") is sourced (NRDC / Anthesis).

**Figure 4 — Machine demand has no floor.**  (§6)
The value of the marginal compute-hour against cumulative demand: human demand saturates, machine demand extends toward arbitrarily low value — past datacenter economics (~$0.50/hr) into the range only cheap idle compute (~$0.08/hr, ~6× cheaper) can serve.
*Beat: why solving it is worth the effort — unbounded machine demand makes the otherwise-wasted resource valuable.* — **conceptual**; the cost anchors are from Omerta's reliability-market simulation, the task-value ladder from its economic analysis.

**Table 3 — The entry cost of first silicon.**  (§7)
Full mask set (>$500k) → academic MPW block (€2,000–5,900) → chipIgnite (~$10k) → Tiny Tapeout ($150–300, packaged, open flow, solo) → the same with an LLM agent (eighteen high-schoolers, ninety minutes).
*Beat: the commons has already collapsed the entry cost of hardware specialization by orders of magnitude.* — **quantitative, sourced** (AnySilicon; Europractice 2021 list; Tiny Tapeout's IEEE paper; Krupp, Venn & Wehn 2026); subsidies prop the lowest tiers.

**Figure 5 — Participation through the platform's death.**  (§7)
Designs per Tiny Tapeout shuttle, 2022 → mid-2026, colored by foundry, with the March 2025 Efabless shutdown marked; the next shuttle was the largest ever and the following year out-produced any prior one.
*Beat: the fitness argument's natural experiment, measured — no single point of strategic death.* — **quantitative** (tinytapeout.com); demand per run is spiky and partly subsidy-driven.

**Figure 6 — Where the optimum lands as the commons matures.**  (§10)
A phase diagram over commons-maturity-over-time × workload-diversity; the reconfigurable-optimal region sweeps into territory that today defaults to general-purpose silicon.
*Beat: over time the optimum for real workloads migrates into reconfigurable silicon — not fixed ASICs.* — **conceptual**; the boundary is exactly what a bigger whole-system characterization (§12) would pin down.

**Figure 7 — Reconfigurable hardware is already moving in; the commons is the inflection.**  (§10)
A decade of reconfigurable entry into the datacenter — Catapult, Intel–Altera $16.7B, AWS F1, AMD–Xilinx $49B, the AI-accelerator wave — with a projected inflection as the programmability gap closes.
*Beat: the migration is measurable and already expensive; machine intelligence is the accelerant.* — **real milestones + acquisition values**; share curve illustrative, post-2025 a projection.

**Table A1 — The program: four efforts, two questions, honest state.**  (Appendix A)
Omerta (pool idle compute), the project-manager coordination layer (work on the pool), coherence (the inoculation thesis), and the reconfigurable demonstrator (the Q1 experiment) — latest progress and open items for each, stated plainly.
*Beat: the questions are under active attack, and the breadth of the program is itself evidence of the §9 multiplier.* — **status report, self-reported**; states verified against the repos at the time of writing.

**Table A2 — The wedge economics.**  (Appendix A)
macOS CI and inference prices, mid-2026: GitHub macOS runner $3.72/hr (10× Linux) and EC2 Mac $0.65/hr (24-hr minimum) vs ~$0.006/hr idle-Mac electricity; 70B unified-memory inference ~$0.60/Mtoken vs $0.40 cheapest API and ~$0.06 batched-4090 small models.
*Beat: the Apple wedge prices where licensing and unified memory are the moat.* — **quantitative** (vendor price lists, published benchmarks); spot rates fluctuate.

---

### How the sequence maps to the prose

| Visual | Section | Argument beat |
|---|---|---|
| Table 1 | §1.1 | the gap is real and large |
| Figure 1 | §1.2 | the gap is effort, not physics (Q1: hardware) |
| — | §2–§3 | privilege → the central claim: continuous optimization is an under-provided public good (prose only) |
| Figure 2 | §4 | the embargo natural experiment: chips restricted, parity anyway |
| Table 2 | §5 | the same failure is everywhere in the stack |
| Figure 3 | §6 | distributed computing is the same problem — the wasted supply (Q2: software) |
| Figure 4 | §6 | unbounded machine demand makes the idle resource valuable |
| Table 3 | §7 | the entry cost of first silicon has collapsed |
| Figure 5 | §7 | the commons survives its platform's death, measured |
| — | §8–§9 | (AI multiplies the commons; the vendor is the aggregation point — prose only) |
| Figure 6 | §10 | where the optimum lands as the commons matures |
| Figure 7 | §10 | and it is already underway |
| — | §11 | honest limits (prose only) |
| — | Conclusion | build collaboration-native hardware (prose only) |
| Table A1 | Appendix A | the program in detail, honestly |
| Table A2 | Appendix A | the wedge economics, priced |

### The "needs a bigger project" items (flagged for honesty)

- **Figure 6's boundary** — the real position of the ASIC / CPU / CGRA optimal regions needs the whole-system workload characterization §11 calls the prerequisite (achieved-vs-achievable parallelism, dataflow locality, phase and input statistics across the real consumer mix).
- **Figure 4's demand curve** — conceptual; the ~$0.50 vs ~$0.08 cost anchors are from Omerta's reliability-market simulation and the task-value ladder from its economic-analysis notes. Omerta itself is partially built: a substantial, well-tested mesh-networking layer (encryption, NAT traversal, gossip discovery, tunnelling, a mesh-native virtual network, plus Terraform-managed bootstrap/STUN servers) and working ephemeral-VM and simulation components, but the end-to-end compute loop is broken mid-migration and the trust/payment chain is validated in simulation rather than running live (two of six transaction types tested).
- **Figure 7's share curve and projection** — the adoption trend is illustrative; the dated milestones and the $16.7B / $49B acquisition values are real.
- **Figure 1's finite-effort curve** — illustrative; only the realizable-frontier endpoints (the intrinsic fabric tax) are measured.
