#!/usr/bin/env python3
"""Is the drift one-way, or does our yardstick only face one way?

THE PROBLEM WITH 4.5a AS IT STANDS

Measured on Kobak's style list, UK Commons roughly quadruples between 1994 and
2026 while US House and Senate move 13% and 19%. The natural reading is
asymmetric diffusion: American register is the attractor and the United States
is not a party to the exchange.

But Kobak's list was derived from PubMed abstracts -- American scientific
English. On a yardstick calibrated to American usage, a country that already
writes that way starts at the reference point and has nowhere to drift. The
same picture would appear under perfectly MUTUAL exchange, because the
dimension along which the US would be moving is not the dimension being
measured. The observation cannot distinguish "the US does not move" from "we
are not looking where it moves".

THE TEST

Build two instruments from the SAME base period by the SAME procedure, one
facing each way:

  US-marked words   most over-represented in US House+Senate vs UK Commons
  UK-marked words   most over-represented in UK Commons vs US House+Senate

both drawn from 1994-1996 -- pre-web, pre-transformer, and the earliest window
where all three chambers exist -- then tracked in BOTH corpora through 2026.
Four series from one construction. The prediction that separates the
hypotheses:

  ONE-WAY     UK rises on US-marked words; US flat on UK-marked words.
  MUTUAL      each rises on the other's words.
  ARTIFACT    neither rises on the other's words, and 4.5a was measuring the
              instrument's orientation rather than a diffusion.

CONTROLS, BECAUSE THE NAIVE VERSION PASSES ON ARTIFACTS

  SPELLING. -ize/-ise, -our/-or and friends would dominate both lists and would
  say only that the two countries spell differently. Dropped both ways.

  TOPIC AND INSTITUTIONS. "senator", "riding", "dollar" are markers of subject
  matter, not register, and cannot diffuse -- Westminster has no senators.
  Requiring a word to be attested >= MIN_BOTH times in BOTH corpora in the base
  period removes untranslatable referents while keeping managerial vocabulary,
  whose diffusion is the phenomenon rather than a confound.

  REGRESSION TO THE MEAN. A word selected for being extreme in 1994-96 will
  drift toward average afterwards in ANY corpus, including the one it was
  selected from, purely as sampling noise. This is the trap that would
  manufacture a "convergence" finding out of nothing. Two guards: the selection
  window is EXCLUDED from the reported series, and each instrument is tracked
  in its OWN source too -- if UK-marked words decline in the UK at the same
  rate they rise in the US, that is reversion, not diffusion.

Usage: python mirror_instrument.py [--n 150] [--min-both 40]
"""
import argparse
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_RE = re.compile(r"[a-z']+")
OUT = os.path.join(HERE, "mirror_instrument.json")
BASE = ("1994", "1995", "1996")
SRC = {"UK": ["uk/segments_uk_deep.jsonl"],
       "US": ["us/segments_us_house.jsonl", "us/segments_us_senate.jsonl"]}
SPELL = [(re.compile(r"ise$"), "ize"), (re.compile(r"ised$"), "ized"),
         (re.compile(r"ising$"), "izing"), (re.compile(r"isation$"), "ization"),
         (re.compile(r"our$"), "or"), (re.compile(r"ours$"), "ors"),
         (re.compile(r"tre$"), "ter"), (re.compile(r"ogue$"), "og"),
         (re.compile(r"ence$"), "ense"), (re.compile(r"elled$"), "eled"),
         (re.compile(r"elling$"), "eling")]
ORTHO = {"percent", "per", "cent", "anymore", "programme", "programmes"}


def _count(job):
    """Per-year token counts for one corpus."""
    name, files, need = job
    per_year, words = defaultdict(Counter), Counter()
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
                if need is None:
                    c.update(t)
                else:
                    for w in t:
                        if w in need:
                            c[w] += 1
    return name, {y: dict(c) for y, c in per_year.items()}, dict(words)


def spelling_variants(vocab):
    out = set()
    for w in vocab:
        for pat, rep in SPELL:
            if pat.search(w):
                b = pat.sub(rep, w)
                if b in vocab:
                    out.add(w)
                    out.add(b)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--min-both", type=int, default=40)
    a = ap.parse_args()

    print("pass 1: full vocabulary in the 1994-96 base window")
    with Pool(2) as pool:
        res = pool.map(_count, [(k, v, None) for k, v in SRC.items()])
    base_c, base_w = {}, {}
    for name, per_year, words in res:
        c, n = Counter(), 0
        for y in BASE:
            c.update(per_year.get(y, {}))
            n += words.get(y, 0)
        base_c[name], base_w[name] = c, n
        print(f"  {name}: {n:,} words in {'/'.join(BASE)}")

    shared = [w for w in set(base_c["UK"]) & set(base_c["US"])
              if w.isalpha() and len(w) >= 4
              and base_c["UK"][w] >= a.min_both
              and base_c["US"][w] >= a.min_both]
    spell = spelling_variants(set(shared))
    cand = [w for w in shared if w not in spell and w not in ORTHO]
    print(f"  {len(shared):,} words attested >={a.min_both} in both; "
          f"{len(spell)} spelling variants and {len(cand):,} candidates remain")

    def lr(w):
        return math.log((base_c["US"][w] / base_w["US"])
                        / (base_c["UK"][w] / base_w["UK"]))
    ranked = sorted(cand, key=lr)
    uk_marked = ranked[:a.n]
    us_marked = ranked[-a.n:]
    print(f"\n  US-marked sample: {', '.join(us_marked[-12:])}")
    print(f"  UK-marked sample: {', '.join(uk_marked[:12])}")

    need = set(uk_marked) | set(us_marked)
    print("\npass 2: tracking both instruments in both corpora")
    with Pool(2) as pool:
        res = pool.map(_count, [(k, v, need) for k, v in SRC.items()])
    series = {}
    for name, per_year, words in res:
        rows = []
        for y in sorted(per_year):
            if words[y] < 200_000 or y in BASE:
                continue        # base window excluded: see regression-to-mean
            rows.append({
                "year": int(y), "words": words[y],
                "us_marked": sum(per_year[y].get(w, 0) for w in us_marked)
                / words[y] * 1e5,
                "uk_marked": sum(per_year[y].get(w, 0) for w in uk_marked)
                / words[y] * 1e5})
        series[name] = rows

    print(f"\n  {'year':<6s}" + "".join(
        f"{c + ' ' + m:>16s}" for c in ("UK", "US") for m in ("us-mk", "uk-mk")))
    yrs = sorted({r["year"] for s in series.values() for r in s})
    for y in yrs:
        row = f"  {y:<6d}"
        for c in ("UK", "US"):
            r = next((r for r in series[c] if r["year"] == y), None)
            for m in ("us_marked", "uk_marked"):
                row += f"{r[m]:>16.1f}" if r else f"{'-':>16s}"
        print(row)

    print("\n\nCHANGE OVER THE SERIES (first year -> last)\n")
    verdict = {}
    for c in ("UK", "US"):
        s = series[c]
        if len(s) < 2:
            continue
        for m in ("us_marked", "uk_marked"):
            f, l = s[0][m], s[-1][m]
            verdict[f"{c}:{m}"] = l / f if f else 0
            print(f"  {c} on {m.replace('_', '-'):<10s} "
                  f"{f:>8.1f} -> {l:>8.1f}   x{l/f:.2f}")
    json.dump({"us_marked": us_marked, "uk_marked": uk_marked,
               "series": series, "ratios": verdict},
              open(OUT, "w"), indent=1)
    print(f"\nwrote {os.path.basename(OUT)}")
    print("\nRead the two CROSS terms: UK on us-marked (does Britain adopt "
          "American usage?)\nand US on uk-marked (does America adopt British "
          "usage?). The two OWN terms\nare the reversion check -- if a list "
          "falls in its own source as fast as it\nrises elsewhere, that is "
          "regression to the mean, not diffusion.")


if __name__ == "__main__":
    main()
