export const meta = {
  name: 'round2-prose',
  description: 'Track B: blind multi-model writing-quality pass over S10 — propose, de-author + mix, no-self-vote multi-factor ballot, synthesize into gated diffs',
  phases: [
    { title: 'Propose' },
    { title: 'Mix' },
    { title: 'Vote' },
    { title: 'Synthesize' },
  ],
}

// ---------------------------------------------------------------------------
// args: { scope, draft }
//   scope : "all" for the whole paper, or a section-group label for the pilot
//           (e.g. "4.6" to run only the cohort section and its subsections)
//   draft : repo-relative path to the manuscript (default the S10 writeup)
// Run from a claude-mixed session so the external agent models route.
// ---------------------------------------------------------------------------
const DRAFT = (args && args.draft) || 'analysis/s10/S10-WRITEUP-DRAFT.md'
const SCOPE = (args && args.scope) || 'all'

// review panel: id -> agentType. All seven vote; the Anthropic seat is Fable.
const PANEL = [
  { id: 'anthropic', type: 'panel-anthropic', family: 'fable' },
  { id: 'openai',    type: 'panel-openai',    family: 'openai' },
  { id: 'google',    type: 'panel-google',    family: 'google' },
  { id: 'xai',       type: 'panel-xai',       family: 'xai' },
  { id: 'moonshot',  type: 'panel-moonshot',  family: 'moonshot' },
  { id: 'alibaba',   type: 'panel-alibaba',   family: 'alibaba' },
  { id: 'deepseek',  type: 'panel-deepseek',  family: 'deepseek' },
]
// generation members: propose-only, Fable-family (so Fable self-excludes from voting on them)
const GENERATORS = [
  { id: 'gen-prose',   type: 'gen-prose',   family: 'fable' },
  { id: 'gen-dataviz', type: 'gen-dataviz', family: 'fable' },
]
const PROPOSERS = [...PANEL, ...GENERATORS]

// ======================= STAGE PROMPTS (review these) =======================

const PROPOSE_PROMPT = (who) => `ROLE: PROPOSE.
Read the manuscript at \`${DRAFT}\`${SCOPE === 'all' ? '' : `, section-group ${SCOPE} only`}.
${who.generator
  ? 'Follow your reference brief exactly (read it first, as your definition instructs).'
  : 'Propose writing and structure improvements on the merits.'}

Return a changelist. Each entry is ONE concrete, self-contained change:
- type: "structural" (reorder / merge / split / move a section or subsection)
        or "prose" (rewrite a specific passage).
- locus: the section number and a short verbatim quote (<=12 words) of the
  passage's first words, so the change can be located exactly.
- action: reorder | merge | split | move | rewrite.
- proposed: for prose, the full replacement text; for structural, the exact
  move ("move §X to before §Y", "merge §X into §Y", etc.).
- rationale: one or two sentences. Name the principle if you are applying one.

Absolute constraint: change presentation and structure only. Never alter a
number, add or drop a claim, or change how hedged a claim is. If a passage
is already good, do not propose a change to it — silence is a valid answer.
Propose only changes you would defend to a skeptical co-author.`

const MIX_PROMPT = (clusterText) => `ROLE: AGGREGATOR (neutral, de-authored).
Below are several proposed changes to the SAME passage, with all authorship
removed. Produce at most THREE distinct candidate variants that a voter
should choose between — merging near-identical proposals into one, and
keeping genuinely different approaches as separate variants. Do not add a
variant of your own invention; only consolidate and mix what is given. For
each variant give the final proposed text/move and a one-line note on what
distinguishes it. Preserve the faithfulness constraint (no number/claim/hedge
change); drop any input proposal that violates it and say so.

PROPOSALS (de-authored):
${clusterText}`

const VOTE_PROMPT = (cand) => `ROLE: VOTE.
Here is ONE candidate change to the manuscript, with authorship removed. The
current text and the proposed change:

CURRENT (§${cand.locus}):
${cand.current}

PROPOSED (${cand.action}):
${cand.proposed}
RATIONALE: ${cand.rationale}

Score it. Return an object:
- faithfulness: "pass" | "fail" — FAIL if it changes any number, adds/drops a
  claim, or changes how hedged a claim is. This is a hard gate.
- clarity: 1-5 (reader comprehension vs the current text; 3 = no change)
- voice: 1-5 (match to a confident, plain house voice; penalize blandification)
- concision: 1-5
- structural_soundness: 1-5 (for structural changes; 3 if prose-only)
- keep: true | false (your bottom-line: should this replace the current text?)
- why: one sentence.
Judge only the text. Do not guess who wrote it.`

// ============================== ORCHESTRATION ==============================

const PROPOSAL_SCHEMA = { type: 'object', required: ['changes'], properties: { changes: { type: 'array', items: {
  type: 'object', required: ['type', 'locus', 'action', 'proposed', 'rationale'],
  properties: { type: { enum: ['structural', 'prose'] }, locus: { type: 'string' },
    action: { enum: ['reorder', 'merge', 'split', 'move', 'rewrite'] },
    proposed: { type: 'string' }, rationale: { type: 'string' } } } } } }

const VOTE_SCHEMA = { type: 'object',
  required: ['faithfulness', 'clarity', 'voice', 'concision', 'structural_soundness', 'keep', 'why'],
  properties: { faithfulness: { enum: ['pass', 'fail'] }, clarity: { type: 'integer' },
    voice: { type: 'integer' }, concision: { type: 'integer' },
    structural_soundness: { type: 'integer' }, keep: { type: 'boolean' }, why: { type: 'string' } } }

phase('Propose')
const raw = await parallel(PROPOSERS.map(m => () =>
  agent(PROPOSE_PROMPT({ generator: m.type.startsWith('gen-') }),
        { agentType: m.type, label: `propose:${m.id}`, schema: PROPOSAL_SCHEMA })
    .then(r => ({ member: m.id, family: m.family, changes: (r && r.changes) || [] }))))
// attach provenance (member + family) to every proposal; key by (locus-ish, action)
const proposals = []
for (const p of raw.filter(Boolean))
  for (const c of p.changes) proposals.push({ ...c, member: p.member, family: p.family })
log(`${proposals.length} proposals from ${raw.filter(Boolean).length} proposers`)

phase('Mix')
// deterministic clustering by (normalized locus, action); provenance kept in JS
const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9. ]/g, '').slice(0, 40)
const clusters = {}
for (const c of proposals) {
  const k = `${norm(c.locus)}|${c.action}`
  ;(clusters[k] = clusters[k] || []).push(c)
}
const ballot = []
await parallel(Object.entries(clusters).map(([k, group]) => async () => {
  const families = [...new Set(group.map(c => c.family))]      // provenance for self-exclusion
  const deAuthored = group.map((c, i) => `[${i + 1}] (${c.type}/${c.action}) ${c.proposed}\n    rationale: ${c.rationale}`).join('\n')
  // singletons skip the mix agent; clusters of 2+ get consolidated
  let variants
  if (group.length === 1) variants = [{ proposed: group[0].proposed, note: 'single proposal' }]
  else {
    const mixed = await agent(MIX_PROMPT(deAuthored), { agentType: 'panel-google', label: `mix:${k}`,
      schema: { type: 'object', required: ['variants'], properties: { variants: { type: 'array', items: {
        type: 'object', required: ['proposed', 'note'], properties: { proposed: { type: 'string' }, note: { type: 'string' } } } } } } })
    variants = (mixed && mixed.variants) || []
  }
  for (const v of variants) ballot.push({
    locus: group[0].locus, action: group[0].action, type: group[0].type,
    proposed: v.proposed, rationale: v.note, support: group.length,
    author_families: families,                                  // NOT shown to voters
  })
}))
log(`${ballot.length} de-authored candidates on the ballot`)

phase('Vote')
// each candidate voted only by panel members whose FAMILY did not author it (self-exclusion)
const scored = await parallel(ballot.map(cand => async () => {
  const eligible = PANEL.filter(m => !cand.author_families.includes(m.family))
  const cur = '(current text located from locus at synthesis time)'  // filled by the synth step / kept short here
  const ballots = await parallel(eligible.map(v => () =>
    agent(VOTE_PROMPT({ ...cand, current: cur }), { agentType: v.type, label: `vote:${v.id}`, schema: VOTE_SCHEMA })
      .then(s => ({ voter: v.id, ...s })).catch(() => null)))
  return { ...cand, votes: ballots.filter(Boolean) }
}))

phase('Synthesize')
const decide = (c) => {
  const v = c.votes
  const anyFailFaith = v.some(x => x.faithfulness === 'fail')
  const keeps = v.filter(x => x.keep).length
  const composite = v.length ? v.reduce((s, x) => s + x.clarity + x.voice + x.concision + x.structural_soundness, 0) / v.length : 0
  const accepted = !anyFailFaith && keeps > v.length / 2
  return { accepted, keeps, n: v.length, faith_fail: anyFailFaith, composite: Math.round(composite * 100) / 100 }
}
const results = scored.map(c => ({ ...c, verdict: decide(c) }))
  .sort((a, b) => (b.verdict.accepted - a.verdict.accepted) || (b.verdict.composite - a.verdict.composite))
return {
  scope: SCOPE,
  n_proposals: proposals.length,
  n_candidates: ballot.length,
  accepted: results.filter(r => r.verdict.accepted),
  all: results,   // full record (votes + factors + provenance) for panel analysis
}
