# The Performance Commons — project handoff

Context for continuing this work in Claude Code. This folder was handed off from a
Claude app (claude.ai) conversation; the conversation itself does not transfer, so this
file is the memory. Read it first.

**What this is:** a position paper, *The Performance Commons*, arguing that the gap to
ASIC-level performance (and to better ASICs) is a **collective-action problem within and
across the computing stack — not physics**. Machine intelligence is "inoculated" against
that problem, so it exposes it. Two forward-looking design questions follow:
- **Q1 (hardware):** design for abundant shared optimization intelligence → **more
  reconfigurable, less "programmable"** silicon.
- **Q2 (software):** design software stacks assuming distributed computing's
  programmability barriers are solved.

## Files in this folder

| File | What it is |
|---|---|
| `the-performance-commons.md` | **Canonical source.** Edit this. |
| `the-performance-commons-2col.pdf` | **Main deliverable** — two-column render (7 pp). |
| `the-performance-commons-figure*.png` | Figures 1–5 (see below). |
| `the-performance-commons-figures-and-tables.md` / `.pdf` | "List of Figures and Tables" — the visual argument spine. Keep in sync with the paper. |
| `dataflow-vs-heterogeneous-architecture.md` / `.pdf` | Companion technical report the paper draws on for §2 / Figure 1. |
| `the-performance-commons.pdf` | **STALE** single-column render. `-2col.pdf` is canonical; regenerate or delete. |
| `build/` | Figure + PDF pipeline (`bash build/build.sh`). |

## Rebuild

    bash build/build.sh        # regenerates all 5 figures + the 2-col PDF

Deps: `pip install matplotlib markdown weasyprint pypdf` (WeasyPrint needs system
Pango/cairo; macOS: `brew install pango`). See `build/README.md` for the script→figure map.
`render_twocol.py` decides full-width vs single-column per figure in its `fig_class()`.

## Paper structure (sections 1–11)

1. The gap is real, and it is not physics — **Table 1**
2. The general-purpose vs. custom trade-off is mostly an effort artifact — **Figure 1** (answers Q1)
3. Distributed computing is the same problem, one level up — **Figures 2 & 3**, Omerta (answers Q2)
4. Near-oracular performance is a privilege
5. The privilege is a collective-action problem
6. The same logic explains the absence of better ASICs — **Table 2**
7. Open source already solved this — and did it by itself — **Table 3**
8. Machine intelligence multiplies the commons; it does not replace it
9. The aggregation point already exists
10. The implication: design hardware for that future — **Figures 4 & 5**
11. Honest limits → Conclusion

## Figures (1–5) — content, sourcing, layout

- **Fig 1** (§2, full-width) — flexibility–efficiency frontier *flattens* under unlimited effort; effort gap = fabric tax + realization gap. *Endpoints (CGRA ~2.8×, FPGA ~20–35×) measured; curve illustrative.*
- **Fig 2** (§3, full-width) — useful compute vs looseness of coupling; naive methods collapse, DiLoCo-class hold ~90%. *Anchored to DiLoCo/OpenDiLoCo; utilization illustrative.*
- **Fig 3** (§3, single-column) — "Machine demand has no floor": human demand saturates, machine demand extends below datacenter cost (~$0.50/hr) into idle-home range (~$0.08/hr). *Cost anchors from Omerta's reliability-market simulation; task-value ladder from its economic-analysis notes; curve illustrative.*
- **Fig 4** (§10, single-column) — phase diagram (commons-maturity × workload-diversity); reconfigurable-optimal region sweeps left as the commons matures. *Conceptual.*
- **Fig 5** (§10, full-width) — reconfigurable datacenter adoption: real milestones (Catapult; Intel–Altera $16.7B 2015; AWS F1; AMD–Xilinx $49B 2022) + projected inflection. *Milestones/values real; share curve and post-2025 a projection.*

## Tables (1–3)

- **T1** (§1) efficiency gap quantified (Hameed; Kuon & Rose; Prabhakar).
- **T2** (§6) the same non-rival-good hoarding at every stack layer + its open counter-trend.
- **T3** (§7) open commons that out-competed proprietary alternatives (Linux, LLVM, RISC-V, Mesa, PyTorch, FFmpeg).

## Omerta (the companion software project) — github.com/mjtomei/omerta

The meta-repo aggregates five subrepos by pinned commit. Clone and populate:

    git clone https://github.com/mjtomei/omerta && cd omerta && make   # pulls subrepos

§3 cites Omerta as **in-progress, not finished**. State verified from the code at the
pinned commits below (do not overstate it):

| Subrepo | State | Detail |
|---|---|---|
| `omerta_mesh` | **most built** | ~33k src / ~34k tests. ChaCha20-Poly1305, X25519/Ed25519, NAT traversal, relays, gossip discovery, gVisor tunnelling, virtual networking. |
| `omerta_node` | partial; **e2e broken** | ~17.6k. Ephemeral-VM lifecycle works (Virtualization.framework/QEMU); consumer↔provider session broken mid-migration (WireGuard→mesh). |
| `omerta_lang` | working | ~11k. `.omt` parser / validator / codegen / CLI. |
| `omerta_protocol` | **design + simulation** | ~27k sim. 2 of 6 transactions tested (escrow_lock, cabal_attestation); 4 drafts. Trust/payment layer validated in simulation, **not a live chain**. |
| `omerta_infra` | working | Terraform for AWS bootstrap + STUN servers. |

Pinned commits (`.commit` files in the meta-repo): node `ad807ed`, mesh `81af0c1`,
lang `7813cb9`, protocol `1173e90`, infra `fe82252`.

**Data anchors the paper borrows from Omerta:**
- Home vs datacenter cost: **$0.08 vs $0.50/hr (~6×)**, reliability 92% vs 99.8% — `omerta_protocol/simulations/economic/economic_value_simulation.py`, `reliability_market_*.py`.
- Task-value ladder (frontier→precompute; "humans run out of ideas; machines run out of compute") — `omerta_protocol/plans/economic-analysis/ECONOMIC_ANALYSIS.md` (an analysis doc, **not** the simulator — keep the attribution split).
- Supply-waste stats in §3 (12–18% avg server utilization, up to ~30% "comatose", ~10M idle servers ≈ $30B) are **external** — NRDC/Anthesis "comatose servers" study; figures repeated in a Fortune opinion piece (Aug 2025). Attribute in prose, not to Omerta.

## How Matthew works (conventions)

- **Preserve his wording verbatim.** Fix only obvious typos, and flag them; don't rewrite his prose to taste.
- Figure **captions are reader-facing** (not notes to the author).
- **Flag honestly:** conceptual/illustrative figures say so, with the real anchors named.
- **Minimise white space;** pack figures tight. QA every figure/PDF by rasterizing and viewing it.
- Wants **real quantitative data** and the argument to "bite"; values honest pushback over agreement.
- Web facts: attributed by author/venue in the paper's prose (cited inline when in chat).

## Open items / next steps

1. **Page-2 whitespace (~20%)** before the full-width Figure 2. Close it by either making Figure 2 single-column (compact, like Figs 3–4) or adding one on-thesis paragraph — the "induced demand: building more datacenters just pulls more demand, like adding highway lanes" point (from the Fortune piece) fits §3's supply argument.
2. **LOC claim in §3** — the mesh is described as "tens of thousands of lines, with a comparable volume of tests." Accurate, but Matthew may want it softened to a qualitative claim for a position paper. Open question.
3. **Stale single-column PDF** (`the-performance-commons.pdf`) — regenerate from the current source or delete; `-2col.pdf` is the maintained render.
4. Structure work (promote §3, renumber sections 1–11 and figures 1–5, relocate Figure 2 into §3) is **done**.
