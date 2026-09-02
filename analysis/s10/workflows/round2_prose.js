export const meta = {
  name: 'round2-prose',
  description: 'Track B: blind multi-model writing-quality pass over S10 — propose, de-author, no-self-vote multi-factor ballot (prose + structural rubrics), synthesize into gated per-change records',
  phases: [
    { title: 'Propose' },
    { title: 'Vote' },
    { title: 'Synthesize' },
  ],
}

// ---------------------------------------------------------------------------
// args: { scope, draft }
//   scope : "all" for the whole paper, or a section label for the pilot ("4.6")
//   draft : repo-relative manuscript path (default the S10 writeup)
// Run from a claude-mixed session so the external agent models route.
// No MIX / no semantic clustering: each proposal is its own de-authored
// candidate; only byte-identical proposals for the same locus are collapsed
// (support count + unioned provenance). The proposer supplies the current
// text it is replacing (the workflow JS sandbox cannot read the draft).
// ---------------------------------------------------------------------------
const DRAFT = (args && args.draft) || 'analysis/s10/S10-WRITEUP-DRAFT.md'
const SCOPE = (args && args.scope) || 'all'

const PANEL = [
  { id: 'anthropic', type: 'panel-anthropic', family: 'fable' },
  { id: 'openai',    type: 'panel-openai',    family: 'openai' },
  { id: 'google',    type: 'panel-google',    family: 'google' },
  { id: 'xai',       type: 'panel-xai',       family: 'xai' },
  { id: 'moonshot',  type: 'panel-moonshot',  family: 'moonshot' },
  { id: 'alibaba',   type: 'panel-alibaba',   family: 'alibaba' },
  { id: 'deepseek',  type: 'panel-deepseek',  family: 'deepseek' },
]
const GENERATORS = [
  { id: 'gen-prose',   type: 'gen-prose',   family: 'fable' },
  { id: 'gen-dataviz', type: 'gen-dataviz', family: 'fable' },
]
const PROPOSERS = [...PANEL, ...GENERATORS]

// ======================= STAGE PROMPTS (review these) =======================

const PROPOSE_PROMPT = (isGen) => `ROLE: PROPOSE.
Read the manuscript at \`${DRAFT}\`${SCOPE === 'all' ? '' : `, section ${SCOPE} only`}.
${isGen
  ? 'Follow your reference brief exactly (read it first, as your definition instructs).'
  : 'Propose writing and structure improvements on the merits.'}

Return a changelist. Each entry is ONE concrete, self-contained change:
- type: "structural" (reorder / merge / split / move a section or subsection)
        or "prose" (rewrite a specific passage).
- locus: the section number plus a short verbatim quote (<=12 words) of where
  the change starts, so it can be located exactly.
- action: reorder | merge | split | move | rewrite.
- current: the exact current text you are changing — the full paragraph for a
  prose change, or the section as it stands (heading + one-line gist) for a
  structural change. Copy it verbatim; a voter will compare against it.
- proposed: for prose, the full replacement text; for structural, the exact
  move ("move to before §Y", "merge into §Y", "split after '<quote>'").
- rationale: one or two sentences; name the principle if you apply one.

Absolute constraint: change presentation and structure only. Never alter a
number, add or drop a claim, or change how hedged a claim is. If a passage is
already good, do not propose a change — silence is a valid answer. Propose
only changes you would defend to a skeptical co-author.`

const VOTE_PROSE = (c) => `ROLE: VOTE (prose change), authorship removed.

CURRENT (§${c.locus}):
${c.current}

PROPOSED rewrite:
${c.proposed}
RATIONALE: ${c.rationale}

Return an object:
- faithfulness: "pass" | "fail" — FAIL if it changes any number, adds/drops a
  claim, or changes how hedged a claim is. Hard gate.
- clarity: 1-5 (reader comprehension vs current; 3 = no change)
- voice: 1-5 (match to a confident, plain house voice; penalize blandification)
- concision: 1-5
- structural_soundness: 3 (not applicable to a prose change)
- keep: true | false (should this replace the current text?)
- why: one sentence. Judge only the text; do not guess who wrote it.`

const VOTE_STRUCTURAL = (c) => `ROLE: VOTE (structural change), authorship removed.

CURRENT PLACEMENT (§${c.locus}):
${c.current}

PROPOSED MOVE (${c.action}):
${c.proposed}
RATIONALE: ${c.rationale}

Return an object:
- faithfulness: "pass" | "fail" — FAIL only if the move would strand a
  reference, duplicate content, or require changing a claim to work. Hard gate.
- clarity: 1-5 (does the new order read more logically? 3 = no change)
- voice: 3 (not applicable to a move)
- concision: 1-5 (does it remove redundancy / tighten the outline?)
- structural_soundness: 1-5 (does the target location fit; do dependencies
  still resolve in the new order?)
- keep: true | false (should the manuscript adopt this move?)
- why: one sentence. Judge only the proposed structure.`

const PROPOSAL_SCHEMA = { type: 'object', required: ['changes'], properties: { changes: { type: 'array', items: {
  type: 'object', required: ['type', 'locus', 'action', 'current', 'proposed', 'rationale'],
  properties: { type: { enum: ['structural', 'prose'] }, locus: { type: 'string' },
    action: { enum: ['reorder', 'merge', 'split', 'move', 'rewrite'] },
    current: { type: 'string' }, proposed: { type: 'string' }, rationale: { type: 'string' } } } } } }

const VOTE_SCHEMA = { type: 'object',
  required: ['faithfulness', 'clarity', 'voice', 'concision', 'structural_soundness', 'keep', 'why'],
  properties: { faithfulness: { enum: ['pass', 'fail'] }, clarity: { type: 'integer' },
    voice: { type: 'integer' }, concision: { type: 'integer' },
    structural_soundness: { type: 'integer' }, keep: { type: 'boolean' }, why: { type: 'string' } } }

// ============================== ORCHESTRATION ==============================

phase('Propose')
const raw = await parallel(PROPOSERS.map(m => () =>
  agent(PROPOSE_PROMPT(m.type.startsWith('gen-')),
        { agentType: m.type, label: `propose:${m.id}`, schema: PROPOSAL_SCHEMA })
    .then(r => ({ member: m.id, family: m.family, changes: (r && r.changes) || [] }))))
const proposals = []
for (const p of raw.filter(Boolean))
  for (const c of p.changes) proposals.push({ ...c, member: p.member, family: p.family })
log(`${proposals.length} proposals from ${raw.filter(Boolean).length} proposers`)

// de-author -> candidates. Collapse only byte-identical (locus, action, proposed).
const byKey = {}
for (const c of proposals) {
  const k = `${c.locus}|${c.action}|${c.proposed}`
  if (!byKey[k]) byKey[k] = { locus: c.locus, type: c.type, action: c.action,
    current: c.current, proposed: c.proposed, rationale: c.rationale,
    support: 0, author_families: new Set() }
  byKey[k].support += 1
  byKey[k].author_families.add(c.family)
}
const candidates = Object.values(byKey).map((c, i) =>
  ({ ...c, id: `C${i + 1}`, author_families: [...c.author_families] }))
log(`${candidates.length} de-authored candidates (from ${proposals.length} proposals)`)

phase('Vote')
const scored = await parallel(candidates.map(cand => async () => {
  const eligible = PANEL.filter(m => !cand.author_families.includes(m.family))
  const prompt = cand.type === 'structural' ? VOTE_STRUCTURAL(cand) : VOTE_PROSE(cand)
  const ballots = await parallel(eligible.map(v => () =>
    agent(prompt, { agentType: v.type, label: `vote:${cand.id}:${v.id}`, schema: VOTE_SCHEMA })
      .then(s => ({ voter: v.id, ...s })).catch(() => null)))
  return { ...cand, votes: ballots.filter(Boolean) }
}))

phase('Synthesize')
const decide = (c) => {
  const v = c.votes
  const faith_fail = v.some(x => x.faithfulness === 'fail')
  const keeps = v.filter(x => x.keep).length
  const composite = v.length
    ? Math.round((v.reduce((s, x) => s + x.clarity + x.voice + x.concision + x.structural_soundness, 0) / v.length) * 100) / 100
    : 0
  return { accepted: !faith_fail && keeps > v.length / 2, keeps, n: v.length, faith_fail, composite }
}
const results = candidates
  .map((c, i) => ({ ...c, votes: scored[i].votes, verdict: decide(scored[i]) }))
  .sort((a, b) => String(a.locus).localeCompare(String(b.locus)))   // report order = document order
return {
  scope: SCOPE,
  n_proposals: proposals.length,
  n_candidates: candidates.length,
  accepted: results.filter(r => r.verdict.accepted).length,
  changes: results,   // full per-change record: current/proposed, every voter's factors, verdict, provenance
}
