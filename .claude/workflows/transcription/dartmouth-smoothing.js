export const meta = {
  name: 'dartmouth-smoothing',
  description: 'Opus agents smooth the Dartmouth markdown in place: fix inferable OCR garbles, image consult only when context cannot decide',
  phases: [{ title: 'Smooth', detail: '14 agents, ~14 printed pages each, editing in place', model: 'opus' }],
}

const MD = '/home/matt/reading/artificial-persons/dartmouth-v-woodward-1819.md'
const PDF = '/home/matt/reading/artificial-persons/dartmouth-v-woodward-1819.pdf'
const OUTDIR = '/tmp/claude-1000/-home-matt-performance-commons/aaa6ff40-df04-4f4b-8a9a-fa58d7a4e24b/scratchpad/dartmouth'

const REPORT = {
  type: 'object',
  properties: {
    pages: { type: 'string' },
    edits_made: { type: 'integer' },
    image_consults: { type: 'integer', description: 'how many times you rasterized/read a page image' },
    notable_fixes: { type: 'array', items: { type: 'string' }, description: 'up to 10 examples, old -> new' },
    unresolved: { type: 'array', items: { type: 'string' }, description: 'spans left as-is because neither context nor image could decide' },
  },
  required: ['pages','edits_made','image_consults','notable_fixes','unresolved'],
}

// printed-page ranges, ~14 pages each over 519-715; last chunk also owns the Notes section
const RANGES = [[519,532],[533,546],[547,560],[561,574],[575,588],[589,602],[603,616],[617,630],[631,644],[645,658],[659,672],[673,686],[687,700],[701,715]]

phase('Smooth')
const reports = await parallel(RANGES.map(([a,b], i) => () => agent(
`You are a careful copy-editor smoothing an OCR-derived transcription of
Trustees of Dartmouth College v. Woodward, 17 U.S. 518 (1819), in
${MD}. Printed-page anchors appear inline as [*N*]. Your span: from anchor
[*${a}*] (or the file start if ${a}==519) through the end of page ${b}'s
text${b===715 ? ", PLUS the '## Notes' section at the end of the file (its entries are keyed fn<page><letter> — smooth the garbled citation strings there too)" : ""}.

Goal: make the text READ CLEANLY while staying faithful to the 1819
printing. The owner's two complaints: nonexistent words, and debris that
breaks the flow.

Work through your span paragraph by paragraph and fix, using the Edit tool
with SMALL, surgical old_string/new_string replacements (never rewrite a
whole paragraph, never Write the file):
- nonexistent/garbled words whose intended reading is unambiguous from
  context ("comínon" -> "common", "th'e" -> "the", broken Latin like "ex
  meyo motu" -> "ex mero motu", scrambled citation abbreviations)
- stray OCR debris: orphaned single characters, doubled punctuation,
  spaced-out l e t t e r s, sidenote residue (fragments of "Dartmouth",
  "College", "Woodward", "1819" injected mid-sentence)
- broken quote marks around quoted charters/speeches where the opening or
  closing mark is plainly missing or wrong
- words split by a spurious space or fused together

STRICT limits:
- Preserve genuine 1819 orthography exactly: "shew", "chuse", "compleat",
  "expence", "recal", "farther", "-our" spellings, "&c.", archaic
  capitalization and comma-heavy punctuation. Modernizing is corruption.
- Never paraphrase, reorder, drop, or add content. Fidelity outranks flow.
- Do not touch page anchors [*N*] or footnote markers [^fnNNNx].
- If a reading is NOT unambiguous from context, only then consult the scan:
  printed page N = PDF page N-517; rasterize just that page
  (mkdir -p ${OUTDIR} && pdftoppm -png -r 200 -f <N-517> -l <N-517> ${PDF} ${OUTDIR}/sm${i})
  and Read the PNG. Use this sparingly — count every consult. If even the
  image cannot decide, leave the text as-is and list the span under
  unresolved.

Return the structured report (edits_made = number of Edit calls that
succeeded).`,
  { label: `smooth:${a}-${b}`, phase: 'Smooth', schema: REPORT, model: 'opus', effort: 'medium' }
)))

const ok = reports.filter(Boolean)
log(`${ok.length}/14 chunks done, ${ok.reduce((s,r)=>s+r.edits_made,0)} edits, ${ok.reduce((s,r)=>s+r.image_consults,0)} image consults`)
return { reports: ok }