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

Deps (installed): `matplotlib markdown weasyprint`. **CRITICAL renderer note (2026-07):**
WeasyPrint's `column-span: all` is buggy — under certain page geometries it silently
drops the entire rest of the document (we hit 14pp→2pp). render_twocol.py therefore
splits the body at full-width figures/tables into alternating `.paper` two-column
chunks and top-level `.fullblock` elements; NEVER reintroduce column-span. Full-width
figure markdown blocks are floated to section ends (Fig 1 after §2's last paragraph,
Fig 2 after §7's demand paragraph) so the preceding chunk packs. `render_twocol.py` sets per-figure
layout in `fig_class()`: **figures 2, 3, 4 single-column; 1, 5 full-width**. Tables never
split across pages (`break-inside: avoid`). **QA convention: after every rebuild,
rasterize every page (`pdftoppm -png -r 80`) and view them** — check for table splits,
column gaps, and figure placement; layout is tuned to the current text and prose edits
shift pagination. Figure 2's markdown block deliberately sits after the demand paragraph
(not at its reference) so pages 2–3 pack; that was the fix for the old page-2 whitespace.

## Paper structure (§1–11 + Conclusion + Appendix A; merged/subsectioned 2026-07)

§1 opens with the SPINE SENTENCE (economics of specialization) + the whole-paper
MOVEMENT MAP + §1's own subsection map (per Matthew, after ChatGPT review feedback:
hierarchy made visible; declined that review's §1/§2 merge-flattening and 30-40% herd
cut — instead merged 1+2 as SUBSECTIONS and subsectioned the herd).
**Diagnosis:** 1. The gap is effort, not physics — 1.1 The gap, measured (**T1**;
programmability split, ninja gap, dominated frontier, GPU row + Dally bound) ·
1.2 Effort artifact (**F1** now incl. GPU point; fabric tax; LSSD/DSAGEN/OverGen;
accelerator wall; Walter toolchains) · 2. Privilege (+ diagnosis signpost) ·
3. **Continuous optimization is an under-provided public good** (RETITLED 2026-07 —
the claim elevated to subtitle/abstract/spine/§3-title + ceremony paragraph per Matthew;
satisficing/missing markets; positioning para) ·
4. **The herd** — 4.1 Copying, and the returns to defecting (mechanism, M1/R1/Etched,
entry-fee prediction) · 4.2 What actually binds it (competence/encoding, embargo +
**F2 (embargo natural experiment — measured)**, wanting, subjugation) · 4.3 What
unbinds it (legibility, best-story, thoughts-allowed).
**Scope:** 5. ASICs — **T2** · 6. Distributed — **F3, F4**.
**Cure:** 7. Open source — **T3, F5**, EDA/AHA, Efabless · 8. ML multiplies ·
9. Aggregation point.
**Implication:** 10. Design — **F6 (phase), F7 (adoption + Mozart/ML markers)**,
inversion, financing · 11. Honest limits (incl. best-opposing-case bullet) · Conclusion.
**Appendix A** — program, roadmap (phases 1 / 1.5-seeding / 2 / 3), **A1, A2**.

Figure files: figure.png=F1, figure-embargo=F2, figure-2/3=F3/F4, figure-tapeout=F5,
figure-4=F6, figure-5=F7. File names do NOT match figure numbers — captions are
authoritative. Subsections render as h3. All § cross-refs renumbered by script; grep
"§" after any structure edit.

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
- **Published-anchor pass (2026-07, all web-verified)**: Leiserson et al. Science 2020
  (60,000× matmul; §1 + §4 related-work para); Thompson-Spanuth, Hess-Ostrom, Fursin-Temam,
  Lerner-Tirole (§4/§8 positioning — NOTE: prior-art search found the paper's synthesis
  novel); DiLoCo scaling laws (Charles 2025), INTELLECT-1, Consilience-40B, Covenant-72B
  + three honest flags incl. INTELLECT-3-centralized (§7); Wu NSDI'24 spot economics (§7);
  productivity trio Peng/Cui-MgmtSci-2026/METR + Feb-2026 METR walkback + fleet-gap-
  still-holds (§9); Groq/SambaNova/Cerebras dataflow cites (§11); Dreslinski/ISSCC-2012
  near-threshold (§5). Ouchi/Holmström-Milgrom/Kuran now VERIFIED (no unverified cites remain).
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

1. **Memory idea-cluster not yet in the paper**: CXL/hardware-managed locality,
   distributed logical-machine telos, standards-coordinate-interface-not-competence.
   (Depth/competence bet now named in §6; herding fully inserted §1/§6 — see memory:
   herd-mentality-monoculture-point for the full anchor set and framing rules,
   incl. NEVER citing Markov's CACM AlphaChip critique and K3-weights-not-yet-published.)
2. **Regenerate `the-performance-commons-figures-and-tables.pdf`** whenever its md
   changes (no build script — simple markdown+weasyprint inline render; see git history
   for the CSS used).
3. Table 4's pm and coherence rows were **not** re-verified with the git-recency rigor
   applied to Omerta; worth a pass if those claims become load-bearing.
4. Canonical-tier citations placed from model knowledge without agent verification
   (flagged to Matthew): Thiel & Masters 2014, and §4's missing-markets quartet —
   Simon 1956, Akerlof 1970, Coase 1937, Arrow 1969, Samuelson 1954, Olson 1965;
   (§8's RSI set is now WEB-VERIFIED 2026-07: Good 1965 Advances-in-Computers-v6 + quote,
   Korinek-Stiglitz NBER 2017, Korinek-Suh NBER 2024, AlphaEvolve 23%-Gemini-kernel,
   STOP COLM 2024, Darwin Gödel Machine 20→50%-preprint-flagged, and all three lab
   frameworks gating on self-improvement: OpenAI PF v2, Anthropic RSP AI-R&D-5,
   DeepMind FSF ML-R&D); §11's Klein-seL4 SOSP 2009 and Grossman 1981 (warranties). The structure-review data pass (Dally CACM 2020 13-23% bound, KernelBench, Game Ready/Baseline-Profiles, Oliker 4-14%, Koomey-Taylor 2015, Ericsson/Microsoft/LiteGreen, IBS NRE, Anderson BOINC 2020, LBNL 59%-2012) is all web-verified. Citation-graph pass around the Sankaralingam line (2026-07, all verified): LSSD/TopPicks, DSAGEN, OverGen 0.55x, Lottarini Master-of-None, Dark Silicon arc, Walter CGRA-toolchain fragmentation 2025, Accelerator Wall (307x-vs-1.7x), Mozart ISCA-2022 lessons quotes + MapZero ISCA-2023, AHA Amber/Onyx, Dally/Jouppi named as S12's best counter. (Ouchi/Holmström-Milgrom/Kuran
   were later verified.) Verify if they become load-bearing.
