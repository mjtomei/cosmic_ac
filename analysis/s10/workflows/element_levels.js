export const meta = {
  name: 'onet-corporate-levels',
  description: 'Blind multi-label derivation: which elements mark free / bottom / middle / top of a corporate hierarchy',
  phases: [
    { title: 'Nominate', detail: 'three independent coders per subset, four levels, multi-label', model: 'fable' },
  ],
}

// WHY THIS RUN EXISTS
//
// A ladder instrument (free / corporate-bottom / corporate-middle / corporate-
// top) built by rotating the existing directional components degenerated on
// predictor-side values: measured discretion is high across the entire
// white-collar range, so the "top" profile absorbed teachers, nurses, police
// and farmers alike, and middle-vs-top reduced to a single weak axis. The
// standing hypothesis from that failure: O*NET's element set cannot express
// hierarchy LEVELS -- it rates what work is done, not where the job sits.
//
// Matthew's design to test that hypothesis rather than accept it: ask blind
// coders for level signatures DIRECTLY. Four levels including free; an element
// may be nominated for several levels (multi-label -- levels share markers,
// and separation may live in combinations); no draft, no prior results, no
// mention of any earlier derivation or of the components it produced.
//
// READOUT, fixed in advance. The hypothesis is CONFIRMED if the consensus
// signatures fail to separate the levels -- in particular if nothing marks
// "has a boss" (bottom+middle vs top) except discretion reverse-scored, or if
// middle's signature is merely bottom's plus top's with nothing of its own.
// It is REFUTED if distinct signatures exist and, joined to per-occupation
// values, place the known archetypes correctly (executives top, HR/financial
// managers middle, clerks bottom, farmers free). That join happens after this
// run, predictor-side only, no register involved.
const ARGS = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const DIR = ARGS.dir
const K = ARGS.k || 6

const STUDY = [
'THE TASK, in plain terms.',
'',
'We are scoring occupations by their position in a corporate hierarchy, using',
'O*NET descriptors. The occupations are the prior careers of legislators in',
'Australian, British, Canadian and Irish chambers -- lawyers, teachers, farmers,',
'journalists, nurses, business owners, clerks, civil servants, executives,',
'police, manual trades.',
'',
'Four positions:',
'',
'  FREE    -- outside any chain of command. Answers to nobody and commands',
'             nobody: farmers, sole practitioners, own-account tradespeople,',
'             shopkeepers.',
'  BOTTOM  -- inside an organisation, at the base. Supervised, with no',
'             subordinates: clerks, data-entry workers, junior staff, floor',
'             workers, front-line professionals without reports.',
'  MIDDLE  -- managed from above AND managing below, at any remove from the',
'             apex: department heads, HR and finance managers, mid-level',
'             administrators, supervisors of supervisors.',
'  TOP     -- the apex. Directs the organisation with no day-to-day superior',
'             inside it: chief executives, heads of agencies, proprietors of',
'             large firms.',
'',
'Your job: identify which elements\' per-occupation RATINGS mark specific',
'positions. A marker means: occupations at that position rate systematically',
'HIGH on the element (or systematically LOW -- nominate with reverse: true).',
].join('\n')

const RULES = [
'RULES',
'',
'1. MOST ELEMENTS MARK NOTHING. You are seeing a slice of the whole O*NET',
'   content model -- abilities, knowledge, working conditions, interests. The',
'   great majority say nothing about hierarchy position. Returning few or no',
'   nominations for your slice is a correct answer. Do not fill quotas.',
'2. ONE ELEMENT MAY MARK SEVERAL LEVELS, and nominating it for each is expected',
'   where true. Levels share markers: an element high for both MIDDLE and TOP',
'   (say, supervising others) is a fine and useful nomination for both --',
'   separation can come from combinations. Nominate one row per (element,',
'   level) pair, each with its own direction and confidence.',
'3. THE VALUABLE MARKERS ARE THE SEPARATING ONES. Anything that distinguishes',
'   MIDDLE from TOP, or BOTTOM+MIDDLE from TOP (having a boss at all), is worth',
'   more than another marker of "is a manager". Say in the rationale which',
'   levels the element separates.',
'4. REQUIREMENT, NOT APTITUDE. Prefer elements describing what the job INVOLVES',
'   (activities, context) over what a worker must BE GOOD AT (abilities) or',
'   KNOW. "Oral Comprehension" is a capacity; "Repairing and Maintaining',
'   Equipment" is a task. (Neither marks a level -- they illustrate the',
'   distinction only.) Nominate an ability or knowledge element only if the',
'   capacity is a direct indicator of position, and say why.',
'5. REVERSE SCORING IS AVAILABLE per nomination: if occupations at a level rate',
'   systematically LOW on the element, nominate that level with reverse: true.',
'6. INTEREST RATINGS ARE WEAKER EVIDENCE than activity or context ratings.',
'   Not disqualifying, but reflect it in confidence.',
'7. THERE IS NO DRAFT AND NO PRIOR RESULT. Nothing from any earlier coding pass',
'   is shown to you, on purpose. Work from the element definitions and the',
'   level definitions alone.',
].join('\n')

const SCHEMA = {
  type: 'object', required: ['nominations'],
  properties: {
    notes: { type: 'string' },
    nominations: { type: 'array', items: {
      type: 'object', required: ['id', 'level'],
      properties: {
        id: { type: 'string', description: 'element ID verbatim from the subset file' },
        level: { type: 'string', description: 'FREE | BOTTOM | MIDDLE | TOP' },
        reverse: { type: 'boolean', description: 'true if occupations at this level rate LOW on it' },
        confidence: { type: 'string', description: 'high | medium | low' },
        rationale: { type: 'string', description: 'one clause; name which levels it separates' },
      } } },
  },
}

phase('Nominate')
const jobs = []
for (let s = 0; s < K; s++) for (let c = 0; c < 3; c++) jobs.push({ s, c })
const votes = (await parallel(jobs.map(j => () =>
  agent([
'Find O*NET elements whose ratings mark corporate-hierarchy positions, for study S10.',
'',
'Read ' + DIR + '/subset_' + j.s + '.json -- an array of {id, name, desc, file, n_occ}.',
'Consider EXACTLY the elements in that file and no others.',
'',
'You are one of three independent coders on this slice. The others are not shown',
'your answers and you are not shown theirs; a nomination is kept only if at least',
'two of the three make it for the same element, level and direction. Code what',
'you actually think.',
'',
STUDY, '', RULES,
'',
'Return one nomination per (element, level) pair you assert, and omit everything',
'else. Write nothing outside your structured return.',
  ].join('\n'), { label: 'lvl:s' + j.s + 'c' + j.c, phase: 'Nominate',
                  schema: SCHEMA, model: 'fable', effort: 'medium' })
))).map((v, i) => ({ ...jobs[i], v }))

const tally = {}
let nomTotal = 0
const LV = new Set(['FREE', 'BOTTOM', 'MIDDLE', 'TOP'])
for (const { s, v } of votes) {
  if (!v) continue
  for (const n of (v.nominations || [])) {
    if (!n || !n.id || !n.level) continue
    const lv = String(n.level).trim().toUpperCase()
    if (!LV.has(lv)) continue
    nomTotal++
    const sign = n.reverse ? '-' : '+'
    const key = n.id + '|' + lv + '|' + sign
    ;(tally[key] = tally[key] || { id: n.id, level: lv, sign, subset: s, n: 0, why: [] })
    tally[key].n++
    if (n.rationale) tally[key].why.push(n.rationale)
  }
}
const consensus = Object.values(tally).filter(x => x.n >= 2)
                        .sort((a, b) => b.n - a.n || a.id.localeCompare(b.id))
const singleton = Object.values(tally).filter(x => x.n === 1)
const per = {}
for (const c of consensus) per[c.level] = (per[c.level] || 0) + 1
log(nomTotal + ' nominations; ' + consensus.length + ' (element,level,sign) triples at 2-of-3 ' +
    JSON.stringify(per) + '; ' + singleton.length + ' singletons')

return { nominations: nomTotal, consensus: consensus.length, singletons: singleton.length,
         per_level: per, consensus_pairs: consensus,
         singleton_pairs: singleton.map(x => ({ id: x.id, level: x.level, sign: x.sign })) }
