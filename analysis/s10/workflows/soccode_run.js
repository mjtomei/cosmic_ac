export const meta = {
  name: 'soc-coding',
  description: 'Map cleaned occupation titles to O*NET-SOC codes by double-blind coding with adjudication',
  phases: [
    { title: 'Code', detail: 'first independent pass' },
    { title: 'Recode', detail: 'second blind pass, same occupations, different agents' },
    { title: 'Adjudicate', detail: 'resolve only where the two passes disagree' },
    { title: 'Write', detail: 'record the mapping to disk' },
  ],
}

// WHY THIS RUN EXISTS
//
// PREREG-occupational-accountability.md tests whether an O*NET composite for
// subordinate account-giving predicts the register better than EGP class does.
// O*NET publishes ratings per O*NET-SOC code, so every legislator's prior
// occupation needs one. That mapping is this workflow's only job: once a
// occupation has a SOC code, all ~271 rated elements join for free.
//
// Chunks are CONTIGUOUS over a pool sorted by member count, not strided, so a
// run that stops early leaves the highest-coverage occupations finished rather
// than gaps spread across the frequency range.
//
// args: { batches: 30, pool: 'soc_strings_pool.json', from: 0 }
const ARGS = {"batches": 30, "pool": "soc_strings_pool.json", "n": 4402}   // baked in at launch
const N_BATCH = ARGS.batches
if (!N_BATCH) throw new Error('args.batches required — got: ' + JSON.stringify(args).slice(0, 120))
const POOL = ARGS.pool || 'soc_strings_pool.json'
const FROM = ARGS.from || 0

const RUBRIC = [
'THE TARGET: an O*NET-SOC 2019 occupation code, the 8-digit form like "25-2031.00" (Secondary School Teachers) or "23-1011.00" (Lawyers).',
'',
'You may look occupations up at onetonline.org — its search takes a job title and returns candidate SOC codes with definitions. Read the definition before accepting a code; titles collide across very different occupations.',
'',
'RULES',
'',
'1. CODE THE OCCUPATION, NOT THE SENIORITY. "senior partner in a law firm" and "lawyer" are both 23-1011.00. O*NET has separate codes for managers where management IS the occupation (11-xxxx), so use those only when the person managed as their job rather than practised as a senior person.',
'2. THE MODAL MEMBER OF THE CATEGORY. "farmer" is 11-9013.00 (Farmers, Ranchers, and Other Agricultural Managers) — an operator of a holding — not a farm labourer (45-2092.00), unless the string says labourer or hand.',
'3. NATIONAL VARIANTS MAP TO THE US CODE. "barrister" and "solicitor" are both 23-1011.00 Lawyers. "chartered accountant" is 13-2011.00 Accountants and Auditors. "grazier" is 11-9013.00. The corpus is Australian, Canadian, Irish and British; O*NET is US-coded, and that mapping is the point of this pass.',
'4. FIRST-LISTED CAREER when several are given. "teacher; later school principal" codes as the teacher unless the string makes clear the later role dominated the career.',
'5. UNKNOWN IS A CORRECT ANSWER. If the string names no determinate occupation ("community advocate", "businessman" with no sector), return soc_code "unknown" with a rationale saying what was missing. A plausible-looking wrong code cannot be detected downstream and does more damage than an honest unknown.',
'6. DO NOT INVENT CODES. Every code you return must exist in the O*NET-SOC taxonomy. If you cannot verify a code, return unknown.',
'',
'An EGP class code is supplied for context because it was assigned by an earlier double-blind pass on the same string. Treat it as a hint about seniority and employment relation, never as a constraint — it is a seven-category schema and O*NET has ~900 occupations.',
].join('\n')

const CODE_SCHEMA = {
  type: 'object',
  required: ['chunk', 'n_items', 'codings'],
  properties: {
    chunk: { type: 'integer' }, n_items: { type: 'integer' }, notes: { type: 'string' },
    codings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'soc_code'],
        properties: {
          id: { type: 'integer', description: 'pool id, verbatim' },
          soc_code: { type: 'string', description: '8-digit O*NET-SOC code, or "unknown"' },
          soc_title: { type: 'string', description: 'the official title for that code' },
          confidence: { type: 'string', description: 'high | medium | low' },
          rationale: { type: 'string', description: 'one clause: which rule decided it' },
        },
      },
    },
  },
}

function batchPrompt(i, pass) {
  const size = Math.ceil((ARGS.n || 4402) / N_BATCH)
  const lo = FROM + i * size, hi = FROM + (i + 1) * size - 1
  return [
'Map cleaned occupation titles to O*NET-SOC codes, for study S10.',
'',
'Read ' + POOL + ' in /home/mjtomei/s10_soc — an array of {id, occupation, n_members, egp_existing, chambers}, sorted by how many legislators held that occupation. Take entries at zero-based indices ' + lo + ' through ' + hi + ' inclusive (the last chunk may run past the end; do the entries that exist). Code ALL of them.',
'',
'Return the pool "id" VERBATIM for every entry. It is the join key; an altered id makes the record unusable.',
'',
pass === 2
  ? 'You are the SECOND of two independent coders. The first pass has already coded these and you are deliberately NOT shown its answers, so that agreement measures how determinate the occupations are. Code from the rubric alone.'
  : 'You are the FIRST of two independent coders. A second agent will code the same entries blind, and disagreements go to adjudication. Code what the rubric says; do not try to guess the other coder.',
'',
RUBRIC,
'',
'Return a coding for every id in your slice, including the ones you mark unknown — coverage data is data. Write nothing outside your structured return.',
  ].join('\n')
}

phase('Code')
const pass1 = await parallel(Array.from({ length: N_BATCH }, (_, i) => () =>
  agent(batchPrompt(i, 1), { label: 'soc:b' + i, phase: 'Code',
                             schema: CODE_SCHEMA, effort: 'medium' })))
phase('Recode')
const pass2 = await parallel(Array.from({ length: N_BATCH }, (_, i) => () =>
  agent(batchPrompt(i, 2), { label: 'resoc:b' + i, phase: 'Recode',
                             schema: CODE_SCHEMA, effort: 'medium' })))

const m1 = {}, m2 = {}
for (const r of pass1.filter(Boolean)) for (const c of (r.codings || [])) m1[c.id] = c
for (const r of pass2.filter(Boolean)) for (const c of (r.codings || [])) m2[c.id] = c
const ids = Object.keys(m1).filter(k => k in m2)
const agree = ids.filter(k => (m1[k].soc_code || '') === (m2[k].soc_code || ''))
const disagree = ids.filter(k => (m1[k].soc_code || '') !== (m2[k].soc_code || ''))
log(ids.length + ' double-coded; ' + agree.length + ' agree (' +
    (100 * agree.length / (ids.length || 1)).toFixed(1) + '%), ' + disagree.length + ' to adjudicate')

const ADJ_SCHEMA = { type: 'object', required: ['rulings'], properties: { rulings: { type: 'array', items: {
  type: 'object', required: ['id', 'soc_code'], properties: {
    id: { type: 'integer' }, soc_code: { type: 'string' }, soc_title: { type: 'string' },
    rationale: { type: 'string' },
    note: { type: 'string', description: 'flag rubric ambiguity if the RUBRIC, not the title, caused the split' } } } } } }

phase('Adjudicate')
const CHUNK = 40
const groups = []
for (let i = 0; i < disagree.length; i += CHUNK) groups.push(disagree.slice(i, i + CHUNK))
const rulings = groups.length ? (await parallel(groups.map((g, gi) => () =>
  agent([
'Adjudicate O*NET-SOC codings where two independent coders disagreed, for study S10.',
'Read ' + POOL + ' for each id\'s occupation text. For each case below decide the correct code, or "unknown" if neither is right and none is determinate.',
'You may verify codes at onetonline.org. Do not invent codes.',
'',
RUBRIC,
'',
'CASES:',
...g.map(id => '  id ' + id + ': coder A said ' + (m1[id].soc_code || '?') + ' (' + (m1[id].soc_title || '') + '), coder B said ' + (m2[id].soc_code || '?') + ' (' + (m2[id].soc_title || '') + ')'),
  ].join('\n'), { label: 'adj:g' + gi, phase: 'Adjudicate',
                  schema: ADJ_SCHEMA, effort: 'high' })))).filter(Boolean) : []

const ruled = {}
for (const r of rulings) for (const x of (r.rulings || [])) ruled[x.id] = x
const final = ids.map(id => {
  const a = m1[id], b = m2[id], r = ruled[id]
  const ok = (a.soc_code || '') === (b.soc_code || '')
  return { id: Number(id), soc_code: ok ? a.soc_code : (r ? r.soc_code : null),
           soc_title: ok ? (a.soc_title || b.soc_title) : (r ? r.soc_title : null),
           resolution: ok ? 'agreed' : (r ? 'adjudicated' : 'unresolved'),
           coder_a: a.soc_code || null, coder_b: b.soc_code || null,
           confidence: ok ? (a.confidence || b.confidence) : 'adjudicated',
           rationale: ok ? (a.rationale || b.rationale) : (r ? r.rationale : null),
           rubric_note: r ? (r.note || '') : '' }
})

phase('Write')
const writer = await agent([
'Write ./soc_coding_new.json in /home/mjtomei/s10_soc: the JSON array below, each record joined to its pool entry from ' + POOL + ' (match on id; add occupation, n_members, egp_existing, chambers). Then report as text: total coded, raw agreement rate, count unknown, the ten most common SOC codes by member count, and any rubric_note contents. Do not alter any field.',
'', 'RECORDS:', JSON.stringify(final),
].join('\n'), { label: 'write', phase: 'Write', effort: 'medium' })

const socs = {}
for (const f of final) socs[f.soc_code || 'null'] = (socs[f.soc_code || 'null'] || 0) + 1
return { n: final.length, agreement: agree.length / (ids.length || 1),
         adjudicated: disagree.length, distinct_soc: Object.keys(socs).length, writer }
