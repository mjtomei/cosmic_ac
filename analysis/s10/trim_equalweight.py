#!/usr/bin/env python3
"""Speaker trims ranked by the EQUAL-WEIGHT statistic, which was the bug.

speaker_shift.py ranked members by a pooled per-speaker rate ratio and then
deleted the top movers. But pooled and equal-weight per-speaker shifts
disagree badly (Canada: 22.5% vs 53.1% of members positive), and the corpus
primary is the equal-weight one. So the first trim deleted the wrong members
-- which is exactly why the Ireland effect did not move when they were
removed. That is not evidence of robustness, it is evidence of a mis-aimed
trim, and it has to be redone before the result means anything.

Here the ranking statistic matches the corpus statistic: each member's mean
per-word log fold-change over the instrument words they actually used in the
pre-period, minus the same quantity over frequency-matched placebo words.
Delete the top movers by THAT, and the question becomes the one we want:
does the corpus effect survive removing the members who most drove it?

Usage: python trim_equalweight.py   ->  then bash trim_ew_run.sh
"""
import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
PRE_MAX = "2022-12-31"
POST_MIN = "2024-01-01"
MIN_WORDS = 8000
N_PLACEBO_SETS = 10
MIN_USED = 20
OUT = "permeation"

CORPORA = {
    "ie": ("ie/segments_ie_en.jsonl", "Dail Eireann"),
    "ca": ("ca/segments_ca_en.jsonl", "Canada House of Commons"),
    "uk": ("uk/segments_uk.jsonl", "UK House of Commons"),
}


def load_instrument(path="kobak_excess_words.csv"):
    return sorted({r["word"].lower() for r in csv.DictReader(open(path))
                   if r["type"] == "style" and r["word"].isalpha()})


def keep(d):
    return (d.get("scoreable") and not d.get("translated")
            and d.get("orig_frac", 1.0) > 0.5)


def main():
    os.makedirs(OUT, exist_ok=True)
    style = load_instrument()
    cmds = []
    for code, (path, name) in CORPORA.items():
        if not os.path.exists(path):
            continue
        rng = random.Random(int(hashlib.sha1(
            f"{name}ewtrim".encode()).hexdigest()[:8], 16))
        pre, post = defaultdict(Counter), defaultdict(Counter)
        corpus_pre = Counter()
        for line in open(path):
            d = json.loads(line)
            if not keep(d):
                continue
            if d["date"] <= PRE_MAX:
                tgt, isp = pre, True
            elif d["date"] >= POST_MIN:
                tgt, isp = post, False
            else:
                continue
            toks = TOKEN_RE.findall(d["text"].lower())
            tgt[d.get("person_id") or d.get("speaker", "")].update(toks)
            if isp:
                corpus_pre.update(toks)

        excluded = set(style) | {w for w, _ in corpus_pre.most_common(120)}
        bucket = defaultdict(list)
        for w, c in corpus_pre.items():
            if w in excluded or len(w) < 4 or not w.isalpha():
                continue
            bucket[int(math.log2(c + 1))].append(w)

        def pool_for(b):
            for off in (0, 1, -1, 2, -2, 3, -3, 4, -4):
                if bucket.get(b + off):
                    return bucket[b + off]
            return bucket[max(bucket)]

        pools = [pool_for(int(math.log2(corpus_pre[w] + 1))) for w in style]
        placs = [[rng.choice(p) for p in pools] for _ in range(N_PLACEBO_SETS)]

        def eqw(a, b, wa, wb, words):
            used = [w for w in words if a[w] > 0]
            if len(used) < MIN_USED:
                return None
            return sum(math.log(((b[w] + 0.5) / wb) / ((a[w] + 0.5) / wa))
                       for w in used) / len(used)

        rows = []
        for sp in set(pre) & set(post):
            a, b = pre[sp], post[sp]
            wa, wb = sum(a.values()), sum(b.values())
            if wa < MIN_WORDS or wb < MIN_WORDS:
                continue
            ei = eqw(a, b, wa, wb, style)
            if ei is None:
                continue
            ep = [x for x in (eqw(a, b, wa, wb, P) for P in placs) if x is not None]
            if not ep:
                continue
            rows.append({"speaker": sp, "excess": ei - sum(ep) / len(ep),
                         "w_pre": wa, "w_post": wb})
        rows.sort(key=lambda r: -r["excess"])
        json.dump(rows, open(f"{OUT}/{code}_speaker_shift_ew.json", "w"), indent=1)
        print(f"{name}: {len(rows)} members ranked by equal-weight excess "
              f"(top {rows[0]['excess']:+.3f}, median "
              f"{rows[len(rows)//2]['excess']:+.3f}, bottom {rows[-1]['excess']:+.3f})")

        eligible = {r["speaker"] for r in rows}
        for tag, frac in (("ewtrim10", 0.10), ("ewtrim25", 0.25), ("ewtrim50", 0.50)):
            drop = {r["speaker"] for r in rows[:int(len(rows) * frac)]}
            outp = f"{OUT}/{code}_{tag}.jsonl"
            n = 0
            with open(outp, "w") as fh:
                for line in open(path):
                    d = json.loads(line)
                    if not keep(d):
                        continue
                    sp = d.get("person_id") or d.get("speaker", "")
                    # keep only ranked members, minus the top movers, so the
                    # trimmed and untrimmed corpora differ ONLY by the drop
                    if sp in eligible and sp not in drop:
                        fh.write(line)
                        n += 1
            print(f"   {tag}: dropped {len(drop)}, kept {n:,} segments")
            cmds.append(f'python3 run_protocol.py "{name} {tag}" '
                        f'perm_{code}_{tag} {outp}')
        # the untrimmed baseline over the SAME eligible members, so the
        # comparison is trim-vs-no-trim and not trim-vs-whole-corpus
        outp = f"{OUT}/{code}_ewtrim00.jsonl"
        n = 0
        with open(outp, "w") as fh:
            for line in open(path):
                d = json.loads(line)
                if keep(d) and (d.get("person_id") or d.get("speaker", "")) in eligible:
                    fh.write(line)
                    n += 1
        print(f"   ewtrim00 (baseline): kept {n:,} segments")
        cmds.insert(len(cmds) - 3, f'python3 run_protocol.py "{name} ewtrim00" '
                                   f'perm_{code}_ewtrim00 {outp}')

    with open("trim_ew_run.sh", "w") as f:
        f.write("#!/usr/bin/env bash\nset -e\n" + "\n".join(cmds) + "\n")
    os.chmod("trim_ew_run.sh", 0o755)
    print("\nwrote trim_ew_run.sh")


if __name__ == "__main__":
    main()
