export const meta = {
  name: 'opus-screen-nb-full',
  description: 'Lean Opus screening of the full NB corpus (one half per run)',
  phases: [{ title: 'Screen', detail: '~473 batch files x 40 segments' }],
}

// args: {start: 0, end: 473}  (batch file index range, end exclusive)
// defensive: harness may deliver args as a JSON string
const _a = typeof args === 'string' ? JSON.parse(args) : (args || {})
const start = _a.start ?? 0
const end = _a.end ?? 473
const DIR = '/home/matt/performance_commons/analysis/s10/screen_batches'

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

const nums = []
for (let i = start; i < end; i++) nums.push(i)

phase('Screen')
const out = await parallel(nums.map(i => () => {
  const f = DIR + '/batch_' + String(i).padStart(4, '0') + '.json'
  return agent(
    `Read the JSON file ${f} (Read tool). It maps segment IDs to excerpts of transcribed legislative floor speech. For EVERY segment in the file, estimate the probability (0-100) that it was drafted with AI assistance. Judge from the text alone. Work quickly; no explanations; return every segment via structured output.`,
    { label: `b${i}`, phase: 'Screen', schema: SCHEMA,
      model: 'opus', effort: 'low' }
  ).then(r => r.scores)
}))

// results are harvested from journal.jsonl (return arrays are capped at
// 4096 items across the VM boundary); return only a count
return { n_scored: out.filter(Boolean).flat().length }