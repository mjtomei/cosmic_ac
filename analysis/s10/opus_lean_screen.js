export const meta = {
  name: 'opus-lean-screen',
  description: 'Lean Opus-5 low-effort AI screening of 241 blinded segments (Pangram-correlation trial)',
  phases: [{ title: 'Screen', detail: '25 batches, detection-only, terse' }],
}

const POOL = '/home/matt/performance_commons/analysis/s10/judge_blind_pool.json'
const ids = Array.from({length: 241}, (_, i) => 'S' + String(i).padStart(3, '0'))
const batches = []
for (let i = 0; i < ids.length; i += 10) batches.push(ids.slice(i, i + 10))

const SCHEMA = {
  type: 'object',
  properties: {
    scores: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          ai_guess: { type: 'integer', minimum: 0, maximum: 100 },
        },
        required: ['id', 'ai_guess'],
      },
    },
  },
  required: ['scores'],
}

function prompt(b) {
  return `Read the JSON file ${POOL} (Read tool). It maps segment IDs to excerpts of transcribed legislative floor speech. For ONLY these segments: ${b.join(', ')} — estimate the probability (0-100) that each was drafted with AI assistance. Judge from the text alone. Work quickly; no explanations; return all ${b.length} via structured output.`
}

phase('Screen')
const main = await parallel(batches.map((b, i) => () =>
  agent(prompt(b), {
    label: `screen:${i}`, phase: 'Screen',
    schema: SCHEMA, model: 'opus', effort: 'low',
  }).then(r => r.scores)))

return { main: main.filter(Boolean).flat() }