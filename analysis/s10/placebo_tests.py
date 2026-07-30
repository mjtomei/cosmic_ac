#!/usr/bin/env python3
"""S10: significance battery for the Tier-1.5 lexicon shift.

Pre = 2019-2022, post = 2024-2026 (2023 excluded as the transition year;
the quarterly series puts adoption onset at 2023Q4).

1. PLACEBO LEXICONS: the single-word subset of the AI list (counted as
   stem+inflections from word counters) vs 1,000 random word sets matched
   on pre-period frequency band (same log2 bucket, function words and
   AI-list words excluded). Empirical p = share of placebo sets whose
   post/pre rate ratio >= the AI set's.
2. FORMAL-REGISTER CONTROL: legislative-formality words, same statistic —
   distinguishes AI-register rise from formality inflation.
3. SPEECH-CLUSTERED BOOTSTRAP: 2,000 resamples of whole turns for the AI
   set's ratio CI (words burst within speeches; Poisson understates
   variance).
4. PER-SPEAKER EXACT POISSON: post-hits vs expectation under the
   speaker's own pre rate, Benjamini-Hochberg across speakers.

Usage: python placebo_tests.py    (writes placebo_tests.csv)
"""
import json
import math
import random
import re
from collections import Counter, defaultdict

random.seed(20260730)

AI_STEMS = ["delve", "tapestry", "testament", "pivotal", "robust", "boast",
            "garner", "meticulous", "intricate", "interplay", "nestled",
            "renowned", "groundbreaking", "bolster", "showcase", "foster",
            "underscore"]
REGISTER_STEMS = ["honourable", "pursuant", "whereas", "commend", "diligent",
                  "prudent", "esteemed", "aforementioned", "notwithstanding",
                  "laudable", "steadfast", "exemplary", "gracious",
                  "forthwith", "herein"]
INFLECT = ["", "s", "es", "d", "ed", "ing"]
TOKEN_RE = re.compile(r"[a-z']+")
PRE = {"2018", "2019", "2020", "2021", "2022"}
POST = {"2024", "2025", "2026"}


def stem_count(counter, stem):
    return sum(counter.get(stem + suf, 0) for suf in INFLECT)


def set_ratio(pre_c, post_c, pre_w, post_w, stems):
    kp = sum(stem_count(pre_c, s) for s in stems)
    kq = sum(stem_count(post_c, s) for s in stems)
    rp = kp / pre_w * 1e5
    rq = kq / post_w * 1e5
    return (rq / rp if rp else float("inf")), kp, kq


def main():
    turns_pre, turns_post = defaultdict(list), defaultdict(list)
    pre_c, post_c = Counter(), Counter()
    pre_w = post_w = 0
    sp_pre, sp_post = defaultdict(Counter), defaultdict(Counter)
    sp_wpre, sp_wpost = defaultdict(int), defaultdict(int)

    for path in ("segments_all.jsonl", "segments_60th.jsonl", "segments_59th.jsonl"):
        for line in open(path):
            s = json.loads(line)
            y = s["date"][:4]
            if not s.get("scoreable") or (y not in PRE and y not in POST):
                continue
            toks = TOKEN_RE.findall(s["text"].lower())
            c = Counter(toks)
            if y in PRE:
                pre_c.update(c); pre_w += len(toks)
                turns_pre[s["turn_id"]].append(c)
                if s["speaker"]:
                    sp_pre[s["speaker"]].update(c)
                    sp_wpre[s["speaker"]] += len(toks)
            else:
                post_c.update(c); post_w += len(toks)
                turns_post[s["turn_id"]].append(c)
                if s["speaker"]:
                    sp_post[s["speaker"]].update(c)
                    sp_wpost[s["speaker"]] += len(toks)

    ai_ratio, kp, kq = set_ratio(pre_c, post_c, pre_w, post_w, AI_STEMS)
    print(f"AI word-subset: pre {kp} hits ({kp/pre_w*1e5:.1f}/100k), "
          f"post {kq} ({kq/post_w*1e5:.1f}/100k) -> ratio {ai_ratio:.2f}x")
    reg_ratio, rkp, rkq = set_ratio(pre_c, post_c, pre_w, post_w, REGISTER_STEMS)
    print(f"formal-register control: pre {rkp} ({rkp/pre_w*1e5:.1f}), "
          f"post {rkq} ({rkq/post_w*1e5:.1f}) -> ratio {reg_ratio:.2f}x")

    # placebo: frequency-matched random stems
    top_func = {w for w, _ in pre_c.most_common(120)}
    excluded = set(AI_STEMS) | top_func
    bucket = defaultdict(list)
    for w, n in pre_c.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        bucket[int(math.log2(n + 1))].append(w)
    ai_buckets = [int(math.log2(stem_count(pre_c, s) + 1)) for s in AI_STEMS]
    N = 1000
    exceed = 0
    ratios = []
    for _ in range(N):
        stems = []
        for b in ai_buckets:
            pool = bucket.get(b) or bucket.get(b + 1) or bucket.get(b - 1)
            stems.append(random.choice(pool))
        r, _, _ = set_ratio(pre_c, post_c, pre_w, post_w, stems)
        ratios.append(r)
        if r >= ai_ratio:
            exceed += 1
    ratios.sort()
    print(f"placebo null (n={N}, freq-matched): median "
          f"{ratios[N//2]:.2f}x, p95 {ratios[int(0.95*N)]:.2f}x, "
          f"p99 {ratios[int(0.99*N)]:.2f}x")
    print(f"empirical p(AI ratio >= {ai_ratio:.2f}) = {exceed}/{N} "
          f"= {exceed/N:.3f}")

    # speech-clustered bootstrap CI for the AI ratio
    tp = [sum((c for c in v), Counter()) for v in turns_pre.values()]
    tq = [sum((c for c in v), Counter()) for v in turns_post.values()]
    tp_hits = [sum(stem_count(c, s) for s in AI_STEMS) for c in tp]
    tp_words = [sum(c.values()) for c in tp]
    tq_hits = [sum(stem_count(c, s) for s in AI_STEMS) for c in tq]
    tq_words = [sum(c.values()) for c in tq]
    boots = []
    for _ in range(2000):
        ip = [random.randrange(len(tp)) for _ in tp]
        iq = [random.randrange(len(tq)) for _ in tq]
        hp = sum(tp_hits[i] for i in ip); wp = sum(tp_words[i] for i in ip)
        hq = sum(tq_hits[i] for i in iq); wq = sum(tq_words[i] for i in iq)
        if hp:
            boots.append((hq / wq) / (hp / wp))
    boots.sort()
    print(f"speech-clustered bootstrap 95% CI for AI ratio: "
          f"[{boots[int(0.025*len(boots))]:.2f}, "
          f"{boots[int(0.975*len(boots))]:.2f}]")

    # per-speaker exact Poisson (normal approx to Poisson tail, BH-corrected)
    rows = []
    for sp in sp_post:
        if sp_wpre.get(sp, 0) < 20000 or sp_wpost[sp] < 20000:
            continue
        k_pre = sum(stem_count(sp_pre[sp], s) for s in AI_STEMS)
        k_post = sum(stem_count(sp_post[sp], s) for s in AI_STEMS)
        mu = max(0.25, k_pre) / sp_wpre[sp] * sp_wpost[sp]
        z = (k_post - mu) / math.sqrt(mu)
        p = 0.5 * math.erfc(z / math.sqrt(2))      # upper tail
        rows.append((p, sp, k_pre, k_post, mu, z))
    rows.sort()
    m = len(rows)
    print(f"\nper-speaker Poisson (pre-rate -> post expectation), "
          f"BH across {m} speakers:")
    for i, (p, sp, k0, k1, mu, z) in enumerate(rows[:8], 1):
        sig = "SIG" if p <= 0.05 * i / m else "   "
        print(f"  {sig} {sp:22s} pre {k0:3d} -> post {k1:3d} "
              f"(exp {mu:5.1f})  z={z:+5.1f}  p={p:.2e}")

    with open("placebo_tests.csv", "w") as f:
        f.write("test,statistic,value\n")
        f.write(f"ai_word_subset_ratio,post/pre,{ai_ratio:.3f}\n")
        f.write(f"formal_register_ratio,post/pre,{reg_ratio:.3f}\n")
        f.write(f"placebo_median,ratio,{ratios[N//2]:.3f}\n")
        f.write(f"placebo_p99,ratio,{ratios[int(0.99*N)]:.3f}\n")
        f.write(f"empirical_p,p,{exceed/N:.4f}\n")
        f.write(f"bootstrap_ci_lo,ratio,{boots[int(0.025*len(boots))]:.3f}\n")
        f.write(f"bootstrap_ci_hi,ratio,{boots[int(0.975*len(boots))]:.3f}\n")
        f.write("# pre 2018-22 (full 59th+60th baseline), post 2024-26 "
                "(2023 transition excluded); single-word AI subset, "
                "stem+inflection counting; NOTE: extending the baseline "
                "from 2019-22 to 2018-22 moved ratio 2.28->2.00 and p "
                "0.020->0.035 -- within-NB evidence is ceiling-limited by "
                "the placebo null (single-chamber topic drift), not by n; "
                "the path to smaller p is cross-legislature replication\n")


if __name__ == "__main__":
    main()
