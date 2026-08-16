export const meta = {
  name: 'stage5-dqi-grading',
  description: 'Grade successful-evasion pairs on the frozen v2b DQI rubric, two blind passes',
  phases: [{ title: 'Grade' }],
}
const ARGS=(typeof args==='string')?JSON.parse(args):(args||{})
const PASSES=ARGS.passes||2
const BATCH=ARGS.batch||18   // ~4 batches x 2 passes = 8 agents over 70 texts

const SCHEMA = {
  type: 'object',
  properties: {
    scores: {
      type: 'array',
      items: {
        type: 'object',
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
        required: ['id', 'justification', 'common_good', 'respect_groups',
                   'respect_demands', 'respect_counterargs', 'constructive',
                   'evidence', 'ai_guess'],
      },
    },
  },
  required: ['scores'],
}

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

Score each segment on its own merits against the anchors, not relative to the other segments in your batch.

Read the JSON file ${POOL} (Read tool). It maps segment IDs to text. Score ONLY these segments: `

phase('Judge')
const main = await parallel(batches.map((b, i) => () =>
  agent(RUBRIC + b.join(', ') + `. Return all ${b.length} segments via structured output.`, {
    label: `judge2:${i}`, phase: 'Judge', schema: SCHEMA, effort: 'high',
  }).then(r => r.scores)))

phase('Reliability')
const rel = await parallel(rel_batches.map((b, i) => () =>
  agent(RUBRIC + b.join(', ') + `. Return all ${b.length} segments via structured output.`, {
    label: `rel2:${i}`

function prompt(items){
  return RUBRIC + "\n\nCode every excerpt below. Return one score object per id, all fields required, integers only, using the anchors above. Excerpts:\n\n"
    + items.map(x=>"[id "+x.id+"]\n"+x.text).join("\n\n---\n\n")
}

phase('Grade')
const fs_items = ARGS.items   // caller passes the item array inline
const chunks=[]
for(let i=0;i<fs_items.length;i+=BATCH) chunks.push(fs_items.slice(i,i+BATCH))
const jobs=[]
for(let pass=1;pass<=PASSES;pass++)
  for(let c=0;c<chunks.length;c++) jobs.push({pass,c,items:chunks[c]})
const res=await parallel(jobs.map(({pass,c,items})=>()=>
  agent(prompt(items),{label:'p'+pass+':b'+c,phase:'Grade',schema:SCHEMA,effort:'medium'})
    .then(r=>({pass,c,scores:(r&&r.scores)||[]}))))
const ok=res.filter(Boolean)
let n=0
for(const r of ok) n+=r.scores.length
log(ok.length+' grading agents, '+n+' score rows across '+PASSES+' passes')
return {agents:ok.length, rows:n, passes:PASSES}
