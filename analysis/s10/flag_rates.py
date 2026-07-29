#!/usr/bin/env python3
"""S10 pilot: flag rates with Wilson CIs + Rogan-Gladen reading.

Writes flag_rates.csv. The 2019 control supplies the in-domain
false-positive floor (1-Sp) per threshold; the corrected prevalence
tau-hat = (pi-hat + Sp - 1)/(Se + Sp - 1) is computed for a range of
hypothetical Se values because no in-domain Se measurement exists yet
(the known-AI reference corpus is future work). Where pi-hat < 1-Sp the
point estimate truncates to zero; we also report a rough upper bound using
the Wilson upper limit of pi-hat and the Wilson lower limit of (1-Sp).

CAVEAT recorded here and in PILOT.md: the control shows the score
distribution DRIFTS between eras (2019 flags higher than 2025-26), so Sp
measured in 2019 need not equal Sp in 2025-26 text. The bound assumes
era-stable Sp, which this very data challenges. Treat as illustrative.

Usage: python flag_rates.py SCORES_CSV
"""
import csv
import math
import sys

ACC = 0.9015310749276843
FPR = 0.8536432310785527


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def main():
    rows = list(csv.DictReader(open(sys.argv[1])))
    for r in rows:
        r["score"] = float(r["score"])
    ctl = [r for r in rows if r["date"].startswith("2019")]
    new = [r for r in rows if r["date"][:4] >= "2025"]

    out = []
    for name, thr in [("accuracy", ACC), ("low-fpr", FPR)]:
        k_c = sum(r["score"] < thr for r in ctl)
        k_n = sum(r["score"] < thr for r in new)
        lo_c, hi_c = wilson(k_c, len(ctl))
        lo_n, hi_n = wilson(k_n, len(new))
        rec = {
            "threshold": name,
            "ctl_2019_flag": f"{k_c}/{len(ctl)}", "ctl_rate": round(k_c / len(ctl), 4),
            "ctl_wilson95": f"[{lo_c:.4f},{hi_c:.4f}]",
            "new_2025_flag": f"{k_n}/{len(new)}", "new_rate": round(k_n / len(new), 4),
            "new_wilson95": f"[{lo_n:.4f},{hi_n:.4f}]",
        }
        # Rogan-Gladen: pi = tau*Se + (1-tau)*(1-Sp); Sp est from control
        for se in (0.95, 0.85, 0.70):
            sp = 1 - k_c / len(ctl)
            tau = (k_n / len(new) + sp - 1) / (se + sp - 1)
            # rough upper bound: pi at Wilson-upper, (1-Sp) at Wilson-lower
            tau_up = (hi_n - lo_c) / (se - lo_c)
            rec[f"tau_hat_Se{se}"] = round(max(0.0, tau), 4)
            rec[f"tau_upper_Se{se}"] = round(max(0.0, tau_up), 4)
        out.append(rec)

    with open("flag_rates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
        f.write("# Sp from 2019 control (era-stability assumption is "
                "questionable -- see PILOT.md); Se hypothetical, no in-domain "
                "measurement yet; tau_upper = (pi_wilson_hi - fpfloor_wilson_lo)"
                "/(Se - fpfloor_wilson_lo), truncated at 0\n")
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
