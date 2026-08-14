#!/usr/bin/env python3
"""What fraction of the legislative record can this study actually see?

WHY WORDS AND NOT SEGMENTS

A "segment" is not a natural unit. It is produced by `segment.py`, which
assembles paragraphs into speaker turns and then greedily packs each turn into
windows of at most MAX_WORDS = 360, flushing whenever the next paragraph would
overflow, and flagging anything under MIN_WORDS = 50 as unscoreable. A
1,000-word speech becomes roughly three segments; a 60-word interjection
becomes one. So a segment-weighted rate is partly a measurement of our packer.

Words are the record. A word-weighted rate answers "what share of what was
said is machine-drafted", which is the question the study is actually asking,
and it is invariant to how we chose to cut the text up. Word-weighted is the
primary measure; segment-weighted is reported alongside for comparability with
the sampling frame.

WHAT THIS PRINTS

A complete accounting of every word in the extracted record, split by whether
the study can score it and why not. The point is the last line: the share of
words that no amount of sampling can reach, which is the irreducible error bar
on any prevalence figure this study reports.

Usage: python corpus_audit.py
"""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = (sorted(glob.glob(os.path.join(HERE, "provinces", "segments_*.jsonl")))
         + [os.path.join(HERE, p) for p in
            ("ca/segments_ca2.jsonl", "uk/segments_uk.jsonl",
             "ie/segments_ie_en.jsonl", "us/segments_us_house.jsonl",
             "us/segments_us_senate.jsonl")])

SCOREABLE = ("LONG band 120-360", "SHORT band 50-119")


def bucket(d):
    n = int(d.get("n_words") or 0)
    if not d.get("scoreable"):
        return "under 50 words"
    if d.get("translated"):
        return "translated"
    if (d.get("orig_frac") or 1.0) <= 0.5:
        return "majority translated"
    if n < 120:
        return "SHORT band 50-119"
    if n <= 360:
        return "LONG band 120-360"
    return "over 360 words"


def main():
    seg = collections.Counter()
    wrd = collections.Counter()
    turns = collections.defaultdict(list)
    for f in FILES:
        if not os.path.exists(f):
            continue
        for line in open(f):
            d = json.loads(line)
            n = int(d.get("n_words") or 0)
            if n < 1:
                continue
            k = bucket(d)
            seg[k] += 1
            wrd[k] += n
            if d.get("turn_id"):
                turns[d["turn_id"]].append((n, bool(d.get("scoreable"))))

    S, W = sum(seg.values()), sum(wrd.values())
    print(f"extracted record: {S:,} segments, {W:,} words\n")
    print(f"{'':<22s} {'segments':>11s} {'% seg':>7s} {'words':>14s} "
          f"{'% words':>8s}")
    order = ["LONG band 120-360", "SHORT band 50-119", "under 50 words",
             "translated", "majority translated", "over 360 words"]
    for k in order:
        if not seg[k]:
            continue
        tag = "  [scored]" if k in SCOREABLE else "  [OUT]"
        print(f"{k:<22s} {seg[k]:>11,} {100*seg[k]/S:>6.1f}% "
              f"{wrd[k]:>14,} {100*wrd[k]/W:>7.1f}%{tag}")

    inb = sum(wrd[k] for k in SCOREABLE)
    out = W - inb
    print(f"\n  reachable at all: {100*inb/W:.1f}% of words "
          f"({100*sum(seg[k] for k in SCOREABLE)/S:.1f}% of segments)")
    print(f"  OUTSIDE ANY BAND: {100*out/W:.1f}% of words -- "
          f"{100*wrd['under 50 words']/W:.1f}pp of it is text under 50 words,")
    print(f"  which Pangram refuses outright, so it is unmeasurable rather "
          f"than merely unmeasured.")
    print(f"\n  IMPLIED ERROR BAR. A word-weighted rate r measured on the "
          f"reachable {100*inb/W:.1f}%")
    print(f"  bounds the true corpus rate to [{inb/W:.3f}r, "
          f"{inb/W:.3f}r + {out/W:.3f}], since the unreachable share could in "
          f"principle be")
    # r is now the word-weighted, all-bands pooled rate from
    # banded_prevalence.py (9.03%, 20 chambers, fraction-weighted), not the old long-band
    # 12.4%. The bands the study once excluded are scored; what remains
    # outside is text under 50 words, which Pangram refuses outright.
    R = 0.0897
    print(f"  all human or all machine. At r = {100*R:.1f}% that is "
          f"[{100*inb/W*R:.1f}%, {100*(inb/W*R + out/W):.1f}%].")

    # The over-360 exclusion is not evenly spread, and it biases the OTHER
    # WAY from the short band: long text has the highest flag rates.
    print("\n  Over-360 exclusion by source -- this one is concentrated, and")
    print("  because flag rate rises with length it biases DOWNWARD:")
    per = collections.Counter()
    perw = collections.Counter()
    tot = collections.Counter()
    for f in FILES:
        if not os.path.exists(f):
            continue
        src = os.path.basename(f).replace("segments_", "").replace(".jsonl", "")
        for line in open(f):
            d = json.loads(line)
            n = int(d.get("n_words") or 0)
            if n < 1:
                continue
            tot[src] += n
            if n > 360:
                per[src] += 1
                perw[src] += n
    for src, _ in perw.most_common(4):
        print(f"    {src:<16s} {per[src]:>7,} segments  "
              f"{100*perw[src]/tot[src]:>5.1f}% of that chamber's words")

    # how much of the short band is an offcut rather than a whole utterance
    sole = rem = mid = 0
    for ws in turns.values():
        if len(ws) == 1:
            n, sc = ws[0]
            if sc and 50 <= n < 120:
                sole += 1
            continue
        for i, (n, sc) in enumerate(ws):
            if sc and 50 <= n < 120:
                if i == len(ws) - 1:
                    rem += 1
                else:
                    mid += 1
    t = sole + rem + mid
    if t:
        print(f"\n  Short-band composition, since the packer can leave a tail "
              f"when it splits a turn:")
        print(f"    whole short turn        {sole:>9,}  {100*sole/t:>5.1f}%")
        print(f"    remainder of split turn {rem:>9,}  {100*rem/t:>5.1f}%")
        print(f"    mid-turn window         {mid:>9,}  {100*mid/t:>5.1f}%")
        print(f"  So {100*(rem+mid)/t:.0f}% of short-band segments are offcuts "
              f"of longer speeches rather than")
        print(f"  complete utterances. Worth splitting the short-band rate by "
              f"origin when it lands.")


if __name__ == "__main__":
    main()
