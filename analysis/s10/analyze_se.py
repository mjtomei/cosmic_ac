#!/usr/bin/env python3
"""S10: pilot Se — what fraction of known-AI legislative speech does each
detector pair catch, at thresholds calibrated to the same 2019-control FPR?

This is the in-domain answer to "do bigger models improve Binoculars?"
(pilot-grade: generator is Mistral-7B-Instruct-v0.3, a weak stand-in for
the frontier chat models staff plausibly used — see gen_se_corpus.py).

Usage: python analyze_se.py
  (expects scores_{falcon,qwen1.7,qwen8}.csv and se_scores_*.csv)
"""
import csv
import json


def load(path):
    return {r["seg_id"]: float(r["score"]) for r in csv.DictReader(open(path))}


def pctile(xs, q):
    xs = sorted(xs)
    return xs[max(0, min(len(xs) - 1, int(q * len(xs))))]


def main():
    pairs = ["falcon", "qwen1.7", "qwen8"]
    rows = []
    for p in pairs:
        try:
            corpus = load(f"scores_{p}.csv")
            se = load(f"se_scores_{p}.csv")
        except FileNotFoundError:
            print(f"({p}: scores missing, skipped)")
            continue
        ctl = [v for k, v in corpus.items() if k.startswith("2019")]
        se_scores = sorted(se.values())
        for q in (0.05, 0.01):
            thr = pctile(ctl, q)
            caught = sum(s < thr for s in se_scores)
            rows.append({"pair": p, "calib_fpr": q, "threshold": round(thr, 4),
                         "se_n": len(se_scores), "caught": caught,
                         "Se": round(caught / len(se_scores), 3)})
        med = se_scores[len(se_scores) // 2]
        print(f"{p}: synthetic median score {med:.3f} "
              f"(control median {sorted(ctl)[len(ctl)//2]:.3f})")
    print()
    for r in rows:
        print(r)
    with open("se_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        f.write("# Se = fraction of Mistral-7B-Instruct synthetic legislative "
                "speech scored below the detector's 2019-control-calibrated "
                "threshold; pilot mechanism check, NOT the study Se "
                "(generator-vintage caveat in gen_se_corpus.py)\n")


if __name__ == "__main__":
    main()
