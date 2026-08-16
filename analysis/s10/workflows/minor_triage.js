export const meta = {
  name: 's10-minor-triage',
  description: 'Re-adjudicate the 76 minor review findings against the CURRENT draft, one agent per arm',
  phases: [{ title: 'Triage' }],
}

const ARMS = [
  { arm: 'Calibration and prevalence', ids: 'P1–P10' },
  { arm: 'Genre arm', ids: 'G1–G6' },
  { arm: 'Opus screen', ids: 'O1–O9' },
  { arm: 'Series and cohort', ids: 'S1–S10' },
  { arm: 'Ladder and permeation', ids: 'L1–L9' },
  { arm: 'Quality / DQI arm', ids: 'Q1–Q12' },
  { arm: 'Bypass arm', ids: 'B1–B8' },
  { arm: 'Cross-cutting', ids: 'X1–X12' },
]

const SCHEMA = {
  type: 'object',
  required: ['arm', 'findings'],
  properties: {
    arm: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['id', 'status', 'severity', 'effort', 'summary', 'action'],
        properties: {
          id: { type: 'string', description: 'the review id, e.g. P3' },
          review_verdict: { type: 'string', description: 'CONFIRMED | PARTIAL | REFUTED, as the review labelled it' },
          status: { type: 'string', description: 'already-fixed | mooted | live — checked against the CURRENT draft, not the review' },
          severity: { type: 'string', description: 'high | medium | low — how much it would change a reader\'s conclusions if left' },
          effort: { type: 'string', description: 'trivial | small | substantive — to fix now, if live' },
          summary: { type: 'string', description: 'one sentence: the actual defect' },
          action: { type: 'string', description: 'the concrete fix, or why no action (fixed where/by what; mooted by what change)' },
          evidence: { type: 'string', description: 'what in the current draft you checked to decide status' },
        },
      },
    },
  },
}

function brief(arm, ids) {
  return [
'Re-adjudicate a block of MINOR review findings for study S10 against the CURRENT state of the draft. This is triage, not fixing.',
'',
'READ, in /home/matt/performance_commons/analysis/s10:',
'  1. REVIEW-2026-08-11.md — section "### 2.4 MINOR findings, by arm", subsection "#### ' + arm + '". Those are your findings (' + ids + ').',
'  2. S10-WRITEUP-DRAFT.md — the CURRENT draft. It has been heavily revised since the review: §4.2, §4.6a, §4.7 and §4.9 were rewritten, appendices A–D restructured. Many minors may already be fixed or mooted.',
'  3. METHODOLOGY.md and any script the finding names, as needed to verify.',
'',
'FOR EACH finding in your block, decide its status AGAINST THE CURRENT DRAFT (not against the review\'s own verdict, which predates the revisions):',
'  - already-fixed: the current text no longer has the defect. Say where/how you confirmed it.',
'  - mooted: the passage or claim the finding attacked no longer exists, or a later change made it moot.',
'  - live: still present in the current draft. Give severity (would it change a reader\'s conclusion?), effort to fix, and the concrete one-line fix.',
'',
'Be skeptical in BOTH directions. Do not mark something fixed because it "probably" was — quote the current draft line that resolves it. Do not mark something live without confirming the defective text is still there. If the review\'s own finding was REFUTED or was factually wrong, say so and mark it accordingly (status live but severity low with action "no change — review finding does not hold, because ...").',
'',
'Return one record per finding id in your block. Terse and concrete; a human will work the live ones in severity order.',
  ].join('\n')
}

phase('Triage')
const res = await parallel(ARMS.map(a => () =>
  agent(brief(a.arm, a.ids), { label: a.arm.split(' ')[0], phase: 'Triage',
                               schema: SCHEMA, model: 'sonnet', effort: 'medium' })))
const ok = res.filter(Boolean)
const all = ok.flatMap(r => r.findings || [])
const byStatus = {}, bySev = {}
for (const f of all) {
  byStatus[f.status] = (byStatus[f.status] || 0) + 1
  if (f.status === 'live') bySev[f.severity] = (bySev[f.severity] || 0) + 1
}
log(all.length + ' minors triaged. status: ' + JSON.stringify(byStatus))
log('live by severity: ' + JSON.stringify(bySev))
return { arms: ok.length, total: all.length, byStatus, bySev, findings: all }
