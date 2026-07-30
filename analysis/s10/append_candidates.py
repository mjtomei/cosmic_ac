#!/usr/bin/env python3
"""S10: expand the Pangram batch from the eight local statistics.

New strata (deduped against the existing batch):
  A3-fused        — top-N 2025-26 segments by mean AI-direction percentile
                    across all 8 statistics (3 Binoculars pairs low=AI,
                    Fast-DetectGPT/LRR high=AI, 3 classifiers high=AI).
  A5-tail-union   — any 2025-26 segment in ANY statistic's control-
                    calibrated 1% strict tail, not already covered.
  A4-speaker      — for the 3 speakers with the highest share of segments
                    in the top fused decile (min 10 scored segments), their
                    up-to-5 highest-fused remaining segments: the plan's
                    "expand into a flagged speaker's other speeches".

Usage: python append_candidates.py [TOP_N_FUSED]
"""
import csv
import json
import sys
from collections import defaultdict

TOP_N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
REAL = lambda d: d[:4] in ("2025", "2026")
CTL = lambda d: d.startswith("2019")


def load(path, col, low_is_ai):
    out = {}
    for r in csv.DictReader(open(path)):
        v = float(r[col])
        out[r["seg_id"]] = (-v if low_is_ai else v, r["date"])
    return out


def main():
    stats = {
        "binoc_falcon": load("scores_falcon.csv", "score", True),
        "binoc_q17": load("scores_qwen1.7.csv", "score", True),
        "binoc_q8": load("scores_qwen8.csv", "score", True),
        "fastdetect": load("scores_multistat.csv", "fastdetect_d", False),
        "lrr": load("scores_multistat.csv", "lrr", False),
        "cls_hc3": load("scores_cls_hc3roberta.csv", "p_ai", False),
        "cls_openai": load("scores_cls_openai_det.csv", "p_ai", False),
        "cls_radar": load("scores_cls_radar.csv", "p_ai", False),
    }
    ids = sorted(set.intersection(*(set(s) for s in stats.values())))
    new_ids = [i for i in ids if REAL(stats["binoc_falcon"][i][1])]
    ctl_ids = [i for i in ids if CTL(stats["binoc_falcon"][i][1])]

    # fused percentile (AI-direction value, higher = more AI-like)
    pct = defaultdict(float)
    tails = set()
    for name, s in stats.items():
        vals = sorted(s[i][0] for i in new_ids)
        n = len(vals)
        import bisect
        for i in new_ids:
            pct[i] += bisect.bisect_left(vals, s[i][0]) / n / len(stats)
        cvals = sorted(s[i][0] for i in ctl_ids)
        thr = cvals[min(len(cvals) - 1, int(0.99 * len(cvals)))]
        tails |= {i for i in new_ids if s[i][0] > thr}

    fused = sorted(new_ids, key=lambda i: -pct[i])
    batch_ids = {json.loads(l)["seg_id"] for l in open("pangram_batch.jsonl")}
    texts = {json.loads(l)["seg_id"]: json.loads(l)
             for l in open("segments_all.jsonl")}

    def emit(f, i, stratum):
        s = texts[i]
        f.write(json.dumps({"seg_id": i, "stratum": stratum,
                            "date": s["date"], "speaker": s["speaker"],
                            "n_words": s["n_words"], "text": s["text"]},
                           ensure_ascii=False) + "\n")
        batch_ids.add(i)

    n3 = n5 = n4 = 0
    with open("pangram_batch.jsonl", "a") as f:
        for i in fused[:TOP_N]:
            if i not in batch_ids:
                emit(f, i, "A3-fused"); n3 += 1
        for i in sorted(tails):
            if i not in batch_ids:
                emit(f, i, "A5-tail-union"); n5 += 1
        by_sp = defaultdict(list)
        for i in new_ids:
            sp = texts[i]["speaker"]
            if sp:
                by_sp[sp].append(i)
        top_decile = set(fused[:len(fused) // 10])
        ranked_sp = sorted(
            ((len(set(v) & top_decile) / len(v), sp) for sp, v in by_sp.items()
             if len(v) >= 10), reverse=True)[:3]
        for share, sp in ranked_sp:
            print(f"speaker-expansion: {sp} ({share:.0%} of segments in top decile)")
            for i in sorted(by_sp[sp], key=lambda i: -pct[i]):
                if i not in batch_ids and n4 < 15:
                    emit(f, i, "A4-speaker"); n4 += 1

    total = sum(1 for _ in open("pangram_batch.jsonl"))
    words = sum(json.loads(l)["n_words"] for l in open("pangram_batch.jsonl"))
    print(f"added A3-fused {n3}, A5-tail-union {n5}, A4-speaker {n4} "
          f"-> batch {total} segments, {words:,} words")


if __name__ == "__main__":
    main()
