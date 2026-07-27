#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#15324f"; GREY = "#9aa7b4"; SLATE = "#5f7081"; FILL = "#2a4a6b"

labels = ["ASIC\n(fully custom)", "CGRA", "FPGA", "GPU\n(SIMT)", "CPU\n(fully general)"]
x = [1, 2, 3, 4, 5]

realizable = [1.0, 2.8, 25.0, 8.0, 200.0]
achieved   = [1.0, 11.0, 80.0, 55.0, 260.0]

fig, ax = plt.subplots(figsize=(8.4, 5.1))

ax.fill_between(x, realizable, achieved, color=FILL, alpha=0.12, zorder=1,
                label="The effort gap - efficiency lost to programming difficulty\n(what a shared / AI optimization commons reclaims)")
ax.plot(x, achieved, "--o", color=GREY, lw=2.0, ms=6.5, zorder=2,
        label="Achieved today - finite programmer effort")
ax.plot(x, realizable, "-o", color=NAVY, lw=2.6, ms=8, zorder=3,
        label="Realizable frontier - unlimited programmer effort")

ax.set_yscale("log")
ax.set_ylim(0.78, 430)
ax.set_xlim(0.55, 5.45)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
ax.set_yticks([1, 10, 100]); ax.set_yticklabels([u"1\u00d7 (ASIC)", u"10\u00d7", u"100\u00d7"], fontsize=9)
ax.set_ylabel("Energy per operation relative to an ASIC\n(lower is better, log scale)", fontsize=10)
ax.set_xlabel(u"Generality  \u2192", fontsize=10.5)
ax.set_title("The general-purpose vs. custom trade-off is mostly an effort artifact",
             fontsize=12.5, color=NAVY, fontweight="bold", pad=12)

ax.annotate(u"Unlimited effort \u2192 within ~2\u20133\u00d7 of an ASIC,\nwith full flexibility (estimated)",
            xy=(2, 2.8), xytext=(2.18, 6.6), fontsize=8.8, color=NAVY,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.3))
ax.annotate("Realizable frontier = intrinsic physical fabric tax -\nthe irreducible floor; effort removes everything above it",
            xy=(3, 25), xytext=(1.12, 155), fontsize=8.5, color=NAVY,
            arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.1))
ax.annotate("gap smallest here:\nlittle left to program\n(but fixed forever)",
            xy=(1, 1.0), xytext=(0.6, 1.75), fontsize=8, color=SLATE)
ax.annotate("at the general-purpose end the\nresidual gap is architectural,\nnot a matter of effort",
            xy=(5, 235), xytext=(3.72, 100), fontsize=8, color=SLATE,
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.0))

ax.grid(True, which="both", axis="y", ls=":", color="#dde2e8", zorder=0)
ax.annotate(u"~3\u201315\u00d7 on regular kernels;\n~1.2\u00d7 on tensor-core matmul (Dally '20)",
            xy=(4.02, 8.6), xytext=(3.85, 20), fontsize=7.4, color=SLATE,
            arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.0))
ax.legend(fontsize=8.2, loc="lower right", framealpha=0.96, edgecolor="#d6dce2")
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)

plt.tight_layout()
for p in ["the-performance-commons-figure.png",
          "the-performance-commons-figure.png"]:
    plt.savefig(p, dpi=200, bbox_inches="tight")
print("figure written")
