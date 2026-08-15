export const meta = {
  name: 'governance-citgraph-acquire',
  description: 'Fetch the citation-graph acquire-list into the governance directory',
  phases: [{ title: 'Fetch', detail: '5 agents, ~30 works' }],
}

const DIR = '/home/matt/reading/governance-and-state-capacity'
const RULES = `
GROUND RULES:
- Save into ${DIR}/ with the exact filename given.
- Verify: %PDF magic, >50KB, page-1 text matches title/author. Report the
  VERSION you got (published vs working paper) in the note.
- curl with browser UA first; Playwright chromium for Cloudflare/forced
  downloads. KNOWN TECHNIQUE: aeaweb.org (JEP/AER) serves PDFs as browser
  downloads - use pg.expect_download(); goto raises "Download is starting".
  NBER working papers: nber.org/system/files/working_papers/wNNNNN/wNNNNN.pdf.
  JSTOR is blocked - use repositories, author pages, course pages, Wayback.
- NEVER fabricate. status: ok|failed|no_oa with what you tried.
- Return JSON array: [{file, status, source_used, note}].`

phase('Fetch')
const r = await parallel([
  () => agent(`Fetch (seminal foundations). ${RULES}
1. stigler-1971-economic-regulation.pdf - Stigler, "The Theory of Economic Regulation," Bell Journal of Economics 2(1):3-21 (1971). doi:10.2307/3003160. Widely posted on course pages.
2. arrow-1962-welfare-invention.pdf - Arrow, "Economic Welfare and the Allocation of Resources for Invention," in The Rate and Direction of Inventive Activity (NBER/Princeton 1962). OA at nber.org/chapters (c2144).
3. baumol-1990-productive-unproductive.pdf - Baumol, "Entrepreneurship: Productive, Unproductive, and Destructive," JPE 98(5):893-921 (1990). Course pages.
4. wittman-1989-democracies-efficient.pdf - Wittman, "Why Democracies Produce Efficient Results," JPE 97(6):1395-1424 (1989).
5. scotchmer-1991-shoulders-of-giants.pdf - Scotchmer, "Standing on the Shoulders of Giants," JEP 5(1):29-41 (1991). AEA download technique.
6. dixit-olson-2000-coase-theorem.pdf - Dixit & Olson, "Does voluntary participation undermine the Coase Theorem?" J. Public Economics 76(3):309-335 (2000).`,
   { label: 'fetch:seminal', phase: 'Fetch' }),

  () => agent(`Fetch (the bridge planks). ${RULES}
1. holmes-schmitz-1995-resistance-new-technology.pdf - Holmes & Schmitz, "Resistance to New Technology and Trade Between Areas," Minneapolis Fed Quarterly Review 19(1) (1995). OA at minneapolisfed.org.
2. akcigit-baslandze-lotti-2023-connecting-to-power.pdf - Akcigit, Baslandze & Lotti, "Connecting to Power: Political Connections, Innovation, and Firm Dynamics," Econometrica 91(2) (2023). NBER w25136 or Atlanta Fed WP version OK.
3. bessen-2020-industry-concentration-it.pdf - Bessen, "Industry Concentration and Information Technology," J. Law & Economics 63(3) (2020). BU/SSRN version OK.
4. karna-karlsson-engberg-2022-political-failure.pdf - Kärnä, Karlsson & Engberg, "Political failure: a missing piece in innovation policy analysis," Economics of Innovation and New Technology 32(7) (2022/2023). Ratio Institute WP version OK; T&F may be OA.
5. goodman-lehto-2023-knowledge-commons.pdf - Goodman & Lehto, "Intellectual property, complex externalities, and the knowledge commons," Public Choice (2023). doi:10.1007/s11127-023-01110-8.
6. mckelvey-2025-genai-commons.pdf - The McKelvey et al. 2025 paper on generative AI driving commons closure (surfaced from the Shapiro seed in 00-CITATION-GRAPH.json - check that file's oa_hint for the exact handle; fetch whatever version exists).`,
   { label: 'fetch:bridge', phase: 'Fetch' }),

  () => agent(`Fetch (appropriability + collective invention). ${RULES}
1. levin-1987-appropriating-returns.pdf - Levin, Klevorick, Nelson & Winter, "Appropriating the Returns from Industrial Research and Development," Brookings Papers on Economic Activity 1987(3):783-831. Brookings OA.
2. cohen-nelson-walsh-2000-protecting-assets.pdf - Cohen, Nelson & Walsh, "Protecting Their Intellectual Assets," NBER w7552 (2000). NBER OA.
3. allen-1983-collective-invention.pdf - Allen, "Collective invention," J. Economic Behavior & Organization 4(1):1-24 (1983). Course pages/repositories.
4. vonhippel-1987-knowhow-trading.pdf - von Hippel, "Cooperation between Rivals: Informal Know-How Trading," Research Policy 16(6):291-302 (1987). evhippel.mit.edu hosts his papers.
5. heller-eisenberg-1998-anticommons.pdf - Heller & Eisenberg, "Can Patents Deter Innovation? The Anticommons in Biomedical Research," Science 280:698-701 (1998). Repositories (umich).
6. merges-1996-contracting-liability-rules.pdf - Merges, "Contracting into Liability Rules," California Law Review 84(5):1293 (1996). californialawreview.org / berkeley escholarship OA.
7. bessen-maskin-2009-sequential-innovation.pdf - Bessen & Maskin, "Sequential innovation, patents, and imitation," RAND J. Economics 40(4):611-635 (2009). Harvard/MIT/IAS repositories.`,
   { label: 'fetch:appropriability', phase: 'Fetch' }),

  () => agent(`Fetch (rents, dynamism, macro). ${RULES}
1. ansolabehere-2003-so-little-money.pdf - Ansolabehere, de Figueiredo & Snyder, "Why Is There So Little Money in U.S. Politics?" JEP 17(1) (2003). AEA download technique or MIT OA.
2. hacker-2004-privatizing-risk.pdf - Hacker, "Privatizing Risk without Privatizing the Welfare State," APSR 98(2):243-260 (2004). Repositories.
3. akcigit-ates-2023-business-dynamism.pdf - Akcigit & Ates, "What Happened to US Business Dynamism?" JPE 131(8) (2023). NBER w25756 OK.
4. galasso-schankerman-2014-patents-cumulative.pdf - Galasso & Schankerman, "Patents and Cumulative Innovation: Causal Evidence from the Courts," QJE 129(4) (2014). LSE eprints OA.
5. autor-2020-superstar-firms.pdf - Autor, Dorn, Katz, Patterson & Van Reenen, "The Fall of the Labor Share and the Rise of Superstar Firms," QJE 135(2) (2020). MIT OA / NBER w23396.
6. callander-foarta-sugaya-2022-market-political.pdf - Callander, Foarta & Sugaya, "Market Competition and Political Influence," Econometrica 90(6) (2022). Stanford GSB WP version OK.
7. lancieri-posner-zingales-2022-antitrust-decline.pdf - Lancieri, Posner & Zingales, "The Political Economy of the Decline of Antitrust Enforcement," NBER w30326 (2022). NBER OA.
8. brynjolfsson-rock-syverson-2017-productivity-paradox.pdf - Brynjolfsson, Rock & Syverson, "Artificial Intelligence and the Modern Productivity Paradox," NBER w24001 (2017). NBER OA.`,
   { label: 'fetch:rents-macro', phase: 'Fetch' }),

  () => agent(`Fetch (objections + procedure). ${RULES}
1. mccubbins-noll-weingast-1987-administrative-procedures.pdf - McCubbins, Noll & Weingast, "Administrative Procedures as Instruments of Political Control," JLEO 3(2):243-277 (1987). Repositories/course pages (JSTOR blocked).
2. yackee-yackee-2009-ossification-federal.pdf - Yackee & Yackee, "Administrative Procedures and Bureaucratic Performance: Is Federal Rule-making 'Ossified'?" JPART 20(2):261-282 (2010; online 2009). doi:10.1093/jopart/mup011. Repositories.
3. becker-1983-pressure-groups.pdf - Becker, "A Theory of Competition Among Pressure Groups for Political Influence," QJE 98(3):371-400 (1983). Course pages.
4. kitsikopoulos-2023-cornish-patents.pdf - The Kitsikopoulos 2023 work re-reading the Cornish steam-engine case toward the patent system (surfaced from the Bessen-Nuvolari seed - check 00-CITATION-GRAPH.json in ${DIR} for the exact handle and oa_hint).
5. duranton-puga-2023-urban-growth.pdf - Duranton & Puga, "Urban Growth and Its Aggregate Implications," Econometrica 91(6) (2023). CEPR/Wharton WP version OK.
6. elhauge-1991-interest-group-theory.pdf - Elhauge, "Does Interest Group Theory Justify More Intrusive Judicial Review?" Yale L.J. 101(1):31-110 (1991). Yale LJ / Harvard repositories.
7. hinterleitner-2023-growth-of-policies.pdf - Hinterleitner, Knill & Steinebach, "The growth of policies, rules, and regulations: a review," Regulation & Governance (2023). Wiley may be OA (check); else repository.`,
   { label: 'fetch:objections', phase: 'Fetch' }),
])
return r.filter(Boolean)
