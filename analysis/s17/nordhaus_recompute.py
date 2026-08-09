#!/usr/bin/env python3
"""
S17 — Nordhaus's capture ratio, re-solved over measured AI imitation lags.

WHAT THIS COMPUTES
------------------
Nordhaus (2004), "Schumpeterian Profits in the American Economy" (NBER WP
10433), estimates that innovators captured ~2.2% of the present value of
social returns to innovation (US nonfarm business, 1948-2001), from a low
instantaneous appropriability ratio a ~= 0.07 combined with a depreciation
rate on Schumpeterian profits lambda = 0.20/yr. lambda was NOT estimated:
it is imposed a priori from patent-renewal data (Pakes & Simpson, BPEA
1989; see WP 10433 fn.8 and Table 2, which sweeps lambda 0.1-0.4).

lambda is the model's stand-in for the imitation lag: Nordhaus lists
imitation among the decay channels (p.9). For the AI sector the lag is now
directly measured (Epoch AI open-vs-closed frontier series; see
imitation_lag.csv). This script re-solves the capture ratio with measured
lambda, holding everything else at Nordhaus's values, then sweeps a.

THE CAPTURE EQUATION (derived; the paper states 2.2% but never prints the
formula -- see reading/notes/nordhaus-2004.md)
----------------------------------------------
Innovation at t=0 cuts cost by a small fraction h. Output Q grows at g,
profits discounted at r (r > g).

  Social benefit flow at age theta:   h * Q0 * e^(g*theta)
  PV_social  = h*Q0 / (r - g)
  Innovator appropriates the fraction a*e^(-lambda*theta) of that flow
  (WP 10433 p.9: appropriation rate a*e^(-lambda*theta)):
  PV_private = h*Q0 * a / (r + lambda - g)

  capture(a, lambda) = PV_private / PV_social = a*(r-g) / (r - g + lambda)

At Nordhaus's central parameters (a=.07, lambda=.20, r=.10, g=.03) this
gives 1.81%, not his published 2.2% -- his exact calculation is unprinted
and presumably differs in discretization or an h* term. We therefore report
BOTH the raw formula value and a normalized column that anchors the
lambda=0.2 cell to his published 2.2%:

  capture_norm(lambda) = 2.2% * (r - g + 0.20) / (r - g + lambda)

The normalization is legitimate because the lambda-dependence enters only
through the (r - g + lambda) factor, which is common to any variant of the
derivation; the headline "capture falls K-fold" is identical in raw and
normalized columns.

MAPPING MEASURED LAG -> lambda
------------------------------
We read the imitation lag L (years) as the mean lifetime of the innovator's
lead: lambda = 1/L. (Alternative half-life reading lambda = ln2/L is
reported as a sensitivity column; it shifts levels, not the story.)
Measured lags (verified 2026-08-04; per-row sources in imitation_lag.csv):
  GPT-3 -> OPT-175B open replication  ~23 months  -> lambda ~= 0.52/yr
    (Cottier/Rethink Priorities framing, cited by Epoch; Epoch's own
     measurement of the era is BLOOM-176B MMLU parity at 25 months)
  Epoch Nov-2024 open-models report: "a lag of about one year"
                                                  -> lambda ~= 1.0/yr
  Epoch ECI, Jan 2023 - Oct 2025:     ~3 months   -> lambda ~= 4.0/yr
  Epoch ECI, Jan - May 2026:          ~4 months   -> lambda ~= 3.0/yr
Against Nordhaus's postwar lambda = 0.20/yr (implied mean lead ~5 years;
Mansfield-Schwartz-Wagner 1981: ~60% of patented innovations imitated
within 4 years, imitation time ~70% of innovation time -- consistent).

HONEST LIMITS (carried with the result, not footnoted away)
-----------------------------------------------------------
- Benchmark parity is not economic substitutability; the lag in enterprise
  willingness-to-pay is longer than the lag on ECI. Direction of bias:
  measured lambda overstates the effective decay -> capture understated.
- Epoch's own caveats cut the other way: open models score worse on
  private benchmarks, and labs withhold their best models, so the measured
  lag UNDERSTATES the true capability lag. The two biases partially offset;
  we report a lambda RANGE rather than a point.
- a (instantaneous appropriability) is swept, not asserted: appropriation
  migrates to complements (distribution, integration, trust, data, supply
  chain -- Teece's appropriability regimes). The claim is about the
  artifact, not the firm.
- The 2025 -> 2026 3->4-month move is a widening; no exponential is fit.

Nordhaus's own words license the extension (WP 10433 pp.30-32): the
depreciation rate "is likely to be very high in new-economy sectors"
because "the low costs of imitation, transmission, and distribution of
information technologies ... reduce the durability of Schumpeterian
profits."

SOURCES for every non-derived number
------------------------------------
- a = 0.07 central, 0.059-0.104 across specs: WP 10433 Tables 1-3.
- lambda = 0.20/yr baseline: WP 10433 (a priori, patent renewals, fn.8).
- r = 0.10, g = 0.03: WP 10433 p.22 ("discount rate on Schumpeterian
  profits of 10 percent", "growth rate of the economy of 3 percent").
- 2.2% (range 1.3-3.3%): WP 10433 p.22 and Conclusion.
- Measured lags: analysis/s17/imitation_lag.csv (per-row sources).

Output: capture_ratio_grid.csv + stdout summary.
"""

import csv
import math
import os

R = 0.10        # discount rate on Schumpeterian profits (Nordhaus p.22)
G = 0.03        # economy growth rate (Nordhaus p.22)
A_NORDHAUS = 0.07
LAMBDA_NORDHAUS = 0.20
NORDHAUS_PUBLISHED = 0.022   # his 2.2% headline at (a=.07, lambda=.2)


def capture_raw(a, lam, r=R, g=G):
    """capture = a*(r-g)/(r-g+lambda). Derivation in module docstring."""
    return a * (r - g) / (r - g + lam)


def capture_norm(a, lam, r=R, g=G):
    """Anchored so (a=.07, lambda=.2) reproduces Nordhaus's published 2.2%.
    Scales linearly in a and through the common (r-g+lambda) factor."""
    anchor = NORDHAUS_PUBLISHED * (a / A_NORDHAUS)
    return anchor * (r - g + LAMBDA_NORDHAUS) / (r - g + lam)


# (label, lag_years or None, lambda) -- lambda = 1/lag where lag measured
SCENARIOS = [
    ("Nordhaus 1948-2001 baseline (patent renewals)", None, 0.20),
    ("GPT-3 -> OPT-175B era, lag ~23 mo (2020-22)",   23 / 12, 12 / 23),
    ("Epoch Nov-2024 report, lag ~1 yr",              1.0,     1.0),
    ("Epoch ECI Jan-2026 - May-2026, lag ~4 mo",      4 / 12,  3.0),
    ("Epoch ECI Jan-2023 - Oct-2025, lag ~3 mo",      3 / 12,  4.0),
]

A_SWEEP = [0.104, 0.07, 0.059, 0.03, 0.01]  # Table-1 extremes + migration cases


def main():
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "capture_ratio_grid.csv")
    rows = []
    for label, lag, lam in SCENARIOS:
        for a in A_SWEEP:
            lam_half = math.log(2) / lag if lag else lam  # half-life sensitivity
            rows.append({
                "scenario": label,
                "imitation_lag_years": f"{lag:.3f}" if lag else "n/a (lambda a priori)",
                "lambda_per_yr": f"{lam:.3f}",
                "a": f"{a:.3f}",
                "capture_raw": f"{capture_raw(a, lam):.5f}",
                "capture_normalized_to_nordhaus_2.2pct":
                    f"{capture_norm(a, lam):.5f}",
                "capture_norm_halflife_reading":
                    f"{capture_norm(a, lam_half):.5f}",
                "fold_drop_vs_baseline_same_a":
                    f"{capture_norm(a, LAMBDA_NORDHAUS)/capture_norm(a, lam):.1f}",
            })

    with open(outpath, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {outpath} ({len(rows)} rows)\n")
    print("Headline (a held at Nordhaus's 0.07, normalized column):")
    for label, lag, lam in SCENARIOS:
        c = capture_norm(A_NORDHAUS, lam)
        fold = capture_norm(A_NORDHAUS, LAMBDA_NORDHAUS) / c
        print(f"  {label:48s} lambda={lam:4.2f}/yr  "
              f"capture={100*c:5.2f}%  ({fold:4.1f}x below baseline)")
    print("\nCross-check: raw formula at Nordhaus params = "
          f"{100*capture_raw(A_NORDHAUS, LAMBDA_NORDHAUS):.2f}% "
          f"(vs published 2.2% -- see docstring; normalization anchors this).")
    print("Uncaptured share at lambda=3/yr, a=0.07: "
          f"{100*(1-capture_norm(0.07,3.0)):.2f}% (Nordhaus baseline: 97.8%).")


if __name__ == "__main__":
    main()
