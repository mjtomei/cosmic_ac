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
| `assets-rents-socialized-buildout.pdf` | Companion report (Claude dialogue w/ Matthew, 2026-07-27): AI capital cycle — $27T attach vs ~$1.2T stock, rent/revenue requirements, telecom precedent, open-weights-as-bequest. Feeds Cosmic AC outline IV.3. |
| `outline-cosmic-ac.md` | Working outline for the widened compute-commons paper (v1 + capital-cycle integration). Matthew iterating on structure/subtitle with ChatGPT in parallel. |
| `studies-and-work-log.md` | **Study register + dated work log** (S1–S14: done, committed, candidate) — start here for "what have we actually run, and what's next." |
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
figure markdown blocks are floated so the preceding chunk packs (Fig 1 now sits BEFORE
§1.2's last paragraph — moved 2026-07-27 to fill a p3 gap; F3+F4 render as one twin
block after §4's demand paragraph). `render_twocol.py` sets per-figure
layout in `fig_class()`: **figures 2, 3, 4 single-column; 1, 5 full-width**. Tables never
split across pages (`break-inside: avoid`). **QA convention: after every rebuild,
rasterize every page (`pdftoppm -png -r 80`) and view them** — check for table splits,
column gaps, and figure placement; layout is tuned to the current text and prose edits
shift pagination. Figure 2's markdown block deliberately sits after the demand paragraph
(not at its reference) so pages 2–3 pack; that was the fix for the old page-2 whitespace.

## Paper structure (§1–9 + Conclusion + Appendix A; §§2–4 combined 2026-07 per Matthew)

§1 opens with the SPINE SENTENCE (economics of specialization) + the whole-paper
MOVEMENT MAP + §1's own subsection map (per Matthew, after ChatGPT review feedback:
hierarchy made visible; declined that review's §1/§2 merge-flattening and 30-40% herd
cut — instead merged 1+2 as SUBSECTIONS and subsectioned the herd; then combined old
§§2–4 into one §2 with sub-subsections, old-§2 privilege text as its intro).
**Diagnosis:** 1. The gap is effort, not physics — 1.1 The gap, measured (**T1**;
programmability split, ninja gap, dominated frontier, GPU row + Dally bound) ·
1.2 Effort artifact (**F1** now incl. GPU point; fabric tax; LSSD/DSAGEN/OverGen;
accelerator wall; Walter toolchains) ·
2. **Continuous optimization is an under-provided public good** (the central claim as
section title; intro = privilege/who-pays + signpost) — 2.1 The textbook failure
(satisficing/missing markets; positioning para; ceremony paragraph) ·
2.2 **The herd** — 2.2.1 Copying, and the returns to defecting (mechanism, M1/R1/Etched,
entry-fee prediction) · 2.2.2 What actually binds it (competence/encoding, embargo +
**F2 (embargo natural experiment — measured)**, wanting, subjugation) · 2.2.3 What
unbinds it (legibility, best-story, thoughts-allowed).
**Scope:** 3. ASICs — **T2** · 4. Distributed — **F3, F4**.
**Cure:** 5. Open source — 5.1 precedent/fitness · 5.2 ML-breaches-EDA/AHA ·
5.3 silicon commons measured (**T3, F5**, Efabless) · 6. ML multiplies (+ RSI
break-off strong form) · 7. Aggregation point (+ commoditize-the-layer).
**Implication:** 8. Design — 8.1 reconfigurability trade (+ Itanium inversion) ·
8.2 federation loop + financing/underwriter · 8.3 optimum lands (**F6 (phase,
inline at its reference — fixes a p12 column gap), F7 (adoption + Mozart/ML
markers)**) · 9. Honest limits (incl. best-opposing-case bullet) · Conclusion.
**Appendix A** — program, roadmap (phases 1 / 1.5-seeding / 2 / 3), **A1, A2**.
Sub-subsections render as italic h4 (added to render_twocol.py CSS 2026-07).
NOTE: § numbers in the source-ledger notes below may predate the renumberings;
this structure map and the paper itself are authoritative.

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

- **Citation-faithfulness audit (2026-07, 50-agent Opus workflow, all 129 references)**:
  every inline claim checked against its fetched source, mismatches adversarially
  verified. Six fixes applied: BOINC 1M→200K numbers are tracker counts NOT in
  Anderson 2020 (which reports ~700K; quote is "likely inherent"); Bernstein novelty
  cut is ~50% not ~40%; DeepSeek FP8/MLA/PTX engineering lives in the V3 tech report
  (R1 Nature paper is the RL story — cite both); Ericsson 2025 smartphone subs ~7.3B
  not 7.5B; Game Ready profiles are NVIDIA-engineered per title, not population-
  aggregated (Android Cloud Profiles carry the aggregation point); Walter CGRA
  failures concentrate on complex loops, not simple kernels. The ~24%-more-PRs claim
  now has its primary source: Murphy-Hill, Butler & Savelieva, arXiv:2607.01418.

- **Review-response pass (2026-07-27, from Matthew's reviews.txt)**: §1 intro rewritten
  (natural journey, distributed/utilization set up from the start, thoughts-allowed
  moved to intro); NO FORWARD §-REFERENCES convention adopted paper-wide; Table 1
  reworked to multi-source RANGES with GPU split pre/post-tensor-core (TPU v1
  corrected to 14–16× total / 25–29× incremental), ASIC-denominator-soft row,
  Landauer floor (~10⁵× — Landauer 1961, Frank IEEE Spectrum 2017); Plasticine 2.8×
  demoted to "2.8× base / 3.9–42.8× cumulative" (its own paper's numbers); dark
  silicon cut per Matthew ("not a real thing because of voltage scaling"); §2.1
  rebuilt ON the software-economics literature (Johnson 2002, Bessen 2006, von
  Hippel–von Krogh 2003, Varian 2004 best-shot, Dongarra & Walker 1995, Chetlur
  cuDNN 2014, Eghbal 2016, Woodside 2007 — all web-verified) instead of claiming
  novelty; design-reuse-as-convention grounded (Naur 1985, Henderson-Clark 1990,
  DiMaggio-Powell 1983, David 1985, Arthur 1989); M1 rearchitecting carried by
  Frumusanu deep-dive + Dougall Johnson + Handley (AnandTech retired — archive
  note in refs); accelerator wall moved to §5.3 to meet open-silicon data + TSMC
  capex-intensity point (53%→32-33%, Lyons Chipstrat 2026, agent-verified);
  federation claim scoped (embarrassingly-parallel work federates trivially —
  BOINC/Lambda; DiLoCo matters for tightly-coupled); GPU-utilization claim
  hedged with MFU record (38–56% well-tuned, PaLM/Llama-3); zero-sum hardware
  asymmetry added to §3. **analysis/ dir convention: every novel number gets a
  CSV with computations + sources + assumptions** (cost_model.py: stranded
  compute profitable at any utilization; hw-included needs ≥~30% util at
  spot-like discounts). reviews.txt also contains the WIDER-SCOPE outline
  ("Towards the Cosmic AC" / compute-commons reframe) — Matthew wants to work
  that outline TOGETHER, not autonomously; focused fixes were the precondition.

## How Matthew works (conventions)

- **Build on published work; do not argue novelty** (Matthew, 2026-07-28: "we
  aren't publishing economists, more published work is better for us"). Start
  from the existing literature, extend its models, credit prior authors for
  getting there first. State an absence at most once, quietly, and never let an
  argument's weight rest on it. This supersedes any earlier "the synthesis is
  novel" framing (already applied to §2.1 and to the outline's Hayek-criterion
  section).
- **Preserve his wording verbatim**; fix only obvious typos and flag them.
- **Voice: confident and plain.** No defensive hedging or preemptive apology; no
  self-congratulation or flourish. Keep substantive honest caveats, framed as frontiers.
  Anecdotes/sparsely-supported trends are OK to include *with light honest flags*.
- **Verify web facts by search before they enter the paper**; attribute by author/venue
  inline. A full References section now exists before Appendix A (agent-compiled
  2026-07; entries styled via ul.refs in render_twocol.py; keep it in sync when
  citations change). Figures/PDF: QA by rasterizing and viewing.
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
