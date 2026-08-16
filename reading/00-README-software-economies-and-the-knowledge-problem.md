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
17b. ★★★ **lange-taylor-1938-economic-theory-of-socialism.pdf** — Lange &
    Taylor, *On the Economic Theory of Socialism*, ed. Lippincott, Univ. of
    Minnesota Press 1938 — the book version of the two *Review of Economic
    Studies* articles (4(1):53–71, 1936; 4(2):123–142, 1937), plus Taylor's
    1929 AEA address and Lippincott's introduction. The trial-and-error Central
    Planning Board as Walrasian auctioneer: the position everything in the
    "formal descendants" sections was built to test. **Cite the RES articles for
    the argument — pagination differs here; this is an archive.org DLI scan,
    image-only and of unclear rights, so treat it as a reading copy.**
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
    extend it. (Image-only scan.)
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

38. ★★ **brynjolfsson-hitzig-2025-ai-use-of-knowledge.pdf** — NBER chapter c15303.
    **The near-collision**: same premise (AI erodes Hayek via codified tacit
    knowledge + processing capacity), near-same title, GHM property-rights
    apparatus, *no criterion, no engagement with items 21–31*. The paper must
    position against this explicitly and early.
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
