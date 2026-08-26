#!/usr/bin/env python3
"""Detector-transfer table (evidence-standards survey rec 4a).

The evasion arm attacked one detector (Pangram). Does a rewrite that walked
past Pangram also fool detectors it never saw? Three open detectors are
scored on the same 341 final-run variants + 65 originals as Pangram
(detector_bench_scores.csv) and on 1,255 pre-2022 human controls
(detector_bench_ctl_scores.csv): Fast-DetectGPT curvature, Binoculars, and
the DetectLLM log-rank ratio, all from one committed Falcon-pair pass
(score_multistat.py). Each detector's decision threshold is set where the
human controls put it -- the 5% false-positive operating point (the
detector flags 5% of genuine pre-2022 human speech) -- so "flagged" means
the same thing across detectors. Then:

  originals flagged   how often each open detector catches the un-rewritten
                      machine-flagged text Pangram flagged (its base recall
                      on this material)
  variants flagged    how often it still catches the rewrite
  transfer            a variant that Pangram was walked past -- does the
                      open detector still flag it? per-detector evasion rate

Higher-is-more-machine for fastdetect_d, lrr, binoc means the threshold is
the 95th percentile of controls; logppl is not a detector here. Writes
detector_transfer.txt.

Usage: python detector_transfer.py
"""
import csv
import statistics

DET = [("fastdetect_d", "Fast-DetectGPT", True),
       ("lrr", "log-rank ratio", True),
       ("binoc", "Binoculars", True)]


def load(path):
    return list(csv.DictReader(open(path)))


def pctile(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    ctl = load("detector_bench_ctl_scores.csv")
    var = load("detector_bench_scores.csv")
    variants = [r for r in var if r["speaker"].startswith("variant")]
    origs = [r for r in var if r["speaker"].startswith("original")]
    print(f"controls {len(ctl)}, variants {len(variants)}, "
          f"originals {len(origs)}\n")

    def col(rows, k):
        return [float(r[k]) for r in rows if r.get(k) not in (None, "", "nan")]

    print(f"{'detector':<18}{'thresh(95%ctl)':>15}{'orig flagged':>14}"
          f"{'variant flagged':>16}")
    thr = {}
    for k, name, hi in DET:
        t = pctile(col(ctl, k), 0.95)         # 5% FPR operating point
        thr[k] = t
        of = sum(1 for r in origs if float(r[k]) >= t) / len(origs)
        vf = sum(1 for r in variants if float(r[k]) >= t) / len(variants)
        print(f"{name:<18}{t:>15.4f}{of:>13.1%}{vf:>16.1%}")

    # transfer: of variants, what share does each open detector still flag?
    # (Pangram flagged the originals AI and was walked to Human on the
    # variants by construction, so every open-detector flag here is a catch
    # Pangram missed.)
    print("\nTransfer — a rewrite that beat Pangram, still caught by the open "
          "detector:")
    for k, name, hi in DET:
        vf = sum(1 for r in variants if float(r[k]) >= thr[k]) / len(variants)
        print(f"  {name:<18} still flags {vf:>6.1%} of the Pangram-evading "
              f"variants")

    # union: caught by ANY of the three
    def flagged(r):
        return any(float(r[k]) >= thr[k] for k, _, _ in DET)
    u = sum(1 for r in variants if flagged(r)) / len(variants)
    print(f"\n  any of the three still flags {u:.1%} of variants; "
          f"{1-u:.1%} evade all four detectors at once")

    # by run
    print("\nby run (variant flag rate per detector):")
    runs = sorted({r["speaker"].split("|")[1] for r in variants})
    for run in runs:
        sub = [r for r in variants if r["speaker"].endswith(run)]
        cells = "  ".join(f"{name} {sum(1 for r in sub if float(r[k])>=thr[k])/len(sub):.0%}"
                          for k, name, _ in DET)
        print(f"  {run:<10} n={len(sub):<4} {cells}")


if __name__ == "__main__":
    main()
