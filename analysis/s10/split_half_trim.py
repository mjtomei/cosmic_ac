#!/usr/bin/env python3
"""Split-half trim: rank speakers on one half of sittings, measure on the other.

WHY THE FIRST TRIM WASN'T ENOUGH

trim_equalweight.py ranked members by their vocabulary shift and then measured
the shift in the members who were left. That is selection on the outcome:
removing the upper half of any noisy distribution lowers the mean even when
every member shifted identically, so the observed drop is an UPPER BOUND on
what adopters contribute, not an estimate of it.

Fix: use independent data for the two jobs. Sitting dates are split into two
folds by alternating date index within each window. Members are ranked using
fold A only; the corpus effect is then measured on fold B only. Because fold B
played no part in choosing who to delete, a member who merely got a noisy-high
fold-A score is no longer preferentially removed, and the downward bias goes
away.

What each outcome would mean, measured on fold B:

  effect collapses when top fold-A movers are removed
      -> the rise really is concentrated in a subset: adoption, not permeation

  effect largely survives
      -> members outside the top of the distribution are shifting too, which
         is permeation, and it cannot be explained by a few heavy AI users

Usage: python split_half_trim.py   ->  then bash split_half_run.sh
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
MIN_WORDS = 4000          # per speaker, per window, per FOLD
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


def window(date):
    if date <= PRE_MAX:
        return "pre"
    if date >= POST_MIN:
        return "post"
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    style = load_instrument()
    cmds = []
    for code, (path, name) in CORPORA.items():
        if not os.path.exists(path):
            continue

        # fold assignment: alternate sitting dates within each window, so both
        # folds span the whole period and neither is an early/late slice
        dates = {"pre": set(), "post": set()}
        for line in open(path):
            d = json.loads(line)
            w = window(d["date"]) if keep(d) else None
            if w:
                dates[w].add(d["date"])
        fold = {}
        for w in ("pre", "post"):
            for i, dt in enumerate(sorted(dates[w])):
                fold[dt] = "A" if i % 2 == 0 else "B"

        rng = random.Random(int(hashlib.sha1(
            f"{name}splithalf".encode()).hexdigest()[:8], 16))
        cnt = {("A", "pre"): defaultdict(Counter), ("A", "post"): defaultdict(Counter)}
        corpus_pre_A = Counter()
        for line in open(path):
            d = json.loads(line)
            if not keep(d):
                continue
            w = window(d["date"])
            if not w or fold[d["date"]] != "A":
                continue
            toks = TOKEN_RE.findall(d["text"].lower())
            cnt[("A", w)][d.get("person_id") or d.get("speaker", "")].update(toks)
            if w == "pre":
                corpus_pre_A.update(toks)

        excluded = set(style) | {w for w, _ in corpus_pre_A.most_common(120)}
        bucket = defaultdict(list)
        for w, c in corpus_pre_A.items():
            if w in excluded or len(w) < 4 or not w.isalpha():
                continue
            bucket[int(math.log2(c + 1))].append(w)

        def pool_for(b):
            for off in (0, 1, -1, 2, -2, 3, -3, 4, -4):
                if bucket.get(b + off):
                    return bucket[b + off]
            return bucket[max(bucket)]

        pools = [pool_for(int(math.log2(corpus_pre_A[w] + 1))) for w in style]
        placs = [[rng.choice(p) for p in pools] for _ in range(N_PLACEBO_SETS)]

        def eqw(a, b, wa, wb, words):
            used = [w for w in words if a[w] > 0]
            if len(used) < MIN_USED:
                return None
            return sum(math.log(((b[w] + 0.5) / wb) / ((a[w] + 0.5) / wa))
                       for w in used) / len(used)

        pre_A, post_A = cnt[("A", "pre")], cnt[("A", "post")]
        rows = []
        for sp in set(pre_A) & set(post_A):
            a, b = pre_A[sp], post_A[sp]
            wa, wb = sum(a.values()), sum(b.values())
            if wa < MIN_WORDS or wb < MIN_WORDS:
                continue
            ei = eqw(a, b, wa, wb, style)
            if ei is None:
                continue
            ep = [x for x in (eqw(a, b, wa, wb, P) for P in placs) if x is not None]
            if ep:
                rows.append({"speaker": sp, "foldA_excess": ei - sum(ep) / len(ep)})
        rows.sort(key=lambda r: -r["foldA_excess"])
        json.dump(rows, open(f"{OUT}/{code}_foldA_rank.json", "w"), indent=1)
        print(f"{name}: ranked {len(rows)} members on fold A "
              f"(top {rows[0]['foldA_excess']:+.3f}, "
              f"median {rows[len(rows)//2]['foldA_excess']:+.3f})")

        eligible = {r["speaker"] for r in rows}
        for tag, frac in (("sh00", 0.0), ("sh10", 0.10),
                          ("sh25", 0.25), ("sh50", 0.50)):
            drop = {r["speaker"] for r in rows[:int(len(rows) * frac)]}
            outp = f"{OUT}/{code}_{tag}.jsonl"
            n = 0
            with open(outp, "w") as fh:
                for line in open(path):
                    d = json.loads(line)
                    if not keep(d) or fold.get(d["date"]) != "B":
                        continue          # MEASURE ON FOLD B ONLY
                    sp = d.get("person_id") or d.get("speaker", "")
                    if sp in eligible and sp not in drop:
                        fh.write(line)
                        n += 1
            print(f"   {tag}: dropped {len(drop)} of {len(rows)}, "
                  f"fold-B segments kept {n:,}")
            cmds.append(f'python3 run_protocol.py "{name} {tag}" '
                        f'perm_{code}_{tag} {outp}')

    with open("split_half_run.sh", "w") as f:
        f.write("#!/usr/bin/env bash\nset -e\n" + "\n".join(cmds) + "\n")
    os.chmod("split_half_run.sh", 0o755)
    print("\nwrote split_half_run.sh")


if __name__ == "__main__":
    main()
