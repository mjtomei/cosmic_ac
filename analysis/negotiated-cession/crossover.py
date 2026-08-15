#!/usr/bin/env python3
"""crossover.py — when does ceding negotiated control of your compute beat
defending it? The S16 x S18 join (the novel number of this study).

THE INEQUALITY (S18 brief). Cession is individually rational when
    E[rent from ceded compute] + defense cost avoided + insurance transfer
        > E[residual loss under negotiated access].
This script prices every term per machine-year from S16's fetched inputs and
solves for the crossover rent rate R* — the rent at which cession breaks even
— by isolation architecture (S16 Case 1-4), incident probability p_m, owner
severity tier, and hardware tier. R* is then compared with the OBSERVED
market rate (OBS_RATE = $0.00218/TFLOPS-hr, Salad 2026-08-02).

TWO CONTRACT FORMS:
  insured   — the builder/underwriter bears residual sharing risk and prices
              it into the rent split (S16 Path 1; Grossman 1981 warranty).
              Owner's net = machine profit (rev - energy - fixed - premium)
              + avoided defense cost. Residual-loss term = 0 by contract.
  uninsured — the owner bears residual risk: subtract p_m x boundary-index x
              owner severity, plus the correlated-event reimaging term
              (P_sys x $200/machine, S16 actuarial section 5).

ALL INPUTS from analysis/enterprise-idle-fleet/ (S16, fetched 2026-08-02/03)
unless marked OURS:
  revenue/wattage tiers   profit_per_machine.py (Salad demand-monitor API)
  energy rates            EIA EPM T5.3: commercial 13.79 c/kWh, residential 18.11
  fixed costs per case    profit_per_machine.py (BOM + NRE + upkeep amortized)
  insurance               premium = p_m x idx x $83k / 0.65 (claims median,
                          Verizon 2026; 65% loss ratio; boundary index
                          Case 1/2/3-4 = 1.0 / 0.010 / 0.0009 from KEV)
  owner severity          Verizon 2026 medians: SMB $38k, mid $96k,
                          large $283k. Household: IC3 2024 $16.6B/859,532
                          complaints = $19.3k mean/complaint [OUR arithmetic,
                          a mean over reported complaints, not a household
                          incident median — flagged].
  reimaging               ~$200/machine (S16 assumption, declared)
  OBS_RATE                $0.00218/TFLOPS-hr FP32 (flat 3060->5090, v4/v5)
  household consent       $25.60/household-yr (EIA demand-response 2024,
                          S16's anchor for what household consent costs)

Output: crossover.csv + printed digest.
"""
import csv
import pathlib

HERE = pathlib.Path(__file__).parent

# ------------------------------------------------------------------ inputs
KWH_COMMERCIAL, KWH_RESIDENTIAL = 0.1379, 0.1811   # EIA EPM T5.3, YTD May 2026
YRS = 4                                            # Dell 10-K depreciation life
SEV_CLAIM, LOSS_RATIO = 83_000, 0.65               # Verizon 2026; A3
IDX = {"case1_sameOS": 1.0, "case2_vm_nic": 0.010,
       "case3_hw_partition": 0.0009, "case4_new_silicon": 0.0009}
FIXED = {"case1_sameOS": 8.50, "case2_vm_nic": 57.75,     # $/machine-yr,
         "case3_hw_partition": 17.95, "case4_new_silicon": 19.75}  # profit_per_machine.py
SEV_OWNER = {"household": 19_313,   # IC3 2024 mean/complaint [OURS, flagged]
             "smb": 38_000, "mid": 96_000, "large": 283_000}  # Verizon 2026
REIMAGE = 200.0                     # S16 declared assumption
OBS_RATE = 0.00218                  # $/TFLOPS-hr, Salad observed
CONSENT_HH = 25.60                  # $/household-yr, EIA demand response 2024

# (tier, revenue $/yr, watts, FP32 TFLOPS, earning-hours factor) — Salad host
# rates 2026-08-02. S16 accounting followed exactly: dGPU tiers are dedicated
# 24/7 earners (revenue = $/hr x 8760, e.g. top $0.229 x 8760 = $2,006;
# energy also x 8760); the iGPU rows earn only during the 76% idle share
# (S16 v5) while paying always-on energy. TFLOPS: 4090/5090 backed out of
# OBS_RATE (82.6/105.0, matches specs); entry/mid vendor FP32 (7.2 approx
# 2060-class, 35.6 3090). iGPU_today revenue $0: the participation barrier
# (S16 v4 — no marketplace accepts the machine); iGPU_fungible prices the
# same machine at OBS_RATE if the denomination barrier fell.
TIERS = [
    ("iGPU_today", 0.0, 65, 0.51, 0.76),
    ("iGPU_fungible_fp32", OBS_RATE * 0.51 * 8760 * 0.76, 65, 0.51, 0.76),
    ("entry_1660_2060", 123.0, 235, 7.2, 1.0),
    ("mid_3090", 596.0, 415, 35.6, 1.0),
    ("high_4090", 1577.0, 515, 82.6, 1.0),
    ("top_5090", 2006.0, 640, 105.0, 1.0),
]
P_M = (1e-5, 1e-3, 1e-2)            # sweep: sharing-caused incident prob (A2)
P_SYS = 0.01                        # correlated boundary-event prob [OURS]
DEF_AVOID = (0.0, 100.0)            # $/machine-yr defense converted [OURS sweep]


def rows_for(pop, kwh, sev_owner, extra_cost):
    out = []
    for tier, rev, watts, tflops, avail in TIERS:
        energy = watts / 1000 * kwh * 8760          # always-on (S16 accounting)
        for case, idx in IDX.items():
            fixed = FIXED[case]
            for p_m in P_M:
                prem = p_m * idx * SEV_CLAIM / LOSS_RATIO
                el_own = p_m * idx * sev_owner + P_SYS * idx / IDX["case1_sameOS"] * REIMAGE
                for d_avoid in DEF_AVOID:
                    for form in ("insured", "uninsured"):
                        cost = energy + fixed + extra_cost + (prem if form == "insured" else 0.0)
                        risk = 0.0 if form == "insured" else el_own
                        net = rev + d_avoid - cost - risk
                        r_star = cost + risk - d_avoid        # $/yr rent to break even
                        r_star_tfh = r_star / (tflops * 8760 * avail)
                        out.append({
                            "population": pop, "tier": tier, "case": case,
                            "p_m": p_m, "defense_avoided": d_avoid, "form": form,
                            "revenue_yr": round(rev, 1), "energy_yr": round(energy, 1),
                            "fixed_yr": fixed, "premium_yr": round(prem, 2),
                            "residual_el_yr": round(risk, 2),
                            "net_cession_yr": round(net, 1),
                            "crossover_rent_yr": round(r_star, 1),
                            "crossover_rate_tflops_hr": round(r_star_tfh, 5),
                            "obs_over_crossover": round(OBS_RATE / r_star_tfh, 2)
                            if r_star_tfh > 0 else "",
                        })
    return out


def main():
    rows = rows_for("enterprise", KWH_COMMERCIAL, SEV_OWNER["large"], 0.0)
    rows += rows_for("smb", KWH_COMMERCIAL, SEV_OWNER["smb"], 0.0)
    rows += rows_for("household", KWH_RESIDENTIAL, SEV_OWNER["household"], CONSENT_HH)
    with open(HERE / "crossover.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        [w.writerow(r) for r in rows]
    print(f"wrote crossover.csv ({len(rows)} rows)\n")

    # digest: the shape of the answer
    def show(pop, tier, case, p_m, form, d=0.0):
        r = next(x for x in rows if x["population"] == pop and x["tier"] == tier
                 and x["case"] == case and x["p_m"] == p_m and x["form"] == form
                 and x["defense_avoided"] == d)
        print(f"{pop:10s} {tier:18s} {case:18s} p_m={p_m:.0e} {form:9s} "
              f"net ${r['net_cession_yr']:>8} R* ${r['crossover_rent_yr']:>7}/yr "
              f"(${r['crossover_rate_tflops_hr']}/TF-hr, obs/R* {r['obs_over_crossover']})")

    print("== enterprise, large-firm severity ==")
    for case in IDX:
        show("enterprise", "high_4090", case, 1e-3, "uninsured")
    print("-- the participation barrier (iGPU fleet) --")
    for tier in ("iGPU_today", "iGPU_fungible_fp32"):
        show("enterprise", tier, "case3_hw_partition", 1e-3, "uninsured")
    print("-- naive sharing at pessimistic p_m: what 'malware' costs --")
    show("enterprise", "high_4090", "case1_sameOS", 1e-2, "uninsured")
    print("== household ==")
    for case in ("case1_sameOS", "case3_hw_partition"):
        show("household", "mid_3090", case, 1e-3, "uninsured")


if __name__ == "__main__":
    main()
