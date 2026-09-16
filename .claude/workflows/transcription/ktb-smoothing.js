export const meta = {
  name: 'ktb-smoothing',
  description: 'Smooth the King\'s Two Bodies markdown in place: fix inferable OCR garbles, protect the Latin, image consult only when context cannot decide',
  phases: [{ title: 'Smooth', detail: '24 agents: 20 body chunks + 4 notes chunks, editing in place', model: 'opus' }],
}

const MD = '/home/matt/reading/artificial-persons/kantorowicz-1957-kings-two-bodies.md'
const PDF = '/home/matt/reading/artificial-persons/kantorowicz-1957-kings-two-bodies-2016-princeton-classics-full.pdf'
const OUTDIR = '/tmp/claude-1000/-home-matt-performance-commons/aaa6ff40-df04-4f4b-8a9a-fa58d7a4e24b/scratchpad/ktb'

const REPORT = {
  type: 'object',
  properties: {
    span: { type: 'string' },
    edits_made: { type: 'integer' },
    image_consults: { type: 'integer' },
    latin_edits: { type: 'array', items: { type: 'string' }, description: 'every edit that touched Latin/Greek, old -> new, individually' },
    notable_fixes: { type: 'array', items: { type: 'string' }, description: 'up to 8 examples' },
    unresolved: { type: 'array', items: { type: 'string' } },
  },
  required: ['span','edits_made','image_consults','latin_edits','notable_fixes','unresolved'],
}

const COMMON = `You are a careful copy-editor smoothing an OCR-derived markdown transcription
of Kantorowicz's *The King's Two Bodies* (Princeton, 1957; 2016 Classics
edition scan) at ${MD}. Printed-page anchors appear inline as [*N*]; printed
page N is PDF page N+40 in ${PDF} (front matter has [pdf N] anchors and
roman-numeral pagination - for those, find the page by its content near the
pdf number given).

Fix, using the Edit tool with SMALL surgical old_string/new_string
replacements (never rewrite whole paragraphs, never Write the file):
- garbled ENGLISH words whose intended reading is unambiguous from context
- intra-word spacing artifacts ("Q uaestiones" -> "Quaestiones", "th e" ->
  "the") and fused words
- stray OCR debris: orphaned characters, doubled punctuation, running-head
  residue (letter-spaced chapter-title fragments injected mid-text)
- broken quote marks where opening/closing is plainly missing or wrong

HARD RULES:
1. **Latin and Greek are edit-forbidden** unless the garble is provable from
   within the passage itself (e.g. "corpus m ysticum" spacing) or you have
   checked the page image. EVERY edit touching Latin/Greek must be listed
   individually in latin_edits. Never "correct" unfamiliar medieval Latin
   toward classical or English-plausible forms - Kantorowicz quotes medieval
   orthography (e.g. "michi", "nichil", "e" for "ae") that LOOKS wrong and is
   right.
2. Preserve the printed orthography and punctuation style; no modernizing,
   no paraphrase, no reordering, no added or dropped content.
3. Do not touch page anchors [*N*], [pdf N], or headings.
4. Superscript footnote numbers survive fused to their words ("Justice,"64) -
   leave them; they are real reference marks.
5. If a reading is not unambiguous from context, only then consult the scan:
   mkdir -p ${OUTDIR} && pdftoppm -png -r 200 -f <pdfpage> -l <pdfpage> ${PDF} ${OUTDIR}/<yourlabel>
   and Read the PNG. Use sparingly; count every consult. If even the image
   cannot decide, leave as-is and list under unresolved.

Concurrency note: 23 other agents are editing OTHER spans of this file. If an
Edit fails with a stale-file error, re-read your region and retry once; if an
old_string stops matching, skip it and move on.`

// body chunks by printed-page anchor ranges (~27 printed pages each, 1-540 + front matter)
const BODY = [
  ['the file start (title header) through the front matter and Introduction, ending just before anchor [*3*]', 'front'],
  ...[[3,29],[30,56],[57,83],[84,110],[111,137],[138,164],[165,191],[192,218],[219,245],[246,272],[273,299],[300,326],[327,353],[354,380],[381,407],[408,434],[435,461],[462,488],[489,540]].map(([a,b]) => [`from anchor [*${a}*] through the end of printed page ${b}'s body text (stop before the ## Notes section)`, `${a}-${b}`]),
]
// notes chunks by keyed page ranges
const NOTES = [[1,140],[141,280],[281,420],[421,545]].map(([a,b]) =>
  [`ONLY the ## Notes section at the end of the file: entries keyed **[p. ${a}]** through **[p. ${b}]**. These are the printed footnotes - dense citation strings, heavy Latin. Smooth garbled journal/author abbreviations and English connective text; hard rule 1 applies doubly here.`, `notes-${a}-${b}`])

phase('Smooth')
const reports = await parallel([...BODY, ...NOTES].map(([span, label]) => () => agent(
`${COMMON}

Your span: ${span}.

Work through it sequentially and return the structured report (edits_made =
successful Edit calls; span = "${label}").`,
  { label: `smooth:${label}`, phase: 'Smooth', schema: REPORT, model: 'opus', effort: 'medium' }
)))

const ok = reports.filter(Boolean)
log(`${ok.length}/24 done, ${ok.reduce((s,r)=>s+r.edits_made,0)} edits, ${ok.reduce((s,r)=>s+r.image_consults,0)} consults, ${ok.reduce((s,r)=>s+r.latin_edits.length,0)} latin edits`)
return { reports: ok }