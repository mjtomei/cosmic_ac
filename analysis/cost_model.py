#!/usr/bin/env python3
"""Consumer-device vs datacenter compute cost model.

Produces consumer_vs_datacenter_cost.csv. Two cases, per the review:
  A. HARDWARE EXCLUDED  - the stranded-compute play: the device was bought for
     other reasons; only marginal cost (electricity + overhead) counts.
  B. HARDWARE INCLUDED  - the new-market play: the device is bought to serve;
     capital amortizes over its service life and only sold hours carry it.

Every number is either sourced (SOURCES below) or an assumption (ASSUMPTIONS).
Run: python3 cost_model.py   (writes the csv next to itself)
"""
import csv, pathlib

# ---------------------------------------------------------------- SOURCES ---
# S1  Device price: Apple Mac mini M4 base MSRP $599 (Apple price list, 2024-).
# S2  Device power: Mac mini M4 ~4 W idle, ~40 W max (Apple support, "Mac mini
#     power consumption"; 2024 M4 figures).
# S3  Electricity: ~$0.15/kWh (US EIA residential average, mid-2025 ~15-17c).
# S4  Datacenter anchor: ~$0.50/hr datacenter vs ~$0.08/hr idle-home marginal
#     (Omerta reliability-market simulation, omerta_protocol
#     plans/economic-analysis/ECONOMIC_ANALYSIS.md).
# S5  Spot discount: interruptible capacity trades 60-90% below on-demand;
#     realized savings 27-84% (Wu et al., NSDI 2024, "Can't Be Late").
# S6  Mac-class market prices: EC2 Mac dedicated $0.65/hr (24-hr min, AWS price
#     list mid-2026); GitHub-hosted macOS runner $0.062/min = $3.72/hr (GitHub
#     Actions pricing, mid-2026). Both from the paper's Table A2 pass.
# ------------------------------------------------------------ ASSUMPTIONS ---
# A1  Service life 4 years, straight-line, zero residual value.
# A2  Serving power draw 30 W average (below S2 max; inference/CI mix).
# A3  Platform/network overhead: +20% on marginal cost (bandwidth, wear,
#     coordination). Assumption, not measured.
# A4  Utilization = fraction of all hours actually SOLD. Scenarios 10/30/50%.
#     (Prior lab experience suggests low; 30% is the working case.)
# A5  Revenue scenarios = reference on-demand price x (1 - spot discount),
#     with discounts 60/75/90% (S5), applied to two references:
#     generic datacenter $0.50/hr (S4) and EC2 Mac $0.65/hr (S6).

PRICE = 599.0            # S1
LIFE_HOURS = 4 * 8760    # A1
POWER_W = 30.0           # A2
KWH = 0.15               # S3
OVERHEAD = 1.20          # A3

marginal = POWER_W / 1000 * KWH * OVERHEAD   # $/hr while serving

rows = []
for util in (0.10, 0.30, 0.50):              # A4
    cost_excl = marginal                                  # case A
    cost_incl = PRICE / (LIFE_HOURS * util) + marginal    # case B
    for ref_name, ref in (("datacenter_0.50", 0.50), ("ec2_mac_0.65", 0.65)):  # A5
        for disc in (0.60, 0.75, 0.90):
            rev = ref * (1 - disc)
            rows.append({
                "utilization": util,
                "reference_price": ref_name,
                "spot_discount": disc,
                "revenue_per_hr": round(rev, 4),
                "cost_per_sold_hr_hw_excluded": round(cost_excl, 4),
                "cost_per_sold_hr_hw_included": round(cost_incl, 4),
                "margin_hw_excluded": round(rev - cost_excl, 4),
                "margin_hw_included": round(rev - cost_incl, 4),
            })

out = pathlib.Path(__file__).parent / "consumer_vs_datacenter_cost.csv"
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
print(f"wrote {out} ({len(rows)} rows)")
print(f"marginal cost (hw excluded): ${marginal:.4f}/hr")
for util in (0.10, 0.30, 0.50):
    print(f"hw included @ {util:.0%} util: ${PRICE/(LIFE_HOURS*util)+marginal:.4f}/hr")
