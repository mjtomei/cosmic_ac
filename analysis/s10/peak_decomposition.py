#!/usr/bin/env python3
"""Does the class peak migrate? Two aggregations, and what moves the gap.

WHY

§4.6b asserts that the register's class profile is an inverted U peaking one
rung below the top and that "the peak itself never moves". The committed
generator, build_class_by_era.py, reaches that conclusion at MEMBER level --
one value per member per five-year bin -- and its own footnote concedes that
"a member-YEAR aggregation of the same data would show the peak migrating
downward", calling that an artifact of counting long-serving members once per
year. That concession is asserted, not shown, and the two aggregations have
never been printed side by side. If the sign of the headline claim depends on
which of two defensible weightings is chosen, readers are owed both.

The second question follows from the first. §4.6b also reports one slow
movement inside the stable shape: the II-over-I gap is narrowest in the
machine-era bin (+0.08 against a series high of +0.23), read as compression --
the chase direction. But a class mean can fall between bins for two entirely
different reasons: the SAME members changed (within-member change), or the
class's MEMBERSHIP changed (high-register members left, low-register members
entered). Those have opposite meanings. Compression that lives in stayers is
diffusion; compression that lives in turnover is a selection story about who
gets elected, with no diffusion in it at all. So each bin-to-bin change is
split Firebaugh-style, with members playing the role cohorts play in his
repeated-survey decomposition.

SPEC

  rows      the committed member-year panel (panel_estimation.provincial_rows
            + tier1_rows, carrying their own >=8,000-words-per-year floor and
            tier-1 ambiguity drops), 1997 onward, EGP-coded members only.
  bins      build_class_by_era.era() verbatim -- six EQUAL five-year bins
            anchored at the data's end, 1997-2001 .. 2022-2026.
  year z    each member-year's rate z-scored against ALL member-years of its
            chamber x bin (unweighted mean, population sd), as
            build_class_by_era. Era rise and chamber level are removed; only
            the cross-class shape survives.
  MEMBER aggregation      a member's bin value is the word-weighted mean of
            their year z's; one value per member per bin, equal weight after
            that. This is build_class_by_era's estimator and is reproduced
            here to the fourth decimal as a check.
  MEMBER-YEAR aggregation every member-year is a unit; the class-bin cell is
            the unweighted mean of its member-years' z. Long-serving members
            count once per year served.

DECOMPOSITION. For class c and consecutive bins t -> t+1, split members into
stayers S (a value in both bins), leavers L (bin t only), entrants E (bin t+1
only), with shares p taken within the bin:

  M(t)   = p_S,t   m_S,t   + p_L,t   m_L,t
  M(t+1) = p_S,t+1 m_S,t+1 + p_E,t+1 m_E,t+1

  WITHIN      = p_S,t (m_S,t+1 - m_S,t)
  ENTRY       = p_E,t+1 (m_E,t+1 - m_S,t+1)
  EXIT        = - p_L,t (m_L,t - m_S,t+1)
  COMPOSITION = ENTRY + EXIT

and WITHIN + COMPOSITION = M(t+1) - M(t) exactly (algebra in the code's test).
Entrants and leavers are each measured against the stayers' NEW level, so
COMPOSITION reads as "what turnover did relative to the people who stayed".
The same split is applied to the II-minus-I GAP by differencing the two
classes' components.

CIs: member bootstrap, seed 7, 1,000 draws, resampling MEMBERS (not member-
years) with replacement and RECOMPUTING the chamber x bin z-scaling inside
each draw, so the normalisation's own sampling error is carried rather than
treated as known. Percentile intervals.

CROSS-CHECK. The same member-level gap series is recomputed from
member_cache_panel.json.gz -- a wholly separate scan of the segment stores,
keyed CHAMBER|speaker rather than the panel's CHAMBER|speaker|person -- to
confirm the series is a property of the corpus and not of the join.

WRITES peak_decomposition.txt (tee'd) and peak_gap_series.csv.

Usage: python peak_decomposition.py
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
import panel_estimation as PE                      # noqa: E402
from build_class_by_era import era                 # noqa: E402

EGP = ["I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"]
POOL = {"IVc", "V/VI", "VIIab"}                    # build_class_by_era's tail
NBOOT = 1000
SEED = 7
OUT = []


def say(s=""):
    print(s, flush=True)
    OUT.append(s)


# ----------------------------------------------------------------- estimators
def zscore(gid, rate, ngroups):
    """z within chamber x bin: unweighted mean, population sd (as committed)."""
    n = np.bincount(gid, minlength=ngroups).astype(float)
    s = np.bincount(gid, weights=rate, minlength=ngroups)
    mu = np.divide(s, n, out=np.zeros_like(s), where=n > 0)
    d = rate - mu[gid]
    v = np.bincount(gid, weights=d * d, minlength=ngroups)
    sd = np.sqrt(np.divide(v, n, out=np.zeros_like(v), where=n > 0))
    ok = sd[gid] > 0
    z = np.zeros_like(rate)
    z[ok] = d[ok] / sd[gid][ok]
    return z, ok


def cells(mid, bid, cid, words, z, keep, nb, nc, member_level):
    """(bin, class) -> mean, and (bin, class) -> {member: value} for stayers."""
    mid, bid, cid = mid[keep], bid[keep], cid[keep]
    words, z = words[keep], z[keep]
    if member_level:
        key = mid.astype(np.int64) * nb + bid          # member x bin
        u, inv = np.unique(key, return_inverse=True)
        w = np.bincount(inv, weights=words)
        wz = np.bincount(inv, weights=words * z)
        val = wz / w
        m_of = (u // nb).astype(np.int64)
        b_of = (u % nb).astype(np.int64)
        c_of = np.zeros(len(u), dtype=np.int64)
        c_of[inv] = cid                                # class is member-constant
        return m_of, b_of, c_of, val
    return mid, bid, cid, z                            # member-year: unit = row


def class_means(b_of, c_of, val, nb, nc):
    k = b_of * nc + c_of
    n = np.bincount(k, minlength=nb * nc)
    s = np.bincount(k, weights=val, minlength=nb * nc)
    m = np.divide(s, n, out=np.full(nb * nc, np.nan), where=n > 0)
    return m.reshape(nb, nc), n.reshape(nb, nc)


def decompose(m_of, b_of, c_of, val, cls, t0, t1):
    """Firebaugh-style split of class `cls`'s change from bin t0 to t1."""
    sel = c_of == cls
    a = {m: v for m, v in zip(m_of[sel][b_of[sel] == t0], val[sel][b_of[sel] == t0])}
    b = {m: v for m, v in zip(m_of[sel][b_of[sel] == t1], val[sel][b_of[sel] == t1])}
    S = a.keys() & b.keys()
    L = a.keys() - S
    E = b.keys() - S
    if not S or not a or not b:
        return None
    mS0 = np.mean([a[m] for m in S])
    mS1 = np.mean([b[m] for m in S])
    pS0 = len(S) / len(a)
    pL0 = len(L) / len(a)
    pE1 = len(E) / len(b)
    mL0 = np.mean([a[m] for m in L]) if L else mS0
    mE1 = np.mean([b[m] for m in E]) if E else mS1
    within = pS0 * (mS1 - mS0)
    entry = pE1 * (mE1 - mS1)
    exit_ = -pL0 * (mL0 - mS1)
    M0 = pS0 * mS0 + pL0 * mL0
    M1 = (1 - pE1) * mS1 + pE1 * mE1
    assert abs((within + entry + exit_) - (M1 - M0)) < 1e-9
    return dict(d=M1 - M0, within=within, entry=entry, exit=exit_,
                comp=entry + exit_, nS=len(S), nL=len(L), nE=len(E),
                pS0=pS0, pE1=pE1)


# ---------------------------------------------------------------------- main
def main():
    code = PE.coding_maps()
    rows = PE.provincial_rows(code) + PE.tier1_rows(code)[0]
    rows = [r for r in rows if era(r["year"])]
    coded = np.array([r["egp"] in EGP for r in rows])
    say(f"panel rows in bins: {len(rows):,} member-years, "
        f"{len({r['member'] for r in rows}):,} members, "
        f"{len({r['chamber'] for r in rows})} chambers")
    say(f"  EGP-coded (the cells): {int(coded.sum()):,} member-years, "
        f"{len({r['member'] for r, c in zip(rows, coded) if c}):,} members")
    say("  z is taken against ALL member-years of the chamber x bin, coded or")
    say("  not, exactly as build_class_by_era.py specifies.")

    bins = sorted({era(r["year"]) for r in rows})
    bix = {b: i for i, b in enumerate(bins)}
    cix = {c: i for i, c in enumerate(EGP)}
    mems = sorted({(r["chamber"], r["member"]) for r in rows})
    mix = {m: i for i, m in enumerate(mems)}
    chb = sorted({(r["chamber"], era(r["year"])) for r in rows})
    gix = {g: i for i, g in enumerate(chb)}

    mid = np.array([mix[(r["chamber"], r["member"])] for r in rows])
    bid = np.array([bix[era(r["year"])] for r in rows])
    cid = np.array([cix.get(r["egp"], -1) for r in rows])
    gid = np.array([gix[(r["chamber"], era(r["year"]))] for r in rows])
    words = np.array([float(r["words"]) for r in rows])
    rate = np.array([r["rate"] for r in rows])
    nb, nc, ng, nm = len(bins), len(EGP), len(chb), len(mems)
    rows_of_member = defaultdict(list)
    for i, m in enumerate(mid):
        rows_of_member[m].append(i)
    rows_of_member = [np.array(rows_of_member[i]) for i in range(nm)]

    def run(idx, member_level, remap=None):
        m_ = mid[idx] if remap is None else remap
        z, ok = zscore(gid[idx], rate[idx], ng)
        return cells(m_, bid[idx], cid[idx], words[idx], z,
                     ok & coded[idx], nb, nc, member_level)

    allidx = np.arange(len(rows))
    res = {}
    for lab, ml in (("member", True), ("member-year", False)):
        m_of, b_of, c_of, val = run(allidx, ml)
        M, N = class_means(b_of, c_of, val, nb, nc)
        res[lab] = (M, N, (m_of, b_of, c_of, val))

    # ------------------------------------------------- profiles + peak location
    for lab in ("member", "member-year"):
        M, N, _ = res[lab]
        say(f"\n{'=' * 74}\nCLASS PROFILE, {lab.upper()} aggregation "
            f"(mean z within chamber x bin)")
        say(f"  {'bin':<11}" + "".join(f"{c:>9}" for c in EGP) +
            f"{'peak':>10}{'peak>=25':>10}")
        for i, b in enumerate(bins):
            row = M[i]
            pk = EGP[int(np.nanargmax(np.where(N[i] > 0, row, -np.inf)))]
            big = np.where(N[i] >= 25, row, -np.inf)
            pk25 = EGP[int(np.argmax(big))] if np.isfinite(big).any() else "-"
            say(f"  {b:<11}" + "".join(
                f"{row[j]:>+9.3f}" if N[i][j] else f"{'-':>9}"
                for j in range(nc)) + f"{pk:>10}{pk25:>10}")
        say(f"  {'n':<11}" + "".join(f"{int(N[:, j].sum()):>9,}"
                                     for j in range(nc)))

    # -------------------------------------------------------- gap series + CIs
    rng = np.random.default_rng(SEED)
    draws = [rng.integers(0, nm, nm) for _ in range(NBOOT)]

    boot_gaps = {"member": [], "member-year": []}
    boot_dec = defaultdict(list)                   # (t, class) -> per-draw triple
    for d in draws:
        idx = np.concatenate([rows_of_member[i] for i in d])
        remap = np.concatenate([np.full(len(rows_of_member[i]), j)
                                for j, i in enumerate(d)])
        for lab, ml in (("member", True), ("member-year", False)):
            m_of, b_of, c_of, val = run(idx, ml, remap=remap)
            M, N = class_means(b_of, c_of, val, nb, nc)
            boot_gaps[lab].append(M[:, cix["II"]] - M[:, cix["I"]])
            if ml:
                for t in range(nb - 1):
                    for cl in ("I", "II"):
                        r = decompose(m_of, b_of, c_of, val, cix[cl], t, t + 1)
                        boot_dec[(t, cl)].append(
                            (r["d"], r["within"], r["comp"]) if r
                            else (np.nan, np.nan, np.nan))
    boot_dec = {k: np.array(v) for k, v in boot_dec.items()}

    def ci(a, q=(2.5, 97.5)):
        a = np.asarray(a, float)
        a = a[np.isfinite(a)]
        return (np.percentile(a, q[0]), np.percentile(a, q[1])) if len(a) \
            else (np.nan, np.nan)

    say(f"\n{'=' * 74}\nII MINUS I GAP PER BIN, both aggregations "
        f"(member-bootstrap 95% CI, {NBOOT} draws)")
    say(f"  {'bin':<11}{'member-level':>28}{'member-year':>28}")
    csv_rows = []
    for i, b in enumerate(bins):
        line = f"  {b:<11}"
        cells_ = {}
        for lab in ("member", "member-year"):
            M, N, _ = res[lab]
            g = M[i, cix["II"]] - M[i, cix["I"]]
            lo, hi = ci([x[i] for x in boot_gaps[lab]])
            cells_[lab] = (g, lo, hi, int(N[i, cix["I"]]), int(N[i, cix["II"]]))
            line += f"{g:>+11.3f} [{lo:+.3f},{hi:+.3f}]"
        say(line)
        csv_rows.append([b] + [f"{v:.4f}" if isinstance(v, float) else v
                               for lab in ("member", "member-year")
                               for v in cells_[lab]])

    for lab in ("member", "member-year"):
        M, N, _ = res[lab]
        g = M[:, cix["II"]] - M[:, cix["I"]]
        x = np.arange(nb, dtype=float)
        sl = np.polyfit(x, g, 1)[0]
        bs = [np.polyfit(x, np.asarray(v), 1)[0] for v in boot_gaps[lab]]
        lo, hi = ci(bs)
        say(f"  gap trend, {lab:<12} {sl:+.4f} per bin  "
            f"[{lo:+.4f},{hi:+.4f}]  (t {sl / np.std(bs):+.2f})")

    # ------------------------------------------------------ the decomposition
    say(f"\n{'=' * 74}\nFIREBAUGH-STYLE DECOMPOSITION, member-level, "
        f"consecutive bins")
    say("  within = stayers' own change; comp = entrants minus leavers, each")
    say("  against the stayers' new level. within + comp = total, exactly.")
    m_of, b_of, c_of, val = res["member"][2]
    for cl in ("I", "II"):
        say(f"\n  class {cl}")
        say(f"    {'transition':<22}{'total':>9}{'within':>9}{'comp':>9}"
            f"{'w share':>9}{'nS':>6}{'nL':>6}{'nE':>6}")
        for t in range(nb - 1):
            r = decompose(m_of, b_of, c_of, val, cix[cl], t, t + 1)
            if not r:
                continue
            bd = boot_dec[(t, cl)]
            wl, wh = ci(bd[:, 1])
            cl_, ch_ = ci(bd[:, 2])
            sh = r["within"] / r["d"] if abs(r["d"]) > 1e-9 else np.nan
            say(f"    {bins[t]}->{bins[t + 1][-4:]:<9}"
                f"{r['d']:>+9.3f}{r['within']:>+9.3f}{r['comp']:>+9.3f}"
                f"{sh:>9.2f}{r['nS']:>6}{r['nL']:>6}{r['nE']:>6}")
            say(f"    {'':22}{'':9}[{wl:+.3f},{wh:+.3f}] "
                f"[{cl_:+.3f},{ch_:+.3f}]")

    say(f"\n  II-minus-I GAP change, decomposed (class II components minus "
        f"class I's)")
    say(f"    {'transition':<22}{'d gap':>9}{'within':>9}{'comp':>9}"
        f"{'within share':>14}")
    for t in range(nb - 1):
        rI = decompose(m_of, b_of, c_of, val, cix["I"], t, t + 1)
        rII = decompose(m_of, b_of, c_of, val, cix["II"], t, t + 1)
        if not (rI and rII):
            continue
        d = rII["d"] - rI["d"]
        w = rII["within"] - rI["within"]
        c = rII["comp"] - rI["comp"]
        bI, bII = boot_dec[(t, "I")], boot_dec[(t, "II")]
        wl, wh = ci(bII[:, 1] - bI[:, 1])
        cl_, ch_ = ci(bII[:, 2] - bI[:, 2])
        say(f"    {bins[t]}->{bins[t + 1][-4:]:<9}{d:>+9.3f}{w:>+9.3f}"
            f"{c:>+9.3f}{w / d if abs(d) > 1e-9 else np.nan:>14.2f}")
        say(f"    {'':22}{'':9}[{wl:+.3f},{wh:+.3f}] [{cl_:+.3f},{ch_:+.3f}]")

    # net over the whole series: components summed across all five transitions
    say(f"\n  SUMMED over all {nb - 1} transitions "
        f"({bins[0]} -> {bins[-1]})")
    say(f"    {'series':<22}{'total':>9}{'within':>9}{'comp':>9}"
        f"{'within share':>14}")
    sums = {}
    for cl in ("I", "II"):
        parts = [decompose(m_of, b_of, c_of, val, cix[cl], t, t + 1)
                 for t in range(nb - 1)]
        tot = sum(p["within"] for p in parts)
        totc = sum(p["comp"] for p in parts)
        bw = sum(boot_dec[(t, cl)][:, 1] for t in range(nb - 1))
        bc = sum(boot_dec[(t, cl)][:, 2] for t in range(nb - 1))
        sums[cl] = (tot, totc, bw, bc)
        wl, wh = ci(bw)
        cl_, ch_ = ci(bc)
        say(f"    class {cl:<16}{tot + totc:>+9.3f}{tot:>+9.3f}{totc:>+9.3f}"
            f"{tot / (tot + totc) if abs(tot + totc) > 1e-9 else np.nan:>14.2f}")
        say(f"    {'':22}{'':9}[{wl:+.3f},{wh:+.3f}] [{cl_:+.3f},{ch_:+.3f}]")
    gw = sums["II"][0] - sums["I"][0]
    gc = sums["II"][1] - sums["I"][1]
    wl, wh = ci(sums["II"][2] - sums["I"][2])
    cl_, ch_ = ci(sums["II"][3] - sums["I"][3])
    say(f"    {'II minus I gap':<22}{gw + gc:>+9.3f}{gw:>+9.3f}{gc:>+9.3f}"
        f"{gw / (gw + gc) if abs(gw + gc) > 1e-9 else np.nan:>14.2f}")
    say(f"    {'':22}{'':9}[{wl:+.3f},{wh:+.3f}] [{cl_:+.3f},{ch_:+.3f}]")

    # ------------------------------------------------------------ cache check
    cache_path = os.path.join(HERE, "member_cache_panel.json.gz")
    if os.path.exists(cache_path):
        say(f"\n{'=' * 74}\nCROSS-CHECK from member_cache_panel.json.gz "
            f"(independent scan, CH|speaker keys)")
        cdat = json.load(gzip.open(cache_path, "rt"))
        crows = []
        for k, r in cdat.items():
            ch = k.split("|")[0]
            for y, v in r["years"].items():
                if v["tot"] < 8000 or not era(int(y)):
                    continue
                crows.append({"chamber": ch, "member": k, "year": int(y),
                              "words": v["tot"],
                              "rate": sum(v["w"].values()) / v["tot"] * 1000,
                              "egp": r["egp"]})
        say(f"  {len(crows):,} member-years, "
            f"{len({r['member'] for r in crows}):,} members; "
            f"{sum(1 for r in crows if r['egp'] in EGP):,} coded member-years")
        cm = sorted({r["member"] for r in crows})
        cmix = {m: i for i, m in enumerate(cm)}
        cgb = sorted({(r["chamber"], era(r["year"])) for r in crows})
        cgix = {g: i for i, g in enumerate(cgb)}
        z, ok = zscore(np.array([cgix[(r["chamber"], era(r["year"]))]
                                 for r in crows]),
                       np.array([r["rate"] for r in crows]), len(cgb))
        ccod = np.array([r["egp"] in EGP for r in crows])
        mo, bo, co, va = cells(
            np.array([cmix[r["member"]] for r in crows]),
            np.array([bix[era(r["year"])] for r in crows]),
            np.array([cix.get(r["egp"], -1) for r in crows]),
            np.array([float(r["words"]) for r in crows]), z, ok & ccod,
            nb, nc, True)
        Mc, Nc = class_means(bo, co, va, nb, nc)
        say(f"  {'bin':<11}{'gap (cache)':>13}{'gap (panel)':>13}"
            f"{'nI':>7}{'nII':>7}")
        for i, b in enumerate(bins):
            gc = Mc[i, cix["II"]] - Mc[i, cix["I"]]
            gp = res["member"][0][i, cix["II"]] - res["member"][0][i, cix["I"]]
            say(f"  {b:<11}{gc:>+13.3f}{gp:>+13.3f}"
                f"{int(Nc[i, cix['I']]):>7}{int(Nc[i, cix['II']]):>7}")
    else:
        say("\n(no member_cache_panel.json.gz yet -- cross-check skipped)")

    with open(os.path.join(HERE, "peak_gap_series.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bin", "gap_member", "lo_member", "hi_member", "nI_member",
                    "nII_member", "gap_memberyear", "lo_memberyear",
                    "hi_memberyear", "nI_memberyear", "nII_memberyear"])
        w.writerows(csv_rows)
    open(os.path.join(HERE, "peak_decomposition.txt"), "w").write(
        "\n".join(OUT) + "\n")
    print("\nwrote peak_decomposition.txt, peak_gap_series.csv")


if __name__ == "__main__":
    main()
