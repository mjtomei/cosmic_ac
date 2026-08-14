#!/usr/bin/env python3
"""Does the instrument track secularism, or professional register?

THE HYPOTHESIS (Matthew's, 2026-08-13)

The Kobak style list is not derived from any legislature -- it comes from
PubMed, i.e. scientific prose. So the thing it measures may be scientific or
secular register rather than anything national, and the United States, founded
on constitutional secularism, would already sit at the ceiling. That would
explain US flatness as saturation rather than as an artifact of orientation.

WHAT THE LIST ACTUALLY CONTAINS

Inspected before testing: crucial, facilitating, fostering, optimizing, delves,
groundbreaking, seamlessly, streamlines, methodologies, invaluable, elevate,
unveils, harness, amidst. That is professional-academic prose, not scientific
content -- the biomedical vocabulary (lncrnas, mpox, hydroxychloroquine) sits
in the list's separate `content` type, which this study already excludes. So
the instrument cannot be measuring science literacy directly. Whether it tracks
SECULARISM is a different question and is what this measures.

THE TEST

Religious-reference density per chamber-year, against the instrument gap. If
the instrument is a secularism proxy the two should be strongly negatively
correlated: chambers that invoke God should score low on it.

THE PREDICTION THAT MAKES THIS DECISIVE

The United States is the case that separates the hypotheses, because its two
kinds of secularism point opposite ways. It has the strongest CONSTITUTIONAL
secularism in the anglophone world and by far the most religious LEGISLATIVE
SPEECH -- opening prayers, "God bless America", floor invocation. Britain has
an established church, bishops sitting in its upper house, and famously secular
Commons rhetoric.

  If the instrument tracks secularism-as-discourse, the US should score LOW.
  It scores highest of any chamber. That is evidence against.

  If it tracks secularism-as-constitution, the US should score high and the UK
  low -- which is the observed direction, so the hypothesis survives this test
  and needs a different one to separate it from "professional register".

WHAT WOULD SEPARATE THEM. Religiosity varies enormously WITHIN countries --
compare Alberta with Quebec, or Queensland with Victoria. If the instrument
tracks secular disposition, that within-country variation should predict it,
holding the country fixed. If it is professional register, it should not.

EXCLUSIONS THAT MATTER. "Lord" and "Lords" are dropped: in Westminster and its
descendants they are overwhelmingly the upper house and the vocative "my
Lords", not invocation. "Chaplain", "prayers" as an order of business, and
"reverend" as a courtesy title are procedural furniture in most of these
chambers. Counting them would measure a chamber's standing orders rather than
its religiosity.

Usage: python secularism_check.py [--procs 10]
"""
import argparse
import collections
import glob
import json
import os
import re

TOKEN_RE = re.compile(r"[a-z']+")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "secularism_check.json")

# Invocation and belief, not institutions or procedure. See the docstring for
# why lord/lords/chaplain/prayers are absent.
RELIGIOUS = {
    "god", "gods", "almighty", "divine", "providence", "holy", "sacred",
    "faith", "faithful", "prayer", "pray", "prayed", "praying", "blessing",
    "blessings", "blessed", "bless", "worship", "religion", "religious",
    "scripture", "scriptures", "bible", "biblical", "gospel", "christ",
    "christian", "christianity", "muslim", "islam", "islamic", "jewish",
    "judaism", "hindu", "sikh", "buddhist", "church", "churches", "mosque",
    "synagogue", "temple", "congregation", "parish", "clergy", "priest",
    "imam", "rabbi", "soul", "souls", "spiritual", "salvation", "sin",
}


def _scan(job):
    ch, files = job
    per_year = collections.Counter()
    words = collections.Counter()
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
                for w in t:
                    if w in RELIGIOUS:
                        per_year[y] += 1
    return ch, dict(per_year), dict(words)


def sources():
    import occurrence_trends as OT
    return OT.SOURCES


def spearman(a, b):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(o):
            r[i] = pos + 1
        return r
    x, y = rk(a), rk(b)
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    import math
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    if not sx or not sy:
        return 0.0
    return sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (sx * sy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=10)
    a = ap.parse_args()
    from multiprocessing import Pool
    import sys
    sys.path.insert(0, HERE)

    src = sources()
    with Pool(a.procs) as pool:
        res = pool.map(_scan, sorted(src.items()))

    trends = json.load(open(os.path.join(HERE, "occurrence_trends.json")))
    out = {}
    for ch, per_year, words in res:
        rows = []
        for y in sorted(per_year):
            if words[y] < 200_000:
                continue
            rows.append({"year": int(y), "religious_per100k":
                         per_year[y] / words[y] * 1e5})
        out[ch] = rows

    print("RELIGIOUS REFERENCE DENSITY vs INSTRUMENT GAP, 2025-26\n")
    print(f"  {'chamber':<11s} {'religious/100k':>15s} {'instrument gap':>15s}")
    pairs = []
    for ch in sorted(out):
        rel = [r for r in out[ch] if r["year"] >= 2025]
        gap = [r for r in trends.get(ch, []) if r["year"] >= 2025]
        if not rel or not gap:
            continue
        rv = sum(r["religious_per100k"] for r in rel) / len(rel)
        gv = sum(r["gap"] for r in gap) / len(gap)
        pairs.append((ch, rv, gv))
    for ch, rv, gv in sorted(pairs, key=lambda x: -x[1]):
        print(f"  {ch:<11s} {rv:>15.1f} {gv:>15.0f}")

    if len(pairs) > 3:
        r = spearman([p[1] for p in pairs], [p[2] for p in pairs])
        print(f"\n  Spearman(religiosity, instrument) = {r:+.3f}  "
              f"over {len(pairs)} chambers")
        print("  A secularism proxy predicts a strongly NEGATIVE correlation.")

    json.dump({"religious": out, "pairs": pairs},
              open(OUT, "w"), indent=1)
    print(f"\nwrote {os.path.basename(OUT)}")


if __name__ == "__main__":
    main()
