export const meta = {
  name: 'onet-element-audit-4col',
  description: 'Blind derivation over four cells -- U, L, D, and undirected N -- no draft and no prior results shown',
  phases: [
    { title: 'Nominate', detail: 'three independent coders per subset, four cells', model: 'fable' },
  ],
}

// WHY THIS RUN EXISTS
//
// The two-arm audit rejected elements for LACKING DIRECTION -- Letters and
// Memos took zero votes in either arm largely because memos go to clients and
// subordinates as readily as to superiors. Matthew's reading: that exposes a
// hole in the cell structure, not only in the elements. The study cares about
// undirected account-giving and sociality too; with no undirected home, the
// earlier runs could only force such elements into a directional cell or drop
// them, so the directional cells collected faute-de-mieux members and honest
// undirected elements were lost entirely.
//
// This run adds a fourth cell, N (undirected), and re-derives from scratch.
// Coders see no draft and none of the earlier runs' results, so nothing about
// the previous U/L/D assignments can anchor which elements now migrate to N.
// The thing to watch on readout: which elements that previously claimed a
// direction stop claiming one when an undirected home exists.
//
// Same universe (295 elements), same six subsets, same three-coders-per-slice
// and 2-of-3 threshold, same fable/medium coders as both earlier arms.
const ARGS = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const DIR = ARGS.dir
const K = ARGS.k || 6

const STUDY = [
'THE STUDY, in plain terms.',
'',
'Legislative speech carries a measurable "register" -- a machine-like, procedural,',
'bureaucratic way of writing. Some legislators use much more of it than others. We',
'want to know what it is about a person\'s PRIOR OCCUPATION, before they entered',
'politics, that predicts how much of this register they use.',
'',
'The hypothesis is that the register belongs to the occupation that RENDERS',
'ACCOUNT TO SOMEONE ABOVE IT. Not that it is a high-status job, not that it is a',
'wordy job -- that the job consists of justifying your judgment, in prose, to a',
'person who can overrule you, and that you do not hold the final say.',
'',
'That construct is resolved by DIRECTION of interaction into four components:',
'',
'  U  UPWARD     -- reporting, documenting and justifying to a superior; and,',
'                   as the other face of the same thing, NOT having discretion.',
'                   Autonomy elements belong here REVERSE-SCORED: having freedom',
'                   to decide is the opposite of answering for your decisions.',
'  L  LATERAL    -- dealing with people who are neither your superiors nor your',
'                   subordinates: the public, clients, outside organisations,',
'                   peers. Serving sideways.',
'  D  DOWNWARD   -- directing, supervising, staffing, instructing and controlling',
'                   other people and resources. Commanding.',
'  N  UNDIRECTED -- squarely about account-giving (documentation, record-keeping,',
'                   procedure, written justification) or about sociality (working',
'                   with and around people), but silent on which way the',
'                   interaction points. A job can be built around rendering',
'                   account without the descriptor recording to whom.',
'',
'The prediction is that U and L go with MORE register and D with LESS: the heavy',
'register user reports upward, serves sideways, and commands nobody. No sign is',
'declared for N here; it exists so the construct is not narrowed to the elements',
'that happen to name a counterpart.',
'',
'The occupations are those of legislators in Australian, British, Canadian and',
'Irish chambers -- lawyers, teachers, farmers, journalists, nurses, trade',
'unionists, business owners, civil servants, soldiers, police, manual trades.',
].join('\n')

const RULES = [
'RULES',
'',
'1. MOST ELEMENTS BELONG NOWHERE. You are being shown a slice of the whole O*NET',
'   content model -- abilities, knowledge areas, physical working conditions,',
'   interests. The great majority fit none of the four cells. Returning "none"',
'   for every element in your slice is a correct answer if that is what you find.',
'   Do not fill quotas.',
'2. DIRECTION PICKS THE COLUMN; THE CONSTRUCT PICKS WHETHER IT BELONGS AT ALL.',
'   If an element tells you which way the interaction points, it goes in U, L',
'   or D. If it is squarely about account-giving or sociality but names no',
'   counterpart -- documentation, correspondence, procedure, general people-work',
'   -- it goes in N. If it serves neither base measure, it belongs in no cell.',
'3. N IS NOT "EVERYTHING ELSE". An element earns N only by measuring account-',
'   giving or sociality as squarely as a directional element would, just without',
'   a named counterpart. If you cannot say which base measure it serves, it',
'   belongs nowhere. Every N nomination must say which measure in "measure".',
'4. REQUIREMENT, NOT APTITUDE. Prefer elements describing what the job INVOLVES',
'   (activities, context) over what a worker must BE GOOD AT (abilities) or KNOW.',
'   "Oral Comprehension" is a capacity; "Repairing and Maintaining Equipment" is',
'   a task. (Neither belongs in a cell -- they illustrate the distinction only.)',
'   Nominate an ability or knowledge element only if you can say why the capacity',
'   is a direct indicator of the activity, and say so in the rationale.',
'5. REVERSE SCORING IS AVAILABLE. If an element measures the OPPOSITE of a cell\'s',
'   construct -- autonomy against upward accountability, say -- nominate it for',
'   that cell with reverse: true.',
'6. INTEREST RATINGS ARE WEAKER EVIDENCE than activity or context ratings, because',
'   they describe what incumbents are drawn to rather than what the work demands.',
'   Not disqualifying, but reflect it in confidence.',
'7. THERE IS NO DRAFT TO MATCH. No existing version of these cells, and no result',
'   from any earlier coding pass, is being shown to you, on purpose. Build each',
'   cell from the construct as described, and expect that most elements in your',
'   slice belong in none of them.',
].join('\n')

const SCHEMA = {
  type: 'object', required: ['nominations'],
  properties: {
    notes: { type: 'string' },
    nominations: { type: 'array', items: {
      type: 'object', required: ['id', 'cell'],
      properties: {
        id: { type: 'string', description: 'element ID verbatim from the subset file' },
        cell: { type: 'string', description: 'U | L | D | N' },
        measure: { type: 'string', description: 'M1 (account-giving) | M2 (sociality) | both -- REQUIRED when cell is N, optional otherwise' },
        reverse: { type: 'boolean', description: 'true if it measures the opposite' },
        confidence: { type: 'string', description: 'high | medium | low' },
        rationale: { type: 'string', description: 'one clause: which cell, and why' },
      } } },
  },
}

phase('Nominate')
const jobs = []
for (let s = 0; s < K; s++) for (let c = 0; c < 3; c++) jobs.push({ s, c })
const votes = (await parallel(jobs.map(j => () =>
  agent([
'Decide which O*NET elements measure directed or undirected accountability and',
'sociality, for study S10.',
'',
'Read ' + DIR + '/subset_' + j.s + '.json -- an array of {id, name, desc, file, n_occ}.',
'Consider EXACTLY the elements in that file and no others.',
'',
'You are one of three independent coders on this slice. The others are not shown',
'your answers and you are not shown theirs; an element is kept only if at least',
'two of the three nominate it for the same cell. So code what you actually think,',
'and do not try to guess what the others will say.',
'',
STUDY, '', RULES,
'',
'Return a nomination for each element you place and omit the rest. Write nothing',
'outside your structured return.',
  ].join('\n'), { label: 'four:s' + j.s + 'c' + j.c, phase: 'Nominate',
                  schema: SCHEMA, model: 'fable', effort: 'medium' })
))).map((v, i) => ({ ...jobs[i], v }))

// deterministic 2-of-3 tally in script, as in both earlier arms
const tally = {}
let nomTotal = 0
for (const { s, v } of votes) {
  if (!v) continue
  for (const n of (v.nominations || [])) {
    if (!n || !n.id || !n.cell) continue
    nomTotal++
    const key = n.id + '|' + String(n.cell).trim().toUpperCase()
    ;(tally[key] = tally[key] || { id: n.id, cell: String(n.cell).trim().toUpperCase(),
                                   subset: s, n: 0, reverse: 0, measures: [], why: [] })
    tally[key].n++
    if (n.reverse) tally[key].reverse++
    if (n.measure) tally[key].measures.push(String(n.measure))
    if (n.rationale) tally[key].why.push(n.rationale)
  }
}
const consensus = Object.values(tally).filter(x => x.n >= 2)
                        .sort((a, b) => b.n - a.n || a.id.localeCompare(b.id))
const singleton = Object.values(tally).filter(x => x.n === 1)
log(nomTotal + ' nominations; ' + consensus.length + ' pairs at 2-of-3 (' +
    consensus.filter(x => x.cell === 'N').length + ' in N); ' +
    singleton.length + ' singletons')

return { nominations: nomTotal, consensus: consensus.length,
         singletons: singleton.length, consensus_pairs: consensus,
         singleton_pairs: singleton.map(x => ({ id: x.id, cell: x.cell })) }
