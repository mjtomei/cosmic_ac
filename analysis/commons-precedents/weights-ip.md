# Is model capability protectable? — legal verification

2026-08-08. Two agent passes (model-output/distillation enforcement; scraping
and ToS case law). Tests Matthew's extension in `agriculture.md`: that weights
resemble seed more than software because capability can be reimplemented once
known, so protections are hard to enforce. **The evidence supports it strongly,
and identifies the precise structural reason.** A third pass on whether
copyright attaches to weights at all was still running when this was written.

## ⚠️ Correction to a claim made in this session

Claude asserted that "distillation is being contested legally rather than
conceded." **That was wrong.** No AI model provider anywhere has sued over model
outputs, distillation, or a no-competing-model API clause. OpenAI's only
affirmative suit is trademark (v. Open Artificial Intelligence/Ravine, SJ won
2025-07-21); Anthropic's are trademark (v. Abnormal AI) and APA (v. Dep't of
War); xAI's two DTSA actions are employee-mobility cases (v. OpenAI,
3:25-cv-08133-RFL, dismissed **with prejudice** 2026-06-15, on appeal 9th Cir.
26-4486; v. Li, 3:25-cv-07292, in mediation). **"OpenAI v. DeepSeek" does not
exist — it is commentary, not a case.** OpenAI suspended ByteDance's API access
in 2024 and publicly alleged DeepSeek distillation in Jan 2025; no suit followed.

## The structural finding: contract, not property

The only instrument actually available against output-based training is
**contract**, and contract has two properties that matter here.

**It requires assent, so it binds counterparties and not the world.** The
scraping line of cases turns entirely on this. *hiQ v. LinkedIn* — CFAA is dead
against public data in the 9th Circuit (31 F.4th 1180, 2022: a computer hosting
public pages "has erected no gates to lift or lower in the first place"), but
LinkedIn **won on contract**: consent judgment 2022-12-07, **$500,000**,
permanent injunction, and **destruction of all source code, data and algorithms
derived from the scraped data** — the direct precedent for a model-deletion
order. Conversely *Meta v. Bright Data* (N.D. Cal. 2024-01-23): summary judgment
for the scraper because it had terminated its accounts and scraped while logged
out; Meta dismissed the remaining count rather than appeal, waiving review.
**Assent is the whole ballgame.** An API customer who clicked through is in
hiQ's position; a third party who trains their own model knowing the capability
exists is in Bright Data's, and no instrument reaches them.

**And even against a counterparty it may be preempted — genuinely unsettled.**
*X Corp. v. Bright Data* (Alsup, N.D. Cal. 2024-05-09): contract claims
**preempted by the Copyright Act**, because X holds only a non-exclusive licence
and enforcing its ToS would give it "greater rights than it is entitled [to]
under the Copyright Act" and block fair use; X wanted to "have it both ways."
Settled with prejudice 2025-06-27, never appealed. Against that,
*Reddit v. Anthropic* (Thompson, N.D. Cal. 2026-03-30): state-law claims **not**
equivalent to any exclusive right within copyright's general scope, hence **not
preempted**, remanded to SF Superior — and note Reddit **deliberately pleaded no
copyright count**. Two N.D. Cal. judges, opposite results, neither reviewed by
the Ninth Circuit.

**No court anywhere has enforced, invalidated, or construed a "no competing
model" clause.** CourtListener returns zero. The theory is untested. (Caveat:
commercial AI contracts commonly carry arbitration clauses, so a dispute could
be resolving confidentially and invisibly.)

## The two sharpest datapoints

**Distillation was admitted under oath, and nothing happened.** In
*Musk v. Altman* (N.D. Cal. 4:24-cv-04722 — a charitable-trust dispute about
something else entirely), Musk testified on **2026-04-30** that xAI *"partly"*
distilled OpenAI's models to train Grok. It has never been pleaded as a claim by
anyone. An admission in open court that draws no cause of action is the
strongest available evidence that no cause of action exists.

**And the one DTSA holding on point says passive receipt is not enough.**
*X.AI v. OpenAI* was dismissed **with prejudice** (Dkt 110, 2026-06-15) on
reasoning that would govern any future distillation suit: *"Courts interpret
acquisition under the DTSA to require active conduct. The mere passive receipt
of trade secrets is not enough"* (citing *Silvaco v. Intel*, 184 Cal. App. 4th
210, 223). Also: *"merely asking Li to discuss his previous work — a routine part
of the hiring process — does not allow a plausible inference that OpenAI induced
Li to reveal anything confidential."* Training on outputs a party legitimately
received looks much more like passive receipt than active acquisition.

**Scholarship agrees the question is open, and leans against protection.**
Philipp, *From Prompt to Clone: Copyright Challenges in AI Model Distillation*,
17 UC Law SF Sci. & Tech. L.J. 49 (2026), concludes distillation is **unlikely**
to be copyright infringement (and does not reach DTSA). Tishler (Beck Reed
Riden, 2026-05-12), the most on-point DTSA treatment: *"The legal frameworks for
how courts will treat it are not yet settled,"* the hard question being whether
harvesting API outputs is *"misappropriation, or merely a novel form of reverse
engineering."* The governing analogy is *Compulife Software v. Newman*, 959 F.3d
1288 (11th Cir. 2020) — bot-scraping public data **at machine scale** can be
improper means. See also Hrdy, *Trade Secrecy Meets Generative AI*, 100
Chi.-Kent L. Rev. 317 (2025) [citation confirmed, body unread].

## The one case where weights were protected — and how

**Douyin v. Yiruike**, Beijing IP Court, (2023) Jing 73 Min Zhong 3802, an SPC
typical case. It protected model architecture and parameters under **Article 2
of the Anti-Unfair Competition Law — expressly not copyright and not trade
secret** — and involved **direct copying of weights**, not training on outputs.
A court reaching for a general unfair-competition doctrine is a court saying the
IP categories do not fit. It is also the wrong fact pattern for the question
here.

The only US case pleading output-based training is **Pagaya v. Klarna**, D. Del.
1:26-cv-00557-CFC — and neither party is an AI model provider. ¶121 alleges
Klarna used Pagaya's licensed "Model Data" (the model's *outputs*) "to train and
improve its own underwriting model"; ¶155 calls it "unlawful distillation."
Theories are contract and DTSA trade secret, not copyright. Klarna's 2026-07-15
MTD leaves the DTSA count unchallenged. **No ruling.**

## What this does to the argument

**The Monsanto parallel is exact, and it completes the seed analogy.** Seed
enclosure ran on two instruments: technology-use agreements binding purchasers
(contract, *in personam*) and utility patents binding everyone (property,
*in rem*). Where only contract existed, protection was weak; enclosure
concentrated where the patent reached — which is what the verified crop data
shows, 86–90% IP concentration across GM crops against 27–35% across non-GM.
**Weights currently have the contract half and not the property half.** Nothing
reaches the party who never agreed and trains their own model knowing the
capability is achievable.

**Provider behaviour confirms the diagnosis.** Three tools are in evidence and
litigation is not among them. Account termination is the template — OpenAI
suspended ByteDance in Dec 2023 over reported ToS-violating use of GPT output,
with no suit, arbitration, or settlement. Cease-and-desist covers routers
(Anthropic → OpenCode; no provider has ever sued a router, despite OpenAI's
Feb 2026 memo complaining of a *"growing circumvention economy"*). And the
chosen forum is **Congress**: Anthropic's 2026-06-10 letter to Senate Banking
says *"Alibaba executed the largest known distillation attack on Anthropic to
date"* — 28.8M exchanges through ~25,000 fraudulent accounts, 22 Apr–5 Jun 2026,
following a Feb 2026 disclosure of ~16M exchanges through ~24,000 accounts
attributed to DeepSeek/Moonshot/MiniMax — and every ask is legislative
(antitrust clarification for threat-intel sharing, export controls, sanctions).
OpenAI's Feb 2026 memo to the House Select Committee on China makes the parallel
ask. The Frontier Model Forum's anti-distillation coalition (~2026-04-06) is
explicitly detection and blocking, not litigation. Firms with a strong right sue
on it. Firms without one control access and ask for legislation. **The enclosure
attempt is
therefore running in the political layer — which is exactly what the
rent-location bullet's second qualification already says: moats made of
standards and validated records are political artifacts.** Agriculture says
commons are too. The layer that decides is the same one in both directions.

**Two adjacent 2026 rulings worth carrying.** Ninth Circuit,
*Amazon v. Perplexity*, 2026-08-04 (2026 WL 2237587, No. 26-1444): an agentic
browser does not itself "access" a computer — "it was the user using the
Assistant tool," an AI assistant being "a tool, not a person for statutory
purposes" — pushing liability from vendor to user without disturbing ToS claims
against whoever assented. And *Ziff Davis v. OpenAI* (S.D.N.Y. 2025-12-15):
robots.txt is **not** a technological protection measure, controlling access
"no more than a sign requesting that visitors 'keep off the grass' effectively
controls access to a lawn."

## The hinge, resolved: no exclusive right attaches — and the argument is already published

**⭐ PRIOR ART — cite and extend, do not claim.** **Peter Henderson & Mark A.
Lemley, "The Mirage of Artificial Intelligence Terms of Use Restrictions," 100
Ind. L.J. 1327 (2025)** (arXiv:2412.07066) states the copyleft-inversion
mechanism almost verbatim:

> "the hook for an open source license is not a breach of contract claim, but
> rather **the conditioning of a copyright license to the underlying work on the
> agreement to in turn make your work open**. But as we have seen, most AI
> companies aren't conveying anything in which copyright subsists. So the thing
> that makes open source licensing provisions enforceable — the threat of
> withdrawing the right to use the copyrighted material from anyone who doesn't
> comply with the terms — **likely won't work here**."

And their conclusion, which is the bequest argument arriving from the legal
side: *"perhaps **all open-weight models are more 'open' than they would seem at
a glance** — not because they meet the classic definition of open source, but
because the company has no effective means of controlling downstream use."*
Also: *"IP rights operate against the world, but contracts don't."* They apply
human-authorship to weights directly (*"The specific values of the weights are
determined autonomously by the training process… strongly suggests that they…
may fall outside the scope of copyright protection"*), stack functionality under
§ 102(b), and call weights-as-compilation "an uphill battle."

**The copyright position, verified.** *Thaler v. Perlmutter* affirmed human
authorship; **cert denied 2026-03-02** (No. 25-449). Compendium (Third) § 313.2
bars registration of machine-produced works. The Copyright Office has **never
addressed weights as a registrable work** — only as a possible *infringing copy
of someone else's* work (Part 3, May 2025, at 28–30). Part 2 (Jan 2025) records
at 35 n.184 that commenters sought sui generis protection for weights and
declines: *"we do not find the policy arguments for additional protection to be
persuasive."* **No US court has decided whether a developer owns copyright in
its own weights; no plaintiff has ever asserted it.** Foreign law is splitting:
*Getty v. Stability* [2025] EWHC 2863 (Ch) — "the model weights are not
themselves an infringing copy"; *GEMA v. Suno*, LG München I, 42 O 763/25
(2026-07-31) — storage inside the model violates the reproduction right.
⚠️ **Scope the claim to US law or address the EU objection**: Sousa e Silva
argues weights may qualify for the sui generis **database right** (Dir. 96/9/EC),
which *would* give open licences teeth beyond contract. Weak point is the CJEU
*BHB/Fixtures* obtaining-vs-creating line, and it is pure speculation — no
ruling. UK CDPA s.9(3) is the clearest rule anywhere and is **proposed for
repeal**.

**Primary-text confirmation that the drafters know.** **Gemma's terms contain no
grant-of-rights clause at all** — § 2.2 is bare permission, and § 3.1 requires
each downstream distributor to *"include the use restrictions… **as an
enforceable provision in any agreement** … governing the use and/or distribution
of Gemma or Model Derivatives."* Because no automatic right exists to condition,
Gemma manufactures a **new contract at every hop**. That is precisely the OSSI
problem, and precisely what German OpenSourceSeeds does with seed. Llama 4
asserts a right without naming it (*"under Meta's intellectual property or other
rights owned by Meta embodied in the Llama Materials"*). And **OSI's Open Source
AI Definition v1.0 concedes the hole**: model parameters *"may be free by their
nature."* **No open-weight licence has ever been enforced by anyone.**

## Capability itself: unprotectable on five independent grounds

- **Trade secret** — the reverse-engineering carve-out sits at four levels of
  authority (18 U.S.C. § 1839(6)(B); *Kewanee Oil v. Bicron*, 416 U.S. 470, 476;
  *Bonito Boats*, 489 U.S. 141, 146; Restatement (Third) Unfair Competition
  § 43). *Kewanee* upheld trade secret law against preemption **because** it
  leaves reverse engineering lawful — the exclusion is the constitutional price
  of the doctrine.
- **Negative know-how** — the interesting near-miss. The category is real and
  symmetric, but **demonstration is fatal**: *Ruckelshaus v. Monsanto*, 467 U.S.
  986 (1984), public disclosure extinguishes the property right.
- **Patent** — actively *publishes* the existence proof (§ 112; *Amgen v.
  Sanofi*, 598 U.S. 594). *Recentive Analytics v. Fox*, 134 F.4th 1205 (Fed.
  Cir. 2025): applying ML to a new data environment is ineligible.
- **Copyright** — § 102(b); *Baker v. Selden*; *Google v. Oracle* blesses
  reimplementation of functional interfaces.
- **Contract** — *ProCD*'s own rationale is the trap: "A copyright is a right
  against the world. Contracts, by contrast, generally affect only their
  parties." **The knowledge launders itself in one hop.**

**⭐ Two findings that matter more to the paper than the legal result.**
(i) **Open weights ≠ open method.** Releasing weights forfeits secrecy in the
*artifact*, not the *training method* — and Meta's own licence bars using
outputs "to improve any other large language model." **The optimization
competence stays enclosed even when the optimized artifact is given away**,
which is a direct qualification on the bequest argument. (ii) **Detectability
inverts the incentive**: Cohen, Nelson & Walsh (NBER w7552, n=1,478 labs) score
patents 34.8 for product vs 23.3 for process innovation, and secrecy **50.6**
for process. Training-time methods leave no signature in weights or API
behaviour, so **the doctrine rewards secrecy over disclosure in exactly the
layer where pooled optimization would compound** — usable directly for the
paper's central claim.

**Supporting economics.** Hausmann & Rodrik, "Economic Development as
Self-Discovery," *J. Dev. Econ.* 72(2) (2003) is the argument minus the AI:
discovering *that a thing can profitably be done* is an unprotectable
information externality, so self-discovery is under-provided. Mansfield,
Schwartz & Wagner (1981): imitator costs average **65%** of the innovator's.
⭐ **Mertens, Fischl-Lanzoni & Thompson (MIT), arXiv:2602.07238** (809 models,
2022–25): *"At the frontier, 80-90% of performance differences are explained by
higher training compute, implying that scale—not proprietary technology—drives
frontier advances."* ⚠️ *"Existence proof" is not a term of art* — use
Hausmann–Rodrik's "information externality" or Mansfield's "imitation cost" as
the citable hook.

## ⚠️ Three corrections to the seed story

1. **The breeder's exemption was itself narrowed in 1994.** Pub. L. 103-349
   added 7 U.S.C. § 2541(c), extending infringement to varieties "**essentially
   derived**" from a protected one. Post-1994 you may still *breed* with a
   protected variety but may not *commercialize* an essentially derived result.
   The US story is a **two-step erosion**, not "full exemption, then patents."
   (The same Act struck § 2543's brown-bag proviso, so **do not cite *Asgrow
   Seed v. Winterboer* as live law** — it construed already-repealed text.)
2. **The best citation for the no-exemption point is the *J.E.M.* majority, not
   the dissent.** Thomas, J. (6–2): "there are no exemptions for research or
   saving seed under a utility patent… a breeder can use a plant that is
   protected by a PVP certificate to 'develop' a new inbred line **while he
   cannot use a plant patented under § 101 for such a purpose**." Empirical
   contrast: Pardey et al., *Nature Biotechnology* 31(1):25 (2013) — two
   applicants hold nearly half the utility patents; **22** were needed to reach
   half the PVP applications.
3. **⚠️ The rebuttal to pre-empt, and it partly inverts the story.** Janis &
   Smith, 82 Chi.-Kent L. Rev. 1557 (2007): "the breeder's exemption has always
   been premised on the assumption that downstream breeders would have access to
   PVP-protected seed, but nothing in the PVP rules guarantees that access."
   Trade secrecy on inbred parent lines did the excluding in hybrid corn long
   before utility patents — and *J.E.M.* notes utility patents require a
   **publicly accessible** deposit while PVP deposits need not be. **On
   disclosure, patents are the more open instrument.** Defensible framing: *the
   germplasm commons was never legally guaranteed, and utility patents removed
   even its nominal statutory basis* — NOT "utility patents destroyed a
   functioning commons."

**And two OSSI corrections.** The *stated* reason for abandoning copyleft is
**practicality**, not the absence of a copyright analogue — nobody publishes our
reason; Kloppenburg (2014) comes closest, on the privity consequence ("if
licensed material is received or acquired without knowledge of the license, the
license cannot be enforced in relation to that recipient… This failure to
virally propagate would negate the key and most powerful feature"). **Present
the inversion reading as our own analysis**, grounded in the primary contrast:
copyright vests automatically (17 U.S.C. §§ 102(a), 408(a)) while PVP requires a
certificate (7 U.S.C. § 2402(a)) and patents a grant (35 U.S.C. § 111(a)(1)).
Second, **"non-binding" is contested by OSSI itself** (FAQ 11: "We believe the
Pledge to be legally enforceable"). Safest formulation: *OSSI abandoned an
eight-page copyleft licence for a one-sentence Pledge whose enforceability has
never been tested.* **Counter-example worth carrying:** German
OpenSourceSeeds/Agrecol built a **binding** copyleft licence as a chain of
contracts under civil law — same absence of an automatic right, opposite design
choice — showing the obstacle is jurisdictional contract formality, not
conceptual impossibility.

## Prior-art status of each sub-claim

| Sub-claim | Status |
|---|---|
| Copyleft needs an underlying right; weights likely have none; open-weight licences are hollow | **PUBLISHED — Henderson & Lemley 2025. Cite, don't claim.** |
| Same structural point in biotech | **PUBLISHED** — Hope, *Biobazaar* (Harvard UP 2008) ch. 5; Kotschi & Horneburg, PLoS Biol. 2018 |
| Capability unprotectable: building blocks | **WELL-TRODDEN** — Arrow 1962, Mansfield, Levin, Teece, Hausmann–Rodrik |
| Patents don't protect foundation models | **ALREADY SAID OF AI** — Azoulay, Krieger & Nagaraj § 3.1 |
| **Weights ≈ germplasm as a framing** | **NOVEL** (zero hits: arXiv, Crossref, OpenAIRE, OpenAlex, S2, HN, four engines) |
| **OSSI's retreat as predictive precedent for open-weight licensing** | **NOVEL** |
| **Deployment itself destroys appropriability** | **NOVEL as scholarship** — ubiquitous in industry commentary ("We Have No Moat"), absent from law and economics |
| **"No right attaches to capability" as a stated doctrinal package** | **NOVEL** — building blocks standard, never assembled against *capability* |

⚠️ **The leading economics paper argues the opposite and must be engaged.**
Azoulay, Krieger & Nagaraj, NBER w32474, conclude appropriability is **tight** —
"pioneering firms… benefit from a tight appropriability regime more owing to the
many avenues to keep critical knowledge proprietary or tacit," including
"incumbents' ability to endogenously raise the costs of reverse engineering over
time." Their natural experiment is the Llama **leak** (weight leakage), not
deployment-revelation. Position the argument as a challenge to a stated
position, not as filling a vacuum. Second live rebuttal: *Compulife v. Newman*
(11th Cir. 2020) — mass automated extraction of individually-public data can be
"improper means"; "the method and scale of the taking" matter. Also engage
Shanklin et al., "The Case for Contextual Copyleft" (arXiv:2507.12713), which
proposes borrowing the hook from the training data's copyright.

**Genuine gap found:** nobody has applied *Baker v. Selden* / merger / § 102(b)
functionality / the *Sears–Compco–Bonito Boats* right-to-copy line specifically
to **model capability**.

## The 2026 policy fight — verified, with the chronology as the finding

**⚠️ "The US exempted open weights from regulation" must not be stated that
way.** The instrument is **EO 14409, "Promoting Advanced Artificial Intelligence
Innovation and Security," signed 2026-06-02** (91 FR, doc 2026-11415,
2026-06-05) — and **the EO itself never mentions open-weight or open-source
models at all.** The carve-out appears only in a downstream implementing
framework **reported 2026-08-04 and never published**. What is exempted is
open models from **government pre-release review of "covered frontier models"**
— and that review is **voluntary**: the EO says expressly that "*Nothing in this
section shall be construed to authorize the creation of a mandatory governmental
licensing, preclearance, or permitting requirement.*" So this is an exemption
from a voluntary, unpublished national-security review programme. **There is no
US open-weight carve-out from binding regulation, because there is no binding US
frontier-model regulation to be carved out of.** It is also unambiguously
**compliance-side and says nothing about appropriability** — merging it with the
IP question would be a real error. Cite as reported (WSJ/Politico/Bloomberg,
4–5 Aug 2026) and say the framework is unpublished; **this is the weakest
evidentiary link in the set.** (Bloomberg adds that the exemption also spares
*Chinese* open-weight models from US testing.) Ruled out as the referent: the
July 2025 AI Action Plan, whose open-model section is purely promotional
("the decision of whether and how to release an open or closed model is
fundamentally up to the developer"), and EU AI Act Art. 2(12), which is neither
US nor recent.

**The industry letter is verified exactly. "Open Weights and American AI
Leadership," 2026-07-24, ~235 signatories** (NVIDIA-hosted). Verbatim:

> "policymakers should be careful not to conflate legitimate model-development
> techniques with misappropriation. Distillation, or the practice of using one
> model's outputs to help train or improve another, is a widely used technique
> for model improvement, evaluation, and validation. **It reflects a long
> tradition of learning from, building upon, and improving existing
> technologies, a tradition that has helped drive innovation since the rise of
> the open-source software movement.** By contrast, unlawful efforts to extract
> value from closed models raise legitimate concerns. Those concerns should be
> addressed through targeted legal and commercial frameworks rather than
> sweeping restrictions on techniques that play an important role in AI
> innovation."

⚠️ **It does not ask that all distillation stay legal.** It concedes that
"unlawful efforts to extract value from closed models raise legitimate
concerns" and asks only that the remedy be targeted. The letter also grounds
itself in open-source software precedent and argues that "transparency can be
more secure than obscurity" — **both of which map directly onto the paper's §5
open-source-precedent argument.**

**⚠️ Correction to Claude's predicted split: the open-vs-closed framing is
wrong, and OpenAI sits on both sides — coherently.** OpenAI signed the July
letter *and* filed the 2026-02-12 memo to the House Select Committee accusing
DeepSeek of "free-riding." Its own memo already draws the same line the letter
asks for: "*there are legitimate use cases for distillation… However, we do not
allow our outputs to be used to create imitation frontier AI models that
replicate our capabilities.*" **Anthropic is the only major frontier lab that
pressed the distillation case and did not sign** — the cleanest Side-A actor.
The real division is over **scope of remedy**, not open versus closed.

**What the industry is actually asking for, and why it matters here.** A right
that distinguishes by **manner of acquisition** rather than by **subject
matter** — legitimate technique lawful, "unlawful extraction" not. That is
trade-secret-shaped (improper means) rather than property-shaped, and it lands
exactly on the unresolved question in §3 above: whether harvesting API outputs
is "misappropriation, or merely a novel form of reverse engineering" (Tishler),
with *Compulife*'s "method and scale of the taking" as the governing test. **So
the industry is not conceding that capability is unprotectable — it is asking
for the one instrument that might work, and that instrument is the one no court
has yet construed.**

**The chronology is the story.** 2026-02-12 OpenAI memo → 2026-04-23 NSTM-4
(national security technology memorandum on adversarial distillation, calling
PRC-linked campaigns "unacceptable"; PDF is image-scanned, quotes unverified) →
2026-06-02 EO 14409 → 2026-06-10 Anthropic's Senate Banking letter → 2026-07-24
the 235-signatory letter pushing back → **2026-08-04 the framework exempts open
weights, eleven days later.** A datable policy fight in which the diffusion side
won the most recent round.

⚠️ Minor: launch-day coverage reported OpenAI and Google as *absent* from the
July letter; the current hosted PDF lists both. Likely added post-launch — hedge
if signatory composition becomes load-bearing.

## Open items

- Whether copyright attaches to weights at all (agent in flight) — the hinge for
  whether copyleft-style licensing can manufacture the commons.
- Third Circuit disposition in *Ryanair* No. 25-1374 (docket terminated
  2026-08-26 without a located opinion).
- *X v. Bright Data* settlement terms (not public).
- Non-US and arbitral decisions on output-restriction clauses would be invisible
  to these sources. **Standard API contracts carry arbitration clauses, so a
  confidential arbitration is the most likely place for a distillation dispute
  to be hiding** — treat the negative findings as "no public law," not "no
  dispute."
- Klarna's actual dismissal arguments (D.I. 18 sealed).

## ⚠️ Source hygiene

A tier of **AI-generated legal-news sites** surfaced during this research —
`ailawsuittracker.com`, `lexsummary.com`, `decisiondepot.legal`,
`legalnewsfeed.com`, `opentools.ai`, `lawfold.com` — several of which assert
case details that **contradict the actual dockets**. The *X v. Bright Data*
docket history above reached this file through a chain that included
`ailawsuittracker.com` — **re-verify it against CourtListener before it is used
for anything.** Everything else here traces to CourtListener, a filed PDF, or
named legal press (Goldman, Proskauer, Skadden, Reuters, American Banker).
Apply the same check before any of this reaches paper text.
