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
// MODELS FOR THE NON-VOTING WORK. Fable is the most capable model here and the
// most expensive, so it is spent on exactly one thing: the faithfulness gate.
// That gate is the only hard stop in the pipeline — it decides whether a change
// moved a datum, and a miss there puts a wrong number into the paper, which no
// amount of downstream voting recovers. Everything else that is not a panel seat
// — indexing headings, reading back a saved result, applying and verifying — is
// judgment or mechanics that Opus does well, so it goes there.
const FAITH_MODEL = 'work/claude-fable-5-1'
const WORKER_MODEL = 'work/claude-opus-5'

const READ_CAP_TOKENS = 25000   // the Read tool's hard per-call cap, measured
const LINES_PER_READ = 900      // ~22k tokens of this draft: what one read returns
// How big a section group is, which is NOT the same question as how much fits in
// one read. args.groups asks for a target number of groups; a group larger than
// LINES_PER_READ simply takes more than one read, and the propose prompt says so.
const TARGET_GROUPS = (args && args.groups) || null
let GROUP_LINES = LINES_PER_READ

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

Report every markdown heading at level 2 or 3 — every line beginning "## " or
"### " — as its 1-based line number, its level (2 or 3), and its heading text
with the leading "#" characters and spaces stripped, in document order. Also
report the file's total line count.

Search for them rather than reading the body; you need the headings and the
line count, nothing else.

Do not read the body text, do not summarize, do not omit any heading — an
omitted heading silently drops that part of the paper from the whole run.`

// Pack the heading blocks into contiguous groups that each fit in ONE read.
// Break at a top-level (##) heading once past ~55% of the budget, so groups
// land on section boundaries instead of mid-section wherever possible.
const packGroups = (headings, totalLines, maxLines) => {
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
    if (cur.length && (span > maxLines || (b.level === 2 && span > maxLines * 0.55))) {
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
    if (prev && g[g.length - 1].b - prev[0].a + 1 <= maxLines) prev.push(...g)
    else merged.push([...g])
  }
  return merged.map((g, i) => ({
    id: `g${i + 1}`,
    lines: [g[0].a, g[g.length - 1].b],
    headings: g.map(x => x.title),
  }))
}

// RESUME. args.resume_from is a list of saved per-scope result files from an
// earlier run. Their changes already carry verdicts, so the run re-enters at
// Select and exercises Apply/Verify without re-proposing. Only results whose
// ballots came from the full panel belong here: "unanimous among whoever voted"
// exists for a seat dropping out mid-run, not for a panel of one, and a
// single-seat result would pass everything.
const RESUME = (args && args.resume_from) || null

// RESUME AT FAITHFULNESS. args.resume_proposals is a list of manifest files
// listing proposals that were made but never judged — iteration 1 lost four
// scopes to a usage limit after the proposers had done their work, and the
// propose stage is by far the most expensive one to repeat. Each manifest row
// carries only what selection needs plus a `path`; the change's full text lives
// in its own small file, because 111 changes is 240KB and every agent needs
// exactly one of them.
const RESUME_PROPOSALS = (args && args.resume_proposals) || null

const CANDIDATE_SCHEMA = {
  type: 'object',
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' }, scope: { type: 'string' },
          type: { type: 'string', description: 'prose or structural' },
          action: { type: 'string' }, locus: { type: 'string' },
          current_key: { type: 'string' }, member: { type: 'string' },
          family: { type: 'string' },
          path: { type: 'string', description: 'file holding this change in full' },
        },
        required: ['id', 'scope', 'type', 'action', 'locus', 'path'],
      },
    },
  },
  required: ['candidates'],
}

const LOAD_SCHEMA = {
  type: 'object',
  properties: {
    scope_id: { type: 'string' },
    seats_max: { type: 'integer', description: 'the largest ballot count any change in this file received' },
    changes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          type: { type: 'string', description: 'prose or structural' },
          action: { type: 'string' },
          locus: { type: 'string' },
          current_key: { type: 'string', description: 'first 120 characters of the change\'s current text, whitespace collapsed — used only to group rival rewrites of one passage' },
          support: { type: 'integer' },
          accepted: { type: 'boolean' },
          keeps: { type: 'integer' },
          n: { type: 'integer' },
          composite: { type: 'number' },
        },
        required: ['id', 'type', 'action', 'locus', 'current_key', 'accepted', 'keeps', 'n', 'composite'],
      },
    },
  },
  required: ['scope_id', 'seats_max', 'changes'],
}

phase('Scope')
let SCOPES = (args && args.scopes) || null
let SCOPE_INDEX = null
if (!SCOPES && !RESUME && !RESUME_PROPOSALS) {
  SCOPE_INDEX = await agent(SCOPE_PROMPT, { label: 'scope:index', phase: 'Scope',
                                            model: WORKER_MODEL, schema: SCOPE_SCHEMA })
  if (!SCOPE_INDEX || !SCOPE_INDEX.total_lines) throw new Error('scope index failed; cannot tile the draft')
  const N = SCOPE_INDEX.total_lines
  // Solve for the requested group count rather than guessing a budget. The
  // packer prefers to break at a top-level heading once past ~55% of budget, so
  // a budget of N/target alone overshoots; widen it until the count is met.
  if (TARGET_GROUPS) {
    GROUP_LINES = Math.ceil(N / TARGET_GROUPS)
    while (packGroups(SCOPE_INDEX.headings, N, GROUP_LINES).length > TARGET_GROUPS && GROUP_LINES < N)
      GROUP_LINES = Math.ceil(GROUP_LINES * 1.05)
  }
  const groups = packGroups(SCOPE_INDEX.headings, N, GROUP_LINES)
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
  // wide sweep: full paper + section groups.
  // 2026-09-03: grok and sol are OUT, glm and muse are IN. Both departures are
  // operational rather than about judgment. sol kept exhausting its ChatGPT Plus
  // cap mid-run — three separate runs lost ballots to it, and in two scopes it
  // never voted at all. grok was 64% of iteration 3's total output at 10,134
  // tokens per ballot against sol's 486, and took 7 of that run's 14
  // data-gate rejections on 48% of the proposals. The replacements route through
  // OpenRouter, which is metered credits with no session cap, so a run cannot be
  // cut in half by a quota resetting three hours out.
  '1': [
    { id: 'opus-5-med',   type: 'sub-anthropic-high',  family: 'anthropic', model: 'work/claude-opus-5',      effort: 'medium' },
    { id: 'glm-5.3',      type: 'panel-zai',           family: 'zai',       model: 'z-ai/glm-5.3-flash' },
    { id: 'muse-spark',   type: 'panel-meta',          family: 'meta',      model: 'meta/muse-spark-1.3-contributor' },
  ],
  // intermediate: full paper
  '2': [
    { id: 'fable-5.1-hi', type: 'sub-anthropic-fable', family: 'anthropic', model: 'work/claude-fable-5-1',     effort: 'high' },
    { id: 'sol-high',     type: 'sub-openai-high',     family: 'openai',    model: 'chatgpt/gpt-5.6-sol-high' },
    { id: 'grok-4.6-hi',  type: 'sub-xai-high',        family: 'xai',       model: 'grok/grok-4.6-high' },
  ],
  // final: the metered labs join the three subscription seats
  '3': [
    { id: 'fable-5.1-hi', type: 'sub-anthropic-fable', family: 'anthropic', model: 'work/claude-fable-5-1',     effort: 'high' },
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
  const reads = Math.ceil(n / LINES_PER_READ)
  const where = sc.scope === 'all'
    ? `Your scope is the whole manuscript at \`${DRAFT}\` — lines ${a}-${b}.`
    : `Your scope is lines ${a}-${b} of \`${DRAFT}\` (${n} lines), which covers:
${sc.headings ? sc.headings.map(h => '  - ' + h).join('\n') : '  ' + sc.scope}`
  const how = reads <= 1
    ? `That range is small enough to take in as one piece, so read it in one go.`
    : `It is too long to take in at once — about ${LINES_PER_READ} lines is as much as one
read returns — so work through it in ${reads} successive stretches, starting at line
${a} and continuing until you reach line ${b}. Cover all of it; do not stop after
the first stretch.`
  const bound = sc.scope === 'all'
    ? `Propose changes anywhere in it.`
    : `Look outside the range only to check a specific cross-reference, and propose
changes only within it.`
  return `${where}
${how}
${bound}`
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

// A resumed candidate's text is in its own file rather than inline. Everything
// else about judging it is unchanged, so the prompts differ only in where the
// change comes from.
const changeBody = (c, curLabel, propLabel) => c.path
  ? `The change is recorded at \`${c.path}\` — read it. The record holds the locus,
the ${curLabel} text, the ${propLabel}, and the rationale.`
  : `${curLabel} (§${c.locus}):
${c.current}

${propLabel}:
${c.proposed}
RATIONALE: ${c.rationale}`

const VOTE_PROSE = (c) => `ROLE: VOTE (prose change), authorship removed.

${changeBody(c, 'CURRENT', 'PROPOSED rewrite')}

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

${changeBody(c, 'CURRENT PLACEMENT', 'PROPOSED MOVE (' + c.action + ')')}

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
${changeBody(c, 'CURRENT (as supplied by the proposer — verify it matches the manuscript)', 'PROPOSED')}

Return { locatable, current_matches, data_faithful: "pass"|"fail", note }.

current_matches asks ONE mechanical question: does the CURRENT text below appear
in the manuscript, allowing only for differences in line wrapping? Search the
file for it and answer from what you find. Do not infer it from whether the
change reads like a sensible edit, and do not reason forward from CURRENT to
PROPOSED to decide it — a proposer can quote a passage that was true of an
earlier draft, or was never there at all. If the manuscript already reads the
way PROPOSED describes, current_matches is false: the passage the proposer
meant to replace is not there.
data_faithful is "fail" if any number, statistic, CI/error bar, sample size,
p-value, sign or direction of a measured effect, unit, estimand label, or a
claim of what was/wasn't found changes, is added, or is dropped. Changes to
interpretation, framing, emphasis, hedging, or order are "pass". Fail closed
if you cannot locate the passage or verify a number.`

// REPAIR (Matthew, 2026-09-03). Most gate failures are a sloppy execution of a
// sound idea rather than a bad idea: of the 16 changes iteration 4 dropped, 13
// either deleted a number the rest of the manuscript does not carry, or moved a
// qualifier so it scoped over a statistic it does not describe. Both are one
// small edit from faithful. So before a candidate is discarded, the model that
// caught the problem is asked whether a minimal repair saves it -- and told
// plainly that refusing is expected whenever repair would mean inventing,
// guessing, or gutting the change.
const REPAIR_PROMPT = (c) => `ROLE: REPAIR A CHANGE THAT FAILED THE DATA CHECK.

Manuscript: \`${DRAFT}\`. Open it and read the passage at the locus.

LOCUS: §${c.locus}
${changeBody(c, 'CURRENT', 'PROPOSED')}

WHY IT FAILED: ${(c.faith || {}).note}

The change's INTENT is worth keeping — a panel would not have seen it otherwise.
Your question is narrow: is there a small edit to the PROPOSED text that fixes
the fault named above while leaving the change recognisably the same change?

The two faults that are usually repairable:
- A datum was dropped that appears nowhere else in the manuscript. Put it back,
  in the proposed text's own phrasing, where it naturally belongs.
- A qualifier or scope-setting phrase was moved or added so that it now covers a
  statistic it does not describe. Narrow it to what the manuscript supports.

Refuse — repaired false — whenever fixing it would mean any of:
- inventing a number, a citation, or a claim not already in the manuscript;
- guessing which of several readings the proposer meant;
- rewriting so much that it is no longer the change that was proposed;
- the quoted CURRENT text not being in the manuscript at all, leaving nothing to
  anchor a repair to.

Refusing is a good answer and the expected one in a fair share of cases. A
repair that quietly disturbs a different datum is far worse than a drop.

If you repair it, return the COMPLETE repaired replacement text — not a diff,
not a description — and one sentence saying what you restored or narrowed.`

const REPAIR_SCHEMA = {
  type: 'object',
  properties: {
    repaired: { type: 'boolean', description: 'true only if a minimal faithful repair exists' },
    proposed: { type: 'string', description: 'the complete repaired replacement text; empty when repaired is false' },
    note: { type: 'string', description: 'one sentence: what was restored or narrowed, or why no repair is possible' },
  },
  required: ['repaired', 'proposed', 'note'],
}

const FAITH_SCHEMA = { type: 'object',
  required: ['locatable', 'current_matches', 'data_faithful', 'note'],
  properties: { locatable: { type: 'boolean' }, current_matches: { type: 'boolean' },
    data_faithful: { enum: ['pass', 'fail'] }, note: { type: 'string' } } }

// APPLICATION happens in this workflow's own Apply and Verify phases, below.
// The rules it follows, gathered here because they are easy to get wrong:
//   1. Only UNANIMOUS changes that cleared the data-faithfulness gate are applied.
//   2. HIGHEST SCORING FIRST. When several accepted proposals contend for the same
//      target, only one can land, so the best-scoring variant wins — never list
//      order. Prose: grouped by the exact passage being replaced. Structural:
//      grouped by (section, action), since rival takes on one reorganization share
//      both, while different actions on a section may be complementary.
//   3. Everything else — non-unanimous, and rival takes that lost — is reported
//      for review rather than written to the draft.
//   3b. PROSE IS APPLIED BEFORE STRUCTURAL, and the order matters: prose applies
//      by exact match on `current`, while structural changes renumber sections
//      and so rewrite the §N references inside those very passages.
//      Structural-first would silently break every prose anchor containing a
//      section reference. Brittle exact-match step first, judgment step second.
//   4. Prose is applied by exact, unique replacement of the passage. A change
//      whose text no longer matches, or matches twice, is reported rather than
//      placed by judgment — a near match is how a silent corruption enters.
//   5. Structural changes are executed by judgment — see
//      analysis/s10/apply_structural_brief.md, which includes the mandatory
//      hygiene pass (LaTeX label map, moved-material references, stale titles,
//      orphaned pronouns).
//   6. Verify then checks the draft's integrity and repeats the fix/re-check
//      cycle UNTIL A FULL PASS IS CLEAN — one pass is not enough, since a fix
//      can expose the next problem. The checks are stated in the prompt rather
//      than held in a script; there is no standing tooling in this loop.
//   7. Each iteration is committed, so every round is separately revertible.

// ============================== ORCHESTRATION ==============================
// One workflow, every scope. Each scope runs the full pipeline independently and
// concurrently; the workflow's own concurrency cap (min(16, cpus-2)) throttles
// the fan-out, which is what a shell-level job limiter failed to do.

// `preset` re-enters the pipeline at Faithfulness with proposals that were made
// in an earlier run but never judged. Everything downstream — the data gate, the
// ballot, selection — is the same code; only the proposing is skipped.
const runScope = async (sc, preset) => {
  const { id, scope } = sc
  const variants = preset ? [] : variantsFor(scope)
  const SEATS = PANEL
  const jobs = []
  for (const m of SEATS) for (const v of variants) jobs.push({ m, v })

  const raw = preset ? [] : await parallel(jobs.map(({ m, v }) => () =>
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
  const candidates = preset
    ? preset.map(c => ({ ...c, current: c.current_key, support: 1,
                         author_seats: [c.member], author_families: [c.family] }))
    : Object.values(byKey).map((c, i) =>
        ({ ...c, id: `${id}-C${i + 1}`, author_seats: [...c.author_seats], author_families: [...c.author_families] }))
  log(preset
    ? `${id}: ${candidates.length} candidates resumed from saved proposals — judging from Faithfulness`
    : `${id}: ${proposals.length} proposals -> ${candidates.length} candidates`)

  const faiths = await parallel(candidates.map(c => () =>
    agent(FAITH_PROMPT(c), { agentType: 'check-faithfulness', model: FAITH_MODEL, label: `faith:${c.id}`,
                             phase: 'Faithfulness', schema: FAITH_SCHEMA }).catch(() => null)))
  const withFaith = candidates.map((c, i) => {
    const f = faiths[i]
    // current_matches is recorded and reported, but does NOT gate: the applier
    // works from the locus and the quote together rather than matching character
    // by character, so a re-wrapped or slightly stale quote is something it can
    // resolve. Gating on it here would drop changes that are perfectly
    // applicable. What still gates is the data check and locatability.
    const gate = !!f && f.locatable !== false && f.data_faithful === 'pass'
    return { ...c, scope: id, faith: f, faith_gate: gate,
             faith_reason: !f ? 'faith_check_errored' : f.locatable === false ? 'not_locatable'
               : f.data_faithful !== 'pass' ? 'data_changed'
               : null,
             quote_stale: !!f && f.current_matches === false }
  })
  // REPAIR PASS. Only for a data_changed failure on a passage that was
  // locatable: if the checker could not find the text there is nothing to anchor
  // a repair to, and an errored check is not evidence of a fault. A repaired
  // candidate is re-checked through the SAME gate, so a repair that does not
  // actually fix it is dropped exactly as it would have been.
  const repairable = withFaith.filter(c => !c.faith_gate && c.faith_reason === 'data_changed')
  let n_repaired = 0
  if (repairable.length) {
    const fixes = await parallel(repairable.map(c => () =>
      agent(REPAIR_PROMPT(c), { agentType: 'check-faithfulness', model: FAITH_MODEL,
                                label: `repair:${c.id}`, phase: 'Faithfulness', schema: REPAIR_SCHEMA })
        .catch(() => null)))
    const patched = []
    repairable.forEach((c, i) => {
      const f = fixes[i]
      if (f && f.repaired && f.proposed && f.proposed.trim())
        patched.push({ ...c, proposed: f.proposed, repaired: true, repair_note: f.note })
    })
    const rechecks = patched.length ? await parallel(patched.map(c => () =>
      agent(FAITH_PROMPT(c), { agentType: 'check-faithfulness', model: FAITH_MODEL,
                               label: `recheck:${c.id}`, phase: 'Faithfulness', schema: FAITH_SCHEMA })
        .catch(() => null))) : []
    patched.forEach((c, i) => {
      const f = rechecks[i]
      if (!(f && f.locatable !== false && f.data_faithful === 'pass')) return
      const k = withFaith.findIndex(x => x.id === c.id)
      if (k >= 0) {
        withFaith[k] = { ...c, faith: f, faith_gate: true, faith_reason: null,
                         quote_stale: f.current_matches === false }
        n_repaired += 1
      }
    })
    log(`${id}: ${repairable.length} failed the data gate — ${patched.length} repair(s) attempted, ${n_repaired} passed re-check`)
  }

  const survivors = withFaith.filter(c => c.faith_gate)

  const scored = await parallel(survivors.map(cand => async () => {
    const prompt = cand.type === 'structural' ? VOTE_STRUCTURAL(cand) : VOTE_PROSE(cand)
    const ballots = await parallel(SEATS.map(v => () =>
      agent(prompt, { agentType: v.type, model: v.model, label: `vote:${cand.id}:${v.id}`, phase: 'Vote',
                      schema: VOTE_SCHEMA, ...(v.effort ? { effort: v.effort } : {}) })
        // agent() RETURNS NULL on a terminal API error after retries — it does not
        // reject, so .catch below never sees it. Spreading a null yields a ballot
        // with no `keep`, which reads as a vote against and still counts toward n.
        // That silently destroyed unanimity for 47 throttled ballots in iteration 2.
        .then(s => (s && s.keep !== undefined)
          ? { voter: v.id, is_author: cand.author_seats.some(a => String(a).split('/')[0] === v.id), ...s }
          : { voter: v.id, failed: true, limit: false, err: 'agent returned no ballot (null or malformed)' })
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
           n_faith_pass: survivors.length, n_faith_dropped: candidates.length - survivors.length, n_repaired,
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
    clean: { type: 'boolean', description: 'true ONLY if a complete final pass found no issues' },
    fixed: { type: 'array', items: { type: 'string' }, description: 'issues found and fixed this pass' },
    remaining: { type: 'string', description: 'issues still outstanding, or empty when clean' },
  },
  required: ['clean', 'fixed', 'remaining'],
}

const loadSaved = async () => parallel(RESUME.map(path => () =>
  agent(`ROLE: LOAD SAVED RESULT. Mechanical, no judgment.
Read the saved workflow result at \`${path}\` and report its changes.

For each entry in its \`changes\` array report: the id; whether it is prose or
structural; its action and locus; the first 120 characters of its \`current\`
text with runs of whitespace collapsed to single spaces (this is only used to
recognise rival rewrites of the same passage, so it need not be exact beyond
that); its support count; and from its verdict, accepted, keeps, n and composite.

Report the largest \`n\` any change in the file received as seats_max, and the
file's scope id. Do not summarise, judge, or omit entries.`,
        { model: WORKER_MODEL, phase: 'Propose', label: `load:${path.split('/').pop()}`, schema: LOAD_SCHEMA })
    .then(r => r && ({ scope_id: path.split('/').pop().replace(/\.json$/, ''), source: path, seats_max: r.seats_max,
      n_proposals: 0, n_candidates: r.changes.length, n_faith_pass: r.changes.length,
      n_faith_dropped: 0, accepted: r.changes.filter(c => c.accepted).length, self_preference: {},
      changes: r.changes.map(c => ({ id: path.split('/').pop().replace(/\.json$/, '') + '/' + c.id,
        type: c.type, action: c.action, locus: c.locus,
        current: c.current_key, support: c.support || 1, source: path,
        verdict: { accepted: c.accepted, keeps: c.keeps, n: c.n, composite: c.composite } })) }))
    .catch(e => { log(`load failed for ${path}: ${String(e).slice(0, 120)}`); return null })))

const loadCandidates = async () => parallel(RESUME_PROPOSALS.map(path => () =>
  agent(`ROLE: LOAD CANDIDATE MANIFEST. Mechanical, no judgment.
Read the manifest at \`${path}\` and report every row in it.

Each row describes one proposal that was made but never judged. Report all of
its fields: id, scope, type, action, locus, current_key, member, family, and
path. Copy them; do not summarise, judge, reword, or omit any row — an omitted
row is a proposal silently dropped from the whole run.`,
        { model: WORKER_MODEL, phase: 'Propose', label: `manifest:${path.split('/').pop()}`,
          schema: CANDIDATE_SCHEMA })
    .then(r => r && r.candidates && r.candidates.length
      ? { scope_id: r.candidates[0].scope, source: path, candidates: r.candidates }
      : null)
    .catch(e => { log(`manifest load failed for ${path}: ${String(e).slice(0, 120)}`); return null })))

phase('Propose')
log(RESUME
  ? `iteration ${ITER}: resuming from ${RESUME.length} saved scope result(s) — no proposing, straight to Select`
  : RESUME_PROPOSALS
  ? `iteration ${ITER}: resuming ${RESUME_PROPOSALS.length} manifest(s) of unjudged proposals — re-entering at Faithfulness with ${PANEL.length} seats`
  : `iteration ${ITER}, phase ${PHASE}: ${SCOPES.length} scope(s), ${PANEL.length} seats — ${PANEL.map(m => `${m.id}=${m.model}`).join(', ')}`)
let perScope
if (RESUME) {
  perScope = await loadSaved()
} else if (RESUME_PROPOSALS) {
  const loaded = (await loadCandidates()).filter(Boolean)
  log(`resumed ${loaded.reduce((n, g) => n + g.candidates.length, 0)} unjudged proposal(s) across ${loaded.length} scope(s)`)
  perScope = await parallel(loaded.map(g => () =>
    runScope({ id: g.scope_id, scope: g.scope_id }, g.candidates)))
} else {
  perScope = await parallel(SCOPES.map(s => () => runScope(s)))
}
if (RESUME) {
  const thin = perScope.filter(Boolean).filter(r => (r.seats_max || 0) < 2)
  for (const r of thin)
    log(`REFUSING ${r.scope_id} (${r.source}): ballots from ${r.seats_max} seat(s) — unanimity is meaningless on a panel that small`)
  for (const r of thin) perScope[perScope.indexOf(r)] = null
  log(`resumed ${perScope.filter(Boolean).length} saved scope(s) straight into Select`)
}

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

// In resume mode the loaded records carry only enough to decide selection — an
// id, a truncated passage key, the verdict. The full text stays in the saved
// result file, so the applier is pointed at the file and the winning ids rather
// than handed text the workflow never loaded.
const payloadFor = (items, fields) => {
  // Whether the applier is handed text or pointed at files depends on the
  // candidates, not on which resume flag was set: a resumed candidate's text
  // lives on disk and was never loaded, so there is nothing to inline.
  const fileOf = (c) => c.path || c.source
  if (!items.length || !items.every(fileOf)) return JSON.stringify(items.map(fields), null, 1)
  const single = items.every(c => c.path)     // one change per file
  return 'Each is recorded in a file, listed below as\n' +
    (single ? '  <file>  (<locus>)\n\nEach file holds exactly one change: its locus, the\n' +
              'text to replace, the replacement, and the rationale.\n\n'
            : '  <file>  <id in that file>  (<locus>)\n\n' +
              'Take each one\'s text verbatim from its own file. Candidate ids are only\n' +
              'unique within a file — C2 exists in every one of them — so never match an id\n' +
              'without also matching the file it is listed against. Ignore every other entry\n' +
              'in those files: selection has already happened.\n\n') +
    items.map(c => single
      ? '  ' + fileOf(c) + '  (' + c.locus + ')'
      : '  ' + fileOf(c) + '  ' + String(c.id).split('/').pop() + '  (' + c.locus + ')').join('\n')
}

// ============================== APPLY ======================================
// Sequential by necessity. Prose applies by exact match on verbatim `current`
// text; structural renumbering rewrites the §N references those anchors live
// inside, so doing structure first would break every prose anchor.
phase('Apply')
const applyResults = {}

applyResults.prose = await agent(`ROLE: APPLY PROSE.
Apply these ${selection.prose.length} unanimously accepted prose rewrites to \`${DRAFT}\`.

Each replaces a passage. \`current\` is the passage as the proposer quoted it and
\`proposed\` is what should stand in its place. Work from the locus and the quote
together to find the passage the change is actually about, and put the proposed
text there.

The quote may not be word-perfect — it can be re-wrapped, or drawn from a
slightly earlier state of the draft — so judge what it refers to rather than
matching it character by character. What must not move is the content: apply the
change as written, and never adjust a number, a statistic, a sample size, an
interval, or a statement of what was or was not found to make anything fit.

Where you genuinely cannot tell which passage is meant, or the quote could
plausibly mean either of two places, say so and skip it. An honest skip is a
good outcome; a change placed on a guess is not.

Some changes may legitimately fail because an earlier change in this same list
already rewrote overlapping text. That is expected, and is exactly what you
should report rather than repair.

Report as applied ONLY what you actually changed. If the draft already reads the
way a change proposes — the passage is already in its target state, so there is
nothing to replace — that is a skip with the reason "already in the desired
state", not an application. Counting a no-op as done overstates what the run did
and hides a stale proposal.

Return the ids applied, the ids skipped each with its reason, and nothing else.

${payloadFor(selection.prose, c => ({ id: c.id, current: c.current, proposed: c.proposed }))}`,
  { agentType: 'apply-integrator', model: WORKER_MODEL, phase: 'Apply', label: 'apply:prose', schema: APPLY_SCHEMA })

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

${payloadFor(selection.structural, c => ({ id: c.id, locus: c.locus, action: c.action,
   proposed: c.proposed, rationale: c.rationale, composite: (c.verdict || {}).composite,
   dependencies: (c.verdict || {}).dependencies || [] }))}`,
  { agentType: 'apply-integrator', model: WORKER_MODEL, phase: 'Apply', label: 'apply:structural', schema: APPLY_SCHEMA })

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
  { agentType: 'apply-integrator', model: WORKER_MODEL, phase: 'Apply', label: 'apply:figures', schema: APPLY_SCHEMA })

// ============================== VERIFY =====================================
// The checks live in the prompt, not in a standing script (Matthew, 2026-09-02:
// no tooling in the iteration loop — give the model room to do the work). The
// agent re-checks itself until a full pass is clean.
phase('Verify')
const verify = await agent(`ROLE: VERIFY AND FIX.
Changes have just been applied to \`${DRAFT}\`. Check the manuscript's integrity,
fix what is broken, then check again — and keep repeating until a complete pass
finds nothing. One pass is never enough: fixing one problem routinely exposes
the next, which is how a desynchronised LaTeX label map survived a past round.

What has to hold, every pass:

1. Every section reference (\`§N\`, \`§N.M\`) resolves to a heading that exists.
   Footnote definition lines do not count as body text. A few references point
   at other documents (METHODOLOGY, README, analysis scripts) — those are fine,
   and worth saying so rather than "fixing".
2. Every "Appendix X" reference resolves to an appendix that exists.
3. Every footnote used has a definition. One defined but never used is worth a
   note, not a fix.
4. No heading text is duplicated, and no section number is used twice.
5. Every image the draft references exists on disk. A reference to a file that
   was never created is a broken build, and it is the failure this stage most
   exists to catch: a proposal can add a figure reference and pass the data gate
   untouched, because no datum changed, while the file never came into being.
6. Every referenced figure is wired into the LaTeX transform in
   \`analysis/s10/latex/reformat.py\` — it needs a figure-label entry, or it
   renders as a bare image with no float, caption or cross-reference.
7. Every numbered heading and every appendix letter has an entry in that file's
   label maps. A heading missing from them cannot be labelled, so nothing can
   reference it.
8. That file's appendix character ranges still span every appendix letter the
   draft uses. Adding an Appendix E while a range stops at D drops it silently.

Two rules while fixing:
- Never hard-code a section or appendix number to make a reference resolve.
  They are numbered from labels; add or correct the label. A literal "§4.7"
  rots the next time anything moves.
- Never delete a reference to make a check pass, unless its target genuinely
  should not exist.

Report honestly. Set clean=true only if a complete final pass found nothing. If
you cannot get there, set clean=false and say precisely what remains — an exact
account of a residual problem is worth far more than a forced pass, because
everything downstream trusts this report.`,
  { agentType: 'apply-integrator', model: WORKER_MODEL, phase: 'Verify', label: 'verify', schema: VERIFY_SCHEMA })

const clean = !!(verify && verify.clean)
log(clean
  ? 'verify: clean' + ((verify.fixed || []).length ? ' after fixing ' + verify.fixed.length : '')
  : 'VERIFY DID NOT REACH CLEAN — ' + ((verify && verify.remaining) || 'no detail returned'))

return { iteration: ITER, phase: PHASE, scopes: ok.map(r => r.scope_id), totals, selection,
         applied: applyResults, verify, by_scope: ok }
