export const meta = {
  name: 'security-economics-acquire',
  description: 'Fetch the security-economics citation-sweep acquire list into ~/reading/security-economics',
  phases: [{ title: 'Fetch', detail: '10 agents, ~80 works' }],
}

const DIR = '/home/matt/reading/security-economics'
const RULES = `
GROUND RULES:
- Save into ${DIR}/ with the exact filename given.
- Verify: %PDF magic, >50KB, page-1 text matches title/author. Report the
  VERSION you got (published vs working paper) in the note.
- curl with a browser User-Agent first; if a site forces browser downloads or
  Cloudflare-blocks, note it and try mirrors instead. KNOWN TECHNIQUES:
  arXiv: https://arxiv.org/pdf/<id> always works. NBER working papers:
  nber.org/system/files/working_papers/wNNNNN/wNNNNN.pdf. RAND landing pages
  bot-block but the direct PDF often lives at
  rand.org/content/dam/rand/pubs/<series>/.../<ID>.pdf — find it via the
  landing page HTML or search. OUP Journal of Cybersecurity is gold OA but
  bot-blocks its PDF links — try the academic.oup.com/cybersecurity
  article-pdf deep link with a browser UA, then Wayback, then repository
  copies. JSTOR is blocked — use repositories, author pages, course pages,
  Wayback. SSRN delivery links need the ?abstractid= download form — try
  papers.ssrn.com/sol3/Delivery.cfm patterns or repository mirrors.
- NEVER fabricate a file. status: ok|failed|no_oa with what you tried.
- Return JSON array: [{file, status, source_used, note}].`

phase('Fetch')
const r = await parallel([
  () => agent(`Fetch (Fable-Carson scholarly seeds, part 1 — mostly arXiv, easy). ${RULES}
1. malavasi-etal-2022-cyber-frequency-severity.pdf - arXiv:2111.03366 (Malavasi, Peters, Shevchenko et al., "Cyber risk frequency, severity and insurance viability")
2. wheatley-hofmann-sornette-2019-catastrophe-framework.pdf - arXiv:1901.00699 ("Data breaches in the catastrophe framework and beyond")
3. chen-embrechts-wang-2024-infinite-mean-risk.pdf - arXiv:2408.08678 ("Infinite-mean models in risk management")
4. edwards-hofmeyr-forrest-2016-hype-heavy-tails.pdf - J. Cybersecurity 2(1) doi:10.1093/cybsec/tyw003, gold OA (OUP technique above)
5. von-skarczinski-etal-2023-german-max-losses.pdf - Geneva Papers 48(2):463, OA at PubMed Central PMC10100641 (pmc.ncbi.nlm.nih.gov/articles/PMC10100641/ has a PDF link)
6. bouveret-2018-cyber-risk-financial-sector.pdf - IMF Working Paper WP/18/143, free at imf.org
7. dreyer-etal-2018-rand-global-cost.pdf - RAND RR-2299 (RAND technique above)
8. jamilov-rey-tahoun-2026-anatomy-cyber-risk.pdf - "The Anatomy of Cyber Risk," Journal of Finance 2026; earlier NBER WP w28906 / SSRN 3866338 versions acceptable (note version)`,
   { label: 'fetch:seeds-1', phase: 'Fetch' }),

  () => agent(`Fetch (EVT/severity cluster, part 1). ${RULES}
1. maillart-sornette-2010-heavy-tailed-cyber-risks.pdf - arXiv:0803.2256
2. wheatley-maillart-sornette-2016-extreme-risk-data-breaches.pdf - arXiv:1505.07684
3. farkas-lopez-thomas-2021-gpd-regression-trees.pdf - https://hal.science/hal-02118080/document
4. chen-embrechts-wang-2024-stochastic-dominance.pdf - arXiv:2208.08471 ("An Unexpected Stochastic Dominance", Operations Research)
5. dacorogna-debbabi-kratz-2023-cyber-resilience-heavy-tails.pdf - ESSEC HAL: https://essec.hal.science/hal-03774108 (download the working-paper PDF from the HAL record; SSRN 4215907 is an alternative)
6. zeller-scherer-2022-marked-point-processes-cyber.pdf - https://link.springer.com/content/pdf/10.1007/s13385-021-00290-1.pdf (EAJ, OA)
7. neslehova-embrechts-chavezdemoulin-2006-infinite-mean-lda.pdf - J. Operational Risk 1(1); paywalled, but Embrechts posts at people.math.ethz.ch/~embrecht/ (look for "Infinite mean models and the LDA for operational risk")
8. chavezdemoulin-embrechts-hofert-2016-evt-covariates.pdf - J. Risk & Insurance 83(3):735; try Embrechts' ETH page or HEC Lausanne repository (Chavez-Demoulin)`,
   { label: 'fetch:evt-1', phase: 'Fetch' }),

  () => agent(`Fetch (EVT/severity cluster, part 2 — the hunts). ${RULES}
1. eling-wirfs-2019-actual-costs-cyber-risk.pdf - EJOR 272(3):1109; try St. Gallen Alexandria repository (alexandria.unisg.ch, "What are the actual costs of cyber risk events?"), else author page / ResearchGate
2. eling-loperfido-2017-data-breaches-goodness-of-fit.pdf - IME 75:126; St. Gallen Alexandria or SSRN
3. eling-jung-2018-copula-data-breach-losses.pdf - IME 82:167; St. Gallen Alexandria or SSRN
4. jung-2021-extreme-data-breach-losses-pml.pdf - NAAJ 25(4):580 "Extreme Data Breach Losses"; WARNING: the OpenAlex-indexed 'OA' link is a mislabeled insurance-industry report — verify page-1 is the actual Jung paper. Try SSRN/author page (Kwangmin Jung, Drake University / POSTECH).
5. xu-etal-2018-hacking-breach-trends.pdf - "Modeling and predicting cyber hacking breaches," IEEE TIFS 2018 (Maochao Xu, Kristin Schweitzer, Raymond Bateman, Shouhuai Xu); try Shouhuai Xu's publication page or citeseerx
6. embrechts-kluppelberg-mikosch-1997-modelling-extremal-events.pdf - Springer book; only fetch if a LEGITIMATE full copy exists openly (it usually does not) — no_oa is the expected answer; do not fetch pirate copies from libgen-style hosts.
7. eling-2020-cyber-risk-research-review.pdf - European Actuarial Journal 10:303 "Cyber risk research in business and actuarial science"; Springer paywalled — try St. Gallen Alexandria
8. eling-schnell-2016-what-do-we-know.pdf - J. Risk Finance 17(5) "What do we know about cyber risk and cyber risk insurance?"; St. Gallen Alexandria or SSRN`,
   { label: 'fetch:evt-2', phase: 'Fetch' }),

  () => agent(`Fetch (infosec-economics canon). ${RULES}
1. anderson-2001-why-infosec-hard.pdf - https://www.acsac.org/2001/papers/110.pdf (mirror: cl.cam.ac.uk/~rja14/Papers/econ.pdf)
2. anderson-moore-2006-economics-infosec-science.pdf - https://www.cl.cam.ac.uk/~rja14/Papers/sciecon2.pdf
3. anderson-moore-2009-cs-econ-psych.pdf - https://www.cl.cam.ac.uk/~rja14/Papers/toulouse.pdf (extended survey version)
4. gordon-loeb-2002-economics-infosec-investment.pdf - ACM TISSEC 5(4):438-457; ACM paywalled — try Lawrence Gordon's UMD page, course mirrors (widely posted), CiteSeerX
5. anderson-etal-2012-measuring-cost-cybercrime.pdf - https://tylermoore.utulsa.edu/weis12.pdf
6. anderson-etal-2019-changing-cost-cybercrime.pdf - https://weis2019.econinfosec.org/wp-content/uploads/sites/6/2019/05/WEIS_2019_paper_25.pdf
7. herley-2009-so-long-externalities.pdf - https://www.nspw.org/papers/2009/nspw2009-herley.pdf
8. moore-clayton-anderson-2009-economics-online-crime.pdf - https://tylermoore.utulsa.edu/jep09.pdf
9. moore-2010-economics-cybersecurity-policy.pdf - IJCIP 3(3-4) "The economics of cybersecurity: Principles and policy options"; try tylermoore.utulsa.edu publications page.
NOTE: Varian 2004 and Akerlof 1970 are already on disk in ~/reading/software-economies-and-the-knowledge-problem/ — do NOT re-fetch.`,
   { label: 'fetch:canon', phase: 'Fetch' }),

  () => agent(`Fetch (insurance/correlation cluster, part 1). ${RULES}
1. kunreuther-heal-2003-interdependent-security.pdf - https://www.nber.org/system/files/working_papers/w8871/w8871.pdf
2. geer-etal-2003-cyberinsecurity-cost-of-monopoly.pdf - https://www.ccianet.org/wp-content/uploads/2003/09/cyberinsecurity%20the%20cost%20of%20monopoly.pdf
3. bohme-schwartz-2010-modeling-cyber-insurance.pdf - https://informationsecurity.uibk.ac.at/pdfs/BS2010_Modeling_Cyber-Insurance_WEIS.pdf
4. bohme-kataria-2006-correlation-cyber-insurance.pdf - WEIS 2006; known text mirror at archive.nyu.edu/bitstream/2451/14997/ (try the sibling .pdf bitstream of the .pdf.txt); also Rainer Bohme's uibk page informationsecurity.uibk.ac.at/pdfs/
5. bohme-2005-cyber-insurance-revisited.pdf - WEIS 2005; the WEIS archive is DEAD — this is the hard one. Try: Wayback Machine of infosecon.net/workshop/pdf/15.pdf and weis2005 URLs, Bohme's uibk publications page, CiteSeerX. Report failed honestly if nothing verifies.
6. biener-eling-wirfs-2015-insurability-cyber-risk.pdf - https://www.internationalinsurance.org/sites/default/files/2018-03/Insurability%20of%20Cyber%20Risk.pdf (Geneva Association report version — note it)
7. awiszus-etal-2023-idiosyncratic-systematic-systemic.pdf - arXiv:2209.07415
8. hillairet-lopez-2021-cyber-propagation-portfolio.pdf - https://inria.hal.science/hal-02564462/document`,
   { label: 'fetch:insurance-1', phase: 'Fetch' }),

  () => agent(`Fetch (insurance/correlation cluster, part 2). ${RULES}
1. welburn-strong-2022-systemic-cyber-risk.pdf - Risk Analysis 42(8); RAND external pub EP68520 (RAND technique), else Wiley OA check, else RAND WP version WR-1311
2. romanosky-etal-2019-content-analysis-cyber-policies.pdf - J. Cybersecurity 5(1) doi:10.1093/cybsec/tyz002, gold OA (OUP technique)
3. eisenbach-kovner-lee-2022-cyber-us-financial-system.pdf - https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr909.pdf (staff-report version — note it)
4. shetty-etal-2010-competitive-cyber-insurance.pdf - WEIS 2009 / Springer chapter "Competitive Cyber-Insurance and Internet Security"; try Galina Schwartz's Berkeley page, WEIS 2009 archive via Wayback, CiteSeerX
5. marotta-etal-2017-cyber-insurance-survey.pdf - Computer Science Review 24:35; try IIT-CNR (Martinelli) institutional page or ResearchGate
6. braun-eling-jaenicke-2023-cyber-ils.pdf - ASTIN Bulletin 53(3):684 "Cyber Insurance-Linked Securities"; try St. Gallen Alexandria, SSRN
7. cremer-etal-2022-data-availability.pdf - https://link.springer.com/content/pdf/10.1057/s41288-022-00266-6.pdf (Geneva Papers, OA)
8. zeller-scherer-2024-risk-mismeasurement.pdf - Zeller & Scherer, European Actuarial Journal 14:711-748 (2024), the systemic-risk mismeasurement paper (S16 anchor); Springer — check OA, else arXiv/TUM repository`,
   { label: 'fetch:insurance-2', phase: 'Fetch' }),

  () => agent(`Fetch (cost-measurement cluster). ${RULES}
1. florencio-herley-2011-sex-lies-cybercrime-surveys.pdf - https://cormac.herley.org/docs/SexLiesandCybercrimeSurveys.pdf
2. romanosky-2016-costs-causes-cyber-incidents.pdf - J. Cybersecurity 2(2) doi:10.1093/cybsec/tyw001, gold OA (OUP technique)
3. woods-bohme-2021-sok-quantifying-cyber-risk.pdf - https://oaklandsok.github.io/papers/woods2021pre.pdf (mirror: informationsecurity.uibk.ac.at/pdfs/WB2020_sok_cyberrisk_snp.pdf)
4. levi-2017-economic-cybercrimes.pdf - Cardiff ORCA: https://orca.cardiff.ac.uk/id/eprint/88097/ (download the deposited PDF)
5. aldasoro-etal-2022-drivers-of-cyber-risk.pdf - https://www.bis.org/publ/work865.pdf (BIS WP version — note it)
6. riek-bohme-2018-consumer-facing-cybercrime.pdf - J. Cybersecurity 4(1) doi:10.1093/cybsec/tyy004, gold OA (OUP technique)
7. kamiya-etal-2021-cyberattacks-target-firms.pdf - JFE 139(3):719; OpenAlex marks the ScienceDirect version OA (S0304405X20300143); else NBER w24409 / Fisher College WP version
8. campbell-gordon-loeb-zhou-2003-economic-cost-breaches.pdf - J. Computer Security 11(3); paywalled — CiteSeerX or course mirrors
9. cavusoglu-mishra-raghunathan-2004-breach-announcements.pdf - IJEC 9(1); paywalled — try UT Dallas author pages, CiteSeerX`,
   { label: 'fetch:measurement', phase: 'Fetch' }),

  () => agent(`Fetch (headline numbers + event-study extras). ${RULES}
1. csis-mcafee-2014-net-losses.pdf - verified mirror: https://afyonluoglu.org/PublicWebFiles/Reports-CS/2014%20McAfee%20THE%20GLOBAL%20COST%20of%20CYBERCRIME.pdf (else csis.org)
2. detica-2011-cost-of-cyber-crime.pdf - https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/60943/the-cost-of-cyber-crime-full-report.pdf
3. gordon-loeb-zhou-2011-downward-shift.pdf - J. Computer Security 19(1):33 "The impact of information security breaches: Has there been a downward shift in costs?"; CiteSeerX / UMD course mirrors
4. acquisti-friedman-telang-2006-privacy-breach-event-study.pdf - ICIS 2006 "Is There a Cost to Privacy Breaches? An Event Study"; try Acquisti's CMU Heinz page (heinz.cmu.edu/~acquisti) or AIS eLibrary
5. herley-florencio-2010-nobody-sells-gold.pdf - "Nobody Sells Gold for the Price of Silver" WEIS 2009; cormac.herley.org/docs/ hosts most of his papers
6. wolff-lehr-2017-degrees-of-ignorance.pdf - TPRC45; the only verified copy is the abstract-as-submitted at law.upenn.edu (live/files/6549...) — fetch it but note it may be the abstract, and try SSRN 2943867 for the full paper
7. hyman-2013-cybercrime-how-serious.pdf - CACM 56(3); cacm.acm.org serves the article — if only HTML exists, status no_oa with the URL noted`,
   { label: 'fetch:headline-nums', phase: 'Fetch' }),

  () => agent(`Fetch (vulnerability-markets cluster). ${RULES}
1. ozment-2004-bug-auctions.pdf - https://www.dtc.umn.edu/weis2004/ozment.pdf
2. rescorla-2005-finding-security-holes.pdf - https://www.dtc.umn.edu/weis2004/rescorla.pdf (WEIS 2004 version — note it)
3. kannan-telang-2005-market-vulnerabilities-think-again.pdf - http://archive.nyu.edu/bitstream/2451/15005/2/InfoSec_ISR_Kannan%2bTelang.pdf
4. ozment-schechter-2006-milk-or-wine.pdf - https://www.usenix.org/legacy/event/sec06/tech/full_papers/ozment/ozment.pdf
5. arora-telang-xu-2008-optimal-disclosure-policy.pdf - Management Science 54(4); SSRN 669023 working version (papers.ssrn.com/sol3/papers.cfm?abstract_id=669023) or Heinz CMU repository
6. arora-krishnan-telang-yang-2010-patch-release-behavior.pdf - ISR 21(1):115; the CMU preprint link is dead — try SSRN, CiteSeerX, Telang's Heinz page
7. beattie-etal-2002-timing-security-patches.pdf - https://www.usenix.org/legacy/publications/library/proceedings/lisa02/tech/full_papers/beattie/beattie.pdf
8. bilge-dumitras-2012-before-we-knew-it.pdf - https://users.umiacs.umd.edu/~tdumitra/papers/CCS-2012.pdf
9. bohme-2006-market-approaches-vulnerability-disclosure.pdf - ETRICS 2006 LNCS 3995:298; Springer paywalled — try Bohme's uibk publications page (informationsecurity.uibk.ac.at/pdfs/) or Wayback of his old TU Dresden page
10. finifter-akhawe-wagner-2013-vrp-study.pdf - USENIX Security 2013; usenix.org/system/files/conference/usenixsecurity13/sec13-paper_finifter.pdf or the presentation page`,
   { label: 'fetch:vuln-markets', phase: 'Fetch' }),

  () => agent(`Fetch (bounty economics + zero-days + AI offense-defense non-arXiv). ${RULES}
1. ablon-bogart-2017-zero-days-thousands-nights.pdf - RAND RR-1751 (RAND technique: find the direct content/dam PDF path)
2. herr-schneier-morris-2017-taking-stock.pdf - Belfer white paper; belfercenter.org publication page links a PDF; else SSRN 2928758
3. zhao-grossklags-liu-2015-vulnerability-ecosystems.pdf - ACM CCS 2015; try Jens Grossklags' TUM publications page or Penn State mirror
4. maillart-etal-2017-given-enough-eyeballs.pdf - J. Cybersecurity 3(2) doi:10.1093/cybsec/tyx008, gold OA (OUP technique)
5. walshe-simpson-2020-bug-bounty-programs.pdf - https://ora.ox.ac.uk/objects/uuid:3245c33c-3542-43c7-9611-257f6116b866 (download the ORA deposited PDF)
6. sridhar-ng-2021-hacking-for-good.pdf - J. Cybersecurity 7(1) doi:10.1093/cybsec/tyab007, gold OA (OUP technique)
7. slayton-2017-cyber-offense-defense-balance.pdf - International Security 41(3):72; MIT Press paywalled — the isij.eu mirror (isij.eu/article/what-cyber-offense-defense-balance-conceptions-causes-and-assessment) may serve a PDF; else Belfer page, else Wayback
8. garfinkel-dafoe-2019-offense-defense-scale.pdf - https://www.tandfonline.com/doi/pdf/10.1080/01402390.2019.1631810 (OA); mirror: Oxford ORA uuid:b537fa1a-f1df-4659-9405-979bc46dc67b
9. healey-2019-persistent-engagement.pdf - J. Cybersecurity 5(1) doi:10.1093/cybsec/tyz008, gold OA (OUP technique)
10. lohn-etal-2023-autonomous-cyber-defence.pdf - https://cetas.turing.ac.uk/sites/default/files/2023-06/autonomous_cyber_defence_final_report.pdf`,
   { label: 'fetch:bounty-zeroday', phase: 'Fetch' }),

  () => agent(`Fetch (AI offense-defense arXiv batch — all direct arXiv PDFs). ${RULES}
1. brundage-etal-2018-malicious-use-ai.pdf - arXiv:1802.07228
2. lohn-2025-ai-cyber-offense-defense.pdf - arXiv:2504.13371
3. murphy-stone-2025-uplifted-attackers.pdf - arXiv:2508.15808
4. ee-etal-2025-asymmetry-by-design.pdf - arXiv:2506.02035
5. potter-etal-2025-frontier-ai-cybersecurity.pdf - arXiv:2504.05408
6. rodriguez-etal-2025-evaluating-cyberattack-capabilities.pdf - arXiv:2503.11917
7. fang-etal-2024-llm-agents-one-day.pdf - arXiv:2404.08144
8. zhu-etal-2024-teams-llm-zero-day.pdf - arXiv:2406.01637
9. zhang-etal-2024-cybench.pdf - arXiv:2408.08926
10. heiding-etal-2024-ai-spear-phishing.pdf - arXiv:2412.00586
11. lukosiute-swanda-2025-evals-real-world-risk.pdf - arXiv:2502.00072
12. zhang-etal-2026-aixcc-sok.pdf - arXiv:2602.07666
13. corsi-kilian-mallah-2024-offense-defense-dynamics.pdf - arXiv:2412.04029
14. hazell-2023-spear-phishing-llm.pdf - https://cdn.governance.ai/Spear_Phishing_with_Large_Language_Models.pdf`,
   { label: 'fetch:ai-arxiv', phase: 'Fetch' }),
])

const rows = r.filter(Boolean).flatMap(x => {
  try { return typeof x === 'string' ? JSON.parse(x.replace(/^[^\[]*/, '').replace(/[^\]]*$/, '')) : x }
  catch (e) { return [{ file: '(unparsed batch)', status: 'see-raw', note: String(x).slice(0, 300) }] }
})
const ok = rows.filter(x => x.status === 'ok').length
log(`${ok} fetched ok of ${rows.length} reported`)
return { fetched_ok: ok, reported: rows }