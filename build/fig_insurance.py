#!/usr/bin/env python3
"""Figure 8 — tolerance on the insurance estimate.

Profit per machine per year against a multiple on the insurance premium, for
four isolation architectures at two machine configurations. Break-even
crossings annotated. Inputs and derivations:
analysis/enterprise-idle-fleet/{actuarial_model,profit_per_machine}.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pathlib

RATE, HOURS = 0.1379, 8760
SEV, LR, P_M = 83_000, 0.65, 1e-3
IDX = {"Case 1": 1.0, "Case 2": 0.010, "Case 3": 0.0009, "Case 4": 0.0009}
FIXED = {"Case 1": 8.50, "Case 2": 57.75, "Case 3": 17.95, "Case 4": 19.59}
LBL = {"Case 1": "1  same OS + network", "Case 2": "2  separate VM + NIC",
       "Case 3": "3  hardware partition", "Case 4": "4  purpose-built silicon"}
COLOR = {"Case 1": "#b0392b", "Case 2": "#d98120", "Case 3": "#2a8f57", "Case 4": "#2d6ca8"}
CONFIGS = {"high configuration  ($1,577/yr)": (1577, 515),
           "mid configuration  ($596/yr)": (596, 415)}

def en(w): return w / 1000 * RATE * HOURS

mult = np.logspace(-1, 4.3, 600)
fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7))

for ax, (cfg, (rev, w)) in zip(axes, CONFIGS.items()):
    top = rev - en(w) - min(FIXED.values())
    for c in IDX:
        base = P_M * IDX[c] * SEV / LR
        head = rev - en(w) - FIXED[c]
        ax.plot(mult, head - base * mult, color=COLOR[c], lw=1.7, label=LBL[c])
        be = head / base
        if 0.1 < be < 10**4.3:
            ax.plot([be], [0], "o", color=COLOR[c], ms=5.5, zorder=6,
                    markeredgecolor="white", markeredgewidth=0.8)
            ax.annotate(f"{be:,.0f}×", xy=(be, 0), xytext=(0, 8),
                        textcoords="offset points", ha="center",
                        fontsize=7.5, color=COLOR[c], fontweight="bold")
    ax.axhline(0, color="0.3", lw=0.9, ls="--")
    ax.set_xscale("log")
    ax.set_ylim(-330, max(top * 1.14, 190))
    ax.set_xlim(0.1, 10**4.3)
    ax.set_xlabel("multiple on the insurance premium", fontsize=8.5)
    ax.set_title(cfg, fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.22, lw=0.5)

axes[0].set_ylabel("profit per machine per year ($)", fontsize=8.5)
axes[0].legend(fontsize=7.2, loc="lower left", framealpha=0.95, title="isolation architecture",
               title_fontsize=7.4)
fig.tight_layout()
out = pathlib.Path(__file__).resolve().parents[1] / "the-performance-commons-figure-insurance.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
print(f"wrote {out.name}")
