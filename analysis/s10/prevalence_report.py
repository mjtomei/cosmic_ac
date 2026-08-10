#!/usr/bin/env python3
"""S10 calibrated prevalence, all chambers, Pangram 4.

WHAT THIS IS

The headline evidence for machine drafting in legislatures. Every number
here rests on a detector whose specificity was MEASURED in the same chamber
it is applied to, not borrowed from a vendor claim or from another chamber.
That is the whole design: a chamber's false-positive rate depends on its own
editorial register, so each chamber buys its own pre-AI control.

Two strata per chamber:
  ctl   60 segments dated <= 2022-06-30 (before ChatGPT shipped 2022-11-30)
  prev  120 segments dated >= 2025-01-01, uniform random, no screen
        stratification, so no reweighting is needed

CALIBRATION. With specificity Sp and sensitivity Se, an observed flag rate
pi relates to true prevalence tau by Rogan-Gladen:

    pi = tau*Se + (1-tau)*(1-Sp)   =>   tau = (pi - (1-Sp)) / (Se - (1-Sp))

When Sp = 1 this collapses to tau = pi/Se. Se is taken from the synthetic
legislative-speech arm (D-synthetic-se), which is in-domain: AI text written
to look like this chamber's business, not generic essays. Sp comes from that
chamber's own control.

MODEL. Everything is Pangram 4. The API defaults to Pangram 3 and the two
disagree materially, so rows are checked for version consistency and any
stragglers are reported rather than silently pooled.

CAVEAT CARRIED IN DATA, NOT IN A COMMENT. Chambers whose transcription
regime changed between the windows carry regime_flag; their prevalence is
printed but held out of the pooled estimate, because a detector cannot
distinguish machine drafting from a change in how the record is produced.

Usage: python prevalence_report.py
"""
import csv
import math
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "pangram_p4_verdicts.csv")
FLAG = ("AI", "Mixed")


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    rows = [r for r in csv.DictReader(open(V)) if r.get("pangram")]
    vers = Counter(r["version"] for r in rows)
    print(f"{len(rows):,} verdicts   versions={dict(vers)}")
    bad = [r for r in rows if r["version"] not in ("4.0", "4.0-web")]
    if bad:
        print(f"  !! {len(bad)} rows not on Pangram 4 — excluded")
        rows = [r for r in rows if r["version"] in ("4.0", "4.0-web")]

    # sensitivity, in-domain, from the synthetic legislative-speech arm
    syn = [r for r in rows if r["stratum"] == "D-synthetic-se"]
    se = (sum(r["pangram"] in FLAG for r in syn) / len(syn)) if syn else None
    print(f"in-domain sensitivity Se = "
          f"{f'{se:.3f} (n={len(syn)})' if se else 'unavailable'}\n")

    ch = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["source"].startswith("expansion") and r["stratum"] in ("ctl", "prev"):
            ch[r["chamber"]][r["stratum"]].append(r)

    print(f"{'chamber':<10s} {'control':>12s} {'Sp':>7s} {'prev n':>7s} "
          f"{'flagged':>9s} {'95% CI':>16s} {'calibrated':>11s}")
    pooled_k = pooled_n = 0
    held = []
    for c in sorted(ch):
        ctl, prev = ch[c]["ctl"], ch[c]["prev"]
        if not prev:
            continue
        fp = sum(r["pangram"] in FLAG for r in ctl)
        sp = (len(ctl) - fp) / len(ctl) if ctl else float("nan")
        k, n = sum(r["pangram"] in FLAG for r in prev), len(prev)
        lo, hi = wilson(k, n)
        tau = ""
        if se and ctl:
            den = se - (1 - sp)
            tau = f"{max(0.0, (k / n - (1 - sp)) / den):.1%}" if den > 0 else "n/a"
        flagreg = any(r.get("regime_flag") for r in prev)
        print(f"{c:<10s} {f'{len(ctl)-fp}/{len(ctl)}':>12s} {sp:>7.3f} "
              f"{n:>7d} {k/n:>8.1%} {f'[{lo:.1%}, {hi:.1%}]':>16s} "
              f"{tau:>11s}" + ("   REGIME-FLAGGED" if flagreg else ""))
        if flagreg:
            held.append(c)
        else:
            pooled_k += k
            pooled_n += n

    if pooled_n:
        lo, hi = wilson(pooled_k, pooled_n)
        print(f"\npooled (excluding {', '.join(held) or 'nothing'}): "
              f"{pooled_k}/{pooled_n} = {pooled_k/pooled_n:.1%} "
              f"[{lo:.1%}, {hi:.1%}]")
    allctl = [r for r in rows if r["stratum"] == "ctl"]
    afp = sum(r["pangram"] in FLAG for r in allctl)
    lo, hi = wilson(len(allctl) - afp, len(allctl))
    print(f"specificity, all controls pooled: {len(allctl)-afp}/{len(allctl)} "
          f"= {(len(allctl)-afp)/len(allctl):.2%} [{lo:.1%}, {hi:.1%}]")

    gen = [r for r in rows if r["arm"] == "genre"]
    if gen:
        print(f"\ngenre arm (federal Canada) — does drafting concentrate in "
              f"scripted business?")
        for g in ("SO31", "DEBATE", "OQ"):
            for s in ("ctl", "prev"):
                sub = [r for r in gen if r["genre"] == g and r["stratum"] == s]
                if not sub:
                    continue
                k, n = sum(r["pangram"] in FLAG for r in sub), len(sub)
                lo, hi = wilson(k, n)
                print(f"  {g:<7s} {s:<5s} {k:>3d}/{n:<3d} = {k/n:>6.1%} "
                      f"[{lo:.1%}, {hi:.1%}]")


if __name__ == "__main__":
    main()
