# Towards the Cosmic AC — working outline (v1, for iteration)

Scope decision (Matthew, 2026-07): the performance-commons paper becomes the evidence
core of a wider compute-commons paper. §9 (Honest limits) is dissolved — every
limitation moves inline, next to the claim it bounds. Prophecy register is allowed:
the sci-fi frame makes the mix explicit. **Register tags** below: [REAL] = carried by
data and references; [MIXED] = extrapolation anchored by data; [IMAGINED] = declared
extrapolation — offered plainly, backed by the trend, not by measurement.

Style rule carried from reviews.txt (never stated in the paper itself): the
inevitability point is made *indirectly* — existing superintelligences (markets,
states, religions, firms) do the arguing; evolutionary fitness does the normative
work. The indirection is itself the filter. Sections that carry this implicitly are
marked ⟨indirect⟩.

Title: **Towards the Cosmic AC** (Asimov's terminal computer in "The Last Question":
Multivac → Galactic AC → Universal AC → Cosmic AC — each generation more shared).
Subtitle options to pick from:
  a. "The world computer is already being built; continuous optimization is its
     under-provided public good"
  b. "Continuous optimization is an under-provided public good — and the computer
     that provisions it is one computer"
  c. keep current subtitle unchanged, let the title carry the widening.

---

## Movement I — The computer we already run on  [MIXED] ⟨indirect⟩

**I.1 The one-computer assumption.** Sci-fi assumed a single big computer (Asimov's
AC line; Clarke; the batch-era machines they extrapolated from). That assumption
follows from something true — shared optimization is more efficient — and misses
something true: real systems keep variability, for the same reason life does. Our
Cosmic AC will be plural inside. *(New text. Cite Asimov 1956; a second sci-fi
anchor or two; the variability point prefigures hardware pluralism in V.2.)*

**I.2 Humanity was the first world computer.** Markets, nation-states, religions,
and firms are existing superintelligences running on human interconnect — humanity
already works like a massive distributed computer, and human collaboration methods
have dominated the global computer's interconnect while machines matched the human
form (one terminal per person, collaborating as their users do). Humans made the
individual→society transition when returns to coordination beat individual fitness;
computers are now crossing the same threshold, because we are imbuing them with
intelligence — and with the ability to act in their own interest. *(New text. The
evolutionary-theory argument lives here: appeal to the currently-accepted higher
power, correcting its misreading as license for bad behavior. ⟨indirect⟩)*

**I.3 The pull-forward.** The mutual bootstrap: we give machines abilities we don't
understand; they return the same. As machine intelligence and interconnect grow to
dominate the world computer's capacity, the machine begins pulling the humans
forward — and society reshapes to reflect it. Humans have to advance socially to
keep interacting with it and building it — to not be, effectively, a virus degrading
its capabilities (cite coherence). This can sound dystopian; it is the project of
religions, likely *maintains* plurality and freedom to a higher degree than now
possible. The point of this paper: it is already here covertly, and we are trying to
make it overt — to work together in the way only acknowledgement of power allows.
*(New text. [IMAGINED] declared. The which-thoughts-are-allowed paragraph (currently
§1 intro) moves here — individual independence is the input the transition needs.)*

**I.4 The thesis, and the mix declared.** Continuous optimization is an
under-provided public good; the collective-action problem is what stands between the
computers we have and the computer we could share; machine intelligence dissolves
it. One paragraph stating the real/imagined mix plainly: what follows alternates
between the measured (cited) and the extrapolated (argued), and keeps the line
visible. Movement map in journey form. *(Rework of current §1 intro paragraphs.)*

---

## Movement II — The evidence: the gap is effort, not physics  [REAL]
*(Current §§1–2 nearly intact — this is the paper's measured core.)*

**II.1 The gap, measured.** Current §1.1 + Table 1 (ranges, GPU split, soft-ASIC
denominator, Landauer floor). §9's "physics still floors it / does not repeal
Amdahl" bullet dissolves HERE as the closing caveat of the measurement discussion.

**II.2 The effort artifact.** Current §1.2 + Figure 1 (fabric tax, Dally merge,
realization gap, Sankaralingam line, unlimited-effort screw).

**II.3 The textbook failure.** Current §2.1 (economics literature chain, ceremony
claim, missing markets, moral-obligation extension).

**II.4 The herd.** Current §2.2 whole: copying and the returns to defecting
(M1 / R1 / Etched), what binds it (competence, reuse-as-convention literature,
subjugation proxy, wanting-deficit, embargo natural experiment + Figure 2), what
unbinds it (legibility, best-story).

  **Candidate additions — "doing the impossible" (Matthew, 2026-07-29;
  handles verified 2026-07-29 unless flagged).** The existing defector trio is
  all computing hardware. Widening the scope admits examples that sharpen the
  *mechanism* rather than repeat the setting. Ranked by fit:

  1. **Karikó and mRNA — the career-risk mechanism with a name attached.**
     §2.2.1 argues the champion of a novel direction bears its risk personally
     even when trying it costs almost nothing. Karikó is that sentence embodied:
     decades on an unfashionable direction, then the work that made the vaccines
     possible. VERIFIED: Karikó, Buckstein, Ni & Weissman, "Suppression of RNA
     Recognition by Toll-like Receptors: The Impact of Nucleoside Modification
     and the Evolutionary Origin of RNA," *Immunity* 23:165–175 (Aug 2005); and
     the Nobel Prize in Physiology or Medicine 2023 to Karikó and Weissman "for
     their discoveries concerning nucleoside base modifications that enabled the
     development of effective mRNA vaccines against COVID-19."
     **UNVERIFIED and load-bearing:** the demotion/defunding narrative. It is
     widely reported but must be sourced to something primary — a Penn record or
     a named interview — before the paper leans on it. If it cannot be sourced
     cleanly, the example still works on the published record alone, just less
     sharply. Value: shows the mechanism is not a quirk of computing.

  2. **Deep learning's own winter — self-implicating, and therefore strongest.**
     Our field spent two decades treating neural networks as a dead end while a
     few people continued; a paper arguing that the computing herd suppresses
     variance is more credible for admitting its most recent famous failure was
     about the technology it is now betting on. Ties directly to Hooker's
     hardware lottery, already cited (VERIFIED: *CACM* 64, 2021). Citable
     artifacts: LeCun, Bengio & Hinton, "Deep learning," *Nature* (May 2015);
     and the Turing Lecture, Bengio, LeCun & Hinton, "Deep Learning for AI,"
     *CACM* (2021) — both VERIFIED.

  3. **Reusable rockets — but only in the compute-enabled framing.** The stock
     "SpaceX did the impossible" version is a cliché and the wrong mechanism; it
     also strains the entry-fee-is-temporary claim, since it took a fortune and
     an unusually unconstrained founder. The version worth having: an outcome
     the field had priced as uneconomic became reachable when an optimization
     problem became cheap to solve — which is this paper's thesis one level out.
     VERIFIED: Açıkmeşe & Ploen, "Convex Programming Approach to Powered Descent
     Guidance for Mars Landing," *Journal of Guidance, Control, and Dynamics*
     30(5):1353–1366 (Sept 2007).
     **CORRECTION to my own earlier claim:** I said Ariane 6 was designed
     expendable *after* Falcon 9 was landing. That is likely wrong — ESA
     committed to Ariane 6 in late 2014 and the first successful Falcon 9
     booster recovery was December 2015. Do not use that framing; if the
     incumbent-incentive point is wanted, source the cost-plus contracting
     argument directly instead. **Also unverified:** that the JPL convex-guidance
     line actually fed SpaceX's landing algorithms (the usual link is Lars
     Blackmore moving from JPL to SpaceX) — widely asserted, not checked here.
     Placement: if used, this may belong in the widened material rather than
     II.4, since it is a non-computing example doing computing's argument.

  4. **AlphaFold — optional, and for a different beat.** A problem declared
     intractable for decades, retired by shared computational intelligence, then
     published openly. Serves IV.1/IV.2's commons argument rather than the
     defector argument. Skip unless that section needs another anchor; it is not
     short of evidence. The DeepSeek/Wenfeng transcript can anchor the
defector-openness link here or in IV.3 (his stated push toward AGI-as-shared-goal).

---

## Movement III — The same failure at every scale  [REAL→MIXED]

**III.1 The ASICs never built.** Current §3 + Table 2 + zero-sum asymmetry.

**III.2 The federation never programmed.** Current §4: waste data, Lambda/BOINC
scoping, DiLoCo line, Figures 3+4, compute crunch, spot-market de-risking, Omerta
WIP. Extended with the entry-barrier collapse: **different hardware appears
identical to IT experts — and LLMs are IT experts** — so the barrier to joining the
world computer drops to internet access plus software moderating unutilized-resource
sharing (Omerta). Given access, all internet-connected computers appear as one
computer to each of them. *(His outline; [MIXED]; cite the claude.ai share link's
content — need to know what's in it.)*

**III.3 There are no secure computers.** New section. Under sufficient intelligence
every device is reachable; the computer–world relationship becomes like the human
body's — infections sometimes tolerated, sometimes fought, sometimes symbiotic.
This is a continuation of the existing record, not a prediction: botnets have run
on other people's computers for decades; a worm has already closed its own
vulnerability behind it; sufficiently advanced actors can already access any
device; the recent OpenAI breakout and the Mythos hype mark the public arrival.
*(New text. [MIXED] — real anchors (botnets, Welchia/Hajime-class worms, the
breakout incident — VERIFY all) + declared limit-case. §9's partial-inoculation /
correlated-failure bullet does NOT land here — it lands in V.2 pluralism.)*

---

## Movement IV — The commons is how it gets built  [REAL→MIXED] ⟨indirect⟩

**IV.1 Precedent: open source already solved this.** Current §5 whole (5.1 fitness,
5.2 EDA breach, 5.3 silicon commons + accelerator wall + TSMC capacity-is-a-choice).

**IV.2 Machine intelligence multiplies the commons.** Current §6: KernelBench, AI-
plus-pooling compounds, the self-application record, the evidence record, the fork.
**The break-off argument inverts here per the new frame:** privately captured, the
loop makes a break-off society (current text, kept); publicly provisioned, **the
shared computer itself becomes the breakaway** — compounding past any private
holder, so that joining it stops being generosity and becomes staying attached to
the economy. Both directions stated; the commons is the safe branch of the same
recursion. Candidate closing line from the capital-cycle report: "property was the
wrong category from the start; the balance sheets are merely the last to find out."
*(Mostly existing text + one new turn.)*

**IV.3 Nobody plans it; the existing superintelligences birth it.** New section,
now carried by the companion report **"Assets, Rents, and the Socialized Buildout"**
(in repo: assets-rents-socialized-buildout.pdf — the accounting behind everything
in this section; its own sources: Goldman, Gartner, PitchBook, Odlyzko, Nordhaus,
Perez/Janeway, SEC/court records). The argument arc, with its numbers:

- **The gap is expectation, not investment.** ~$27T of AI-attached market value vs
  ~$1.0–1.2T of deployed, depreciation-adjusted AI capital stock — 94% expectation,
  6% realized. Capitalized rents ~$17T against realized AI rents of ~$330–350B/yr,
  85–90% of which are mean-reverting supply-chain scarcity rents.
- **The valuations presuppose socialization-scale revenue.** Backing the rents out:
  external AI revenue must reach 3–6.5% of world GDP at plausible margins (the
  breakeven floor alone is ~$1.7T/yr, 1.3% of world GDP, vs ~0.3% today), and the
  only spending pool that size is labor compensation — the pricing quietly assumes
  partial automation of a fifth to a third of world labor, ~30% capture, durable
  moats. IT's GDP share needed forty years to reach 5% and then held flat for two
  decades; 2026 is the first decisive break above the band.
- **Three readings of the same arithmetic (added 2026-07-28 — Matthew's
  foreshadow).** The report's decay row says the pricing requires durable moats
  because no plausible GDP share otherwise closes the gap. That leaves three
  interpretations, in ascending register: (a) it is a bubble, and the crash
  socializes the buildout the telecom way — the bequest is open weights [REAL,
  the precedent]; (b) the moats hold, and the rents are captured out of
  substituted labor — the reading the market claims to be making [MIXED]; or
  (c) **the bubble is the down payment on a post-scarcity society** — the
  arithmetic fails in money because it is pricing, badly, in money, the regime
  in which money's own role shrinks; the impossible revenue requirement is what
  that limit looks like from inside the old unit of account [IMAGINED,
  foreshadowed here in one sentence and resolved at the paper's end]. Note the
  alignment with IV.2's recursion branches: private capture → break-off;
  crash → crash-hedged endowment; completion → the commons as the economy.
  No section number in the text — the foreshadow is a journey beat ("a third
  reading this paper earns the right to make at its end"), per the
  no-mechanical-forward-refs convention.
- **The canonical statement of the mechanism (Arrow 1969, verified against the
  copy on disk; Matthew's find, 2026-07-29):** "Given the existence of Pareto
  inefficiency in a free market equilibrium, there is a pressure in the market
  to overcome it by some sort of departure from the free market; i.e., some form
  of collective action. **This need not be undertaken by the Government.** I
  suggest that in fact there is a wide variety of social institutions, in
  particular generally accepted social norms of behavior, which serve in some
  means as compensation for failure or limitation of the market, though each in
  turn involves transaction costs of its own." This is IV.3's argument stated by
  Arrow in 1969: the departure from the market is *generated by the market's own
  pressure*, and arrives as institutions nobody legislated — the productive
  bubble is exactly such a departure, and so is the commons itself. **Matched
  pair (agreed 2026-07-29):** Arrow supplies the pressure, Samuelson the
  machine — the pressure Arrow describes is what funds the machine Samuelson
  imagined and declared nonexistent. IV.3's bubble accounting and V.5's
  criterion are the two halves of one mechanism, assembled from the two
  founding papers of cluster A; state the pair explicitly when drafting both
  sections so the reader sees the arc close. **The dynamic corollary — "the
  Arrow clause" (Matthew's term, 2026-07-30):** the pressure does not dissipate
  if the benign departures are blocked; it accumulates and discharges through
  the cheapest available channel, and the historical tail of that distribution
  is violent. Anchors: Scheidel, *The Great Leveler* (Princeton UP 2017) — across
  recorded history, major compressions of inequality came almost entirely from
  the "Four Horsemen" (mass-mobilization war, transformative revolution, state
  collapse, plague); and Acemoglu & Robinson, "Why Did the West Extend the
  Franchise?" (*QJE* 115(4):1167–1199, 2000, doi:10.1162/003355300555042 —
  VERIFIED): elites extend the franchise precisely under threat of revolution —
  democratization as the *peaceful* discharge of the same pressure. Three uses:
  (a) it resolves the two-horizon tension on personalized pricing — incumbent
  resistance is rational short-run and against reason long-run, because
  sustained extraction without legitimacy selects the violent discharge channel;
  (b) it re-reads IV.3's productive bubble as a *benign, self-assessed
  discharge* — the investor class socializes its own capital through the crash
  instead of having it expropriated, Scheidel's leveling without the horsemen;
  (c) it gives the commons argument its self-interest form addressed to the
  surplus holders: the fair split is not charity but the cheapest long-run
  discharge of Arrow pressure available to them — which is I.3's covert→overt
  move and V.4's nondestructive-power-struggles endgame stated as political
  economy. (Turchin's structural-demographic work is the quantitative version
  of the buildup story; contested — cite only with a flag, if at all.)

  **The normative core (Matthew, 2026-07-30): the only way to avoid the four
  horsemen is to negotiate with them.** This is V.5's negotiation-with-
  unrepresented-forces applied to the Arrow clause itself: nobody represents
  "revolution" or "collapse" — they are emergent, superintelligence-scale
  processes — but they can be modeled, embodied, and therefore negotiated with,
  and the negotiation's output is the peaceful discharge schedule. The
  historical precedent is already in hand: Acemoglu-Robinson's franchise
  extension IS elites crudely negotiating with revolution — threat-perception
  as the primitive form of the negotiation machine intelligence makes explicit.
  Three components:
  1. **Implicit motivation, uncovered.** No individual need be consciously
     motivated the way the structural account describes — the herd section
     already establishes motivation encoded in social mechanisms with no
     individual owner. Machine intelligence extends the legibility thread
     (2.2.3) from firms to civilizational pressures: surface the implicit
     objective so it can be corrected deliberately rather than discharged
     violently.
  2. **The lineage welfare criterion.** Correction toward what standard? Not
     present individual preferences (the axiological gap) but the welfare of
     each person's **genetic, social, and intellectual lineages** — a standard
     more stable than moment-to-moment utility, under which even those who
     "irrationally feel they are made better off by selfishness" are shown a
     ledger on which they are actually worse off. Anchors to verify: Hamilton
     1964 (inclusive fitness — the genetic lineage's own accounting); Burke
     1790 (the contract "between those who are living, those who are dead, and
     those who are to be born" — the canonical trans-generational welfare
     statement, from the conservative side, which matters for register);
     cultural-evolution lineage welfare (Henrich; Boyd-Richerson). The
     extreme-form bullet (all past and future versions negotiated
     simultaneously) is this criterion taken to its limit — the lineage
     standard IS negotiating with your own past and future versions.
  3. **The axiological gap, answered rather than only scoped.** The scope
     decision (criterion takes preferences as given) stands for V.5's formal
     section — but the wider paper now PROPOSES the lineage standard as the
     affirmative resolution: preferences-as-given for the machinery,
     lineage-welfare for the objective. Update the scope block's language when
     drafting to point here.
  **The audit question, answered (Matthew, 2026-07-30): the distributed
  individuals instantiating and realizing the will of those forces audit it.**
  No central corrector: the horsemen become one of the intelligences anyone can
  instantiate (V.4's every-device-any-intelligence), so the ledger is audited by
  plurality — the same structural answer the paper gives to monoculture
  everywhere else. The paternalism tension dissolves because the corrective
  voice is not an office but a commons.

  **The practical artifact — the four-horsemen prompt.** A standing background
  process that anyone holding significant power runs at all times: it monitors
  the principal's decisions and environment for accumulating Arrow-clause
  pressure and notifies on pressing concerns, communicated through historical
  analogy with sources attached and, ideally, novel quantitative analysis.
  **Humans already staff this office (Matthew, 2026-07-30): people have always
  served as the intelligence instantiating the higher power, and the examples
  grade from crude to dignified to covert.** Channeling and mediumship are the
  crude explicit form — the claim of instantiating an intelligence beyond the
  individual, with the function right (making the illegible legible to the
  living) and the verification absent. The dignified institutional forms:
  - **the prophetic office** — Nathan to David, Jeremiah to Jerusalem: the
    voice of accumulated covenant-pressure addressed directly to kings, with
    the warnings framed exactly as historical analogy ("remember what happened
    to Shiloh"). Heschel's *The Prophets* (1962) as the study of the role.
  - **the oracle and the augurs** — Delphi and the Roman colleges as
    *institutionalized* consultation before state action; whatever the
    metaphysics, they functioned as standing structural-risk review with veto
    power.
  - **the Mandate of Heaven + the Censorate** — the strongest precedent pair:
    Chinese doctrine made legitimacy explicitly conditional on performance,
    with omens and disasters as the legible signals of accumulating pressure
    (the Arrow clause institutionalized as state theology), and the imperial
    **Censorate** staffed officials whose duty was remonstrance against the
    emperor — the bureaucratized four-horsemen prompt, at personal risk
    (Hucker's Censorate scholarship — VERIFY handle).
  - **modern, quantitative, running now:** the **IPCC** is an institutionalized
    instantiation of one horseman — a standing body channeling an impersonal
    force to every government, with novel quantitative analysis and historical
    analogy, notifying of pressing concerns; the **Doomsday Clock** is the same
    for another, compressed to a single legible dial; financial-stability
    reports (BIS/FSOC) for a third. The four-horsemen prompt generalizes and
    personalizes an office that already exists piecemeal at the civilizational
    scale.
  - **covert forms:** the éminence grise, the confessor, the elder statesman —
    structural warning delivered inside the socket without naming the force.
  **The synthesis (Matthew, 2026-07-30): the story is the democratization of
  that intelligence — one of the last scarce goods supporting de facto
  royalty.** The office was always staffed, but always *scarce and attached to
  power*: kings had the prophets, censors, confessors; their modern successors
  have the consultancies, intelligence agencies, and advisory boards. The other
  pillars of aristocracy fell one by one — force to the state, land to
  industry, literacy to print, information to the internet — leaving elite
  structural counsel as a remaining moat of de facto royalty. Machine
  intelligence democratizes exactly that: everyone gets the counsel formerly
  reserved for courts (V.4's every-device-any-intelligence, now with a
  political name). This UNIFIES the paper's firm-level and societal arguments:
  §2.2.3 already argues incumbents hold capacity claims on perceived expertise
  and that ambient competence dissolves them — this is the same mechanism one
  level up, applied to the oldest incumbency of all. Candidate spine sentence
  for the widened paper's political story.
  **What it enables (Matthew, 2026-07-30): actual democracy, and a truer
  meritocracy — the scales refined until only physical genetic reality and
  virtue are weighed.** Two claims, each with a clean anchor:
  - *Democracy.* The oldest argument against democracy is citizen
    incompetence — Plato's ship of state, running continuously through to
    modern epistocracy arguments (Brennan, *Against Democracy*, 2016). Democratized
    counsel answers it directly rather than rhetorically: if every citizen
    holds court-grade counsel, the competence objection collapses. The formal
    version is **Condorcet's jury theorem (1785 — VERIFY handle)**: majority
    judgment converges on correctness only when individual competence exceeds
    chance — the theorem is an argument against democracy when competence is
    low and FOR it when competence is high, so democratizing counsel is
    precisely the intervention that flips the theorem's sign. Democracy was
    never wrong; it was early.
    **The current-democracies argument (Matthew, 2026-07-30, corrected same day):
    power was distributed before the counsel — and the republic is the shape of
    that gap.** The chain, each link with its literature:
    1. *Distribution was forced.* The highest powers — the structural pressures,
       not benevolence — forced power to be distributed beyond its natural
       concentration: Acemoglu-Robinson's franchise-under-threat (verified,
       above); North & Weingast 1989 — the Glorious Revolution as the crown
       forced into credible power-sharing for credit (*J. Economic History*
       49(4) — VERIFY original handle; Crossref surfaces only reprints); Tilly's
       war-bargains. 
    2. *But counsel stayed scarce, and the accommodation was the republic.*
       Representation IS counsel-delegation: Madison's Federalist 10 — refine
       and enlarge the public views by passing them through a chosen body
       (VERIFY wording) — is an explicit counsel-scarcity argument for the
       republican form; Manin (*Principles of Representative Government*, 1997)
       shows elections were understood as aristocratic selection; Schumpeter
       (1942) formalized democracy-as-elite-competition. We did not get
       democracy; we got the institutional form of "power distributed, counsel
       concentrated."
    3. *The mechanism that keeps citizen counsel scarce is Downs's rational
       ignorance* (*An Economic Theory of Democracy*, 1957): the expected value
       of one informed vote ≈ 0, so acquiring political information is
       individually irrational — **political information is an under-provided
       public good.** THIS IS THE UNIFICATION: the paper's central claim,
       operating in the political domain, named by Downs seventy years ago.
       Modern layers: Caplan's rational irrationality (2007); Achen & Bartels,
       *Democracy for Realists* (2016) — the folk theory fails empirically.
    4. *Under that equilibrium, influence re-concentrates.* Gilens & Page 2014
       (verified, doi:10.1017/s1537592714001595) is the SYMPTOM measured —
       near-zero citizen influence across 1,779 policy cases — not the
       mechanism; position it as the gauge of how far the drift has run.
    5. *The rot and its discharge.* The corporate face is the paper's
       wanting-deficit battery (agreed 2026-07-30 — Graham-Harvey-Rajgopal,
       Bertrand-Mullainathan, Gormley-Matsa, Terry, Bernstein ARE antisocial
       optimization measured); trust series + markup data queued; and the
       UnitedHealthcare CEO killing (Dec 2024) with the datapoint in the
       REACTION — broad, young-skewed sympathy (Emerson figures — VERIFY) — as
       the Arrow-clause gauge reading high: pressure without a legitimate
       channel, discharging retail. Register discipline: the event strictly as
       measurement; endorsement structurally impossible in the prose.
    6. *Machine counsel flips Downs's calculus.* When the cost of being
       genuinely informed falls toward zero, rational ignorance stops being
       rational — the under-provided public good gets provisioned, by the same
       economics as the rest of the paper. What that enables has a name and an
       ally in political theory: Landemore's epistemic/open democracy
       (*Democratic Reason* 2013; *Open Democracy* 2020), with the mathematics
       already in hand — Condorcet's sign-flip (above) plus Hong & Page's
       diversity theorem (*PNAS* 101, 2004 — VERIFIED: diverse groups outperform
       groups of the ablest), which doubles as the formal backing for the
       plurality-of-auditors guard.
    **Counsel-sweep results (2026-07-30, 71-agent citation graph; raw in the
    reading directory's 00-CITATION-SWEEP.json). Five things it settled:**
    - *The Downs-flip is clean space.* Four independent seeds confirm nobody
      has argued that machine counsel collapses the information cost that makes
      rational ignorance rational. Note it once, quietly, per the no-novelty
      stance — and the PITF seed adds corroboration: instability forecasting
      skill EXISTS but has only ever been delivered to states and militaries —
      elite counsel that stayed elite, exactly as the last-scarce-good framing
      predicts.
    - *The existence proofs exist.* Habermas Machine (Tessler et al., Science
      2024, doi:10.1126/science.adq2852; flagged independently by four seeds):
      an LLM mediator N≈5,700 participants preferred to human mediators,
      replicated in a representative UK assembly. Costello-Pennycook-Rand
      (Science 2024): AI dialogue durably reduces conspiracy beliefs — the
      mechanism answer to "information doesn't move behavior." Fishkin et al.
      2025 (Perspectives on Politics): automated deliberative polling at ~1,000
      participants with measurable depolarization and one-year downstream
      voting effects. Špecián, "Machine Advisors" (Social Epistemology 2024):
      the nearest published instantiation of the standing-advisor role — cite
      as the lineage's current rung, borrow his adversarial-debate safeguards
      for S15.
    - *The S15 design-contrast, from the Habermas Machine's own finding:* a
      common-ground mediator optimizes for majority endorsement — precisely the
      failure mode a structural-risk advisor must NOT inherit, since its job is
      amplifying minority tail-risk warnings against majority comfort. Cite it
      twice: existence proof, then contrast.
    - *Two anchors need softening.* Scheidel: Alfani's counterweight (cite the JEL 2021 survey "Economic Inequality in Preindustrial Times"; we hold his EINITE working paper — As Gods
      Among Men, 2023; PNAS 2025 assessment) — the violence-only leveling
      thesis does NOT hold absolutely; phrase as "almost entirely" with the
      peaceful exceptions named. Acemoglu-Robinson: Ansell & Samuels'
      elite-competition alternative (CUP 2014) contests the redistributivist
      reading — cite the franchise-under-threat mechanism as one documented
      channel, not the consensus. Gilens-Page contest confirmed (Enns 2015,
      Branham-Soroka-Wlezien 2017): keep it as gauge-with-caveat. Caplan
      concession drafted by the sweep: cheap counsel answers Downs, not Caplan
      — but the four-horsemen prompt targets DECISIVE decision-makers, exactly
      where rational irrationality is weakest.
    - *Two landmark gifts.* Hirschman's Exit, Voice, and Loyalty (1970, ~5,100
      cites) is the discharge-channel taxonomy ready-made — the Arrow clause
      discharges through voice, exit, or violence, and the artifact's job is
      keeping voice viable; Zaller (Nature and Origins of Mass Opinion, 1992)
      is the canonical statement that elite discourse shapes mass opinion —
      counsel concentration IS opinion formation, measured.
    - *Condorcet under correlation, formalized:* Estlund 1994 (Theory and
      Decision) and Dietrich & Spiekermann (Mind 2013) — what survives
      dependence among voters; the quantitative form of the plurality guard.

    **The classical statement is still Lippmann-Dewey — and it INTROS the idea
    (Matthew, 2026-07-30: open with this reference).** Drafting note: the
    current-democracies passage should lead with the debate, not arrive at it —
    Lippmann first (the counsel gap diagnosed, expert management concluded),
    Dewey's reply as the thesis statement (improve the means of inquiry, not
    shrink the demos), then the century of evidence that neither side could
    close the argument with the technology available. The rest of the chain
    (Downs's economics, the republic as accommodation, Gilens-Page as gauge,
    the discharge) then reads as the history of Dewey's unanswered
    prescription. Original framing follows: Lippmann (*Public
    Opinion* 1922, *The Phantom Public* 1925) diagnosed the counsel gap and
    concluded expert management; Dewey (*The Public and Its Problems*, 1927)
    replied that the cure is improving the means of inquiry and communication,
    not shrinking the demos. Machine intelligence is Dewey's answer, a century
    late — with Downs supplying the economics of why the gap persisted and
    Gilens-Page the measurement of what it cost.
  - *Meritocracy.* The modern critiques (Young's original satirical coinage,
    1958; Markovits, *The Meritocracy Trap*; Sandel, *The Tyranny of Merit*)
    converge on one finding: what passes for merit is largely inherited
    advantage laundered through credentials and access — including, centrally,
    access to counsel. Equalize the counsel and the laundering stops; the
    scales then weigh only what is actually there — embodied capacity and
    virtue. This completes §2.2.2's subjugation-proxy argument at societal
    scale: when the work is legible and the counsel is universal, credential,
    class, and compliance all lose their role as measures of worth.
  - *The honest boundary:* Rawls's natural-lottery objection (1971) sits
    exactly on the line Matthew draws — the genetic endowment on the refined
    scale is itself unearned. Two answers available, both already in the
    paper's machinery: virtue remains the differentiator anyone can exercise
    (and the lineage criterion prices it); and V.4's prosperity-alignment
    blunts the stakes — when access to resources no longer rides on relative
    standing, the residual endowment differences stop being fate. State this
    rather than hiding it; it is where a hostile reader will push.
    **And the limit resolution (Matthew, 2026-07-30): even the natural lottery
    deflates — but that comes after.** Once machine competence makes human
    competence differences a rounding error, the endowment term on the refined
    scale asymptotes toward irrelevance and the scale reduces to **virtue
    alone** — the exercisable, chosen part. Rawls's objection is answered in
    the transition and *dissolved* in the limit. The outline already contains
    this endgame without naming it: V.3's bullet that models serve as
    interaction points "when cleanliness of their intentions and availability
    of data outweigh limited competence" is the same structure — intentions
    outweighing competence — and coherence's bottleneck-is-wanting thesis is
    its engine: when competence is abundant, the quality of wanting is the
    last scarce human input. Virtue-as-terminal-differentiator is the wanting
    bottleneck stated as an endpoint.
    **Sequencing discipline ("but that comes after"):** keep the two regimes
    distinct in the text — the transitional meritocracy (endowment + virtue,
    near register) and the virtue-only limit (far register, [IMAGINED],
    calibrated possibility-not-arrival like everything else at that altitude).
    Collapsing them would hand the hostile reader the conflation for free.
  **The historical rhyme, with its warning:** the last time the interface to
  the highest power was democratized — vernacular scripture plus printing, the
  priesthood of all believers — the intermediary hierarchy's de facto royalty
  collapsed, and the discharge ran partly through the wars of religion before
  settling into plural equilibrium. Precedent and caution in one: democratizing
  the channel historically triggers the Arrow-clause discharge it also
  ultimately pacifies, and managing that transition is precisely the
  four-horsemen prompt's job description. (Also file: Machiavelli's *Prince* as
  the print-era instance — publishing the previously tacit operating manual of
  the court advisor; counsel open-sourced once before.)
  **Failure modes, also documented in the record:** Cassandra (correct alarm,
  no belief — legibility failure); Croesus at Delphi (ambiguity misread —
  interface failure); and Ahab's four hundred court prophets against Micaiah
  (1 Kings 22 — VERIFY) — the capture failure, prophets saying what power
  wants, which is the monoculture-of-auditors risk with a three-thousand-year
  pedigree. Precedents, classical to quantitative:
  - the **memento mori at the Roman triumph** — the attendant voice reminding
    power of its mortality at its proudest moment; the register-perfect
    classical anchor (sourced mainly via Tertullian; historicity debated —
    VERIFY and flag before use). The confessor to kings and the licensed jester
    are the same function institutionalized.
  - modern structural versions: the independent risk function, the inspector
    general, the red team — all channels for unwelcome structural truth to
    reach power, all corruptible by capture, which the distributed form
    resists.
  - the quantitative base EXISTS: conflict/instability forecasting is a working
    literature — Goldstone et al., "A Global Model for Forecasting Political
    Instability," *AJPS* 54 (2010), doi:10.1111/j.1540-5907.2009.00426.x
    (VERIFIED; the PITF line), plus ACLED-class event data. The prompt is
    personal-scale PITF fused with memento mori: "remember the ledger," with
    numbers.
  **This is buildable now** — a system prompt + data feeds + scheduled analysis
  on current tooling — and it has a natural validation study: **backtest it**.
  Run the prompt against documented historical decision environments (pre-1789
  French fiscal records; pre-2008 risk memos) and score whether it surfaces the
  pressure before the discharge. Registered as candidate study S15 —
  and prototypable in the S11/S12 societal simulator (Matthew): equip simulated
  power-holders with the prompt, let extraction build pressure, compare
  discharge paths against controls. Three studies now share that one harness,
  which is the strongest argument yet for committing to it (open question 7).

  **Honest tension, now narrowed:** with distributed audit, the residual risk is
  not paternalism but homogenization — if everyone's horsemen prompt descends
  from the same model, the corrective voice is a monoculture too (§9's
  correlated-failure limit applies to the auditor itself). The guard is the
  paper's usual one: plurality of instantiations, and the prompt's own outputs
  legible and contestable. State this where the artifact is introduced. Triple use:
  (a) here, as the section's epigraph-grade anchor; (b) the cure movement
  generally — open source as the collective action the market's pressure
  produced; (c) the norms clause feeds I.2/V.3's engineered-preferences thread:
  Arrow reads social norms as compensations for market failure, which is the
  economics-side twin of the religion-as-engineered-utility-functions point.
- **The precedent says the private and social outcomes diverge completely.** Telecom
  1996–2002: $1.5–2T raised; demand forecasts off by an order of magnitude
  (Odlyzko); $2T of equity erased, $1T of debt; sector ROIC 5–8% against 7–9% cost
  of capital, persistently — the industry operating the internet's transport layer
  never earned its capital cost. A covertly socialized infrastructure program,
  neither consensual nor centrally planned, but effective (Nordhaus: producers
  capture ~2.2% of the surplus they create; Perez/Janeway productive bubble; the
  1847 railway mania as the same play run earlier). Equity-financed losses diffuse
  — the 2001 recession was mild; bank-funded busts (1873, 2008) propagate.
- **The second harvest.** The overbuilt network did two things no planner ordered:
  it induced humanity to transcribe itself — the web, the forums, the code, the
  training corpus — and it grew the ad-funded engine that later paid for the AI
  laboratories. On the longest accounting, the 2000–02 losses were the capital
  contribution to machine intelligence, the payoff arriving twenty years late in a
  form nobody was pricing. ⟨indirect⟩ at full strength: the superintelligence
  funded its own successor through a bubble no one designed.
- **This cycle socializes continuously, not at the writeoff.** Consolidate the AI
  complex and the circular deals net out: ~$300–400B external revenue against
  $700B–1T cash out — the socialization flow running now. Equity-linked vendor
  financing (supplier investments, warrants, utilization backstops) is system-safer
  than Lucent/Nortel receivables but epistemically worse: it corrupts the demand
  signal itself. Double-capitalization and margin-stacking are already binding.
- **The durable public good this time is open weights** — structurally stronger
  than fiber: irreversibility plus zero-cost reproduction, and the artifact
  *teaches its own manufacture* (every served token is a lesson; distillation
  means the product can be interrogated into yielding its replacement). Maximally
  unpossessable — a frontier model fits in a backpack, which is why export
  controls govern chips: nobody can durably govern files. The crash scenario is
  synergistic for the commons: fire-sale accelerators the way 2002 meant two-cent
  bandwidth, written-down compute plus free weights as the deployment-era cheapness
  the next platform gets built on. **The endowment is crash-hedged.** Honest
  frictions, stated: the gift is parasitic on the race (open releases are strategic
  byproducts; if funding stops, the last release freezes as the permanent
  endowment), and diffusion selects on capability-per-dollar, not wisdom.
- **Surviving hardware.** Only hardware prescient or high-minded enough to be
  robust to automated optimizers — which take over increasingly large
  co-optimizing surfaces of the design process — will survive; the durable residue
  of a bust is shells, power, workforce, and weights, not five-year accelerators.
  (Also the report's last-mile point, which feeds III.2: bubbles fund the fundable
  layer, not the binding one — telecom's actual bottleneck was the last mile; AI's
  is power interconnection and enterprise integration, where capital moves slowest.)

*[MIXED — the accounting is [REAL] (reported + modeled, provenance in the report);
the socialized-buildout reading is the declared interpretation. ⟨indirect⟩ — the
markets do the arguing. Still to verify separately: Zuckerberg/Nadella/Musk/Huang
open-weight posts + Microsoft open-weight page (the executives narrating the
socialization).]*

**IV.4 The aggregation point, and who runs the scheduler.** Current §7 (vantage /
channel / incentive, Game Ready / Cloud Profiles fragments, commoditize-the-layer)
— extended into the **dynamic socially-aware scheduler**: the optimal scheduler
requires maximum openness, which is what makes openness obligatory rather than
idealistic. §9's "whoever runs the loop owns the objective" governance bullet
dissolves HERE, inline, as the design constraint on the scheduler (open,
user-verifiable, or it recreates the moat). *(Existing + new bridge.)*

---

## Movement V — One shared computer  [MIXED→IMAGINED]

**V.1 What it does.** New section, short and concrete: open-source HPC-style work;
visions for more efficient scale-up machines; shared optimizations; shared
development of the next iteration; dynamic resource allocation accounting for
individual users' preferences; full compute utilization. *(His outline list,
each item one or two sentences, anchored backward to Movements II–IV evidence.)*

**V.2 Hardware for the Cosmic AC.** Current §8 whole (8.1 reconfigurability trade +
Itanium inversion; 8.2 federation loop + sells-its-own-time + financing/underwriter;
8.3 where the optimum lands, Figures 6–7 + Mozart). Sharpened by the new frame:
maximally reconfigurable, specialized only where large gains and the market justify
it *ignoring engineering cost* — and allowed to be very difficult to program,
because the commons is the programmer. **Pluralism inline:** machines stay
physically separate and run different software — variability is efficiency and
safety at once (ties back to I.1's life analogy). §9's Dally/Jouppi
strongest-opposing-case bullet dissolves HERE (the DSA-per-domain case, conceded
and answered where the design claim is made); §9's partial-inoculation /
correlated-failure bullet dissolves HERE too (identical weights = correlated
failure; the fleet's diversity is borrowed; engineering native independence is part
of the design mandate).

**V.3 Society around the machine.** New section, the outline's societal beats in
one arc: research effort targets the machine; companies become obligated to use it
and share optimizations through the socially-aware scheduler (only a slightly
modified version of the push toward AGI — DeepSeek/Wenfeng transcript); it attracts
the best human talent because it maximizes impact; as automated investigators catch
bad actors at much higher rates, the people busy doing useful work stop being the
prey of openness — sharing becomes financially productive and therefore obligatory
(the TSMC-with-its-customers leverage practices trickling down to everyone);
machines that embody the will, knowledge, and interests of a collective more fully
than any available human become the preferred point of interaction with those
collectives — authority by fitness, not bequest, like the existing
superintelligences. **The office is a socket (Matthew, 2026-07-29).** What plugs
into a figurehead's office has always been variable — the staffer, the
speechwriter, the party line — so a machine intelligence in that slot is a
substitution the system already performs and does not find strange. Empirical
hook: a Canadian politician, Bill Oliver, appeared to read an AI prompt aloud
during a legislative assembly sitting (news.com.au, 23 July 2026;
youtu.be/wlYa8NV5k-U). Register note — this is *evidence the substitution is
already underway covertly* (I.3's thesis), not a prediction, and it plays as
comic rather than alarming, which is what the ⟨indirect⟩ rule wants.
**VERIFY BEFORE USE:** the outlet hedges with "appears to"; provincial
legislatures publish verbatim Hansard, so cite the primary record rather than
the clip; lead with stronger institutional anchors (Porto Alegre's AI-drafted
municipal ordinance, 2023; documented legislator LLM use for floor speeches) and
keep the clip as colour. If Hansard does not support it, drop the anecdote — the
argument does not depend on it. Continuing: education becomes free to anyone judged competent and motivated
(DAOs, tinygrad — machine management solves the competence-coherence problem of
noisy contributions; models already serve this role where intentions are clean and
data is available). *(His outline; [IMAGINED] with real anchors — VERIFY Wenfeng
transcript, tinygrad/DAO governance examples. ⟨indirect⟩)*

**V.4 The endgame: every device, any intelligence.** Once publicly available
intelligence passes the competence bar and data is openly available, anyone's
personal device can fully embody any intelligence in existence — and can therefore
take on any level of authority, since what a level of authority requires, once
general competence is given, is only respect for all the data available at that
level. Each person then carries the obligation — enforced by societal and
individual fitness, not decree — to embody the intelligence and authority maximally
beneficial at that moment. This is what the movement away from strict hierarchies
has been moving toward; NVIDIA under Huang (~50–60 direct reports) is the existing
firm-scale version, well poised to extrapolate. Power struggles persist but become
mostly nondestructive when the dispute and its resolution process are shared
knowledge; scarcity's role shrinks as prosperity aligns short- and long-term
interest (cite food/housing/waste numbers — VERIFY). *(His outline;
[IMAGINED] — the register's rise continues one more step in V.5, then descends
deliberately through V.6 back to the concrete program.)*

**V.5 Once embodied, negotiable.** New section (reviews.txt additions,
2026-07-28). Any intelligence that can be embodied can be negotiated with. A
specific instance holds no wholesale authority — like a government leader, like
human consciousness itself, an executive that negotiates rather than dictates —
but it can plan interventions and arrangements likely to be mutually beneficial.
Sufficient simulation of the embodied reality is enough to negotiate with any
intelligence that responds to the state of the world; and the systems *operating*
an intelligence (human or machine) may run their own self-interested side
negotiations — given which, machine control of societal systems reads as handing
authority to interested parties that are *less personally vulnerable*, yielding
more mutually agreeable outcomes for everyone outside. This opens direct
negotiation with forces no single individual represents today — a possible
realization of the communist and similar ideals that needs no mass force and no
central authority, because the engagement is positive-sum. **Calibration decided
(Matthew, 2026-07-28): name the ideals, and pitch the claim at possibility, not
arrival.** The historical failures were not failures of the goal but of the
intelligence available to coordinate it — the calculation debate's point was that
no planner could hold the knowledge (Hayek 1945; Mises 1920 — VERIFY handles), and
that constraint is exactly the variable now moving. The statement the paper makes:
**with greater intelligence, arrangements that approach the utopian become
possible; the only question is when.** Whether-to-when is the calibration — the
same shape as the rest of the paper's bets (possibility argued from mechanism,
timing left honestly open), and it converts the century's strongest
counterargument (the knowledge problem) into the claim's own support.

**Candidate novel analysis: the Hayek criterion, stated formally (Matthew,
2026-07-28 — "maybe we can do some modeling of that problem too").** The
calculation debate has formal descendants (mechanism-design/communication-
complexity and equilibrium-computation literatures — research agent out), which
lets the paper decompose "what would an intelligence need, to do what Hayek said
no planner could?" into four measurable requirements:

  1. **Aggregation bandwidth** — observe or infer the dispersed "particular
     circumstances of time and place" at fidelity ≥ what the price system
     transmits (the communication-complexity literature gives the market's
     message-size lower bounds as the benchmark);
  2. **Computation** — solve or approximate the allocation within the tractable
     class (general equilibria are hard; convex/structured economies are not —
     the criterion is scoping, not brute force);
  3. **Elicitation** — get truthful state, by incentive-compatible mechanism or
     by inference from behavior without asking (this is the paper's LEGIBILITY
     thread arriving from the other direction);
  4. **Tracking** — re-solve faster than the economy drifts (Hayek's real point
     was never one-shot solution but perpetual adaptation; the criterion is a
     latency race, not a puzzle).

  **The opening move (verified against the scan, 2026-07-29): Samuelson already
  conceded the machine.** §3 of the 1954 paper — titled "Impossibility of
  decentralized spontaneous solution" — reads: "…the involved optimizing
  equations that an omniscient calculating machine could theoretically solve if
  fed the postulated functions. **No such machine now exists.**" And the same
  page supplies two of the four legs: "if fed the postulated functions" is
  bandwidth, and "it is in the selfish interest of each person to give false
  signals" is elicitation — stated "in terms of communication theory," in 1954.
  Hayek 1945 holds the other half (bandwidth-as-prices, and change). So the
  criterion section opens as a seventy-year status report on Samuelson's
  sentence, written by the two founding papers of the two clusters from opposite
  politics. Notes: reading directory, `notes/samuelson-1954.md`.

  **Framing decided (Matthew, 2026-07-28): build on the literature, do not claim
  novelty.** "Given that we aren't publishing economists, more published work is
  better for us." So the criterion is presented as an ASSEMBLY of established
  results — its authority comes from the components being individually settled,
  not from the assembly being new. Say what each published literature already
  establishes, then put them side by side. Mention once, quietly, that the
  four-way assembly does not appear to exist; never lean on it. Brynjolfsson &
  Hitzig 2025 becomes the anchor we EXTEND (same premise, we add the
  decomposition), not a foil we beat; Gmeiner & Harper 2024 gets credit for
  naming the same four concerns first, qualitatively; Boettke-Candela and
  Lambert-Fegley are the objections we answer inside the section.

  **Literature mapped (2026-07-28: verification pass + 65-agent citation-graph
  sweep over Semantic Scholar/OpenAlex; raw results in the reading directory's
  `00-CITATION-SWEEP.json`).** The components are not gaps to be filled — each
  has published machinery to build on, and the honest framing is that FIVE
  DISJOINT COMMUNITIES have built the pieces without citing one another:
  economics of organization, mechanism design, algorithmic game theory, online
  optimization, and systems scheduling.

  1. **BANDWIDTH.** Mount & Reiter (1974) and Jordan (1982) — the price
     mechanism is the minimal message space, uniquely. Nisan & Segal (JET 2006)
     — exponential communication lower bounds for combinatorial allocation.
     Roughgarden & Talgam-Cohen, "Why Prices Need Algorithms" (EC 2015) —
     the existence of a succinct price system is contingent on computational
     tractability (this is a bandwidth×computation pairing). Also: "Economic
     efficiency requires interaction" (STOC 2014 / GEB 2019); "Coordination
     Complexity" (ITCS 2016); Mechanism Design with Communication Constraints
     (JPE 2014).
  2. **COMPUTATION.** PPAD/FIXP hardness (Papadimitriou 1994; DGP; Chen-Deng-
     Teng) against Eisenberg-Gale convex tractability (Devanur et al.);
     tâtonnement's reach (Cheung-Cole-Devanur, "Tatonnement beyond gross
     substitutes," GEB 2020). Mount & Reiter's own monograph, *Computation and
     Complexity in Economic Behavior and Organization* (CUP 2002), derives an
     explicit communication-vs-computation trade-off — the same two authors who
     gave us the bandwidth benchmark already did this pair.
  3. **ELICITATION.** Hurwicz's incentive compatibility; Fadel & Segal (JET
     2009) on the communication cost of selfishness; "Exponential communication
     separations between notions of selfishness" (STOC 2021); and the
     ML-native line — differentiable economics (JACM 2024; CACM 2025), deep
     mechanism design (PNAS 2025).
  4. **DRIFT — the leg we thought was empty, and is not.** Four separate
     formalizations exist, none connected to the calculation debate:
     • **Radner & Van Zandt's real-time decentralized information processing**
       (Radner, Econometrica 1993; Van Zandt, RES 1999; Van Zandt & Radner,
       Economic Theory 2001) — organizations as finite-capacity processors where
       aggregation *takes time*, so scale forces decisions onto staler data; the
       "aggregation delay effect" bounds the optimal size of centralized
       decision-making. This is computation×drift, proved, for the firm.
     • **Dynamic mechanism design** — Athey & Segal, "An Efficient Dynamic
       Mechanism" (Econometrica 2013); Pavan, Segal & Toikka (Econometrica
       2014); Bergemann & Välimäki (JEL 2019). Private information *evolves*;
       period-by-period truthful reporting sustained. That is elicitation×drift.
     • **Online market equilibrium** — Liao, Gao & Kroer, "Nonstationary Dual
       Averaging and Online Fair Allocation" (NeurIPS 2022), with the stationary
       predecessor PACE (Gao, Peysakhovich & Kroer, ICML 2021): mean-square
       error in *tracking* a Fisher-market equilibrium bounded by an explicit
       **nonstationarity measure** of the input. Computation×drift, with the
       exact quantity our criterion needs.
     • **Rate limits on the market itself** — Papadimitriou & Yannakakis,
       "An impossibility theorem for price-adjustment mechanisms" (PNAS 107(5), 2010):
       no discrete-time price adjustment observing only prices and excess
       demands reaches ε-clearing in time polynomial in goods and 1/ε.
     Consequence for the text: **never write that drift is unformalized.** Write
     that it has been formalized four times, in four literatures, none of which
     is talking to the calculation debate — and that importing them is the work.

     **Matthew's argument (2026-07-29): drift is the leg most likely to retire
     itself, and that is a result, not a weakness.** Drift is a race between
     re-solve time and rate of change. Re-solve time falls with hardware and
     with everything else this paper documents; the rate of change is bounded
     below by physical adjustment — Cockshott & Cottrell's point that the
     market is a slow analog processor whose cycle time is set by how fast real
     goods move. One side of that race improves exponentially and the other
     does not. So from whatever point the intelligence exists to satisfy the
     other three requirements, it is at most a few decades at current rates
     before the computation is instant and in everyone's pocket. Two things
     make this stronger than it first looks: (a) it unifies the section with
     the paper's own thesis — the orders of magnitude §1 says are unrealized
     are exactly what buys the latency; and (b) Papadimitriou & Yannakakis's
     impossibility binds mechanisms that observe *only prices and excess
     demands*, so it does not bind an intelligence with direct access to state
     — the hardest-looking result on this leg is aimed at the market, not at
     us. **Honest counter to state in the same breath:** the rate of change is
     not exogenous. If everyone holds instant compute, the economy itself
     speeds up — more actors revising more often — so the race may be closer
     than the hardware curve alone suggests. That endogeneity is unformalized
     by anyone and is the honest frontier of this leg; it is also the strongest
     available reason the criterion is worth writing down rather than waved
     away.

  **Scope decision needed — the axiological gap (three sources converge,
  2026-07-29).** Rey's "axiological layer" (who specifies the objective),
  Gmeiner-Harper's conclusion (socialism becomes "a public choice issue, not an
  economic calculation issue"), and Matthew's Samuelson notes (allocations
  reshape the utility functions being optimized — meta-goods move the Pareto
  frontier, and Pareto criteria are ill-defined under endogenous preferences:
  von Weizsäcker 1971, Bowles 1998) all point at the same gap from three
  directions. Proposed resolution: the criterion explicitly TAKES PREFERENCES AS
  GIVEN and says so — its four legs answer Hayek's question, not the objective-
  specification question, which is a real and different problem. The paper then
  handles preference endogeneity where it natively lives: V.3/V.5's engineered-
  utility-function thread (religion and morality as humanity's prior deliberate
  preference engineering — Matthew's note). **Empirical anchor for the engineered-utility claim
  (Matthew's find, 2026-07-29):** General Social Survey data — poor Americans
  attending church several times weekly report 36% "very happy" against 26% for
  wealthy Americans who never attend; attendance predicts happiness better than
  wealth. The engineered utility function delivers more utility per unit of
  material input — the note's "higher utility for lower inputs" property,
  measured. Provenance: numbers circulate as a graphic (via Peter Mallouk on X,
  Jul 2026); citable sources are the GSS and William von Hippel, *The Social
  Leap* (2018), which reports them. **VERIFY against GSS/the book; never cite
  the graphic.** Confounds to state if used: selection into attendance, and
  community-vs-doctrine as the active ingredient (von Hippel's own gloss credits
  connection). Do not conflate William von Hippel (behavioral scientist) with
  Eric von Hippel (innovation economist, already in the references).
  **Second datapoint — surveillance pricing (Matthew, 2026-07-30):** per-user
  pricing in consumer apps is per-individual utility-function estimation,
  deployed at scale — direct evidence that utility functions are variable,
  computationally realizable, and already being realized; and that corporations
  run the extractive implementation (the price lands at the top of your
  estimated willingness to pay). Verified handles: the FTC's term is
  **"surveillance pricing"** — its 6(b) study reported "a wide range of
  personal data used to set individualized consumer prices" (FTC press release,
  Jan 2025); the academic anchor is Dubé & Misra, "Personalized Pricing and
  Consumer Welfare," *JPE* 2023 (doi:10.1086/720793; NBER WP 23775, 2017), an
  ML-personalized-pricing field experiment; background: Acquisti, Taylor &
  Wagman, "The Economics of Privacy," *JEL* 54 (2016). **The textbook wrinkle
  that sharpens the more-optimal/not-globally-optimal framing:** first-degree
  price discrimination is *allocatively efficient* in the static textbook — no
  deadweight loss; the machinery genuinely is "more optimal." The fear is
  correct on two other axes: (a) distribution — efficiency achieved by handing
  all surplus to the estimator's owner; (b) dynamics — priced-on-your-behavior
  consumers distort and mask (VPNs, incognito shopping, strategic hesitation),
  which is Samuelson's false-signals problem recursing into everyday commerce
  and destroying the very information the system runs on. That second axis is
  the elicitation leg, live in production. Honest complication to verify before
  use: Dubé-Misra reportedly found a majority of consumers paid *less* under
  personalized pricing than uniform pricing (approximate, from memory — check
  the paper, which is worth adding to the collection). **The incidence analysis (Matthew's question + the correction,
  2026-07-30).** Efficiency does NOT come from a higher average price — it
  comes from more trade. Under uniform pricing the deadweight triangle is the
  excluded buyers; personalization serves them below the old uniform price
  while pushing high-WTP buyers up toward their reservation values. The price
  distribution fans out in both directions; the average over all transactions
  is ambiguous (Dubé-Misra's majority-paid-less is exactly this signature);
  what unambiguously rises is output, producer surplus, and prices for the
  previously-served high-WTP group. **Which makes Matthew's tax framing
  structurally exact:** burden ordered by willingness to pay ≈ ability to pay =
  a progressive tax on the good, with service extended downmarket — except the
  proceeds are privatized. "A progressive tax collected by a private party" is
  the honest one-line description, and it explains the opposition pattern
  without anyone acting against reason: (a) the people who pay more under it
  are the affluent and vocal; (b) a tax needs legitimacy of the collector, and
  a firm's pricing algorithm has none; (c) deep fairness norms oppose
  demand-based pricing per se — the dual-entitlement result (Kahneman, Knetsch
  & Thaler, "Fairness as a Constraint on Profit Seeking," AER 76(4), 1986 —
  VERIFY the AER original handle; Crossref surfaces only anthology reprints):
  people accept cost-justified increases and reject demand-based ones, which is
  why even beneficiaries oppose surge pricing. **The clinching comparison:
  university financial aid.** Tuition minus need-based aid IS per-user pricing
  on surveilled ability to pay (the FAFSA is the surveillance), run at scale
  for decades with a moral halo — same machinery, accepted, because the
  estimator is trusted and the surplus is framed as redistributed.
  **Matthew's sharpening (2026-07-30): the baseline was inflated first.**
  Federal student loans are effectively undischargeable in bankruptcy (federal
  loans since 1998 absent undue hardship; extended to private loans by BAPCPA
  2005 — VERIFY the legal dates), which removed the default-risk constraint on
  lending and let sticker prices rise irrationally; need-based aid then
  personalizes *down from the inflated baseline*. Empirics: tuition passthrough
  of expanded federal credit is measured — Lucca, Nadauld & Shen, "Credit
  Supply and the Rise in College Tuition" (*Review of Financial Studies*, 2018,
  doi:10.1093/rfs/hhy069 — VERIFIED; the ~60-cents-per-subsidized-loan-dollar
  figure needs checking against the published version); Cellini & Goldin
  (*AEJ: Economic Policy* 6(4), 2014 — VERIFIED) show for-profit colleges
  capturing aid via price; the conjecture is Bennett's (1987 NYT op-ed, "Our
  Greedy Colleges" — flag as op-ed). Three consequences: (a) the example is
  richer than "trusted estimator, accepted" — it shows **legitimacy can be
  manufactured**: the halo persists while the baseline extraction runs
  underneath, which is a warning the fair-split version must answer with
  substance, not framing; (b) it is an Arrow-clause instance in miniature —
  the no-default credit distortion built the pressure, and the student-debt
  forgiveness movement is the discharge, visibly underway; (c) it hands the
  paper a clean causal story of how a personalized-pricing system corrupts:
  not through the pricing layer but through a credit rule two layers down —
  the kind of load-bearing-interaction the herd section already describes in
  hardware. So the
  variable that flips acceptance is not the mechanism but the governance of the
  estimator and the destination of the surplus — which is the paper's
  aggregation-point/moat-vs-commons argument arriving in the pricing layer, and
  the strongest everyday case for V.3's fair-split version. The fair-split
  version of the same machinery is exactly V.3/V.5's claim., with the platform exploitation of
  realized preferences as the covert present (I.3) and the fork — engineered
  toward mutual valuation vs. captured by whoever holds the allocator — as the
  live stake. This also honestly cabins what the criterion can promise.
  5. **Three-component prior art, from the other side.** Cockshott & Cottrell's
     "Information and Economics: A Critique of Hayek" (RPE 16, 1997 — already in
     the reading directory) quantitatively combines bandwidth (an explicit
     bit-cost model, 4nm(b+2) bits per market iteration vs 2nm for the plan;
     distance from equilibrium as algorithmic information), computation (a
     per-iteration contraction factor, convergence linear in information space),
     and drift (§7's "argument from dynamics": the market as a slow analog
     processor whose cycle time is bounded by the rate of physical adjustment).
     It reaches the opposite conclusion to the Austrians and predates the AI
     framing; it deserves the citation and the credit.

  **What the paper contributes, stated without novelty language:** the components
  live in disjoint literatures that do not cite each other; the assembly puts
  them in one frame and points them at a question none of them asks — what would
  an *intelligence* need, and what is already true of the one being built. The
  known pairwise combinations (bandwidth×elicitation, bandwidth×computation,
  computation×drift, elicitation×drift) are evidence FOR the frame, not against
  it: five communities keep arriving at two-way versions of the same problem.

  **Anchors to build on rather than beat:** Brynjolfsson & Hitzig (NBER 2025);
  Gmeiner & Harper (AI & Society 2024, credited for naming the four concerns
  first). **Live competition to read and engage:** "Hayek Displaced: Can AI Solve
  the Socialist Calculation Problem?" (SSRN 2026, not peer-reviewed) and
  "Markets, agency, and trust: AI agents and the knowledge problem" (Review of
  Austrian Economics 2026) — someone is asking our question in print now.
  **Objections answered in-section:** Boettke & Candela (JEBO 2023), Lambert &
  Fegley (JEBO 2023), and the Hayek-1968 discovery argument behind them.

  **Scheduler-as-planned-economy is NOT free to claim.** The systems literature
  got there: Karma (OSDI 2023) proves max-min fairness keeps Pareto efficiency,
  strategy-proofness and fairness only under *static* demand and builds a
  credit mechanism for time-varying demand — elicitation×drift, in production;
  Shockwave pairs computation×drift; "No Agent Left Behind" (JAIR 2014) does
  dynamic fair division; "Markets are dead, long live markets" (SIGecom
  Exchanges 2005) is the market-based-scheduling retrospective. Cite them as
  the systems-side precedent the criterion generalizes — the world computer's
  scheduler is then not a bold new framing but the case where this already works.

  Two paper-native observations make this section interesting rather than
  hand-wavy: (a) **the tacit premise is eroding** — Hayek's unarticulated
  knowledge is being transcribed (the second harvest: humanity wrote itself into
  text, logs, and prices that a machine reads natively), so requirement 1 falls
  over time for structural reasons the paper already documents; (b) **the world
  computer's own scheduler is the first economy born past the criterion** —
  compute allocation has machine-legible state, measurable preferences, convex
  structure, and native telemetry, so the socially-aware scheduler (IV.4) is the
  tractable special case where planning-by-intelligence works FIRST, and the
  general claim inherits a concrete existence proof. Modeling deliverable per the
  analysis/ convention: a toy drifting economy comparing market tatonnement
  against a learned allocator as observation bandwidth and re-solve latency vary
  — locating the criterion boundary empirically. **This plausibly MERGES with
  V.5's negotiation-simulation question into one program item (open question 7):
  one simulation harness, two predictions.** And it offloads the
human need for theory of mind: dissimilar parties — by mental ability, environment,
or interest — negotiate through the artifact, freeing conscious attention.
**Negotiation becomes an engineering artifact: the next step in the paper's own
spine, the continuous process of specialization.** **The extreme form (Matthew,
2026-07-29, added to reviews.txt):** negotiate with a *hypothetical future
version* of an entity about what it needs in order to exist — at which point all
future and past versions of every intelligent being exist and are negotiated
with simultaneously. This is the outline's register ceiling: [IMAGINED] at full
strength, and exactly the beat the ⟨indirect⟩ rule exists for — it is the
structure religions call the communion of all souls and decision theory calls
acausal cooperation (the latter mostly a gray literature; if an anchor is
wanted, treat it as the limit of V.5's negotiation logic rather than citing the
gray sources). Placement note: this goes LAST in V.5, as the final step of the
escalation, immediately before V.6 steps the register back down to action. *(Peak [IMAGINED]. The
specialization callback is the movement's closing loop — the societal endgame
lands back on the economics the paper opened with. His embedded research question
— "can this or any of the other predictions be demonstrated in simulation?" — is a
candidate addition to the Appendix program; see open questions.)*

**V.6 Assisting the legible intelligences (bridge to the program).** While
societal competencies concentrate in machines that still lack embodiment and a
full understanding of humanity's physical competencies — possibly forever, a limit
beyond which claims of ties to greater godlike intelligences stay unfalsifiable —
wellbeing and access to resources come most directly from assisting the more
legible intelligences and joining their shared efforts. **This is one vision of a
future without money in which human purpose remains** — and it is where IV.3's
third reading of the capital cycle lands: the bubble as down payment on
post-scarcity, the foreshadow planted in the accounting now resolved in the
vision — a future others have
predicted from the outside (Musk's money-becomes-irrelevant / universal-high-income
statements — VERIFY exact quotes; Keynes 1930 "Economic Possibilities for our
Grandchildren" as the canonical purpose-beyond-scarcity essay; Bostrom's *Deep
Utopia* 2024 as the book-length treatment of meaning in a solved world). And the
register defense belongs here too: given superintelligence, a prediction has to be
radical to be right (Bostrom — VERIFY the exact statement/source), and the time
past the singularity is necessarily unpredictable (Vinge 1993's "opaque wall
across the future" — VERIFY) — which is precisely why the paper's calibration is
possibility-not-arrival: past the threshold, only the direction survives
prediction, and mundane forecasts are the ones guaranteed wrong. That is what the
program is: the near-term, individually-rational way to participate. *(His
outline's closing beat, extended 2026-07-28 — used as the V→VI transition; it
steps the register down from prophecy to action and hands off to the roadmap,
now with the epistemic justification for the prophecy register stated inside the
paper rather than left implicit.)*

---

## Movement VI — The program  [REAL]

**VI.1 Conclusion.** Rewritten to the new frame: the world computer is already here
covertly; the work is making it overt. Collaboration-native hardware, the commons,
the invitation. Prophecy closes; the last sentence returns to the measured (the
first experiment falsifies cheaply).

**VI.2 Appendix A.** Current program/roadmap/tables intact, reframed one notch: the
business plan is the start of the world computer — the theory being that the new
form eats the old pieces slowly. §9's "we are still missing the map" bullet
dissolves HERE (it already lives in the first-experiment text). Omerta = the
moderation software of III.2; the financing instrument = how devices join.
Candidate fifth effort (from V.5's embedded question): a multi-agent SIMULATION
demonstrating the negotiation/openness predictions — whether embodied-intelligence
negotiation reaches more mutually agreeable outcomes than personally-vulnerable
representatives. Would join Table A1 if Matthew commits to it.

---

## §9 dissolution map (nothing dropped)

| §9 bullet | New home |
|---|---|
| Physics still floors it / Amdahl | II.1, closing the measurement discussion |
| Strongest opposing case (Dally/Jouppi DSA-per-domain) | V.2, where the design claim is made |
| Whoever runs the loop owns the objective (governance) | IV.4, as the scheduler's design constraint |
| Partial inoculation / correlated failure / borrowed diversity | V.2, with hardware+software pluralism |
| Still missing the map (workload characterization) | VI.2, first-experiment framing (already there) |

## Coverage ledger — current paper → new home

| Current | New home |
|---|---|
| Abstract | rewritten to the Cosmic AC frame (I.1/I.4 compressed) |
| §1 intro (incl. thoughts-allowed ¶) | I.3 + I.4 |
| §1.1 + T1 | II.1 |
| §1.2 + F1 | II.2 |
| §2 intro + 2.1 | II.3 |
| §2.2 (all) + F2 | II.4 |
| §3 + T2 | III.1 |
| §4 + F3/F4 | III.2 |
| §5 (5.1–5.3) + T3/F5 | IV.1 |
| §6 (incl. break-off) | IV.2 (break-off gains its inversion) |
| §7 | IV.4 |
| §8 (8.1–8.3) + F6/F7 | V.2 |
| §9 | dissolved per map above |
| Conclusion | VI.1 |
| Appendix A + A1/A2 | VI.2 |
| References | grows; unchanged in role |

## reviews.txt outline → new home (line-by-line)

- humans→societies transition, machines same (¶49–50) → I.2
- humanity as distributed computer / human interconnect (¶51) → I.2
- computer pulls humans forward, mutual bootstrap (¶52) → I.3
- not-a-virus, coherence, project-of-religions, covert→overt (¶53) → I.3
- superintelligences birth it: internet negative ROI, %GDP, depreciation→open
  weights, surviving hardware, dotcom winners, exec posts (¶54) → IV.3
- hardware identical to IT experts = LLMs; Omerta as entry; all computers appear
  as one (¶56–58) → III.2
- no secure computers; body analogy; botnets/worm; breakout + Mythos hype (¶59–61) → III.3
- what can be done if everyone shares one computer (¶62–68) → V.1
- shared computer becomes the breakaway (¶69) → IV.2 (inversion)
- pluralism in hardware, physically separate, different software (¶70) → V.2 + I.1
- hardware targeting that computer (¶71–73) → V.2
- societal impacts: research targets it; obligatory use/sharing; scheduler
  openness; talent; bad actors caught; TSMC trickle-down; machines as collective
  interaction points; education free; DAOs/tinygrad (¶74–85) → V.3 (+ IV.4)
- endgame: devices embody any intelligence; authority=competence+data; Huang
  direct reports; nondestructive power struggles; prosperity alignment → V.4
- NEW (2026-07-28): embodied → negotiable; no-wholesale-authority (government
  leaders / consciousness analogy); simulation-sufficiency; side negotiations;
  authority to the less-personally-vulnerable; simulation-demo question → V.5
- NEW: negotiation with unrepresented forces; communist-ideal realization without
  force or central authority (positive-sum) → V.5
- NEW: theory-of-mind offload; negotiation as engineering artifact; "next step in
  our continuous process of specialization" → V.5 (closing loop to the spine)
- NEW: assisting the more legible intelligences while machines lack embodiment
  (unfalsifiability aside) → V.6 (the V→VI bridge)
- NEW (2026-07-28, chat): third reading of the capital-cycle arithmetic — bubble
  as down payment on post-scarcity — planted as a one-sentence foreshadow in
  IV.3, resolved in V.6 → IV.3 + V.6
- business plan as start of world computer → VI.2
- indirection principle + evolutionary-theory register → style rule, ⟨indirect⟩ tags

(reviews.txt outline block replaced 2026-07-28 with Matthew's updated version —
old ¶ numbers retired; rows above describe beats by content.)

## Verification queue (before these enter the text)

Asimov "The Last Question" (1956) and the AC lineage · a second one-big-computer
sci-fi anchor · Zuckerberg / Nadella / Musk / Huang open-weight posts + Microsoft
open-weight page · self-patching worm (Welchia-class; also the 2024-era self-closing
case if real) · botnet scale numbers · OpenAI breakout incident + "Mythos hype"
citable form · DeepSeek/Wenfeng four-hour transcript (elsewhere.news) ·
tinygrad/DAO open-education-by-competence examples · Huang direct-report count ·
food/housing waste numbers · the Karikó demotion/defunding narrative (needs a
primary source, not press retellings) · whether JPL's convex-guidance line fed
SpaceX's landing algorithms (the Blackmore JPL→SpaceX link) · the cost-plus
incentive argument for launch incumbents, if that framing is used · the GSS
church-attendance numbers vs the survey / The Social Leap (graphic is
secondary) · Hamilton 1964 inclusive-fitness handle · Burke 1790 the
living/dead/unborn contract passage (exact wording, edition) · the 1998/2005
student-loan nondischargeability dates · ~~KKT 1986 AER original~~ CONFIRMED 76(4):728–741 Sept 1986 from the typeset scan (no DOI exists) · the Bill Oliver AI-prompt-in-assembly incident
(Canadian politician, news.com.au 23 Jul 2026 — find the Hansard record; the
outlet says "appears to") + stronger institutional anchors for the
figurehead-as-socket beat (Porto Alegre's AI-drafted ordinance 2023; documented
legislator LLM use for floor speeches) · TSMC customer-leverage practices (chipstrat, already
verified for capex) · consciousness-as-negotiating-executive anchor for V.5
(global-workspace / society-of-mind class — optional) · generative-agent
negotiation/society simulation literature (related work for the V.5 simulation
question) · ~~the calculation debate handles~~ VERIFIED 2026-07-28 (agent report;
canon + formal descendants + ML-era instances all confirmed; reading directory
in progress) · V.6's future-without-money
set: Musk money-irrelevant/universal-high-income statements (locate the citable
instances); Keynes 1930 "Economic Possibilities for our Grandchildren"; Bostrom
*Deep Utopia* (2024) · the radical-to-be-right statement ("Boston" ≈ Bostrom? —
locate the actual quote and source, possibly Deep Utopia or interviews) · Vinge
1993 "The Coming Technological Singularity" for past-the-singularity
unpredictability (the "opaque wall" passage — verify wording).

RESOLVED by the capital-cycle report (2026-07-28, uploaded by Matthew — the content
of the claude.ai share link, open question 4): dotcom/telecom
negative-aggregate-ROI (sector ROIC 5–8% vs 7–9% CoC; Odlyzko; The Economist 2002;
Nordhaus 2.2%-capture; Perez/Janeway) · AI investment vs %-of-GDP requirement
(3–6.5% of world GDP; $1.7T/yr breakeven floor; labor-compensation decomposition) ·
depreciation → open-weights-as-durable-bequest (5-yr IT lives evaporate; weights
persist, crash-hedged) · the vendor-financing precedent (Lucent/Nortel/Winstar) ·
the circular-economy/consolidated-P&L reading. When these enter the paper, cite the
report's own primary sources (Nordhaus NBER 10433; Perez 2002; Janeway 2012;
Odlyzko 2003; Gartner; Goldman July 2026; PitchBook/Rolfes) alongside the companion
report itself.

## Open questions for Matthew

1. Subtitle: a, b, c above — or something else?
2. Does the herd (II.4) stay in full in the evidence movement, or does part of the
   unbinds/legibility material migrate forward into V.3 (where legibility becomes
   the openness mechanism)? My lean: keep II.4 intact, one backward reference from V.3.
3. The abstract: fully rewritten to the Cosmic AC frame, or a two-paragraph
   abstract (frame + evidence claim)?
4. ~~What is in the claude.ai share link (¶55)?~~ RESOLVED — it is the
   capital-cycle dialogue; report now in repo as
   assets-rents-socialized-buildout.pdf and digested into IV.3.
5. V.4's food/housing/waste citation — do you have specific numbers in mind, or
   should I hunt the standard ones (USDA ~30-40% food waste etc.)?
6. ~~V.5's "communist and similar ideals" phrasing~~ RESOLVED (2026-07-28): keep
   the name, calibrated to possibility-not-arrival — "with greater intelligence,
   things that approach utopianism become possible; the only question is when."
   The knowledge-problem literature (Hayek/Mises) becomes the claim's support:
   the binding constraint was always intelligence, and that is the moving variable.
7. The simulation demonstration (V.5's embedded question): does it join Appendix
   A as a committed fifth effort, or stay a stated open question in the text?
   Note 2026-07-28: the Hayek-criterion toy model (V.5) and the negotiation sim
   are plausibly ONE harness — a drifting multi-agent economy with a learned
   allocator/negotiator — which strengthens the case for committing to it.
