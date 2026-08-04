#!/usr/bin/env python3
"""
Tolerance on the insurance estimate: profit vs multiple on the premium.

The premium is the least-supported number in the model — no source reports how
often shared work causes an incident, so the per-machine annual probability is
swept rather than known. This asks the practical question: how far wrong can
that estimate be before the business stops working?

Baseline premium (p_m = 1e-3, the pessimistic sweep point), actuarial_model.py:
  Case 1 $127.69 · Case 2 $1.28 · Case 3 $0.11 · Case 4 $0.11
Cost stack and profit baselines from profit_per_machine.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, csv, pathlib

RATE, HOURS = 0.1379, 8760
SEV, LR, P_M = 83_000, 0.65, 1e-3
IDX = {"Case 1": 1.0, "Case 2": 0.010, "Case 3": 0.0009, "Case 4": 0.0009}
FIXED = {"Case 1": 8.50, "Case 2": 57.75, "Case 3": 17.95, "Case 4": 19.59}
COLOR = {"Case 1": "#c0392b", "Case 2": "#e67e22", "Case 3": "#27ae60", "Case 4": "#2980b9"}
CONFIGS = {"high, 4090 ($1,577/yr)": (1577, 515), "mid, 3090-class ($596/yr)": (596, 415)}

def en(w): return w / 1000 * RATE * HOURS

mult = np.logspace(-1, 4.3, 600)
rows = []
fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

for ax, (cfg, (rev, w)) in zip(axes, CONFIGS.items()):
    headroom_max = rev - en(w) - min(FIXED.values())
    for c in IDX:
        base = P_M * IDX[c] * SEV / LR
        headroom = rev - en(w) - FIXED[c]
        ax.plot(mult, headroom - base * mult, color=COLOR[c], lw=1.9,
                label=f"{c}   base ${base:,.2f}")
        be = headroom / base
        rows.append({"config": cfg, "case": c, "baseline_premium_usd": round(base, 2),
                     "profit_at_1x_usd": round(headroom - base, 2),
                     "breakeven_multiple": round(be, 1)})
        if 0.1 < be < 10**4.3:
            ax.plot([be], [0], "o", color=COLOR[c], ms=6, zorder=6,
                    markeredgecolor="white", markeredgewidth=0.8)
            ax.annotate(f"{be:,.0f}×", xy=(be, 0), xytext=(0, 9),
                        textcoords="offset points", ha="center",
                        fontsize=8, color=COLOR[c], fontweight="bold")
    ax.axhline(0, color="0.3", lw=1.0, ls="--")
    ax.set_xscale("log")
    ax.set_ylim(-350, max(headroom_max * 1.12, 200))
    ax.set_xlim(0.1, 10**4.3)
    ax.set_xlabel("multiple on the insurance premium")
    ax.set_title(cfg, fontsize=11)
    ax.grid(alpha=0.25, lw=0.5)

axes[0].set_ylabel("profit per machine per year ($)")
axes[0].legend(fontsize=8.5, loc="lower left", framealpha=0.95)
fig.suptitle("Tolerance on the insurance estimate: where each architecture breaks even",
             fontsize=12.5, y=0.985)
fig.tight_layout()
out = pathlib.Path(__file__).with_name("insurance_sensitivity.png")
fig.savefig(out, dpi=150)
print(f"wrote {out.name}")

o = pathlib.Path(__file__).with_name("insurance_sensitivity.csv")
with o.open("w", newline="") as f:
    wtr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wtr.writeheader()
    for r in rows: wtr.writerow(r)
print(f"wrote {o.name}\n")
print(f"{'config':26s}{'case':9s}{'base prem':>11s}{'profit@1x':>11s}{'break-even':>12s}")
for r in rows:
    print(f"{r['config']:26s}{r['case']:9s}{r['baseline_premium_usd']:>11,.2f}"
          f"{r['profit_at_1x_usd']:>11,.0f}{r['breakeven_multiple']:>11,.0f}×")
