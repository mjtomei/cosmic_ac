#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#15324f"; GREY = "#9aa7b4"; SLATE = "#5f7081"

# Illustrative "reconfigurable / dataflow share of new datacenter accelerator silicon".
# The dated milestones and acquisition values are real; the curve is an argued trend.
hx = [2012, 2014, 2015, 2016, 2018, 2020, 2022, 2025]
hy = [4,    7,    9,    12,   15,   18,   24,   32]
px = [2025, 2027, 2029, 2031, 2033, 2035]
py = [32,   43,   55,   68,   80,   90]

fig, ax = plt.subplots(figsize=(8.6, 5.3))

ax.axhline(50, color=GREY, ls=":", lw=1.3, zorder=1)
ax.text(2012.2, 52, "reconfigurable overtakes general-purpose / fixed", fontsize=8, color=SLATE, va="bottom")

ax.plot(hx, hy, "-", color=NAVY, lw=2.6, zorder=3, label="Observed era (real milestones below)")
ax.plot(px, py, "--", color=NAVY, lw=2.4, zorder=3, label="Projected (shared commons + machine-intelligence era)")

# milestone markers on the historical curve, with explicit non-overlapping label positions
mk = [(2014, 7,  "Microsoft Catapult:\nFPGAs in Azure servers",            2012.7, 35),
      (2015, 9,  "Intel buys Altera\n$16.7B",                              2016.3, 27),
      (2016, 12, "AWS F1:\nFPGAs in the cloud",                           2018.6, 18),
      (2022, 24, "AMD buys Xilinx  $49B\n(largest semiconductor deal ever)", 2020.4, 41),
      (2024, 29, "AI-accelerator wave:\nlargely dataflow / reconfigurable", 2026.0, 14)]
for yr, yv, txt, tx, ty in mk:
    ax.scatter([yr], [yv], s=46, color=NAVY, zorder=4, edgecolor="white", lw=1)
    ax.annotate(txt, xy=(yr, yv), xytext=(tx, ty),
                fontsize=7.8, color="#22323f", ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=SLATE, lw=0.8))

ax.annotate("shared commons + machine intelligence\nclose the programmability gap",
            xy=(2029, 55), xytext=(2026.0, 74), fontsize=8.4, color=NAVY,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2))

ax.set_xlim(2011.5, 2035.5); ax.set_ylim(0, 100)
ax.set_xticks([2012, 2015, 2018, 2021, 2024, 2027, 2030, 2033])
ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(["0", "25", "50", "75", "100"], fontsize=9)
ax.set_ylabel("Reconfigurable / dataflow share of new\ndatacenter accelerator silicon (%, illustrative)", fontsize=9.5)
ax.set_xlabel("Year", fontsize=10.5)
ax.set_title("Reconfigurable hardware is already moving in — the commons is the inflection",
             fontsize=12, color=NAVY, fontweight="bold", pad=10)
ax.grid(True, axis="y", ls=":", color="#dde2e8", zorder=0)
ax.legend(fontsize=8.2, loc="upper left", framealpha=0.96, edgecolor="#d6dce2")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
for p in ["the-performance-commons-figure-5.png",
          "the-performance-commons-figure-5.png"]:
    plt.savefig(p, dpi=200, bbox_inches="tight")
print("figure 4 written")
