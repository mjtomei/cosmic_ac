# S9 — Continuous FPGA acceleration by machine intelligence: session plan

*Created 2026-08-05; related-works pass completed same day (4 web agents:
warp-processing citation graph, application-slate verification, LLM-for-
hardware state of the art, Zybo Z7 feasibility — all anchors below verified
from primary sources unless flagged). Supersedes
`plans/S8-dataflow-multicore-gem5.md` as the active architecture study; that
file keeps the dataflow/limit-study ledger and the parked rung-0 ideal-ASIC
bound. Self-contained: a fresh session can execute from this file.*

## 0. What the study is actually about (Matthew, 2026-08-07 — governs
everything below; earlier text that called the accelerator long tail "the
thesis case" was wrong and is corrected in §4)

> *"The sea of accelerators isn't really the thesis. I would be just as happy
> with a general purpose soft core getting optimized. It's about the
> optimization loop getting much smaller. And I'd also be happy just with
> identifying that if the NRE of an ASIC was zero, massive benefits would be
> possible given machine intelligence. That would put a new pressure on NRE."*

**The thesis is loop size.** The claim under test is that machine
intelligence collapses the cost of a full optimize-measure-redesign cycle —
in human effort, wall-clock, and money — by enough to change *what is worth
optimizing at all*. The artifact that gets specialized is an implementation
detail, and any of these outcomes is a success:

1. **Per-application accelerators** (the tier-1/tier-2 slate in §4) — the
   classic warp-processing target.
2. **The general-purpose core itself gets optimized** — retuned
   microarchitecture, custom instructions, ISA extensions, cache/predictor
   parameters, fabric-side helpers, all discovered and validated by the loop.
   Equally satisfying, and often *better conditioned* than the long tail
   because the beneficiary is every workload rather than one kernel. (Sweep
   comparators sitting here: ISAMORE, LACE, Icicle.)
3. **The zero-NRE counterfactual** — establishing that *if* the
   non-recurring engineering cost of a design were ~zero, machine
   intelligence makes large gains available. That is a finding in its own
   right: it relocates the binding constraint onto NRE and puts economic
   pressure there. It is also the direct descendant of the parked rung-0
   ideal-ASIC limit (`plans/S8-dataflow-multicore-gem5.md` §3 Phase B) —
   that bound *is* the zero-NRE question asked in physics units, and this
   study asks it in engineering-cost units.

**Consequences for how we work.** Log loop cost, don't study it (scoped
2026-08-07, Matthew: *"the loop cost tracking idea is too much for the amount
of methodology we have planned. I don't think we will be doing a proper
control. But we should track those metrics still. We will be spending our
time just trying to get good results at all."*). So: record wall-clock,
agent cost, human interventions, and build/measure iterations per accepted
optimization as **cheap instrumentation that runs automatically** — no
control group, no human-counterfactual arm, no claim resting on the series.
It is there so that if the numbers end up telling a story we can point at it,
and so we notice our own overheads; the effort goes into getting good results
at all. A finding that some target class is uneconomic
(see the sea-of-accelerators challenge in §4) is not a failure of the thesis;
it is a measurement of where the loop's reach currently ends, and it points
at what would have to change (coupling, fusion, or NRE) for the reach to
extend.

## 1. The task statement (Matthew, 2026-08-05)

An LLM fully replacing what a human engineer would do given this standing
task: **always be watching what is running on a processor, and accelerate
pieces of it as efficiently as possible** — on the attached FPGA fabric.

Framing: the dataflow-multicore (S8) and FPGA (S9) studies are the *same
study* — two possible more-complicated target architectures for one
continuously-optimizing intelligence. FPGA first: mature tooling absorbs
placement/scheduling, and the hardware is in hand (Matthew's Zybo Z7).

**Three modes of the intelligence, all in scope (their comparison is itself
a result):**
1. **Tool-driving** — manage the existing toolchain: HLS directives,
   synthesis/P&R, timing closure, error repair, interface generation. The
   toolchain's complexity is a documented real-world bottleneck; managing it
   away is a result with zero algorithmic novelty.
2. **Hand-designing in loops** — write RTL/HLS directly where tool output is
   poor, iterating against simulation and on-board measurement.
3. **Optimizing the optimization loop itself** — improve its own profiling
   heuristics, selection models, pragma strategies, scripts, and prompts,
   with measured end-to-end QoR as fitness.

## 2. The historical anchor: warp processing, verified

The exact idea has run once before. **Warp processing** (Vahid, Lysecky,
Stitt; DAC 2003 → the canonical paper: Lysecky, Stitt & Vahid, "Warp
Processors," ACM TODAES 11(3):659–681, 2006): non-intrusive on-chip profiler
→ binary decompilation to CDFG → lean on-chip synthesis/place/route onto a
custom fabric → binary patched to invoke hardware. Measured: **6.3× average
speedup, 66% energy reduction** over 15 embedded benchmarks; the on-chip CAD
ran in **1.2 s average on a 40 MHz ARM7 within 3.6 MB** (folk "~10 MB" is
wrong). Soft-core variant (DATE 2005): 5.8× avg, 57% energy vs MicroBlaze
alone. Thread Warping (CODES+ISSS 2007): avg 130× — with the honest flag
that the fabric equaled 36 ARM11s of area. Retrospective with every honest
limitation: Vahid, Stitt & Lysecky, IEEE Computer 41(7):40–46, 2008.
**Citation trap:** Crossref carries a phantom "Warp Processors, DAC 2004,
pp. 659–681" record — an ACM metadata artifact; cite TODAES 2006
(10.1145/1142980.1142986), never the DAC-2004 phantom.

**Why it died — four walls (their own words):**
1. **Amenability.** "We only considered applications... whose critical
   regions don't use floating-point arithmetic, dynamic memory allocation,
   recursion, or pointers"; on SPEC, "little speedup" (Computer 2008).
2. **Toolchain cost.** On-chip CAD was feasible only on a custom fabric no
   vendor shipped (commercial routing "not amenable to on-chip execution",
   TODAES 2006); on commodity FPGAs, "stalling an application for several
   hours to compile one FPGA kernel will likely not be accepted" (Stitt,
   "Are FPGAs Ready for the Mainstream?", IEEE Micro 31(6), 2011 — the
   line's field verdict: barriers are "amenability, cost, and productivity").
3. **Selection.** Nobody ever shipped the choosing step: SDSoC's docs tell
   the human to profile and mark functions in a dialog; automation shipped
   only by domain collapse (NN inference: Vitis AI, Mipsology) or by manual
   hyperscale engineering (Catapult, ~1M FPGAs).
4. **Economics.** The platforms retreated: SDSoC killed 2019 ("no 2019.2 or
   future releases"), Intel oneAPI-FPGA killed 2025, HARP terminated, Xeon
   6138P had no successor, Altera spun out. Each academic line ended with
   its students, not with a refutation.

**Lineage (extend, don't re-find):** direct heirs — UFRGS DIM→CReAMS→HARTMP
→TransRec (hardware DBT to CGRA, DATE 2008–2019); U. Porto Megablock line
(TII 2013 → FPL 2020/IEEE Micro 2021), whose survey is the field map:
Paulino et al., ACM Computing Surveys 53(1):6, 2020 (genre-wide 2.6–5.6×);
DORA (HPCA 2016 — warp on a DySER CGRA, runtime translation beats the static
compiler, 1.99× vs manual 3.6×); QsCores (MICRO 2011). Parallel
reinventions (verified no warp citation): Conservation Cores/GreenDroid
(ASPLOS 2010), DynaSpAM (Liu/August, ISCA 2015 — harvests the OOO schedule
as the mapping), Chainsaw (MICRO 2016), NEEDLE (Kumar et al., HPCA 2017 —
path-based extraction, 34% perf/20% energy, the best "which code exactly"
science), AccelSeeker (ICCD 2019, +RegionSeeker TCAD 2019 — merit/cost
selection under area budget without running HLS, targets Zynq). Deployment
substrate (orthogonal, reusable): ReconOS/BORPH → AmorphOS/FOS → Coyote v2
(SOSP 2025). Selection/profitability models: COSYMA/Vulcan (1993), Aladdin +
gem5-Aladdin, LogCA (ISCA 2017), Gables, **Accelerometer (ASPLOS 2020 — the
model to adopt, ≤3.7% error on production offloads)**; learned cost models
(Ithemal→GRANITE, ProGraML). NB: no canonical citation exists for the folk
"~10× kernel speedup to survive the interface" rule — derive from
LogCA/Accelerometer instead.

## 3. Positioning

> **Framing, Matthew 2026-08-07 (governs this whole section):** *"It's not a
> problem if we found people doing similar things, it's good in fact. We are
> not trying to carve out a niche for a conference paper. Where I expect we
> will excel if there is enough focus is getting best-in-class results from
> the flow and coming up with interesting optimizations and meta
> optimizations. Also in using it day to day."*
>
> So: **neighbors are shoulders and comparators, not threats.** The success
> criteria are (1) best-in-class results out of the flow, (2) genuinely
> interesting optimizations and meta-optimizations, (3) the thing actually
> gets used day to day. Novelty language below is retained as *situational
> awareness* — knowing who solved what, and whose numbers to beat — not as a
> claim to defend. Practical consequences: adopt others' machinery freely
> (Accelerometer/LogCA cost models, AsmDB's store schema, FirePerf's
> out-of-band trace design, AgRefactor's self-evolving memory, Icicle's TMA
> events); prefer *their* benchmarks where a head-to-head is possible; and
> report where we lose, since that is what makes the wins credible.
> The 2026-08-06 sweep found 64 threat-flagged works — under this framing
> that is a rich comparator set, and the reading shelf now carries all of
> them (see `00-MANIFEST-D.md`).

Two adjacent claims, both checked 2026-08-05 (and substantially narrowed by
the 2026-08-06 citation sweep — see §3.5):

- **The niche is empty.** An arXiv query "hardware/software partitioning" +
  "large language model" returns **zero results**. No published system
  combines autonomous whole-application profiling-driven kernel selection +
  HLS/Vivado flow to bitstream + agent-driven error repair and timing
  closure validated on a real board + self-improvement of its own loop.
- **The neighbors are close and 2026-fast.** Position against, explicitly:
  **HLSPilot** (Xiong, Liu, Li & Li, ICCAD 2024) — gprof→hot-kernel→GPT-4
  C-to-Vitis-HLS→classical-autotuner DSE→Alveo U280; automates optimization
  of designated kernels, not continuous selection, and no self-improvement.
  **ContractHIL-HLS** (arXiv:2607.25283, Jul 2026 preprint) — multi-agent
  HLS→Vivado→PYNQ hardware-in-the-loop incl. power; works from per-task NL
  specs, not from profiling whole applications. Also C2HLSC (TODAES 2025 —
  LLM rewrites C to synthesizable form: the amenability wall, solved in
  isolation) and IBM "Agent Factories" (arXiv:2603.25719, v2 read in full
  2026-08-05 — off-the-shelf Claude Code (Opus 4.5/4.6) agents in a
  two-stage factory (per-kernel pragma/code variants + ILP assembly, then
  N exploration agents doing cross-function restructuring) reach mean
  7.07× on twelve HLS-Eval/Rodinia kernels, peaking at N=8 agents
  (non-monotonic: 6.53× at N=10). **Baseline caveats:** speedups are vs
  the *unoptimized* design; the auto-search control is a deliberately
  restricted per-loop pragma enumeration (5 options/loop) — their own
  limitations concede no AutoDSE-class or expert-human comparison; and
  the v2 intro still carries stale v1 numbers (8.27×, streamcluster 20×)
  that the abstract/results moderate — cite abstract/results figures
  only. Validates the *capability* premise (untrained frontier agents do
  expert-recognizable restructuring, rediscovering ARRAY_PARTITION and
  the pipeline-after-dependences pattern), not superiority — the
  beats-real-autotuner evidence is LIFT and LLM-DSE. Stops at synthesis
  reports: no board, no energy, no selection, no self-improvement).

**The claim, framed per the build-on-published-work rule:** every barrier
that killed warp processing is a judgment/productivity bottleneck that LLMs
directly address — amenability (LLM rewrites non-amenable constructs;
C2HLSC), selection (compose AccelSeeker-class merit/cost + Accelerometer's
interface-cost model into a closed loop), toolchain cost (minutes-to-hours
of off-critical-path Vivado runs, amortized by choosing well; DFX hot-swap
at deploy), economics (commodity Zynq + the plumbing SDSoC/XRT left
behind). What no prior system had is what Stitt named as binding:
**productivity — an unbounded supply of engineering judgment.** S9 is the
warp loop closed on commodity hardware with that supply. The pieces are all
credited; the composition and the autonomy measurement are ours.

## 3.5 The comparator set (2026-08-06 sweep; API-level finds — verify each
before citing, several are weeks-old preprints)

Grouped by which part of S9 they can be measured against. **Every work below
is now on the shelf** (manifest D), unranked.

- **Closest whole-flow neighbors:** A3D (Purdue, arXiv 2605.15237 — agentic
  workload analysis → bottleneck ID → HLS refactor → microarchitecture gen →
  DSE); HSCO-Bench (Carloni's group, arXiv 2605.19399 — states the same
  three-step task and **deploys on real FPGA**, so on-board validation is a
  shared bar, not a differentiator); SECDA-DSE (LLM DSE inside a
  SystemC+FPGA methodology, targets Zynq-7000); Cayman (DAC — non-LLM
  end-to-end automatic kernel extraction + accelerator gen); **Needle (HPCA
  2017, already on the shelf) — the strongest single narrowing: profiling-
  driven automatic region selection + HLS + FPGA SoC deployment, no human
  designating kernels.**
- **HLS-agent neighbors (mode 1/2 comparators — use their benchmarks):**
  AgRefactor (self-evolving memory across designs), HLS-Seek (QoR-aware RL
  with a proxy reward — directly occupies "QoR as fitness"), A2H-MAS
  (FPGA'26, peer-reviewed algorithm→HLS→FPGA), C2HLSC, Agent Factories,
  Evidence-Driven C-to-synthesizable-C agent.
- **Self-improvement (mode 3) comparators:** Dr. RTL (cross-design skill
  library), Self-Evolved ABC, Magellan + AI-PROPELLER (evolved compiler
  heuristics against *fleet profiles*), AccelOpt (self-improving on real
  Trainium silicon), KernelBlaster, Agentic Harness Engineering
  (observability-driven evolution of the agent harness itself — closest
  statement of our meta-optimization goal), HORIZON, Autopoiesis.
- **Observer comparators:** PRAGMA and KernelPro (profiling-in-the-reasoning-
  loop on GPU/NPU — the observer idea, one substrate over); MOA and
  PerfAgent (profiler-evidence-driven code optimization); McDougall &
  Sankaralingam's in-field programmable introspection units (**the live
  realization of our observation thesis minus the LLM**); Icicle (full TMA on
  Rocket/BOOM — the soft-core observation bar to beat); μgrind (dynamic
  instrumentation injected into HLS output); Jafri et al.'s centralized
  multicore performance-monitoring architecture.
- **History we should have had:** Morph (SOSP 1997 — our standing task posed
  as an OS service); the MicroBlaze warp processor (TECS 2009 — the entire
  loop on a soft core, 2009); ISAMORE (ASPLOS 2026 — automatic reusable
  custom-instruction discovery).
- **Critiques to answer:** "When Faster Isn't Greener" (ASE 2025 — LLM code
  optimization's *energy* break-even point: how many executions before the
  optimization repays the compute that found it — this one bites our energy
  framing directly); "AI for Systems is AGI-Complete" (ECO's own authors).

## 4. Who it's for (application slate, verified)

**Fleet evidence:** Google's datacenter tax = **22–27% of all fleet cycles**
(Kanev et al., ISCA 2015, body text; "nearly 30%" is abstract-only; the
number is deliberately an underestimate, and kernel cycles — ~20% of fleet,
scheduler alone >5% — are *excluded* from it). Components: protobuf, RPC,
hashing, compression (~¼ of tax), allocation (no % stated — do not invent
one), memmove (4–5% of fleet). Meta's fleet confirms: microservices spend
"as few as 18% of CPU cycles executing core application logic"
(Accelerometer, ASPLOS 2020). **Flatness — the tier-2 thesis case, in
Google's own words:** hottest application ≈10% of cycles, 50 apps to reach
60%, top-50 coverage falling ~5 pts/year (Kanev); within one binary the
hottest function is 6.3% and 353 functions make 80% (Kanev, search3);
covering ⅔ of front-end misses means ~1M code locations, "only conceivable
with automation" (AsmDB, ISCA 2019); "no single accelerator can provide a
significant benefit but collectively, a sea of accelerators, can" (Gonzalez
et al., ISCA 2023). Client side: "Programmability is a primary roadblock
for using mobile co-processors" (Wu et al., HPCA 2019, >2,000 unique SoCs);
hardware video decode uses <9% of software-decode energy (Kränzler, PCS
2024) — the prize, where specialization did clear the threshold.

**THE SEA-OF-ACCELERATORS CHALLENGE (the ranking pass's most substantive
red flag — 36 of 156 flags, from six independent reviewers).** The premise
under fire is tier 2: *because fleet profiles are flat, the win lies in
accelerating each application's own below-threshold hot code — many small
accelerators, collectively significant.* Four papers on our own shelf say
the economics fight this:
- **LogCA (ISCA 2017):** speedup needs granularity above a break-even point
  g₁ set by offload overhead o + latency L, and *g₁ barely depends on how
  fast the accelerator is*. Measured: in-pipeline SPARC-T4 crypto breaks
  even at **128 B**, on-die UltraSPARC-T2 at **32 KB**, a PCIe card at
  **256 KB**. Sub-linear kernels (β<1) can *never* break even without
  computational intensity C/L > 1; their binary search never wins at any
  size up to 32 MB. Long-tail kernels are small-granularity by construction
  — precisely the losing regime.
- **Accelerometer (ASPLOS 2020):** the per-invocation cost (o₀+Q+L)·n makes
  net speedup negative when per-kernel share a is small — the flat tail is
  the *hardest* case, not the opportunity.
- **AccelSeeker (ICCD 2019):** breadth-first selection of many small leaf
  functions — literally the long-tail play — "fail[s] to achieve high
  performance" from invocation overhead. They measured it; it lost.
- **Conservation Cores (ASPLOS 2010):** full-application results show
  per-function speedup **0.96–1.15×** and execution time *rising up to 22%*;
  the win was energy/EDP only. Warp processing independently caps benefit at
  four regions ≥10% of execution.

**Response (design changes, not rhetoric).** (0) **Scope, per §0: this
challenges one target class, not the study.** If the tail is uneconomic at
our coupling, the loop-size thesis stands and the work redirects to
core-level optimization (§0 outcome 2) and the zero-NRE counterfactual (§0
outcome 3) — where, note, the same LogCA math is *favourable*: in-pipeline
integration breaks even at 128 B, which is what optimizing the core rather
than bolting things beside it buys you. (1) Tier 2 is a *hypothesis under
test*, not an assumption — the honest possible finding is "the tail is
uneconomic at AXI/DMA coupling," which is publishable and useful. (2) The
selection stage must compute g₁ and predicted net speedup **before**
spending build time — adopt LogCA parameters + the Accelerometer model as
the profitability gate, and report predicted-vs-measured as a first-class
result (this is also the cheapest meta-optimization: the agent learns its
own cost model). (3) Two escapes are designed in rather than hoped for:
**fusion** — accelerate *chains* of tail kernels to raise C and amortize one
invocation (the "sea" becomes an archipelago), and **coupling** — phase 2's
in-pipeline soft-core hooks are exactly the 128 B-break-even regime, which
is why the soft core matters beyond observation. (4) Energy is a legitimate
win even where latency isn't (c-cores' own result) — so the fitness function
carries an energy term from day one, and see the ASE-2025 energy-break-even
critique in §3.5. (5) Tier 1 controls stay in precisely because they are the
regime where offload is known to pay: they prove the flow works before the
economics get hard.

**Tier 1 — controls (hardware answer known; validates the flow):**
memcpy/memmove (DSA), (de)compression (QAT/IAA shipping; CDPU ISCA 2023:
2.9% of fleet, 10–50% of key services, 10–16×/core), protobuf (**the
at-threshold boundary case**: ProtoAcc MICRO 2021, 3.8× vs Xeon, prototype
never deployed), AES/SHA (absorbed into ISAs 2010–2016; Accelerometer's
validated case study), hashing/CRC, video (VCU ASPLOS 2021, 20–33×
efficiency, deployed), network stack (AccelNet NSDI 2018, >1M hosts), and
memory allocation (**a tax kernel with no deployed accelerator — the
below-the-line control in the other direction**).

**Tier 2 — one instantiation of the thesis, not the thesis itself
(corrected 2026-08-07; see §0): the below-threshold long tail.** If its
economics fail (see the challenge below), the loop-size claim is untouched
and the finding relocates to §0's outcomes 2 and 3. Flat-profile
service leaf functions; per-platform data operators (Gonzalez's sea);
logging (23% of Web-service cycles, Accelerometer — no accelerator exists);
ML-serving orchestration glue (42–67% of inference-service cycles; infinite
inference speedup nets only 1.49–2.38×); irregular hot paths in ordinary
compiled code (NEEDLE: no dominating path among >100K); client-side JS/app
code. Explicitly not targets: HPC and mainstream ML — the herd's two
well-served domains. Honest counterweight: top 1000 binaries still capture
90% of fleet cycles (AsmDB) — the tail is long, not infinite.

**On the Zybo, concretely:** tier-1 kernels (zstd/gzip, SHA/AES, memcpy
variants, protobuf-style ser/deser) as smoke tests and calibration against
known hardware answers; tier-2 = hot loops from real programs the flow picks
itself (SPEC/PARSEC-class + real applications), where the selection stage,
not the kernel library, is under test.

## 5. Hardware and platform (verified 2026-08)

- **Board: Zybo Z7-20** (Matthew, 2026-08-05: "I think I have the Z7-20" —
  confirm on the silkscreen/part marking at bring-up). XC7Z020: 53.2K LUTs,
  220 DSP, 4.9 Mb BRAM — fits several kernels + DFX slack, and shares its
  exact part (xc7z020clg400) with PYNQ-Z1/Z2, so that ecosystem retargets
  with a constraints-file change. (If it turns out to be a Z7-10: 17.6K
  LUTs, 80 DSP — one modest kernel at a time; tier-2 ambitions shrink.) Both: dual Cortex-A9 @667 MHz
  (NEON), 1 GiB DDR3L @ ~4.26 GB/s peak. Fit intuition: an XAPP1170-class
  FP32 32×32 HLS matmul ≈ 3.5K LUTs + 10 DSPs (~6.5% of a Z7-20).
- **Toolchain, two tracks:**
  - *Track A (primary QoR):* Vivado 2026.1 — Zynq-7000 fully supported (the
    "7-series frozen" rumor is false), free Basic tier incl. Vitis HLS and
    DFX. **x86_64-only, no ARM plans (UG973)** — the GB10 cannot run it
    natively. Live workaround: **FEX-Emu**, which merged Vivado-specific
    fixes in 2026 (PRs #5355, #5618); trial batch/Tcl-mode Vivado under FEX
    on the GB10 in week 1. Pre-provision the fallback: any x86_64 box or
    spot cloud instance driven over SSH (architecturally identical to the
    agent's loop). Schedule risk, not feasibility risk.
  - *Track B (native, parallel):* **openXC7 0.9.x** — aarch64-native (Nix),
    covers xc7z010/020 via prjxray, and **post-route timing analysis landed
    July–Aug 2026** (XDC clocks, per-clock Fmax, delays cross-validated
    against Vivado; DSP timing still "phase 1"). PS7 side via regymm/GenZ.
    F4PGA is dead; openXC7 is the successor. Usable with margin and a
    measurement loop, not as signoff — keep Vivado as QoR reference. A
    fully-native no-emulation flow for the agent is also a result axis.
- **Runtime:** community PYNQ 3.0.1 prebuilt images exist for both Zybo
  variants (nick-petrovsky/PYNQ-ZYBO; tools 2022.1) — Jupyter + overlay
  loading + MMIO/DMA from Python: the ideal agent substrate. Verify the
  dtb carries the A9 PMU node (`arm,cortex-a9-pmu`) or perf events read
  `<not supported>`; patch DT if needed. Fallback: mainline kernel (Zynq
  is first-class in torvalds/master) + Debian rootfs.
- **DFX:** free since Vivado 2019.1, Zynq-7000 supported (UG909); 7-series
  rules: pblocks aligned to clock regions; partials delivered via PCAP from
  the PS — the agent swaps kernels without reboot.
- **PS↔PL:** 4× AXI_HP (~600–1,200 MB/s per port measured, DDR caps ~4.26
  GB/s system); ACP single coherent 64-bit port (>1.6 GB/s full duplex
  measured) — HP for bulk streaming, ACP for small tightly-coupled working
  sets (kills flush/invalidate), GP for CSRs only.
- **Power:** the board self-measures — TPS25940 eFuse IMON routed to the
  XADC (total input current, ±5–10%): the agent reads energy per experiment
  scriptably. Bench supply/inline meter on the 5 V jack for headline
  numbers. USB power alone is marginal under load.

## 5½. The stack, nailed down (2026-08-05; Matthew: open-source HLS
preferred, soft-core hooks endorsed as a novelty source. Facts marked (v)
verified earlier today; (p) pending the toolchain-verification agent)

**FPGA flow — open-first, commercial-as-reference (all verified
2026-08-05):**
- **HLS: Bambu (PandA) primary** — active (release 2024.10, dev benchmarks
  through Jul 2025), the only open HLS with real pointer/dynamic-memory C
  coverage (DAC 2021 paper), Verilog out with a documented Yosys backend.
  QoR honesty (Nane et al., IEEE TCAD 2016 — the only rigorous
  academic-vs-commercial head-to-head): Bambu *matched/beat* the
  commercial tool on geomean wall-clock (16.6 vs 19.9 µs) at ~1.3× LUTs;
  no newer independent comparison vs Vitis exists — today's practical gap
  is interfaces/pragmas/robustness, not raw QoR. **Week-1 action item:
  Bambu has no advertised aarch64 build — test-build on the GB10 first
  thing; fallback is running the HLS step on the x86 box.** Dynamatic
  (EPFL, active, MLIR rewrite) as the *dataflow arm* — same kernel
  through statically-scheduled Bambu vs dataflow Dynamatic is the S8
  two-architectures comparison in miniature; NB its documented flow is
  Vivado-only, so the dataflow arm may ride the reference track. XLScc
  ruled out (no pointers — wrong tool for existing C); LegUp open version
  dead (frozen 2015, now Microchip SmartHLS). Vitis HLS = QoR reference
  only.
- **RTL→bitstream: openXC7 (Yosys + nextpnr-xilinx) primary** —
  aarch64-native on the GB10; covers Zynq-7; **timing nuance reconciled:
  0.9.x added timing *analysis* (post-route Fmax reporting), but P&R is
  still not timing-*driven* — the agent iterates against reported Fmax
  with guard-banded clocks.** GenZ for PS7 config; and the openXC7
  demo-projects repo already contains our exact ingredients: a PS7+AXI
  design for xc7z020, Zybo blinky, and vexriscv/vexriscv-SMP demos.
  **Vivado-under-FEX as the reference track**: QoR comparison + signoff
  sanity, not the loop's inner tool.
- **Consequence, embraced (sharpened 2026-08-07):** open-flow QoR is below
  Vivado's and Bambu's below Vitis — so the agent measures the delta
  *continuously* on every design it builds. Two things follow, and both are
  wanted. (a) Walter-style toolchain-gap evidence, generated by our own
  loop, free. (b) **The honest hazard, accepted with a rule:** a weaker open
  flow leaves headroom the agent can claim as "speedup." Matthew: happy with
  that, because agent-recovers-open-flow-headroom *is* the NRE-lowering
  result — intelligence substituting for license fees. The rule (see §7):
  headline speedups anchor to the **commercial** reference; the
  gap-closing number is reported alongside as the NRE finding. Never one
  without the other.
- **Deploy: PYNQ 3.0.1 (v)** on the Zybo, DFX partials via PCAP (v),
  overlays + MMIO/DMA from Python.

**Profiling setup — three instruments, one execution store:**
1. **Always-on sampling (host + board):** system-wide perf on the GB10
   (pending the paranoid sysctl); on the Zybo, a perf daemon over the A9
   PMU with a fixed TMA-lite multiplex set (cycles, instructions, L1D/L1I
   miss, PL310 L2 events, branch mispredict, stall proxies) + PTM→ETB
   4KB control-flow snapshots on trigger (v: mainline dtsi + OpenCSD).
   Output: continuous low-rate feed into the execution store.
2. **Observable twin (GB10):** QEMU-system with icount record/replay +
   TCG plugins (exec-count/hotblocks + memory-access streams), replay-
   on-demand under the LLM's hypotheses; QEMU covers BOTH deployment ISAs
   (arm for the A9, riscv for the soft core) — one twin substrate, two
   targets. Reduced facts (per-symbol counts, BBV/SimPoint phases, call
   graph, syscall/process timeline) land in the **queryable execution
   store** (the unbuilt primitive we build: sqlite/parquet + a diff
   operator over runs).
3. **The invasive instrument (in-fabric): an instrumented soft core —
   VexRiscv, verified.** Plugin architecture confirmed ("almost nothing
   is fixed"; plugins inject signals at one pipeline stage and read at
   another — the exact substrate for observation hooks); FormalPlugin
   already emits RVFI-style commit reports (pc, instruction, register
   writes, memory address/data per retired instruction) — our hook is
   that plugin generalized into a streaming retire+memory port, out over
   an AXI HP port to PS DRAM. Size/speed verified: 0.5–2K LUTs/core
   (full+MMU 2,021 LUTs) — trivial in 53K, room for SMP + accelerators;
   plan 50–100 MHz on the Zybo's -1 grade. Linux via linux-on-litex-
   vexriscv (active); LiteX has first-class Zynq-7000 PS7 integration
   (AXI GP/HP wiring in-tree); a Zybo Z7 target file is a small
   well-precedented addition. Fallbacks: NEORV32 (ready-made RVFI trace
   port + hardware TRACER, but no MMU → no Linux); CVA6/Rocket size-risky
   on this part.

   **rv64 upgrade path — verified viable (2026-08-05), trial it:**
   Matthew asked why not 64-bit; the answer is we can, with margin, on
   the SpinalHDL lineage specifically. **NaxRiscv RV64IMASU: 17.9K LUTs
   @ 137 MHz (Artix-7 -3; no FPU — add ~est. 4–8K for F+D, extrapolated,
   no published figure), with Debian riscv64 DEMONSTRATED at 100 MHz on
   a -1-grade Artix-7** (Nexys Video — same fabric/speed grade as our
   part). **VexiiRiscv** (the actively developed successor, also
   SpinalHDL/plugin-based, in-tree LiteX `--cpu-variant=debian` RV64GC,
   official Debian rootfs instructions) is the better trial: its
   rv32-linux config is only 3.35K LUTs; rv64gc plausibly ~8–12K
   (extrapolation, flagged). Rocket RV64GC fits a 7020 (Zedboard
   precedent, ucb-bar/fpga-zynq) but at 25 MHz eating most of the
   fabric; **CVA6 confirmed too big** (~55–60K LUTs on 7-series, over
   even an A7-100T with FPU). Prerequisites verified: Debian trixie
   riscv64 is official with **RV64GC baseline — FPU is mandatory** for
   stock userspace; 1 GiB headless is comfortable (512MB–1GB boards are
   supported Debian riscv64 hardware); **trixie ships Node 20.19 for
   riscv64** — Node workloads under invasive observation become possible
   on the rv64 subject, which rv32 can never offer. Red flags: no
   published rv64+FPU LUT number (trial synthesis is the decider);
   official Fmax figures are -3 grade; the Nax/Vexii-through-PS-DDR
   (AXI HP) LiteX integration is unpublished (VexRiscv-on-Zynq
   precedents exist).

   **Why rv64 cores looked big — resolved (Matthew's question,
   2026-08-05): the cores' performance ambitions, not the ISA.**
   Fundamental costs are only (a) ~1.5–2× datapath scaling — VexiiRiscv's
   rv64i base is 2,157 LUTs, VexRiscv-class small at 64 bits — and
   (b) the D-precision FPU, mandated by Debian's lp64d ABI and in
   practice by V8's JIT (JS numbers are doubles — Node needs hard float
   regardless of distro); the famous rv32 2K-LUT figure "cheats" via
   soft-float Buildroot userspace. NaxRiscv's 17.9K is OoO dual-issue;
   CVA6/Rocket are big-core designs. Honest estimate for a *minimal*
   Debian-capable RV64GC Vexii (single-issue, in-order, small caches,
   iterative FPU): ~8–13K LUTs (extrapolated, flagged).

   **Topology revision (Matthew, 2026-08-05: "if the hard core has
   enough visibility and runs Claude Code we can try that too... that
   would leave more for the accelerator piece anyways") — A9-primary,
   soft core deferred:**
   - *Phase 1 default:* the **A9s are the watched machine**; the fabric
     spends its LUTs on **accelerators + observation capture blocks**,
     not on a soft core. A9 visibility is unusually good for a hard CPU:
     PMU counters + PTM control-flow trace, with the **TPIU→EMIO→PL
     sustained-capture block as a phase-1 build item** (the fabric
     watching its own CPU — an observation artifact in its own right).
     What the A9 can never give: memory-address/value streams (no SPE on
     this generation; PS DDR traffic doesn't traverse the PL) — that is
     the one capability reserved to a soft core.
   - *Claude Code on the A9 — plausible enough to try:* Debian trixie
     ships Node 20.19 for **armhf** (verified), ripgrep is packaged, and
     the pinned ≤2.1.100 JS release runs on Node ≥18. The wall is
     memory: 1 GiB total (shared) vs the 4 GB stated requirement —
     expect it to limp with zram/swap for small tasks at 667 MHz V8
     speeds. Run it as a cheap experiment; **agent-on-GB10 over SSH
     remains the working configuration.**
   - *Phase 2 (when memory-stream visibility earns its area):* add the
     instrumented soft core. **DECIDED (Matthew, 2026-08-05): the
     minimal rv64 core — VexiiRiscv, smallest Debian-capable RV64GC
     config (single-issue, in-order, small caches, iterative FPU).**
     The week-1 trial synthesis now *validates* the choice (fit/Fmax on
     xc7z020clg400-1) rather than deciding it; fallback ladder only if
     it misses badly: NaxRiscv rv64 (Debian-proven at 100 MHz on -1
     Artix) → rv32 VexRiscv + Buildroot as emergency floor. The
     observation plugin targets VexiiRiscv's plugin API from the start.

   armhf fact-check: Debian 13 still ships armhf officially (armel is
   the one sunsetted) — the A9 full-userspace arm is safe through
   ~2028–2030. Plus PL-side AXI monitors on accelerator ports, and the
   stretch (documented: UG585 + AMD AR 46915): TPIU→EMIO A9 trace
   captured in the PL — needs a PL-side PTM packet decoder.

   **Novelty, scoped by the verification pass (cite generously, claim
   narrowly):** soft-core-visibility profiling is prior art — FirePerf
   (ASPLOS 2020: TracerV cycle-exact out-of-band instruction trace +
   AutoCounter automatic counter insertion, on FireSim, feeding a human
   architect), TIP (MICRO 2021), and the ABACUS/LegUp line — LegUp
   already wired an on-FPGA hardware profiler on a soft MIPS into HLS
   partitioning in 2011, with function-level counts and human-directed
   selection. **The defensible novel conjunction: a deployed (not
   simulated) soft core + per-instruction/memory-stream hooks + a fully
   open toolchain + automatic acceleration decisions + the observer
   co-designing its own sensors.** Never claim "first to profile via
   soft-core hooks."

**Topology (Matthew, 2026-08-05: profiling on the GB10 can't close the
loop — the board must be the watched machine):**
- **The Zybo is the subject** — self-contained: workloads + sensors +
  acceleration substrate on one stack, every optimization testable in
  situ. Two subject processors on one die, same fabric, same flow:
  the **A9s** run the full ported workload mix (Debian-class armhf
  userspace — python/matplotlib/weasyprint apt-installable, NEON
  baselines) = the realistic watched machine; the **instrumented
  VexRiscv** runs rv32 Linux (LiteX + Buildroot: python3, zstd, openssl,
  git, dropbear all packaged) = the invasively watched machine, for
  workloads where retire/memory-stream visibility earns its keep.
- **The GB10 is the observer's machine** — the agent (Claude Code cannot
  run on rv32: no V8 backend — it SSHes in), toolchain (Bambu, openXC7,
  cross-compilers), QEMU twin, heavy analysis, execution store. SSH is
  the loop's transport; bitstreams/DFX partials push over it,
  measurements come back.
- **Speed honesty:** VexRiscv at 50–100 MHz in-order is ~100–300× a GB10
  core's deficit — subjects run scaled inputs, in kind not in scale;
  that is fine because workloads are subjects, not production. The A9 is
  ~10× the soft core. If 64-bit userspace ever matters: NaxRiscv
  (VexRiscv's rv64 successor) is the upgrade path — fit on Z7-20
  UNVERIFIED.
- **GB10-side profiling demoted to bootstrap scouting** (the Track-0
  anchors keep that role); the twin stays useful because QEMU emulating
  rv32/armhf IS the subject software stack — but it is timing-blind, and
  all decisions ground on the board.
- **Soft cores in daily use — verified context (2026-08-05):** it happens
  exactly where the soft core IS the point. **Precursor/Betrusted**
  (shipped secure-credentials device; VexRiscv ~100 MHz on a Spartan-7
  XC7S50 — correction: not ECP5; the iCE40 runs the EC): chosen so "we
  can thoroughly inspect the implementation of the processor and confirm
  there is nothing out of place" — "instead of a black-box CPU chip, we
  start with inspectable, open-RTL CPU cores... you no longer have to
  accept on faith that a black epoxy rectangle contains precisely the
  circuits it advertises" (bunnie Huang; betrusted.io's program is
  "evidence-based trust in silicon"). **Somlo's self-hosting Fedora
  workstation** (RV64 Rocket + LiteX, 50–75 MHz, FOSDEM 2023): rebuilds
  its own kernel, gcc, AND its own bitstream on itself — trust framing
  again. Vampire V4 / MEGA65: shipped retro computers, daily-driven.
  Nobody daily-drives a soft core on performance grounds (all sources
  candid: Palm-Pilot-to-Amiga-class). **Framing gift: our observability
  rationale is the optimization-side member of the same family as
  Precursor's inspectability — security says "watched hardware can be
  trusted"; we say "watched software can be optimized." Same design
  move, second payoff.**
- **Claude Code on the subjects — verified verdicts:** rv32 VexRiscv:
  cleanly impossible, every door shut (Node has no riscv32 target; V8's
  riscv32 backend deprecated off-by-default; Bun/Deno nothing; QEMU
  dropped all 32-bit hosts and TCI can't rescue qemu-user; box64 is
  64-bit-hosts-only; and ≤512MB-class memory < the 4GB requirement
  anyway). rv64 (NaxRiscv/Rocket-class): technically yes as a demo —
  Debian trixie ships Node 20.19 on riscv64 and unofficial-builds carry
  v17–v25, BUT current Claude Code releases are native x64/arm64
  binaries (the npm package became a wrapper between 2.1.100 and
  ~2.1.198); the route is pinning the last JS release (≤2.1.100,
  engines node≥18) + system ripgrep, on a ≥4GB board, minutes-long V8
  startup at soft-core clocks. **Decision stands: agent on the GB10,
  SSH into the subjects — now with the alternatives verified closed
  (rv32) or impractical (rv64).**

The A9 arm is the *deployment-realism* story (ordinary Linux, NEON
baselines, warp-loop-on-commodity-SoC); the soft-core arm is the
*observation-depth* story (invasive metrics → better selection/mapping
decisions, and the Q1-flavored question: what does a processor look like
when it's designed to be watched?). Both feed the same accelerator flow
and the same execution store.

## 5¾. Radar: the evolvable-hardware ancestor (Matthew, 2026-08-05)

**Adrian Thompson's intrinsic evolution — verified 2026-08-05, nine PDFs
on the shelf (manifest addendum).** The canonical paper: "An Evolved
Circuit, Intrinsic in Silicon, Entwined with Physics," ICES 1996 / LNCS
1259 (1997), pp. 390–405. Verified: GA (pop 50, ~5,000 generations,
2–3 weeks — "it consumed no human time") evolving a 10×10 region of a
Xilinx XC6216, fitness measured on the physical chip; the 1kHz/10kHz
discriminator ran **clockless** ("not a digital system, but a
continuous-time... dynamical system"), functional core **32 cells**, with
grey cells that "cannot be clamped without degrading performance, even
though there is no connected path by which they could influence the
output." **Citation discipline:** the famous "five" disconnected cells is
Davidson's number (New Scientist, 15 Nov 1997), not Thompson's — cite the
paper for the phenomenon, the article for the count; fragility nuance:
~10°C operating window and ~7% degradation on *region* transfer (the
1996 paper never tested chip-to-chip). CACM 1999 resolved the grey
cells: adjacency to signal paths whose time delays matter.

**The part memory forgot — Thompson fixed the fragility himself:**
Thompson & Layzell, ICES 2000 (LNCS 1801): evolution run on **four chips
simultaneously** (two foundries, 27–60°C, different PSUs), fitness =
worst-of-four → robust circuits that held on six never-seen chips down
to −50°C. "Even within robust digital design, unconstrained evolution
can produce circuits beyond the scope of conventional design rules."
**The design principle for S9's loop: the portability envelope must live
inside the fitness function — whatever conditions the fitness signal
does not vary, the search will quietly sell to buy performance.** (This
is rung-0's per-input-specialization bound meeting deployment reality:
our accelerators must be scored across inputs/temperatures/conditions or
the LLM overfits exactly as the GA did. Bird & Layzell's Evolved Radio,
CEC 2002, is the comic version: circuits that used the oscilloscope as a
component and died when a soldering iron was unplugged.)

**The field's arc, verified:** ICES conference dead after 2014; Haddow &
Tyrrell's 2011 post-mortem — EHW stuck at toy problems, "publishing
driven," industry "fed up" — reads as a collective-action diagnosis. The
intrinsic on-real-silicon line stalled entirely; its modern echo is
physics-aware training (Wright et al., Nature 2022 — gradients instead
of a GA). Matthew's framing stands: extreme nonstandard effort, great
result — and the two roles hold: mode-3's deepest ancestor, and the
abstraction-breaking cautionary tale, now with Thompson's own worst-of-N
fitness as the documented remedy. Bonus quote for the societal thread
(Harvey, in Davidson): "How acceptable is a safety-critical component...
if it has been artificially evolved and nobody knows how it works?"

## 6. Baseline discipline (non-negotiable; where prior work is weakest)

- **NEON-enabled (-O3 -mfpu=neon), dual-core baselines, always.** NEON
  alone gives 4–8× on simple DSP code (XAPP1206): an unvectorized baseline
  inflates FPGA claims by that factor. The literature's loosely-baselined
  8–15× collapses to **2.1–5.3×** against the one rigorously autotuned
  baseline (VTA, IEEE Micro 2019) — expect and report VTA-class numbers.
- **The A9 is weak and we say so:** ~1,667 DMIPS/core; one modern desktop
  core is ~30–40× a 667 MHz A9 single-thread. A 10× on-board win can still
  be an absolute loss to a laptop. Frame results as energy per op, latency,
  and the closed-loop autonomy methodology — never absolute throughput, and
  never implying 1:1 transfer to modern CPUs.
- **Contamination guard:** toy RTL benchmarks are saturated (94–100%
  agentic on VerilogEval-v2) and contaminated (VeriContaminated,
  arXiv:2503.13572), while realistic granularity collapses (≤34% on CVDP;
  0% system-level on RealBench). S9 measures on **novel workloads the flow
  selects itself**, never benchmark kernels as headline results; tier-1
  kernels are calibration only.
- Sim-vs-hardware gap: simulation pass rates overstate hardware readiness
  by ~7.5 pts (arXiv:2603.11287) — on-board validation is the only bar that
  counts here.

**Stance on the published LLM failure modes (Matthew, 2026-08-05):** they
are targets, not blockers — "don't worry about the existing LLM failures
stopping us from doing anything. We will try to address those." Working
hypotheses: (a) much of the published failure record was measured on small
or non-frontier models — frontier Claude-class agents with proper tooling
should do better (the IBM Agent Factories result — off-the-shelf Claude
Code agents, mean 7.07× on HLS kernels vs unoptimized baselines — is the
early capability evidence, with the baseline caveat noted in §3);
(b) orchestration matters: integrating the project-manager tool
(`~/claude-work/project-manager`, github.com/mjtomei/project_manager) is a
candidate for structuring the long-horizon loops where single-context
agents break (CVDP/RealBench-class failures). **Addressing these capability
gaps is the first work item of the study, not a risk to route around.**

## 7. Measurements

- **LOOP COST — logged automatically, not studied (scoped 2026-08-07).**
  Per accepted optimization: wall-clock, agent cost, human interventions
  (with cause), build/measure iterations. Emitted by the harness into the
  execution store as a side effect; no control arm and no human-cost
  counterfactual — the study is not powered for that and the time goes into
  results. Report descriptively if the numbers turn out to say something.
- **The open-vs-commercial QoR gap, reported both ways (Matthew,
  2026-08-07).** The reviewers' catch — a weaker open flow leaves headroom
  the agent then claims — is real, and it is also a *result we want*, because
  closing that gap with intelligence instead of license fees is NRE
  reduction, which is the §0 outcome-3 lever and the paper's §5.2 argument
  ("ML breaches EDA") measured by our own loop. So report the pair, never
  one alone: (a) **agent-on-open-flow vs open-flow-alone** = the agent's
  value inside a free stack; (b) **agent-on-open-flow vs commercial-flow
  QoR** = how much of the paid tool's advantage intelligence recovers. The
  headline speedup number stays anchored to the commercial reference so we
  never sell weak-baseline headroom as acceleration; the gap-closing number
  is reported alongside as the NRE-relevant finding.
- End-to-end wall-clock and energy (IMON + bench meter), naive vs
  autonomous-flow, per workload; NEON dual-core baseline alongside.
- **Zero-NRE counterfactual (§0 outcome 3):** for each accepted design,
  what would the same artifact be worth if design cost were zero — i.e.
  extrapolate from measured per-design loop cost to the break-even design
  volume, and state which optimizations become rational at NRE→0 that are
  irrational today. Pairs with the parked rung-0 ideal-ASIC bound (S8 plan
  §3 Phase B) as the physics-side twin of the same question.
- **Core-optimization arm (§0 outcome 2):** for soft-core changes —
  custom instructions, microarchitecture retunes, ISA extensions — measure
  benefit across the *whole* workload mix rather than one kernel, plus
  LUT/Fmax cost; comparators ISAMORE, LACE, Icicle.
- **Autonomy accounting as a primary result:** every human intervention
  logged with cause; time-to-first-working-accelerator; tool-error-recovery
  rate; timing-closure success rate (no published capability measurement
  exists — ours may be the first).
- Selection quality: profitability model hit rate — accelerations that won
  vs lost after interface costs, against the Accelerometer-style model's
  predictions; coverage (fraction of program cycles moved).
- Mode-3 trajectory: QoR vs optimizer generation — the measured
  commons-maturity axis (same role as the parked plan's T̂_g curve).
- Mode comparison: tool-driving vs hand-design vs self-improved loop on the
  same kernels; plus published hand-tuned Zynq-7020 results as the human
  ceiling where they exist.

## 8. Bring-up path (week-1 shape)

**Track 0 — profiling, running now (Matthew, 2026-08-05: start in parallel,
target applications ASAP).** `analysis/s9/profiling/` — harness live on the
GB10: py-spy (installed, working) for Python workloads, gprof for
compiled-from-source, coarse timing anchors done on real repo data
(`bench_kernels.sh`: gzip -9 ~21 MB/s, xz ~3 MB/s, zstd -19 ~18 MB/s
single-thread; sha256 ~2.3 GB/s — the host ISA already absorbed it, while
the A9 predates the crypto extensions: a natural above/below-threshold
experiment on our own two processors). `candidates.csv` is the living
ranked list. **Blocked on root:** `kernel.perf_event_paranoid=4` — perf
(needed to profile arbitrary binaries without rebuild, i.e. tier-2
discovery) unlocks with `sudo sysctl kernel.perf_event_paranoid=1`.
Host-stage caveat: GB10 shares are structure-portable, not A9-calibrated;
final ranking re-runs on the board.

**Track 0 upgrade — the observer as its own instrument (Matthew,
2026-08-05):** per-binary profiling tools "won't be sufficient. We need
something lower level and more complete, like a VM that an LLM has access
to and is actively monitoring — a new kind of profiling tool that is more
intelligent and grounded." So the profiling track's endpoint is not a
perf wrapper but an **intelligent, grounded whole-system observer**: an
observation substrate with VM-grade completeness (everything running, not
just binaries we chose; instruction/memory-level visibility on demand)
that an LLM actively drives — deciding what to watch, zooming from
system-wide shares to instruction traces, mapping observations back to
program semantics, and maintaining the candidate list continuously. This
is a third novel artifact of the study, alongside the closed loop and the
self-improvement arm.

**Observer prior-art verdict (sweep completed 2026-08-05, three
verification passes):** every layer exists separately, none exist
together. Exists: always-on whole-host stack sampling at ~1% (Parca/
Elastic/OTel eBPF line — stacks only); complete control-flow capture at
single-digit overhead (Intel PT — and **PTM on the Zynq-7000 itself**);
whole-system deterministic record/replay with unlimited replay-time
instrumentation (PANDA, PPREW 2015); the samples→action loop with a
compiler as actuator (AutoFDO/BOLT/Propeller); counterfactual profiling
(COZ, SOSP 2015 — the observer's epistemology: measure what would help,
not where time goes); TMA (Yasin, ISPASS 2014) as the accounting language;
LLMs that synthesize small verified probes (Kgent, 80% semantic
correctness), read fleet profiles and land production optimizations
offline (**Google ECO, OSDI 2026 — the closest neighbor: >6,400 commits,
~99.5% production success, and precisely what S9 differs from: offline,
source-level, decoupled from observation**), and use a simulator as their
performance oracle (**PIE, ICLR 2024 — gem5 as the LLM's deterministic
oracle: the observable-twin precedent**). **Unbuilt, three passes
confirming:** an LLM that continuously holds low-level observation of an
entire running machine, maintains a model of what it is doing, and closes
the loop by choosing what to optimize or offload. Also unbuilt at tooling
level: a queryable whole-execution database and first-class diffing of two
runs — the primitives an LLM observer thinks with; concrete build items.

**Observation stack (three tiers, each used only for what it can answer):**
1. *Host observable twin* — QEMU-system-arm with icount+record/replay;
   TCG plugins (per-instruction/per-memory-access) as the LLM's
   instrumentation verbs; PANDA-style record-once-replay-many, each replay
   instrumented per the LLM's last hypothesis (COZ epistemology over a
   deterministic substrate); replays reduced into a queryable store
   (per-symbol counts, call graphs, BBV/SimPoint phase boundaries,
   syscall/process timeline) so the LLM queries structure, not logs.
2. *Timing model* — gem5 ARM (MinorCPU, A9-like) on SimPoint phases of
   candidate regions only: ranks by cycles, ordinally (tens-of-% error).
3. *Target ground truth (Zybo)* — perf on the A9 PMU (6 counters + cycle,
   multiplexed TMA-lite); **PTM→4KB-ETB snapshots via perf cs_etm/OpenCSD
   (all mainline — the dtsi already wires it)**; and the S9-native option:
   **TPIU trace exported through EMIO into the PL — the FPGA fabric
   capturing its own host CPU's instruction stream.** Decisions are
   proposed on the twin, accepted only on target wall-clock + PMU deltas.

**Distortions, stated:** twin hotness is instruction-count hotness (QEMU
models no caches/branch predictors — its docs say so; emulated NEON
overweighted; virtual I/O timing → twin concurrency is *a* legal schedule,
not the target's); gem5-A9 is ordinal only; target grounding itself is
weak (6 multiplexed counters with skid, 4KB trace windows). Not available
on the A9: rr (no ARM32), SPE/PEBS-class precise memory sampling — memory
visibility comes from the twin or PL-side AXI monitors.

1. Confirm variant; flash PYNQ 3.0.1 community image; verify PMU dtb node;
   `perf stat` smoke test on the A9.
2. Vivado 2026.1 under FEX-Emu on the GB10, batch/Tcl: synth a stock Zybo
   base design end-to-end. If flaky → x86 fallback over SSH. In parallel:
   openXC7 0.9.x Nix install, ps7-blinky-class demo.
3. First accelerator smoke test: XAPP1170-class HLS matmul, AXI_HP data +
   GP CSRs, driven from PYNQ Python — exercises the whole loop: profile →
   HLS → bitstream → overlay load → verify → time → read IMON power.
4. Add one DFX reconfigurable pblock (clock-region-aligned) + PCAP partial
   delivery — kernel swap without reboot.
5. Then the harness: profile → candidate ranking (Accelerometer-style
   model) → LLM HLS/RTL generation → build → deploy → measure, autonomous,
   interventions logged. Tier-1 control kernel first; tier-2 selection run
   on a real program after.

## 9. Risks, ranked

1. **Vivado-under-FEX fragility** — weeks-old support; an autonomous loop
   amplifies nondeterministic crashes. Mitigation: pre-provisioned x86
   fallback over SSH; batch mode avoids the GUI shim pain.
2. **Baseline honesty** — NEON 4–8× and A9-vs-modern 30–40× are the two
   numbers reviewers will check first; committed to in §6.
3. **openXC7 instability if made load-bearing** — timing support is weeks
   old, DSP timing conservative; fine as parallel native track with margin,
   never the only flow.
4. **Neighbor velocity** — HLSPilot/ContractHIL-class work is moving fast
   (three closest works are 2026 preprints); the empty niche (profiling-
   driven selection + on-board + self-improvement) is ours only if we move.

## 10. Open decisions (Matthew's)

1. ~~Zybo variant~~ — Z7-20 per Matthew (confirm marking at bring-up).
2. Track A host arrangement if FEX fails week-1: buy/repurpose an x86 box
   vs spot cloud instance.
3. Tier-2 program slate: which 3–5 real applications the flow gets pointed
   at first.
4. Mode-3 scope for the first paper: prompt/script self-improvement only,
   or full heuristic evolution with QoR fitness.
5. Where results land: paper §5.2/§6 + Appendix A revision, and/or the
   Cosmic AC outline.
6. Observer substrate: how far toward the full observable-twin (QEMU
   whole-system) the first paper goes vs system-wide perf/eBPF on host +
   target; and whether project-manager-tool integration is in scope for
   the first harness or a follow-on.

## 11. Must-reads (deduped across the four reports)

1. Lysecky, Stitt & Vahid, "Warp Processors," ACM TODAES 11(3), 2006 — the
   complete original loop (beware the phantom DAC-2004 Crossref record).
2. Vahid, Stitt & Lysecky, IEEE Computer 41(7), 2008 — every honest
   limitation, quotable.
3. Paulino et al., ACM Computing Surveys 53(1):6, 2020 — the descendant-
   field map.
4. Sriraman & Dhanotia, "Accelerometer," ASPLOS 2020 — the profitability
   model to embed + second-fleet tax evidence.
5. Kanev et al., ISCA 2015 — the tax and the flatness in one paper.
6. Gonzalez et al., ISCA 2023 — "sea of accelerators," Google's own words.
7. HLSPilot, ICCAD 2024 — nearest neighbor, the differentiation target.
8. ContractHIL-HLS, arXiv:2607.25283 — nearest hardware-in-the-loop
   neighbor (PYNQ), preprint.
9. CVDP (arXiv:2506.14074) + VeriContaminated (arXiv:2503.13572) — the
   honest difficulty gauge and the contamination guard.
10. AlphaEvolve (arXiv:2506.13131) + Dr. RTL (arXiv:2604.14989) +
    Self-Evolved ABC (arXiv:2604.15082) — the mode-3 precedents and their
    exact (modest) scopes.
11. For the observer: GWP (IEEE Micro 2010) + PANDA (PPREW 2015) + COZ
    (SOSP 2015) + PIE (ICLR 2024) + ECO (arXiv:2503.15669, OSDI 2026) —
    continuous observation is cheap / record-once-replay-many / the
    counterfactual epistemology / the simulator-as-LLM-oracle precedent /
    the deployed offline neighbor S9 goes beyond.
12. For the stack: Karandikar et al. (FirePerf), ASPLOS 2020 +
    Gottschall et al. (TIP), MICRO 2021 — the soft-core-visibility
    profiling state of the art to cite before claiming anything; Nane et
    al., IEEE TCAD 2016 — the open-vs-commercial HLS QoR numbers;
    Ferrandi et al. (Bambu), DAC 2021 — the chosen tool; Canis et al.
    (LegUp), FPGA 2011 + Aldham's profiler — the 2011 ancestor of
    profiler-driven partitioning on a soft core.

## 12. Corrections recorded during verification (do not re-propagate)

- Datacenter tax: **22–27%** (body), not "~30%"; allocation has no stated %;
  kernel cycles excluded. Accelerometer headline: "as few as 18% in core
  logic," not ~31%; it's Facebook/Meta, not Google.
- Catapult: 95% throughput at ≤10% power / ≤30% TCO; **29% is the
  tail-latency alternative**, not TCO. ProtoAcc honest number: 3.8× vs Xeon.
- Warp: on-chip CAD peak memory **3.6 MB** (not ~10 MB); Binary Synthesis
  survey is TODAES 2007 (not TECS 2011); DATE 2005 soft-core numbers
  (5.8×/57%) confirmed exactly.
- NEEDLE first author is **Kumar** (not Sharifian); AccelSeeker is **ICCD**
  2019 (not ICCAD); DynaSpAM is Liu/August, Princeton, ISCA 2015;
  "RegionSeeker" exists (TCAD 2019) but "Regional out of context" does not;
  SPARTA/PRIME/COREx as remembered do not exist.
- AES-NI ~8× figure is Wikipedia-flagged — use "order-of-magnitude class"
  or fetch Intel's white paper before citing.
- Intel QAT/IAA official gain figures: unverified this pass.
