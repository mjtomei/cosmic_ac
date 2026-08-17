#!/usr/bin/env python3
"""The stage-2 column: DQI on Pangram verdict, with chamber fixed effects.

WHY THIS FILE EXISTS

The stage-2 column in §4.9 was specified in words at the table -- "labelled by
Pangram verdict, with chamber fixed effects" -- and reproduces exactly from that
sentence, but no committed script produced it. `analyze.py --key key2.json`
regresses on the SCREEN's continuous ai_guess instead and returns different
numbers, so the documented command did not match the published column. That
breaks the study's one-script-per-claim convention (review 2026-08-11, Q7).

THE SPECIFICATION, stated here so it cannot drift again:

  outcome    one DQI dimension
  regressor  1 if the Pangram verdict is AI or Mixed, else 0
             (Mixed is POOLED WITH AI; --drop-mixed reports the sensitivity)
  controls   chamber fixed effects
  errors     HC1
  sentinels  respect_demands and respect_counterargs drop their -1
             (inapplicable) rows rather than scoring them zero, which would
             count "nothing to engage with" as "engaged badly"

Reproduces the published column to three decimals on all seven dimensions.

Usage: python analyze_stage2.py [--drop-mixed]
"""
import argparse
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = ["justification", "common_good", "respect_groups", "respect_demands",
        "respect_counterargs", "constructive", "evidence"]
SENTINEL = {"respect_demands", "respect_counterargs"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drop-mixed", action="store_true",
                    help="exclude Mixed verdicts instead of pooling them with AI")
    a = ap.parse_args()
    rows = json.load(open(os.path.join(HERE, "results_stage2.json")))
    chambers = sorted({r["chamber"] for r in rows})[1:]      # first is baseline

    print(f"stage 2 — DQI on Pangram verdict, chamber FE, HC1"
          f"{'  (Mixed dropped)' if a.drop_mixed else '  (Mixed pooled with AI)'}")
    print(f"  {len(rows)} graded segments, {len(chambers) + 1} chambers\n")
    print(f"  {'dimension':<22s}{'coef':>9s}{'se':>8s}{'t':>7s}{'n':>7s}")
    for d in DIMS:
        sub = [r for r in rows
               if r.get(d) is not None
               and not (d in SENTINEL and r[d] == -1)
               and not (a.drop_mixed and r["verdict"] == "Mixed")]
        y = np.array([r[d] for r in sub], float)
        X = np.array([[1.0, 1.0 if r["verdict"] in ("AI", "Mixed") else 0.0]
                      + [1.0 if r["chamber"] == c else 0.0 for c in chambers]
                      for r in sub])
        XtXi = np.linalg.pinv(X.T @ X)
        beta = XtXi @ (X.T @ y)
        e = y - X @ beta
        n, k = X.shape
        V = (n / max(n - k, 1)) * XtXi @ ((X * (e ** 2)[:, None]).T @ X) @ XtXi
        b, se = beta[1], math.sqrt(V[1, 1])
        star = " *" if abs(b / se) > 1.96 else ""
        print(f"  {d:<22s}{b:>+9.3f}{se:>8.3f}{b/se:>7.2f}{len(sub):>7d}{star}")

    print("\n  Sentinel dimensions carry smaller n because inapplicable (-1) rows")
    print("  are dropped. That exclusion conditions on a post-treatment variable:")
    print("  applicability itself falls with AI status (review Q1), so the null on")
    print("  these two means 'engages no worse when there IS something to engage",)
    print("  with', not 'engagement is unaffected'.")


if __name__ == "__main__":
    main()
