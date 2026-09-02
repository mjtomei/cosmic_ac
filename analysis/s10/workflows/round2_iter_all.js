export const meta = {
  name: 'round2-iter-all',
  description: 'ONE workflow over every scope (full paper + section groups) — iterating subscription panel pass over S10 — tiered seats propose, ground-truth data-faithfulness gate, blind all-seats ballot (incl. own proposals), synthesize with self-preference stats',
  phases: [
    { title: 'Scope', detail: 'index the draft, tile it into single-read groups' },
    { title: 'Propose', detail: 'every scope in parallel' },
    { title: 'Faithfulness', detail: 'ground-truth check per candidate' },
    { title: 'Vote', detail: 'all seats, incl. own proposals, blind' },
    { title: 'Synthesize' },
    { title: 'Apply', detail: 'prose, structure, figures, LaTeX' },
    { title: 'Verify', detail: 'check the manuscript until it comes back clean' },
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
// One workflow covers EVERY scope (Matthew, 2026-09-02: one workflow, cleaner
// architecture than one headless session per scope). args.scopes is a list of
// {id, scope}; the full-paper scope is 'all' and is the only one that can see
// cross-section structural moves.

// SCOPE INDEX (Matthew, 2026-09-02). The section groups used to live in a
// hand-maintained section_groups.json, which silently went stale the moment a
// structural reorganization renumbered the paper: iteration 1's agents were
// handed scopes naming a "§8 Discussion" that no longer existed, and five real
// sections belonged to no group at all. The tiling is now derived at the top of
// every run from the draft's own headings, so it cannot drift from the text.
//
// The workflow sandbox has no filesystem access, so an agent supplies the facts
// (heading lines + total line count) and this script does the arithmetic. The
// packing stays deterministic and assertable here rather than being left to a
// model's judgment.
// Every workflow worker runs on the work subscription; only this orchestrating
// session sits on the personal one.
const FAITH_MODEL = 'work/claude-fable-5'

const READ_CAP_TOKENS = 25000   // the Read tool's hard per-call cap, measured
const MAX_GROUP_LINES = 900     // ~22k tokens on this draft: one read, with slack

const SCOPE_SCHEMA = {
  type: 'object',
  properties: {
    total_lines: { type: 'integer', description: 'total number of lines in the file' },
    headings: {
      type: 'array',
      description: 'every level-2 and level-3 markdown heading, in document order',
      items: {
        type: 'object',
        properties: {
          line: { type: 'integer', description: '1-based line number of the heading' },
          level: { type: 'integer', description: '2 for "## ", 3 for "### "' },
          title: { type: 'string', description: 'heading text without the leading #s' },
        },
        required: ['line', 'level', 'title'],
      },
    },
  },
  required: ['total_lines', 'headings'],
}

const SCOPE_PROMPT = `ROLE: SCOPE INDEX. Mechanical indexing task, no judgment.
Index \`${DRAFT}\` so the run can be split into section groups.

Use Grep with a line-number output mode to find every line that begins with
"## " or "### " (markdown headings at level 2 and 3). Report each one as its
1-based line number, its level (2 or 3), and its heading text with the leading
"#" characters and spaces stripped. Keep them in document order.
Also report the file's total line count.

Do not read the body text, do not summarize, do not omit any heading — an
omitted heading silently drops that part of the paper from the whole run.`

// Pack the heading blocks into contiguous groups that each fit in ONE read.
// Break at a top-level (##) heading once past ~55% of the budget, so groups
// land on section boundaries instead of mid-section wherever possible.
const packGroups = (headings, totalLines) => {
  const hs = (headings || []).filter(h => h && h.line >= 1 && h.line <= totalLines)
                             .sort((a, b) => a.line - b.line)
  if (!hs.length) return [{ id: 'g1', lines: [1, totalLines], headings: [] }]
  const blocks = []
  if (hs[0].line > 1) blocks.push({ a: 1, b: hs[0].line - 1, title: '(front matter)', level: 2 })
  hs.forEach((h, i) => blocks.push({
    a: h.line, b: i + 1 < hs.length ? hs[i + 1].line - 1 : totalLines,
    title: h.title, level: h.level,
  }))
  const out = []
  let cur = []
  for (const b of blocks) {
    const span = b.b - (cur.length ? cur[0].a : b.a) + 1
    if (cur.length && (span > MAX_GROUP_LINES || (b.level === 2 && span > MAX_GROUP_LINES * 0.55))) {
      out.push(cur); cur = [b]
    } else cur.push(b)
  }
  if (cur.length) out.push(cur)
  // Merge adjacent groups that still fit in one read together. The packer breaks
  // on section boundaries, which leaves short tail groups (a 242-line appendix
  // pair, say); merging them costs no extra reads and cuts the agent count, and
  // agent COUNT is what the metered subscriptions ration.
  const merged = []
  for (const g of out) {
    const prev = merged[merged.length - 1]
    if (prev && g[g.length - 1].b - prev[0].a + 1 <= MAX_GROUP_LINES) prev.push(...g)
    else merged.push([...g])
  }
  return merged.map((g, i) => ({
    id: `g${i + 1}`,
    lines: [g[0].a, g[g.length - 1].b],
    headings: g.map(x => x.title),
  }))
}

phase('Scope')
let SCOPES = (args && args.scopes) || null
let SCOPE_INDEX = null
if (!SCOPES) {
  SCOPE_INDEX = await agent(SCOPE_PROMPT, { label: 'scope:index', phase: 'Scope',
                                            model: FAITH_MODEL, schema: SCOPE_SCHEMA })
  if (!SCOPE_INDEX || !SCOPE_INDEX.total_lines) throw new Error('scope index failed; cannot tile the draft')
  const N = SCOPE_INDEX.total_lines
  const groups = packGroups(SCOPE_INDEX.headings, N)
  // Assert the tiling before anything expensive runs on it. A gap here means a
  // whole stretch of the paper goes unreviewed while the run still looks clean.
  if (groups[0].lines[0] !== 1) throw new Error(`tiling does not start at line 1 (starts ${groups[0].lines[0]})`)
  if (groups[groups.length - 1].lines[1] !== N) throw new Error(`tiling ends at ${groups[groups.length - 1].lines[1]}, file has ${N} lines`)
  for (let i = 0; i + 1 < groups.length; i++)
    if (groups[i].lines[1] + 1 !== groups[i + 1].lines[0])
      throw new Error(`gap between ${groups[i].id} and ${groups[i + 1].id}`)
  SCOPES = [{ id: 'full', scope: 'all', lines: [1, N] }].concat(
    groups.map(g => ({ id: g.id, scope: g.headings.join(', '), lines: g.lines, headings: g.headings })))
  log(`scope index: ${SCOPE_INDEX.headings.length} headings over ${N} lines -> ${groups.length} groups + the full paper`)
  for (const g of groups)
    log(`  ${g.id}: lines ${g.lines[0]}-${g.lines[1]} (${g.lines[1] - g.lines[0] + 1}) — ${g.headings.slice(0, 3).join(', ')}${g.headings.length > 3 ? ` (+${g.headings.length - 3})` : ''}`)
}

const PHASE = String((args && args.phase) || 1)
const ITER = (args && args.iteration) || 1
// Panels per phase (Matthew, 2026-09-02). Every seat proposes AND votes on
// every candidate including its own — no self-exclusion — while staying blind
// to authorship; provenance is kept out of band so self-preference is
// measurable. `effort` is passed through to the agent call.
const PANELS = {
  // wide sweep: full paper + section groups
  '1': [
    { id: 'opus-5-med',   type: 'sub-anthropic-high',  family: 'anthropic', model: 'work/claude-opus-5',      effort: 'medium' },
    { id: 'sol',          type: 'sub-openai-mid',      family: 'openai',    model: 'chatgpt/gpt-5.6-sol' },
    { id: 'grok-4.6',     type: 'sub-xai-mid',         family: 'xai',       model: 'grok/grok-4.6' },
  ],
  // intermediate: full paper
  '2': [
    { id: 'fable-5.1-hi', type: 'sub-anthropic-fable', family: 'anthropic', model: 'work/claude-fable-5',     effort: 'high' },
    { id: 'sol-high',     type: 'sub-openai-high',     family: 'openai',    model: 'chatgpt/gpt-5.6-sol-high' },
    { id: 'grok-4.6-hi',  type: 'sub-xai-high',        family: 'xai',       model: 'grok/grok-4.6-high' },
  ],
  // final: the metered labs join the three subscription seats
  '3': [
    { id: 'fable-5.1-hi', type: 'sub-anthropic-fable', family: 'anthropic', model: 'work/claude-fable-5',     effort: 'high' },
    { id: 'sol-high',     type: 'sub-openai-high',     family: 'openai',    model: 'chatgpt/gpt-5.6-sol-high' },
    { id: 'grok-4.6-hi',  type: 'sub-xai-high',        family: 'xai',       model: 'grok/grok-4.6-high' },
    { id: 'gemini',       type: 'panel-google',        family: 'google',    model: 'google/gemini-3.1-pro-preview' },
    { id: 'kimi',         type: 'panel-moonshot',      family: 'moonshot',  model: 'moonshotai/kimi-k3' },
    { id: 'qwen-max',     type: 'panel-alibaba',       family: 'alibaba',   model: 'qwen/qwen3.8-max' },
    { id: 'deepseek',     type: 'panel-deepseek',      family: 'deepseek',  model: 'deepseek/deepseek-v4-pro' },
  ],
}
// USAGE LIMITS. Quota can run out mid-run, so ballot counts legitimately differ
// from one candidate to the next. That is fine: a change is judged unanimous
// among the seats that actually voted on IT. No quorum, no minimum — every
// verdict carries its ballot count, and any thin decision can be revisited after
// the iteration, since each round is committed separately.
const isLimit = (e) => /rate.?limit|quota|usage limit|429|overload|capacity|exhaust/i.test(String(e || ''))

const PANEL = PANELS[PHASE]
const PROPOSERS = PANEL

// ACCOUNTS (Matthew, 2026-09-02). Every workflow worker runs on the WORK
// Anthropic subscription; only this orchestrating session sits on the personal
// one. That is what iteration 1 got wrong — seats, faithfulness gate and
// orchestrator all landed on the personal pool and hit its session limit an
// hour in, losing 4 of 7 scopes. The seat's model is named here rather than in
// the agent definition's frontmatter, which only accepts names ending in
// `claude-*` and was the reason the router needed alias backends at all.

// ======================= STAGE PROMPTS (review these) =======================

// Role variants (Matthew, 2026-09-02): the three the first run had — a neutral
// reviewer plus two brief-primed specialists — now available to EVERY seat, but
// only on full-text runs, where a global view of prose flow and of the tables and
// figures is what the briefs are for. Section runs use the neutral variant alone.
// The primed variants are propose-only; voting stays with the neutral seats, so
// ballot cost does not triple.
const variantsFor = (scope) => scope === 'all'
  ? [
      { id: 'neutral', brief: null },
      { id: 'prose',   brief: 'analysis/s10/writing_refs/gopen_swan_principles.md' },
      { id: 'dataviz', brief: 'analysis/s10/dataviz_refs/data_presentation_principles.md' },
    ]
  : [{ id: 'neutral', brief: null }]

const BRIEF_NOTE = {
  prose: `Before proposing, read \`analysis/s10/writing_refs/gopen_swan_principles.md\`
— the reader-expectation brief (subject-verb proximity, topic and stress
positions, old-before-new, one-unit-one-point). Propose prose and flow changes
that those principles actually justify, and name the principle in each rationale.`,
  dataviz: `Before proposing, read \`analysis/s10/dataviz_refs/data_presentation_principles.md\`
— the data-presentation brief (proportional ink, encoding by decodability, direct
labels over legends, small multiples, honest axes, no mixed estimands in one
column). Propose changes to how quantities are presented: tables, figures, and
the in-text presentation of numbers. If a change would require recomputing a
value, say so and skip it — never invent a number.`,
}

const readingNote = (sc) => {
  if (!sc || !sc.lines) return `Read the manuscript at \`${DRAFT}\`.`
  const [a, b] = sc.lines
  const n = b - a + 1
  if (sc.scope === 'all') return `Read the whole manuscript at \`${DRAFT}\` — lines ${a}-${b}.
Read it in ${Math.ceil(n / MAX_GROUP_LINES)} successive calls of ${MAX_GROUP_LINES} lines: offset=${a}, then
offset=${a + MAX_GROUP_LINES}, and so on until you reach line ${b}. Cover all of it — do not
stop after the first chunk.`
  return `Your scope is lines ${a}-${b} of \`${DRAFT}\` (${n} lines), which covers:
${sc.headings ? sc.headings.map(h => '  - ' + h).join('\n') : '  ' + sc.scope}
Read exactly that range in one call: Read with offset=${a}, limit=${n}. Read
outside the range only to check a specific cross-reference, and propose changes
only within the range.`
}

const PROPOSE_PROMPT = (variant, sc) => `ROLE: PROPOSE.
${readingNote(sc)}
${BRIEF_NOTE[variant] || 'Propose writing and structure improvements on the merits.'}

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

What you write is MANUSCRIPT TEXT ONLY. Never insert notes to the author,
build instructions, TODOs, or bracketed asides about how a change should be
produced — if a change needs work outside the text, say so in \`rationale\`,
which is not part of the manuscript. Never reference a figure, image, table,
or file that does not already exist: proposing \`![](new_figure.png)\` puts a
broken reference into the paper, because nothing downstream creates the file.
To argue for a figure that does not yet exist, describe it in \`rationale\`
instead of inserting a reference to it.

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

// APPLICATION (runs AFTER this workflow returns; see analysis/s10/apply_changes.py):
//   1. Only UNANIMOUS changes that cleared the data-faithfulness gate are applied.
//   2. HIGHEST SCORING FIRST. When several accepted proposals contend for the same
//      target, only one can land, so the best-scoring variant wins — never list
//      order. Prose: grouped by the exact passage being replaced. Structural:
//      grouped by (section, action), since rival takes on one reorganization share
//      both, while different actions on a section may be complementary.
//   3. Everything else — non-unanimous, and rival takes that lost — goes to a
//      review queue rather than the draft.
//   3b. PROSE IS APPLIED BEFORE STRUCTURAL, and the order matters: mechanical
//      prose application needs `current` verbatim, while structural changes
//      renumber sections and so rewrite the §N references inside prose
//      passages. Structural-first would silently break every prose anchor
//      containing a section reference. Brittle exact-match step first, tolerant
//      judgment step second.
//   4. Structural changes are executed by an agent, not by string replacement —
//      see analysis/s10/apply_structural_brief.md for its brief, which includes
//      the mandatory hygiene pass (LaTeX label map, moved-material references,
//      stale titles, orphaned pronouns).
//   5. analysis/s10/check_manuscript.py then runs, and the fix/re-check loop
//      repeats UNTIL IT REPORTS CLEAN — one pass is not enough, since a fix can
//      expose the next problem.
//   6. Each iteration is committed, so every round is separately revertible.

// ============================== ORCHESTRATION ==============================
// One workflow, every scope. Each scope runs the full pipeline independently and
// concurrently; the workflow's own concurrency cap (min(16, cpus-2)) throttles
// the fan-out, which is what a shell-level job limiter failed to do.

const runScope = async (sc) => {
  const { id, scope } = sc
  const variants = variantsFor(scope)
  const SEATS = PANEL
  const jobs = []
  for (const m of SEATS) for (const v of variants) jobs.push({ m, v })

  const raw = await parallel(jobs.map(({ m, v }) => () =>
    agent(PROPOSE_PROMPT(v.id, sc),
          { agentType: m.type, model: m.model, label: `propose:${id}:${m.id}:${v.id}`, phase: 'Propose',
            schema: PROPOSAL_SCHEMA, ...(m.effort ? { effort: m.effort } : {}) })
      .then(r => ({ member: `${m.id}/${v.id}`, family: m.family, changes: (r && r.changes) || [] }))
      .catch(e => ({ member: `${m.id}/${v.id}`, family: m.family, changes: [],
                     failed: { seat: m.id, stage: 'propose', limit: isLimit(e), err: String(e).slice(0, 160) } }))))
  const failures = raw.filter(Boolean).filter(r => r.failed).map(r => r.failed)
  const proposals = []
  for (const p of raw.filter(Boolean)) for (const c of p.changes)
    proposals.push({ ...c, member: p.member, family: p.family })

  const byKey = {}
  for (const c of proposals) {
    const k = `${c.locus}|${c.action}|${c.proposed}`
    if (!byKey[k]) byKey[k] = { locus: c.locus, type: c.type, action: c.action, current: c.current,
      proposed: c.proposed, rationale: c.rationale, support: 0,
      author_seats: new Set(), author_families: new Set() }
    byKey[k].support += 1
    byKey[k].author_seats.add(c.member)
    byKey[k].author_families.add(c.family)
  }
  const candidates = Object.values(byKey).map((c, i) =>
    ({ ...c, id: `${id}-C${i + 1}`, author_seats: [...c.author_seats], author_families: [...c.author_families] }))
  log(`${id}: ${proposals.length} proposals -> ${candidates.length} candidates`)

  const faiths = await parallel(candidates.map(c => () =>
    agent(FAITH_PROMPT(c), { agentType: 'check-faithfulness', model: FAITH_MODEL, label: `faith:${c.id}`,
                             phase: 'Faithfulness', schema: FAITH_SCHEMA }).catch(() => null)))
  const withFaith = candidates.map((c, i) => {
    const f = faiths[i]
    const gate = !!f && f.locatable !== false && f.data_faithful === 'pass'
    return { ...c, scope: id, faith: f, faith_gate: gate,
             faith_reason: !f ? 'faith_check_errored' : f.locatable === false ? 'not_locatable'
               : f.data_faithful !== 'pass' ? 'data_changed' : null }
  })
  const survivors = withFaith.filter(c => c.faith_gate)

  const scored = await parallel(survivors.map(cand => async () => {
    const prompt = cand.type === 'structural' ? VOTE_STRUCTURAL(cand) : VOTE_PROSE(cand)
    const ballots = await parallel(SEATS.map(v => () =>
      agent(prompt, { agentType: v.type, model: v.model, label: `vote:${cand.id}:${v.id}`, phase: 'Vote',
                      schema: VOTE_SCHEMA, ...(v.effort ? { effort: v.effort } : {}) })
        .then(s => ({ voter: v.id, is_author: cand.author_seats.some(a => String(a).split('/')[0] === v.id), ...s }))
        .catch(e => ({ voter: v.id, failed: true, limit: isLimit(e), err: String(e).slice(0, 160) }))))
    return { id: cand.id, votes: ballots.filter(b => b && !b.failed), lost: ballots.filter(b => b && b.failed) }
  }))

  const votesById = {}, cast = {}, lostBy = {}, limitBy = {}
  for (const s of scored) {
    votesById[s.id] = s.votes
    for (const b of s.votes) cast[b.voter] = (cast[b.voter] || 0) + 1
    for (const b of (s.lost || [])) {
      lostBy[b.voter] = (lostBy[b.voter] || 0) + 1
      if (b.limit) limitBy[b.voter] = (limitBy[b.voter] || 0) + 1
    }
  }
  const present = SEATS.filter(m => (cast[m.id] || 0) > 0).map(m => m.id)
  const absent = SEATS.filter(m => (cast[m.id] || 0) === 0).map(m => m.id)
  if (absent.length) log(`${id}: seats absent — ${absent.join(', ')}; judged among ${present.join(', ')}`)

  const decide = (v) => {
    const voter_data_fail = v.some(x => x.data_faithful === 'fail')
    const deps = v.map(x => x.dependencies).filter(d => d && d.trim())
    const keeps = v.filter(x => x.keep).length
    const composite = v.length
      ? Math.round((v.reduce((s, x) => s + x.clarity + x.voice + x.concision + x.structural_soundness, 0) / v.length) * 100) / 100
      : 0
    return { accepted: v.length > 0 && !voter_data_fail && keeps > v.length / 2,
             keeps, n: v.length, voter_data_fail, dependencies: deps, composite,
             ...(v.length < present.length ? { thin: true, seats_present: present.length } : {}) }
  }
  const changes = withFaith.map(c => {
    const votes = votesById[c.id] || []
    return { ...c, votes,
      verdict: c.faith_gate ? decide(votes)
        : { accepted: false, keeps: 0, n: 0, dropped: c.faith_reason, composite: 0 } }
  }).sort((a, b) => String(a.locus).localeCompare(String(b.locus)))

  const sp = {}
  for (const r of changes) for (const b of r.votes) {
    const k = b.voter; sp[k] = sp[k] || { self_n: 0, self_keep: 0, other_n: 0, other_keep: 0 }
    if (b.is_author) { sp[k].self_n++; if (b.keep) sp[k].self_keep++ }
    else { sp[k].other_n++; if (b.keep) sp[k].other_keep++ }
  }
  const accepted = changes.filter(c => c.verdict.accepted).length
  log(`${id}: ${accepted} accepted of ${candidates.length} (${candidates.length - survivors.length} failed the data gate)`)
  return { scope_id: id, scope, variants: variants.map(v => v.id),
           n_proposals: proposals.length, n_candidates: candidates.length,
           n_faith_pass: survivors.length, n_faith_dropped: candidates.length - survivors.length,
           accepted, self_preference: sp,
           panel_health: { present, absent, ballots_cast: cast, ballots_lost: lostBy,
                           lost_to_limits: limitBy, propose_failures: failures },
           changes }
}

const APPLY_SCHEMA = {
  type: 'object',
  properties: {
    done: { type: 'array', items: { type: 'string' }, description: 'ids (or short descriptions) of what was applied' },
    skipped: { type: 'array', items: { type: 'string' }, description: 'ids not applied, each with its reason' },
    notes: { type: 'string', description: 'what the tooling printed, and anything the next stage needs to know' },
  },
  required: ['done', 'skipped', 'notes'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    clean: { type: 'boolean', description: 'true ONLY if the final check_manuscript.py run reported no issues' },
    fixed: { type: 'array', items: { type: 'string' }, description: 'issues found and fixed this pass' },
    remaining: { type: 'string', description: 'issues still outstanding, or empty when clean' },
  },
  required: ['clean', 'fixed', 'remaining'],
}

phase('Propose')
log(`iteration ${ITER}, phase ${PHASE}: ${SCOPES.length} scope(s), ${PANEL.length} seats — ${PANEL.map(m => `${m.id}=${m.model}`).join(', ')}`)
const perScope = await parallel(SCOPES.map(s => () => runScope(s)))

phase('Synthesize')
const ok = perScope.filter(Boolean)
const totals = ok.reduce((a, r) => ({
  proposals: a.proposals + r.n_proposals, candidates: a.candidates + r.n_candidates,
  faith_dropped: a.faith_dropped + r.n_faith_dropped, accepted: a.accepted + r.accepted,
}), { proposals: 0, candidates: 0, faith_dropped: 0, accepted: 0 })
log(`iteration ${ITER}: ${totals.accepted} accepted of ${totals.candidates} candidates across ${ok.length} scope(s)`)

// ============================== SELECT =====================================
// Which changes land is pure computation over the ballots, so it lives here
// rather than in a separate script: deterministic, and inspectable next to the
// votes that produced it. Auto-accept requires UNANIMITY among whoever voted on
// THAT change (quota can run out mid-run, so n legitimately varies).
const isUnanimous = (c) => {
  const v = c.verdict || {}
  return !!v.accepted && (v.n || 0) > 0 && v.keeps === v.n
}
const norm = (t) => String(t || '').split(/\s+/).filter(Boolean).join(' ')
const byScore = (a, b) =>
  ((b.verdict || {}).composite || 0) - ((a.verdict || {}).composite || 0) ||
  (b.support || 0) - (a.support || 0) ||
  String(a.id).localeCompare(String(b.id))
// Rival takes on one passage/reorganization: only one can land, and it should be
// the best-scoring one, not whichever happens to come first in the list.
const pickBest = (items, keyOf) => {
  const g = {}
  for (const c of items) (g[keyOf(c)] = g[keyOf(c)] || []).push(c)
  const kept = [], dropped = []
  for (const k of Object.keys(g)) {
    const v = g[k].slice().sort(byScore)
    kept.push(v[0]); dropped.push(...v.slice(1))
  }
  return { kept, dropped }
}
const sectionOf = (c) => {
  const m = String(c.locus || '').match(/(\d+(?:\.\d+[a-z]?)?)/)
  return m ? m[1] : String(c.locus || '').slice(0, 12)
}

const allChanges = ok.flatMap(r => r.changes || [])
const unanimousAll = allChanges.filter(isUnanimous)
const queuedSplit = allChanges.filter(c => (c.verdict || {}).accepted && !isUnanimous(c))
const proseRaw = unanimousAll.filter(c => c.type === 'prose' && (c.action === 'rewrite' || c.action === 'merge'))
const structRaw = unanimousAll.filter(c => !proseRaw.includes(c))
const proseSel = pickBest(proseRaw, c => norm(c.current))
const structSel = pickBest(structRaw, c => sectionOf(c) + '|' + c.action)
const selection = {
  prose: proseSel.kept, structural: structSel.kept,
  dropped_rivals: { prose: proseSel.dropped.map(c => c.id), structural: structSel.dropped.map(c => c.id) },
  queued_not_unanimous: queuedSplit.map(c => c.id),
  thin: unanimousAll.filter(c => (c.verdict || {}).thin).map(c => ({ id: c.id, keeps: c.verdict.keeps, n: c.verdict.n })),
}
log(`select: ${unanimousAll.length} unanimous of ${allChanges.length} -> ${selection.prose.length} prose + ${selection.structural.length} structural`)
log(`  dropped as rival takes: ${proseSel.dropped.length} prose, ${structSel.dropped.length} structural; ${queuedSplit.length} accepted-but-not-unanimous left for review`)
if (selection.thin.length) log(`  ${selection.thin.length} decided by a reduced panel (ballots lost mid-run) — revisit if desired`)

const APPLY_OFF = args && args.apply === false
if (APPLY_OFF || (!selection.prose.length && !selection.structural.length)) {
  log(APPLY_OFF ? 'apply disabled by args.apply=false' : 'nothing selected; skipping apply')
  return { iteration: ITER, phase: PHASE, scopes: ok.map(r => r.scope_id), totals, selection, by_scope: ok }
}

// ============================== APPLY ======================================
// Sequential by necessity. Prose applies by exact match on verbatim `current`
// text; structural renumbering rewrites the §N references those anchors live
// inside, so doing structure first would break every prose anchor.
phase('Apply')
const applyResults = {}

applyResults.prose = await agent(`ROLE: APPLY PROSE.
Apply these ${selection.prose.length} unanimously accepted prose rewrites to \`${DRAFT}\`.

Use the Edit tool, ONE CALL PER CHANGE, passing \`current\` as old_string and
\`proposed\` as new_string, both verbatim. Edit requires an exact, unique match
and fails otherwise — that failure is the safety property this stage relies on,
so never work around it:

- If a change's \`current\` does not match, report it as skipped with the reason.
  Do NOT hunt for a passage that looks close and edit that instead. A near match
  is how a silent corruption enters a manuscript whose numbers must not move.
- If Edit reports the text is not unique, report it as ambiguous and skip it.
  Do not disambiguate by picking one.
- Do not adjust, re-wrap, or "clean up" either string to make an edit land.
- Apply them in the order given.

Some changes may legitimately fail to match because an earlier change in this
same list already rewrote overlapping text. That is expected and is exactly what
you should report, not repair.

Return the ids applied, the ids skipped each with its reason, and nothing else.

${JSON.stringify(selection.prose.map(c => ({ id: c.id, current: c.current, proposed: c.proposed })), null, 1)}`,
  { agentType: 'apply-integrator', phase: 'Apply', label: 'apply:prose', schema: APPLY_SCHEMA })

applyResults.structural = await agent(`ROLE: APPLY STRUCTURE.
Read \`analysis/s10/apply_structural_brief.md\` first and follow it.

Apply these ${selection.structural.length} unanimously accepted structural changes to
\`${DRAFT}\`. They are natural-language instructions, not diffs, so they need
judgment: carry out the move/split/merge, then repair everything it disturbs —
section numbering, every \`§N\` cross-reference, heading levels, and any
transition sentence left dangling by the move.

Where a change lists dependencies (a stranded reference, a figure that must move
with its text), carry the dependency out. A dependency is work to do, never a
reason to skip the change.

If two of these genuinely conflict, apply the higher-composite one and report the
other as skipped with the reason. Never invent content to bridge a seam.

${JSON.stringify(selection.structural.map(c => ({ id: c.id, locus: c.locus, action: c.action,
   proposed: c.proposed, rationale: c.rationale, composite: (c.verdict || {}).composite,
   dependencies: (c.verdict || {}).dependencies || [] })), null, 1)}`,
  { agentType: 'apply-integrator', phase: 'Apply', label: 'apply:structural', schema: APPLY_SCHEMA })

applyResults.figures = await agent(`ROLE: BUILD REQUESTED FIGURES.
Read \`analysis/s10/apply_structural_brief.md\` sections "Building figures the
panel asked for" and "Wiring a figure into LaTeX" first, and follow them.

Some accepted changes may ask for a figure or table that does not exist yet.
Find any such request among the changes just applied to \`${DRAFT}\`.

For each: build it from the manuscript's OWN numbers with a script under
analysis/s10/ (never invent or re-derive a value), render it, look at the output
and fix what is wrong, then wire it in. Every figure reference must resolve —
a reference to a file that does not exist on disk is a broken build, and that is
the specific failure this stage exists to prevent.

If nothing asks for a new figure, do nothing and say so. Never create a figure
that was not requested.`,
  { agentType: 'apply-integrator', phase: 'Apply', label: 'apply:figures', schema: APPLY_SCHEMA })

// ============================== VERIFY =====================================
// One pass is not enough: fixing one problem routinely exposes the next, which
// is how a desynchronized LaTeX label map survived the last round. Loop until
// the checker reports clean, and say so plainly if it never does.
phase('Verify')
let clean = false
const verifyPasses = []
for (let pass = 1; pass <= 5 && !clean; pass++) {
  const r = await agent(`ROLE: VERIFY AND FIX (pass ${pass}).
Run: python3 analysis/s10/check_manuscript.py

It checks that every §-reference and appendix reference resolves, every footnote
is defined, headings and numbers are unique, every numbered heading and appendix
letter has a label-map entry in \`analysis/s10/latex/reformat.py\`, every asset
referenced by the draft exists on disk, and every figure has a FIGLABEL entry.

If it reports issues, fix them at the source and run it again. Two rules:
- Never hard-code a number or a letter to satisfy a reference. Sections and
  appendices are numbered by LaTeX from labels; add or correct the label and let
  it resolve. A hard-coded "§4.7" silently rots the next time anything moves.
- Never delete a reference to make the check pass unless the thing it points to
  genuinely should not exist.

Set clean=true ONLY if the checker's final run reported no issues. If you cannot
get it clean, set clean=false and report precisely what remains — an honest
report of a residual problem is worth more than a forced pass.`,
    { agentType: 'apply-integrator', phase: 'Verify', label: `verify:pass${pass}`, schema: VERIFY_SCHEMA })
  verifyPasses.push(r)
  clean = !!(r && r.clean)
  log(`verify pass ${pass}: ${clean ? 'clean' : 'issues remain — ' + ((r && r.remaining) || 'no detail returned')}`)
  if (!r) break
}
if (!clean) log('VERIFY DID NOT REACH CLEAN — the draft needs a look before this iteration is trusted')

return { iteration: ITER, phase: PHASE, scopes: ok.map(r => r.scope_id), totals, selection,
         applied: applyResults, verify: { clean, passes: verifyPasses }, by_scope: ok }
