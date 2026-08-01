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

**Tier 2 — distributional estimation (free, the headline number).** Built on
**Liang, Izzo, Zhang et al., "Monitoring AI-Modified Content at Scale"
(arXiv:2403.07183)**. How it actually works, from the paper:

- It never classifies a document. It models the corpus as a **mixture**: each
  document is drawn from `(1−α)·P + α·Q`, where `P` is the human token
  distribution, `Q` the AI one, and **α — the fraction of the corpus that is
  AI-generated — is the single parameter being estimated** by maximising the
  corpus log-likelihood `Σ log((1−α)P(xᵢ) + αQ(xᵢ))`.
- **The vocabulary is adjectives only.** Every calculation depends solely on
  which adjectives appear in a document; the authors report this is more stable
  than adverbs, verbs, nouns, or all tokens (alternatives in their Appendix D).
  Their headline signal is a frequency shift in ICLR 2024 reviews — *commendable*
  9.8×, *meticulous* 34.7×, *intricate* 11.2× more likely per sentence.
- **`P` and `Q` come from reference corpora**, not from a model's internals:
  `P` from historical documents known to be human-written; `Q` by taking the same
  *writing instructions* given to the humans, prompting an LLM with them, and
  collecting the output. So the AI reference is generated under the real task's
  own brief.
- Their reported cost advantage is enormous — about **seven orders of magnitude
  cheaper than per-document detectors**, while reducing estimation error 3.4×
  in-distribution and 4.6× out-of-distribution.
- They give a **sample-size bound** (Theorem I.1): the error on α̂ shrinks as
  `1/√n` with an explicit constant depending on how separated `P` and `Q` are and
  on α itself. This is the piece that matters for any sampling design — see below.
- Applied result in their case study: **6.5–16.9%** of peer-review text at four
  2023–24 AI conferences was substantially LLM-modified, with corpus-level
  trends they note are too subtle to see per document.

*Mapping onto Hansard:* `P` = pre-2022 sittings from the same chambers; `Q` =
speeches generated by prompting a model with the actual bill text and the
speaking role (the legislative analogue of their "review instructions" trick);
α estimated per session, per chamber, per party, over time. Note their adjective
choice may not transfer — legislative register has its own adjectival habits —
so run their Appendix-D alternatives and pick on stability against the pre-2022
control, not on which gives the biggest number.

**Cost: zero.**

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

**Estimator — redesigned 2026-07-29 on Matthew's reframing.** He proposed
treating the question as *"what is the probability that a given piece of text is
flagged AI by Pangram?"* rather than fitting Liang's token-mixture model. That is
a better fit here, and it is standard survey sampling rather than a bespoke
likelihood.

*How Liang models the text, for the record (it is simpler than it sounds):* a
document is a **set** of adjectives, not a bag of counts (deliberately — unique
tokens grow sublinearly with length, so longer documents are not crushed;
they cite the coupon-collector intuition). Per-token occurrence rates are just
`p̂(t) = #documents containing t / #documents`, and the document likelihood is
**independent Bernoulli across the vocabulary**:
`P(x) = Π_{t∈x} p̂(t) · Π_{t∉x} (1 − p̂(t))`, and likewise `Q`. So it is naive
Bayes over adjective presence, with sentences as the unit. The independence
assumption is doing a lot of work, and the adjective vocabulary was tuned on peer
reviews — two reasons not to copy it wholesale into legislative register.

*Our estimator instead.* For a randomly drawn segment let `F = 1` if Pangram
flags it, and let `π = P(F = 1)` in some stratum. Then:

1. **`π̂ = k/n` is a binomial proportion.** Precision is exactly known — with
   n = 1,000 and a true rate near 5%, the 95% interval is about [3.8%, 6.5%];
   n = 2,000 gives [4.1%, 6.0%]. No modelling assumptions at all.
2. **`π` is instrument-dependent, so correct it.** What we want is the true rate
   `τ`, related by `π = τ·Se + (1−τ)·(1−Sp)` for detector sensitivity `Se` and
   specificity `Sp`. Inverting gives the **Rogan–Gladen prevalence estimator**,
   `τ̂ = (π̂ + Sp − 1)/(Se + Sp − 1)` — standard epidemiology for screening with
   an imperfect test (Rogan & Gladen, *Am. J. Epidemiology*, 1978 — **verify the
   handle before citing**).
3. **Both nuisance parameters are measurable in-domain, cheaply.** The pre-2022
   control *is* the estimate of `1 − Sp`, the false-positive rate on exactly this
   register — so the negative control stops being a sanity check and becomes a
   parameter. `Se` comes from generating known-AI legislative speech (Liang's `Q`
   trick: prompt with the real bill text and speaking role) and scoring it.
   Nothing here needs the vendor's published accuracy claims.
4. **Watch the correction's leverage.** Variance is amplified by
   `1/(Se + Sp − 1)`: about 1.06× at Se .95/Sp .99, 1.25× at Se .85/Sp .95. And
   when `π̂ < 1 − Sp` the point estimate goes negative — truncate at zero and
   report the interval, never the truncated point alone. At Se .90/Sp .97 a 3%
   flag rate corrects to ≈0%, which is the honest and important answer: at low
   true prevalence, a detector this good still cannot distinguish signal from its
   own error floor.

**Two-phase design — this is where Matthew's expand-from-samples idea becomes
principled.** Phase 1: run the free local detectors (Binoculars et al.) over the
*entire* corpus, giving every segment an auxiliary score. Phase 2: draw a
stratified sample on that score × year × chamber and pay for Pangram only there.
This is textbook two-phase sampling for stratification, and it has a property
worth stating plainly: **the free detector does not need to be accurate — only
correlated with the truth — to cut the variance of the paid estimate.** Its
errors bias nothing, because stratum weights are known exactly from the full
corpus. Expanding into a flagged speaker's other speeches is then the same
mechanism applied at the speaker level, which is also the only way to get
per-speaker estimates stable enough to report.

*Also handle:* segments within a speech or sitting are correlated, so use
cluster-robust variance (or the design effect `1 + (m−1)ρ`) rather than treating
segments as independent. Sample whole speeches as clusters.

*Cost at this design:* 2,000 segments of ~150 words is 300k words ≈ **$120** at
the bulk API rate, and **fits inside a single $65 Professional month**. Even
5,000 segments of 300 words (1.5M words) fits that month's allowance. The
corpus-sweep pricing below is now purely historical.

*Liang is out of the plan (decided 2026-07-29), kept as a reference only.* Its
mixture estimator is a good paper and the source of the `Q`-by-prompting trick we
still use, but running two estimators means defending two sets of assumptions,
and the corrected-sample design above is both simpler and better matched to the
instrument we actually trust.

*Session plan:* `plans/S10-legislative-ai-detection.md` — self-contained
starting point (detector survey, NB pilot, corpus search, throughput/batching).

*Pilot (2026-07-29, `analysis/s10/` + PILOT.md there):* full pipeline ran on
all 38 sittings plus a 6-sitting 2019 control. Three results. (1) Throughput:
Falcon-pair Binoculars scores the whole corpus+control (1.21M tokens) in
40 min on the GB10 — 509 tok/s end-to-end, and the GPU was discovered
clock-capped at 513/3003 MHz (fix needs root), so that is a floor with ~5.9×
headroom; Qwen3-1.7B pair runs ~2–3× faster. A 260M-token multi-legislature
sweep is overnight-to-days scale — the two-phase design stands. (2) Substance:
2025–26 raw flag rates sit BELOW the 2019 pre-ChatGPT false-positive floor
(2.85% vs 5.64% acc-threshold; 0.53% vs 1.03% low-FPR), so Rogan–Gladen gives
τ̂ = 0 with a rough upper bound ≤~0.5%; Tier-1 leakage regex: 0 hits in 993k
words (edited-record caveat). No detectable machine share via this
instrument — a null that is partly about the instrument (2023-era detector,
2026 text; Se unmeasured). (3) Design finding: the score distribution DRIFTS
between eras (2019 reads more AI-like than 2025–26), and the drift
REPLICATES across architectures (Falcon-7B and Qwen3-1.7B pairs, ρ≈0.73
agreement) — a property of the record, not the detector — so Sp/threshold
transport across eras is invalid — Se/Sp must be measured per era, add
within-era human anchors (spontaneous crosstalk), keep Pangram as the
second instrument. Bonus discovery: NB's two-column record puts language-as-
spoken in the left column, so speaker-authored English (709k words) separates
cleanly from translator-authored English — validated per speaker.

*Status:* pilot done; corpus + control archived with the pipeline in
`analysis/s10/`. Next: in-domain per-era `Se` corpus (highest value), the
detector survey (Task 1), prepared-vs-spontaneous labels, Pangram stratified
sample, Hansard Office request for the Bill Oliver sitting. Remaining
decisions unchanged: estimator code, and which model generates `Q`
(plausible-vintage, not necessarily 2026-frontier).

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
*Note:* S11, S12, and now S15 share one harness — a drifting multi-agent
economy with a learned allocator/negotiator and power asymmetries. Three
predictions, one build: the criterion boundary (S11), negotiation outcomes
(S12), and the four-horsemen prompt's effect on discharge paths (S15). This is
the strongest version of the case for committing to the simulator as the
program's fifth effort (open question 7).

### S15. The four-horsemen prompt — **CANDIDATE, buildable now**
*Origin:* the Arrow-clause thread (outline IV.3): the only way to avoid the four
horsemen is to negotiate with them; the audit is distributed instantiation.
*Artifact:* a standing background agent for anyone holding significant power —
monitors decisions/environment for accumulating structural pressure, notifies
with historical analogies (sources attached) and quantitative signals.
*Quantitative base:* instability forecasting works — Goldstone et al., AJPS 54
(2010), the PITF model (verified); ACLED-class event data.
*Validation:* backtest against documented historical decision environments
(pre-1789 fiscal records, pre-2008 risk memos): does it surface the pressure
before the discharge? Precision matters as much as recall — an alarm that
always fires is a jester nobody hears.
*Honest flags:* the memento-mori framing's classical sourcing is debated
(Tertullian; verify before use); a monoculture of auditors is the residual risk
— plurality of instantiations is the guard.
*Cost:* prompt + tooling ≈ free; backtest is archival work.
*Note:* cheapest item on this list after S10's regex tier, and the only one
that is itself an artifact of the paper's societal argument.
*Simulation link (Matthew, 2026-07-30):* prototypable and testable in the
S11/S12 societal simulator — seed a multi-agent economy with power asymmetries,
let extraction accumulate Arrow-clause pressure, equip a treatment group of
power-holders with the prompt, and compare discharge paths (reform vs revolt vs
collapse) against controls. The controlled counterfactual the backtest cannot
give: history runs once, the simulator reruns 1789 with the prompt installed.
Backtest and simulation cover each other's weaknesses (external validity vs
control).

### S13. Whole-system workload characterization — **NAMED PREREQUISITE**
*Question:* across the real consumer workload mix, what are achieved vs maximum
parallelism, dataflow locality, phase behaviour, and input statistics?
*Status:* named in the paper's limits as the missing map and the prerequisite for
pinning Figure 6's boundary. Larger than S8; S8 is its first slice.

### S14½ / S15. Staff-change detection via authorship drift — **CANDIDATE (side study, spun out of S10, 2026-07-29)**
*Question:* can stylometric changepoints in a member's **prepared** speech
detect documented staff turnover, using the member's **spontaneous**
crosstalk as the within-speaker control?

*Why:* it validates S10's authorship arm against ground truth that has
nothing to do with AI — and any AI-substitution claim made via style drift
must first rule out (or measure the signature of) ordinary staff change.
Standalone interest too: prepared text tracks the *office*, spontaneous
text tracks the *member* — V.3's "office is a socket," measured.

*Ground truth availability (assessed 2026-07-29):* ministers' and premier's
offices are reconstructible — GNB online directory lists ministers' office
staff (Wayback Machine gives dated snapshots), Public Accounts name-level
salary disclosures give annual diffs, chief-of-staff/comms moves get
reported by CBC NB. Backbench MLA staffing is mostly not public. Election
turnovers (the Oct 2024 government change) supply bulk known changepoints.

*Method sketch:* per-member monthly stylometric profiles, prepared vs
spontaneous streams scored separately (Burrows' Delta now; LUAR-class
embeddings as upgrade); changepoint statistic (e.g., CUSUM on
self-distance); power analysis first — members' statements are ~150 words,
so months aggregate into single points.

*Pilot evidence already in hand (`analysis/s10/authorship_delta.csv`):*
closed-set attribution 54.5% over 43 speakers (chance 2.3%) — signal
survives Hansard editing; Coon/Mitton rank 1 against their own profiles
across six years; **Austin ranks 34/43** (party + office change bundled —
first case study, confound and use-case in one).

*Needs:* the 60th-Legislature pull (2020–24) so more members span eras;
the staff-timeline scrape; prepared/spontaneous labels (S10's noisy
section tracker, upgraded).

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
| 2026-07-29 | **S10 pilot executed** — full pipeline on NB corpus + 2019 control; Falcon-pair Binoculars over 1.21M tokens; Qwen3-1.7B pair; Tier-1 regex | 509 tok/s e2e (GPU clock-capped 513/3003 MHz — see PILOT.md); 0 Tier-1 hits in 993k words; 2025–26 flag rates sit BELOW the 2019 false-positive floor → τ̂=0, rough bound ≤~0.5%; era drift in score distribution = the design finding |
| 2026-07-31 | **S10 quality arm** — DQI-anchored judging: Q1 lexical battery, Qwen pilot, Fable-5 blinded workflow v1+v2 (strict DQI + Steenbergen Commons anchors), corpus-wide per-year metrics | AI speech: 3× less first-person, formally stronger, worse-engaged; **blind Fable-5 AUC 0.936 vs Pangram**; v2 repeat-reliability at the published human bar; blinded 2019→2025-26: justification/evidence UP, respect-toward-demands −0.36, constructive −0.30 — form up, deliberation down |
| 2026-07-30 | **S10 Pangram adjudication** — 438 segs, Se/Sp both measured 1.0 in-domain (40/40 synthetic, 60/60 control; later extended to Sp 240/240 across five control years) | **τ̂ = 8.3% of 2025–26 segments pooled** [4.6–14.6] — superseded as the headline by the per-year series (see 2026-07-31 row): the pooled figure averages 4.3% (2025) with 13.6% (Jan–May 2026), so quote the year, not the pool; hits uniform across detector deciles (edited-AI invisible to zero-shot detectors — retro-explains all nulls); 68/218 candidates confirmed incl. McKee May-2023 cluster, Oliver, Sodhi, the Premier |
| 2026-07-29 | **S10** Fast-DetectGPT+LRR done; synthetic-leak bug caught+corrected; Tier-1.5 Wikipedia-signs lexicon; **S15 registered** | FD Se=0.975 both thresholds, corpus below floors (8 statistics, 0 elevations); Oliver specimen in FD tail; **AI-lexicon aggregate 3.31× (CI-separated)** — trend-shape test needs 60th-Leg pull |
| 2026-07-29 | **S10 detector trials** (PILOT.md addendum) — Qwen3-8B third pair; synthetic Se corpus (Mistral-7B-Instruct, 40 speeches); 3 classifiers (HC3-RoBERTa, RADAR, GPT-2-era); Burrows-Delta authorship; Pangram batch built | **Falcon pair Se=1.0/0.975 at calibrated 5%/1% FPR — bigger ≠ better** (Qwen3-8B 0.825/0.25; classifiers ≤0.675); 6 detectors, none lifts 2025–26 above its floor → bound ≤~0.4% at measured Se; authorship attribution 54.5% vs 2.3% chance, Austin cross-era anomaly; `pangram_batch.jsonl` 265 segs/52.6k words ready |
| 2026-07-30 | **Counsel cluster ranked** (27 papers + calibrator); 4 couldn't-get items obtained (Tessler main, Špecián, Kreps-Kriner, Alfani-WP) | 8/12/7 tiers; argument-ordered path + 6 side tracks; Fishkin demoted (facilitation ≠ counsel); Estlund = the shared-advisor defense |
| 2026-07-30 | V.3b recorded — **the trustworthy firm** (Matthew's text): preference-correcting bank, variable purchasing power, religious-institution iteration, universal-owner limit | Placed as fair-split twin of surveillance pricing; honest tensions logged (manipulation-adjacency; concentrates counsel → plurality guard) |
| 2026-07-31 | **Trustworthy-firm sweeps** (9-agent verify+graph; 6-agent what-changed) + reading directory | All V.3b anchors verified (3 handle corrections); markets-select-the-extractive-twin critique → the paper's own what-changed mechanism; what-changed evidence ASYMMETRIC: wedge-knowing overwhelming, wisdom-demonstrating the frontier |
| 2026-07-31 | **Trustworthy-firm shelf ranked** — 102 PDFs, two rounds (54+47 reviewers, 1 resume through session-limit reset); 2 calibrator hallucinations caught and reversed | 20/71/11 tiers; 18-step main path ends on Sharma sycophancy + Salganik ceiling; convergence result: three literatures independently select outcome-coupled incentives as the only surviving advisor design |
| 2026-07-31 | **S10 per-year prevalence** (calibrated, Pangram) — Se 40/40, Sp 240/240 across five control years, zero errors both ways | **0% (2019–22) → 4.0% (2023) → 4.0% (2024) → 4.3% (2025) → 13.6% (Jan–May 2026)** [2026 CI ≈ 6–27%, n=44] — accelerating, not plateauing. This is the citable series; the earlier pooled 8.3% is the same data averaged over a window that straddles the inflection. ITS slope change at the pre-registered 2023 break +23.7%/yr (placebo p=0.007) |
| 2026-08-01 | Paper: Brynjolfsson-Li-Raymond QJE 2025 added to §2.2.2 (tacit competence → copyable artifact, measured); F3/F4 twin block split into in-column figures | 20pp rebuild QA'd page-by-page; p8 gap eliminated; figures now sit at their references |

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

- S10: which detector, and subscription vs API pacing? (pilot answer: Falcon pair + Fast-DetectGPT sweep, Pangram adjudicates; batch ready)
- S15: Delta vs LUAR embeddings; staff-timeline sourcing depth (directory Wayback vs Public Accounts only)
- S11/S12: commit as a fifth Appendix A effort, or leave as stated open questions?
- S9: Intel desktop for PIN-based tracing, or stay on the current machine?
