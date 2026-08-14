#!/usr/bin/env python3
"""How much of the instrument signal is machine-written text?

THE QUESTION

The trend chart counts Kobak instrument words per 100k. The detector arm says
9.03% of 2025-26 words are machine-written. Those are two different
measurements of the same corpus, and the obvious question is how much of the
first is explained by the second: of all the instrument occurrences in the
recent record, what share sits inside text a detector calls machine-written?

It is NOT simply 9.03%. That would hold only if machine text used the
instrument vocabulary at the same rate as human text. The whole premise of the
instrument is that it does not.

THE METHOD

Every segment carrying a Pangram verdict is looked up in the corpus, its
instrument words counted, and the segments grouped by verdict. That gives the
instrument rate inside machine-written text against human-written text, and
their ratio is the multiplier that turns a share of WORDS into a share of
OCCURRENCES:

    ai_share_of_occurrences = (w_ai * r_ai) / (w_ai * r_ai + w_hu * r_hu)

MIXED SEGMENTS ARE THE HONEST DIFFICULTY. A Mixed verdict says a segment is
part machine and part human but not WHICH part, so its instrument words cannot
be assigned. Two bounds are reported instead of a false point estimate:

  LOW    Mixed segments contribute machine occurrences in proportion to their
         AI fraction -- i.e. the machine and human halves use the instrument
         equally often.
  HIGH   the machine half of a Mixed segment uses the instrument at the same
         elevated rate as a fully-AI segment.

The truth is between them, and the gap between the two is the honest width of
this estimate.

WHAT THIS IS NOT. It is not causal. A high instrument rate inside flagged text
is partly why the detector flagged it, so the two measurements are not
independent -- the detector and the word list are both keying on register.
This quantifies overlap between two instruments, not the causal contribution of
machine drafting to the corpus.

Usage: python ai_share_of_instrument.py
"""
import collections
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHMAP = {}
TOKEN_RE = re.compile(r"[a-z']+")
sys.path.insert(0, HERE)
import banded_prevalence as BP          # noqa: E402
import occurrence_trends as OT          # noqa: E402


def scored():
    """seg_id -> (verdict, ai_fraction), for 2025-26 prevalence segments."""
    out = {}
    for r in csv.DictReader(open(os.path.join(HERE, "pangram_p4_verdicts.csv"))):
        if r.get("stratum") != "prev":
            continue
        if (r.get("chamber") or "").upper() in ("TAS", "MB"):
            continue
        out[r["seg_id"]] = (r["pangram"],
                            BP.ai_fraction(r["file"].split(".")[0],
                                           r["pangram"], r.get("fraction_ai")))
    for f, idc in (("pangram_shortband_verdicts.csv", "id"),
                   ("pangram_mb_redraw_verdicts.csv", "id"),
                   ("pangram_ch_p4_verdicts.csv", "id")):
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(open(p)):
            era = r.get("era") or r.get("stratum")
            if era != "prev":
                continue
            if f.startswith("pangram_shortband") and \
               (r["chamber"] or "").upper() == "MB":
                continue
            out[r["seg_id"]] = (r["pangram"],
                                BP.ai_fraction(r[idc], r["pangram"]))
    return out


def main():
    want = scored()
    print(f"  {len(want):,} scored 2025-26 segments to look up\n")

    style = set(OT.load_style())
    agg = collections.defaultdict(lambda: [0, 0])      # verdict -> [words, hits]
    frac_words = frac_hits = 0.0
    found = 0
    files = sorted(set(f for fs in OT.SOURCES.values() for f in fs))
    # A seg_id can appear in more than one corpus file -- a chamber's record is
    # split across its original download, its _fill backfill and its 2025 file,
    # and a stale copy can linger. Counting a segment twice would silently
    # double its contribution, so each is taken once.
    seen = set()
    per_ch = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for path in files:
        p = os.path.join(HERE, path)
        if not os.path.exists(p):
            continue
        for line in open(p):
            d = json.loads(line)
            sid = d.get("seg_id")
            if sid not in want:
                continue
            if sid in seen:
                continue
            seen.add(sid)
            verdict, fr = want[sid]
            t = TOKEN_RE.findall(d["text"].lower())
            hits = sum(1 for w in t if w in style)
            agg[verdict][0] += len(t)
            agg[verdict][1] += hits
            ch = CHMAP.get(d.get("prov") or "", d.get("prov") or "?")
            per_ch[ch][verdict][0] += len(t)
            per_ch[ch][verdict][1] += hits
            frac_words += len(t) * fr
            frac_hits += hits * fr
            found += 1

    print(f"  matched {found:,} of {len(want):,} in the corpora\n")
    print(f"  {'verdict':<8s} {'segments':>9s} {'words':>10s} {'instrument':>11s} "
          f"{'per 100k':>10s}")
    for v in ("Human", "Mixed", "AI"):
        w, h = agg[v]
        if not w:
            continue
        print(f"  {v:<8s} {'':>9s} {w:>10,} {h:>11,} {h/w*1e5:>10.0f}")

    hu_w, hu_h = agg["Human"]
    ai_w, ai_h = agg["AI"]
    mx_w, mx_h = agg["Mixed"]
    r_hu = hu_h / hu_w
    r_ai = ai_h / ai_w
    print(f"\n  instrument rate in machine text is {r_ai/r_hu:.2f}x the human rate")

    # corpus-level shares from the prevalence estimate
    rows = [r for r in BP.load() if r[1] == "prev"]
    W = sum(r[3] for r in rows)
    W_ai = sum(r[3] * r[5] for r in rows)
    share_words = W_ai / W
    print(f"  machine share of WORDS (4.2): {100*share_words:.2f}%\n")

    tot_h = hu_h + ai_h + mx_h
    # LOW: Mixed contributes its AI fraction of its own occurrences
    mixed_lo = 0.0
    # HIGH: the machine half of a Mixed segment carries the AI-text rate
    mixed_hi = 0.0
    seen2 = set()
    for path in files:
        p = os.path.join(HERE, path)
        if not os.path.exists(p):
            continue
        for line in open(p):
            d = json.loads(line)
            sid = d.get("seg_id")
            if sid not in want:
                continue
            if sid in seen2:
                continue
            seen2.add(sid)
            verdict, fr = want[sid]
            if verdict != "Mixed":
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            hits = sum(1 for w in t if w in style)
            mixed_lo += hits * fr
            ai_words_here = len(t) * fr
            mixed_hi += min(hits, ai_words_here * r_ai)

    lo = (ai_h + mixed_lo) / tot_h
    hi = (ai_h + mixed_hi) / tot_h
    print("  SHARE OF INSTRUMENT OCCURRENCES SITTING IN MACHINE-WRITTEN TEXT")
    print(f"    low  (Mixed halves use the instrument equally)  {100*lo:.1f}%")
    print(f"    high (Mixed machine half at the AI-text rate)   {100*hi:.1f}%")
    print(f"\n  against {100*share_words:.1f}% of words -- machine text is "
          f"over-represented\n  in the instrument signal by roughly "
          f"{lo/share_words:.1f}-{hi/share_words:.1f}x.")
    print("\n  Not causal: the detector and the word list both key on register,")
    print("  so a high instrument rate inside flagged text is partly WHY it was")
    print("  flagged. This measures overlap between two instruments.")

    # -------------------------------------------------- write the share file
    #
    # ai_share_by_chamber.json feeds convergence_check.py and the charts page.
    # It used to be maintained BY HAND, and it went stale the moment federal
    # Canada's chamber row moved from the genre arm to its uniform draw: the
    # file still said 16.46% while the estimator said 18.48%, and nothing in
    # either consumer could have noticed. It is generated here now, from the
    # same estimator that produces every other figure.
    #
    # share_words         each chamber's machine share of words -- the 4.2 rate
    # ratio               instrument rate in machine text over human text
    # share_occurrences   share of INSTRUMENT OCCURRENCES sitting in machine
    #                     text, which is the higher number, because machine
    #                     text carries the instrument more densely
    ratio = r_ai / r_hu
    sw, so = {}, {}
    for ch, wsum, ksum in per_chamber_rates():
        s = ksum / wsum if wsum else 0.0
        sw[ch] = s
        so[ch] = (s * ratio) / (s * ratio + (1 - s)) if s else 0.0
    out = {"ratio": ratio, "share_words": sw, "share_occurrences": so,
           "generated_by": "ai_share_of_instrument.py",
           "note": ("share_occurrences applies the machine/human instrument-rate "
                    "ratio to each chamber's word share; it is NOT a separate "
                    "measurement and inherits every caveat above.")}
    p = os.path.join(HERE, "ai_share_by_chamber.json")
    json.dump(out, open(p, "w"), indent=1)
    print(f"\n  wrote {os.path.basename(p)} "
          f"({len(sw)} chambers, ratio {ratio:.2f}x)")


def per_chamber_rates():
    """(chamber, total words, machine words) per chamber, from the estimator."""
    agg = collections.defaultdict(lambda: [0.0, 0.0])
    for ch, era, band, nw, fl, fr in BP.load():
        if era != "prev":
            continue
        agg[ch][0] += nw
        agg[ch][1] += nw * fr
    return [(ch, v[0], v[1]) for ch, v in sorted(agg.items())]


if __name__ == "__main__":
    main()
