export const meta = {
  name: 'governance-citation-graph',
  description: 'Citation-graph search around the governance directory top tier',
  phases: [
    { title: 'Graph', detail: '4 agents walk references + citers of 13 starred works' },
    { title: 'Synthesize', detail: 'dedup, rank, recommend acquisitions' },
  ],
}

const PURPOSE = `
PROJECT CONTEXT (judge relevance against this):
A position paper argues continuous optimization of computing systems is an
UNDER-PROVIDED PUBLIC GOOD - a collective-action failure, not a physics limit -
and cheap machine intelligence changes the supply economics. The
governance-and-state-capacity reading directory carries the institutional record
of the analogous problem in government: counsel institutions built and
withdrawn (Kennedy School, PPBS, OTA/CBO), capacity decay (proceduralism,
administrative burden), and capture/rents economics (Olson, Teles, Frischmann).
The paper ASSEMBLES a bridge from policy-capture economics to technical
under-provision - it never claims novelty; more published work is strictly
better. We are looking for: (a) SEMINAL works these papers stand on that we lack;
(b) recent work that extends/tests/refutes them; (c) anything that touches BOTH
capture economics AND technical infrastructure (the bridge we assemble);
(d) genuine objections. NOT looking for: topical policy commentary, think-tank
ephemera, or repeats of what is already on disk.`

const ONDISK_SCHEMA = { type: 'object', required: ['candidates'], properties: {
  candidates: { type: 'array', items: { type: 'object',
    required: ['handle', 'year', 'why', 'direction', 'seed', 'oa_hint'],
    properties: {
      handle: { type: 'string', description: 'Author(s), title, venue, year - enough to acquire it' },
      year: { type: 'integer' },
      why: { type: 'string', description: 'what it adds to THIS project, <=40 words' },
      direction: { type: 'string', enum: ['reference', 'citer'], description: 'found among the seed\'s references or its citers' },
      seed: { type: 'string', description: 'which seed work led here' },
      score: { type: 'integer', minimum: 1, maximum: 3, description: '3=acquire now, 2=worth having, 1=marginal' },
      objection: { type: 'boolean' },
      oa_hint: { type: 'string', description: 'DOI/arXiv/repository URL if seen, else ""' },
    } } } } }

const SEEDS = [
  ['Frischmann 2005 "An Economic Theory of Infrastructure and Commons Management" Minnesota Law Review 89:917',
   'Olson 1996 "Big Bills Left on the Sidewalk" Journal of Economic Perspectives 10(2):3-24',
   'Bessen & Nuvolari 2019 "Diffusing new technology without dissipating rents" (Lean\'s Engine Reporter; also circulated as a BU working paper)'],
  ['Bagley 2019 "The Procedure Fetish" Michigan Law Review 118:345',
   'Yackee & Yackee 2024 "Procedural constraints and regulatory ossification in the US states" Regulation & Governance doi:10.1111/rego.12627',
   'Teles 2013 "Kludgeocracy in America" National Affairs 17 (magazine essay - graph its named sources: Mettler submerged state, Howard, Derthick, and who cites Teles academically)'],
  ['Zingales 2017 "Towards a Political Theory of the Firm" JEP 31(3) / NBER w23593',
   'Furman & Orszag 2015 "A Firm-Level Perspective on the Role of Rents in the Rise in Inequality"',
   'Gutierrez & Philippon 2018 "How European Markets Became Free / How EU Markets Became More Competitive" NBER w24700'],
  ['Shapiro 2001 "Navigating the Patent Thicket" Innovation Policy and the Economy 1',
   'Hall & Ziedonis 2001 "The Patent Paradox Revisited" RAND Journal of Economics 32(1) (the WP on disk is Hall & Ham NBER w7062)',
   'Karlson, Sandstrom & Wennberg 2021 "Bureaucrats or Markets in Innovation Policy?" Ratio WP 331 / Review of Austrian Economics',
   'Hsieh & Moretti 2019 "Housing Constraints and Spatial Misallocation" AEJ:Macro 11(2) + Greaney comment'],
]

phase('Graph')
const found = await parallel(SEEDS.map((seeds, i) => () => agent(
  `${PURPOSE}

YOUR SEEDS:
${seeds.map(s => '  - ' + s).join('\n')}

For each seed, walk its citation graph using the OpenAlex API (api.openalex.org,
no key needed; use https://api.openalex.org/works?search=... to find the work,
then its referenced_works and cites filter for citers, e.g.
https://api.openalex.org/works?filter=cites:W123 sorted by cited_by_count).
Semantic Scholar api.semanticscholar.org/graph/v1 as fallback (handle 429s by
slowing down). For each seed collect:
  - its most-cited REFERENCES (the shoulders it stands on),
  - its most-cited and most-relevant CITERS (who built on it since),
and filter hard against the project purpose - return only works a careful
reader of this project would actually want, scored 1-3. Aim for the best
5-12 candidates per seed, not exhaustiveness. EXCLUDE works already on disk:
Olson 1965/1982/1996, Frischmann 2005+his 2019 book is NOT on disk (fair game),
Teles 2013/2015, Bagley, Yackee, Moynihan x2, Pahlka, Dunkelman, Hsieh-Moretti,
Greaney, Zingales 2017, G-P 2017/2018, Furman-Orszag, Lemley 2005,
Bessen-Nuvolari, Boldrin-Levine, Shapiro 2001, Hall-Ziedonis, Karlson,
Jasanoff 2006, Irving 2018, and the counsel directory's Lippmann/Dewey/Downs/
Landemore line. Also EXCLUDE: Markov's CACM AlphaChip critique (project
convention: never cite) and the RETRACTED Whitehouse et al. Nature 2019.
Record real bibliographic handles from the API - never from memory.`,
  { label: `graph:${i + 1}`, phase: 'Graph', schema: ONDISK_SCHEMA }
)))

const candidates = found.filter(Boolean).flatMap(f => f.candidates || [])
log(`${candidates.length} candidates before dedup`)

phase('Synthesize')
const report = await agent(
  `${PURPOSE}

Below are ${candidates.length} candidate works surfaced by walking the citation
graphs of the governance directory's top-ranked works. Deduplicate (same work
surfaced from multiple seeds - merge, keep all seed attributions), then write a
compact MARKDOWN report:

1. "## Acquire now" - the 3-scored works after dedup, each with: handle, which
   seeds led to it (convergence from multiple seeds is itself evidence), why in
   one sentence, and the oa_hint. Rank by value to the project. Be ruthless -
   if a 3 does not deserve it, demote it and say so.
2. "## Worth having" - the 2s, one line each.
3. "## Objections found" - anything objection:true, at any score, with why.
4. "## What the graph says about the bridge" - did ANY candidate touch both
   capture economics and technical infrastructure? If none did, say plainly
   that the graph walk CONFIRMS the absence again.
5. "## Convergences" - works surfaced independently from 2+ seeds.

Return ONLY the markdown.

CANDIDATES:
${JSON.stringify(candidates, null, 1)}`,
  { label: 'synthesize', phase: 'Synthesize', effort: 'high' }
)

return { n: candidates.length, report }
