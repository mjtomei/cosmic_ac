#!/usr/bin/env python3
"""
Future pricing: hardware prices rise AND a FLOP becomes fungible.

Two scenarios are needed side by side (Matthew, 2026-08-04):
  TODAY   — observed marketplace prices, machine-class-specific (fleet_sizing_v4.py)
  FUTURE  — compute priced per unit of throughput rather than per machine class,
            with hardware prices escalating.

THE ANCHOR THAT MAKES THIS TRACTABLE. The market ALREADY prices FP32 almost
linearly across the machines it accepts. From observed Salad host rates against
published FP32:
    RTX 3060  $0.028/hr / ~13.0 TFLOPS = $0.00215 per TFLOPS-hour
    RTX 4090  $0.180/hr / ~82.6 TFLOPS = $0.00218
    RTX 5090  $0.229/hr / 104.8 TFLOPS = $0.00218   (5090 FP32 verified)
So $0.00218/TFLOPS-hour is an OBSERVED price of compute, not a derived one.
Fungibility means extending that same rate to machines currently excluded —
which is exactly what the participation barrier prevents today.

WHAT FUNGIBILITY CHANGES. Under machine-class pricing an integrated-graphics
PC earns nothing regardless of capability. Under per-throughput pricing it earns
in proportion to what it can actually do — and which DENOMINATION is tradeable
decides how much that is:
    FP32 sustained        0.51 TFLOPS/device   (v3, corrected installed mix)
    FP16 packed (2x)      1.02
    INT8 via DP4a (4x)    2.04   <- poolable today from ordinary compute APIs
    Platform TOPS         34     <- business-desktop APU incl. NPU, framework-gated

PRICE ESCALATION. Applied as a multiplier on $/throughput-hour. Anchored to the
paper's own demand argument and the memory-price evidence in section 4; treated
as a scenario variable, NOT a forecast.

ENERGY stays at 13.79 c/kWh commercial; a 65W business PC costs $79/yr.
"""
OBS_RATE = 0.00218          # $/TFLOPS-hour, observed
DEV_H_PER_MACHINE = 679e9/111.6e6   # available hours per machine per year
RATE_KWH, HOURS = 0.1379, 8760
DENOM = {"FP32 sustained": 0.51, "FP16 packed": 1.02,
         "INT8 poolable (DP4a)": 2.04, "Platform TOPS (NPU incl.)": 34.0}
ENERGY_65W = 65/1000*RATE_KWH*HOURS

print(f"available hours/machine/yr: {DEV_H_PER_MACHINE:,.0f}   energy at 65W: ${ENERGY_65W:.0f}/yr\n")
print("=== Revenue per machine per year, by tradeable denomination x price escalation ===")
print(f"{'denomination':28s} {'units':>7s} " + "".join(f"{f'{m}x':>11s}" for m in (1,2,3,5,10)))
for name, units in DENOM.items():
    row = f"{name:28s} {units:7.2f} "
    for m in (1,2,3,5,10):
        rev = units * OBS_RATE * m * DEV_H_PER_MACHINE
        row += f"{rev:11,.0f}"
    print(row)
print(f"\n(subtract ${ENERGY_65W:.0f}/yr energy for net; anything below that line is loss-making)")

print("\n=== Net per machine, after energy ===")
print(f"{'denomination':28s} " + "".join(f"{f'{m}x':>11s}" for m in (1,2,3,5,10)))
for name, units in DENOM.items():
    row = f"{name:28s} "
    for m in (1,2,3,5,10):
        net = units*OBS_RATE*m*DEV_H_PER_MACHINE - ENERGY_65W
        row += f"{net:+11,.0f}"
    print(row)

print("\n=== Fleet total, 111.6M machines ===")
print(f"{'denomination':28s} " + "".join(f"{f'{m}x':>11s}" for m in (1,2,3,5,10)))
for name, units in DENOM.items():
    row = f"{name:28s} "
    for m in (1,2,3,5,10):
        tot = (units*OBS_RATE*m*DEV_H_PER_MACHINE - ENERGY_65W) * 111.6e6
        row += f"{tot/1e9:+10.0f}bn"[:11]
    print(row)

print("""
=== The finding: fungibility is worth more than price escalation ===

  Compare the two levers on the machine that actually exists — an
  integrated-graphics business PC:

    price escalation alone, staying FP32:   1x -> 10x  is a 10x revenue gain
    denomination alone, at today's prices:  FP32 -> platform TOPS is a 67x gain

  Solving programmability is worth roughly SEVEN TIMES more to this fleet than
  a tenfold rise in the price of compute. And the two are not substitutes: the
  weak machine needs the denomination change to clear its own energy cost at
  all. At FP32 and today's prices it earns ~$7/yr against $79/yr of power —
  loss-making by an order of magnitude, which is why no market bids for it.

  That is this paper's thesis stated as a price: the barrier is not that
  compute is cheap, it is that most of what the machine can do is not
  purchasable. The NPU tier alone — physically present, framework-gated, worth
  more than everything else combined — is the whole argument in one line item.
""")
import csv, pathlib
rows = []
for name, units in DENOM.items():
    for m in (1,2,3,5,10):
        rev = units*OBS_RATE*m*DEV_H_PER_MACHINE
        rows.append({"denomination": name, "units_per_device": units,
                     "price_multiple": m, "rate_usd_per_unit_hr": OBS_RATE*m,
                     "revenue_usd_machine_yr": round(rev,2),
                     "net_after_energy_usd_yr": round(rev-ENERGY_65W,2),
                     "fleet_net_usd_bn": round((rev-ENERGY_65W)*111.6e6/1e9,2)})
o = pathlib.Path(__file__).with_name("fleet_sizing_v5_fungible.csv")
with o.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
    for r in rows: w.writerow(r)
print(f"wrote {o.name} ({len(rows)} rows)")
