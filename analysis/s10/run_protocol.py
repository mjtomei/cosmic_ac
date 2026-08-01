#!/usr/bin/env python3
"""Frozen replication protocol v1.0 — see replication_protocol.md.

Runs the identical instrument, windows, statistic and null on ANY corpus in
the segment schema. Nothing here may be tuned per corpus; the only inputs
are the segment file(s) and the corpus name (which seeds the RNG).

  python run_protocol.py CORPUS_NAME OUT_PREFIX SEGMENTS.jsonl [more.jsonl ...]

Primary statistic (choice-free): equal-word-weight mean log fold-change over
the full Kobak style list. Null: 1,000 frequency-matched placebo instruments.
Secondaries: pooled-ratio threshold sweep, formal-register control,
speech-clustered bootstrap.
"""
import csv
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
PRE_MAX = "2022-12-31"
POST_MIN = "2024-01-01"
N_PLACEBO = 1000
REGISTER = ["honourable", "pursuant", "whereas", "commend", "diligent",
            "prudent", "esteemed", "aforementioned", "notwithstanding",
            "laudable", "steadfast", "exemplary", "gracious", "forthwith",
            "herein"]
INFLECT = ["", "s", "es", "d", "ed", "ing"]


def load_instrument(path="kobak_excess_words.csv"):
    return sorted({r["word"].lower() for r in csv.DictReader(open(path))
                   if r["type"] == "style" and r["word"].isalpha()})


def main():
    name, prefix, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    seed = int(hashlib.sha1(name.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    style = load_instrument()

    pre_c, post_c = Counter(), Counter()
    pre_w = post_w = 0
    turns_pre, turns_post = defaultdict(Counter), defaultdict(Counter)
    for path in files:
        for line in open(path):
            s = json.loads(line)
            if not s.get("scoreable"):
                continue
            d = s["date"]
            if d <= PRE_MAX:
                bucket, tb = "pre", turns_pre
            elif d >= POST_MIN:
                bucket, tb = "post", turns_post
            else:
                continue
            toks = TOKEN_RE.findall(s["text"].lower())
            if bucket == "pre":
                pre_c.update(toks); pre_w += len(toks)
            else:
                post_c.update(toks); post_w += len(toks)
            tb[s["turn_id"]].update(toks)
    print(f"[{name}] seed={seed}  pre {pre_w:,}w  post {post_w:,}w", flush=True)

    # placebo pools: same log2 pre-frequency bucket, excluding instrument,
    # the 120 most frequent words, short and non-alphabetic tokens
    excluded = set(style) | {w for w, _ in pre_c.most_common(120)}
    bucket = defaultdict(list)
    for w, n in pre_c.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        bucket[int(math.log2(n + 1))].append(w)

    def pool_for(b):
        for off in (0, 1, -1, 2, -2, 3, -3, 4, -4):
            if bucket.get(b + off):
                return bucket[b + off]
        return bucket[max(bucket)]

    lr = {}

    def logratio(w):
        if w not in lr:
            lr[w] = math.log(((post_c[w] + 0.5) / post_w) /
                             ((pre_c[w] + 0.5) / pre_w))
        return lr[w]

    # ---- PRIMARY: equal-word-weight mean log fold-change, full list ----
    real = sum(logratio(w) for w in style) / len(style)
    buckets = [int(math.log2(pre_c[w] + 1)) for w in style]
    pools = [pool_for(b) for b in buckets]
    draws = []
    for _ in range(N_PLACEBO):
        draws.append(sum(logratio(random.choice(p)) for p in pools) / len(pools))
    draws.sort()
    exceed = sum(1 for d in draws if d >= real)
    p_primary = exceed / N_PLACEBO
    print(f"PRIMARY mean logFC = {real:+.4f} | placebo median {draws[len(draws)//2]:+.4f} "
          f"p99 {draws[int(0.99*N_PLACEBO)]:+.4f} max {draws[-1]:+.4f} | "
          f"p = {exceed}/{N_PLACEBO}" + ("" if exceed else f" (<{1/N_PLACEBO})"), flush=True)

    # ---- SECONDARY: pooled-ratio threshold sweep ----
    def pooled(ws):
        kp = sum(pre_c[w] for w in ws)
        kq = sum(post_c[w] for w in ws)
        return ((kq / post_w) / (kp / pre_w)) if kp else float("nan")

    sweep = []
    for thr in (1, 2, 5, 10, 20, 50):
        sub = [w for w in style if pre_c[w] / pre_w * 1e5 < thr]
        if len(sub) < 30:
            continue
        r = pooled(sub)
        bs = [int(math.log2(pre_c[w] + 1)) for w in sub]
        ps = [pool_for(b) for b in bs]
        ex = 0
        for _ in range(N_PLACEBO):
            sel = [random.choice(p) for p in ps]
            if pooled(sel) >= r:
                ex += 1
        sweep.append({"threshold_per100k": thr, "n_words": len(sub),
                      "ratio": round(r, 4), "p": ex / N_PLACEBO})
        print(f"  sweep <{thr}/100k: n={len(sub)} ratio={r:.3f} p={ex/N_PLACEBO:.3f}", flush=True)

    # ---- SECONDARY: formal-register control ----
    def stem_count(c, s):
        return sum(c.get(s + suf, 0) for suf in INFLECT)
    rkp = sum(stem_count(pre_c, s) for s in REGISTER)
    rkq = sum(stem_count(post_c, s) for s in REGISTER)
    reg_ratio = (rkq / post_w) / (rkp / pre_w)
    print(f"  formal-register control ratio = {reg_ratio:.3f} (expect ~1)", flush=True)

    # ---- SECONDARY: speech-clustered bootstrap on the full-list pooled ratio ----
    sset = set(style)
    tp = [(sum(c[w] for w in sset), sum(c.values())) for c in turns_pre.values()]
    tq = [(sum(c[w] for w in sset), sum(c.values())) for c in turns_post.values()]
    boots = []
    for _ in range(2000):
        hp = wp = hq = wq = 0
        for _ in range(len(tp)):
            h, w = tp[random.randrange(len(tp))]; hp += h; wp += w
        for _ in range(len(tq)):
            h, w = tq[random.randrange(len(tq))]; hq += h; wq += w
        if hp and wp and wq:
            boots.append((hq / wq) / (hp / wp))
    boots.sort()
    lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]
    print(f"  clustered bootstrap 95% CI (full list ratio): [{lo:.3f}, {hi:.3f}]", flush=True)

    with open(f"{prefix}_protocol.json", "w") as f:
        json.dump({"corpus": name, "seed": seed, "pre_words": pre_w,
                   "post_words": post_w, "n_instrument": len(style),
                   "primary_mean_logFC": round(real, 5),
                   "placebo_median": round(draws[len(draws)//2], 5),
                   "placebo_p99": round(draws[int(0.99*N_PLACEBO)], 5),
                   "placebo_max": round(draws[-1], 5),
                   "primary_p": p_primary, "n_placebo": N_PLACEBO,
                   "sweep": sweep, "formal_register_ratio": round(reg_ratio, 4),
                   "bootstrap_ci": [round(lo, 4), round(hi, 4)]}, f, indent=1)
    print(f"wrote {prefix}_protocol.json", flush=True)


if __name__ == "__main__":
    main()
