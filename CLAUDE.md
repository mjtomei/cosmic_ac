# The Performance Commons — project handoff

Context for continuing this work in Claude Code. This folder began as a handoff from a
claude.ai conversation; this file plus the memory directory are the cross-session memory.
Read this first.

**What this is:** a position paper, *The Performance Commons*, arguing that the gap to
ASIC-level performance (and to better ASICs) is a **collective-action problem within and
across the computing stack — not physics**. Machine intelligence is "inoculated" against
that problem, so it exposes it. Two design questions follow — **Q1 (hardware):** design
for abundant shared optimization intelligence → more reconfigurable, less "programmable";
**Q2 (software):** design software stacks assuming distributed computing's programmability
barriers are solved. The paper is **Matthew's forward-looking positioning bet** for
engineers (load-bearing wager: ML gains depth, not just breadth), with a §12 program of
four committed efforts and a first experiment (dataflow-multicore in gem5 first, FPGA
soft-core validation second).

## Files

| File | What it is |
|---|---|
| `the-performance-commons.md` | **Canonical source.** Edit this. |
| `the-performance-commons-2col.pdf` | **Main deliverable** — two-column render (9 pp). |
| `the-performance-commons-figure*.png` | Figures 1–5. Fig 2 is the compact single-column version (direct labels, no legend box). |
| `the-performance-commons-figures-and-tables.md` / `.pdf` | Companion "List of Figures and Tables." Keep in sync (md updated for T4; pdf regenerate pending). |
| `dataflow-vs-heterogeneous-architecture.md` / `.pdf` | Companion technical report behind §2 / Figure 1. |
| `performance-commons-handoff.zip` | Original handoff archive (historical; already extracted). |
| `build/` | Figure + PDF pipeline (`bash build/build.sh`). |

Git repo initialized (2026-06); commit history is now part of the project memory.
The stale single-column `the-performance-commons.pdf` was deleted (recoverable via git).

## Rebuild + QA

    bash build/build.sh        # regenerates all 5 figures + the 2-col PDF

Deps (installed): `matplotlib markdown weasyprint`. `render_twocol.py` sets per-figure
layout in `fig_class()`: **figures 2, 3, 4 single-column; 1, 5 full-width**. Tables never
split across pages (`break-inside: avoid`). **QA convention: after every rebuild,
rasterize every page (`pdftoppm -png -r 80`) and view them** — check for table splits,
column gaps, and figure placement; layout is tuned to the current text and prose edits
shift pagination. Figure 2's markdown block deliberately sits after the demand paragraph
(not at its reference) so pages 2–3 pack; that was the fix for the old page-2 whitespace.

## Paper structure (§1–12 + Conclusion)

1. The gap is real, and it is not physics — **Table 1**
2. General-purpose vs. custom is an effort artifact — **Figure 1**
3. Distributed computing, one level up — **Figures 2 & 3**, Omerta
4. Near-oracular performance is a privilege
5. The privilege is a collective-action problem *(herding paragraph pending — see open items)*
6. The same logic explains the absence of better ASICs — **Table 2**
7. Open source already solved this — **Table 3**, plus: ML-on-open-EDA moat paragraph,
   open-silicon participation/effort-collapse data, Efabless natural experiment
8. Machine intelligence multiplies the commons — velocity anchor (headline-with-asterisk),
   consensus-amplifier vs. coherence-subsidy fork
9. The aggregation point already exists
10. Design hardware for that future — **Figures 4 & 5**, commodity/programmer-inversion
    paragraph (Itanium/Knuth; Wood & Hill; NOW; Bell's Law — all verified citations)
11. Honest limits — incl. partial-inoculation/monoculture and relocated-incentive bullets
12. **The program: where this stands** — **Table 4** (four efforts × progress/open items),
    breadth-is-part-of-the-bet, "A first experiment" (committed, first-person),
    "The flow itself is a target" (automated tool-dev flow, fair comparisons)

## Key incorporated sources (verified)

- **Velocity data**: `~/claude-work/project-manager/docs/velocity-analysis/` (PITCH.md is
  canonical; no compiled PDF exists). §8 cites 250–1,250 py-equiv lines/hr vs 10–50 norm,
  with the honest asterisk (defect rate rising; null/negative solo-assist studies).
- **Coherence**: `~/coherence` (+ github.com/mjtomei/coherence, `pdf/` renders). Supplies
  the inoculation mechanism (suppression-of-idea-variance), §8 fork, §11 monoculture.
  Self-flagged as internally reviewed only; its data anchors belong to a sibling report.
- **Open-lab founding doc** (`~/claude-work/project-manager/papers/open-lab.pdf`, final;
  github.com/mjtomei/project_manager): **deliberately NOT absorbed** (spine-only scope
  decision) except as background; avoid importing its inevitability framing or pm's
  "AI as equal" metaphysics.
- **Omerta status** (§3 + Table 4): re-verified 2026-06 against `~/omerta` plan files
  (use **git dates, not file mtimes** — mtimes are clone-time). Mesh virtual network
  (`OmertaNetwork`: addressing/DHCP/routing/gateway) is built + tested; e2e
  consumer→provider session **broken mid-migration** (WireGuard→mesh; repos' own words);
  protocol 2-of-6 transactions, simulation-only. Economic anchors ($0.08 vs $0.50/hr, 6×)
  confirmed in `omerta_protocol/plans/economic-analysis/ECONOMIC_ANALYSIS.md`.
- **ML-on-EDA + architecture-history citations**: all web-verified before insertion
  (ELM, FunSearch, AlphaEvolve, TRM, DSO.ai/Cerebrus, ORFS-agent, Wood & Hill, Knuth,
  H&P CACM 2019, etc.). **AlphaChip is cited "deployed but contested" via Cheng/Kahng
  ISPD 2023 — never cite Markov's CACM version (active ACM do-not-cite notice).**
- **Open-silicon trend** (§7, verified 2026-07): Tiny Tapeout 152→547 designs/shuttle,
  $150–300 entry vs €4–6k academic MPW, Efabless death→commons-reroute (Mar 2025),
  QTcore-C1 (Pearce 2023), 18-high-schoolers/90-min LLM datapoint (Krupp, Venn & Wehn 2026).

## How Matthew works (conventions)

- **Preserve his wording verbatim**; fix only obvious typos and flag them.
- **Voice: confident and plain.** No defensive hedging or preemptive apology; no
  self-congratulation or flourish. Keep substantive honest caveats, framed as frontiers.
  Anecdotes/sparsely-supported trends are OK to include *with light honest flags*.
- **Verify web facts by search before they enter the paper**; attribute by author/venue
  inline (no bibliography). Figures/PDF: QA by rasterizing and viewing.
- Figure captions are reader-facing. Conceptual/illustrative figures say so, with real
  anchors named. Minimize whitespace; pack figures tight.
- Wants real quantitative data and honest pushback over agreement.

## Open items

1. **Herding/§5 paragraph — in flight.** Approved for inclusion. Mechanism (Matthew's
   correction): teams **copy** each other and **suppress internal novelty** because
   career risk is individual even when marginal cost is trivial. Echo his published
   coherence language (see memory: herd-mentality-monoculture-point). Kimi **K3**
   (July 16, 2026: 2.8T open-weight, top-3 on Artificial Analysis evals, #1 blind
   Frontend Code arena ahead of Fable 5) is the embargo-era anchor; DeepSeek R1
   engineering-under-constraint + monoculture scholarship (Kleinberg-Raghavan,
   Bommasani, Scharfstein-Stein) were being verified by an agent when this was written.
2. **Regenerate `the-performance-commons-figures-and-tables.pdf`** from its updated md
   (no build script exists for it — simple markdown+weasyprint render).
3. **Memory idea-cluster not yet in the paper**: CXL/hardware-managed locality,
   distributed logical-machine telos, standards-coordinate-interface-not-competence,
   naming the depth-bet explicitly. See `MEMORY.md` in the project memory directory.
4. Table 4's pm and coherence rows were **not** re-verified with the git-recency rigor
   applied to Omerta; worth a pass if those claims become load-bearing.
