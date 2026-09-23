# Software Economies and the Knowledge Problem — reading list (open-access PDFs)

Downloaded from arXiv / author pages / institutional repositories / NBER /
nobelprize.org / mises.org / course mirrors of classics. Two clusters behind the
**Cosmic AC** paper (`~/performance_commons`): **(A)** the economics of software as
a public good — the literature §2.1 of the current paper is built on, and the
"trend with a forty-year record" it extends; **(B)** the socialist-calculation
debate and its formal descendants — the literature behind the planned **Hayek
criterion** section (outline V.5 in `~/performance_commons/outline-cosmic-ac.md`):
what an intelligence would need — bandwidth, computation, truthful elicitation,
drift-tracking — to do what Hayek said no planner could. The headline from the
verification pass: **no prior work assembles the four-part criterion; the drift
component is unclaimed by anyone** (see the outline for the full novelty table).
Handles verified by research agents 2026-07-28; version-number traps at the
bottom.

**Reading order:** the numbered sequence within each cluster is the recommended
order — each cluster is arranged as an argument, not alphabetically. For a fast
first pass, read the ★★★ entries in numbered order (12 papers), then ★★ on
demand, ★ for context.

**Importance tiers.** Assigned 2026-07-28 by a 52-agent review pass: one Opus
agent read each PDF and scored three factors independently — relevance to this
project, standing in its own field, publicly recognized quality — then a
calibration pass normalized across all 51 (composite = 0.5×relevance +
0.3×standing + 0.2×quality; tiers cut at the natural composite gaps, not by
quota). Scores and rationales: `00-RANKINGS.json`.
- ★★★ (27) — structurally load-bearing *and* high standing. Composite ≥ 8.5.
- ★★ (36) — strong on at least one factor. Composite ~7.2–8.4.
- ★ (21) — context, background, or secondary instances. Composite ≤ 7.0.

**All 74 have now been through the review pass** (round 1: 51 papers, 2026-07-28;
round 2: the 23 later additions, 2026-07-29, calibrated against round 1's
composites so both halves sit on one scale). Counts verified against the
directory. Round 2 also re-tiered five round-1 entries — Cockshott-Cottrell 1997
and Eisenberg-Gale 1959 promoted to ★★★, Fadel-Segal and Devanur raised within
★★, Dapprich-Greenwood reconciled down to ★ — each marked `retiered` in
`00-RANKINGS.json` with its reason.

**★★★ fast path, in reading order:** Samuelson 1954 → Arrow 1969 → Mises 1920 →
Lange & Taylor 1938 → Hayek 1945 → Hayek 1937 → Hayek 1940 → Hayek 2002 →
Cockshott-Cottrell 1997 → Mount-Reiter 1973 → Nisan-Segal 2006 → Segal 2006 →
Dobzinski-Nisan-Oren 2014 → Scarf 1973 → Papadimitriou 1994 →
Daskalakis-Goldberg-Papadimitriou 2009 → Chen-Deng-Teng 2009 →
Papadimitriou-Yannakakis 2010 → Roughgarden-Talgam-Cohen 2015 →
Eisenberg-Gale 1959 → Radner 1993 → Pavan-Segal-Toikka 2014 → Borg 2015 →
DRF 2011.

**For the drift leg specifically** — still the thinnest of the four, and the one
the paper's contribution most depends on: Bergemann-Välimäki 2019 (survey) →
Radner 1993 → Van Zandt 1999 (the only sharp threshold theorem) → Van Zandt &
Radner 2001 → Athey-Segal 2013 → Liao-Gao-Kroer 2022 (the only explicit drift
budget) → Papadimitriou-Yannakakis 2010 → Karma 2023 (the only measured drift
magnitudes from production).

**Read as if ★★★ regardless of tier — the two modern opponents.**
Brynjolfsson-Hitzig 2025 and Boettke-Candela 2023 score 7.7 (their standing is
dragged by draft/heterodox-venue status), but they are the paper's named foils:
the same-premise-no-criterion chapter, and the sharpest form of the discovery
objection. Required for drafting the positioning.

## A. Software economies — the commons that already exists

*The chain the paper's §2.1 walks: under-provision is formally modeled → open
provision wins for complex goods → commons form when private benefits ride along
→ it has already happened twice (publicly and vendor-funded) → and it is
chronically under-carried.*

1. ★★★ **samuelson-1954-pure-theory-public-expenditure.pdf** — REStat 36(4):387–389.
   Three pages that define public goods; under-provision when no actor captures
   the aggregate benefit. The paper's central claim is an instance.
2. ★★ **akerlof-1970-market-for-lemons.pdf** / ★★ **coase-1937-nature-of-the-firm.pdf**
   / ★★★ **arrow-1969-organization-economic-activity.pdf** — the missing-markets
   trio: quality unverifiable to the buyer unravels the market; transaction
   costs; market vs. nonmarket allocation. Why the optimization market is missing.
3. ★★ **simon-1956-rational-choice-environment.pdf** — Psych Review 63(2).
   Satisficing; why the equilibrium selects "good enough."
4. ★★ **johnson-2001-economics-of-open-source.pdf** — WP version of Johnson, JEMS
   11(4) 2002. The formal model: private provision of open source under-provides
   in equilibrium, free-riding and duplication together. §2.1's load-bearer.
5. ★★ **bessen-2005-complex-public-goods.pdf** — WP of the 2006 Elsevier chapter.
   Open provision beats proprietary exactly for complex goods with heterogeneous
   uses — maps onto per-workload optimization.
6. ★★ **vonhippel-2003-private-collective-innovation.pdf** — Org Sci 14(2) preprint.
   The "private-collective" middle regime: contributors capture private benefits
   tied to producing the public good. When the commons does get provisioned.
7. ★★ **varian-2004-system-reliability-free-riding.pdf** — the effort-technology
   taxonomy (total-effort / weakest-link / best-shot). Optimization is best-shot:
   one good kernel serves everyone — provision concentrates in the most capable
   agent. Hold that thought for when the most capable agent stops being human.
8. ★★ **lerner-2002-simple-economics-open-source.pdf** — NBER w7600 (JIE 2002).
   Career-concern/signaling economics of contribution.
9. ★ **dongarra-1995-linear-algebra-libraries.pdf** — LAWN 58, tech-report twin of
   the SIAM Review 37(2) article (variant title, same text). The forty-year
   performance commons: EISPACK→BLAS→LAPACK. The paper's "it already happened,
   publicly funded" exhibit.
10. ★★ **chetlur-1410.0759-cudnn.pdf** — NVIDIA's own stated rationale for giving
    cuDNN away: kernel optimization is "difficult and time-consuming" and must
    be redone as architectures evolve. The vendor-funded commons in primary form.
11. ★ **eghbal-2016-roads-and-bridges.pdf** — Ford Foundation, 143pp. Digital
    infrastructure as unseen, under-maintained volunteer labor.
12. ★ **woodside-2007-future-of-spe.pdf** — FOSE/ICSE 2007. The field's own
    concession: performance engineering routinely skipped for lack of
    demonstrated economic justification. (Copy is a university teaching mirror
    of the IEEE paper — swap for the IEEE version via library if it becomes
    load-bearing.)
13. ★ **fursin-2009-collective-optimization.pdf** — HiPEAC 2009, earlier version of
    the TACO 2010 article the paper cites. Built the optimization commons before
    there was machine intelligence to fill it. (TACO version is bronze-OA at the
    ACM DOI — browser-save works; curl is bot-blocked.)
14. ★ **nagle-2019-oss-firm-productivity.pdf** — HBS WP 15-062 (pub. Mgmt Sci 2019
    under a new title). Measured firm returns to OSS; capture requires
    complementary capability.
15. ★★ **hoffmann-2024-value-of-open-source.pdf** — HBS WP 24-038. The $4.15B
    supply-side vs ~$8.8T demand-side value estimate the paper cites.
16. ★ **keynes-1930-economic-possibilities.pdf** — the canonical
    purpose-beyond-scarcity essay; feeds V.6's future-without-money vision.

## A. Preferences, clubs, and the free-rider answer
*(Added 2026-07-29 from the Samuelson notes session — `notes/samuelson-1954.md`
maps each of Matthew's reading notes to these. Hand-tiered on the standard
scale.)*

61. ★★ **buchanan-1965-clubs.pdf** — *Economica* 32(125):1–14. Club goods: the
    continuum between Samuelson's polar private and collective goods. The
    canonical answer to "there is no such thing as a pure collective or private
    good."
62. ★ **leibenstein-1950-bandwagon-snob-veblen.pdf** — *QJE* 64(2):183–207.
    Interdependent utilities — bandwagon, snob, Veblen. Utility depends on
    others' allocations; with Hirsch's positional goods, the economics of
    exclusivity-valued-per-se (moats as positional goods).
63. ★ **galbraith-1958-dependence-effect.pdf** — the *Affluent Society* chapter:
    production creates the wants it satisfies. One half of the exchange with:
64. ★ **hayek-1961-non-sequitur-dependence-effect.pdf** — *Southern Economic
    Journal* 27(4):346–348 (anthology-reprint typescript, not page images).
    Hayek's three-page reply: learned wants are not therefore illegitimate. The
    same author anchoring both clusters, here on the endogeneity question.
65. ★★ **weizsacker-1971-endogenous-tastes.pdf** — *JET* 3(4):345–372 (author
    offprint, MPI archive). Welfare criteria when tastes change with
    consumption — the formal version of "meta-goods move the Pareto frontier."
66. ★★ **bowles-1998-endogenous-preferences.pdf** — *JEL* 36(1):75–111. The
    survey: markets and institutions select preferences, not just allocations.
    Load-bearing for the outline's axiological scope decision.
66b. ★★ **stigler-becker-1977-de-gustibus.pdf** — *AER* 67(2):76–90 (JSTOR
    scan, retrieved by Matthew). The fixed-preferences pole: tastes are stable
    and common; apparent preference change is price and capital effects in
    household production. The position the endogeneity argument must answer —
    and note their move survives partially: much "preference change" IS
    consumption capital, which matters for the engineered-utility thread
    (engineering the capital vs engineering the function).
67. ★★★ **groves-ledyard-1977-free-rider.pdf** — *Econometrica* 45(4):783–809.
    "A Solution to the 'Free Rider' Problem" — the formal answer to Samuelson's
    false-signals pessimism, twenty-three years later. With #68, the
    elicitation leg's origin story; its known fragilities (budget balance,
    collusion) are part of that story.
68. ★★ **clarke-1971-multipart-pricing.pdf** — *Public Choice* 11:17–33. The
    pivotal (Clarke) mechanism — demand-revealing taxation, independently the
    other half of the Samuelson answer.
69. ★★ **crawford-sobel-1982-strategic-information.pdf** — *Econometrica*
    50(6):1431–1451. Cheap talk: with misaligned interests only coarse,
    partial-pooling communication survives — clear signaling is literally
    non-optimal for the sender. The formal home of "deception hides in noise."

## B. The knowledge problem — canon

17. ★★★ **mises-1920-economic-calculation.pdf** — official Mises Institute edition of
    the 1920 essay (Adler transl.; original pages 86–121). No prices for
    producer goods → no rational calculation. The debate's opening move.
17b. ★ (background/archive — **retired 2026-08-16**, superseded by 17c/17d, the
    RES originals with clean text) **lange-taylor-1938-economic-theory-of-socialism.pdf** — Lange &
    Taylor, *On the Economic Theory of Socialism*, ed. Lippincott, Univ. of
    Minnesota Press 1938 — the book version of the two *Review of Economic
    Studies* articles (4(1):53–71, 1936; 4(2):123–142, 1937), plus Taylor's
    1929 AEA address and Lippincott's introduction. The trial-and-error Central
    Planning Board as Walrasian auctioneer: the position everything in the
    "formal descendants" sections was built to test. **The RES originals are now on disk (17c/17d) — cite and quote
    those; this book is a *revised* text (attribute nothing across editions), an
    image-only archive.org DLI scan of unclear rights. Reading copy only.**
18. ★★★ **hayek-1945-use-of-knowledge.pdf** — AER 35(4):519–530. Dispersed "knowledge
    of the particular circumstances of time and place"; prices as the economizing
    telecommunication system. The paper the criterion is named for — note his
    real emphasis: "economic problems arise always and only in consequence of
    change." That is the drift component, and nobody has formalized it.
19. ★★★ **hayek-1937-economics-and-knowledge.pdf** / ★★★ **hayek-1940-socialist-calculation-competitive-solution.pdf**
    — equilibrium as division of knowledge; the direct anti-Lange reply. (Chapter
    extracts from the mises.org *Individualism and Economic Order* PDF — 1948
    reprint pagination, not Economica's.)
20. ★★★ **hayek-2002-competition-discovery-procedure.pdf** — QJAE 5(3) Snow
    translation of the 1968 Kiel lecture. The strongest objection the criterion
    must scope against: competition *generates* knowledge that does not
    pre-exist to be transmitted. Boettke-Candela (below) press exactly this.

## B. The formal descendants — mechanism design / communication

*The calculation debate became measurable here: the criterion's bandwidth and
elicitation components.*

21. ★★ **hurwicz-2008-guard-the-guardians.pdf** + ★★ **myerson-2008-mechanism-design-perspectives.pdf**
    — the two Nobel lectures; Myerson explicitly roots mechanism design in the
    Hayek–Lange debate. Read first as the guided tour.
22. ★★★ **mount-reiter-1973-informational-size-message-spaces.pdf** — Kellogg DP #3,
    the discussion-paper twin of JET 8(2) 1974. Message-space dimension as the
    communication cost measure; prices are minimal among Pareto-satisfactory
    mechanisms.
23. ★★ **jordan-1979-competitive-allocation-informationally-efficient.pdf** — UMN DP
    79-108, twin of JET 28(1) 1982. Uniqueness: any informationally minimal
    efficient mechanism *is* Walrasian. Hayek's efficiency claim, proved.
24. ★★★ **nisan-segal-2006-communication-requirements-prices.pdf** — JET 129(1).
    Exponential communication lower bounds for efficient allocation; supporting
    prices as the minimal certificate. The modern quantitative bandwidth bound —
    the benchmark an intelligence's aggregation must clear.
25. ★★★ **segal-2006-communication-in-economic-mechanisms.pdf** — the World Congress
    survey, explicitly Hayekian framing.
26. ★★ **fadel-segal-2009-communication-cost-of-selfishness.pdf** — JET 144(5). The
    *extra* communication incentive compatibility costs — the only quantitative
    pairwise combination of criterion components in print.

## B. The formal descendants — computation

27. ★★★ **papadimitriou-1994-parity-argument-ppad.pdf** — JCSS 48(3). Defines PPAD.
28. ★★★ **daskalakis-goldberg-papadimitriou-2009-complexity-of-nash.pdf** — CACM
    expository version. Nash is PPAD-complete: intractable even with all
    information centralized. Computation is a separate wall from bandwidth.
29. ★★★ **chen-deng-teng-2009-two-player-nash.pdf** — arXiv 0704.1678 (JACM 56(3)).
    Hardness at two players; no FPTAS unless PPAD ⊆ P.
30. ★★★ **eisenberg-gale-1959-consensus-subjective-probabilities.pdf** — Ann. Math.
    Stat. 30(1):165–168. The tractable island: linear-utility Fisher equilibria
    as one convex program.
30b. ★★★ **scarf-1973-computation-economic-equilibria.pdf** — Cowles Monograph 24
    (259pp, free from Cowles; image-only scan). The pre-history of the whole
    computation leg: Scarf's simplicial algorithm made general-equilibrium
    computation a subject at all, decades before anyone proved how hard it is.
    Context for #27–31 rather than a source we cite.
31. ★★ **devanur-2008-market-equilibrium-primal-dual.pdf** — JACM 55(5). Poly-time
    market equilibrium in the convex class. With 27–29: the criterion's
    computation component is *scoping* — convex economies tractable, one class
    up PPAD-complete, general FIXP-hard.

## B. Drift, dynamics, and the pairwise assemblies
*(Added 2026-07-28 from the 65-agent citation sweep. The drift leg turned out
not to be empty: it has been formalized four times, in four literatures, none
of which talks to the calculation debate. These are the papers to build on.)*

44b. ★★★ **radner-1993-organization-decentralized-information-processing.pdf**
    — Radner, *Econometrica* 61(5):1109–1146. The founding paper of the
    real-time-processing line: organizations as networks of finite-capacity
    processors with delay as a first-class cost. Read before #45–46, which
    extend it. (**File replaced 2026-08-16**: the JPASS publisher copy with a
    clean text layer overwrote the July image-only scan — this entry and the
    2026-08-16 entry below describe the same, single file.)
45. ★★★ **vanzandt-1999-realtime-decentralized-information-processing.pdf** —
    Van Zandt, *RES* 66(4):633–658. Organizations as finite-capacity processors
    where aggregation *takes time*, so decisions run on data of heterogeneous
    lags; decentralization does not unambiguously reduce delay. Drift and
    computation, coupled and proved, at the scale of the firm. **Image-only
    scan — no text layer; OCR if you need to grep it.**
46. ★★ **vanzandt-radner-2001-realtime-processing-returns-to-scale.pdf** —
    *Economic Theory* 17:545–575. The "aggregation delay effect" breaks the
    replication argument for nondecreasing returns and bounds the optimal size
    of centralized decision-making. The nearest thing in print to a drift
    theorem for coordination.
47. ★★ **liao-2022-nonstationary-dual-averaging-fair-allocation.pdf** —
    Liao, Gao & Kroer, NeurIPS 2022 (arXiv:2202.11614). Mean-square error in
    *tracking* a Fisher-market equilibrium, bounded by an explicit
    **nonstationarity measure** of the input, recovering the i.i.d. bound as a
    special case. The exact quantity the drift criterion needs, already written
    down — for a toy economy, never connected to Hayek.
48. ★★ **gao-2021-online-market-equilibrium-fair-division.pdf** — the
    stationary predecessor (PACE, ICML 2021). Read for the setup; #47 is the
    result.
49. ★★★ **papadimitriou-yannakakis-2010-price-adjustment-impossibility.pdf** —
    *PNAS* 107(5):1854–1859. No discrete-time price-adjustment mechanism seeing
    only prices and excess demands reaches ε-clearing in time polynomial in
    goods and 1/ε; three goods with a unique equilibrium already admit no bound.
    Rate limits on the *market's* side — the benchmark any allocator must beat.
50. ★★ **athey-segal-2013-efficient-dynamic-mechanism.pdf** — *Econometrica*
    81(6). Agents' private information evolves; period-by-period truthful
    reporting sustained with efficiency and budget balance. Elicitation×drift.
51. ★★★ **pavan-segal-toikka-2014-dynamic-mechanism-design.pdf** — *Econometrica*
    82(2). The dynamic envelope theorem; the general machinery behind #50.
52. ★★ **bergemann-valimaki-2019-dynamic-mechanism-design-intro.pdf** — *JEL*
    57(2). The survey — best single entry point to the whole elicitation×drift
    literature. Start here before #50/#51.
53. ★★★ **roughgarden-talgam-cohen-2015-why-prices-need-algorithms.pdf** —
    EC 2015. The existence of a succinct price system is contingent on the
    computational tractability of the underlying welfare-maximization problem.
    Bandwidth×computation — the second known pairwise assembly, disjoint from
    Fadel-Segal's.
54. ★★★ **dobzinski-nisan-oren-2014-economic-efficiency-requires-interaction.pdf**
    — STOC 2014 / GEB 2019 (arXiv:1311.4721). One-shot communication cannot
    achieve efficiency; interaction is necessary. Sharpens the bandwidth leg.
55. ★★ **cummings-2016-coordination-complexity.pdf** — Cummings, Ligett,
    Radhakrishnan, Roth & Wu, ITCS 2016. How little information suffices to
    coordinate a large population — the optimistic bound facing #54.
56. ★★ **cheung-cole-devanur-2020-tatonnement-beyond-gross-substitutes.pdf** —
    GEB 123. Tâtonnement as gradient descent; how far price dynamics converge
    outside the classical class. The computation leg's dynamic edge.
57. ★★★ **rubinstein-2021-communication-separations-selfishness.pdf** — STOC 2021.
    Exponential separations between notions of selfishness; the technical
    frontier past Fadel-Segal.
58. ★★ **vuppalapati-2023-karma-resource-allocation.pdf** — OSDI 2023. Proves
    max-min fairness keeps Pareto efficiency, strategy-proofness *and* fairness
    only under **static** demand, then builds a credit mechanism recovering them
    under time-varying demand, validated on production traces. Elicitation×drift,
    in production. **This is why scheduler-as-planned-economy is not ours to
    claim** — cite it as the systems-side precedent the criterion generalizes.
59. ★★ **kash-procaccia-shah-2014-dynamic-fair-division.pdf** — *JAIR* 51.
    Dynamic fair division of multiple resources; the theory behind #58.
60. ★ **mcdavid-kiesling-chassin-2026-ai-agents-knowledge-problem.pdf** —
    *Review of Austrian Economics* (Springer OA). **Live competition** — AI
    agents and the knowledge problem, in print now. Read before drafting.


## B. Computability socialism, and the modern debate

32. ★★ **cockshott-cottrell-1993-towards-new-socialism.pdf** — the full book (free
    author PDF). Labor-time planning with computers.
33. ★★ **cottrell-cockshott-1993-calculation-complexity-planning.pdf** — RPE 5(1)
    preprint; their complexity case that planning scales.
34. ★★★ **cockshott-cottrell-1997-hayek-critique.pdf** — RPE 16:177–202. Point-by-
    point reply to Hayek 1945 arguing IT undermines it.
35. ★★ **crookedtimber-2012-red-plenty-seminar.pdf** — CC-licensed compilation;
    Shalizi's "In Soviet Union, Optimization Problem Solves You" at pp. 21–46.
    LP complexity at Soviet scale + the preferences/incentives/change
    objections, treated informally — the criterion formalizes what he lists.
36. ★★ **boettke-candela-2023-feasibility-of-technosocialism.pdf** — JEBO 205
    published version. The Austrian rejoinder: computation cannot substitute for
    competitive discovery. The criterion's strongest live opponent.
37. ★ **dapprich-greenwood-2024-cybersocialism.pdf** — EJPE 17(1). Where the
    debate stands as of 2024.
37b. ★ **rey-2026-hayek-displaced.pdf** — Gastón Rey, "Hayek displaced: Can AI
    solve the socialist calculation problem?" (SSRN 7091139, 2026, not peer
    reviewed). **The closest thing to a direct competitor in print.** Argues the
    Hayekian limit is not falsified by AI but *displaced* into structural
    layers — epistemological (partially superseded by computation), axiological
    (specifying the objective function), and others. Read before drafting: its
    layer decomposition is a rival to our four-component one, and where it is
    right we should adopt it.
37c. ★ **morozov-2019-digital-socialism.pdf** — *NLR* 116/117:33–67. "The
    Calculation Debate in the Age of Big Data" — the essayistic survey of the
    same terrain; useful for framing and who-said-what, not for machinery.
37d. ★ **lambert-2023-diss-ch1-economic-calculation-big-data-ai.pdf** —
    Lambert & Fegley, *JEBO* 206:243–250 (2023). **This file is Lambert's GMU
    dissertation** (*Three Essays on Economic Order and Intervention*, MARS
    handle 1920/14001, 121pp); **the paper is Chapter One, PDF pages 12–32**,
    identified as the published article in its own footnote 1. The accepted
    version — the argument is intact, but the chapter runs under Lambert's name
    with Fegley credited in the note, so cite the JEBO article and check
    wording against it before quoting. The Austrian negative case: why big data
    and AI do not supply what calculation requires, and why labor time cannot
    serve as the basis.
37e. ★ **gmeiner-harper-2020-ai-economic-calculation.pdf** — the **2020 working
    paper** behind Gmeiner & Harper, "Artificial intelligence and economic
    planning," *AI & Society* 39(3):985–1007 (2024). Different title
    ("…Economic Calculation"), Kennesaw State working-paper series, 19pp vs the
    published 23pp; recovered from the Internet Archive after the host URL went
    dead. **Attribute quotations to the 2020 working paper, not the journal
    version.** Raises the same four concerns the criterion decomposes —
    bandwidth, computation, elicitation, speed of collection — qualitatively;
    this is the structural precedent that gets the credit for naming them
    first, and it lands on socialism being "more of a public choice issue than
    an economic calculation issue."

## B. ML-era instances and datafication

38. ★★★ **brynjolfsson-hitzig-2025-ai-use-of-knowledge.pdf** — NBER chapter c15303,
    **now published as ch. 12 of *The Economics of Transformative AI* (Chicago/NBER,
    Sept 2026)**; on disk is the Sept 2025 conference draft — cite the published
    chapter, never the draft's pagination (promoted ★★→★★★ 2026-09-23).
    **Anchor AND best opposing case**: same premise (AI erodes Hayek via codified
    tacit knowledge + processing capacity), GHM property-rights apparatus, *no
    criterion, no engagement with items 21–31* — but an explicit **centralization
    prediction** (larger firms, concentration, less local autonomy; early
    evidence "largely consistent") that cuts against the commons/federation
    claims and must be carried whole. Their §6 countervailing forces and §8
    ("how power is made accountable") are where our position lives. Carried in
    the outline's Hayek-criterion section and IV.4.
38a. ★★ **goldfarb-2025-comment-on-brynjolfsson-hitzig-ai-use-of-knowledge.pdf** —
    NBER c15304, the discussant comment (published pp. 330–335; on disk = the
    pre-publication ms, running title "Artificial intelligence and
    decentralization"). **The published counter, from the same session**: three
    decentralizing forces B&H omit (tacit knowledge often resides at
    headquarters, so AI alienates it downward; individuals gain
    organization-scale capability; fast diffusion), platforms as coordination
    with distributed decision rights, and open/competing models named as the
    constraint on platform centralization — our openness claim in his words.
    His risks-of-decentralization section (echo chambers, malicious AI swarms)
    is the objection to our side; his footnote 2 questions B&H's leap from a
    two-party model to Hayek and socialism. Acquired 2026-09-23. The citation-graph run
    around B&H completed 2026-09-23 → `00-CITATION-GRAPH-brynjolfsson-hitzig.md`
    (report: standouts, objection block, acquire list, coverage) and `.json`
    (63 deduplicated entries; 29 objections; 26 acquire-now, launched). **Hub
    bibliography cautions — do not inherit:** "Kwon, Ma & Zimmermann JFE 2022"
    is *100 Years of Rising Corporate Concentration*, AER 114(7) 2024; "Agarwal,
    Smith & Lee, JAIR 2025" is a phantom (real: Agarwal et al., AEA P&P 2024);
    Decker et al. is AER 110(12) 2020, not AEJ:Macro; NBER w31065 has four
    authors (Brynjolfsson, Jin, Petropoulos & Wang); "Bessen 2019, Research
    Policy" is the held JLE 2020 paper miscited. Already-shelved works the run
    confirmed and skipped: Rey 2026 *Hayek Displaced*, McDavid-Kiesling-Chassin
    2026 (RAE), Autor 2020, Bessen 2020, Radner, Van Zandt, Autor 2014,
    Brynjolfsson-McElheran 2016. The hub has no indexed forward-citation graph
    yet (no chapter DOIs); re-run when they propagate.
39. ★ **autor-2014-polanyis-paradox.pdf** — NBER WP 20485. The bridge citation on
    ML vs. tacit knowledge ("we can know more than we can tell").
40. ★ **hilbert-lopez-2011-worlds-technological-capacity.pdf** — Science 332:60–65.
    The single best datafication anchor: digital share of stored information
    0.8% (1986) → 94% (2007). Feeds the tacit-premise-eroding argument and ties
    to the paper's second-harvest thread.
41. ★ **brynjolfsson-mcelheran-2016-data-driven-decision-making.pdf** — AER P&P
    106(5). Data-driven decision-making tripled in US manufacturing 2005–2010.
42. ★ **zheng-2022-ai-economist.pdf** — Science Advances 8(18). RL tax design
    beats the Saez baseline by **12%** (16% is the arXiv number — do not mix).
43. ★ **koster-2022-democratic-ai.pdf** — arXiv twin of NHB 6(10). RL-designed
    redistribution majority-preferred by human players.
44. ★ **mao-2016-deeprm-resource-management.pdf** (★) / ★★ **mao-2019-decima-learning-scheduling.pdf**
    / ★★★ **verma-2015-borg.pdf** / ★★★ **ghodsi-2011-dominant-resource-fairness.pdf** —
    learned and engineered cluster scheduling (DeepRM, Decima, Borg, DRF).
    Nobody in print frames these as planned economies — that framing is the
    paper's to claim: the world computer's scheduler as the first economy born
    past the criterion (machine-legible state, convex structure, native
    telemetry).

## Not downloaded — paywalled (library list)

***No article on this list is now unobtainable.*** Six items were retrieved
2026-07-28: the Lange 1938 book, Radner 1993, Rey 2026 and Morozov 2019
directly; Lambert & Fegley as the author's dissertation chapter (#37d) and
Gmeiner & Harper as the 2020 working paper (#37e) — both legitimate open
versions of otherwise-closed journal articles, with the version caveats noted
in their entries. What remains is only versions-of-record and books.

- **Versions of record** where an open WP/preprint/chapter stands in — upgrade
  only if one becomes load-bearing at the sentence level, since wording and
  pagination differ: Lambert & Fegley (*JEBO* 206, doi:10.1016/j.jebo.2022.12.009);
  Gmeiner & Harper (*AI & Society* 39(3), doi:10.1007/s00146-022-01523-x — for
  the record, Gmeiner is now at the University of South Dakota and an author
  request is the fast route); Johnson (*JEMS* 2002, doi:10.1111/j.1430-9134.2002.00637.x);
  von Hippel & von Krogh (*Org Sci* 14(2)); Lerner & Tirole (*JIE* 50(2));
  Nagle (*Mgmt Sci* 65(3), doi:10.1287/mnsc.2017.2977); Dongarra & Walker
  (*SIAM Review* 37(2), doi:10.1137/1037042); Mount & Reiter (*JET* 8(2) 1974);
  Jordan (*JET* 28(1) 1982); Woodside et al. (IEEE FOSE 2007,
  doi:10.1109/FOSE.2007.32); Fursin & Temam (*TACO* 7(4), bronze-OA in browser).

## Not downloaded — books

★★ **Olson 1965** (*Logic of Collective Action*); ★★ **Hess & Ostrom 2007**
(*Understanding Knowledge as a Commons* — the eScholarship "PDF" is a 4-page
review, not the book); ★ **Shapiro & Varian 1999** (*Information Rules*); ★ **Boehm
1981** (*Software Engineering Economics*); ★★ **Polanyi 1966** (*The Tacit
Dimension*); ★★ **Phillips & Rozworski 2019** (*The People's Republic of Walmart* —
firms as existing planned economies; nearest neighbor to the scheduler claim);
★ **Hurwicz & Reiter 2006** (*Designing Economic Mechanisms*); ★ **Mayer-Schönberger &
Cukier 2013** (*Big Data* — "datafication," popularized not coined). ★★ **Scheidel 2017** (*The Great Leveler*, Princeton UP — the Four Horsemen:
historically, inequality compresses through war, revolution, collapse, and
plague; the Arrow clause's historical record); ★ **von Hippel,
W. 2019** (*The Social Leap*, Harper Wave — pop-science; wanted only as the
citable reporter of the GSS church-attendance/happiness numbers for the
engineered-utility thread; check the year, 2018 vs 2019 editions).

**★★★ and missing: Mount & Reiter, *Computation and Complexity in Economic
Behavior and Organization* (Cambridge UP 2002, doi:10.1017/cbo9780511754241).**
Surfaced by the citation sweep: the same two authors who gave us the bandwidth
benchmark (#22) build a complexity measure for continuous-variable economic
models and derive an explicit **communication-versus-computation trade-off** in
an Edgeworth Box economy — the bandwidth×computation pairing, from the people
whose lower bound the criterion cites. The sweep's verifier judged it something
we "cannot omit without looking negligent." Library or purchase; no OA copy.

(Lange's 1938 book was retrieved 2026-07-28 — see #17b.)

---

*Ranking provenance: tiers come from the 52-agent review pass described at the
top (per-paper scores, cluster assignments, and calibration overrides in
`00-RANKINGS.json`). Three notes from the calibrator worth carrying: DeepRM was
marked down (4-page HotNets workshop paper, simulation-only — Decima carries the
weight); Dapprich-Greenwood was pushed above its composite because it is the
clearest secondary source foregrounding **drift-tracking**, the component the
paper claims nobody has formalized; and several JSTOR scans here (Hayek 1945,
Samuelson, Eisenberg-Gale, Mount-Reiter) are image-only, so reviewers judged
them from prior reading rather than extracted text — exact-quote verification
against clean editions is still owed before any becomes load-bearing at the
sentence level.*

*Provenance: handles verified by research agents 2026-07-28 (Crossref/publisher/
primary-PDF checks; the novelty sweep and per-component criterion map are in
`~/performance_commons/outline-cosmic-ac.md` §V.5). Version-number traps found in
verification: AI Economist is 12% in Science Advances, 16% only on arXiv; Mises
1920 is pp. 86–121 of Archiv für Sozialwissenschaft (singular); Chen-Deng FOCS
2006 is pp. 261–272; the 175 ZB IDC figure belongs to the 2018 "Digitization of
the World" paper, not 2017's "Data Age 2025"; Fernández-Villaverde's "Simple
Rules… with AI" was never journal-published. Substituted versions (WP/preprint/
chapter-extract) are flagged per entry above — double-check pagination against
the journal of record before anything goes into a doc.*


## Paywalled list cleared (2026-08-16, JPASS) — ranked 2026-08-16

The three items flagged "for your library run" in July are on disk and ranked
here. All three are text-layer publisher PDFs, so unlike most of section B they
can be grepped and quoted directly. Tier placements: 17c and 17d belong to the
knowledge-problem canon, 44b to the drift/dynamics line.

17c. ★★★ **lange-1936-economic-theory-socialism-part-one.pdf** — Lange, *RES*
    4(1):53–71, Oct. 1936 (JSTOR 2967660; text layer, 20 pp.). The trial-and-error
    Central Planning Board in its original published form: prices as an accounting
    rule, and error announcing itself as a physical shortage or surplus. This is
    the exact position the whole "formal descendants" half was assembled to test,
    and the target Hayek 1940 (#19) replies to line by line. §2 sets out Walrasian
    tâtonnement; §3 transplants it — the Board imposes the *parametric function of
    prices* on managers as an accounting rule (all accounting done "as if prices
    were independent of the decisions taken"), fixes prices, and reads its own
    errors off physical surpluses and shortages at the end of the accounting
    period. Two rules replace profit maximization (minimize average cost; produce
    until average cost equals price) and replace free entry. The whole Lange
    solution in about eight pages, and the deflationary answer the Hayek-criterion
    section must beat: if Lange is right, a planner needed no special intelligence
    in 1936 and the "what changed" move loses its premise. Note §3's closing move,
    the nearest thing in the debate to our own framing — "The Central Planning
    Board performs the functions of the market" (p. 64): the market as a
    computation something else can execute. **Substantively redundant with the
    1938 book (#17b), but the book is a *revised* text — attribute quotes to RES
    1936, never to Lippincott, and vice versa. Retire #17b to background/archive
    (it still carries Taylor's 1929 address and Lippincott's introduction, which
    this file does not), and drop its "cite the RES articles, pagination differs
    here" workaround: this arrival makes it obsolete.**
17d. ★★ **lange-1937-economic-theory-socialism-part-two.pdf** — Lange, *RES*
    4(2):123–142, Feb. 1937 (JSTOR 2967609; text layer, 21 pp.). Lange's welfare
    case rather than his calculation case, plus the concession that the real risk
    was never calculation at all but bureaucratization. Completes the citation and
    carries much less than Part One. §5 argues the formal equivalence between
    competitive capitalism and planning is exactly that — formal — and that the
    two differ in the *distribution* condition C and in the comprehensiveness of
    what enters the price system at all. That second point is the useful one for
    the wider project: Lange's claim that a planner can "convert its social
    overhead costs into prime costs" and account for alternatives private cost
    accounting drops is a 1937 statement of the same under-provision structure the
    Performance Commons argument runs on, made from the other side of the aisle,
    and it sits beside the Samuelson/Arrow/Pigou line already held (#65–68). The
    one load-bearing sentence is the bureaucratization concession — "the real
    danger of socialism is that of a bureaucratisation of economic life, and not
    the impossibility of coping with the problem of allocation of resources"
    (pp. 127–128), volunteered against his own position. **But do not let that
    line do work it cannot: Lange immediately rules the question out of scope
    ("belongs to the field of sociology rather than of economic theory"). It is a
    conceded intuition, not a result.** §6 on the policy of transition is 1930s
    political sequencing and the Appendix is Marx-exegetical — context at best;
    §5's business-cycle claim (a socialist economy localizes mistakes, no
    cumulative demand shrinkage) is an undefended assertion history did not treat
    kindly. Same revision trap as #17c: attribute to RES 1937, not the book.
44b. ★★★ **radner-1993-organization-decentralized-information-processing.pdf**
    — Radner, *Econometrica* 61(5):1109–1146 (JSTOR 2951495; text layer, 39 pp. —
    this JPASS copy supersedes the image-only scan the July entry above describes).
    A hard lower bound on how fast any organization can decide: delay grows at
    least like log₂N, so decision latency cannot be held constant as the thing
    being managed grows. The sharpest formal result in the batch, and it lands on
    the criterion's computation-and-latency leg — the thinnest of the four.
    Managers are capacity-limited processors; efficiency is measured in processors
    P and delay C; two bounds survive any network shape, P ≥ N/T and C ≥ 1 + log₂N
    (§1, p. 1114). The second bites: timeliness *cannot* be held fixed while scale
    rises, however many processors you buy. That converts Hayek's rhetorical "by
    the time the equations were solved the information would be obsolete" (which
    Lange quotes from Robbins at #17c p. 56 and waves away) into a theorem,
    generated inside mainstream economics rather than by Austrians. §7's second
    example is stronger and is the passage to build the section on: with benefit
    decaying exponentially in delay, net benefit of processing goes *negative* at
    sufficient scale — the optimal organization stops observing and decides on the
    prior ("in a statistical decision problem, this would imply that the decision
    should be based on prior information, without using any observations,"
    p. 1138). It also supplies the citation spine: #45 and #46 extend it, and
    Proposition 1 in §5.3 is Van Zandt's sharpness result in Radner's own
    notation, so this file is what makes those two readable as a line rather than
    as orphans. For the Q2/distributed half, Radner is explicit that his subject
    sits "close to the boundary between economics and computer science" and that
    his associative-operation trees are literally parallel computation (§1,
    p. 1111). **Two limits Radner flags himself must travel with any citation.
    (1) The model covers only *associative* operations; §7.3 says these are
    believed most amenable to parallelization, so his bounds would be lower bounds
    for all operations, but "I am not aware of any precise result along these
    lines" — never present the log bound as general without that hedge. (2) The
    returns-to-scale verdict flips with the cost specification: increasing returns
    under a delay cost independent of N (eq. 3.4), decreasing under one
    proportional to N (eq. 7.1), both plausible — never quote "decreasing returns
    to scale in information processing" without naming the cost function.**
    Separately, the P/C bounds count *processors*, so a machine-intelligence
    rebuttal that cheapens processors attacks the bandwidth/capacity leg and
    leaves the latency leg untouched. That asymmetry is the argument, and it
    should be stated that way.

## Citation-graph acquisition (2026-09-23): 24 of 26 fetched, 129 agents

From `00-CITATION-GRAPH-brynjolfsson-hitzig.md`'s acquire-now list. Version
doctrine applies — cite the published version, never a working copy's
pagination. **Working papers / preprints standing in for closed VoRs:**
Kwon-Ma-Zimmermann (BFI WP 2023-20, not the AER pp. 2111–2140); Myerson 1977
(Northwestern discussion paper 246, Sept 1976 — image-only — not the MOR
pp. 225–229); Buterin-Hitzig-Weyl (arXiv v2, not Mgmt Sci pp. 5171–5187);
Brynjolfsson-Jin-Petropoulos-Wang (NBER w31065 as revised Nov 2025);
Shahidi et al. (NBER WP 34468) and Athey-Scott Morton (NBER WP 34444) for
their volume chapters; Hadfield-Koh (arXiv 2509.01063) and
Chatterji-Rock-Talamàs "TAI and Firms" (NBER pre-publication ch. PDF) for
theirs; Jensen-Meckling is the JACF 1995 version (pp. 4–18), not the 1992
Blackwell chapter; Cullen-Li-Li is the March 2026 "preliminary & incomplete"
HBS draft (cite 2026, filename says 2025). **VoRs:** Lu 2025 (RAE, OA),
Kurun 2026 (Phil & Tech 39:148), Cao & Cai 2026 (Minds & Machines 36(1) art.
4 — the "36(4)" in the graph list was the article number), Bloom et al.
2014 (Mgmt Sci pp. 2859–2885), Garicano 2000, Grossman-Hart 1986 and
Hart-Moore 1990 (Harvard DASH scans), Bolton-Dewatripont 1994 (JSTOR scan,
image-only), Cemri 2025 (NeurIPS D&B camera-ready), Allen-Weyl 2024 (Project
MUSE), Acemoglu 2023 (2-page offprint, folios 48–49 — check before citing
50–52). Preprints with no VoR: Catalini-Hui-Wu, Chatterji-Rock-Talamàs
"Knowledge Spiral," Longpre et al.

**LOCATED-NEEDS-HUMAN — Sunstein, "The AI Calculation Debate" (SSRN
5054402, 17 pp, the only version that exists).** SSRN's Cloudflare check is
the stop line. In a browser: papers.ssrn.com/sol3/papers.cfm?abstract_id=5054402
→ confirm title/author on screen → "Download This Paper" (free; may want a
free SSRN sign-in) → save as `sunstein-2024-ai-calculation-debate.pdf`.

The four volume-chapter comments (Stuart c15328, Rothschild c15310, Bryan
c15306, Tucker c15302) were not installed; they sit behind the same NBER
Sept-2026 file restriction as Ludwig et al. below and need the same human
route if wanted. Ranked below (2026-09-23).

## Arrivals ranked 2026-09-23 - the Brynjolfsson & Hitzig citation graph

Twenty-four of the 26 acquire-now targets from
`00-CITATION-GRAPH-brynjolfsson-hitzig.md`, ranked as pass 3 in
`00-RANKINGS.json` on the shelf's usual arithmetic (composite = 0.5×relevance +
0.3×standing + 0.2×quality; ★★★ ≥ 8.5, ★★ 7.2–8.4, ★ ≤ 7.0). Objections score up.
Result: **14 ★★★ / 10 ★★ / 0 ★** - the strongest batch this shelf has taken,
which is what a run aimed at the paper's named opponent should produce. Five
composites were trimmed or raised within tier for consistency with the existing
distribution (the 8.9–9.0 band stays with the calculation-debate primaries;
Catalini to the ★★★ floor as an unrefereed preprint on the same promotion path
B&H itself had; Cemri up to 8.7 as a measured objection; Acemoglu down to 7.7
as a two-page op-ed); the JSON carries each reason. New shelf totals in the JSON: 41 ★★★ /
40 ★★ / 18 ★ over 99 ranked entries (111 PDFs on disk; the difference is
unranked duplicates and book chapters). The `Obj.` column marks works that cut
against the commons/federation position; a work can be an objection and still
be ours to build on.

| | File | Obj. | What it is for us | Version caution |
|---|---|---|---|---|
| ★★★ 8.8 | grossman-hart-1986-costs-and-benefits-of-ownership.pdf | | The frame B&H argue inside: ownership = residual rights of control. IV.4's "whoever runs the loop owns the objective" is a residual-rights claim; without this it is a slogan. | DASH copy carrying the JPE page images, 94(4):691–719 - page-level cites are safe; OCR spacing artifacts, check quotes against the image. |
| ★★ 8.4 | hart-moore-1990-property-rights-nature-of-the-firm.pdf | | GH generalized to human capital; cooperatives and partnerships as special cases of the control-structure mapping - the formal vocabulary for federation's governance, not an argument for it. Indispensability criterion is the counter-pressure. | JSTOR scan of JPE 98(6):1119–1158 with a dirty text layer (running heads interleave, digits break) - quote from the page image. |
| ★★★ 8.7 | jensen-meckling-1992-specific-and-general-knowledge.pdf | ✗ | The syllogism under B&H §7: rights co-locate with specific knowledge; codified knowledge is general; so codification centralizes. Built on Hayek 1945, so their own criterion - put the right where the knowledge is - is what an open loop satisfies. | On disk is the JACF 8(2), Summer 1995, pp. 4–18 printing (rendered 2026-09-23 from HTML), a "slightly revised" version of the 1992 Blackwell chapter (pp. 251–274). Cite the edition you quote; never cross-attribute pages. Two-column extraction splices sentences. |
| ★★★ 8.8 | garicano-2000-hierarchies-organization-of-knowledge.pdf | | The model the whole dispute runs in. Cheaper knowledge *acquisition* ("expert systems") widens discretion, cuts layers, cuts delay - our copyable-competence-to-the-edge claim in a mainstream 2000 comparative static. §V's outsourcing result is the long-tail commons in organizational form. | JSTOR VoR, JPE 108(5):874–904, text layer; OCR mangles the mathematics - transcribe formal statements from the image. |
| ★★★ 8.6 | bolton-dewatripont-1994-firm-as-communication-network.pdf | ✗ | "Efficient networks involve centralization" in a pure processing-cost model with no property rights in it - B&H's prediction proved thirty years earlier, so IV.4 cannot dismiss the case as a GHM artefact. The wedge: the driver is returns to specialization in *human* processing time, the parameter machine intelligence moves. Sits with Radner (#44b) / Van Zandt. | VoR QJE 109(4):809–839 via JSTOR (doi 10.2307/2118349, not 2118350), image-only - OCR before quoting; quote against printed folios. |
| ★★★ 8.7 | myerson-1977-graphs-and-cooperation-in-games.pdf | ✗ | The hinge under the hub-and-spoke claim. Myerson proves where value lands on a fixed graph, not that the star is optimal: Thm 3 makes the mesh stable under superadditivity, and the §5 example (7 vs 4 vs 1) is the hub premium - "whoever runs the loop owns the objective" in numbers. | CRITICAL: the file is Northwestern Discussion Paper 246 (Sept 1976), image-only, NOT MOR 2(3):225–229. Cite MOR by DOI 10.1287/moor.2.3.225; re-check theorem numbering and the §5 example against the published text. |
| ★★★ 8.8 | bloom-garicano-sadun-vanreenen-2014-distinct-effects-it-ct.pdf | ✗ | IT decentralizes decision rights, communication technology centralizes them, on plant data with IVs. Converts "does machine intelligence centralize?" into the measurable IT-or-CT question; absent from B&H's bibliography. Two-sided, which is why it is the sharpest objection here. | VoR Management Science 60(12):2859–2885, clean text layer; NBER w14975 has different pagination - do not cross-attribute. |
| ★★★ 8.8 | brynjolfsson-jin-petropoulos-wang-2023-it-firm-size-concentration.pdf | ✗ | The evidence under the concentration prediction (IT → sales and concentration without headcount; retail C4). HC/IV.4 argue with these numbers, not the claim. Its replication-at-near-zero-marginal-cost mechanism is our subject matter - the channel we say the commons socializes. | NBER w31065, revised Nov 2025 vintage (73 pp) on disk; B&H and the graph report cite March 2023 - never carry a number across vintages unchecked. Four authors; not peer-reviewed. |
| ★★ 8.3 | kwon-ma-zimmermann-2024-100-years-rising-corporate-concentration.pdf | ✗ | Concentration has risen for a century and predates IT; the qualifier on any technology-causes-concentration story, B&H's included, and the fixed-cost reading the under-provision argument already runs on. One step removed from decision rights. Also the corrected identity for B&H's phantom JFE cite. | BFI WP 2023-20 (Feb 2023, 108 pp), NOT the AER 114(7):2111–2140 VoR - never attribute AER pages; re-check magnitudes against AER before print. |
| ★★ 7.9 | lu-2025-tacit-knowledge-in-llms.pdf | ✗ | LLMs hold two of three tacit forms (costly-to-articulate; subtext and norms) and not embodied knowledge; "an LLM still cannot be a central planner." The honest boundary of the codifiability premise, stated by a peer-reviewed citer. | VoR, OA, Review of Austrian Economics, doi 10.1007/s11138-025-00710-5, online-first - cite by DOI and section, no page numbers yet. |
| ★★ 7.9 | kurun-2026-ai-entrepreneurial-discovery-embodied-tacit-knowledge.pdf | ✗ | Five epistemic functions of markets; entrepreneurial discovery rests on embodied tacit knowledge that disembodied agents lack. The live form of the Hayek-2002 discovery objection; discovery is not one of our four requirements, and this is why that scoping is a concession. | VoR Philosophy & Technology 39:148 (article number, not a page) - cite by article number and section. |
| ★★ 7.7 | acemoglu-2023-hayek-vs-ai-socialism.pdf | ✗ | The calculation question is misposed - control, not computability, is what matters - and LLM development is itself centralizing ("a large share of humanity gets its information from the same model"): the monoculture point in a published sentence. Author's standing, not the venue's. | Two pages, folios 48–49 of The International Economy, Spring 2023, a Project Syndicate op-ed - never cite past p. 49; attribute the book claims to Acemoglu & Johnson, Power and Progress (2023). |
| ★★★ 8.5 | catalini-hui-wu-2026-simple-economics-of-agi.pdf | ✗ | The only indexed citer of B&H. Cost-to-automate falls exponentially, cost-to-verify is human-bounded, so the Measurability Gap fixes what can be deployed and rents move to provenance and liability underwriting. The codifier's curse - centralization destroys distributed verification capacity - turns B&H's prediction against itself; §6.1.6's Ω decomposition is our openness argument in their notation. Also the sharpest objection: a user-verifiable commons is bounded by the same cH. | Preprint, no VoR: arXiv 2602.20946v2 (25 Feb 2026), SSRN 6298838, 113 pp, unrefereed. Cite arXiv v2 and its section numbers; promote on publication. |
| ★★★ 8.7 | cemri-2025-why-multi-agent-llm-systems-fail.pdf | ✗ | MAST: 14 failure modes, 1,600+ traces across 7 frameworks, 41–86.7% failure, multi-agent often losing to single-agent; interventions buy +9.4%. The must-answer for V.1/V.2's federated computer. 23.5% of failures are task *verification* - the same data says verification, not decentralization as such, is the binding constraint. | NeurIPS 2025 D&B camera-ready (54 pp), doi 10.52202/085713-4082; arXiv 2503.13657's earlier versions carry different counts - take every number from the camera-ready. |
| ★★ 8.2 | cullen-li-li-2025-labor-as-capital.pdf | ✗ | Workers can and do withhold the tacit residue: told their records may train AI to do their work, refusal rises 25%→41%. Codification has an incentive ceiling independent of model capability, and the loop is contested before it exists. Then the gift: collective data ownership attains the first best where individual ownership does not - V.3b/IV.4 in labor-market form. | HBS WP 26-063, "PRELIMINARY & INCOMPLETE", draft of 30 Mar 2026 (filename's 2025 is the first-draft year); Prolific sample; every number provisional - re-verify against whatever version exists when cited. |
| ★★ 7.8 | chatterji-rock-talamas-2026-human-machine-knowledge-spiral.pdf | | Tacit machine knowledge in Nonaka's spiral: like human tacit knowledge it resists articulation, unlike it, it "need not remain local." Their portability is our copyable competence; NotCo selling Giuseppe is the competence itself circulating. Build on it in §6/§7 rather than argue the point fresh. Friction: portable-yet-opaque vs user-verifiable. | Preprint, no VoR: arXiv 2606.29227v1 (28 Jun 2026). Chatterji is OpenAI's Chief Economist (disclosed, not representing OpenAI). |
| ★★ 7.6 | chatterji-rock-talamas-2026-transformative-ai-and-firms.pdf | | A research agenda that states three of our framings as open questions - measurability decides what delegates; the scarce factor moves; upstream concentration raises downstream cost - and closes by conceding the intractability objection with Shalizi (#35). The computation leg in the opponents' words. | NBER pre-publication PDF of ch. 7 (c15327); its 1–16 folios are not the book's pages. Stuart's comment (c15328) not held. |
| ★★★ 8.6 | shahidi-rusak-manning-fradkin-horton-2025-coasean-singularity.pdf | | "By collapsing the costs of eliciting preferences, enforcing commitments, and verifying identity, agents make mechanisms that were once only theoretically attractive now feasible at scale" - the elicitation leg by other authors, and the in-volume reading of falling transaction costs as disaggregation. Carry its congestion, obfuscation and vertical-integration counters with it. | NBER WP 34468 (Nov 2025) on disk; published as ch. 6 (c15309) - cite chapter and pages, never WP sections. Rothschild's comment (c15310) not held; Fradkin employed by Amazon (disclosed). |
| ★★ 8.4 | hadfield-koh-2025-economy-of-ai-agents.pdf | ✗ | Markets presuppose legal infrastructure built by and for humans; an agent economy needs identity, records, licensing, liability - none of which the federated computer yet has. The institutional frame for V.3c; §2.1's specification-wedge argument (Ely-Szentes) is sharper than ours on how an agent-mediated commons degrades signal. Questions, not results. | arXiv 2509.01063v1 (3 Sept 2025) on disk; published as ch. 5 (c15305) - cite the chapter's pages. Bryan's comment (c15306) not held. |
| ★★★ 8.7 | athey-scottmorton-2026-ai-competition-welfare.pdf | ✗ | Derives the aggregation point: a monopolist upstream AI input sets a two-part tariff on an adoption frontier, and capping one fee moves the rent to the other. The formal economics of "commoditize the layer" and of the toll-booth corollary - and an objection, since concentration gets a mechanism independent of property rights and open models are a one-line aside. | NBER WP 34444 (Nov 2025), not peer-reviewed; published as ch. 4 (c15301) - cite the chapter, never WP sections. Tucker's comment (c15302) not held. Disclosures on p. 1 (DOJ, Keystone; Microsoft, NVIDIA) matter if cited on policy. |
| ★★★ 8.6 | longpre-2025-economies-of-open-intelligence.pdf | | The only quantitative counter to the centralization prediction we hold, on the exact object the commons is about: 851k models, 2.2B downloads, HHI/Gini/top-10 share falling after 2022 toward unaffiliated and Chinese developers. Its own caveat is ours: open-weights passing open-source in 2025 is competence that copies but is not user-verifiable. | arXiv 2512.03073v1 (27 Nov 2025), self-labelled preprint - cite the handle only; the dashboard updates, so dashboard figures need a retrieval date. |
| ★★ 8.1 | cao-cai-2026-decreasing-disruption-increasing-concentration-ai.pdf | ✗ | Disruptive AI concentrates in well-resourced institutions, with government (military) support the largest single driver - the peer-reviewed half of the pair with Longpre, and a public-as-much-as-corporate concentration the outline has not addressed. Sample closes in 2020 on patents: pre-open-weights, cannot speak to 2023–25. | VoR, OA: Minds and Machines vol. 36, article 4 (2026), doi 10.1007/s11023-025-09755-8. The masthead's "36:4" is volume:article - never write 36(4), and never quote the PDF's "Page N of 24" as journal pages. |
| ★★★ 8.5 | allen-weyl-2024-real-dangers-of-generative-ai.pdf | ✗ | The exemplar objection to the cure, from authors whose sympathies are ours: open release is the obvious antidote to concentration and they reject it as double-edged (Scylla and Charybdis). §9 and V.3c rest here rather than on our hedging; their "mobilization" is also the friendliest frame for the commons as democratic infrastructure. | VoR: Journal of Democracy 35(1):147–162, Jan 2024, doi 10.1353/jod.2024.a915355 (MUSE). An essay - trace its labor-share and training-run figures to primaries before use. |
| ★★★ 8.5 | buterin-hitzig-weyl-2019-flexible-design-funding-public-goods.pdf | | Quadratic finance: the published financing mechanism for a commons with no central owner, by B&H's coauthor. Completes cluster A's free-rider line (Samuelson → Clarke → Groves-Ledyard) with the form that runs at scale; §5.2 names the real failure mode, Sybil collusion. Cluster A, the batch's one. | arXiv 1809.06421v2 (Aug 2020) on disk, dated after the Management Science 65(11):5171–5187 VoR - never attribute MS pages; check proposition numbering against the journal. |

**What they change.** The disagreement with Brynjolfsson & Hitzig is no longer
a stance against a stance. Garicano 2000 is the model both sides argue in, and
Bloom, Garicano, Sadun & Van Reenen 2014 measured its two cost parameters
separately: information technology pushed decision rights down, communication
technology pulled them up. So the question IV.4 must now pose is whether
machine intelligence is IT or CT - whether it cheapens knowledge acquisition at
the edge or only communication to the centre - and the paper's copyable-
competence claim is a bet on the first, stated in Garicano's own comparative
statics. Jensen-Meckling 1992 gives the opposing syllogism at its source
(codified knowledge is general; rights follow specific knowledge; therefore
centralization), and Grossman-Hart 1986 supplies the frame in which "whoever
runs the loop owns the objective" is a claim about residual rights rather than
a slogan. Catalini, Hui & Wu answer the syllogism from inside the same channel:
the codifier's curse is that experts' verification work trains their own
automation while centralization fails to regenerate distributed verification
capacity, so the scarce factor is verification bandwidth and the commons must
say how it scales *that* - which is also the objection. Cemri et al. is the
must-answer: 41–86.7% failure across seven multi-agent frameworks is measured
against exactly the configuration V.1/V.2 propose, and the section cannot
proceed without saying why the loop is not a MAST failure mode; the usable
half is that a quarter of those failures are task verification, the same bound
Catalini names. Myerson 1977 and Bolton-Dewatripont 1994 are the star-network
hinge: Myerson locates rents at the hub without making the star optimal (the
mesh is stable under superadditivity), and Bolton-Dewatripont derive
centralization from human processing time alone, which is the parameter
machine intelligence moves. Cullen, Li & Li put a ceiling under requirement 1
that no model capability lifts - the holders of the tacit residue withhold it
when told what it will train - and then hand over the closest thing to a
formal efficiency case for collective over individual ownership of expertise.
Brynjolfsson-Jin-Petropoulos-Wang and Longpre are the two series the outline
should now argue with rather than around; Athey-Scott Morton derives the
aggregation point's two-part tariff; Allen-Weyl is the objection to the cure
itself; Buterin-Hitzig-Weyl is the financing mechanism §8.2 and IV.3 build on.

**Still missing.** Two acquire-now targets are LOCATED-NEEDS-HUMAN and were not
ranked: **Sunstein, "The AI Calculation Debate" (SSRN 5054402)** belongs on this
shelf and sits behind SSRN's Cloudflare check (browser route above); **Ludwig,
Mullainathan, Pink & Rambachan, "Behavioral Economics 2.0" (ch. 11, c15325)**
belongs on the-trustworthy-firm and sits behind NBER's Sept-2026 file
restriction - its discussant comment (Nagaraj, c15326) is installed and ranked
there, arguing for now with an absent opponent. The four other volume comments
(Tucker, Rothschild, Bryan, Stuart) are behind the same wall.
