#!/usr/bin/env python3
"""Render the two figures the review panel asked for (C59, C60).

Both plot values that are ALREADY COMMITTED in the manuscript tables they sit
beside — no new computation. To guarantee a figure can never drift from the
table above it, the numbers are parsed out of the manuscript itself rather than
transcribed here. Re-run after any edit to those tables.

  chamber_prevalence_dotplot.png  ranked dot plot of the 20 chamber rates with
                                  cluster-bootstrap 95% CIs, pooled 9.03% marked
  convergence_slopegraph.png      19 chambers, 2006 -> 2026 gap-vocabulary rate

Usage: python plot_manuscript_figures.py
"""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DRAFT = os.path.join(HERE, "S10-WRITEUP-DRAFT.md")
POOLED = 9.03                                 # the pooled rate, as the caption states

GREY, US, UK = "#8C8C8C", "#D55E00", "#0072B2"
UK_GROUP = {"UK Commons", "Scotland", "Northern Ireland", "Wales"}


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def unbold(s):
    return s.replace("**", "").strip()


def table_after(text, header_snippet):
    """Rows of the first markdown table whose header contains header_snippet."""
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if header_snippet in l and l.lstrip().startswith("|"):
            rows, j = [], i + 2          # skip header + separator
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(lines[j]); j += 1
            return rows
    raise SystemExit(f"table not found: {header_snippet!r}")


def prevalence(text):
    """20 chambers, one per row: (name, rate, lo, hi)."""
    out = []
    for line in table_after(text, "| chamber | machine-drafted share of words |"):
        c = cells(line)
        if len(c) < 3 or not c[0]:
            continue
        name, rate, ci = unbold(c[0]), unbold(c[1]), unbold(c[2])
        m = re.match(r"\[([\d.]+),\s*([\d.]+)\]", ci)
        if not m:
            continue
        out.append((name, float(rate.rstrip("%")), float(m.group(1)), float(m.group(2))))
    return out


def convergence(text):
    """19 chambers: (name, gap2006, gap2026)."""
    out = []
    for line in table_after(text, "| chamber | gap 2006"):
        c = cells(line)
        if len(c) < 3:
            continue
        name = unbold(c[0])
        try:
            out.append((name, float(unbold(c[1]).replace(",", "")),
                        float(unbold(c[2]).replace(",", ""))))
        except ValueError:
            continue
    return out


def draw_prevalence(rows, path):
    rows = sorted(rows, key=lambda r: r[1])                    # ascending, best at top
    fig, ax = plt.subplots(figsize=(6.6, 6.4))
    for i, (name, rate, lo, hi) in enumerate(rows):
        col = US if name.startswith("US ") else GREY
        ax.plot([lo, hi], [i, i], color=col, lw=1.4, alpha=.55, solid_capstyle="round", zorder=2)
        ax.plot([rate], [i], "o", color=col, ms=6, zorder=3)
        ax.text(hi + 0.5, i, f"{rate:.1f}%", va="center", ha="left", fontsize=7.5, color=col)
    ax.axvline(POOLED, color="0.35", lw=1.0, ls=":", zorder=1)
    ax.text(POOLED, len(rows) - 0.3, f" pooled {POOLED:.2f}%", fontsize=7.5,
            color="0.35", ha="left", va="top")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    for lbl, (name, *_ ) in zip(ax.get_yticklabels(), rows):
        if name.startswith("US "):
            lbl.set_color(US); lbl.set_fontweight("bold")
    ax.set_xlim(0, max(r[3] for r in rows) + 4.5)
    ax.set_xlabel("machine-drafted share of 2025–26 words (%)", fontsize=9)
    ax.set_title("Machine-drafted share by chamber\n"
                 "word- and fraction-weighted, with cluster-bootstrap 95% CIs",
                 fontsize=9.5, loc="left")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="0.9", lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"  wrote {os.path.basename(path)}  ({len(rows)} chambers)")


def spread(items, minsep, lo, hi):
    """Push overlapping labels apart, keeping order AND staying inside [lo, hi].

    A 19-chamber slopegraph collides badly at the left edge; nudging the TEXT
    (never the line) is the standard remedy. If the stack cannot fit at the
    requested separation, the separation is reduced rather than letting labels
    escape the axes.
    """
    items = sorted(items, key=lambda t: t[0])
    n = len(items)
    if n > 1:
        minsep = min(minsep, (hi - lo) / (n - 1))
    ys = [y for y, _ in items]
    for i in range(1, n):                      # push up
        ys[i] = max(ys[i], ys[i - 1] + minsep)
    if ys[-1] > hi:                            # then pull the stack back down
        shift = ys[-1] - hi
        ys = [y - shift for y in ys]
        for i in range(n - 2, -1, -1):         # re-separate downward
            ys[i] = min(ys[i], ys[i + 1] - minsep)
    ys = [min(max(y, lo), hi) for y in ys]
    return [(ys[i], items[i][1]) for i in range(n)]


def draw_convergence(rows, path):
    fig, ax = plt.subplots(figsize=(7.6, 7.4))
    vals = [v for _, a, b in rows for v in (a, b)]
    lo_v, hi_v = min(vals), max(vals)
    pad = (hi_v - lo_v) * 0.06
    ax.set_ylim(lo_v - pad, hi_v + pad)
    minsep = (hi_v - lo_v) * 0.032             # ~one line of text, in data units
    lo_lab, hi_lab = lo_v - pad * 0.6, hi_v + pad * 0.6

    for name, a, b in rows:                    # lines first, labels after
        col = US if name.startswith("US ") else (UK if name in UK_GROUP else GREY)
        wide = col is not GREY
        ax.plot([0, 1], [a, b], color=col, lw=2.0 if wide else 1.0,
                alpha=1.0 if wide else .40, zorder=3 if wide else 2,
                solid_capstyle="round")
        ax.plot([0, 1], [a, b], "o", color=col, ms=4 if wide else 2.5,
                alpha=1.0 if wide else .40, zorder=3 if wide else 2)

    for y, (name, val, side) in spread([(a, (n, a, "L")) for n, a, _ in rows], minsep, lo_lab, hi_lab):
        col = US if name.startswith("US ") else (UK if name in UK_GROUP else GREY)
        wide = col is not GREY
        ax.annotate(f"{name} {val:,.0f}", xy=(0, val), xytext=(-0.06, y),
                    textcoords="data", ha="right", va="center", fontsize=7.2,
                    color=col if wide else "0.45",
                    fontweight="bold" if wide else "normal",
                    arrowprops=dict(arrowstyle="-", lw=0.5,
                                    color=col if wide else "0.75", alpha=.7,
                                    shrinkA=1, shrinkB=1))
    for y, (name, val, side) in spread([(b, (n, b, "R")) for n, _, b in rows], minsep, lo_lab, hi_lab):
        col = US if name.startswith("US ") else (UK if name in UK_GROUP else GREY)
        wide = col is not GREY
        ax.annotate(f"{val:,.0f} {name}" if wide else f"{val:,.0f}",
                    xy=(1, val), xytext=(1.06, y), textcoords="data",
                    ha="left", va="center", fontsize=7.2,
                    color=col if wide else "0.45",
                    fontweight="bold" if wide else "normal",
                    arrowprops=dict(arrowstyle="-", lw=0.5,
                                    color=col if wide else "0.75", alpha=.7,
                                    shrinkA=1, shrinkB=1))

    ax.set_xlim(-0.62, 1.62)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["2006", "2026"], fontsize=9)
    ax.set_ylabel("gap-vocabulary rate (occurrences per 100k words)", fontsize=9)
    ax.set_title("The fan closes upward: chambers converge on the level the\n"
                 "United States already held — the UK group climbs steepest,\n"
                 "while the two US chambers stay flat",
                 fontsize=9.5, loc="left")
    for s_ in ("top", "right", "bottom"):
        ax.spines[s_].set_visible(False)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color="0.92", lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"  wrote {os.path.basename(path)}  ({len(rows)} chambers)")


def main():
    text = open(DRAFT, encoding="utf-8").read()
    p = prevalence(text)
    c = convergence(text)
    print(f"parsed {len(p)} prevalence rows, {len(c)} convergence rows from the manuscript")
    assert len(p) == 20, f"expected 20 chambers, parsed {len(p)}"
    assert len(c) == 19, f"expected 19 chambers, parsed {len(c)}"
    draw_prevalence(p, os.path.join(HERE, "chamber_prevalence_dotplot.png"))
    draw_convergence(c, os.path.join(HERE, "convergence_slopegraph.png"))


if __name__ == "__main__":
    main()
