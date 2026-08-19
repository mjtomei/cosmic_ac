export const meta = {
  name: 'acquire-sources',
  description: 'Acquire scholarly sources per reading/00-FETCH-METHODOLOGY.md: identity-first, then three INDEPENDENT full-methodology fetch attempts per target (varied emphasis, no shared state); unavailable only when all three complete empty with no infrastructure failure',
  whenToUse: 'Any time works need acquiring into a reading directory. args = {targets: [{want, hint?, directory, filename?}, ...]} — want is the fullest citation/handle known, hint any DOI/URL/lead, directory an absolute path, filename optional (agent names honestly if omitted).',
  phases: [
    { title: 'Resolve', detail: 'identity (DOI + citation) for every target; no fetch before identity' },
    { title: 'Fetch', detail: 'three independent attempts per target, each with the complete source ladder, differently ordered' },
    { title: 'Merge', detail: 'verify staged candidates, install the best version, derive the state' },
    { title: 'Ledger', detail: 'final verification on disk, four-state ledger out' },
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
const MODEL = args.model || 'opus'
const EFFORT = args.effort || 'medium'

const METHOD = `FIRST ACTION: read /home/matt/performance_commons/reading/00-FETCH-METHODOLOGY.md
in full — it is the contract for this job. Binding rules regardless of anything
else: never pirate (no libgen/annas-archive/scribd-premium/dokumen.pub); NEVER
automate past a CAPTCHA (that is the stop line — record located_needs_human with
the exact URL and action instead); never construct/pattern-guess IDs — resolve
them; verify every saved file (%PDF magic + early-page title/author match
against the RESOLVED identity) and record the VERSION (VoR / accepted /
preprint / WP / rendered-HTML with source+date stamped on p.1); filenames tell
the truth about what the file actually is. ANY LEGITIMATE VERSION IS A SUCCESS:
a working paper, accepted manuscript, or preprint carrying the work's substance
counts as fetched — do not report located_needs_human for a paywalled VoR when
an earlier version is obtainable; fetch the version, record what it is, and
note the published citation so pagination is never cross-attributed. Prefer VoR
when both are reachable (the merge stage picks the best), but never treat
version preference as a reason to come home empty.`

// The complete source ladder appears in EVERY attempt; only order and emphasis
// vary, so the three attempts are independent redundant passes, not slices.
const LADDER = {
  indexes: `OA indexes by DOI: Unpaywall v2; OpenAlex locations[] (repository copies, pdf_url); Semantic Scholar. Then direct fetch of whatever they surface (curl w/ browser UA). A 429/quota-out is check_failed, never a negative.`,
  author: `author-side routes: institutional repositories guessed from affiliations (LSE eprints, DASH, eScholarship, DiVA, PURE, ORA...); personal sites live AND via Wayback CDX (dead pages often survive as id_ captures); academia.edu asset-scrape (page images at attachments.academia-assets.com rebuilt into a PDF).`,
  aggregators: `aggregators and mirrors: national OJS hosts (tidsskrift.dk, RACO.cat, Dialnet, redalyc/scielo); Europe PMC render endpoint; DSpace/Omeka bitstream APIs; lawcat-style catalogs; govinfo for anything a committee ever printed; IA serials microfilm (sim_<journal>_<year> — check real coverage first).`,
  anthology: `anthology/reprint route for pre-1990 classics: Google Books SearchWithinVolume on a distinctive phrase to locate carrying volumes (negative-control the scan's index health); IA loans API for real borrowability, report identifiers.`,
  browser: `browser-hardness ladder: headless Firefox under Playwright (~/.venvs/pw — clears Cloudflare where Chromium fails); warmed sessions; Wayback Save-Page-Now (archive.org's egress beats IP-scoped WAF blocks); response sniffing with service workers blocked for viewer-only platforms. A CAPTCHA is the stop line: located_needs_human.`,
}

// Three independent framings of the same complete kit — order and opening
// stance differ so the passes diversify rather than mirror each other.
const VARIANTS = [
  `You are the FIRST of three independent hunters; the others' work is invisible
to you — assume nothing has been tried. Work the ladder in this order, but use
your judgment about where this particular work is most likely to surface:
1) ${LADDER.indexes}
2) ${LADDER.author}
3) ${LADDER.aggregators}
4) ${LADDER.anthology}
5) ${LADDER.browser}`,
  `You are the SECOND of three independent hunters; the others' work is invisible
to you — assume nothing has been tried. Start from the people, not the indexes:
authors keep copies of their own work. Order for this pass:
1) ${LADDER.author}
2) ${LADDER.anthology}
3) ${LADDER.aggregators}
4) ${LADDER.browser}
5) ${LADDER.indexes} (run these even if late — they catch what browsing missed.)`,
  `You are the THIRD of three independent hunters; the others' work is invisible
to you — assume nothing has been tried. Start from the infrastructure others
skip: mirrors, national aggregators, government reprints, and the hard-browser
routes; finish on the standard indexes as a cross-check. Order for this pass:
1) ${LADDER.aggregators}
2) ${LADDER.browser}
3) ${LADDER.anthology}
4) ${LADDER.indexes}
5) ${LADDER.author}`,
]

const RESOLVE_SCHEMA = { type: 'object', required: ['resolved', 'citation', 'notes'], properties: {
  resolved: { type: 'boolean' },
  doi: { type: 'string', description: 'resolved DOI, or "" if the work genuinely has none (books, gray lit)' },
  citation: { type: 'string', description: 'full bibliographic citation as resolved from Crossref/OpenAlex/publisher — never from memory' },
  year: { type: 'integer' },
  no_doi_class: { type: 'string', description: 'if doi is "": book|report|gray|pre-doi-article|unknown' },
  notes: { type: 'string', description: 'how identity was resolved, or why it could not be' },
} }

const ATTEMPT_SCHEMA = { type: 'object', required: ['status', 'notes'], properties: {
  status: { type: 'string', enum: ['fetched', 'located_needs_human', 'nothing', 'check_failed'] },
  file: { type: 'string', description: 'absolute path of the STAGED file, or ""' },
  version: { type: 'string', description: 'VoR / accepted / preprint / WP / rendered / scan — required when fetched' },
  human_action: { type: 'string', description: 'for located_needs_human: the exact URL + action a human should take, with verified IDs' },
  checked_absent_basis: { type: 'string', description: 'for nothing: which indexes/routes confirmed absence in THIS pass' },
  notes: { type: 'string' },
} }

const esc = (t) => JSON.stringify(t)
const VRANK = (v) => { const s = (v || '').toLowerCase()
  if (s.includes('vor') || s.includes('record') || s.includes('publisher')) return 5
  if (s.includes('accepted')) return 4
  if (s.includes('preprint') || s.includes('wp') || s.includes('working')) return 3
  if (s.includes('scan')) return 2
  return 1 }

const attemptOnce = (t, i, ident, n) => agent(`${METHOD}

PHASE: FETCH — independent attempt ${n + 1} of 3.
${VARIANTS[n % VARIANTS.length]}

RESOLVED IDENTITY (fetch THIS, verify against THIS): ${esc(ident.citation)}
DOI: ${esc(ident.doi || '(none — ' + (ident.no_doi_class || 'no-doi') + ')')}
Hint from the requester: ${esc(t.hint || '')}

STAGING (yours alone — do not write anywhere else): save your candidate to
${t.directory}/.acquire-staging/t${i}-a${n}/ ${t.filename ? ('as ' + t.filename) : '(name honestly: <author>-<year>-<slug>.pdf)'}
First check ${t.directory}/ itself — if a file for this work already exists
there, verify it against the identity and report fetched with that path.

Report honestly: fetched (file+version) / located_needs_human (exact action,
verified IDs) / nothing (state in checked_absent_basis which indexes and routes
you confirmed absence on) / check_failed (an index or route was rate-limited or
down — name it; infrastructure failure is NOT a negative).`,
  { label: `fetch:t${i + 1}a${n + 1}`, phase: 'Fetch', schema: ATTEMPT_SCHEMA, model: MODEL, effort: EFFORT })

const mergeState = (attempts) => {
  const ok = attempts.filter(Boolean)
  const fetched = ok.filter(a => a.status === 'fetched' && a.file)
  if (fetched.length) return { state: 'FETCHED', best: fetched.sort((a, b) => VRANK(b.version) - VRANK(a.version))[0], fetchedAll: fetched }
  const human = ok.filter(a => a.status === 'located_needs_human')
  if (human.length) return { state: 'LOCATED_NEEDS_HUMAN', human_action: human.map(h => h.human_action).filter(Boolean).join(' | ') }
  const failed = ok.filter(a => a.status === 'check_failed')
  if (failed.length || ok.length < 3) return { state: 'CHECK_FAILED', basis: failed.map(f => f.notes).join('; ') || 'attempt(s) died' }
  return { state: 'CHECKED_AND_ABSENT', basis: ok.map(a => a.checked_absent_basis || a.notes).join(' | ') }
}

phase('Resolve')
const results = await pipeline(
  TARGETS,
  (t, _t, i) => agent(`${METHOD}

PHASE: IDENTITY RESOLUTION ONLY — do not fetch anything yet.
Target ${i + 1}: ${esc(t.want)}
Hint: ${esc(t.hint || '')}

Resolve to a full citation + DOI via Crossref REST (unmetered), OpenAlex, or
the publisher's records. If the hint is a URL, reverse-resolve it (publisher
URLs encode journal/volume/page; JSTOR stables are 10.2307/<id>). Books and
pre-DOI works: fullest citation the records support + no_doi_class.
resolved=false ONLY if identity genuinely cannot be pinned down — say what blocked it.`,
    { label: `resolve:${i + 1}`, phase: 'Resolve', schema: RESOLVE_SCHEMA, model: MODEL, effort: EFFORT })
    .then(ident => ({ ident: ident || { resolved: false, citation: t.want, notes: 'resolver died' } })),

  // three INDEPENDENT attempts, concurrently, no shared state between them
  (prev, t, i) => {
    if (!prev.ident.resolved) { prev.merged = { state: 'UNRESOLVED', basis: prev.ident.notes }; return prev }
    return parallel([0, 1, 2].map(n => () => attemptOnce(t, i, prev.ident, n)))
      .then(attempts => { prev.attempts = attempts; prev.merged = mergeState(attempts); return prev })
  },

  // check_failed earns one more independent pass (infrastructure failures reset)
  (prev, t, i) => {
    if (!prev.merged || prev.merged.state !== 'CHECK_FAILED') return prev
    return attemptOnce(t, i, prev.ident, (prev.attempts || []).length % 3)
      .then(a => {
        prev.attempts = [...(prev.attempts || []), a]
        const re = mergeState(prev.attempts)
        // absence still requires 3 clean empty passes; keep CHECK_FAILED otherwise
        prev.merged = (re.state === 'CHECKED_AND_ABSENT' &&
          (prev.attempts.filter(Boolean).filter(x => x.status === 'nothing').length < 3))
          ? { state: 'CHECK_FAILED', basis: 're-attempt clean but under 3 empty passes; retry later' } : re
        return prev
      })
  },

  // merge/install: verify staged candidates, install best, clean staging
  (prev, t, i) => {
    if (!prev.merged || prev.merged.state !== 'FETCHED') return prev
    const cands = prev.merged.fetchedAll.map(f => ({ file: f.file, version: f.version }))
    return agent(`${METHOD}

PHASE: MERGE for one target. Candidates staged by independent hunters for:
${esc(prev.ident.citation)}
${JSON.stringify(cands, null, 1)}

In bash: verify each candidate (%PDF magic; pdftotext p.1-2 matches the
resolved identity). Install the BEST verified version (VoR > accepted >
preprint/WP > rendered > scan; if tied, larger/cleaner file) at its final home
in ${t.directory}/ ${t.filename ? ('as ' + t.filename) : '(honest <author>-<year>-<slug>.pdf name)'} —
unless an already-verified copy sat in the directory before this run, in which
case keep it and say so. Then delete ${t.directory}/.acquire-staging/t${i}-* .
Report the installed path + version + which candidates failed verification.`,
      { label: `merge:t${i + 1}`, phase: 'Merge', model: MODEL, effort: EFFORT })
      .then(m => { prev.installed = m; return prev })
  }
)

phase('Ledger')
const ledger = await agent(`${METHOD}

PHASE: LEDGER. In bash, spot-verify every installed file below (%PDF + p.1
title match), confirm no .acquire-staging directories remain under the target
directories (clean any stragglers), then return a compact markdown ledger, one
section per terminal state (FETCHED with file+version / LOCATED-NEEDS-HUMAN
with actions / CHECKED-AND-ABSENT with basis / CHECK-FAILED retry queue /
UNRESOLVED), one line per target.

OUTCOMES:
${JSON.stringify(results.map((r, i) => ({
  want: TARGETS[i].want, directory: TARGETS[i].directory,
  citation: r.ident.citation, doi: r.ident.doi || '',
  state: r.merged ? r.merged.state : 'UNKNOWN',
  installed: r.installed ? String(r.installed).slice(0, 400) : '',
  human_action: r.merged ? (r.merged.human_action || '') : '',
  basis: r.merged ? (r.merged.basis || '') : '',
  attempts: (r.attempts || []).length,
})), null, 1)}`,
  { label: 'ledger', phase: 'Ledger', model: MODEL, effort: EFFORT })

return { ledger, results: results.map((r, i) => ({
  want: TARGETS[i].want,
  state: r.merged ? r.merged.state : 'UNKNOWN',
  human_action: r.merged ? (r.merged.human_action || '') : '',
  attempts: (r.attempts || []).length,
})) }
