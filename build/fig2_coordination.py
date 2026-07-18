#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#15324f"; GREY = "#9aa7b4"; SLATE = "#5f7081"; FILL = "#2a4a6b"

labels = ["Tightly-coupled\ndatacenter", "Datacenter\nEthernet",
          "Multiple\ndatacenters (WAN)", "Consumer-device\nfederation"]
x = [1, 2, 3, 4]

# Useful compute realized as % of ideal (higher is better).
robust = [99, 96, 93, 90]   # methods built for loose coupling (DiLoCo-class)
naive  = [98, 80, 45, 8]     # communicate-every-step / synchronous

fig, ax = plt.subplots(figsize=(8.4, 5.1))

ax.fill_between(x, naive, robust, color=FILL, alpha=0.12, zorder=1,
                label="The programmability / coordination gap - latent compute the\ncollective-action problem leaves unharnessed (reclaimed by\nmethods built for loose coupling)")
ax.plot(x, naive, "--o", color=GREY, lw=2.0, ms=6.5, zorder=2,
        label="Naive synchronous methods - communicate every step")
ax.plot(x, robust, "-o", color=NAVY, lw=2.6, ms=8, zorder=3,
        label="Methods built for loose coupling (DiLoCo-class)")

ax.set_ylim(0, 108)
ax.set_xlim(0.55, 4.45)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
ax.set_yticks([0, 25, 50, 75, 100])
ax.set_yticklabels(["0", "25", "50", "75", "100"], fontsize=9)
ax.set_ylabel("Useful compute realized\n(% of ideal; higher is better)", fontsize=10)
ax.set_xlabel(u"Looseness of coupling  \u2192", fontsize=10.5)
ax.set_title("Distributed computing is a collective-action problem, not a hardware limit",
             fontsize=12.5, color=NAVY, fontweight="bold", pad=12)

ax.annotate(u"Built for loose coupling (DiLoCo): ~500\u00d7 less\ncommunication \u2192 ~90% utilization across continents",
            xy=(3.6, 91), xytext=(1.35, 64), fontsize=8.6, color=NAVY,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2))
ax.annotate("Most idle consumer compute lives here -\nnaive methods waste ~90% of it",
            xy=(4, 8), xytext=(2.05, 18), fontsize=8.6, color=SLATE,
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.1))
ax.annotate(u"gap \u2248 0: tight coupling\nis easy to coordinate",
            xy=(1, 98.5), xytext=(0.62, 70), fontsize=8, color=SLATE,
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.0))

ax.grid(True, axis="y", ls=":", color="#dde2e8", zorder=0)
ax.legend(fontsize=8.0, loc="lower left", framealpha=0.96, edgecolor="#d6dce2")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
for p in ["the-performance-commons-figure-2.png",
          "the-performance-commons-figure-2.png"]:
    plt.savefig(p, dpi=200, bbox_inches="tight")
print("figure 2 written")
