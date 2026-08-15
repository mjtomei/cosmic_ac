#!/usr/bin/env python3
"""horizon.py — S18 horizon extension: the sealed dynamics rolled to 2032,
baseline arm vs cession arm.

EVERYTHING PAST 2028 IS OUR CONSTRUCTION, NOT THEIR FORECAST. Their
parameters are sealed for 2026-2028 only. Stated assumptions of the roll:
  - baselines: the fitted log-linear x full-window trends extrapolated to
    2032 (their functional form, our projection window);
  - AI deviation ramp HELD at the sealed 2028 value (1.5x) for 2029-2032
    (the "2028 held at 2027 level, no sealed growth" precedent);
  - Ch4 phase-in held at 1.0; D-15 damping chained year-over-year;
  - S3a scenario severities stay anchored in absolute dollars (no economy
    scaling) — conservative;
  - the D-14 caps ($250B/event, $3.5T/yr systemic) stay fixed.

ARMS (mix-time only; both arms share one simulation - common random numbers):
  baseline — sealed 30/45/25 mixture, all years (w_cession = 0).
  cession  — cession-regime weight phases in 2029-2032, taken from the
             sealed weights proportionally:
               main: 0 / 0 / 0.05 / 0.15 / 0.30 / 0.45  (2027..2032)
               slow: half of main.
             The schedule is a SCENARIO, not a forecast. Its rationale is
             the crossover result (crossover.py: cession already beats
             defense wherever hardware can participate) plus S16's Paths
             2-3 (compute-price escalation and internal-MI integration
             build the plumbing regardless).

RENT LEDGER (side-by-side, never netted silently into delta): the ceded
fleet's rent income at each year's penetration, using S16's US-commercial
numbers only — retrofit $6-40B/yr at mature penetration, purpose-bought
ceiling ~$140B/yr. Scope mismatch is flagged loudly: delta is GLOBAL, the
rent column is US-commercial-buildings-only (S16 refuses a global
extrapolation; an illustrative global scaling by their US->global modal
multiplier 2.449 is given in its own clearly-labeled column).

Usage: python horizon.py [--n 4000] [--full]
"""
import argparse
import csv
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))

import counterfactual_ext as cf
import engine_ext as eng

REF = "log_linear|full_2015_2024"
YEARS = (2027, 2028, 2029, 2030, 2031, 2032)
SEALED = {"offense": 0.30, "balanced": 0.45, "defense": 0.25}
W_C = {"main": {2027: 0.0, 2028: 0.0, 2029: 0.05, 2030: 0.15,
                2031: 0.30, 2032: 0.45},
       "slow": {2027: 0.0, 2028: 0.0, 2029: 0.025, 2030: 0.075,
                2031: 0.15, 2032: 0.225}}
# S16 mature-penetration rent, US commercial buildings only, $B/yr:
RENT_LO, RENT_HI, RENT_CEIL = 6.0, 40.0, 140.0
US_TO_GLOBAL = 2.449   # their modal multiplier; OUR application to rent


def stats(acc):
    return {"median_busd": round(acc.quantile(0.5), 1),
            "mean_busd": round(acc.mean(), 1),
            "p90_busd": round(acc.quantile(0.9), 1),
            "p99_busd": round(acc.quantile(0.99), 1)}


def mix(res, yr, v, basis, w_c):
    w = {rg: wt * (1 - w_c) for rg, wt in SEALED.items()} | {"cession": w_c}
    accs = [res.head[(yr, v, rg, REF, basis)] for rg in eng.REGIMES]
    return eng.Acc.mix(accs, [w[rg] for rg in eng.REGIMES])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--seed", type=int, default=20260810)
    args = ap.parse_args()
    n = 10000 if args.full else args.n

    with open(HERE / "params_cession.json") as f:
        params = json.load(f)

    t0 = time.time()
    baselines = cf.fit_baselines(params, years=YEARS)
    res = eng.simulate(params, baselines, n, n, args.seed,
                       s3_variant="both", regimes=eng.REGIMES, years=YEARS)
    print(f"simulate 4 regimes x 2027-2032: {time.time()-t0:.0f}s",
          file=sys.stderr)

    rows = []
    for v in ("anchored", "fresh"):
        for basis in ("transfer_inclusive", "resource_only"):
            for sched in ("main", "slow"):
                for yr in YEARS:
                    w_c = W_C[sched][yr]
                    base = stats(mix(res, yr, v, basis, 0.0))
                    cess = stats(mix(res, yr, v, basis, w_c))
                    rent_lo, rent_hi = w_c * RENT_LO, w_c * RENT_HI
                    rows.append({
                        "year": yr, "variant": v, "basis": basis,
                        "schedule": sched, "w_cession": w_c,
                        **{f"base_{k}": val for k, val in base.items()},
                        **{f"cess_{k}": val for k, val in cess.items()},
                        "wedge_median": round(cess["median_busd"] - base["median_busd"], 1),
                        "wedge_mean": round(cess["mean_busd"] - base["mean_busd"], 1),
                        "wedge_p99": round(cess["p99_busd"] - base["p99_busd"], 1),
                        "rent_us_lo_busd": round(rent_lo, 1),
                        "rent_us_hi_busd": round(rent_hi, 1),
                        "rent_us_ceiling_busd": round(w_c * RENT_CEIL, 1),
                        "rent_global_illustrative_busd": round(
                            w_c * RENT_HI * US_TO_GLOBAL, 1),
                    })
    with open(HERE / "horizon.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        [w.writerow(r) for r in rows]

    print(f"wrote horizon.csv (n={n}, seed={args.seed}, "
          f"{time.time()-t0:.0f}s total)")
    print("\nyear  w_c   base med/mean      cession med/mean    wedge med/mean"
          "   rent US lo-hi ($B)")
    for r in rows:
        if (r["variant"], r["basis"], r["schedule"]) == \
           ("anchored", "transfer_inclusive", "main"):
            print(f"{r['year']}  {r['w_cession']:.2f}  "
                  f"{r['base_median_busd']:7.1f}/{r['base_mean_busd']:7.1f}  "
                  f"{r['cess_median_busd']:7.1f}/{r['cess_mean_busd']:7.1f}  "
                  f"{r['wedge_median']:7.1f}/{r['wedge_mean']:7.1f}  "
                  f"{r['rent_us_lo_busd']}-{r['rent_us_hi_busd']}")


if __name__ == "__main__":
    main()
