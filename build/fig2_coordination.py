#!/usr/bin/env python3
# Compact single-column version of the coordination-gap figure.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#15324f"; GREY = "#9aa7b4"; SLATE = "#5f7081"; FILL = "#2a4a6b"

labels = ["Tightly-coupled\ndatacenter", "Datacenter\nEthernet",
          "Multiple\ndatacenters", "Consumer\nfederation"]
x = [1, 2, 3, 4]

# Useful compute realized as % of ideal (higher is better).
robust = [99, 96, 93, 90]   # methods built for loose coupling (DiLoCo-class)
naive  = [98, 80, 45, 8]     # communicate-every-step / synchronous

fig, ax = plt.subplots(figsize=(4.35, 4.15))

ax.fill_between(x, naive, robust, color=FILL, alpha=0.12, zorder=1)
ax.plot(x, naive, "--o", color=GREY, lw=1.8, ms=5, zorder=2)
ax.plot(x, robust, "-o", color=NAVY, lw=2.2, ms=6, zorder=3)

ax.set_ylim(0, 108)
ax.set_xlim(0.55, 4.45)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.8)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0", "25", "50", "75", "100"], fontsize=8.3)
ax.set_ylabel("Useful compute realized\n(% of ideal; higher is better)", fontsize=8.8)
ax.set_xlabel(u"Looseness of coupling  →", fontsize=9)
ax.set_title("Distributed computing is a coordination\nproblem, not a hardware limit",
             fontsize=10.5, color=NAVY, fontweight="bold", pad=8, linespacing=1.15)

# direct labels instead of a legend box
ax.annotate(u"built for loose coupling (DiLoCo-class):\n~500× less communication,\n~90% utilization across continents",
            xy=(3.55, 91.3), xytext=(0.68, 47), fontsize=7.8, color=NAVY, linespacing=1.2,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.1))
ax.annotate("naive synchronous methods:\ncommunicate every step",
            xy=(2.55, 60.5), xytext=(0.85, 28), fontsize=7.8, color=SLATE, linespacing=1.2,
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.0))
ax.text(3.78, 72, "the coordination\ngap", fontsize=8.2, color=FILL,
        style="italic", ha="center", linespacing=1.15)
ax.annotate("most idle consumer compute lives\nhere - naive methods waste ~90%",
            xy=(3.97, 9.5), xytext=(2.2, 16), fontsize=7.4, color=SLATE, linespacing=1.2,
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.0))

ax.grid(True, axis="y", ls=":", color="#dde2e8", zorder=0)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
plt.savefig("the-performance-commons-figure-2.png", dpi=200, bbox_inches="tight")
print("compact coordination figure -> figure-2.png")
