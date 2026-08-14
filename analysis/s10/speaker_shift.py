#!/usr/bin/env python3
"""Is the vocabulary shift a few heavy AI users, or everybody moving a little?

WHY THIS TEST EXISTS

Every detector-based argument for permeation has the same hole: if members
run machine drafts through a humanizer, a "Human" verdict means the detector
lost, not that a person wrote it. So the permeation claim cannot rest on the
detector. This test does not use one.

It uses a structural prediction that separates the two stories regardless of
whether any detector can see the difference:

  DRAFTING (humanized or not) is adoption by a SUBSET. Adopters' AI-vocabulary
  rate jumps; non-adopters are unchanged. The per-speaker shift distribution
  should be near zero for most members with a right tail of adopters, and the
  corpus effect should collapse when the tail is removed.

  PERMEATION is a shift in the ambient register that everyone reads, hears and
  absorbs -- including members who never touch a model. The whole distribution
  should translate: the MEDIAN member moves, the lower quartile moves, and the
  corpus effect should SURVIVE deleting the most-shifted speakers.

Both are measured against each speaker's own frequency-matched placebo shift,
because all vocabulary drifts and the question is only whether the instrument
drifts more.

The decisive output is the trimmed corpus: segment files with the top decile
and top quartile of shifters deleted, to be run through the frozen protocol
unmodified. If the effect survives removal of the top 25% of movers, no
minority of adopters can account for it.

Usage: python speaker_shift.py            # stats + write trimmed corpora
       bash speaker_shift_run.sh          # frozen protocol on the trims
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
MIN_WORDS = 3000          # per speaker, per window, for a stable rate
N_PLACEBO_SETS = 40       # per-speaker placebo shift is averaged over these
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
    if not d.get("scoreable") or d.get("translated"):
        return False
    return d.get("orig_frac", 1.0) > 0.5


def speaker_key(d):
    return d.get("person_id") or d.get("speaker", "")


def quantile(v, q):
    if not v:
        return float("nan")
    s = sorted(v)
    i = q * (len(s) - 1)
    lo = int(i)
    return s[lo] if lo + 1 >= len(s) else s[lo] + (i - lo) * (s[lo + 1] - s[lo])


def analyse(code, path, name, style):
    rng = random.Random(int(hashlib.sha1(f"{name}shift".encode()).hexdigest()[:8], 16))
    pre = defaultdict(Counter)
    post = defaultdict(Counter)
    corpus_pre = Counter()
    for line in open(path):
        d = json.loads(line)
        if not keep(d):
            continue
        if d["date"] <= PRE_MAX:
            tgt = pre
        elif d["date"] >= POST_MIN:
            tgt = post
        else:
            continue
        toks = TOKEN_RE.findall(d["text"].lower())
        tgt[speaker_key(d)].update(toks)
        if tgt is pre:
            corpus_pre.update(toks)

    # frequency-matched placebo sets, built once from the corpus pre-period
    sset = set(style)
    excluded = sset | {w for w, _ in corpus_pre.most_common(120)}
    bucket = defaultdict(list)
    for w, n in corpus_pre.items():
        if w in excluded or len(w) < 4 or not w.isalpha():
            continue
        bucket[int(math.log2(n + 1))].append(w)

    def pool_for(b):
        for off in (0, 1, -1, 2, -2, 3, -3, 4, -4):
            if bucket.get(b + off):
                return bucket[b + off]
        return bucket[max(bucket)]

    pools = [pool_for(int(math.log2(corpus_pre[w] + 1))) for w in style]
    placebos = [[rng.choice(p) for p in pools] for _ in range(N_PLACEBO_SETS)]

    def rate(c, words, tot):
        return (sum(c[w] for w in words) + 0.5) / max(tot, 1)

    rows = []
    for sp in set(pre) & set(post):
        wpre, wpost = sum(pre[sp].values()), sum(post[sp].values())
        if wpre < MIN_WORDS or wpost < MIN_WORDS:
            continue
        inst = math.log(rate(post[sp], sset, wpost) / rate(pre[sp], sset, wpre))
        plac = sum(math.log(rate(post[sp], set(P), wpost) / rate(pre[sp], set(P), wpre))
                   for P in placebos) / len(placebos)
        rows.append({"speaker": sp, "w_pre": wpre, "w_post": wpost,
                     "instrument_shift": inst, "placebo_shift": plac,
                     "excess": inst - plac})
    rows.sort(key=lambda r: -r["excess"])

    ex = [r["excess"] for r in rows]
    pos = sum(e > 0 for e in ex)
    print(f"\n=== {name} ===")
    print(f"  {len(rows)} members with >={MIN_WORDS:,} words in BOTH windows")
    print(f"  excess shift (instrument minus own placebo), per member:")
    for q in (0.10, 0.25, 0.50, 0.75, 0.90):
        print(f"    p{int(q*100):02d} {quantile(ex, q):+.4f}")
    print(f"  members shifting positive: {pos}/{len(rows)} = {pos/len(rows):.1%}")
    # binomial tail against 50% -- if permeation, near-universal
    n = len(rows)
    p_bin = sum(math.comb(n, k) for k in range(pos, n + 1)) / 2 ** n if n < 1000 else 0.0
    print(f"    sign test vs 50%: p = {p_bin:.2e}" if p_bin else
          "    sign test vs 50%: p < 1e-300")
    top = sorted(ex, reverse=True)
    share = sum(top[:max(1, n // 10)]) / sum(t for t in top if t > 0)
    print(f"  share of total positive shift held by top decile: {share:.1%} "
          f"(would be ~10% if uniform, ~100% if a few adopters)")
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    style = load_instrument()
    cmds = []
    for code, (path, name) in CORPORA.items():
        if not os.path.exists(path):
            print(f"skip {code}: {path} missing")
            continue
        rows = analyse(code, path, name, style)
        json.dump(rows, open(f"{OUT}/{code}_speaker_shift.json", "w"), indent=1)

        # trimmed corpora: delete the most-shifted speakers entirely
        for tag, frac in (("trim10", 0.10), ("trim25", 0.25)):
            drop = {r["speaker"] for r in rows[:int(len(rows) * frac)]}
            keepers = {r["speaker"] for r in rows} - drop
            outp = f"{OUT}/{code}_{tag}.jsonl"
            n = 0
            with open(outp, "w") as fh:
                for line in open(path):
                    d = json.loads(line)
                    if keep(d) and speaker_key(d) in keepers:
                        fh.write(line)
                        n += 1
            print(f"  {tag}: dropped {len(drop)} speakers, kept {n:,} segments")
            cmds.append(f'python3 run_protocol.py "{name} {tag}" '
                        f'perm_{code}_{tag} {outp}')

    with open("speaker_shift_run.sh", "w") as f:
        f.write("#!/usr/bin/env bash\n# Frozen protocol on speaker-trimmed corpora.\nset -e\n")
        f.write("\n".join(cmds) + "\n")
    os.chmod("speaker_shift_run.sh", 0o755)
    print("\nwrote speaker_shift_run.sh")


if __name__ == "__main__":
    main()
