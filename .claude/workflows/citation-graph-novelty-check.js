export const meta = {
  name: 'citation-graph-knowledge-problem',
  description: 'Forward/backward citation sweep around the tier-1 works to test the Hayek-criterion novelty claim',
  phases: [
    { title: 'Sweep', detail: 'per-seed forward-citation harvest + screening', model: 'opus' },
    { title: 'Verify', detail: 'adversarial check of each threat-to-novelty candidate', model: 'opus' },
  ],
}

const API_HELP = `USE THE CITATION APIS VIA curl (Google Scholar itself is bot-walled and must not be scraped):
- Semantic Scholar: https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>/citations?fields=title,year,venue,abstract,authors,externalIds&limit=100
  (also /references for backward; search: /graph/v1/paper/search?query=...&fields=title,year,venue,abstract)
- OpenAlex: resolve id via https://api.openalex.org/works/doi:<doi> then forward cites via
  https://api.openalex.org/works?filter=cites:<W-id>&per-page=100&sort=cited_by_count:desc
  (also full-text search: https://api.openalex.org/works?search=...&filter=from_publication_year:2015)
Both are free, no key. Paginate if needed. If a seed has no DOI, find it by title search first.`

const PROJECT = `CONTEXT — what the citation sweep is testing.
A position paper plans a novel "HAYEK CRITERION": decomposing what an intelligence would need to solve the socialist-calculation / knowledge problem into FOUR measurable requirements:
 (1) BANDWIDTH — aggregate dispersed local knowledge at fidelity >= what the price system transmits (benchmark: communication-complexity lower bounds, Mount-Reiter / Jordan / Nisan-Segal).
 (2) COMPUTATION — solve/approximate allocation within a tractable class (PPAD/FIXP hardness vs Eisenberg-Gale convex tractability).
 (3) ELICITATION — obtain truthful state, by incentive-compatible mechanism or by inference from behavior (Hurwicz; Fadel-Segal).
 (4) DRIFT — re-solve faster than the economy changes (Hayek 1945: "economic problems arise always and only in consequence of change"). WE BELIEVE THIS ONE IS UNFORMALIZED IN THIS DEBATE.
Our claimed novelty: NO prior work assembles all four quantitatively. Nearest neighbors already known: Brynjolfsson & Hitzig, "AI's Use of Knowledge in Society" (NBER 2025 — same premise, no criterion); Gmeiner & Harper (AI & Society 2024 — same four concerns, qualitative); Fadel & Segal 2009 (only quantitative PAIRWISE combination we know of).
YOUR JOB IS TO TRY TO FALSIFY THAT NOVELTY CLAIM, and to find work we should be citing.`

const FIND_SCHEMA = {
  type: 'object', required: ['candidates', 'seed_note'],
  properties: {
    seed_note: { type: 'string', description: 'what the forward-citation set around this seed looks like overall' },
    candidates: { type: 'array', items: {
      type: 'object', required: ['title', 'year', 'venue', 'why', 'threat_level'],
      properties: {
        title: { type: 'string' }, year: { type: 'integer' }, venue: { type: 'string' },
        authors: { type: 'string' }, doi_or_id: { type: 'string' },
        components_covered: { type: 'string', description: 'which of bandwidth/computation/elicitation/drift it addresses' },
        why: { type: 'string', description: 'what it establishes and why it matters to us' },
        threat_level: { type: 'string', enum: ['assembles-criterion', 'formalizes-drift', 'multi-component', 'should-cite', 'context'] },
      } } },
  },
}

const VERIFY_SCHEMA = {
  type: 'object', required: ['isReal', 'verdict', 'reason'],
  properties: {
    isReal: { type: 'boolean', description: 'true if this genuinely threatens or constrains the novelty claim' },
    verdict: { type: 'string', enum: ['pre-empts-criterion', 'partially-pre-empts', 'must-cite-not-a-threat', 'not-relevant'] },
    reason: { type: 'string' },
    how_to_position: { type: 'string', description: 'concrete: how the paper should cite or distinguish itself from this' },
  },
}

// Seeds: the tier-1 spine + the modern near-neighbors + the scheduler anchors.
const SEEDS = [
  { key: 'hayek-1945', q: 'Hayek "The Use of Knowledge in Society" AER 1945 — forward citations are enormous, so RESTRICT to 2015+ and to works that formalize or quantify the knowledge problem (ignore general econ/management uses).' },
  { key: 'brynjolfsson-hitzig-2025', q: 'Brynjolfsson & Hitzig, "AI\'s Use of Knowledge in Society" (NBER chapter, The Economics of Transformative AI, 2025). BOTH directions: who cites it already, AND what its own bibliography cites (that tells us what the closest prior author considered). This is the single most important seed.' },
  { key: 'nisan-segal-2006', q: 'Nisan & Segal, "The communication requirements of efficient allocations and supporting prices", JET 129(1) 2006, doi:10.1016/j.jet.2004.10.007. Forward cites — especially anything applying these bounds to AI/planning/learning systems.' },
  { key: 'mount-reiter-jordan', q: 'Mount & Reiter "The informational size of message spaces" JET 1974 (doi:10.1016/0022-0531(74)90012-x) and Jordan "The competitive allocation process is informationally efficient uniquely" JET 1982 (doi:10.1016/0022-0531(82)90088-6). Forward cites, recent especially.' },
  { key: 'fadel-segal-2009', q: 'Fadel & Segal "The communication cost of selfishness" JET 2009 (doi:10.1016/j.jet.2007.09.015). Forward cites — anyone extending the bandwidth+incentive combination, or adding a third dimension.' },
  { key: 'ppad-line', q: 'Daskalakis-Goldberg-Papadimitriou Nash complexity (doi:10.1137/070699652) and Chen-Deng-Teng (JACM 2009). Forward cites that connect equilibrium hardness to ECONOMIC PLANNING feasibility (not pure algorithmic game theory).' },
  { key: 'tractable-markets', q: 'Eisenberg-Gale 1959 / Devanur et al. JACM 2008 (doi:10.1145/1411509.1411512) / Vazirani-Yannakakis. Forward cites on tractable market equilibrium computation, especially anything arguing real economies fall in or out of the tractable class.' },
  { key: 'boettke-candela-2023', q: 'Boettke & Candela "On the feasibility of technosocialism" JEBO 205 (doi:10.1016/j.jebo.2022.10.046) + Lambert & Fegley JEBO 206 (doi:10.1016/j.jebo.2022.12.009). Forward AND backward: the Austrian side of the AI-planning debate 2022-2026.' },
  { key: 'gmeiner-harper-2024', q: 'Gmeiner & Harper "Artificial intelligence and economic planning" AI & Society 39(3) 2024 (doi:10.1007/s00146-022-01523-x). Forward cites and its own references — it has the same four concerns qualitatively, so who built on it?' },
  { key: 'cockshott-cottrell', q: 'Cockshott & Cottrell "Information and Economics: A Critique of Hayek" (RPE 16, 1997) and "Calculation, Complexity and Planning" (RPE 5(1) 1993, doi:10.1080/09538259300000005). Forward cites — the computability-socialism line through 2026.' },
  { key: 'dynamic-mechanism-design', q: 'CRITICAL SEED FOR THE DRIFT CLAIM. Search the DYNAMIC MECHANISM DESIGN literature: Pavan, Segal & Toikka "Dynamic Mechanism Design: A Myersonian Approach" (Econometrica 2014); Bergemann & Välimäki "Dynamic Mechanism Design: An Introduction" (JEL 2019); Bergemann & Said. Question: does this literature ALREADY formalize re-solving/tracking a CHANGING environment in a way that covers our DRIFT component? Report honestly — this is the most likely refutation of our "drift is unformalized" claim.' },
  { key: 'online-nonstationary', q: 'ANOTHER DRIFT PROBE: online/dynamic resource allocation and learning in NON-STATIONARY environments — online convex optimization with drift, competitive analysis for allocation, regret under distribution shift, dynamic pricing that tracks changing demand. Does any of it get framed as "keeping up with economic change" in the Hayek sense?' },
  { key: 'scheduler-as-economy', q: 'Borg (EuroSys 2015), DRF (NSDI 2011), Decima (SIGCOMM 2019), and market-based cluster scheduling generally. Question: does ANY published work explicitly frame datacenter schedulers as planned economies or connect them to the calculation debate? We believe not — try hard to falsify.' },
  { key: 'ai-economist-line', q: 'Zheng et al. "The AI Economist" (Science Advances 2022, doi:10.1126/sciadv.abk2607) and Koster et al. "Democratic AI" (Nature Human Behaviour 2022). Forward cites — RL/ML for economic mechanism design 2022-2026, especially anything claiming to solve allocation better than markets.' },
  { key: 'tacit-datafication', q: 'Autor "Polanyi\'s Paradox" (NBER 20485) and Hilbert-Lopez (Science 2011, doi:10.1126/science.1200970). Forward cites on whether ML CODIFIES tacit knowledge — the evidence base for our claim that Hayek\'s tacit premise is eroding.' },
]

phase('Sweep')
const swept = await pipeline(
  SEEDS,
  s => agent(`${PROJECT}\n\n${API_HELP}\n\nSEED: ${s.q}\n\nHarvest the citation neighborhood, screen it, and report only what matters. Prioritize: (a) anything that ASSEMBLES two or more criterion components quantitatively; (b) anything that FORMALIZES drift/non-stationarity in an economic-coordination setting; (c) anything we plainly ought to be citing. Ignore the long tail of routine citations. Cap at 8 candidates; fewer is fine. Give verified handles (title/year/venue/DOI) — do not invent citations. If the neighborhood contains nothing threatening, say so plainly in seed_note; a clean negative result is a valuable answer here.`,
    { label: `sweep:${s.key}`, phase: 'Sweep', schema: FIND_SCHEMA, model: 'opus', effort: 'medium' })
    .catch(() => null),
  (res, seed) => {
    if (!res) return []
    const threats = (res.candidates || []).filter(c =>
      c.threat_level === 'assembles-criterion' || c.threat_level === 'formalizes-drift' || c.threat_level === 'multi-component')
    return parallel(threats.map(c => () =>
      agent(`${PROJECT}\n\n${API_HELP}\n\nA sweep agent flagged this as a possible threat to the novelty claim (from the ${seed.key} neighborhood):\n\nTITLE: ${c.title} (${c.year}, ${c.venue})\nID: ${c.doi_or_id || 'n/a'}\nCOMPONENTS CLAIMED: ${c.components_covered}\nWHY FLAGGED: ${c.why}\n\nGo read the actual abstract/paper (fetch it — S2/OpenAlex/arXiv/publisher page). Decide honestly: does it genuinely pre-empt or constrain the four-part Hayek criterion? Default to isReal=false for work that merely discusses the knowledge problem, applies one component, or is qualitative. Set isReal=true only if it (a) quantitatively combines 2+ components, or (b) formalizes drift/tracking in an economic-coordination setting, or (c) states a comparable intelligence criterion. Then give how_to_position: exactly how our paper should cite or distinguish itself.`,
        { label: `verify:${(c.title||'').slice(0,28)}`, phase: 'Verify', schema: VERIFY_SCHEMA, model: 'opus', effort: 'medium' })
        .then(v => ({ ...c, seed: seed.key, verify: v }))
        .catch(() => null)))
      .then(rs => ({ seed: seed.key, seed_note: res.seed_note, all: res.candidates || [], verified: rs.filter(Boolean) }))
  })

const rows = swept.filter(Boolean)
const verified = rows.flatMap(r => r.verified || [])
return {
  seeds_reported: rows.length,
  confirmed_threats: verified.filter(v => v.verify?.isReal).map(v => ({
    title: v.title, year: v.year, venue: v.venue, id: v.doi_or_id, seed: v.seed,
    verdict: v.verify.verdict, reason: v.verify.reason, position: v.verify.how_to_position })),
  dismissed: verified.filter(v => v.verify && !v.verify.isReal).map(v => ({ title: v.title, reason: v.verify.reason })),
  should_cite: rows.flatMap(r => (r.all || []).filter(c => c.threat_level === 'should-cite')
    .map(c => ({ title: c.title, year: c.year, venue: c.venue, id: c.doi_or_id, why: c.why, seed: r.seed }))),
  seed_notes: rows.map(r => ({ seed: r.seed, note: r.seed_note })),
}