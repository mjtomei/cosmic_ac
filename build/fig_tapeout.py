#!/usr/bin/env python3
# Compact single-column figure: Tiny Tapeout designs per shuttle through the Efabless shutdown.
# Counts from tinytapeout.com/runs (verified 2026-07).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#15324f"; GREY = "#9aa7b4"; SLATE = "#5f7081"; FILL = "#2a4a6b"

# (label, designs, fab) in chronological order
runs = [
    ("TT01", 152, "sky"), ("TT02", 165, "sky"), ("TT03", 100, "sky"),
    ("TT04", 143, "sky"), ("TT05", 174, "sky"), ("TT06", 238, "sky"),
    ("TT07", 120, "sky"), ("TT08", 135, "sky"), ("TT09", 369, "sky"),
    ("IHP25a", 547, "ihp"), ("IHP25b", 81, "ihp"),
    ("SKY25a", 237, "sky"), ("SKY25b", 316, "sky"),
    ("IHP26a", 283, "ihp"), ("SKY26a", 289, "sky"), ("SKY26b", 273, "sky"),
    ("GF26a", 95, "gf"), ("GF26b", 90, "gf"), ("GF0p3", 32, "gf"),
]
COLOR = {"sky": NAVY, "ihp": SLATE, "gf": GREY}

fig, ax = plt.subplots(figsize=(4.35, 3.6))
xs = range(len(runs))
ax.bar(xs, [r[1] for r in runs], color=[COLOR[r[2]] for r in runs], width=0.78, zorder=2)

# Efabless shutdown between TT09 (idx 8) and IHP25a (idx 9)
ax.axvline(8.5, color=SLATE, ls=(0, (5, 3)), lw=1.4, zorder=3)
ax.annotate("Efabless shuts down\n(Mar 2025)", xy=(8.5, 430), xytext=(4.0, 395),
            fontsize=7.8, color=SLATE, linespacing=1.2, ha="center",
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.0))
ax.annotate("547 - largest open\nshuttle ever", xy=(9.45, 552), xytext=(13.0, 525),
            fontsize=7.6, color=NAVY, linespacing=1.15, ha="center",
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.0))

# year markers under groups: 2022(0-1) 2023(2-4) 2024(5-8) 2025(9-12) 2026(13-18)
for x0, x1, yr in [(0, 1, "2022"), (2, 4, "2023"), (5, 8, "2024"), (9, 12, "2025"), (13, 18, "2026")]:
    ax.text((x0 + x1) / 2, -52, yr, fontsize=8, color="#42505c", ha="center")

# fab legend, direct
ax.text(0.02, 0.955, "SkyWater", transform=ax.transAxes, fontsize=7.8, color=NAVY)
ax.text(0.02, 0.895, "IHP", transform=ax.transAxes, fontsize=7.8, color=SLATE)
ax.text(0.02, 0.835, "GlobalFoundries", transform=ax.transAxes, fontsize=7.8, color=GREY)

ax.set_xticks([])
ax.set_xlim(-0.7, len(runs) - 0.3)
ax.set_ylim(0, 600)
ax.set_yticks([0, 150, 300, 450])
ax.set_yticklabels(["0", "150", "300", "450"], fontsize=8.3)
ax.set_ylabel("Designs per shuttle", fontsize=8.8)
ax.set_title("Participation through the platform's death", fontsize=10.5,
             color=NAVY, fontweight="bold", pad=8)
ax.grid(True, axis="y", ls=":", color="#dde2e8", zorder=0)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
plt.savefig("the-performance-commons-figure-tapeout.png", dpi=200, bbox_inches="tight")
print("tapeout participation figure -> figure-tapeout.png")
