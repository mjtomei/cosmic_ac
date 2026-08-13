// MODEL PROVENANCE. This workflow sets no `model` on its agent() calls, so
// grading ran on whatever the host session's default was. That is a
// reproducibility hole: stages 3 and 4 were graded by claude-fable-5, and
// the only record of it is the string in the agent transcripts on the
// machine that ran them. Recovered 2026-08-12 and written into Appendix C.
// Set `model` explicitly on any future grading run.

export const meta = {
  name: 's10-quality-genre-controlled',
  description: 'Genre-controlled DQI grading of 840 blinded Canadian Hansard segments, plus a blinded AI screen on the same text',
  phases: [
    { title: 'Screen', detail: '18 batches of 48 — AI probability, detection-only' },
    { title: 'Grade', detail: '84 batches of 10 — anchored Discourse Quality Index' },
  ],
}

// ---------------------------------------------------------------------------
// WHAT THIS IS FOR
//
// The quality arm found that AI-flagged legislative speech is better-formed
// and worse-engaged than human speech ("form up, deliberation down"). Its
// unsolved confound is GENRE: AI concentrates in scripted formats, so the
// finding may partly be "scripted speech engages opponents less".
//
// This grades a pool balanced BY CONSTRUCTION across genre and era:
//   140 segments x {SO31 scripted, Oral Questions unscripted, Government
//   Orders debate} x {2018-19, 2025-26} = 840, all Canadian House of Commons,
//   120-360 words, English-original, non-chair.
//
// Both an AI probability and a DQI grade are produced for every segment, so
// the analysis can ask whether the quality gap survives holding genre fixed.
//
// The pool file carries TEXT ONLY. No date, genre, speaker or era — the
// judge cannot condition on any of it.
// ---------------------------------------------------------------------------

// Stage is selectable so the SAME script runs both pools without editing
// source. Pass args when invoking:
//   Workflow({scriptPath: '.../grade_workflow.js'})                -> stage 1
//   Workflow({scriptPath: '.../grade_workflow.js', args: {stage:2}}) -> stage 2
//
// stage 1 = pool.json, 840 genre-balanced federal-Canadian segments. The
//           only arm that can settle the genre confound.
// stage 2 = pool2.json, 682 segments across 22 chambers labelled by PANGRAM
//           verdict rather than an LLM screen (207 AI / 134 Mixed / 341
//           Human). Cannot control genre; fixes the power problem instead.
const HERE = '/home/matt/performance_commons/analysis/s10/quality_expansion'
// args can arrive as a JSON-encoded STRING rather than an object depending on
// how the Workflow tool is invoked. Parse both forms. Without this, every
// stage silently falls back to 1 and grades the wrong pool -- a footgun that
// had to be re-fixed by hand on arch-home after each new stage was shipped.
const A = typeof args === 'string' ? JSON.parse(args) : args
const STAGE = (A && A.stage !== undefined) ? A.stage : 1
// stage 0 = REPLICATION of the PUBLISHED v2 run: judge_blind_pool.json,
// 241 segments, S-prefixed ids, compared per-segment against
// fable_judge_v2_scores.csv.
//
// NOT judge_blind_pool_t.json. That 220-segment T-prefixed pool belongs to
// dqi_judge_v2b.js, the later per-year variant. Its rubric is byte-identical
// (verified against commit 19deb97) so the instrument is the same, but its
// ids share no overlap with the published scores -- pointing stage 0 at it
// yields a silent zero-overlap comparison that looks like a clean run.
//
// ai_guess comes from the judge itself as in the original, so stage 0 runs no
// separate Screen phase.
// stage 3 = PAIRED humanized-vs-original. 38 texts, each contributing its
// unmodified original AND its best detector-evading rewrite, blinded and
// interleaved. Within-text pairing means DQI differences are attributable to
// the rewrite rather than to content, speaker or occasion.
// stage 4 = the Government Orders arm of the same paired design, kept
// separate from stage 3 so the two chambers can be checked for
// consistency BEFORE pooling rather than merged by default.
const POOL = STAGE === 4 ? `${HERE}/pool4.json`
           : STAGE === 3 ? `${HERE}/pool3.json`
           : STAGE === 0 ? `${HERE}/judge_blind_pool.json`
           : STAGE === 2 ? `${HERE}/pool2.json`
           : `${HERE}/pool.json`
const N = STAGE === 4 ? 50 : STAGE === 3 ? 76 : STAGE === 0 ? 241 : STAGE === 2 ? 682 : 840
const PREFIX = STAGE === 4 ? 'G' : STAGE === 3 ? 'H' : STAGE === 0 ? 'S' : STAGE === 2 ? 'R' : 'Q'
const PAD = (STAGE === 0 || STAGE === 3 || STAGE === 4) ? 3 : 4

const ids = Array.from({length: N}, (_, i) => PREFIX + String(i).padStart(PAD, '0'))

// ---------- Phase 1: blinded AI screen ----------
const SCREEN_BATCH = 48
const screenBatches = []
for (let i = 0; i < ids.length; i += SCREEN_BATCH) screenBatches.push(ids.slice(i, i + SCREEN_BATCH))

const SCREEN_SCHEMA = {
  type: 'object', required: ['scores'],
  properties: {
    scores: {
      type: 'array',
      items: {
        type: 'object', required: ['id', 'ai_guess'],
        properties: {
          id: { type: 'string' },
          ai_guess: { type: 'integer', minimum: 0, maximum: 100 },
        },
      },
    },
  },
}

function screenPrompt(b) {
  return `Read the JSON file ${POOL} (Read tool). It maps segment IDs to excerpts of transcribed legislative floor speech.

For ONLY these segments: ${b.join(', ')}

Estimate the probability (0-100) that each was drafted with AI assistance. Judge from the text alone.

Some of these predate the existence of such tools, so a substantial number should score very low. Do not let length drive the score.

Work quickly; no explanations; return all ${b.length} via structured output.`
}

// ---------- Phase 2: anchored DQI grading ----------
// Rubric follows Steenbergen, Bachtiger, Sporndli & Steiner (2003), the
// standard deliberation-quality scale for parliamentary debate. The anchors
// below are the calibration that matters: without them judges inflate
// "justification" and "constructive politics" badly (measured: constructive
// 0.99 -> 0.25 once anchored, matching Steenbergen's own all-zeros finding
// on a 1998 Commons debate).
const GRADE_BATCH = 10
const gradeBatches = []
for (let i = 0; i < ids.length; i += GRADE_BATCH) gradeBatches.push(ids.slice(i, i + GRADE_BATCH))

const GRADE_SCHEMA = {
  type: 'object', required: ['grades'],
  properties: {
    grades: {
      type: 'array',
      items: {
        type: 'object',
        // -1 is a real code, not missing data: respect_demands and
        // respect_counterargs are INAPPLICABLE when no other demand or
        // counterargument is on the table. Collapsing -1 into 0 would score
        // "nothing to engage with" as "refused to engage".
        required: ['id', 'justification', 'common_good', 'respect_groups',
                   'respect_demands', 'respect_counterargs', 'constructive',
                   'evidence', 'ai_guess'],
        properties: {
          id: { type: 'string' },
          justification: { type: 'integer', minimum: 0, maximum: 3 },
          common_good: { type: 'integer', minimum: 0, maximum: 2 },
          respect_groups: { type: 'integer', minimum: 0, maximum: 2 },
          respect_demands: { type: 'integer', minimum: -1, maximum: 2 },
          respect_counterargs: { type: 'integer', minimum: -1, maximum: 3 },
          constructive: { type: 'integer', minimum: 0, maximum: 2 },
          evidence: { type: 'integer', minimum: 0, maximum: 3 },
          ai_guess: { type: 'integer', minimum: 0, maximum: 100 },
        },
      },
    },
  },
}

// VERBATIM from dqi_judge_v2b.js — the instrument that produced the
// existing v2 results. Its anchors are the ORIGINAL AUTHORS' OWN CODINGS
// from a 1998 UK Commons debate, not paraphrases. Do not reword: an
// earlier copy of this file silently ran a 6-dimension paraphrase with
// respect_groups dropped and the -1 sentinels removed, which is a
// different instrument and not comparable to the v2 numbers.
const RUBRIC = `You are coding legislative floor-speech excerpts with the Discourse Quality Index (Steenbergen, Bächtiger, Spörndli & Steiner 2003), using their exact categories. Work strictly from the text; you have NO information about speaker, date, or party, and must not try to infer them. All worked examples below are the original authors' own codings from a 1998 UK House of Commons debate on women's issues; use them as calibration anchors.

DIMENSIONS AND ANCHORS

1. justification (level of justification, 0-3) — completeness of the inferences supporting demands:
   0 = no justification: a demand with no reason. Anchor (coded 0): "I am pleased that the hon. Lady praises the work of Chwarae Teg... Does she share my hope that the Government will continue to support fair play for women in Wales and the rest of the country? We want a firm commitment from the Minister to back that." (demands support, gives no reason why it is desirable)
   1 = inferior justification: a reason is given but the inference from reason to demand is incomplete, or the conclusion rests on illustration only. Anchor (coded 1): "Does my hon. Friend agree that, if the rumours are true that people will not need receipts to claim the child care allowance, they could indeed spend the money on washing machines?" (implicit demand for receipts; suggestion of frivolous spending is not backed by argument or evidence)
   2 = qualified justification: one complete inference linking reason to demand. Anchor (coded 2): "Women who are abused in the household sometimes find it difficult to get away from the home. Separate taxation helps women to have the courage to move out on an abusive household." (one complete inference: policy -> courage to escape)
   3 = sophisticated justification: two or more complete justifications. Anchor (coded 3): "There are several reasons why that is important. First, some parents want to look after their own children. Secondly... the difficulty of getting them to different arrangements... increases exponentially. Thirdly... for many children there are advantages in experiencing daily daytime care from their father..." (three complete justifications for extending family-friendly employment to fathers)
   Implicit inferences count as complete only when their meaning would be beyond reasonable doubt to all debate participants.

2. common_good (content of justification, 0-2): 0 = appeals framed only in terms of specific group or constituency interests; 1 = no explicit reference to either group interests or the common good; 2 = explicit appeal to the common good, EITHER in utilitarian terms ("the best for society", greatest good) OR in terms of the difference principle (helping the least advantaged). Anchor (coded common-good, both variants): "I hope that the Government will consider back-to-work benefits for the many people in that situation..." (difference principle: the least advantaged) followed by "Any welfare system with paid work as its primary goal has serious implications for women and for society. I do not believe that it is in our best interests as a society to force carers out to work." (utilitarian).

3. respect_groups (respect toward the groups a policy would help, 0-2): 0 = only negative statements about the groups; 1 = no explicitly negative and no explicitly positive statements; 2 = at least one explicitly positive statement, regardless of negatives. Anchor (coded 2): "I warmly welcome the announcements... I pay tribute to the women's organisations, the unsung heroes of our communities; we should be better off if we listened to them."

4. respect_demands (respect toward others' demands, -1 if no other demand is engaged or obvious agreement makes it inapplicable, else 0-2 with the same logic as respect_groups): Anchor (coded 0, sarcasm degrading a demand): "Would we not be going backwards if, while we were trying to abolish woman-free zones in public life, we started to create man-free zones?" Anchor (coded 2): "All issues affect women, and it is important that we tackle those issues across Government. The previous Government recognised that fact... and I believe that this Government are doing the same. I think that that is a positive step forward."

5. respect_counterargs (respect toward counterarguments, -1 if no counterargument is on the table or anticipated, else 0-3): 0 = counterarguments ignored; 1 = acknowledged but explicitly degraded. Anchor (coded 1): the exchange ending "The hon. Lady is absolutely right. She knows everything about positive discrimination being illegal, as her own party was ruled illegal in positively discriminating for women..." (sarcastic degradation). 2 = acknowledged neutrally. Anchor (coded 2): "I hear what the hon. Lady says." 3 = acknowledged and explicitly valued. Anchor (coded 3): "The hon. Lady raises an important issue, about which the pensions review is liaising with actuaries."

6. constructive (constructive politics, 0-2): 0 = positional politics, the speaker sits on their position with no attempt at compromise or consensus; 1 = an alternative proposal that does not fit the current agenda; 2 = a mediating proposal that fits the current agenda. (The anchor debate had no variation here; code from the definitions.)

7. evidence (NOT a DQI dimension — our addition, kept separate): 0 = none; 1 = vague references; 2 = one checkable specific (number, named source, dated event); 3 = several checkable specifics.

8. ai_guess 0-100: your independent estimate of the probability this text was drafted with AI assistance. Judge this ONLY after the quality codes, and do not let it influence them.

Score each segment on its own merits against the anchors, not relative to the other segments in your batch.`

function gradePrompt(b) {
  // v2b's tail, verbatim. It deliberately names NO chamber: the rubric already
  // blinds the judge, and an earlier copy of this file asserted "from the
  // Canadian House of Commons" -- false for stages 0 and 2, and an invitation
  // to grade against the wrong procedural expectations.
  return `${RUBRIC}

Read the JSON file ${POOL} (Read tool). It maps segment IDs to text. Score ONLY these segments: ${b.join(', ')}. Return all ${b.length} segments via structured output, no commentary.`
}

// ---------- run ----------
phase('Screen')
const screened = (STAGE === 0 || STAGE === 3 || STAGE === 4) ? [] : (log(
  `Blinded AI screen over ${N} segments in ${screenBatches.length} batches`),
  await parallel(screenBatches.map((b, i) => () =>
  agent(screenPrompt(b), {
    label: `screen:${i}`, phase: 'Screen',
    schema: SCREEN_SCHEMA, effort: 'low',
  }).then(r => r && r.scores))))

phase('Grade')
log(`Anchored DQI grading in ${gradeBatches.length} batches`)
const graded = await parallel(gradeBatches.map((b, i) => () =>
  agent(gradePrompt(b), {
    label: `dqi:${i}`, phase: 'Grade',
    schema: GRADE_SCHEMA, effort: 'high',
  }).then(r => r && r.grades)))

const s = screened.filter(Boolean).flat()
const g = graded.filter(Boolean).flat()
log(`screened ${s.length}/${N}, graded ${g.length}/${N}`)

// Return counts only; the per-segment rows are harvested from journal.jsonl
// by analyze.py, which stays clear of the workflow return-size boundary.
return { screened: s.length, graded: g.length, pool: N }
