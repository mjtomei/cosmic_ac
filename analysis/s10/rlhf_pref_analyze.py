#!/usr/bin/env python3
"""Is the register that leaked into Hansard specifically the ALIGNMENT register?

Four tests on the paired base-vs-instruct generations.

  rlhf_pref(w) = log[ rate of w in INSTRUCT output / rate of w in BASE output ]

Both models saw identical prompts, so a word's corpus frequency cancels: this
is a paired contrast, unlike the study's withdrawn ai_pref test, which
compared model output against a human corpus and turned out to be 92% a rarity
index.

  TEST A  Is the Kobak instrument itself an alignment artifact?
          Mean rlhf_pref for the style words vs frequency-matched control
          words. If style words are systematically what post-training ADDS,
          then "AI vocabulary" is more precisely "assistant vocabulary".

          THE CONTROL POOL MUST BE SYMMETRIC. An earlier version drew control
          candidates from base_c alone and bucketed them on
          int(log2(base_c[w]+1)) -- i.e. on the ratio's own denominator. Two
          things went wrong. A control word with zero base count became
          structurally impossible (bucket 0 was empty), while 57 of the 212
          admitted style words -- 26.9% -- have zero base count and carry mean
          pref +1.4471; they were matched against controls with base count 1-2.
          And selecting on the denominator drags the control median to -0.4525
          where a symmetric control sits at ~0.
          The result was an excess of +0.8797 against a true value near +0.42.
          Fed 30 random word lists matched only on frequency, the old procedure
          returned +0.454 (sd 0.068, 30/30 positive) -- a pedestal for lists
          with no special property at all. The symmetric version returns +0.012
          (17/30 positive), as a null should.
          Candidates now come from set(base_c) | set(inst_c) and are bucketed
          on the COMBINED count. The null pedestal is printed alongside the
          estimate so the reader can see what the procedure returns on noise.

  TEST B  Does rlhf_pref predict which words actually rose in Hansard, once
          pre-period frequency is stratified out? This is the replacement for
          the withdrawn mechanism test, run with the correction that killed it.

  TEST C  Does it beat the rival explanation? llm_pref compares BASE output to
          human Hansard -- generic "machine text", no alignment involved. If
          rlhf_pref predicts the Hansard shift and llm_pref does not, the
          leaked register is the post-training layer, not model text per se.

  TEST D  Descriptive: what does post-training actually add? If the top of the
          rlhf_pref ranking is hedges, affirmations and boosters, that is the
          sycophancy signature in concrete words.

Usage: python rlhf_pref_analyze.py
"""
import csv
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
GEN = "rlhf_gen"
# Instruct models sometimes ANALYSE the prompt instead of continuing it
# ("This passage appears to be from a parliamentary debate..."). That is an
# instruction-following artifact, not register, and it inflates exactly the
# meta-vocabulary that would contaminate TEST A. Generations whose opening
# looks meta are dropped from BOTH members of the pair, so the pairing holds.
META = re.compile(r"\b(this (text|passage|speech|statement|excerpt)|the speaker|"
                  r"appears to be|it seems that this|summary|analysis|"
                  r"in this (text|passage)|here is|sure[,!]|I cannot|as an ai|"
                  r"does this answer)\b", re.I)
SRC = ["ie/segments_ie_en.jsonl", "uk/segments_uk.jsonl", "ca/segments_ca_en.jsonl"]
FAMS = ["llama3", "qwen3", "mistral"]
_HERE = os.path.dirname(os.path.abspath(__file__))

# hand-grouped markers for TEST D only (descriptive, not used in any test)
SYCO = {"hedge": {"perhaps", "arguably", "somewhat", "generally", "typically",
                  "often", "might", "could", "may", "seems", "suggests",
                  "potentially", "relatively", "fairly", "largely"},
        "affirm": {"important", "crucial", "vital", "essential", "significant",
                   "valuable", "meaningful", "compelling", "profound", "key",
                   "notable", "remarkable"},
        "structure": {"moreover", "furthermore", "additionally", "however",
                      "overall", "ultimately", "notably", "importantly",
                      "consequently", "therefore"},
        "constructive": {"ensure", "foster", "enhance", "promote", "support",
                         "strengthen", "advance", "facilitate", "empower",
                         "underscore", "highlight", "emphasise", "emphasize"}}


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def counts(texts):
    c = Counter()
    n = 0
    for t in texts:
        toks = TOKEN_RE.findall(t.lower())
        c.update(toks)
        n += len(toks)
    return c, n


def rank(v):
    s = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
            j += 1
        a = (i + j) / 2 + 1
        for k in range(i, j + 1):
            rk[s[k]] = a
        i = j + 1
    return rk


def pear(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return num / den if den else float("nan")


def spear(x, y):
    return pear(rank(x), rank(y))


def partial(x, y, z):
    rx, ry, rz = rank(x), rank(y), rank(z)

    def resid(t):
        n = len(rz)
        mz, mt = sum(rz) / n, sum(t) / n
        b = sum((a - mz) * (c - mt) for a, c in zip(rz, t)) / \
            sum((a - mz) ** 2 for a in rz)
        return [c - (mt + b * (a - mz)) for a, c in zip(rz, t)]
    return pear(resid(rx), resid(ry))


def strat_perm(pred, out, strat, rng, n=10000, ntile=5):
    """Permute pred WITHIN contiguous strata of `strat`, preserving the
    frequency structure that a global shuffle destroys."""
    real = spear(pred, out)
    order = sorted(range(len(pred)), key=lambda i: strat[i])
    size = max(1, len(order) // ntile)
    groups = [order[i * size:(i + 1) * size] for i in range(ntile)]
    groups[-1] += order[ntile * size:]
    p = list(pred)
    ex = 0
    for _ in range(n):
        for g in groups:
            v = [p[i] for i in g]
            rng.shuffle(v)
            for i, x in zip(g, v):
                p[i] = x
        if spear(p, out) >= real:
            ex += 1
    return real, ex / n


def main():
    style = load_style()
    rng = random.Random(20260802)

    fams = [f for f in FAMS if os.path.exists(f"{GEN}/{f}_base.json")
            and os.path.exists(f"{GEN}/{f}_instruct.json")]
    if not fams:
        raise SystemExit("no completed base/instruct pairs in rlhf_gen/")
    print(f"families available: {', '.join(fams)}\n")

    base_c, base_n = Counter(), 0
    inst_c, inst_n = Counter(), 0
    per_fam = {}
    for f in fams:
        bg = json.load(open(f"{GEN}/{f}_base.json"))
        ig = json.load(open(f"{GEN}/{f}_instruct.json"))
        keep = [k for k in range(min(len(bg), len(ig)))
                if not META.search(ig[k][:300]) and not META.search(bg[k][:300])]
        print(f"  {f}: kept {len(keep)}/{len(ig)} prompt pairs after meta filter")
        bg = [bg[k] for k in keep]
        ig = [ig[k] for k in keep]
        bc, bn = counts(bg)
        ic, inn = counts(ig)
        per_fam[f] = (bc, bn, ic, inn)
        base_c += bc
        base_n += bn
        inst_c += ic
        inst_n += inn
        print(f"  {f}: base {bn:,} words, instruct {inn:,} words")

    def pref(w, bc=None, bn=None, ic=None, inn=None):
        bc, bn = (base_c, base_n) if bc is None else (bc, bn)
        ic, inn = (inst_c, inst_n) if ic is None else (ic, inn)
        return math.log(((ic[w] + 0.5) / inn) / ((bc[w] + 0.5) / bn))

    # ---------- TEST A: is the instrument an alignment artifact? ----------
    print("\n=== TEST A: do instruct models prefer the Kobak style words? ===")
    # symmetric: a control candidate may be absent from either model's
    # output, exactly as a style word may be, and the bucket is the combined
    # count rather than the ratio's denominator
    allw = set(base_c) | set(inst_c)
    cand = [w for w in allw
            if len(w) >= 4 and w.isalpha() and w not in set(style)]
    bucket = defaultdict(list)
    for w in cand:
        bucket[int(math.log2(base_c[w] + inst_c[w] + 1))].append(w)

    def pool_for(b):
        for off in (0, 1, -1, 2, -2, 3, -3):
            if bucket.get(b + off):
                return bucket[b + off]
        return max(bucket.values(), key=len)

    def bucket_of(w):
        return int(math.log2(base_c[w] + inst_c[w] + 1))

    def excess(words, reps=1000):
        v = sum(pref(w) for w in words) / len(words)
        pl = [pool_for(bucket_of(w)) for w in words]
        dr = sorted(sum(pref(rng.choice(p)) for p in pl) / len(pl)
                    for _ in range(reps))
        return v, dr[len(dr) // 2], v - dr[len(dr) // 2], \
            sum(1 for d in dr if d >= v)

    present = [w for w in style if base_c[w] + inst_c[w] > 0]
    real, med, exc, ex = excess(present)
    print(f"  Kobak style words, mean log(instruct/base) = {real:+.4f}")
    print(f"  frequency-matched controls: median {med:+.4f}")
    print(f"  EXCESS {exc:+.4f}   p = {ex}/1000"
          + ("  <0.001" if ex == 0 else ""))

    # Null calibration: what does this procedure return for word lists with
    # no special property? Anything it returns on noise is a pedestal and
    # must be subtracted before the estimate means anything.
    byb = defaultdict(list)
    for w in cand:
        byb[bucket_of(w)].append(w)
    prof = [bucket_of(w) for w in present]

    def fake(seed):
        r = random.Random(seed)
        out = []
        for b in prof:
            for off in (0, 1, -1, 2, -2, 3, -3):
                if byb.get(b + off):
                    out.append(r.choice(byb[b + off]))
                    break
        return out

    nulls = [excess(fake(1000 + s), reps=200)[2] for s in range(30)]
    nm = sum(nulls) / len(nulls)
    nsd = (sum((x - nm) ** 2 for x in nulls) / (len(nulls) - 1)) ** 0.5
    print(f"  null pedestal (30 random frequency-matched lists): "
          f"{nm:+.4f} sd {nsd:.4f}, {sum(1 for x in nulls if x > 0)}/30 "
          f"positive")
    print(f"  -> the style list sits {(exc - nm) / nsd:.1f} sd above what "
          f"this estimator returns on noise")

    # Where the effect lives: words the base model never emits at all.
    zero = [w for w in present if base_c[w] == 0]
    nz = [w for w in present if base_c[w] > 0]
    if zero and nz:
        print(f"  decomposition: {len(zero)} of {len(present)} style words "
              f"({100*len(zero)/len(present):.0f}%) are ABSENT from base "
              f"output,")
        print(f"    mean pref {sum(pref(w) for w in zero)/len(zero):+.4f}; "
              f"the other {len(nz)} average "
              f"{sum(pref(w) for w in nz)/len(nz):+.4f}.")
        print("    The alignment effect is concentrated, not broad.")
    # Per family, as an EXCESS against the same symmetric control pool, with
    # a bootstrap interval over words. An earlier METHODOLOGY.md table gave
    # per-family excesses of +1.04 [+1.05, +1.31] and +0.65 [+0.67, +0.99] --
    # in both rows the point estimate falls OUTSIDE its own interval, which is
    # impossible. Those came from a superseded run and are not reconstructible;
    # this replaces them.
    print("  per family (excess vs the same symmetric controls, "
          "95% bootstrap over words):")
    for f in fams:
        bc, bn, ic, inn = per_fam[f]

        def fp(w):
            return math.log(((ic[w] + 0.5) / inn) / ((bc[w] + 0.5) / bn))

        v = sum(fp(w) for w in present) / len(present)
        pl = [pool_for(bucket_of(w)) for w in present]
        cm = sorted(sum(fp(rng.choice(p)) for p in pl) / len(pl)
                    for _ in range(400))[200]
        bs = []
        for _ in range(1000):
            samp = [present[rng.randrange(len(present))]
                    for _ in range(len(present))]
            bs.append(sum(fp(w) for w in samp) / len(samp) - cm)
        bs.sort()
        print(f"    {f:<9s} {v - cm:+.4f}  "
              f"[{bs[25]:+.4f}, {bs[975]:+.4f}]  "
              f"(mean pref {v:+.4f}, control median {cm:+.4f})")

    # ---------- Hansard outcome, for tests B and C ----------
    pre_c, post_c = Counter(), Counter()
    pre_w = post_w = 0
    for path in SRC:
        if not os.path.exists(path):
            continue
        for line in open(path):
            d = json.loads(line)
            if not (d.get("scoreable") and not d.get("translated")
                    and d.get("orig_frac", 1.0) > 0.5):
                continue
            toks = TOKEN_RE.findall(d["text"].lower())
            if d["date"] <= "2022-12-31":
                pre_c.update(toks)
                pre_w += len(toks)
            elif d["date"] >= "2024-01-01":
                post_c.update(toks)
                post_w += len(toks)

    ws = [w for w in style if pre_c[w] > 0 and post_c[w] > 0
          and base_c[w] + inst_c[w] > 0]
    shift = [math.log(((post_c[w] + 0.5) / post_w) / ((pre_c[w] + 0.5) / pre_w))
             for w in ws]
    rl = [pref(w) for w in ws]
    lpre = [math.log(pre_c[w] + 1) for w in ws]
    # rival predictor: base-model output vs human Hansard -- generic machine
    # text, no post-training involved. This is the UNPAIRED form, the one the
    # review showed is contaminated by rarity; included precisely to show that.
    llm = [math.log(((base_c[w] + 0.5) / base_n) / ((pre_c[w] + 0.5) / pre_w))
           for w in ws]

    print(f"\n=== TEST B/C: predicting the Hansard shift (n = {len(ws)} words) ===")
    print(f"{'predictor':<26s} {'Spearman':>9s} {'partial|freq':>13s} {'strat p':>9s}")
    for label, pred in (("rlhf_pref (paired)", rl),
                        ("llm_pref (unpaired)", llm)):
        r = spear(pred, shift)
        pa = partial(pred, shift, lpre)
        _, p = strat_perm(pred, shift, lpre, random.Random(5))
        print(f"{label:<26s} {r:>+9.4f} {pa:>+13.4f} {p:>9.4f}")
    print("  per family (does each replicate on its own?):")
    for f in fams:
        bc, bn, ic, inn = per_fam[f]
        pf = [math.log(((ic[w] + 0.5) / inn) / ((bc[w] + 0.5) / bn)) for w in ws]
        _, pp = strat_perm(pf, shift, lpre, random.Random(9))
        print(f"    {f:<9s} Spearman {spear(pf, shift):+.4f}  "
              f"partial {partial(pf, shift, lpre):+.4f}  strat p {pp:.4f}")
    print(f"{'(rarity check)':<26s} {spear(rl, [-v for v in lpre]):>+9.4f}"
          f"{'  <- rlhf_pref vs -log(pre freq); the old test scored +0.92 here':<0s}")

    # ---------- TEST D: what does post-training add? ----------
    print("\n=== TEST D: what post-training adds (descriptive) ===")
    common = [w for w in base_c if base_c[w] >= 20 and len(w) >= 4]
    top = sorted(common, key=lambda w: -pref(w))[:40]
    print("  most instruct-preferred (>=20 base occurrences):")
    print("   ", ", ".join(top[:30]))
    for cat, words in SYCO.items():
        got = [w for w in words if base_c[w] + inst_c[w] > 0]
        if got:
            m = sum(pref(w) for w in got) / len(got)
            print(f"  {cat:<13s} n={len(got):2d}  mean log(instruct/base) {m:+.4f}")

    json.dump({"test_a_excess": real - draws[len(draws) // 2],
               "test_a_p": ex / 1000,
               "families": fams,
               "n_words": len(ws)},
              open("rlhf_pref_results.json", "w"), indent=1)
    print("\nwrote rlhf_pref_results.json")


if __name__ == "__main__":
    main()
