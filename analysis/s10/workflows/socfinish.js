export const meta = {
  name: 'soc-coding-finish',
  description: 'Second votes for the 727 single-voted occupations, then Opus adjudication of every disagreement',
  phases: [
    { title: 'SecondVote', detail: 'blind second vote where only one exists' },
    { title: 'Adjudicate', detail: 'resolve every disagreement, high effort' },
    { title: 'Write', detail: 'record the finished mapping' },
  ],
}

// WHY THIS RUN EXISTS
//
// The SOC mapping ran on arch-home across two sessions and was stopped twice by
// the session limit. Salvaging both journals with votes kept SEPARATE (not
// collapsed) leaves 3,675 of 4,402 occupations double-coded at 91.9% raw
// agreement, 299 disagreements unadjudicated, and 727 occupations holding only
// one vote.
//
// Those votes came from Fable, because arch-home's session model is Fable and
// neither this workflow nor occcode.js specifies a model -- agent() inherits.
// The EGP coding they will sit beside in the same regression was done on Opus.
// Matthew's call: keep the Fable votes (91.9% is acceptable for what is largely
// a taxonomy lookup) and finish here on Opus at high effort, so the hard cases
// -- the second votes and every adjudication -- get the better model.
//
// No model is named below, deliberately: this runs in an Opus session and
// inherits it. Naming one would silently pin the workflow if it were reused.
const ARGS = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const NEED2 = ARGS.need_second || []      // pool ids holding one vote
const DISPUTED = ARGS.disputed || []      // [{id, a, b, a_title, b_title}]
const POOL = ARGS.pool || 'soc_strings_pool.json'
const PER = ARGS.per || 120

const RUBRIC = [
'THE TARGET: an O*NET-SOC 2019 occupation code, the 8-digit form like "25-2031.00" (Secondary School Teachers) or "23-1011.00" (Lawyers).',
'',
'You may look occupations up at onetonline.org — its search takes a job title and returns candidate SOC codes with definitions. Read the definition before accepting a code; titles collide across very different occupations.',
'',
'RULES',
'',
'1. CODE THE OCCUPATION, NOT THE SENIORITY. "senior partner in a law firm" and "lawyer" are both 23-1011.00. Use the 11-xxxx management codes only when managing WAS the occupation, not when someone was senior at practising something else.',
'2. THE MODAL MEMBER OF THE CATEGORY. "farmer" is 11-9013.00 (Farmers, Ranchers, and Other Agricultural Managers) — an operator of a holding — not a farm labourer (45-2092.00), unless the string says labourer or hand.',
'3. NATIONAL VARIANTS MAP TO THE US CODE. "barrister" and "solicitor" are both 23-1011.00. "chartered accountant" is 13-2011.00. "grazier" is 11-9013.00. The corpus is Australian, Canadian, Irish and British; O*NET is US-coded, and that mapping is the point of this pass.',
'4. FIRST-LISTED CAREER when several are given, unless the string makes clear a later role dominated.',
'5. UNKNOWN IS A CORRECT ANSWER. If the string names no determinate occupation ("community advocate", bare "businessman"), return "unknown" with a rationale saying what was missing. A plausible-looking wrong code cannot be detected downstream and does more damage than an honest unknown.',
'6. DO NOT INVENT CODES. Every code must exist in the O*NET-SOC taxonomy. If you cannot verify one, return unknown.',
].join('\n')

const CODE_SCHEMA = {
  type: 'object', required: ['codings'],
  properties: { notes: { type: 'string' }, codings: { type: 'array', items: {
    type: 'object', required: ['id', 'soc_code'],
    properties: {
      id: { type: 'integer', description: 'pool id, verbatim' },
      soc_code: { type: 'string' }, soc_title: { type: 'string' },
      confidence: { type: 'string', description: 'high | medium | low' },
      rationale: { type: 'string' } } } } },
}

const groups2 = []
for (let i = 0; i < NEED2.length; i += PER) groups2.push(NEED2.slice(i, i + PER))
log(NEED2.length + ' occupations need a second vote -> ' + groups2.length + ' agents')

phase('SecondVote')
const second = groups2.length ? (await parallel(groups2.map((g, gi) => () =>
  agent([
'Code occupation titles to O*NET-SOC codes, for study S10.',
'',
'Read ' + POOL + ' — an array of {id, occupation, n_members, egp_existing, chambers}. Code EXACTLY these pool ids:',
'  ' + g.join(', '),
'',
'You are an INDEPENDENT coder. Another agent has already coded these and you are deliberately not shown its answers, so that agreement measures how determinate the occupations are. Code from the rubric alone.',
'',
RUBRIC,
'',
'Return one coding per id, including any you mark unknown. Write nothing outside your structured return.',
  ].join('\n'), { label: 'vote2:g' + gi, phase: 'SecondVote',
                  schema: CODE_SCHEMA, effort: 'high' })))).filter(Boolean) : []

const newVotes = {}
for (const r of second) for (const c of (r.codings || [])) newVotes[c.id] = c

// anything whose second vote disagrees joins the disputed set
const disputed = DISPUTED.slice()
const firstOf = ARGS.first_vote || {}
let added = 0
for (const [id, c] of Object.entries(newVotes)) {
  const a = firstOf[id]
  if (a && a.soc_code !== c.soc_code) {
    disputed.push({ id: Number(id), a: a.soc_code, a_title: a.soc_title || '',
                    b: c.soc_code, b_title: c.soc_title || '' })
    added++
  }
}
log(added + ' new disagreements from the second votes; ' + disputed.length + ' to adjudicate in total')

const ADJ_SCHEMA = { type: 'object', required: ['rulings'], properties: { rulings: { type: 'array', items: {
  type: 'object', required: ['id', 'soc_code'], properties: {
    id: { type: 'integer' }, soc_code: { type: 'string' }, soc_title: { type: 'string' },
    rationale: { type: 'string' },
    note: { type: 'string', description: 'flag if the RUBRIC, not the title, caused the split' } } } } } }

phase('Adjudicate')
const AD = 35
const adGroups = []
for (let i = 0; i < disputed.length; i += AD) adGroups.push(disputed.slice(i, i + AD))
const rulings = adGroups.length ? (await parallel(adGroups.map((g, gi) => () =>
  agent([
'Adjudicate O*NET-SOC codings where two independent coders disagreed, for study S10.',
'Read ' + POOL + ' for each id\'s occupation text. Decide the correct code, or "unknown" if neither is right and none is determinate. You are not bound to either coder\'s answer.',
'Verify codes at onetonline.org. Do not invent codes.',
'',
RUBRIC,
'',
'CASES:',
...g.map(d => '  id ' + d.id + ': coder A ' + d.a + ' (' + (d.a_title || '') + ') vs coder B ' + d.b + ' (' + (d.b_title || '') + ')'),
  ].join('\n'), { label: 'adj:g' + gi, phase: 'Adjudicate',
                  schema: ADJ_SCHEMA, effort: 'high' })))).filter(Boolean) : []

const ruled = {}
for (const r of rulings) for (const x of (r.rulings || [])) ruled[x.id] = x
log(Object.keys(ruled).length + ' of ' + disputed.length + ' disagreements resolved')

phase('Write')
const writer = await agent([
'Assemble the finished SOC mapping for study S10 and write it to ./soc_coding_new.json.',
'',
'Inputs in this directory:',
'  soc_votes_salvaged.json  — {pool_id: [vote, ...]}, one or two votes each',
'  ' + POOL + '             — the pool entries',
'',
'ADDITIONAL SECOND VOTES (id -> coding), from this run:',
JSON.stringify(newVotes),
'',
'ADJUDICATIONS (id -> ruling), from this run:',
JSON.stringify(ruled),
'',
'For each pool id build one record: id, occupation, n_members, egp_existing, chambers, soc_code, soc_title, resolution ("agreed" when the two votes match, "adjudicated" when a ruling exists, "unresolved" otherwise), vote_a, vote_b, confidence, rationale. Use the adjudicated code wherever a ruling exists. Do not alter any field.',
'',
'Then report as text: total records, how many agreed vs adjudicated vs unresolved, the raw agreement rate, how many are "unknown", the ten most common SOC codes by member count, and any rubric notes.',
].join('\n'), { label: 'write', phase: 'Write', effort: 'high' })

return { second_votes: Object.keys(newVotes).length,
         adjudicated: Object.keys(ruled).length,
         disputed_total: disputed.length, writer }
