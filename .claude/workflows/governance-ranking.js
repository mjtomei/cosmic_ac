export const meta = {
  name: 'governance-ranking',
  description: 'Rank the 33 governance-and-state-capacity PDFs and build a reading path',
  phases: [
    { title: 'Read', detail: '8 agents read and score the 33 works' },
    { title: 'Path', detail: 'synthesize reading path, side tracks, gaps' },
  ],
}

const PURPOSE = `
THE DIRECTORY'S PURPOSE (score everything against this):
/home/matt/reading/governance-and-state-capacity/ supports the counsel arc of a
position paper ("The Performance Commons" -> "Towards the Cosmic AC") by
Matthew Tomei. The paper's core claim: continuous optimization of computing
systems is an UNDER-PROVIDED PUBLIC GOOD - a collective-action failure, not a
physics limit - and cheap machine intelligence changes the economics of
supplying it. The governance directory carries the INSTITUTIONAL RECORD of an
analogous problem in government: institutions built to SUPPLY counsel (schools
that manufacture a governing class; analytic machinery like PPBS; agencies like
CEA/OTA/CBO), why that capacity DECAYS (proceduralism, administrative burden,
accreted process), and CAPTURE/RENTS economics (Olson, Teles's kludgeocracy,
measured-rents literature) - plus Frischmann on non-rival infrastructure
under-provision, which is the closest PUBLISHED form of the paper's own claim.

Two things the directory exists to hold:
(a) THE CONFIRMED ABSENCE: nothing published bridges policy-capture economics to
    technical under-provision of shared computing infrastructure. The bridge is
    to be ASSEMBLED from Olson 1982 + Frischmann 2005 + Teles 2013, never claimed
    as novel. Project convention: BUILD ON PUBLISHED WORK, DO NOT ARGUE NOVELTY.
(b) THE SHARPEST OBJECTION to the paper's own argument (Teles): automating
    cognition risks "pulling out where the actual discretion and judgment are in
    organizations."

Framing poles, 90 years apart: Harvard Kennedy School on Littauer's 1935 gift -
"a school for A NEW PROFESSIONAL governing class"; Teles on the Johns Hopkins
school he is building now - "serve something like THE ENTIRETY of the governing
class." Same object; DISTRIBUTION named as the reform.

SCORING (be discriminating - a flat distribution is a failed ranking):
  3 = load-bearing. Either supplies a number/quote the paper would cite directly,
      or is structurally necessary to one of the five clusters, or is a genuine
      counter-argument the paper must answer.
  2 = supporting. Real evidence or a useful mechanism, but the argument survives
      without it; read for depth.
  1 = context/background. Worth having on the shelf, not on the path.
Value a work MORE if it is a genuine objection to the paper's thesis. The paper's
convention is that contested findings appear WITH their contest.`

const SCHEMA = {
  type: 'object',
  required: ['works'],
  properties: {
    works: {
      type: 'array',
      items: {
        type: 'object',
        required: ['file', 'title_verified', 'stars', 'cluster', 'one_line', 'why', 'quotable'],
        properties: {
          file: { type: 'string' },
          title_verified: { type: 'string', description: 'actual title+author+venue+year read off the document' },
          stars: { type: 'integer', minimum: 1, maximum: 3 },
          cluster: { type: 'integer', minimum: 1, maximum: 5, description: '1 manufacturing a governing class; 2 analytic machinery installed+abandoned; 3 counsel institutions created+withdrawn; 4 why capable states cannot execute; 5 capture, rents, technical bridge' },
          one_line: { type: 'string', description: 'what it establishes, <=25 words' },
          why: { type: 'string', description: 'why this score, referencing the directory purpose' },
          quotable: { type: 'string', description: 'the single most citable verbatim sentence or figure WITH page number, or "" if none' },
          objection: { type: 'boolean', description: 'true if this work argues AGAINST the paper thesis' },
          caution: { type: 'string', description: 'version traps, contested findings, image-only scans, or "" ' },
        },
      },
    },
  },
}

const DIR = '/home/matt/reading/governance-and-state-capacity'
const BATCHES = [
  ['teles-2013-kludgeocracy.pdf', 'teles-2015-upward-redistribution.pdf', 'olson-1996-big-bills-sidewalk.pdf', 'frischmann-2005-infrastructure-commons.pdf'],
  ['bagley-2019-procedure-fetish.pdf', 'moynihan-2025-rescuing-state-capacity.pdf', 'moynihan-herd-harvey-2015-administrative-burden.pdf', 'yackee-2022-ossification-states.pdf'],
  ['pahlka-2024-wrong-jobs.pdf', 'pahlka-2024-we-have-cancer.pdf', 'dunkelman-2019-penn-station.pdf', 'hsieh-moretti-2019-housing-constraints.pdf', 'greaney-2026-comment-hsieh-moretti.pdf'],
  ['crimson-1935-littauer-gift.pdf', 'crimson-1937-littauer-opens.pdf', 'crimson-1969-mpp-launch.pdf', 'miller-1966-review-scientific-estate.pdf', 'ellwood-2008-policy-school-challenges.pdf'],
  ['ota-act-1972-statute.pdf', 'employment-act-1946-statute.pdf', 'brookings-vital-statistics-congress-staff.pdf', 'lawcontemp-2006-transparency-public-science.pdf'],
  ['zingales-2017-political-theory-firm.pdf', 'gutierrez-philippon-2017-declining-competition.pdf', 'gutierrez-philippon-2018-institutional-drift.pdf', 'furman-orszag-2015-rents-inequality.pdf'],
  ['lemley-2005-free-riding.pdf', 'bessen-nuvolari-2019-diffusing-without-dissipating.pdf', 'boldrin-levine-2013-case-against-patents.pdf'],
  ['shapiro-2001-patent-thicket.pdf', 'hall-ziedonis-2001-patent-paradox.pdf', 'karlson-2021-critique-entrepreneurial-state.pdf', 'irving-2018-ai-safety-via-debate.pdf'],
]

phase('Read')
const batches = await parallel(BATCHES.map((b, i) => () => agent(
  `You are ranking works in a reading directory. ${PURPOSE}

YOUR BATCH (in ${DIR}/):
${b.map(f => '  - ' + f).join('\n')}

For EACH file: actually open it (pdftotext, or pdftoppm+Read for image-only
scans - shapiro-2001-patent-thicket.pdf has NO text layer and hall-ziedonis's
page 1 is a scanned cover, so use pdftoppm -png -r 110 and the Read tool there).
Read enough to judge: abstract/intro, the empirical core, and the conclusion.
DO NOT score from prior knowledge of the paper - score from what you read.

Verify the title/author/venue/year off the document itself and report it in
title_verified; if the filename is WRONG about any of these, say so there
(e.g. yackee is dated 2022 in the filename but published 2024).

For 'quotable', give the single most citable VERBATIM sentence or figure, with a
page number, that this project would actually put in a paper. Prefer concrete
numbers and sharp mechanism sentences over throat-clearing. Verbatim means
verbatim - do not paraphrase into the quote field. Empty string if the work has
nothing worth quoting directly.

Be discriminating with stars. In a batch of 4, it is normal for at most 1-2 to
be a 3.`,
  { label: `read:batch${i + 1}`, phase: 'Read', schema: SCHEMA, model: 'opus' }
)))

const works = batches.filter(Boolean).flatMap(b => b.works || [])
log(`scored ${works.length} works: ${[3,2,1].map(s => works.filter(w => w.stars===s).length + '×' + s).join('  ')}`)

phase('Path')
const path = await agent(
  `${PURPOSE}

Here are all ${works.length} scored works in the directory, as JSON:

${JSON.stringify(works, null, 1)}

Produce the reading-path section of the directory README, in MARKDOWN, matching
the house style of a sibling list (sections: "## The ranking", "## The reading
path - the argument in order", "## Side tracks", "## Gaps the path-builder
surfaced"). Requirements:

1. THE READING PATH is a NUMBERED sequence that builds the ARGUMENT, not the
   chronology and not the star order. Each entry: number, stars, **filename**,
   then one or two sentences saying what it adds AT THAT POINT IN THE ARGUMENT
   and why it comes after the previous one. The path should be walkable by
   someone who reads only the 3s, so mark which entries are skippable.
2. SIDE TRACKS: coherent sub-bundles worth reading together but off the spine
   (e.g. the patent/IP rents set; the abundance-and-its-refutation pair).
   Explain what each track is FOR.
3. GAPS: what the directory still needs. Known-absent and already identified:
   Schick 1973 "A Death in the Bureaucracy" (PPBS obituary), Olson 1982 "The
   Rise and Decline of Nations", Price "The Scientific Estate" 1965 (only a 1966
   review is on disk), Davies "The Unaccountability Machine" 2024, Rivlin,
   Wildavsky, and the OTA closure appropriation line item. Say which of these
   the PATH most needs and why; add any others you infer from what you see.
4. Flag every work marked objection:true prominently - the project's convention
   is that contested findings appear WITH their contest.
5. State the star distribution.

Return ONLY the markdown, no preamble. Do not invent works that are not in the
JSON. Do not soften: if a work is weak for this directory, the path should say
so or leave it off.`,
  { label: 'build-path', phase: 'Path', model: 'opus', effort: 'high' }
)

return { works, path }
