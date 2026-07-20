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

## Paper structure (§1–12 + Conclusion + Appendix A; five movements, settled 2026-07)

The defections (M1 / R1 / Etched LVI) + the entry-fee prediction live in §5's defector
paragraphs, previewed briefly in §1's dominated-frontier paragraph. They are NOT in the
abstract (a closing sentence was tried there and removed — Matthew: didn't fit) and NOT
a cold-open section (also tried and dissolved).
**Diagnosis:** 1. Gap is real, not physics — **T1** (§1 rewritten 2026-07: opens by
splitting "programmability" into constant-effort vs realizable-frontier (roofline, CACM
2009), evidences the realization gap on FIXED silicon (Leiserson 60,000×; Satish
ninja-gap 24×, ISCA 2012 — both verified), then dominated-frontier proofs (M1/LVI), and
only then the cross-arch ratios as the separate intrinsic floor — fixing the old
non-sequitur; abstract's defection sentences REMOVED, defections live in §5 only) ·
2. Effort artifact — **F1** (§2 now says "§1's realization gap") ·
3. Privilege · 4. Collective-action problem (+ satisficing/missing-markets paragraph:
good-enough as distribution failure; Akerlof/Coase/Arrow; market-creation as recursed
collective-action problem; ML creates missing markets — added 2026-07) · 5. **The herd** (mechanism/copying,
defectors + entry-fee prediction, systemic-timidity "the encoding is changing", embargo
experiment, executive wanting-data, subjugation-as-proxy, legibility prediction,
which-thoughts-are-allowed capstone).
**Scope:** 6. Absence of better ASICs — **T2** · 7. Distributed computing, one level up
— **F2, F3**, Omerta (pointer to Appendix A).
**Cure:** 8. Open source solved it — **T3 (entry cost of first silicon — replaced the
old commons-wins list, folded to prose)**, **F4 (Tiny Tapeout participation through the
Efabless shutdown — the only fully-measured figure; build/fig_tapeout.py)**, ML-on-EDA ·
9. ML multiplies (velocity, fork) · 10. Aggregation point.
**Implication:** 11. Design — **F5 (phase), F6 (adoption)**, programmer inversion,
hardware-sells-its-own-free-time paragraph (architectural sharing below the OS;
gatekeepers/social-integration barrier; 0%-loan with sharing-variable, even NEGATIVE
(profit-sharing → farm-building) payments — Matthew: flat discount too weak for ~30%
utilization, consumers less risk-averse than gatekeepers; solar/handset precedent;
builder as lender+underwriter —
added 2026-07; appendix notes it as Omerta's best version) ·
12. Honest limits · Conclusion.
**Appendix A: The program in detail** — the program intro + breadth-bet + velocity
measurement + Omerta status + **Table A1** + full experimental protocols.
**RULE (Matthew, strict): main text = argument + existing published work ONLY; anything
we are planning, proposing, or building ourselves lives in Appendix A** (pointers in
main are fine; citations of his existing public companion papers are fine).

Figure files: figure.png=F1, figure-2/3=F2/F3, figure-tapeout=F4, figure-4=F5,
figure-5=F6 (file names no longer match figure numbers for F5/F6 — captions are
authoritative). All § cross-refs renumbered by script; grep "§" after any structure edit.

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
   Simon 1956, Akerlof 1970, Coase 1937, Arrow 1969, Samuelson 1954, Olson 1965; §11's Klein-seL4 SOSP 2009 and Grossman 1981 (warranties). The structure-review data pass (Dally CACM 2020 13-23% bound, KernelBench, Game Ready/Baseline-Profiles, Oliker 4-14%, Koomey-Taylor 2015, Ericsson/Microsoft/LiteGreen, IBS NRE, Anderson BOINC 2020, LBNL 59%-2012) is all web-verified. (Ouchi/Holmström-Milgrom/Kuran
   were later verified.) Verify if they become load-bearing.
