export const meta = {
  name: 'dartmouth-ocr-correction',
  description: 'LLM perplexity pass over the Dartmouth markdown: flag OCR-suspect spans, verify against page images, emit corrections',
  phases: [
    { title: 'Flag', detail: '8 agents scan the markdown for OCR-implausible spans', model: 'opus' },
    { title: 'Verify', detail: 'agents check flagged spans against the scan page images', model: 'opus' },
  ],
}

const MD = '/home/matt/reading/artificial-persons/dartmouth-v-woodward-1819.md'
const PDF = '/home/matt/reading/artificial-persons/dartmouth-v-woodward-1819.pdf'
const OUTDIR = '/tmp/claude-1000/-home-matt-performance-commons/aaa6ff40-df04-4f4b-8a9a-fa58d7a4e24b/scratchpad/dartmouth'

const FLAG_SCHEMA = {
  type: 'object',
  properties: {
    flags: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          page: { type: 'integer', description: 'printed page from the nearest preceding [*N*] anchor' },
          context: { type: 'string', description: 'EXACT substring from the file, 40-120 chars, containing the suspect span - must match the file verbatim for later patching' },
          suspect: { type: 'string', description: 'the specific broken token(s) inside context' },
          proposed: { type: 'string', description: 'most likely intended reading by language prior' },
          kind: { type: 'string', description: 'garbled-word | latin | citation | punctuation | sidenote-residue | quote-marks | other' },
          confidence: { type: 'string', description: 'high = certainly broken; check-image = might be genuine 1819 orthography or genuinely ambiguous' },
        },
        required: ['page','context','suspect','proposed','kind','confidence'],
      },
    },
  },
  required: ['flags'],
}

// page ranges per chunk (printed pages)
const RANGES = [[518,542],[543,567],[568,592],[593,617],[618,642],[643,667],[668,691],[692,715]]

phase('Flag')
const flagResults = await parallel(RANGES.map(([a,b], i) => () => agent(
`Read ${MD} - it is a markdown transcription of Trustees of Dartmouth College
v. Woodward, 17 U.S. 518 (1819), derived from 2015-era commercial OCR of the
1819 printing. Printed-page anchors appear as [*N*]. Your span: pages ${a}-${b}
(from anchor [*${a}*] or the file start, through the end of page ${b}'s text;
also cover footnote definitions [^fnNNNx]: whose page number falls in your
range).

Find OCR errors by language-model plausibility. Flag:
- garbled words ("naturaly", "tinto", "gife", broken Latin like "ex meyo motu")
- mangled citations (reporter abbreviations, volume/page numbers that look
  scrambled), broken names
- stray sidenote residue (fragments of "Dartmouth College v. Woodward",
  "1819", column words injected mid-sentence)
- quote-mark damage (missing/doubled/wrong quotation marks around quoted
  charters and speeches)
- impossible punctuation ("of.. ", "; ;", period-comma collisions)

Do NOT flag genuine period orthography: "shew", "chuse", "compleat",
"publick", "farther" (where modern usage says "further"), "recal",
"expence", "-our" spellings, "&c.", capitalization conventions, or long
compound legal sentences. When you cannot tell whether a reading is period
orthography or an OCR break, flag it with confidence "check-image" rather
than guessing. British-vs-modern spelling is never an error.

The context field must be copied EXACTLY from the file (it will be used for
literal string replacement) and must be unique enough to locate. Be
thorough - walk your whole range paragraph by paragraph. Return only the
structured flags.`,
  { label: `flag:${a}-${b}`, phase: 'Flag', schema: FLAG_SCHEMA, model: 'opus', effort: 'medium' }
)))

const flags = flagResults.filter(Boolean).flatMap(r => r.flags)
log(`${flags.length} suspect spans flagged`)

// group flags by printed page, then batch pages into verify jobs
const byPage = {}
for (const f of flags) { (byPage[f.page] = byPage[f.page] || []).push(f) }
const pages = Object.keys(byPage).map(Number).sort((x, y) => x - y)
const BATCHES = []
const NB = Math.min(8, Math.max(1, Math.ceil(pages.length / 12)))
for (let i = 0; i < NB; i++) BATCHES.push(pages.filter((_, j) => j % NB === i))

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          context: { type: 'string' },
          verdict: { type: 'string', description: 'fix | keep | unresolvable' },
          corrected_context: { type: 'string', description: 'the context string with the correction applied, per the page image; empty if verdict != fix' },
          note: { type: 'string' },
        },
        required: ['context','verdict','corrected_context','note'],
      },
    },
  },
  required: ['verdicts'],
}

phase('Verify')
const verifyResults = await parallel(BATCHES.filter(b => b.length).map((pgs, i) => () => agent(
`You are verifying suspected OCR errors in a transcription of Dartmouth v.
Woodward (17 U.S. 518) against the authoritative page images of the Library
of Congress scan ${PDF}. Printed page N = PDF page N-517.

For each printed page below: rasterize it
  (mkdir -p ${OUTDIR} && pdftoppm -png -r 200 -f <N-517> -l <N-517> ${PDF} ${OUTDIR}/vb${i})
then Read the PNG and check each flagged span against what is actually
printed. Return one verdict per flag:
- "fix": the transcription is wrong; corrected_context = the flag's context
  string with ONLY the erroneous part corrected to match the printed page
  exactly (preserve 1819 orthography as printed - if the page says
  "farther", keep "farther").
- "keep": the transcription already matches the print (the flag was a false
  alarm / genuine period spelling).
- "unresolvable": the print itself is illegible at that spot.
Do not rewrite anything beyond the flagged error. Delete your PNGs when done.

Flags by page:
${JSON.stringify(pgs.map(p => ({ page: p, flags: byPage[p].map(f => ({ context: f.context, suspect: f.suspect, proposed: f.proposed })) })), null, 1)}`,
  { label: `verify:batch${i}`, phase: 'Verify', schema: VERIFY_SCHEMA, model: 'opus', effort: 'medium' }
)))

const verdicts = verifyResults.filter(Boolean).flatMap(r => r.verdicts)
log(`${verdicts.length} verdicts returned`)
return { flagCount: flags.length, verdicts, flags }