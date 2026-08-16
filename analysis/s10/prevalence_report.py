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

CALIBRATION. With specificity Sp (sensitivity is not estimated), an observed flag rate
pi relates to true prevalence tau by Rogan-Gladen:

    pi = tau*Se + (1-tau)*(1-Sp)   =>   tau = (pi - (1-Sp)) / (Se - (1-Sp))

Se is NOT estimated. With Sp = 1 (measured) and Se <= 1 necessarily,
tau = pi/Se >= pi, so the observed flag rate is a conservative FLOOR on true
prevalence and is what we report. (An earlier version estimated Se from a
small synthetic arm; it was dropped as weaker than the published FNRs it
duplicated.)
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


import banded_prevalence as _BP


def _frac(r):
    """Share of this segment that is machine-written (see banded_prevalence)."""
    return _BP.ai_fraction(r["file"].split(".")[0], r["pangram"],
                           r.get("fraction_ai"))


def wboot(sub, seed=0, n=20000):
    """95% CI for a word-weighted rate, resampling segments.

    Every PREVALENCE rate in this study is word-weighted, so its interval
    cannot be a Wilson interval on segment counts: the estimator is a ratio of
    two random sums (flagged words over total words) that move together, and a
    binomial on segments cannot express that a chamber whose one flagged
    segment ran 900 words is less certain than one whose flag ran 130.
    """
    import random
    if not sub:
        return (0.0, 0.0)
    rng = random.Random(seed)
    m = len(sub)
    out = []
    for _ in range(n):
        w = k = 0
        for _ in range(m):
            x = sub[rng.randrange(m)]
            nw = int(x["n_words"])
            w += nw
            k += nw * _frac(x)
        out.append(k / w if w else 0.0)
    out.sort()
    return (out[int(.025 * n)], out[int(.975 * n)])


def wrate(sub):
    """Fraction-weighted rate: a Mixed segment contributes only its AI share.

    Counting every word of a Mixed segment as machine over-states the pooled
    rate by a third, and not evenly across genres -- Mixed is commoner in the
    mixed-format Government Orders than in the one-minute SO31 set pieces, so
    the binary version flatters the middle of the ladder.
    """
    w = sum(int(r["n_words"]) for r in sub)
    k = sum(int(r["n_words"]) * _frac(r) for r in sub)
    return (k, w, k / w if w else 0.0)


def wilson(k, n, z=1.96):
    """Kept ONLY for counts whose unit really is the document -- specificity
    (a control either fired or it did not) and route-agreement checks. Never
    for a prevalence rate; use wboot."""
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

    ch = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["source"].startswith("expansion") and r["stratum"] in ("ctl", "prev"):
            ch[r["chamber"]][r["stratum"]].append(r)

    print(f"{'chamber':<10s} {'control':>12s} {'Sp':>7s} {'prev n':>7s} "
          f"{'flagged':>9s} {'95% CI':>16s} {'calibrated':>11s}")
    pooled_rows = []
    held = []
    for c in sorted(ch):
        ctl, prev = ch[c]["ctl"], ch[c]["prev"]
        if not prev:
            continue
        fp = sum(r["pangram"] in FLAG for r in ctl)
        sp = (len(ctl) - fp) / len(ctl) if ctl else float("nan")
        kw, w, wr = wrate(prev)
        k, n = sum(r["pangram"] in FLAG for r in prev), len(prev)
        lo, hi = wboot(prev, seed=abs(hash(c)) % 9999)
        # Sp-only floor: with Se unestimated and <=1, tau >= wr-(1-sp).
        tau = f"{max(0.0, wr - (1 - sp)):.1%}" if ctl else ""
        flagreg = any(r.get("regime_flag") for r in prev)
        print(f"{c:<10s} {f'{len(ctl)-fp}/{len(ctl)}':>12s} {sp:>7.3f} "
              f"{n:>7d} {wr:>8.1%} {f'[{lo:.1%}, {hi:.1%}]':>16s} "
              f"{tau:>11s}" + ("   REGIME-FLAGGED" if flagreg else ""))
        if flagreg:
            held.append(c)
        else:
            pooled_rows += prev

    if pooled_rows:
        kw, w, wr = wrate(pooled_rows)
        lo, hi = wboot(pooled_rows, seed=7)
        print(f"\npooled (excluding {', '.join(held) or 'nothing'}): "
              f"{kw:,}/{w:,} words = {wr:.2%} [{lo:.2%}, {hi:.2%}] "
              f"over {len(pooled_rows):,} segments")
        print("  NOTE: long band only. The unbanded figure the study reports "
              "is in banded_prevalence.py, which pools the short and over-360 "
              "bands scored at a matched rate.")
    allctl = [r for r in rows if r["stratum"] == "ctl"]
    afp = sum(r["pangram"] in FLAG for r in allctl)
    lo, hi = wilson(len(allctl) - afp, len(allctl))
    print(f"specificity, all controls pooled: {len(allctl)-afp}/{len(allctl)} "
          f"= {(len(allctl)-afp)/len(allctl):.2%} [{lo:.1%}, {hi:.1%}]")

    gen = [r for r in rows if r["arm"] == "genre"]
    if gen:
        print(f"\ngenre arm (federal Canada) — does drafting concentrate in "
              f"scripted business?")
        # WORD-WEIGHTED, like every other rate in the study. A segment is
        # packer output, not an utterance, and the genres differ sharply in
        # how long their segments are -- SO31 is a one-minute set piece while
        # Government Orders runs twenty. Weighting by segments therefore
        # compares the packer's behaviour across genres as much as the
        # drafting. Intervals are cluster bootstraps over segments: the
        # estimator is a ratio of two random sums, which a Wilson interval on
        # segment counts cannot represent.
        # uses the module-level wboot/wrate; an earlier version defined a
        # second copy here, which shadowed them and left the per-chamber loop
        # calling an unbound name
        print(f"  {'genre':<7s} {'era':<5s} {'flag w':>8s} {'total w':>8s} "
              f"{'rate':>7s} {'95% CI':>16s} {'segs':>5s}")
        for g in ("SO31", "DEBATE", "OQ"):
            for s in ("ctl", "prev"):
                sub = [r for r in gen if r["genre"] == g and r["stratum"] == s]
                if not sub:
                    continue
                kw, w, wr = wrate(sub)
                lo, hi = wboot(sub, seed=abs(hash(g + s)) % 9999)
                print(f"  {g:<7s} {s:<5s} {kw:>8,.0f} {w:>8,} {wr:>6.1%} "
                      f"{'[' + format(100*lo, '.1f') + ', ' + format(100*hi, '.1f') + ']':>16s} "
                      f"{len(sub):>5d}")

        # Cochran-Armitage trend across the three rungs, on SEGMENT counts of
        # the post-AI stratum with doses OQ=0, DEBATE=1, SO31=2. The pairwise
        # Fisher exacts leave the two adjacent steps individually underpowered
        # at 60 segments per cell; the trend test is the ladder's proper
        # monotonicity statistic and is what the write-up quotes.
        cells = []
        for g, x in (("OQ", 0), ("DEBATE", 1), ("SO31", 2)):
            sub = [r for r in gen if r["genre"] == g and r["stratum"] == "prev"]
            if sub:
                cells.append((g, x, len(sub),
                              sum(1 for r in sub if r["pangram"] in FLAG)))
        if len(cells) == 3:
            N = sum(n for _, _, n, _ in cells)
            R = sum(r for _, _, _, r in cells)
            pbar = R / N
            T = sum(x * (r - n * pbar) for _, x, n, r in cells)
            xbar = sum(x * n for _, x, n, _ in cells) / N
            varT = pbar * (1 - pbar) * sum(n * (x - xbar) ** 2
                                           for _, x, n, _ in cells)
            z = T / math.sqrt(varT) if varT > 0 else float("nan")
            p = math.erfc(abs(z) / math.sqrt(2))
            print(f"  Cochran-Armitage trend (segments, doses OQ<DEBATE<SO31): "
                  f"z = {z:.3f}, p = {p:.2e}  "
                  f"[{'/'.join(f'{r}of{n}' for _, _, n, r in cells)}]")


if __name__ == "__main__":
    main()
