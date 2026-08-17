#!/usr/bin/env python3
"""Class profile of the register, one line per half-decade (pooled tail).

The cross-section (§4.6a) shows an inverted U peaking at class II. The question
this plots is whether the peak MOVES: under a chase-and-flight reading the
originating tier abandons the form first and the peak migrates downward, so
successive half-decades should slide.

Y is the mean within-(chamber x half-decade) z, collapsed to one value per
member so long-serving members are not counted repeatedly, and z-scored inside
each chamber-and-period cell so the overall era rise is removed and only the
SHAPE across classes remains. Cells with fewer than 25 members are dropped
rather than drawn thin, which is why the manual and farm classes start in
2005-09 -- provincial class coding does not reach earlier.

Reads class_by_era.csv; writes class_by_era_grouped.png.
"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["I", "II", "III", "IVab", "manual+farm"]
LABEL = {"I": "I\nhigher\nservice", "II": "II\nlower\nservice",
         "III": "III\nroutine\nnon-manual", "IVab": "IVab\npetty\nbourgeoisie",
         "manual+farm": "IVc + V/VI + VIIab\nmanual and farm"}

rows = list(csv.DictReader(open(os.path.join(HERE, "class_by_era_grouped.csv"))))
bins = sorted({r["half_decade"] for r in rows})
# sequential single hue, light = earliest, dark = latest: the series are ORDERED
ramp = plt.get_cmap("Blues")
cols = [ramp(0.30 + 0.62 * i / max(len(bins) - 1, 1)) for i in range(len(bins))]

fig, ax = plt.subplots(figsize=(9.6, 6.3))
ax.axhline(0, color="#c7c7c7", lw=1, zorder=1)
for i, b in enumerate(bins):
    d = {r["group"]: r for r in rows if r["half_decade"] == b}
    xs = [j for j, c in enumerate(ORDER) if c in d]
    ys = [float(d[c]["mean_z"]) for c in ORDER if c in d]
    es = [float(d[c]["se"]) for c in ORDER if c in d]
    # +/-1 se drawn on every point: the thin classes (III, VIIab) carry
    # intervals several times the spread between periods, which is the whole
    # reason the apparent movement in those columns is not readable as movement
    ax.errorbar(xs, ys, yerr=es, fmt="-o", color=cols[i], lw=1.9, ms=4.4,
                elinewidth=1.0, capsize=2.5, alpha=0.92,
                markeredgecolor="white", markeredgewidth=1.0,
                zorder=3, label=b)

ax.set_xticks(range(len(ORDER)))
ax.set_xticklabels([LABEL[c] for c in ORDER], fontsize=8.5)
ax.set_ylabel("register, z within chamber × period", fontsize=10)
ax.set_title("The crossover holds in every half-decade: class II above class I, "
             "manual and farm below both", fontsize=11.5, loc="left", pad=26)
ax.text(0, 1.035, "error bars are ±1 se — the manual and farm classes are pooled, as §4.6a "
        "already treats them; III remains thin at 26–81 members",
        transform=ax.transAxes, fontsize=8.6, color="#777")
ax.set_xlim(-0.35, len(ORDER) - 0.55)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.spines["left"].set_color("#c7c7c7"); ax.spines["bottom"].set_color("#c7c7c7")
ax.tick_params(colors="#555", length=0)
ax.grid(axis="y", color="#eeeeee", lw=0.8, zorder=0)
ax.legend(title="half-decade", fontsize=8.4, title_fontsize=8.4,
          frameon=False, loc="upper right", ncol=2, handlelength=1.6)
fig.text(0.012, 0.018,
         "One point per class per period, ≥25 members; member-level means over 22 chambers,\n"
         "z-scored within chamber × period so the overall era rise is removed and only the class\n"
         "shape remains. IVc, V/VI and VIIab are pooled (n 50–260) because separately they run\n"
         "26–113 and cross each other on noise; I and II are kept apart because the crossover\n"
         "between them is the claim under test. n per point in class_by_era_grouped.csv.",
         fontsize=7.5, color="#666", linespacing=1.6)
fig.tight_layout(rect=(0, 0.155, 1, 1))
fig.savefig(os.path.join(HERE, "class_by_era_grouped.png"), dpi=170)
print("wrote class_by_era_grouped.png")
