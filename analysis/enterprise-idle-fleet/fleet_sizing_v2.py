#!/usr/bin/env python3
"""
Fleet sizing, extended: daytime sharing, and hardware chosen with resale in mind.

v1 (fleet_sizing.py) counted only hours OUTSIDE working time. Two corrections,
both raised by Matthew 2026-08-02:

 (1) DAYTIME SHARING. "Work-active" is not "CPU-saturated." A person editing a
     document consumes a few percent of a modern machine. The correct measure of
     availability is (hours powered and connected) x (fraction of cycles unused),
     not (hours nobody is at the keyboard). This is what cycle-stealing systems
     have always harvested; HTCondor's default policy is keyboard-idle plus low
     load average, i.e. it yields to the user rather than waiting for them to
     leave.

 (2) HARDWARE CHOSEN FOR RESALE. Today a business specifies a machine for one
     employee's workload; surplus capacity is pure waste, so the rational buy is
     modest. If idle capacity earns revenue, surplus stops being waste and the
     optimal specification moves up. This is the demand-side twin of the paper's
     financing instrument (S8/Omerta: the device sells its own time).

NEW ASSUMPTIONS (v1's A1-A9 still apply)
 B1 CPU idleness during powered hours: 97.9% measured across a managed
    institutional fleet (Domingues, Marques & Silva, ICPPW 2005, 169 machines,
    77 days, 583,653 samples). University teaching labs, so an upper bound for
    knowledge work. Swept 85-98% below; 90% used as the default.
 B2 Powered hours under a sharing policy: desktops 24h/day; laptops 16h/day
    (assumed lid-open or docked window). ASSUMPTION, not measured.
 B3 User-priority reservation: 10% of cycles held back so the interactive user
    never contends. ASSUMPTION; HTCondor-style preemption is the mechanism.
 B4 Device depreciation life: 3-5 years (Dell 10-K FY2026 PP&E policy). Used
    to convert annual idle revenue into justified up-front hardware spend.
 B5 Compute-per-dollar at the margin: NOT ASSUMED. We report the justified
    spend and let the multiplier be swept, because $/TFLOPS for an incremental
    GPU or SoC tier is a moving, unverified figure. What is defensible: a
    business PC with integrated graphics sits at the WORST end of
    compute-per-dollar, so the multiplier is bounded well above 1.
"""

DESKTOPS, LAPTOPS = 63.85e6, 47.76e6
DOCKED = 0.20
REV_LO, REV_HI = 0.05, 0.20
HOURS_YR = 8760
CPU_IDLE = 0.90          # B1, conservative vs the measured 97.9%
USER_RESERVE = 0.10      # B3
DEPREC = 4               # B4, midpoint

def avail(devices, powered_frac):
    """device-hours/yr of genuinely available capacity"""
    return devices * HOURS_YR * powered_frac * CPU_IDLE * (1 - USER_RESERVE)

# v1 baselines, for comparison (hours outside work only)
v1_A = (DESKTOPS + LAPTOPS*DOCKED) * HOURS_YR * 0.76
v1_AB = v1_A + LAPTOPS*(1-DOCKED) * HOURS_YR * 0.85

# v2: powered-hours x unused-cycles
d_prem = avail(DESKTOPS, 24/24)                      # desktops, always on
l_prem = avail(LAPTOPS*DOCKED, 16/24)                # docked laptops
l_home = avail(LAPTOPS*(1-DOCKED), 16/24)            # at-home laptops
v2_A, v2_AB = d_prem + l_prem, d_prem + l_prem + l_home

print("=== Effect of counting daytime cycles, not just after-hours ===")
for name, v1, v2 in (("Tier A", v1_A, v2_A), ("Tier A+B", v1_AB, v2_AB)):
    print(f"{name:9s} v1 {v1/1e9:6.0f}B dev-h  ->  v2 {v2/1e9:6.0f}B dev-h "
          f"({v2/v1:.2f}x)   value ${v2*REV_LO/1e9:5.0f}-{v2*REV_HI/1e9:.0f}bn/yr")

print("\nSensitivity on B1 (unused-cycle fraction), Tier A+B:")
for ci in (0.85, 0.90, 0.95, 0.979):
    tot = (DESKTOPS*HOURS_YR*1.0 + LAPTOPS*HOURS_YR*(16/24)) * ci * (1-USER_RESERVE)
    print(f"  {ci:.1%} idle -> {tot/1e9:5.0f}B dev-h, "
          f"${tot*REV_LO/1e9:5.0f}-{tot*REV_HI/1e9:.0f}bn/yr")

print("\n=== What a business could justify spending per device ===")
print("(annual idle revenue x depreciation life = up-front hardware budget)")
for dev_h in (avail(1, 24/24), avail(1, 16/24)):
    lo, hi = dev_h*REV_LO, dev_h*REV_HI
    print(f"  {dev_h:6.0f} available h/yr -> ${lo:6.0f}-{hi:,.0f}/yr "
          f"-> ${lo*DEPREC:6.0f}-{hi*DEPREC:,.0f} over {DEPREC}y")

print("\nAgainst a typical business PC price of $600-1,500, that revenue is")
print("of the same order as the DEVICE ITSELF -- so the constraint on")
print("specification stops being the employee's workload.")

print("\n=== If specification rises: fleet output at multiplier M ===")
print("(M = compute per device relative to today's mix; not a price model)")
for M in (1, 2, 3, 5):
    print(f"  M={M}x -> Tier A+B effective capacity {v2_AB*M/1e9:7.0f}B device-h-equivalents/yr")

print("\nNOTE: the value column does NOT scale linearly with M. Price per")
print("device-hour would fall as supply rises; the $/hr references here are")
print("current spot-like prices for scarce compute. Treat M as a capacity")
print("statement, not a revenue statement.")

import csv, pathlib
rows = [
    {"scenario": "v1 Tier A (after-hours only)", "device_hours_yr": v1_A},
    {"scenario": "v1 Tier A+B (after-hours only)", "device_hours_yr": v1_AB},
    {"scenario": "v2 Tier A (powered x unused cycles)", "device_hours_yr": v2_A},
    {"scenario": "v2 Tier A+B (powered x unused cycles)", "device_hours_yr": v2_AB},
]
for r in rows:
    r["value_lo_usd"] = r["device_hours_yr"]*REV_LO
    r["value_hi_usd"] = r["device_hours_yr"]*REV_HI
out = pathlib.Path(__file__).with_name("fleet_sizing_v2.csv")
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
    for r in rows: w.writerow(r)
print(f"\nwrote {out.name}")
