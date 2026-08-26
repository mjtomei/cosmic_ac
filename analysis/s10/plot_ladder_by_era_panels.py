#!/usr/bin/env python3
"""The coded-ladder-by-era figure: the surviving occupational instrument, era-resolved.

One panel per level of the coded altitude ladder — the joint model's
surviving occupational block — each showing that level's base slope entered
alone (per sd, HC1) across the six equal bins, on the class-era machinery's
member-bin values. Same styling as the class panels.

Reads ladder_by_era.csv (build_ladder_by_era.py). Writes
ladder_by_era_panels.png.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["FREE", "BOTTOM", "MIDDLE", "TOP"]
LABEL = {"FREE": "free (off the organisational ladder)",
         "BOTTOM": "bottom", "MIDDLE": "middle", "TOP": "top"}
BLUE = "#1f77b4"

rows = list(csv.DictReader(open(os.path.join(HERE, "ladder_by_era.csv"))))
eras = sorted({r["half_decade"] for r in rows})
ex = {e: i for i, e in enumerate(eras)}

# 4 rows x 2 columns (Matthew, 2026-08-26): at the PDF's 0.85 linewidth the
# old 2x4 grid shrank panel text below readability; 4x2 keeps fonts ~8pt
# effective with panels wide enough for six labelled bins
fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.4), sharey=True, sharex=True)
panels = [(lv, LABEL[lv],
           sorted((ex[r["half_decade"]], float(r["slope_per_sd"]),
                   float(r["se"]), int(r["n_members"]))
                  for r in rows if r["level"] == lv))
          for lv in ORDER]
for ax, (cls, label, pts) in zip(axes.flat, panels):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ses = [p[2] for p in pts]
    ax.axhline(0, color="0.82", lw=0.8, zorder=1)
    ax.fill_between(xs, [y - s for y, s in zip(ys, ses)],
                    [y + s for y, s in zip(ys, ses)],
                    color=BLUE, alpha=0.16, lw=0, zorder=2)
    ax.plot(xs, ys, "-", color=BLUE, lw=1.5, zorder=3)
    ns = [p[3] for p in pts]
    W = sum(ns)
    xw = sum(n * x for n, x in zip(ns, xs)) / W
    yw = sum(n * y for n, y in zip(ns, ys)) / W
    den = sum(n * (x - xw) ** 2 for n, x in zip(ns, xs))
    if den:
        b = sum(n * (x - xw) * (y - yw) for n, x, y in zip(ns, xs, ys)) / den
        x0, x1 = min(xs), max(xs)
        ax.plot([x0, x1], [yw + b * (x0 - xw), yw + b * (x1 - xw)],
                ":", color=BLUE, lw=1.3, alpha=0.85, zorder=2.5)
    for x, y, s, n in pts:
        thin = n < 25
        ax.plot([x], [y], "o", ms=4.2, zorder=4, color=BLUE,
                mfc="white" if thin else BLUE, mew=1.2)
        if thin:
            ax.annotate(f"{n}", (x, y), textcoords="offset points",
                        xytext=(0, 5), fontsize=6.5, color="0.4",
                        ha="center")
    ax.set_title(label, fontsize=10.5, loc="left")
    ax.set_xticks(range(len(eras)))
    ax.set_xticklabels([e[2:4] + "–" + e[7:] for e in eras], fontsize=8.5)
    ax.set_yticks([-0.1, 0.0])
    ax.tick_params(labelsize=8.5)
fig.supylabel("slope of register z per sd of the level, alone", fontsize=10)
# no suptitle: the paper caption carries the description
fig.tight_layout(rect=(0.015, 0, 1, 1))
out = os.path.join(HERE, "ladder_by_era_panels.png")
fig.savefig(out, dpi=160)
print("wrote", out)
