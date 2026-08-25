#!/usr/bin/env python3
"""Plot the multi-chamber trend from trend_cache.json (fast; iterate the rare
set and chamber choice here). Rare Kobak set = style words <5/100k pooled
pre-2023 across the plotted chambers. Writes the-ai-lexicon-trend.png."""
import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = json.load(open("trend_cache.json"))
style, cache = D["style"], D["cache"]
# chambers to draw (NB dropped from lines: sparse with straight-line-through-gaps)
PLOT = [("UK Commons","#D55E00"),("Canada federal","#009E73"),
        ("Ireland","#CC79A7"),("US House","#555555"),("US Senate","#E69F00")]
MINW = 100_000

# pooled pre-2023 baseline over plotted chambers -> rare set (<5/100k)
pre_cnt = {w: 0 for w in style}; pre_w = 0
for name, _ in PLOT:
    for y, v in cache[name].items():
        if int(y) < 2023:
            pre_w += v["words"]
            for w, c in v["style"].items():
                pre_cnt[w] += c
rare = [w for w in style if pre_cnt[w] / max(pre_w, 1) * 1e5 < 5.0]
print("rare set:", len(rare), "of", len(style), "  pooled pre-2023 words:", pre_w)

def series(name, which):
    c = cache[name]
    ys = sorted(int(y) for y, v in c.items() if v["words"] >= MINW)
    def rate(y):
        v = c[str(y)]
        n = v["wiki"] if which == "wiki" else sum(v["style"].get(w, 0) for w in rare)
        return n / v["words"] * 1e5
    vals = {y: rate(y) for y in ys}
    pre = [vals[y] for y in ys if y < 2023]
    if not pre or np.mean(pre) == 0:
        return ys, None
    b = np.mean(pre)
    return ys, {y: vals[y] / b * 100 for y in ys}

fig, (aW, aK) = plt.subplots(1, 2, figsize=(11.4, 4.8), dpi=150, sharey=True)
for ax, which, title in ((aW,"wiki","Obvious tells: Wikipedia “signs of AI writing”"),
                         (aK,"kob","Subtler set: Kobak rare-style vocabulary")):
    ax.axhline(100, color="#c7c7c7", lw=1, zorder=1)
    ax.axvline(2022.92, color="#999", lw=1, ls=(0,(4,3)), zorder=1)
    for name, col in PLOT:
        ys, idx = series(name, which)
        if not idx: continue
        ax.plot(ys, [idx[y] for y in ys], "-o", color=col, lw=1.8, ms=4.2,
                markeredgecolor="white", markeredgewidth=0.8, label=name, zorder=3)
    ax.set_title(title, fontsize=11, loc="left")
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    ax.set_xlim(2017.7, 2026.4)
aW.set_ylabel("rate, indexed (pre-2023 mean = 100)", fontsize=9.5)
aW.text(2022.8, aW.get_ylim()[1]*0.97, "ChatGPT", ha="right", va="top", fontsize=8, color="#777")
aK.legend(loc="upper left", frameon=False, fontsize=8.7)
fig.tight_layout()
fig.savefig("the-ai-lexicon-trend.png", bbox_inches="tight")
print("wrote the-ai-lexicon-trend.png")
# quick numeric peek: 2024/2025/2026 indexed values per chamber, wiki
print("\nWIKI indexed (peek):")
for name,_ in PLOT:
    ys,idx=series(name,"wiki")
    if idx: print(f"  {name:15s}", {y:round(idx[y]) for y in ys if y>=2023})
print("KOBAK indexed (peek):")
for name,_ in PLOT:
    ys,idx=series(name,"kob")
    if idx: print(f"  {name:15s}", {y:round(idx[y]) for y in ys if y>=2023})
