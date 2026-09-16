export const meta = {
  name: 'ktb-translations',
  description: 'Add marked English translations in parentheses after non-English text in the KTB and Dartmouth markdowns',
  phases: [{ title: 'Translate', detail: '24 KTB chunks + 1 Dartmouth agent, inserting (tr.: ...) glosses in place', model: 'opus' }],
}

const KTB = '/home/matt/reading/artificial-persons/kantorowicz-1957-kings-two-bodies.md'
const DART = '/home/matt/reading/artificial-persons/dartmouth-v-woodward-1819.md'

const REPORT = {
  type: 'object',
  properties: {
    span: { type: 'string' },
    translations_added: { type: 'integer' },
    skipped_already_translated: { type: 'integer', description: 'spans skipped because the text already translates or closely paraphrases them nearby' },
    uncertain: { type: 'array', items: { type: 'string' }, description: 'glosses marked (tr. uncert.: ...) because the source reading or sense is doubtful' },
    notes: { type: 'string' },
  },
  required: ['span','translations_added','skipped_already_translated','uncertain','notes'],
}

const RULES = `Insert English glosses for non-English text, editing in place with the
Edit tool (small old_string/new_string replacements; never rewrite paragraphs,
never Write the file).

Format: immediately after the non-English span (after its closing italic
marker or quotation mark), insert a space and "(tr.: <translation>)". The
marker "tr.:" is mandatory — these glosses are OUR additions and must never
be mistakable for the printed text. If the source reading or sense is
genuinely doubtful, use "(tr. uncert.: <best rendering>)" and list it in the
report.

What to gloss:
- Quoted or run-in Latin, Greek, German, French, Italian, and Old French
  CONTENT — phrases, clauses, whole quoted passages (for long passages one
  faithful, compact rendering of the whole).
- Technical terms and mottoes on their FIRST occurrence in your span only
  (e.g. corpus mysticum, dignitas non moritur, rex qui nunquam moritur) —
  do not re-gloss every recurrence.

What NOT to touch:
- The non-English text itself — never alter, "correct," or re-punctuate it
  in this pass.
- Spans the author already translates or closely paraphrases in the adjacent
  sentence (Kantorowicz constantly does this; check before glossing — count
  these as skipped_already_translated).
- Bibliographic titles appearing only as citations (journal names, book
  titles in the notes) — gloss a title only where its meaning is being
  discussed in the prose.
- Proper names, and archaic/legal ENGLISH (law-French terms so absorbed into
  English legal usage that translation is noise — quo warranto, nunc pro
  tunc — gloss these only on first occurrence in your span, briefly).
- Page anchors, footnote markers, headings.

Medieval Latin caution: translate the medieval sense, not a classicizing
correction (michi = mihi, e for ae, etc.); where Kantorowicz's own gloss
exists nearby, defer to his sense.`

const RANGES = [[3,29],[30,56],[57,83],[84,110],[111,137],[138,164],[165,191],[192,218],[219,245],[246,272],[273,299],[300,326],[327,353],[354,380],[381,407],[408,434],[435,461],[462,488],[489,540]]
const JOBS = [
  [`the front matter of ${KTB}: from the file start through the front matter and Introduction, ending just before anchor [*3*]`, 'ktb-front', KTB],
  ...RANGES.map(([a,b]) => [`${KTB}, from anchor [*${a}*] through the end of printed page ${b}'s body text (stop before the ## Notes section)`, `ktb-${a}-${b}`, KTB]),
  ...[[1,140],[141,280],[281,420],[421,545]].map(([a,b]) => [`ONLY the ## Notes section at the end of ${KTB}: entries keyed **[p. ${a}]** through **[p. ${b}]**. These are dense footnotes: gloss quoted Latin/German/French passages, skip citation-only titles.`, `ktb-notes-${a}-${b}`, KTB]),
  [`the ENTIRE file ${DART} (Trustees of Dartmouth College v. Woodward, 1819 — its non-English content is sparse: scattered Latin and law-French phrases in the arguments, opinions, and Notes section)`, 'dartmouth', DART],
]

phase('Translate')
const reports = await parallel(JOBS.map(([span, label]) => () => agent(
`You are adding English translation glosses to an OCR-derived transcription.
Your span: ${span}.

${RULES}

Concurrency note: other agents are editing OTHER spans of the same file. If
an Edit fails stale, re-read your region and retry once; if an old_string no
longer matches, skip and move on.

Work through your span sequentially and return the structured report
(span = "${label}").`,
  { label, phase: 'Translate', schema: REPORT, model: 'opus', effort: 'medium' }
)))

const ok = reports.filter(Boolean)
log(`${ok.length}/${JOBS.length} done, ${ok.reduce((s,r)=>s+r.translations_added,0)} glosses, ${ok.reduce((s,r)=>s+r.skipped_already_translated,0)} skipped-as-already-translated`)
return { reports: ok }