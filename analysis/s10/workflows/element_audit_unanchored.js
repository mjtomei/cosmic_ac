export const meta = {
  name: 'onet-element-audit-unanchored',
  description: 'Same audit, but coders never see the current cell contents -- the anchoring control',
  phases: [
    { title: 'Nominate', detail: 'three independent coders per subset, no draft shown', model: 'fable' },
  ],
}

// WHY THIS RUN EXISTS
//
// PREREG-occupational-accountability.md builds three directional components --
// U (upward), L (lateral), D (downward) -- from 19 named O*NET elements chosen
// by hand. Matthew's concern: those cells were assembled by one process that
// already got at least one call wrong (it left Management/Administration out of
// D until he put it in), so the contents are worth re-deriving independently.
//
// This does NOT look at the register outcome. It is instrument selection from
// element definitions alone, run before any element is joined to a member --
// which is what makes it legitimate to do at all at this stage.
//
// DESIGN. The 295 O*NET 30.3 elements carrying per-occupation ratings are split
// six ways, round-robin over a file-sorted list so each subset spans all eleven
// descriptor families and no coder sees only Abilities or only Work Context.
// Three independent coders per subset; an element is carried forward when at
// least two of its three nominate it for the same cell. Every element is seen
// by exactly three coders, so "at least twice" is 2-of-3 throughout.
//
// THIS IS THE UNANCHORED ARM (Matthew). The first run showed coders the current
// cell contents so they could challenge them; the cost is that agreement with
// the draft is then partly anchoring rather than independent re-derivation.
// Here they are never shown it. Same 295 elements, same six subsets, same
// construct description, same rules -- the only difference is that no draft
// exists in the prompt, and with nothing to challenge, the challenge task is
// dropped.
//
// Read the two together: elements the UNANCHORED arm re-derives are genuinely
// implied by the construct; elements only the ANCHORED arm keeps were plausibly
// just read off the draft. Elements the unanchored arm nominates that are in
// neither the draft nor the anchored result are the strongest candidates of
// all, since nothing pointed the coders at them.
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
'That construct is resolved by DIRECTION of interaction into three components:',
'',
'  U  UPWARD    -- reporting, documenting and justifying to a superior; and,',
'                  as the other face of the same thing, NOT having discretion.',
'                  Autonomy elements belong here REVERSE-SCORED: having freedom',
'                  to decide is the opposite of answering for your decisions.',
'  L  LATERAL   -- dealing with people who are neither your superiors nor your',
'                  subordinates: the public, clients, outside organisations,',
'                  peers. Serving sideways.',
'  D  DOWNWARD  -- directing, supervising, staffing, instructing and controlling',
'                  other people and resources. Commanding.',
'',
'The prediction is that U and L go with MORE register and D with LESS: the heavy',
'register user reports upward, serves sideways, and commands nobody.',
'',
'The occupations are those of legislators in Australian, British, Canadian and',
'Irish chambers -- lawyers, teachers, farmers, journalists, nurses, trade',
'unionists, business owners, civil servants, soldiers, police, manual trades.',
].join('\n')

// CURRENT deliberately absent: this arm shows no draft.

const RULES = [
'RULES',
'',
'1. MOST ELEMENTS BELONG NOWHERE. You are being shown a slice of the whole O*NET',
'   content model -- abilities, knowledge areas, physical working conditions,',
'   interests. The great majority have nothing to do with directed accountability.',
'   Returning "none" for every element in your slice is a correct answer if that',
'   is what you find. Do not fill quotas.',
'2. DIRECTION IS THE TEST, NOT TOPIC. "Public Speaking" is talking, but to whom?',
'   An element earns a cell only if it tells you WHICH WAY the interaction points.',
'   An element about communication in general, with no direction, belongs nowhere.',
'3. REQUIREMENT, NOT APTITUDE. Prefer elements describing what the job INVOLVES',
'   (activities, context) over what a worker must BE GOOD AT (abilities) or KNOW.',
'   "Oral Comprehension" is a capacity; "Repairing and Maintaining Equipment" is',
'   a task. (Neither belongs in a cell -- they illustrate the distinction only.)',
'   Nominate an ability or knowledge element only if you can say why the capacity',
'   is a direct indicator of the directed activity, and say so in the rationale.',
'4. REVERSE SCORING IS AVAILABLE. If an element measures the OPPOSITE of a cell\'s',
'   construct -- autonomy against upward accountability, say -- nominate it for',
'   that cell with reverse: true.',
'5. INTEREST RATINGS ARE WEAKER EVIDENCE than activity or context ratings, because',
'   they describe what incumbents are drawn to rather than what the work demands.',
'   Not disqualifying, but reflect it in confidence.',
'6. THERE IS NO DRAFT TO MATCH. No existing version of these cells is being shown',
'   to you, on purpose. Build each cell from the construct as described, and',
'   expect that most elements in your slice belong in none of them.',
].join('\n')

const SCHEMA = {
  type: 'object', required: ['nominations'],
  properties: {
    notes: { type: 'string' },
    nominations: { type: 'array', items: {
      type: 'object', required: ['id', 'cell'],
      properties: {
        id: { type: 'string', description: 'element ID verbatim from the subset file' },
        cell: { type: 'string', description: 'U | L | D' },
        reverse: { type: 'boolean', description: 'true if it measures the opposite' },
        confidence: { type: 'string', description: 'high | medium | low' },
        rationale: { type: 'string', description: 'one clause: which direction, and why' },
      } } },
    challenges: { type: 'array', items: {
      type: 'object', required: ['id', 'issue'],
      properties: {
        id: { type: 'string' },
        issue: { type: 'string', description: 'what is wrong with its current placement' },
        suggest: { type: 'string', description: 'move to U/L/D, drop, or reverse' },
      } } },
  },
}

phase('Nominate')
const jobs = []
for (let s = 0; s < K; s++) {
  for (let c = 0; c < 3; c++) {
    jobs.push({ s, c })
  }
}
const votes = (await parallel(jobs.map(j => () =>
  agent([
'Decide which O*NET elements measure directed accountability, for study S10.',
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
'Return a nomination for each element you place and omit the rest. Leave',
'"challenges" empty -- there is nothing to challenge in this arm. Write nothing',
'outside your structured return.',
  ].join('\n'), { label: 'blind:s' + j.s + 'c' + j.c, phase: 'Nominate',
                  schema: SCHEMA, model: 'fable', effort: 'medium' })
))).map((v, i) => ({ ...jobs[i], v }))

// ---- deterministic 2-of-3 tally, in script rather than by an agent ----
const tally = {}, challenges = {}
let nomTotal = 0
for (const { s, v } of votes) {
  if (!v) continue
  for (const n of (v.nominations || [])) {
    if (!n || !n.id || !n.cell) continue
    nomTotal++
    const key = n.id + '|' + String(n.cell).trim().toUpperCase()
    ;(tally[key] = tally[key] || { id: n.id, cell: String(n.cell).trim().toUpperCase(),
                                   subset: s, n: 0, reverse: 0, why: [] })
    tally[key].n++
    if (n.reverse) tally[key].reverse++
    if (n.rationale) tally[key].why.push(n.rationale)
  }
  for (const c of (v.challenges || [])) {
    if (!c || !c.id) continue
    ;(challenges[c.id] = challenges[c.id] || { id: c.id, n: 0, issues: [] })
    challenges[c.id].n++
    challenges[c.id].issues.push((c.suggest ? c.suggest + ': ' : '') + c.issue)
  }
}
const consensus = Object.values(tally).filter(x => x.n >= 2)
                        .sort((a, b) => b.n - a.n || a.id.localeCompare(b.id))
const singleton = Object.values(tally).filter(x => x.n === 1)
const chal2 = Object.values(challenges).filter(x => x.n >= 2)
log(nomTotal + ' nominations cast; ' + consensus.length + ' element-cell pairs reached 2-of-3, ' +
    singleton.length + ' were singletons; ' + chal2.length + ' challenges seconded')

// No report agent in this arm. The interesting comparison is three-way --
// hand-built against anchored against unanchored -- and is done once both runs
// are in, rather than by two agents each seeing half the picture.
return { nominations: nomTotal, consensus: consensus.length, singletons: singleton.length,
         consensus_pairs: consensus,
         singleton_pairs: singleton.map(x => ({ id: x.id, cell: x.cell })) }
