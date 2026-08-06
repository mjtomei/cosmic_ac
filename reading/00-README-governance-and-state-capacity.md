# Governance and State Capacity — reading list

The empirical record of institutions built to **supply** counsel to government,
and of why capable states fail to execute. Sibling to
`democratization-of-counsel/`, and the division of labour between them is:

- **counsel** keeps the *normative* argument — who gets advice, and what its
  distribution does to democratic authority (Lippmann–Dewey → Federalist/Burke →
  Downs → Condorcet/Landemore → the LLM-deliberation proofs), plus the
  partisanship literature about how citizens actually behave.
- **governance** (here) keeps the *institutional* record — schools built to
  manufacture a governing class, analytic machinery installed and abandoned,
  counsel agencies created and defunded, and the proceduralism and capture
  literatures that explain why capacity decays.

Cross-linked both ways. `notes/` is the shared repo-versioned notes directory.

Opened 2026-08-05, prompted by Loury & Teles, *The Glenn Show*, 29 July 2026
(`notes/teles-loury-2026.md` + transcript), whose two poles frame the whole
cluster ninety years apart:

> Harvard Kennedy School on Littauer's 1935 gift: he "backed his vision of **a
> school for a new professional governing class**."
>
> Teles on the Johns Hopkins school he is now building: "we want to **serve
> something like the entirety of the governing class of the United States**."

Same institutional object; *distribution* named as the reform.

## The five clusters

**1. Manufacturing a governing class.** The Littauer gift and the 1937 opening;
Don K. Price (dean from 1958, *not* the first — Williams 1937, Mason 1947) and
*The Scientific Estate* (1965); the 1969 MPP and the Ford Foundation programme
that built eight policy schools on a shared analytic core.

The three *Crimson* pieces are on disk and sharpen the record. The gift is
$2,000,000 from Lucius Nathan Littauer '78, announced 11 December 1935, standing
up "the thirteenth graduate school of the University." The 1937 opening is
better than "with no students" — it opened that way **deliberately**: a
three-month session from 1 March in which the faculty sat with "fifty prominent
officials drawn from federal, state and" local government. The school's first
act was to convene practitioners rather than to teach, which is the
supply-of-counsel reading of its founding, in its own words, at the time. The
MPP launched July 1969 with **21 students**.
Price's four estates — autonomy varying inversely with power — is the governance
principle the counsel arc lacks. His p.186 is the complication: policy is
"determined by scientific developments that we cannot foresee," so the expert
estate generates the option set.

**2. The analytic machinery, installed and abandoned.** PPBS extended
government-wide in 1965 and dead by 1971 (Schick, "A Death in the Bureaucracy,"
*PAR* 1973); Rivlin's insider assessment; Wildavsky's critiques. Teles's account
of what the Kennedy School was *for* — "systems analysis… advanced
microeconomics… the basic analytical plumbing," on an end-of-ideology premise
that did not hold.

**3. Counsel institutions created and withdrawn.** The Employment Act of 1946
writing the CEA into statute; the OTA Act of 1972 stating the counsel-gap
diagnosis in law; OTA's closure on 29 September 1995 — $21,970,000 and 143 staff
replaced by $3,615,000 "to carry out the orderly closure." House committee staff
down 39% in a single year and never recovered. **CBO survived flat because its
numbers are procedurally required**: counsel that is not structurally demanded
gets cut. Standing counsel for Congress now costs ~$1.02bn/yr.

**4. Why capable states cannot execute.** Bagley's "procedure fetish"; Moynihan
on proceduralism and state capacity; the administrative-burden construct, with
its finding that burden "will often be a **deliberate political choice**";
Pahlka on accreted process (DoD 5000-series: 7 pages to 2,000+ in 53 years) and
"doing a great job at the wrong jobs"; Dunkelman on devolved veto power. Read
with the counter-evidence: Yackee & Yackee's survey of 1,460 agency leaders
finds agencies do issue rules quickly.

**5. Capture, rents, and the technical bridge.** Teles's "Kludgeocracy" —
"complexity is the friend of the organized and well-resourced" — which is this
project's competence/encoding argument in the policy domain, from a term he took
*out of programming*. Olson 1982 on distributional coalitions retarding
technology adoption; Olson 1996 on "big bills left on the sidewalk." Zingales,
Philippon, Furman & Orszag on measured rents. Frischmann on non-rival
infrastructure under-provision — the closest published form of the paper's own
technical claim.

## Two findings this directory exists to hold

**The confirmed absence.** Nothing published bridges policy-capture economics to
technical under-provision of shared computing infrastructure (searched across
Crossref, OpenAlex full text, arXiv, Unpaywall). Frischmann has infrastructure
without capture; Teles has capture without the technical half. Per project
convention the bridge is **assembled from Olson 1982 + Frischmann 2005 + Teles
2013**, not claimed.

**The sharpest objection to our own argument**, from Teles: automating cognition
risks "pull[ing] out where the actual discretion and judgment are in
organizations," so we need "a sense of what are the essentially human tasks in
governance." Pair with Davies, *The Unaccountability Machine* (2024).

## What is on disk

**33 works, all retrieved and verified** (2026-08-05, 4-agent sweep; page-1
titles checked against filenames, not trusted from the fetch reports). Both
priority targets landed: **Frischmann 2005** (115pp, the Minnesota Law Review
version) and **Olson 1996** (the published *JEP* text, which had blocked twice —
AEA serves it as a browser download, so `expect_download()` was needed; the
technique is reusable for other AEA articles).

Three files are browser renditions rather than publisher PDFs, and it matters
for quoting: `teles-2013-kludgeocracy` and `teles-2015-upward-redistribution`
are Wayback captures of *National Affairs* with the archive banner on page 1
(no page numbers — cite by section), and `moynihan-2025-rescuing-state-capacity`
is a rendition of the Wiley full-text HTML because Cloudflare blocks the
publisher PDF here; it is complete (18pp, *JPAM* 44(2):364–378) but not the
publisher's pagination.

Two are scans. `shapiro-2001-patent-thicket` has **no text layer at all** — it is
readable but not greppable, and needs OCR before any search over it counts as
evidence of absence. `hall-ziedonis-2001-patent-paradox` has a scanned cover
page and text throughout the rest.

Filename corrections found by reading the documents: `yackee-2022-…` is
**Yackee & Yackee 2024** (*Regulation & Governance*, online 7 Sep 2024);
`gutierrez-philippon-2018-institutional-drift` is the NBER working paper titled
"How European Markets Became Free," the earlier title of the published
comparison paper; `hsieh-moretti-2019-housing-constraints` is the **working
paper** (NBER 21154), not the *AEJ:Macro* version.

**Still missing, and the sweep did not attempt them** — books and paywalled
back-numbers needing a purchase or a browser: Schick, "A Death in the
Bureaucracy" (*PAR* 1973, the PPBS obituary); **Olson 1982, *The Rise and
Decline of Nations*** (★★★ priority — it is the objection that operates at the
same level as our own claim); Price, *The Scientific Estate* (1965; only
Miller's 1966 *Duke L.J.* review is on disk); Davies, *The Unaccountability
Machine* (2024); Rivlin; Wildavsky; and the OTA closure appropriation line item.

Status: opened 2026-08-05; acquisition complete; ranked (below).


---

## The ranking

33 works. Star distribution: **16 × ★★★ · 15 × ★★ · 2 × ★**. That is top-heavy, and deliberately so — this directory was assembled to hold two primary records (the counsel institutions' founding and decay documents) plus the three legs of a bridge that must be *assembled from published work, never claimed as novel*. Both sets are load-bearing by construction.

Six works are marked **OBJECTION** and are flagged inline everywhere they appear below. Project convention: contested findings appear WITH their contest, so none of these is optional decoration.

- **★★★ (16)** — `frischmann-2005-infrastructure-commons` · `olson-1996-big-bills-sidewalk` · `teles-2013-kludgeocracy` · `bagley-2019-procedure-fetish` · `yackee-2022-ossification-states` ⚠ · `hsieh-moretti-2019-housing-constraints` · `greaney-2026-comment-hsieh-moretti` ⚠ · `ellwood-2008-policy-school-challenges` · `crimson-1935-littauer-gift` · `ota-act-1972-statute` · `brookings-vital-statistics-congress-staff` · `zingales-2017-political-theory-firm` · `furman-orszag-2015-rents-inequality` · `bessen-nuvolari-2019-diffusing-without-dissipating` ⚠ · `shapiro-2001-patent-thicket` · `karlson-2021-critique-entrepreneurial-state` ⚠
- **★★ (15)** — `teles-2015-upward-redistribution` · `moynihan-2025-rescuing-state-capacity` · `moynihan-herd-harvey-2015-administrative-burden` · `dunkelman-2019-penn-station` · `pahlka-2024-wrong-jobs` · `pahlka-2024-we-have-cancer` · `crimson-1937-littauer-opens` · `miller-1966-review-scientific-estate` ⚠ · `employment-act-1946-statute` · `lawcontemp-2006-transparency-public-science` ⚠ · `gutierrez-philippon-2018-institutional-drift` · `gutierrez-philippon-2017-declining-competition` · `boldrin-levine-2013-case-against-patents` · `lemley-2005-free-riding` · `hall-ziedonis-2001-patent-paradox`
- **★ (2)** — `crimson-1969-mpp-launch` · `irving-2018-ai-safety-via-debate`

⚠ = genuine objection to the paper's own argument.

Cluster coverage is uneven: cluster 1 (schools) has 4 works, cluster 3 (analytic machinery / agencies) has 4, cluster 4 (decay) has 7, cluster 5 (capture, rents, commons economics) has 18 — and **cluster 2 has nothing at all**. See Gaps.

## The reading path — the argument in order

Twenty-six entries. **The 3s alone are a complete walk**; every ★★ and ★ entry is marked *(skippable)* and exists to add depth at the point where it sits. The path runs: what kind of good this is → why it is captured → how capacity decays without anyone abolishing it → the institutional record of counsel built and withdrawn → the objections → the historical precedent for the cure.

**A. What kind of good this is, and why markets undersupply it**

1. ★★★ **`frischmann-2005-infrastructure-commons`** — Start here. It gives the paper a *testable definition* of its own object (nonrival generic input; demand driven by downstream production; wide range of downstream uses, including nonmarket ones) and locates the failure on the demand side: users cannot appropriate the downstream value, so they never bid for it. This is the closest published form of the paper's central claim, which is exactly why it goes first — everything after is either the mechanism, the evidence, or the contest. Read Part II (pp. 939–980); the rest is 2005-vintage worked examples. Note his own bracket at p. 1023: he does not answer who pays to build the commons. That gap is the paper's §8, and should be named, not papered over.
2. ★★★ **`olson-1996-big-bills-sidewalk`** — Frischmann says the good is undersupplied; Olson supplies the *argumentative template* for proving it. He measures the gap to potential, then knocks out endowments, technology access, and marketable human capital one at a time until only coordination remains — structurally identical to "the gap is effort, not physics," a level up. It comes second because it lets the paper inherit a canonical move rather than invent one, and its migration natural experiments are the precedent for the paper's own embargo and tapeout experiments. **Version warning: this is the 1996 JEP lecture, not Olson 1982.** If the bridge is cited as "Olson 1982," that citation currently has no file behind it (see Gaps).
3. ★★ *(skippable)* **`lemley-2005-free-riding`** — Read here because it disciplines the claim before it is made. Uncompensated positive externalities are the normal condition of a market economy, so the paper's argument cannot be "optimizers capture too little of the social value" — it must be "nobody covers the fixed cost of supplying the optimization at all." Lemley cites Frischmann directly, so it sits literally on the path between entry 1 and the capture literature. Do not enlist it as evidence that free riding is not a real problem.
4. ★★★ **`zingales-2017-political-theory-firm`** — Now the mechanism that turns under-provision into a stable equilibrium: the Medici vicious circle, where market power buys political power that buys more market power. This is what an incumbent does *instead of* supplying improvement, and it comes after the definition because it explains why the good stays unsupplied once it is undersupplied. His methodological point is the one the paper needs most: influence must be read off outputs, not inputs (Alphabet, $16M lobbying on $80B revenue) — because under-provision, like capture, is invisible in spend.
5. ★★★ **`furman-orszag-2015-rents-inequality`** — The measured shape of that equilibrium: the 90/50 ratio of returns on invested capital rose from under 3 to about 10, with ~100% returns at the 90th percentile, persisting rather than being competed away. Cite the *dispersion* — improvement that does not diffuse — which is the empirical form of the paper's claim about the computing stack. It follows Zingales because it is what his mechanism looks like in data. The authors disclaim it themselves ("a question worth further exploration rather than a definitive conclusion"), and the inference from high returns to rents is contested; carry both.
6. ★★ *(skippable)* **`gutierrez-philippon-2017-declining-competition`** — The nearest thing in the directory to a measured under-provision result: US firms invest below what Tobin's Q implies, capital stock 5–10% short, and industries with rising regulation concentrated more and invested less. Read for the mechanism sentence (firms facing no entry threat have no urge to invest), but note carefully that this is under-provision of *private* capital from slack incentive — a different failure from free-riding on a nonrival good, with a different cure. Draw the analogy carefully or not at all.
7. ★★★ **`hsieh-moretti-2019-housing-constraints`** — The canonical quantification of the exact move the directory is built on: a locally rational private veto suppresses a good whose benefits are national, and the loss is computed in general equilibrium rather than asserted. The Rosen-Roback machinery is the closest formal template available for the paper's own under-provision claim. **SERIOUS VERSION TRAP: this file is the NBER working paper (rev. 2017), which reports 8.9% of GDP and ">50% of aggregate growth." The published AEJ:Macro 2019 figure is 3.7%. Never quote this file's numbers as "Hsieh and Moretti (2019)."**
8. ★★★ ⚠ **`greaney-2026-comment-hsieh-moretti`** — **OBJECTION, and mandatory: never cite entry 7 without it.** Re-running Hsieh-Moretti's own code flips the sign; repaired, the effect is +0.02%, two orders of magnitude smaller, and the model turns out to be unit-dependent (results depend on the arbitrary normalization L=1). It comes immediately after because the paper's honesty discipline is the point of the pairing: the headline measured-rents number is fragile in three independent ways. Note the objection is narrower than it reads — Greaney does not show land-use capture is costless. **Filename says 2026; the document is dated October 2023.**

**B. How capacity decays without anyone abolishing it**

9. ★★★ **`teles-2013-kludgeocracy`** — The pivot from economics to institutions, and the third named leg of the bridge. Two mechanisms transfer nearly unmodified: *layering* ("new ideas have to be layered over old programs rather than replace them") is the political-economy statement of accreted ISA/toolchain/compatibility debt, arising from the same cause — whoever holds a veto extracts continuity of their own layer as the price of passage; and the *kludge industry*, a class of intermediaries whose revenue depends on the complexity persisting. It follows the rents evidence because it names who benefits from the mess not being cleaned up. Archived Wayback capture — no journal pagination, and pdftotext interleaves toolbar text into the body; check quotes against the rendered page.
10. ★★★ **`bagley-2019-procedure-fetish`** — Sharpens Teles from "process accretes" to "formally neutral procedure *is* the capture channel," with four hard numbers (81% vs 4% of EPA comments, 170× more pre-notice contacts, 93% of Volcker contacts) and Olson cited by name at p. 393 as the predictive theory. This is the single densest bridge-assembly point in the directory — it is where the Olson leg and the decay leg are already joined by a published author. Its capture evidence is all secondary; pull primaries if a number becomes load-bearing.
11. ★★★ ⚠ **`yackee-2022-ossification-states`** — **OBJECTION, targeting a load-bearing premise.** 1,460 state agency leaders across 50 states, 42% response, timing counted from the decision to initiate rather than from the published NPRM: 75% promulgate rules in under a year, and procedural constraints show no consistent ossification effect. If proceduralism does not measurably ossify, the decay story is about federal peculiarity or about *quality*, not about process volume. It comes directly after Bagley because it is Bagley's contest, and it names the surviving version of the claim (weaker rules, not fewer) — cheap to concede, and the argument is stronger for conceding it. **Filename year is wrong: published 2024, two authors.** OCR'd scan; verify quoted strings character by character.
12. ★★ *(skippable)* **`moynihan-2025-rescuing-state-capacity`** — Reads as the paper's own under-provision logic transposed into government: capacity is invisible, voters never reward it, nobody is paid to remove a rule, so the stock only grows. Worth it for the rules-accumulate asymmetry and for the Shi Medicare figure ($24–29 saved per dollar of monitoring capacity), a rare hard return-on-capacity number. Review essay, all evidence secondhand; roughly half is on Trump-era politicization and is off the path.
13. ★★ *(skippable)* **`moynihan-herd-harvey-2015-administrative-burden`** — The canonical citation for burden as learning + psychological + compliance costs, and the mechanism the paper actually wants: friction is a distributional choice made below the threshold of political attention and presented as a technical fix. The Wisconsin verification form — predicted −2–3%, delivered −20% — is the best single natural experiment here on how badly a paperwork step's cost is underestimated, and transfers directly to toolchain friction as an unowned, unmeasured tax on take-up. Conceptual paper plus one state; no identification strategy.
14. ★★ *(skippable)* **`gutierrez-philippon-2018-institutional-drift`** — Closes part B with the cleanest name for its premise: *drift* — enforcement erodes while statute, agency, and org chart all stay put, which is precisely how the counsel institutions in part C died without ever being abolished. It also smuggles in the first constructive result on the path: rivals who each want to capture a rule-setter will nonetheless agree ex ante to a more independent one, because being captured-against dominates capturing. That is a usable template for why competitors might underwrite a neutral optimization commons. Lobbying asymmetry (US >2× EU) rests on the voluntary EU Transparency Register — a lower bound of uncertain quality. This copy is the Aug 2020 revision of a 2018 WP.

**C. The institutional record: counsel manufactured, installed, and withdrawn**

15. ★★★ **`crimson-1935-littauer-gift`** — Pole one, in contemporaneous primary form rather than a school's retrospective marketing: a $2M private gift creating a graduate school to "educate men in a broad way for public service," explicitly *not* to train technical specialists. It comes here, after the decay mechanism, because the mechanism is what makes the founding document tragic rather than quaint. **The directory's own framing quote — "a school for a new professional governing class" — is NOT in this file**; it comes from HKS's history page and must be sourced separately. Crimson transcription is rough on names; quote Conant's sentence only.
16. ★★ *(skippable)* **`crimson-1937-littauer-opens`** — Supplies what the charter lacks: counsel supply was rationed *on purpose*, capped at forty to seventy so as not to graduate people for whom no posts existed. That is the exact inverse of Teles's "the entirety of the governing class," which is what makes the 90-year pole contrast bite rather than merely rhyme. Also documents that the founders knew no accumulated method existed to teach. It is an announcement of a plan; do not present 40–70 as realized enrollment.
17. ★★★ **`ellwood-2008-policy-school-challenges`** — The only work here that states the counsel-manufacturing purpose *and* measures the decay, told by a former CBO staffer against himself: schools founded to staff the PPBS-era analytic units (a one-sentence bridge from cluster 1 to cluster 3); the CBO pipeline degree-crept until MPPs do budget estimates while policy divisions are all PhDs; defense analytic capacity "has clearly atrophied"; the wage gap quantified (OMB entry ~mid-$40k vs top-MBA means >$100k). It follows the founding documents because it is what became of them. Conference plenary, not peer-reviewed — cite the institutional and pipeline facts, not the ideology figures, and mind that the PDF contains a different paper from p. 188 on.
18. ★★ *(skippable)* **`employment-act-1946-statute`** — The paradigm creation document: Congress legislating that specific persons be "exceptionally qualified to analyze and interpret" as a *condition of office*. The cleanest statutory statement anywhere of manufacturing a professional analytic class. Skippable only because CEA survived, so it carries the created half of the arc and not the decay. Sec. 4(e)(2)'s anti-duplication instruction is a nice small anchor. Text is as enacted; Humphrey-Hawkins 1978 amended it.
19. ★★★ **`ota-act-1972-statute`** — The closest founding document in the directory to the paper's own domain: a legislature declaring in statute that no existing body supplied it competent independent assessment *of technology*, and buying that capacity for $5M over two fiscal years. This is a legislature diagnosing an under-provided analytic public good and acting — and it was killed in 1995. Poor OCR of a Statutes-at-Large scan; re-key any quote against a clean GPO copy. The statute says nothing about the abolition; that is an appropriations line item the directory does not hold (see Gaps).
20. ★★★ **`brookings-vital-statistics-congress-staff`** — The decay as a number series rather than an assertion, and the empirical spine of cluster 3. Table 5-8: CRS 868 (1980) → 609 (2015); GAO 5,303 (1979) → 2,989 (2015); OTA 10 (1974) → 143 → gone. Table 5-1 catches the single-Congress collapse: House committee staff 2,147 (1993) → 1,266 (1995). Paired with entry 19 it gives the created-and-withdrawn arc in two primary documents. It is a compilation and asserts no causal story — the decay reading is the paper's to argue. **Do not cite the 1946 GAO figure (14,219) as lost expertise; that was a wartime voucher-audit agency.** Data stop at 2015/16.
21. ★★ *(skippable)* **`teles-2015-upward-redistribution`** — The causal join between part C and part A, by the same author who defined part B: cut committee staff and the legislature must buy its expertise from the regulated ("has to rely for expertise on the lobbyists who represent the regressive rent-seekers themselves," p. 21). It also supplies the closest published precedent for the paper's federation-underwriter problem — Jack Walker's third-party support, where the counterweight to a concentrated interest must be subsidized from outside — complete with its honest failure mode: sustained donor interest is rare, and reformers can become the captors. Archive capture; the rents survey itself is better carried by entries 5 and 14.

**D. The objections, and the precedent for the cure**

22. ★★★ ⚠ **`karlson-2021-critique-entrepreneurial-state`** — **OBJECTION, aimed at the diagnosis rather than the cure.** Market-failure justifications for innovation policy were theoretical, never validated, and cannot be located or sized; information and incentive problems turn attempted corrections into policy failure and rent-seeking, and organizations "regularly work their way around knowledge investment and appropriation problems." It comes after the full institutional record because that is where its bite lands: everything preceding could be a story about why *state* provision fails. Crucially, the authors cite Frischmann's knowledge commons and von Hippel approvingly as the alternative — the paper's own frame — which forces the paper to say why open/commons supply escapes the policy-failure critique that sinks industrial policy. Ratio Institute working paper, avowedly market-liberal, evidence is a secondhand literature review; the "dozens, even hundreds, of failures" line is Lerner's, not theirs.
23. ★★ *(skippable)* ⚠ **`miller-1966-review-scientific-estate`** — **OBJECTION**, and the 1965 ancestor of the one the directory most wants: technically derived counsel cannot supply the purposive judgment governing requires, and depending on it risks Eisenhower's "captive of a scientific-technological elite." It sits here because it is Teles's worry stated at the moment PPBS was being installed, by the dean of the same school in entries 15–17 — tying cluster 1 to cluster 3 from the inside. It is a secondary review; if this becomes load-bearing, cite Price 1965 directly (see Gaps). PDF metadata names the wrong author.
24. ★★ *(skippable)* ⚠ **`lawcontemp-2006-transparency-public-science`** — **OBJECTION** to the openness-as-cure move: disclosure is bounded, "sequestration" is often unintentional, and more transparency does not reliably produce better knowledge. Its real value is the interpretive-culture sentence — information means little absent an active culture able to make sense of it — which is close to the paper's own bridge, since competence-to-use is exactly what the paper says cheap machine intelligence supplies. Mild and domain-distant (regulatory science, not automated counsel); do not inflate it into a general anti-open-source argument.
25. ★★★ **`shapiro-2001-patent-thicket`** — The return to the paper's own industry, and the directory's cleanest technical bridge: overlapping blocking rights tax and stall cumulative innovation in semiconductors, with the Cournot-complements result formalized (N essential holders → N times the monopoly markup, p. 149) and cross-licenses, pools, and standard-setting as the institutional workaround. It comes near the end because it is the published precedent for the paper's federation-and-commons cure — the cure need not be claimed as new. **Image-only scan, no text layer**; read via pdftoppm. Pre-eBay and pre-AIA: cite the mechanism, not the litigation environment.
26. ★★★ ⚠ **`bessen-nuvolari-2019-diffusing-without-dissipating`** — **The path ends on its sharpest challenge, and it is an OBJECTION wrapped inside the best supporting evidence in the directory.** Support: Lean's Engine Reporter *is* a performance commons — monthly publication of engine duty, technical detail, and operating procedure, launched to diffuse best practice — and it coincides with Cornwall taking world leadership in steam; the heaviest reporters earned the highest returns; Cornish steam patents fell below 1% of the national total while duty rose; across three cases royalties were 1–3% of operating profits against 78–79% productivity gains. The binding constraint was "the limited supply of people with the practical knowledge and skills to build, install, operate, and maintain the new technologies" — effort and competence, not physics, in 1830s clothing. The objection: their model says sharing survives only while that skill constraint keeps old and new technology coexisting, and *predicts sharing ends when the constraint eases* (after 1833, power weaving was all patented). The paper's own bet is that cheap machine intelligence eases exactly that constraint — which by this mechanism predicts collapse back into proprietary exclusion, not a durable commons. **This is the argument the paper must answer, so it is the last thing on the path.** Scope trap: the authors concede standard rent dissipation "might typically apply in the long run."

## Side tracks

**The accretion narratives** — `dunkelman-2019-penn-station` (★★), `pahlka-2024-we-have-cancer` (★★), `pahlka-2024-wrong-jobs` (★★). *For:* color, mechanism detail, and quotable illustration on part B, which the path carries more compactly and more citably via Teles and Bagley. Dunkelman gives the closest *physical* analogue to the paper's object — non-rival infrastructure everyone wants and no one can build — and names the mechanism precisely: not one blocker but a distribution of blockers, none able to kill and all able to delay to death. Pahlka's cancer piece gives an accretion *rate* (DoD 5000-series, 7 → 2,000+ pages in 53 years, ~11%/yr) and, better, the Axe-the-Fax regeneration story: repeal fails because new rules inherit references from old ones, so the stock regrows faster than it clears — precisely the shape of problem where cheap machine intelligence changes the supply economics, and Pahlka says so in a footnote (Niskanen/Stanford RegLab), which is a published hook to build on. Pahlka's wrong-jobs piece is the *demand-side* complement to the whole counsel arc: institutions can manufacture counsel indefinitely and it lands nowhere ("not one of these files is about a child not learning"). *Cautions:* all three are journalism or Substack; the 11% and 7→2,000 figures are Shyam Sankar's, unsourced here; the Pritchett quote is two hands removed; Dunkelman's Caro thesis is interpretive, and his "no major new public infrastructure since the mid-1960s" is his own accounting, hedged in his own text.

**Patent and IP rents** — `shapiro-2001-patent-thicket` (★★★, on the path) anchors it; read with `hall-ziedonis-2001-patent-paradox` (★★), `boldrin-levine-2013-case-against-patents` (★★), and `lemley-2005-free-riding` (★★, on the path). *For:* the measurement half of the thicket story and the political-economy ratchet behind it, in the paper's own industry. Hall & Ham interviewed semiconductor firms who rank patents a distant sixth for appropriating R&D returns yet doubled patent yield per R&D dollar — "a race to secure the right to exclude others before being excluded themselves" — which is engineering effort diverted from optimization into exclusion, with a number on it. Boldrin & Levine generalize the capture logic off IP: per-capita rents to the few holders always exceed per-capita deadweight loss to the many non-holders, so lobbying asymmetry guarantees monotone strengthening regardless of evidence, and patents arrive *after* a shakeout to tax entrants — the shape the paper wants for open silicon. *Cautions:* two version traps in one track. `hall-ziedonis-2001` is actually **Hall & Ham, NBER WP 7062 (1999)**, whose §4.4 is labelled "Preliminary Results" — cite RAND 32(1) 2001 for numbers. `boldrin-levine-2013` is actually the **St. Louis Fed WP 2012-035A**, not the JEP 27(1) 2013 version. Boldrin-Levine's abolitionist conclusion is a liability to lean on; Bessen & Nuvolari themselves name it as the exception to the standard model.

**The Harvard timeline, for the pole contrast only** — `crimson-1935-littauer-gift` (★★★), `crimson-1937-littauer-opens` (★★), `crimson-1969-mpp-launch` (★). *For:* dating the three moments — charter, rationed opening, retooling into an analytic tool-kit degree under Don K. Price. The 1969 piece is the weak link and belongs on the shelf, not the path: two paragraphs of announcement, one scarcity number (21 admitted), no mechanism, and the text is garbled at the only interesting quote (Bok truncated mid-word, "law-years" for lawyers). Ellwood states the same retooling point in a citable sentence with the pipeline consequence attached. Use 1969 for the date and the headcount, nothing else.

**Shelf: auditing counsel you cannot yourself produce** — `irving-2018-ai-safety-via-debate` (★). Honestly off this directory's path: no institutional record, no capture economics, no measured under-provision. Its only bearing is by analogy — a formal treatment of whether a principal can safely consume counsel from advisors more capable than itself, which is the *shape* of the Teles objection. §§5.2–5.3 are the relevant pages and are candid that the question is empirical and unresolved. Proposal-stage 2018 preprint whose only experiment is a toy MNIST classifier, with no human-judge trials at all. Keep it only if the paper ever argues machine-supplied counsel can be audited by a non-expert; do not present it as a demonstrated mechanism.

## Gaps the path-builder surfaced

**Cluster 2 is empty.** Every work in the directory is tagged cluster 1, 3, 4, or 5. The analytic-machinery cluster — PPBS itself, as a designed method for manufacturing counsel and as the thing whose death is the arc's hinge — is represented only obliquely: Ellwood's one sentence that schools were founded to staff the PPBS units, and Miller's 1966 review footnoting Novick and BoB Bulletin 66-3. This is the largest structural hole.

Ranked by what the *path* most needs:

1. **Schick 1973, "A Death in the Bureaucracy."** The single highest-value acquisition. It is the missing cluster-2 spine and the only document that would let the path show analytic machinery being *installed and then dying*, rather than inferring decay from staff counts. Right now entries 17–20 carry created-and-withdrawn for OTA and congressional staff, but PPBS — the method the schools were built to feed — has no obituary on disk. Without it, the arc's hinge is asserted.
2. **Olson 1982, *The Rise and Decline of Nations*.** The directory's stated bridge is Olson 1982 + Frischmann 2005 + Teles 2013, and **one of the three legs is not here.** What is on disk is the 1996 JEP lecture, which is excellent for the argumentative template but is development economics, not the distributional-coalitions/institutional-sclerosis argument the bridge actually leans on. Either acquire 1982 or re-anchor the bridge's citation to 1996 in the paper's text — the current mismatch is a citation the paper cannot support from its own directory.
3. **The Teles quote itself.** The directory exists partly to hold the sharpest objection to the paper — automating cognition risks "pulling out where the actual discretion and judgment are in organizations" — and **that sentence is in neither Teles file on disk.** It must be sourced (interview, podcast, or the Hopkins-school material) before it can be quoted. As things stand the directory's own framing rests on an unsourced string. The same is true of the 1935 pole: "a school for a new professional governing class" is HKS's phrasing, not the Crimson's.
4. **Price, *The Scientific Estate* (1965).** Everything sharp in entry 23 is Price's, quoted at second hand by a reviewer whose own frame is a polemic about legal education and whose Eisenhower footnote is misattributed. If the "technical counsel cannot supply purposive judgment" objection becomes load-bearing — and it should, since it is the published ancestor of the Teles objection — the book has to be on disk.
5. **The 1995 OTA closure appropriation line item.** Entry 19 gives the creation in statute and entry 20 gives the headcount going to zero, but the *act of withdrawal* is documented nowhere. The created-and-withdrawn arc currently has a primary source at one end and a table footnote at the other.
6. **Rivlin and Wildavsky.** Rivlin (*Systematic Thinking for Social Action*) is the practitioner's case that analysis can be supplied usefully; Wildavsky is its most serious internal critic. Together they would give cluster 2 its own contest, in the project's convention — right now the directory has no work that argues the counsel apparatus *worked*, which makes the decay story unfalsifiable as assembled.
7. **Davies, *The Unaccountability Machine* (2024).** The cybernetic/systems framing of accountability sinks — the closest recent published treatment of institutions that cannot absorb the counsel they generate. It would sit between entries 14 and 22 and would sharpen the Pahlka side track into something citable.

Further gaps inferred from the shape of what is here:

- **No supply-side account of who pays.** Frischmann brackets it explicitly (p. 1023); Teles 2015 offers Walker's third-party support with its own failure mode; Gutiérrez-Philippon 2018 offers ex-ante delegation to a neutral rule-setter. That is three fragments and no anchor. The paper's §8 financing/underwriter problem currently has no leg to stand on in this directory.
- **No published bridge from policy-capture economics to technical under-provision.** This is the directory's stated *confirmed absence* and the path confirms it: Frischmann is the only work that reasons about technical infrastructure at all, and he does not touch capture; Shapiro is the only work in the paper's own industry, and he does not touch counsel institutions. The bridge remains to be assembled, never claimed.
- **Nothing measures analytic quality, only analytic headcount.** Yackee (entry 11) explicitly leaves Bagley's quality channel untested, and Brookings counts staff, not output. The decay claim's strongest form — capacity fell in quality, not volume — has no evidence on disk in either direction.

---

## What the ranking changed about this directory

Four findings from the pass, recorded because each one corrects something the
README asserted before the works were read.

**1. The bridge is missing a leg.** This README says the capture-to-technical
bridge is assembled from **Olson 1982 + Frischmann 2005 + Teles 2013**. Two of
those are on disk; **Olson 1982 is not.** What we hold is the 1996 *JEP*
lecture, which is superb for the argumentative template — measure the gap to
potential, then eliminate endowments, technology access and human capital until
only coordination remains, which is "the gap is effort, not physics" one level
up — but it is development economics, not the distributional-coalitions argument
the bridge leans on. Until the book is acquired, either get it or re-anchor the
citation to 1996 in the paper's own text. Citing a leg the directory cannot
supply is exactly the failure mode the project's verification convention exists
to prevent.

**2. Two framing quotes are correctly attributed, and it is worth saying so
explicitly, because neither is where a reader would look for it.** The sharpest
objection — automating cognition risks "pull[ing] out where the actual discretion
and judgment are in organizations" — is **not in either Teles PDF**; it is from
the podcast at ~34:30, and `notes/teles-loury-2026.md` carries it with its
timestamp. Likewise "a school for **a new professional** governing class" is
**HKS's own retrospective phrasing, not the *Crimson*'s** — the 1935 article
says the school will "educate men in a broad way for public service" and
explicitly not train technical specialists. Both attributions in this README are
right as written; the risk is a future editor moving the quote next to the PDF
that does not contain it.

**3. The path ends on a real challenge to us, and it should stay there.**
Bessen & Nuvolari is the directory's best supporting evidence *and* its sharpest
objection. Lean's *Engine Reporter* is a performance commons in 1830s clothing —
monthly publication of engine duty and operating procedure, coinciding with
Cornwall taking world leadership in steam, heaviest reporters earning the highest
returns, Cornish steam patents falling below 1% of the national total while duty
rose, royalties 1–3% of operating profits against 78–79% productivity gains — and
the binding constraint was "the limited supply of people with the practical
knowledge and skills to build, install, operate, and maintain the new
technologies." That is our thesis, measured, in another century. **But their
model says sharing survives only while that skill constraint holds, and predicts
sharing ends when it eases** — and our bet is that cheap machine intelligence
eases exactly that constraint. On their mechanism, that predicts collapse back
into proprietary exclusion rather than a durable commons. This is the argument
the paper has to answer.

**4. Cluster 2 is empty.** Nothing on disk is tagged to the analytic machinery
itself. PPBS — the method the schools were built to feed, installed
government-wide in 1965 and dead by 1971 — is present only obliquely, through
one sentence in Ellwood and a footnote in Miller. Schick 1973 is therefore the
highest-value acquisition in the whole directory: without it the arc's hinge is
asserted rather than shown, and decay is inferred from staff counts instead of
documented as a method dying. Related and equally structural: **the directory
holds no work arguing the counsel apparatus WORKED.** Rivlin would supply that
and Wildavsky its internal critique. As assembled, the decay story is
unfalsifiable, which the project's own conventions should not tolerate.

## Version traps found by reading the documents

Recorded here because in every case the filename or the citation-as-remembered is
wrong, and all of them would survive into a draft unnoticed.

| File | The trap |
|---|---|
| `hsieh-moretti-2019-housing-constraints` | This is the **NBER working paper**, which reports 8.9% of GDP and ">50% of aggregate growth." **CONFLICT TO RESOLVE:** the ranking agent reports the published *AEJ:Macro* figure as 3.7%, while `notes/economics-is-radical.md` records the widely-cited published figure as 36% (1964–2009). Both cannot be right. Resolve against the published article before any number is used. |
| `greaney-2026-comment-hsieh-moretti` | Filename says 2026; the document is dated **October 2023**. |
| `yackee-2022-ossification-states` | Published **2024**, two authors, *Regulation & Governance*. OCR'd scan — verify quoted strings character by character. |
| `hall-ziedonis-2001-patent-paradox` | Actually **Hall & Ham, NBER WP 7062 (1999)**; its §4.4 is labelled "Preliminary Results." Cite *RAND* 32(1) 2001 for numbers. |
| `boldrin-levine-2013-case-against-patents` | Actually **St. Louis Fed WP 2012-035A**, not the *JEP* 27(1) 2013 version. |
| `gutierrez-philippon-2018-institutional-drift` | This copy is the **Aug 2020 revision**; titled "How European Markets Became Free." |
| `teles-2013` / `teles-2015` | Wayback captures — **no journal pagination**, and `pdftotext` interleaves the archive toolbar into the body. Check every quote against the rendered page. |
| `shapiro-2001-patent-thicket` | **Image-only, no text layer.** Read via `pdftoppm`. A grep over this file proves nothing. |
| `brookings-vital-statistics-congress-staff` | Do **not** cite the 1946 GAO figure (14,219) as lost expertise — that was a wartime voucher-audit agency. Data stop at 2015/16. |
