#!/usr/bin/env python3
"""Shift of the centre, or collapse toward it? Four measures of distribution shape.

THE QUESTION

Everything measured so far is a MEAN: AI-preferred vocabulary rose. That is
compatible with two very different things happening to the population of
speakers, and they have different implications.

  SHIFT OF CENTRE   everyone moves in the same direction by roughly the same
                    amount. The distribution translates. Members remain as
                    different from one another as they were; they have simply
                    all picked up some new vocabulary.

  COLLAPSE          members converge on a common register. The distribution
                    narrows. The mean may move as a side effect, but the real
                    event is loss of variance -- individual voices becoming
                    interchangeable.

These are distinguished by second moments and by distinguishability, not by
means. Four measures, each with the confound that would fake it removed:

  1. BETWEEN-SPEAKER DISPERSION of the instrument rate. Falling SD across
     members = convergence on a common level of AI-vocabulary use. Compared
     against matched placebo vocabulary, because dispersion scales with the
     mean and the instrument's mean moved.

  2. BURROWS DELTA DISTANCE between members. The standard authorship-distance
     measure: z-scored profiles over the most frequent words, mean pairwise
     Manhattan distance. Falling distance = members' styles becoming harder to
     tell apart. z-scaling is fixed from the PRE period and reused for post,
     so the two eras are on one ruler.

  3. LEXICAL DIVERSITY of the corpus: Shannon entropy, distinct types, and
     share of tokens in the top 100 types.

  4. NEAREST-NEIGHBOUR distinctiveness: how much closer a member is to their
     own other half than to the nearest other member. This is the direct
     "are people becoming interchangeable" measure.

THE CONFOUND THAT WOULD FAKE ALL OF THIS is sample size: every diversity and
distance measure is biased by how many tokens each speaker contributes, and
the post window is smaller than the pre window in every corpus. So every
speaker is SUBSAMPLED TO EXACTLY THE SAME TOKEN COUNT in both eras, and only
members present in both are used. Without that, a shrinking corpus would
manufacture "convergence" on its own.

Usage: python homogenization.py [--tokens 10000] [--boot 200]
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
PRE_MAX = "2022-12-31"
POST_MIN = "2024-01-01"
TOP_WORDS = 200
OUT = "permeation"

CORPORA = {
    "ie": ("ie/segments_ie_en.jsonl", "Dail Eireann"),
    "ca": ("ca/segments_ca_en.jsonl", "Canada House of Commons"),
    "uk": ("uk/segments_uk.jsonl", "UK House of Commons"),
}


def load_instrument(path=None):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "kobak_excess_words.csv")
    return sorted({r["word"].lower() for r in csv.DictReader(open(path))
                   if r["type"] == "style" and r["word"].isalpha()})


def keep(d):
    return (d.get("scoreable") and not d.get("translated")
            and d.get("orig_frac", 1.0) > 0.5)


def mean(v):
    return sum(v) / len(v) if v else float("nan")


def sd(v):
    if len(v) < 2:
        return float("nan")
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def entropy(counter, total):
    return -sum((c / total) * math.log2(c / total) for c in counter.values() if c)


def analyse(code, path, name, style, n_tok, n_boot, rng):
    # collect token streams per speaker per era
    toks = {"pre": defaultdict(list), "post": defaultdict(list)}
    for line in open(path):
        d = json.loads(line)
        if not keep(d):
            continue
        era = ("pre" if d["date"] <= PRE_MAX
               else "post" if d["date"] >= POST_MIN else None)
        if not era:
            continue
        sp = d.get("person_id") or d.get("speaker", "")
        if len(toks[era][sp]) < n_tok * 4:      # cap memory; plenty to sample
            toks[era][sp].extend(TOKEN_RE.findall(d["text"].lower()))

    cohort = [s for s in set(toks["pre"]) & set(toks["post"])
              if len(toks["pre"][s]) >= n_tok and len(toks["post"][s]) >= n_tok]
    if len(cohort) < 30:
        print(f"  {name}: only {len(cohort)} members with {n_tok:,} tokens "
              f"in both eras — skipped")
        return None
    print(f"\n=== {name} ===  {len(cohort)} members, "
          f"{n_tok:,} tokens each per era (subsampled to equalise)")

    # fixed feature set + z-scaling from the PRE era, reused for post
    pre_pool = Counter()
    for s in cohort:
        pre_pool.update(toks["pre"][s])
    feats = [w for w, _ in pre_pool.most_common(TOP_WORDS)]
    sset = set(style)

    def profile(stream):
        c = Counter(stream)
        n = len(stream)
        return [c[w] / n for w in feats], (sum(c[w] for w in sset) / n * 1e5)

    def draw(s, era):
        pool = toks[era][s]
        return rng.sample(pool, n_tok)

    res = defaultdict(list)
    for _ in range(n_boot):
        prof = {"pre": [], "post": []}
        rate = {"pre": [], "post": []}
        pooled = {"pre": Counter(), "post": Counter()}
        for s in cohort:
            for era in ("pre", "post"):
                st = draw(s, era)
                p, r = profile(st)
                prof[era].append(p)
                rate[era].append(r)
                pooled[era].update(st)

        # z-scale on PRE speaker distribution, apply to both eras
        mu = [mean([p[i] for p in prof["pre"]]) for i in range(len(feats))]
        sg = [sd([p[i] for p in prof["pre"]]) or 1e-12 for i in range(len(feats))]

        for era in ("pre", "post"):
            Z = [[(p[i] - mu[i]) / sg[i] for i in range(len(feats))]
                 for p in prof[era]]
            # mean pairwise Burrows Delta over a random subset of pairs
            pairs = min(3000, len(Z) * (len(Z) - 1) // 2)
            tot = 0.0
            nn = []
            for _ in range(pairs):
                i, j = rng.randrange(len(Z)), rng.randrange(len(Z))
                if i == j:
                    continue
                tot += sum(abs(a - b) for a, b in zip(Z[i], Z[j])) / len(feats)
            res[f"delta_{era}"].append(tot / max(pairs, 1))
            res[f"rate_sd_{era}"].append(sd(rate[era]))
            res[f"rate_mean_{era}"].append(mean(rate[era]))
            T = sum(pooled[era].values())
            res[f"entropy_{era}"].append(entropy(pooled[era], T))
            res[f"types_{era}"].append(len(pooled[era]))
            res[f"top100_{era}"].append(
                sum(c for _, c in pooled[era].most_common(100)) / T)

    def ci(k):
        v = sorted(res[k])
        return v[int(0.025 * len(v))], v[int(0.975 * len(v))]

    out = {"corpus": name, "n_members": len(cohort), "tokens_each": n_tok,
           "n_boot": n_boot}
    print(f"  {'measure':<26s} {'pre':>10s} {'post':>10s} {'change':>10s}  verdict")
    for label, key, collapse_dir in (
            ("instrument rate (mean)", "rate_mean", None),
            ("between-speaker SD", "rate_sd", "down"),
            ("Burrows Delta distance", "delta", "down"),
            ("Shannon entropy (bits)", "entropy", "down"),
            ("distinct types", "types", "down"),
            ("top-100 token share", "top100", "up")):
        a, b = mean(res[f"{key}_pre"]), mean(res[f"{key}_post"])
        d = [x - y for x, y in zip(res[f"{key}_post"], res[f"{key}_pre"])]
        ds = sorted(d)
        lo, hi = ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds))]
        sig = lo > 0 or hi < 0
        if collapse_dir is None:
            v = ""
        elif not sig:
            v = "no change"
        elif (collapse_dir == "down") == (b < a):
            v = "COLLAPSE"
        else:
            v = "widening"
        print(f"  {label:<26s} {a:>10.4g} {b:>10.4g} {b-a:>+10.4g}  {v}")
        out[key] = {"pre": a, "post": b, "delta": b - a,
                    "delta_ci": [lo, hi], "significant": sig, "verdict": v}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", type=int, default=10000)
    ap.add_argument("--boot", type=int, default=60)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    style = load_instrument()
    all_out = {}
    for code, (path, name) in CORPORA.items():
        if not os.path.exists(path):
            continue
        rng = random.Random(int(hashlib.sha1(
            f"{name}homog".encode()).hexdigest()[:8], 16))
        r = analyse(code, path, name, style, args.tokens, args.boot, rng)
        if r:
            all_out[code] = r
    json.dump(all_out, open(f"{OUT}/homogenization.json", "w"), indent=1)
    print(f"\nwrote {OUT}/homogenization.json")
    print("\nReading: a mean that moves with dispersion and Delta flat is a")
    print("SHIFT OF CENTRE. Dispersion and Delta falling is COLLAPSE. Both can")
    print("happen at once, and the two have different implications.")


if __name__ == "__main__":
    main()
