#!/usr/bin/env python3
"""S10 Tier-1: prompt-leakage regex sweep.

Searches for meta-discourse addressed to a requester rather than an audience
— text that can only plausibly appear if model output was pasted unedited
(see studies-and-work-log.md, S10 Tier 1). Every hit is printed with context
for manual verification; the deliverable is quotable specimens, not a rate.

Usage: python tier1_regex.py SEGMENTS_JSONL [SEGMENTS_JSONL ...]
"""
import json
import re
import sys

PATTERNS = {
    # assistant framing
    "assistant-framing": [
        r"\bcertainly[,!]? here (?:is|'s)\b",
        r"\bhere(?:'s| is) (?:a|an|the|your) (?:draft|revised|rewritten|updated|polished|improved)\b",
        r"\bi hope this helps\b",
        r"\blet me know if you(?:'d| would) like\b",
        r"\bwould you like me to\b",
        r"\bi(?:'d| would) be happy to (?:help|assist|draft|write|revise)\b",
        r"\bfeel free to (?:adjust|modify|tweak|customize)\b",
    ],
    # instruction echoes
    "instruction-echo": [
        r"\bin a (?:more )?professional tone\b",
        r"\ba more natural[,-]? ?flowing version\b",
        r"\bas requested,? here\b",
        r"\brewritten (?:version|for clarity)\b",
        r"\b(?:approximately|around) \d+ words\b",
        r"\bfor your review and approval\b",
    ],
    # self-identification
    "self-id": [
        r"\bas an ai\b", r"\blanguage model\b", r"\bi am an ai\b",
        r"\bi cannot (?:browse|access) the internet\b",
    ],
    # unfilled placeholders
    "placeholder": [
        r"\[(?:your |insert |the )?(?:name|title|date|riding|constituency|member|city|town|organization)[^\]]{0,30}\]",
        r"\bXX{1,3}\b",
    ],
    # markdown artifacts surviving into the record
    "markdown": [r"\*\*[^*]{2,60}\*\*", r"```", r"(?:^|\s)#{2,4}\s+\w"],
}

COMPILED = [(cat, re.compile(pat, re.I)) for cat, pats in PATTERNS.items()
            for pat in pats]


def main():
    hits = []
    n_segs = 0
    n_words = 0
    for path in sys.argv[1:]:
        for line in open(path):
            s = json.loads(line)
            n_segs += 1
            n_words += s["n_words"]
            for cat, rx in COMPILED:
                for m in rx.finditer(s["text"]):
                    a, b = max(0, m.start() - 110), min(len(s["text"]), m.end() + 110)
                    hits.append({
                        "corpus": path, "category": cat, "pattern": rx.pattern,
                        "seg_id": s["seg_id"], "date": s["date"],
                        "speaker": s["speaker"], "match": m.group(0),
                        "context": s["text"][a:b],
                    })
    print(f"# scanned {n_segs} segments, {n_words:,} words "
          f"from {len(sys.argv) - 1} file(s); {len(hits)} hits\n")
    for h in hits:
        print(f"[{h['category']}] {h['date']} | {h['speaker']} | {h['seg_id']} "
              f"({h['corpus']})")
        print(f"  match: {h['match']!r}")
        print(f"  ...{h['context']}...")
        print()
    with open("tier1_hits.jsonl", "w") as f:
        for h in hits:
            f.write(json.dumps(h, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
