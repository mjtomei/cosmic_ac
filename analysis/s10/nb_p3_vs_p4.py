#!/usr/bin/env python3
"""What the model-tier defect cost us: New Brunswick on Pangram 3 vs Pangram 4.

The 2026-07 tier-4 run passed no model parameter to the Pangram API and
silently took the default, which is Pangram 3 (version 3.3.2), not Pangram 4.
Every web-scored chamber ran on Pangram 4. So NB's 658 verdicts were a
different instrument from everything they were being compared against.

This scores byte-identical text on both and reports what changed. The text is
the stored input from the P3 run itself, so nothing but the model differs.

Two things matter in the output:

  1. THE CONTROL STRATUM. C-control-2019 is pre-AI text; every flag there is
     a false positive. This is the specificity comparison, and it is the one
     that decides whether the P3 numbers were usable at all.

  2. DIRECTION OF DISAGREEMENT. If P4 flags strictly more, the old numbers
     were an undercount and the tail adjudication missed AI. If it flags
     fewer, the opposite. A symmetric churn would mean neither run is stable.

Usage: python nb_p3_vs_p4.py
"""
import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    p3 = {}
    for line in open(os.path.join(HERE, "pangram_results.jsonl")):
        d = json.loads(line)
        p3["nb_" + str(d["seg_id"])] = {
            "v": d["response"].get("prediction_short"),
            "stratum": d.get("stratum", ""),
            "frac": d["response"].get("fraction_ai")}

    p4 = {}
    path = os.path.join(HERE, "pangram_p4_verdicts.csv")
    for r in csv.DictReader(open(path)):
        if r["source"] == "nb_rescore" and r.get("pangram"):
            p4[r["file"]] = {"v": r["pangram"], "stratum": r["stratum"],
                             "frac": r.get("fraction_ai")}

    both = sorted(set(p3) & set(p4))
    print(f"segments scored on both models: {len(both):,} "
          f"(P3 {len(p3):,}, P4 {len(p4):,})\n")
    if not both:
        return

    print("=== overall ===")
    a = Counter(p3[k]["v"] for k in both)
    b = Counter(p4[k]["v"] for k in both)
    for lab in ("AI", "Mixed", "Human"):
        print(f"  {lab:<6s} P3 {a[lab]:>4d}  ->  P4 {b[lab]:>4d}  "
              f"({b[lab] - a[lab]:+d})")
    agree = sum(1 for k in both if p3[k]["v"] == p4[k]["v"])
    print(f"  exact agreement: {agree}/{len(both)} ({agree / len(both):.0%})")

    print("\n=== cross-tab (P3 down, P4 across) ===")
    ct = Counter((p3[k]["v"], p4[k]["v"]) for k in both)
    labs = ["AI", "Mixed", "Human"]
    print(f"  {'':<8s}" + "".join(f"{l:>8s}" for l in labs))
    for r in labs:
        print(f"  {r:<8s}" + "".join(f"{ct[(r, c)]:>8d}" for c in labs))

    print("\n=== by stratum (AI+Mixed flag rate) ===")
    st = defaultdict(lambda: [0, 0, 0])
    for k in both:
        s = p3[k]["stratum"]
        st[s][0] += 1
        st[s][1] += p3[k]["v"] in ("AI", "Mixed")
        st[s][2] += p4[k]["v"] in ("AI", "Mixed")
    print(f"  {'stratum':<22s} {'n':>4s} {'P3':>12s} {'P4':>12s}")
    for s in sorted(st):
        n, x3, x4 = st[s]
        note = "   <-- PRE-AI: flags here are false positives" \
            if s.startswith("C-control") else ""
        print(f"  {s:<22s} {n:>4d} {x3 / n:>11.1%} {x4 / n:>11.1%}{note}")

    ctl = [k for k in both if p3[k]["stratum"].startswith("C-control")]
    if ctl:
        f3 = sum(p3[k]["v"] in ("AI", "Mixed") for k in ctl)
        f4 = sum(p4[k]["v"] in ("AI", "Mixed") for k in ctl)
        print(f"\n=== specificity on the pre-AI control (n={len(ctl)}) ===")
        for nm, f in (("Pangram 3", f3), ("Pangram 4", f4)):
            lo, hi = wilson(len(ctl) - f, len(ctl))
            print(f"  {nm}: {len(ctl) - f}/{len(ctl)} correct "
                  f"= {(len(ctl) - f) / len(ctl):.1%}  "
                  f"[{lo:.1%}, {hi:.1%}]  ({f} false positive"
                  f"{'s' if f != 1 else ''})")

    out = os.path.join(HERE, "nb_p3_vs_p4.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["seg", "stratum", "p3", "p4", "p3_frac_ai", "p4_frac_ai",
                    "changed"])
        for k in both:
            w.writerow([k, p3[k]["stratum"], p3[k]["v"], p4[k]["v"],
                        p3[k]["frac"], p4[k]["frac"],
                        int(p3[k]["v"] != p4[k]["v"])])
    print(f"\nwrote {os.path.basename(out)}")


if __name__ == "__main__":
    main()
