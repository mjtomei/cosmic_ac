# Handoff — the appropriability collapse and the price of an externality

> **Renumbering note (2026-08-04, on intake):** this handoff proposed the
> study as "S16" and suggested `plans/S16-...` / `analysis/s16/`. S16 was
> already assigned (enterprise idle fleets, with committed history under
> that name), and the S15 double-assignment the handoff flags was resolved
> the same day (S15 = four-horsemen; staff-change stays S14½). **The study
> is registered as S17**; artifacts live in `analysis/s17/`. Read "S16"
> below as S17 throughout. Otherwise the handoff is preserved as received.

**For:** a fresh Claude Code session in `mjtomei/cosmic_ac`.
**Origin:** claude.ai dialogue, 2026-08-04 — an extended pass through Arrow 1962/1969
(missing markets, appropriability, exclusion, universality, the date-zero economy),
Samuelson 1954 rivalry, and the participation-constraint literature. Suggested home:
`plans/S16-appropriability-and-externality-pricing.md`.

**Read first, in this order:** `CLAUDE.md` (conventions and the source ledger) →
`outline-cosmic-ac.md` §IV.3 (the Arrow clause, the three readings of the capital
cycle) and §V.5 (the Hayek criterion, four legs) → `reading/notes/arrow-1969.md` and
`reading/notes/samuelson-1954.md` → `studies-and-work-log.md` (study register). The
new material attaches to all four and is not free-standing.

**Hard constraint carried from CLAUDE.md:** Matthew wants the Cosmic AC outline worked
*together*, not autonomously. Do not restructure the outline, renumber sections, or
insert paper prose from this document without him. What this session should produce is
the study, the analysis artifacts, the verified citation set, and *proposed* text —
staged for his review.

---

## 1. The thesis to be built

Two curves, moving in opposite directions, driven by the same underlying capability.

**Curve A — the private return to producing a non-rival good is collapsing.**
Appropriability depends on how long and how completely the producer can hold a lead.
Both terms are falling: machine intelligence drives the cost of independent
reproduction toward zero, and the existence of a near-substitute at zero price caps
the price of the original at the *differential* value rather than the total value.

**Curve B — the social value of the same good is rising.** Non-rivalry means value
scales with the number of users; the population of users (human and machine) is
growing, and the paper's own thesis is that shared optimization compounds.

**The wedge between them is the quantity to measure.** That wedge is not new — Arrow
1962 named it, and it is what the paper's §2.1 already calls a public-goods failure.
What is new is that it is *widening measurably and fast*, and that the widening is
caused by the same force the paper says will provision the commons.

**The second half, and the reason this is not just a lament.** The historical reason
positive externalities went uncompensated was measurement cost: you cannot pay a
producer for value you cannot attribute. Arrow's 1969 taxonomy of transaction costs
(exclusion, information/communication, disequilibrium) makes the information leg
explicit. Sensing and attribution costs are now falling by orders of magnitude. So the
same capability that kills the *sales* market for non-rival goods creates, for the
first time, the machinery for a *compensation* market — paying for positive
externalities rather than only taxing negative ones, which is the asymmetric case the
Pigouvian literature has largely left alone.

**The synthesis to argue:** the market for non-rival goods does not disappear. It
migrates from sale to compensation. Arrow's 1962 conclusion — that information goods
require nonmarket institutions — finally acquires the measurement layer it never had.
That is the mechanism under reading (c) in IV.3 (the bubble as down payment on a
post-scarcity society): the arithmetic "fails in money" because the good is ceasing to
be sold and beginning to be compensated, and money is the unit of account for the
former.

**The punchline that makes it a section rather than a complaint:** Nordhaus measured
innovator capture at ~2.2% of social surplus. The prize is not defending the 2.2%. It
is the 97.8%. A compensation channel that captured even a tenth of it would dwarf the
sales channel it replaces.

---

## 2. The formal skeleton — extend Nordhaus, do not invent

This satisfies the repo's standing rule (build on published work; do not argue
novelty). The model already exists, with a published parameterization, and it has
exactly the two knobs the argument needs.

**Nordhaus (2004), "Schumpeterian Profits in the American Economy: Theory and
Measurement," NBER WP 10433.** Innovators capture ~**2.2%** of total social surplus
from innovation over the 1948–2001 US nonfarm business sector. The decomposition is
the load-bearing part and is what to extend: a low **instantaneous appropriability
rate (~7%)** combined with a **depreciation rate on Schumpeterian profits (~20%/yr)**.
Capture share rises in appropriability α and falls in depreciation δ.

**The extension:** δ is the reciprocal of the imitation lag, and the imitation lag is
now directly measurable for the sector this paper is about. Recompute the capture
ratio with measured δ.

**The 1981 baseline to recompute against — Mansfield, Schwartz & Wagner, "Imitation
Costs and Patents: An Empirical Study," *Economic Journal* 91(364):907–918,
doi:10.2307/2232499.** Verified: across 48 product innovations in chemicals, drugs,
electronics and machinery, imitation cost averaged **~65%** of innovation cost,
imitation time **~70%** of innovation time, **~60%** of patented innovations were
imitated within four years, and patent protection raised imitation cost by only
**~7%** (Levin et al. 1987: 7–15%). This is the pre-machine-intelligence anchor. The
study below is Mansfield recomputed for frontier AI capability.

**Modern δ, measured (Epoch AI, all verified 2026-08-04):**
- GPT-3 → OPT-175B open replication: **~23 months**.
- Epoch's Nov 2024 open-models report: lag "centers around one year."
- Jan 2023 – Oct 2025, Epoch Capabilities Index: open-weight frontier lags closed
  frontier by an average of **~3 months** (~7 ECI points).
- Jan – May 2026: **~4 months** (~8 ECI points) — a modest widening, not a reversal.
- Frontier capability runnable on a single consumer GPU: **6–12 months** behind.

Read as δ: roughly 0.5/yr in 2020–22 rising to ~3/yr in 2025–26, against Nordhaus's
postwar 0.20/yr. That is the number the section turns on.

**Honest counters that must appear in the same breath** (repo convention, and each is
real):
- Epoch's own caveat: open-weight models score worse on private than public
  benchmarks — trained to the test — so the measured lag understates the true one.
- Labs withhold their most capable models, so the closed baseline is the *published*
  frontier, not the actual one. Epoch flags this as inferential.
- The 3→4 month move is a widening. The series is short and noisy; do not draw a
  clean exponential through it.
- α is not obviously collapsing everywhere. Complements — distribution, integration,
  trust, data, and the physical supply chain — are where appropriation migrates
  (Teece's appropriability regimes are the right frame). The claim is about the
  artifact, not about the firm.
- Bessen & Maskin (2009): where innovation is sequential and complementary, imitation
  *raises* total innovation. This is a friendly result, but it means "unprofitable"
  must be stated as "unprofitable to sell," not "unproduced."

**Where this closes a loop already in the repo:** `assets-rents-socialized-buildout.pdf`
concludes the AI valuations require *durable moats* because no plausible GDP share
otherwise closes the gap. The Nordhaus recomputation measures the moat depreciation
rate directly and finds it rising. Those are the same claim approached from two sides,
and stating the pair explicitly is what makes this material structural to IV.3 rather
than a bolt-on. Matched-pair convention already in use there (Arrow supplies the
pressure, Samuelson the machine) — this is a third pair.

---

## 3. S16 — the study

**Numbering flag:** the register currently assigns **S15 twice** (the four-horsemen
prompt, and staff-change detection via authorship drift, spun out of S10 as "S14½ /
S15"). Resolve that before adding S16.

**S16. The Mansfield ratio, recomputed.**

*Question:* how far has the imitation lag for frontier capability fallen since
Mansfield measured it in 1981, and what does that do to Nordhaus's capture ratio?

*Method:*
1. Build the lag series. For each frontier capability release, find the date the first
   open-weight model reached parity on a fixed benchmark set. Sources: Epoch AI Models
   database and Benchmarking Hub (ECI is CC-BY and their analysis code is published),
   Artificial Analysis, LM Arena, developer-reported results. Report on at least two
   independent metrics so the result does not rest on ECI alone.
2. Build the cost-ratio series where public numbers exist — cost to reach parity
   (distillation and post-training runs with published budgets) over cost to create.
   This is the direct Mansfield analogue. It will be sparse and vendor-reported; flag
   accordingly and prefer ranges to point estimates.
3. Re-solve Nordhaus's capture equation over the observed δ range, holding α at his 7%
   and then sweeping α down, producing a capture-ratio surface. The headline is a
   single number: the AI-sector capture ratio implied by measured imitation lags,
   against Nordhaus's 2.2% postwar benchmark.
4. Negative control, in the S10 spirit: run the same lag computation on a domain where
   machine intelligence is *not* the imitation mechanism (a conventional
   manufacturing or pharmaceutical class, from the patent-imitation literature) and
   show the lag has not collapsed there.

*Artifacts, per the `analysis/` convention:* `analysis/s16/imitation_lag.csv` (series
with per-row source and metric), `analysis/s16/nordhaus_recompute.py` →
`capture_ratio_grid.csv` (equations written out, assumptions in the script header,
sources for every number not derived). One figure candidate: the two curves — capture
ratio falling, social surplus per innovation rising — on one axis, with the wedge
shaded. Conceptual elements labelled as such in the caption, per repo rule.

*What it lets the paper say:* that the collapse in appropriability is measured rather
than asserted, on the sector the paper is about, using the same model that established
the postwar baseline.

*Honest limit to state:* capability parity on benchmarks is not economic
substitutability. A four-month lag on ECI does not mean a four-month lag in enterprise
willingness to pay. The gap between those two is the real frontier here and the study
cannot close it.

---

## 4. The externality-pricing half

**Structural move that makes this fit the paper: externality pricing is the Hayek
criterion with a different objective.** V.5's four legs transfer directly, and using
them is what keeps this from being a new framework:

1. **Bandwidth** — sense the externality. This is the leg that is collapsing.
2. **Computation** — attribute it to sources. Inverse modelling and source
   apportionment; the compute-bound leg, and where ML enters.
3. **Elicitation** — get truthful valuation. Samuelson's false signals; the
   Clarke/Groves-Ledyard demand-revealing answer and its known fragilities. Still hard.
4. **Tracking** — re-price as the economy drifts. Same latency race as V.5.

Stating it this way also inherits V.5's scope decision: the criterion takes preferences
as given, and the axiological gap is handled where it natively lives.

**Anchors to verify and build the cost series from:**
- **The canonical case where measurement created a market:** Title IV SO₂ allowances.
  Continuous emissions monitoring is what made the allowance tradable. Ellerman et al.,
  *Markets for Clean Air*; Schmalensee & Stavins, *JEP* 2013 retrospective. Get the
  per-unit monitoring cost and its share of program cost.
- **Satellite methane** as the modern order-of-magnitude case: per-km² screening costs
  now quoted around $1–2/km² against OGI programs at roughly $4,200/site/yr. **Both
  numbers are vendor-sourced (Bridger Photonics, an industry cost-comparison site) and
  must be replaced with primary or peer-reviewed figures before use.** Peer-reviewed
  starting points: the single-blind controlled-release validation in *Scientific
  Reports* (2023) on satellite detection and quantification accuracy, and the
  Permian tiered top-down analysis in *Renewable and Sustainable Energy Reviews*
  (2023) which models OGI survey costs explicitly.
- **The counter that must be carried:** CRS (IF12072, 2025) states plainly that
  top-down satellite and aircraft measurement currently costs *more* than bottom-up
  emissions-factor estimation. The cheap historical option was the *inaccurate* one.
  The honest claim is that the cost of an *accurate* externality estimate is falling
  fast, not that measurement was ever the binding cost of a bad one.
- **Low-cost sensing** generally: reference-grade air monitors against sub-$1k
  sensors (EPA Air Sensor Toolbox for the performance caveats, which are substantial).

**The three counters that bound the whole claim, and none of them are technological:**

1. **Measurement does not produce agreement on valuation.** The social cost of carbon
   is the demonstration: emissions are measured precisely and the official US central
   estimate still moved from ~$51 (IWG 2021) to ~$190 (EPA 2023), because the
   disagreement is about discount rate and equity weighting. Nordhaus vs Stern is the
   canonical version. Cheap sensing closes the information leg and leaves elicitation
   and the axiological leg exactly where they were. Verify both figures before use.
2. **Goodhart, at the level of the sanction.** Any measured contribution metric becomes
   the optimization target the moment it is load-bearing. Attribution of value to
   contributions in a commons is the Shapley problem, which is #P-hard in general and
   approximated in practice — that approximation is the attack surface.
3. **Who runs the estimator.** This is already a live thread in the repo. The
   Samuelson notes (Addendum 3) establish that surveillance pricing and university
   financial aid are the *same mechanism* with different governance and different
   destinations for the surplus, and that acceptance turns on those two things rather
   than on the mechanism. Externality compensation is that same estimator pointed at
   positive externalities. Say so — it is the cleanest available statement of why the
   aggregation-point governance constraint in IV.4 (open, user-verifiable, or it
   recreates the moat) is not optional.

---

## 5. Proposed placement — for Matthew's decision, not for unilateral edit

- **The appropriability collapse → IV.2/IV.3.** It supplies the economic mechanism
  under "the commons wins," which currently rests on the fitness argument (variation,
  selection, inheritance) in §5.1 of the finished paper. Fitness explains why commons
  persist; the collapsing capture ratio explains why the alternative stops paying.
  Pairs directly with the capital-cycle report's durable-moats requirement.
- **The externality-pricing machinery → V.5**, as the criterion applied to a second
  objective. It costs little space because the four legs are already built there.
- **The synthesis (sale → compensation) → IV.3's reading (c) and the conclusion.**
  This is what earns the post-scarcity reading the paper says it will earn at the end.
  Keep the no-forward-reference convention: the foreshadow in IV.3 stays one sentence.
- **One line for II.3.** §2.1 already predicts that machine intelligence "attacks every
  input of market formation at once — verification above all." The externality half is
  that prediction instantiated on a second class of missing market. A single sentence
  there, pointing forward without a section number, is probably all it needs.

---

## 6. Conventions this session must obey

From `CLAUDE.md` and `notes.txt`:

- **Build on published work; do not argue novelty.** State an absence at most once,
  quietly, and never rest an argument on it. Nordhaus, Mansfield, Arrow, Samuelson,
  Ellerman are the authors who got there first; the contribution is recomputation with
  new data, not a new framework.
- **Verify every web fact before it enters the text**, attribute by author and venue
  inline, keep the References section in sync. Everything in this document marked
  verified was checked on 2026-08-04; everything else is a lead.
- **Every novel number gets an artifact in `analysis/`** with computations written out,
  sources for anything not derived, and assumptions documented.
- **Reading notes go in `reading/notes/`**, one file per work, structured as Matthew's
  notes → the literature that answers each → the text changes motivated. If this
  session reads Arrow 1962 or Nordhaus 2004 properly, they get notes files.
- **Voice for paper prose:** confident and plain; no defensive hedging, no
  self-congratulation. Honest caveats stay, framed as frontiers. `notes.txt` holds the
  specific prohibitions (no em dashes, no rule of three, no corrective negation, no
  landing sentences, and so on) — those apply to paper text, not to internal documents
  like this one.
- **Figures:** rasterize and view after every rebuild. Never reintroduce
  `column-span: all` in `render_twocol.py`.

---

## 7. Verification queue

Verified 2026-08-04, safe to build on:
- Nordhaus 2004, NBER WP 10433 — 2.2% capture; ~7% initial appropriability; ~20%/yr
  depreciation of Schumpeterian profits; 1948–2001 US nonfarm business.
- Mansfield, Schwartz & Wagner 1981, *EJ* 91(364):907–918, doi:10.2307/2232499 —
  imitation cost ~65%, time ~70%, 60% imitated within four years, patents +7% to
  imitation cost; Levin et al. 1987 gives 7–15%.
- Epoch AI lag series: ~3 months (Jan 2023–Oct 2025, ECI, ~7 points), ~4 months
  (Jan–May 2026, ~8 points), GPT-3→OPT-175B ~23 months, consumer-GPU lag 6–12 months,
  plus Epoch's own private-benchmark and withheld-model caveats.

Not yet verified — do not insert without checking:
- Social cost of carbon figures ($51 IWG 2021, $190 EPA 2023) and the exact scenario
  each refers to.
- All methane and sensing cost figures. The two currently in hand are vendor-sourced.
- Ellerman et al. and Schmalensee-Stavins monitoring-cost numbers.
- Bloom, Schankerman & Van Reenen (*Econometrica* 2013) spillover magnitudes; Jones &
  Summers social-return ratios; Cohen, Nelson & Walsh (2000) appropriability survey.
  Each is a plausible supporting anchor; none has been checked here.
- Shapley-approximation and data-valuation literature for the attribution claim.

---

## 8. Open questions for Matthew

1. Does the appropriability collapse go in IV.2/IV.3 as economic mechanism, or does it
   want its own subsection? It is arguably load-bearing enough for one.
2. Is S16 worth running before S8 and S10, or does it wait? It is cheap — the Epoch
   data is public and CC-BY, and the recomputation is an afternoon — which argues for
   doing it now, but it competes with the register's stated priority order.
3. How hard should the compensation-market claim be pitched? The V.5 calibration
   (possibility argued from mechanism, timing left open) is the obvious template, and
   the same whether-to-when framing applies.
4. Does the externality half want its own study — measuring the cost curve for
   externality estimation the way S16 measures the imitation lag — or does it stay a
   structural argument carried by cited anchors?

---

## Execution addendum (2026-08-04, this repo — not part of the received handoff)

**Framing correction (Matthew, 2026-08-06), overriding §1's "sensing and
attribution costs are now falling" wording:** "It's not the price of measuring
intelligence that is falling. It's the price of intelligence itself. So that
makes things like the impossibly complex accounting possible." The falling
input is general intelligence; attribution (Arrow 1962's "unimaginably complex
and subtle" accounting) is one of the things it buys. The argument itself was
also recentered 2026-08-06 — see `plans/S17-proposed-text.md` v2 §0 for
Matthew's four-leg statement; this handoff's §1 thesis is the earlier framing.

The study ran the same day. Status of the plan above:

- §3 (the study): **done as S17** — `analysis/s17/` holds
  `nordhaus_recompute.py` → `capture_ratio_grid.csv`, `imitation_lag.csv`
  (two ECI-independent metrics included), `imitation_cost_ratio.csv`,
  `negative_control.md`, the figure, and a README with the honest limits.
  Headline: capture 2.2% → ~0.15–0.19% at 2023–2026 measured lags (11–15×),
  α held at Nordhaus's 0.07. Nordhaus read in full:
  `reading/notes/nordhaus-2004.md` (the paper never prints its capture
  formula — see the notes for how the recompute handles that).
- §7 verification queue: **all resolved** — outcomes in
  `analysis/s17/externality_anchor_verification.md` (SCC both figures
  verified with a mandatory framing correction; SO2 7% share verified with
  quote, the per-unit dollar figure NOT FOUND — dropped; Sherwin
  controlled-release is AMT 2024, performance only, never costs; CRS IF12072
  verified, title corrected; EPA sensor guidebook verified verbatim) and in
  `analysis/s17/negative_control.md` (pharma flat 13.5→14.1 yr; fab flat
  ~4 yr; no modern Mansfield replication exists). Two corrections to §2's
  verified list: the "23 months" framing is Cottier/Rethink Priorities
  (Epoch's own measurement is BLOOM at 25 months), and Epoch's verbatim
  wording is "a lag of about one year," not "centers around one year."
- §5 (placement) + §1's synthesis: staged as proposed text only, in
  `plans/S17-proposed-text.md`, per the work-it-together rule. The outline
  is untouched.
- §8 open questions: 2 resolved by events (it was indeed an afternoon);
  1, 3, 4 remain Matthew's, restated at the end of the proposed-text file
  with the verification's answer to 4's factual half.
