#!/usr/bin/env python3
"""§4.9 bypass-arm design schematic: the detector-evasion search loop.

The figure a reader needs to understand what a 'variant', a 'target', a
'submission' and a 'flip' are, and where the detector does and does not enter
(review item B3). Produces bypass_search.png.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(7.4, 5.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

def box(x, y, w, h, text, fc="#eef2f7", ec="#33415c"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                 fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)

def arrow(x1, y1, x2, y2, text="", ls="-", color="#33415c"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                 mutation_scale=13, lw=1.3, color=color, linestyle=ls))
    if text:
        ax.text((x1 + x2) / 2 + 0.15, (y1 + y2) / 2, text, fontsize=7.5,
                ha="left", va="center", color=color)

# the attack loop (no detector inside it)
box(0.3, 8.4, 3.2, 1.1, "TARGET\na flagged speech", fc="#fdecea", ec="#c0392b")
box(3.9, 8.4, 3.0, 1.1, "Opus rewrites\n(3 variants/round)")
box(7.3, 8.4, 2.4, 1.1, "Opus self-score\n(AI + plausibility)")
box(3.9, 6.5, 3.0, 1.0, "keep the best;\nrepeat ~6 rounds", fc="#e8f3ec", ec="#1e6b3a")
arrow(3.5, 8.95, 3.9, 8.95)
arrow(6.9, 8.95, 7.3, 8.95)
arrow(5.4, 8.4, 5.4, 7.5)                                  # down into loop
ax.add_patch(FancyArrowPatch((3.9, 7.0), (2.0, 7.0), arrowstyle="-|>",
             mutation_scale=13, lw=1.3, color="#33415c",
             connectionstyle="arc3,rad=-0.3"))
ax.add_patch(FancyArrowPatch((2.0, 7.0), (4.6, 8.4), arrowstyle="-|>",
             mutation_scale=13, lw=1.3, color="#33415c",
             connectionstyle="arc3,rad=-0.3"))
ax.text(1.35, 7.6, "score ≥ 50:\ndiscard,\nrewrite again", fontsize=7.3,
        ha="center", va="center", color="#33415c")

ax.text(8.0, 6.55, "the attack queries\nthe detector\nZERO times",
        ha="center", fontsize=7.8, style="italic", color="#c0392b")

# submission gate + detector
box(3.5, 4.4, 3.0, 1.0, "score < 50:\nSUBMIT to Pangram", fc="#fff6e5", ec="#b9770e")
arrow(5.4, 6.5, 5.0, 5.4, "one SUBMISSION = one variant")
box(3.5, 2.4, 3.0, 1.0, "Pangram verdict:\nAI / Mixed / Human", fc="#e9e6f7", ec="#5b4b9a")
arrow(5.0, 4.4, 5.0, 3.4)

# outcomes
box(0.3, 0.4, 4.3, 1.2,
    "FLIP: verdict leaves AI\n(→ Mixed or → Human)", fc="#eef2f7")
box(5.1, 0.4, 4.3, 1.2,
    "SUCCESS: → Human\n(the reversal we count)", fc="#e8f3ec", ec="#1e6b3a")
arrow(4.3, 2.4, 2.8, 1.6)
arrow(5.7, 2.4, 7.0, 1.6)

ax.text(5, 9.75, "Detector-evasion search: the attack self-screens; the "
        "detector is queried only at submission",
        ha="center", fontsize=9.5, weight="bold")
fig.tight_layout()
fig.savefig("bypass_search.png", dpi=130, bbox_inches="tight")
print("wrote bypass_search.png")
