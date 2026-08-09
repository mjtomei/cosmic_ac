# AI capital stock model, mid-2026. All figures $B, global, AI-attributable.
# Vintage gross capex (low, central, high). Sources: big-4 capex 226(2024)->410(2025)->725 guided(2026),
# AI share ~50-55% (2024) rising to ~75% (2026, CreditSights); plus Oracle/neoclouds/xAI/China/sovereign.
vintages = {                      # (low, central, high), age in years at mid-2026
    2023.0: ((45, 65, 85), 3.0),
    2024.0: ((150, 185, 215), 2.0),
    2025.0: ((400, 460, 500), 1.0),
    2026.5: ((310, 370, 420), 0.25),   # H1 2026
}
# Asset mix & straight-line lives
mix = {'IT': (0.62, 5.0), 'infra': (0.23, 15.0), 'shell': (0.15, 30.0)}

for case_idx, case in enumerate(['low', 'central', 'high']):
    gross = net = 0.0
    net_by_class = {k: 0.0 for k in mix}
    for (vals, age) in vintages.values():
        g = vals[case_idx]
        gross += g
        for k, (share, life) in mix.items():
            remaining = max(0.0, 1 - age / life)
            net_by_class[k] += g * share * remaining
    net = sum(net_by_class.values())
    # Add-ons (net): upstream fab PP&E AI share; power/grid; model IP at cost (ex-compute to avoid double count)
    addons = {'low': (105, 45, 35), 'central': (125, 65, 55), 'high': (145, 85, 75)}[case]
    total_net = net + sum(addons)
    # Competitive-cost adjustment: accel+networking ~75% of IT stock, competitive price ~45% of paid;
    # other IT ~25%, competitive ~75% of paid (memory scarcity pricing); infra/shell at cost.
    it = net_by_class['IT']
    it_comp = it * (0.75 * 0.45 + 0.25 * 0.75)
    comp_net = it_comp + net_by_class['infra'] + net_by_class['shell'] + sum(addons)
    print(f"{case:>8}: gross={gross:6.0f}  net_dc={net:6.0f}  (IT={it:5.0f} infra={net_by_class['infra']:5.0f} shell={net_by_class['shell']:5.0f})")
    print(f"          total_net_stock={total_net:6.0f}   competitive_cost_stock={comp_net:6.0f}")

print()
# Rent decomposition. Market value gain attributable to AI (GS: $27T total, not all AI)
for mv in [14000, 18000, 27000]:
    stock = 1180  # central total net
    rentcap = mv - stock
    print(f"MV_AI={mv/1000:.0f}T  rent_capitalization={rentcap/1000:5.1f}T  "
          f"req_flow: grow3%@8%={rentcap*0.05/1000:5.2f}T/yr  flat@8%={rentcap*0.08/1000:5.2f}T/yr  "
          f"decay10%@8%={rentcap*0.18/1000:5.2f}T/yr")
