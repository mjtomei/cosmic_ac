#!/usr/bin/env python3
"""Word-count distributions: generated text against the real legislative record.

THE QUESTION

§4.7 compares vocabulary between base and instruct generations, and between
generations and Hansard. Any such comparison assumes the two corpora are
composed of comparable pieces of text. They are not obviously so, and this
measures how far apart they are.

TWO CAPS TO KEEP IN MIND, BECAUSE BOTH ARE ARTIFACTS OF OUR OWN CODE

  * Generated text is capped at NEW_TOKENS = 400 new tokens, so its
    distribution is TRUNCATED FROM ABOVE by construction. A pile-up at the top
    of the generated range is the sampler hitting the cap, not a property of
    the model. Base models also run on past a natural ending, so the cap binds
    for them far more often than for instruct models, which emit a stop token.

  * Hansard segments are packer output, not utterances. `segment.py` packs
    speaker turns into windows of at most 360 words and marks anything under 50
    unscoreable, so the segment distribution has a hard ceiling at 360 (except
    where a single paragraph exceeds it) and a shoulder at 50. TURN-level
    counts are reported alongside because a turn is a real unit of speech and a
    segment is not.

So three distributions are printed for the legislative side -- all segments,
scoreable segments, and whole turns -- and the honest comparison against
generated text is the one that says which cap is doing the work.

Usage:
  python length_distributions.py --build     # writes length_distributions.json
  python length_distributions.py --report
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "length_distributions.json")
GEN = os.path.join(HERE, "rlhf_gen")
NW_RE = re.compile(rb'"n_words":\s*(\d+)')
TURN_RE = re.compile(rb'"turn_id":\s*"?([^",}]+)"?')
SCOREABLE_RE = re.compile(rb'"scoreable":\s*(true|false)')

# The scored era only. The historical files are a different sampling frame and
# mixing them in would make the "real record" distribution partly a statement
# about which years happened to be downloaded.
CHAMBERS = {
    "UK": ["uk/segments_uk.jsonl"],
    "IE": ["ie/segments_ie_en.jsonl"],
    "CA-FED": ["ca/segments_ca2.jsonl"],
    "US-House": ["us/segments_us_house.jsonl"],
    "US-Senate": ["us/segments_us_senate.jsonl"],
}


def _chambers():
    out = dict(CHAMBERS)
    for p in sorted(glob.glob(os.path.join(HERE, "provinces",
                                           "segments_*_2025.jsonl"))):
        stem = os.path.basename(p)[len("segments_"):-len("_2025.jsonl")]
        out[stem.upper()] = [os.path.join("provinces", os.path.basename(p))]
    return {k: v for k, v in out.items()
            if all(os.path.exists(os.path.join(HERE, f)) for f in v)}


def summarize(vals):
    """Percentile summary. Kept as a list of counts rather than raw values so
    the JSON stays small on corpora of a million segments."""
    if not vals:
        return None
    v = sorted(vals)
    n = len(v)

    def q(p):
        return v[min(n - 1, int(p * n))]
    return {"n": n, "mean": sum(v) / n, "min": v[0], "max": v[-1],
            "p05": q(.05), "p25": q(.25), "median": q(.50), "p75": q(.75),
            "p95": q(.95), "total_words": sum(v)}


def hist(vals, edges):
    c = [0] * (len(edges) + 1)
    for x in vals:
        i = 0
        while i < len(edges) and x >= edges[i]:
            i += 1
        c[i] += 1
    return c


SEG_EDGES = [25, 50, 75, 100, 120, 150, 200, 250, 300, 360, 500, 750, 1000]


def _scan(job):
    ch, files = job
    seg_all, seg_score = [], []
    turns = defaultdict(int)
    for f in files:
        with open(os.path.join(HERE, f), "rb") as fh:
            for line in fh:
                m = NW_RE.search(line)
                if not m:
                    continue
                n = int(m.group(1))
                if n < 1:
                    continue
                seg_all.append(n)
                s = SCOREABLE_RE.search(line)
                if s and s.group(1) == b"true":
                    seg_score.append(n)
                t = TURN_RE.search(line)
                if t:
                    turns[(f, t.group(1))] += n
    return ch, {
        "segments_all": {"stats": summarize(seg_all),
                         "hist": hist(seg_all, SEG_EDGES)},
        "segments_scoreable": {"stats": summarize(seg_score),
                               "hist": hist(seg_score, SEG_EDGES)},
        "turns": {"stats": summarize(list(turns.values())),
                  "hist": hist(list(turns.values()), SEG_EDGES)},
    }


def build(procs):
    sys.path.insert(0, HERE)
    import rlhf_pref_scale as S

    print("GENERATED TEXT (per family, base and instruct separately)\n")
    models = {}
    for fam, _, _ in S.PAIRS:
        for role in ("base", "instruct"):
            p = os.path.join(GEN, f"{fam}_{role}.json")
            if not os.path.exists(p):
                continue
            v = [len(x.split()) for x in json.load(open(p))]
            models[f"{fam}/{role}"] = {"stats": summarize(v),
                                       "hist": hist(v, SEG_EDGES)}
            s = models[f"{fam}/{role}"]["stats"]
            print(f"  {fam+'/'+role:<24s} n={s['n']:>5d}  median {s['median']:>4d}"
                  f"  mean {s['mean']:>6.1f}  p95 {s['p95']:>4d}  max {s['max']:>5d}")

    for role in ("base", "instruct"):
        v = []
        for fam, _, _ in S.PAIRS:
            p = os.path.join(GEN, f"{fam}_{role}.json")
            if os.path.exists(p):
                v += [len(x.split()) for x in json.load(open(p))]
        if v:
            models[f"ALL/{role}"] = {"stats": summarize(v),
                                     "hist": hist(v, SEG_EDGES)}

    chs = _chambers()
    print(f"\nLEGISLATIVE RECORD ({len(chs)} chambers, scored era)\n")
    cham = {}
    with Pool(procs) as pool:
        for ch, d in pool.imap_unordered(_scan, sorted(chs.items())):
            cham[ch] = d
            s = d["segments_scoreable"]["stats"]
            t = d["turns"]["stats"]
            print(f"  {ch:<12s} scoreable n={s['n']:>7,} median {s['median']:>4d}"
                  f"  mean {s['mean']:>6.1f}   turns median {t['median']:>4d}"
                  f"  mean {t['mean']:>7.1f}", flush=True)

    # pooled legislative distribution, by summing histograms rather than
    # re-reading: exact for the histogram, and the stats are recomputed from
    # the per-chamber totals so nothing is double counted
    # Snapshot the chamber names first: the pooled entry is written INTO cham,
    # so iterating cham itself picks up a half-built "_ALL" on the second key.
    names = sorted(cham)
    for key in ("segments_all", "segments_scoreable", "turns"):
        h = [0] * (len(SEG_EDGES) + 1)
        n = tw = 0
        for ch in names:
            d = cham[ch][key]
            if not d["stats"]:
                continue
            h = [a + b for a, b in zip(h, d["hist"])]
            n += d["stats"]["n"]
            tw += d["stats"]["total_words"]
        cham.setdefault("_ALL", {})[key] = {
            "hist": h, "stats": {"n": n, "total_words": tw,
                                 "mean": tw / n if n else 0}}

    json.dump({"edges": SEG_EDGES, "models": models, "chambers": cham,
               "new_tokens": S.NEW_TOKENS},
              open(OUT, "w"), indent=1)
    print(f"\nwrote {os.path.basename(OUT)}")


def labels(edges):
    out = [f"<{edges[0]}"]
    for a, b in zip(edges, edges[1:]):
        out.append(f"{a}-{b-1}")
    out.append(f"{edges[-1]}+")
    return out


def report():
    d = json.load(open(OUT))
    lab = labels(d["edges"])
    print(f"generated text is capped at {d['new_tokens']} new tokens; "
          f"segments are capped at 360 words by the packer\n")
    print("DISTRIBUTION, % of items in each word-count bin\n")
    print(f"  {'':<24s} " + " ".join(f"{x:>8s}" for x in lab))
    rows = ([(k, v) for k, v in d["models"].items()]
            + [(f"HANSARD {k}", d["chambers"][k]["segments_scoreable"])
               for k in ("_ALL",)]
            + [(f"HANSARD turns", d["chambers"]["_ALL"]["turns"])])
    for k, v in rows:
        n = sum(v["hist"]) or 1
        print(f"  {k:<24s} " + " ".join(f"{100*c/n:>7.1f}%" for c in v["hist"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--procs", type=int, default=6)
    a = ap.parse_args()
    if a.build:
        build(a.procs)
    if a.report:
        report()
    if not (a.build or a.report):
        print("pass --build or --report")


if __name__ == "__main__":
    main()
