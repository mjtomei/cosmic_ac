---
name: ml-on-open-eda
description: "Turn machine intelligence on the open EDA tools themselves — optimize OpenROAD's steps, replace verifiable steps with small learned models; openness is the precondition for ML compounding"
metadata: 
  node_type: memory
  type: project
  originSessionId: aaa6ff40-df04-4f4b-8a9a-fa58d7a4e24b
  modified: 2026-07-18T19:19:18.797Z
---

Matthew's idea (2026-06-22): point ML at **OpenROAD** to optimize all its steps ("optimize the optimizer"), and replace some steps with pure ML generation — ideally a small net we train ourselves ([[dataflow-multicore-demo]]-adjacent scale; TRM-style "Tiny Recursive Models," ~7M params, single-GPU). Rooted in his grad-school observation: even GPT-3 could propose usable improvements to genetic-algorithm optimizer code and implement them.

**The sharp structural point:** openness is the *precondition*, not a nicety — you cannot point a model at Synopsys's placer (the internals are the moat); OpenROAD is the only P&R stack a model can read, rewrite, improve, with improvements landing upstream for everyone. This mechanizes §8's "AI plus pooling compounds" and answers §7's qualifier (commons "has not yet cracked leading-edge EDA") — machine intelligence collapses the contribution cost that kept EDA knowledge tacit/locked in firms. EDA is ideal ML territory because every step has a **hard verifier** (timing, DRC/LVS) → the paper's own §10 line "inference proposes and verification disposes" applies literally.

**Citations (ALL VERIFIED 2026-06-22 by web search):**
- ELM: Lehman et al., "Evolution through Large Models," arXiv:2206.08896 (2022; also Springer *Handbook of Evolutionary ML* 2023) — LLM as mutation operator in genetic programming.
- FunSearch: Romera-Paredes et al., "Mathematical discoveries from program search with large language models," *Nature* 625:468–475 (2024) — cap set + bin-packing heuristics.
- AlphaEvolve: Novikov et al., arXiv:2506.13131 + DeepMind blog May 2025 — production wins: Borg scheduling heuristic recovering ~0.7% of Google fleet compute; 4×4 **complex-valued** matmul in 48 mults (don't say "beat Strassen generally"); 23% Gemini-kernel speedup. All Google self-reported, not independently audited.
- TRM: Jolicoeur-Martineau (Samsung SAIL Montréal), "Less is More: Recursive Reasoning with Tiny Networks," arXiv:2510.04871 (Oct 2025, **preprint only**) — 7M params, 45% ARC-AGI-1. Predecessor HRM: Wang et al. (Sapient), arXiv:2506.21734.
- DSO.ai: Synopsys, launched 11 Mar 2020; 100th commercial tapeout 7 Feb 2023 (press). Cerebrus: Cadence, launched 22 Jul 2021.
- **ORFS-agent** (the find — Matthew's idea is ALREADY HAPPENING): Ghose, Kahng, Kundu, Wang, "ORFS-agent: Tool-Using Agents for Chip Design Optimization," arXiv:2506.08332 (June 2025) — LLM agent tuning OpenROAD flow, ~13% better wirelength/clock with 40% fewer iterations than Bayesian optimization. Plus "Automated QoR improvement in OpenROAD with coding agents," arXiv:2601.06268 (Jan 2026) — coding agents improving OpenROAD itself. AutoTuner baseline: Jung, Kahng, Kim, Varadarajan, ICCAD 2021 (METRICS2.1 + AutoTuner, Ray Tune).
- **AlphaChip — cite as "deployed but contested":** Mirhoseini et al., *Nature* 594:207 (2021); Nature editor's note Sept 2023, resolved with Addendum 26 Sept 2024 (DOI 10.1038/s41586-024-08032-5); pretrained checkpoint released 26 Sept 2024; used in 3 TPU generations + MediaTek. Independent reimplementation found no advantage over SA/commercial baselines: **cite Cheng/Kahng et al., ISPD 2023 (DOI 10.1145/3569052.3578926) — NOT Markov's CACM version (under active ACM do-not-cite integrity notice as of Feb 2026)**. Google rebuttal: "That Chip Has Sailed," arXiv:2411.10053.

**Framing upgrade from verification:** §12 draft should shift from "we propose to point models at OpenROAD" to "this has begun (ORFS-agent, coding agents on OpenROAD) — we join and extend it, and feed results back through the commons." Stronger for the thesis: the commons is already turning ML on itself.

**STATUS: INSERTED 2026-06-22 (Matthew approved):**
1. §7, new paragraph after the "has not yet cracked leading-edge EDA" qualifier — moat-erosion + ELM/FunSearch/AlphaEvolve lineage + ORFS-agent/coding-agents + DSO.ai/Cerebrus.
2. §12, new paragraph ("The flow itself is a target") between the builds-the-map and Two-honesties paragraphs — **Matthew's added framing:** an *automated tool-development flow* that uses ML wherever it is measurably better, with fair/open comparisons (same benchmarks, same verifiers, in public) built in structurally — the lesson of the AlphaChip debacle (he blames the authors/process, not ML; paper frames it as "baselines and benchmarks were never agreed," citing Mirhoseini Nature 2021 + Cheng ISPD 2023, NOT Markov). TRM cited as "(Jolicoeur-Martineau, 2025)" for one-person-trainable step replacement.
3. Table 2 EDA hoarded cell now includes "and their new RL optimizers (…; DSO.ai, Cerebrus)".

Related: [[standards-coordinate-interface-not-competence]] (generative competence applied to the tool layer), [[commodity-shift-and-programmer-inversion]].
