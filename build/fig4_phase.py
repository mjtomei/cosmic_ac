#!/usr/bin/env python3
# Compact, single-column version of the phase diagram (square-ish, larger relative type).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

NAVY = "#15324f"; SLATE = "#5f7081"
C_ASIC = "#cdd6de"; C_CPU = "#aab7c4"; C_CGRA = "#9db4cc"

fig, ax = plt.subplots(figsize=(4.25, 4.0))
yband = 2.7
cpu  = Polygon([(0, yband), (6.4, yband), (3.2, 10), (0, 10)], closed=True,
               facecolor=C_CPU, edgecolor="white", lw=1.0, zorder=1)
cgra = Polygon([(6.4, yband), (10, yband), (10, 10), (3.2, 10)], closed=True,
               facecolor=C_CGRA, edgecolor="white", lw=1.0, zorder=1)
asic = Polygon([(0, 0), (10, 0), (10, yband), (0, yband)], closed=True,
               facecolor=C_ASIC, edgecolor="white", lw=1.0, zorder=1)
for p in (cpu, cgra, asic):
    ax.add_patch(p)

ax.text(1.75, 6.7, "CPU /\ngeneral-purpose\noptimal", fontsize=9.6, color=NAVY,
        ha="center", va="center", fontweight="bold", linespacing=1.25)
ax.text(7.8, 6.9, "Reconfigurable\n(CGRA)\noptimal", fontsize=9.6, color=NAVY,
        ha="center", va="center", fontweight="bold", linespacing=1.25)
ax.text(5.0, 1.35, "ASIC optimal\n(fixed workload)", fontsize=9.2, color="#2b3640",
        ha="center", va="center", fontweight="bold", linespacing=1.2)

ax.plot([6.4, 3.2], [yband, 10], color="white", lw=2.0, zorder=2)
ax.annotate("", xy=(8.9, 9.35), xytext=(1.1, 9.35),
            arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.8))
ax.text(5.0, 9.55, "commons matures over time", fontsize=8.4, color=NAVY,
        ha="center", va="bottom", style="italic")

ax.scatter([2.3], [8.0], s=46, color=NAVY, zorder=4, edgecolor="white", lw=1)
ax.text(2.3, 8.5, "today", fontsize=8.6, color=NAVY, ha="center", fontweight="bold")
ax.scatter([8.0], [8.0], s=46, color=NAVY, zorder=4, edgecolor="white", lw=1)
ax.text(8.0, 8.5, "future", fontsize=8.6, color=NAVY, ha="center", fontweight="bold")
ax.annotate("", xy=(7.4, 8.0), xytext=(2.9, 8.0),
            arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.2, ls=(0, (4, 3))))

ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.set_xticks([0.3, 9.7]); ax.set_xticklabels(["hand-\ntuned", "near-\noracular"], fontsize=8)
ax.set_yticks([0.4, 9.6]); ax.set_yticklabels(["fixed", "varied"], fontsize=8, rotation=90, va="center")
ax.set_xlabel(u"Time  \u2192  (commons maturity)", fontsize=9)
ax.set_ylabel(u"Workload diversity  \u2192", fontsize=9)
ax.set_title("Where the optimum lands as\nthe commons matures",
             fontsize=10.5, color=NAVY, fontweight="bold", pad=9, linespacing=1.2)
ax.tick_params(length=0)
for s in ["top", "right", "left", "bottom"]:
    ax.spines[s].set_color("#c4ccd4")

plt.tight_layout()
for p in ["the-performance-commons-figure-4.png",
          "the-performance-commons-figure-4.png"]:
    plt.savefig(p, dpi=200, bbox_inches="tight")
print("compact fig3 written")
