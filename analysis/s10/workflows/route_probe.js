export const meta = {
  name: 'route-probe',
  description: 'Tiny routing probe: one agent per lab family confirms it answers through the router',
  phases: [{ title: 'Probe' }],
}
const MEMBERS = [
  { id: 'anthropic',   type: 'panel-anthropic' },
  { id: 'openai',      type: 'panel-openai' },
  { id: 'google',      type: 'panel-google' },
  { id: 'xai',         type: 'panel-xai' },
  { id: 'moonshot',    type: 'panel-moonshot' },
  { id: 'alibaba',     type: 'panel-alibaba' },
  { id: 'deepseek',    type: 'panel-deepseek' },
  { id: 'gen-prose',   type: 'gen-prose' },
  { id: 'gen-dataviz', type: 'gen-dataviz' },
]
const SCHEMA = { type: 'object', required: ['lab', 'model_self_report', 'canary'],
  properties: { lab: { type: 'string' }, model_self_report: { type: 'string' }, canary: { type: 'string' } } }
const PROMPT = `ROLE: PROBE (one-off; set aside your usual review role for this single message).
Return an object:
- lab: the AI lab that built you, one word (e.g. OpenAI, Google, Anthropic, xAI, Moonshot, Alibaba, DeepSeek).
- model_self_report: your model name if you know it, else "unknown".
- canary: the exact string "RT-9271".`
phase('Probe')
const out = await parallel(MEMBERS.map(m => () =>
  agent(PROMPT, { agentType: m.type, label: `probe:${m.id}`, schema: SCHEMA })
    .then(r => ({ member: m.id, ok: true, ...(r || {}) }))
    .catch(e => ({ member: m.id, ok: false, error: String(e).slice(0, 200) }))))
return { probe: out }
