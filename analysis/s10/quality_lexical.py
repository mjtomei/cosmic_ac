#!/usr/bin/env python3
"""S10 quality tier Q1: model-free lexical/information metrics, AI vs human.

Groups (see quality_methods.md): candidate-strata AI/Mixed vs Human
(selection-matched), B-sample AI vs Human (unbiased, small), 2019 control
anchor. Filters: 100-360 words, orig_frac >= 0.5 where known, non-chair.
Cluster bootstrap by speech for the AI-vs-human deltas on the primary set.

Usage: python quality_lexical.py   (writes quality_lexical.csv)
"""
import csv
import json
import math
import random
import re
from collections import defaultdict

random.seed(20260730)
CHAIRS = {"Madam Speaker", "Mr. Speaker", "Mr. Deputy Speaker", "Mr. Chair",
          "Madam Chair", "Her Honour", "His Honour", ""}
NB_PLACES = ["fredericton", "moncton", "saint john", "bathurst", "miramichi",
             "edmundston", "dieppe", "riverview", "quispamsis", "rothesay",
             "campbellton", "oromocto", "shediac", "sackville", "woodstock",
             "dalhousie", "sussex", "caraquet", "shippagan", "tracadie",
             "restigouche", "madawaska", "kennebecasis", "memramcook",
             "tantramar", "kent", "acadie", "fundy", "carleton", "victoria",
             "gloucester", "northumberland", "charlotte", "sunbury", "queens",
             "kings", "albert", "westmorland", "new brunswick", "nouveau-brunswick"]
CONNECTIVES = re.compile(r"\b(because|therefore|however|but|although|"
                         r"nevertheless|consequently|since|whereas)\b", re.I)
FIRST_PERSON = re.compile(r"\b(I|I'm|I've|I'd|I'll|my|mine)\b")
NUMERAL = re.compile(r"\$?\d[\d,.]*%?")
SENT_SPLIT = re.compile(r"[.!?]+\s")


def midcap_rate(text):
    sents = SENT_SPLIT.split(text)
    n = 0
    for s in sents:
        words = s.split()
        for w in words[1:]:
            if w[:1].isupper() and w.lower() not in ("i", "i'm", "i've"):
                n += 1
    return n


def metrics(text, n_words):
    t = text
    low = t.lower()
    sents = [s for s in SENT_SPLIT.split(t) if s.split()]
    toks = low.split()
    bigrams = list(zip(toks, toks[1:]))
    rep = 1 - len(set(bigrams)) / max(1, len(bigrams))
    syll = sum(max(1, len(re.findall(r"[aeiouy]+", w))) for w in toks)
    flesch = (206.835 - 1.015 * (len(toks) / max(1, len(sents)))
              - 84.6 * (syll / max(1, len(toks))))
    return {
        "numerals": len(NUMERAL.findall(t)) / n_words * 100,
        "midcap_ne": midcap_rate(t) / n_words * 100,
        "nb_places": sum(low.count(p) for p in NB_PLACES) / n_words * 100,
        "first_person": len(FIRST_PERSON.findall(t)) / n_words * 100,
        "rep_bigram": rep,
        "connectives": len(CONNECTIVES.findall(t)) / n_words * 100,
        "sent_len": len(toks) / max(1, len(sents)),
        "flesch": flesch,
    }


def summarize(name, rows):
    if not rows:
        return None
    keys = list(rows[0]["m"].keys())
    out = {"group": name, "n": len(rows)}
    for k in keys:
        vals = sorted(r["m"][k] for r in rows)
        out[k] = round(sum(vals) / len(vals), 3)
    return out


def main():
    verdict = {}
    for r in (json.loads(l) for l in open("pangram_results.jsonl")):
        p = (r["response"].get("prediction_short") or "").lower()
        verdict[r["seg_id"]] = (r["stratum"], "ai" if p in ("ai", "mixed") else "human")
    segs = {}
    for path in ("segments_all.jsonl", "segments_60th.jsonl",
                 "segments_59th.jsonl", "segments_61s1.jsonl"):
        for line in open(path):
            s = json.loads(line)
            if s.get("scoreable"):
                segs[s["seg_id"]] = s

    def keep(s):
        return (100 <= s["n_words"] <= 360 and s["speaker"] not in CHAIRS
                and s.get("orig_frac", 1.0) >= 0.5)

    groups = defaultdict(list)
    for sid, (stratum, v) in verdict.items():
        s = segs.get(sid)
        if not s or not keep(s):
            continue
        row = {"sid": sid, "turn": s["turn_id"], "m": metrics(s["text"], s["n_words"])}
        if stratum.startswith("A"):
            groups[f"cand_{v}"].append(row)
        elif stratum.startswith("B"):
            groups[f"B_{v}"].append(row)
        elif stratum.startswith("C"):
            groups["ctl2019"].append(row)

    print(f"{'group':12s} {'n':>4s} " + " ".join(f"{k:>10s}" for k in
          ["numerals", "midcap_ne", "nb_places", "first_person", "rep_bigram",
           "connectives", "sent_len", "flesch"]))
    outrows = []
    for g in ("cand_ai", "cand_human", "B_ai", "B_human", "ctl2019"):
        s = summarize(g, groups[g])
        if s:
            outrows.append(s)
            print(f"{g:12s} {s['n']:>4d} " + " ".join(
                f"{s[k]:>10.3f}" for k in ["numerals", "midcap_ne", "nb_places",
                "first_person", "rep_bigram", "connectives", "sent_len", "flesch"]))

    # cluster bootstrap for primary deltas (cand_ai - cand_human)
    ai, hu = groups["cand_ai"], groups["cand_human"]
    keys = ["numerals", "midcap_ne", "nb_places", "first_person",
            "rep_bigram", "connectives"]
    ai_by_turn = defaultdict(list)
    hu_by_turn = defaultdict(list)
    for r in ai:
        ai_by_turn[r["turn"]].append(r)
    for r in hu:
        hu_by_turn[r["turn"]].append(r)
    at, ht = list(ai_by_turn.values()), list(hu_by_turn.values())
    print("\nprimary deltas (cand AI − cand human), speech-clustered 95% CI:")
    for k in keys:
        deltas = []
        for _ in range(3000):
            a = [r["m"][k] for _ in at for r in at[random.randrange(len(at))]]
            h = [r["m"][k] for _ in ht for r in ht[random.randrange(len(ht))]]
            deltas.append(sum(a) / len(a) - sum(h) / len(h))
        deltas.sort()
        lo, hi = deltas[int(0.025 * len(deltas))], deltas[int(0.975 * len(deltas))]
        point = (sum(r["m"][k] for r in ai) / len(ai)
                 - sum(r["m"][k] for r in hu) / len(hu))
        star = " *" if (lo > 0 or hi < 0) else ""
        print(f"  {k:14s} {point:+.3f}  [{lo:+.3f}, {hi:+.3f}]{star}")

    with open("quality_lexical.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(outrows[0].keys()))
        w.writeheader()
        w.writerows(outrows)
        f.write("# groups per quality_methods.md; 100-360w, orig>=0.5, "
                "non-chair; candidate strata are selection-matched (both "
                "verdicts passed identical filters); B = unbiased sample; "
                "sent_len/flesch descriptive only (C-high circularity)\n")


if __name__ == "__main__":
    main()
