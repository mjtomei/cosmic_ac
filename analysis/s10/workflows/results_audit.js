export const meta = {
  name: 's10-results-audit',
  description: 'Three sweeps: deleted-corpus/fabricated-number reliance (X1), weighting/pooling across all rate results (X12), and stale-number reconciliation across all prose (B+X)',
  phases: [
    { title: 'CorpusAudit', detail: 'X1: reliance on deleted synthetic corpus or hardcoded numbers', model: 'opus' },
    { title: 'WeightAudit', detail: 'X12: segment-vs-word weighting and pooled-vs-per-chamber across rate results', model: 'opus' },
    { title: 'Reconcile', detail: 'stale numbers in draft/methodology/work-log vs current results', model: 'opus' },
  ],
}
const ROOT = '/home/matt/performance_commons'
const S10 = ROOT + '/analysis/s10'

const FIND = {
  type: 'object', required: ['findings'],
  properties: { findings: { type: 'array', items: {
    type: 'object', required: ['file', 'issue', 'severity'],
    properties: {
      file: { type: 'string' }, line: { type: 'string' },
      issue: { type: 'string', description: 'what is wrong, concretely' },
      current: { type: 'string', description: 'the exact stale/suspect text or number' },
      correct: { type: 'string', description: 'the correct value/text if known, else "verify"' },
      severity: { type: 'string', description: 'high | medium | low' },
    } } } },
}

// ---- Phase 1: X1 deleted-corpus / fabricated-number audit ----
phase('CorpusAudit')
const corpusGroups = [
  { label: 'scripts', glob: `${S10}/*.py`,
    what: 'any script that still reads, divides by, or depends on the deleted Mistral synthetic sensitivity corpus (se_segments.jsonl, stratum D-synthetic-se, Se=1.0), OR hardcodes a result number that should be computed from data' },
  { label: 'result-json', glob: `${S10}/*.json and ${S10}/*.csv`,
    what: 'result files that are the sole source of a paper number with no committed script that regenerates them, or that embed the deleted-corpus verdicts as a live dependency' },
  { label: 'prose', glob: `${S10}/S10-WRITEUP-DRAFT.md, ${S10}/METHODOLOGY.md`,
    what: 'any claim still resting on the deleted synthetic corpus as if live, or any prevalence/sensitivity number presented as estimated-by-us when it is now a floor (Se not estimated; Se=1 conservative; external anchor RAID 99.3%; the 40/40 pilot is corroboration only)' },
]
const corpus = await parallel(corpusGroups.map(g => () =>
  agent([
'Audit S10 for reliance on the DELETED synthetic sensitivity corpus and for fabricated/hardcoded numbers (review item X1).',
'CONTEXT: the study once estimated detector sensitivity Se from 40 Mistral-generated synthetic legislative speeches (Se=40/40=1.0). That corpus was set aside; prevalence is now reported as a conservative FLOOR (tau >= pi, since Sp=1 and Se<=1). Nothing in the paper should still DIVIDE by a home-grown Se or depend on that corpus as live. The 40/40 hit-rate may appear only as one-sentence corroboration.',
`SCAN: ${g.glob}`,
`LOOK FOR: ${g.what}`,
'Use grep/read. Report each concrete problem; empty findings is a valid result. Do not edit anything.',
  ].join('\n'), { label: 'corpus:' + g.label, phase: 'CorpusAudit', schema: FIND, model: 'opus', effort: 'medium' })
    .then(r => (r && r.findings) || [])))

// ---- Phase 2: X12 weighting / pooling audit ----
phase('WeightAudit')
const rateArms = [
  { label: 'prevalence', files: 'prevalence_report.py, banded_prevalence.py' },
  { label: 'bypass', files: 'bypass_report.py' },
  { label: 'permeation', files: 'word_context_delta.py and any §4.8 permeation script' },
  { label: 'quality', files: 'quality_expansion/analyze.py, analyze_stage2.py, analyze_stage3.py, analyze_stage6.py' },
  { label: 'cohort-class', files: 'member_level_estimation.py, panel_estimation.py, cohort_vs_period.py' },
]
const weight = await parallel(rateArms.map(a => () =>
  agent([
'Audit an S10 rate-producing arm for the length/weighting bias in review item X12.',
'THE QUESTION: samples are often drawn UNIFORMLY over segments, but longer segments are more machine-drafted, so a SEGMENT-weighted rate understates and a WORD-weighted rate is the correction. For each rate this arm reports, determine: (a) is it segment-weighted or word-weighted; (b) if segment-weighted, is that defensible for what it measures or is it an uncorrected bias; (c) is a per-chamber breakdown AND both a word-weighted-pooled and an equal-weight mean-of-chambers reported, or only one; (d) any sampling that is uniform-over-segments where word-weighting was NOT applied afterward.',
`FILES (in ${S10}): ${a.files}`,
'Read the code and any results/docstrings. Report concrete gaps; "correctly word-weighted, no issue" is a valid empty finding. Do not edit.',
  ].join('\n'), { label: 'weight:' + a.label, phase: 'WeightAudit', schema: FIND, model: 'opus', effort: 'medium' })
    .then(r => (r && r.findings) || [])))

// ---- Phase 3: stale-number reconciliation across prose ----
phase('Reconcile')
const TRUTH = [
'CURRENT TRUTH (edits already committed; prose must match):',
'- Bypass per-variant rate is 11.1% (two final runs), NOT 8.5% (old, kept only in Appendix B as superseded). Per-target 22.5%. Vendor multiple 4.8x, NOT 3.7x. Bypass restructured: two final runs primary, two first attempts superseded.',
'- Prevalence rates are word-weighted (ratio estimator over a uniform segment draw); length bias real but corrected; report per-chamber + pooled + mean-of-chambers.',
'- Sensitivity: not estimated by us; floor framing (Se=1 conservative); external anchor RAID 99.3%; 40/40 pilot corroboration only.',
'- Occupational study: four-level middle-peak U is the registered result; the three-profile free/front-line/corporate LINEAR rank is retired to Appendix B.',
'- Quality arm has SIX gradings + stage 6 (seven total); C.1 cross-account appendix was REMOVED.',
'- Chamber counts: verify every "19/20/22 chambers" against the actual arm (prevalence vs covariate) and make them consistent (review item X6/P8; §2 line ~46 "Nineteen chambers" is suspect).',
'- Bands / seed-verdict are exploratory, not findings.',
].join('\n')
const proseFiles = [
  { label: 'draft-methods', f: 'S10-WRITEUP-DRAFT.md sections 1-3 and METHODOLOGY.md' },
  { label: 'draft-results', f: 'S10-WRITEUP-DRAFT.md section 4 (all subsections)' },
  { label: 'draft-disc', f: 'S10-WRITEUP-DRAFT.md sections 5-8 and appendices' },
  { label: 'worklog', f: 'studies-and-work-log.md (review item X8: the S10 register entry still carries superseded bypass/prevalence numbers)' },
]
const recon = await parallel(proseFiles.map(pf => () =>
  agent([
'Find every place in this S10 text that states a number or claim now superseded by committed results, so it can be corrected (reviews X6, X8, and the B/X updates).',
TRUTH,
`SCAN: ${pf.f} (under ${ROOT})`,
'Report each stale mention: the file, the exact current text, and the correct replacement. Distinguish text that legitimately cites an OLD number as superseded (fine) from text asserting it as current (stale). Do not edit; report exact strings so edits can be applied mechanically.',
  ].join('\n'), { label: 'recon:' + pf.label, phase: 'Reconcile', schema: FIND, model: 'opus', effort: 'medium' })
    .then(r => (r && r.findings) || [])))

const all = { corpus: corpus.flat(), weighting: weight.flat(), reconcile: recon.flat() }
const writer = await agent([
'Write a single markdown report to ' + S10 + '/RESULTS-AUDIT-2026-08-24.md consolidating these findings.',
'Three sections (Corpus/X1, Weighting/X12, Reconciliation/B+X), each a table: file | current | correct | severity | issue.',
'Sort each by severity (high first). Add a one-line count summary per section at the top. Then reply with the totals.',
'FINDINGS JSON:', JSON.stringify(all),
].join('\n'), { label: 'write', phase: 'Reconcile', model: 'opus', effort: 'low' })
return { corpus: all.corpus.length, weighting: all.weighting.length, reconcile: all.reconcile.length, writer }
