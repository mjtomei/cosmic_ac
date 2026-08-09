# S8 — Dataflow-multicore in gem5: session plan

> **STATUS: SUPERSEDED as the active plan (2026-08-05, Matthew's call).**
> The program pivoted FPGA-first — see `plans/S9-fpga-continuous-acceleration.md`.
> Reframing: the dataflow-multicore and FPGA studies are the *same study* —
> two possible target architectures for one continuously-optimizing
> intelligence; the FPGA target goes first because mature tooling absorbs
> placement/scheduling and a board (Zybo Z7) is in hand. The gem5 arm is
> parked. The rung-0 ideal-ASIC limit (§3 Phase B) is parked as promising but
> not yet well defined ("the optimal is not well defined yet although I think
> there is something there" — Matthew). The related-works ledger (§2) and the
> matmul movement back-of-envelope (`analysis/s8/matmul_movement_boe.py`)
> remain the shared citation and physics base for both targets. Do not
> execute from this file.

*Created 2026-08-05 from a six-agent related-works pass (all citations below
web-verified that day unless flagged). Self-contained: a fresh session can
execute from this file. Companion register entry: `studies-and-work-log.md` §S8.*

**Question:** how much of the realization gap is recoverable by automatic
dataflow mapping of ordinary code?

**What it replaces in the paper:** §1.2's central inference — "the effort gap
is concentrated exactly on the reconfigurable substrates... it can only be
larger in the middle" — is bracketing plus monotonicity, not measurement; the
paper concedes "no published study pins the achieved-versus-achievable gap on
an FPGA or CGRA." Figure 6's CPU↔CGRA boundary (`build/fig4_phase.py`, file
figure-4.png = F6; captions authoritative, not filenames) is a hand-placed
straight line from (6.4, 2.7) to (3.2, 10) on commons-maturity × diversity
axes, self-flagged "conceptual." S8 supplies the middle's first measured
points. NOTE an unstated methodological step: S8 measures on *mapping-quality ×
workload* axes; converting to Figure 6's *commons-maturity × diversity* axes is
a design decision, not a given (see Open decisions).

---

## 1. Positioning: what is known, what S8 can own

The six-way survey converged on one clean statement. Every *piece* of S8's
mechanism exists in isolation with published gains:

- **Automatic task extraction** — TaskMiner (Ramos et al., PACT 2018) inserts
  OpenMP task pragmas into un-annotated structured C, matching manual
  annotations; static-only, no NUMA mapping. T4 (Ying, Jeffrey & Sanchez, ISCA
  2020, code open) compiles ordinary sequential code onto Swarm's speculative
  task hardware — the closest existing artifact to S8's automatic-mapping claim.
- **Placement alone, zero code change** — Carrefour (Dashti et al., ASPLOS
  2013): up to 3.6× on contention-heavy apps, typically tens of percent;
  key recalibration: *congestion* on controllers/interconnect dominates, pure
  remote-latency costs at most ~20–30%. AsymSched (ATC 2015), AutoNUMA.
- **Locality-aware scheduling within a task runtime** — ADWS (Shiina & Taura,
  SC 2019): up to ~6× over plain work stealing on memory-bound task code;
  theory says plain stealing is locality-pathological (Acar-Blelloch-Blumofe,
  SPAA 2000).
- **The naive-to-expert gap** — ninja gap (Satish et al., ISCA 2012): 24×
  average / 53× max; compilers+pragmas close it to ~3×; closing to 1.3× took
  *human algorithmic restructuring*. Suite is regular kernels, pre-NUMA.
- **Task-dataflow runtimes** — StarPU/Legion/PaRSEC/OmpSs match hand-tuned
  libraries, but only on *hand-taskified* programs, overwhelmingly dense LA.
  Legion's own paper shows the win rides on programmer regions + custom mappers.

**What no published work does:** (a) measure the *composite* end-to-end
unrealized gap of ordinary application code on a modern NUMA multicore —
structure + granularity + placement together, against a defensible available-
parallelism bound; (b) go from unannotated ordinary code to a NUMA-mapped
task/dataflow graph with *no human in the loop*. Gupta & Sohi (MICRO 2011) is
the closest mechanism (dataflow execution of statically-sequential C++ — but
requires rewriting into their library idiom); TaskStream (Dadu & Nowatzki,
ASPLOS 2022) is the closest architecture (tasks on a reconfigurable dataflow
fabric — but pragma'd C, not extraction). Position explicitly against both.

**Framing rule (matches CLAUDE.md "build on published work; do not argue
novelty"):** S8 is a *quantification claim plus a composition claim* — the
pieces exist, each credited; what is unmeasured is the size of the end-to-end
gap on ordinary code and whether the composition closes it automatically.
State the absence once, quietly.

---

## 2. Related works by pillar (verified anchors)

### 2.1 Available-parallelism measurement (the "gap" instrument)

The oracle tradition: Riseman & Foster 1972 (control flow is the wall), Nicolau
& Fisher 1984 (~90× oracle on scientific Fortran), **Wall ASPLOS 1991 / WRL
93/6** ("even with impossibly good techniques, average parallelism rarely
exceeds 7" — the honest-idealization-sweep template: >100 model combinations,
report medians), **Lam & Wilson ISCA 1992** (the constraint lattice; the
S8-critical numbers: BASE 2.14 → CD-MF 6.96 — *the dataflow-machine
no-speculation limit* — → SP-CD-MF 39.62 → ORACLE 158.26, harmonic means,
non-numeric codes; data-dependent control flow, not source language, predicts
parallelism), **Austin & Sohi ISCA 1992** (dynamic dependency graph from a
serial trace — essentially S8's instrument; parallelism is *bursty*), Theobald
et al. MICRO 1992 (smoothability), Rauchwerger et al. MICRO 1993 (fragility to
resource constraints), Postiff et al. 1999 (stack-pointer linkage dependence:
some measured serialization is *toolchain convention, not semantics* — directly
load-bearing for the commons thesis).

The modern tool line (UCSD): Parkour (HotPar 2011) → **Kremlin (PLDI 2011)**
(hierarchical critical path analysis + self-parallelism; plans matched
third-party manual parallelizations within 3.8% avg) → **Kismet (OOPSLA
2011)** — *the closest existing S8-style measurement*: unmodified serial code,
HCPA + hardware/expressibility constraints → speedup upper bound; on low-
parallelism SpecInt the bounds plateau at 2–4× and published heroic
parallelizations all sit beneath them. Flat CPA without expressibility and
overhead terms wildly overestimates — S8 must constrain its bound by what the
dataflow fabric can exploit. Also: Cilkview/Cilkscale (work-span + burdened
span — the metric to report for the *remapped* version), TaskProf (FSE 2017),
COZ (SOSP 2015 — causal, non-oracle cross-check), DiscoPoP (IPDPS 2015 —
maintained dependence profiler), Prospector (HotPar 2010), Alchemist (CGO 2009
— dependence *distance*, a granularity signal), Intel Advisor (industrial
embodiment).

The achieved side, consumer workloads: Flautner et al. ASPLOS 2000 → Blake et
al. ISCA 2010 (desktop TLP ~2 a decade into multicore) → Feng et al. ISPASS
2019 (18-year update; no TLP improvement in low-core apps). Kulkarni et al.
PPoPP 2009 (irregular apps: parallelism is profile-shaped and invisible to
loop-dependence analysis — report profiles over time, not scalars). **Eyerman
et al. ISPASS 2012 "Speedup Stacks"** — the accounting form S8's gap
attribution should take.

NUMA locality measurement: Carrefour (above), **MemProf (ATC 2012)** —
unmodified FaceRec did 63% of accesses remotely, fixed to 2.2% with <10 lines:
the existence proof that large locality losses sit in ordinary code and are
mechanically recoverable; NumaMMA (ICPP 2018) — the maintained open tool.

### 2.2 The automatic-parallelization prior (why "automatic" failed; what moved)

Static era ceiling: Polaris (Eigenmann-Hoeflinger-Padua TPDS 1998 — success on
~6/13 Perfect benchmarks, i.e. ~50% of *Fortran science codes*), SUIF (Hall et
al. IEEE Computer 1996 — 3/4 of NAS+SPECfp95), HPF post-mortem (Kennedy-
Koelbel-Zima HOPL 2007 — failure partly ecosystem/economics: congenial to the
commons framing). Polyhedral: Pluto PLDI 2008; complete theory, tiny domain
(affine SCoPs; SPECint essentially out of scope). Thread extraction on
SPEC-class C: DSWP (MICRO 2005 — "decades of compiler research have not
succeeded in delivering automatic threading for prevalent code properties"),
PS-DSWP (CGO 2008, 114% avg on selected loops), **HELIX (CGO 2012, 2.25× avg
on 6 real cores across 13 SPEC C codes — still the best all-software number on
real hardware)**; HELIX-RC needed co-designed silicon for 6.85×. Speculation:
POSH (PPoPP 2006, 1.30× simulated, a quarter of it prefetching), STAMPede,
LRPD.

The limit-and-loophole pair (read together): Kejariwal et al. ICS 2006 —
speculation beyond true TLP bounded at ~39%/18% (arith/geo) on SPEC2000,
<1% conservative on SPEC2006; **Packirisamy et al. ISPASS 2009** — but
tolerating dependences occurring in <20% of iterations unlocks loops covering
**96% of execution** (473.astar): the latent parallelism sits behind
*probabilistic, not provable* dependences. This is the cleanest quantitative
statement of S8's dynamic-information argument. Dependence profiling is
feasible at whole-SPEC scale: SD3 (MICRO 2010).

What ML moved, precisely (three barriers, moved differently):
1. **Legality: NOT moved by ML** — every credible system outsources
   correctness: Alive2 formal check (LLM-Vectorizer, Taneja et al. CGO 2025 —
   1.1–9.4× over ICC/GCC/Clang on scalar C, *the propose-then-verify template
   S8 should adopt*), compile-and-run (OMPar 2024), runtime speculation
   (LRPD/TLS line). Eigenmann's own LLM-vs-Cetus study (arXiv:2406.12146, SCA
   2025) locates the binding constraint at verification.
2. **Profitability: strongly moved** — Halide autoscheduler (SIGGRAPH 2019,
   first ML-beats-experts in scheduling), Ansor (OSDI 2020), MLGO (deployed in
   LLVM), Meta LLM Compiler (77% of autotuning benefit without executing).
3. **Restructuring search: partially moved, oracle-gated** — AlphaDev (Nature
   2023), AlphaEvolve (23% Gemini-kernel — already cited in the paper);
   algorithmic rewrites appear only where an automatic fitness/correctness
   oracle exists. For ordinary code with no oracle, open — this is S8's crux,
   and gem5 itself supplies the oracle (correctness by identical output,
   fitness by simulated cycles).
   Framing gift: Hall-Padua-Pingali CACM 2009 called for "compilers capable of
   self-improvement" 16 years early.

### 2.3 Dataflow / task-support architectures (what to model)

Classical arc (context, keep tight): Dennis & Misunas 1974, TTDA 1990, Monsoon
ISCA 1990; the critique that matters — **Culler, Schauser & von Eicken 1993,
"Two Fundamental Limits on Dataflow Multiprocessing"**: token/frame traffic
destroys locality; greedy local scheduling is inadequate. These are exactly the
failure modes S8's NUMA experiment measures against; the bridge from dataflow
to task-based execution. TRIPS (eval: ASPLOS 2009 — compiled code loses to a
Core 2, hand-optimized beats it ~3×: the compiled-vs-hand gap is itself a
realization-gap-under-automatic-mapping measurement, the closest prior in
spirit and the cautionary baseline). WaveScalar (MICRO 2003 / TOCS 2007 —
sober version: single-thread parity with OOO at ~70% area; wave-ordered memory
is the run-ordinary-C mechanism S8 needs an answer to). Companion report
already carries TRIPS/WaveScalar/SEED/Swarm — extend its ledger, don't re-cite
from scratch.

Task-execution support on multicore: Carbon (ISCA 2007, HW task queues; NB its
headline % couldn't be re-verified — paywalled; effect corroborated via ADM's
reimplementation), **ADM (Sanchez, Yoo & Kozyrakis, ASPLOS 2010** — note Yoo
not Yen, ASPLOS not HPCA) — register-to-register messages + software
scheduling matches/beats hardware queues by up to 70%; *evaluated in M5+GEMS,
gem5's direct ancestor* — proof this experiment class runs in the gem5 lineage,
and the cheapest credible S8 architecture variant. Task Superscalar (MICRO
2010). **Swarm (Jeffrey et al., MICRO 2015** — 43–117× over tuned serial on
ordered-irregular at 64 cores; custom Pin-based sim, *not* gem5; the
irregular-parallelism ceiling and the **baseline gold standard: tuned serial
AND best software-parallel on identical modeled hardware**) + Espresso (MICRO
2018 — non-speculative task mode is a legitimate efficient subset: S8's pilot
can stay non-speculative), Chronos (ASPLOS 2020), Hive (ISCA 2022), Fifer
(MICRO 2021 — irregular apps as decoupled pipelines on a CGRA).

Spatial with automatic compilation — the compilation-automation spectrum:
DySER (HPCA 2011; *evaluated in gem5 extended with DySER*, PACT 2013) and SEED
(ISCA 2015 — region taxonomy: dataflow wins some region classes, loses where
control speculation dominates; advantage shrinks as the host core grows) =
ordinary C, fully automatic; DSAGEN/dsa-framework (ISCA 2020) = C+pragmas;
SGMF (ISCA 2014) = CUDA; Fifer = manual decomposition; Plasticine (ISCA 2017)
= DSL. S8's claim lives at the left end; T4 and DySER prove that end is real.
Locality mechanisms: DeSC (MICRO 2015, automatic access/execute slicing),
Stash (ISCA 2015, scratchpad-vs-cache numbers), Lee-Kim-Vuduc TACO 2012
(prefetching fragile exactly on irregular patterns — defines where the
baseline should already win, i.e. S8's control).

### 2.4 gem5 methodology (capability facts, 2026-08 current)

- **NUMA: feasible, roll-your-own.** No turnkey config; pieces exist — CHI/Ruby
  address-range→home-node mapping (v22+), Garnet/HeteroGarnet per-link latency
  topologies, Arm auto-DTB exposes nodes to Linux. Template with open code:
  **CXL-DMSim (Wang et al., IEEE TCAD 2025, arXiv:2411.02282)** — far memory as
  a Linux NUMA node, silicon-validated, 3.4% avg error.
- **FS mode is non-negotiable**: SE mode has no OS page placement / first-touch
  / scheduler migration — NUMA behavior there is synthetic. Arm FS is the most
  mature target (Neoverse-V2 config in v25.1; prebuilt Ubuntu images).
- **Host:** the GB10 (aarch64, 20 cores, 119 GB) is the *right* machine —
  Arm-target KVM fast-forward requires an aarch64 host. Verify `/dev/kvm` on
  DGX OS before committing; fallback Atomic fast-forward. Native compilation of
  simulated aarch64 workloads; no cross-compiling.
- **Cost:** O3+Ruby ~100–200 KIPS, single-threaded event loop → ROI sampling
  from day one: KVM boot → checkpoint (known KVM→O3 restore bugs on Arm FS —
  stage via Atomic; gem5 issues #1505/#932) → 10–100M-instruction detailed
  windows; LoopPoint methodology (Sabu et al., HPCA 2022) for multithreaded
  regions; farm configurations as independent gem5 processes across host cores.
- **Credibility:** report *relative* deltas, same memory system both arms;
  calibrate the memory model (Mess, MICRO 2024 — gem5's default memory curves
  ~30% off, Mess integration →~3%); cite Arm validation lineage
  (Butko 2012 ~6% avg; Akram & Sawalha for x86 caveats); anticipate the
  Nowatzki WDDD "sim-harmful" critique — never present an uncalibrated config
  as a real machine. Sniper as optional cross-check. Alternatives (Sniper/
  ZSim/SST) don't do OS-visible NUMA + custom execution models; gem5 is the
  only credible tool here.
- **Dataflow modeling, ranked by effort:** (1) **trace-driven limit study** —
  gem5 elastic traces (Jagtap et al., ISPASS 2016) record data-dependency-
  annotated instruction streams = the dataflow graph; replay under a custom
  topology-aware dataflow scheduler against the same Ruby memory system;
  accepted "limit-study" genre, and gives achieved-vs-available for free.
  (2) ADM-style messaging/task-queue extensions + DySER/dsa-framework-style
  per-tile fabric (PolyArch dsa-framework: gem5-integrated spatial sim + LLVM
  compiler, MICRO 2022 tutorial; gem5-SALAM merging into mainline per gem5.org
  July 2025; ASU CCF as CGRA-as-core template). (3) Full custom dataflow CPU
  model — documented heavy lift (UW TR1820); avoid for the first study.
  No open gem5 EDGE/TRIPS model exists.

### 2.5 Energy-costed ideal-hardware bounds (added and web-verified 2026-08-05)

The pillar behind §3 Phase B. All anchors below verified from primary PDFs.

*Instrument ancestors:* **Aladdin** (Shao, Reagen, Wei & Brooks, ISCA 2014 —
C → dynamic trace → idealized DDDG ("optimistic enough for ILP limit
studies", their words) → constrained realization + power models; 0.9%/4.9%/
6.6% perf/power/area error vs RTL; **verified to model no spatial placement
or wire distance whatsoever** — lumped per-FU energies only) and gem5-Aladdin
(MICRO 2016 — SoC coupling shifts optimal designs up to 7.4× EDP).
**Timeloop** (Parashar et al., ISPASS 2019 — energy-costed mapping-space
search; near-peak mappings vary ~19× in energy; domain provably restricted to
dense affine loop nests with reorderable bodies) + **Accelergy** (Wu, Emer &
Sze, ICCAD 2019 — plug-in energy tables, the architecture to copy for our
tables) + MAESTRO (MICRO 2019). **TDG** (Nowatzki & Sankaralingam, ASPLOS
2016 — dependence-graph transformations modeling DySER/SEED/BERET-class
designs on general-purpose code, <15% avg error; computes no unconstrained
ideal; inter-FU latency "estimated," their Limitations).

*Analytical bound family (the floor to sandwich against):* Choi, Bedard,
Fowler & Vuduc, "A Roofline Model of Energy," IPDPS 2013 (E = W·ε_flop +
Q·ε_mem + π0·T; fitted pJ coefficients); Woo & Lee, IEEE Computer Dec 2008
(power-constrained Amdahl); Demmel, Gearhart, Lipshitz & Schwartz, IPDPS 2013
(communication lower bounds → energy lower bounds); Hong-Kung pebble games /
IOLB (automated movement lower bounds, affine only). Algebra, no schedule, no
placement — Phase B's constructive bound sits between this floor and real
machines.

*Energy constants (cite each to its own node, never mix):* Horowitz ISSCC
2014, 45nm — 32b int add 0.1 pJ, 32b FP mult 3.7 pJ, 64b SRAM word 10 pJ
(8KB) → 100 pJ (1MB), DRAM 1.3–2.6 nJ, ~70 pJ/instr overhead. Keckler,
Dally et al., IEEE Micro 2011, 40nm→10nm — **wire 240 → 115 fJ/bit/mm**;
256 bits over 10mm ≈ 310 pJ ≈ 6× a 64b DFMA. Dally, Turakhia & Han, CACM
2020, 14nm — **on-chip wire 100 fJ/bit-mm**, 8KB SRAM 50 fJ/bit, LPDDR4
~4 pJ/bit; instruction interpretation 10–4000× a simple op. Storage vs
capacity: CACTI 7 (Balasubramonian et al., ACM TACO 2017) — NB effectively
frozen (tech files 90–32nm, last substantive commit 2017): extrapolate or use
Accelergy-style plug-in tables, and say which.

*Optimizer machinery:* SDC scheduling (Cong & Zhang, DAC 2006 — totally
unimodular LP, optimal in polynomial time; the basis of Vitis/LegUp/XLS —
the formalism to relax: drop area, add power-budget and wire-latency terms);
HLS DSE survey (Schafer & Wang, IEEE TCAD 2020). ML leg, all published:
AutoDMP (Agnesina et al., ISPD 2023 — DREAMPlace + Bayesian opt, open
source), MapZero (ISCA 2023, already in the paper), FunSearch (Nature 2023),
AlphaEvolve (2025, self-reported), EoH (Liu et al., ICML 2024 oral) / ReEvo
(NeurIPS 2024) — LLM-evolved heuristics, with the generalization caveat
(arXiv:2501.11411); and the self-improving-loop existence proof: **AuDoPEDA**
(Ghose, Jang, Kahng & Lee, arXiv:2601.06268, 2026 — LLM agents editing
OpenROAD's own source with flow PPA as fitness, up to 19.4% power; the
paper's §5.2 already cites this line). Context: Sankaralingam, "Computer
Architecture's AlphaZero Moment" (arXiv:2604.03312, 2026) *proposes* the
automated architecture-discovery loop, computes no bound. AlphaChip remains
contested — cite via Cheng/Kahng ISPD 2023 only (standing rule).

*Novelty verdict (state once, quietly, per convention):* no prior study
computes an unlimited-area, power-budgeted, **distance-costed** ideal-ASIC
bound for general-purpose programs. Closest three, each short one piece: TDG
(right input, bounds specific designs, no placement); Timeloop/Accelergy
(right output shape, affine/DNN-only, lumped interconnect); the analytical
family (bound-shaped, no schedule/placement). Wall 1991 / Austin-Sohi 1992 do
unlimited resources with zero energy accounting; Fuchs-Wentzlaff bounds
CMOS, not programs; Chainsaw (MICRO 2016) measures vs an un-energy-costed
ideal dataflow machine. The unprovided term is exactly the one that keeps an
unlimited-area bound from being trivially loose: **wire energy under
optimized placement**. That term is S8's to contribute — with the pieces
above credited as the assembled prior art.

---

## 3. Draft methodology

*(Restructured 2026-08-05 to Matthew's design: ideal-ASIC ceiling → constraint
projection onto the gem5 architecture → gap targeting. One optimizer, several
constraint sets; the earlier trace-replay lattice survives as cross-checks.)*

Three-phase pipeline; each phase publishable-grade on its own. Convention:
every novel number → `analysis/s8/` artifact with sources and assumptions.

### Phase A — achieved, measured (conventional NUMA multicore in gem5)

1. **Platform:** gem5 v25.x, Arm FS, Ubuntu image, Neoverse-V2-calibrated O3
   cores; Ruby CHI + Garnet two-cluster topology (2×8 cores to start),
   per-cluster memory controllers, heterogeneous inter-cluster link latency,
   ranges mapped to home nodes, exposed via DTB as two NUMA nodes. Calibrate
   local/remote ratio (~1.5–2.2×) against published two-socket data; validate
   the latency-bandwidth curve with Mess before any headline number.
2. **Workloads:** "ordinary code" must be defended, not assumed (no standard
   suite exists — survey finding). Candidate mix, ~6–10 programs: serial/naive
   PARSEC variants (streamcluster, canneal, dedup, fluidanimate), 2–3 irregular
   kernels (graph traversal, discrete-event — the Swarm class), 1–2
   LLM-generated "programmer of median effort" implementations of standard
   tasks (novel, on-thesis, but flag selection risk), NPB serial as the
   regular-code control where prefetchers should already win (Lee-Kim-Vuduc).
   Multiple inputs per program; report input sensitivity.
3. **Measurements per workload:**
   - *Achieved:* speedup vs tuned serial at 1–16 cores, naive pthread/OpenMP
     versions, with AutoNUMA on and off (it is the deployed automatic baseline).
   - *Locality:* remote-access fraction per object (MemProf-style attribution)
     AND controller/interconnect congestion share (Carrefour's recalibration —
     congestion, not wire latency, dominates); stall-attribution as a
     **speedup stack** (Eyerman): synchronization / memory interference /
     placement / residual.
   - *Graph capture:* elastic traces (dependency-annotated) from these same
     runs — the input to Phase B. Cheap cross-check rungs of the classic
     lattice (Austin-Sohi dataflow limit; Kismet-style expressibility-
     constrained CPA) computed from the same traces, to sanity-check Phase B's
     graph construction against the published tradition.
4. **Deliverable:** the achieved side + locality accounting; artifact
   `analysis/s8/gap_measurement/` (configs, traces, CSVs).

### Phase B — the ceiling: ideal-ASIC energy-bounded limit (Matthew's
formulation, 2026-08-05)

The instrument replacing abstract "available parallelism" as the top anchor.

1. **Rung 0 — the pure computation bound (the first novel deliverable;
   Matthew, 2026-08-05):** map the graph of operations onto unlimited area —
   purely the computation placement and scheduling problem. **No memory
   model; and no instruction delivery *by construction*, not by assumption**
   (corrected 2026-08-05): with infinite area every operation has its own
   place, so there is nothing to fetch or configure. Per-op energies from a
   published table at a stated node (Horowitz ISSCC 2014 / Dally CACM 2020
   lineage); producer→consumer transfers wire-costed in energy under
   placement (Keckler/Dally pJ/bit/mm); sustained **power budget P** (swept —
   results are curves in P). Semantics: the bound for hardware perfectly
   specialized to the exact app *and input*, run every time — the benefit
   ASICs are trying to extract, stated as a limit. Per-input specialization
   is definitional at this rung, not a caveat; app-level bounds aggregate
   over inputs. Fixed operating point first; voltage/frequency freedom
   (near-threshold, Table 1's row) as a later knob. Two design choices to
   settle (Open decisions): wire distance costs energy only vs energy +
   latency; and **place reuse** — same-op reuse (folding a loop onto one
   unit: a datapath, still instruction-free) permitted as an optimizer choice
   with a one-op-per-place-per-cycle serialization constraint, vs full
   spatialization (no reuse — a valid but looser bound: it overpays wire
   energy, and latency if wires are timed, exactly on loop-carried/serial
   structure). Leading option: permit same-op reuse, run no-reuse as a
   variant — the delta measures how much of the ASIC benefit is
   compactness/feedback locality vs pure spatialization.
2. **Realism rungs (the descent toward buildable):** each rung re-solved by
   the same optimizer, so the rung-by-rung energy build-up is a bound-side,
   measured analogue of Hameed's sources-of-inefficiency decomposition.
   **Two kinds of rung, distinguished (Matthew's all-to-all point,
   2026-08-05):** *constraints* (instruction delivery, finite area, power)
   can only worsen the bound; *resources* (a memory primitive the optimizer
   MAY instantiate) can only improve it, since not using them is always
   allowed. The rungs:
   (i) *storage* — dual role: as realism, values that wait must live
   somewhere (capacity-costed storage, CACTI-class / Accelergy plug-in
   tables, prices dataflow slack); as a **resource**, a RAM is physically a
   compact any-to-any interconnect (decoder + shared bitlines; access energy
   ~√capacity) while all-to-all placed as wires pays bisection-limited energy
   growing with span — so **which workloads pull a memory into their optimal
   mapping, and at what capacity, is a named result target** ("where a RAM
   earns its place"): weights-stationary ML predicts none; dynamic
   gather/scatter, sorting, hashing, graph traversal predict yes. The
   memory-hierarchy-as-evolved-locality-management thread, derived instead of
   assumed. **First numbers** (`analysis/s8/matmul_movement_boe.py`,
   2026-08-05, design-guidance not paper-grade): matmul movement pJ/MAC under
   the plan's constants — folded systolic ~0.7–2.8 (const in n, below the
   4.6 pJ MAC), fully-unrolled-with-tapped-broadcast ~12–182 (∝√n),
   monolithic RAM 80–1280 (∝n, loses everywhere), but **Hong-Kung-blocked
   RAM+8KB-buffer 12–38 — beats unrolled spatialization at large n**: reuse
   through a small cheap buffer outruns reuse-free space. Morals: (a) the
   rung-0 optimizer MUST be allowed same-op folding or the matmul bound is
   loose by √n; (b) RAM-as-interconnect loses on static structured patterns
   to *both* folded spatial and blocked hierarchy — its constants win only
   with blocking (reuse) or dynamic patterns; (c) systolic sits 5–50× below
   the blocked-RAM line, confirming Hong-Kung is not a floor for spatial
   residency; (d) wires and RAMs obey the same √area-per-touch physics — the
   winner is whoever exploits reuse at the shortest distance; (ii) *instruction/configuration delivery* — born exactly
   when a place is shared across *different static ops* (same-op reuse is a
   datapath and stays instruction-free; the rung boundary is a structural
   property of the mapping, not an assumption): add fetch/config energy
   (Horowitz's ~70 pJ/instr
   overhead; Dally's 10–4000×): this rung IS Table 1's ASIC→CGRA→CPU axis
   made continuous; (iii) *memory hierarchy + DRAM boundary* beyond a swept
   on-chip cap; (iv) *finite area / multiplexing* → shades into Phase C's
   architecture constraint sets.
2. **Program model:** the *static* dataflow graph weighted by dynamic
   execution counts, plus memory objects as placeable nodes — a billion-node
   dynamic graph cannot be placed; program phases treated separately
   (burstiness: Austin-Sohi, Kulkarni). Control flow resolved by the trace —
   the ceiling therefore sits on an oracle rung; the probabilistic-dependence
   variant (speculate away dependences occurring in <p% of iterations —
   ISPASS 2009; sweep p) is the explicit knob between oracle and
   conservative graphs.
3. **The bound:** two regimes — dependence-limited (critical path at op
   latencies) and power-limited (T ≥ E/P, with E's transfer component set by
   placement). The optimizer minimizes T subject to power, trading transfer
   energy against concurrency. **Direction of error:** any feasible schedule
   is achievable-by-construction, so T̂ ≥ T*(true ideal); measured gaps of
   real systems against T̂ are *lower bounds* on the true gap — optimizer
   weakness understates the claim, the safe direction.
4. **The optimizer:** placement = energy-weighted graph embedding (physical-
   design placement machinery); scheduling = HLS's SDC/list/modulo scheduling
   with the area constraint deleted; heavyweight offline compute is fine.
   ML-assisted, with an **automated outer loop improving the optimization
   algorithm itself** (AlphaEvolve/FunSearch-style; bound-tightness as
   fitness). Each optimizer generation g yields T̂_g(P) — a monotone-
   improving curve, and **the measured commons-maturity axis of Figure 6**:
   how much of the ceiling automatic optimization of increasing quality
   unlocks, per workload.
5. **Prior-art discipline:** pillar 2.5's anchors (Aladdin/TDG/Timeloop line)
   are the closest instruments — the verified extension S8 contributes is
   wire energy under optimized placement at unlimited area, on whole ordinary
   (irregular) programs (novelty verdict in §2.5). **Reporting sandwich:**
   present the constructive bound between the analytical floor (Choi/Demmel
   algebra evaluated with the same coefficients) and the real-machine points —
   if the constructive bound ever crosses the analytical floor, the harness
   has a bug; the floor is the built-in sanity check. NB (sharpened by
   Matthew, 2026-08-05): **a floor is only valid under the rung's own machine
   assumptions.** Hong-Kung-class I/O bounds assume finite fast memory with
   per-computation accounting — they charge recurrent traffic that persistent
   spatial residency never pays (weights-stationary data enters once, ever;
   the bound does not count reuse *across* operations), so applied outside
   their machine class they sit above the truth and would falsely flag the
   harness. Universal floors only: Σ ops·ε_op plus compulsory I/O (inputs in
   once, outputs out once, amortized across repeated runs). Rung-matched
   floors beyond that; a placement-independent wire-energy floor would need
   embedding/bisection-width lower bounds (Thompson's VLSI area-time theory —
   from model knowledge, VERIFY before use). Artifact:
   `analysis/s8/ideal_asic/` (energy tables with per-node sources, optimizer
   code, bound curves).

### Phase C — constraint projection onto the gem5 architecture, then gap
targeting

1. **Reproduce, then extend (Matthew, 2026-08-05: start from existing
   architectures):** before modifying anything, reproduce published results
   for the chosen baselines — the conventional NUMA multicore validated
   against real-hardware curves (Phase A + Mess), and at least one published
   dataflow/spatial design via its own tooling (candidates by effort:
   DySER/SEED-class via the maintained dsa-framework, gem5-integrated;
   Swarm+T4 via the open SwarmArch Pin sim as the irregular-ceiling
   cross-check). Place every reproduced point on the Phase B bound chart —
   the study's connective figure: published architectures located against
   the limit. Constraint sets below start from these reproduced
   architectures, not invented ones.
2. **Constraint projection:** re-run the *same* optimizer with a real
   architecture's constraint set added — finite tiles/cores, actual
   interconnect latencies and topology, cache-vs-scratchpad capacities,
   task-dispatch/messaging costs (ADM numbers), coherence where applicable —
   and emit the schedule/mapping it produces. The conventional NUMA multicore
   and dataflow-multicore variants are *different constraint sets on one
   optimizer*: the conventional set yields an auto-mapped task/placement
   program (extends TaskMiner with NUMA-aware placement, Kremlin with closed-
   loop automation); the dataflow set yields the mapping for the modeled
   machine (tile-local queues, ADM-cost messaging, Stash-informed local
   stores; non-speculative first — Espresso licenses that subset).
3. **Evaluation:** run the emitted schedule in gem5 on the corresponding
   machine model (Phase A platform; dataflow variant via trace-driven
   scheduler over the identical Ruby/Garnet memory system first,
   dsa-framework / gem5-SALAM tile fabric only if warranted). Verifier for
   any code the mapper emits: differential output testing (+ Alive2-class
   checks where applicable); gem5 cycles as fitness. No human in the loop
   after the harness is built — that is the claim; log every intervention.
4. **The gap stack (the study's central figure):** ceiling T̂(P) →
   constrained-schedule prediction → gem5-measured → naive baseline. Each
   adjacent gap is attributable: ceiling vs constrained = the architecture's
   intrinsic tax; predicted vs measured = dynamic effects the static schedule
   didn't foresee, plus modeling error; auto-mapped vs naive = the recovered
   realization gap. Analysis frame: SEED's region taxonomy and core-size
   sensitivity; Culler 1993's two limits and the TRIPS compiled-vs-hand gap
   as the priors the results must answer.
5. **Gap targeting — the convergence program (the iterate):** the bound and
   the reproduced architectures move *toward each other*. Descending: add
   realism rungs to the limit (Phase B's ladder — storage, instruction
   delivery, memory, finite area). Ascending: improve the architectures —
   better mappings from the optimizer, then architecture changes where the
   bound says the tax is largest (the Q1 sweep: which constraint relaxations
   buy back the most bound). The meeting region is Figure 6's territory,
   measured. This loop is the paper's federation/commons loop instantiated
   as methodology.

### Reporting discipline (from the survey, non-negotiable)

Relative deltas only; every idealization named and swept; medians and harmonic
means; per-era... per-workload-class breakdown; input sensitivity; baseline
trio (tuned serial, best software-parallel, auto-mapped) on identical modeled
hardware; sim-only results flagged as such (FPGA/S9 validates a point later);
"we reinvented Legion" pre-empted by the §1 positioning table.

---

## 4. Honest limits (register with the study)

- Simulation is not silicon; modeling error bounds everything; hence relative
  claims + Mess calibration + validation lineage citations.
- The automatic mapper's quality is the result, not a nuisance parameter — a
  weak mapper understates recoverable gap (that is the honest reading of
  TRIPS's compiled-vs-hand 3×). Report mapper effort/interventions. In the
  ideal-ASIC frame this becomes a feature: the bound is conservative by
  construction, and its improvement across optimizer generations is itself a
  result.
- The ceiling's energy tables are node- and assumption-dependent (state the
  node; relative claims are the robust ones); the ceiling sits on an oracle
  control-flow rung (per-input trace) — say so, and show the p%-speculation
  knob.
- The ideal-ASIC bound is only meaningful down to its stated energy model:
  no leakage/clocking/margining detail, no yield, no real wires — it is a
  physics-flavored bound, not a buildable chip. Landauer (~10⁵× below current
  CMOS, Table 1) marks how much further the *tables themselves* are from
  physics' own floor.
- Workload selection risk: locality-sensitive ordinary code chosen because
  there's a gap to show (the memory note's own caveat); the regular-code
  control and the published desktop-TLP line (Blake, Feng) are the guards.
- Kismet's warning: unconstrained CPA bounds are fantasy; all headline bounds
  must be expressibility-constrained, with the oracle lattice shown.
- Dynamic dependence profiles are per-input under-approximations (may miss
  dependences other inputs exercise) — multiple inputs, stated.
- The Figure 6 conversion (measured axes → conceptual axes) is a modeling
  choice; present it as such or present the measured axes directly.

## 5. Open decisions (Matthew's)

1. Workload slate — and whether LLM-generated "median programmer" code is in
   (on-thesis, but a reviewer magnet).
2. ISA/host confirmation: Arm FS on the GB10 (recommended; check `/dev/kvm`)
   vs x86 FS (worse models) vs RISC-V (weaker FS maturity).
3. Phase C depth for the first paper: trace-driven limit study only (cheap,
   defensible) vs +dsa-framework fabric model (heavier, more Q1).
4. Speculative dependences: keep the p%-speculation knob in the Phase B graph
   only, or build runtime speculation into Phase C's dataflow model (big scope
   add).
5. Where results land: replace F6's conceptual boundary vs add a new measured
   figure alongside it; and whether S8 text enters the paper or the Cosmic AC
   outline first.
6. Energy model choices: which node and table set (Horowitz 45nm vs Dally
   7nm-era numbers); on-chip capacity discipline (unbounded SRAM with
   capacity-costed access vs hard cap + DRAM boundary); power-budget sweep
   range.
7. Optimizer scope: how much compute the self-improving loop gets, and what
   counts as "converged" for a reportable T̂_g curve (fixed generations vs
   plateau criterion).
8. Reproduction targets and fidelity bar: which published architectures
   (DySER/SEED via dsa-framework; Swarm+T4 via SwarmArch sim; others) and
   how close counts as "reproduced."
9. Rung 0 wire cost: energy-only (time = critical path in op latencies) vs
   energy + distance latency on the critical path. NB the reuse question
   couples to this: with energy-only wires, forbidding reuse loses only
   energy; with timed wires it also lengthens serial-recurrence critical
   paths (folded feedback ≈ zero distance vs one iteration-diameter per
   iteration unrolled).
10. Rung 0 place reuse: permit same-op folding (optimizer's choice, one op
    per place per cycle — brings modulo-scheduling machinery and implicit
    zero-cost buffering, which both variants already assume) vs full
    spatialization only. Leading option: permit, and report the
    no-reuse delta as a result (compactness share of the ASIC benefit).
    Under a power budget there is a regime where folding wins outright:
    when unrolled concurrency would be throttled anyway, spatial unrolling's
    extra wire energy buys nothing.

## 6. Must-reads before writing code (consolidated, deduped)

1. Lam & Wilson, ISCA 1992 — constraint lattice + the dataflow-limit numbers
   S8 will be compared against.
2. Kismet (OOPSLA 2011) + Kremlin (PLDI 2011) — the nearest existing
   measurement; expressibility-constrained bounds.
3. Satish et al., ISCA 2012 — the gap-measurement methodology to extend.
4. Dashti et al. (Carrefour), ASPLOS 2013 — congestion recalibration + the
   no-code-change ceiling.
5. Sanchez, Yoo & Kozyrakis (ADM), ASPLOS 2010 — cheapest credible
   architecture, run in gem5's ancestor.
6. Jeffrey et al. (Swarm), MICRO 2015 + Ying et al. (T4), ISCA 2020 — the
   irregular ceiling, the baseline gold standard, and the closest automatic
   compiler.
7. Nowatzki et al. (SEED), ISCA 2015 — region taxonomy; when dataflow wins.
8. Gebhart et al. (TRIPS eval), ASPLOS 2009 — the compiled-vs-hand gap.
9. Culler, Schauser & von Eicken 1993 — the two limits the design must answer.
10. Wang et al. (CXL-DMSim), TCAD 2025 + Mess (MICRO 2024) + LoopPoint (HPCA
    2022) + gem5 v20+ paper (arXiv:2007.03152) — the tooling stack.
    (Tooling docs: PolyArch dsa-framework tutorial; gem5-SALAM mainline-merge
    blog, gem5.org 2025-07-30.)
11. For the Phase B limit study specifically: Shao et al. (Aladdin), ISCA 2014
    — the DDDG→schedule→power skeleton to extend; Nowatzki & Sankaralingam,
    ASPLOS 2016 — the graph-transformation machinery and validation
    discipline; Parashar et al. (Timeloop), ISPASS 2019 + Wu et al.
    (Accelergy), ICCAD 2019 — the mapping-search template and plug-in energy-
    table architecture; Keckler 2011 + Horowitz 2014 + Dally 2020 — the
    constants, per node; Choi IPDPS 2013 + Demmel IPDPS 2013 — the analytical
    floor for the sandwich; Cong & Zhang, DAC 2006 — the scheduling formalism
    to relax.

## 7. Corrections recorded during verification (do not re-propagate)

- ADM is Sanchez–**Yoo**–Kozyrakis, **ASPLOS** 2010 (not Yen; not HPCA).
- Kremlin is **PLDI** 2011 (not MICRO); Speedup Stacks is **ISPASS** 2012 (not
  ISCA); Alchemist is **CGO** 2009 (not HPCA).
- Swarm's simulator is a custom Pin-based sim with zsim-derived timing, not
  gem5. Hive is Posluns et al., ISCA 2022 (Toronto).
- Carbon's headline speedup % unverified (paywalled) — cite the effect via
  ADM's calibrated reimplementation instead.
- Lam & Wilson's 158× oracle is the harmonic mean over the seven non-numeric
  benchmarks only; Austin & Sohi's 13–23,302 is per-benchmark under unlimited
  resources. Quote with those qualifiers.
