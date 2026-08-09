#!/usr/bin/env python3
# "Assets, Rents, and the Socialized Buildout" - Second edition, August 4, 2026.
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, HRFlowable)

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "assets-rents-socialized-buildout-2e.pdf")
PW, PH = letter
M = 0.95 * inch

body = ParagraphStyle('body', fontName='Times-Roman', fontSize=10, leading=14,
                      alignment=TA_JUSTIFY, spaceAfter=7)
h1 = ParagraphStyle('h1', fontName='Times-Bold', fontSize=13, leading=16,
                    spaceBefore=16, spaceAfter=6)
h2 = ParagraphStyle('h2', fontName='Times-Bold', fontSize=10.5, leading=13,
                    spaceBefore=10, spaceAfter=4)
title_s = ParagraphStyle('t', fontName='Times-Bold', fontSize=21, leading=25,
                         alignment=TA_LEFT, spaceAfter=6)
sub_s = ParagraphStyle('s', fontName='Times-Italic', fontSize=11.5, leading=15,
                       alignment=TA_LEFT, spaceAfter=4, textColor=colors.HexColor('#333333'))
by_s = ParagraphStyle('b', fontName='Times-Roman', fontSize=9.5, leading=12,
                      alignment=TA_LEFT, textColor=colors.HexColor('#444444'), spaceAfter=2)
abst = ParagraphStyle('a', fontName='Times-Roman', fontSize=9.5, leading=13,
                      alignment=TA_JUSTIFY, leftIndent=22, rightIndent=22, spaceAfter=6)
cap = ParagraphStyle('c', fontName='Times-Italic', fontSize=8.8, leading=11,
                     alignment=TA_LEFT, spaceBefore=3, spaceAfter=10)
ref = ParagraphStyle('r', fontName='Times-Roman', fontSize=8.8, leading=11.6,
                     alignment=TA_LEFT, leftIndent=14, firstLineIndent=-14, spaceAfter=3)
note = ParagraphStyle('n', fontName='Times-Roman', fontSize=8.8, leading=11.6,
                      alignment=TA_JUSTIFY, spaceAfter=5, textColor=colors.HexColor('#222222'))
cellp = ParagraphStyle('cp', fontName='Times-Roman', fontSize=7.3, leading=9.2,
                       alignment=TA_LEFT)
cellb = ParagraphStyle('cb', fontName='Times-Bold', fontSize=7.3, leading=9.2,
                       alignment=TA_LEFT)

def footer(canv, doc):
    canv.saveState()
    canv.setStrokeColor(colors.HexColor('#999999')); canv.setLineWidth(0.4)
    canv.line(M, 0.62*inch, PW-M, 0.62*inch)
    canv.setFont('Times-Roman', 8); canv.setFillColor(colors.HexColor('#555555'))
    canv.drawString(M, 0.46*inch, "Assets, Rents, and the Socialized Buildout - Second Edition, August 2026")
    canv.drawRightString(PW-M, 0.46*inch, f"Page {doc.page}")
    canv.restoreState()

doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=M, rightMargin=M,
                      topMargin=0.85*inch, bottomMargin=0.85*inch,
                      title="Assets, Rents, and the Socialized Buildout (Second Edition)",
                      author="Claude (Anthropic), from a dialogue with Matthew Tomei")
frame = Frame(M, 0.85*inch, PW-2*M, PH-1.7*inch, id='f')
doc.addPageTemplates([PageTemplate(id='p', frames=[frame], onPage=footer)])

S = []
def P(t, st=body): S.append(Paragraph(t, st))
def H(t): S.append(Paragraph(t, h1))
def H2(t): S.append(Paragraph(t, h2))
def SP(h=6): S.append(Spacer(1, h))

def tbl(data, widths, fontsize=8.6, header=True, align_right_from=1):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), fontsize),
        ('LEADING', (0,0), (-1,-1), fontsize+2.4),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (align_right_from,0), (-1,-1), 'RIGHT'),
        ('LINEBELOW', (0,0), (-1,0), 0.7, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 0.7, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.7, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F4F2EE')]),
    ]
    if header:
        style.append(('FONTNAME', (0,0), (-1,0), 'Times-Bold'))
    t.setStyle(TableStyle(style))
    S.append(t)

def ptbl(data, widths):
    rows = []
    for i, row in enumerate(data):
        st = cellb if i == 0 else cellp
        rows.append([Paragraph(c, cellb if (i == 0 or j == 0) else cellp)
                     for j, c in enumerate(row)])
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,0), 0.7, colors.black),
        ('LINEABOVE', (0,0), (-1,0), 0.7, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 0.7, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F4F2EE')]),
    ]))
    S.append(t)

# ----------------------------- TITLE BLOCK -----------------------------------
P("Assets, Rents, and the Socialized Buildout", title_s)
P("An accounting of the AI capital cycle: market values, capital stocks, revenue "
  "requirements, the buildout precedents, and the July 2026 rotation", sub_s)
SP(2)
P("Prepared by Claude (Anthropic) from a dialogue with Matthew Tomei &#183; Second edition, "
  "August 4, 2026", by_s)
S.append(HRFlowable(width='100%', thickness=0.8, color=colors.black, spaceBefore=8, spaceAfter=10))
P("<b>Abstract.</b> Roughly $27 trillion of equity value has attached to AI-related companies "
  "since November 2022, against which the physically deployed, depreciation-adjusted AI capital "
  "stock is on the order of $1.2 trillion. This report separates the two quantities and sizes what "
  "must fill the gap. It builds a vintage model of the AI capital stock, reprices it at competitive "
  "supply-chain margins, backs out the economic-rent stream the market has capitalized, and inverts "
  "that requirement into the share of world GDP that must flow to AI at plausible margins. It "
  "calibrates the requirement against forty years of IT-spending history; develops three completed "
  "buildouts - Britain's Railway Mania, the American railroads, and telecom 1996-2002 - as "
  "structural precedents, covertly socialized infrastructure programs whose losses funded a "
  "commons; introduces the toll-booth layer that historically kept the profits the network capital "
  "never earned; maps the related-party pathologies of 1873 and 1996-2002 (Credit Mobilier; "
  "Lucent, Nortel, Winstar) onto today's circular deal graph; and reads the July 2026 rotation - "
  "the forced unwind of Situational Awareness LP and Microsoft's $480 billion single-session "
  "repricing - as the first live experiment on where AI's rents will land. Reported figures and "
  "the authors' estimates are distinguished throughout; sources and model assumptions appear at "
  "the end.", abst)
SP(4)

# ----------------------------- SECTION 1 -------------------------------------
H("1. The Question and a Correction")
P("The prompt for this analysis was a Goldman Sachs Insights piece (July 2026) asking whether US "
  "equity valuations have outrun fundamentals [1]. Its load-bearing figures: AI-related companies "
  "have added roughly $27 trillion of market value since November 2022 (up from about $19 trillion "
  "seven months earlier), while the bank's baseline estimate of the present discounted value of "
  "AI-related capital revenues to US companies is roughly $9 trillion. US technology investment as "
  "a share of GDP has surpassed its late-1990s peak, and the 2026 spending plans of the largest "
  "cloud and computing companies came in about fifty percent higher than estimates made only six "
  "months prior. Goldman's stated risk is that the market overestimates the persistence of the "
  "earnings streams - particularly for the companies supplying the capex boom - beyond a two-to-"
  "three-year horizon, and it concedes the reflexive point that the investment boom itself currently "
  "generates a substantial portion of the profits justifying the prices.")
P("One correction frames everything downstream: the $27 trillion is not investment. It is market-"
  "capitalization appreciation - capitalized expectation. Actual capital expenditure is an order of "
  "magnitude smaller. The four largest hyperscalers spent about $226 billion in 2024 and about $410 "
  "billion in 2025, and after Q1 2026 earnings guided to roughly $725 billion combined for 2026, "
  "with Microsoft alone at $190 billion [13, 15]. Goldman projects $5.3 trillion of big-four capex "
  "over 2025-2030 [1]. Cumulative AI-attributable investment since ChatGPT, built up carefully in "
  "Section 3, is roughly $1.0-1.2 trillion gross. Realized investment is therefore about six percent "
  "of the market-value move; the other ninety-four percent is expectation. That ratio is the "
  "article's tension stated as arithmetic, and the remainder of this report is an attempt to give "
  "each side of the ratio its correct accounting.")

# ----------------------------- SECTION 2 -------------------------------------
H("2. The Capex Boom and Its Persistence")
P("The mechanical core of the persistence concern is that supplier revenue is a derivative of the "
  "capex flow, not of the installed stock. If spending merely plateaus, supplier growth goes to "
  "zero; if it reverts toward replacement level, supplier revenue contracts outright. The historical "
  "base rate is unkind - US telecom capex roughly halved between 2000 and 2003 - but the "
  "depreciation structure here genuinely differs from fiber. Dark fiber carried near-zero "
  "replacement demand; accelerators on four-to-six-year lives at a ~$500 billion annual run rate "
  "imply a replacement floor above $100 billion per year and rising with the installed base. Short "
  "asset lives are bearish for the buyers' balance sheets and bullish for recurring supplier "
  "revenue: the same fact, booked on opposite sides.")
P("The stronger evidence for the limited-time view is the financing signature. Capital intensity "
  "now runs 45-57 percent of revenue for the big four and 86 percent for Oracle; Amazon's free cash "
  "flow is projected to turn negative; roughly $108 billion of debt was raised by hyperscalers in "
  "2025 with on the order of $1.5 trillion projected over the coming years [15]. Moody's now "
  "projects $785 billion of capital expenditure by the six largest US hyperscalers in 2026, approaching $1 trillion in "
  "2027, part-funded by roughly $175 billion of debt issuance this year [28, 35]. Migration from "
  "cash-funded to debt-and-lease-funded spending is the canonical late-phase marker: it extends the "
  "boom past internal cash generation and makes the flow fragile to sentiment.")
H2("2.1 Production capacity: reallocation, not new build")
P("A second-order question with first-order consequences: how much of the apparent explosion in "
  "compute production is new physical capacity versus existing capacity redirected and repriced? "
  "So far, mostly the latter. Leading-edge logic barely grew in aggregate: high-performance "
  "computing reached 61 percent of TSMC revenue by Q1 2026, up from roughly a third before the "
  "boom - the same fabs, shifted from phones to accelerators as mobile demand softened [14]. Memory "
  "is the purest relabeling: HBM consumed 23 percent of global DRAM wafer starts in 2026 versus 8 "
  "percent in 2024, at roughly a three-to-one wafer-intensity penalty against DDR5; Micron exited "
  "consumer memory entirely, and DDR5 contract pricing more than doubled [16]. The one place "
  "physical capacity genuinely multiplied is advanced packaging, because it was the binding "
  "constraint and is cheap relative to fabs: TSMC CoWoS went from about 35,000 wafers per month at "
  "end-2024 to about 75,000 at end-2025, targeting 125,000-130,000 by end-2026 - a near-4x "
  "expansion that still trails demand by an estimated 10-20 percent [16]. Meanwhile TSMC's entire "
  "2026 capital budget is $52-56 billion and total semiconductor-industry capex runs about $200 "
  "billion per year - against more than $725 billion of downstream datacenter spending. The "
  "production base for compute is expanding far more slowly than spending on its output.")
P("That asymmetry concentrates pricing power upstream - TSMC at a 66.2 percent gross margin, "
  "memory prices doubling - and Microsoft attributed $25 billion of its 2026 capex increase purely "
  "to rising memory and component costs [13, 14]. A nontrivial slice of measured capex growth is "
  "therefore intra-supply-chain price inflation: scarcity rents, which are definitionally transient "
  "because they persist only while supply lags. The market capitalizing scarcity rents as durable "
  "franchise earnings is the mechanically precise form of Goldman's earnings-bubble worry. The "
  "watch variables are the CoWoS supply gap narrowing toward ~10 percent through 2026 and the new "
  "memory fabs landing in 2027-28 - fresh supply arriving just as capex growth must decelerate is "
  "the classic semiconductor bullwhip setup. The falsifier runs through end demand: cloud AI "
  "revenue compounding at rates like Google Cloud's reported 63 percent year-over-year is the kind "
  "of number that, sustained, absorbs the supply as it lands [13].")

# ----------------------------- SECTION 3 -------------------------------------
H("3. An Asset-Side Estimate: The AI Capital Stock")
P("The direct route around speculative pricing is to build the asset side: a replacement-cost "
  "capital stock, compared against market value - Tobin's Q at sector level. Q above one is not "
  "per se irrational, since market value legitimately capitalizes rents on future investment as "
  "well as installed assets; the exercise does not eliminate the speculative component but "
  "quarantines it into a single residual that can be sized and argued about. Aggregate versions "
  "exist - Econbrowser ran whole-market q against the intellectual-property capital stock in "
  "December 2025 [17] - and Goldman's $9 trillion is the profit-side dual, but an AI-sector "
  "decomposition does not appear to have been published. We construct it here.")
H2("3.1 Vintage build-up")
P("Global AI-attributable gross capex by vintage, estimated from hyperscaler disclosures (applying "
  "an AI share rising from roughly 30 percent in 2023 to 75 percent in 2026, per CreditSights [15]) "
  "plus Oracle, the neoclouds, xAI and OpenAI's direct spending, Chinese platforms, and sovereign "
  "programs:")
SP(3)
tbl([["Vintage", "Low ($B)", "Central ($B)", "High ($B)", "Age at mid-2026 (yr)"],
     ["2023", "45", "65", "85", "3.0"],
     ["2024", "150", "185", "215", "2.0"],
     ["2025", "400", "460", "500", "1.0"],
     ["H1 2026", "310", "370", "420", "0.25"],
     ["Cumulative gross", "905", "1,080", "1,220", "-"]],
    [1.35*inch, 1.05*inch, 1.15*inch, 1.05*inch, 1.55*inch])
P("Table 1. Vintage gross AI-attributable capex (authors' estimates from reported figures).", cap)
P("A supply-side cross-check anchors the range. Nvidia's datacenter revenue was $115.2 billion in "
  "FY2025, $193.7 billion in FY2026, and $75.2 billion in Q1 FY2027 alone - cumulative roughly "
  "$430 billion from early 2023 through April 2026, approaching $500 billion through July [12]. At "
  "Nvidia around 60 percent of AI IT-equipment value (custom accelerators such as TPU and Trainium "
  "at cost, AMD, non-Nvidia networking making up the rest), implied IT spending of $750-830 "
  "billion pushes the true gross figure toward the upper half of the modeled range.")
H2("3.2 Depreciation, add-ons, and the competitive-cost adjustment")
P("Depreciating by asset class - 62 percent IT equipment on five-year straight line, 23 percent "
  "power and cooling infrastructure on fifteen, 15 percent shell and land on thirty, mid-year "
  "convention - removes roughly $160 billion. To the net datacenter stock we add the AI-allocated "
  "share of upstream fab plant (TSMC and the memory makers, ~$125B), AI-attributable grid and "
  "power investment (~$65B), and model intellectual property at cost, excluding compute already "
  "counted (~$55B). One further adjustment matters: book value embeds the scarcity rents, because "
  "the accelerator stock was purchased at ~75 percent gross margins and memory at doubled prices. "
  "Repricing the IT stock at competitive supply-chain margins cuts it roughly in half, giving the "
  "long-run equilibrium anchor that entry drives toward - and implying the asset base itself "
  "deflates by roughly $250 billion if supplier pricing normalizes.")
P("The five-year IT life deserves defense, because the industry's own schedules mostly say six. "
  "Between fiscal 2021 and 2025 the major operators repeatedly extended server useful lives, "
  "adding non-cash operating income of roughly $3.7 billion (Microsoft, FY2023, to six years), "
  "$3.9 billion (Alphabet, 2023), $3.2 billion (Amazon, 2024), $2.9 billion (Meta, 2025), and "
  "$0.7 billion (Oracle, FY2025) - more than $14 billion per year of reported operating income, "
  "roughly $11.7 billion after tax, manufactured across the complex by an assumption about how "
  "long a chip stays useful, per the companies' own change-in-estimate disclosures [33]. The "
  "reversal is the honest signal: "
  "effective January 2025, Amazon shortened a subset of server and networking lives from six years "
  "back to five, citing in its 10-K the increased pace of AI and machine-learning hardware "
  "development, at a cost of $1.4 billion of additional depreciation in 2025 [26, 33]. The operator with "
  "the longest experience running datacenters at scale agrees with this model's assumption against "
  "its peers' schedules.")
SP(3)
tbl([["Case", "Gross capex", "Net DC stock", "Total net stock*", "Competitive-cost stock"],
     ["Low", "905", "773", "958", "746"],
     ["Central", "1,080", "919", "1,164", "911"],
     ["High", "1,220", "1,034", "1,339", "1,056"]],
    [1.0*inch, 1.2*inch, 1.2*inch, 1.35*inch, 1.6*inch])
P("Table 2. AI capital stock at mid-2026, $B. *Includes upstream fabs, power/grid, and model IP "
  "at cost. Authors' model; assumptions in Appendix A.", cap)
H2("3.3 The rent decomposition")
P("Against the $27 trillion market-value gain - or roughly $18 trillion taking Goldman's own "
  "caveat that perhaps a third reflects non-AI businesses - sector Q runs 15-23x. The rent "
  "capitalization (market value minus assets) is about $17 trillion on the conservative "
  "attribution. Backed out as a required flow at an 8 percent discount rate:")
SP(3)
tbl([["AI-attributable MV", "Rent capitalization", "Growing 3%/yr", "Flat perpetuity", "Decaying 10%/yr"],
     ["$14T", "$12.8T", "$0.64T/yr", "$1.03T/yr", "$2.31T/yr"],
     ["$18T", "$16.8T", "$0.84T/yr", "$1.35T/yr", "$3.03T/yr"],
     ["$27T", "$25.8T", "$1.29T/yr", "$2.07T/yr", "$4.65T/yr"]],
    [1.45*inch, 1.45*inch, 1.15*inch, 1.15*inch, 1.2*inch])
P("Table 3. Required economic-rent flow implied by rent capitalization at r = 8%, central asset "
  "stock of $1.18T. Authors' model.", cap)
P("Current realized AI economic rents run roughly $330-350 billion per year: Nvidia annualizing "
  "about $200 billion of operating income, TSMC's AI-attributable share around $40 billion, memory "
  "scarcity profits around $60 billion, thin hyperscaler direct-AI margin, and an application layer "
  "that does not earn what its software analogues did [12, 14, 37]. The market therefore requires the rent stream to grow roughly 2.5-4x and "
  "persist indefinitely - while 85-90 percent of today's rents sit in the supply chain, in exactly "
  "the scarcity-rent form that mean-reverts. The reconciliation with Goldman is clean: $1.2 "
  "trillion of assets plus their $9 trillion rent PDV accounts for about $10 trillion against $18 "
  "trillion of AI-attributable market gain, leaving roughly $8 trillion as the speculative residual "
  "under their own baseline. A fully auditable variant exists for anyone who wants it: summing net "
  "property, plant and equipment plus finance-lease assets from the 10-Ks of the AI complex and "
  "taking the delta since Q4 2022 yields roughly $450-500 billion for the big four through 2025, "
  "corroborating the vintage build once non-AI growth is stripped and the rest of the ecosystem "
  "added.")
P("The model layer needs a note, because the margin figures that circulate for it are not "
  "comparable to each other. DeepSeek's self-published 545 percent and the roughly 70 percent "
  "&#8220;compute margin&#8221; reported for OpenAI are ratios of price to marginal serving cost, "
  "and on that measure serving tokens is genuinely cheap: DeepSeek's own disclosure put a day of "
  "V3/R1 inference at $87,072 of GPU rental against $562,027 of theoretically billable output, "
  "while noting that its web and app tiers are free, that off-peak pricing is discounted, and that "
  "realized revenue was far lower [37]. Blended gross margin is a different quantity and a much "
  "smaller one. OpenAI's adjusted gross margin ran about 33 percent in 2025, down from 40 percent "
  "and below its own 46 percent plan; Anthropic's 2025 guidance was cut by roughly ten points to "
  "about 40 percent when inference rented from Google and Amazon overran plan by about a quarter "
  "[37]. Free tiers, flat-rate pricing over metered compute, training amortization, and rented "
  "capacity all sit between the marginal cost and the income statement - and flat rates invert the "
  "software margin logic, because the heaviest users are the least profitable, which is why the "
  "$200-per-month tier lost money by its own seller's account. At the application layer the same "
  "wedge shows up as a gross-margin gap of twenty-five to thirty-five points against traditional "
  "software - 33 percent in 2024 rising to a projected 45 percent in 2026, against 75-85 percent "
  "for SaaS - with flagship AI-native firms running negative gross margin at billion-dollar "
  "revenue scale, and turning positive by integrating backward into their own models [37]. That "
  "last move is the tell: the margin is recoverable by whoever owns the inference, which is the "
  "rent-location question of Section 4.1 posed one layer down.")
H2("3.4 Water: a nineteenth-century precedent for the method")
P("The method has a precedent, run by contemporaries on the railroads. Total railroad "
  "capitalization grew from $4.6 billion in 1876 to $10.6 billion by 1890, and one railroad "
  "historian estimated that forty percent of the latter figure was &#8220;water&#8221; - securities "
  "issued in excess of any investment in roadbed, rails, or rolling stock, floated against branch "
  "lines not yet built and towns that existed only on promotional maps [29]. Water is precisely a "
  "replacement-cost gap: market value minus tangible assets, named and measured a century before "
  "Tobin. The railroad sector's implied Q at peak watering was roughly 1.7x. The AI complex's is "
  "15-23x. The honest reading of that spread is a fork: either genuine intangibles - the models, "
  "the know-how, the network positions - are worth an order of magnitude more relative to the "
  "physical plant than anything in 1890, or the watering is proportionally larger. Naming which of "
  "those one believes is the entire argument.")

# ----------------------------- SECTION 4 -------------------------------------
H("4. The Revenue Requirement: What Share of GDP Must Flow to AI")
P("Inverting the rent requirement into a revenue requirement demands one construction choice: AI "
  "revenue must be measured as external revenue - sales from the consolidated AI stack to the rest "
  "of the economy. Summing layer revenues double-counts (Nvidia's revenue is Microsoft's cost is "
  "OpenAI's cost), and today most of the stack's profit is funded by intra-stack capex - by capital "
  "markets rather than final demand. The transition being priced is precisely that external revenue "
  "replaces the capex flow as the funding source of the rents.")
P("Required after-tax profit by roughly 2030 is the rent stream plus normal returns on what will by "
  "then be a ~$5 trillion capital stock: about $1.25 trillion per year in the growing-rents case, "
  "$1.75 trillion flat, $3.4 trillion if rents decay. Dividing by consolidated net margin on "
  "external revenue:")
SP(3)
tbl([["Case (required profit)", "30% margin", "20% margin", "12% margin"],
     ["Growing rents ($1.25T/yr)", "$4.1T = 3.1% W / 12% US", "$6.2T = 4.6% W / 18% US", "$10.4T = 7.7% W / 30% US"],
     ["Flat perpetuity ($1.75T/yr)", "$5.8T = 4.3% W / 17% US", "$8.8T = 6.5% W / 25% US", "$14.6T = 10.8% W / 42% US"],
     ["Decaying rents ($3.4T/yr)", "$11.4T = 8.5% W", "$17.2T = 12.7% W", "$28.6T = 21.2% W"]],
    [1.9*inch, 1.55*inch, 1.55*inch, 1.6*inch], fontsize=8.2)
P("Table 4. Required external AI revenue and share of 2030 world (~$135T) and US (~$35T) GDP. "
  "Authors' model; Appendix B.", cap)
P("Three readings. First, the decay row is the valuation restated as a theorem: the pricing "
  "requires durable moats, because without them no plausible GDP share closes the gap. Second, the "
  "US-only column is arithmetic nonsense at 12-42 percent of GDP, so the valuations mathematically "
  "presuppose global revenue capture - which sits awkwardly against export controls and Chinese "
  "self-supply. Third, the bracket: the floor - merely making the buildout NPV-neutral, covering "
  "depreciation (~$940B/yr on the 2030 stock, dominated by five-year IT lives), operations, and "
  "cost of capital with zero rents - is about $1.7 trillion per year, 1.3 percent of world GDP. "
  "Current external AI revenue (cloud AI services, the application layer, enterprise on-premise; "
  "authors' estimate) runs perhaps $300-400 billion, about 0.3 percent of world GDP. The sector "
  "needs roughly 4-5x revenue growth to stop destroying value and 12-18x to justify the market "
  "pricing. External triangulations land on the same gap: Bain estimates roughly $2 trillion of "
  "annual AI revenue required by 2030 and finds the world about $800 billion short even if "
  "every on-premise IT dollar migrates to cloud and every productivity saving is reinvested [36], while "
  "Sequoia's David Cahn has walked his running estimate of the revenue question from $200 billion "
  "to $600 billion to roughly $840 billion [28].")
P("For scale: 3-6.5 percent of world GDP means external AI spending matching or exceeding all "
  "current global IT spending and two to three times all software plus cloud combined, and $1.25-"
  "1.75 trillion of after-tax profit stands against a total US corporate-profit pool of roughly "
  "$3.9 trillion. Which raises the question the GDP framing usually obscures: which spending pool "
  "funds this? IT budgets cannot - they total about five percent of world GDP and AI will not take "
  "all of them. Consumer discretionary does not produce trillions at software margins. The only "
  "pool of sufficient size is labor compensation, roughly 53 percent of GDP, about $70 trillion by "
  "2030. If AI vendors capture around 30 percent of the labor-cost savings they create, then $4-7 "
  "trillion of revenue implies AI substantively addressing 19-33 percent of global labor income. "
  "The percentage-of-GDP assumption thus decomposes into four separately contestable conjuncts: "
  "partial automation of a fifth to a third of world labor; the AI complex capturing about 30 "
  "percent of that surplus rather than competing it away to users; doing so at 25-30 percent "
  "consolidated margins; and moats durable enough that the rents do not decay. The margin "
  "assumption and the moat assumption are the same assumption in different clothes. Telecom built "
  "the internet at ten percent margins and never earned its cost of capital; software is the other "
  "precedent. The market has priced the software outcome.")
H2("4.1 The rent-location corollary")
P("Everything above concerns the level of the required rent stream and says nothing about its "
  "distribution - and history's answer to the distribution question inverts the market's. In each "
  "precedent of Section 6, the capital that built the network earned poor returns while asset-"
  "light businesses riding the network - owning the customer relationship, the standard, or the "
  "validated record, at near-zero incremental capital cost - kept the profit: the express "
  "companies and Pullman on the railroads; Google, Amazon, and Netflix on fiber that bankruptcy "
  "had made nearly free. The market's current allocation is the opposite: the rent capitalization "
  "sits overwhelmingly in the builders and suppliers, while incumbent application software entered "
  "mid-2026 trading at 11-14x trailing earnings - priced as a dying industry while converting a "
  "third to nearly half of revenue into free cash [28]. These two allocations cannot both be "
  "right. &#8220;Right in total, wrong in location&#8221; is therefore a coherent resolution of "
  "the $17 trillion residual: builder capitalization compressing toward replacement cost while "
  "rider capitalization expands. Relocation redistributes the requirement without relaxing it - "
  "whoever earns the rents, the external revenue must still arrive at 3-6.5 percent of world GDP "
  "for the aggregate pricing to hold. Section 10 examines the first violent market experiment on "
  "exactly this question.")

# ----------------------------- SECTION 5 -------------------------------------
H("5. Historical Calibration: IT Spending and GDP")
P("Gartner's April 2026 revision puts worldwide IT spending at $6.31 trillion for 2026, up 13.5 "
  "percent - about 5.3 percent of world GDP (~$120T). Hardware is $788 billion of datacenter "
  "systems plus $856 billion of devices, about $1.64 trillion or 1.4 percent of world GDP; "
  "software runs $1.44 trillion, IT services $1.87 trillion, communications services $1.36 "
  "trillion [2].")
SP(3)
tbl([["Segment", "2025 ($B)", "2025 growth", "2026 ($B)", "2026 growth"],
     ["Data center systems", "489", "+46.8%", "788", "+55.8%"],
     ["Devices", "783", "+8.4%", "856", "+8.2%"],
     ["Software", "1,244", "+11.9%", "1,440", "+15.1%"],
     ["IT services", "1,719", "+6.5%", "1,870", "+8.7%"],
     ["Communications services", "1,304", "+3.8%", "1,360", "+4.8%"],
     ["Total", "5,540", "+10.0%", "6,310", "+13.5%"]],
    [1.9*inch, 1.0*inch, 1.05*inch, 1.0*inch, 1.05*inch])
P("Table 5. Worldwide IT spending by segment. 2025 figures and 2025 growth from Gartner's October "
  "2025 release [3]; 2026 from the April 2026 revision [2] (2026 devices growth as reported "
  "against revised 2025 base).", cap)
P("The historical shape is more interesting than a simple rise, and it disciplines the Section 4 "
  "requirement. The global ratio has essentially round-tripped: roughly 5.3 percent of world GDP "
  "around 2008, drifting down to about 4.3 percent by 2019-20 as communications stagnated in "
  "absolute terms while GDP grew, then inflecting back - 4.8 percent in 2025, 5.3 percent in 2026 "
  "(historical shares are authors' estimates from Gartner series and IMF GDP data). The headline "
  "share sat in a 4.3-5.3 percent band for two decades, and 2026 is the first decisive break above "
  "the band's ceiling. Composition rotated completely underneath: telecom fell from nearly half "
  "the total to about a fifth; software went from roughly $300 billion in 2010 to $1.44 trillion; "
  "and datacenter systems - the line that matters for this report - sat at $150-200 billion for "
  "essentially the entire 2010s, four to five percent of IT spending, before going roughly $243B "
  "(2023) to $333B (2024) to $489B (2025) to $788B (2026): a tripling in three years, now 12.5 "
  "percent of all IT.")
P("The mechanism behind two decades of flatness is worth naming: compute consumption grew "
  "exponentially throughout, but hardware price deflation - Moore's law plus competitive supply - "
  "absorbed it, holding the nominal line flat. The current breakout is partly the suspension of "
  "that deflation: accelerators priced at 75 percent gross margins and HBM at doubled prices mean "
  "the datacenter line now grows with volume and price together, and Gartner's own commentary "
  "attributes its upward revisions substantially to memory pricing [2]. Some fraction of the IT "
  "share of GDP finally rising is the scarcity-rent regime showing up in category data. As a base "
  "rate for Section 4, this is sobering: the share needed forty years to reach five percent and "
  "then did not grow for twenty, and the valuation math needs a second IT-sector-sized wedge - "
  "3-6.5 percent of world GDP - inside a decade. The one measurement caveat cutting the other way: "
  "Gartner's perimeter excludes the ad-funded consumer internet (Google's and Meta's roughly $700 "
  "billion of revenue is not counted as IT spending), and the BEA's broader digital-economy "
  "account puts the fuller US tech share near ten percent of GDP, up a couple of points over two "
  "decades. The economy can grow a multi-point tech wedge; it did so once, over about twenty-five "
  "years, funded largely by advertising's fixed share of GDP. The open question is whether labor "
  "substitution funds the second one faster.")

# ----------------------------- SECTION 6 -------------------------------------
H("6. The Buildout Precedents: Railways, Railroads, Telecom")
P("Three completed buildouts frame the AI cycle: Britain's Railway Mania of the 1840s, the "
  "American railroad expansion from the Civil War through the 1890s, and the telecom buildout of "
  "1996-2002. Each was, in its day, the largest private-capital infrastructure program in history; "
  "each transformed its economy; each treated its investors badly in a characteristic way. Table 6 "
  "compares them; the records follow.")
H2("6.1 Three records")
P("<b>Britain, 1844-1852.</b> Railway investment peaked near five to seven percent of GDP in 1847 "
  "- a share no private program has matched since [30]. The mania's texture matters more than its "
  "size. Dividends rose from 4.4 percent in 1843 to 7 percent in 1847 while consols paid 3, and "
  "share prices rose 106 percent into 1845 - then both collapsed together, dividends to 2.4 "
  "percent by 1852 and prices below their starting value [30]. Campbell's reconstruction yields "
  "the finding this report leans on in Section 11: railway shares were not obviously mispriced "
  "even at the peak, because prices tracked dividends up and down; the catastrophe was aggregate, "
  "not per-security. The expansion, moreover, was carried out mostly by established, hitherto-"
  "profitable railways through rights issues - respectable incumbents, not fly-by-night promotions "
  "- and the new lines were simply, collectively, unremunerative [30]. Britain received a national "
  "network it would never have voted to fund through taxation, and railway shareholders spent "
  "decades earning less than the government's own perpetuities paid.")
P("<b>The United States, 1865-1900.</b> Between 1865 and 1875 the country roughly doubled its "
  "rail network - 35,085 miles to 74,096, with construction peaking at 7,439 miles laid in 1872 "
  "[34] - and railroad capital reached roughly $4.5 billion when the entire banking system's "
  "capital was $720 million and the federal debt $2.3 billion [28, 29]. In January 1870, 87 percent of shares "
  "traded on the New York Stock Exchange were railroad shares, and from 1870-74 roughly seventy "
  "percent of all railroad securities issued in London were American - foreign capital drawn by "
  "6.5 percent gold bonds against far lower consol yields [28]. The financier's failure was the "
  "underwriter's: Jay Cooke contracted to place $100 million of Northern Pacific bonds, sold less "
  "than $20 million, and ended up owning three-quarters of the railroad he was financing when his "
  "house failed on September 18, 1873, closing the NYSE for ten days - the first closure in its "
  "history [28, 29]. By 1876, 134 railroads were in default on $500 million of roughly $2 billion "
  "outstanding; by January 1877 more than 18 percent of national mileage was in receivership; and "
  "the 1893 panic repeated the cycle at larger scale, with a fifth of mileage - Union Pacific, "
  "Northern Pacific, Santa Fe, and Reading among them - in receivers' hands at the March 1894 peak, "
  "a quarter of aggregate capitalization passing through receivership across 1893-97 [29, 34]. The boom-decade peak came later: "
  "construction quadrupled from 2,665 miles in 1878 to 11,569 in 1882 [34], railroads absorbed an "
  "estimated fifteen percent of all American capital formation across the 1880s - roughly six "
  "percent of GDP at peak - and 1890s capitalization carried the forty-percent water of Section "
  "3.4 [29]. And where roads survived, competition took the returns: revenue per ton-mile fell "
  "from roughly 2.2 cents in 1870 (Fishlow's estimate - no all-road series reaches back that "
  "far) to 0.73 cents in 1900, both nominal [29, 34], and rate wars drove the New York-Chicago "
  "through rate from $1.88 toward twenty cents [28]. Every additional mile made the network more "
  "valuable to the country and less valuable to the men who had paid for it.")
P("<b>Telecom, 1996-2002.</b> Between the Telecommunications Act and 2002 the sector raised on "
  "the order of $1.5-2 trillion in equity and debt and roughly tripled annual capex, peaking "
  "around $110-120 billion per year in the US in 2000 before collapsing by half within three "
  "years. The demand forecast underneath - internet traffic doubling every hundred days - was off "
  "by roughly an order of magnitude (actual doubling was close to annual; Odlyzko spent years "
  "dismantling the meme [18]), while DWDM multiplied capacity per fiber strand roughly a "
  "hundredfold mid-buildout. By 2002 an estimated 3-5 percent of installed long-haul fiber was "
  "lit and bandwidth prices on major routes had fallen more than ninety percent. WorldCom - $107 "
  "billion of stated assets, $11 billion of fraudulent accounting - became the largest bankruptcy "
  "in US history to that date; Global Crossing put roughly $10 billion of audited capex into its "
  "network and sold control out of bankruptcy for $250 million, a reorganization value near one "
  "cent on the dollar of peak book assets; Level 3 "
  "survived a 99 percent drawdown. European carriers paid about EUR 110 billion for 3G spectrum "
  "in 2000, mostly written off - a direct shareholder-to-treasury transfer. FCC Chairman Michael "
  "Powell told the Senate in July 2002 that roughly $2 trillion of market value and nearly $1 "
  "trillion of debt had been lost; The Economist's leader the same month put sector debt at about "
  "$1 trillion, up to half of which might never be repaid [21], and "
  "sector-level studies through the 2000s and 2010s consistently put telecom returns on invested "
  "capital at 5-8 percent against 7-9 percent costs of capital. Persistently, on both sides of "
  "the Atlantic, the industry operating the internet's transport layer earned less than its "
  "capital cost.")
SP(3)
ptbl([
 ["", "UK Railway Mania (1840s)", "US Railroads (1865-1900)", "Telecom (1996-2002)", "AI (2023- )"],
 ["Peak investment",
  "~5-7% of GDP (1847)",
  "~6% of GDP (1880s peak); ~15% of capital formation across the decade",
  "~1.0% of US GDP (2000); more than $500B in five years",
  "~1.2% of US GDP (2025); ~$725B big-four guidance for 2026"],
 ["Financing",
  "Partly-paid equity and calls; incumbents' rights issues",
  "Bonds, ~70% sold abroad (London, 1870-74); federal land grants; promoter construction companies (Credit Mobilier)",
  "Public equity and high-yield debt; vendor receivables financing (Lucent, Nortel); state 3G fees",
  "Operating cash flow, then debt ($108B in 2025, ~$175B 2026E), SPVs (Hyperion $27.3B), equity-linked vendor deals"],
 ["Dominant asset life",
  "30-50 yr way and works",
  "30-50 yr roadbed; shorter rolling stock",
  "~25 yr fiber; shorter electronics",
  "~5 yr IT equipment (62% of stock); 15-30 yr shells and power (38%)"],
 ["Private return",
  "Dividends 7% (1847) to 2.4% (1852); long-run below consols",
  "20% of mileage in receivership by 1877, ~25% again by 1894; ton-mile revenue -61%, 1870-1900",
  "ROIC 5-8% vs 7-9% WACC; ~$2T equity and ~$1T debt erased; capex halved 2000-03",
  "Open; realized rents ~$330-350B/yr, mostly supply-chain scarcity; sector Q 15-23x"],
 ["Toll-booth winners",
  "W.H. Smith bookstalls; Thomas Cook excursions",
  "Adams Express, American Express, Pullman - asset-light riders on others' track",
  "Google, Amazon, Netflix; content platforms funding ~4 of 5 new transatlantic-cable dollars by 2018-19",
  "Contested - incumbent software vs model layer vs users; July 2026 the first live test (Section 10)"],
 ["Loss absorption",
  "Shareholders via calls; diffuse",
  "Foreign bondholders (~$600M, 1873-79); domestic equity; receivership courts",
  "Diffuse equity (pensions, retail); mild 2001 recession",
  "Index public via cap weight; credit if the debt migration continues; ratepayers at the margin"],
], [0.95*inch, 1.35*inch, 1.5*inch, 1.4*inch, 1.4*inch])
P("Table 6. Four network buildouts compared. Sources: [18]-[21], [28]-[31]; AI column, this "
  "report. Express-company and per-name figures relayed via [28]; see Data Provenance.", cap)
H2("6.2 The productive-bubble thesis")
P("From a global rather than shareholder perspective, all three records admit a stronger reading: "
  "the networks were built with investor money that never saw a return - covertly socialized "
  "infrastructure programs, neither consensual nor centrally planned, but effective. Nordhaus's "
  "estimate is the clean theorem behind it: even in successful innovation, producers capture on "
  "the order of 2.2 percent of the social surplus they create [19]. A productive bubble is the "
  "degenerate case where private capture goes negative - investors pre-fund infrastructure whose "
  "surplus they cannot appropriate, and the crash is the moment that fact is marked to market. "
  "This is Perez's installation/deployment structure and Janeway's productive bubble [20]: the "
  "crash transfers assets to new owners at written-down cost basis, and that basis is what makes "
  "deployment-era services cheap. Google bought dark fiber from bankrupt carriers for pennies "
  "mid-decade; YouTube launched in 2005 into a bandwidth regime ninety percent cheaper than any "
  "rationally priced buildout would have produced. Because the losses were equity-financed and "
  "diffuse - pensions and retail absorbed them - the 2001 recession was mild; bank-funded "
  "buildout busts (1873, 2008) propagate instead of dissipating.")
P("Two complications keep the frame honest. First, within the investor class it was a transfer, "
  "not a shared sacrifice: insiders at Qwest and Global Crossing sold billions near the top, "
  "conflicted research and the IPO machinery pulled late retail money in, $11 billion of "
  "WorldCom's numbers were fabricated - and the Mania had George Hudson paying dividends out of "
  "capital. Consensual socialization it was not. Second, Odlyzko's sharper point: the bubble "
  "funded the fundable layer, not the binding one. Long-haul transport was a small fraction of "
  "total network cost with easy entry, so speculative capital pooled there; the actual bottleneck "
  "- the last mile - was built later, slowly, by incumbents on regulated economics. Bubbles "
  "allocate by legibility and venture-shape, not by bottleneck. The AI equivalent of the last "
  "mile is plausibly power interconnection and enterprise integration, which is roughly where "
  "capital moves slowest today.")
H2("6.3 Asymmetries and the deflation clock")
P("One asymmetry deserves heavy weight in any mapping to AI: the gift mechanism requires the "
  "capital stock to outlive the crash. Fiber in conduit had twenty-five-year life and near-zero "
  "carrying cost - it could sit dark waiting for YouTube; rail roadbed lasted half a century. The "
  "AI stock modeled in Section 3 is 62 percent IT equipment on roughly five-year lives: of the "
  "four episodes, this is the weakest bequest case. An AI overbuild does not bequeath, it "
  "evaporates, leaving the shells and power infrastructure (roughly 38 percent of the stock), the "
  "trained workforce, and whatever persists in open weights. The ton-mile series doubles as the "
  "cycle's clock: railroad ton-mile revenue deflated by roughly two-thirds in nominal terms "
  "over thirty years, while AI "
  "inference prices routinely fall as much in a single year. The commodity-deflation phase that "
  "consumed a generation compresses here into quarters - the network's output becomes cheap "
  "before its owners have depreciated the plant, which is the five-year life restated from the "
  "price side. And the financing drift cuts the other way: dot-com losses were equity-diffused, "
  "while this cycle's debt migration, private credit, and special-purpose vehicles move it toward "
  "the banked-bubble category, where socialization stops being benign and becomes literal - "
  "bailouts and ratepayers, the latter channel already active in utility bills.")

# ----------------------------- SECTION 7 -------------------------------------
H("7. The Second Harvest: What the Losses Actually Bought")
P("Take the socialized-buildout claim at full strength and the retrospective justification of the "
  "telecom writeoff was never merely cheap video. The overbuilt network did two things no planner "
  "ordered. It induced humanity to transcribe itself - the web, the forums, the code repositories, "
  "trillions of tokens produced as exhaust by people using bandwidth priced below its buildout "
  "cost - and it grew the ad-funded engine that later paid for the laboratories. The corpus and "
  "the cash flows were both second harvests of the glut. On the longest accounting, the 2000-02 "
  "losses were the capital contribution to machine intelligence: privately negative, socially "
  "incalculable, with the payoff arriving twenty years late in a form nobody was pricing. That is "
  "not a metaphor stretched over the facts; it is the causal chain.")
P("Open weights are then the piece that makes this cycle's version of the bequest structurally "
  "stronger than fiber. Fiber persisted because glass in conduit does not rot. Weights persist "
  "because of irreversibility plus zero-cost reproduction - and they add a property no prior "
  "infrastructure had: the artifact teaches its own manufacture. Every served token is a lesson; "
  "distillation means the product can be interrogated into yielding its replacement. Nordhaus "
  "found producers capture about two percent of innovation surplus on average; for this good that "
  "starts to look like a ceiling, because appropriability leaks through the product's own "
  "function. The physical form is maximally unpossessable - the crown jewels of a multi-trillion-"
  "dollar complex are a few hundred gigabytes, which fit in a backpack and therefore in no vault. "
  "Export controls govern chips because nobody can durably govern files. Two refinements keep the "
  "analogy honest. The dark fiber of this cycle is not the weights already published - those are "
  "lit and carrying traffic - but the elicitation overhang: capability resident in released "
  "artifacts that current scaffolding has not yet extracted. And the crash scenario is synergistic "
  "for the commons rather than destructive: a bust means fire-sale accelerators the way 2002 meant "
  "two-cent bandwidth, and written-down compute plus free weights is exactly the deployment-era "
  "cheapness the next platform gets built on. The rent capitalization of Section 3 is crash-"
  "exposed; the endowment is crash-hedged.")
P("The friction is real and should be stated against the grain of the optimism: the gift is "
  "parasitic on the race. Open releases are strategic byproducts - complement commoditization, "
  "positioning, recruiting - funded by the very rent expectations sized above. The floor rises "
  "only while the frontier is contested; the day the funding stops, the last release freezes as "
  "the permanent public endowment, trailing closed capability by an unknowable gap. And diffusion "
  "through this commons selects on capability per dollar, not on wisdom - a discrimination "
  "problem with no filter at all, because the unpossessable is also the unrecallable. There is an "
  "old resonance here that requires no forcing: the provision that spoiled when hoarded, save the "
  "portion set aside; closed frontier value decays on roughly that schedule - months to "
  "obsolescence - while the released portion keeps. Property was the wrong category from the "
  "start; the balance sheets are merely the last to find out.")

# ----------------------------- SECTION 8 -------------------------------------
H("8. The Circular Economy: The Ouroboros Formalized")
P("A recent Atlantic essay describes the AI economy as a trillion-dollar ouroboros of buying and "
  "selling, investment and equity staking, largely among a handful of firms - Big Tech advancing "
  "money to AI startups to buy cloud services from Big Tech [10]. Two underlying sources supply "
  "the microstructure for precisely the aggregate claims built above: the funding gap and the "
  "margin-stacking constraint.")
H2("8.1 The firm-level instance: OpenAI")
P("PitchBook's analysis (Harrison Rolfes) is the firm-level version of the Section 3 inversion, "
  "and it closes consistently: to justify an $852 billion valuation, OpenAI must generate $95-105 "
  "billion of free cash flow by 2030 - roughly the same 8-12x forward-rent multiple the aggregate "
  "implied - while on Q1 trajectory it loses $10-30 billion that year instead [5]. (Free cash "
  "flow: operating cash flow minus capital expenditure - the cash actually left after running and "
  "investing in the business; FCF margin is that as a share of revenue.) Q1 2026 revenue was $5.7 "
  "billion at a negative 122 percent adjusted operating margin: $2.22 spent per dollar earned. "
  "Even OpenAI's own plan - roughly $280 billion of 2030 revenue, up from $13.1 billion in 2025, "
  "with its infrastructure target cut from $1.4 trillion to about $600 billion [11] - requires a "
  "~36 percent FCF margin at scale, better than Microsoft's or Apple's mature cash economics, "
  "achieved within four years while buying compute at scale against Google, Anthropic, and free "
  "open weights. The infrastructure target itself is mostly not owned assets but long-term "
  "purchase commitments: named pledges of roughly $250B to Azure, $300B to Oracle, $138B to AWS, "
  "$22.4B to CoreWeave, $10B to Broadcom, up to $100B from Nvidia (still a letter of intent per "
  "Nvidia's CFO as of December 2025), plus a 6GW AMD deal carrying warrants for up to ten percent "
  "of that supplier [7, 8, 9]. Roughly $820 billion of commitments stand against a $25-33 billion "
  "current revenue run rate - and this is the designated demand terminus of the whole loop, the "
  "node where external revenue is supposed to enter, with 85 percent of its 800-900 million "
  "weekly users on free tiers [5, 6]. The February 2026 markdown of the target from $1.4T to "
  "$600B was therefore not housekeeping: the terminus wrote down its own pledged draw by roughly "
  "$800 billion, and those pledges are exactly the flows other layers had capitalized.")
H2("8.2 Consolidation, double-capitalization, and margin stacking")
P("Draw the accounting perimeter around the complex and eliminate intra-group transactions, as "
  "consolidation would for any conglomerate: every circular deal vanishes in elimination entries, "
  "and what remains is the external P&amp;L - roughly $300-400 billion of outside revenue against "
  "$700 billion to $1 trillion of cash out. That gap is the socialization flow, running now, "
  "continuously - the structural difference from telecom, which socialized at the writeoff. The "
  "funding legs are index flows (the largest seven technology companies' ~35 percent S&amp;P 500 "
  "weight makes every passive retirement dollar a mechanical contribution), the debt migration, "
  "and sovereign capital. The Atlantic's what-happens-to-one-happens-to-all is then simply the "
  "observation that intra-complex claims net to zero: the complex is economically one consolidated "
  "entity whose equity tranches happen to trade separately.")
P("The sharpest structural feature is double-capitalization of a single uncertain flow. The same "
  "expected OpenAI spending appears as Oracle's remaining performance obligations - RPO, the "
  "accounting disclosure of contracted-but-undelivered revenue, which exploded to roughly half a "
  "trillion dollars largely on that one contract and repriced Oracle's equity enormously - as "
  "Nvidia's backlog, as CoreWeave's contracted revenue, and as hyperscaler committed-spend "
  "disclosures. Each layer capitalizes its margin slice of the flow into its own market "
  "capitalization, while OpenAI's $852 billion capitalizes the end revenue that must fund all of "
  "them. A trillion dollars of commitments is not a trillion of demand; it is one ~$280-billion-"
  "per-year aspiration pledged severally, which is why tail correlation inside the perimeter "
  "approaches one. The flagship toll-booth exhibit shows the same contamination directly: "
  "Microsoft's commercial remaining performance obligation reached $678 billion in mid-2026, up "
  "84 percent year over year - widely cited as the railroad-freight-contract evidence of durable "
  "enterprise demand - and includes OpenAI's $250 billion Azure commitment [26, 28]. Railroad "
  "freight contracts were signed by shippers with cargo; a third or more of this one is signed by "
  "the loop's own negative-margin terminus. And the margin-stacking constraint is already "
  "binding: the April renegotiation capping Microsoft's revenue share at $38 billion through 2030 "
  "- without which, per PitchBook, positive free cash flow is not possible - is rent reallocation "
  "inside the loop, by private negotiation, before external revenue has arrived [5]. The layers' "
  "summed margin assumptions exceeded what the flow could fund, and the reconciliation has "
  "quietly begun.")
H2("8.3 Equity-linked vendor financing and the corrupted signal")
P("The instrument set rhymes with 1999 but differs in one load-bearing way. Lucent and Nortel did "
  "vendor financing through receivables, concentrating customer credit risk on their own working "
  "capital. This cycle's version is equity-linked: supplier investments in customers, warrants "
  "granted to a customer, utilization backstops (Nvidia's arrangement to absorb unused CoreWeave "
  "capacity), compute credits structured as investment [7, 8, 9]. Equity-linked financing is "
  "system-safer - losses diffuse to shareholders rather than triggering a receivables death "
  "spiral - but epistemically worse, because it contaminates the demand signal itself. When the "
  "supplier funds the purchase and books it at 75 percent gross margin, and when Google's and "
  "Amazon's reported earnings include paper gains on their laboratory equity stakes (a point "
  "Fortune quantified in April 2026), the market's instruments for measuring whether external "
  "demand exists are themselves inside the loop. The contamination is now quarterly routine: "
  "Microsoft's July 2026 print included a $3.2 billion gain on its Anthropic stake - roughly nine "
  "percent of the quarter's net income marked from lab equity inside the loop [26]. Price "
  "discovery degrades because nearly every transaction carries a financing leg. Add OpenAI's "
  "DeployCo joint venture guaranteeing private-equity investors a 17.5 percent annual return [9] "
  "- equity risk repackaged as a debt-like claim - and the marginal capital is no longer risk-"
  "bearing in Perez's sense at all; it is rented, which is how installation phases end.")
P("The banked-bubble drift now has concrete instruments. Meta's Hyperion campus in Louisiana is "
  "financed through a special-purpose vehicle in which Blue Owl holds 80 percent: $27.3 billion "
  "of senior secured notes at a 6.581 percent coupon maturing 2049, secured not by the datacenter "
  "but by Meta's promise to pay rent from 2029 plus a residual-value guarantee - $27 billion of "
  "capacity debt held off balance sheet against a lease [28]. And credit markets already tier the "
  "loop that equity trades as one theme: Meta's SPV paper at 6.6 percent against CoreWeave's term "
  "loans at 11-15 percent and a 12.3 percent weighted short-term borrowing rate - a spread of "
  "five to six hundred basis points inside the same buildout, the tail correlation priced by "
  "lenders and ignored by index weights [28]. The IPO wave - OpenAI and Anthropic listing "
  "alongside Databricks [5] - is the 1999 rhyme: exposure migrating from strategic balance sheets "
  "to the index-holding public precisely as the internal reconciliation begins.")
H2("8.4 The ancestor: Credit Mobilier")
P("The related-party graph has an exact ancestor, one buildout older than Lucent. Credit Mobilier "
  "of America was the construction company owned by the Union Pacific's own promoters, which "
  "billed the railroad on the order of $94 million for construction costing perhaps $50 million "
  "and distributed discounted shares to congressmen for protection; the scandal broke in 1872 and "
  "the censures came in 1873, the year the boom itself did [32]. The structure's essence: the "
  "profits of the buildout were booked by insiders on the construction leg while the operating "
  "asset was born overloaded with obligations - construction-phase rent extraction wearing the "
  "costume of network demand, the corrupted signal a century and a half before vendor financing. "
  "Every generation's version differs in instrument and rhymes in function: Credit Mobilier's "
  "construction invoices, Lucent's receivables, Nvidia's equity stakes and warrants. The "
  "diagnostic question is constant across all three: who profits if the network is built, "
  "regardless of whether it is ever profitably run?")

# ----------------------------- SECTION 9 -------------------------------------
H("9. Vendor Financing, 1996-2002: Lucent, Nortel, Winstar")
P("The precedent deserves its detail, because both protagonists were blue-chip institutions. "
  "Lucent - Bell Labs plus Western Electric, spun out of AT&amp;T in 1996 - was briefly the most "
  "widely held stock in America, peaking near $250 billion of market value on about $38 billion "
  "of revenue. Nortel traced to 1895 and at its July 2000 peak represented roughly a third of the "
  "entire Toronto index at about C$400 billion. Both lost ~99 percent of their value within two "
  "years; Lucent merged into Alcatel in 2006 for $13.4 billion - a nineteenfold markdown from "
  "peak - and Nortel ceased to exist.")
P("The mechanism: the 1996 Act spawned hundreds of competitive local exchange carriers - thinly "
  "capitalized startups whose business plan was borrowing money to buy network equipment - and "
  "the vendors competed for those orders by supplying the purchase money themselves. Lucent's "
  "vendor-financing commitments reached roughly $8 billion, Nortel's several billion more, the "
  "industry perhaps beyond $20 billion. The accounting made it lethal: a vendor-financed sale "
  "books as revenue immediately, at full margin, with a receivable on the asset side - so the "
  "income statement showed booming demand while the balance sheet quietly accumulated credit "
  "exposure to customers solvent only while capital markets stayed open. Demand was partially "
  "synthetic - the vendors' own capital returning as orders - and the street extrapolated the "
  "revenue growth without consolidating the loop. When CLEC funding closed in 2000-01, customers "
  "died, receivables became writeoffs, and the extrapolated demand evaporated simultaneously. The "
  "canonical case is Winstar: Lucent committed $2 billion of financing to a fixed-wireless CLEC; "
  "Winstar went bankrupt in April 2001 and sued Lucent for $10 billion for cutting off the credit "
  "line - the customer suing the supplier for refusing to keep funding its own purchases, the "
  "loop stated as a legal claim.")
P("Each company added its own pathology. Lucent pulled demand forward with quarter-end discounts "
  "and distributor stuffing, restated $679 million of fiscal-2000 revenue, and ultimately faced "
  "SEC charges over roughly $1.1 billion of improperly recognized revenue [22]; the stock went "
  "from $84 to under a dollar, survival required spinning off Avaya and Agere and cutting "
  "headcount from ~130,000 toward ~35,000. The signature is the triple hit - revenue restated, "
  "receivables written off, credibility gone - each amplifying the others. Nortel's variant was "
  "paying about $32 billion in inflated stock for acquisitions and writing essentially all of it "
  "off - a $19.4 billion single-quarter loss in mid-2001, roughly $27 billion for the year - "
  "followed by a second act in which post-crash management released accounting reserves to "
  "manufacture a 2003 return to profitability, triggering executive bonuses, terminations for "
  "cause, two multi-year restatements, and criminal trials ending in acquittal in 2012 but never "
  "in recovered credibility. It filed in January 2009 - Canada's largest bankruptcy [23]. The "
  "estate sale connects to the residue thread: the operating businesses fetched a few billion in "
  "pieces while the single most valuable asset was the patent portfolio, sold for $4.5 billion to "
  "an Apple-Microsoft-Ericsson consortium that outbid Google, whose opening bid was literally "
  "$3.14159 billion - pi. The durable product of a century-old institution was pure intellectual "
  "property, purchased for exclusion. Cross-border litigation over splitting the estate burned "
  "roughly $2 billion in professional fees over eight years, and some twenty thousand pensioners "
  "took devastating losses.")
P("What the detail adds to the AI mapping. First, the vendors acted knowingly, inside a "
  "prisoner's dilemma: if Lucent would not finance Winstar, Nortel or Cisco would, and land-grab "
  "logic made unilateral prudence equivalent to ceding share. The same structure operates now - "
  "each equity-linked deal defensible as positioning, the ensemble a machine for manufacturing "
  "the demand signal. Second, the failure mode differs by instrument: receivables financing put "
  "customer credit risk on the vendor's own working capital, so death came fast and triple-"
  "barreled; equity-linked losses mark to a line investors already treat as speculative, so an "
  "unwind would be slower and less mechanically self-reinforcing - genuinely safer plumbing "
  "around the same corrupted signal. Third, collateral: repossessed CLEC networks were worth "
  "nearly nothing to anyone else, whereas repossessed GPUs are fungible - though fungible into a "
  "glut, which is how two-cent bandwidth happened. Fourth, any unwind's complexity: Nortel's "
  "estate had one jurisdictional web to untangle and consumed $2 billion in fees; the OpenAI-"
  "Microsoft-Oracle-Nvidia-SoftBank claim graph would make that fight look like small claims. The "
  "cheerful coda stands: Winstar's stranded assets and the CLECs' dark fiber became the cheap "
  "substrate of the deployment era. The vendors financed a commons and were repaid in bankruptcy "
  "claims.")

# ----------------------------- SECTION 10 ------------------------------------
H("10. The July 2026 Rotation: Rent Location Goes Live")
P("The rent-location question stopped being theoretical in July 2026, but the experiment began "
  "nine months earlier. From October 2025 the market ran the builder-versus-rider trade at index "
  "scale, in the builders' favor: enterprise software sold off on fears that agents would "
  "cannibalize seat-based spending - the debate acquired a name, the &#8220;SaaSpocalypse&#8221; - "
  "with Salesforce down 33 percent and Adobe down 31 percent for the year by late July, while the "
  "buildout's second derivative ran [27]. Situational Awareness LP - founded in mid-2024 by "
  "Leopold Aschenbrenner, a former OpenAI researcher, on $225 million from Patrick and John "
  "Collison, Nat Friedman, and Daniel Gross - was that trade in its purest form: long memory, "
  "fuel cells, neoclouds, and bitcoin miners converting substations into compute; short the "
  "application incumbents; roughly four times levered [24, 28]. It returned 439 percent net in "
  "the first half of 2026 and reached about $45 billion of assets with a staff of roughly a "
  "dozen, and its July 24 letter to investors invited additional capital [24, 25].")
P("Twenty sessions inverted both legs. The fund's disclosed longs fell 36-55 percent in July - "
  "Sandisk -55, Nebius -46, Bloom Energy -46, CoreWeave -39, Micron -36 - while the software "
  "side surged: for the full month, Workday +31, Adobe +22, Intuit +22, Salesforce +18, and "
  "Microsoft +25, against a Nasdaq down roughly ten percent and an S&amp;P down two, with Nvidia "
  "about flat [27, 28]. This was not an AI crash; the index barely moved. It was a violent "
  "migration out of the leveraged, capital-hungry end of the complex into the profitable, asset-"
  "light end - out of the builders, into the toll booths. Margin calls from Bank of America, "
  "Goldman Sachs, and JPMorgan forced the sale of the entire public book, longs and shorts "
  "together, roughly $16 billion, to Citadel in a single block at about a ten percent discount "
  "before the July 30 open [24]. Assets finished near $10 billion - roughly half of it a "
  "retained private stake in Anthropic, which a spokesman said was not for sale - with the fund "
  "still up about 80 percent for the year and reopened to subscriptions on August 1 [24].")
P("The tape's testimony must be read with care, because it cuts both ways. Every core long "
  "bottomed on July 29 - margin-call day - and snapped back violently the moment the block "
  "cleared: both sides of the book moved in the fund's favor the day the book stopped being the "
  "fund's, which is the cleanest available statement that July's prices measured positioning, "
  "not truth [25]. The Microsoft print is the controlled experiment inside the event. Into its "
  "July 29 report the stock carried its highest short interest in a decade - 92 million shares, "
  "the largest increase among the seven largest technology companies, with no covering into "
  "earnings - and a 19 percent year-to-date decline: the market had spent 2026 treating "
  "Microsoft as a doomed capex name [26]. It reported Azure accelerating to 43 percent growth - "
  "the fastest in four years, past $100 billion for the fiscal year - and held rather than "
  "raised its capital-spending guidance, and the stock rose about 16 percent, adding $480 "
  "billion in a single session, as the shorts covered and the market's largest forced seller "
  "exited the same morning [26]. Forced to choose between Microsoft-the-builder and Microsoft-"
  "the-rails, the market chose the rails; the violence of the choosing was flow. The choice then "
  "held: through the turn of the month the rotation extended rather than reversed [27]. And "
  "inside the celebrated print sat Section 8's contamination, live: a $3.2 billion gain on the "
  "company's Anthropic stake - roughly nine percent of the quarter's net income marked from lab "
  "equity inside the loop - alongside the company's first-ever voluntary retirement program in "
  "the same quarter it passed thirty million paid Copilot seats [26].")
P("Three lessons for the framework, none of them the consensus one. First, the event is the "
  "first mass repricing from the market's rent allocation toward history's - builders toward "
  "replacement cost, riders toward rent capture - and it occurred without any aggregate crash, "
  "exactly as the location corollary permits: the level and the location of the rents are "
  "separate questions, and July moved only the second. Second, the blowup does not adjudicate "
  "the decade thesis. Early and levered is punished identically to wrong; a fund can be carried "
  "out of positions that later prove correct, and the public post-mortems split on precisely "
  "this point within days [25, 28]. The residual irony is instructive without being conclusive: "
  "when the second-derivative book burned, the asset that survived was equity in a model "
  "laboratory. Third, the toll-booth reading carries two qualifications its promoters omit. "
  "Seat-priced software is a derivative claim on headcount: the express companies won because "
  "package traffic exploded, while a seat-based toll booth sits on a road whose traffic is the "
  "thing being automated - and Microsoft ran its first voluntary retirement program in the same "
  "quarter it sold thirty million Copilot seats. Survival requires repricing from seats to work "
  "faster than usage-native entrants undercut, and the incumbents' agent products - consumption-"
  "priced, growing at triple-digit rates from small bases - are that repricing attempted in real "
  "time. And the historical toll booths did die: parcel post in 1913, consolidation into "
  "American Railway Express in 1918, Pullman by consent decree - killed by the state, not by "
  "competition [31]. Moats built of standards, audit trails, and validated records are political "
  "artifacts, and regulatory tail risk is what concentration accumulates. A provenance caution "
  "completes the record: the sharpest public post-mortem of the episode doubles as marketing for "
  "toll-booth stock recommendations [28]. Its history checks out; its certainty is merchandise.")

# ----------------------------- SECTION 11 ------------------------------------
H("11. Synthesis and Watch Variables")
P("The through-line of this report is a single decomposition applied at every scale. Market value "
  "equals replacement-cost assets plus capitalized rents; the assets are ~$1.2 trillion and the "
  "capitalized rents ~$17 trillion, so the entire live dispute concerns a rent stream that must "
  "grow several-fold and persist. The rents currently earned are predominantly scarcity rents in "
  "the supply chain - the mean-reverting kind - and they are simultaneously embedded in the asset "
  "book values, so competitive normalization shrinks numerator and denominator together. The "
  "revenue that must eventually fund the rents has no sufficient source except labor "
  "substitution, at a GDP share that history says takes decades to grow, and the interim is "
  "bridged by a circular financing structure that consolidates to a negative external cash flow "
  "funded continuously by index capital, debt, and sovereigns - a socialized buildout in real "
  "time rather than at the crash. The precedents say the private outcome and the social outcome "
  "can diverge completely: three networks were built by capital that was never repaid, and "
  "society received the substrate of the modern world - including, on the longest accounting, "
  "the corpus and the cash engine that produced machine intelligence. History adds that the "
  "profits, where they existed, went to asset-light riders on the network rather than its "
  "owners; July 2026 was the first mass repricing toward that allocation. Whether this cycle's "
  "version bequeaths or evaporates turns on asset lives and on what fraction of capability "
  "persists in open, unpossessable form.")
P("The strongest form of the whole argument comes from the railway literature and deserves the "
  "closing word on method. Campbell's reconstruction of the 1840s found that railway shares were "
  "not obviously mispriced even at the peak - prices rose 106 percent and then fell below their "
  "starting value, but dividends rose and fell along the same path - even though the Mania's "
  "investors took large losses and the network build was, in aggregate, ruinous [30]. A sector "
  "can overbuild catastrophically without any individual security being mispriced against its "
  "own expected cash flows. The $8-17 trillion residual of Section 3 therefore requires no claim "
  "that anyone is irrational about Nvidia or Microsoft; fallacy of composition suffices - each "
  "layer fairly priced against margin assumptions that cannot jointly be satisfied by the end "
  "flow. That is a harder claim to dismiss than &#8220;the market is wrong,&#8221; and it is the "
  "claim this report intends.")
P("The variables worth watching, each tied to a specific failure or falsification mode developed "
  "above: the CoWoS supply-demand gap closing through 2026 and memory fabs landing 2027-28 "
  "(scarcity-rent normalization; the bullwhip); external AI revenue against the ~$1.7 trillion "
  "breakeven floor and the 3-6.5 percent-of-GDP ceiling (the transition from capex-funded to "
  "demand-funded rents); cloud AI growth rates sustaining above ~50 percent (the falsifier of "
  "the pessimistic case); the seat-to-work repricing of application software and whether the "
  "July 2026 rotation holds (the live rent-location experiment); the credit spread between the "
  "complex's investment-grade core and its levered edge (the lenders' pricing of the tail); the "
  "debt and private-credit share of buildout funding (equity-diffused versus banked-bubble loss "
  "distribution); further intra-loop rent renegotiations of the Microsoft-cap type (margin "
  "stacking made visible); RPO and backlog concentration against single counterparties (double-"
  "capitalization exposure); the IPO absorption of OpenAI, Anthropic, and Databricks paper (the "
  "migration of exposure to the public); and the cadence and capability gap of open-weight "
  "releases (the size of the permanent endowment if the funding stops).")

# ----------------------------- PROVENANCE ------------------------------------
H("Data Provenance")
P("Figures in this report divide into three classes. <b>Reported:</b> company disclosures and "
  "named third-party research - hyperscaler capex and guidance, Nvidia and TSMC results, Gartner "
  "spending series, PitchBook's OpenAI analysis, the CNBC/WSJ/FT accounts of the Situational "
  "Awareness unwind, and Microsoft's FQ4 2026 results. <b>Estimated by the authors:</b> the "
  "AI-attribution shares of capex, the vintage capital-stock model and all of Tables 1-4, the "
  "competitive-cost repricing, current external AI revenue ($300-400B), realized rent composition "
  "(~$330-350B/yr), historical IT-share-of-GDP ratios, and the labor-decomposition arithmetic. "
  "<b>Historical literature:</b> the railway, railroad, telecom, and vendor-financing records, "
  "cited below. An August 2026 primary-verification pass re-anchored the depreciation-extension "
  "inventory and Amazon's reversal to the companies' own filings [33] (correcting the mixed "
  "operating/net series relayed by [28]), the mileage and ton-mile series to Historical "
  "Statistics, NBER Macrohistory, and Fishlow [34] (restating the 1870 ton-mile endpoint as "
  "Fishlow's ~2.2-cent estimate), and the Moody's and Bain projections to their publishers "
  "[35, 36]. Per-name July 2026 long/short returns, the nineteenth-century express-company "
  "financials, the Cooke and NYSE-share detail, and the loop's private financing terms are still "
  "taken from [28] - a marketing document - and have not been independently verified line by "
  "line; the aggregate account of the fund unwind is "
  "verified against [24]-[25], the Microsoft print against [26], the software-rotation aggregates "
  "against [27], and the railroad statistics against [29]-[30] and [34] where sources exist. Where a range "
  "is given, the range is the claim. Nothing here is investment advice; it is an accounting "
  "framework with explicit assumptions, built to be argued with.", note)

# ----------------------------- APPENDICES ------------------------------------
H("Appendix A. Capital Stock Model")
P("Vintage gross capex as in Table 1. Asset mix and straight-line lives: IT equipment "
  "(accelerators, servers, networking, memory, storage) 62 percent at 5 years; power and cooling "
  "infrastructure 23 percent at 15 years; shell and land 15 percent at 30 years; mid-year "
  "convention per vintage. The five-year IT life is corroborated by Amazon's January 2025 "
  "reversion of a subset of server lives from six years to five, disclosed as a response to the "
  "pace of AI hardware development [26, 28]. Add-ons at mid-2026, net (low/central/high, $B): "
  "upstream fab plant AI-allocated 105/125/145; power and grid 45/65/85; model IP at cost "
  "excluding compute 35/55/75. Competitive-cost adjustment: accelerator and networking spend "
  "taken as 75 percent of the IT stock, repriced to 45 percent of paid price (competitive-margin "
  "replacement); other IT repriced to 75 percent; infrastructure and shell at cost. Rent flows in "
  "Table 3 use required flow = rent capitalization times (r - g) for the growing case (r = 8%, "
  "g = 3%), times r for the flat case, and times (r + d) with d = 10% for the decaying case. "
  "Sensitivity: moving every vintage to its high case and Nvidia's implied IT share to 55 percent "
  "raises the central net stock by roughly $200B; the rent capitalization changes by less than 2 "
  "percent, because it is dominated by the market-value term.", note)
H("Appendix B. Revenue Requirement Model")
P("Required after-tax profit = required rent flow (Table 3, $18T attribution) + 8 percent normal "
  "return on a projected 2030 net stock of ~$5T (from ~$5.3T big-four capex 2025-2030 plus the "
  "rest of the ecosystem, net of depreciation). External revenue = profit / consolidated net "
  "margin, shown at 12, 20, and 30 percent. GDP bases: world ~$135T and US ~$35T nominal in 2030 "
  "(~5 percent nominal growth from ~$118T and ~$30.5T in 2026, IMF-consistent). Breakeven floor "
  "= depreciation on the 2030 stock (~$940B/yr at the Appendix A mix, net-to-gross ~0.77) + "
  "operations (~$275B) + tax-adjusted cost of capital (~$480B) = ~$1.70T/yr = 1.3 percent of "
  "2030 world GDP. Labor decomposition: revenue R = capture share times labor cost addressed; at "
  "30 percent capture, R of $4.0/5.5/7.0T implies $13.3/18.3/23.3T addressed = 19/26/33 percent "
  "of global labor income (53 percent of world GDP).", note)

# ----------------------------- REFERENCES ------------------------------------
H("Sources")
refs = [
 "[1] Goldman Sachs Insights, \"Are US stock market valuations outpacing fundamentals?\" (July "
   "2026). goldmansachs.com/insights/articles/are-us-stock-market-valuations-outpacing-fundamentals",
 "[2] Gartner press release, \"Gartner Forecasts Worldwide IT Spending to Grow 13.5% in 2026, "
   "Totaling $6.31 Trillion\" (April 22, 2026). gartner.com/en/newsroom/press-releases/2026-04-22",
 "[3] Gartner press release, \"Worldwide IT Spending to Grow 9.8% in 2026, Exceeding $6 Trillion "
   "for the First Time\" (October 22, 2025), including the segment table cited. gartner.com/en/"
   "newsroom/press-releases/2025-10-22",
 "[4] Gartner press release, \"Worldwide IT Spending to Grow 10.8% in 2026, Totaling $6.15 "
   "Trillion\" (February 3, 2026) - the intermediate revision. gartner.com/en/newsroom/press-releases/2026-02-03",
 "[5] H. Rolfes, PitchBook, \"OpenAI is going public as the worst value among its AI peers\" "
   "(June 2026). pitchbook.com/news/articles/openai-business-quality-valuation-analysis; also as "
   "syndicated by Morningstar and Yahoo Finance (June 3-5, 2026).",
 "[6] H. Rolfes, PitchBook, \"AI's giants: Mostly priced on promise\" (March 2026). "
   "pitchbook.com/news/articles/ais-giants-mostly-priced-on-promise",
 "[7] Bloomberg Graphics, \"AI Circular Deals: How Microsoft, OpenAI and Nvidia Keep Paying Each "
   "Other\" (2026, continuously updated). bloomberg.com/graphics/2026-ai-circular-deals",
 "[8] E. Forgash and A. Ghosh, Bloomberg, \"OpenAI, Nvidia Fuel $1 Trillion AI Market With Web of "
   "Circular Deals\" (October 7, 2025); N. Smith, \"Should we worry about AI's circular deals?\" "
   "Noahpinion (October 2025), noahpinion.blog/p/should-we-worry-about-ais-circular; S. Rasgon, "
   "Bernstein Research note (September 2025), as reported.",
 "[9] AI Circular Economy tracker (ai-circular-economy.com, 2026): compiled deal terms including "
   "OpenAI compute commitments by counterparty, Nvidia CFO letter-of-intent status (December "
   "2025), DeployCo return guarantee (May 2026), and the Fortune (April 2026) analysis of paper "
   "gains on laboratory equity in Google and Amazon earnings. Secondary compilation; individual "
   "deal terms as reported by Bloomberg, FT, and WSJ.",
 "[10] The Atlantic (July 2026), essay on AI valuations and circular investment, as excerpted by "
   "the requester; the ouroboros characterization and the PitchBook FCF citation appear there.",
 "[11] Press coverage of OpenAI investor communications (February 2026): infrastructure target "
   "reduced from ~$1.4T to ~$600B through 2030; ~$280B projected 2030 revenue from $13.1B in "
   "2025; ~$8B 2025 cash burn; ~$100B round at ~$830-852B valuation.",
 "[12] Nvidia quarterly results, FY2025-FY2027: datacenter revenue $115.2B (FY2025), $193.7B "
   "(FY2026), $75.2B (Q1 FY2027, total revenue $81.6B, +85% y/y).",
 "[13] Hyperscaler Q4 2025 and Q1 2026 earnings disclosures: combined 2026 capex guidance ~$725B; "
   "Microsoft $190B (including ~$25B attributed to memory and component inflation); Google Cloud "
   "+63% y/y; Oracle remaining performance obligations ~half a trillion dollars.",
 "[14] TSMC Q1 2026 results and investor commentary: HPC at 61% of revenue; 66.2% gross margin; "
   "2026 capex $52-56B.",
 "[15] Financial Times and CreditSights compilations of hyperscaler capex, AI shares (~75% for "
   "2026), capital intensity (45-57%; Oracle 86%), and debt issuance ($108B in 2025; ~$1.5T "
   "projected); Morgan Stanley and Goldman Sachs capex projections as reported.",
 "[16] TrendForce and trade-press reporting on TSMC CoWoS capacity (~35K wpm end-2024, ~75K "
   "end-2025, 125-130K target end-2026; 10-20% supply gap) and on memory: HBM share of DRAM "
   "wafer starts 8% (2024) to 23% (2026); ~3:1 HBM:DDR5 wafer intensity; Micron consumer-memory "
   "exit; DDR5 contract pricing +100%+.",
 "[17] Econbrowser, \"q-theory in a Time of AI\" (December 2025), econbrowser.com - aggregate "
   "Tobin's q against the intellectual-property capital stock, Federal Reserve Z.1 data.",
 "[18] A. Odlyzko, \"Internet traffic growth: Sources and implications\" (2003) and related "
   "papers on the doubling-every-100-days myth and telecom-bubble capital allocation.",
 "[19] W. Nordhaus, \"Schumpeterian Profits in the American Economy: Theory and Measurement,\" "
   "NBER Working Paper 10433 (2004).",
 "[20] C. Perez, Technological Revolutions and Financial Capital (2002); W. Janeway, Doing "
   "Capitalism in the Innovation Economy (2012).",
 "[21] The Economist, \"The great telecoms crash\" and \"Too many debts; too few calls\" (July "
   "2002) - sector debt ~$1 trillion, up to half unrecoverable; M. Powell, testimony before the "
   "Senate Commerce Committee (July 30, 2002) - ~$2 trillion of market value and ~$1 trillion of "
   "debt lost, ~500,000 jobs (the $2T figure is Powell's, not The Economist's); contemporaneous "
   "reporting on WorldCom, Global Crossing, Level 3, and European 3G auctions.",
 "[22] SEC v. Lucent Technologies Inc., Litigation Release 18715 (May 2004); contemporaneous "
   "reporting on Lucent vendor financing, the Winstar commitment and litigation, and the fiscal-"
   "2000 restatement.",
 "[23] Nortel Networks bankruptcy proceedings (January 2009) and the Rockstar consortium patent "
   "auction ($4.5B, 2011), including Google's opening bid of $3.14159B; court records on estate "
   "professional fees and pension outcomes.",
 "[24] CNBC reporting on the Situational Awareness unwind (D. Faber and others, July 30-31, "
   "2026): forced sale of the public book to Citadel; margin calls from Bank of America, Goldman "
   "Sachs, and JPMorgan; peak ~$45B and residual ~$10B; retained Anthropic stake not for sale per "
   "spokesman; the Wall Street Journal's identification of Citadel; the Financial Times' report "
   "of the July 24 investor letter (439% net H1); Bloomberg on reopened capital raising. "
   "cnbc.com/2026/07/30 and /2026/07/31.",
 "[25] SpotGamma, \"Anatomy of a Margin Call: How Situational Awareness LP Unwound a $20 Billion "
   "AI Book in One Trade\" (July 31, 2026) - unwind mechanics, disclosed positions, leverage, and "
   "the July 29 bottoms in core longs. spotgamma.com.",
 "[26] Microsoft FQ4 2026 results and coverage (July 29-30, 2026): CNBC results report ($3.2B "
   "gain on Anthropic investment; Azure FY26 revenue above $100B, +41%; 30M+ paid Copilot seats; "
   "shares -19% YTD into the print; first voluntary retirement program); Bloomberg (shares +16%, "
   "fastest cloud growth in four years); Fortune ($480B single-session market-value gain); "
   "Investing.com (Azure +43% vs ~40% consensus; FQ4 capex $41B, ~two-thirds short-lived assets; "
   "guidance); CNBC/S3 Partners (July 28: 92M shares short, largest short interest since May "
   "2015, no covering into earnings).",
 "[27] Software-rotation coverage: Stocktwits (August 3, 2026) - July returns of Workday +31%, "
   "Adobe +22.1%, Intuit +21.6%, Autodesk +20.4%, Salesforce +17.5%, Microsoft +24.6%, on "
   "rotation out of chip stocks; 24/7 Wall St. (July 27, 2026) - YTD drawdowns (Salesforce -33%, "
   "Adobe -31%) and the \"SaaSpocalypse\" framing; CNBC (May 29, 2026) on the earlier software "
   "rebound from April lows.",
 "[28] F. P. Stansberry / Porter &amp; Co. (August 2026), essay on the Situational Awareness "
   "unwind and the toll-booth thesis, circulated on X and via members.porterandcompanyresearch."
   "com - source, as relayed, of the per-name July long/short returns; hyperscaler capex-to-"
   "operating-cash-flow ratios; Moody's 2026-27 capex and debt projections; Bain and Sequoia "
   "(Cahn) revenue-gap estimates; the depreciation-extension inventory and Amazon's reversal; "
   "Oracle FY2026 and CoreWeave financing terms; the Meta Hyperion SPV terms; OpenAI audited "
   "2025 results; the 1865-77 railroad statistics; and the express-company and Pullman "
   "financials. A marketing document for the author's newsletter; aggregate claims verified "
   "against [24]-[27] and historical claims against [29]-[31] where possible; the depreciation "
   "inventory, Moody's and Bain figures, and mileage/ton-mile series have since been re-anchored "
   "to primaries [33]-[36].",
 "[29] US railroad history: R. Fogel, Railroads and American Economic Growth (1964); A. Fishlow "
   "(1965); Donaldson &amp; Hornbeck, NBER WP 19213; Pereira, W&amp;M economics WP 153 "
   "(antebellum returns); Depression of 1882-85 literature, including the estimate of railroads "
   "at ~15% of 1880s US capital formation; Investment Research Partners (August 2025) - "
   "datacenter capex ~1.2% of US GDP (2025) vs telecom ~1.0% (2000) vs railroads ~6.0% (1880s); "
   "Fabricated Knowledge, \"Lessons from History: The Great Railroad Buildout\" (December 2025) "
   "- capitalization $4.6B (1876) to $10.6B (1890), ~40% \"water\"; standard receivership "
   "accounts for 1873-77 and 1893-94.",
 "[30] Railway Mania: G. Campbell, \"Deriving the Railway Mania\" (2013) and VoxEU/CEPR column "
   "(prices +106% 1843-45; dividends 4.4% to 7% to 2.4%; shares not obviously mispriced at "
   "peak); Campbell &amp; Turner (2012; 2015); A. Odlyzko, \"The collapse of the Railway Mania\" "
   "and related; Bruner et al., Journal of Applied Corporate Finance (2025); Business History "
   "(2022-24) on managerial failure and the incumbents' expansion.",
 "[31] Express companies and Pullman: standard histories (A. Harlow, Old Waybills; company "
   "records); Adams Express reorganization as a closed-end fund (1929; today Adams Diversified "
   "Equity Fund); Parcel Post Act (1913); wartime consolidation into American Railway Express "
   "(1918); Pullman antitrust consent decree and divestiture (1944-47). Specific dividend and "
   "capital figures as relayed by [28]; see Data Provenance.",
 "[32] Credit Mobilier: standard accounts of the Union Pacific construction financing, the "
   "congressional share distribution, and the 1872-73 investigation and censures.",
 "[33] Useful-life change-in-estimate disclosures, verified verbatim (August 2026): Microsoft "
   "10-K FY2023 (+$3.7B operating income / +$3.0B net); Alphabet 10-K FY2023 (+$3.9B "
   "depreciation reduction / +$3.0B net); Amazon 10-K FY2024 (+$3.2B D&amp;A / +$2.5B net) and "
   "10-K FY2025 with Q1-2025 10-Q (the 6-to-5-year reversal: +$1.4B D&amp;A / -$1.0B net in "
   "2025, primarily AWS; separate from ~$920M Q4-2024 accelerated depreciation on early "
   "retirements); Meta 10-K FY2024 and FY2025 (+$2.92B depreciation / +$2.59B net); Oracle 10-K "
   "FY2025 (+$733M opex / +$573M net; an earlier FY2023 change added $434M). All at SEC EDGAR.",
 "[34] Railroad primaries: Historical Statistics of the United States, Colonial Times to 1970 "
   "(Bicentennial Ed.), Series Q 321 (miles of road operated: 1865 = 35,085; 1875 = 74,096; "
   "first differences 2,665 in 1878 and 11,569 in 1882) and Q 329 (miles built: 7,439 in 1872) "
   "- note the construction figures mix the two adjacent series; both are Poor's-derived. NBER "
   "Macrohistory A0303BUSA259NNBR (revenue per freight ton-mile, all railroads, 1882-1911: 1900 "
   "= 0.729 cents) and A02F2AUSA374NNBR (miles built); A. Fishlow, \"Productivity and "
   "Technological Change in the Railroad Sector, 1840-1910\" (NBER, 1966), Table 1 (1870 = 2.18 "
   "cents, an estimate by his own caveat). Figures nominal; the general price level also fell "
   "1870-1900.",
 "[35] Moody's Ratings, hyperscaler capex forecast update (May 2026): $785B in 2026, "
   "approaching $1T in 2027, for the six largest US hyperscalers (Microsoft, Amazon, Meta, "
   "Alphabet, Oracle, CoreWeave); an $85B markup from the March 2026 forecast. As covered by "
   "Data Center Dynamics and CNBC (July 24, 2026). AWS capex is Moody's estimate. Distinct from "
   "Moody's December 2025 global datacenter outlook (&gt;$3T over five years).",
 "[36] Bain &amp; Company, 6th annual Global Technology Report, press release (September 23, "
   "2025): roughly $2 trillion in annual revenue needed by 2030 to fund AI compute demand; "
   "\"even with AI-related savings, the world is still $800 billion short.\" bain.com.",
 "[37] Inference margins and revenue mix (August 2026 verification pass): DeepSeek, \"Overview "
   "of DeepSeek-V3/R1 Inference System\" (open-infra-index, February 2025) - $87,072 daily GPU "
   "cost at an assumed $2/hr H800 against $562,027 theoretical daily revenue, self-labeled "
   "theoretical, with free web/app tiers and off-peak discounts excluded. OpenAI adjusted gross "
   "margin ~33% (2025) vs 40% (2024) and a 46% plan, and the ~70% figure as a compute margin "
   "rather than gross margin: The Information, as relayed in secondary coverage - treat as "
   "reported-not-disclosed. Anthropic gross-margin guidance cut ~10 points to ~40% on third-party "
   "inference overrun (~23% over plan): The Information, January 2026. Revenue mix: OpenAI API "
   "~25% of a $12B run rate (Financial Times, August 2025), the majority being subscriptions; "
   "Anthropic ~75-85% API and enterprise (estimated, no segment disclosure - the S-1 is "
   "confidential). Application-layer gross margins 33% (2024) / 38% (2025) / 45% (2026 "
   "projected): ICONIQ survey of ~300 software executives, published January 2026; negative "
   "gross margins at AI-native coding firms and the recovery via backward integration, reported "
   "via investor sourcing. S. Altman, public statement (January 2025), on losing money at $200 "
   "per month.",
]
for r in refs:
    P(r, ref)
SP(6)
S.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#888888'),
                    spaceBefore=4, spaceAfter=6))
P("Second edition, compiled August 4, 2026, from a working dialogue; first edition "
  "July 27, 2026. "
  "Estimates are the authors' and carry the uncertainties stated in the Data Provenance note; "
  "reported figures are as of their cited dates and may since have been revised.", note)

doc.build(S)
print("built", OUT)
