export const meta = {
  name: 'acquire-sources',
  description: 'Acquire scholarly sources per reading/00-FETCH-METHODOLOGY.md: identity-first, three escalating fetch attempts plus an adversarial verdict pass before any unavailable verdict, four-state ledger out',
  whenToUse: 'Any time works need acquiring into a reading directory. args = {targets: [{want, hint?, directory, filename?}, ...]} — want is the fullest citation/handle known, hint any DOI/URL/lead, directory an absolute path, filename optional (agent names honestly if omitted).',
  phases: [
    { title: 'Resolve', detail: 'identity (DOI + citation) for every target; no fetch before identity' },
    { title: 'Fetch', detail: 'up to three escalating attempts per target, each skipping exhausted angles by name' },
    { title: 'Verdict', detail: 'adversarial confirmation of every non-fetch; CHECK-FAILED items get a fourth attempt' },
    { title: 'Ledger', detail: 'verify files on disk, compile the four-state ledger' },
  ],
}

// ---------------------------------------------------------------- args
if (!args || !Array.isArray(args.targets) || args.targets.length === 0) {
  throw new Error(
    'acquire-sources needs args = {targets: [{want, hint?, directory, filename?}, ...]}\n' +
    '  want:      fullest known citation/handle (free text)\n' +
    '  hint:      optional DOI, URL, or other lead\n' +
    '  directory: absolute path to save into (e.g. /home/matt/reading/<dir>)\n' +
    '  filename:  optional; omit to let the agent name honestly (<author>-<year>-<slug>.pdf)'
  )
}
const TARGETS = args.targets

const METHOD = `FIRST ACTION: read /home/matt/performance_commons/reading/00-FETCH-METHODOLOGY.md
in full — it is the contract for this job. Binding rules regardless of anything
else: never pirate (no libgen/annas-archive/scribd-premium/dokumen.pub); NEVER
automate past a CAPTCHA (that is the stop line — record located_needs_human with
the exact URL and action instead); never construct/pattern-guess IDs — resolve
them; verify every saved file (%PDF magic + early-page title/author match
against the RESOLVED identity) and record the VERSION (VoR / accepted /
preprint / WP / rendered-HTML with source+date stamped on p.1); filenames tell
the truth about what the file actually is.`

const RESOLVE_SCHEMA = { type: 'object', required: ['resolved', 'citation', 'notes'], properties: {
  resolved: { type: 'boolean' },
  doi: { type: 'string', description: 'resolved DOI, or "" if the work genuinely has none (books, gray lit)' },
  citation: { type: 'string', description: 'full bibliographic citation as resolved from Crossref/OpenAlex/publisher — never from memory' },
  year: { type: 'integer' },
  no_doi_class: { type: 'string', description: 'if doi is "": book|report|gray|pre-doi-article|unknown' },
  notes: { type: 'string', description: 'how identity was resolved, or why it could not be' },
} }

const ATTEMPT_SCHEMA = { type: 'object', required: ['status', 'tried', 'notes'], properties: {
  status: { type: 'string', enum: ['fetched', 'located_needs_human', 'not_yet', 'check_failed'] },
  file: { type: 'string', description: 'absolute path saved, or ""' },
  version: { type: 'string', description: 'VoR / accepted / preprint / WP / rendered / scan — required when fetched' },
  human_action: { type: 'string', description: 'for located_needs_human: the exact URL + action a human should take' },
  tried: { type: 'array', items: { type: 'string' }, description: 'every angle attempted THIS attempt, named specifically enough that the next attempt can skip it' },
  notes: { type: 'string' },
} }

const VERDICT_SCHEMA = { type: 'object', required: ['state', 'basis'], properties: {
  state: { type: 'string', enum: ['checked_and_absent', 'located_needs_human', 'check_failed', 'unresolved_identity'] },
  human_action: { type: 'string' },
  basis: { type: 'string', description: 'which indexes/routes confirm the verdict, checked independently in THIS pass' },
} }

const esc = (t) => JSON.stringify(t)

// ---------------------------------------------------------------- stages
const resolveStage = (t, i) => agent(`${METHOD}

PHASE: IDENTITY RESOLUTION ONLY — do not fetch anything yet.
Target ${i + 1}: ${esc(t.want)}
Hint: ${esc(t.hint || '')}

Resolve this to a full citation + DOI using Crossref REST (unmetered),
OpenAlex, or the publisher's own records. If the hint is a URL, reverse-resolve
it (publisher URLs encode journal/volume/page; JSTOR stables are 10.2307/<id>).
If the work predates DOIs or is a book/report, say so in no_doi_class and give
the fullest citation the records support. resolved=false ONLY if the work's
identity genuinely cannot be pinned down — say exactly what blocked it.`,
  { label: `resolve:${i + 1}`, phase: 'Resolve', schema: RESOLVE_SCHEMA, effort: 'low' })

const attemptStage = (round, prompt_extra) => (prev, t, i) => {
  // prev = {ident, attempts:[...]} threaded state; skip if done
  if (prev.done) return prev
  if (!prev.ident.resolved && round === 1) {
    prev.verdict = { state: 'unresolved_identity', basis: prev.ident.notes, human_action: '' }
    prev.done = true
    return prev
  }
  const triedSoFar = prev.attempts.flatMap(a => a.tried || [])
  return agent(`${METHOD}

PHASE: FETCH — attempt ${round} of 3 for this target.
RESOLVED IDENTITY (fetch THIS, verify against THIS): ${esc(prev.ident.citation)}
DOI: ${esc(prev.ident.doi || '(none — ' + (prev.ident.no_doi_class || 'no-doi') + ')')}
Save into: ${t.directory}/ ${t.filename ? 'as ' + t.filename : '(name honestly: <author>-<year>-<slug>.pdf)'}
Check the directory first — if a file for this work already exists, verify it and report fetched.

ANGLES ALREADY EXHAUSTED in earlier attempts — do NOT repeat these:
${triedSoFar.length ? triedSoFar.map(x => '  - ' + x).join('\n') : '  (none yet)'}

${prompt_extra}

Report status honestly: fetched (with file+version) / located_needs_human (with
the exact action) / check_failed (an index or route was rate-limited or down —
name it; this is NOT a negative) / not_yet (angles exhausted this round, none
succeeded). List every angle you tried, named specifically.`,
    { label: `fetch${round}:${i + 1}`, phase: 'Fetch', schema: ATTEMPT_SCHEMA })
    .then(a => {
      prev.attempts.push(a || { status: 'check_failed', tried: [], notes: 'agent died' })
      if (a && a.status === 'fetched') { prev.done = true; prev.fetched = a }
      if (a && a.status === 'located_needs_human' && round === 3) {
        prev.verdict = { state: 'located_needs_human', human_action: a.human_action || a.notes, basis: 'fetch attempts' }
        prev.done = true
      }
      return prev
    })
}

const ATTEMPT_FOCUS = {
  1: `THIS ROUND'S LADDER (methodology steps 2–3): Unpaywall v2 by DOI; OpenAlex
locations[] (repository copies, pdf_url); Semantic Scholar; then direct fetch of
whatever they surface (curl w/ browser UA first). Distinguish checked-and-absent
from check-failed — a 429 means status check_failed, not not_yet.`,
  2: `THIS ROUND'S LADDER (methodology steps 4–6): author-side routes —
institutional repository guessed from affiliations, personal sites live and via
Wayback CDX, academia.edu asset-scrape; aggregators/mirrors — national OJS
hosts, Europe PMC render, DSpace/Omeka bitstreams, govinfo, IA serials
microfilm (check real coverage); anthology/reprint route via Google Books
SearchWithinVolume with negative controls, IA loans API for real borrowability.`,
  3: `THIS ROUND'S LADDER (methodology step 7, the browser-hardness ladder):
headless Firefox under Playwright (~/.venvs/pw — clears Cloudflare where
Chromium fails); warmed sessions; Wayback Save-Page-Now for IP-scoped WAF
blocks; response sniffing with service workers blocked for viewer-only
platforms. Plus any creative legitimate angle the first two rounds suggest.
Remember the stop line: a CAPTCHA means located_needs_human, not defeat-it.`,
}

phase('Resolve')
const results = await pipeline(
  TARGETS,
  (t, _t, i) => resolveStage(t, i).then(ident => ({ ident: ident || { resolved: false, citation: t.want, notes: 'resolver died' }, attempts: [], done: false })),
  attemptStage(1, ATTEMPT_FOCUS[1]),
  attemptStage(2, ATTEMPT_FOCUS[2]),
  attemptStage(3, ATTEMPT_FOCUS[3]),
  // adversarial verdict for anything still not fetched and not already verdicted
  (prev, t, i) => {
    if (prev.done && !prev.fetched) return prev            // verdicted earlier
    if (prev.fetched) return prev
    return agent(`${METHOD}

PHASE: VERDICT — three fetch attempts failed for:
${esc(prev.ident.citation)}  (DOI: ${esc(prev.ident.doi || 'none')})

The attempt ledger (do not repeat these angles; audit them):
${JSON.stringify(prev.attempts.map(a => ({ status: a.status, tried: a.tried, notes: (a.notes || '').slice(0, 300) })), null, 1)}

Your job is ADVERSARIAL CONFIRMATION of the negative, not a fourth fetch:
(1) independently re-check Unpaywall + OpenAlex + Semantic Scholar NOW — if any
was rate-limited during the attempts, this is where that gets caught;
(2) audit the ledger for an angle the methodology requires that no attempt ran;
(3) classify: checked_and_absent (name the indexes confirming, in basis) /
located_needs_human (the exact cheapest action: JSTOR/ILL/purchase/borrow with
verified IDs) / check_failed (some check STILL cannot be completed — name it).`,
      { label: `verdict:${i + 1}`, phase: 'Verdict', schema: VERDICT_SCHEMA, effort: 'high' })
      .then(v => { prev.verdict = v || { state: 'check_failed', basis: 'verdict agent died' }; return prev })
  }
)

// CHECK-FAILED items earn a fourth attempt + re-verdict (rate limits reset)
phase('Verdict')
const retryIdx = results.map((r, i) => (r && !r.fetched && r.verdict && r.verdict.state === 'check_failed') ? i : -1).filter(i => i >= 0)
log(`${retryIdx.length} check-failed target(s) get a fourth attempt`)
for (const i of retryIdx) {
  const prev = results[i]; prev.done = false
  await attemptStage(4, `FOURTH ATTEMPT — earlier rounds hit infrastructure failures (rate limits /
outages), which are not negatives. Re-run the failed checks named in the ledger
first, then any route they unlock. ${ATTEMPT_FOCUS[1]}`)(prev, TARGETS[i], i)
  if (!prev.fetched && !prev.verdict) prev.verdict = { state: 'check_failed', basis: 'still failing after retry — human retry later', human_action: 'retry when indexes recover' }
}

phase('Ledger')
const ledger = await agent(`${METHOD}

PHASE: LEDGER. Verify and compile. For every FETCHED file below, run the checks
yourself in bash: %PDF magic bytes, pdftotext of page 1–2, title/author match
against the resolved citation; flag any mismatch as a FAILED verification.
Then return a compact markdown ledger: one section per terminal state
(FETCHED with file+version / LOCATED-NEEDS-HUMAN with actions / CHECKED-AND-
ABSENT with basis / CHECK-FAILED retry queue / UNRESOLVED), one line per target.

TARGETS AND OUTCOMES:
${JSON.stringify(results.map((r, i) => ({
  want: TARGETS[i].want, directory: TARGETS[i].directory,
  citation: r.ident.citation, doi: r.ident.doi || '',
  fetched: r.fetched ? { file: r.fetched.file, version: r.fetched.version } : null,
  verdict: r.verdict || null,
  attempts: r.attempts.length,
})), null, 1)}`,
  { label: 'ledger', phase: 'Ledger', effort: 'low' })

return { ledger, results: results.map((r, i) => ({
  want: TARGETS[i].want,
  state: r.fetched ? 'FETCHED' : (r.verdict ? r.verdict.state.toUpperCase() : 'UNKNOWN'),
  file: r.fetched ? r.fetched.file : '',
  version: r.fetched ? r.fetched.version : '',
  human_action: r.verdict ? (r.verdict.human_action || '') : '',
  attempts: r.attempts.length,
})) }
