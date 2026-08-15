export const meta = {
  name: 'security-economics-ranking',
  description: 'Review each security-economics PDF and assign a multi-factor importance ranking',
  phases: [
    { title: 'Review', detail: 'one agent per paper reads it and scores three factors', model: 'opus' },
    { title: 'Calibrate', detail: 'cross-paper normalization into three tiers', model: 'opus' },
  ],
}

const DIR = '/home/matt/reading/security-economics'

const PROJECT = `The reading list serves the compute-commons project in ~/performance_commons (the "Performance Commons" paper and its widened successor "Towards the Cosmic AC"). This collection backs the SECURITY side. What the project claims and needs:
(1) III.3 "THERE ARE NO SECURE COMPUTERS": under sufficient intelligence every device is reachable; the computer-world relationship becomes like the human body's — infections tolerated, fought, or symbiotic. Fable & Carson 2026 (the collection's anchor, fable-carson-2026-cyber-costs.pdf) is cited as the best disciplined NEAR-TERM number: median AI-added cyber cost ~$116B/yr by 2028 but mean ~$262B — a modest-median, tail-driven-mean structure that IS the body metaphor in dollars. Its known limits: defense in its engine is a severity-truncation haircut only (continuous autonomous defense cannot appear except as a regime label), and its "diffusion asymmetry" (offense adopts frontier capability instantly, defense deploys through enterprise procurement) is the project's collective-action thesis stated in security clothing.
(2) S16 (actuarial layer): four isolation architectures for shared enterprise compute (same-OS -> VM+NIC -> hardware partition -> new silicon); realized boundary-exploitation indices from KEV; Bohme-Kataria internal-vs-global correlation with the same-production-batch exception (one partition design on every endpoint = the hard-to-insure cell); the two-factor decomposition (correlated boundary failure converts to per-machine reimaging unless the attacker independently defeats each firm's IT).
(3) S19 (negotiated cession): ceding negotiated control of one's compute becomes individually rational where hardware can participate in a market at all — residual risk at hardware-partitioned isolation is ~cents/machine-yr; the only value-destroying cell is unnegotiated unpartitioned access (malware, priced); the categories rewrite (unauthorized -> unnegotiated; compromise -> breach-of-contract; ownership -> residual control rights per Grossman-Hart); the honest counter-channel is same-batch correlation — symbiosis thins the body of the loss distribution and concentrates the tail.
(4) The wider frame: federation of idle compute (the fleet stranded by participation barriers, not physics), architectural sharing below the OS with the builder as underwriter (warranty as costly-to-fake quality signal), and the cost-measurement discipline needed to keep any $B-scale claim honest.
Score RELEVANCE against these specific claims — what the paper would be load-bearing FOR — not against "security economics" generally.`

const SCORE_SCHEMA = {
  type: 'object',
  required: ['file', 'relevance_to_project', 'field_standing', 'quality', 'one_line', 'load_bearing_for', 'which_cluster'],
  properties: {
    file: { type: 'string' },
    relevance_to_project: { type: 'integer', minimum: 1, maximum: 10, description: 'how directly this supports or disciplines a claim the project makes (III.3, S16, S19, federation frame)' },
    field_standing: { type: 'integer', minimum: 1, maximum: 10, description: 'citation weight / canonical status / venue in its own field' },
    quality: { type: 'integer', minimum: 1, maximum: 10, description: 'publicly recognized quality and rigor of the work itself' },
    which_cluster: { type: 'string', enum: ['A-loss-distributions-evt', 'B-infosec-econ-canon', 'C-insurance-correlation-systemic', 'D-measuring-cybercrime-cost', 'E-vulnerability-markets', 'F-ai-offense-defense', 'anchor'] },
    load_bearing_for: { type: 'string', description: 'the specific project claim/section it supports or disciplines, or "context" if background only; note if it is ADVERSARIAL to a project claim (that raises relevance, not lowers it)' },
    one_line: { type: 'string', description: 'one sentence: what it establishes, judged from reading it' },
    caveat: { type: 'string', description: 'version/provenance issue noticed while reading (working paper vs published, wrong author list, abstract-only file), or empty' },
  },
}

const RANK_SCHEMA = {
  type: 'object',
  required: ['rankings', 'notes'],
  properties: {
    rankings: { type: 'array', items: {
      type: 'object',
      required: ['file', 'tier', 'composite', 'rationale'],
      properties: {
        file: { type: 'string' },
        tier: { type: 'integer', minimum: 1, maximum: 3, description: '1 = must-read (top), 2 = strong, 3 = context' },
        composite: { type: 'number', description: 'weighted score used for the ordering' },
        rank_within_cluster: { type: 'integer' },
        rationale: { type: 'string', description: 'one line on why this tier, referencing the three factors' },
      } } },
    notes: { type: 'string', description: 'calibration notes: reviewer scores overridden and why; disagreements with the sweep agents prior SEMINAL/LOAD-BEARING/CONTEXT suggestions worth flagging; version caveats worth surfacing' },
  },
}

const files = ["ablon-bogart-2017-zero-days-thousands-nights.pdf", "acquisti-friedman-telang-2006-privacy-breach-event-study.pdf", "aldasoro-etal-2022-drivers-of-cyber-risk.pdf", "anderson-2001-why-infosec-hard.pdf", "anderson-etal-2012-measuring-cost-cybercrime.pdf", "anderson-etal-2019-changing-cost-cybercrime.pdf", "anderson-moore-2006-economics-infosec-science.pdf", "anderson-moore-2009-cs-econ-psych.pdf", "arora-krishnan-telang-yang-2010-patch-release-behavior.pdf", "arora-telang-xu-2008-optimal-disclosure-policy.pdf", "awiszus-etal-2023-idiosyncratic-systematic-systemic.pdf", "beattie-etal-2002-timing-security-patches.pdf", "biener-eling-wirfs-2015-insurability-cyber-risk.pdf", "bilge-dumitras-2012-before-we-knew-it.pdf", "bohme-2005-cyber-insurance-revisited.pdf", "bohme-2006-market-approaches-vulnerability-disclosure.pdf", "bohme-kataria-2006-correlation-cyber-insurance.pdf", "bohme-schwartz-2010-modeling-cyber-insurance.pdf", "bouveret-2018-cyber-risk-financial-sector.pdf", "braun-eling-jaenicke-2023-cyber-ils.pdf", "brundage-etal-2018-malicious-use-ai.pdf", "campbell-gordon-loeb-zhou-2003-economic-cost-breaches.pdf", "cavusoglu-mishra-raghunathan-2004-breach-announcements.pdf", "chavezdemoulin-embrechts-hofert-2016-evt-covariates.pdf", "chen-embrechts-wang-2024-infinite-mean-risk.pdf", "chen-embrechts-wang-2024-stochastic-dominance.pdf", "corsi-kilian-mallah-2024-offense-defense-dynamics.pdf", "cremer-etal-2022-data-availability.pdf", "csis-mcafee-2014-net-losses.pdf", "dacorogna-debbabi-kratz-2023-cyber-resilience-heavy-tails.pdf", "detica-2011-cost-of-cyber-crime.pdf", "dreyer-etal-2018-rand-global-cost.pdf", "edwards-hofmeyr-forrest-2016-hype-heavy-tails.pdf", "ee-etal-2025-asymmetry-by-design.pdf", "eisenbach-kovner-lee-2022-cyber-us-financial-system.pdf", "eling-schnell-2016-what-do-we-know.pdf", "eling-wirfs-2019-actual-costs-cyber-risk.pdf", "fable-carson-2026-cyber-costs.pdf", "fang-etal-2024-llm-agents-one-day.pdf", "farkas-lopez-thomas-2021-gpd-regression-trees.pdf", "finifter-akhawe-wagner-2013-vrp-study.pdf", "florencio-herley-2011-sex-lies-cybercrime-surveys.pdf", "garfinkel-dafoe-2019-offense-defense-scale.pdf", "geer-etal-2003-cyberinsecurity-cost-of-monopoly.pdf", "gordon-loeb-2002-economics-infosec-investment.pdf", "hazell-2023-spear-phishing-llm.pdf", "healey-2019-persistent-engagement.pdf", "heiding-etal-2024-ai-spear-phishing.pdf", "herley-2009-so-long-externalities.pdf", "herley-florencio-2010-nobody-sells-gold.pdf", "herr-schneier-morris-2017-taking-stock.pdf", "hillairet-lopez-2021-cyber-propagation-portfolio.pdf", "jamilov-rey-tahoun-2026-anatomy-cyber-risk.pdf", "kamiya-etal-2021-cyberattacks-target-firms.pdf", "kannan-telang-2005-market-vulnerabilities-think-again.pdf", "kunreuther-heal-2003-interdependent-security.pdf", "levi-2017-economic-cybercrimes.pdf", "lohn-2025-ai-cyber-offense-defense.pdf", "lohn-etal-2023-autonomous-cyber-defence.pdf", "lukosiute-swanda-2025-evals-real-world-risk.pdf", "maillart-etal-2017-given-enough-eyeballs.pdf", "maillart-sornette-2010-heavy-tailed-cyber-risks.pdf", "malavasi-etal-2022-cyber-frequency-severity.pdf", "marotta-etal-2017-cyber-insurance-survey.pdf", "moore-2010-economics-cybersecurity-policy.pdf", "moore-clayton-anderson-2009-economics-online-crime.pdf", "murphy-stone-2025-uplifted-attackers.pdf", "neslehova-embrechts-chavezdemoulin-2006-infinite-mean-lda.pdf", "ozment-2004-bug-auctions.pdf", "ozment-schechter-2006-milk-or-wine.pdf", "potter-etal-2025-frontier-ai-cybersecurity.pdf", "rescorla-2005-finding-security-holes.pdf", "riek-bohme-2018-consumer-facing-cybercrime.pdf", "rodriguez-etal-2025-evaluating-cyberattack-capabilities.pdf", "romanosky-2016-costs-causes-cyber-incidents.pdf", "romanosky-etal-2019-content-analysis-cyber-policies.pdf", "shetty-etal-2010-competitive-cyber-insurance.pdf", "slayton-2017-cyber-offense-defense-balance.pdf", "sridhar-ng-2021-hacking-for-good.pdf", "von-skarczinski-etal-2023-german-max-losses.pdf", "walshe-simpson-2020-bug-bounty-programs.pdf", "welburn-strong-2022-systemic-cyber-risk.pdf", "wheatley-hofmann-sornette-2019-catastrophe-framework.pdf", "wheatley-maillart-sornette-2016-extreme-risk-data-breaches.pdf", "wolff-lehr-2017-degrees-of-ignorance.pdf", "woods-bohme-2021-sok-quantifying-cyber-risk.pdf", "xu-etal-2018-hacking-breach-trends.pdf", "zeller-scherer-2022-marked-point-processes-cyber.pdf", "zeller-scherer-2024-risk-mismeasurement.pdf", "zhang-etal-2024-cybench.pdf", "zhang-etal-2026-aixcc-sok.pdf", "zhao-grossklags-liu-2015-vulnerability-ecosystems.pdf", "zhu-etal-2024-teams-llm-zero-day.pdf"]
log(`${files.length} papers to review`)

phase('Review')
const scored = await parallel(files.map(f => () =>
  agent(`${PROJECT}

Read the PDF at ${DIR}/${f} (use pdftotext or the Read tool; for long reports read the abstract/intro/conclusion and skim the body — enough to judge it). Then score it on three 1-10 factors as a reviewer who has actually read it, not from the title:
- relevance_to_project: how directly it supports OR disciplines a claim THIS project makes (III.3's body-metaphor and near-term quantification, S16's isolation/insurability layer, S19's negotiated-cession economics, the federation frame). A paper that is ADVERSARIAL to a project claim (e.g. cost-measurement critiques that would push back on $B-scale forecasts) is HIGHLY relevant — the project wants honest pushback.
- field_standing: its canonical status / citation weight / venue in its OWN field;
- quality: publicly recognized rigor and quality of the work itself.
Assign which_cluster (use 'anchor' only for fable-carson itself). Say what it is load_bearing_for, naming the specific claim. Note any version/provenance caveat visible in the actual file (working-paper vs published version, author-list surprises, abstract-only). Be honest and calibrated — most papers are a 5-7 on field_standing; reserve 9-10 for genuinely canonical work (Anderson 2001, Gordon-Loeb 2002, Anderson-Moore 2006 Science, Akerlof-class classics).`,
    { label: `review:${f.replace('.pdf','').slice(0,28)}`, phase: 'Review', schema: SCORE_SCHEMA, model: 'opus', effort: 'medium' })
    .catch(() => null)))

const good = scored.filter(Boolean)
log(`${good.length}/${files.length} reviewed; calibrating`)

phase('Calibrate')
const ranked = await agent(`${PROJECT}

Here are per-paper reviews (each scored relevance_to_project, field_standing, quality 1-10, with cluster and load-bearing notes) from ${good.length} independent reviewers who each read one paper:

${JSON.stringify(good, null, 1)}

Produce a calibrated three-tier ranking of the whole reading list. Method:
1. Compute a composite emphasizing project relevance but honoring field standing and quality: composite = 0.5*relevance_to_project + 0.3*field_standing + 0.2*quality.
2. Sort, and cut into three tiers: TIER 1 (must-read — structurally load-bearing AND high standing), TIER 2 (strong on at least one factor), TIER 3 (context/secondary). Aim roughly for 15-20 in tier 1 given the list is ~93 works, but let the natural gaps in composite decide, not a quota.
3. Independent reviewers over-score their own paper; correct obvious inflation (a recent low-citation preprint rated 9 on field_standing should come down; adversarial relevance should NOT be corrected down). Note any such overrides.
4. Give rank_within_cluster so each of the six clusters has its own ordering. Treat fable-carson (cluster 'anchor') separately — rank it but note it is the collection's seed, not a discovery.
Return every file with its tier, composite, within-cluster rank, and a one-line rationale citing the factors. In notes, also surface the version caveats reviewers flagged (working-paper versions, author-list issues) so the README can carry them.`,
  { label: 'calibrate', phase: 'Calibrate', schema: RANK_SCHEMA, model: 'opus', effort: 'high' })

return { reviewed: good.length, ranked }