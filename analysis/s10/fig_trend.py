#!/usr/bin/env python3
"""S10: AI-lexicon trend figure + trend-shape tests.

Panel A: yearly rates 2018-2026, both instruments (Wikipedia-signs
33-pattern set; Kobak rare-style words), each indexed to its own
pre-2023 mean = 100 so shapes compare on one axis.
Panel B: quarterly Kobak-rare rate per 100k with Poisson 95% whiskers
(quarters with >=50k words), ChatGPT release marked.

Tests printed + saved:
  - Mann-Kendall monotone trend on the Kobak-rare yearly series.
  - Interrupted time series: weighted LS on log quarterly rates,
    log r = a + b*t + c*(t-2023)+, break pre-specified (ChatGPT);
    empirical p for c from 1,000 frequency-matched placebo word sets
    run through the identical fit.

Usage: python fig_trend.py   (writes the-ai-lexicon-trend.png, trend_series.csv)
"""
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tier15_wiki_signs import PATTERNS
from tier15_quarters_speakers import UP

random.seed(20260730)
TOKEN_RE = re.compile(r"[a-z']+")
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED = "#0b0b0b", "#52514e"
RX = {n: re.compile(p, 0 if n == "additionally-start" else re.I)
      for n, p in PATTERNS.items() if n in UP}


def main():
    q_tok, q_words, q_text = defaultdict(Counter), defaultdict(int), defaultdict(list)
    for path in ("segments_all.jsonl", "segments_60th.jsonl",
                 "segments_59th.jsonl", "segments_61s1.jsonl"):
        for line in open(path):
            s = json.loads(line)
            y = s["date"][:4]
            if not s.get("scoreable") or not y.isdigit():
                continue
            qtr = int(y) + (int(s["date"][5:7]) - 1) // 3 * 0.25
            toks = TOKEN_RE.findall(s["text"].lower())
            q_tok[qtr].update(toks)
            q_words[qtr] += len(toks)
            q_text[qtr].append(s["text"])

    style = [r["word"].lower() for r in
             csv.DictReader(open("kobak_excess_words.csv"))
             if r["type"] == "style" and r["word"].isalpha()]
    pre_c = Counter()
    pre_w = 0
    for q, c in q_tok.items():
        if q < 2023:
            pre_c.update(c)
            pre_w += q_words[q]
    rare = [w for w in style if pre_c[w] / pre_w * 1e5 < 5.0]
    rset = set(rare)

    # quarterly Kobak-rare series
    quarters = sorted(q for q in q_words if q_words[q] >= 50000)
    q_rate, q_ci = {}, {}
    for q in quarters:
        k = sum(q_tok[q][w] for w in rset)
        r = k / q_words[q] * 1e5
        q_rate[q] = r
        q_ci[q] = 1.96 * math.sqrt(max(k, 1)) / q_words[q] * 1e5

    # yearly series, both instruments
    years = sorted({int(q) for q in quarters})
    y_kob, y_wiki, y_words = {}, {}, {}
    for y in years:
        ws = sum(q_words[q] for q in q_words if int(q) == y)
        text = "\n".join(t for q in q_text if int(q) == y for t in q_text[q])
        nw = len(text.split())
        y_words[y] = ws
        k = sum(q_tok[q][w] for q in q_tok if int(q) == y for w in rset)
        y_kob[y] = (k / ws * 1e5, 1.96 * math.sqrt(max(k, 1)) / ws * 1e5)
        kk = sum(len(rx.findall(text)) for rx in RX.values())
        y_wiki[y] = (kk / nw * 1e5, 1.96 * math.sqrt(max(kk, 1)) / nw * 1e5)

    kob_pre = np.mean([y_kob[y][0] for y in years if y < 2023])
    wiki_pre = np.mean([y_wiki[y][0] for y in years if y < 2023])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.2, 6.4), dpi=150,
                                   sharex=True, facecolor="#fcfcfb")
    for ax in (ax1, ax2):
        ax.set_facecolor("#fcfcfb")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color("#d8d7d2")
        ax.tick_params(colors=MUTED, labelsize=8.5)
        ax.grid(axis="y", color="#e8e7e2", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.axvline(2022.92, color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
    ax1.text(2022.86, 218, "ChatGPT\nreleased", ha="right", va="top",
             fontsize=8, color=MUTED)

    xs = [y + 0.5 for y in years]
    for series, base, color, label, dy in (
            (y_kob, kob_pre, BLUE, "Kobak excess-vocabulary (rare style words)", 8),
            (y_wiki, wiki_pre, ORANGE, "Wikipedia signs-of-AI-writing set", -14)):
        idx = [series[y][0] / base * 100 for y in years]
        ci = [series[y][1] / base * 100 for y in years]
        ax1.errorbar(xs, idx, yerr=ci, color=color, linewidth=2,
                     marker="o", markersize=5, capsize=2, elinewidth=1)
        ax1.annotate(label, (xs[-1], idx[-1]), xytext=(8, dy),
                     textcoords="offset points", fontsize=8.5, color=color,
                     ha="left", va="center")
    ax1.axhline(100, color="#d8d7d2", linewidth=1)
    ax1.set_ylabel("rate, indexed\n(pre-2023 mean = 100)", fontsize=9,
                   color=MUTED)
    ax1.set_title("AI-preferred vocabulary in NB Hansard, 2018–2026 — "
                  "two independent instruments, one shape",
                  fontsize=10.5, color=INK, loc="left", pad=10)
    ax1.set_xlim(2018.2, 2028.4)

    qx = [q + 0.125 for q in quarters]
    ax2.errorbar(qx, [q_rate[q] for q in quarters],
                 yerr=[q_ci[q] for q in quarters], color=BLUE, linewidth=1.8,
                 marker="o", markersize=4, capsize=2, elinewidth=0.9)
    ax2.set_ylabel("Kobak rare-style words\nper 100k (quarterly)",
                   fontsize=9, color=MUTED)
    ax2.set_xlabel("")
    ax2.set_xticks([y + 0.5 for y in years])
    ax2.set_xticklabels(years)
    fig.tight_layout()
    fig.savefig("the-ai-lexicon-trend.png", bbox_inches="tight")
    print("wrote the-ai-lexicon-trend.png")

    with open("trend_series.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["period", "words", "kobak_rare_per100k", "kobak_ci",
                    "wiki33_per100k", "wiki_ci"])
        for y in years:
            w.writerow([y, y_words[y], round(y_kob[y][0], 2),
                        round(y_kob[y][1], 2), round(y_wiki[y][0], 2),
                        round(y_wiki[y][1], 2)])
        for q in quarters:
            w.writerow([q, q_words[q], round(q_rate[q], 2),
                        round(q_ci[q], 2), "", ""])

    # Mann-Kendall on the Kobak yearly series
    vals = [y_kob[y][0] for y in years]
    S = sum(np.sign(vals[j] - vals[i])
            for i in range(len(vals)) for j in range(i + 1, len(vals)))
    n = len(vals)
    var = n * (n - 1) * (2 * n + 5) / 18
    z = (S - np.sign(S)) / math.sqrt(var)
    p_mk = 0.5 * math.erfc(z / math.sqrt(2))
    print(f"Mann-Kendall (yearly, n={n}): S={S:+.0f} z={z:+.2f} "
          f"one-sided p={p_mk:.4f}")

    # ITS segmented fit + placebo null for the slope change
    def seg_c(counts_by_q):
        t = np.array(quarters)
        k = np.array([counts_by_q[q] for q in quarters], dtype=float)
        wds = np.array([q_words[q] for q in quarters], dtype=float)
        r = np.log((k + 0.5) / wds)
        X = np.column_stack([np.ones_like(t), t - 2018,
                             np.clip(t - 2023.0, 0, None)])
        W = np.diag(np.maximum(k, 0.5))
        beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ r)
        return beta

    ai_counts = {q: sum(q_tok[q][w] for w in rset) for q in quarters}
    b = seg_c(ai_counts)
    print(f"ITS fit (break pre-set at 2023.0): pre-slope {b[1]:+.4f}/yr, "
          f"post-break slope change {b[2]:+.4f}/yr "
          f"(=> post-2023 growth {math.exp(b[1]+b[2])-1:+.1%}/yr)")
    top_func = {w for w, _ in pre_c.most_common(120)}
    bucket = defaultdict(list)
    for w, nn in pre_c.items():
        if w in rset or w in top_func or len(w) < 4 or not w.isalpha():
            continue
        bucket[int(math.log2(nn + 1))].append(w)
    def pool_for(bb):
        for off in (0, 1, -1, 2, -2, 3, -3, 4, -4):
            p = bucket.get(bb + off)
            if p:
                return p
        return bucket[max(bucket)]
    buckets = [int(math.log2(pre_c[w] + 1)) for w in rare]
    exceed = 0
    N = 1000
    for _ in range(N):
        sel = [random.choice(pool_for(bb)) for bb in buckets]
        cnt = {q: sum(q_tok[q][w] for w in sel) for q in quarters}
        if seg_c(cnt)[2] >= b[2]:
            exceed += 1
    print(f"placebo null for the slope change: p = {exceed}/{N} "
          f"= {exceed/N:.3f}")


if __name__ == "__main__":
    main()
