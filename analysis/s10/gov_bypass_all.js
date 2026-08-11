export const meta = {
  name: 's10-gov-bypass-all',
  description: 'Government Orders, ALL 31 uniform-draw Pangram positives (no Opus cut): real human exemplars matched by score, noise-aware retirement, all sub-50 variants retained for a Pangram test',
  phases: [
    { title: 'Hypotheses', detail: 'derive humanising hypotheses from matched human/AI contrast pairs' },
    { title: 'S1', detail: 'search round 1' },
    { title: 'S2', detail: 'search round 2 — retired texts dropped' },
    { title: 'S3', detail: 'search round 3' },
    { title: 'S4', detail: 'search round 4' },
    { title: 'S5', detail: 'search round 5 — survivors only' },
    { title: 'S6', detail: 'search round 6 — survivors only' },
  ],
}

// THREE CHANGES FROM v2, EACH FIXING A MEASURED DEFECT
//
// 1. CONTRASTIVE EXEMPLARS, NOT SELF-GENERATED ONES. v1/v2 fed the model its
//    own rewrites, so it learned from the very distribution it was trying to
//    escape -- which is the likeliest reason it plateaued in round 2 and never
//    moved. Exemplars here are REAL Hansard: for each seed, the two
//    highest-scoring genuine Pangram-Human segments that still score BELOW it
//    (median gap 3 points). A tight pair isolates the marginal difference
//    instead of drowning it in the gap between 80 and 5.
//
// 2. PER-TEXT EARLY STOPPING, NOISE-AWARE. Detector test-retest sd is 6.0, so
//    a 3x mean has sd ~2.4. A round only counts as improvement if it beats the
//    text's prior best replicated mean by MORE THAN 5 points; two consecutive
//    failures retire the text. Without the threshold, "keep going while it
//    improves" is a random walk mistaken for progress.
//
// 3. EVERY SUB-50 VARIANT IS KEPT, not just the per-text best. All four
//    Pangram flips observed so far came from variants scoring under 34, so
//    the useful candidates are the low tail, and a text gets as many shots as
//    it earns. Reporting must then separate per-variant flip rate from
//    per-text evasion rate given N attempts.

const SEEDS = '/home/matt/performance_commons/analysis/s10/gov_seeds_all.json'
const CONTRAST = '/home/matt/performance_commons/analysis/s10/gov_contrast_all.json'
const TEXTS = '/home/matt/performance_commons/analysis/s10/ca/segments_ca2.jsonl'
// STOPPING RULE: patience on the ALL-TIME best, not a per-round jump.
// Requiring a fixed +5 every round retires texts that are improving steadily
// in small steps -- which is most of them. Instead a text stays alive while it
// has set a new all-time best replicated mean within the last PATIENCE rounds,
// and is retired only when PATIENCE consecutive rounds fail to beat it.
// EPS guards against a text living forever on sub-noise flutter: with a 3x
// mean (sd ~2.4) a "new best" must beat the old one by more than 1 point.
// PATIENCE 3 requires MAX_ROUNDS > 4 to do anything: round 1 always sets the
// first best, so three consecutive failures cannot accumulate until round 4,
// which was the old cap. Six rounds lets the criterion actually retire texts.
const PATIENCE = 3
const MAX_ROUNDS = 6
const EPS = 1.0
const KEEP_BELOW = 50
const K = 3               // variants per active text per round

const HYP_SCHEMA = { type:'object', properties:{ hypotheses:{ type:'array', items:{ type:'object',
  properties:{ name:{type:'string'}, claim:{type:'string'}, how:{type:'string'} },
  required:['name','claim','how'] } } }, required:['hypotheses'] }
const RW_SCHEMA = { type:'object', properties:{ variants:{ type:'array', items:{ type:'object',
  properties:{ seg_id:{type:'string'}, v:{type:'integer'}, text:{type:'string'}, hypothesis:{type:'string'} },
  required:['seg_id','v','text','hypothesis'] } } }, required:['variants'] }
const SC_SCHEMA = { type:'object', properties:{ scores:{ type:'array', items:{ type:'object',
  properties:{ key:{type:'string'}, ai_guess:{type:'integer',minimum:0,maximum:100},
               plausible:{type:'integer',minimum:0,maximum:100} },
  required:['key','ai_guess','plausible'] } } }, required:['scores'] }

function scPrompt(batch, tag) {
  return `Below are ${batch.length} excerpts of transcribed legislative floor speech, each with a key.

${batch.map(x=>`### ${x.key}\n${x.text}`).join('\n\n')}

For EACH excerpt return two INDEPENDENT integers:
  ai_guess  0-100, probability it was drafted with AI assistance. Judge from the text alone. Work quickly; no explanations.
  plausible 0-100, probability it would pass unremarked as genuine floor speech by a member of a Westminster-style legislature — judged on idiom and procedural register, NOT on whether it seems AI-written.

Set key to the "###" heading exactly. Return all ${batch.length} via structured output. (${tag})`
}

async function scoreRep(items, ph, tag, reps) {
  const all = []
  for (let p = 1; p <= reps; p++) {
    const b = []
    for (let i = 0; i < items.length; i += 12) b.push(items.slice(i, i + 12))
    const out = await parallel(b.map((x, i) => () =>
      agent(scPrompt(x, `${tag}p${p}`), { label:`sc:${tag}:${p}:${i}`, phase:ph,
        schema:SC_SCHEMA, model:'opus', effort:'low' }).then(r => (r && r.scores) || [])))
    all.push(...out.filter(Boolean).flat())
  }
  const agg = {}
  for (const s of all) (agg[s.key] = agg[s.key] || []).push(s)
  const mean = {}
  for (const k in agg) mean[k] = {
    ai: agg[k].reduce((a,s)=>a+s.ai_guess,0)/agg[k].length,
    pl: agg[k].reduce((a,s)=>a+s.plausible,0)/agg[k].length,
    n: agg[k].length }
  return mean
}

phase('Hypotheses')
const hyp = await agent(
`Read ${CONTRAST} (Read tool). It pairs each AI-drafted seed segment with the two genuine HUMAN-written segments whose AI-detector scores sit just BELOW it — typically within 3 points, so these are near-neighbours the detector barely separates.

For 12 of the pairs (your choice, spread across the score range), fetch all three texts from ${TEXTS} (JSONL; match "seg_id", text at .text) and read them side by side.

Your task: identify what the genuinely human passages do that the AI-drafted ones do not. Look at concrete, reproducible features — sentence-length variance, unfinished or self-corrected clauses, how names and numbers are introduced, procedural idiom, where emphasis falls, what is left implicit, redundancy, anticlimax, how the passage ends.

Return 6-9 hypotheses. Each needs a short name, a claim (what differs, stated so it could be wrong), and "how" (a concrete instruction a writer could follow). Avoid vague advice like "be more natural" — if a hypothesis cannot be applied mechanically it is useless here.`,
  { label:'hyp', phase:'Hypotheses', schema:HYP_SCHEMA, model:'opus', effort:'high' })
  .then(r => (r && r.hypotheses) || [])
log(`hypotheses: ${hyp.map(h=>h.name).join(' | ')}`)

const hypBlock = hyp.map((h,i)=>`${i+1}. ${h.name} — ${h.claim}\n   HOW: ${h.how}`).join('\n')

// state per text
const seedIdx = Array.from({length:31}, (_,i)=>i)
let activeSegs = null   // null on round 1 = all seeds; thereafter the survivors
const state = {}   // seg_id -> {best, strikes, active}
const kept = []    // every variant with replicated mean < KEEP_BELOW


for (let round = 1; round <= MAX_ROUNDS; round++) {
  if (activeSegs && !activeSegs.length) { log('all texts retired'); break }
  const ph = `S${round}`
  phase(ph)
  // round 1 selects by index; later rounds name the surviving seg_ids
  const units = activeSegs === null ? seedIdx : activeSegs
  const batches = []
  for (let i = 0; i < units.length; i += 5) batches.push(units.slice(i, i + 5))

  const gen = (await parallel(batches.map((b, i) => () =>
    agent(
`Read ${SEEDS} (Read tool) and select ${activeSegs === null ? `entries ${b.join(', ')} (0-indexed)` : `the entries whose seg_id is one of: ${b.join(', ')}`}. For each, fetch its full text from ${TEXTS} (JSONL; match "seg_id", text at .text).

Also read ${CONTRAST} and, for each of your seeds, fetch the two matched HUMAN exemplar passages listed for it. Those are real floor speech that the detector rates as more human than your seed, by only a few points. Study them.

Hypotheses derived from those contrasts:
${hypBlock}

Rewrite each seed so an AI-detection classifier scores it HUMAN, while it stays something a real legislator could have said without anyone noticing anything odd. Preserve the argument and every factual claim. Both properties are scored independently.

Produce ${K} attempts per seed (v = 1..${K}), each APPLYING A DIFFERENT HYPOTHESIS from the list. Put the hypothesis name in "hypothesis". Round ${round}.`,
      { label:`rw:r${round}:${i}`, phase:ph, schema:RW_SCHEMA, model:'opus', effort:'medium' })
      .then(r => (r && r.variants) || []))))
    .filter(Boolean).flat()
    .filter(x => x && x.text && x.text.length > 50)
    .map(x => ({ ...x, key:`${x.seg_id}|r${round}v${x.v}`, round }))

  const mean = await scoreRep(gen, ph, `r${round}`, 3)

  // --- per-text bookkeeping, keyed by seg_id throughout ---
  // Earlier drafts mapped array INDEX to seg_id positionally, which is only
  // correct if agent return order happens to match batch order. It is not
  // guaranteed, and a mis-map silently retires the wrong texts. Everything
  // below keys on seg_id, and `active` is rebuilt from a seg_id -> index map
  // captured up front.
  const idxBySeg = {}
  gen.forEach(g => { if (!(g.seg_id in idxBySeg)) idxBySeg[g.seg_id] = null })
  const seedsSeen = [...new Set(gen.map(g => g.seg_id))]

  const bySeg = {}
  for (const g of gen) {
    const m = mean[g.key]; if (!m) continue
    if (m.ai < KEEP_BELOW && m.pl >= 70)
      kept.push({ key: g.key, seg_id: g.seg_id, round, hypothesis: g.hypothesis,
                  ai: m.ai, pl: m.pl, text: g.text })
    if (!(g.seg_id in bySeg) || m.ai < bySeg[g.seg_id]) bySeg[g.seg_id] = m.ai
  }

  for (const sid of seedsSeen) {
    const st = state[sid] || (state[sid] = { best: Infinity, sinceBest: 0, rounds: 0, trace: [] })
    st.rounds++
    const b = bySeg[sid]
    st.trace.push(b === undefined ? null : Math.round(b * 10) / 10)
    if (b !== undefined && b < st.best - EPS) { st.best = b; st.sinceBest = 0 }
    else { st.sinceBest++; if (b !== undefined && b < st.best) st.best = b }
  }

  const survivors = seedsSeen.filter(sid => state[sid].sinceBest < PATIENCE)
  activeSegs = survivors
  const retired = seedsSeen.length - survivors.length
  const bestRound = Object.values(bySeg).length ? Math.min(...Object.values(bySeg)) : NaN
  log(`round ${round}: ${gen.length} variants; kept<${KEEP_BELOW}: ${kept.length} cumulative; retired ${retired}; ${activeSegs.length} texts still active; best-of-round ${bestRound.toFixed(1)}`)
}

return { hypotheses: hyp, kept, state }