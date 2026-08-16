# The Trustworthy Firm — reading list

The cluster behind **V.3b** of the Cosmic AC outline
(`~/performance_commons/outline-cosmic-ac.md`): deploying an intelligence that
knows a human's preferences (a time series of utility functions) better than the
human — without eroding freedom. The vehicle: a firm that profits by correcting
the *internality* (the human's misalignment with their own preferences), in
concrete form a bank whose capital's purchasing power varies with how it is
spent; trust as the binding constraint (the demonstrably-wise instance maximizes
participation — an iteration on religious institutions); the universal-owner
limit (a sufficiently diversified profit maximizer benefits from real well-being
and maintains market health).

**Sibling directories.** `democratization-of-counsel/` holds the state-side
counsel arc (this firm is its household-side twin — the trusted counselor as a
market actor) and already holds three works this cluster argues with: KKT 1986
(dual entitlement — why per-user pricing reads as unfair), Dubé-Misra 2023 (the
extractive twin, deployed), Špecián 2024 (machine advisors, policy side).
`software-economies-and-the-knowledge-problem/` holds the Hayek-criterion
cluster; the axiological scope decision (criterion takes preferences as given)
punts to exactly this directory.

**The argument's legs, and what each needs from the literature:**
1. **The internality is real and priced** — behavioral welfare economics
   (Bernheim-Rangel), internality taxation (Gruber-Kőszegi), measured wedges.
2. **Demand for the product exists** — commitment devices (Ashraf-Karlan-Yin;
   people pay to bind their future selves); the extractive twin already
   profits from the wedge (DellaVigna-Malmendier contract design).
3. **Money-with-conditions has precedent** — Zelizer's special monies, in-kind
   transfer economics, scrip.
4. **The advice channel corrupts by default** — conflicted-advice evidence
   (Mullainathan-Noeth-Schoar; Egan-Matvos-Seru) = the honest tension, measured.
5. **Alignment mechanisms exist** — cheap talk (Crawford-Sobel) up through
   AI-advisor economics; nudge + its who-nudges-the-nudgers critique
   (Rizzo-Whitman — NOTE: a *Hayekian* critique, connecting to the paper's
   other half); the firm's answer is incentive alignment via profit-sharing.
6. **The universal-owner limit** — Hawley-Williams as alignment mechanism,
   cited WITH the anticompetitive critique (Azar-Schmalz-Tecu).

## Sweep results (9 agents, 2026-07-31 — `00-CITATION-SWEEP.json`: 196 finds,
## 58 landmarks; all handles API-verified, never from model memory)

All seven seeds verified; three corrections caught (Herrnstein's exact title is
"Utility maximization **and** melioration"; Hawley-Williams' 1997 *CGIR* article
is "The Emergence of **Fiduciary** Capitalism" while "The Emergence of
**Universal Owners**" is *Challenge* 43(4) 2000; the rewards paper is
Agarwal-Presbitero-Silva-Wix, FEDS 2023). Version traps recorded in the JSON
notes fields (Zelizer's Princeton-edition DOI is not the 1994 original;
Mullainathan-Noeth-Schoar was never journal-published — cite NBER w17929;
Kaur-Kremer-Mullainathan JPE has an erratum; Crawford-Sobel has a 2021
corrigendum; law-review page numbers came from model knowledge and need a
spot-check before print).

**What the sweep changed about the argument:**
1. Leg 2 upgraded: Save More Tomorrow (Thaler-Benartzi, JPE 2004) is the
   closest *running* instance of the whole mechanism — employer channel,
   voluntary adoption, welfare-improving — lacking only profit-sharing.
   SEED (Ashraf-Karlan-Yin) and CARES (Giné-Karlan-Zinman) are banks already
   selling internality correction at small scale.
2. Leg 5 gained its formal backbone: "Money Doctors" (Gennaioli-Shleifer-
   Vishny, JF 2015) — trust as the binding constraint on delegated advice,
   modeled; plus the reputation-distortion warning (Ottaviani-Sørensen:
   wisdom-signaling can itself corrupt advice).
3. The must-answer critique is sharper than expected and becomes the paper's
   own mechanism: markets equilibrium-select the *extractive* twin
   (Heidhues-Kőszegi credit markets; Gabaix-Laibson shrouded attributes;
   DellaVigna-Malmendier gyms measured; Bryan-Karlan-Nelson undersupply
   puzzle). The paper must say what changed — machine intelligence collapses
   the cost of knowing the per-person wedge and of demonstrating wisdom
   legibly. Same what-changed move as the Hayek-criterion section.
4. Load-bearing honest flag: nudge efficacy is actively contested (Mertens
   PNAS 2022 d≈0.43 vs Maier PNAS 2022 ~0 after publication-bias correction).
5. Rizzo-Whitman's who-nudges-the-nudgers critique is explicitly HAYEKIAN —
   the paper's two halves close a loop; the Sunstein/Sugden *BPP* 7(1) 2023
   exchange shows the field mid-argument on exactly our question.
6. Leg 6 must be argued as mechanism, not practice: real universal owners
   steward feebly (Fichtner-Heemskerk; Bebchuk-Hirst agency costs), the
   anticompetitive result is contested (Azar-Schmalz-Tecu vs
   Dennis-Gerardi-Schenone + Lewellen-Lowry), but the underlying exposure
   shift is measured (Backus-Conlon-Sinkinson: ~700% rise since 1980).
   Nearest published statement of our alignment claim: Condon, "Externalities
   and the Common Owner" (Wash. L. Rev. 2020).

**Coverage gap:** 2023–26 AI-advisor economics — S2 throttling limited the
sweep; only Kleinberg-Mullainathan-Raghavan surfaced. Dedicated pass later.

## The ranking (102 PDFs across two rounds, 2026-07-31; scores + rationales
## in `00-RANKINGS.json`) — 20 ★★★ / 71 ★★ / 11 ★

Composite = 0.5×relevance + 0.3×field-standing + 0.2×quality; tiers cut at
natural gaps (≥8.5 / ≥7.0). Calibration incidents recorded in the JSON notes:
two calibrator overrides were REVERSED after direct file inspection (its
"duplicate file" claims for bebchuk-hirst and backus-conlon-sinkinson were
hallucinated — both files are genuine); four papers were reviewed directly
after twice failing the structured-output layer and merged with the same
formula. ~25 of 55 are working-paper versions — re-verify any quoted number
against the published version before it enters the paper (the JSON's version-
trap list has the mapping; gordon-2022 is an ECGI draft marked do-not-cite —
cite the J. Corp. L. version).

## The reading path — the argument in order

1. ★★★ **bernheim-taubinsky-2018-behavioral-public-economics.pdf**
   Opens leg 1 by defining what must be known: the internality as a per-person money-metric wedge, t*=γ̄ — and its own verdict that this wedge is essentially unmeasured, which is the cost the paper claims MI collapses.
2. ★★★ **taubinsky-rees-jones-2018-attention-variation-welfare.pdf**
   Turns leg 1 into the case for personalization: variance in the wedge carries welfare weight equal to its mean, so representative-agent correction captures little and the value lives in per-person measurement.
3. ★★★ **farhi-gabaix-2020-optimal-taxation-behavioral-agents.pdf**
   [merged] The instrument formalized: behavioral-optimal policy includes vouchers/rigid mental accounts — money whose purchasing power depends on spend — and Prop 3.6 warrants the suggestion channel (a nudge beats a tax for redistributing toward the biased agent).
4. ★★ **bernheim-2016-good-bad-ugly-behavioral-welfare.pdf**
   Licenses acting on the wedge without a true-preference crutch, and names the channel: an advisor supplying option-consequence information without recommending — first-best but historically too costly to scale.
5. ★★ **beshears-2020-early-withdrawal-penalty.pdf**
   Leg 2's demand, plus the design constraint: people pay for more illiquidity, but restricting WHAT money buys suppresses participation — so the firm's lever must be price and suggestion, not prohibition.
6. ★★★ **carrera-2022-who-chooses-commitment.pdf**
   The pivot of leg 2: self-chosen commitment is not targeted on the internality and destroys surplus, while a price correction sized to the wedge gains — so the wedge must be estimated externally. This is the firm's premise.
7. (not on disk) **ZELIZER 1994 — THE SOCIAL MEANING OF MONEY**
   Leg 3's precedent, not on disk: money has repeatedly been earmarked into special monies whose purchasing power depends on who spends it and on what. Spend-contingent money is a recurring institution, not an invention.
8. ★★★ **hastings-shapiro-2018-snap-benefits-spent.pdf**
   Leg 3's modern proof that labels bind: MPC 0.53–0.59 out of earmarked benefits vs ~0 out of cash. Without this, category-conditioned purchasing power is arbitraged away by relabeling.
9. ★★★ **casaburi-macchiavello-2019-infrequent-payments-kenya.pdf**
   Shows the structure already running commercially: correction supplied through the counterparty, priced as a negative interest rate, rationed by trust rather than capital — the closest existing analogue to the proposed bank.
10. ★★★ **jones-molitor-reif-2019-workplace-wellness.pdf**
   Tests V.3b's specific conduit — paying employers for access to employees. Nulls on 37/39 outcomes and profit from selection rather than correction set the floor any version of the firm must clear.
11. ★★ **guiso-sapienza-zingales-2008-trusting-stock-market.pdf**
   Establishes the binding constraint empirically: participation in a delegated financial institution is gated by trust, and trust in one's own advisor moves it most — the 'demonstrably wise instance maximizes participation' claim.
12. ★★★ **gennaioli-shleifer-vishny-2015-money-doctors.pdf**
   Leg 4's turn: the same trust that makes the advisor viable pays for pandering. The debiasing instrument exists and is never used, and strong trust kills the contrarian deviation. Trust alone does not select the honest twin.
13. ★★★ **baicker-mullainathan-schwartzstein-2015-behavioral-hazard.pdf**
   The escape hatch, formalized: equilibrium advice minimizes the intermediary's cost unless λ>0 — its balance sheet moves with realized well-being. This is the paper's device stated as a proposition.
14. ★★ **gordon-2022-systematic-stewardship.pdf**
   Leg 6: in the diversified limit the intermediary's return tracks system health rather than firm-level extraction, with the anticompetitive contest engaged head-on rather than ignored.
15. ★★★ **gabaix-laibson-2006-shrouded-attributes.pdf**
   The must-answer critique in theory: shrouding survives competition and debiasing is unprofitable, so the honest twin wins no business. Converts the thesis into a falsifiable target — move α past α†, cut e, or make wisdom legible.
16. (not on disk) **HEIDHUES & KOSZEGI — EXPLOITATIVE CONTRACTS / NAIVETE-BASED DISCRIMINATION (2010; ANNU. REV. ECON. 2018)**
   Not on disk, and the argument names it: markets equilibrium-select the extractive twin, exploitation surviving competition and cross-subsidized by sophisticates. The sharpest statement of what the paper must overturn.
17. ★★★ **agarwal-2023-who-pays-for-rewards.pdf**
   The critique measured in the exact analogue: a bank that profits from how customers spend, steering purchases and moving $15.1B/yr from naive to sophisticated. The observed equilibrium is the extractive twin.
18. (not on disk) **MI-MEASURES-THE-WEDGE EVIDENCE — MISSING FROM THE CLUSTER**
   The what-changed resolution has no source on disk. Nothing here shows machine intelligence estimating a per-person wedge cheaply or demonstrating wisdom legibly; the closing move is currently asserted, not evidenced.

## Side tracks

- **The wedge measured in the wild — magnitudes, and why the tax is blunt** — detour After step 2, when the paper needs dollar magnitudes for the internality or the uniform-tax benchmark the firm competes against (Dubois: the largest wedges are the least price-responsive).
  ★★ allcott-lockwood-taubinsky-2019-ssb-overview.pdf; ★★ allcott-lockwood-taubinsky-2019-regressive-sin-taxes.pdf; ★★ allcott-taubinsky-2015-lightbulb.pdf; ★★ dubois-griffith-oconnell-2020-soda-taxes-targeting.pdf; ★★ allcott-sunstein-2015-regulating-internalities.pdf; ★★ decicca-kenkel-lovenheim-2022-tobacco-regulation.pdf; ★★ dellavigna-malmendier-2006-paying-not-gym.pdf; ★★ schilbach-2019-alcohol-and-self-control-a-field-experiment-in.pdf
- **Commitment demand and its failure modes — why small instances stay small** — detour After step 5, when defending 'demand exists and small instances run' against the charge that commitment markets are thin, economist-seeded, and harm the naive who self-size them.
  (book/fetch) SAVE MORE TOMORROW (THALER & BENARTZI 2004); (book/fetch) ASHRAF, KARLAN & YIN 2006 — SEED; (book/fetch) GINE, KARLAN & ZINMAN 2010 — CARES; ★★ bai-2021-self-control-preventive-health.pdf; ★★ john-2020-when-commitment-fails.pdf; ★★ laibson-2015-why-dont-present-biased-commit.pdf; ★★★ laibson-1997-golden-eggs.pdf; ★ hyndman-bisin-2026-deadlines-replication.pdf; ★ milkman-2014-temptation-bundling-hunger-games.pdf
- **Money with conditions — precedents, the cash counterfactual, and the digital form** — detour After step 7, when specifying the balance sheet: fungibility must fail, unrestricted cash already performs well (the paternalism boundary), and platform money is already spend-contingent.
  ★★ hastings-shapiro-2013-fungibility-gasoline.pdf; ★★ haushofer-shapiro-2016-cash-transfers-kenya.pdf; ★★ brunnermeier-james-landau-2019-digitalization-of-money.pdf
- **The employer conduit's track record** — detour At step 9, when arguing employers will pay for the right to have employees advised: the $3.27-per-$1 prior, the RCT nulls that replaced it, and the one design that retained effects.
  ★ baicker-cutler-song-2010-wellness-savings.pdf; ★★ song-baicker-2019-wellness-jama.pdf; ★★ royer-stehr-sydnor-2015-gym-commitment.pdf; ★ backus-conlon-sinkinson-2021-common-ownership-america.pdf
- **Advice corrupts — beyond the trust rent** — detour Between steps 11 and 12, when arguing reputation could discipline the advisor: zero-conflict experts still misreport, and harm tracks the absence of continuing exposure to client outcomes.
  ★★ ottaviani-sorensen-2006-reputational-cheap-talk.pdf; ★★ christoffersen-evans-musto-2013-fund-flows.pdf; ★★ mullainathan-noeth-schoar-2012-financial-advice-audit.pdf; ★★ alonso-matouschek-2008-optimal-delegation.pdf
- **Does the advice channel work at all, and who nudges the nudgers** — detour At step 12, when sizing the suggestion channel and answering the Hayekian critique: effects are weakest in finance, may vanish under bias correction, and the i-frame objection lands here.
  ★★ mertens-2022-nudge-meta-analysis.pdf; ★★ maier-2022-no-evidence-nudging.pdf; ★★ chater-loewenstein-2023-iframe-sframe.pdf; ★★ gigerenzer-2015-supposed-evidence-libertarian-paternalism.pdf; ★★ sugden-2017-do-people-want-to-be-nudged.pdf; (book/fetch) NUDGE (THALER & SUNSTEIN 2008); (book/fetch) ESCAPING PATERNALISM (RIZZO & WHITMAN 2020); (book/fetch) HAYEK 1945 — THE USE OF KNOWLEDGE IN SOCIETY; ★ glaeser-2005-paternalism-and-psychology.pdf
- **Universal ownership: thesis, mechanism, and the anticompetitive contest** — detour At step 13, the moment leg 6 is asserted: the contest (Azar vs Dennis), the agency-cost rebuttal (Bebchuk-Hirst, feeble stewardship), and the one positive mechanism datum (NBIM's Note).
  (book/fetch) THE RISE OF FIDUCIARY CAPITALISM (HAWLEY & WILLIAMS 2000); (book/fetch) bebchuk-hirst-2019-index-funds-governance.pdfNCE; ★★ fichtner-2017-hidden-power-big-three.pdf; ★ fichtner-heemskerk-2020-permanent-universal-owners.pdf; ★ aguilera-bermejo-capape-cunat-2020-systemic-universal-owners.pdf; ★★ condon-2020-externalities-common-owner.pdf; ★★ schmalz-2018-common-ownership-survey.pdf; ★★ azar-schmalz-tecu-2018-anticompetitive-common-ownership.pdf; ★★ dennis-gerardi-schenone-2022-common-ownership-airlines.pdf; ★ quigley-2019-universal-ownership-anthropocene.pdf


## The what-changed extension (round 2, 2026-07-31 — 47 arrivals reviewed;
## merge notes in `00-RANKINGS.json` under `round2`)

**Main-path steps 18a–18e** (replacing the empty step-18 slot, in order after
agarwal-2023; the path now ends honestly on the two cautions):

1. ★★★ **mullainathan-2022-diagnosing-physician-error-a-machine.pdf**
   Opens the slot with the wedge machine-measured inside a real welfare decision aggregates hide — and is honest that proving the machine right still took a quasi-experiment.
2. ★★ **knittel-2025-using-machine-learning-to-target-treatment.pdf**
   Scales the wedge to 900K households and monetizes it (12-120% of net benefits), while the untargeted nudge harms >=15% — so correction must be per-person or it extracts.
3. ★★ **brynjolfsson-2025-generative-ai-at.pdf**
   The employer-channel half of V.3b working at 5,179-agent scale, with value visible in third-party outcomes rather than self-report.
4. ★★ **sharma-2023-towards-understanding-sycophancy-in.pdf**
   Turns the critique inward: optimizing revealed preference selects convincing agreement over truth, so the extractive twin is selected inside the technology before any market does it.
5. ★★★ **salganik-2020-measuring-the-predictability-of-life.pdf**
   Ends the path honestly on limb (a): the strongest common-task null on predicting a specific person, implying a floor the cheap-wedge claim must be argued around, not past.

**New side tracks** (files tiered individually):

- **The wedge machine-measured** — ★★★ kleinberg-2018-human-decisions-and-machine.pdf; ★★ kleinberg-2015-prediction-policy.pdf; ★★★ obermeyer-6464-dissecting-racial-bias-in-an-algorithm-used.pdf; ★★★ ludwig-2024-machine-learning-as-a-tool-for-hypothesis.pdf; ★★ handel-2015-health-insurance-for-humans-information.pdf
- **Estimating the per-person wedge — the machinery** — ★★★ athey-2021-policy-learning-with-observational.pdf; ★★ athey-2019-generalized-random.pdf; ★★ chernozhukov-2025-fisher-schultz-lecture-generic-machine.pdf; ★★ fudenberg-2022-measuring-the-completeness-of-economic.pdf
- **Reading the person from exhaust** — ★★ kosinski-2013-private-traits-and-attributes-are.pdf; ★★ youyou-2015-computer-based-personality-judgments-are.pdf; ★★ peters-2024-large-language-models-can-infer.pdf; ★★ park-2024-llm-agents-grounded-in-self-reports-enable.pdf; ★★ aiken-2022-machine-learning-and-phone-data-can-improve.pdf
- **Silicon selves and their critics** — ★★ argyle-2023-out-of-one-many-using-language-models-to.pdf; ★★ bisbee-2024-synthetic-replacements-for-human-survey.pdf; ★★ santurkar-2023-whose-opinions-do-language-models.pdf; ★★ horton-2023-large-language-models-as-simulated-economic.pdf; ★★ binz-2025-a-foundation-model-to-predict-and-capture.pdf; ★ wang-2024-large-language-models-for-market-research-a.pdf
- **LLM advice trials** — ★★ goh-2024-large-language-model-influence-on.pdf; ★★ otis-2024-the-uneven-impact-of-generative-ai-on.pdf; ★★ wang-2024-tutor-copilot-a-human-ai-approach-for.pdf; ★ kestin-2025-ai-tutoring-outperforms-in-class-active.pdf; ★★ becker-2025-measuring-the-impact-of-early-2025-ai-on.pdf; ★★ schoenegger-2025-ai-augmented-predictions-llm-assistants.pdf; ★★ yang-2026-my-advisor-her-ai-and-me-evidence-from-a.pdf
- **Legibility engineering** — ★★ mellers-2014-psychological-strategies-for-winning-a.pdf; ★★ tadelis-2016-reputation-and-feedback-systems-in-online.pdf; ★★ shin-2023-superhuman-artificial-intelligence-can.pdf; ★ liang-2023-holistic-evaluation-of-language.pdf
- **Preference learning and its failure modes** — ★★★ christiano-2017-deep-reinforcement-learning-from-human.pdf; ★★ ouyang-2022-training-language-models-to-follow.pdf; ★★ casper-2023-open-problems-and-fundamental-limitations.pdf
- **Does the advice channel work at all, and who nudges the nudgers** — ★★ milkman-2021-megastudies-improve-the-impact-of-applied.pdf; ★★ milkman-2024-megastudy-shows-that-reminders-boost.pdf; ★★ hoffman-2018-discretion-in.pdf; ★★ angelova-2025-algorithmic-recommendations-and-human.pdf; ★★ dietvorst-2018-overcoming-algorithm-aversion-people-will.pdf
- **Advice corrupts — beyond the trust rent** — ★★ matz-2017-psychological-targeting-as-an-effective.pdf; ★★ matz-2024-the-potential-of-generative-ai-for.pdf; ★★ salvi-2025-on-the-conversational-persuasiveness-of-gpt.pdf

## Version variants on disk

- `hastings-shapiro-2018-snap-main-wp.pdf` — NBER WP of the *QJE* article; the
  other Hastings-Shapiro file is the online appendix only. Quote from this one.
- `schilbach-2019-alcohol-self-control-main.pdf` — the published *AER* 109(4)
  text (MIT DSpace); `schilbach-2019-alcohol-appendix-only.pdf` is its appendix.

## Gaps the path-builder surfaced

1. **RESOLVED (what-changed sweep, 6 Opus agents, 2026-07-31):** 162 verified
   finds in `00-WHAT-CHANGED-SWEEP.json`; ~30 new PDFs on the shelf (more in
   flight). The evidence is ASYMMETRIC and the paper should say so: knowing
   the per-person wedge is overwhelmingly demonstrated (Dubé-Misra deployed
   WTP; Allcott-Kim-Taubinsky-Zinman per-borrower internality; Centaur in
   Nature; Youyou-Kosinski beats your spouse; Kleinberg/Mullainathan-Obermeyer
   /Hoffman machines-beat-experts trio), and machine advice measurably works
   (Brynjolfsson QJE 2025; Noy-Zhang; Goh JAMA; Gargano-Rossi — a fintech
   profiting by closing internality gaps). But DEMONSTRATING wisdom legibly
   is the honest frontier: Dietvorst aversion vs Logg appreciation, the
   Dell'Acqua jagged-frontier warning, and Obermeyer's label-choice failure
   (a deployed algorithm optimizing the wrong wedge for 200M people). The
   firm's design features ARE the engineering of that remaining leg.
2. **Books/named works to acquire:** Zelizer 1994 (main path), Heidhues-
   Kőszegi AER 2010 (main path — paywalled, no green copy found in sweep),
   Nudge 2008, Escaping Paternalism 2020, The Rise of Fiduciary Capitalism
   2000, Save More Tomorrow (JPE 2004), Ashraf-Karlan-Yin (QJE 2006),
   Giné-Karlan-Zinman (AEJ:Applied 2010).
3. Gjessing-Syse 2007 is closed-access (re-paywalled 2025, SSRN copy pulled);
   superseded here by aguilera-bermejo-capape-cunat-2020 (Matthew's find —
   the same Norwegian-fund story as a natural experiment).



## Broken-handle entry resolved and fetched (2026-08-16) — ranked 2026-08-16

The failed-fetch entry `ricardo-2008-optimal` is **Alonso & Matouschek,
"Optimal Delegation," *RESTUD* 75(1):259-293 (2008)** — on disk as the LSE
eprints accepted version (green OA; no JSTOR slot needed). Ranked here; it
joins the side track "Advice corrupts — beyond the trust rent," where it was
already listed.

★★ **alonso-matouschek-2008-optimal-delegation.pdf**
   The general characterization of Holmström's delegation problem without
   transfers: what set of choices to leave an agent, and why more alignment does
   not imply more discretion. The cluster's framing sentence — deploying
   preference-knowing intelligence 'without eroding freedom' — is a discretion
   question, and this answers discretion questions in full generality when the
   principal cannot commit to contingent transfers. That no-transfers assumption
   is exactly the firm's situation: it cannot contract on a person's private
   consumption states. Prop. 2 characterizes the optimal delegation set; Prop. 4
   collapses it to a single interval once the agent is sufficiently aligned,
   which is why real organizations use simple caps; and the regulation
   application shows a welfare-maximizing regulator without transfers can do no
   better than a price cap — the structural cousin of a spend-limit. Two results
   cut against the cluster's intuitions. Whether to rule a choice out depends on
   the *slope* of the bias, not its level: an agent whose preferences are locally
   flat in the state chooses insufficiently state-sensitively, so the principal
   removes intermediate options to force responsiveness — a rationale for gapped
   rather than capped choice sets that behavioral welfare economics does not
   supply. And the Ally and Uncertainty Principles fail once sets can be
   arbitrary: 'the principal may then give less discretion to a more aligned
   agent or to one with a bigger informational advantage' (§9). Held at ★★ for a
   specific reason: the model's only instrument is prohibition — a choice is in
   the set or out of it — and this README already concludes from Beshears 2020
   that the firm's lever must be price and suggestion, not prohibition. It is
   therefore the rigorous theory of the instrument the argument has decided
   against: indispensable for saying precisely what is given up by pricing rather
   than forbidding, but not carrying a leg on its own. **Upgrade to ★★★ if the
   firm's design ever admits a hard permitted-set component (category-restricted
   accounts, vouchers in the Farhi-Gabaix sense), at which point it becomes leg
   3's optimality theory.** Cautions, and the first is sharp for a directory
   where ~25 of 55 files are working papers: this is the LSE accepted-version
   postprint and its pagination is the manuscript's own (body pp. 1–33,
   appendices A–B to p. 59), NOT *RESTUD* 75(1):259–293 — the front matter warns
   'there may be differences between this version and the published version', so
   re-map every page cite before print. Substantively the model has no ability
   differences between principal and agent and no information-acquisition
   incentives, and §9 concedes it cannot rationalize management by exception.
   The role mapping also needs an argument the cluster has not yet made: here the
   *agent* holds the informational advantage and is interpersonally biased,
   whereas the trustworthy firm's premise is that the *firm* knows the wedge and
   the human's misalignment is intrapersonal. The standard fix — principal as
   long-run self, agent as present self — is a modeling move to defend, not a
   free translation.
