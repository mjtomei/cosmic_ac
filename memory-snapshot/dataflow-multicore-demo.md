---
name: dataflow-multicore-demo
description: Dataflow multicore as another programmability-limited architecture and a candidate low-hanging-fruit demo — extract the latent NUMA/parallelism gap in ordinary code via automatic dataflow mapping
metadata: 
  node_type: memory
  type: project
  originSessionId: aaa6ff40-df04-4f4b-8a9a-fa58d7a4e24b
---

Matthew's idea (2026-06-22): dataflow is the canonical "too complex to program" architecture — already the paper's central example (companion report `dataflow-vs-heterogeneous`, §2/§10 "lost not on efficiency but on programmability," Figure 5's "AI-accelerator wave is largely dataflow"). **Dataflow multi-core** extends the point to commodity NUMA: today's multicore has NUMA but is very likely **programmer-limited** in complexity and performance — ordinary code under-exposes parallelism and ignores locality, leaving large gains unrealized (§2 effort gap, on hardware everyone already owns).

**As a candidate low-hanging-fruit demo (parallel to the §12 FPGA experiment):**
- Attractive because *no special hardware* — runs on a NUMA multicore box already on hand; task-dataflow runtimes exist (OpenMP tasks, StarPU, Legion, TBB flow graph).
- Isolates the core claim: same hardware, automatic management, measure the latent gap. Uses dynamic info (runtime placement from actual contention/sizes the static program never had) — the hardware-vs-software-cache argument again ([[cxl-unified-memory-idea]]).
- Design: take ordinary (NOT already-HPC-tuned), memory-bound/irregular code; measure its parallel efficiency + NUMA locality; have the commons (automatic / ML-assisted) map it to a locality-aware dataflow/task graph; measure the gain *without* programmer NUMA tuning. Headline: "ordinary code leaves X% on the table; automatic dataflow mapping captures it, no expert effort."

**Preferred path — architectural simulator (Matthew prefers this to the FPGA, 2026-06-22; FPGA still interesting but more effort):** an arch simulator (gem5 primary — multicore, NUMA, coherence, RISC-V/ARM/x86, full-system; Sniper/ZSim/SST = faster, lower-fidelity alternatives) is not just lower-effort — it's the *right* instrument for a what-hardware-to-build thesis: evaluate architectures that don't exist yet on real workloads with full cycle/locality visibility, AND *change the architecture* (conventional cache-coherent SMP vs dataflow-oriented multicore). That **upgrades this from a management-only demo to a genuine Q1 hardware-design exploration** (fixes the earlier "not Q1" caveat). Can sweep commons-quality × workload-diversity to make Figure 4's phase diagram *measured*, not conceptual. Feed it the RISC-V workloads via the QEMU/Spike front-end, or run binaries directly.
Sim caveats: simulation isn't silicon (modeling error; weaker evidence than FPGA — sim *explores + quantifies the relative gap*, FPGA later *validates* a point; flag sim-only results as such); detailed gem5 is slow (need SimPoint sampling / small workloads); the automatic commons-driven mapping is still the crux either way.
**§12 implication — DONE 2026-06-22:** the §12 "A first experiment" passage was reframed in the draft to lead with the architectural-simulator (gem5) dataflow-multicore demo as the accessible first experiment, with the FPGA repositioned as the harder real-silicon validation; Table 4's "Reconfigurable demonstrator" row updated to match.

**Honest caveats:** (1) Tests a *different facet* than the FPGA demo — not Q1 reconfigurable hardware, but automatic/commons-driven *management* extracting latent perf from existing hardware (realization gap / CXL-locality thread). Complementary, not duplicate. (2) "Dataflow runtime beats naive threads on NUMA" is partly *known* (HPC: Legion/StarPU) — to avoid "we reinvented Legion," the novelty must be (a) *automatic* extraction (no expert tuning) and (b) *quantifying the unrealized gap in ordinary code*. (3) Selection caveat (like the FPGA hot-kernel one): pick ordinary, locality-sensitive workloads or there's no gap to show.

**Ties:** the programmer-inversion ([[commodity-shift-and-programmer-inversion]]) applied to the cores you already have — you may use a harder-to-program model (dataflow) because the commons programs it. NUMA locality = the on-node version of [[distributed-logical-machine-telos]]. Candidate second demonstrator for §12, or a more accessible first one.
