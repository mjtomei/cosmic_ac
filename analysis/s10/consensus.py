#!/usr/bin/env python3
"""S10: multi-detector consensus with control-calibrated operating points.

Each detector's threshold is set at a chosen percentile of ITS OWN 2019
pre-ChatGPT control distribution (so every detector runs at the same
by-construction false-positive rate on the control). We then measure, on
2025-26 and on the control:
  - per-detector flag rates,
  - k-of-n consensus flag rates,
  - the expected consensus rate if detector errors were independent.
The control's consensus rate IS the consensus instrument's (1 - Sp); the
question "does consensus kill false positives?" is answered by whether the
2025-26 consensus rate exceeds that floor, and by whether the control
consensus rate approaches the independence product (it will not if the
detectors share failure modes, e.g. ceremonial formula).

Also dumps the 2025-26 consensus hit list with text snippets for eyeballing.

Usage: python consensus.py OUT_CSV SCORES_CSV [SCORES_CSV ...]
"""
import csv
import json
import sys


def load(path):
    rows = {}
    for r in csv.DictReader(open(path)):
        rows[r["seg_id"]] = (float(r["score"]), r)
    return rows


def pctile(xs, q):
    xs = sorted(xs)
    i = max(0, min(len(xs) - 1, int(q * len(xs))))
    return xs[i]


def main():
    out_csv, paths = sys.argv[1], sys.argv[2:]
    dets = {p.split("scores_")[-1].replace(".csv", ""): load(p) for p in paths}
    names = list(dets)
    ids = sorted(set.intersection(*(set(d) for d in dets.values())))
    ctl = [i for i in ids if i.startswith("2019")]
    new = [i for i in ids if i[:4] >= "2025"]
    print(f"detectors: {names}; n={len(ids)} ({len(ctl)} control, {len(new)} 2025-26)\n")

    seg_text = {}
    try:
        seg_text = {json.loads(l)["seg_id"]: json.loads(l)["text"]
                    for l in open("segments_all.jsonl")}
    except FileNotFoundError:
        pass

    recs = []
    for q in (0.05, 0.01):
        thr = {n: pctile([dets[n][i][0] for i in ctl], q) for n in names}
        flags = {n: {i for i in ids if dets[n][i][0] < thr[n]} for n in names}
        for era, era_ids in (("2019-ctl", ctl), ("2025-26", new)):
            per = {n: len(flags[n] & set(era_ids)) / len(era_ids) for n in names}
            inter = set(era_ids)
            for n in names:
                inter &= flags[n]
            k_all = len(inter) / len(era_ids)
            indep = 1.0
            for n in names:
                indep *= per[n]
            rec = {"calib_fpr": q, "era": era,
                   **{f"rate_{n}": round(per[n], 4) for n in names},
                   "rate_all_agree": round(k_all, 4),
                   "rate_if_independent": round(indep, 6),
                   "n_all_agree": len(inter)}
            recs.append(rec)
            print(rec)
        # consensus hit list on 2025-26 at this operating point
        inter_new = set(new)
        for n in names:
            inter_new &= flags[n]
        if q == 0.05 and inter_new:
            print(f"\n-- 2025-26 segments flagged by ALL detectors (calib_fpr={q}) --")
            meta = dets[names[0]]
            for i in sorted(inter_new,
                            key=lambda i: sum(dets[n][i][0] for n in names)):
                r = meta[i][1]
                scores = " ".join(f"{n}={dets[n][i][0]:.3f}" for n in names)
                print(f"{r['date']} | {r['speaker'][:22]:22s} | orig={r['orig_frac']} | {scores}")
                if i in seg_text:
                    print(f"   {seg_text[i][:170]}")
            print()

    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
        f.write("# thresholds per detector at the 2019-control percentile "
                "(calib_fpr); control rate_all_agree = consensus (1-Sp); "
                "rate_if_independent = product of per-detector rates\n")


if __name__ == "__main__":
    main()
