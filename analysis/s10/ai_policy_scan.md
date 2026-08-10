# AI policy scan of legislatures in the S10 corpus

**Compiled 2026-08-09.** Companion data: `ai_policy_scan.json`.

Question: does each chamber have an official policy, rule, guideline or formal recommendation
governing members' and staff use of generative AI in preparing speeches, questions, motions,
correspondence or committee work — and in particular, would AI-drafted text be flagged in the record?

Executive-branch AI policies (public-service directives, government AI assurance frameworks) are
**excluded** throughout unless they explicitly bind the legislature. Several jurisdictions have
substantial government AI regimes that cover no part of the parliament; those are recorded as
`no_policy_found` for the chamber, with the executive instrument named so the distinction is auditable.

`no_policy_found` means *nothing located in the public record*. It is not proof of absence: most of
these instruments, where they exist, are unpublished intranet documents. Queensland's only became
visible because a committee asked the Speaker about it on the record.

---

## The one-line answer

**No chamber in scope requires AI-drafted text to be disclosed in its published record. Zero out of 22.**
No chamber forbids members from using generative AI to draft speeches, questions or motions. Exactly
one chamber has published guidance addressed to members about AI in proceedings — the UK Parliament —
and it resolves the question permissively.

---

## Master table

| # | Chamber | Policy exists | Who it binds | Disclosure in the record | Date | Instrument |
|---|---|---|---|---|---|---|
| 1 | **UK House of Commons** (+ Lords) | **Yes — members & staff** | Members of both Houses and their staff | **No** (reactive: "be prepared to disclose … if requested") | Jan 2025; v4 Sep 2025; **current Apr 2026** | *Artificial Intelligence: Guidance for Members*, Parliamentary Digital Service / Speaker's Steering Group |
| 2 | **US House of Representatives** | **Yes — members & staff** (not public) | "House Users": Members, Committees, Leadership, staff, contractors | **No** in the Congressional Record (internal disclosure duty to CAO only) | Effective **28 Aug 2024**; announced Sep 2024 | HITPOL 8, CAO / Cttee on House Administration |
| 3 | **US Senate** | **Yes — members & staff** (not public) | All Senate offices, committees, contractors | **No** (office-level disclosure merely encouraged) | Dec 2023 → framework **27 Oct 2025** → Tier 2 tools **Mar 2026** | SAA-CIO-CYB-040 v1.00, Sergeant at Arms / CIO |
| 4 | **Canada, House of Commons** | Yes — **administration**; MP resources only | Administration staff; online GenAI resources for MPs | **No** | AI hub Jun 2024; MP resources **May 2025**; strategy autumn 2025 | House Administration AI programme (no BOIE rule) |
| 5 | **Scottish Parliament** | **No policy found** | — | No | — | — |
| 6 | **Senedd Cymru** | **Yes — text not published** | Staff guidance; **Copilot trial includes Members and their support staff** | **No** | FOI **9 Apr 2025**; Llywydd statement **24 Sep 2025** | Commission staff guidance + AI section of ICT Strategy 24-29 |
| 7 | **Northern Ireland Assembly** | **Unclear** | — | Unknown | — | RaISe briefing 33/25 (comparative, not prescriptive); 3 Commission/FOI items unretrieved |
| 8 | **Houses of the Oireachtas** | Yes — **Service (staff)**; in deployment | Oireachtas Service | **No** | Strategic Plan **10 Oct 2025**; charter drafted Q4 2025; **deployment 2026** | Responsible AI Framework + AI Charter |
| 9 | **British Columbia** | Yes — **staff only** | Assembly employees (Policy 5405 §5) | **No** (§5.04(d) disclosure binds staff work product, not the record) | **11 Feb 2026**; members' policy revision scheduled 2026-27 | Policy 5405 (Clerk); Policy 7410 (LAMC) is AI-silent |
| 10 | **Alberta** | **No policy found** | — | No | — | MSC Orders: zero AI mentions. **But: the only Speaker's ruling on AI-authored speeches, 2 Dec 2025** |
| 11 | **Saskatchewan** | **No policy found** | — | No | — | All 21 BOIE Directives: zero AI mentions |
| 12 | **Manitoba** | No policy found *(partial coverage)* | — | Unknown | — | LAMC documents not retrieved |
| 13 | **Ontario** | **No policy found** | — | No | — | BOIE publishes no directives; OPS directive is executive-only |
| 14 | **Nova Scotia** | **No policy found** | — | No | — | HAMC policies, annotated regulations and 5 sets of minutes: zero AI mentions |
| 15 | **Newfoundland & Labrador** | **No policy found** | — | No | — | 25 published policies + Management Commission papers (~125k words): zero AI mentions |
| 16 | **Prince Edward Island** | No policy found *(partial coverage)* | — | Unknown | — | Site behind bot-management captcha |
| 17 | **New South Wales** | **No policy found** | — | No | — | Only an internal staff "AI Interest Group" (DPS AR 2024-25) |
| 18 | **Victoria** | **No policy found** | — | No | — | DPS Annual Report 2024-25: **zero** occurrences of AI/artificial intelligence/generative/Copilot |
| 19 | **Queensland** | **Yes — staff only** (text not retrieved) | Parliamentary Service | **No** | Policy **Dec 2025**, rev. **Jun 2026**; Digital Strategy May 2026 | Parliamentary Service AI Policy + Guidelines |
| 20 | **Western Australia** | **No policy found** | — | No | — | No rule, **but a private AI Parliamentary Assistant was deployed to members Apr 2025** |
| 21 | **South Australia** | No policy found *(low confidence)* | — | Unknown | — | Thinnest web presence of the six states |
| 22 | **Tasmania** | **No policy found** | — | Unknown | — | Only DPAC guidance, binding *agencies* not the Parliament |
| B1 | *Australian Parliament (federal)* | **Yes — members & staff** | DPS, parliamentary departments, **parliamentarians and their staff**, PWSS | **No** | last updated **13 Feb 2026** | DPS AI Transparency Statement |
| B2 | *New Zealand Parliament* | **Yes — text withheld** | MPs | **No** | evidenced May 2026 (DPMC OIA) | Parliamentary Service guidance; Copilot as preferred tool |

---

## Strictest and loosest

**Strictest: the US House of Representatives.** HITPOL 8 is the only instrument in scope with an
enumerated prohibited-use list that bites on legislative work — it forbids inputting constituent PII
for casework, creating deepfakes, and, oddly, "finalizing legislation." It puts AI-generated
constituent correspondence and first drafts of talking points behind *management approval*, requires
approved tools on House-managed devices, forbids House credentials on external AI tools, carries an
internal disclosure obligation and a reporting duty to the CAO on request, and threatens criminal and
civil penalties. It is also broad in scope: "House User" is defined to include Members and Committees,
who are independent employing authorities — an authority question POPVOX Foundation flags as unresolved.

**Runner-up on strictness, and the strictest on process:** the **Australian federal DPS**, which
requires *any* user of parliamentary ICT — including parliamentarians' offices — to report each new AI
use case to the ICT service desk and obtain departmental approval *before* using AI, maintained in a
central register.

**Loosest: Saskatchewan, and the Canadian provinces generally.** Saskatchewan has no instrument, no
Hansard mention of AI authorship in fifteen months of sittings, and 21 Board of Internal Economy
directives that never say the word. Nova Scotia and Newfoundland and Labrador are equivalent. Among
chambers that *have* engaged with the question, the loosest is the **UK**: its guidance says "Use it if
you wish," and expressly settles the proceedings question in favour of the member.

**Most permissive on the specific question S10 measures: the UK.** The guidance states that AI-generated
content used in formal proceedings is the member's own contribution and is "protected by privilege
**regardless of the tools used to produce that material**." That sentence is the closest thing anywhere
to an authoritative ruling that AI-drafted speeches and questions are unobjectionable.

---

## What the landscape actually looks like

**1. Where policies exist, they are IT policies, not rules of authorship.** Almost every instrument
found was issued by a Clerk, a CIO, a Sergeant at Arms or a digital-services department, and is framed
around information security, data protection, tool approval and human review. The Queensland
Parliamentary Service policy, the BC Clerk's Policy 5405, the Senate SAA framework, the DPS Transparency
Statement and the Oireachtas Responsible AI Framework are all of this type. None of them asks the
question "should a legislator's words be their own?" The one document that does ask it — the UK
guidance — answers no, in the sense that the tool is irrelevant to the member's responsibility.

**2. The members/staff asymmetry is the structural story.** Where an institution's *administration*
governs itself, the rules are detailed. Where *members* govern themselves, there is usually nothing.
British Columbia is the clean natural experiment: the same Assembly wrote a detailed AI regime for its
own employees in February 2026 — approved-tool lists, mandatory human review, an affirmative duty to
"disclose when the substantive basis of their content, analysis, or recommendations has been produced
by generative AI" — while the parallel Members' policy (7410, May 2024) remains AI-silent. The scheduled
fix, a Tier 1 item on the 2026-27 LAMC work plan, is scoped to whether member AI use "does not create a
risk to information security." Authorship, accuracy and disclosure are not part of the remit. Queensland
shows the same shape: a compulsory AI learning module for Parliamentary Service staff, zero AI content
in the Members' Remuneration Handbook or the Speaker's Financial Guidelines.

**3. Nobody is regulating the record.** Not one chamber requires an AI-drafted speech, question, motion
or submission to be flagged in Hansard, the Official Report or the Congressional Record. The nearest
analogues are all off-record: BC's staff work-product duty, the House's internal disclosure principle,
the Senate's encouragement that offices write their own disclosure rules, and DPS's undertaking to label
*its own* AI chatbots. Notably, the EU comparison shows this is not inevitable — the Sejm's June 2025
survey found that **4 of 9** retrieved EU-chamber AI guidelines require an "AI-assisted" disclaimer on
significantly AI-generated output. Anglophone chambers have not gone there.

**4. Procedure has been tested exactly once, and it went permissive.** Alberta, 2 December 2025.
Opposition House Leader Christina Gray argued that the long-standing rule against alleging a member is
reading a staff-written speech should extend to AI: "Reading speeches written by ChatGPT strikes me as
very much the same thing." Speaker Nathan Cooper: *"while I have at least some sympathy for the last
argument I heard, **ChatGPT is not staff**."* Matter of debate; no point of order. He reiterated the
position on 23 March 2026. That is the only Speaker's ruling on AI authorship found in any of the 22
chambers, and it declines to build a procedural doctrine around it. Ontario (twice) and Manitoba (twice)
saw near-identical accusations — "90% of their speeches came right out of ChatGPT" — traded across the
floor with no point of order raised at all.

**5. Several parliaments are handing AI to members while regulating nothing.** Western Australia's
Parliamentary Portal, launched April 2025, lets members "prompt a private AI Parliamentary Assistant";
the WA annual report mentions artificial intelligence exactly once, in that sentence. The Senedd's
Copilot trial explicitly includes Members and their support staff. The House of Commons is distributing
6,000 Copilot licences. The UK Parliament provides Copilot Chat to every account holder. Provision is
running ahead of rules in most places, and in Victoria the Parliament published an article in October
2025 interviewing three MPs about their own AI use without citing a single parliamentary rule, because
there isn't one.

**6. The comparative baseline says this is normal.** IPU's *World e-Parliament Report 2024* (115
chambers): **11%** are bound by AI law, **14%** have internal procedures or regulations, **7%** have
both. "Given the potential impact of GenAI… the lack of governance and regulation is an aspect that must
be addressed sooner rather than later." NCSL found **no US state legislature reported prohibiting AI in
2025**, down from four in 2024, while self-reported staff use nearly doubled to 44%. Europe is the
outlier in the other direction: the Sejm survey found only 10 of 34 EU chambers have neither adopted nor
started internal AI rules.

---

## The interesting cases

**UK House of Commons — the only chamber whose policy speaks to the study's variable.** It is also the
chamber where the AI-detection question has already gone public (the "I rise to speak" affair, Aug-Sep
2025) and where a competing published analysis exists (Pimlico Journal). It is the highest-information
chamber in the corpus in both directions: most explicit permission, most public scrutiny.

**Alberta — the only chamber with a procedural precedent, and it is permissive.** Also the only chamber
where an AI-generated document was formally tabled: Mr. Stephan (Red Deer-South) read ChatGPT output into
debate on 6 May 2025 and tabled "five requisite copies of a ChatGPT analysis" the next day, without
objection to its provenance.

**British Columbia — the disclosure natural experiment.** The only affirmative AI-disclosure duty in any
Canadian legislature, applying to staff, adopted February 2026, with a members' equivalent scheduled and
deliberately scoped away from disclosure. If disclosure norms have any measurable effect on prevalence,
BC's staff/member split is where to look for it — though the duty attaches to Assembly administration
output, which does not enter Hansard.

**Queensland — the only Australian state with a policy, and it surfaced by accident.** Implemented
December 2025, revised June 2026, with a compulsory staff learning module. It is visible only because
the Governance, Energy and Finance Committee put a question on notice to the Speaker at Estimates 2026.
This is the strongest methodological lesson in the scan: **estimates and questions-on-notice transcripts
are the highest-yield route to unpublished parliamentary AI policies**, and running that route across
NSW, Victoria, WA, SA and Tasmania would likely change some of the `no_policy_found` rows.

**Ireland — a live contradiction worth resolving.** The Chancellery of the Sejm's EU-wide survey
(11 June 2025) lists the Oireachtas among chambers with *adopted* internal AI guidelines and reports,
uniquely among the 34 chambers surveyed, that Irish scope covers "all staff, i.e. **members of
parliament**, parliamentary staff, employees, contractors…" The Oireachtas's own documents describe the
charter as still in draft in Q4 2025 with deployment in 2026, scoped to the Service. Either the survey
captured a different instrument or it overstated the scope. Do not assert that Oireachtas AI rules bind
TDs without pinning the underlying document.

**Saskatchewan — the clean null.** No instrument, no debate, no accusation, no mention. If the study
wants a "silent chamber" reference category, this is it.

**New Brunswick (not in the corpus) — the proof of concept for the study's premise.** On 9 June 2026,
MLA Bill Oliver read AI prompt residue aloud in the Legislative Assembly — "Here's a more natural flowing
version of that section that reads like a legislative speech rather than a series of short points" — more
than once. Per Global News, no one else in the chamber appeared to notice or react. It surfaced weeks
later via Reddit. Undeclared AI-drafted text passed through a Canadian chamber, into the record, unremarked.

---

## Recorded incidents (condensed)

**Declared AI-written speeches.** Luke Evans MP, UK Commons, 20 Dec 2022 ("I think this may be a first";
Kevin Brennan intervened to ask). Jake Auchincloss, US House, Jan 2023. Julian Hill and Aaron Violi,
Australian House of Reps, Feb 2023. Jacqui Lambie, Australian Senate, 9 May 2023 ("This speech was 100
per cent written by artificial intelligence"); Ross Cadell likewise. Tom Giffard MS, Senedd, Jun 2023 —
the first in the Senedd chamber. Adam Olsen MLA, BC, 14 Mar 2024. In none of these cases did any
procedural consequence follow.

**Accusations without adjudication.** Ontario (May-Jun 2025 and Dec 2025), Manitoba (Mar 2026), NL
(Apr 2026, where a Minister admitted using ChatGPT to create an image she had posted), UK (Aug-Sep 2025).

**AI-hallucinated citations in committee material — all Australian.** Academics led by Emeritus Prof.
James Guthrie used Google Bard to generate case studies for the Senate consulting-firms inquiry, which
invented misconduct allegations against the Big Four; Guthrie apologised to the Senate (Oct-Nov 2023;
AI Incident Database #614). A joint committee published and then had to unwind an AI-drafted submission
containing false allegations, reported at Senate estimates 28 May 2024 — Clerk of the Senate Richard Pye
confirmed there are no routine diagnostic tools to detect AI-generated submissions, but cautioned against
"dismissing products that are generated with the assistance of AI out of hand." Rainforest Reserves
Australia filed fabricated citations to two Senate inquiries and a NSW inquiry, with its writer admitting
AI use on 100+ submissions since Aug 2024. **No UK case of hallucinated citations in a select committee
submission was found.** No chamber anywhere bans or restricts AI-generated petitions or submissions.

---

## Two warnings for S10

**Prior art on the same substrate, with the opposite result.** Ben Rice, "Hunting for ChatGPT in
Parliament (and mostly not finding it)" (riceonpaper.substack.com), runs essentially the S10 design on
the Australian federal corpus: 124,734 Hansard speeches 2018-2026, 64,643 post-ChatGPT, scored with
Binoculars (0.4% flagged), Fast-DetectGPT (3.1%), per-MP stylometric change-point analysis **and Claude
Sonnet 4.6 scoring 0-10 on 64,642 speeches**. Result: no statistically significant post-ChatGPT increase
(7.7% pre-2022 vs 7.1% post); seven speeches scored "likely AI"; calibration showed an **8% false-positive
rate exceeding the corpus detection rate**. Pimlico Journal (1 Sep 2025) runs a per-year z-score analysis
of AI-associated phrasing on the UK Commons and reaches the opposite conclusion. Both should be read
before S10's findings are framed.

**Transcript provenance is a confound.** Several chambers now use AI to *produce* the record. NSW Hansard
"has incorporated artificial intelligence and automated speech recognition"; WA has introduced automatic
speech recognition for the first take of Hansard; the Oireachtas Service has an approved use case for
"automated first-draft generation of the Journal of Parliamentary Proceedings"; and across the EU,
transcription of plenary proceedings is the most common parliamentary AI application (27 of 34 chambers).
AI-mediated transcription and editing could plausibly move detector scores independently of whether any
member used AI to draft anything.

---

## Coverage and confidence

| Confidence | Chambers |
|---|---|
| High (primary text retrieved) | UK, US House, US Senate, Canada HoC, Scotland, BC, Alberta, Saskatchewan, Nova Scotia, NL, Victoria, Queensland, Australia federal |
| Medium | Senedd, Oireachtas, Ontario, NSW, WA, New Zealand |
| Low / partial | Northern Ireland (3 Commission/FOI items unretrieved), Manitoba (LAMC docs unretrieved), PEI (site blocked), South Australia (site blocked) |

Highest-yield next steps if any of this becomes load-bearing: (a) estimates / questions-on-notice
transcripts for each Australian state parliament's own appropriation — the route that exposed Queensland;
(b) the three NI Assembly Commission and FOI items behind the site's facet filter; (c) an access request
for BC's unpublished *Procedure on the Integration of AI* and *Guide to Using Generative AI*, the only
known Canadian provincial-legislature documents addressing generative-AI disclosure directly; (d) the
underlying Oireachtas document behind the Sejm survey's members-scope claim.
