#!/usr/bin/env python3
# Compact single-column version of the machine-intelligence demand curve.
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

NAVY = "#15324f"; GREY = "#9aa7b4"; SLATE = "#5f7081"; FILL = "#2a4a6b"

x = np.linspace(0, 11.5, 400)
y = 120 * np.exp(-0.62 * x)
x_hum = 5.0
y_hum = 120 * np.exp(-0.62 * x_hum)

fig, ax = plt.subplots(figsize=(4.35, 4.05))

mask = x >= x_hum
ax.fill_between(x[mask], 0.05, y[mask], color=FILL, alpha=0.13, zorder=1)
ax.plot(x, y, color=NAVY, lw=2.4, zorder=3)

ax.axvline(x_hum, color=SLATE, ls=(0, (5, 3)), lw=1.4, zorder=2)
ax.text(x_hum - 0.2, 138, "humans\nsaturate", fontsize=8.6, color=SLATE, ha="right", va="top", linespacing=1.1)

ax.axhline(0.50, color=GREY, ls=":", lw=1.3, zorder=2)
ax.text(0.2, 0.6, "datacenter  ~$0.50/hr", fontsize=8, color="#42505c", va="bottom")
ax.axhline(0.08, color=GREY, ls=":", lw=1.3, zorder=2)
ax.text(0.2, 0.094, "idle home  ~$0.08/hr (6\u00d7)", fontsize=8, color="#42505c", va="bottom")

ax.scatter([0.25], [100], s=30, color=NAVY, zorder=4, edgecolor="white", lw=0.8)
ax.text(0.55, 118, "frontier", fontsize=8.2, color=NAVY, va="bottom")
ax.text(8.0, 6.5, "the elastic tail\n(machine-only)", fontsize=8.4, color=FILL, ha="center",
        style="italic", linespacing=1.15)
ax.annotate("\u2192 arbitrarily\nlow value", xy=(11.3, 120*np.exp(-0.62*11.3)), xytext=(8.5, 0.4),
            fontsize=8, color=NAVY, ha="center", linespacing=1.1,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.0))

ax.set_yscale("log")
ax.set_ylim(0.05, 240); ax.set_xlim(0, 11.7)
ax.set_yticks([0.1, 1, 10, 100]); ax.set_yticklabels(["$0.10", "$1", "$10", "$100"], fontsize=8.3)
ax.set_xticks([])
ax.set_xlabel(u"Cumulative compute demanded  \u2192", fontsize=9)
ax.set_ylabel("Value of marginal compute-hour\n($/hr, log)", fontsize=8.8)
ax.set_title("Machine demand has no floor", fontsize=11, color=NAVY, fontweight="bold", pad=8)
ax.grid(True, axis="y", ls=":", color="#e2e7ec", zorder=0)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
for p in ["the-performance-commons-figure-3.png",
          "the-performance-commons-figure-3.png"]:
    plt.savefig(p, dpi=200, bbox_inches="tight")
print("compact demand figure -> figure-3.png")
