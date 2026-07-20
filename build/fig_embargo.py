#!/usr/bin/env python3
# Compact single-column figure: the embargo natural experiment.
# Series: top-US vs top-Chinese model gap on LMArena (Stanford AI Index 2025/2026).
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#15324f"; GREY = "#9aa7b4"; SLATE = "#5f7081"; FILL = "#2a4a6b"

x = [2024.05, 2025.1, 2026.3]
y = [9.3, 1.7, 2.7]

fig, ax = plt.subplots(figsize=(4.35, 3.5))

ax.plot(x, y, "-o", color=NAVY, lw=2.2, ms=6, zorder=3)
ax.text(2024.32, 8.9, "9.3%", fontsize=8.4, color=NAVY, ha="left", fontweight="bold")
ax.text(2025.1, 0.55, "1.7%", fontsize=8.4, color=NAVY, ha="center", fontweight="bold")
ax.text(2026.32, 1.6, "2.7%", fontsize=8.4, color=NAVY, ha="right", fontweight="bold")

for xe, lab in [(2022.79, "Oct '22:\nexport\ncontrols"), (2023.8, "Oct '23:\ntightened")]:
    ax.axvline(xe, color=SLATE, ls=(0, (5, 3)), lw=1.3, zorder=2)
    ax.text(xe + 0.05, 10.6, lab, fontsize=7.6, color=SLATE, va="top", linespacing=1.15)

ax.annotate("meanwhile: US training-hardware\nlead holds at ~4 years (Epoch AI)",
            xy=(2025.6, 7.6), fontsize=7.8, color=FILL, ha="center",
            style="italic", linespacing=1.2)
ax.annotate("R1", xy=(2025.05, 1.7), xytext=(2024.85, 3.6), fontsize=7.6, color=SLATE,
            ha="center", arrowprops=dict(arrowstyle="->", color=SLATE, lw=0.9))
ax.annotate("K3", xy=(2026.3, 2.7), xytext=(2026.35, 4.6), fontsize=7.6, color=SLATE,
            ha="center", arrowprops=dict(arrowstyle="->", color=SLATE, lw=0.9))

ax.set_xlim(2022.5, 2026.75)
ax.set_ylim(0, 11)
ax.set_xticks([2023, 2024, 2025, 2026])
ax.set_xticklabels(["2023", "2024", "2025", "2026"], fontsize=8.3)
ax.set_yticks([0, 3, 6, 9])
ax.set_yticklabels(["0", "3", "6", "9"], fontsize=8.3)
ax.set_ylabel("Top US vs top Chinese model,\nArena gap (%)", fontsize=8.8)
ax.set_title("The embargo natural experiment", fontsize=10.5,
             color=NAVY, fontweight="bold", pad=8)
ax.grid(True, axis="y", ls=":", color="#dde2e8", zorder=0)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
plt.savefig("the-performance-commons-figure-embargo.png", dpi=200, bbox_inches="tight")
print("embargo figure -> figure-embargo.png")
