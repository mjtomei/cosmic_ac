#!/usr/bin/env python3
"""S10 Tier-1.5: Wikipedia "Signs of AI writing" lexicon, rate-compared.

Patterns from Wikipedia:Signs_of_AI_writing (WikiProject AI Cleanup;
fetched 2026-07-29), curated to what is machine-checkable in SPOKEN,
professionally edited legislative text (wiki-markup and citation categories
dropped). None of these is evidence alone — political oratory has real
base rates for most (rule-of-three is Cicero, not ChatGPT). The design is
per-pattern rate per 100k words, 2019 control vs 2025-26, with Poisson
intervals: the *shift* is the statistic. Punctuation habits are
Hansard-editor-mediated (house style) — em-dash row is included but flagged.

Usage: python tier15_wiki_signs.py   (writes tier15_rates.csv)
"""
import csv
import json
import math
import re

PATTERNS = {
    # AI-vocabulary words (page's cross-model list)
    "delve": r"\bdelv(?:e|es|ed|ing)\b",
    "tapestry": r"\btapestry\b",
    "testament": r"\btestament\b",
    "underscore-v": r"\bunderscor(?:e|es|ed|ing)\b",
    "pivotal": r"\bpivotal\b",
    "crucial": r"\bcrucial\b",
    "meticulous": r"\bmeticulous(?:ly)?\b",
    "intricate": r"\bintricac(?:y|ies)\b|\bintricate\b",
    "robust": r"\brobust\b",
    "foster-v": r"\bfoster(?:s|ed|ing)?\b",
    "garner": r"\bgarner(?:s|ed|ing)?\b",
    "showcase": r"\bshowcas(?:e|es|ed|ing)\b",
    "boasts": r"\bboasts\b",
    "landscape-abstract": r"\b(?:evolving|changing|competitive|economic|political|digital) landscape\b",
    "vibrant": r"\bvibrant\b",
    "enduring": r"\benduring\b",
    "interplay": r"\binterplay\b",
    "bolster": r"\bbolster(?:s|ed|ing)?\b",
    "align-with": r"\balign(?:s|ed|ing)? with\b",
    "resonate-with": r"\bresonat(?:e|es|ed|ing) with\b",
    # significance/legacy emphasis
    "stands-serves-as": r"\b(?:stands|serves) as an?\b",
    "testament-to": r"\b(?:is|as) a testament to\b",
    "setting-the-stage": r"\bsetting the stage for\b",
    "turning-point": r"\bkey turning point\b",
    "indelible-mark": r"\bindelible mark\b",
    "deeply-rooted": r"\bdeeply rooted\b",
    "focal-point": r"\bfocal point\b",
    "rich-heritage": r"\brich (?:cultural )?heritage\b",
    "natural-beauty": r"\bnatural beauty\b",
    "nestled": r"\bnestled\b",
    "in-the-heart-of": r"\bin the heart of\b",
    "groundbreaking": r"\bgroundbreaking\b",
    "renowned": r"\brenowned\b",
    "diverse-array": r"\bdiverse (?:array|range) of\b",
    "valuable-insights": r"\bvaluable insights?\b",
    "commitment-to": r"\b(?:unwavering|ongoing|steadfast) (?:commitment|dedication) to\b",
    # constructions
    "not-only-but": r"\bnot only\b[^.;:]{0,60}\bbut(?: also)?\b",
    "not-just-its": r"\bnot just\b[^.;:]{0,50}\b(?:it is|it's|but)\b",
    "participle-tail": r", (?:highlighting|underscoring|emphasizing|reflecting|ensuring|fostering|showcasing|demonstrating) [^.]{0,70}\.",
    "additionally-start": r"(?:^|\. )Additionally,",
    # punctuation (editor-mediated; weak)
    "em-dash": r"—",
}


def count_all(texts):
    joined = "\n".join(texts)
    words = len(joined.split())
    counts = {}
    for name, pat in PATTERNS.items():
        counts[name] = len(re.findall(pat, joined, re.I if name != "additionally-start" else 0))
    return counts, words


def poisson_ci(k, scale):
    # Garwood-ish approx via sqrt; fine at these counts
    lo = max(0.0, (math.sqrt(k) - 1.96 / 2) ** 2) if k else 0.0
    hi = (math.sqrt(k) + 1.96 / 2) ** 2 if k else 3.69
    return lo * scale, hi * scale


def main():
    segs = [json.loads(l) for l in open("segments_all.jsonl")]
    segs = [s for s in segs if s.get("scoreable")]
    ctl = [s["text"] for s in segs if s["date"].startswith("2019")]
    new = [s["text"] for s in segs if s["date"][:4] in ("2025", "2026")]
    c_counts, c_words = count_all(ctl)
    n_counts, n_words = count_all(new)
    c_scale = 1e5 / c_words
    n_scale = 1e5 / n_words

    rows = []
    for name in PATTERNS:
        ck, nk = c_counts[name], n_counts[name]
        cr, nr = ck * c_scale, nk * n_scale
        c_lo, c_hi = poisson_ci(ck, c_scale)
        n_lo, n_hi = poisson_ci(nk, n_scale)
        ratio = (nr / cr) if cr else float("inf") if nr else 1.0
        sep = (n_lo > c_hi) or (c_lo > n_hi)   # CI-separated shift
        rows.append({"pattern": name, "ctl_n": ck, "ctl_per100k": round(cr, 2),
                     "new_n": nk, "new_per100k": round(nr, 2),
                     "ratio_new_over_ctl": round(ratio, 2) if ratio != float("inf") else "inf",
                     "ci_separated": sep})
    rows.sort(key=lambda r: -(r["new_per100k"] / (r["ctl_per100k"] + 0.5)))

    with open("tier15_rates.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        f.write(f"# control {c_words:,} words (2019), corpus {n_words:,} words "
                f"(2025-26); patterns from Wikipedia:Signs_of_AI_writing "
                f"(fetched 2026-07-29); em-dash is Hansard-house-style mediated\n")

    print(f"control {c_words:,}w vs 2025-26 {n_words:,}w")
    print(f"{'pattern':22s} {'2019/100k':>10s} {'2025/100k':>10s} {'ratio':>7s} sep")
    for r in rows:
        if r["ctl_n"] + r["new_n"] == 0:
            continue
        print(f"{r['pattern']:22s} {r['ctl_per100k']:>10} {r['new_per100k']:>10} "
              f"{str(r['ratio_new_over_ctl']):>7s} {'*' if r['ci_separated'] else ''}")


if __name__ == "__main__":
    main()
