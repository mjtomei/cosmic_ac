export const meta = {
  name: 'tier1-covariates',
  description: 'Education, occupation and birth data for US/UK/IE/CA-FED legislators, keyed to corpus speaker rosters',
  phases: [
    { title: 'Collect', detail: 'per-chamber roster slices, all sources with provenance' },
  ],
}

// args, two modes:
//   { chambers: [{ch: "US-HOUSE", n: 1234, chunk: 80}, ...] }   roster-index slices
//   { missing: true, chambers: [{ch, n, chunk}, ...] }          slices over
//     covariates_tier1_missing_keys.json instead of the roster head — the
//     recovery mode after a partial run; n = length of that chamber's missing
//     list. Agents are told which file to slice so nothing done is re-paid.
const ARGS = (typeof args === 'string') ? JSON.parse(args) : (args || {})
const CH = ARGS.chambers || []
const MISSING = !!ARGS.missing
if (!CH.length) throw new Error('no chambers in args — got: ' + JSON.stringify(args).slice(0, 200))

const SOURCES = {
  'US-HOUSE': [
    'PRIMARY, structured: the unitedstates/congress-legislators dataset on GitHub (legislators-current.json and legislators-historical.json) — bioguide id, full name, birthday, and per-term chamber/state/party/date ranges. This resolves identity: a roster key like "smith of texas" plus its year span picks the person via terms. Tier: official.',
    'SECONDARY, prose: the Biographical Directory of the United States Congress (bioguide.congress.gov), one page per member — education and pre-congressional occupation in the first sentences. Tier: official.',
    'Wikipedia/news for whatever remains, tiered as such.',
  ].join('\n'),
  'US-SENATE': 'Same sources as US-HOUSE; senators are in the same datasets with chamber="sen" terms.',
  'UK': [
    'The UK Parliament Members API (members-api.parliament.uk) for canonical identity and membership dates. Tier: official.',
    'Wikipedia/Wikidata for birth year, education (almost the only source for it), occupation. Tier: wikipedia.',
    'Roster keys are Hansard forms like "amess" or "kenneth baker"; members who spoke mainly under office titles are absent from the roster by design — do not chase them.',
  ].join('\n'),
  'IE': [
    'The Oireachtas members API (api.oireachtas.ie) for identity and membership. Tier: official.',
    'Wikipedia for birth year, education, occupation. Tier: wikipedia.',
    'Roster keys are "micheál martin" style full names — identity is usually unambiguous.',
  ].join('\n'),
  'CA-FED': [
    'PRIMARY: PARLINFO (lop.parl.ca), the Library of Parliament biographical database — profession and birth date for every MP in history, structured. Tier: official.',
    'Wikipedia to fill education level where PARLINFO gives only profession. Tier: wikipedia.',
    'Roster keys are "denis paradis" style full names from Hansard.',
  ].join('\n'),
}

const SCHEMA = {
  type: 'object',
  required: ['chamber', 'chunk', 'n_keys', 'records'],
  properties: {
    chamber: { type: 'string' }, chunk: { type: 'integer' },
    n_keys: { type: 'integer' }, notes: { type: 'string' },
    records: {
      type: 'array',
      items: {
        type: 'object',
        required: ['key', 'person_name'],
        properties: {
          key: { type: 'string', description: 'roster key VERBATIM — the join key, never altered' },
          person_name: { type: 'string' },
          term_first: { type: 'integer', description: 'first year this PERSON held the seat — assigns key+year to person where a key spans several people' },
          term_last: { type: 'integer' },
          ambiguous: { type: 'boolean', description: 'true if the key could not be confidently resolved to this person for the stated years' },
          birth_year: { type: 'integer' },
          gender: { type: 'string' },
          education_level: { type: 'string', description: 'none | secondary | college | bachelor | graduate | professional | unknown' },
          education_field: { type: 'string' },
          alma_maters: { type: 'array', items: { type: 'string' } },
          prior_occupation: { type: 'string', description: 'verbatim as the source states it; coded centrally later' },
          father_occupation: { type: 'string' },
          mother_occupation: { type: 'string' },
          evidence: {
            type: 'array',
            items: {
              type: 'object',
              required: ['field', 'tier', 'url'],
              properties: {
                field: { type: 'string' }, value: { type: 'string' },
                tier: { type: 'string', description: 'official | wikipedia | news | obituary | party | academic | other' },
                url: { type: 'string' }, quote: { type: 'string' },
              },
            },
          },
        },
      },
    },
  },
}

function brief(ch, chunk, chunkSize) {
  return [
'Collect biographical covariates for legislators in the ' + ch + ' chamber, for study S10 in /home/matt/performance_commons/analysis/s10.',
'',
'YOUR SLICE',
'',
'All file paths below are relative to /home/mjtomei/s10_tier1_recovery — read them from there.',
'',
MISSING
  ? 'Read covariates_tier1_missing_keys.json — an object mapping chamber name to the list of roster keys a previous run missed. Take the "' + ch + '" list, entries at zero-based indices ' + (chunk * chunkSize) + ' through ' + (chunk * chunkSize + chunkSize - 1) + ' inclusive (the last chunk may run past the end; just do the entries that exist). Then look each of your keys up in rosters/' + ch + '.json to get its word counts and year spans. Work through ALL of them.'
  : 'Read rosters/' + ch + '.json — corpus speaker keys with word counts and year spans, sorted by words spoken (descending, so early indices matter most to the study\'s power). Take entries at zero-based indices ' + (chunk * chunkSize) + ' through ' + (chunk * chunkSize + chunkSize - 1) + ' inclusive. Work through ALL of them.',
'',
'THE KEY IS THE DELIVERABLE\'S SPINE. Return each roster "key" VERBATIM. It is the corpus join key; an altered key makes the record unusable. This study has already lost one collection round to key drift.',
'',
'ONE KEY CAN BE SEVERAL PEOPLE. These are Hansard/Record speaker forms — a US key like "smith" may be different members in different Congresses; the roster\'s first/last years and by_year word counts show the span. Where a key covers more than one person, return ONE RECORD PER PERSON, each with term_first/term_last so key+year resolves to the right person downstream. If you cannot resolve confidently, set ambiguous=true and say why in notes — an honest ambiguity flag is usable, a silent guess poisons the join.',
'',
'SOURCES FOR THIS CHAMBER, in order of preference:',
SOURCES[ch],
'',
'FIELDS: birth_year, gender, education_level (none|secondary|college|bachelor|graduate|professional|unknown), education_field, alma_maters, prior_occupation (VERBATIM — class coding happens centrally, never assign a class yourself), father_occupation and mother_occupation when a source happens to state them.',
'',
'PROVENANCE IS MANDATORY. Every non-unknown value needs an evidence entry: field, tier (official|wikipedia|news|obituary|party|academic|other), url, and a short quote. Values without evidence are dropped at merge — an unrecorded source equals no data. Provenance is what lets every analysis be re-run per source tier.',
'',
'DISCIPLINE: "unknown" is a correct and expected answer. Never infer a value from party, state, or office. Never bypass bot detection or rate limits — if blocked, skip and note it; at least 1 second between requests to any one host. Write nothing outside your structured return.',
'',
'Return every roster entry in your slice, including all-unknown ones — coverage data is data.',
  ].join('\n')
}

phase('Collect')
const jobs = []
for (const c of CH) {
  const chunks = Math.ceil(c.n / c.chunk)
  for (let i = 0; i < chunks; i++) jobs.push({ ch: c.ch, i, size: c.chunk })
}
log(jobs.length + ' collection agents across ' + CH.length + ' chambers')

const results = await parallel(jobs.map(({ ch, i, size }) => () =>
  agent(brief(ch, i, size), { label: ch + ':c' + i, phase: 'Collect',
                              schema: SCHEMA, model: 'sonnet',
                              effort: 'medium' })))

const ok = results.filter(Boolean)
const by = {}
for (const r of ok) {
  by[r.chamber] = by[r.chamber] || { chunks: 0, records: 0, withEdu: 0, withBirth: 0, withOcc: 0 }
  const b = by[r.chamber]
  b.chunks++
  for (const rec of (r.records || [])) {
    b.records++
    if (rec.education_level && rec.education_level !== 'unknown') b.withEdu++
    if (rec.birth_year) b.withBirth++
    if (rec.prior_occupation) b.withOcc++
  }
}
for (const ch of Object.keys(by)) {
  const b = by[ch]
  log(ch + ': ' + b.records + ' records (' + b.withBirth + ' birth, ' +
      b.withEdu + ' edu, ' + b.withOcc + ' occupation) in ' + b.chunks + ' chunks')
}
return { agents: ok.length, by }
