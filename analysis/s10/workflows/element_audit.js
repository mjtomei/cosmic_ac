export const meta = {
  name: 'onet-element-audit',
  description: 'Blind re-derivation of the U/L/D element assignments from the full O*NET element list',
  phases: [
    { title: 'Nominate', detail: 'three independent coders per element subset', model: 'fable' },
    { title: 'Report', detail: 'compare the 2-of-3 consensus against the current instrument' },
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
// Coders see the current cell contents, because half the job is flagging what
// is already in a cell and should not be. That does risk anchoring toward the
// status quo, so the prompt says plainly that the current contents are one
// person's draft and that agreeing with them is not the goal.
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

const CURRENT = [
'THE CURRENT CONTENTS OF EACH CELL. One person assembled these by hand. Treat',
'them as a draft to be checked, NOT as an answer key -- reproducing them is not',
'the goal, and an empty return is a perfectly good result.',
'',
'U (upward), 6 elements:',
'  4.C.1.a.2.j  Letters and Memos              4.A.3.b.6   Documenting/Recording Information',
'  4.A.4.a.2    Communicating with Supervisors 4.A.4.c.1   Performing Administrative Activities',
'  4.C.3.a.4    Freedom to Make Decisions      REVERSE-SCORED',
'  4.C.3.b.8    Determine Tasks/Priorities     REVERSE-SCORED',
'',
'L (lateral), 5 elements:',
'  4.A.4.a.3    Communicating with People Outside the Organization',
'  4.A.4.a.4    Establishing and Maintaining Interpersonal Relationships',
'  4.A.4.a.5    Assisting and Caring for Others',
'  4.A.4.a.8    Performing for or Working Directly with the Public',
'  1.B.1.d      Social interest MINUS 1.B.1.a Realistic interest',
'',
'D (downward), 7 elements:',
'  4.A.4.b.1    Coordinating the Work and Activities of Others',
'  4.A.4.c.2    Staffing Organizational Units  4.A.4.c.3  Monitoring and Controlling Resources',
'  4.A.4.b.3    Training and Teaching Others   4.A.4.b.4  Guiding, Directing and Motivating Subordinates',
'  4.A.4.b.5    Coaching and Developing Others 1.B.3.al   Management/Administration interest',
].join('\n')

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
'   "Oral Comprehension" is a capacity; "Communicating with Supervisors" is a task.',
'   Nominate an ability or knowledge element only if you can say why the capacity',
'   is a direct indicator of the directed activity, and say so in the rationale.',
'4. REVERSE SCORING IS AVAILABLE. If an element measures the OPPOSITE of a cell\'s',
'   construct -- autonomy against upward accountability, say -- nominate it for',
'   that cell with reverse: true.',
'5. INTEREST RATINGS ARE WEAKER EVIDENCE than activity or context ratings, because',
'   they describe what incumbents are drawn to rather than what the work demands.',
'   Not disqualifying; the current L and D each contain one. Flag it in confidence.',
'6. YOU MAY CHALLENGE THE CURRENT CONTENTS. If an element listed above looks',
'   wrongly placed, or wrongly reverse-scored, or too weak to be there, say so in',
'   "challenges". You are not being asked to defend the draft.',
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
STUDY, '', CURRENT, '', RULES,
'',
'Return a nomination for each element you place, omitting the rest, plus any',
'challenges to the current contents. Write nothing outside your structured return.',
  ].join('\n'), { label: 'nom:s' + j.s + 'c' + j.c, phase: 'Nominate',
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

phase('Report')
const report = await agent([
'Compare a blind re-derivation of an instrument against the version built by hand,',
'for study S10. Write the comparison to ' + DIR + '/../element_audit_report.md.',
'',
'THE HAND-BUILT INSTRUMENT (19 elements):', '', CURRENT,
'',
'THE BLIND RESULT. Three independent coders saw each element; these reached 2-of-3',
'for a cell. "reverse" counts how many of the agreeing coders wanted it reverse-scored.',
JSON.stringify(consensus.map(c => ({ id: c.id, cell: c.cell, votes: c.n, reverse: c.reverse,
                                     why: c.why.slice(0, 2) }))),
'',
'NOMINATED BY ONLY ONE OF THREE (below threshold, listed for context only):',
JSON.stringify(singleton.map(c => ({ id: c.id, cell: c.cell }))),
'',
'CHALLENGES TO THE CURRENT CONTENTS, seconded by at least two coders:',
JSON.stringify(chal2),
'',
'Look up any element ID you need in ' + DIR + '/subset_*.json for its name and description.',
'',
'Write a short markdown report with these sections and nothing else:',
'  1. CONFIRMED -- current elements the blind pass independently re-derived, per cell.',
'  2. MISSED -- elements the blind pass put in a cell that the hand-built version',
'     does not contain. For each: name, what it measures, which cell, vote count.',
'     This is the section the study cares about most.',
'  3. NOT RE-DERIVED -- current elements that did NOT reach 2-of-3. Say for each',
'     whether any coder nominated it at all, or whether it went unmentioned.',
'  4. CHALLENGED -- seconded objections to current placements.',
'  5. A short verdict: is the hand-built instrument substantially reproduced, and',
'     what are the two or three changes most worth making?',
'',
'Be plain. Do not recommend adopting everything the blind pass found -- a 2-of-3',
'vote from three coders is weak evidence, and adding elements widens the construct.',
'Say which changes are worth it and which are noise. Then report the same as text.',
].join('\n'), { label: 'report', phase: 'Report', effort: 'high' })

return { nominations: nomTotal, consensus: consensus.length, singletons: singleton.length,
         challenges_seconded: chal2.length, consensus_pairs: consensus, report }
