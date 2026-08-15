export const meta = {
  name: 'occupation-class-coding',
  description: 'Code occupation strings to EGP class by double-blind Claude coding with adjudication',
  phases: [
    { title: 'Code', detail: 'first independent coding pass' },
    { title: 'Recode', detail: 'second blind pass, same strings, different agents' },
    { title: 'Adjudicate', detail: 'resolve only where the two passes disagree' },
    { title: 'Write', detail: 'record the coding to disk' },
  ],
}

const ARGS = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const N_BATCH = ARGS.batches
if (!N_BATCH) throw new Error('args.batches required — got: ' + JSON.stringify(args).slice(0, 120))
const POOL = ARGS.pool || 'occupation_strings_new.json'

// Given VERBATIM to both passes: different instructions would make
// disagreement measure the prompt rather than the string.
const RUBRIC = [
'THE SCHEMA: EGP (Erikson, Goldthorpe & Portocarero 1979), seven-class collapse.',
'',
'EGP is built on EMPLOYMENT RELATIONS, not prestige or income. The primary cuts are between employers, the self-employed and employees; and among employees, between a service relationship (salaried, career ladder, autonomy) and a labour contract (paid for effort, supervised).',
'',
'  I     higher service: credentialled professionals (physician, lawyer, engineer,',
'        professor, accountant), higher administrators, managers of large',
'        organisations, large proprietors',
'  II    lower service: semi-professionals (teacher, nurse, social worker, clergy,',
'        journalist), lower administrators, managers without evidence of scale,',
'        technicians with supervisory duty',
'  III   routine non-manual: clerical, secretarial, sales assistant, service',
'  IVab  petty bourgeoisie: small proprietors and own-account workers, with or',
'        without employees — shopkeepers, commission agents, brokers, realtors,',
'        franchisees, self-employed tradespeople running their own business',
'  IVc   farmers and smallholders who OWN or OPERATE the holding',
'  V/VI  technicians and skilled manual: apprenticed trades (electrician,',
'        carpenter, machinist, millwright), foremen and supervisors of manual work,',
'        engine drivers, police and fire other-ranks',
'  VIIab semi- and unskilled manual, AND agricultural labourers — labourer, miner,',
'        driver, cleaner, factory and mill work, farm hand',
'',
'RULES THAT DECIDE THE HARD CASES',
'',
'1. SCALE, NOT TITLE, separates I from II. "Director" spans I to III in these',
'   records — a communications director is II, a managing director of a firm is I,',
'   a director of a two-person non-profit is II. Code the organisation implied,',
'   not the word. The worked rule: head of an actual firm is I unless the',
'   organisation is evidently tiny; functional directors and unspecified managers',
'   are II.',
'',
'2. OWNERSHIP MOVES PEOPLE TO IV, not up the service classes. Someone who "owned',
'   and operated a trucking company" is IVab, not I, unless the firm is clearly',
'   large. Anyone practising a profession or semi-profession on their own account',
'   (a solo lawyer, a family doctor in private practice) codes on the profession,',
'   not the proprietorship.',
'',
'3. FARMING SPLITS ON ROLE. An owner or operator is IVc; a farm hand or',
'   agricultural labourer is VIIab. Where a string says only "farmer" with no',
'   role marker, code IVc — proprietorship is the modal case in these records —',
'   and set confidence to "medium".',
'',
'4. "ENGINEER" IS AMBIGUOUS in North American records: it names both a chartered',
'   professional (I) and a locomotive or operating engineer (V/VI). Use the',
'   context. If there is none, code unknown rather than guessing.',
'',
'5. COMPOUND STRINGS ARE THE NORM — many list several occupations. Code the',
'   FIRST-LISTED substantive occupation: sources order these by principal or most',
'   recent role, and taking the highest position anyone ever held systematically',
'   inflates the distribution. Rule 5 selects BETWEEN listed occupations, never',
'   between grades within one career ("police officer, rising to Superintendent"',
'   codes as the career, at its stated level, not its entry grade). Record the',
'   other occupations in other_occupations.',
'',
'6. AN ELECTED OR PARTY ROLE IS NOT A CLASS ORIGIN. Councillor, trustee, mayor,',
'   legislator, ministerial staffer, caucus staff — if the political roles',
'   exhaust the string, set egp to "none-political". If a political item is',
'   first-listed but a substantive occupation follows, code the occupation.',
'',
'7. UNKNOWN IS A CORRECT ANSWER. "Senior positions in the oil and gas industry"',
'   does not say whether the person was a rig hand or a vice-president. Code',
'   unknown rather than guessing. A wrong code is worse than a missing one,',
'   because it enters the analysis silently.',
'',
'8. CROSSWALK-COMPATIBLE: where this rubric is silent, follow the standard',
'   ISCO-to-EGP mappings. Concretely: business, finance and computing',
'   professionals are I; registered paramedics and certified health technologists',
'   are II (health associate professionals); a bare "consultant" with a named',
'   professional field codes on the field, without one it is unknown.',
'',
'CONFIDENCE. high = the string names an occupation the schema covers directly.',
'medium = a defensible reading requiring an assumption you can state.',
'low = you are close to guessing; consider unknown instead.',
].join('\n')

const CODE_SCHEMA = {
  type: 'object',
  required: ['batch', 'codings'],
  properties: {
    batch: { type: 'integer' },
    codings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'egp', 'confidence'],
        properties: {
          id: { type: 'string' },
          egp: { type: 'string',
            description: 'I | II | III | IVab | IVc | V/VI | VIIab | unknown | none-political' },
          confidence: { type: 'string', description: 'high | medium | low' },
          rationale: { type: 'string', description: 'one clause: which rule decided it' },
          coded_occupation: { type: 'string' },
          other_occupations: { type: 'array', items: { type: 'string' } },
        },
      },
    },
  },
}

function batchPrompt(i, pass) {
  return [
'Code occupation strings into EGP social classes, for study S10.',
'',
'Read ' + POOL + ' in the current directory — distinct occupation descriptions of legislators (and their parents) across thirteen chambers, each entry {id, string, n_members, whose, chambers}. Take every entry whose zero-based index satisfies index % ' + N_BATCH + ' == ' + i + '. Code ALL of them, one coding per id.',
'',
'This is a measurement instrument, not a summary. The codes feed a regression, so a plausible-looking wrong code does more damage than an honest "unknown" — it cannot be detected downstream. Whether a string describes a member or a parent makes no difference to the coding.',
'',
pass === 2
  ? 'You are the SECOND of two independent coders. The first pass has already coded these strings and you are deliberately NOT shown its answers, so that agreement measures how determinate the strings are. Code from the rubric alone.'
  : 'You are the FIRST of two independent coders. A second agent will code the same strings blind, and disagreements go to adjudication. Do not try to guess what the other coder will say — code what the rubric says.',
'',
RUBRIC,
'',
'Return a coding for every id in your batch. Do not skip a hard string; code it unknown with a rationale saying what was missing.',
  ].join('\n')
}

phase('Code')
const pass1 = await parallel(
  Array.from({ length: N_BATCH }, (_, i) => () =>
    agent(batchPrompt(i, 1), { label: 'code:b' + i, phase: 'Code',
                               schema: CODE_SCHEMA, effort: 'medium' })))

phase('Recode')
const pass2 = await parallel(
  Array.from({ length: N_BATCH }, (_, i) => () =>
    agent(batchPrompt(i, 2), { label: 'recode:b' + i, phase: 'Recode',
                               schema: CODE_SCHEMA, effort: 'medium' })))

const m1 = {}, m2 = {}
for (const r of pass1.filter(Boolean)) for (const c of (r.codings || [])) m1[c.id] = c
for (const r of pass2.filter(Boolean)) for (const c of (r.codings || [])) m2[c.id] = c
const ids = [...new Set([...Object.keys(m1), ...Object.keys(m2)])].sort()
const agree = [], disagree = []
for (const id of ids) {
  const a = m1[id], b = m2[id]
  if (a && b && a.egp === b.egp) agree.push(id)
  else disagree.push(id)
}
log('coded ' + ids.length + '; agreement ' +
    Math.round(100 * agree.length / (ids.length || 1)) + '%; ' +
    disagree.length + ' to adjudicate')

phase('Adjudicate')
const ADJ_SCHEMA = {
  type: 'object', required: ['rulings'],
  properties: { rulings: { type: 'array', items: {
    type: 'object', required: ['id', 'egp'],
    properties: { id: { type: 'string' }, egp: { type: 'string' },
      confidence: { type: 'string' }, rationale: { type: 'string' },
      note: { type: 'string', description: 'flag rubric ambiguity if the RUBRIC, not the string, caused the split' } } } } },
}
const CHUNK = 40
const groups = []
for (let i = 0; i < disagree.length; i += CHUNK) groups.push(disagree.slice(i, i + CHUNK))
const rulings = groups.length ? (await parallel(groups.map((g, gi) => () =>
  agent([
'Adjudicate disagreements between two independent EGP codings. Decide each from the rubric; where both readings are defensible and the string underdetermines the class, rule "unknown" — a coin-flip recorded as a class is invisible measurement error. If the RUBRIC caused the split, say so in note.',
'', RUBRIC, '',
'Look up full strings by id in ' + POOL + '. THE DISAGREEMENTS:', '',
g.map(id => {
  const a = m1[id] || {}, b = m2[id] || {}
  return 'id: ' + id +
         '\n  A: ' + (a.egp || 'MISSING') + ' (' + (a.confidence || '?') + ') — ' + (a.rationale || '') +
         '\n  B: ' + (b.egp || 'MISSING') + ' (' + (b.confidence || '?') + ') — ' + (b.rationale || '')
}).join('\n'),
  ].join('\n'), { label: 'adjudicate:' + gi, phase: 'Adjudicate',
                  schema: ADJ_SCHEMA, effort: 'high' })))).filter(Boolean) : []
const ruled = {}
for (const r of rulings) for (const x of (r.rulings || [])) ruled[x.id] = x

phase('Write')
const final = ids.map(id => {
  const a = m1[id] || {}, b = m2[id] || {}
  const agreed = a.egp && b.egp && a.egp === b.egp
  const r = ruled[id]
  return { id,
    egp: agreed ? a.egp : (r ? r.egp : null),
    confidence: agreed ? (a.confidence === b.confidence ? a.confidence : 'medium')
                       : (r ? r.confidence : null),
    resolution: agreed ? 'agreed' : (r ? 'adjudicated' : 'UNRESOLVED'),
    coder_a: a.egp || null, coder_b: b.egp || null,
    rationale: agreed ? (a.rationale || b.rationale) : (r ? r.rationale : null),
    coded_occupation: a.coded_occupation || b.coded_occupation || null,
    other_occupations: a.other_occupations || b.other_occupations || [],
    rubric_note: r ? (r.note || '') : '' }
})
const writer = await agent([
'Write the finished coding to ./occupation_coding_new.json in the current directory: the JSON array below, each record joined to its pool entry from ' + POOL + ' (match on id; add string, n_members, whose, chambers). Then report as text: total, raw agreement rate, EGP distribution, unknown vs none-political counts, and any rubric_note contents. Do not alter any field.',
'', 'RECORDS:', JSON.stringify(final),
  ].join('\n'), { label: 'write', phase: 'Write', effort: 'medium' })

const dist = {}
for (const f of final) dist[f.egp || 'null'] = (dist[f.egp || 'null'] || 0) + 1
return { n: final.length, agreement: agree.length / (ids.length || 1),
         adjudicated: disagree.length, distribution: dist, writer }
