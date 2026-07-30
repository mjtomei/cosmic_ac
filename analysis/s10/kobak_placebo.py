#!/usr/bin/env python3
"""S10: replication of the lexicon shift on an INDEPENDENT frozen
instrument — Kobak et al.'s excess-vocabulary list.

Instrument: the type=="style" words from Kobak, Gonzalez-Marquez, Horvat &
Berens (arXiv:2406.07016; berenslab/llm-excess-vocab
results/excess_words.csv, fetched 2026-07-30). Derived from 15M PubMed
abstracts, before and entirely independent of this corpus and of the
Wikipedia editors' list — so the instrument-circularity objection to the
Tier-1.5 result does not apply to it.

Test: identical to placebo_tests.py — literal word forms (their list
already enumerates inflections as separate entries), pre 2018-2022 vs
post 2024-2026, 1,000 frequency-matched placebo word sets, speech-
clustered bootstrap. Overlap with the Wikipedia-derived set exists
(delve/underscore/showcase...) — this is a second instrument, not an
independent p to Fisher-combine within NB.

Usage: python kobak_placebo.py    (writes kobak_placebo.csv)
"""
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict

random.seed(20260730)
TOKEN_RE = re.compile(r"[a-z']+")
PRE = {"2018", "2019", "2020", "2021", "2022"}
POST = {"2024", "2025", "2026"}


def main():
    style = [r["word"].lower() for r in csv.DictReader(open("kobak_excess_words.csv"))
             if r["type"] == "style" and r["word"].isalpha()]
    print(f"Kobak style words: {len(style)}")

    pre_c, post_c = Counter(), Counter()
    pre_w = post_w = 0
    turns_pre, turns_post = defaultdict(Counter), defaultdict(Counter)
    for path in ("segments_all.jsonl", "segments_60th.jsonl",
                 "segments_59th.jsonl"):
        for line in open(path):
            s = json.loads(line)
            y = s["date"][:4]
            if not s.get("scoreable") or (y not in PRE and y not in POST):
                continue
            toks = TOKEN_RE.findall(s["text"].lower())
            c = Counter(toks)
            if y in PRE:
                pre_c.update(c); pre_w += len(toks)
                turns_pre[s["turn_id"]].update(c)
            else:
                post_c.update(c); post_w += len(toks)
                turns_post[s["turn_id"]].update(c)

    wordset = set(style)
    kp = sum(pre_c[w] for w in wordset)
    kq = sum(post_c[w] for w in wordset)
    ratio = (kq / post_w) / (kp / pre_w)
    print(f"Kobak-style set: pre {kp} ({kp/pre_w*1e5:.1f}/100k), "
          f"post {kq} ({kq/post_w*1e5:.1f}/100k) -> ratio {ratio:.3f}x")

    top_func = {w for w, _ in pre_c.most_common(120)}
    bucket = defaultdict(list)
    for w, n in pre_c.items():
        if w in wordset or w in top_func or len(w) < 4 or not w.isalpha():
            continue
        bucket[int(math.log2(n + 1))].append(w)
    buckets = [int(math.log2(pre_c[w] + 1)) for w in wordset]
    N = 1000
    exceed = 0
    ratios = []
    for _ in range(N):
        ws = []
        for b in buckets:
            pool = bucket.get(b) or bucket.get(b + 1) or bucket.get(b - 1) \
                or bucket.get(b + 2)
            ws.append(random.choice(pool))
        rkp = sum(pre_c[w] for w in ws)
        rkq = sum(post_c[w] for w in ws)
        r = (rkq / post_w) / (rkp / pre_w) if rkp else float("inf")
        ratios.append(r)
        if r >= ratio:
            exceed += 1
    ratios.sort()
    print(f"placebo null: median {ratios[N//2]:.3f}, p95 "
          f"{ratios[int(0.95*N)]:.3f}, p99 {ratios[int(0.99*N)]:.3f}")
    print(f"empirical p = {exceed}/{N} = {exceed/N:.3f}")

    tp = list(turns_pre.values())
    tq = list(turns_post.values())
    tp_h = [sum(c[w] for w in wordset) for c in tp]
    tp_w = [sum(c.values()) for c in tp]
    tq_h = [sum(c[w] for w in wordset) for c in tq]
    tq_w = [sum(c.values()) for c in tq]
    boots = []
    for _ in range(2000):
        hp = wp = hq = wq = 0
        for _ in tp:
            i = random.randrange(len(tp)); hp += tp_h[i]; wp += tp_w[i]
        for _ in tq:
            i = random.randrange(len(tq)); hq += tq_h[i]; wq += tq_w[i]
        if hp:
            boots.append((hq / wq) / (hp / wp))
    boots.sort()
    lo, hi = boots[int(0.025*len(boots))], boots[int(0.975*len(boots))]
    print(f"speech-clustered bootstrap 95% CI: [{lo:.3f}, {hi:.3f}]")

    with open("kobak_placebo.csv", "w") as f:
        f.write("test,value\n")
        f.write(f"n_style_words,{len(style)}\n")
        f.write(f"ratio,{ratio:.4f}\n")
        f.write(f"placebo_median,{ratios[N//2]:.4f}\n")
        f.write(f"placebo_p99,{ratios[int(0.99*N)]:.4f}\n")
        f.write(f"empirical_p,{exceed/N:.4f}\n")
        f.write(f"bootstrap_ci,{lo:.4f}..{hi:.4f}\n")
        f.write("# Kobak et al. style-word list (arXiv:2406.07016), literal "
                "forms; pre 2018-22 post 2024-26; independent frozen "
                "instrument vs the Wikipedia-derived set\n")


if __name__ == "__main__":
    main()
