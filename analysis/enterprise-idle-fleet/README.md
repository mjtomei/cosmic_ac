# Enterprise idle fleets as a federation substrate

Question (Matthew, 2026-08-02): are business laptops left plugged in at offices
overnight a more reliable federation resource than household consumer devices,
with owners who are incentivised to sell the idle capacity?

Method: four agent sweeps over primary sources only — EIA CBECS microdata, EIA
Electric Power Monthly, Eurostat APIs, BEA fixed assets, SEC filings, EPA
ENERGY STAR's open dataset, EUR-Lex, NIST's OSCAL catalog, and peer-reviewed
papers. Raw results with per-item provenance and caveats: `sweep-findings.json`
(57 findings). Anything the agents could not fetch is marked UNVERIFIED there
and is **not** repeated as fact here.

## The answer in one line

The premise is half right, and the wrong half is the laptop half: **laptops go
home; desktops stay.** The strong version of the idea is a desktop story.

## What supports the idea

| Fact | Number | Source |
|---|---|---|
| Business PCs in US commercial buildings | 63.85M desktops + 47.76M laptops = 111.6M | EIA CBECS 2018 public microdata (FINALWT-weighted; our computation, not an EIA table) |
| PCs per worker in those buildings | 1.30 | Same |
| Desktops left on after hours | ~64% turn-off rate 36%, n=1,453 | Roberson/Webber et al., LBNL-53729 (2004), doi:10.2172/821675 |
| Power management essentially absent | 6% of not-off desktops in low power | Same |
| Laptops present after hours were mains-connected | 95% plugged in, 60% docked (n=37) | Same |
| Commercial electricity vs residential | 13.79 vs 18.11 c/kWh (YTD May 2026) | EIA Electric Power Monthly T5.3 — **the business pays ~24% less than a household** |
| Notebook idle power | 5.15 W short idle / 0.90 W long idle (mean, n=1,140 certified models) | EPA ENERGY STAR Certified Computers V9.0 |
| Apple silicon throughput / efficiency | 2.9 FP32 TFLOPS (M4 GPU), 10–20 W, 0.33 TFLOPS/W | Hübner et al., IPDPSW 2025, arXiv:2502.05317 |
| Managed CPU idleness, institutional fleet | 97.9% mean, 169 machines, 77 days | Domingues et al., ICPPW 2005 |
| Volunteer (household) host availability — the baseline to beat | ~0.61 of wall time (product of on/connected/active/efficiency) | Anderson & Fedak, CCGrid 2006 |
| Commercial share of PC vendor revenue | Dell 86.4% CSG; HP 71.2% Personal Systems | Dell 10-K FY2026; HP 10-K FY2025 |

**Derived (our arithmetic, stated as such):** 63.85M desktops × ~64% left on
≈ **~41M business desktops powered and idle overnight in US commercial buildings**.
Energy to harvest one idle Apple-class SoC ≈ 20 W × 13.79 c/kWh ≈ **$0.003/hour**,
about 3 cents a night. Both figures combine sources across years; treat as
order-of-magnitude sizing, not measurement.

## What cuts against it

1. **Most laptops leave.** 80% of 107 docking stations were empty after hours,
   and only 24% of laptops found were clearly on (LBNL-53729). Hybrid work has
   sharpened this: 35% of employed people did some work at home on a given day
   in 2025, 51% among degree-holders (BLS ATUS 2025).
2. **Sleep is mandated, as shipped.** EU Ecodesign Reg. 617/2013 requires
   notebooks to enter sleep within 30 min of inactivity, capped at ≤3 W, and to
   throttle gigabit links on the way into sleep; ENERGY STAR v8 §3.3.1 imposes
   the same default in the US. The counterfactual to harvesting is not a wasteful
   idle machine but a 3 W sleeping one.
3. **Waking the fleet is harder than folklore.** Windows WOL does not work from
   the default shutdown state (MS KB2776718); Modern Standby machines have no S3
   to wake from, and Windows 11 24H2 disables most wake sources on detected
   drain. ENERGY STAR does require notebook WOL on AC power — the docked subset
   is reachable by design, which is the pro-case's best single fact.
4. **Endpoint policy gives IT the tooling to refuse.** NIST SP 800-53r5 CM-7(5)
   (deny-all, permit-by-exception execution), CM-10 (control P2P specifically),
   CM-6 (most restrictive setting consistent with operations). macOS Gatekeeper
   requires notarisation. None of this is prohibitive; all of it is friction and
   an approval gate. *Prevalence of enforcement is unmeasured — a real gap.*
5. **Sustained load on mobile hardware.** Battery calendar ageing accelerates at
   high state-of-charge and temperature (Stroe et al., IEEE TIA 2017); mobile-class
   silicon throttles under continuous inference (Wang et al., arXiv:2206.10849).

## The Mac claim, verified — and narrower than the advertisement

Apple's live wording (apple.com/business, fetched 2026-08-02) is **"84% of top
U.S. companies use Mac at scale,"** footnoted to *LinkedIn Top Companies 2026:
the 50 best large employers* plus undisclosed internal Apple data. So the
denominator is **50 companies (42 of 50)**, not the Fortune 500, and "at scale"
is undefined. **Do not repeat the popular ">80% of the Fortune 500" phrasing —
no primary Apple source supports it.**

For scale, Apple is **9.2% of worldwide PC units** (24.83M of 270.2M, 2025;
Gartner, via Wayback). The best hard number for managed Apple fleets is
**33.2M devices across 76,500 organisations** (Jamf 10-K FY2024) — but Jamf never
splits Mac from iPhone/iPad, and the base includes large K-12 iPad deployments,
so it is a loose upper bound. Apple's other enterprise claims are commissioned
studies with undefined denominators (Forrester TEI on help tickets; Omdia's
"57% of enterprise AI models can run locally on MacBook Air"). **The federation
argument should not lean on Macs specifically.**

## The open measurement

Nobody has repeated the after-hours census since 2004. LBNL-53729 predates
modern sleep defaults entirely, its laptop sample is 37 machines, and the
desktop-to-laptop shift and hybrid work have both happened since. **The central
number for this entire question — what fraction of business machines are
powered and reachable outside working hours in 2026 — is unmeasured.** It is
cheap to measure (a network sweep of one organisation's fleet) and would be
publishable on its own.
