#!/usr/bin/env python3
"""One scan of every segment store: per-word, per-chamber, per-year counts.

WHY

The register instrument is a FIXED list of 407 Kobak style words, and §4.5 runs
it backwards to 1985 as a level series. The list was selected on the post-2022
jump in scholarly text, so a backward projection of its AGGREGATE is exposed to
selection-on-trend: any word chosen because it rose lately will, on average,
have been below its own mean earlier, and 407 such words summed will trace a
rising line whether or not anything happened. Nothing committed in this study
is per-word, so the objection cannot currently be answered -- occurrence_trends
.json holds chamber-year aggregates only.

This produces the two things needed to answer it, in one pass over ~12.7 GB:

  (a) word_year_counts.json.gz   per chamber-year: total tokens, total
      segments, an exact count for EVERY one of the 407 style words, an exact
      count for every Wikipedia "signs of AI writing" pattern in the committed
      up-family, and a segment-length histogram carrying tokens and hits per
      length bin (the composition guard in length_poststrat.py needs it).

  (b) vocab_year_counts.json.gz  per chamber-year: counts for the FULL
      vocabulary, restricted to words with >= 200 occurrences corpus-wide, so
      donor_series.py can match each style word to a non-style word with the
      same frequency, dispersion and pre-period slope.

STORE SELECTION -- reused, not reinvented

Imported verbatim from occurrence_trends.py's `_sources()`, which is the
committed series' own store list: 22 chambers, and for each one the base
download plus its `_2025` and `_fill*` continuations, which are one series and
must map to one chamber key. That selection deliberately excludes the earlier
or overlapping variants that would double-count a chamber:

  uk/segments_uk.jsonl, uk/segments_uk_long.jsonl   subsets of _deep
  uk/segments_uk_within.jsonl                       within-speaker redraw
  us/segments_us*_pre_backfill.jsonl                pre-2026-08-13 versions of
                                                    the US files now used
  us/segments_us.jsonl, us/segments_us_new.jsonl    pre-split US pool
  ca/segments_ca.jsonl, ca/segments_ca_en.jsonl     superseded by segments_ca2
  ie/segments_ie.jsonl                              superseded by _ie_en
  *_within.jsonl, provinces/superseded/*            redraws and bug-fixed
                                                    predecessors
  segments*.jsonl in the S10 root                   New Brunswick, the
                                                    discovery corpus, which
                                                    occurrence_trends.py does
                                                    not pool either

The 2026 additions are already inside that list: the `_fill*` province files
and uk/segments_uk_2023.jsonl (2026-08-13), and the rebuilt US House/Senate
files that carry the record back to 1994 (2026-08-13; their `_pre_backfill`
predecessors are excluded above).

MEASUREMENT, kept identical to the committed series

  - only `scoreable` segments count, as in occurrence_trends.py
  - tokens are TOKEN_RE = [a-z']+ over lowercased text
  - the Wikipedia set is the up-family of tier15_wiki_signs.PATTERNS joined
    into one case-insensitive alternation over RAW text, exactly as
    build_trend_cache.py does it. Case-folding first and matching
    case-sensitively is NOT equivalent (`additionally-start` anchors on a
    sentence-initial capital) and was measured to differ, so the slow form is
    kept. Named groups attribute each hit to its pattern; attribution is paid
    per match, not per byte, so it is free at this scale.

ONE APPROXIMATION, stated

Artifact (b) drops any word occurring fewer than 2 times within a chamber
before the corpus-wide >= 200 filter is applied. A word dropped that way
contributes at most 22 occurrences (one per chamber) to its corpus total, so
the >= 200 membership decision is unaffected in every realistic case, but the
per-chamber-year counts of a kept word are missing its within-chamber
singletons. That matters only for dispersion of very rare words and is noted
where donor_series.py uses it. Artifact (a)'s style and wiki counts are exact:
they are extracted before any pruning.

Usage:
  python build_word_year_counts.py            # full scan, 20 processes
  python build_word_year_counts.py --procs 8 --shard-mb 400
"""
import argparse
import csv
import gzip
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from occurrence_trends import SOURCES                      # noqa: E402
from tier15_quarters_speakers import UP                    # noqa: E402
from tier15_wiki_signs import PATTERNS                     # noqa: E402

TOKEN_RE = re.compile(r"[a-z']+")
WIKI_NAMES = sorted(UP)
# named-group alternation; the up-family patterns contain no capturing groups
# (checked), so m.lastgroup names the alternative that matched.
WIKI_RE = re.compile(
    "|".join("(?P<g%d>%s)" % (i, PATTERNS[n]) for i, n in enumerate(WIKI_NAMES)),
    re.I)
GNAME = {"g%d" % i: n for i, n in enumerate(WIKI_NAMES)}

MIN_CHAMBER_COUNT = 2        # within-chamber prune before the global filter
MIN_GLOBAL_COUNT = 200       # corpus-wide floor for artifact (b)
OUT_A = os.path.join(HERE, "word_year_counts.json.gz")
OUT_B = os.path.join(HERE, "vocab_year_counts.json.gz")


def load_style():
    """The 407 type=='style' words, same loader as long_trend.py."""
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(HERE,
                                                    "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


STYLE = load_style()
STYLESET = set(STYLE)


def lbin(n):
    """Segment-length bin index, 32 bins per octave (~2.2% wide).

    Fine enough that decile cut points of the pooled length distribution land
    inside a bin of negligible width, coarse enough that the histogram is a few
    hundred keys per chamber-year instead of tens of thousands.
    """
    return int(32 * math.log2(n)) if n > 0 else -1


def shards(path, shard_bytes):
    """Byte ranges of `path`, split on newline boundaries by the reader."""
    size = os.path.getsize(path)
    n = max(1, math.ceil(size / shard_bytes))
    step = math.ceil(size / n)
    return [(i * step, min(size, (i + 1) * step)) for i in range(n)]


def _scan(job):
    """Count one byte range of one file. Returns plain dicts, keyed by year."""
    ch, path, start, end = job
    words = Counter()                       # year -> tokens
    segs = Counter()                        # year -> scoreable segments
    vocab = defaultdict(Counter)            # year -> word -> n
    wiki = defaultdict(Counter)             # year -> pattern -> n
    lens = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
    with open(os.path.join(HERE, path), "rb") as fh:
        fh.seek(start)
        pos = start
        if start:
            pos += len(fh.readline())       # the shard before us owns it
        while pos < end:
            line = fh.readline()
            if not line:
                break
            pos += len(line)
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            y = (d.get("date") or "")[:4]
            if not y.isdigit():
                continue
            txt = d["text"]
            t = TOKEN_RE.findall(txt.lower())
            n = len(t)
            words[y] += n
            segs[y] += 1
            vocab[y].update(t)
            c = Counter(t)
            sh = sum(c[w] for w in STYLESET & c.keys())
            wh = 0
            wy = wiki[y]
            for m in WIKI_RE.finditer(txt):
                wy[GNAME[m.lastgroup]] += 1
                wh += 1
            b = lens[y][lbin(n)]
            b[0] += 1
            b[1] += n
            b[2] += sh
            b[3] += wh
    return (ch,
            dict(words), dict(segs),
            {y: dict(c) for y, c in vocab.items()},
            {y: dict(c) for y, c in wiki.items()},
            {y: {b: v for b, v in d.items()} for y, d in lens.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=20)
    ap.add_argument("--shard-mb", type=int, default=250)
    a = ap.parse_args()

    jobs = []
    for ch, files in sorted(SOURCES.items()):
        for f in files:
            for s, e in shards(os.path.join(HERE, f), a.shard_mb * 1_000_000):
                jobs.append((ch, f, s, e))
    total_gb = sum(os.path.getsize(os.path.join(HERE, f))
                   for v in SOURCES.values() for f in v) / 1e9
    # biggest shards first: the scan is regex-bound and this is what keeps the
    # 3.1 GB UK file from being the whole wall clock
    jobs.sort(key=lambda j: j[2] - j[3])
    print(f"{len(SOURCES)} chambers, {sum(len(v) for v in SOURCES.values())} "
          f"files, {total_gb:.2f} GB, {len(jobs)} shards, {a.procs} procs")
    print(f"instrument {len(STYLE)} style words; wiki set {len(WIKI_NAMES)} "
          f"up-family patterns", flush=True)

    words = defaultdict(Counter)
    segs = defaultdict(Counter)
    vocab = defaultdict(lambda: defaultdict(Counter))
    wiki = defaultdict(lambda: defaultdict(Counter))
    lens = defaultdict(lambda: defaultdict(lambda: defaultdict(
        lambda: [0, 0, 0, 0])))
    t0 = time.time()
    done = 0
    with Pool(a.procs) as pool:
        for ch, w, s, v, k, L in pool.imap_unordered(_scan, jobs):
            for y, n in w.items():
                words[ch][y] += n
            for y, n in s.items():
                segs[ch][y] += n
            for y, c in v.items():
                vocab[ch][y].update(c)
            for y, c in k.items():
                wiki[ch][y].update(c)
            for y, d in L.items():
                tgt = lens[ch][y]
                for b, val in d.items():
                    q = tgt[b]
                    for i in range(4):
                        q[i] += val[i]
            done += 1
            if done % 10 == 0 or done == len(jobs):
                print(f"  {done:>3d}/{len(jobs)} shards  "
                      f"{time.time()-t0:>6.0f}s", flush=True)

    # ------------------------------------------------------------ artifact (a)
    out_a = {}
    for ch in sorted(words):
        rows = {}
        for y in sorted(words[ch]):
            v = vocab[ch][y]
            rows[y] = {
                "words": words[ch][y],
                "segs": segs[ch][y],
                "style": {w: v[w] for w in STYLE if v.get(w)},
                "wiki": {p: n for p, n in sorted(wiki[ch][y].items())},
                "wiki_total": sum(wiki[ch][y].values()),
                "lenbins": {str(b): lens[ch][y][b]
                            for b in sorted(lens[ch][y])},
            }
        out_a[ch] = rows
    meta = {"sources": {k: v for k, v in sorted(SOURCES.items())},
            "style_words": STYLE, "wiki_patterns": WIKI_NAMES,
            "token_re": TOKEN_RE.pattern, "lenbin": "int(32*log2(n_tokens))",
            "min_chamber_count": MIN_CHAMBER_COUNT,
            "min_global_count": MIN_GLOBAL_COUNT,
            "built": time.strftime("%Y-%m-%d")}
    with gzip.open(OUT_A, "wt") as fh:
        json.dump({"_meta": meta, "chambers": out_a}, fh)
    print(f"\nwrote {os.path.basename(OUT_A)} "
          f"({os.path.getsize(OUT_A)/1e6:.1f} MB)")

    # ------------------------------------------------------------ artifact (b)
    kept_ch = {}                              # ch -> {year: {word: n}}
    gtot = Counter()
    for ch in sorted(vocab):
        ctot = Counter()
        for y, c in vocab[ch].items():
            ctot.update(c)
        keep = {w for w, n in ctot.items() if n >= MIN_CHAMBER_COUNT}
        kept_ch[ch] = {y: {w: n for w, n in c.items() if w in keep}
                       for y, c in sorted(vocab[ch].items())}
        for w in keep:
            gtot[w] += ctot[w]
    glob = {w for w, n in gtot.items() if n >= MIN_GLOBAL_COUNT}
    out_b = {ch: {y: {w: n for w, n in c.items() if w in glob}
                  for y, c in rows.items()}
             for ch, rows in kept_ch.items()}
    with gzip.open(OUT_B, "wt") as fh:
        json.dump({"_meta": meta,
                   "totals": {w: gtot[w] for w in sorted(glob)},
                   "chambers": out_b}, fh)
    print(f"wrote {os.path.basename(OUT_B)} "
          f"({os.path.getsize(OUT_B)/1e6:.1f} MB)")

    # ------------------------------------------------------------- what we got
    tw = sum(sum(c.values()) for c in words.values())
    ts = sum(sum(c.values()) for c in segs.values())
    print(f"\nscanned {tw/1e9:.3f}B tokens in {ts/1e6:.2f}M scoreable segments"
          f"  ({time.time()-t0:.0f}s)")
    print(f"vocabulary: {len(gtot):,} words at >= {MIN_CHAMBER_COUNT} in some "
          f"chamber; {len(glob):,} at >= {MIN_GLOBAL_COUNT} corpus-wide")
    missing = [w for w in STYLE if gtot.get(w, 0) == 0]
    print(f"style words never seen in the corpus: {len(missing)}"
          + (f"  {missing}" if missing else ""))
    print(f"\n  {'chamber':<12s} {'years':>5s} {'span':>11s} {'Mtokens':>9s} "
          f"{'Mseg':>7s} {'style/100k':>10s} {'wiki/100k':>9s}")
    for ch in sorted(out_a):
        ys = [y for y in out_a[ch] if out_a[ch][y]["words"] >= 200_000]
        if not ys:
            continue
        W = sum(out_a[ch][y]["words"] for y in ys)
        S = sum(sum(out_a[ch][y]["style"].values()) for y in ys)
        K = sum(out_a[ch][y]["wiki_total"] for y in ys)
        G = sum(out_a[ch][y]["segs"] for y in ys)
        print(f"  {ch:<12s} {len(ys):>5d} {min(ys)+'-'+max(ys):>11s} "
              f"{W/1e6:>9.1f} {G/1e6:>7.2f} {S/W*1e5:>10.1f} {K/W*1e5:>9.2f}")


if __name__ == "__main__":
    main()
