#!/usr/bin/env python3
"""
Fleet valuation on OBSERVED marketplace rates — supersedes v1/v2 for dollars.

WHY THIS FILE EXISTS. v1 and v2 valued device-hours at $0.05-0.20, derived from
a $0.50/hr datacenter reference. That anchor traces to EC2 Mac at $0.65/hr,
which embeds a macOS licence scarcity rent and does not generalise. v3 dropped
dollars entirely and reported capacity. This file restores dollars on rates
actually observed in the markets that buy this kind of compute.

OBSERVED RATES (fetched 2026-08-02; see sweep JSONs)
 R1 Salad, paid TO THE HOST per idle machine-hour, by graphics card:
      $0.014 floor (GTX1660/RTX2060 class) · $0.028 (RTX 3060 12GB)
      $0.068 (RTX 3090) · $0.180 (RTX 4090) · $0.229 (RTX 5090)
 R2 CPU-only capacity, RENTER side: Salad $0.024/hr (4 vCPU/8GB),
      Akash $0.066/hr (4 vCPU/16GiB), vs AWS/GCP/Azure $0.25-0.29 same spec.
 R3 Host share of renter price: Salad's disclosed split implies ~33-88%
      depending on class. ASSUMED 30-50% for CPU capacity, where no host-side
      rate is published.

THE PARTICIPATION CORRECTION (2026-08-04). The CPU rate in R2 is not
hypothetical: Akash and Salad both sell CPU instances today. What excludes the
business fleet is host-side ONBOARDING conditions — discrete GPU with >=8GB
VRAM (Salad), or Linux + vendor drivers + inbound ports + a dedicated machine
(Vast.ai) — not absence of demand. So the CPU-slice valuation below is the
REALISTIC price for the bulk of the fleet, conditional on participation being
solved, and is reported as a first-class scenario rather than a hypothetical.

FLEET (v2/v3 basis): 679B available device-hours/yr, Tier A+B, US commercial
buildings. 111.6M devices, overwhelmingly integrated graphics (v3).
"""
DEV_H = 679e9
SALAD_HOST = {"entry (1660/2060)": 0.014, "RTX 3060": 0.028, "RTX 3090": 0.068,
              "RTX 4090": 0.180, "RTX 5090": 0.229}
CPU_RENTER = {"Salad 4vCPU/8GB": 0.024, "Akash 4vCPU/16GiB": 0.066,
              "hyperscaler same spec": 0.27}
HOST_SHARE = (0.30, 0.50)

print("=== A. The fleet AS IT IS: integrated graphics, sold as CPU capacity ===")
print("   (the realistic basis for the bulk of 111.6M machines)")
for n, r in CPU_RENTER.items():
    lo, hi = r*HOST_SHARE[0], r*HOST_SHARE[1]
    print(f"  {n:24s} renter ${r:.3f}/hr -> host ${lo:.4f}-{hi:.4f} "
          f"-> fleet ${DEV_H*lo/1e9:6.1f}-{DEV_H*hi/1e9:.1f}bn/yr")
print("""
  -> On the Akash rate, the existing fleet is worth roughly $13-22bn/yr to its
     owners IF it could participate. That is the number the participation
     barrier is currently destroying, and it needs no new hardware.
""")
print("=== B. The fleet UPGRADED: observed host rates by card ===")
for n, r in SALAD_HOST.items():
    print(f"  {n:20s} ${r:.3f}/hr -> ${r*8760:7.0f}/machine/yr -> fleet ${DEV_H*r/1e9:7.1f}bn/yr")
print("""
  (Fleet-wide figures assume every machine carries that card, which the SKU
   evidence rules out — laptops and SFF desktops have no slot. Read column
   three as a ceiling; the per-machine column is the usable number and is what
   profit_per_machine.py consumes.)
""")
print("=== C. What changed from v1/v2 ===")
for label, lo, hi in (("v1/v2 derived basis ($0.05-0.20)", 0.05, 0.20),
                      ("observed CPU-slice, host share", 0.024*0.30, 0.066*0.50),
                      ("observed GPU host rate, entry->top", 0.014, 0.229)):
    print(f"  {label:38s} ${DEV_H*lo/1e9:7.1f}-{DEV_H*hi/1e9:.1f}bn/yr")
print("""
  The derived basis sat ABOVE the observed CPU-slice range and BELOW the
  observed top-end GPU rate — it was not uniformly wrong, it was measuring the
  wrong machine. The CPU-slice row is the right comparison for the fleet that
  actually exists; the GPU rows require the upgrade path priced in
  profit_per_machine.py.
""")
import csv, pathlib
rows = []
for n, r in CPU_RENTER.items():
    rows.append({"basis": f"CPU renter: {n}", "rate_usd_hr": r,
                 "host_lo": r*HOST_SHARE[0], "host_hi": r*HOST_SHARE[1],
                 "fleet_bn_lo": DEV_H*r*HOST_SHARE[0]/1e9, "fleet_bn_hi": DEV_H*r*HOST_SHARE[1]/1e9})
for n, r in SALAD_HOST.items():
    rows.append({"basis": f"GPU host: {n}", "rate_usd_hr": r, "host_lo": r, "host_hi": r,
                 "fleet_bn_lo": DEV_H*r/1e9, "fleet_bn_hi": DEV_H*r/1e9})
o = pathlib.Path(__file__).with_name("fleet_sizing_v4.csv")
with o.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
    for r_ in rows: w.writerow(r_)
print(f"wrote {o.name}")
