#!/usr/bin/env python3
"""One slow pass: cache per-chamber-year word counts, Wikipedia-sign hits, and
per-style-word token counts (only ~407 keys) so the rare set / chamber choice
can be re-plotted instantly. Writes trend_cache.json."""
import csv, json, re
from collections import defaultdict
from tier15_wiki_signs import PATTERNS
from tier15_quarters_speakers import UP

TOKEN_RE = re.compile(r"[a-z']+")
WIKI_RE = re.compile("|".join("(?:%s)" % PATTERNS[n] for n in UP), re.I)
style = [r["word"].lower() for r in csv.DictReader(open("kobak_excess_words.csv"))
         if r["type"] == "style" and r["word"].isalpha()]
styleset = set(style)

CH = [
 ("New Brunswick", ["segments_all.jsonl", "segments_59th.jsonl", "segments_60th.jsonl", "segments_61s1.jsonl"]),
 ("UK Commons",    ["uk/segments_uk_long.jsonl"]),
 ("Canada federal",["ca/segments_ca.jsonl"]),
 ("Ireland",       ["ie/segments_ie.jsonl"]),
 ("US House",      ["us/segments_us_house.jsonl"]),
 ("US Senate",     ["us/segments_us_senate.jsonl"]),
]
cache = {}
for name, paths in CH:
    yr = defaultdict(lambda: {"words": 0, "wiki": 0, "style": defaultdict(int)})
    for path in paths:
        try:
            fh = open(path)
        except FileNotFoundError:
            continue
        for line in fh:
            s = json.loads(line); d = s.get("date", "")
            if not s.get("scoreable") or len(d) < 4 or not d[:4].isdigit():
                continue
            y = int(d[:4])
            if y < 2018 or y > 2026:
                continue
            txt = s["text"]; toks = TOKEN_RE.findall(txt.lower())
            e = yr[y]; e["words"] += len(toks); e["wiki"] += len(WIKI_RE.findall(txt))
            for t in toks:
                if t in styleset:
                    e["style"][t] += 1
    cache[name] = {str(y): {"words": v["words"], "wiki": v["wiki"], "style": dict(v["style"])}
                   for y, v in yr.items()}
    print(name, "years>=100k:", sorted(int(y) for y, v in cache[name].items() if v["words"] >= 100_000))
json.dump({"style": style, "cache": cache}, open("trend_cache.json", "w"))
print("wrote trend_cache.json")
