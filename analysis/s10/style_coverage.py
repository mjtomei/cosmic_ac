#!/usr/bin/env python3
"""Does the generated corpus under-sample the style list, or is the list
out-of-domain for legislatures?

THE QUESTION

§4.7's alignment excess is computed over Kobak et al.'s 407 "style" words. In
the original 166k-word generation only 212 of those 407 appeared at all, so the
"excess over the style list" was really an excess over whichever half of the
list happened to show up. That looks like a sampling failure and it was
reported as one.

It is not. Kobak's list was derived from PubMed abstracts, and the natural
check -- Matthew's -- is whether REAL legislative text covers the list any
better than generated text does at the same volume. If it does not, the
missing words are biomedical vocabulary that legislatures do not use, and the
denominator of 407 is simply the wrong denominator.

WHAT THIS MEASURES

Style-word coverage at MATCHED WORD VOLUME in three corpora:

  * the paired base+instruct generation (rlhf_gen/)
  * real Hansard from the prompt source era (pre-2023, IE/UK/CA)
  * real Hansard from the scored era (2025-26, same chambers)

Two coverage statistics, because they answer different things. "Present" is
how much of the list the corpus touches at all; ">= 20 occurrences" is how much
of it the corpus measures well enough to estimate a rate on.

RESULT AS OF 2026-08-12, volume-matched at ~770k words (2 families @1600):

  generated BASE        224/407 present (55.0%)   67 at >=20 (16.5%)
  generated INSTRUCT    279/407 present (68.6%)   98 at >=20 (24.1%)
  real Hansard pre-2023 300/407 present (73.7%)   85 at >=20 (20.9%)
  real Hansard 2025-26  296/407 present (72.7%)   92 at >=20 (22.6%)

Three things, and the first correction matters most.

1. THE LIST IS PARTLY OUT-OF-DOMAIN. 111 of 407 words never appear in human
   legislative English at this volume either. The in-domain denominator is
   ~296, not 407, and any coverage statistic quoted against 407 understates
   both corpora equally.

2. BASE GENERATION UNDER-COVERS WHAT REMAINS. 224 against Hansard's 296 -- 76%
   of the coverage at equal volume, and 73% of the depth. Base continuations
   are narrower than the speech they imitate. So the missing vocabulary is NOT
   purely out-of-domain: part of it is real legislative usage the base models
   do not reproduce.

3. INSTRUCT COVERAGE IS HIGHER THAN BASE AND NEARLY MATCHES HANSARD -- 279
   against 296 on presence, and 98 against 92 on depth, where instruct
   actually exceeds it. That is §4.7's claim visible as coverage rather than
   as a rate: post-training moves the model's vocabulary toward this list. It
   is independent corroboration, since it needs no control matching, no
   excess computation and no pseudocount.

AN EARLIER VERSION OF THIS SCRIPT REPORTED FALSE PARITY. It pooled base AND
instruct counts, so 1.66M generated words were compared against 770k of
Hansard, and coverage came out at 73.2% against 72.7% -- apparently identical.
Volume-matched and side-separated, base is 55.0%. Compare one author against
one author.

RE-RUN THIS WHEN THE FULL GENERATION LANDS. Above is two families at
checkpoint 1600; the scaled run targets four families at 6,400 prompts, ~6x
the volume. Two statistics to watch: whether base coverage closes on Hansard
as volume grows (if it does not, narrowness is a property of base
continuation, not of sample size), and whether the instruct-over-base coverage
gap holds on llama31 and the 30B MoE.

Usage: python style_coverage.py [--words 769660]
"""
import argparse
import glob
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rlhf_pref_analyze as A          # noqa: E402
import rlhf_pref_scale as S            # noqa: E402

HANSARD = ["ie/segments_ie_en.jsonl", "uk/segments_uk.jsonl",
           "ca/segments_ca2.jsonl"]


def hansard(style, target, era, seed=9):
    pool = []
    for p in HANSARD:
        fp = os.path.join(HERE, p)
        if not os.path.exists(fp):
            continue
        for line in open(fp):
            d = json.loads(line)
            if not d.get("scoreable") or d.get("translated"):
                continue
            if era == "pre" and d["date"] > "2022-12-31":
                continue
            if era == "post" and d["date"] < "2025-01-01":
                continue
            pool.append(d["text"])
    rng = random.Random(seed)
    rng.shuffle(pool)
    c, n = Counter(), 0
    for t in pool:
        tok, w = A.counts([t])
        c += tok
        n += w
        if n >= target:
            break
    return c, n


def generated(style, side, prompts=None):
    """Counts for ONE side (base or instruct), so the comparison against a
    single human corpus is like-for-like.

    Pooling base AND instruct doubles the generated word count and inflates
    coverage against a volume-matched human corpus. An earlier version of this
    script did exactly that and reported false parity with Hansard.
    """
    c, n, fams = Counter(), 0, []
    for fam, _, _ in S.PAIRS:
        bp = os.path.join(HERE, "rlhf_gen", f"{fam}_base.json")
        ip = os.path.join(HERE, "rlhf_gen", f"{fam}_instruct.json")
        if not (os.path.exists(bp) and os.path.exists(ip)):
            continue
        bg, ig = json.load(open(bp)), json.load(open(ip))
        k = min(len(bg), len(ig))
        if prompts:
            k = min(k, prompts)
        if k < (prompts or 0):
            continue          # family too far behind to contribute
        bg, ig = bg[:k], ig[:k]
        keep = [i for i in range(k) if not A.META.search(ig[i][:300])
                and not A.META.search(bg[i][:300])]
        src = bg if side == "base" else ig
        tok, w = A.counts([src[i] for i in keep])
        c += tok
        n += w
        fams.append(f"{fam}({k})")
    return c, n, fams


def report(name, c, n, style):
    tot = len(style)
    pres = sum(1 for w in style if c[w] > 0)
    ge20 = sum(1 for w in style if c[w] >= 20)
    print(f"  {name:<34s} {n:>10,}w  present {pres:>3d}/{tot} "
          f"({100*pres/tot:>5.1f}%)   >=20 {ge20:>3d} ({100*ge20/tot:>5.1f}%)")
    return pres, ge20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", type=int, default=0,
                    help="match volume; default = the generated corpus size")
    ap.add_argument("--prompts", type=int, default=0,
                    help="balance families at this prompt count")
    args = ap.parse_args()
    style = A.load_style()

    # Balance families so the comparison is not one model at 2x another, but
    # do not let a family that has only just started collapse the whole
    # comparison to its size. Use the largest count at least two families
    # reach.
    have = sorted((len(json.load(open(os.path.join(HERE, "rlhf_gen",
                                                   f"{f}_base.json"))))
                   for f, _, _ in S.PAIRS
                   if os.path.exists(os.path.join(HERE, "rlhf_gen",
                                                  f"{f}_base.json"))),
                  reverse=True)
    bal = args.prompts or (have[1] if len(have) > 1 else
                           (have[0] if have else 0))
    gb, gbn, fams = generated(style, "base", bal)
    gi, gin, _ = generated(style, "instruct", bal)
    target = args.words or gbn
    print(f"Kobak style list: {len(style)} words "
          f"(derived from PubMed abstracts, not from legislative text)\n")
    print(f"matched at ~{target:,} words, families balanced at {bal} prompts\n")
    gp, gg = report(f"generated BASE [{', '.join(fams)}]", gb, gbn, style)
    report("generated INSTRUCT", gi, gin, style)
    hp = hg = None
    for era, lab in (("pre", "real Hansard, pre-2023 (prompts)"),
                     ("post", "real Hansard, 2025-26 (scored)")):
        c, n = hansard(style, target, era)
        p, g = report(lab, c, n, style)
        if era == "post":
            hp, hg = p, g

    if hp and hg:
        print(f"\n  Real Hansard touches {hp}/{len(style)} of the list at this "
              f"volume; {len(style)-hp} words never appear in human")
        print(f"  legislative English either, so the in-domain denominator is "
              f"~{hp}, not {len(style)}.")
        print(f"  But generated text touches only {gp} -- "
              f"{100*gp/hp:.0f}% of what Hansard does at equal volume, and "
              f"reaches depth")
        print(f"  on {100*gg/hg:.0f}% as many words. Generated continuations "
              f"are narrower than the")
        print(f"  speech they imitate. BOTH facts hold: the list is partly "
              f"out-of-domain AND the")
        print(f"  generation under-covers what remains.")


if __name__ == "__main__":
    main()
