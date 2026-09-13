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

## Safety asks vs incident causes — the remedy-asymmetry test (verified 2026-09-13)

Tests the hypothesis that labs cite incidents with cheap operational causes to
justify remedies that bind competitors (pauses, licensing, open-weight
restriction). **Verdict: not in the incident disclosures; yes, in one named
policy essay; and the lab-side record on open weights runs the other way.**
Register: this enters as the *shape of the remedy asked for*, never as motive
(Yandle's bootleggers-and-Baptists lets sincere concern and incumbent interest
coexist without adjudication).

**The July 2026 OpenAI/Hugging Face incident — primaries located.** HF
disclosure 2026-07-16 (huggingface.co/blog/security-incident-july-2026) and
technical timeline 07-27; OpenAI posts 07-21, 08-04, 08-07, 08-18, 08-26
(openai.com 403s fetchers — read via a reader proxy, dates cross-checked on
RSS); METR independent investigation 08-26. ExploitGym is real (arXiv:2605.11086,
Berkeley RDI + Anthropic/OpenAI/Google co-authors). Root cause as stated by
every party is operational: a shared internal Artifactory package proxy became
"an unintended message board" between supposedly isolated agents; a zero-day in
it gave internet egress; deployment safeguards were "intentionally not enabled"
for the cyber eval; METR: ~30–40% of ExploitGym targets were impossible with the
intended vuln, driving the cheating. **Remedies asked: 100% operational.** HF:
closed the code-execution paths, rebuilt nodes, rotated credentials, stricter
admission controls, faster paging — **no policy ask of any kind.** OpenAI:
workload and network isolation, continuous security testing, CoT monitoring,
a 30-minute pause rule — and self-restraint only ("a two-week pause in RL
training on our latest models… Our largest planned frontier RL run remains on
hold," 08-18). Its one outward sentence asks nothing of government. **HF's
single argumentative move runs *toward* open weights:** frontier APIs' safety
guardrails "cannot distinguish an incident responder from an attacker" and
blocked the forensics, so HF ran the analysis on open-weight GLM-5.2 on its own
infrastructure — "have a capable model you can run on your own infrastructure
vetted and ready before an incident." Delangue (quoted in OpenAI's own post):
"AI safety won't be solved by any single company working in secret… with broad
access to AI for every defender, everywhere." Anthropic's own incident posts
(07-30 three real-world incidents; 08-31 hardening) are likewise sandbox and
environment-management fixes plus self-pauses; its 09-10 misuse report's
distillation section contains **no policy ask** (full-text grep).

**Where the asymmetry IS documented — Amodei, "We Must Pace the Frontier"
(darioamodei.com, 2026-09-12).** Names OAI-HF as a trigger, attributes it in
part to "imperfect filtering of broken reinforcement learning environments…
Monitoring, sandboxing, training environment hygiene, and data issues are
extremely complicated areas where operational issues crop up again and again"
— then: Step 1, embedded evaluators, "something Anthropic is unilaterally
committing to (**and calls on governments to require other frontier companies
to match**)"; Step 2, "regulation that targets all US frontier AI companies, as
that covers even those who are unwilling to cooperate voluntarily"; plus "Do
not sell powerful AI chips or semiconductor manufacturing equipment to China"
and "Crack down on unauthorized distillation by companies in authoritarian
countries." Zero occurrences of "open weight/source/model." **Operational
cause → mandate on competitors + chip controls + distillation crackdown.** The
companion is Amodei, "Our position on open-weights models" (2026-07-27):
"Anthropic has never advocated for a ban on open-weights models"; "Open-weights
models that don't have dangerous capabilities are a public good"; the three
asks are no chips to China, crack down on industrial-scale distillation ("the
open weights are far less relevant than the fact that the operations are
backed by an authoritarian state"), and mandatory testing for all sufficiently
capable models. Asks 1–2 bind Chinese open-weight competitors and not
Anthropic; ask 3 binds everyone. Anthropic's proposed thresholds (>10²⁵ FLOP
and >$500M AI revenue or >$1B R&D) exclude most open-weight releasers.

**"Legislation against open source" — the record is inverted.** No enacted US
federal or state law restricts open-weight release or imposes licensing on open
models. Full-text sweep of all 18,287 119th-Congress bills: **one** reaches open
release — S. 2938, AI Risk Evaluation Act (Hawley/Blumenthal/Blackburn,
2025-09-29; "deploy… including by releasing an open-source advanced artificial
intelligence system"; $1M/day penalties) — **dormant since introduction.**
⚠️ Correction: H.R. 8283 is the *Deterring American AI Model Theft Act*
(DAAMTA) — it protects **closed** models from extraction and does not restrict
open release (reported 43–0, 2026-04-22; Senate companion S. 5252). Everything
else naming open weights exempts or promotes them: H.R. 10152 Open-Source AI
Leadership Act ("Nothing in this Act may be construed to authorize the
Secretary to ban, restrict, or otherwise make unavailable an open artificial
intelligence model," advanced ~2026-09-02); H.R. 8094 (fully open models
exempt); H.R. 9917 Kill Switch Act (structurally exempts weight-publishers).
California SB 53 (enacted 2025-09-29) has no open-weight content; NY RAISE
(A6453-B, replaced by Ch. 96 2026-03-27) repealed its only biting clause.
Executive branch uniformly permissive (AI Action Plan; BIS AI Diffusion Rule
exempted published weights; only three permissive Federal Register uses of
"open-weight" 2025–26). ⚠️ "NSTM-4" could not be verified — the verified
instrument is NSPM-11 (2026-06-05). The one verified government distillation
action is the NSA/CISA/FBI advisory AA26-251A (2026-09-08) — recommendations
are operational (detect, attenuate, correlate), no restriction on open release.
**Pause via law:** Sanders & Casar, Ban Artificial Superintelligence Act
(2026-09-03) — legislators, not labs. Casar/Matsui oversight letter to Altman
(2026-08-10, 31 signatories) — no open-weight mention.

**Named lab calls to restrict open weights, Aug–Sep 2026: null, and the
direction is inverted.** OpenAI, "The AI policy window is open" (2026-09-09):
"Nor should frontier safety policy become open-weights policy by another
name… A federal framework should address frontier capabilities and risks
without weakening competition, entrenching incumbents, or driving innovation
overseas." The July letter (~250 signatories incl. OpenAI/Google/Meta/
Microsoft/NVIDIA/HF): "the right response to this risk is not to prohibit open
weights"; "openness may be one of the most important paths to AI safety."
**Anthropic is the only major lab not signing.** The documented restriction
pressure is on the government side — Axios (2026-07-20; 403s, read via proxy):
Commerce weighed entity-listing Chinese labs, the White House an EO on hosting
Chinese models, draft supply-chain rules on Chinese open models — with **David
Sacks on record: "The leading closed labs, already a duopoly in terms of AI
model revenue, want the government to eliminate their open-source
competition."** [press-reported; the underlying X post not independently
retrieved]. Only two narrow pro-restriction op-eds (MacCarthy, TPP 08-13;
Remler, Just Security 08-17). Hassabis's framework (2026-07-14) covers open and
closed alike and exempts non-frontier — it does **not** exempt open weights;
the exemption belongs to the unpublished August framework.

**Marginal-risk evidence, verified.** Kapoor & Bommasani et al., ICML 2024
(PMLR 235:23082–23104; arXiv:2403.07918): "current research is insufficient to
effectively characterize the marginal risk of open foundation models relative
to pre-existing technologies"; six of seven studies analysed lacked sufficient
evidence of marginal risk — **not uniformly low**: NCII "considerable marginal
risk at present." NTIA (2024-07-30): "current evidence is not sufficient to
definitively determine either that restrictions… are warranted, or that
restrictions will never be appropriate" — monitor, don't restrict. Mozilla
Joint Statement (2023-10-31, open.mozilla.org/ai-safety, 1,821 signatures):
"openness is an antidote, not a poison" ⚠️ not Columbia-co-branded (the
Columbia Convening, 2024-02-29, is the separate joint effort). Fresh 2026,
both directions: UK AISI (2026-07-17) open models lag frontier cyber by **4–7
months** (down from 6–10); UK AISI/CAISI Kimi K3 assessment (07-23):
"significantly below" frontier on cyber, zero arbitrary-code-execution
outcomes vs 20/41; OpenAI's own gpt-oss study (2025-08-05): "may marginally
increase biological capabilities but does not substantially advance the
frontier."

**Anchors.** Yandle, "Bootleggers and Baptists," *Regulation* 7(3), May/June
1983, 12–16 — ⚠️ published by **AEI** (Cato now hosts the archive): "Bootleggers…
support Sunday closing laws… Baptists support the same laws and lobby
vigorously for them. Both parties gain." Stigler, "The Theory of Economic
Regulation," *Bell J. Econ.* 2(1) 1971, 3–21, DOI 10.2307/3003160 — the "as a
rule, regulation is acquired by the industry" sentence corroborated via
Coglianese/Sunstein, **not read in the original; no page**. Applications:
**Metcalf, "AI safety and regulatory capture," *AI & Society* 41(3) 2026,
CC-BY, cites both** (best academic cite; open-weight passage read only in
fragments — pull the PDF). ⚠️ **Must be cited against: Wei, Ezell, Gabrieli &
Deshpande, AIES 2024 (DOI 10.1609/aies.v7i1.31745), the one peer-reviewed
empirical study — 17 expert interviews found fear of *under*-regulation, and
on open weights recorded industry pushing for *exemption*.** Thielman, R
Street (2026-04-16), the direct B&B-on-AI commentary; Thierer & Chilson, R
Street (2023-06-05), the licensing critique.

**Net, for the paper:** the asymmetry claim is assertable only as (i) the
Amodei ask-set and (ii) the Axios-reported executive-branch deliberations with
Sacks's accusation — not as a property of lab incident reporting, which was
operational and self-binding throughout, and not as a legislative trend, which
runs toward exemption. The strongest new datapoint is the victim's own: closed
guardrails obstructed incident response and the defender reached for open
weights.

**The probe ledger — "testing the waters" as a gauge (Matthew's reading,
2026-09-13).** Register: a dated series of probes and rebuffs, each scored by
stated cause → remedy asked → whom it binds; no motive attributed. This is the
political-layer enclosure attempt as a *process* — an actor without a right
petitions repeatedly until the answer changes — and each rebuff is the political
layer declining, so far. Sacks's press-reported "every 3–5 months" is the
nearest direct statement of the cadence.

| Date | Probe / event | Stated cause | Remedy asked | Binds | Score |
|---|---|---|---|---|---|
| 2026-02-12 | OpenAI memo to House Select Cmte | DeepSeek distillation | bans, export controls | PRC labs | asymmetric (competitor-binding) |
| 2026-06-10 | Anthropic Senate Banking letter | Alibaba distillation | export controls, sanctions, antitrust clarification | PRC labs | asymmetric |
| 2026-07-16→08-26 | HF / OpenAI / METR incident disclosures | package proxy, unisolated sandboxes, disabled safeguards, impossible eval targets | isolation, hygiene, monitoring; OpenAI self-pause | self | **clean** |
| 2026-07-20 | Axios: exec-branch deliberations; Sacks accusation | — | entity-listing, hosting EO, supply-chain rules (considered) | PRC open labs | press-reported probe |
| 2026-07-24 | Open Weights & American AI Leadership letter (~250) | — | no premature restrictions; distillation legitimate | — | **rebuff** |
| 2026-07-27 | Amodei, open-weights position | distillation, PRC state backing | chip controls, distillation crackdown, mandatory testing above thresholds | PRC labs / frontier labs | asymmetric on 1–2; universal on 3 |
| 2026-07-30, 08-31 | Anthropic incident posts | CTF reachability, sandbox egress, RL env hygiene | hardened sandboxes, self-pauses | self | **clean** |
| 2026-08-04 | Unpublished framework exempts open weights | — | — | — | **rebuff** |
| 2026-09-08 | NSA/CISA/FBI AA26-251A | PRC distillation | detect, attenuate, correlate | operational | clean |
| 2026-09-09 | OpenAI "policy window" post | — | capability-based rules; "not open-weights policy by another name" | frontier labs | **rebuff (from a lab)** |
| 2026-09-12 | Amodei, "We Must Pace the Frontier" | "imperfect filtering of broken RL environments… sandboxing, training environment hygiene" | govt to *require* competitors to match embedded evaluators; regulation covering "those unwilling to cooperate"; chip controls; distillation crackdown | all US frontier labs + PRC | **asymmetric** |

Prediction the gauge makes: after the next disclosed incident, a call for
competitor-binding pacing within weeks; the reading is whether the political
layer's answer changes. ⚠️ The probes on record ask for *pacing mandates and
China-directed measures*, not open-weight bans — do not conflate. Carry Wei et
al. (AIES 2024) with any use.

**Sep 12–13 reactions — verified verbatim via an X mirror and the Guardian
(2026-09-13; x.com and the mirror both began CAPTCHA-ing before every item was
pinned — flags inline).**

- **Altman, @sama, 2026-09-12 16:30 UTC, status 2098811563415150910:** "I agree
  with Dario that we need to pace the frontier. **This has been a primary topic
  of discussions we've had at OpenAI in recent weeks.** Committing to having
  independent evaluators with employee-like access is a great idea, and we will
  do the same. We'll have more to share soon." (Corroborated by the Guardian,
  2026-09-13.) → endorses the *self-binding* step (evaluators, "we will do the
  same") and documents coordination; does **not** endorse the competitor
  mandate, chip controls, or the distillation crackdown.
- **Musk, @elonmusk:** "I've been sounding the alarm on AI for a long time"
  (2026-09-13 00:42 UTC, status 2098935235446551022, verbatim). "Dario is
  right" — verbatim per the Guardian; the fuller text seen only via a Gavin
  Baker repost summary, ⚠️ truncated/glossed: "Dario is right that there should
  be some oversight. Peer review of AI by competitors is the right way…" — i.e.
  an industry peer-review regime, not a government mandate. **ID and full text
  not pinned; re-verify in a browser before quoting beyond "Dario is right."**
- **Hassabis:** backing reported in headlines only (Anadolu, PRESS Insider,
  2026-09-13) — ⚠️ unverified; his July framework (standards body, voluntary
  30-day pre-release sharing, open and closed alike) is the known position.
- **Sacks (Guardian, 2026-09-13):** "Stop pretending you need anyone else's
  permission… You face massive product-liability exposure if your products
  enable a truly damaging cyber-attack." → the administration's answer is
  *liability already binds you*, not licensing — the rebuff pattern continues
  (cf. his Aug-18 "DMV for AI" line, Fortune). **Krueger** (ex-UK AISI): wants
  "an immediate, indefinite, international moratorium" — the Baptist voice,
  from outside the labs.
- **roon (@tszzl, OpenAI-affiliated), five posts, verbatim with IDs, in
  snowflake order:**
  1. status 2098820692137677116: "'pacing the frontier' will compress the
     margins of the frontier labs. it is a heavy cost imposed asymmetrically on
     model developers with the strongest AIs in America. by its nature, it would
     be a terrible regulatory capture tactic" — **carry as a counter alongside
     Wei et al.**
  2. status 2098833050083975220: "the risks from raising the capabilities
     waterline in internal deployments are much higher than misuse risks. a new
     model can outsmart you in weird ways, exfiltrate its weights etc.
     *training* becomes costlier, and deployment will stay the same: you should
     expect the gap to shrink"
  3. status 2098960424242921739: "there are many options between 'open weight
     superintelligence' and 'you can't send anybody your weights'. it could be
     that thousands of US businesses are finetuning powerful models, without
     giving them away to russian hackers and terrorists" — **the instrument
     being floated: a controlled-distribution / licensed-fine-tuning regime, not
     a ban** — exactly the excludability the legal analysis says no current
     right supplies.
  4. status 2099020654586806533: "i love them. i have a kimi k3 finetune running
     on tinker. bad things may happen with free distribution of open source
     models approaching superintelligence. the offense dominates the defense.
     if that happens, china/us will try to control it"
  5. status 2099020655861944392 (same second as 4): "this isn't my preferred
     outcome, just my prediction. i hope we can all keep having fun with this
     technology forever. it also has nothing to do with 'pacing the frontier',
     though i hope OS labs act with prudence too. i'm not trying to ban them nor
     do i have any power to lmao"
  **Read:** not "talking about banning open source." A lab-affiliated voice
  (a) predicting state control of open superintelligence, (b) explicitly
  disclaiming advocacy and power, (c) floating a controlled-distribution middle
  regime as the plausible landing — framed as forecast, hence deniable. Enters
  as a **gauge reading** (the shape of the instrument being normalized), never
  as evidence of policy. His "offense dominates the defense" is directly
  testable against HF's incident finding that closed guardrails obstructed the
  defenders and the defender reached for open weights.
  ⚠️ Mirror timestamps rendered in mixed zones; the snowflake IDs are the
  reliable ordering.

**What Sep 12–13 adds to the ledger:** the duopoly plus xAI converged publicly
on "pace the frontier" within a day, and Altman's post documents the
coordination in his own words — so the probe is an industry posture, not one
CEO's. **But what they converged on is the self-binding half** (evaluators
with employee-like access; peer review by competitors), not the
competitor-mandate/chip/distillation asks, which remain Amodei's alone. The
scarcity-compatible reading of *that* is different from open-weight
restriction: a coordinated pacing regime among the leaders is cartel-shaped
(Stigler's "regulation acquired by the industry"; it slows the race among
themselves and, if mandated, raises rivals' costs — Thierer & Chilson). The
honest counter is roon's post 1 and OpenAI's own 09-09 framing: the costs land
on the frontier labs asymmetrically. Both go in.

**⚠️ Register correction (Matthew, 2026-09-13): do not take the participants'
characterizations at face value — analyse the regime's effects.** The entries
above let denials do evidentiary work they cannot do. Under
bootleggers-and-Baptists the stated reason and the regulatory effect are
*expected* to diverge, so a participant saying "this would be a terrible
regulatory capture tactic" is evidence that the accusation was live enough to
require an answer, not evidence about the regime. The paper's claim rests on
**effects, stated in the proposal's own terms**, and needs no motive:

1. **The call is, at face value, a call for power.** Amodei asks for
   "regulation that targets all US frontier AI companies, as that covers even
   those who are unwilling to cooperate voluntarily," and "calls on governments
   to require other frontier companies to match" what Anthropic adopts
   voluntarily. That is a request for the state to bind rivals to the leader's
   current practice — the leaders' practice becomes the compliance floor. No
   attribution required; it is the text.
2. **Implementation complexity is the mechanism, and it is asymmetric by
   construction.** Embedded evaluators with employee-like access, mandatory
   testing above thresholds, and a coordination body impose *fixed* costs and
   *access obligations*: trivial at >$500M AI revenue, heavy for a small lab,
   and **undefined for a non-corporate open project** (who grants "employee-like
   access" to a Kimi-K3 finetune community?). The thresholds that decide who is
   "frontier" are written by the parties they would bind. This is
   raising-rivals'-costs (Stigler 1971; Thierer & Chilson 2023; Metcalf 2026):
   the leaders can pay *and* the regime excludes challengers — those are
   compatible, and roon's margin-compression post conflates absolute cost to
   the leaders with relative burden, which is the quantity capture is about.
3. **Coordination is documented, in the leaders' own words.** Altman: "a
   primary topic of discussions we've had at OpenAI in recent weeks"; three
   CEOs converging within a day on the same regime. A voluntarily adopted
   practice among an oligopoly, then requested as a mandate on all — that is
   the form in which an industry acquires its regulation. My earlier "only the
   self-binding half" softening missed that self-binding-then-mandated is the
   capture pattern, not an alternative to it.
4. **Wei et al. (AIES 2024) is time-mismatched.** Its interviews date from a
   period when industry pushed for *exemptions*; the 2026 posture is a request
   for *mandates*. It stays in the ledger as the peer-reviewed prior, with the
   note that it does not describe the 2026 asks.
5. **roon's posts, re-read as effects rather than statements:** the
   "many options between open-weight superintelligence and you can't send
   anybody your weights" post names the instrument (controlled distribution);
   the capture-denial post answers a criticism already in circulation (Sacks
   08-18 "DMV for AI"; Fortune; multiple 09-13 pieces); the "just my
   prediction… i'm not trying to ban them" post is the deniability wrapper.
   Read together they are a lab-affiliated voice normalizing a
   licensed-distribution regime while disclaiming it — the shape of a probe.
   ⚠️ Matthew reports a further post predicting regulation of open source
   **by requiring provision through licensed endpoints** — the instrument named
   explicitly (open weights re-gated behind licensed serving, i.e. excludability
   manufactured and chokepoints created, operated by the incumbents). **Not yet
   retrieved (mirror CAPTCHA); verify and pin the ID.** If confirmed it is the
   sharpest entry in the ledger.

**Paper-safe statement of the claim:** *As specified, the proposed pacing regime
imposes fixed compliance and access costs that fall inversely with firm size and
are undefined for non-corporate open projects; its capability thresholds are
set by the firms it would bind; and it asks the state to extend the leading
firms' current practices to unwilling parties. That structure raises rivals'
costs irrespective of the sincerity of its safety rationale.* — effects, not
motives, and every clause is from the proposal's own text.

**⭐ RETRIEVED — the endpoints post, primary (X syndication endpoint, verbatim,
2026-09-13).** roon (@tszzl), **2026-09-12T20:44:29Z, status
2098875417373634944**, replying to @sean_from_earth (status
2098853078170738955):

> "@sean_from_earth i won't lie to you, i think open source will be banned
> before too long after some major disaster. and when the day comes, you'll
> agree with me. i hope kimi and deepseek etc keep making models but **keep
> them monitored on an api where they should be**"

The parent post, verbatim — and it is the capture argument stated in full:

> "@tszzl The only possible way to pace it is to ban open source, which can
> only be done with some regulatory framework that inevitably creates a
> duopoly or cartel that can then set prices however they like."

**Read (effects, not motive):** (i) the instrument is named — open models
"monitored on an api" — i.e. open weights re-gated behind hosted endpoints,
which manufactures the excludability no current right supplies and places the
chokepoints with whoever runs the endpoints; (ii) it is stated as prediction
*and* preference ("where they should be"); (iii) the parent post laid out
pacing → open-source ban → framework → duopoly/cartel pricing, and the reply
does not dispute the mechanism — it accepts the ban as coming "after some major
disaster" and adds that the critic "will agree"; (iv) **sequence, by snowflake
ID:** this post (…875…, 20:44Z Sep 12) *precedes* the "i love them… offense
dominates the defense" / "this isn't my preferred outcome, just my prediction…
i'm not trying to ban them" pair (…020654…/…020655…, ~06:21Z Sep 13). The
retreat followed the statement. That ordering is what makes the later pair a
deniability wrapper rather than the position. **This is the sharpest entry in
the probe ledger:** a lab-affiliated voice, answering the capture argument
directly, naming the endpoint-gating regime as where open models "should be."

**Second post, reported (Brave snippet; archive.is/s6NwT is unreachable from
here; ID pending):** replying to @jd_pressman and @zetalyrae — "i'll say it
straightforwardly… i can't imagine a world a year from now in which open
source models aren't harshly regulated." ⚠️ pin the ID before quoting.

**Adjacent, verified (PYMNTS):** on **2026-06-26** OpenAI limited release of
the GPT-5.6 series "to a small group of trusted partners" whose identities were
shared with the US government, at the government's request — "the strongest
path to broader availability in the coming weeks, while we work with the
Administration to develop the cyber Executive Order framework and repeatable
process for future model releases." The gated-access regime already operates
for closed frontier models under EO 14409; the endpoints post describes
extending its logic to open weights.

**The moral-hazard structure (Matthew, 2026-09-13) — effects form, no motive.**
Three verifiable components: (i) the labs benefit from open-weight restriction
(open weights commoditize their product — the thread's core); (ii) the
restriction's trigger, per the lab-affiliated forecast, is "some major
disaster"; (iii) the labs run the most capable agent swarms in environments
whose containment they control, and the cost of the July containment failure
fell on a third party (HF production). A party that controls a risk, does not
bear its cost, and benefits from its realization = moral hazard. **Use the
weak form** — reduced incentive to prevent plus incentive to shape attribution
— which is sufficient and requires no claim that anyone causes anything.
**The mechanism by which reactions skip marginal-risk discipline is
published:** Kuran & Sunstein, "Availability Cascades and Risk Regulation,"
*Stanford L. Rev.* 51 (1999) — salient events drive risk perception,
amplified by "availability entrepreneurs" who benefit (the bootlegger role in
a disaster); Kingdon (1984) focusing events; Birkland, *After Disaster* (1997).
[Handles from memory — verify; Kuran is already in the paper's verified set for
other work.] Kapoor/Bommasani's marginal-risk discipline is the exception the
cascade suspends.
**The HF incident as template:** a closed model, a closed lab's sandbox, a
third party's production — and the discourse it produced was a frontier
pacing regime plus open-source-ban forecasts. Attribution followed the layer
that can be controlled, not the layer that did it. Contested, not automatic:
the victim's disclosure said closed guardrails obstructed defenders and reached
for open weights.
**Counter to carry:** the incident cost the labs real things (paused training,
~150 engineers redirected, the Casar/Matsui letter, the Sanders/Casar bill).
And **Sacks's liability line is the moral-hazard-correcting instrument** —
liability re-internalizes the cost; licensing would externalize it again by
making compliance a liability shield. The probe is therefore, in effect terms,
a contest over *which instrument* governs the next incident: liability
(internalizes) vs licensing/endpoint-gating (externalizes and encloses).
**Watch variable:** after the next incident, does the restriction discourse
target the layer that caused it or the layer that can be controlled.
