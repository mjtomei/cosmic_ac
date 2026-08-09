# Recognition half-life: how fast each era's accounting forces a capital vintage's
# COST into the P&L. Annual straight-line rate on gross stock = sum(share/life);
# half-life solves sum(share_i * min(t/life_i, 1)) = 0.5. A class with life None
# is under betterment/replacement (RRB) or otherwise unscheduled accounting: its
# vintage cost is never amortized — recognition only at events (receivership,
# impairment, restatement) — the "storable loss."
#
# HONEST FRAME (from the sourcing pass, VERIFICATION.md 2026-08-06):
# - RRB is not zero recognition of WEAR: replacement-in-kind was expensed, so
#   steady-state physical consumption flowed through income. What RRB never
#   recognizes is the VINTAGE'S CAPITALIZED COST — obsolescence, deferred
#   maintenance, mispricing (Brief, JAR 1965). This measure is about the cost.
# - Railroad receivership wrote down claims, not assets (fixed charges -29%,
#   capitalization +13%, Ripley 1915): the asset account outlived the event.
# - Telecom booked lives were themselves overstated ex post: WorldCom fiber
#   40y -> 25y restated, ocean cable 40y -> ~11y contract life; WilTel
#   fresh-start cut the weighted-average life 21y -> 15y. "As booked" is the
#   era's own clock, not reality's.
# Sources for every share/life: README.md + VERIFICATION.md (EDGAR verbatim,
# ICC/Fishlow/Ulmer, report Appendix A).

eras = {
    # US railroads 1865-1900, era practice: no depreciation on anything pre-1907;
    # road ~92% / equipment ~8% (ICC 1902-08; Fishlow 1869-99: 6.4-9.9% equipment).
    'Railroads 1865-1900 (era RRB accounting)': {
        'road+structures (~92%)': (0.92, None),
        'equipment (~8%)':        (0.08, None),
    },
    # Same mix under the schedule the ICC eventually prescribed (equipment
    # composite 3.5%/yr ~= 28.6y in 1935; road composite 0.86%/yr ~= 116y in
    # 1943/1917 terms; track structures only 1983).
    'Railroads (eventual ICC schedule, 1935/1943)': {
        'road+structures': (0.92, 116.0),
        'equipment':       (0.08, 28.6),
    },
    # Telecom ILEC as booked: FCC SOCC end-2001 plant stock (TPIS $355.4B) with
    # FCC-prescribed lives (FCC 99-397 App. B; DA 03-2738): cable & wire 41.6%
    # at ~25y blend (metallic 20-26, fiber 25-30, conduit 50), buildings 7.2%
    # at 47y, land 0.4% never, electronics 44.0% at ~12y, computers/other 6.8%
    # at 6y. Cross-check: implied composite book life (TPIS / D&A) = 14.1y.
    'Telecom ILEC (SOCC stock, FCC lives)': {
        'cable & wire':     (0.416, 25.0),
        'buildings':        (0.072, 47.0),
        'land':             (0.004, None),
        'electronics':      (0.440, 12.0),
        'computers/other':  (0.068, 6.0),
    },
    # Telecom long-haul as booked: Williams FY2000 gross plant ex-CIP (the only
    # carrier splitting fiber from electronics), shares renormalized over the
    # classed 90.4%: fiber+ROW 48.5 @ 25-30y (mid 27.5), optronics 28.8 @ 7-10y
    # (mid 8.5), buildings 9.1 @ 30y, computers+furniture 4.0 @ ~3.5y, other
    # 9.6 assigned the plant-wide average ~15y. WorldCom corroborates the tilt:
    # ~70% of gross plant in classes with 40-45y maxima.
    'Telecom 1996-2002 (as booked, Williams mix)': {
        'fiber + right-of-way': (0.485 / 0.904, 27.5),
        'optronics':            (0.288 / 0.904, 8.5),
        'buildings':            (0.091 / 0.904, 30.0),
        'computers/furniture':  (0.040 / 0.904, 3.5),
    },
    # The carrier's own summary number: WilTel fresh-start disclosure, weighted
    # average life 21y pre-crash (cut to 15y at emergence, Oct 2002).
    'Telecom (WilTel disclosed 21y wtd avg)': {
        'all plant': (1.0, 21.0),
    },
    # AI 2023-2026: report Appendix A mix (CreditSights AI shares; hyperscaler
    # disclosures; 5y IT life corroborated by Amazon's Jan-2025 reversion).
    'AI 2023-2026': {
        'IT equipment':        (0.62, 5.0),
        'power/cooling infra': (0.23, 15.0),
        'shell+land':          (0.15, 30.0),
    },
}

def recognized(mix, t):
    return sum(sh * min(t / life, 1.0) for sh, life in mix.values() if life is not None)

print(f"{'Era':<48} {'dep %/yr':>9} {'half-life':>15} {'unscheduled':>12}")
for name, mix in eras.items():
    rate = sum(sh / life for sh, life in mix.values() if life is not None)
    nodep = sum(sh for sh, life in mix.values() if life is None)
    if recognized(mix, 1000.0) >= 0.5:
        lo, hi = 0.0, 1000.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if recognized(mix, mid) < 0.5:
                lo = mid
            else:
                hi = mid
        hl = f"{hi:6.1f} yr"
    else:
        hl = "never (events)"
    print(f"{name:<48} {rate*100:8.1f}% {hl:>15} {nodep*100:10.0f}%")

print("""
Reading: the share of a capital vintage's cost the era's own books amortize, and
how fast. Railroads stored ~100% of vintage cost off the income statement (wear
flowed through renewals expense; cost recognition waited 80-120 years for ICC
schedules, and even receivership wrote down claims, not assets). Telecom booked
a ~8-10yr half-life clock that ex post was rigged slow (fiber 40->25, WA 21->15;
GX plant 17.9% depreciated when impaired 74%);
recognition of the mispricing arrived as one 2001-04 impairment/restatement wave.
AI runs a 3.5yr half-life on the era's OWN schedule - the first buildout whose
accounting clock is faster than its bubble: mispricing cannot be stored, it
surfaces as continuous P&L drag within one product cycle.""")
