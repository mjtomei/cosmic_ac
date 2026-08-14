#!/usr/bin/env python3
"""Is the register climb the SAME people changing, or DIFFERENT people arriving?

THE QUESTION THIS SETTLES

The pre-LLM climb is now replicated across the UK's 20-year series and seven
Canadian provinces. Every explanation for it falls into one of two families,
and they make opposite predictions about a decomposition:

  WITHIN-MEMBER   sitting legislators changed how they speak
                  -> media/audience change, written-first speech, managerial
                     language diffusion, tooling, ambient exposure
  BETWEEN-MEMBER  the chamber's composition changed
                  -> cohort replacement, shifting occupational backgrounds
                     (law/consulting/NGO displacing trades/farming), education,
                     candidate-selection professionalisation

Both are plausible and they are rarely separated, because most corpus studies
only have the aggregate. We have per-member counts in both windows, so the
corpus change decomposes exactly:

    total = within (continuing members' own change, weighted by their words)
          + between (compositional: who is speaking, and how much)

Computed on the province panel, where each province is an independent
replication with its own Hansard office.

The instrument is the Kobak style rate per 1,000 words -- deliberately the RAW
rate here, not the placebo-normalised drift, because the decomposition must
add up to the observed corpus change and a normalised quantity would not.

Usage: python drift_decomposition.py
"""
import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
EARLY = {str(y) for y in range(2006, 2011)}
LATE = {str(y) for y in range(2015, 2020)}
TITLE_RE = re.compile(
    r"^(hon\.?|honourable|l'hon\.?|mr\.?|mrs\.?|ms\.?|miss|dr\.?|mme\.?|m\.|"
    r"madame|monsieur|the)\s+", re.I)
ROLE = re.compile(r"^(premier|deputy premier|leader of the (official )?opposition|"
                  r"minister\b|government house leader|opposition house leader|"
                  r"attorney general|speaker|chair)", re.I)


def norm(s):
    s = s.strip().rstrip(":").strip()
    prev = None
    while prev != s:
        prev = s
        s = TITLE_RE.sub("", s).strip()
    return re.sub(r"\s*\(.*?\)\s*$", "", s).lower()


def main():
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}

    prov = defaultdict(lambda: {"e": defaultdict(lambda: [0, 0]),
                                "l": defaultdict(lambda: [0, 0])})
    for path in sorted(glob.glob(os.path.join(_HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            y = d["date"][:4]
            win = "e" if y in EARLY else "l" if y in LATE else None
            if not win:
                continue
            nm = norm(d.get("speaker", ""))
            if not nm or ROLE.match(nm):
                continue
            t = TOKEN_RE.findall(d["text"].lower())
            cell = prov[d["prov"]][win][nm]
            cell[0] += len(t)
            cell[1] += sum(1 for x in t if x in style)

    print("Decomposition of the corpus-level rise in Kobak style rate")
    print("(rate = style words per 1,000; continuing = spoke in BOTH windows)\n")
    print(f"{'prov':<5s} {'early':>7s} {'late':>7s} {'total':>8s} "
          f"{'WITHIN':>8s} {'BETWEEN':>8s} {'within%':>8s} {'n_cont':>7s}")
    tot_w = tot_b = 0.0
    nprov = 0
    for pv in sorted(prov):
        E, L = prov[pv]["e"], prov[pv]["l"]
        we = sum(v[0] for v in E.values())
        wl = sum(v[0] for v in L.values())
        if we < 500_000 or wl < 500_000:
            print(f"{pv:<5s} (too little data: {we:,} / {wl:,} words)")
            continue
        re_ = sum(v[1] for v in E.values()) / we * 1000
        rl_ = sum(v[1] for v in L.values()) / wl * 1000
        cont = [n for n in set(E) & set(L)
                if E[n][0] >= 3000 and L[n][0] >= 3000]
        if len(cont) < 8:
            print(f"{pv:<5s} (only {len(cont)} continuing members)")
            continue
        # within: continuing members' own rate change, weighted by their
        # late-window words (their share of the new corpus)
        wt = sum(L[n][0] for n in cont)
        within = sum((L[n][1] / L[n][0] - E[n][1] / E[n][0]) * 1000 * L[n][0]
                     for n in cont) / wt
        total = rl_ - re_
        between = total - within
        nprov += 1
        tot_w += within
        tot_b += between
        print(f"{pv:<5s} {re_:>7.2f} {rl_:>7.2f} {total:>+8.2f} "
              f"{within:>+8.2f} {between:>+8.2f} "
              f"{100 * within / total if total else float('nan'):>7.0f}% "
              f"{len(cont):>7d}")
    if nprov:
        print(f"\nmean across {nprov} provinces: within {tot_w / nprov:+.2f}, "
              f"between {tot_b / nprov:+.2f} "
              f"({100 * tot_w / (tot_w + tot_b):.0f}% within)")
        print("\nReading: a large WITHIN share means sitting legislators changed")
        print("how they speak — favouring media/audience, written-first speech,")
        print("managerial-language diffusion or tooling. A large BETWEEN share")
        print("means the chamber's composition changed — favouring cohort")
        print("replacement and shifting occupational backgrounds.")


if __name__ == "__main__":
    main()
