export const meta = {
  name: 'round2-iter',
  description: 'Iterating subscription panel pass over S10 — tiered seats propose, ground-truth data-faithfulness gate, blind all-seats ballot (incl. own proposals), synthesize with self-preference stats',
  phases: [
    { title: 'Propose' },
    { title: 'Faithfulness' },
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

const PHASE = String((args && args.phase) || 1)
const ITER = (args && args.iteration) || 1
// Panels per phase (Matthew, 2026-09-02). Every seat proposes AND votes on
// every candidate including its own — no self-exclusion — while staying blind
// to authorship; provenance is kept out of band so self-preference is
// measurable. `effort` is passed through to the agent call.
const PANELS = {
  // wide sweep: full paper + section groups
  '1': [
    { id: 'opus-5-med',   type: 'sub-anthropic-high', family: 'anthropic', effort: 'medium' },
    { id: 'sol',          type: 'sub-openai-mid',     family: 'openai' },
    { id: 'grok-4.6',     type: 'sub-xai-mid',        family: 'xai' },
  ],
  // intermediate: full paper
  '2': [
    { id: 'fable-5.1-hi', type: 'sub-anthropic-fable', family: 'anthropic', effort: 'high' },
    { id: 'sol-high',     type: 'sub-openai-high',     family: 'openai' },
    { id: 'grok-4.6-hi',  type: 'sub-xai-high',        family: 'xai' },
  ],
  // final: the metered labs join the three subscription seats
  '3': [
    { id: 'fable-5.1-hi', type: 'sub-anthropic-fable', family: 'anthropic', effort: 'high' },
    { id: 'sol-high',     type: 'sub-openai-high',     family: 'openai' },
    { id: 'grok-4.6-hi',  type: 'sub-xai-high',        family: 'xai' },
    { id: 'gemini',       type: 'panel-google',        family: 'google' },
    { id: 'kimi',         type: 'panel-moonshot',      family: 'moonshot' },
    { id: 'qwen-max',     type: 'panel-alibaba',       family: 'alibaba' },
    { id: 'deepseek',     type: 'panel-deepseek',      family: 'deepseek' },
  ],
}
const PANEL = PANELS[PHASE]
const PROPOSERS = PANEL

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

Faithfulness constraint — about DATA, not interpretation. You must not alter,
add, or drop any DATUM: a number, statistic, sample size, confidence
interval, the direction of a measured effect, or a statement of what was or
was not found. You MAY revise interpretation, framing, and emphasis — that
is what a rewrite legitimately improves, and voters weigh it. If a passage
is already good, do not propose a change — silence is a valid answer.`

const VOTE_PROSE = (c) => `ROLE: VOTE (prose change), authorship removed.

CURRENT (§${c.locus}):
${c.current}

PROPOSED rewrite:
${c.proposed}
RATIONALE: ${c.rationale}

Return an object:
- data_faithful: "pass" | "fail" — FAIL only if it alters the DATA (a number,
  statistic, sample size, confidence interval, the direction of a measured
  effect, or what was/wasn't found). Changing interpretation, framing, or
  emphasis is NOT a failure.
- dependencies: any companion edit this change requires — a cross-reference to
  update, a figure or table that should move with it, renumbering. "" if none.
  A needed companion edit is NEVER a reason to fail or reject a change: the
  remedy is to make the companion edit. Record it, do not punish it.
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
- data_faithful: "pass" | "fail" — FAIL only if the move would require
  MISSTATING the DATA to work. Reordering that changes only
  interpretation/emphasis is fine.
- dependencies: what must be updated alongside the move — cross-references,
  a figure or table that should travel with the text, section renumbering.
  "" if none. A stranded reference or a figure that needs relocating is a
  DEPENDENCY, never a reason to fail or reject: the correct remedy is to move
  the figure / update the reference. Record it, do not punish it.
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
  required: ['data_faithful', 'clarity', 'voice', 'concision', 'structural_soundness', 'keep', 'why'],
  properties: { data_faithful: { enum: ['pass', 'fail'] }, dependencies: { type: 'string' },
    clarity: { type: 'integer' },
    voice: { type: 'integer' }, concision: { type: 'integer' },
    structural_soundness: { type: 'integer' }, keep: { type: 'boolean' }, why: { type: 'string' } } }

const FAITH_PROMPT = (c) => `ROLE: FAITHFULNESS CHECK — objective, not a quality judgment.
Manuscript file: \`${DRAFT}\`. Open it and find the passage at the locus below.
Verify against the TRUE manuscript text in the file, not the CURRENT text shown.

LOCUS: §${c.locus}
CURRENT (as supplied by the proposer — verify it matches the file):
${c.current}

PROPOSED:
${c.proposed}

Return { locatable, current_matches, data_faithful: "pass"|"fail", note }.
data_faithful is "fail" if any number, statistic, CI/error bar, sample size,
p-value, sign or direction of a measured effect, unit, estimand label, or a
claim of what was/wasn't found changes, is added, or is dropped. Changes to
interpretation, framing, emphasis, hedging, or order are "pass". Fail closed
if you cannot locate the passage or verify a number.`

const FAITH_SCHEMA = { type: 'object',
  required: ['locatable', 'current_matches', 'data_faithful', 'note'],
  properties: { locatable: { type: 'boolean' }, current_matches: { type: 'boolean' },
    data_faithful: { enum: ['pass', 'fail'] }, note: { type: 'string' } } }

// ============================== ORCHESTRATION ==============================

phase('Propose')
const raw = await parallel(PROPOSERS.map(m => () =>
  agent(PROPOSE_PROMPT(false), { agentType: m.type, label: `propose:${m.id}`, schema: PROPOSAL_SCHEMA, ...(m.effort ? { effort: m.effort } : {}) })
    .then(r => ({ member: m.id, family: m.family, changes: (r && r.changes) || [] }))
    .catch(() => ({ member: m.id, family: m.family, changes: [] }))))
const proposals = []
for (const p of raw.filter(Boolean))
  for (const c of p.changes) proposals.push({ ...c, member: p.member, family: p.family })
log(`iter ${ITER} phase ${PHASE} scope=${SCOPE}: ${proposals.length} proposals from ${PANEL.length} seats`)

const byKey = {}
for (const c of proposals) {
  const k = `${c.locus}|${c.action}|${c.proposed}`
  if (!byKey[k]) byKey[k] = { locus: c.locus, type: c.type, action: c.action, current: c.current,
    proposed: c.proposed, rationale: c.rationale, support: 0, author_seats: new Set(), author_families: new Set() }
  byKey[k].support += 1
  byKey[k].author_seats.add(c.member)
  byKey[k].author_families.add(c.family)
}
const candidates = Object.values(byKey).map((c, i) =>
  ({ ...c, id: `C${i + 1}`, author_seats: [...c.author_seats], author_families: [...c.author_families] }))
log(`${candidates.length} candidates`)

phase('Faithfulness')
const faiths = await parallel(candidates.map(c => () =>
  agent(FAITH_PROMPT(c), { agentType: 'check-faithfulness', label: `faith:${c.id}`, schema: FAITH_SCHEMA })
    .catch(() => null)))
const withFaith = candidates.map((c, i) => {
  const f = faiths[i]
  const gate = !!f && f.locatable !== false && f.data_faithful === 'pass'
  return { ...c, faith: f, faith_gate: gate,
           faith_reason: !f ? 'faith_check_errored' : f.locatable === false ? 'not_locatable'
             : f.data_faithful !== 'pass' ? 'data_changed' : null }
})
const survivors = withFaith.filter(c => c.faith_gate)
log(`faithfulness: ${survivors.length}/${candidates.length} pass`)

phase('Vote')
// No self-exclusion: every seat votes on every surviving candidate.
const scored = await parallel(survivors.map(cand => async () => {
  const prompt = cand.type === 'structural' ? VOTE_STRUCTURAL(cand) : VOTE_PROSE(cand)
  const ballots = await parallel(PANEL.map(v => () =>
    agent(prompt, { agentType: v.type, label: `vote:${cand.id}:${v.id}`, schema: VOTE_SCHEMA, ...(v.effort ? { effort: v.effort } : {}) })
      .then(s => ({ voter: v.id, is_author: cand.author_seats.includes(v.id), ...s })).catch(() => null)))
  return { id: cand.id, votes: ballots.filter(Boolean) }
}))
const votesById = {}
for (const s of scored) votesById[s.id] = s.votes

phase('Synthesize')
const decide = (v) => {
  const voter_data_fail = v.some(x => x.data_faithful === 'fail')
  const deps = v.map(x => x.dependencies).filter(d => d && d.trim())
  const keeps = v.filter(x => x.keep).length
  const composite = v.length
    ? Math.round((v.reduce((s, x) => s + x.clarity + x.voice + x.concision + x.structural_soundness, 0) / v.length) * 100) / 100
    : 0
  return { accepted: !voter_data_fail && v.length > 0 && keeps > v.length / 2,
           keeps, n: v.length, voter_data_fail, dependencies: deps, composite }
}
const results = withFaith.map(c => {
  const votes = votesById[c.id] || []
  return { ...c, votes,
    verdict: c.faith_gate ? decide(votes)
      : { accepted: false, keeps: 0, n: 0, dropped: c.faith_reason, composite: 0 } }
}).sort((a, b) => String(a.locus).localeCompare(String(b.locus)))

// self-preference: does a seat treat its own (unlabelled) proposal more kindly?
const sp = {}
for (const r of results) for (const b of r.votes) {
  const k = b.voter; sp[k] = sp[k] || { self_n: 0, self_keep: 0, other_n: 0, other_keep: 0 }
  const s = sp[k]
  if (b.is_author) { s.self_n++; if (b.keep) s.self_keep++ } else { s.other_n++; if (b.keep) s.other_keep++ }
}
return {
  scope: SCOPE, phase: PHASE, iteration: ITER,
  n_proposals: proposals.length, n_candidates: candidates.length,
  n_faith_pass: survivors.length, n_faith_dropped: candidates.length - survivors.length,
  accepted: results.filter(r => r.verdict.accepted).length,
  self_preference: sp,
  changes: results,
}
