#!/usr/bin/env python3
"""Protocol v1.1 — the adversarial review's three statistical findings, applied.

v1.0 (run_protocol.py) is NOT deleted and its results are NOT withdrawn. This
is a pre-specified sensitivity analysis run alongside it, and both are
reported. The review found three defects in v1.0's null and estimand; each is
fixed here, and the point of running both is to show exactly what each fix
costs.

  F3  PRESENT-IN-BOTH. v1.0 scores all 407 instrument words, including words
      that appear in neither period. Those contribute a constant positive
      term from the +0.5 smoothing (F9), and because Kobak's 462 CONTENT
      words are mostly biomedical jargon absent from Hansard, that artifact
      is large enough that v1.0 cannot distinguish the style list from the
      content list in Canada or the UK. Restricting both instrument and
      placebo pool to words present in both periods removes it.

  F2  DISPERSION-MATCHED PLACEBO. v1.0 matches placebo words to instrument
      words on pre-period frequency only. Corpus linguistics treats
      dispersion as co-equal with frequency (Gries IJCL 2008; Egbert & Biber
      Corpora 2019), and a pool full of bursty topic words decays faster
      between windows, depressing the placebo median and inflating every
      excess. Here placebos are matched on BOTH axes: log2 frequency bucket
      x log2 sitting-count bin, nearest-cell fallback.

  F3b CONTENT-WORD NEGATIVE CONTROL. Kobak's team annotated all 900 words
      content-vs-style blinded to year, precisely so the two could be
      separated. The content list is the field's canonical topic-churn
      control and v1.0 never ran it. It is run here in every chamber. The
      instrument only means what we claim if style rises and content does not.

Usage: python run_protocol_v11.py CORPUS_NAME OUT_PREFIX SEGMENTS.jsonl [...]
"""
import csv
import hashlib
import json
import math
import os
import random
import re
import sys
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
PRE_MAX = "2022-12-31"
POST_MIN = "2024-01-01"
N_PLACEBO = 1000


_HERE = os.path.dirname(os.path.abspath(__file__))


def load_lists(path=None):
    path = path or os.path.join(_HERE, "kobak_excess_words.csv")
    style, content = set(), set()
    for r in csv.DictReader(open(path)):
        w = r["word"].lower()
        if not w.isalpha():
            continue
        (style if r["type"] == "style" else content).add(w)
    return sorted(style), sorted(content)


def main():
    name, prefix, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    seed = int(hashlib.sha1((name + "v11").encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    style, content = load_lists()

    pre_c, post_c = Counter(), Counter()
    pre_w = post_w = 0
    # dispersion over pre-period sitting dates; `last` avoids holding a set
    # per word, which does not fit for the larger corpora
    disp = Counter()
    last = {}
    pre_dates = set()
    for path in files:
        for line in open(path):
            s = json.loads(line)
            if not s.get("scoreable"):
                continue
            d = s["date"]
            toks = TOKEN_RE.findall(s["text"].lower())
            if d <= PRE_MAX:
                pre_c.update(toks)
                pre_w += len(toks)
                pre_dates.add(d)
                for w in set(toks):
                    if last.get(w) != d:
                        disp[w] += 1
                        last[w] = d
            elif d >= POST_MIN:
                post_c.update(toks)
                post_w += len(toks)
    n_dates = max(len(pre_dates), 1)
    print(f"[{name}] v1.1 seed={seed}  pre {pre_w:,}w  post {post_w:,}w  "
          f"{n_dates} pre sittings", flush=True)

    def present(ws):
        return [w for w in ws if pre_c[w] > 0 and post_c[w] > 0]

    def logratio(w):
        return math.log(((post_c[w] + 0.5) / post_w) /
                        ((pre_c[w] + 0.5) / pre_w))

    def cell(w):
        """(frequency bucket, dispersion bin) — the two matching axes."""
        return (int(math.log2(pre_c[w] + 1)),
                int(math.log2(disp.get(w, 0) + 1)))

    # placebo pool: present in both, not in either instrument, not top-120
    both = set(style) | set(content)
    excluded = both | {w for w, _ in pre_c.most_common(120)}
    pool = defaultdict(list)
    for w, n in pre_c.items():
        if w in excluded or len(w) < 4 or not w.isalpha() or post_c[w] == 0:
            continue
        pool[cell(w)].append(w)

    def pool_for(c):
        """Nearest cell on both axes, expanding rings."""
        if pool.get(c):
            return pool[c]
        for r in range(1, 8):
            best = None
            for df in range(-r, r + 1):
                for dd in range(-r, r + 1):
                    if max(abs(df), abs(dd)) != r:
                        continue
                    cand = pool.get((c[0] + df, c[1] + dd))
                    if cand and (best is None or len(cand) > len(best)):
                        best = cand
            if best:
                return best
        return max(pool.values(), key=len)

    out = {"corpus": name, "protocol": "v1.1", "seed": seed,
           "pre_words": pre_w, "post_words": post_w,
           "pre_sittings": n_dates, "n_placebo": N_PLACEBO, "arms": {}}

    for label, words in (("style", style), ("content", content)):
        ws = present(words)
        if len(ws) < 30:
            print(f"  {label}: only {len(ws)} present in both — skipped")
            continue
        real = sum(logratio(w) for w in ws) / len(ws)
        pools = [pool_for(cell(w)) for w in ws]
        draws = sorted(sum(logratio(rng.choice(p)) for p in pools) / len(pools)
                       for _ in range(N_PLACEBO))
        med = draws[len(draws) // 2]
        ex = sum(1 for d in draws if d >= real)
        print(f"  {label:8s} n={len(ws):3d}/{len(words):3d} present  "
              f"primary {real:+.4f}  placebo med {med:+.4f}  "
              f"EXCESS {real - med:+.4f}  p = {ex}/{N_PLACEBO}", flush=True)
        out["arms"][label] = {
            "n_words_total": len(words), "n_words_present": len(ws),
            "primary_mean_logFC": round(real, 5),
            "placebo_median": round(med, 5),
            "placebo_max": round(draws[-1], 5),
            "excess": round(real - med, 5),
            "p": ex / N_PLACEBO}

    if "style" in out["arms"] and "content" in out["arms"]:
        gap = out["arms"]["style"]["excess"] - out["arms"]["content"]["excess"]
        out["style_minus_content"] = round(gap, 5)
        print(f"  STYLE - CONTENT = {gap:+.4f}  "
              f"(the instrument only means what we claim if this is clearly > 0)",
              flush=True)

    json.dump(out, open(f"{prefix}_v11.json", "w"), indent=1)
    print(f"wrote {prefix}_v11.json", flush=True)


if __name__ == "__main__":
    main()
