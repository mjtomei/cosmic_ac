#!/usr/bin/env python3
"""Cross-legislature synthesis: one table, one combined p-value, one figure.

Reads every *_protocol.json (frozen protocol v1.0 output) and the matching
*_formality.json (data-defined formality control), and produces:

  - a comparison table across chambers, ordered by chamber size
  - Fisher's combined p over the CONFIRMATORY corpora only (NB is the
    discovery corpus and is reported separately, per replication_protocol.md)
  - cross_corpus.png: effect size vs chamber size, with the formality-control
    gap shown alongside each instrument value

Usage: python cross_corpus.py
"""
import glob
import json
import math
import os
import re

# seats in the chamber, for the size hypothesis
SEATS = {
    "NB": 49, "New Brunswick": 49,
    "Dail Eireann": 160, "Dáil Éireann": 160,
    "Canada House of Commons": 338,
    "UK House of Commons": 650,
    "UK House of Commons within-speaker": 650,
}
DISCOVERY = {"NB", "New Brunswick"}


def seats_for(name):
    for k, v in SEATS.items():
        if name.lower().startswith(k.lower()):
            return v
    return None


def fisher(ps):
    """Fisher's method; ps may contain conservative bounds."""
    X = -2 * sum(math.log(p) for p in ps)
    df = 2 * len(ps)
    # survival of chi2 with even df has a closed form
    k = df // 2
    s = sum((X / 2) ** i / math.factorial(i) for i in range(k))
    return X, df, math.exp(-X / 2) * s


def main():
    rows = []
    for path in sorted(glob.glob("**/*_protocol.json", recursive=True)):
        d = json.load(open(path))
        name = d["corpus"]
        base = re.sub(r"\W+", "_", name.lower()) + "_formality.json"
        fm = None
        for cand in (base, os.path.join(os.path.dirname(path), base)):
            if os.path.exists(cand):
                fm = json.load(open(cand))
                break
        p = d["primary_p"] or (1.0 / d["n_placebo"])
        rows.append({
            "corpus": name, "seats": seats_for(name),
            "pre_Mw": d["pre_words"] / 1e6, "post_Mw": d["post_words"] / 1e6,
            "primary": d["primary_mean_logFC"],
            "p": p, "p_is_bound": d["primary_p"] == 0,
            "placebo_max": d["placebo_max"],
            "register": d.get("formal_register_ratio"),
            "formality_gap": fm["gap"] if fm else None,
            "discovery": name in DISCOVERY,
        })
    rows.sort(key=lambda r: (r["seats"] or 0))

    print(f"{'corpus':<38s} {'seats':>5s} {'pre Mw':>7s} {'post Mw':>8s} "
          f"{'primary':>8s} {'p':>9s} {'form.gap':>9s}")
    for r in rows:
        p = f"<{r['p']:.0e}" if r["p_is_bound"] else f"{r['p']:.3f}"
        g = f"{r['formality_gap']:+.4f}" if r["formality_gap"] is not None else "  —"
        tag = " (discovery)" if r["discovery"] else ""
        print(f"{r['corpus'][:36]+tag:<38s} {r['seats'] or '?':>5} "
              f"{r['pre_Mw']:>7.1f} {r['post_Mw']:>8.1f} "
              f"{r['primary']:>+8.4f} {p:>9s} {g:>9s}")

    conf = [r for r in rows if not r["discovery"]
            and "within-speaker" not in r["corpus"]]
    if conf:
        X, df, p = fisher([r["p"] for r in conf])
        print(f"\nFisher over {len(conf)} CONFIRMATORY corpora "
              f"({', '.join(r['corpus'] for r in conf)}):")
        print(f"  X2 = {X:.1f}, df = {df}, combined p = {p:.3e}")
        disc = [r for r in rows if r["discovery"]]
        if disc:
            print(f"  (discovery corpus {disc[0]['corpus']} reported "
                  f"separately: primary {disc[0]['primary']:+.4f}, "
                  f"p < {disc[0]['p']:.0e})")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        pts = [r for r in rows if r["seats"] and "within-speaker" not in r["corpus"]]
        if len(pts) >= 2:
            fig, ax = plt.subplots(figsize=(7.6, 4.4), dpi=150, facecolor="#fcfcfb")
            ax.set_facecolor("#fcfcfb")
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color("#d8d7d2")
            x = [r["seats"] for r in pts]
            y = [r["primary"] for r in pts]
            g = [r["formality_gap"] for r in pts]
            ax.plot(x, y, "o-", color="#2a78d6", lw=2, ms=7,
                    label="AI-instrument mean logFC")
            if all(v is not None for v in g):
                ax.plot(x, g, "s--", color="#eb6834", lw=1.6, ms=6,
                        label="gap over data-defined formality control")
            for r in pts:
                ax.annotate(r["corpus"].split(" House")[0].split(" Éireann")[0][:14],
                            (r["seats"], r["primary"]), xytext=(0, 9),
                            textcoords="offset points", fontsize=8,
                            color="#52514e", ha="center")
            ax.axhline(0, color="#d8d7d2", lw=1)
            ax.set_xscale("log")
            ax.set_xlabel("chamber size (seats, log scale)", fontsize=9, color="#52514e")
            ax.set_ylabel("mean log fold-change", fontsize=9, color="#52514e")
            ax.set_title("AI-vocabulary shift vs chamber size, frozen protocol v1.0",
                         fontsize=10.5, color="#0b0b0b", loc="left", pad=10)
            ax.tick_params(colors="#52514e", labelsize=8.5)
            ax.grid(axis="y", color="#e8e7e2", lw=0.7)
            ax.set_axisbelow(True)
            ax.legend(frameon=False, fontsize=8.5)
            fig.tight_layout()
            fig.savefig("cross_corpus.png", bbox_inches="tight")
            print("\nwrote cross_corpus.png")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
