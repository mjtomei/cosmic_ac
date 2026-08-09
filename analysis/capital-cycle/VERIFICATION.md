# Primary-verification pass — capital-cycle report 2e

2026-08-04, web-search agents. Scope: the "cheap primary-verification" items from
handoff §5/§8 — the figures that rode on the report's ref [28] (Stansberry/Porter
& Co., a marketing essay; **never cite [28] as an authority in paper text**) and
are load-bearing for the outline-IV.3 integration. Everything else in [28]'s
list (per-name July long/short returns, express-company/Pullman financials,
Cooke/NP detail, NYSE volume shares, London issuance, Oracle/CoreWeave terms,
Hyperion SPV terms, capex/OCF ratios) remains **unverified** — re-anchor before
paper use.

## Moody's hyperscaler capex — VERIFIED, with a universe correction

Moody's Ratings (May 2026 forecast update; +$85B revision from March 2026)
projects **$785B of 2026 capex, approaching ~$1T in 2027 — for the six largest
US hyperscalers: Microsoft, Amazon, Meta, Alphabet, Oracle, CoreWeave.** The
figures check out, but the universe is narrower than "AI/datacenter capex":
it includes those firms' non-AI capex and excludes non-hyperscaler datacenter
build. AWS capex is Moody's estimate (Amazon doesn't break it out). Don't
conflate with Moody's Dec-2025 global datacenter outlook (≥$3T over five
years — a different, broader number). Attribute: "Moody's Ratings, May 2026,
capex of the six largest US hyperscalers."
Sources: datacenterdynamics.com (Moody's markup coverage), cnbc.com/2026/07/24
(Moody's AI spending & credit quality), Moody's own podcast page.

## Bain ~$800B shortfall — VERIFIED

Bain & Company, 6th annual Global Technology Report, press release 2025-09-23:
**~$2T in annual revenue needed by 2030** to fund the compute to meet
anticipated AI demand; even redirecting all on-prem IT budgets to cloud and
reinvesting all AI-driven savings, **the world is ~$800B short** annually.
Context figures: ~200 GW incremental global AI compute by 2030 (~half US),
~$500B/yr capex to deploy. Framing caution: Bain states a **funding gap**, not
"AI companies' revenue shortfall" — use Bain's framing.
Source: bain.com press release ("$2 trillion in new revenue needed to fund
AI's scaling trend"), report hub bain.com/insights/topics/technology-report/.

## Depreciation 10-K inventory — VERIFIED, with a metric correction

All figures anchored to verbatim SEC-filing language (URLs below). **The
secondary essay mixed two metrics**: filings disclose a pre-tax operating-level
effect (D&A / opex reduction) and an after-tax net-income effect. The essay's
list (MSFT 3.7 / GOOG 3.0 / AMZN 2.5 / META 2.6 / ORCL 0.6) is Microsoft's
operating figure plus everyone else's net figure. The consistent series:

| Company | Change | Fiscal yr | Operating-level | Net income |
|---|---|---|---|---|
| Microsoft | 4y→6y servers+network (Jul 2022) | FY2023 (end 6/2023) | **+$3.7B** | +$3.0B |
| Alphabet | servers 4y→6y, some network 5y→6y (Jan 2023) | 2023 | **+$3.9B** | +$3.0B |
| Amazon | servers 5y→6y (Jan 2024) | 2024 | **+$3.2B** | +$2.5B |
| Meta | to 5.5y (Jan 2025) | 2025 | **+$2.92B** (realized) | +$2.59B |
| Oracle | 5y→6y (FY2025); earlier 4y→5y FY2023 +$434M opex | FY2025 (end 5/2025) | **+$0.733B** | +$0.573B |

Sum: operating-level ~$14.5B/yr; net ~$11.7B/yr. The report's ">$12B of
reported operating income" survives numerically only by accident of the mixed
series — corrected in the report text to label the series properly.

**Amazon reversal — CONFIRMED.** FY2024 10-K: subset of servers/networking
6y→5y effective 2025-01-01, "due to an increased pace of technology
development, particularly in the area of artificial intelligence and machine
learning"; anticipated ~$0.7B 2025 operating-income decrease (assets in
service at 12/31/24 only). FY2025 10-K actual: **+$1.4B D&A increase / −$1.0B
net income, primarily AWS**. Separate and additive, don't conflate: ~$920M
accelerated depreciation Q4-2024 + ~$0.6B in 2025 from early retirements of
certain servers/network equipment.

Sources (verified verbatim): MSFT FY2023 10-K
sec.gov/Archives/edgar/data/789019/000095017023035122/msft-20230630.htm ·
GOOGL FY2023 10-K .../1652044/000165204424000022/goog-20231231.htm ·
AMZN FY2024 10-K .../1018724/000101872425000004/amzn-20241231.htm, Q1-2025
10-Q .../000101872425000036/amzn-20250331.htm, FY2025 10-K
.../000101872426000004/amzn-20251231.htm · META FY2024 10-K
.../1326801/000132680125000017/meta-20241231.htm, FY2025 10-K
.../000162828026003942/meta-20251231.htm · ORCL FY2025 10-K
.../1341439/000095017025087926/orcl-20250531.htm

## US railroad ton-mile revenue series — CLOSE, 1870 endpoint corrected

**1900 = 0.729¢ confirmed exactly** (NBER Macrohistory A0303BUSA259NNBR, all
railroads, computed from Poor's Manual, 1882–1911; Fishlow Table 1 gives 0.73¢
via Barger/ICC). **1870 = 1.88¢ appears in no canonical series** — no
all-railroad series reaches 1870 (the Historical Statistics/Poor's all-road
series starts 1882 at 1.236¢). Documented 1870 values: Fishlow's all-road
estimate **2.18¢** (interpolated, his own caveat) or the NBER/Frickey
13-railroad trunk-line sample **1.802¢** (runs below the national average).
The 1.88¢ looks like an unsourced blend of the two.

**Correction adopted for the report:** cite Fishlow (NBER, Table 1): ~2.2¢
(1870, estimated) → 0.73¢ (1900), a **~66% nominal** decline — and note it is
nominal (the general price level also fell 1870–1900, so the real decline is
smaller). The deflation-clock passage's "61%" becomes "roughly two-thirds."
Sources: fred.stlouisfed.org/series/A0303BUSA259NNBR ·
fred.stlouisfed.org/series/A0303FUSA259NNBR ·
nber.org/system/files/chapters/c1578/c1578.pdf (Fishlow) ·
www2.census.gov/library/publications/1949/compendia/hist_stats_1789-1945/hist_stats_1789-1945-chK.pdf

## US railroad mileage series — VERIFIED exactly

Historical Statistics of the United States, Bicentennial Ed., pp. 731–732
(underlying: Poor's Manual):
- **1865 = 35,085 / 1875 = 74,096 miles of road operated** — exact match,
  Series Q 321 (also in the 1949 ed., Series K 1). 2.11× — "roughly doubled"
  is fair.
- **7,439 miles built in 1872** — exact match, Series Q 329 (also NBER
  Macrohistory A02F2AUSA374NNBR). The "1871" variant seen elsewhere is ΔQ 321
  (net road-operated added: 7,379 peak in 1871) — different series, same
  primary.
- **2,665 (1878) → 11,569 (1882)** — exact first differences of Q 321 (4.34×;
  "quadrupled" holds). Sorkin (1997, in Glasner, *Business Cycles and
  Depressions*) quotes the same pair. Miles-built series alternative:
  2,428 → 11,599 (4.78×), which strengthens the claim.

One flag for precision: the report mixes the two adjacent series (7,439 is
miles built; 2,665→11,569 is net additions). Both are HSUS/Poor's; noted in
the report's source entry rather than changing the numbers.
Sources: www2.census.gov/library/publications/1975/compendia/
hist_stats_colonial-1970/hist_stats_colonial-1970p2-chQ.pdf ·
fred.stlouisfed.org/series/A02F2AUSA374NNBR

---

## Recognition-half-life sourcing (2026-08-06, for `recognition_halflife.py`)

**WorldCom depreciable lives + plant mix — VERIFIED (EDGAR full-submission
texts, CIK 0000723527, high confidence).** Disclosed lives, FY1998–FY2000
10-Ks: transmission equipment *including conduit* 5–45y; communications
equipment 5–20y; furniture/fixtures/buildings 4–40y. FY2001 10-K quietly moved
the maxima (45→40, 20→10) while stating "no material changes in asset lives."
Gross plant mix as reported at 12/31/2001 ($48.7B): transmission 49%, comm
equipment 16%, furniture/buildings/other 23%, CIP 12% — **~70% of gross plant
in classes with 40–45-year disclosed maxima**. The restated FY2002 10-K
(Note 4, verbatim): ocean cable had been on 40y against ~11y average contract
lives; **fiber cut 40→25y; fiber-optic electronics 15→8y**; life-error
adjustments −$1.0B (2001) / −$672M (2000) pre-tax; the $3.9B of capitalized
line costs flowed into the same long-lived transmission accounts; total
restatement took equity down $70.8B. Recognition of the era's loss was
event-shaped: nothing disclosed contemporaneously 1999–2002, then the
2002–04 restatement/impairment wave. Filings: 10-Ks FY1997–FY2003, accessions
in the agent ledger (0000950134-98-002566 … 0001193125-04-074088).

**Qwest / US WEST lives + plant mix — VERIFIED (EDGAR full-submission texts,
CIKs 1037949 / 0000068622, high confidence).** ILEC (US WEST/Qwest Corp):
telecom outside plant **8–57y, unchanged 1998–2003**; network/communications
equipment 8–14y (later 7–10y ILEC, 2–25y consolidated — the 25y tail is
20-year IRU optical capacity); plant mix ~50/50 outside plant vs electronics
by dollars with ~4× life difference at the top. Pre-merger long-haul Qwest:
fiber network 10–25y, **$2.3B fiber vs $117M electronics** — the overbuild
dollars sat in the long-lived class. Life changes were quiet table deltas
(only one narrative disclosure, FY1999); the recognition event was the 2002
**$10.5B PP&E impairment**, which cut go-forward depreciation ~$900M/yr.
Use the FY2002 10-K for a consistent restated series.

**Williams / 360networks / Broadwing lives + mix — VERIFIED (EDGAR, high
confidence).** Williams (the only carrier splitting fiber from electronics):
fiber **25–30y**, optronics **7–10y**, right-of-way 20–40y; FY2000 gross plant
ex-CIP: fiber+ROW **48.5%** vs optronics **28.8%**, computers/furniture 4%,
buildings 9%. WilTel fresh-start (Oct 2002), verbatim: PP&E useful lives
changed **"from a weighted average life of 21 years to 15 years"** alongside a
$2.4B book-value reduction; D&A fell ~52%/month. 360networks: fiber flat 25y
(FY1999) → 15–25y (FY2000), never labeled a change; $429M of fiber sat
undepreciated as *inventory*. Broadwing: transmission facilities bundled
3–20y, 86% of ex-CIP plant FY2001; FY2002 exit was a $2.2B impairment, not a
life change. Pattern across all three: life changes were silent table drifts;
recognition arrived as impairment/bankruptcy events.

**Railroad-era depreciation practice — VERIFIED (scholarly + ICC primaries,
high confidence).** No depreciation on anything before 1907 ("a virtual
absence of depreciation accounting by the railroads," Ulmer, NBER 1960);
retirement/replacement/betterment (RRB) accounting carried original cost
indefinitely, expensing replacement-in-kind. Date ladder: equipment
depreciation at carrier-chosen rates 1907 (Hepburn Act rules; upheld
*Kansas City Southern v. US*, 1913), ICC-prescribed composite rates 1935;
road ex-track **1943**; track structures **1983** (FAS 73) — 80–120 years
after the 1865–1900 buildout. Even then: ICC composite road rate 0.86%/yr
(1917) ≈ 116-year implied life; grading explicitly non-depreciating
(Engineering Board Memo 226); equipment composite 3.5% ≈ 28.6y.
Capital composition: **road ~90–94% / equipment ~6–10%** (ICC balance sheets
1902/1906/1908; Fishlow Table 6 constant-dollar stock agrees: 6.4–9.9%
equipment 1869–99). Handles: Brief JAR 1965 + BHR 1966 ("about 50 per cent
of the track mileage constructed in the US prior to 1900 was placed in
receivership"); Heier AHJ 2006; Heier & Gurley AHJ 2007; Sivakumar & Waymire
JAR 2003. Receivership peaks measured: **18.2% of mileage Jan 1877, 20.4%
Mar 1894** (Swain, AEA 1898 — sharper than the 2e's ~20%/~25%, which
conflated mileage with Ripley's ~25% of *capitalization* cumulative
1893–97; correct the report if the claim is reused). **Model-critical
nuances:** (i) renewal accounting DID expense replacement-in-kind — what it
never recognized was a vintage's capitalized cost (obsolescence, deferred
maintenance, write-downs); Brief 1965's argument is that era income and ROC
were overstated. (ii) Reorganization wrote down claims, not assets: fixed
charges −29% against capitalization +13% on 35,000+ reorganized miles
(Ripley 1915) — the asset account survived even the event channel.

**Railroad reconciliation notes (full agent report, 2026-08-06).** Composition:
the two ICC-1908 readings differ (equipment $1.18B → 9.0% vs $2.18B → 15.5% —
digit-level discrepancy in extraction; the 1897 5.5% is a stated lower bound
because "cost of road includes cost of equipment of certain roads"). Fishlow's
independent constant-dollar physical-unit series gives **6.4–9.9% equipment
across 1869–99**, so the model's 92/8 stands for the era; at 85/15 the
ICC-counterfactual half-life moves 53→~48y and the era row is "never" under
any split. Receivership calibration (Swain 1898, primary tables): **18.19% of
mileage Jan 1877; 20.43% Mar 1894**; Ripley's "one-quarter" is of aggregate
*capitalization* 1893–97 — report and outline corrected accordingly. Relay
practice: rail ran two cycles (new→relay traffic-dependent; relay→scrap 50y,
sidetrack 75y); the "indefinite" bridge classes renewed in fact at ~28.6y
average. Working-file cache: session scratchpad (Daggett/Ripley/Swain/Schultz/
ICC texts).

**Railroad service-lives addendum (parallel pass, 2026-08-06).** Era engineers
quoted rail life in **gross tons, never years** (iron ~4–15M tons, modal 8M ≈
3.3y at 1910 density; steel 100–250M tons — Wellington, Camp 1903, Fishlow);
ties untreated ~5–9y (USDA Bull. 118 Table 12), creosote +100–500%; trestles
7–10y (the non-indefinite exception); Fishlow excludes rails and ties from the
depreciated stock outright ("their lives are short") and levies 1%/yr on
earthworks. Locomotive/car consensus 20–25y (Fishlow); ICC equipment composite
3.50% (1917). **Citation flag: 118 I.C.C. 295 (1926, Ex Parte 15100) has no
reachable digitized text — do not cite it for any number; use Ulmer's dates
(equipment rates fixed 1935-01-01, road depreciation 1943-01-01).**

**Telecom buildout composition + lives + write-off waves — VERIFIED (FCC
SOCC/ARMIS, FCC orders, EDGAR, OECD; high confidence except where noted).**
Scale: US telecom capex 1996–2001 = **$513.3B** (USTelecom series), −39% by
2002. ILEC account-level (SOCC Table 2.7): capex flow 32.2% long-lived
(cable&wire+buildings+land) / 56.7% electronics; **stock end-2001 49.3%
long-lived** — the flow→stock gap is the storable loss accumulating; composite
implied book life **14.1y**, accumulated depreciation 54.7%. FCC-prescribed
lives (FCC 99-397, App. B): fiber 25–30y, conduit **50y** (Bureau-decided,
DA 03-2738), digital switching 12–18y, circuit equipment 11–13y — and the FCC
**refused to shorten** all but digital switching over uniform ILEC objection
(carriers proposed fiber 20, circuit 6–9). Greenfield long-haul: **70–78% of
gross plant in >15y classes** (Level 3 77.3% FY2001; Williams 48.5% fiber+ROW
ex-CIP; Qwest ~50%); blended storable share of the $513B ≈ 40–50% [MEDIUM —
segment weighting inferred]. Stated ≠ realized: implied composite lives ran
Level 3 6.7y / XO 6.6y (electronics dominated the *depreciating* base while
fiber sat in CIP); GX pre-Oct-1999 and 360networks carried fiber as
*inventory/capacity-for-sale* — no clock at all. Recognition waves: 2001
SFAS-121 impairments (JDSU **$50.1B** FY2001 10-K figure; GX ~$20B, ~97% in
Q4-01, plant 17.9% depreciated when impaired 74%; Level 3 $3.2B incl. $1.2B
excess conduits; Williams $2.98B incl. $1.88B dark fiber/conduit; Nortel
$12.4B; Corning $4.6B; 360networks $4.4B) then 2002 SFAS-142 transition
(Qwest $22.8B+$8.5B+$10.5B; AT&T Broadband $16.5B; XO $1.9B; WorldCom
audited $64.8B impairments 2000–02, equity −$70.8B) — FAS 142 ¶56's
below-the-line Q1 treatment made 2002 a dated amnesty window (Willens/WSJ).
Sector aggregate: OECD 2003 — 2001 balance-sheet reductions $243B intangibles
+ $63B tangibles across 78 operators (~80/20 split); US transitional-142
aggregate defensibly $100–150B. **Attribution corrections applied to
report+outline: the "$2T erased" is Powell's Senate figure (2002-07-30), not
The Economist's (whose number was ~$1T debt, half unrecoverable).**

**Impairment-wave addendum (parallel pass, 2026-08-06).** Final audited
figures where earlier ones were preliminary: JDSU $50.1B FY2001 10-K
($56.1B over FY01–02); WorldCom audited restatement $64.8B impairments
2000–02 / equity −$70.8B ($79.8B was the Mar-2003 preliminary vs the
fraudulent balance sheet); Qwest transitional $22.8B + $8.5B goodwill +
$10.5B PP&E, FY2002 loss $38.5B; AT&T Broadband $16.5B pretax/$11.8B after
tax; GX FY2001 loss $22.6B, ~97% of its ~$20B impairment in Q4-01, **audited
capex ~$9.7B 1998–2002 (the "$12–15B network" is press-only — report
corrected)**, reorganization value $407M = 1.3–2% of $30.2B peak book
assets. Fiber-lit correction: TeleGeography Sept 2003 = **3.9% of Chicago
long-haul fiber lit** (2.7% was the IP share of the lit portion); ~1–2% of
theoretical capacity in use — the report's "3–5%" stands. Aggregate
discipline: "$750B–$1T of 2002 goodwill write-offs" is untraceable folklore;
use $100–150B transitional (Huefner & Largay; Li et al.) + OECD's $243B
intangibles/$63B tangibles (2001). Full agent ledger with URLs in the task
output; cached filings in the session scratchpad.

## Inference margins and revenue mix (2026-08-07, prompted by Matthew's challenge)

Occasioned by two errors, one in each direction. **Claude's (in conversation,
never in the repo): "inference is sold below cost" — WRONG.** Marginal serving
is profitable; DeepSeek's own February 2025 disclosure put a day of V3/R1
inference at $87,072 of GPU rental against $562,027 theoretically billable
(self-labeled *theoretical*: free web/app tiers, off-peak discounts, realized
revenue far lower). **Matthew's ("most revenue is APIs at very high margin") —
WRONG for OpenAI on both counts, half-right for Anthropic.**

- **Revenue mix.** OpenAI: API ≈ **25% of a $12B run rate** (FT, Aug 2025,
  high confidence) — subscriptions are the majority. Caution: OpenAI's ">40%
  enterprise" framing bundles ChatGPT Enterprise/Business *seats* with API, so
  a clean three-way split is nowhere disclosed; what is solid is
  seat-subscriptions ≫ API. Anthropic: API+enterprise dominant, **~75–85%
  (estimated; no segment disclosure — S-1 confidential)** — Matthew's mix
  claim is right here.
- **The margin figures that circulate are not gross margins.** DeepSeek's 545%
  and OpenAI's ~70% are marginal-serving/compute-margin ratios. Blended
  **adjusted gross margin: OpenAI ~33% in 2025, down from 40%, below its own
  46% plan** (The Information, secondhand — reported-not-disclosed);
  **Anthropic guided ~40% for 2025, cut ~10 points** when GCP/AWS-rented
  inference overran ~23%. Renting inference caps the margin. Leaked H1-CY2025
  inference spend ($5.0B) exceeded H1 revenue ($4.3B) because that line
  includes non-revenue compute.
- **Flat rates invert SaaS logic:** heaviest users are least profitable —
  Altman, Jan 2025, on losing money at $200/month. Free-tier drag estimated
  20–30pp (low confidence).
- **Application layer:** "near zero" was directionally right but too strong.
  ICONIQ survey (n≈300, Jan 2026, the best structured evidence): app-layer
  gross margin **33% (2024) → 38% (2025) → 45% (2026 proj)** vs 75–85% SaaS.
  Flagship AI-native firms ran **negative** gross margin at billions of ARR
  (Cursor ≈ −23% to −30%), flipping positive **by integrating backward into
  their own models** — a rents-migrate-to-whoever-owns-inference story, not a
  permanent-zero story. Report text softened to "does not earn what its
  software analogues did" and the whole reconciliation added as a new §3.3
  paragraph + source [37].

**Why the $330–350B aggregate survives:** it is *economic rent* — profit above
a normal return, after all costs — not gross margin. Healthy marginal serving
economics and zero economic rent at the model layer are fully compatible, and
the 33–40% blended gross margins make the "thin direct-AI margin" language
closer to right than either challenge assumed.

**Net effect on the outline integration:** the three-record precedent bullet's
US mileage and ton-mile numbers can now carry [REAL] on primaries (HSUS,
NBER Macrohistory, Fishlow), with the 1870 ton-mile endpoint restated as
~2.2¢ (Fishlow, estimated). The Cooke/Northern Pacific detail, 87%-of-NYSE
volume, London issuance share, and default counts remain [28]-only.
