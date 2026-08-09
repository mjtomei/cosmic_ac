# S9 profiling track — candidate discovery for the FPGA flow

*Started 2026-08-05, in parallel with board bring-up (Matthew: "start the
profiling in parallel with a goal of targeting applications [it] finds with
the FPGA flow as soon as possible"). Goal: a ranked candidate list of hot
regions in real workloads, ready when the Zybo flow comes up.*

## Design

*(Revised 2026-08-05, Matthew: profiling on the GB10 cannot close the loop —
optimizations found there aren't testable on the same stack. The board is
the watched machine; the GB10 is the observer's machine, reached by SSH.)*

1. **Host stage (GB10) = bootstrap scouting only:** coarse anchors and
   candidate shortlisting (this harness). Structure-portable, never
   decision-grade.
2. **Subject stage (Zybo) = the study:** workloads run ON the board — the
   full ported mix on the A9s (Debian-class armhf userspace, NEON
   baselines), and scaled workloads on the instrumented VexRiscv (rv32
   Linux via LiteX+Buildroot) where retire/memory-stream visibility
   matters. Profiles, candidate ranking (Accelerometer-style merit/cost
   with real PS↔PL interface costs), acceleration, and validation all
   happen on one stack, in situ. The QEMU twin on the GB10 emulates the
   subject ISAs (rv32/armhf — the same software stack) for deep discovery,
   timing-blind; decisions ground on the board.

## Candidate criteria (from the verified literature)

- **Merit:** cycles × invocation count in real runs (not microbenchmarks).
- **Interface cost:** bytes moved per invocation vs HP (~1 GB/s/port) and
  ACP; offload profitability per the Accelerometer model (sync/async,
  dispatch + data movement + queuing) — no folk "need 10×" rule, derive it.
- **Amenability (the warp wall, §2 of the S9 plan):** loop-dominated,
  bounded working set, limited pointer-chasing/recursion/dynamic
  allocation; note which failures an LLM rewrite could fix (C2HLSC-class)
  vs structural ones.
- **Tier:** tier-1 (known-good tax kernels — calibration against known
  hardware answers) vs tier-2 (application-specific hot code below the
  specialization threshold — the thesis case; headline results come from
  here, never from benchmark kernels: contamination guard).

## Backends on the GB10

| Backend | Status | Covers |
|---|---|---|
| `perf` | **BLOCKED: kernel.perf_event_paranoid=4.** One-time root fix: `sudo sysctl kernel.perf_event_paranoid=1` (persist in /etc/sysctl.conf). Unlocks profiling of any binary, no rebuild. | everything |
| `py-spy` (0.4.2, ~/.local/bin) | working (own children; ptrace_scope=1) | Python workloads |
| `gprof` (-pg rebuild) | working | candidates built from source |
| `/usr/bin/time -v` + loops | working | coarse end-to-end anchors |

## Files

- `profile_py.sh <out-name> -- <python cmd...>` — py-spy speedscope + top-N
  function table.
- `bench_kernels.sh` — tier-1 kernel timing anchors on real repo data
  (zstd/gzip/xz/sha256/json), coarse, backend-free.
- `candidates.csv` — the living ranked list (one row per candidate region):
  workload, region, host_cycles_share, bytes_per_invocation, amenability,
  tier, notes, a9_cycles_share (empty until target stage).
- `runs/` — raw profiler output, one subdir per dated run.

## Honest limits

- Host-stage shares are GB10 (Cortex-X925-class cores, 4-wide+ OOO, SVE) —
  the A9 will weight memory-bound and scalar code differently; treat host
  ranking as a shortlist generator only.
- py-spy is a sampler: ~1% shares are noise-level; report ≥5% only.
- The repo's own pipelines (S10 scoring etc.) are partly GPU-bound; profile
  their CPU phases (extraction, parsing, stats) — the GPU parts are not
  FPGA targets on a Z7-class fabric.
