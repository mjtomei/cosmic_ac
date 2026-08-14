#!/usr/bin/env python3
"""How often does each Kobak style word actually occur? The frequency histogram.

THE ARGUMENT BEING CHECKED

§4.7's excess is computed over Kobak et al.'s 407 "style" words, and only about
half of them appear in the generated corpus at all. `style_coverage.py` answered
that with a presence count -- real Hansard covers barely more of the list at the
same volume, so the list is partly out-of-domain and 407 is the wrong
denominator. That is a two-number summary of a distribution, and it can hide the
thing it is meant to rule out.

This prints the distribution. For each corpus at MATCHED WORD VOLUME, the count
of style words occurring 0 times, 1-2 times, 3-5, and so on. The argument
survives only if the corpora have the SAME SHAPE -- if generated text has a
fatter zero bin than Hansard does at equal volume, the missing words are a
property of the generation and not of the word list.

THE DECISIVE TEST IS THE OVERLAP, NOT THE SHAPE

Two corpora can have identical zero counts and still be missing different words.
So this also partitions the list four ways: absent from both, absent from
Hansard only, ABSENT FROM GENERATED ONLY, and present in both. The third cell is
the one that matters -- those are words real legislators use at this volume and
the models did not produce. If that cell is large, "the list is out of domain"
is the wrong defence no matter how similar the histograms look.

MATCHED VOLUME IS NOT OPTIONAL

Occurrence counts scale with corpus size, so comparing a 1.6M-word generated
corpus against 770k of Hansard would show the generated side covering more of
the list for arithmetic reasons alone. An earlier version of style_coverage.py
made exactly that mistake by pooling base and instruct. Every corpus here is
truncated to the same word count, and base and instruct are counted separately.

Usage: python style_word_frequency.py [--prompts 1600] [--words N]
"""
import argparse
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rlhf_pref_analyze as A          # noqa: E402
import style_coverage as SC            # noqa: E402

OUT = os.path.join(HERE, "style_word_frequency.json")
BINS = [(0, 0, "0"), (1, 2, "1-2"), (3, 5, "3-5"), (6, 10, "6-10"),
        (11, 20, "11-20"), (21, 50, "21-50"), (51, 100, "51-100"),
        (101, 500, "101-500"), (501, 10 ** 9, "500+")]


def hist(counts, style):
    out = []
    for lo, hi, _ in BINS:
        out.append(sum(1 for w in style if lo <= counts[w] <= hi))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", type=int, default=0)
    ap.add_argument("--words", type=int, default=0)
    a = ap.parse_args()
    style = A.load_style()

    import rlhf_pref_scale as S
    have = sorted((len(json.load(open(os.path.join(HERE, "rlhf_gen",
                                                   f"{f}_base.json"))))
                   for f, _, _ in S.PAIRS
                   if os.path.exists(os.path.join(HERE, "rlhf_gen",
                                                  f"{f}_base.json"))),
                  reverse=True)
    bal = a.prompts or (have[1] if len(have) > 1 else have[0])
    gb, gbn, fams = SC.generated(style, "base", bal)
    gi, gin, _ = SC.generated(style, "instruct", bal)
    target = a.words or min(gbn, gin)
    hp, hpn = SC.hansard(style, target, "pre")
    ho, hon = SC.hansard(style, target, "post")

    corpora = [("generated BASE", gb, gbn), ("generated INSTRUCT", gi, gin),
               ("Hansard pre-2023", hp, hpn), ("Hansard 2025-26", ho, hon)]

    print(f"Kobak style list: {len(style)} words (from PubMed abstracts)")
    print(f"families {', '.join(fams)}; matched at ~{target:,} words\n")
    print("HOW MANY STYLE WORDS OCCUR THIS OFTEN\n")
    print(f"  {'corpus':<20s} {'words':>9s} " +
          " ".join(f"{b[2]:>8s}" for b in BINS))
    rows = {}
    for name, c, n in corpora:
        hh = hist(c, style)
        rows[name] = {"hist": hh, "words": n,
                      "present": len(style) - hh[0],
                      "median_count": sorted(c[w] for w in style)[len(style) // 2]}
        print(f"  {name:<20s} {n:>9,} " + " ".join(f"{x:>8d}" for x in hh))
    print(f"\n  {'as % of 407':<20s} {'':>9s} " +
          " ".join(f"{100*rows['generated BASE']['hist'][i]/len(style):>7.1f}%"
                   for i in range(len(BINS))))

    print("\n\nTHE OVERLAP -- which words are missing, not how many\n")
    ref = ("Hansard 2025-26", ho)
    for gname, g in (("generated BASE", gb), ("generated INSTRUCT", gi)):
        both = [w for w in style if g[w] == 0 and ref[1][w] == 0]
        gen_only = [w for w in style if g[w] == 0 and ref[1][w] > 0]
        han_only = [w for w in style if g[w] > 0 and ref[1][w] == 0]
        pres = [w for w in style if g[w] > 0 and ref[1][w] > 0]
        rows[gname]["overlap"] = {
            "absent_both": len(both), "absent_generated_only": len(gen_only),
            "absent_hansard_only": len(han_only), "present_both": len(pres),
            "generated_only_examples": sorted(gen_only,
                                              key=lambda w: -ref[1][w])[:25]}
        print(f"  {gname} vs {ref[0]}")
        print(f"    absent from BOTH          {len(both):>4d}   "
              f"out-of-domain for legislatures")
        print(f"    ABSENT FROM GENERATED ONLY{len(gen_only):>4d}   "
              f"real usage the models did not produce")
        print(f"    absent from Hansard only  {len(han_only):>4d}")
        print(f"    present in both           {len(pres):>4d}")
        if gen_only:
            top = sorted(gen_only, key=lambda w: -ref[1][w])[:12]
            print("    most-used of the generated-only absences: "
                  + ", ".join(f"{w}({ref[1][w]})" for w in top))
        print()

    json.dump({"style_n": len(style), "bins": [b[2] for b in BINS],
               "target_words": target, "families": fams, "corpora": rows},
              open(OUT, "w"), indent=1)
    print(f"wrote {os.path.basename(OUT)}")


if __name__ == "__main__":
    main()
