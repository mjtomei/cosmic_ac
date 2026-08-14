#!/usr/bin/env python3
"""Instrument-word occurrence rate per chamber per year, over the whole record.

WHAT THIS IS

`long_trend.py` asked when the Kobak-vocabulary rise began, on UK Commons
alone. This runs the same measurement on every chamber the study has, so the
question becomes whether the shape replicates across independent legislatures
rather than being one parliament's register drift.

THE MEASUREMENT

For each chamber and calendar year: occurrences per 100k words of the Kobak
"style" words, against the median of 200 frequency-and-dispersion-matched
placebo sets. The GAP between them is the quantity of interest -- if the
instrument and its matched placebo rise together, ordinary vocabulary change
explains it and nothing specific is happening.

ONE INSTRUMENT AND ONE PLACEBO SET FOR EVERY CHAMBER

Both are built once, on UK Commons 2010-2012, and then applied unchanged
everywhere. That is deliberate: chambers are only comparable to each other if
the words being counted are the same words. The cost is that placebo matching
is calibrated to UK baseline frequency and dispersion, so a word that is rare
in Westminster and common in Canberra is matched slightly wrong for Canberra.
Matching per chamber would fix that and destroy the comparability, which is the
whole point of the exercise. It follows long_trend.py, whose baseline era and
N_PLACEBO are reused unchanged.

WHAT THE RECORD ACTUALLY COVERS -- read this before reading any chart

  UK Commons     1985-2026   the ONLY chamber reaching before 2006
  US House/Sen   2006-2026
  CA federal     2015-2026
  Ireland        2018-2026
  15 states and provinces
                 2006-2019 and 2025-2026, WITH A FIVE-YEAR HOLE 2020-2024

  2023 is missing from every source, UK and US included.

Those gaps are properties of what was downloaded, not of the legislatures. A
line that crosses a gap is interpolating over missing years, so the plotting
code must break the series rather than join it. `--min-words` drops any
chamber-year too thin to estimate a rate on, which is what keeps a partial
first or last year from reading as a collapse.

Usage:
  python occurrence_trends.py --build      # writes occurrence_trends.json
  python occurrence_trends.py --report     # prints the table
"""
import argparse
import csv
import glob
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_RE = re.compile(r"[a-z']+")
N_PLACEBO = 200
BASE_YEARS = ("2010", "2011", "2012")
BASE_SEG = "uk/segments_uk_deep.jsonl"
OUT = os.path.join(HERE, "occurrence_trends.json")
MIN_WORDS = 200_000

# chamber -> the files that make up its record. Several chambers are split
# across a historical file and a 2025- file; they are one series.
def _sources():
    src = defaultdict(list)
    src["UK"].append("uk/segments_uk_deep.jsonl")
    # 2023 was skipped by the download design as the ChatGPT washout year --
    # sound for a pre/post contrast, wrong for a trend, since it leaves a hole
    # at the year a reader looks at first. Fetched 2026-08-13; zero date
    # overlap with the deep file.
    src["UK"].append("uk/segments_uk_2023.jsonl")
    src["US-House"].append("us/segments_us_house.jsonl")
    src["US-Senate"].append("us/segments_us_senate.jsonl")
    src["CA-FED"].append("ca/segments_ca2.jsonl")
    src["IE"].append("ie/segments_ie_en.jsonl")
    for p in sorted(glob.glob(os.path.join(HERE, "provinces",
                                           "segments_*.jsonl"))):
        stem = os.path.basename(p)[len("segments_"):-len(".jsonl")]
        # A chamber's record is split across several files: the original
        # two-window download, the 2025- download, and "_fill" files holding
        # the years the windowed design skipped (2011-14, 2020-24), numbered
        # when one fill needed a second pass -- NI's _fill2 is the 2011-12 to
        # 2012-09 window that sits between its two platforms. They are one
        # series and must map to one chamber key, or a backfilled chamber
        # silently becomes two half-covered ones (or, with a numbered fill, a
        # phantom chamber called NI2).
        key = re.sub(r"_(?:2025|fill\d*)$", "", stem).upper()
        src[key].append(os.path.join("provinces", os.path.basename(p)))
    return {k: v for k, v in src.items()
            if all(os.path.exists(os.path.join(HERE, f)) for f in v)}


SOURCES = _sources()


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(HERE,
                                                    "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def build_instrument():
    """Instrument + 200 matched placebo sets, from UK 2010-2012. Same
    construction as long_trend.py, kept identical on purpose."""
    style = load_style()
    sset = set(style)
    base, disp, last = Counter(), Counter(), {}
    base_w = 0
    pre = tuple(f'"date": "{y}'.encode() for y in BASE_YEARS)
    pre2 = tuple(f'"date":"{y}'.encode() for y in BASE_YEARS)
    with open(os.path.join(HERE, BASE_SEG), "rb") as fh:
        for line in fh:
            if not (any(p in line for p in pre) or any(p in line for p in pre2)):
                continue
            d = json.loads(line)
            if not d.get("scoreable") or d["date"][:4] not in BASE_YEARS:
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            base.update(t)
            base_w += len(t)
            for w in set(t):
                if last.get(w) != d["date"]:
                    disp[w] += 1
                    last[w] = d["date"]
    if base_w == 0:
        raise SystemExit(f"no {'/'.join(BASE_YEARS)} data in {BASE_SEG}")

    rng = random.Random(int(hashlib.sha1(b"occurrence_trends").hexdigest()[:8],
                            16))
    excluded = sset | {w for w, _ in base.most_common(120)}
    pool = defaultdict(list)
    for w, n in base.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        pool[(int(math.log2(n + 1)),
              int(math.log2(disp.get(w, 0) + 1)))].append(w)

    def pool_for(c):
        if pool.get(c):
            return pool[c]
        for r in range(1, 8):
            best = None
            for df in range(-r, r + 1):
                for dd in range(-r, r + 1):
                    if max(abs(df), abs(dd)) != r:
                        continue
                    cd = pool.get((c[0] + df, c[1] + dd))
                    if cd and (best is None or len(cd) > len(best)):
                        best = cd
            if best:
                return best
        return max(pool.values(), key=len)

    present = [w for w in style if base[w] > 0]
    pools = [pool_for((int(math.log2(base[w] + 1)),
                       int(math.log2(disp.get(w, 0) + 1)))) for w in present]
    placebo = [[rng.choice(p) for p in pools] for _ in range(N_PLACEBO)]
    return present, placebo, base_w


def _count(job):
    """Per-year counts of the words we need, for one chamber."""
    ch, files, need = job
    per_year = defaultdict(Counter)
    words = Counter()
    for f in files:
        with open(os.path.join(HERE, f), "rb") as fh:
            for line in fh:
                d = json.loads(line)
                if not d.get("scoreable"):
                    continue
                y = (d.get("date") or "")[:4]
                if not y.isdigit():
                    continue
                t = TOKEN_RE.findall(d["text"].lower())
                words[y] += len(t)
                c = per_year[y]
                for w in t:
                    if w in need:
                        c[w] += 1
    return ch, {y: dict(c) for y, c in per_year.items()}, dict(words)


def add_panels(out):
    """Composition-stable pooled series. Safe to re-run on a built file."""
    # ---------------------------------------------------------------- pooling
    #
    # A pooled line whose COMPOSITION changes from year to year is not a trend.
    # The naive all-chamber total rises from 2473 to 3112 between 2005 and
    # 2006 purely because nineteen chambers join the average that year, and
    # falls again in 2011 when the provinces' download window ends. Every one
    # of those steps is an artifact of what was downloaded.
    #
    # So each pooled series is computed over a FIXED SET of chambers, named,
    # and only across years where every member of that set is present. The
    # all-chamber line is still emitted because it is what someone would
    # naively compute, but it carries n_chambers so a chart can show that the
    # composition moves, and it must not be read as a trend.
    def pool(names, label):
        names = [n for n in names if n in out]
        if not names:
            return []
        years = set.intersection(*[{r["year"] for r in out[n]} for n in names])
        rows = []
        for y in sorted(years):
            w = iw = pw = 0.0
            for n in names:
                r = next(r for r in out[n] if r["year"] == y)
                w += r["words"]
                iw += r["instrument_per100k"] * r["words"]
                pw += r["placebo_per100k"] * r["words"]
            rows.append({"year": y, "words": int(w),
                         "instrument_per100k": iw / w,
                         "placebo_per100k": pw / w, "gap": (iw - pw) / w,
                         "n_chambers": len(names)})
        print(f"  panel {label:<12s} {len(names):>2d} chambers, "
              f"{len(rows):>2d} balanced years", flush=True)
        return rows
    
    # Word-weighted regional aggregates, so twenty-two lines become eight.
    # Each is a BALANCED panel -- only years where every member is present --
    # because a group average whose membership changes between years is a
    # picture of coverage, not a trend. Members excluded for having gaps are
    # named in the output rather than quietly dropped; they are still available
    # individually.
    out["_GRP_CA_PROV"] = pool(
        ["AB", "BC", "MB", "NL", "NS", "ON", "SK"], "CA provinces")
    out["_GRP_AUS_STATE"] = pool(
        ["AUS_NSW", "AUS_QLD", "AUS_TAS", "AUS_VIC", "AUS_WA"], "AUS states")
    out["_GRP_UK_DEVOLVED"] = pool(["SCOT", "WALES"], "UK devolved")

    provs = [c for c in out if not c.startswith("_") and c not in
             ("UK", "US-House", "US-Senate", "CA-FED", "IE")]
    out["_PANEL_UK"] = pool(["UK"], "UK")
    out["_PANEL_ANGLO3"] = pool(["UK", "US-House", "US-Senate"], "ANGLO3")
    out["_PANEL_PROV"] = pool(provs, "PROV")
    
    tot = defaultdict(lambda: [0, 0.0, 0.0, 0])
    for ch, rows in out.items():
        if ch.startswith("_"):
            continue
        for r in rows:
            t = tot[r["year"]]
            t[0] += r["words"]
            t[1] += r["instrument_per100k"] * r["words"]
            t[2] += r["placebo_per100k"] * r["words"]
            t[3] += 1
    out["_TOTAL_UNBALANCED"] = [
        {"year": y, "words": t[0], "instrument_per100k": t[1] / t[0],
         "placebo_per100k": t[2] / t[0], "gap": (t[1] - t[2]) / t[0],
         "n_chambers": t[3]} for y, t in sorted(tot.items())]


def build(procs):
    present, placebo, base_w = build_instrument()
    need = set(present)
    for p in placebo:
        need.update(p)
    print(f"instrument {len(present)} words, {N_PLACEBO} placebo sets, "
          f"{len(need):,} distinct words to count")
    print(f"baseline {'/'.join(BASE_YEARS)} on {BASE_SEG}: {base_w:,} words\n")

    jobs = [(ch, files, need) for ch, files in sorted(SOURCES.items())]
    out = {}
    with Pool(procs) as pool:
        for ch, per_year, words in pool.imap_unordered(_count, jobs):
            rows = []
            for y in sorted(per_year):
                if words[y] < MIN_WORDS:
                    continue
                ri = sum(per_year[y].get(w, 0) for w in present) / words[y] * 1e5
                rp = sorted(sum(per_year[y].get(w, 0) for w in ps)
                            / words[y] * 1e5 for ps in placebo)
                med = rp[len(rp) // 2]
                rows.append({"year": int(y), "words": words[y],
                             "instrument_per100k": ri, "placebo_per100k": med,
                             "gap": ri - med})
            out[ch] = rows
            print(f"  {ch:<12s} {len(rows):>3d} years  "
                  f"{min((r['year'] for r in rows), default=0)}-"
                  f"{max((r['year'] for r in rows), default=0)}  "
                  f"{sum(r['words'] for r in rows)/1e6:>8.1f}M words",
                  flush=True)

    add_panels(out)
    out["_META"] = {"instrument_words": present, "n_placebo": N_PLACEBO,
                    "base_years": list(BASE_YEARS), "base_seg": BASE_SEG,
                    "min_words": MIN_WORDS}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"\nwrote {os.path.basename(OUT)}")


def report():
    d = json.load(open(OUT))
    chs = [k for k in d if not k.startswith("_")]
    print("COVERAGE\n")
    for ch in sorted(chs):
        ys = [r["year"] for r in d[ch]]
        if not ys:
            continue
        gaps = [y for y in range(min(ys), max(ys) + 1) if y not in set(ys)]
        g = f"  MISSING {','.join(str(x) for x in gaps)}" if gaps else ""
        print(f"  {ch:<12s} {min(ys)}-{max(ys)}  {len(ys):>2d} yrs{g}")
    print("\n\nPOOLED PANELS (word-weighted, fixed composition)\n")
    print(f"  {'year':<6s} {'chambers':>9s} {'Mwords':>8s} {'instrument':>11s} "
          f"{'placebo':>9s} {'GAP':>8s}")
    for r in d.get("_PANEL_ANGLO3", []):
        print(f"  {r['year']:<6d} {r['n_chambers']:>9d} "
              f"{r['words']/1e6:>8.1f} {r['instrument_per100k']:>11.1f} "
              f"{r['placebo_per100k']:>9.1f} {r['gap']:>8.1f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--procs", type=int, default=10)
    ap.add_argument("--repool", action="store_true",
                    help="recompute the pooled panels from the built file, "
                         "without rescanning a billion words")
    a = ap.parse_args()
    if a.build:
        build(a.procs)
    if a.repool:
        d = json.load(open(OUT))
        for k in [k for k in d if k.startswith(("_PANEL", "_TOTAL"))]:
            del d[k]
        add_panels(d)
        json.dump(d, open(OUT, "w"), indent=1)
        print(f"repooled {os.path.basename(OUT)}")
    if a.report:
        report()
    if not (a.build or a.report):
        print("pass --build or --report")


if __name__ == "__main__":
    main()
