# Convert required economic rent -> required external revenue -> % of GDP
# World GDP: ~$118T (2026), ~$135T (2030 est, ~5%/yr nominal). US GDP ~$30.5T -> ~$35T.
WGDP26, WGDP30, USGDP26, USGDP30 = 118e3, 135e3, 30.5e3, 35e3  # $B

# Required after-tax profit (rent + normal 8% return on invested capital), $B/yr, ~2030 window
# Invested capital path: ~$1.2T (2026) -> ~$5T net by 2030 (GS big-4 $5.3T capex 25-30 + others - dep)
K30 = 5000.0
cases = {
    'growing rents (3%g)': 840 + 0.08*K30,     # rent grows; normal return on 2030 stock
    'flat perpetuity':     1350 + 0.08*K30,
    'decaying rents (10%)': 3030 + 0.08*K30,   # initial-year requirement
}
margins = [0.12, 0.20, 0.30]   # consolidated net margin on external revenue

print("Required external revenue ($T/yr) and % of world GDP (2030) | % of US GDP:")
for name, prof in cases.items():
    row = []
    for m in margins:
        rev = prof/m
        row.append(f"m={int(m*100)}%: {rev/1000:4.1f}T ({rev/WGDP30*100:4.1f}% W / {rev/USGDP30*100:4.1f}% US)")
    print(f"  {name:22s} profit={prof/1000:.2f}T -> " + " | ".join(row))

# Breakeven floor: revenue to make the buildout NPV-neutral (no rents) on 2030 stock
gross30 = K30/0.77                      # net/gross ratio from vintage model ~0.77
dep = gross30*(0.62/5 + 0.23/15 + 0.15/30)
opex = 275.0                            # power + operations, central
normal = 0.08*K30*1.2                   # grossed up ~20% for tax
floor = dep + opex + normal
print(f"\nBreakeven floor: dep={dep/1000:.2f}T + opex={opex/1000:.2f}T + return={normal/1000:.2f}T"
      f" = {floor/1000:.2f}T/yr = {floor/WGDP30*100:.1f}% of world GDP")

# Context anchors
print(f"\nAnchors: global IT spend ~5.8T ({5800/WGDP26*100:.1f}% WGDP);"
      f" global software+cloud ~2.0T ({2000/WGDP26*100:.1f}%);"
      f" US corporate profits ~3.9T ({3900/USGDP26*100:.1f}% US GDP)")
# Labor-substitution funding requirement: R = capture_share * labor_cost_displaced
for R in [4000, 5500, 7000]:
    for cap in [0.3]:
        L = R/cap
        print(f"  R={R/1000:.1f}T at {int(cap*100)}% capture -> {L/1000:.1f}T labor cost addressed"
              f" = {L/(0.53*WGDP30)*100:.0f}% of global labor income")
