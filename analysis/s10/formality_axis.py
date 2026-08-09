#!/usr/bin/env python3
"""Build an EMPIRICAL formality control set, then test the AI instrument against it.

The hand-picked register control (honourable/pursuant/...) behaved perfectly
on NB and the UK full corpus but rose to 1.105 in the UK within-speaker
subset, leaving "is the AI signal just formalization?" unresolved. A
hand-picked list also invites the objection that it was chosen to pass.

This builds the control from data instead, using PRE-PERIOD ONLY (no
outcome leakage):

  formality score(w) = log[ rate(w | long pre-period speeches)
                          / rate(w | short pre-period speeches) ]

Long speeches (>=300 words) are overwhelmingly prepared; short interventions
(50-120 words) are overwhelmingly spontaneous. Words that mark the prepared
register score high. We take the top-scoring words, frequency-matched to the
AI instrument's own pre-period frequency profile, as the control.

Then the decisive comparison, on the identical statistic:
    instrument mean logFC   vs   formality-control mean logFC
If formalization explains the AI signal, the two move together. If the
instrument leads a *data-defined* formality axis, it is measuring something
formalization does not.

Usage: python formality_axis.py CORPUS_LABEL SEGMENTS.jsonl [more.jsonl ...]
"""
import csv
import json
import math
import os
import re
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
MIN_COUNT = 20
TOKEN_RE = re.compile(r"[a-z']+")
TOKEN_CASE = re.compile(r"[A-Za-z']+")
PRE_MAX = "2022-12-31"
POST_MIN = "2024-01-01"
LONG_MIN = 300
SHORT_MAX = 120


def main():
    label, files = sys.argv[1], sys.argv[2:]
    style = sorted({r["word"].lower() for r in
                    csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                    if r["type"] == "style" and r["word"].isalpha()})

    pre_c, post_c = Counter(), Counter()
    long_c, short_c = Counter(), Counter()
    pre_w = post_w = long_w = short_w = 0
    # dispersion: how many distinct pre-period sitting dates each word appears
    # in. Topic words and proper nouns concentrate in few sittings; register
    # words spread across all of them. Without this the long-vs-short axis
    # measures topical specificity, not formality (verified: it returned
    # place names and bill topics).
    date_sets = {}
    pre_dates = set()
    cap_c = Counter()

    for path in files:
        for line in open(path):
            s = json.loads(line)
            if not s.get("scoreable"):
                continue
            d, n = s["date"], s["n_words"]
            raw = TOKEN_CASE.findall(s["text"])
            toks = [t.lower() for t in raw]
            if d <= PRE_MAX:
                pre_c.update(toks); pre_w += len(toks)
                pre_dates.add(d)
                # proper-noun detector: capitalised NOT at sentence start
                for j, t in enumerate(raw):
                    if j and t[:1].isupper():
                        cap_c[t.lower()] += 1
                for w in set(toks):
                    date_sets.setdefault(w, set()).add(d)
                if n >= LONG_MIN:
                    long_c.update(toks); long_w += len(toks)
                elif n <= SHORT_MAX:
                    short_c.update(toks); short_w += len(toks)
            elif d >= POST_MIN:
                post_c.update(toks); post_w += len(toks)
    n_dates = len(pre_dates)
    disp = {w: len(ds) / n_dates for w, ds in date_sets.items()}
    # the instrument's own dispersion floor — the control must be at least as
    # topic-general as the thing it is controlling for
    inst_disp = sorted(disp.get(w, 0) for w in style)
    DISP_MIN = inst_disp[len(inst_disp) // 2]    # MEDIAN of instrument
    print(f"dispersion floor = instrument median: {DISP_MIN:.3f} "
          f"of {n_dates} sitting dates")

    print(f"[{label}] pre {pre_w:,}w (long {long_w:,} / short {short_w:,}), "
          f"post {post_w:,}w")

    # --- formality axis from pre-period only ---
    scored = []
    for w, n in pre_c.items():
        # Floor was 200, which sits above log2 bucket 7 -- but 227 of the
        # instrument's 407 words live in buckets 0-3, so those quotas could
        # never fill and the realised control came out systematically MORE
        # COMMON than the thing it controls (review F7: NB filled only 67 of
        # 407). 20 is low enough to fill the rare buckets while still giving
        # a stable long-vs-short ratio.
        if n < MIN_COUNT or len(w) < 4 or not w.isalpha():
            continue
        if disp.get(w, 0) < DISP_MIN:
            continue
        if cap_c[w] / n > 0.25:      # mostly a proper noun
            continue
        lo = (long_c[w] + 0.5) / long_w
        sh = (short_c[w] + 0.5) / short_w
        scored.append((math.log(lo / sh), w))
    scored.sort(reverse=True)

    # frequency-match the control to the instrument's pre-period profile
    inst_buckets = Counter(int(math.log2(pre_c[w] + 1)) for w in style)
    by_bucket = {}
    for sc, w in scored:
        b = int(math.log2(pre_c[w] + 1))
        by_bucket.setdefault(b, []).append(w)
    control, sset = [], set(style)
    realised = {}
    for b, want in sorted(inst_buckets.items()):
        pool = [w for w in by_bucket.get(b, []) if w not in sset]
        take = pool[:want]
        # If a bucket still cannot fill, borrow from the nearest neighbouring
        # buckets rather than silently shipping a shorter control -- an
        # unfilled quota is exactly the frequency mismatch this is meant to
        # remove.
        if len(take) < want:
            for off in (1, -1, 2, -2, 3, -3, 4, -4):
                if len(take) >= want:
                    break
                extra = [w for w in by_bucket.get(b + off, [])
                         if w not in sset and w not in take]
                take.extend(extra[:want - len(take)])
        realised[b] = (want, len(take))
        control.extend(take)
    filled = sum(n for _, n in realised.values())
    print(f"formality control: {filled} words of {len(style)} requested; "
          f"overlap with instrument: {len(set(control) & sset)}")
    print("  bucket match (log2 pre-count: wanted/filled): " +
          " ".join(f"{b}:{w}/{n}" for b, (w, n) in sorted(realised.items())))
    print(f"  top formality markers: {', '.join(control[:12])}")

    def mean_lfc(words):
        return sum(math.log(((post_c[w] + 0.5) / post_w) /
                            ((pre_c[w] + 0.5) / pre_w)) for w in words) / len(words)

    inst = mean_lfc(style)
    ctrl = mean_lfc(control)
    print(f"\n  AI instrument      mean logFC = {inst:+.4f}")
    print(f"  formality control  mean logFC = {ctrl:+.4f}")
    print(f"  GAP (instrument - formality)  = {inst - ctrl:+.4f}")
    print("  -> the instrument is measuring formalization" if inst - ctrl < 0.02
          else "  -> the instrument leads the formality axis")

    out = {"corpus": label, "n_instrument": len(style), "n_control": len(control),
           "instrument_mean_logFC": round(inst, 5),
           "formality_mean_logFC": round(ctrl, 5),
           "gap": round(inst - ctrl, 5),
           "control_words": control}
    fn = re.sub(r"\W+", "_", label.lower()) + "_formality.json"
    json.dump(out, open(fn, "w"), indent=1)
    print(f"wrote {fn}")


if __name__ == "__main__":
    main()
