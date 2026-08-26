#!/usr/bin/env python3
"""The class-by-era paper figure: one panel per class, every cell shown.

Replaces the pooled single-axes figure (Matthew, 2026-08-26): same data,
contextualised — each class carries its own se band, thin cells (n < 25,
open markers) are shown rather than filtered, and the partial 2025-26 bin
(two years, half-sized cells) is excluded from the figure entirely; its
cells live in class_by_era_all.csv and none of them changes a conclusion.

Reads class_by_era_all.csv (build_class_by_era.py). Writes
class_by_era_panels.png.
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"]
LABEL = {"I": "I higher service", "II": "II lower service",
         "III": "III routine non-manual", "IVab": "IVab petty bourgeoisie",
         "IVc": "IVc farmers", "V/VI": "V/VI skilled manual",
         "VIIab": "VIIab semi- and unskilled"}
BLUE = "#1f77b4"

rows = [r for r in csv.DictReader(open(os.path.join(HERE, "class_by_era_all.csv")))
        if r["partial"] == "0"]
eras = sorted({r["half_decade"] for r in rows})
ex = {e: i for i, e in enumerate(eras)}

fig, axes = plt.subplots(2, 4, figsize=(11.8, 5.2), sharey=True, sharex=True)
for ax, cls in zip(axes.flat, ORDER):
    pts = sorted((ex[r["half_decade"]], float(r["mean_z"]), float(r["se"]),
                  int(r["n_members"])) for r in rows if r["egp"] == cls)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ses = [p[2] for p in pts]
    ax.axhline(0, color="0.82", lw=0.8, zorder=1)
    ax.fill_between(xs, [y - s for y, s in zip(ys, ses)],
                    [y + s for y, s in zip(ys, ses)],
                    color=BLUE, alpha=0.16, lw=0, zorder=2)
    ax.plot(xs, ys, "-", color=BLUE, lw=1.5, zorder=3)
    for x, y, s, n in pts:
        thin = n < 25
        ax.plot([x], [y], "o", ms=4.2, zorder=4, color=BLUE,
                mfc="white" if thin else BLUE, mew=1.2)
        if thin:
            ax.annotate(f"{n}", (x, y), textcoords="offset points",
                        xytext=(0, 5), fontsize=6.5, color="0.4",
                        ha="center")
    ax.set_title(LABEL[cls], fontsize=10.5, loc="left")
    ax.set_xticks(range(len(eras)))
    ax.set_xticklabels([e[2:4] + "–" + e[7:] for e in eras],
                       fontsize=7.5)
    ax.tick_params(labelsize=8)
axes.flat[-1].axis("off")
fig.supylabel("register, z within chamber × period", fontsize=10)
# no suptitle: the paper caption carries the description
fig.tight_layout(rect=(0.012, 0, 1, 1))
out = os.path.join(HERE, "class_by_era_panels.png")
fig.savefig(out, dpi=160)
print("wrote", out)
