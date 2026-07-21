---
name: distributed-logical-machine-telos
description: "The ultimate Q2 target — a hardware-independent logical computer with free, automatic, elastic distribution; prior art exists but realization is unpooled"
metadata: 
  node_type: memory
  type: project
  originSessionId: aaa6ff40-df04-4f4b-8a9a-fa58d7a4e24b
---

Matthew's articulation (2026-06-22) of the ultimate target for Q2 (distributed computing's programmability barrier), unifying [[cxl-unified-memory-idea]] with §3 / Omerta.

**The ideal system:** the OS as visible to the user exists only *logically*, independent of the hardware it runs on; connections to other logical computers spin up/down at *near-zero cost* and *without programmer intervention*. This is the CXL / hardware-managed-locality idea taken to its limit — from one node's memory hierarchy out to the whole fabric. Big shared-memory machines are one of the biggest problems holding back distributed-computing adoption.

**Prior art (pieces exist; none took over — realization gap, not absence of ideas):**
- PGAS — OpenSHMEM, UPC, Chapel, Legion: global address space over distributed memory, but programmer still hand-manages affinity for performance (abstraction leaks).
- Single-system-image — TidalScale (ML-driven vCPU/page migration; acquired by HPE ~2022 — verify), ScaleMP vSMP, Numascale; and the older software-DSM graveyard (IVY, TreadMarks, openMosix, MOSIX).
- DPUs / SmartNICs — NVIDIA BlueField, AMD Pensando, Intel IPU: hardware to make remote access/coordination near-free by offloading from the host.

**Sharpest point:** TidalScale had the right *mechanism* (dynamic, learned locality management) but not the *commons* — one vendor's ML on one customer's machine, so the learning never compounded across instances. Pool it + optimize across instances and their combinations = the missing leg.

**Honest floor (= §11 "physics still floors it"):** the logical-machine dream is one of computing's oldest and has failed repeatedly on physics — local-vs-remote latency is a real cliff; an abstraction that hides it either tanks or forces manual locality management. What's different now is two-sided: the substrate is closing the gap (CXL/RDMA/DPU) AND the optimizer (commons + dynamic/ML management) can hide more of what's left. The boundary of "distribution-transparent-friendly" workloads sweeps outward (Figure-4 logic) but never covers everything. Asymptotic, not free.

**Paper ties:** the telos of Q2; unifies the CXL idea + §3 + Omerta (the mesh + ephemeral-VM-as-mesh-peer architecture is reaching for exactly "logical computers, elastic near-zero-cost connections"). Generalizes §9's "code as a contract" to "the machine/OS as a logical contract independent of hardware." Not yet in the paper.
