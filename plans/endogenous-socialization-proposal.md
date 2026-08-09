# Proposal: the non-rivalry / endogenous-socialization thread

**Status: PROPOSAL — nothing here has been applied to `outline-cosmic-ac.md`.**
Assembled 2026-08-09 from the 08-07/08-09 dialogue. Per the repo rule, staged
for Matthew to accept, amend, or reject. Every claim's verification status is in
`analysis/capital-cycle/NONRIVALRY-ANCHORS.md`,
`analysis/commons-precedents/agriculture.md`, and
`analysis/commons-precedents/weights-ip.md`.

Decisions already taken in dialogue are marked ⟨agreed⟩. Open decisions are
collected in §7.

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

## 7. Open decisions for Matthew

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
