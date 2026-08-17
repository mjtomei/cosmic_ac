export const meta = {
  name: 'missing9-covariates',
  description: 'Birth, education and occupation for the 9 chambers with no member covariates: 6 Australian states + Scotland, Wales, Northern Ireland',
  phases: [
    { title: 'Collect', detail: 'per-chamber roster slices, all sources with provenance' },
  ],
}

// WHY THIS RUN EXISTS
//
// The class and education arms are POWER-BOUND, not null. In the joint
// member-level model (cohort + class + education + prominence, n = 2,989) the
// class II-over-I crossover falls to t = 1.26 and the education ladder to
// t = 0.65 once cohort is controlled -- but cohort is collinear with both
// (class I skews older; later-born members are more educated), so the joint
// model cannot separate them at current n. These nine chambers have member
// covariates for nobody, and adding them is the cheapest available power.
//
// args: { chambers: [{ch: "NSW", n: 356, chunk: 50}, ...] }
const ARGS = {"chambers": [{"ch": "QLD", "n": 50, "chunk": 50}, {"ch": "SA", "n": 179, "chunk": 50}, {"ch": "TAS", "n": 85, "chunk": 50}, {"ch": "VIC", "n": 440, "chunk": 50}, {"ch": "WA", "n": 321, "chunk": 50}, {"ch": "NI", "n": 258, "chunk": 50}, {"ch": "SCO", "n": 315, "chunk": 50}, {"ch": "WAL", "n": 154, "chunk": 50}]}   // baked in at launch (round 2: remaining keys only)
const CH = ARGS.chambers || []
if (!CH.length) throw new Error('no chambers in args — got: ' + JSON.stringify(args).slice(0, 200))

const AU_COMMON = [
  'Wikipedia and Wikidata are the realistic PRIMARY source for birth year and education in these chambers — use them, and tier the evidence honestly as "wikipedia".',
  'The parliament\'s own former-members register is the authority for IDENTITY and term dates; prefer it whenever the roster key is ambiguous.',
].join('\n')

const SOURCES = {
  NSW: [
    'Parliament of New South Wales former-members register (parliament.nsw.gov.au) — one biographical page per member, with electorate and service dates, often occupation before politics. Tier: official.',
    AU_COMMON,
  ].join('\n'),
  QLD: [
    'The Queensland Parliament former-members record (parliament.qld.gov.au) and the Queensland "Re-Member" former-members database, which carries occupation and service dates. Tier: official.',
    AU_COMMON,
  ].join('\n'),
  SA: [
    'Parliament of South Australia members pages (parliament.sa.gov.au). Tier: official.',
    'NOTE ON KEYS: South Australian Hansard prints members as initials plus surname ("a. koutsantonis", "a.l. mclachlan"). Resolve the initials to the full person via the parliament register before searching further; do not skip a key because it is abbreviated.',
    AU_COMMON,
  ].join('\n'),
  TAS: [
    'Parliament of Tasmania members pages (parliament.tas.gov.au). Tier: official.',
    AU_COMMON,
  ].join('\n'),
  VIC: [
    'The Parliament of Victoria "Re-Member" database (parliament.vic.gov.au) — a former-members biographical database with occupation, education and service dates. This is the best single source in any of these nine chambers; use it first. Tier: official.',
    AU_COMMON,
  ].join('\n'),
  WA: [
    'Parliament of Western Australia members pages (parliament.wa.gov.au), and the Biographical Register of Members of the Parliament of Western Australia. Tier: official.',
    'NOTE ON KEYS: WA Hansard prints members as initials plus surname ("a.d. buti" is Tony Buti, "a.j. carpenter" is Alan Carpenter). Resolve initials via the parliament register first; these are real members, not junk keys.',
    AU_COMMON,
  ].join('\n'),
  NI: [
    'The Northern Ireland Assembly members site (aims.niassembly.gov.uk / niassembly.gov.uk) for identity, party and mandate dates. Tier: official.',
    'Wikipedia for birth year, education and prior occupation. Tier: wikipedia.',
    'Keys are Hansard forms, often surname-only ("a maginness" is Alban Maginness). Several members served across suspensions of the Assembly — use the roster year spans.',
  ].join('\n'),
  SCO: [
    'The Scottish Parliament MSP pages (parliament.scot), which cover current and former MSPs with session membership. Tier: official.',
    'Wikipedia/Wikidata for birth year and education — for MSPs this is usually the only education source. Tier: wikipedia.',
    'Keys are full names ("adam tomkins", "aileen campbell"), so identity is usually unambiguous.',
  ].join('\n'),
  WAL: [
    'The Senedd / Welsh Parliament members site (senedd.wales) and its members register. Tier: official.',
    'Wikipedia/Wikidata for birth year, education and prior occupation. Tier: wikipedia.',
    'Keys are full names ("adam price", "aled roberts"). Some members appear in both Welsh and English forms of the record; the roster key is the join key regardless.',
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
          term_first: { type: 'integer', description: 'first year this PERSON held the seat' },
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
'Collect biographical covariates for legislators in the ' + ch + ' chamber, for study S10.',
'',
'YOUR SLICE',
'',
'All file paths below are relative to /home/mjtomei/s10_missing9b — read them from there.',
'',
'Read rosters/' + ch + '.json — corpus speaker keys with word counts and year spans, sorted by words spoken (descending, so early indices matter most to the study\'s power). Take entries at zero-based indices ' + (chunk * chunkSize) + ' through ' + (chunk * chunkSize + chunkSize - 1) + ' inclusive (the last chunk may run past the end; just do the entries that exist). Work through ALL of them.',
'',
'THE KEY IS THE DELIVERABLE\'S SPINE. Return each roster "key" VERBATIM. It is the corpus join key; an altered key makes the record unusable. This study has already lost one collection round to key drift.',
'',
'ONE KEY CAN BE SEVERAL PEOPLE. These are Hansard speaker forms, and a surname key may cover more than one member across decades; the roster\'s first/last years and by_year counts show the span. Where a key covers more than one person, return ONE RECORD PER PERSON, each with term_first/term_last so key+year resolves to the right person downstream. If you cannot resolve confidently, set ambiguous=true and say why in notes — an honest ambiguity flag is usable, a silent guess poisons the join.',
'',
'SOURCES FOR THIS CHAMBER, in order of preference:',
SOURCES[ch],
'',
'FIELDS: birth_year, gender, education_level (none|secondary|college|bachelor|graduate|professional|unknown), education_field, alma_maters, prior_occupation (VERBATIM — class coding happens centrally, never assign a class yourself), father_occupation and mother_occupation when a source happens to state them.',
'',
'EDUCATION LEVEL IS THE SCARCE FIELD and the one this run most needs, so spend your effort there: "bachelor" for a first degree, "graduate" for a masters or doctorate, "professional" for law/medicine/accountancy qualifications, "college" for sub-degree tertiary, "secondary" where a source states schooling ended there. Do not guess from occupation — a lawyer whose degree is unrecorded is education_level "unknown" with prior_occupation "lawyer".',
'',
'PROVENANCE IS MANDATORY. Every non-unknown value needs an evidence entry: field, tier (official|wikipedia|news|obituary|party|academic|other), url, and a short quote. Values without evidence are dropped at merge — an unrecorded source equals no data.',
'',
'DISCIPLINE: "unknown" is a correct and expected answer. Never infer a value from party, electorate, or office. Never bypass bot detection or rate limits — if blocked, skip and note it; at least 1 second between requests to any one host. Write nothing outside your structured return.',
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
