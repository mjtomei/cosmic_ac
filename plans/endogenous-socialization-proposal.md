# Proposal: the non-rivalry / endogenous-socialization thread

**Status: PROPOSAL — nothing here has been applied to `outline-cosmic-ac.md`.**
Assembled 2026-08-09 from the 08-07/08-09 dialogue. Per the repo rule, staged
for Matthew to accept, amend, or reject. Every claim's verification status is in
`analysis/capital-cycle/NONRIVALRY-ANCHORS.md`,
`analysis/commons-precedents/agriculture.md`, and
`analysis/commons-precedents/weights-ip.md`.

Decisions already taken in dialogue are marked ⟨agreed⟩. Open decisions are
collected in §8; §7 holds the 2026-08-12 additions motivated by the Nvidia
credit event, kept separate so they review as a unit.

---

## 1. The core claim

Previous infrastructure buildouts socialized their capital only through **crash
and dispossession**: the asset was rival and appropriable, so society got cheap
infrastructure only when bankruptcy transferred ownership at distressed prices.
The AI buildout's durable output is **non-rival and copyable**, so it can
socialize **without any transfer of ownership and without a crash** — copying is
not dispossession. The pop, if it comes, is therefore caused by the technology
*working* rather than by demand failing, which inverts every precedent in the
section.

**Prior-art discipline (load-bearing — see §6).** The commoditization half of
this is **already published repeatedly** and must be cited into, not claimed.
Only the historical inversion came back unclaimed, and it should be presented as
a contrast drawn on top of published work rather than as a discovery.

## 2. The four legs

1. **Bubbles leave a legacy** — Perez, Janeway, Hobart & Huber. Already in the
   section. ⚠️ The specific sentence asserting *the crash is the mechanism* was
   **not verifiable** in either Perez or Janeway; carry that step on our own
   evidence instead (Global Crossing's reorganization value of ~1.3–2% of peak
   book assets after ~$9.7B of audited capex; dark fiber unlit until bankruptcy
   repriced it).
2. **The legacy is non-rival this time** — Arrow 1962, Romer 1990, Jones &
   Tonetti 2020. This is a **type distinction, not an analogy**, and should be
   written that way. Arrow's sentence does the work: "no amount of legal
   protection can make a thoroughly appropriable commodity of something so
   intangible as information. The very use of the information in any productive
   way is bound to reveal it, at least in part." **Matched pair:** the section
   already quotes Arrow 1969 for the pressure-toward-collective-action point;
   Arrow 1962 supplies the reason the value cannot be captured. Same author,
   both halves — state the pair explicitly.
3. **Innovators capture ~2.2% anyway** — Nordhaus. Converts the claim from a
   forecast about AI into the measured base rate. ⚠️ Cite the **working paper**
   (the 2.2% is in the conclusion; the published abstract says only "a minuscule
   fraction").
4. **The market already prices the distinction** — Björkegren (long-term bond
   yields shift in *opposite* directions following open vs closed releases);
   Borri, Liu & Tsyvinski (the AI equity premium loads on closed-source models
   and paying users, **not** on open-weight use). Moves the argument off theory
   onto a test someone else ran.

## 3. Why the rent cannot be collected — three independent mechanisms

All three are triggered by the technology succeeding, which is the unifying
observation and the section's best line of attack.

**(a) Non-rivalry.** §1–2 above.

**(b) Wanting saturates below the frontier.** ⟨agreed⟩ Matthew's argument,
carried by the coherence paper's §5 ("The bottleneck"): *"what would a person do
with a thousand competent workers ready to start now?… Today anyone with an API
key has it — and the median response is a freeze. The capability arrived; the
wanting did not."* Supported by the enterprise-pilot record — implementation
cost collapsed by orders of magnitude while measured end-to-end value stalled,
which is what a non-capability-constrained world looks like.

⟨agreed, Matthew's correction⟩ The bar is **not stationary** — the set of things
possible to want changes with capability. So the argument is *qualitative with a
rate comparison attached*, and must be labelled that way rather than dressed as
a measurement. The rate: effective compute per dollar for a fixed capability
improves at roughly **3×/year** — hardware ~1.37×/yr times algorithmic
efficiency ~1.75–2.8×/yr — genuinely faster than Moore's law, but by ~1.6–2×/yr
of extra multiplier, **not an order of magnitude**.

⚠️ **Three constraints on how the rate is stated.** Use algorithmic efficiency ×
hardware and never training-compute growth (5.3×/yr is ~4×/yr of *spending*).
Never stack price-per-capability on top — it is already the compound, its
9×–900×/yr range is inflated by benchmark saturation, and it is a posted-price
series. And do **not** use the "Moore's law is dead so the bar is low" move:
ML-hardware price-performance is still doubling every ~2.2 years. **Cite Gundlach
et al. (MIT, arXiv:2511.21622) ourselves** as the honest flag — their ablations
account for under 100× of a claimed 22,000×, and attribute the measured gains to
two discrete scale-dependent events rather than smooth innovation.

**The window formulation** (candidate, gives the rate specific work): rent on
any want is collectable only between the moment it becomes possible and the
moment it becomes cheap. New capability opens the window; commoditization closes
it. Total collectable rent scales with the arrival rate of new wants times the
average window length, and window length is inversely proportional to the
commoditization clock the report already measures from two other directions.

**(c) The rent's own collection destroys the conditions for collecting it.**
⟨agreed⟩ The required rent stream **is** the Arrow-clause pressure generator:
the only spending pool large enough is labour compensation, so the pricing
assumes automating a fifth to a third of world labour, and executing that
generates pressure with no legitimate channel. This closes a loop IV.3 currently
leaves open — the capital-cycle accounting and the Arrow clause are presently
two threads running past each other in the same section. **Sharpest consequence:
reading (b) of the three-readings fork ("the moats hold, rents captured out of
substituted labour") is internally unstable, not merely optimistic.**

⚠️ Three limits to state rather than resolve. Rate, not fact — US agriculture
went 40% → 2% of employment without breaking the market, over a century (Goldin
& Katz's race). Build the claim on the **uneven-geography** version, which is
stronger: displacement lands globally while buffers are national, so pressure
discharges where the buffer is thinnest. And the **direction of the break is
ambiguous** — instability historically produces security states and capture as
often as levelling; only the destructive branch pops the bubble. State the fork.

⚠️ **Register (important):** the migration/reaction material enters strictly as a
gauge reading, per the convention already established for the UnitedHealthcare
datapoint. Do **not** rest anything on crime trends (mixed, and the
immigration-crime literature runs against intuition). The measurable signal is
the **political reaction**, which is well documented and needs no contested
empirical claim.

## 4. The mindshare/resources distinction

⟨agreed, Matthew's correction⟩ Niche means **niche in human mindshare**, not in
resources. A frontier consuming the majority of the visible universe's resources
can still be niche by that measure. Two consequences:

- **"The frontier consumes everything" and "the AI bubble pops" are fully
  compatible.** The $17T was capitalized against broad labour substitution — a
  wide base of payers. A frontier that is vast in resources but niche in
  mindshare produces a few very large customers, a different revenue shape that
  cannot service that capitalization.
- **Three candidate funders, none of which rescues the valuations.** Capital
  markets on expectation of future broad rents (that is the bubble); the
  frontier's own output value (a real and possibly vast research business, but
  not a rent-on-everyone business); or states for strategic reasons (not a
  market rent at all).

**And the circular-flow synthesis, which settles the segmentation without
needing to adjudicate whether labs are institutionally bounded.** Whatever
unbounded-wanting demand exists sits *inside* the loop, so those payments net
out in consolidation — they are the circularity, not external revenue. The
report's own accounting (~$300–400B external against $700B–1T out) means the
money that must arrive comes **by construction** from the bounded-wanting
population outside the complex. So the compute-excludability counter protects
rent over a segment whose payments cancel: true and irrelevant at once.

⚠️ **The unresolved tension, to be named not hidden.** Aggregate demand ≈
(number of genuine wants) × (compute per want). Coherence says the first term is
small; agentic orchestration makes the second large and growing — and §6 plus
the Appendix A programme exist precisely to make it large. That concentrates
demand in the unbounded-wanting tier and leaves open whether that tier absorbs
enough to carry the rents anyway.

⚠️ **A political-economy consequence the paper should decide about.** A tiny
number of people directing an unbounded share of civilization's compute is
exactly the structure the Arrow-clause block calls *de facto royalty*. The
picture is two-tier: ambient capability genuinely democratized because it
saturates wanting and costs nothing, plus a frontier that concentrates and grows
without limit. The commons argument wins completely where mindshare lives and
does not touch where the resources go. **Is that the good outcome or the failure
mode wearing its clothes?** Possibly what the widened paper's ending is about.

## 5. The legal layer — capability is unprotectable

⟨agreed⟩ Matthew's extension: weights resemble **seed** more than software,
because capability can be reimplemented once known. Verified consequences:

- **It generalizes to closed models.** A served model reveals that its
  capability level is achievable, and knowing a thing is possible is a large
  fraction of the work. Arrow 1962 again: revelation is the business model, not
  a leak.
- **No exclusive right attaches.** Human authorship (*Thaler*, cert denied
  2026-03-02) plus § 102(b) functionality; the Copyright Office has never
  addressed weights as a registrable work and declined sui generis protection;
  **no US court has decided it and no plaintiff has ever asserted it.**
- **Primary-text confirmation:** Gemma's terms contain **no grant-of-rights
  clause at all** and require each downstream distributor to manufacture a new
  contract — structurally identical to German OpenSourceSeeds. OSI concedes
  weights "may be free by their nature."
- **Contract, not property.** Assent is decisive (hiQ won on contract with a
  model-deletion order; Meta lost to a logged-out scraper). *ProCD*: "A
  copyright is a right against the world. Contracts, by contrast, generally
  affect only their parties." **The knowledge launders itself in one hop.**
- **Nobody has ever sued.** No AI provider anywhere has litigated over outputs,
  distillation, or a no-competing-model clause. Musk conceded under oath that
  xAI "partly" distilled OpenAI's models — no claim followed. Enforcement is
  account termination, cease-and-desist, and **lobbying Congress**, which is
  what firms without a right do.
- ⚠️ **But this cuts against the bequest too: open weights ≠ open method.**
  Releasing weights forfeits secrecy in the artifact, not the training method,
  and training-time techniques leave no signature. **The optimization competence
  stays enclosed even when the optimized artifact is given away.**
- ⭐ **And one finding cuts sharply *for* the thesis:** the empirical work scores
  secrecy far above patenting for *process* innovation precisely because process
  leaves no trace — so IP doctrine rewards concealment over disclosure in
  exactly the layer where pooled optimization would compound.

**The 2026 policy fight** ⟨agreed as trajectory evidence, not rights evidence⟩.
Chronology: OpenAI memo (Feb 12) → NSTM-4 on adversarial distillation (Apr 23) →
EO 14409 (Jun 2) → Anthropic's Senate Banking letter (Jun 10) → the
235-signatory "Open Weights and American AI Leadership" letter (Jul 24) → the
implementing framework exempting open weights (Aug 4), eleven days later. At the
moment the case for building the enclosure instrument was strongest, the
political layer declined — and the exemption reportedly spares *Chinese*
open-weight models too, so the operative category is openness rather than
origin.

⚠️ **State the exemption precisely or not at all.** EO 14409 never mentions open
models; the carve-out is in an **unpublished** implementing framework; and the
review it exempts them from is **voluntary** (the EO disclaims any "mandatory
governmental licensing, preclearance, or permitting requirement"). It is
compliance-side and says nothing about appropriability. Weakest link in the set.
⚠️ **Also correct the industry-split reading:** it is not open vs closed. OpenAI
signed the July letter *and* filed the February memo, coherently — its own memo
draws the same legitimate/adversarial line. **Anthropic is the only major
frontier lab that pressed the case and did not sign.** The division is over
*scope of remedy*, and what the industry asks for is a right distinguishing by
**manner of acquisition** rather than subject matter — trade-secret-shaped, and
landing exactly on the unconstrued *Compulife* "method and scale" question.

## 6. Prior art — cite, don't claim

| Sub-claim | Status |
|---|---|
| Open weights commoditize and undermine the required returns | **PUBLISHED repeatedly** — Surman (FT op-ed), Moody, Dediu (and Ben Thompson's published rebuttal). Cite into. |
| Copyleft needs an underlying right; weights have none; open-weight licences are hollow | **PUBLISHED — Henderson & Lemley, 100 Ind. L.J. 1327 (2025).** States our mechanism almost verbatim. |
| Appropriability of AI capability | **Real literature** — Azoulay/Krieger/Nagaraj (NBER 32474), Korinek & Vipra, Jones & Tonetti |
| The collective-action mechanism | **Named thirty years early** — Bresnahan & Trajtenberg 1995, "innovational complementarities" |
| The crash-vs-copy **inversion** | **Unclaimed** — build on the four legs, present as contrast |
| Weights ≈ germplasm framing | **Unclaimed** |
| OSSI's retreat as predictive precedent | **Unclaimed** |
| "No right attaches to capability" as a doctrinal package | **Unclaimed** — building blocks standard, never assembled |

**Opponents to engage by name.** Ord (arXiv:2503.05705) and Sastry et al.
(arXiv:2402.08797) on excludability migrating to compute — answer with decay
(the appropriable asset is wasting: open-weight lag fell from ~1 year to ~4
months; price-per-capability falling fast) plus the wanting argument (concede
the frontier, contest its relevance). Korinek & Vipra on natural monopoly at the
frontier — same shape of answer. **Azoulay, Krieger & Nagaraj argue
appropriability is *tight*** via tacit knowledge and endogenously raised
reverse-engineering costs — their natural experiment is the Llama **leak**,
which is the opening: their evidence is weights escaping, ours is capability
revealed by ordinary use. ⚠️ Note they are simultaneously the **theoretical
backing for the rent-location corollary** (complementary assets *are* the toll
booth), so cite them in both places.

## 7. Additions since staging (2026-08-12) — review as a unit

Items (a)–(e): occasioned by the Nvidia compute-credit platforms (2026-08-10;
facts, frames, and to-do checklist in
`analysis/capital-cycle/nvidia-credit-note.md`). Item (f): the subscription
economics (Matthew, 2026-08-12). Everything motivated since the 08-09 staging
is collected here — both changes proposed *to this proposal* and changes
motivated *elsewhere* — so it reviews as one block. Nothing below has been
folded into §§1–6 or the outline.

**(a) → §1: the transmission mechanism.** As staged, the argument has a gap:
endogenous socialization is a *diffuse* process, and a rent stream can erode
gracefully for years without any discrete event — leaving the "pop" unlocated
and the claim exposed to "it just deflates slowly." The credit platforms close
the gap. Collateralized lending against GPUs converts commoditization into a
repricing event with a schedule: credit reprices at refinancing; the first
vintage of platform-financed hardware exhausts its book life ~5 years after
deployment; the refinancing wave lands ~2030 — exactly when the model's ~$5T
stock needs its returns to have arrived. Underwriting must assume scarcity
pricing (Matthew's formulation: **expected returns priced on non-commodity
expectations against commodity reality** — telecom's DWDM failure restated:
debt underwritten on doubling-every-100-days demand while DWDM multiplied
capacity per strand ~100× mid-buildout). If commodity reality arrives first,
it surfaces as **failed refinancings** — so the inversion gains a
falsification point with an approximate date, and "the pop is caused by the
technology working" acquires its concrete channel: capability diffusion →
collateral repricing → credit event. ⚠️ Assertable only once actual terms
surface (residual guarantees, assumed lives, utilization-price curves — the
checklist is in the note).

**(b) → §3(b): the market has taken the other side of the wanting bet, with
size and named actors.** The $500B platforms are underwritable only in the
growing-rents scenario — the model's cheapest row — and "the whole economy
accelerating" is broad absorption, i.e. the wanting race resolving favourably.
The wanting argument now has a counterparty: ⟨indirect⟩, the markets do the
arguing, and someone loses money on a specific row of Table 3. Evidence of
*stakes*, not of outcome.

**(c) → §4: funder #1 named.** The trilemma's "capital markets on expectation
of future broad rents" now has actors and a structure: Apollo/BlackRock/
Blackstone/Brookfield/Goldman/KKR, $500B+, SPVs, insurance-linked and
pension-adjacent pools — the socialization base widening in real time.

**(d) → NOT this proposal: the continuous-socialization bullet (IV.3).** The
event is primarily an entry for the *existing* thread: the §11 watch variables
firing (debt/private-credit share; intra-loop renegotiation), the Credit
Mobilier lineage's next entry (supplier orchestrating third-party capital into
platforms financing purchases of its own product), and the fungibility/scarcity
contradiction (collateral requires fungibility AND scarcity; fungible+abundant
= commodity pricing; the legs cohere only under Nvidia's own supply
discipline — the lenders' security is the monopolist's scarcity management).
Same dated-case-study aging policy as July 2026.

**(e) → NOT this proposal: the surviving-hardware bullet, after verification.**
Railroad equipment trusts as the honest counter: rolling stock financed as
fungible movable collateral, and equipment-trust certificates **survived
receiverships** (receivers needed the cars) while roadbed equity was wiped
out. A sophisticated read of the platforms is that structure deliberately
rebuilt. Disanalogies: ~25y boxcar life vs 3–5y GPUs; industry-standard gauge
vs single-vendor CUDA. [UNVERIFIED — needs a pass (Tufano BHR 1997;
"Philadelphia plan" certificates) before any use.]

**(f) → §3(b): the labs' own pricing is a solvency bet on wanting
saturation.** SemiAnalysis (June 2026) stress-drained the plans: Claude Max
20x ($200/mo) delivers ~$8,000/mo of API-equivalent tokens, ChatGPT Pro up to
$14,000 — 40–70× face value [via aggregator; re-verify against the paywalled
original before use]. Break-even: at $8,000 equivalent, any assumed API markup
≤ ~4× puts break-even under **10% average utilization** (reconstructs
Matthew's earlier-session calculation). Two uses. *Socialization:* the paid
subscription channel — not just free tiers — delivers capability at a small
fraction of metered value; below-cost delivery is running through the plans,
cross-subsidized by light users and the loop's capital. *Wanting:* flat-rate
pricing is solvent **only if most subscribers do not want most of what they
bought** — the labs' own price structure is revealed-preference evidence for
the wanting argument, sitting on the same side of the bet as §3(b)'s
counterparty observation but from inside the labs. Corollary gauge: if agentic
orchestration makes everyone a heavy user, the subscription model reprices to
metered or dies — a live, observable indicator on the wanting race, and the
labs' own version of the seat-to-work question the report's §11 already
watches.

**(g) → §6 (the Ord/Sastry answer) and §4: the appropriability window is
halving per era, and the rent is visibly relocating to complementary assets.**
SemiAnalysis (2026-08-21): open models' catch-up time to each era's first
closed frontier model fell **~18 months → 8.5 → ~5–6** across the
scaling/reasoning/agentic eras — "with each generation, open-source models
take half as long to catch up." Upgrades the wasting-asset answer from a
level to a **rate**, and gives the window formulation (§3(b)) its measured
window-length series. Fireworks serving >40T tokens/day (2× OpenAI's API)
is diffusion measured in served tokens. The frontier's response — release
cadence compressed 213→120→51 days — is the wasting-asset frame from the
inside: the artifact depreciates, only the pipeline holds value, which is
also the damping-loop's shape (if funding stops, the cadence stops, the last
release freezes as the endowment). **And their own caveat carries the other
half:** they prefer Fable for daily work despite Kimi K3's higher composite —
the surviving gap is *productization* (harness), i.e. Teece's complementary
assets collecting the rent the model layer cannot hold, with Anthropic's
+$65B ARR since Claude Code as the measured instance. That is the
rent-location corollary operating inside the AI stack, and it should be
cited alongside Azoulay-Krieger-Nagaraj in both places they appear.
⚠️ Three data points, author-chosen era boundaries, gameable benchmarks (their
own admission) — cite as a trend claim with flags, not a law.

**(h) → §6: the compute-concentration counter, now quantitative — engage it as
the primary opponent.** SemiAnalysis's paywalled "Upcoming Era" section is
Ord/Sastry/Korinek made concrete: Anthropic+OpenAI are only 27% of net-new GW
today, but frontier-token API sales yield up to $100M/MW/yr vs sub-$30M for
everything else, so the labs outbid all other compute uses, training ROIC
compounds (models help build successors), and the gap could re-widen an order
of magnitude — the one thing that stops catch-up time halving. It **concedes
our premises and relocates the moat to compute access.** Our crux-level answer
is already in the thread: the $100M/MW ROIC requires *frontier-token demand at
volume*, which is the wanting/mindshare question (§4) restated as compute
allocation — and it is the same scarcity-priced expectation the credit note
(§7a) says is being underwritten and the commodity-reality argument disputes.
So (h) does not sit outside the thread; it names the single variable on which
our bet and theirs are opposite, and that variable is frontier-token demand at
volume. Note also: even the authors expect open source to close the *next*
gap in <3 months absent the compute divergence — the trend claim survives
their own forecast. **This is the opponent to foreground; cite it as the best
opposing case (role the outline gives "Dally/Jouppi" in the hardware
argument).**

**Also resolved (not a proposal edit):** the July-2026 OpenAI/Hugging Face
sandbox-escape incident (agent swarm, multi-week, lateral movement to
production) resolves the outline's queued "OpenAI breakout incident" item for
III.3 — banked in NONRIVALRY-ANCHORS.md with a ⚠️ find-the-primary flag.

**(i) → §6, pointer only (content in `NONRIVALRY-ANCHORS.md`):** the
mechanism-level answer to (h)'s compute-concentration counter — draft the
*structural* form (breadth of objective recruits more search than a narrow
beam; Hong & Page), not the naive "humans intuit better" form, which fails
under the future paradigms it is offered for. Strategy and goodwill are one
mechanism at different timescales (folk theorem; Axelrod; Ostrom), converging
as the rate of change rises (shorter time-to-payoff) and ease of living rises
(lower discount rates). The old strategic-vs-goodwill "distinction" was wrong
and is retracted in the anchors file. **The architectural consequence is §9.**

**Decision asked:** accept (a)–(c), (f), (g), (h) into §§1/3/4/6; route
(d)–(e) to their threads now or hold everything until deal terms make (a)
assertable.

## 9. Architectural implication — the two halves are one bet (cross-movement)

⚠️ **This is not an IV.3 edit.** It is a claim about how the paper's *diagnosis*
half (the capital cycle: do the valuations hold?) and its *cure* half (the
commons: does openness endure?) connect, and it lands in the Arrow-clause block
and at the ending, not in the non-rivalry bullet. Raised here because it fell
out of the §7 work; decide separately from (a)–(h).

**The claim.** Both halves are the same bet on one variable — the length of the
horizon agents act on, which rises with ease of living. A long horizon
simultaneously (1) makes *release the dominant strategy* (a fast-depreciating
lead is dominated by contribution; the wasting-asset dynamic applied to
strategic incentives) → open weights durably socialize; and (2) makes the *fair
split cheaper than extraction* (the Arrow-clause "cheapest long-run discharge")
→ the transition discharges peacefully. Immiseration shortens horizons and
blocks both at once. So the open-weights-durability claim and the
peaceful-discharge claim are **not two bets but one**, resolved by the same
prosperity/immiseration race, and should be drafted as two faces of one
dynamic.

**The mechanism is published** (build on, don't claim): the folk theorem —
cooperation is the individually rational strategy once the shadow of the future
is long enough — with Axelrod and Ostrom's cooperation conditions (Ostrom
already in the paper). Rising rate of change and rising ease of living are the
two things that lengthen that shadow (time-to-payoff; discount rate).

**The structural payoff — it resolves the three-readings fork.** Reading (c)
("the bubble is the down payment on a post-scarcity society"), currently
"foreshadowed in one sentence and resolved at the paper's end," **is the
convergence completing**: the regime where ease of living has risen enough that
strategy and goodwill coincide for most people is exactly the post-scarcity
regime where money's role shrinks. The convergence is the *resolution* the
foreshadow promises — so this material is a strong candidate for the ending,
carrying reading (c) from foreshadow to payoff.

**Honest conditions (the same two that gate the whole optimistic case).** The
folk theorem needs repeated, observable interaction — a one-shot decisive grab
(hard takeoff) breaks it (the singleton, treated separately in coherence as
"the wrong fear"). And rising ease of living is not guaranteed — the extraction
phase could immiserate first, unevenly by geography. State both as frontiers.

**Decision asked (separate from §7):** does this become (i) the resolution beat
at the ending, carrying reading (c); (ii) an addition to the Arrow-clause block
in IV.3's tail; or (iii) its own short structural note? My lean: (i), because it
is what the three-readings foreshadow was written to pay off. Needs a
verification pass on the folk-theorem/Ostrom anchors and a prior-art check on
the acceleration-shortens-horizons step before drafting.

## 8. Open decisions for Matthew

1. **Where the inversion lives** — inside the three-readings block as a
   refinement of reading (a), or as its own bullet before it?
2. **Does the wanting argument enter IV.3, or stay in II.4/coherence territory
   with a backward reference?** It currently does economic work in IV.3 that it
   was not written for.
3. **The two-tier question in §4** — name it as an open question in IV.3, or
   defer it to the ending, where it may belong?
4. **The window formulation** — keep as an explicit model, or fold into prose?
5. **Dated-material policy.** July 2026 is already ⟨agreed⟩ as a dated case
   study. The Aug 2026 exemption has the same aging problem and is weaker
   evidence. Same treatment, lighter, or cut?
6. **Agriculture placement** ⟨agreed⟩: IV.1 primary, IV.3 one-line contrast,
   and the Bessen–Nuvolari answer in the limits section — the enclosure
   mechanism there was **institutional, not technological**, which answers their
   objection without needing to win the technological argument. Still to decide:
   does the OSSI/copyleft-propagation material go with it in IV.1, or with the
   legal layer in §5 above?
