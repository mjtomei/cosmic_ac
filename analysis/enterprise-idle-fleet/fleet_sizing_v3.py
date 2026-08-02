#!/usr/bin/env python3
"""
Fleet sizing v3 — rebuilt on the measured installed mix, not an Apple stand-in.

WHAT CHANGED FROM v1/v2
 The per-device throughput assumption, which dominates every downstream figure,
 was 2.9 FP32 TFLOPS — a *measured Apple M4 GPU* applied to a fleet that is
 ~91% not Apple (Gartner 2025: Apple 9.2% of worldwide PC units). The
 installed-mix sweep (2026-08-02) replaces it.

WHAT THE VOLUME BUSINESS SKU ACTUALLY IS (VERIFIED from 9 Lenovo PSREF official
spec PDFs, fetched 2026-08-02 — Dell 403, HP 503, so single-vendor)
 - ThinkPad T14/L14 Gen 5-6 (volume laptop): graphics options are ALL
   integrated. No discrete GPU on the spec sheet at all.
 - ThinkCentre M70q / M75q Gen 5 (volume tiny/SFF desktop): all integrated
   (Intel UHD 710/730/770; AMD Radeon 740M/760M/780M).
 - Only the M70t TOWER offers discrete (RTX 3050/5050, RX 6600 LE, Arc A310).
 - Volume CPU tier is low-power: T-suffix i3/i5 desktops, U-series Core Ultra
   laptops — not performance parts.
 - Lenovo's own note: Arc iGPU needs 16GB DUAL-CHANNEL memory "otherwise it
   will function as Intel Graphics" — single-channel fleets are derated below
   even these figures.

C1 Per-device PEAK FP32, weighted: ~0.85 TFLOPS (range 0.6-1.2).
   Desktops 57.2% at ~0.5-0.8 (UHD 710/730/770 = 0.33-0.79 TFLOPS);
   laptops 42.8% at ~0.42-1.8 (UHD 620 through Iris Xe; Arc only on H-series).
   DERIVED — per-SKU rates from published tables, weights are judgement.
C2 PEAK-vs-SUSTAINED derate: 0.5-0.7. An iGPU shares the CPU's DDR bus
   (dual-channel DDR5-5600 ~= 89.6 GB/s) and is memory-bound far below the
   arithmetic intensity peak rates assume. NOT MEASURED — no sustained iGPU
   benchmark was fetchable. Using 0.6.
   NOTE THE ASYMMETRY: 2.9 for the M4 was SUSTAINED-MEASURED; 0.85 here is
   PEAK. Comparing them already flatters the iGPU, so the true gap is wider.
C3 Fleet available device-hours: 679B/yr (v2 basis: powered hours x unused
   cycles x user reservation). Unchanged.
C4 Optimised configurations, priced (spec-ladder sweep, same day):
   RTX A2000 12GB  8.0 TFLOPS FP32,  70W, ~$525  <- fits existing SFF chassis
   RTX 5070       30.9 TFLOPS FP32, 250W,  $549
   RTX 5090      104.8 TFLOPS FP32, 575W, $1,999
   Apple ladder is FLAT in $/TFLOPS ($276-324) so "buy a bigger Mac" is
   dominated; a card in an existing desktop is ~16x better per FP32 dollar.
C5 Energy 13.79 c/kWh commercial (EIA EPM T5.3). Base business PC 65W.
C6 Justified budget from idle revenue: $355-1,419/device/yr (v2).

STILL PENDING (two sweeps in flight): observed market rates per machine-hour
(today's denomination) and FP16/FP8/NPU throughput (the fungible-compute
denomination). This file deliberately reports CAPACITY, not dollars, because
the dollar anchor was shown to be inflated (EC2 Mac embeds a macOS scarcity
rent) and its replacement is not yet in hand.
"""

DEV_HOURS = 679e9          # C3
PEAK_LO, PEAK_MID, PEAK_HI = 0.6, 0.85, 1.2   # C1
DERATE = 0.6               # C2
RATE = 0.1379              # C5
HOURS_YR = 8760
BASE_W = 65

print("=== 1. Fleet capacity on the corrected baseline ===")
print(f"{'per-device FP32':>22s} {'EFLOPS':>10s}  {'vs v1 (2.9 TF)':>16s}")
for label, tf in (("v1 assumption 2.9", 2.9),
                  ("peak, low 0.6", PEAK_LO),
                  ("peak, central 0.85", PEAK_MID),
                  ("peak, high 1.2", PEAK_HI),
                  ("SUSTAINED central", PEAK_MID*DERATE)):
    ef = DEV_HOURS * tf / HOURS_YR / 1e6   # EFLOPS of continuous capacity
    print(f"{label:>22s} {ef:10.1f}  {tf/2.9:15.2f}x")

print(f"\n  -> the corrected sustained central figure is {PEAK_MID*DERATE:.2f} TFLOPS/device,")
print(f"     {2.9/(PEAK_MID*DERATE):.1f}x below the v1 assumption. Every v1/v2 dollar")
print(f"     figure denominated on compute should be divided by ~{2.9/(PEAK_MID*DERATE):.0f}.")

print("\n=== 2. What optimisation actually buys, per device ===")
print(f"{'config':28s} {'FP32':>8s} {'x base':>7s} {'card $':>8s} {'W':>5s} {'energy/yr':>10s} {'net vs budget':>14s}")
base_tf = PEAK_MID * DERATE
budget_lo, budget_hi = 355, 1419      # C6
for name, tf, price, watts in (("business PC as-is", base_tf, 0, BASE_W),
                               ("+ RTX A2000 (SFF-safe)", 8.0, 525, BASE_W+70),
                               ("+ RTX 5070", 30.9, 549, BASE_W+250),
                               ("+ RTX 5090", 104.8, 1999, BASE_W+575)):
    e = watts/1000*RATE*HOURS_YR
    print(f"{name:28s} {tf:8.2f} {tf/base_tf:6.0f}x {price:8d} {watts:5d} {e:10.0f} "
          f"{budget_lo-e:6.0f}/{budget_hi-e:<7.0f}")

print("""
  -> The A2000 rung is the efficient one: ~16x the capability of the base
     machine, fits an existing small-form-factor chassis, and leaves the
     revenue budget intact. The 5090 rung consumes $773/yr of the $355-1,419
     it was bought with -- at the low end of the budget it is loss-making
     before any other cost.""")

print("=== 3. Fleet capacity if the fleet were optimised ===")
for name, tf in (("as-is (sustained)", base_tf), ("+A2000 fleetwide", 8.0), ("+5070 fleetwide", 30.9)):
    ef = DEV_HOURS * tf / HOURS_YR / 1e6
    print(f"  {name:20s} {ef:8.1f} EFLOPS continuous-equivalent")
print("""
  (Fleetwide upgrade is a thought experiment, not a forecast: it assumes every
   machine takes a card, which the SKU data says is impossible for laptops and
   tiny/SFF desktops -- only the TOWER chassis accepts one, and the tower share
   of commercial desktop volume was NOT verified. Treat as an upper bound on
   the optimised case.)""")

import csv, pathlib
rows = []
for label, tf in (("v1 assumption", 2.9), ("peak low", PEAK_LO), ("peak central", PEAK_MID),
                  ("peak high", PEAK_HI), ("sustained central", PEAK_MID*DERATE),
                  ("optimised A2000", 8.0), ("optimised 5070", 30.9)):
    rows.append({"basis": label, "tflops_per_device": tf,
                 "fleet_eflops_continuous": DEV_HOURS*tf/HOURS_YR/1e6,
                 "ratio_to_v1": tf/2.9})
out = pathlib.Path(__file__).with_name("fleet_sizing_v3.csv")
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {out.name}")
