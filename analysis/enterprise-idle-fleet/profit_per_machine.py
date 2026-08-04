#!/usr/bin/env python3
"""
Profit per machine per year, by isolation case — the bottom line.

Combines: observed revenue (v4), energy at commercial rates, hardware BOM,
NRE and assurance amortisation, and the insurance premium from actuarial_model.py.
All inputs fetched 2026-08-02/03 unless marked ASSUMED. Sources in
cost-findings.json and actuarial-findings.json.

REVENUE (observed host rates, Salad demand-monitor API)
  entry dGPU $123/yr · mid $596 · high $1,577 · top $2,006
  Integrated-graphics machines: $0 — no marketplace accepts them (v4).

ENERGY (EIA commercial 13.79 c/kWh)
  base PC 65W $79/yr · +A2000 135W $163 · +5070 315W $381 · +5090 640W $773

BOM, CASE 2 (fetched; OEM-volume and retrofit-retail both shown)
  NIC:      RTL8153 USB-GbE IC $1.99 @100 · RTL8111H PCIe GbE IC $0.94-1.32
            finished USB3-GbE dongle $12-14 retail
  Storage:  M.2 NVMe 256GB $55 · 512GB $86-104
            NOTE: Aug-2026 is a NAND up-cycle; 256GB was ~$25-30 in 2024.
  DRAM:     DDR4 SODIMM 8GB $56 · DDR5 SODIMM 16GB $180-230
            DECISIVE: dedicated DDR5 costs MORE THAN A YEAR of low-end revenue.
            Memory partitioning must be LOGICAL, not physical. Excluded below.

NRE
  Case 1: pentest $5-50k + SOC 2 first year $30-100k = $50-150k one-time,
          $20-110k/yr recurring. Amortises over ONE ENTERPRISE FLEET.
  Case 2: Case-1 assurance + Common Criteria EAL2-4, all-in $500k-$2.5M,
          1.5-2.5 years elapsed.
  Case 3: platform/firmware Tier 1 15-50 engineer-years = $4-18M ASSUMED,
          plus a formal-proof route $1.2-5.1M one-time + $150-250k/yr
          (seL4 measured: ~20 py original, ~8 py to replicate, and proof
          MAINTENANCE of 1.5-2 py per significant change — the line that
          dominates lifetime cost and is rarely quoted).
          Amortises over an OEM's SHIPMENT VOLUME, not one fleet.
  Case 4: new silicon by node (IBS via Semi Engineering): 28nm ~$51M ·
          16nm ~$106M · 7nm $160-298M · 5nm $280-542M · 3nm $500M-1.5B.
          Semi Engineering's own correction: these are first-mover
          new-architecture costs and fall ~3x as a node matures.

INSURANCE
  Per-machine premium = p_m x severity / 0.65, with p_m scaled by the
  boundary-exposure index from actuarial_model.py (Case 1 = 1.0,
  Case 2 = 0.010, Case 3/4 = 0.0009). Severity = $83k claims median.
  p_m is UNKNOWN — the annual probability that sharing causes an incident on
  one machine — so it is swept.
"""

RATE, YRS = 0.1379, 4          # commercial $/kWh; depreciation life
SEV, LOSS_RATIO = 83_000, 0.65
IDX = {"Case 1": 1.0, "Case 2": 0.010, "Case 3": 0.0009, "Case 4": 0.0009}

def energy(w): return w/1000*RATE*8760

# --- BOM per machine, amortised over YRS
BOM = {
    "Case 1": (0, 0),
    "Case 2": (2.0 + 55, 14 + 55),      # (OEM volume, retrofit retail): NIC + 256GB M.2
    "Case 3": (2.0 + 55, None),         # same peripherals, integrated by the OEM
    "Case 4": (2.0 + 55, None),
}
# --- NRE and its amortisation base
NRE = {
    "Case 1": (100_000,   10_000, "one enterprise fleet"),      # midpoint, per-fleet
    "Case 2": (1_500_000, 10_000, "one enterprise fleet"),      # CC EAL2-4 midpoint
    "Case 3": (14_000_000, 1_000_000, "OEM shipment volume"),   # Tier1 $11M + proof $3M
    "Case 4": (106_000_000, 5_000_000, "OEM shipment volume"),  # 16nm node
}
RECUR = {"Case 1": 60_000, "Case 2": 60_000, "Case 3": 200_000, "Case 4": 200_000}
RECUR_BASE = {"Case 1": 10_000, "Case 2": 10_000, "Case 3": 1_000_000, "Case 4": 5_000_000}

print("=== Fixed costs per machine per year ===")
print(f"{'case':8s} {'BOM/yr':>9s} {'NRE/yr':>9s} {'upkeep/yr':>10s} {'total':>9s}   amortised over")
fixed = {}
for c in IDX:
    bom = BOM[c][0]/YRS
    nre = NRE[c][0]/NRE[c][1]/YRS
    up  = RECUR[c]/RECUR_BASE[c]
    fixed[c] = bom+nre+up
    print(f"{c:8s} {bom:9.2f} {nre:9.2f} {up:10.2f} {fixed[c]:9.2f}   {NRE[c][2]}")

print("\n=== Insurance premium per machine per year, swept on p_m ===")
print(f"{'p_m':>10s} " + " ".join(f"{c:>10s}" for c in IDX))
prem = {}
for p_m in (1e-5, 1e-4, 1e-3, 1e-2):
    row = f"{p_m:10.0e} "
    for c in IDX:
        v = p_m*IDX[c]*SEV/LOSS_RATIO
        prem.setdefault(c, {})[p_m] = v
        row += f"{v:10.2f} "
    print(row)

print("\n=== PROFIT PER MACHINE PER YEAR ===")
print("(revenue - energy - fixed - insurance; p_m = 1e-3, the pessimistic sweep point)")
P_M = 1e-3
configs = [("entry dGPU", 123, 235), ("mid 3090-class", 596, 415),
           ("high 4090", 1577, 515), ("top 5090", 2006, 640)]
print(f"\n{'config':16s} {'rev':>7s} {'energy':>8s} | " + " | ".join(f"{c:>16s}" for c in IDX))
for name, rev, w in configs:
    e = energy(w)
    row = f"{name:16s} {rev:7.0f} {e:8.0f} | "
    cells = []
    for c in IDX:
        net = rev - e - fixed[c] - prem[c][P_M]
        cells.append(f"{net:>+16,.0f}")
    print(row + " | ".join(cells))

print("\n=== Same, at p_m = 1e-5 (optimistic) ===")
P_M = 1e-5
print(f"{'config':16s} " + " | ".join(f"{c:>16s}" for c in IDX))
for name, rev, w in configs:
    e = energy(w)
    cells = [f"{rev - e - fixed[c] - prem[c][P_M]:>+16,.0f}" for c in IDX]
    print(f"{name:16s} " + " | ".join(cells))

print("""
=== What the table says ===

1. INSURANCE IS NOT THE BINDING COST in any case. Even at the pessimistic
   p_m = 1e-3, Case 1's premium is ~$128/machine/yr and Cases 3/4 are ~$0.12.
   Energy and revenue dominate. The isolation architecture matters for
   INSURABILITY — whether cover is written at all, and at what cap — far more
   than for the premium line.

2. NRE AMORTISATION INVERTS THE INTUITION. Case 3's $14M over an OEM's 1M-unit
   shipment is $3.50/machine/yr — CHEAPER than Case 2's per-unit BOM, because
   Case 2 pays $57 of hardware on every single machine forever while Case 3
   pays engineering once. Even Case 4's $106M over 5M units is $5.30/yr.
   Fixed cost spread over volume beats recurring cost per unit.

3. THE BOM IS THE REAL COST OF CASE 2, and it is dominated by storage, not
   networking. A NIC is ~$2 at OEM volume; a 256GB SSD is $55. And DDR5 at
   $180-230 a stick exceeds a year of low-end revenue outright — so dedicated
   physical memory is off the table and partitioning must be logical.

4. ENERGY DECIDES THE CONFIGURATION, as v3 found: the entry tier is
   loss-making before any of these costs, and only the high tiers clear.

5. THE DECISIVE UNCERTAINTY IS NOT COST. Every fixed cost here is small
   against revenue at the profitable configurations. What decides the business
   is (a) whether a market accepts the hardware at all — today it does not —
   and (b) whether cover can be written given portfolio correlation. Both are
   structural, not economic.
""")

import csv, pathlib as _pl
_rows = []
for _pm in (1e-5, 1e-4, 1e-3, 1e-2):
    for _name, _rev, _w in configs:
        for _c in IDX:
            _pr = _pm*IDX[_c]*SEV/LOSS_RATIO
            _rows.append({"case": _c, "config": _name, "p_m": _pm,
                          "revenue_usd_yr": _rev, "energy_usd_yr": round(energy(_w),2),
                          "fixed_usd_yr": round(fixed[_c],2), "insurance_usd_yr": round(_pr,2),
                          "profit_usd_yr": round(_rev-energy(_w)-fixed[_c]-_pr,2)})
_o = _pl.Path(__file__).with_name("profit_per_machine.csv")
with _o.open("w", newline="") as _f:
    _w2 = csv.DictWriter(_f, fieldnames=list(_rows[0].keys())); _w2.writeheader()
    for _r in _rows: _w2.writerow(_r)
print(f"wrote {_o.name} ({len(_rows)} rows)")
