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

Status: opened 2026-08-05; acquisition complete; ranking pass running.
