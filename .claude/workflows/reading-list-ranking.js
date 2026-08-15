export const meta = {
  name: 'reading-list-ranking',
  description: 'Review each PDF and assign a multi-factor importance ranking for the reading list',
  phases: [
    { title: 'Review', detail: 'one agent per paper reads it and scores three factors', model: 'opus' },
    { title: 'Calibrate', detail: 'cross-paper normalization into three tiers', model: 'opus' },
  ],
}

const DIR = '/home/matt/reading/software-economies-and-the-knowledge-problem'

// Context every reviewer needs: what the paper the reading list serves is about.
const PROJECT = `The reading list serves a position paper ("Towards the Cosmic AC", in ~/performance_commons). Two clusters:
(A) SOFTWARE ECONOMIES — the paper argues "continuous optimization is an under-provided public good," rebuilt on the economics-of-software literature (public-goods under-provision; open provision winning for complex goods; commons that already exist like BLAS/LAPACK and cuDNN; the claim that as ML collapses production+packaging cost, the public-good share of software rises toward all of it).
(B) THE KNOWLEDGE PROBLEM — the paper plans a novel "Hayek criterion": decomposing what an intelligence would need to solve the socialist-calculation problem into four measurable requirements — aggregation BANDWIDTH (vs the market's communication lower bounds), COMPUTATION (equilibrium-hardness vs convex tractability), truthful ELICITATION (incentive compatibility), and DRIFT-tracking (re-solving faster than the economy changes — the component nobody has formalized). The paper positions against Brynjolfsson-Hitzig 2025 (same premise, no criterion) and must answer the Austrian discovery objection (Hayek 1968 / Boettke-Candela: competition GENERATES knowledge, it doesn't just transmit it). It will also claim datacenter schedulers are the first economies born past the criterion.`

const SCORE_SCHEMA = {
  type: 'object',
  required: ['file', 'relevance_to_project', 'field_standing', 'quality', 'one_line', 'load_bearing_for'],
  properties: {
    file: { type: 'string' },
    relevance_to_project: { type: 'integer', minimum: 1, maximum: 10, description: 'how directly this supports a claim the paper makes or the criterion needs' },
    field_standing: { type: 'integer', minimum: 1, maximum: 10, description: 'citation weight / canonical status / venue in its own field' },
    quality: { type: 'integer', minimum: 1, maximum: 10, description: 'publicly recognized quality and rigor of the work itself' },
    which_cluster: { type: 'string', enum: ['A-software-economies', 'B-knowledge-problem', 'both'] },
    which_criterion_component: { type: 'string', description: 'if cluster B: bandwidth | computation | elicitation | drift | canon | opponent | ML-instance | none' },
    load_bearing_for: { type: 'string', description: 'the specific claim/section it supports, or "context" if background only' },
    one_line: { type: 'string', description: 'one sentence: what it establishes, judged from reading it' },
    caveat: { type: 'string', description: 'edition/version/provenance issue noticed while reading, or empty' },
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
    notes: { type: 'string', description: 'calibration notes: any reviewer scores overridden and why; disagreements with the prior hand-ranking worth flagging' },
  },
}

const files = ["akerlof-1970-market-for-lemons.pdf", "arrow-1969-organization-economic-activity.pdf", "autor-2014-polanyis-paradox.pdf", "bessen-2005-complex-public-goods.pdf", "boettke-candela-2023-feasibility-of-technosocialism.pdf", "brynjolfsson-hitzig-2025-ai-use-of-knowledge.pdf", "brynjolfsson-mcelheran-2016-data-driven-decision-making.pdf", "chen-deng-teng-2009-two-player-nash.pdf", "chetlur-1410.0759-cudnn.pdf", "coase-1937-nature-of-the-firm.pdf", "cockshott-cottrell-1993-towards-new-socialism.pdf", "cockshott-cottrell-1997-hayek-critique.pdf", "cottrell-cockshott-1993-calculation-complexity-planning.pdf", "crookedtimber-2012-red-plenty-seminar.pdf", "dapprich-greenwood-2024-cybersocialism.pdf", "daskalakis-goldberg-papadimitriou-2009-complexity-of-nash.pdf", "devanur-2008-market-equilibrium-primal-dual.pdf", "dongarra-1995-linear-algebra-libraries.pdf", "eghbal-2016-roads-and-bridges.pdf", "eisenberg-gale-1959-consensus-subjective-probabilities.pdf", "fadel-segal-2009-communication-cost-of-selfishness.pdf", "fursin-2009-collective-optimization.pdf", "ghodsi-2011-dominant-resource-fairness.pdf", "hayek-1937-economics-and-knowledge.pdf", "hayek-1940-socialist-calculation-competitive-solution.pdf", "hayek-1945-use-of-knowledge.pdf", "hayek-2002-competition-discovery-procedure.pdf", "hilbert-lopez-2011-worlds-technological-capacity.pdf", "hoffmann-2024-value-of-open-source.pdf", "hurwicz-2008-guard-the-guardians.pdf", "johnson-2001-economics-of-open-source.pdf", "jordan-1979-competitive-allocation-informationally-efficient.pdf", "keynes-1930-economic-possibilities.pdf", "koster-2022-democratic-ai.pdf", "lerner-2002-simple-economics-open-source.pdf", "mao-2016-deeprm-resource-management.pdf", "mao-2019-decima-learning-scheduling.pdf", "mises-1920-economic-calculation.pdf", "mount-reiter-1973-informational-size-message-spaces.pdf", "myerson-2008-mechanism-design-perspectives.pdf", "nagle-2019-oss-firm-productivity.pdf", "nisan-segal-2006-communication-requirements-prices.pdf", "papadimitriou-1994-parity-argument-ppad.pdf", "samuelson-1954-pure-theory-public-expenditure.pdf", "segal-2006-communication-in-economic-mechanisms.pdf", "simon-1956-rational-choice-environment.pdf", "varian-2004-system-reliability-free-riding.pdf", "verma-2015-borg.pdf", "vonhippel-2003-private-collective-innovation.pdf", "woodside-2007-future-of-spe.pdf", "zheng-2022-ai-economist.pdf"]
log(`${files.length} papers to review`)

phase('Review')
const scored = await parallel(files.map(f => () =>
  agent(`${PROJECT}

Read the PDF at ${DIR}/${f} (use pdftotext or the Read tool; for long books read the intro/abstract/conclusion and skim the body — enough to judge it). Then score it on three 1-10 factors as a reviewer who has actually read it, not from the title:
- relevance_to_project: how directly it supports a claim THIS paper makes or a component the Hayek criterion needs;
- field_standing: its canonical status / citation weight / venue in its OWN field;
- quality: publicly recognized rigor and quality of the work itself.
Assign which_cluster and (for cluster B) which_criterion_component. Say what it is load_bearing_for. Note any edition/version/provenance caveat you notice from the actual file (e.g. it's a working-paper draft, a chapter extract with different pagination, a review not the book). Be honest and calibrated — most papers are a 5-7 on field_standing; reserve 9-10 for genuinely canonical work (Hayek 1945, Mises, Nash-complexity, Samuelson, Akerlof).`,
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
2. Sort, and cut into three tiers: TIER 1 (must-read — top of the list, structurally load-bearing AND high standing), TIER 2 (strong on at least one factor), TIER 3 (context/secondary). Aim roughly for 12-16 in tier 1, the rest split by the natural gaps in composite — but let the gaps decide, not a quota.
3. Independent reviewers over-score their own paper; correct obvious inflation (a minor systems paper rated 9 on field_standing should come down). Note any such overrides.
4. Give rank_within_cluster so each of cluster A and cluster B has its own ordering.
Return every file with its tier, composite, within-cluster rank, and a one-line rationale citing the factors.`,
  { label: 'calibrate', phase: 'Calibrate', schema: RANK_SCHEMA, model: 'opus', effort: 'high' })

return { reviewed: good.length, ranked }