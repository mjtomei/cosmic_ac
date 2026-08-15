export const meta = {
  name: 'artificial-persons-ranking',
  description: 'Rank the 21 artificial-persons PDFs and build a reading path',
  phases: [
    { title: 'Read', detail: '5 agents read and score 21 works' },
    { title: 'Path', detail: 'synthesize reading path, side tracks, gaps' },
  ],
}

const PURPOSE = `
THE DIRECTORY'S PURPOSE (score everything against this):
/home/matt/reading/artificial-persons/ supports two theses in a position paper
("Towards the Cosmic AC" by Matthew Tomei), both about machine counsel in
governance. Unifying claim: GOD, KING, CORPORATION, AND STATE ARE THE SAME
OBJECT - a collective intelligence personified, with humans as the
instantiation medium - and the machine version is the first instantiation that
can SHOW ITS WORK.

Thesis 1 (the tulpa thesis): the US president is not a sovereign individual but
"a kind of tulpa for the leader of the United States"; rotation between humans
prevents the individual leaking into the instantiation (term limits as
regularisation). This answers the objection (Teles) that automating cognition
"pulls out where the actual discretion and judgment are in organizations" -
the chief offices of government were never essentially human tasks; their
design actively suppresses the individual.

Thesis 2 (the shared-lie thesis): one function of belief in a higher power
"directly watching you as an individual" is to compensate for the real
orientation-toward-good structures being too hard to see for most people;
machine counsel is a literal instantiation of those structures, legible at any
competence level. The fear it answers: freer information produces nihilism.
The panopticon worry is answered by symmetry: the worry requires a power
imbalance, which the design removes (the powerful become the most-watched).

Conventions: build on published work, never argue novelty; contested findings
appear WITH their contest; genuine objections to the theses score HIGHER, not
lower.

SCORING (be discriminating):
  3 = load-bearing: supplies a quote/number/doctrine the paper would cite
      directly, or is structurally necessary, or is a genuine counter-argument.
  2 = supporting: real evidence or mechanism; the argument survives without it.
  1 = context/background.`

const SCHEMA = { type: 'object', required: ['works'], properties: {
  works: { type: 'array', items: { type: 'object',
    required: ['file', 'title_verified', 'stars', 'cluster', 'one_line', 'why', 'quotable'],
    properties: {
      file: { type: 'string' },
      title_verified: { type: 'string', description: 'actual title+author+venue+year read off the document; note if filename misleads' },
      stars: { type: 'integer', minimum: 1, maximum: 3 },
      cluster: { type: 'integer', minimum: 1, maximum: 5, description: '1 doctrine (two bodies, artificial man, corporate personhood); 2 group agency formal; 3 cybernetics/handover; 4 watching god measured; 5 panopticon and inversion' },
      one_line: { type: 'string', description: 'what it establishes, <=25 words' },
      why: { type: 'string' },
      quotable: { type: 'string', description: 'most citable VERBATIM sentence with page/section, or ""' },
      objection: { type: 'boolean' },
      caution: { type: 'string' },
    } } } } }

const DIR = '/home/matt/reading/artificial-persons'
const BATCHES = [
  ['hobbes-1651-leviathan.pdf', 'plato-republic-jowett.pdf', 'dartmouth-v-woodward-1819.pdf', 'shortall-2023-kings-two-bodies-secularization.pdf'],
  ['french-1979-corporation-moral-person.pdf', 'list-2018-group-agent-what-is-it-like.pdf', 'beer-vsm-provenance.pdf', 'runciman-corporations-ai-essay.pdf'],
  ['purzycki-2016-moralistic-gods.pdf', 'shariff-norenzayan-2007-god-is-watching.pdf', 'norenzayan-shariff-2008-religious-prosociality.pdf', 'northover-2017-watching-eyes-meta.pdf'],
  ['johnson-kruger-2004-good-of-wrath.pdf', 'zuckerman-2009-atheism-secularity-wellbeing.pdf', 'durkheim-1912-elementary-forms.pdf', 'voltaire-1768-epitre-trois-imposteurs.pdf', 'nietzsche-gay-science-125-madman.pdf'],
  ['bentham-1791-panopticon.pdf', 'foucault-panopticism-chapter.pdf', 'brin-1996-transparent-society-essay.pdf', 'mann-nolan-wellman-2003-sousveillance.pdf'],
]

phase('Read')
const batches = await parallel(BATCHES.map((b, i) => () => agent(
  `You are ranking works in a reading directory. ${PURPOSE}

YOUR BATCH (in ${DIR}/):
${b.map(f => '  - ' + f).join('\n')}

For EACH file: actually open it (pdftotext; for image-only scans -
bentham-1791-panopticon.pdf has NO text layer - use pdftoppm -png -r 110 on
selected pages and the Read tool). For the long primary texts (Hobbes, Plato,
Durkheim, Nietzsche) do NOT read the whole book: locate and read the relevant
passages (Leviathan ch. 16; Republic Book III noble-lie passage around
"audacious fiction"; Durkheim's conclusion + the society-worships-itself
argument; Gay Science section 125) plus enough surrounding context to judge.
DO NOT score from prior knowledge - score from what you read. NOTE for
Nietzsche: this is Thomas Common's 1910 translation ("Where is God gone?") -
record his actual wording, not Kaufmann's.

Verify title/author/venue/year off the document; if the filename misleads,
say so in title_verified. For 'quotable': VERBATIM, with page or section
number, the single sentence this paper would actually print. Be discriminating
with stars: in a batch of 4-5, 1-2 threes is normal.`,
  { label: `read:batch${i + 1}`, phase: 'Read', schema: SCHEMA, model: 'opus' }
)))

const works = batches.filter(Boolean).flatMap(b => b.works || [])
log(`scored ${works.length} works: ${[3,2,1].map(s => works.filter(w => w.stars===s).length + '×' + s).join('  ')}`)

phase('Path')
const path = await agent(
  `${PURPOSE}

All ${works.length} scored works, as JSON:

${JSON.stringify(works, null, 1)}

Produce the reading-path section of the directory README in MARKDOWN, matching
the house style (sections: "## The ranking", "## The reading path - the
argument in order", "## Side tracks", "## Gaps the path-builder surfaced").
Rules: numbered path that builds the ARGUMENT (not chronology); 3s alone must
be a complete walk, mark 2s/1s "(skippable)"; flag every objection:true work
prominently; state the star distribution; side tracks = coherent off-spine
bundles; gaps = what the directory still needs, knowing the purchase list
already holds Kantorowicz 1957, List & Pettit 2011, Norenzayan 2013, Runciman
2023, Davies 2024, Brin 1998, Foucault 1975, Zuckerman 2008 (books, no OA).
Do not invent works not in the JSON. Return ONLY the markdown.`,
  { label: 'build-path', phase: 'Path', model: 'opus', effort: 'high' }
)

return { works, path }
