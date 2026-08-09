#!/usr/bin/env python3
"""
S17 figure: innovator capture of social returns, re-solved at measured
imitation lags. Horizontal bars, linear axis, one hue + gray baseline.

Values come from nordhaus_recompute.py's normalized column (anchored to
Nordhaus's published 2.2% at lambda=0.20, a held at his 0.07). Sources for
each lag: imitation_lag.csv. The rising-social-value half of the wedge is
conceptual and stays in the caption, per the repo rule that conceptual
elements are labelled as such (and the dataviz one-axis rule).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nordhaus_recompute import capture_norm, A_NORDHAUS

BLUE = "#2a78d6"
GRAY = "#898781"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e1e0d9"
SURFACE = "#ffffff"

rows = [
    ("Nordhaus baseline, 1948–2001\n(λ = 0.20/yr, from patent renewals)", 0.20, GRAY, None),
    ("GPT-3 → OPT-175B era, 2020–22\n(lag ≈23 mo)", 12 / 23, BLUE, None),
    ("Epoch open-models report, 2024\n(lag ≈ 1 yr)", 1.0, BLUE, None),
    ("Epoch ECI, Jan–May 2026\n(lag ≈ 4 mo)", 3.0, BLUE, None),
    ("Epoch ECI, Jan 2023–Oct 2025\n(lag ≈ 3 mo)", 4.0, BLUE, None),
]

fig, ax = plt.subplots(figsize=(6.6, 3.0), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

labels = [r[0] for r in rows]
vals = [100 * capture_norm(A_NORDHAUS, r[1]) for r in rows]
colors = [r[2] for r in rows]
y = list(range(len(rows)))[::-1]

ax.barh(y, vals, height=0.62, color=colors, edgecolor="none")

baseline = vals[0]
for yi, v, (label, lam, c, _) in zip(y, vals, rows):
    fold = baseline / v
    fold_txt = f"{fold:.0f}×" if fold >= 10 else f"{fold:.1f}×"
    txt = f"{v:.2f}%" + ("" if fold < 1.05 else f"   ({fold_txt} below baseline)")
    ax.text(v + 0.04, yi, txt, va="center", ha="left", fontsize=8.5,
            color=INK)

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=8.5, color=INK)
ax.set_xlim(0, 3.05)
ax.set_xlabel("share of the social returns to innovation captured by the innovator\n"
              "(Nordhaus WP 10433 machinery; appropriability held at his α = 0.07)",
              fontsize=8.5, color=MUTED)
ax.xaxis.set_major_formatter(lambda x, _: f"{x:g}%")
ax.tick_params(axis="x", labelsize=8, colors=MUTED, length=0)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, linewidth=0.7)
ax.set_axisbelow(True)
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#c3c2b7")

fig.tight_layout(pad=0.4)
out = __file__.replace("build_figure.py", "s17-capture-collapse.png")
fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
print(f"wrote {out}")
