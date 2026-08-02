#!/usr/bin/env python3
"""
Sizing the idle business-PC fleet, with and without a fleet-policy change.

Scope: US commercial buildings only (the one place with a weighted device census).
Global figures would be several times larger; no fetchable global commercial
installed-base number exists, so we do not extrapolate.

ASSUMPTIONS AND SOURCES  (every input below is either fetched or flagged)
 A1 Device counts: 63.85M desktops, 47.76M laptops in US commercial buildings.
    EIA CBECS 2018 public-use microdata, FINALWT-weighted (our computation).
    2018 vintage and buildings >=1,000 sq ft only, so this UNDERCOUNTS today.
 A2 Desktops already left on outside hours: 64% (turn-off rate 36%, n=1,453).
    Roberson/Webber et al., LBNL-53729 (2004), doi:10.2172/821675.
    WEAKEST INPUT: 2004 data, predates modern sleep defaults. Treat as the
    no-policy-change case only; a policy change makes it moot.
 A3 Idle share of the week, on-premises: 76% (168h - 5x8.21h work-active).
    BLS ATUS 2025 Table 6, full-time at-workplace hours.
 A4 Idle share, at-home laptop: 79% on a used day (24 - 5.10h), 100% unopened.
    BLS ATUS 2025 Table 6. We use a blended 85% for the at-home population.
 A5 Docked-laptop share staying on premises overnight: 20% (80% of 107 docks
    empty). LBNL-53729. VERY uncertain, n=107, 2004; swept 10-40% below.
 A6 At-home laptop share: laptops not on premises = 1 - A5, of the laptop base.
 A7 Per-device sustained throughput: 2.9 FP32 TFLOPS (Apple M4 GPU, measured
    via MPS). Hubner et al., IPDPSW 2025, arXiv:2502.05317. THIS IS THE
    LOOSEST ASSUMPTION: Apple is ~9% of PC units, and a typical business
    desktop with integrated graphics is materially below this. Swept 0.5-2.9.
 A8 Revenue per device-hour: $0.05-0.20, being a $0.50/hr datacenter reference
    at 60-90% spot-like discounts. analysis/cost_model.py conventions.
 A9 Energy: 20W under load at 13.79 c/kWh commercial (EIA EPM T5.3, YTD May
    2026) = $0.00276/device-hour. Residential 18.11 c/kWh for the at-home tier.

NOT MODELLED (all reduce the result): office HVAC penalty for rejecting heat,
IT administration, security review, hardware wear, network egress, the
utilisation discount on remotely-accessed desktops, and redundancy overhead
(volunteer-computing practice costs ~2x for unreliable hosts).
"""

DESKTOPS, LAPTOPS = 63.85e6, 47.76e6
ALREADY_ON = 0.64
IDLE_PREM, IDLE_HOME = 0.76, 0.85
DOCKED = 0.20
TFLOPS = 2.9
REV_LO, REV_HI = 0.05, 0.20
KWH_COMM, KWH_RES, WATTS = 0.1379, 0.1811, 20
HOURS_YR = 8760

def energy(rate):
    return WATTS / 1000 * rate

def block(name, devices, idle, rate):
    dev_hours = devices * HOURS_YR * idle
    e = dev_hours * energy(rate)
    return {
        "scenario": name, "devices": devices, "idle_share": idle,
        "device_hours_yr": dev_hours,
        "value_lo": dev_hours * REV_LO, "value_hi": dev_hours * REV_HI,
        "energy_cost": e,
        "net_lo": dev_hours * REV_LO - e, "net_hi": dev_hours * REV_HI - e,
        "pflops": devices * TFLOPS / 1000,
    }

rows = [
    block("S1 no policy change (desktops already on)",
          DESKTOPS * ALREADY_ON, IDLE_PREM, KWH_COMM),
    block("S2 Tier A, policy change (all on-prem)",
          DESKTOPS + LAPTOPS * DOCKED, IDLE_PREM, KWH_COMM),
    block("S3 Tier A + B (adds at-home laptops)",
          DESKTOPS + LAPTOPS * DOCKED, IDLE_PREM, KWH_COMM),
]
# S3 adds the at-home tier on residential power
home = block("_home", LAPTOPS * (1 - DOCKED), IDLE_HOME, KWH_RES)
for k in ("devices", "device_hours_yr", "value_lo", "value_hi",
          "energy_cost", "net_lo", "net_hi", "pflops"):
    rows[2][k] += home[k]

H100_FP32 = 67e-3  # PFLOPS per H100, FP32 non-tensor

print(f"{'scenario':46s} {'devices':>10s} {'dev-hrs/yr':>12s} "
      f"{'$bn value':>16s} {'$bn net':>16s} {'EFLOPS':>8s}")
for r in rows:
    print(f"{r['scenario']:46s} {r['devices']/1e6:9.1f}M "
          f"{r['device_hours_yr']/1e9:11.1f}B "
          f"{r['value_lo']/1e9:6.1f}-{r['value_hi']/1e9:<8.1f} "
          f"{r['net_lo']/1e9:6.1f}-{r['net_hi']/1e9:<8.1f} "
          f"{r['pflops']/1000:7.1f}")

print(f"\nFP32-equivalent H100s (A7 caveat applies HARD — FP32 non-tensor only,")
print(f"no tensor cores, no HBM, no interconnect; AI-workload parity is far lower):")
for r in rows:
    print(f"  {r['scenario']:46s} {r['pflops']/H100_FP32/1e6:6.2f}M H100-equivalents")

print("\nSensitivity on A7 (per-device TFLOPS), scenario S2:")
for tf in (0.5, 1.0, 2.0, 2.9):
    p = (DESKTOPS + LAPTOPS * DOCKED) * tf / 1000
    print(f"  {tf:.1f} TFLOPS/device -> {p/1000:7.1f} EFLOPS "
          f"({p/H100_FP32/1e6:5.2f}M H100-eq)")

print("\nSensitivity on A5 (docked-laptop share), scenario S2 value at $0.05/hr:")
for d in (0.10, 0.20, 0.30, 0.40):
    dh = (DESKTOPS + LAPTOPS * d) * HOURS_YR * IDLE_PREM
    print(f"  {d:.0%} docked -> ${dh*REV_LO/1e9:.1f}bn/yr")

import csv, pathlib
out = pathlib.Path(__file__).with_name("fleet_sizing.csv")
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)
print(f"\nwrote {out.name}")
