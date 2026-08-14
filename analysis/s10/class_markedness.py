#!/usr/bin/env python3
"""Where in the instrument does each class's excess sit?

THE QUESTION, AND ITS LIMITED STANDING

Register rate by EGP class is an inverted U: routine non-manual and lower
service sit ABOVE the higher service class, and the manual classes sit below
(covariate_study.py). One reading is hypercorrection -- the middle is familiar
with the register but has not mastered it and overuses it for signal, while the
top uses it correctly, meaning sparingly.

If that is what is happening, the middle's excess might concentrate in the
CONSPICUOUS words rather than spreading evenly across the instrument, because
signalling selects for what is noticeable.

THIS IS A CONFIRMATORY TEST ONLY, AND DELIBERATELY SO. Matthew's objection is
that concentration does not follow necessarily from the signalling account --
a speaker steeped in the register would plausibly overuse all of it, and a
signaller might reach for whatever comes to hand rather than what is showy. So:
if the excess concentrates, that is evidence for signalling. If it does not,
NOTHING IS REFUTED. The asymmetry is stated up front so the negative result
cannot later be reported as a disconfirmation.

MEASURING CONSPICUOUSNESS WITHOUT A SECOND INSTRUMENT

Kobak's list carries no salience score -- word, type, part of speech and a
comment, nothing more. So markedness is derived from the corpus itself: how
rare was each style word in these chambers BEFORE the machines arrived? A word
legislators already said constantly (`across`, `key`) is unremarkable however
much its rate rises; a word essentially absent from pre-2022 Hansard is
conspicuous when it appears.

Pre-period is everything on or before 2022-06-30, the study's own control
cutoff, so the baseline is uncontaminated by the thing being measured.

The comparison is each class's word-level profile against CLASS I's, because
class I is the tier the hypercorrection reading says uses the register
correctly. The question is not whether other classes use more of it -- we know
they do -- but whether the surplus is differently distributed.

Usage:
  python class_markedness.py --build    # scan the corpus (~10 min)
  python class_markedness.py            # report
"""
import argparse
import csv
import glob
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "class_word_counts.json")
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402

EGP = ["I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"]
FILES = [("AB", "provinces/ab_education_official.json", "records"),
         ("BC", "provinces/bc_member_education.json", "records"),
         ("MB", "provinces/mb_education_occupation.json", "records"),
         ("NL", "provinces/nl_education_occupation.json", None),
         ("NS", "provinces/ns_member_bios.json", None),
         ("ON", "provinces/on_member_education.json", None),
         ("PE", "provinces/pe_member_education.json", "records"),
         ("SK", "provinces/sk_legislature_bios.json", None)]


def member_class():
    coding = {r["string"]: r for r in
              json.load(open(os.path.join(HERE, "provinces",
                                          "occupation_coding.json")))}
    out = {}
    for pv, rel, key in FILES:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for r in (d[key] if key else d):
            nm = FW.norm(r.get("hansard_speaker_key") or r.get("speaker_key")
                         or r.get("_key") or r.get("name")
                         or r.get("full_name") or "")
            c = coding.get((r.get("prior_occupation") or "").strip())
            if nm and c and c["egp"] in EGP:
                out[(pv, nm)] = c["egp"]
    return out


def build():
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(HERE,
                                              "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}
    cls = member_class()
    print(f"{len(cls)} members carry a class; scanning...")

    # per class: total words, and per style word a count. Plus a pre-period
    # baseline over ALL speakers, which is what markedness is measured against.
    tot = Counter()
    per = defaultdict(Counter)
    pre_tot = 0
    pre = Counter()
    for path in sorted(glob.glob(os.path.join(HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            nm = FW.norm(d.get("speaker", ""))
            if not nm or FW.ROLE.match(nm):
                continue
            toks = FW.TOKEN_RE.findall(d["text"].lower())
            if d["date"][:10] <= "2022-06-30":
                pre_tot += len(toks)
                for t in toks:
                    if t in style:
                        pre[t] += 1
            c = cls.get((d.get("prov"), nm))
            if not c:
                continue
            tot[c] += len(toks)
            for t in toks:
                if t in style:
                    per[c][t] += 1
    json.dump({"tot": tot, "per": {k: dict(v) for k, v in per.items()},
               "pre_tot": pre_tot, "pre": dict(pre)},
              open(CACHE, "w"))
    print(f"wrote {os.path.basename(CACHE)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if a.build:
        return build()
    if not os.path.exists(CACHE):
        raise SystemExit("no cache; run --build first")
    d = json.load(open(CACHE))
    tot, per, pre, pre_tot = d["tot"], d["per"], d["pre"], d["pre_tot"]

    words = sorted(pre, key=lambda w: pre[w])
    # Markedness = rarity in pre-AI Hansard. Split the instrument into thirds
    # by pre-period rate so "conspicuous" is defined before any class is
    # looked at.
    rate_pre = {w: pre[w] / pre_tot * 1e5 for w in words}
    ranked = sorted(words, key=lambda w: rate_pre[w])
    n = len(ranked)
    band = {}
    for i, w in enumerate(ranked):
        band[w] = ("rare" if i < n / 3 else
                   "mid" if i < 2 * n / 3 else "common")

    print("MARKEDNESS: where each class's instrument use sits\n")
    print("  Words split into thirds by how often they appeared in these")
    print("  chambers BEFORE 2022-07. 'rare' = conspicuous when used.\n")
    print(f"  {'class':<8}{'words':>12}" +
          "".join(f"{b:>10}" for b in ("rare", "mid", "common")) +
          f"{'  rare share':>13}")
    base = None
    for c in EGP:
        if c not in per or not tot.get(c):
            continue
        b = Counter()
        for w, k in per[c].items():
            b[band.get(w, "common")] += k
        s = sum(b.values()) or 1
        rates = {x: b[x] / tot[c] * 1e5 for x in ("rare", "mid", "common")}
        share = 100 * b["rare"] / s
        if c == "I":
            base = share
        print(f"  {c:<8}{tot[c]:>12,}" +
              "".join(f"{rates[x]:>10.1f}" for x in ("rare", "mid", "common")) +
              f"{share:>12.2f}%")

    print("\n  RARE-WORD SHARE OF EACH CLASS'S INSTRUMENT USE, vs class I\n")
    for c in EGP:
        if c not in per or not tot.get(c) or c == "I":
            continue
        b = Counter()
        for w, k in per[c].items():
            b[band.get(w, "common")] += k
        s = sum(b.values()) or 1
        share = 100 * b["rare"] / s
        print(f"    {c:<8}{share - base:>+7.2f} pp")
    print("\n  A positive number means that class's instrument use is tilted")
    print("  toward conspicuous words relative to class I. Concentration")
    print("  supports the signalling reading. Its ABSENCE refutes nothing --")
    print("  see the docstring.")


if __name__ == "__main__":
    main()
