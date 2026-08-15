#!/usr/bin/env python3
"""run_cession.py — S18 four-regime runs of the extended Fable-Carson engine.

Two products:
  1. mixture_2028.csv — the sealed 2027-2028 window with the cession regime
     mixed in at a sensitivity grid of weights w_c (0 = their sealed forecast;
     the sealed 30/45/25 renormalized proportionally, plus an offense-first
     displacement variant). Shows what an early-arriving cession regime does
     to their headline in their own currency.
  2. per_regime.csv — each regime's own distribution (median/mean/P90/P99,
     exceedances, both bases) at the reference cell. The cession row IS the
     study's model-level answer: what the cyber-cost world looks like if
     negotiated cession is the regime.

Their sealed forecast is w_c = 0 and is reproduced exactly by their own code
(verified separately: 2028 anchored median 107.2/mean 240.6, fresh
122.9/282.6, P(>$200B) 38.0/40.5%). Everything with w_c > 0 is OURS.

Usage: python run_cession.py [--n 4000] [--full]
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
THRESH = (25, 50, 100, 200)
SEALED = {"offense": 0.30, "balanced": 0.45, "defense": 0.25}


def stats(acc):
    return {"median_busd": round(acc.quantile(0.5), 2),
            "mean_busd": round(acc.mean(), 2),
            "p90_busd": round(acc.quantile(0.9), 1),
            "p99_busd": round(acc.quantile(0.99), 1),
            **{f"p_gt_{t}b": round(acc.exceedance(t), 4) for t in THRESH}}


def weights4(w_c, mode="proportional"):
    """Four-regime weights at cession weight w_c."""
    if mode == "proportional":
        return {rg: w * (1 - w_c) for rg, w in SEALED.items()} | {"cession": w_c}
    # offense-first: cession displaces offense-regime mass first (cession as
    # the adaptation TO offense pressure), then proportional from the rest.
    take = min(w_c, SEALED["offense"])
    rest = w_c - take
    w = {"offense": SEALED["offense"] - take}
    rem = SEALED["balanced"] + SEALED["defense"]
    for rg in ("balanced", "defense"):
        w[rg] = SEALED[rg] * (1 - rest / rem)
    w["cession"] = w_c
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--full", action="store_true", help="n = 10000 (sealed size)")
    ap.add_argument("--seed", type=int, default=20260810)
    args = ap.parse_args()
    n = 10000 if args.full else args.n

    with open(HERE / "params_cession.json") as f:
        params = json.load(f)

    t0 = time.time()
    baselines = cf.fit_baselines(params)
    res = eng.simulate(params, baselines, n, n, args.seed,
                       s3_variant="both", regimes=eng.REGIMES,
                       years=(2027, 2028))
    print(f"simulate 4 regimes x 2027-28: {time.time()-t0:.0f}s", file=sys.stderr)

    # ---- per-regime distributions, reference cell ----
    rows = []
    for yr in (2027, 2028):
        for v in ("anchored", "fresh"):
            for rg in eng.REGIMES:
                for b in ("transfer_inclusive", "resource_only"):
                    a = res.head[(yr, v, rg, REF, b)]
                    rows.append({"year": yr, "variant": v, "regime": rg,
                                 "basis": b, **stats(a)})
    with open(HERE / "per_regime.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        [w.writerow(r) for r in rows]

    # ---- mixtures at the w_c grid ----
    rows = []
    for yr in (2027, 2028):
        for v in ("anchored", "fresh"):
            for b in ("transfer_inclusive", "resource_only"):
                accs = {rg: res.head[(yr, v, rg, REF, b)] for rg in eng.REGIMES}
                for mode in ("proportional", "offense_first"):
                    for w_c in (0.0, 0.05, 0.10, 0.25, 0.50):
                        ww = weights4(w_c, mode)
                        mixed = eng.Acc.mix([accs[rg] for rg in eng.REGIMES],
                                            [ww[rg] for rg in eng.REGIMES])
                        rows.append({"year": yr, "variant": v, "basis": b,
                                     "mode": mode, "w_cession": w_c,
                                     **{f"w_{rg}": round(ww[rg], 3)
                                        for rg in eng.REGIMES},
                                     **stats(mixed)})
    with open(HERE / "mixture_2028.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        [w.writerow(r) for r in rows]

    print(f"wrote per_regime.csv, mixture_2028.csv (n={n}, seed={args.seed}, "
          f"{time.time()-t0:.0f}s total)")


if __name__ == "__main__":
    main()
