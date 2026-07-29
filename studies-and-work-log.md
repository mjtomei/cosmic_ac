# Studies and Work Log

Register of every empirical effort behind the paper — done, committed, and
candidate — plus a dated log of what has actually been run. Companion to
`outline-cosmic-ac.md` (argument structure) and `analysis/` (data and models).

Convention carried from `analysis/README.md`: **every novel number gets a
reproducible artifact** — a script, a CSV, or a documented workflow — with
sources for anything not derived here and assumptions written down.

---

## Study register

### S1. Open-source hardware entry cost and participation — **DONE, in paper**
*Question:* has the entry cost of custom silicon collapsed, and did participation
follow it down?
*Findings:* full mask set >$500k → Tiny Tapeout tile $150–300; designs per
shuttle 152 → 547; the platform's commercial center (Efabless) died in March
2025 and throughput rose anyway; eighteen high-schoolers to eight verified
tapeout-ready designs in ninety minutes with an LLM agent.
*Artifacts:* Table 3, Figure 5 (`build/fig_tapeout.py`), §5.3.
*Honest flags:* showcases self-select; first-silicon failure rates unpublished;
a shuttle tile is thousands of gates, not a commercial ASIC.

### S2. The embargo natural experiment — **DONE, in paper**
*Question:* did restricting training hardware restrict capability?
*Findings:* US–China Arena gap 9.3% (Jan 2024) → 1.7% (Feb 2025) → 2.7% (early
2026) while the hardware lead held at ~4 years.
*Artifacts:* Figure 2 (`build/fig_embargo.py`), §2.2.2.
*Honest flags:* single-metric series; distillation, stockpiles and subsidy are
real confounders — the narrow inference (silicon was not the binding
constraint) is what survives them.

### S3. Consumer vs datacenter compute economics — **DONE**
*Question:* does pooled consumer compute clear margin at spot-like prices, with
and without hardware cost?
*Findings:* marginal cost ~$0.005/hr hardware-excluded; ~$0.04/$0.06/$0.18 per
hour at 50/30/10% utilization hardware-included. Stranded compute is profitable
at any discount; giving devices away needs ≥~30% utilization or pricing above
the deepest spot tier.
*Artifacts:* `analysis/cost_model.py` → `consumer_vs_datacenter_cost.csv`.
*Open:* real utilization distributions (see S11).

### S4. Citation-faithfulness audit — **DONE (method reusable)**
*Question:* does every inline claim faithfully represent its source?
*Method:* 50 Opus agents, one per reference batch, each fetching the source;
every mismatch adversarially verified before action.
*Findings:* 6 real misrepresentations out of 129 references, all fixed; the
~24%-more-PRs claim found its primary source.
*Artifact:* workflow script in the session's workflow directory; ledger in
`CLAUDE.md`.

### S5. Reading-list review and ranking — **DONE**
*Question:* which of the assembled literature is actually load-bearing?
*Method:* one agent reads each paper and scores relevance / field standing /
quality; a calibration pass normalizes across all of them. Two rounds (51 + 23),
round 2 anchored to round 1's composites so both sit on one scale.
*Artifacts:* `~/reading/software-economies-and-the-knowledge-problem/`
(74 PDFs, `00-README-*.md`, `00-RANKINGS.json`).

### S6. Citation-graph sweep — **DONE**
*Question:* what published work already does part of the Hayek criterion's job?
*Method:* 65 agents over Semantic Scholar and OpenAlex from 14 seeds; forward
and backward citations; every candidate adversarially verified.
*Findings:* all four criterion legs have published machinery in five disjoint
communities; drift is formalized four times over; scheduler-as-planned-economy
is not ours to claim (Karma, OSDI 2023).
*Artifact:* `00-CITATION-SWEEP.json` in the reading directory.

### S7. Development-velocity measurement — **DONE elsewhere, cited**
*Source:* `~/claude-work/project-manager/docs/velocity-analysis/`.
*Use:* §6 and Appendix A, with the honest asterisk that defect rate rises as
output outpaces review.

---

### S8. Dataflow-multicore in gem5 — **COMMITTED, not started**
*Question:* how much of the realization gap is recoverable by automatic dataflow
mapping of ordinary code?
*Method:* ordinary code on a simulated multicore with NUMA and a full memory
hierarchy; measure achieved vs available parallelism, locality on the floor,
remote-access counts; remap to a dataflow architecture; measure again.
*Why it matters:* §1.2's central inference — that the effort gap is largest on
reconfigurable substrates — is currently unmeasured. This is the measurement.
*Cost:* compute only; gem5 is free.
*Artifact target:* `analysis/` sweep + a figure replacing Figure 6's conceptual
boundary with a measured one.

### S9. FPGA soft-core specialization — **COMMITTED, second**
*Question:* does the simulated gain survive on real silicon?
*Method:* RISC-V soft core (Rocket/CVA6/VexRiscv) on a commodity FPGA; profile a
genuine workload on the core's own performance counters; synthesize a
tightly-coupled accelerator or retune the microarchitecture; re-place with the
open flow (Yosys, OpenROAD); measure the same workload again.
*Honest flags:* a soft core on an FPGA is itself ~20–35× off an ASIC, so this
isolates *relative* gain from profile-guided specialization, never an absolute
number. The crux in both S8 and S9 is automatic mapping — measuring the gap is
easy, closing it without a human in the loop is the claim.

---

### S10. AI-generated text in legislative transcripts — **CANDIDATE, designed**
*Origin:* the Bill Oliver clip (New Brunswick, May–June 2026) in which a member
appears to read a model's framing sentence aloud mid-speech. Matthew ran the
YouTube auto-caption transcript through Pangram: **100% AI-generated**.

*Question:* what share of legislative speech is machine-generated, and how has
it moved since late 2022?

*Why it matters for the paper:* it converts V.3's "the office is a socket" from
an anecdote into a measured trend — direct evidence that substitution of machine
cognition into institutional roles is already underway and unremarked. It is the
paper's best candidate for an original empirical figure, and it is *cheap*.

*Method:*
1. Corpus: official Hansard (not auto-captions). New Brunswick's 61st Legislature
   is already downloaded — 38 sittings, 1.60M words bilingual, ~0.80M English.
   Extend to other Canadian provinces, the federal Parliament, UK, Australia,
   US states with published verbatim records.
2. Segment by speech and by speaker, keeping date, chamber, party, and whether
   the passage is prepared remarks or spontaneous debate (the distinction is
   likely to dominate the signal).
3. Score each segment with a detector (Pangram; ideally a second detector for
   agreement).
4. Report share-of-words flagged over time, per chamber and per speaker.

*The methodological crux — a negative control:* score pre-2022 transcripts from
the same chambers and speakers. Any nonzero rate there is the false-positive
floor, and the study's entire claim is the delta above it. Without this the
result is worthless, because formal prepared oratory is exactly the register
detectors over-flag.

*Other confounds to state:* Hansard is lightly edited by professional editors,
which may itself normalize prose toward the flagged register; prepared speeches
have always been staff-drafted, so "AI" and "not written by the speaker" are
different claims and only the former is being measured; bilingual chambers carry
professional translations that should be scored separately or excluded.

*Cost (Pangram, measured against the NB corpus):*

| Scope | English words | Pangram 4 API | bulk −20% |
|---|---|---|---|
| NB, one session (have it) | 0.80M | $401 | **$321** |
| NB, full legislature (~4 sessions) | 3.2M | $1,604 | $1,284 |
| One large provincial legislature, 1 yr | ~8M | $4,000 | $3,200 |
| Canadian Parliament, 1 yr | ~40M | $20,000 | $16,000 |
| 10 legislatures × 5 yrs | ~200M | $100,000 | $80,000 |

Pangram's older model is listed at 1/10th the price ($0.05/1,000 words), which
would put a full NB legislature at ~$128 — worth testing whether its accuracy
suffices, since a 10× price difference changes what is affordable by two orders
of scope. The **Professional plan ($65/mo, 1.5M words/mo + $200 API credit)**
covers roughly two NB sessions per month at no marginal cost: a slow,
subscription-paced study over a year costs ~$780 and covers ~18M words, which is
a serious corpus. *Recommended entry point: one month of Professional, NB corpus
plus a pre-2022 control, ≈$65.*

*Instrumentation — revised 2026-07-29 after Matthew asked about cheaper and
local options. The paid detector turns out to be the wrong primary instrument.*

**Tier 1 — prompt-leakage regex (free, hard lower bound).** Not "common LLM
phrases" in the stylistic sense (delve, tapestry, "it is important to note"),
which have real and drifting human base rates. The strong version searches for
**meta-discourse addressed to a requester rather than an audience** — text that
can only appear if model output was pasted without editing. The Bill Oliver line
is the type specimen: an offer to produce a revised version, read aloud in the
chamber. Categories: assistant framing ("Here's a…", "Certainly, here is…",
"I hope this helps", "Let me know if you'd like…"); instruction echoes ("in a
professional tone", "as requested", "a more natural flowing version");
self-identification ("as an AI language model"); unfilled placeholders
("[INSERT NAME]", "[Your Name]"); and markdown artifacts surviving into a
spoken or printed record. Every hit is individually verifiable and quotable, so
this yields a defensible **floor**, not an estimate — the rate will be small,
and the trend plus the specimens are the story.

**Tier 2 — distributional estimation (free, the headline number).** The method
this study should actually be built on: **Liang, Izzo, Zhang et al.,
"Monitoring AI-Modified Content at Scale" (arXiv:2403.07183)** estimates the
*fraction* of a corpus substantially modified by an LLM using maximum-likelihood
over word-frequency distributions, calibrated with human-written and
AI-generated reference texts. It works at corpus level, so it never needs
per-document accuracy — which is exactly the weakness of every per-document
detector on this register. Applied here: pre-2022 Hansard is the human
reference; model-drafted speeches on the same bills are the AI reference; the
estimate runs per month or per session and becomes the figure. This is Matthew's
lexical-filter intuition formalized, and strictly better than a hand-picked
list, because it uses the whole distribution and cannot be accused of
cherry-picking. **Cost: zero.**

**Tier 3 — local zero-shot detectors (free, validation).** The machine has an
NVIDIA GB10 and 119 GB of RAM, so per-document scoring is a compute question,
not a budget one. Candidates, all verified to exist:
- **Binoculars** (Hans, Schwarzschild, Cherepanova et al., arXiv:2401.12070) —
  zero-shot, contrasts two closely related models, no training required. First
  choice.
- **Fast-DetectGPT** (Bao, Zhao, Teng et al., arXiv:2310.05130) — conditional
  probability curvature; the cheap successor to DetectGPT.
- **Ghostbuster** (Verma, Fleisig, Tomlin et al., arXiv:2305.15047) — features
  from weaker models, no token-probability access needed for the target model.
Use these to score the segments Tiers 1–2 surface, not to sweep the corpus
blind. **Caveat to state in any writeup:** these were validated on essays and
news, mostly against 2023–24 models; legislative oratory is a different register
and 2026 models are harder to detect, so treat their absolute rates as
uncalibrated for this domain.

**Tier 4 — Pangram on a sample (paid, cross-check).** Demoted from the primary
instrument to an independent second opinion on a few hundred segments. At that
volume the free tier (2,000 words/day) or one month of Professional ($65) is
sufficient; the four- and five-figure corpus-sweep estimates below are no longer
the plan, and are kept only to show what the naive approach would have cost.

*Status:* not started. Blocking questions — none on cost any more. The remaining
decisions are which reference corpus to use for the Tier-2 AI side, and whether
to write the estimator or adapt the authors' released code.

### S11. Hayek-criterion toy model — **CANDIDATE**
*Question:* where is the boundary at which an allocator beats a market, as a
function of observation bandwidth and re-solve latency?
*Method:* a small drifting economy; compare market tâtonnement against a learned
allocator while varying (a) how much of the state the allocator observes,
(b) how fast it can re-solve, (c) how fast the economy drifts. Locate the
crossover empirically.
*Standing on:* Liao/Gao/Kroer's nonstationarity measure (the drift budget),
Eisenberg-Gale convex structure (the tractable island), Nisan-Segal bounds (the
bandwidth benchmark).
*What it would let the paper say:* that the criterion is not merely stated but
*located* — with the honest note that a toy economy is not an economy.
*Open:* Matthew's argument that drift retires itself on hardware trends makes
the interesting axis the **endogenous** one — if the allocator's speed also
speeds up the economy, does the crossover move? Nobody has formalized this;
it is the most novel thing the model could show.

### S12. Negotiation simulation — **CANDIDATE (probably merges with S11)**
*Question:* do machine representatives that are less personally vulnerable reach
more mutually agreeable outcomes than human-style vulnerable ones?
*Origin:* V.5's embedded question, "can this or any of the other predictions be
demonstrated in simulation?"
*Method:* multi-agent negotiation over a shared resource with agents varying in
personal exposure to loss; measure joint outcome quality and dispute persistence.
*Note:* S11 and S12 plausibly share one harness — a drifting multi-agent economy
with a learned allocator/negotiator — which is the main argument for committing
to either.

### S13. Whole-system workload characterization — **NAMED PREREQUISITE**
*Question:* across the real consumer workload mix, what are achieved vs maximum
parallelism, dataflow locality, phase behaviour, and input statistics?
*Status:* named in the paper's limits as the missing map and the prerequisite for
pinning Figure 6's boundary. Larger than S8; S8 is its first slice.

### S14. Omerta utilization measurement — **FUTURE, phase 1.5**
*Question:* what utilization, demand and reliability distributions do donated
consumer devices actually show?
*Why:* S3's cost model turns on utilization, and the financing instrument in §8
cannot be priced without it. Matthew's prior expectation: low, but not as low as
lab machines.

---

## Work log

| Date | What ran | Result |
|---|---|---|
| 2026-06 → 07 | Paper built out from handoff; figures, structure, §12→Appendix A | 15pp two-column deliverable |
| 2026-07-20 | Structure and readability workflows (59 + 32 agents) | 27 + 14 fixes implemented |
| 2026-07-24 | RSI citation verification | §8 break-off argument fully sourced |
| 2026-07-27 | **S4** citation-faithfulness audit (50 Opus agents, all 129 refs) | 6 fixes; ~24%-PR claim sourced |
| 2026-07-27 | reviews.txt response pass | Table 1 → ranges; §2.1 rebuilt on the literature; `analysis/` created (**S3**) |
| 2026-07-27 | Cosmic AC outline v1 | Six movements; §9 dissolved inline |
| 2026-07-28 | Capital-cycle report integrated | IV.3 rebuilt; three-readings fork |
| 2026-07-28 | **S5** reading-list review, round 1 (51 papers) | Tiers + rationales |
| 2026-07-28 | **S6** citation-graph sweep (65 agents) | Drift leg found already formalized ×4 |
| 2026-07-28 | Reading directory assembled | 74 PDFs, nothing unobtainable |
| 2026-07-29 | **S5** round 2 (23 papers) + merge | All 74 on one scale; 5 round-1 re-tierings |
| 2026-07-29 | Bill Oliver clip investigated | Canadian not Australian; transcript pulled; Hansard not yet published |
| 2026-07-29 | **S10** designed and costed | ~$321/session at bulk API; $65 entry via Professional plan |

---

## Priorities, as I see them

1. **S10, now essentially free.** Tiers 1–3 cost nothing but compute, the corpus
   is already downloaded, and the method has a published anchor (Liang et al.).
   It produces an original figure and is the only study here that could stand
   alone as a short paper.
   The negative control is non-negotiable.
2. **S8**, because it is the paper's own committed first experiment and the only
   thing that converts §1.2's central inference into a measurement.
3. **S11+S12 merged**, if the criterion section is going to make a quantitative
   claim rather than a structural one.
4. S14 when Omerta phase 1.5 exists; S13 is the long-horizon version of S8.

## Open decisions

- S10: which detector, and subscription vs API pacing?
- S11/S12: commit as a fifth Appendix A effort, or leave as stated open questions?
- S9: Intel desktop for PIN-based tracing, or stay on the current machine?
