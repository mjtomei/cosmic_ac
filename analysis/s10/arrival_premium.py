#!/usr/bin/env python3
"""Is the new-arrival register premium a COHORT effect or a TENURE artifact?

THE PROBLEM IT SETTLES

Across eight Canadian provinces, members who arrived after 2010 use the Kobak
register at +2.47 per 1,000 words more than members who were already sitting —
in the same years, larger than the entire corpus-level change. That looks like
cohort replacement driving the whole pre-LLM climb.

But there is a mundane rival. New members are backbenchers; long-serving
members are disproportionately ministers reading departmental answers. If
backbench speech simply carries more of this register than ministerial speech,
the premium is about ROLE and would appear in any era, including eras before
the register was climbing.

The two are separable with enough time depth, and the UK series has it
(2006-2026, one chamber, one Hansard office, one extractor):

  TENURE ARTIFACT  the premium is roughly constant across eras — newcomers
                   always speak this way relative to incumbents
  COHORT EFFECT    the premium GROWS — each intake arrives further along the
                   register than the one before, which is what would make
                   replacement a mechanism rather than a constant offset

For each probe year the premium is (rate of members not seen in the preceding
four years) minus (rate of members who were), both measured in that same year,
so era, chamber and extractor are held fixed by construction.

Members are matched on the printed speaker string, normalised for honorifics.
The Speaker and procedural voices are excluded; UK Hansard prints ministers
under their own names, so ministers are present in both groups — which is what
makes the role rival testable rather than assumed away.

Usage: python arrival_premium.py [--seg uk/segments_uk_long.jsonl]
"""
import argparse
import csv
import json
import os
import re
from collections import defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
TITLE_RE = re.compile(
    r"^(rt\.?\s+hon\.?|hon\.?|honourable|mr\.?|mrs\.?|ms\.?|miss|dr\.?|sir|"
    r"dame|lord|baroness|the)\s+", re.I)
CHAIR = re.compile(r"^(speaker|deputy speaker|madam deputy speaker|chair|"
                   r"clerk|several hon|hon\.? members|an hon)", re.I)
LOOKBACK = 4
MIN_WORDS = 4000


def norm(s):
    s = (s or "").strip().rstrip(":").strip()
    prev = None
    while prev != s:
        prev = s
        s = TITLE_RE.sub("", s).strip()
    return re.sub(r"\s*\(.*?\)\s*$", "", s).lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seg", default="uk/segments_uk_long.jsonl")
    args = ap.parse_args()
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}

    # per (year, member): [words, style hits]
    cell = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for line in open(args.seg):
        d = json.loads(line)
        if not d.get("scoreable"):
            continue
        nm = norm(d.get("speaker", ""))
        if not nm or CHAIR.match(nm):
            continue
        y = int(d["date"][:4])
        t = TOKEN_RE.findall(d["text"].lower())
        c = cell[y][nm]
        c[0] += len(t)
        c[1] += sum(1 for x in t if x in style)

    years = sorted(y for y in cell if sum(v[0] for v in cell[y].values()) > 3_000_000)
    print(f"UK, {years[0]}–{years[-1]}; a member counts as NEW in year Y if "
          f"absent from all of Y−1..Y−{LOOKBACK}\n")
    print(f"{'year':<6s} {'incumbent':>10s} {'new':>8s} {'PREMIUM':>9s} "
          f"{'n_new':>6s} {'n_inc':>6s}")
    rows = []
    for y in years:
        if y - LOOKBACK < years[0]:
            continue
        prior = set()
        for b in range(1, LOOKBACK + 1):
            prior |= set(cell.get(y - b, {}))
        inc = [n for n, v in cell[y].items() if n in prior and v[0] >= MIN_WORDS]
        new = [n for n, v in cell[y].items() if n not in prior and v[0] >= MIN_WORDS]
        if len(inc) < 20 or len(new) < 10:
            continue
        ri = (sum(cell[y][n][1] for n in inc) /
              sum(cell[y][n][0] for n in inc) * 1000)
        rn = (sum(cell[y][n][1] for n in new) /
              sum(cell[y][n][0] for n in new) * 1000)
        rows.append((y, ri, rn, rn - ri, len(new), len(inc)))
        print(f"{y:<6d} {ri:>10.2f} {rn:>8.2f} {rn - ri:>+9.2f} "
              f"{len(new):>6d} {len(inc):>6d}")

    if len(rows) >= 4:
        xs = [r[0] for r in rows]
        ys = [r[3] for r in rows]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        den = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
        early = [r[3] for r in rows if r[0] <= 2014]
        late = [r[3] for r in rows if r[0] >= 2015]
        print(f"\nmean premium {my:+.2f} per 1,000 words")
        print(f"trend in the premium: {slope:+.4f} per year")
        if early and late:
            print(f"  mean premium {min(xs)}–2014: {sum(early)/len(early):+.2f}")
            print(f"  mean premium 2015–{max(xs)}: {sum(late)/len(late):+.2f}")
        print("\nReading: a premium that is large but FLAT is a tenure/role")
        print("artifact — newcomers always differ from incumbents. A premium")
        print("that GROWS means each intake arrives further along the register,")
        print("which is the cohort mechanism the province decomposition implies.")


if __name__ == "__main__":
    main()
