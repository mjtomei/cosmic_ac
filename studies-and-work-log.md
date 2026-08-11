# Studies and Work Log

Register of every empirical effort behind the paper — done, committed, and
candidate — plus a dated log of what has actually been run. Companion to
`outline-cosmic-ac.md` (argument structure) and `analysis/` (data and models).

Convention carried from `analysis/README.md`: **every novel number gets a
reproducible artifact** — a script, a CSV, or a documented workflow — with
sources for anything not derived here and assumptions written down.

Register scope (tightened 2026-08-04): studies only — efforts that produce a
number or artifact the paper stands on. Meta/process passes (citation audits,
literature rankings, structure reviews) are good practice, recur per study, and
live in the work log, not the register. Numbering is permanent: retired or
renumbered entries leave gaps rather than shifting later numbers.

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

*(S4–S6 — citation-faithfulness audit, reading-list ranking, citation-graph
sweep — retired from the register 2026-08-04 as meta/process work; numbers stay
reserved. Full entries in git history; runs in the work log; the audit ledger
in `CLAUDE.md`; rankings and sweep artifacts in the reading directories.)*

### S7. Development-velocity measurement — **DONE elsewhere, cited**
*Source:* `~/claude-work/project-manager/docs/velocity-analysis/`.
*Use:* §6 and Appendix A, with the honest asterisk that defect rate rises as
output outpaces review.

---

### S8. Dataflow-multicore in gem5 — **PARKED (2026-08-05: merged into S9's framing; FPGA target first)**
*(2026-08-05, Matthew: S8 and S9 are the same study — two target architectures
for one continuously-optimizing intelligence. The FPGA target (S9) goes first;
the gem5 arm and the rung-0 ideal-ASIC limit are parked — the limit "is not
well defined yet although I think there is something there." The S8 plan file
keeps the shared related-works ledger.)*
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
*Session plan:* `plans/S8-dataflow-multicore-gem5.md` (2026-08-05) —
related-works pass done (6 agents, all anchors web-verified), three-phase
methodology drafted, open decisions listed. Positioning finding: every piece
of the mechanism exists published (TaskMiner, T4, Carrefour, ADWS, ninja gap);
what is unmeasured is the composite end-to-end gap on ordinary code and its
automatic recovery — a quantification + composition claim, not novelty.

### S9. Continuous FPGA acceleration by machine intelligence — **ACTIVE (reframed 2026-08-05; absorbs S8's aims)**
*Question:* can an LLM fully replace a human engineer at the standing task
"always watch what is running on this processor and accelerate pieces of it
as efficiently as possible" — on an attached FPGA fabric?
*Reframing (2026-08-05, supersedes the old soft-core-specialization entry,
kept below for history):* three modes, all in scope — (1) LLM-driven use of
existing tooling (the toolchain's complexity is itself the bottleneck);
(2) LLM hand-designing RTL/HLS in measurement loops; (3) the intelligence
optimizing its own optimization loop, QoR as fitness. Historical anchor: warp
processing (Vahid & Lysecky, mid-2000s) — transparent profile-guided
hot-code-to-fabric, which worked and died of exactly the collective-action
gap the paper diagnoses. Applications: tier 1 = datacenter-tax kernels as
controls; tier 2 = the below-ISA-extension-threshold long tail (the thesis
case). Hardware: Matthew's Zybo Z7 (Zynq-7000: profile on the A9 PS, offload
to the PL).
*Session plan:* `plans/S9-fpga-continuous-acceleration.md` (self-contained;
citation-graph pass 2026-08-05).
*Honest flags:* the 2012-era Cortex-A9 baseline is weak — report relative
gain from autonomy, and energy, never implying 1:1 transfer to modern CPUs;
FPGA is ~20–35× off ASIC so absolute efficiency claims stay off the table;
selection caveat carries over from the old entry.
*(Old S9 entry, for history: RISC-V soft core, profile-guided
specialization, open-flow re-place — subsumed as one possible tier-2
mechanism rather than the study's frame.)*

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
τ̂ = 0 at the pilot's sensitivity (bound in `analysis/s10/`); Tier-1 leakage regex: 0 hits in 993k
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

### S14½. Staff-change detection via authorship drift — **CANDIDATE (side study, spun out of S10, 2026-07-29)**
*(Numbering note, 2026-08-04: this entry briefly carried "S15" as an
alternate label while S15 was also assigned to the four-horsemen prompt.
Deduped: S15 = four-horsemen (the label the work log and S11/S12 notes
already use); this study keeps S14½.)*
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

### S16. Enterprise idle fleets as a federation substrate — **CANDIDATE, scoped**
*Origin:* Matthew, 2026-08-02, from an Apple ad claiming >80% of top companies
use Macs: business machines left plugged in at offices overnight should be a
more reliable federation resource than household devices, with owners
(businesses) rationally incentivised to sell idle capacity.
*Status:* desk research done — `analysis/enterprise-idle-fleet/` (57 findings,
primary sources only). **Finding: the premise is half right and the wrong half
is the laptop half — laptops go home (80% of docks empty after hours), desktops
stay (~64% left on).** ~41M business desktops idle overnight in US commercial
buildings (derived); businesses pay ~24% less for electricity than households;
harvesting costs ~$0.003/hr. Against: EU/ENERGY STAR mandate sleep-as-shipped,
Wake-on-LAN is narrower than folklore, endpoint policy gives IT a refusal, and
hybrid work removes the good hardware from the building.
*The measurement worth making:* nobody has repeated the after-hours census since
LBNL-53729 (2004), which predates modern sleep defaults, the laptop shift, and
hybrid work. What fraction of business machines are powered and reachable
outside working hours in 2026 is **unmeasured**, cheap to measure on one
organisation's fleet, and publishable alone. Would directly harden §4 and the
Omerta plan's supply assumptions.
*Do not use:* ">80% of the Fortune 500 use Macs" — Apple's actual claim is 84%
of LinkedIn's 50 top US employers, i.e. 42 of 50, with "at scale" undefined.

### S17. The Mansfield ratio, recomputed — **REGISTERED 2026-08-04, in execution**
*Origin:* claude.ai dialogue 2026-08-04 (Arrow 1962/1969, Samuelson 1954,
appropriability); handoff at `plans/S17-appropriability-and-externality-pricing.md`.
*(Arrived numbered "S16"; renumbered S17 — S16 was already the idle-fleet study,
and the S15 double-assignment was deduped the same day: S15 = four-horsemen,
staff-change stays S14½.)*
*Question:* how far has the imitation lag for frontier capability fallen since
Mansfield, Schwartz & Wagner measured it (EJ 1981: imitation time ~70% of
innovation time, ~60% imitated within 4 years), and what does the measured lag
do to Nordhaus's 2.2% capture ratio (NBER WP 10433: a≈0.07, λ=0.20/yr imposed
from patent renewals)?
*Method:* (1) open-vs-closed frontier lag series from Epoch AI (ECI) plus at
least one ECI-independent metric; (2) sparse imitation-cost-ratio series where
budgets are public (distillation runs vs frontier training cost), vendor
numbers flagged; (3) re-solve the capture ratio over measured λ (~0.5/yr in
2020–22 → ~3/yr in 2025–26), sweeping α; (4) negative control: a domain where
machine intelligence is not the imitation mechanism (generic-drug entry lags),
showing no collapse there.
*Artifacts:* `analysis/s17/` — `imitation_lag.csv`, `nordhaus_recompute.py` →
`capture_ratio_grid.csv`, wedge figure. Reading notes:
`reading/notes/nordhaus-2004.md`.
*Honest limits (registered with the study):* benchmark parity ≠ economic
substitutability; Epoch's private-benchmark and withheld-model caveats mean
the measured lag understates the true one; the 2025→2026 3→4-month move is a
widening — no clean exponential; α migrates to complements (Teece) rather than
collapsing everywhere — the claim is about the artifact, not the firm;
Bessen-Maskin 2009 means "unprofitable to sell," not "unproduced."
*Placement (proposed, Matthew decides):* IV.2/IV.3 economic mechanism; pairs
with the capital-cycle 2e report's durable-moats requirement (same claim from
two sides). Externality-pricing half: V.5 as the criterion pointed at a second
objective — whether it gets its own study is an open question below.

### S18. AI capital stock, rents, and rent location — **CANDIDATE**
*(Carried as unnumbered "Sx" until 2026-08-04; assigned S18.)*
*Question:* what is the deployed AI capital stock, what rent stream has the
market capitalized against it, and what external revenue must arrive for the
pricing to hold?
*Findings:* ~$1.08T gross / ~$1.16T net stock vs ~$18T AI-attributable market
gain; sector Q 15–23×; required external revenue 3–6.5% of world GDP (breakeven
floor ~$1.7T/yr) vs ~0.3% today; rents ~85–90% mean-reverting supply-chain
scarcity; rent-location precedent (railroads/fiber: riders profit, network
capital doesn't) inverts the market's allocation, and July 2026 was the first
mass repricing toward history's allocation without any aggregate crash.
*Artifacts:* `analysis/capital-cycle/` (ai_stock.py, gdp_req.py,
build_report_v2.py, VERIFICATION.md), `assets-rents-socialized-buildout-2e.pdf`.
*Honest flags:* AI-attribution shares and add-ons are authors' estimates;
several 2e figures rode on a flagged secondary source — the load-bearing ones
(10-K depreciation inventory, Moody's, Bain, mileage, ton-mile) re-anchored to
primaries 2026-08-04 (`analysis/capital-cycle/VERIFICATION.md`), the rest
pending; market-value attribution ($18T vs $27T) follows Goldman's own caveat.

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
| 2026-07-29 | **S10 pilot executed** — full pipeline on NB corpus + 2019 control; Falcon-pair Binoculars over 1.21M tokens; Qwen3-1.7B pair; Tier-1 regex | 509 tok/s e2e (GPU clock-capped 513/3003 MHz — see PILOT.md); 0 Tier-1 hits in 993k words; 2025–26 flag rates sit BELOW the 2019 false-positive floor → τ̂=0 at pilot sensitivity; era drift in score distribution = the design finding |
| 2026-07-29 | **S10** Fast-DetectGPT+LRR done; synthetic-leak bug caught+corrected; Tier-1.5 Wikipedia-signs lexicon; **staff-change study registered** (then labeled S15; renumbered S14½ in the 2026-08-04 dedupe) | FD Se=0.975 both thresholds, corpus below floors (8 statistics, 0 elevations); Oliver specimen in FD tail; **AI-lexicon aggregate 3.31× (CI-separated)** — trend-shape test needs 60th-Leg pull |
| 2026-07-29 | **S10 detector trials** (PILOT.md addendum) — Qwen3-8B third pair; synthetic Se corpus (Mistral-7B-Instruct, 40 speeches); 3 classifiers (HC3-RoBERTa, RADAR, GPT-2-era); Burrows-Delta authorship; Pangram batch built | **Falcon pair Se=1.0/0.975 at calibrated 5%/1% FPR — bigger ≠ better** (Qwen3-8B 0.825/0.25; classifiers ≤0.675); 6 detectors, none lifts 2025–26 above its floor → bound ≤~0.4% at measured Se; authorship attribution 54.5% vs 2.3% chance, Austin cross-era anomaly; `pangram_batch.jsonl` 265 segs/52.6k words ready |
| 2026-07-30 | **S10 Pangram adjudication** — 438 segs, Se/Sp both measured perfect in-domain (synthetic AI legislative speech; pre-2023 controls, later extended across five control years) | Corrected prevalence estimated for recent speech and superseded by the per-year series (2026-07-31 row). **Figures live in `analysis/s10/` and are still moving — do not quote a number from this log while the study is open.** hits uniform across detector deciles (edited-AI invisible to zero-shot detectors — retro-explains all nulls); 68/218 candidates confirmed incl. McKee May-2023 cluster, Oliver, Sodhi, the Premier |
| 2026-07-30 | **Counsel cluster ranked** (27 papers + calibrator); 4 couldn't-get items obtained (Tessler main, Špecián, Kreps-Kriner, Alfani-WP) | 8/12/7 tiers; argument-ordered path + 6 side tracks; Fishkin demoted (facilitation ≠ counsel); Estlund = the shared-advisor defense |
| 2026-07-30 | V.3b recorded — **the trustworthy firm** (Matthew's text): preference-correcting bank, variable purchasing power, religious-institution iteration, universal-owner limit | Placed as fair-split twin of surveillance pricing; honest tensions logged (manipulation-adjacency; concentrates counsel → plurality guard) |
| 2026-07-31 | **S10 quality arm** — DQI-anchored judging: Q1 lexical battery, Qwen pilot, Fable-5 blinded workflow v1+v2 (strict DQI + Steenbergen Commons anchors), corpus-wide per-year metrics | AI speech: 3× less first-person, formally stronger, worse-engaged; **blind Fable-5 AUC 0.936 vs Pangram**; v2 repeat-reliability at the published human bar; blinded 2019→2025-26: justification/evidence UP, respect-toward-demands −0.36, constructive −0.30 — form up, deliberation down. **SUPERSEDED 2026-08-10: the "deliberation down" half was genre.** With genre or chamber fixed effects the engagement dimensions go null in both the 840-segment genre-balanced pool and the 682-segment cross-chamber pool, while the form dimensions strengthen; the original run's own two group-pairs already disagreed in sign on respect-toward-demands (−0.356 vs +0.650). Revised claim and evidence: `analysis/s10/S10-WRITEUP-DRAFT.md` §4.9; superseded headline logged at Appendix B item 5. Do not cite this row's engagement figures. |
| 2026-07-31 | **Trustworthy-firm sweeps** (9-agent verify+graph; 6-agent what-changed) + reading directory | All V.3b anchors verified (3 handle corrections); markets-select-the-extractive-twin critique → the paper's own what-changed mechanism; what-changed evidence ASYMMETRIC: wedge-knowing overwhelming, wisdom-demonstrating the frontier |
| 2026-07-31 | **Trustworthy-firm shelf ranked** — 102 PDFs, two rounds (54+47 reviewers, 1 resume through session-limit reset); 2 calibrator hallucinations caught and reversed | 20/71/11 tiers; 18-step main path ends on Sharma sycophancy + Salganik ceiling; convergence result: three literatures independently select outcome-coupled incentives as the only surviving advisor design |
| 2026-07-31 | **S10 per-year prevalence** (calibrated, Pangram) — sensitivity and specificity both perfect in-domain, controls spanning five pre-2023 years | Prevalence is flat and at the control floor through 2022, inflects after 2023, and rises steeply through early 2026 — accelerating, not plateauing; interrupted-time-series slope change at the pre-registered 2023 break is significant against placebo. **Current point estimates and CIs: `analysis/s10/PROGRESS-REPORT-*.md`. Study open — do not quote figures from this log.** |
| 2026-08-01 | Paper: Brynjolfsson-Li-Raymond QJE 2025 added to §2.2.2 (tacit competence → copyable artifact, measured); F3/F4 twin block split into in-column figures | 20pp rebuild QA'd page-by-page; p8 gap eliminated; figures now sit at their references |
| 2026-08-02 | **S10 teaching-grade methodology write-up** (`analysis/s10/METHODOLOGY.md`) — every number's provenance, the reasoning behind each design choice, and what each figure does and does not license | Written for a reader new to this kind of analysis; paired with an adversarial review sourcing published comparators (`METHODOLOGY-REVIEW.md`) |
| 2026-08-02 | **S10 per-chamber Pangram calibration** (Ireland/Canada/UK, uniform random — no screen stratification, so plain design-based estimates) | **Specificity 1.0 replicates outside NB: Canada 60/60 and Ireland 60/60 pre-2023 controls all Human.** Canada prevalence 17.5% AI / 26.7% AI+Mixed on the 120–360w band |
| 2026-08-02 | **Segment-length confound found and corrected** — the chamber samples used a 120-word floor excluding 46% of segments, and flag rate rises steeply with length (Canada 11.1% at 120–199w → 22.6% at 280–360w) | Measured the excluded 50–119w band rather than extrapolating: Canada short band **2.5%** vs long band 17.5%. Corpus-weighted Canada = **10.6% ± 4.3 segment-weighted, 14.0% ± 5.3 word-weighted**. NB's sample was already length-representative (16% short vs 13.9% in pool), so **NB 7.5% and Canada 10.6% are indistinguishable — the uncorrected 7.5%-vs-17.5% gap was a sampling-frame artifact** |
| 2026-08-02 | **S10 US corpus** — GovInfo CREC, 330 stratified sitting days. API route abandoned (DEMO_KEY caps at ~40 req/hr); the content endpoint needs no credential, so the sitting-day oracle is the zip's own status code | Extractor drops **Extensions of Remarks** (written insertions, never spoken — the largest US-specific contaminant) and Daily Digest; House and Senate run as separate corpora; `congMember` gives bioGuideId + party + state, so within-speaker is exact rather than surname-matched. Residual revise-and-extend contamination is flagged, not solved |
| 2026-08-03 | **S10 protocol v1.1** (adversarial-review round 1 applied): present-in-both restriction + dispersion-matched placebos; mechanism test WITHDRAWN (predictor was 92% a rarity index — verified independently); citation fixed (Lause, not Berens) | Effect sizes halve; Fisher 2.4e-7 → 2.9e-6 over five chambers (US House +0.104 sig., US Senate real null on 24M words); House-vs-Senate = within-country institutional contrast |
| 2026-08-04 | **S10 round-2 review found the fatal flaw**: the placebo null does not control for TREND. In-time placebos (pre-LLM window pairs) return excesses equal to the real effect at p<0.001 in UK/IE/CA; estimator check (odd/even split) ~0, so the drift is real and secular | Every lexicon p-value demoted to descriptive. Kobak's own trend-break counterfactual then run on a rebuilt 20-year UK corpus (2006-2026): fires on COVID 2020-21,**null on 2024/2026** — no break at LLM arrival. Lexicon arm retired as an AI instrument |
| 2026-08-04 | **The trajectory finding** (Matthew's RLHF-mirror hypothesis): split Kobak list by instruct-over-base preference (paired generation, no Hansard data). Frequency-matched halves: RLHF-preferred words diverged from matched controls +0.25 across 2006-2019, then PLATEAUED (+0.01 across 2019-2026) | LLM output as a measure of pre-existing human preference direction; preference tuning selects the register humans were already drifting toward. Alignment experiments: instruct models over-produce Kobak style vs own base (+0.88 pooled Qwen3/Mistral; OLMo ladder: SFT +0.76, DPO +0.86, RLVR +0.37 — accrues every stage, preference heaviest, placebo stage not null) |
| 2026-08-05 | **S10 corpus-likelihood instruments retired**: full-trace instruct-vs-base delta null in 3 families; word-position variant (Matthew's design, self-normalised, no placebo words) is the one that lands: **+0.0099 [+0.0007,+0.0196], P(<=0)=0.02, 9/10 family-chamber cells positive** | First contextual permeation evidence: phrasing around register words drifts toward the assistant; corpus-wide version stays null, so the drift is confined to register-word neighbourhoods |
| 2026-08-06 | **S10 exposure-gradient tests** (Coherence mechanism): US Congress drift vs home-state adoption NULL (with power: party covariate t=+3.4); then the clean version — 7 provincial Hansards built from scratch (BC/AB/SK/ON/MB/NS/NL, 259 members), StatCan 22-10-0034 adoption gradient | Registered spec −0.0045 [−0.0108,+0.0009] (wrong sign); growth spec null. **No dose-response on local adoption in either country.** Emergent: pre-LLM register drift +0.04..+0.09 in 6/7 provinces — the UK secular climb is continental. NB's own archive predates 2016 only (discovery chamber, least-preserved history) |
| 2026-08-07 | **S10 sixteen-chamber panel built**: 8 Canadian provinces + 6 Australian states (203.6M words) + Scotland/Wales/NI, each from its own archive with a bespoke extractor and a mandatory validation report | Decomposition: the register climb is **compositional**. Arrival premium (new members minus incumbents, same years) **+1.87 per 1,000, CI [+1.25,+2.49], positive in 15/16 chambers**, sign test p≈2.6e-4. Within-member change **not significant pooled** (−0.42, CI [−1.32,+0.49]) — the honest form is "incumbents flat, arrivals higher", not "incumbents declined" |
| 2026-08-07 | **Member biographies collected** (1,396 provincial members, 79% birth-year coverage via Wikidata/enwiki) → the cohort regression | **Birth decade +0.93 (t=+12.0), rising to +1.06 with occupation and education controlled.** Candidate professionalisation and educational expansion REFUTED: communications backgrounds −0.67, law −1.67, post-secondary −0.53 — all the wrong sign. Cohort not age: chamber age flat (52.2→51.4) while register rises, and mean birth year advancing 13.8 yrs predicts +1.28 of the observed +2.06 (~60%) |
| 2026-08-08 | **The onset is observed**: UK Commons extended to **1985–2026** (10,006 sitting-day files) | Register **declines** 1985–1994 (−18.97/yr, minimum 593 in 1994), then reverses: +31.64 (1996–2005), +42.22 (2006–2016), +28.26 (2017–2026). Placebo flat across all 41 years. **Inflection at 1994–96 = mass consumer internet; the transformer era is the slowest-growing rising period.** A pre-existing secular trend is ruled out — it was falling before the web |
| 2026-08-08 | **Mechanism still unidentified**: cohort × province-adoption interaction **+0.09 (t=+0.97)** — later-born members from early-adopting provinces drifted no more than same-age members from late-adopting ones | Third null on isolating computer exposure specifically (after the US-state and province gradients). Defensible claim is **generational, mechanism unidentified**, ambient computing leading on timing alone. Isolating it needs province of FORMATION, which the biography data lacks |
| 2026-08-08 | **Third and final exposure test**: member birthplaces collected (Wikidata P19, 70% coverage; **34% serve a province other than their birth province**, half foreign-born across 34 countries) — the right geography at last | Pre-committed spec A (birth-province adoption during the member's own age-15-25 window): **−0.40, t=−1.00 — null and wrong-signed**. Spec B looked significant (t=+2.20) until inference was clustered on the 10 birth provinces: **CI [−0.22,+0.33]**, 23% of resamples ≤0. Second occurrence in this study of unclustered inference on a province-level regressor manufacturing a result that flattered the hypothesis. Cohort effect unmoved throughout (+1.02..+1.22, t≈11-12). **Stopping here: three dose-response nulls; further proxies not worth running** |
| 2026-08-04 | **Capital-cycle report 2e integrated** — models + generator into `analysis/capital-cycle/`, PDF rebuilt in-repo, primary-verification pass (10-K depreciation inventory, Moody's, Bain, mileage, ton-mile) via web agents | 2e in repo root; outline-IV.3 edits STAGED as `plans/capital-cycle-2e-integration.md` (not applied — work with Matthew); verification results in `analysis/capital-cycle/VERIFICATION.md`; Stansberry [28] never-cite rule recorded |
| 2026-08-04 | **IV.3 worked with Matthew** — three-record precedent, rent-location bullet (July 2026 as dated case study), socialization additions, deflation clock, Arrow-clause "discharge already running" | Decisions ledgered in `plans/capital-cycle-2e-integration.md`; composition point placed in the Britain record; legibility cross-link in |
| 2026-08-07 → 08-09 | **Endogenous-socialization thread worked with Matthew** — non-rivalry inversion, wanting/absorption, mindshare-vs-resources, the legal layer. Five Opus verification passes: non-rivalry anchors + prior art; capability-vs-Moore's-law; agriculture commons; weights/capability IP (three agents incl. peer-session work); 2026 open-weights policy | Staged as `plans/endogenous-socialization-proposal.md`; evidence in `analysis/capital-cycle/NONRIVALRY-ANCHORS.md` and `analysis/commons-precedents/{agriculture,weights-ip}.md`. **Key results:** Arrow 1962/Romer/Teece verified verbatim; the copyleft-inversion argument is **already published** (Henderson & Lemley, 100 Ind. L.J. 1327) — cite, don't claim; only the crash-vs-copy inversion, the weights≈germplasm framing, and "no right attaches to capability" came back unclaimed. **No AI provider has ever sued over distillation** (Musk conceded it under oath; no claim followed) — enforcement is termination + lobbying. Agriculture: TFP ×2.84 while terms of trade fell to 35%; the extension system **built** the farm lobby (Olson, correcting the Populism arc); OSSI abandoned copyleft over propagation, not enforceability. **Corrections applied:** capability-vs-Moore's-law is ~1.6–2×/yr extra multiplier, not an order of magnitude (Gundlach et al. is the flag to cite ourselves); the US open-weights "exemption" is from a *voluntary, unpublished* review; the industry split is over remedy scope, not open-vs-closed (OpenAI is on both sides) |
| 2026-08-06 | **Recognition half-life measured** (`analysis/capital-cycle/recognition_halflife.py`) — era asset mixes × lives from primaries (ICC/Fishlow/Ulmer; FCC SOCC + FCC 99-397; EDGAR verbatim: WorldCom/Qwest/Williams/Level 3) via Opus agents | Railroads: **never** (betterment accounting, 100% storable; mandates 1907/1943/1983; receivership restructured claims, not assets — 18.2%/20.4% mileage peaks corrected in report+outline). Telecom: ~8–10y as booked, booked slow (fiber 40→25 restated; WilTel 21→15; GX 17.9% depreciated when impaired 74%); recognition = the 2001–04 impairment waves ($2T figure re-attributed Economist→Powell; GX capex corrected to ~$9.7B audited). AI: **3.5y** on its own schedule — the first buildout whose accounting clock outruns its bubble. Proposed IV.3 clause pending Matthew |
| 2026-08-04 | **Register overhaul** (Matthew): S8/S9 COMMITTED → CANDIDATE, deferred — econ work first for the time being; meta/process entries retired (S4–S6, numbers reserved); Sx assigned S18; entries reordered numerically (S16/S17 moved up from below Priorities); priorities rewritten; stale S15 labels fixed to S14½; work-log rows date-sorted | Old versions in git history; Appendix A's committed-program framing in the paper left as is — revising it is a separate decision |
| 2026-08-05 | **S8 related-works + methodology pass** (6 web agents: in-repo citation inventory, limit studies, task runtimes/NUMA, dataflow architectures, auto-parallelization history, gem5 norms) | `plans/S8-dataflow-multicore-gem5.md` written (self-contained). Key facts: gem5 NUMA feasible via CHI+Garnet (CXL-DMSim template, 3.4% silicon-validated); FS mode non-negotiable; GB10 is the right host (Arm KVM needs aarch64 — verify /dev/kvm); trace-driven limit study is the least-effort credible dataflow arm; T4/TaskMiner/Gupta-Sohi are the position-against set; ISPASS-2009 96%-coverage-behind-rare-dependences is the dynamic-information anchor; venue corrections recorded (ADM=Yoo/ASPLOS, Kremlin=PLDI, Speedup Stacks=ISPASS) |
| 2026-08-05 | **S8 methodology reformulated** (Matthew): ideal-ASIC limit study — unlimited area under a power budget with energy-costed ops/transfers, ML-assisted placement+scheduling with a self-improving optimizer loop → constraint-project onto the gem5 architecture → evaluate → target gaps. Anchors verified (1 web agent, primary PDFs) | Plan §3 restructured (ceiling/projection/targeting; gap stack as central figure; bound conservative by construction; optimizer generations = F6's commons-maturity axis, measured). Novelty verdict: no prior unlimited-area, power-budgeted, distance-costed ideal-ASIC bound for general-purpose programs — the unprovided term is wire energy under optimized placement (Aladdin has no placement; Timeloop is affine-only; TDG bounds specific designs). Energy constants pulled from primaries (Horowitz 45nm, Keckler 40→10nm wire 240→115 fJ/bit/mm, Dally 14nm 100 fJ/bit-mm); CACTI 7 frozen at 32nm — extrapolation needed. Same day, sequencing pinned (Matthew): rung 0 = no memory, no instruction-delivery cost — pure computation placement/scheduling, the perfect-specialization (same-app-same-input) bound; program = limit + reproductions of published architectures (dsa-framework, SwarmArch candidates), then converge the two by adding realism rungs to the bound and improvements to the architectures. Floor discipline sharpened (Matthew): Hong-Kung I/O bounds don't count cross-operation reuse (weights-stationary residency pays them zero) — floors must match each rung's machine class; universal floor = op energy + compulsory I/O only. Rungs split into constraints (only hurt) vs resources (only help); "which workloads pull a RAM into the optimal mapping" named a result target |
| 2026-08-05 | **FPGA-first pivot** (Matthew): S8+S9 unified — dataflow multicore and FPGA are two target architectures for one continuously-optimizing intelligence; FPGA first (mature tooling absorbs P&R; Zybo Z7 in hand). S8 gem5 arm + rung-0 limit parked; S9 reframed as "LLM fully replaces the human at continuous profile-and-accelerate"; new plan `plans/S9-fpga-continuous-acceleration.md`; 4-agent citation-graph pass launched (warp-processing lineage, datacenter-tax slate, LLM-for-hardware SOTA, Zybo feasibility) | Pivot rationale: end-user analysis (datacenter tax ~30% of fleet cycles; below-ISA-threshold long tail as the thesis case) plus warp processing as the on-thesis precedent — it died of the collective-action gap the paper names |
| 2026-08-05 | **S9 related-works pass completed** — 4 agents landed (warp-processing citation graph from primary PDFs; datacenter-tax slate; LLM-for-hardware SOTA; Zybo feasibility); plan rewritten integrated | **Verified open gap: arXiv "hardware/software partitioning"+"LLM" = zero results; no published system closes the full warp loop (continuous profiling → selection → LLM synthesis → on-board validation → self-improvement)**; nearest neighbors HLSPilot (ICCAD 2024) and ContractHIL-HLS (2026 preprint, PYNQ). Warp verified: 6.3×/66% (TODAES 2006), CAD 1.2s/3.6MB; four walls (amenability/toolchain/selection/economics) all judgment bottlenecks. Tax corrected to 22–27%; flatness data (6.3% hottest function, 353 for 80%, "sea of accelerators"). Feasibility: Vivado x86-only → FEX-Emu path (2026 fixes) + x86 fallback; openXC7 0.9.x timing landed, aarch64-native; PYNQ 3.0.1 community image; board self-measures power (IMON→XADC). Baseline discipline: NEON 4–8×, A9 ~30–40× below modern core, VTA 2.1–5.3× is the calibrated expectation |
| 2026-08-05 | **S9 profiling track started** (`analysis/s9/profiling/`) — harness on the GB10 (py-spy installed+smoke-tested, gprof path, coarse anchors), tier-1 kernel anchors on real repo data (90MB s10 JSON), `candidates.csv` seeded | gzip -9 ~21 MB/s and xz ~3 MB/s single-thread (classic FPGA targets); sha256 ~2.3 GB/s via host ARMv8 crypto vs A9 which predates the extension — a natural above/below-threshold pair on our own hardware; JSON ~235 MB/s (bridge kernel, no deployed accelerator). perf blocked (`perf_event_paranoid=4`; unlock = `sudo sysctl kernel.perf_event_paranoid=1`) — needed for tier-2 discovery on arbitrary binaries |
| 2026-08-05 | **S9 refinements** (Matthew): LLM failure modes = first work item, not blockers (frontier models + possible project-manager-tool orchestration); board = Z7-20; profiling reframed as an **intelligent grounded whole-system observer** (VM-grade, LLM-driven — a third novel artifact) — prior-art sweep launched (continuous profiling/GWP, CoreSight/Intel PT, QEMU introspection/PANDA, LLM+monitoring). Reading collection created: `~/reading/automatic-hardware-specialization/` (README + reading path in house style; 2 fetch agents downloading ~45 PDFs) | Observable-twin pattern sketched: workload runs emulated on the GB10 where everything is visible, ground truth measured on the Zybo |
| 2026-08-05 | **S9 observer sweep + reading shelf complete** — whole-system-observation prior art verified (3 passes); 47/47 PDFs fetched into `~/reading/automatic-hardware-specialization/` (manifests A/B, none paywalled-only) | **Second unclaimed niche confirmed: no published system has an LLM continuously holding low-level whole-machine observation and closing the optimize/offload loop** (ECO = offline/source-level; SchedCP = scheduler-only; AIOps agents = curated APIs, 11% success; HLSPilot = one-shot). Three-tier observer designed into the plan: QEMU observable twin (record/replay + TCG plugins + queryable execution store — the store and trace-diffing are themselves unbuilt primitives) → gem5 ordinal timing → Zybo ground truth (A9 PMU TMA-lite + **PTM→ETB CoreSight trace, mainline-wired; TPIU→EMIO→PL = the FPGA capturing its own CPU's instruction stream**). Key precedents: PIE (gem5 as LLM oracle), COZ (counterfactual epistemology), PANDA (record-once-replay-many) |
| 2026-08-05 | **S9 stack nailed down** (Matthew: open-source HLS preferred; soft-core hooks endorsed as novelty source) — plan §5½; toolchain verification agent confirmed | **Flow: Bambu (primary HLS; Nane TCAD-2016: matched/beat commercial wall-clock at ~1.3× LUTs; aarch64 build untested → week-1 item) + Dynamatic dataflow arm + openXC7 (timing *analysis* landed, P&R not timing-driven) + GenZ + PYNQ/DFX; Vivado-under-FEX = reference track. Profiling: 3 instruments → one queryable execution store — always-on perf/TMA-lite+PTM snapshots; QEMU observable twin (covers both ISAs); instrumented VexRiscv (plugin architecture + FormalPlugin/RVFI verified; 2K LUTs full+MMU; Linux via LiteX, PS7 in-tree; openXC7 demos already include ps7+vexriscv).** Novelty scoped: FirePerf/TIP/ABACUS+LegUp-2011 are prior art (LegUp even did profiler→partitioning); claim only the conjunction — deployed soft core + instruction/memory-stream hooks + fully open flow + automatic decisions + observer co-designing its sensors |
| 2026-08-05 | **S9 topology flipped** (Matthew: GB10 profiling can't close the loop) — the Zybo is the watched machine (A9 = realistic subject, full armhf userspace; instrumented VexRiscv = invasive subject, rv32 Linux via Buildroot — python3/zstd/openssl/git/ssh all packaged; NO Node/V8 on rv32 so the agent stays on the GB10 and SSHes in); GB10 = observer's machine (agent, toolchain, QEMU twin, execution store); GB10 profiling demoted to bootstrap scouting | Soft core runs the non-GPU workload mix in kind, not scale (~100–300× per-core deficit → scaled inputs; A9 ~10× the soft core); NaxRiscv rv64 flagged as unverified upgrade path |
| 2026-08-05 | **S9 daily-driver + Claude-Code-on-RISC-V checks** (1 agent, primary sources) | Soft cores ARE daily-driven where the core is the point: Precursor/Betrusted (VexRiscv on Spartan-7 — inspectability, "evidence-based trust in silicon" quotes pulled), Somlo's self-hosting Fedora/Rocket workstation (rebuilds own bitstream on itself), Vampire V4/MEGA65; never on performance grounds. Framing: our observability = optimization-side twin of Precursor's security-side inspectability. Claude Code: rv32 = verified impossible (no Node target, V8 rv32 deprecated, QEMU 32-bit hosts dropped, box64 64-only); rv64 = demo-possible (Debian Node 20 + pinned ≤2.1.100 JS release; current releases are x64/arm64 native binaries). Agent-on-GB10 + SSH confirmed as the design |
| 2026-08-05 | **S9 rv64 soft-core check** (Matthew: why not 64-bit?) — verified viable with margin on the SpinalHDL path | NaxRiscv RV64IMASU 17.9K LUT @137MHz (-3), **Debian riscv64 demonstrated at 100MHz on -1-grade Artix-7**; VexiiRiscv (successor, LiteX `--cpu-variant=debian` RV64GC) is the trial target — rv32-linux config only 3.35K LUT; CVA6 confirmed too big (~55–60K); Rocket fits but 25MHz. Debian trixie riscv64 official (RV64GC baseline — FPU mandatory), 1GiB headless fine, **Node 20.19 ships riscv64** → Node workloads under invasive observation possible on rv64. armhf safe through trixie. Decision rule in plan: week-1 trial synthesis, ≤25K LUT @ ≥50MHz → VexiiRiscv rv64 becomes the invasive subject |
| 2026-08-05 | **S9 topology settled A9-primary** (Matthew): rv64-size question resolved — the published cores are big because they're *performance* designs, not because of the ISA (Vexii rv64i base = 2.16K LUTs; the real adders are ~1.5–2× datapath + the D-FPU that Debian's lp64d ABI and V8's JIT mandate; rv32's 2K figure rides soft-float Buildroot). Phase 1: A9 = watched machine (PMU + PTM trace; TPIU→EMIO→PL sustained-capture block = build item), fabric spent on accelerators; Claude-Code-on-A9 = cheap experiment (armhf Node 20.19 verified in trixie + pinned ≤2.1.100 JS release; 1 GiB vs 4 GB wall); agent-on-GB10/SSH stays the working config. Phase 2: instrumented soft core when memory-stream visibility earns its area — week-1 Vexii rv64gc trial synthesis prices it in advance | Soft core's unique capability precisely scoped: memory-address/value streams — the one thing neither the A9 nor any hard CPU of that era exposes |
| 2026-08-05 | **S9 soft core decided** (Matthew): minimal rv64 — VexiiRiscv smallest Debian-capable RV64GC config; week-1 trial synthesis validates rather than decides; NaxRiscv → rv32 VexRiscv only as fallback ladder. **Radar added: Thompson's evolvable hardware** — verified same day (ICES 1996/LNCS 1259; 32-cell clockless core; "five" disconnected cells is Davidson's New-Scientist number, not the paper's; ~10°C window, ~7% *region*-transfer degradation). Key recovery: **Thompson & Layzell ICES 2000 solved the fragility — worst-of-four-chips fitness across foundries/temps → robust on six unseen chips at −50°C**; design principle recorded: the portability envelope must live inside the fitness function or the search sells whatever isn't varied. 9 PDFs added to the shelf (incl. Evolved Radio, Haddow-Tyrrell 2011 post-mortem, Wright Nature 2022 echo); field arc: ICES dead after 2014, intrinsic line stalled | Plan §5¾; ties to rung-0 per-input specialization vs deployment robustness |
| 2026-08-06 | **Reading collection assembled: `~/reading/the-price-of-thought/`** (S17 v2's shelf — the ledger / captured protections / credit economy / the estimator); 15 direct fetches + 12-agent Opus fetch workflow; leg-4 prose corrected per Matthew (the falling price is intelligence itself, which is what makes Arrow's "impossibly complex" accounting possible — correction recorded in proposed-text §4 and the handoff addendum) | 26 verified PDFs incl. Machlup 1958 scan, BPEA 1987 official, Eldred brief, Boldrin-Levine full book (cite by chapter), Hemphill-Sampat SSRN-version flag, Mansfield-1985 image-only flag; **3 gaps need library pulls: Mansfield 1981 (namesake — no OA copy exists), Dasgupta-David 1994 (embargoed), Deng-Papadimitriou 1994**; README with per-item provenance; notes/ symlinked to repo |
| 2026-08-06 | **S17 v2 — argument rebuilt per Matthew's correction** (not collapse-under-existing-metrics; the four legs: negative ledger under externality accounting / power abusing protective systems / right-to-think conditioned on market participation / open tracking intelligence as lowest-cost credit assignment); Arrow 1962 read in full (`reading/notes/arrow-1962.md`); 3 verification agents over the newly load-bearing anchors | All verified (`analysis/s17/v2_anchor_verification.md`): BSV 55/21 + LBV 57.7/13.6 + Jones-Summers $5–20/$1 (WP corrected to 27863); *Patent Failure* ~$12B costs vs ~$3B rents (contested — flag); quinolones DWL 13× the holder's gain; **Arrow signed the Eldred brief** (0.33% incentive, 224× DWL asymmetry, lost 7–2); Machlup p.80 exact; CNW framing corrected (copying still #1; strategic majorities + horse-trading quote is the defensible form); Elsevier STM 38.4% computed from RELX primary; Merton verbatim; Shapley phrasing corrected (#P-complete weighted-majority, not "in general"); Epoch 9–900×/yr (not "1000× in 2 yr"); ASCAP sampling→census + BMI v. CBS founding-on-measurement-cost quote. Staged text v2 at `plans/S17-proposed-text.md` — outline untouched |
| 2026-08-07 | **S9 deep hunt: 9 of 13 missing works recovered** (13 Opus-medium agents, one per work; routes the shallow pass skipped — author theses, lab-wiki Wayback captures, repository OAI/REST APIs, linked code repos, SSRN, browser) | Shelf **157 PDFs**. Originals: NOVIA (MICRO 2021), Cayman (DAC 2025, author page), RACER (TACO 2025 CC-BY, + XRT sibling), Lahti HLS-QoR (green AM), Confucius. Alternates: Nair/Lysecky profiler → the two conference papers the TECS version merges (CASES'08 + DAC'09, from a Wayback capture of Lysecky's lab wiki), TraceDoctor → thesis Paper C, Sriraman Top Picks → PhD dissertation ch. VI (superset), Quickloop → SSRN preprint under a different title. Two IDs resolved (Quickloop truncation; the Confucius "companion" was a phantom — v1 title of the same arXiv entry). **Operational lesson: dl.acm.org 403 to scripts = bot-blocking, NOT paywall — ACM marks many MICRO/ISCA/TACO papers FREE ACCESS; check the landing page in a browser before declaring an ACM work unobtainable.** Outstanding 4 with verdicts: MicroBlaze warp TECS'09 (skip — DATE'05/TODAES'06 siblings carry it), AGI-Complete (free browser click gets the author's gold-OA ASPLOS'25 version), SmartNIC tax (nothing exists), Fleetbench (repo is the better artifact) |
| 2026-08-07 | **S9 shelf completed: every sweep-proposed work fetched** (12-batch Opus-medium workflow + index pass) | **144 PDFs** (was 72); `00-MANIFEST-D.md` covers the 72 additions with sources; 13 works unobtainable (ACM/IEEE paywalled — notably NOVIA MICRO 2021 *inline* accelerators, Nair-Lysecky TECS 2011 hardware profiler, MicroBlaze warp processor TECS 2009, Fleetbench ISPASS 2024, Cayman DAC 2025; RACER TACO 2025 is gold-OA but Cloudflare-blocked — retryable); 3 byte-identical duplicates removed; all new files page-size + title verified. **The D shelf is UNRANKED.** Notable haul given the same-day thesis correction: the in-pipeline reconfigurable-coprocessor lineage (PRISC MICRO-27 1994, Garp 1997, Chimaera 2000) — the ancestry of "optimize the core itself"; Morph SOSP 1997; the observer line past TIP (TEA 2023, DIP 2026); FarSlayer (turnkey legacy-software FPGA acceleration); Melnyk's self-improvable reconfigurable system (2013/2021); Yu & Wentzlaff "Area Bloating and the Future of Specialization"; Loyd 2025 bitstream evolution (modern Thompson descendant) |
| 2026-08-07 | **S9 thesis corrected: it's loop size, not the accelerator long tail** (Matthew: "I would be just as happy with a general purpose soft core getting optimized... And I'd also be happy just with identifying that if the NRE of an ASIC was zero, massive benefits would be possible"). New plan §0 defines three equal-success outcomes: per-app accelerators / **core-level optimization** (custom instructions, µarch retunes — better conditioned: LogCA in-pipeline break-even 128B vs 32KB on-die vs 256KB PCIe) / **zero-NRE counterfactual** (engineering-cost twin of the parked rung-0 ideal-ASIC bound). Tier 2 demoted from "the thesis case" to one instantiation; §7 gains loop-cost as the primary measured series (wall-clock, agent cost, interventions, iterations per accepted optimization, tracked as a trend) | Also settled: open-flow QoR inflation accepted — agent recovering headroom a weak free toolchain left IS the NRE-lowering result (paper §5.2's "ML breaches EDA", measured by our own loop); rule = headline speedups anchor to the commercial reference, gap-closing number reported alongside |
| 2026-08-07 | **S9 reframed on success criteria** (Matthew: not carving a conference niche — excel at best-in-class flow results, interesting optimizations/meta-optimizations, and daily use; overlapping work is good). Plan §3 reframed (neighbors = shoulders/comparators), §3.5 comparator set added (grouped by what they measure against), §4 gained the **sea-of-accelerators challenge + design response**; all 110 sweep-proposed works dispatched for fetch | The challenge, stated: LogCA (break-even granularity g₁ set by offload overhead — in-pipeline 128B vs on-die 32KB vs PCIe 256KB), Accelerometer (per-invocation cost makes flat-tail speedup negative), AccelSeeker (breadth-first small-leaf selection measured to fail), c-cores (per-function 0.96–1.15×, runtime +22%, energy-only win) all say the long tail is the *hardest* regime, not the opportunity. Response designed in: profitability gate computes g₁ before build; kernel **fusion** to raise C; phase-2 in-pipeline coupling is the 128B regime; energy term in fitness from day one; tier-1 controls prove the flow where offload is known to pay; "the tail is uneconomic at AXI/DMA coupling" accepted as a publishable finding |
| 2026-08-06 | **S9 shelf ranked + citation-graph swept** (90-agent workflow: 16-PDF part-C fetch, 72 Opus reviewers, 16 Opus sweep seeds, Fable calibrator; one session-limit interruption, resumed from cache) | Shelf now 72 PDFs; `00-RANKINGS.json` (18/51/3 tiers; 156 red flags — recurring: LogCA-class interface-cost math pressures the tier-2 "sea of accelerators" premise at AXI/DMA coupling, argues for in-pipeline hooks/fusion) + `00-CITATION-SWEEP.json` (**64 threat-flagged 2025–26 works — the agentic-hardware neighborhood is far busier than the 08-05 verification found**: A3D (Purdue, "closest to niche 1"), HSCO-Bench (real-FPGA deploy, erodes on-board-validation differentiator), AgRefactor/HLS-Seek/A2H-MAS (mode-2/3 neighbors), PRAGMA/KernelPro/AccelOpt (profiling-guided LLM loops on GPU/NPU/Trainium), Magellan/AI-PROPELLER (fleet profiles + evolved optimizer), Icicle (TMA on Rocket/BOOM, narrows niche 3), McDougall/Sankaralingam in-field introspection units, Morph SOSP 1997 (the standing task as OS service), Cayman/ISAMORE (non-LLM auto kernel selection). ALL API-level finds pending verification before positioning rewrites). Calibration: 4 tier promotions noted in README; Accelerometer PDF was the talk deck (re-fetch dispatched); 46 priority-1 shelf additions proposed |
| 2026-08-04 | **S17 registered and executed** — Nordhaus WP 10433 read in full (notes: `reading/notes/nordhaus-2004.md`), capture ratio re-solved over measured AI imitation lags (Epoch ECI + 2 independent metrics), cost-ratio series, negative control, externality anchors verified (3 web agents); register numbering deduped (S15 = four-horsemen, staff-change = S14½) | **Capture 2.2% → ~0.15–0.19% at 2023–26 lags (11–15×, α held at 0.07); uncaptured share 97.8% → 99.8%.** Negative control flat (pharma 13.5→14.1 yr; fab ~4 yr both sides of export controls); no modern Mansfield replication exists (reportable absence). Nordhaus's own §V predicted the direction. Artifacts `analysis/s17/`; proposed text STAGED `plans/S17-proposed-text.md` (outline untouched); vendor methane cost figures killed in verification; SCC 4× move NOT attributable to discounting alone — framing constraint recorded |
| 2026-08-09 | **S10 Pangram model-tier defect found and fixed.** The API's default model is Pangram 3 (v3.3.2); the web dashboard runs Pangram 4. A 20-segment check enriched for AI/Mixed agreed 11/20 across routes on the default and **20/20 with `model="pangram-4"`**. The 2026-07 NB tier-4 run passed no model and silently took P3. Billing confirms the split (web = 1 credit/100 words = P4 pricing; default API billed per document at P3's 1,000-word unit). API and dashboard are **independent pools** (44 API scans moved the dollar balance, left the 15,000 credits untouched). | `api_route_check.py`; routes interchangeable only when the model is named |
| 2026-08-09 | **NB rescored on Pangram 4** (658 segs, byte-identical stored text) | **Specificity unchanged — 60/60 on the pre-AI control on both models, 0% on Y-2020/21/22.** P4 is more sensitive: AI+Mixed 122 → 144, agreement 92%. The defect was an undercount, not a false-positive problem; earlier NB conclusions stand as conservative. `nb_p3_vs_p4.py` |
| 2026-08-09 | **Transcript-regime diagnostic** — words/sentence + contraction density per chamber-year, random-sampled | Policy scan named NSW/WA as ASR users; **the text says otherwise** — both flat 2006–2026. **Tasmania moved**: contractions 3.4 → 15.9 per 1k (+364%), step falling BETWEEN the windows, so no pre-AI text exists in its current regime. NL/WAL/MB step inside the control window → controls floored to the current regime in the builder. `transcript_regime_check.py` |
| 2026-08-09 | **S10 expansion, API portion** — 1,431 segs on Pangram 4 (658 NB rescore + 360 genre + 413 chamber controls) | **Specificity 593/593 across 8 new chambers** (AB, CA-FED, NSW, QLD, SA, TAS, VIC, WA), zero false positives; with the prior 423/423 that is 1,016/1,016. **Genre arm resolves the scripted-drafting question with the detector**: SO31 36.7% / Government Orders 23.3% / Oral Questions 8.3%, all six controls 0.0%; SO31 vs OQ 4.40×, Fisher p=0.00034 — the lexicon's inference now confirmed by an independent instrument. 2,827 files remain for the dashboard route. **Study open — do not quote from this log.** |
| 2026-08-09 | **Prior art logged** — Rice (Australian federal Hansard; Binoculars + Fast-DetectGPT + LLM scoring; null) and Pimlico Journal (UK Commons z-score; positive). Neither used Pangram. | `analysis/s10/PRIOR_ART.md`. Rice's reported ~8% FPR exceeds his detection rate, making the null underpowered rather than negative — the calibration argument, not a dismissal. Pimlico shares the family of the arm we demoted, so its agreement is not corroboration. **All figures unverified against primary sources.** |
| 2026-08-09 | **S10 Pangram expansion COMPLETE** — 4,258 verdicts on Pangram 4 across 19 chambers, 4 countries (1,431 Bulk API + 2,827 dashboard; routes verified equivalent 20/20 before mixing) | **Specificity 1,260/1,260 = 100% [99.7%, 100%]** — every chamber bought its own 60-segment pre-AI control and not one produced a false positive. In-domain Se = 1.000 (n=40 synthetic legislative speech), so calibrated prevalence = observed. **Pooled prevalence 12.4% [11.1%, 13.8%]** (2,220 segments, TAS excluded as regime-flagged). Range 3.3% (US Senate) to 23.3% (NSW). **Genre arm: SO31 36.7% / Government Orders 23.3% / Oral Questions 8.3%, all controls 0.0%** — 4.4x scripted-vs-unscripted, Fisher p=0.00034. Artifacts: `prevalence_report.py`, `pangram_p4_verdicts.csv`, `nb_p3_vs_p4.py`, `transcript_regime_check.py`, `PRIOR_ART.md`. **Study open — do not quote from this log.** |
| 2026-08-10/11 | **S10 bypass arm + verification close-out.** Four adversarial search runs across two chambers (461 rewritten variants of 130 Pangram-flagged originals): blind, contrastive, Opus-seeded, and a clean uniform-draw run. Plus quality stages 3-4 (63 paired DQI grades), the Opus effort A/B, and a primary-source pass on both prior-art comparators. | **Asking Opus to rework a speech in a loop beats the commercial evasion industry ~10x.** Per target (final search per chamber, >=1 variant reaching a clean Human verdict): **24.6%** [16, 36], 23.1% strict — against **2.31%** for the 13 humanizer services in Pangram's own report, i.e. **10.6x**, and 72x its clean-conditions FNR. No fine-tuning, no detector access, no evasion tooling. Like-for-like on single attempts the multiple is 3.7x (the 2.31% is one-shot, 24.6% allows <=18 attempts — state this whenever the 10x is used). Conservative per-variant rate **8.5%** [6.3, 11.4] by label, **8.0%** strict, all four runs. Both against **0 AI labels in 1,260** pre-AI controls. The two chambers agree (26.3%/22.2%) despite contradicting each other on which edits work — the rate transfers, the playbook does not. Evasion costs **no** deliberative quality (all 7 DQI dimensions null on both arms, length-adjusted), but is not cheap: it needs a frontier model, contrastive exemplars and multi-round search — a single "sound human" prompt *raises* the score. **Two corrections:** the "seed AI 22% vs Mixed 76%" claim does not survive (computed on a partial batch, and the two halves were different statistics; like-for-like Fisher p = 0.735 — the borderline-original hypothesis is now explicitly unestablished), and our answer to Rice rested on *his* invalid threshold-crossing comparison — the durable argument is sensitivity, not specificity. Rice verified: he diagnoses his own detector as blind (20% sensitivity) and must not be cited as evidence of absence. All nine † figures re-derived and reproducing; §4.9 rewritten; `bypass_report.py` is the new single source. |

---

## Priorities, as I see them

*(Rewritten 2026-08-04 for the econ focus; the earlier committed-program
ordering is in git history.)*

1. **The econ thread.** S17's capture-ratio result into the outline (placement
   staged at `plans/S17-proposed-text.md` — decide with Matthew, not
   autonomously), the capital-cycle 2e integration
   (`plans/capital-cycle-2e-integration.md`, same rule), S18's remaining
   verification debt, and S16's after-hours census — the one cheap original
   measurement in the thread.
2. **S10, open and essentially free.** The per-year prevalence series is the
   project's best original figure; the negative control remains non-negotiable.
   S14½ rides along on the same corpus.
3. **S11+S12 merged**, if the criterion section is going to make a quantitative
   claim rather than a structural one — and the S15 simulation link makes the
   shared harness the strongest version of that case.
4. **Architecture studies, when focus returns:** S8 first (it converts §1.2's
   central inference into a measurement), S9 second, S13 as the long horizon;
   S14 when Omerta phase 1.5 exists.

## Open decisions

- S10: which detector, and subscription vs API pacing? (pilot answer: Falcon pair + Fast-DetectGPT sweep, Pangram adjudicates; batch ready)
- S14½: Delta vs LUAR embeddings; staff-timeline sourcing depth (directory Wayback vs Public Accounts only)
- S11/S12: commit as a fifth Appendix A effort, or leave as stated open questions?
- S9: Intel desktop for PIN-based tracing, or stay on the current machine?
- S17: does the appropriability collapse go into IV.2/IV.3 as mechanism, or get
  its own subsection? How hard to pitch the sale→compensation claim (V.5's
  whether-to-when template is the obvious calibration)? Does the externality
  half become its own study (measuring the externality-estimation cost curve
  the way S17 measures the imitation lag), or stay a cited structural argument?
