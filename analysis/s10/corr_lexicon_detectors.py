#!/usr/bin/env python3
"""S10: does the Tier-1.5 lexicon agree with the model detectors?

Three views (2025-26 corpus; 2019 control as the register check):
  1. Segment-level: detector scores for segments with >=1 AI-lexicon hit
     vs none (hits are sparse, so conditional medians beat raw r).
  2. Segment-level rank correlation (Spearman) between lexicon hits/word
     and each detector statistic, AI-direction aligned.
  3. Speaker-level (>=10k words, 2025-26): mean lexicon rate vs mean
     detector percentile — the powered version.

If lexicon-hit segments score more AI-like in BOTH eras equally, the two
instruments merely share the formulaic-register response; if the
association is stronger in 2025-26 than in the 2019 control, they are
corroborating something era-specific.

Usage: python corr_lexicon_detectors.py
"""
import csv
import json
import math
import re
from collections import defaultdict

from tier15_wiki_signs import PATTERNS
from tier15_quarters_speakers import UP

RX = {n: re.compile(p, 0 if n == "additionally-start" else re.I)
      for n, p in PATTERNS.items() if n in UP}


def nhits(text):
    return sum(len(rx.findall(text)) for rx in RX.values())


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx_, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx_) / len(rx_), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx_, ry))
    vx = sum((a - mx) ** 2 for a in rx_)
    vy = sum((b - my) ** 2 for b in ry)
    return cov / math.sqrt(vx * vy) if vx and vy else 0.0


def med(xs):
    return sorted(xs)[len(xs) // 2]


def main():
    segs = {json.loads(l)["seg_id"]: json.loads(l)
            for l in open("segments_all.jsonl")}
    dets = {
        "binoc_falcon": ("scores_falcon.csv", "score", -1),
        "fastdetect": ("scores_multistat.csv", "fastdetect_d", +1),
        "lrr": ("scores_multistat.csv", "lrr", +1),
        "cls_hc3": ("scores_cls_hc3roberta.csv", "p_ai", +1),
    }
    scores = {}
    for name, (path, col, sign) in dets.items():
        scores[name] = {r["seg_id"]: sign * float(r[col])
                        for r in csv.DictReader(open(path))
                        if r["seg_id"] in segs}

    lex = {i: nhits(s["text"]) for i, s in segs.items() if s.get("scoreable")}
    out_rows = []
    for era, pred in (("2025-26", lambda d: d[:4] in ("2025", "2026")),
                      ("2019ctl", lambda d: d.startswith("2019"))):
        ids = [i for i in lex if pred(segs[i]["date"])
               and all(i in s for s in scores.values())]
        hit = [i for i in ids if lex[i] > 0]
        no = [i for i in ids if lex[i] == 0]
        print(f"\n== {era}: {len(ids)} segments, {len(hit)} with >=1 lexicon hit ==")
        for name in dets:
            s = scores[name]
            m_hit, m_no = med([s[i] for i in hit]), med([s[i] for i in no])
            rho = spearman([lex[i] / segs[i]["n_words"] for i in ids],
                           [s[i] for i in ids])
            # AI-direction: higher = more AI-like for all (sign applied)
            print(f"  {name:14s} median AI-dir score: hits {m_hit:8.3f} "
                  f"vs none {m_no:8.3f}   Spearman(lex-rate) {rho:+.3f}")
            out_rows.append({"era": era, "detector": name,
                             "median_hitsegs": round(m_hit, 4),
                             "median_nohitsegs": round(m_no, 4),
                             "spearman": round(rho, 4),
                             "n": len(ids), "n_hitsegs": len(hit)})

    # speaker level, 2025-26
    by_sp = defaultdict(list)
    for i in lex:
        if segs[i]["date"][:4] in ("2025", "2026") and segs[i]["speaker"]:
            by_sp[segs[i]["speaker"]].append(i)
    sps = [sp for sp, v in by_sp.items()
           if sum(segs[i]["n_words"] for i in v) >= 10000]
    lex_rate, det_mean = [], []
    for sp in sps:
        ids = [i for i in by_sp[sp] if i in scores["binoc_falcon"]]
        w = sum(segs[i]["n_words"] for i in ids)
        lex_rate.append(sum(lex[i] for i in ids) / w * 1e5)
        det_mean.append(sum(scores["binoc_falcon"][i] for i in ids) / len(ids))
    rho_sp = spearman(lex_rate, det_mean)
    print(f"\n== speaker level (2025-26, {len(sps)} speakers >=10k words) ==")
    print(f"  lexicon rate vs mean binoc-falcon (AI-dir): Spearman {rho_sp:+.3f}")

    with open("corr_lexicon_detectors.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
        f.write(f"# speaker-level Spearman (2025-26, n={len(sps)}): {rho_sp:+.3f}; "
                "AI-direction aligned (binoc negated)\n")


if __name__ == "__main__":
    main()
