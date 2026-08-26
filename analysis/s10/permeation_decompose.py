#!/usr/bin/env python3
"""Did the register rise because people changed, or because the people changed?

WHY

The frequency-side result -- the register's rate rises sharply after 2022 --
is the study's headline, and it is an AGGREGATE. An aggregate rate can rise
two ways that mean opposite things:

  WITHIN       the same legislators, still sitting, use more of the register
               than they did before. That is permeation: the machines' idiom
               entering the speech of people who were already there.
  COMPOSITION  the chamber's membership turned over, and the arrivals speak
               more of it than the departures did. That is selection, and it
               says nothing about anyone changing how they talk.

§4.6 establishes a large birth-cohort gradient, which is the composition
channel's engine; §4.7 and the within-speaker corpora argue the within
channel is real. Neither states the split. This does, panel-wide, on the
pre/post windows the study already uses: 2018-2022 against 2023-2026.

ESTIMAND. The aggregate register rate R = (style-word occurrences) / (words
spoken), per 1,000 words, over all 22 chambers, computed separately in each
window over the members who qualify in that window. A member qualifies in a
window with >= 2,000 tokens there -- below that a member's rate is mostly
sampling noise, and the same floor is used by the study's other member-level
cuts.

TWO INSTRUMENTS, because the pooled one is misleading on its own. The full
407-word style set is dominated by words that are common in ordinary
parliamentary English -- "this", "their", "through", "between" -- so its
pooled rate sits near 35 per 1,000 and moves by about one percent across
these windows. That pooled rate is nevertheless the exact quantity §4.6's
class and altitude regressions are run on, so it is decomposed first. The
RARE subset -- style words whose pooled 2018-2022 rate is under 5 per 100,000
words, the same threshold fig_trend.py and plot_trend_from_cache.py use to
define the study's "subtler set" -- is decomposed second, and it is the one
that carries the post-2022 movement.

DECOMPOSITION. Foster-Haltiwanger-Krizan, the standard exact five-term split
of a change in a share-weighted mean, with legislators playing the part of
firms. With s the member's token share of the window, r the member's rate,
S continuing members, E entrants (window 2 only), L leavers (window 1 only):

  WITHIN   = sum_S  s_i0 (r_i1 - r_i0)
  BETWEEN  = sum_S (s_i1 - s_i0)(r_i0 - R0)      reallocation among stayers
  CROSS    = sum_S (s_i1 - s_i0)(r_i1 - r_i0)    the interaction
  ENTRY    = sum_E  s_i1 (r_i1 - R0)
  EXIT     = -sum_L s_i0 (r_i0 - R0)

and WITHIN + BETWEEN + CROSS + ENTRY + EXIT = R1 - R0 exactly; the code
asserts it. The three-term reading asked of a decomposition like this groups
BETWEEN + ENTRY + EXIT as COMPOSITION and keeps CROSS as the INTERACTION, so
both groupings are printed.

Entrants and leavers are measured against R0, the base-window aggregate, so
ENTRY is positive when arrivals speak MORE register than the chamber did
before them, and EXIT is positive when departures spoke LESS.

An equal-member-weight version is printed alongside, because the token-share
weighting lets a handful of very loud members carry the aggregate, and the
two answers should be compared rather than one of them chosen quietly.

A DATA PROBLEM THIS UNCOVERED, AND HOW IT IS HANDLED. Members are keyed by
the normalised printed speaker string, and some Hansards CHANGE that string's
format mid-series. Victoria switched from "Ms SYMES" to "Jaclyn SYMES" exactly
at the 2022/2023 boundary -- the boundary between these two windows -- so only
2 of ~125 sitting Victorian members carry over; Western Australia switched
from initials ("Mr R.S. LOVE") to given names in 2025. A member whose printed
name changes reads as a leaver plus an entrant, which moves their contribution
out of WITHIN and into COMPOSITION. The bias therefore runs one way: measured
within-member change is a LOWER bound. Three things are done about it: the
per-chamber carryover across the window boundary is printed as a diagnostic;
the decomposition is re-run with chamber-local SURNAME RECONCILIATION, which
merges a window-1-only key with a window-2-only key when they are the only two
keys sharing a surname in that chamber; and the decomposition is re-run again
on only the chambers whose boundary carryover is already clean. The three
answers bracket the truth.

The reconciliation is deliberately conservative and recovers only part of the
damage -- Victoria has THREE printed-name eras, not two (its 2006-2019 store
prints given names, its 2011-2022 fill prints "Mr DAVIS", and 2023 onward
prints given names again), so many Victorian surnames carry a key that is
present in BOTH windows alongside the split pair, and the two-key test
declines to merge them. That is why the clean-chambers arm matters: it drops
Victoria outright, and the answer barely moves.

CIs: member bootstrap, seed 11, 1,000 draws over the union of members, every
term and both aggregate levels recomputed inside each draw. Percentile
intervals. Shares are reported as component / (R1 - R0) and are unstable
wherever the denominator is small, so the absolute components carry the
result and the shares are the gloss.

WRITES permeation_decompose.txt (tee'd) and permeation_components.csv.

Usage: python permeation_decompose.py
"""
import csv
import gzip
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

W0 = (2018, 2022)
W1 = (2023, 2026)
MIN_TOK = 2000
RARE_PER_100K = 5.0
NBOOT = 1000
SEED = 11
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


def fhk(t0, h0, t1, h1, weighted=True):
    """Five-term FHK split of the change in the aggregate rate per 1,000.

    t0/h0, t1/h1 are per-member token and hit arrays for the two windows;
    a member absent from a window has t = 0 there.
    """
    a0, a1 = t0 >= MIN_TOK, t1 >= MIN_TOK
    T0, T1 = t0[a0].sum(), t1[a1].sum()
    if T0 <= 0 or T1 <= 0:
        return None
    if weighted:
        s0 = np.where(a0, t0 / T0, 0.0)
        s1 = np.where(a1, t1 / T1, 0.0)
    else:                                   # equal weight per qualifying member
        s0 = np.where(a0, 1.0 / a0.sum(), 0.0)
        s1 = np.where(a1, 1.0 / a1.sum(), 0.0)
    r0 = np.where(a0, h0 / np.maximum(t0, 1) * 1000.0, 0.0)
    r1 = np.where(a1, h1 / np.maximum(t1, 1) * 1000.0, 0.0)
    R0, R1 = float(s0 @ r0), float(s1 @ r1)
    S, E, L = a0 & a1, ~a0 & a1, a0 & ~a1
    within = float((s0[S] * (r1[S] - r0[S])).sum())
    between = float(((s1[S] - s0[S]) * (r0[S] - R0)).sum())
    cross = float(((s1[S] - s0[S]) * (r1[S] - r0[S])).sum())
    entry = float((s1[E] * (r1[E] - R0)).sum())
    exit_ = float(-(s0[L] * (r0[L] - R0)).sum())
    assert abs(within + between + cross + entry + exit_ - (R1 - R0)) < 1e-8, \
        "FHK identity broken"
    return dict(R0=R0, R1=R1, d=R1 - R0, within=within, between=between,
                cross=cross, entry=entry, exit=exit_,
                comp=between + entry + exit_,
                nS=int(S.sum()), nE=int(E.sum()), nL=int(L.sum()),
                T0=float(T0), T1=float(T1))


def ci(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return (np.percentile(v, 2.5), np.percentile(v, 97.5))


TERMS = [("WITHIN", "within", "stayers' own change"),
         ("BETWEEN", "between", "reallocation among stayers"),
         ("CROSS", "cross", "the interaction"),
         ("ENTRY", "entry", "arrivals vs the base-window aggregate"),
         ("EXIT", "exit", "departures vs the base-window aggregate")]


def arm(name, t0, h0, t1, h1, ch, live, csv_rows):
    say(f"\n{'#' * 74}\nINSTRUMENT: {name}")
    main_res = {}
    for lab, wt in (("token-weighted", True), ("equal member weight", False)):
        r = fhk(t0, h0, t1, h1, weighted=wt)
        main_res[lab] = r
        say(f"\n{'=' * 74}\nAGGREGATE REGISTER RATE, {lab}")
        say(f"  {W0[0]}-{W0[1]}: {r['R0']:.4f} per 1,000 words   "
            f"({r['T0'] / 1e6:.0f}M words, {r['nS'] + r['nL']:,} members)")
        say(f"  {W1[0]}-{W1[1]}: {r['R1']:.4f} per 1,000 words   "
            f"({r['T1'] / 1e6:.0f}M words, {r['nS'] + r['nE']:,} members)")
        say(f"  change  : {r['d']:+.4f}  ({100 * r['d'] / r['R0']:+.1f}%)")
        say(f"  members : {r['nS']:,} in both windows, {r['nE']:,} entrants, "
            f"{r['nL']:,} leavers")

    rng = np.random.default_rng(SEED)
    idx_live = np.flatnonzero(live)
    boot = {lab: defaultdict(list) for lab in main_res}
    for _ in range(NBOOT):
        j = idx_live[rng.integers(0, len(idx_live), len(idx_live))]
        for lab, wt in (("token-weighted", True),
                        ("equal member weight", False)):
            r = fhk(t0[j], h0[j], t1[j], h1[j], weighted=wt)
            if r:
                for k, v in r.items():
                    boot[lab][k].append(v)

    for lab in main_res:
        r = main_res[lab]
        say(f"\n{'=' * 74}\nFHK DECOMPOSITION, {lab}   "
            f"(total change {r['d']:+.4f} per 1,000)")
        say(f"  {'term':<10}{'value':>10}{'share':>9}   "
            f"{'95% CI (member bootstrap)':<26}what it is")
        for nm, key, gloss in TERMS:
            lo, hi = ci(boot[lab][key])
            sh = r[key] / r["d"] if abs(r["d"]) > 1e-9 else np.nan
            say(f"  {nm:<10}{r[key]:>+10.4f}{sh:>9.3f}   "
                f"[{lo:+.4f}, {hi:+.4f}]{'':<7}{gloss}")
            csv_rows.append([name, lab, nm, f"{r[key]:.6f}", f"{sh:.4f}",
                             f"{lo:.6f}", f"{hi:.6f}"])
        say(f"  {'-' * 70}")
        say("  three-term grouping (composition = between + entry + exit):")
        for nm, key in (("WITHIN", "within"), ("COMPOSITION", "comp"),
                        ("INTERACTION", "cross")):
            lo, hi = ci(boot[lab][key])
            slo, shi = ci(np.asarray(boot[lab][key], float) /
                          np.asarray(boot[lab]["d"], float))
            sh = r[key] / r["d"] if abs(r["d"]) > 1e-9 else np.nan
            say(f"  {nm:<14}{r[key]:>+10.4f}   share {sh:>+7.3f} "
                f"[{slo:+.3f}, {shi:+.3f}]   abs CI [{lo:+.4f}, {hi:+.4f}]")
            csv_rows.append([name, lab, nm, f"{r[key]:.6f}", f"{sh:.4f}",
                             f"{lo:.6f}", f"{hi:.6f}"])
        lo, hi = ci(boot[lab]["d"])
        say(f"  {'TOTAL':<14}{r['d']:>+10.4f}   abs CI [{lo:+.4f}, {hi:+.4f}]")

    say(f"\n{'=' * 74}\nPER CHAMBER, token-weighted (no CIs; ordered by total "
        f"change)")
    say(f"  {'chamber':<10}{'R 18-22':>9}{'R 23-26':>9}{'change':>9}"
        f"{'within':>9}{'comp':>9}{'cross':>9}{'w share':>9}"
        f"{'nS':>6}{'nE':>6}{'nL':>6}")
    per = []
    for c in sorted(set(ch)):
        m = ch == c
        r = fhk(t0[m], h0[m], t1[m], h1[m], weighted=True)
        if r:
            per.append((c, r))
    for c, r in sorted(per, key=lambda x: -x[1]["d"]):
        sh = r["within"] / r["d"] if abs(r["d"]) > 1e-9 else np.nan
        say(f"  {c:<10}{r['R0']:>9.3f}{r['R1']:>9.3f}{r['d']:>+9.3f}"
            f"{r['within']:>+9.3f}{r['comp']:>+9.3f}{r['cross']:>+9.3f}"
            f"{sh:>9.2f}{r['nS']:>6}{r['nE']:>6}{r['nL']:>6}")
    say(f"  within positive in {sum(1 for _, r in per if r['within'] > 0)}"
        f"/{len(per)} chambers; composition positive in "
        f"{sum(1 for _, r in per if r['comp'] > 0)}/{len(per)}")


def surname(key):
    nm = key.split("|", 1)[1].replace(".", " ").replace("'", " ")
    parts = [p for p in nm.split() if p]
    return parts[-1] if parts else nm


def reconcile(keys, t0, t1):
    """Group index -> merged index, joining window-split name variants.

    Within one chamber, if a surname is carried by exactly two keys, one of
    which speaks only in window 1 and the other only in window 2, they are
    almost certainly the same person under two printed forms. Any other
    pattern is left alone.
    """
    by = defaultdict(list)
    for i, k in enumerate(keys):
        by[(k.split("|")[0], surname(k))].append(i)
    grp = np.arange(len(keys))
    merged = []
    for g in by.values():
        if len(g) != 2:
            continue
        a, b = g
        pa = (t0[a] > 0, t1[a] > 0)
        pb = (t0[b] > 0, t1[b] > 0)
        if pa == (True, False) and pb == (False, True):
            grp[b] = a
            merged.append((keys[a], keys[b]))
        elif pa == (False, True) and pb == (True, False):
            grp[a] = b
            merged.append((keys[b], keys[a]))
    return grp, merged


def collapse(grp, *arrs):
    u, inv = np.unique(grp, return_inverse=True)
    return [np.bincount(inv, weights=a, minlength=len(u)) for a in arrs], u


def main():
    cache = json.load(gzip.open(os.path.join(HERE,
                                             "member_cache_panel.json.gz"), "rt"))
    keys = sorted(cache)
    n = len(keys)
    words = sorted({w for r in cache.values() for y in r["years"].values()
                    for w in y["w"]})
    ch = np.array([k.split("|")[0] for k in keys])

    # per-member window tokens, all-word hits, and per-word hits in window 0
    t0 = np.zeros(n)
    t1 = np.zeros(n)
    hw0 = defaultdict(lambda: np.zeros(n))
    hw1 = defaultdict(lambda: np.zeros(n))
    for i, k in enumerate(keys):
        for y, v in cache[k]["years"].items():
            yi = int(y)
            if W0[0] <= yi <= W0[1]:
                t0[i] += v["tot"]
                for w, c in v["w"].items():
                    hw0[w][i] += c
            elif W1[0] <= yi <= W1[1]:
                t1[i] += v["tot"]
                for w, c in v["w"].items():
                    hw1[w][i] += c
    live = (t0 > 0) | (t1 > 0)
    say(f"cache: {n:,} members, {int(live.sum()):,} speaking in "
        f"{W0[0]}-{W1[1]}, {len(set(ch))} chambers, {len(words)} style words")
    say(f"windows: {W0[0]}-{W0[1]} vs {W1[0]}-{W1[1]}; a member qualifies in a "
        f"window with >= {MIN_TOK:,} tokens there")

    pre_tok = t0.sum()
    rare = [w for w in words
            if hw0[w].sum() / pre_tok * 1e5 < RARE_PER_100K]
    say(f"rare subset (< {RARE_PER_100K:g} per 100k in {W0[0]}-{W0[1]}): "
        f"{len(rare)} of {len(words)} words")

    # the panel-wide yearly series, for context on what the windows contain
    yr_tok = defaultdict(float)
    yr_all = defaultdict(float)
    yr_rare = defaultdict(float)
    rset = set(rare)
    for k in keys:
        for y, v in cache[k]["years"].items():
            yi = int(y)
            if yi < 2010:
                continue
            yr_tok[yi] += v["tot"]
            yr_all[yi] += sum(v["w"].values())
            yr_rare[yi] += sum(c for w, c in v["w"].items() if w in rset)
    say(f"\npanel-wide yearly rates (all 22 chambers; chamber mix varies, so "
        f"read the shape, not the level)")
    say(f"  {'year':<6}{'Mwords':>9}{'all 407 /1k':>13}{'rare /100k':>12}")
    for y in sorted(yr_tok):
        say(f"  {y:<6}{yr_tok[y] / 1e6:>9.1f}"
            f"{yr_all[y] / yr_tok[y] * 1e3:>13.2f}"
            f"{yr_rare[y] / yr_tok[y] * 1e5:>12.2f}")

    # ------------------------------------ boundary diagnostic: key carryover
    say(f"\n{'=' * 74}\nSPEAKER-KEY CARRYOVER ACROSS THE WINDOW BOUNDARY "
        f"({W0[1]} -> {W1[0]})")
    say("  A chamber whose Hansard changes its printed-name format at the")
    say("  boundary shows near-zero carryover, and its members read as")
    say("  leavers plus entrants rather than as stayers.")
    yset = defaultdict(lambda: defaultdict(set))
    for k in keys:
        for y, v in cache[k]["years"].items():
            if v["tot"] >= MIN_TOK:
                yset[k.split("|")[0]][int(y)].add(k)
    say(f"  {'chamber':<10}{'n ' + str(W0[1]):>8}{'n ' + str(W1[0]):>8}"
        f"{'carried':>9}{'share':>8}")
    clean = []
    for c in sorted(yset):
        a, b = yset[c].get(W0[1], set()), yset[c].get(W1[0], set())
        if not a or not b:
            continue
        sh = len(a & b) / min(len(a), len(b))
        clean.append((c, sh))
        flag = "   <-- format break" if sh < 0.5 else ""
        say(f"  {c:<10}{len(a):>8}{len(b):>8}{len(a & b):>9}{sh:>8.2f}{flag}")
    ok_ch = {c for c, s in clean if s >= 0.5}
    say(f"  chambers with clean carryover (>= 0.50): {len(ok_ch)} of "
        f"{len(clean)}")
    missing = sorted(set(yset) - {c for c, _ in clean})
    if missing:
        say(f"  not shown, no qualifying members in one of the two boundary "
            f"years: {', '.join(missing)}")
        say("    NI: the Assembly was suspended (no 2023 sittings) -- real.")
        say("    IE: the store itself has a COMPLETE 2023 HOLE. Both "
            "ie/segments_ie_en.jsonl")
        say("    and ie/segments_ie.jsonl jump 2022 -> 2024, so every Irish "
            "series in this")
        say("    study is missing the first full machine-era year. Flagged, "
            "not patched here.")

    csv_rows = []
    h0all = np.sum([hw0[w] for w in words], axis=0)
    h1all = np.sum([hw1[w] for w in words], axis=0)
    h0r = np.sum([hw0[w] for w in rare], axis=0)
    h1r = np.sum([hw1[w] for w in rare], axis=0)
    rare_lab = f"rare subset, {len(rare)} words (< {RARE_PER_100K:g}/100k pre)"
    arm("all 407 style words", t0, h0all, t1, h1all, ch, live, csv_rows)
    arm(rare_lab, t0, h0r, t1, h1r, ch, live, csv_rows)

    # ---------------------------------------------- robustness 1: reconciled
    grp, merged = reconcile(keys, t0, t1)
    say(f"\n{'#' * 74}\nROBUSTNESS 1 -- SURNAME RECONCILIATION: "
        f"{len(merged):,} window-split key pairs merged")
    for a, b in merged[:8]:
        say(f"    {a}  +  {b}")
    if len(merged) > 8:
        say(f"    ... and {len(merged) - 8:,} more "
            f"(chambers: {', '.join(sorted({a.split('|')[0] for a, _ in merged}))})")
    (T0, H0a, T1, H1a, H0r, H1r), u = collapse(
        grp, t0, h0all, t1, h1all, h0r, h1r)
    chg = np.array([keys[i].split("|")[0] for i in u])
    lv = (T0 > 0) | (T1 > 0)
    arm("all 407 style words, surname-reconciled", T0, H0a, T1, H1a, chg, lv,
        csv_rows)
    arm(rare_lab + ", surname-reconciled", T0, H0r, T1, H1r, chg, lv, csv_rows)

    # --------------------------------------- robustness 2: clean chambers only
    m = np.isin(ch, sorted(ok_ch))
    say(f"\n{'#' * 74}\nROBUSTNESS 2 -- ONLY THE {len(ok_ch)} CHAMBERS WITH "
        f"CLEAN BOUNDARY CARRYOVER")
    arm(rare_lab + f", {len(ok_ch)} clean chambers",
        t0[m], h0r[m], t1[m], h1r[m], ch[m], live[m], csv_rows)

    with open(os.path.join(HERE, "permeation_components.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["instrument", "weighting", "term", "value_per_1000",
                    "share", "ci_lo", "ci_hi"])
        w.writerows(csv_rows)
    open(os.path.join(HERE, "permeation_decompose.txt"), "w").write(
        "\n".join(OUT) + "\n")
    print("\nwrote permeation_decompose.txt, permeation_components.csv")


if __name__ == "__main__":
    main()
