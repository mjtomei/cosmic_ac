#!/usr/bin/env python3
"""The occupational register profile: it peaks at the insulated middle.

Reproduces the §4.6b headline table exactly. Each legislator's prior
occupation is scored on a four-level altitude ladder -- free (self-directed),
bottom, middle, top of an organisational hierarchy -- two semi-independent
ways: the DIRECTIONAL instrument (up/lateral/down/undirected components folded
to an altitude) and the CODED corporate ladder (levels scored from element
signatures by coders blind to the register and hypothesis). Both trace the
same shape: a peak at the middle and a dip at the top.

Points are each level's base slope entered alone (standardised, n = 4,762),
the values reported in the §4.6b table; bars are +/-1 se (se = beta / t). The
levels are individually noisy but jointly significant; the powered inferential
claim is the apex delta (middle - top), a dedicated contrast of +0.049 (t 3.3),
+0.067 (t 3.9) under full covariates, stated in the caption.

Writes altitude_u.png.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ORDER = ["free", "bottom", "middle", "top"]
XLAB = ["free\nself-directed", "bottom\nsupervised", "middle\ninsulated", "top\nexposed"]

# (beta, t) from the §4.6b headline table; se = |beta / t|
DIR = {"free": (-0.060, -4.2), "bottom": (-0.021, -1.5), "middle": (+0.029, 2.0), "top": (+0.010, 0.7)}
LVL = {"free": (-0.066, -4.7), "bottom": (+0.010, 0.7), "middle": (+0.028, 2.0), "top": (+0.021, 1.5)}

# Okabe-Ito colourblind-safe pair; distinct markers for redundant encoding
SERIES = [("theoretical ladder", DIR, "#0072B2", "o", -0.05),
          ("folk ladder", LVL, "#D55E00", "s", +0.05)]

fig, ax = plt.subplots(figsize=(8.2, 5.6))
ax.axhline(0, color="#c7c7c7", lw=1, zorder=1)

for name, D, col, mk, dx in SERIES:
    xs = [i + dx for i in range(len(ORDER))]
    ys = [D[k][0] for k in ORDER]
    es = [abs(D[k][0] / D[k][1]) for k in ORDER]
    ax.errorbar(xs, ys, yerr=es, fmt=f"-{mk}", color=col, lw=1.9, ms=7,
                elinewidth=1.1, capsize=3, alpha=0.95,
                markeredgecolor="white", markeredgewidth=1.1, zorder=3, label=name)

ax.set_xticks(range(len(ORDER)))
ax.set_xticklabels(XLAB, fontsize=9.5)
ax.set_ylabel("register slope, z (level entered alone)", fontsize=10.5)
ax.set_title("The machine register peaks at the insulated middle of the hierarchy,\n"
             "not at the exposed top", fontsize=12.5, loc="left", pad=30)
ax.text(0, 1.045,
        "each point: one altitude level entered alone (n = 4,762); bars ±1 se; two "
        "instruments built by different processes",
        transform=ax.transAxes, fontsize=8.7, color="#777")
ax.legend(loc="lower right", frameon=False, fontsize=10)
ax.set_xlim(-0.4, len(ORDER) - 0.55)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(length=0)
plt.tight_layout()
plt.savefig("altitude_u.png", dpi=150, bbox_inches="tight")
print("wrote altitude_u.png")
