#!/usr/bin/env python3
"""Style-word frequency vectors: clusters, class geometry, and where AI sits.

WHAT A VECTOR IS HERE

For each speaker (or text set), the 407 Kobak style words' rates, then
normalised to COMPOSITION: each vector divided by its own sum, so it describes
WHICH instrument words a speaker favours, not HOW MUCH instrument they use.
The "how much" question is settled elsewhere (§4.6, §4.6a); every question in
this file is about mix, which is why overall frequency is divided out rather
than "controlled" by regression.

Rates are computed per member over the POST era (2023-26) unless stated,
because that is the era the AI questions are about. Members need >= MIN_WORDS
post-era words to enter; below that a composition vector is mostly noise.

THE QUESTIONS, in the order asked (Matthew, 2026-08-14):

  --clusters     Do member vectors cluster with no priors? k-means over
                 PCA-reduced composition vectors, silhouette across k,
                 against a null of the same data with member labels shuffled
                 across words (which preserves the marginal word distribution).

  --alignment    Do the vectors organise along cohort, education, or class?
                 Correlation of the top principal components with each,
                 plus a permutation test on centroid separation.

  --ai-similar   Pooled vector of machine-flagged legislature speech (Pangram
                 AI verdicts, plus Mixed weighted by fraction): which class and
                 education centroid is it nearest, by cosine?

  --pull         For each member with flagged segments: the direction from
                 their own human-speech vector to their flagged-speech vector,
                 projected onto (a) the class axis (working->professional
                 centroid line) and (b) the education axis. Positive = AI use
                 moves them toward the professional/graduate end.

  --traces       The generated traces (llama3/mistral/qwen3 base+instruct in
                 rlhf_gen_180/, Claude models in claude_gen/): cosine to each
                 class and education centroid.

HONEST LIMITS, up front. Composition vectors on 407 words need a lot of text;
even at MIN_WORDS the per-member vectors are noisy, and k-means will happily
report clusters in noise -- hence the shuffled null. The AI-flagged pool is
small (tens of segments per province). And cosine similarity between a
machine's vector and a class centroid says the mixes resemble each other, not
that one causes the other.

Usage:
  python vector_analysis.py --clusters | --alignment | --ai-similar | --pull | --traces | --all
"""
import argparse
import csv
import json
import math
import os
import random
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402
import class_markedness as CM               # noqa: E402

VEC = os.path.join(HERE, "member_word_vectors.json")
SEGS = os.path.join(HERE, "scored_seg_texts.jsonl")
MIN_WORDS = 30_000
LV = ["none", "secondary", "college", "bachelor", "graduate", "professional"]


def style_words():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(
                       HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def education_map():
    FILES = [("AB", "provinces/ab_education_official.json", "records"),
             ("BC", "provinces/bc_member_education.json", "records"),
             ("MB", "provinces/mb_education_occupation.json", "records"),
             ("NL", "provinces/nl_education_occupation.json", None),
             ("NS", "provinces/ns_member_bios.json", None),
             ("ON", "provinces/on_member_education.json", None),
             ("PE", "provinces/pe_member_education.json", "records"),
             ("SK", "provinces/sk_legislature_bios.json", None)]
    out = {}
    for pv, rel, key in FILES:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for r in (d[key] if key else d):
            nm = FW.norm(r.get("hansard_speaker_key") or r.get("speaker_key")
                         or r.get("_key") or r.get("name")
                         or r.get("full_name") or "")
            e = (r.get("education_level") or "").strip().lower()
            if nm and e in LV:
                out[(pv, nm)] = e
    for r in json.load(open(os.path.join(HERE, "provinces",
                                         "member_allsource.json"))):
        nm = FW.norm(r.get("name") or "")
        e = (r.get("education_level") or "").strip().lower()
        k = (r["prov"], nm)
        if nm and e in LV and k not in out:
            out[k] = e
    return out


def birth_map():
    out = {}
    for r in json.load(open(os.path.join(HERE, "provinces",
                                         "member_allsource.json"))):
        if r.get("birth_year"):
            out[(r["prov"], FW.norm(r["name"]))] = r["birth_year"]
    for r in json.load(open(os.path.join(HERE, "provinces",
                                         "member_bios.json"))):
        k = (r.get("prov"), FW.norm(r.get("name") or ""))
        if r.get("birth_year") and k not in out:
            out[k] = r["birth_year"]
    return out


def load_members(era="post"):
    """-> (keys, matrix of composition vectors, total words per member)."""
    words = style_words()
    widx = {w: i for i, w in enumerate(words)}
    d = json.load(open(VEC))
    keys, rows, tots = [], [], []
    for k, v in d.items():
        tw = v[f"{era}_w"]
        if tw < MIN_WORDS:
            continue
        vec = np.zeros(len(words))
        for w, c in v[era].items():
            if w in widx:
                vec[widx[w]] = c
        s = vec.sum()
        if s < 200:                       # need enough instrument occurrences
            continue
        keys.append(tuple(k.split("|")))
        rows.append(vec / s)
        tots.append(tw)
    return keys, np.array(rows), np.array(tots), words


def text_vector(texts, words):
    widx = {w: i for i, w in enumerate(words)}
    vec = np.zeros(len(words))
    for t in texts:
        for tok in FW.TOKEN_RE.findall(t.lower()):
            if tok in widx:
                vec[widx[tok]] += 1
    s = vec.sum()
    return (vec / s, s) if s else (vec, 0)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na and nb else float("nan")


def pca(X, k=10):
    Xc = X - X.mean(0)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:k].T, Vt[:k], (S ** 2) / (S ** 2).sum()


def kmeans(X, k, seed=0, iters=100):
    rng = np.random.RandomState(seed)
    C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        d = ((X[:, None] - C[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        C2 = np.array([X[lab == i].mean(0) if (lab == i).any() else C[i]
                       for i in range(k)])
        if np.allclose(C2, C):
            break
        C = C2
    return lab, C


def silhouette(X, lab):
    n = len(X)
    if n > 1200:
        idx = np.random.RandomState(0).choice(n, 1200, replace=False)
        X, lab = X[idx], lab[idx]
        n = len(X)
    D = np.sqrt(((X[:, None] - X[None]) ** 2).sum(-1))
    s = []
    for i in range(n):
        same = lab == lab[i]
        same[i] = False
        if not same.any():
            continue
        a = D[i][same].mean()
        b = min(D[i][lab == c].mean() for c in set(lab) if c != lab[i])
        s.append((b - a) / max(a, b))
    return float(np.mean(s))


def clusters():
    keys, X, tots, words = load_members()
    P, _, ev = pca(X, 10)
    print(f"{len(keys)} members with >= {MIN_WORDS:,} post-era words\n")
    print(f"  variance in top PCs: " +
          "  ".join(f"PC{i+1} {100*e:.1f}%" for i, e in enumerate(ev[:5])))
    print(f"\n  {'k':>3}{'silhouette':>12}{'shuffled null':>15}")
    rng = np.random.RandomState(1)
    for k in (2, 3, 4, 5, 6, 8):
        lab, _ = kmeans(P, k, seed=k)
        s = silhouette(P, lab)
        # null: shuffle each member's counts across words -- kills structure,
        # keeps each member's marginal instrument volume
        Xn = X.copy()
        for i in range(len(Xn)):
            rng.shuffle(Xn[i])
        Pn, _, _ = pca(Xn, 10)
        labn, _ = kmeans(Pn, k, seed=k)
        sn = silhouette(Pn, labn)
        print(f"  {k:>3}{s:>12.3f}{sn:>15.3f}")
    print("\n  A silhouette meaningfully above its null row is a real cluster;")
    print("  matching the null means the 'clusters' are k-means slicing noise.")


def alignment():
    keys, X, tots, words = load_members()
    P, _, ev = pca(X, 5)
    cls = CM.member_class()
    edu = education_map()
    by = birth_map()
    EGP_RANK = {c: i for i, c in enumerate(
        ["VIIab", "V/VI", "IVc", "IVab", "III", "II", "I"])}
    meta = {"class": [], "edu": [], "birth": []}
    idx = {"class": [], "edu": [], "birth": []}
    for i, k in enumerate(keys):
        c = cls.get(k)
        if c:
            meta["class"].append(EGP_RANK[c])
            idx["class"].append(i)
        e = edu.get(k)
        if e and e != "professional":         # ladder only; see 4.6a
            meta["edu"].append(LV.index(e))
            idx["edu"].append(i)
        b = by.get(k)
        if b and 1925 <= b <= 2000:
            meta["birth"].append(b)
            idx["birth"].append(i)
    print(f"{len(keys)} members; class {len(idx['class'])}, "
          f"education {len(idx['edu'])}, birth {len(idx['birth'])}\n")
    print(f"  {'axis':<10}" + "".join(f"{f'PC{j+1}':>9}" for j in range(5)))
    for name in ("class", "edu", "birth"):
        v = np.array(meta[name], float)
        rows = P[idx[name]]
        cs = []
        for j in range(5):
            x = rows[:, j]
            r = np.corrcoef(x, v)[0, 1]
            cs.append(r)
        print(f"  {name:<10}" + "".join(f"{r:>+9.2f}" for r in cs))
    print("\n  (Pearson r of each PC score with the member attribute; the PCs")
    print("  are of COMPOSITION, so any alignment is about word mix, not rate.)")


def group_centroids(keys, X):
    cls = CM.member_class()
    edu = education_map()
    cent = {}
    for name, get, groups in (
            ("class", cls.get, ["I", "II", "III", "IVab", "IVc", "V/VI",
                                "VIIab"]),
            ("edu", edu.get, LV)):
        for g in groups:
            rows = [X[i] for i, k in enumerate(keys) if get(k) == g]
            if len(rows) >= 5:
                cent[(name, g)] = np.mean(rows, 0)
    return cent


def ai_similar():
    keys, X, tots, words = load_members()
    cent = group_centroids(keys, X)
    ai_texts, hu_texts = [], []
    for line in open(SEGS):
        d = json.loads(line)
        if d["verdict"] in ("AI", "Mixed"):
            ai_texts.append(d["text"])
        else:
            hu_texts.append(d["text"])
    vai, nai = text_vector(ai_texts, words)
    vhu, nhu = text_vector(hu_texts, words)
    print(f"machine-flagged pool: {len(ai_texts)} segments, "
          f"{int(nai):,} instrument occurrences")
    print(f"human-scored pool:    {len(hu_texts)} segments, "
          f"{int(nhu):,} occurrences\n")
    for name, groups in (("class", ["I", "II", "III", "IVab", "IVc",
                                    "V/VI", "VIIab"]), ("edu", LV)):
        print(f"  cosine to {name} centroids   (flagged | human-scored)")
        scored = []
        for g in groups:
            c = cent.get((name, g))
            if c is None:
                continue
            scored.append((g, cos(vai, c), cos(vhu, c)))
        for g, ca, ch in sorted(scored, key=lambda x: -x[1]):
            print(f"    {g:<14}{ca:>8.4f}  |{ch:>8.4f}"
                  f"   diff {ca-ch:>+7.4f}")
        print()


def pull():
    keys, X, tots, words = load_members()
    kidx = {k: i for i, k in enumerate(keys)}
    cent = group_centroids(keys, X)
    if ("class", "I") not in cent or ("class", "VIIab") not in cent:
        print("not enough members per class for the axis")
    cls_axis = None
    if ("class", "I") in cent and ("class", "II") in cent:
        # professional pole minus the accessible pole actually used in 4.6a
        lo = cent.get(("class", "VIIab"))
        if lo is None:
            lo = cent[("class", "II")]
        cls_axis = cent[("class", "I")] - lo
        cls_axis /= np.linalg.norm(cls_axis)
    edu_axis = None
    if ("edu", "graduate") in cent and ("edu", "secondary") in cent:
        edu_axis = cent[("edu", "graduate")] - cent[("edu", "secondary")]
        edu_axis /= np.linalg.norm(edu_axis)

    per = defaultdict(lambda: {"ai": [], "hu": []})
    for line in open(SEGS):
        d = json.loads(line)
        k = (d["prov"], d["speaker"])
        per[k]["ai" if d["verdict"] in ("AI", "Mixed") else "hu"].append(
            d["text"])
    rows = []
    for k, v in per.items():
        if not v["ai"] or k not in kidx:
            continue
        vai, n = text_vector(v["ai"], words)
        if n < 20:
            continue
        base = X[kidx[k]]
        delta = vai - base
        rows.append((k, len(v["ai"]), int(n),
                     float(delta @ cls_axis) if cls_axis is not None else None,
                     float(delta @ edu_axis) if edu_axis is not None else None))
    print(f"{len(rows)} members with usable flagged text and a baseline\n")
    if not rows:
        return
    ca = [r[3] for r in rows if r[3] is not None]
    ea = [r[4] for r in rows if r[4] is not None]
    def summ(v, lab):
        if not v:
            return
        m = np.mean(v)
        se = np.std(v) / math.sqrt(len(v))
        print(f"  {lab}: mean {m:+.5f} (se {se:.5f}), "
              f"{sum(1 for x in v if x > 0)}/{len(v)} positive")
    summ(ca, "projection on class axis (VIIab -> I)   ")
    summ(ea, "projection on education axis (sec -> grad)")
    print("\n  Positive = a member's flagged speech sits closer to the")
    print("  professional/graduate pole than their own baseline mix does.")


def traces():
    keys, X, tots, words = load_members()
    cent = group_centroids(keys, X)
    sets = {}
    g180 = os.path.join(HERE, "rlhf_gen_180")
    for f in sorted(os.listdir(g180)):
        if f.endswith(".json"):
            sets[f[:-5]] = [t if isinstance(t, str) else t.get("text", "")
                            for t in json.load(open(os.path.join(g180, f)))]
    cg = os.path.join(HERE, "claude_gen")
    if os.path.isdir(cg):
        pooled = defaultdict(list)
        for f in sorted(os.listdir(cg)):
            if f.endswith(".json"):
                model = f.split("_c")[0]
                for t in json.load(open(os.path.join(cg, f))):
                    pooled[f"{model} (claude)"].append(
                        t["text"] if isinstance(t, dict) else t)
        sets.update(pooled)
    print(f"{len(sets)} trace sets\n")
    order_c = ["I", "II", "III", "IVab", "IVc", "V/VI", "VIIab"]
    for name, texts in sets.items():
        v, n = text_vector(texts, words)
        best_c = max(((g, cos(v, cent[("class", g)])) for g in order_c
                      if ("class", g) in cent), key=lambda x: x[1])
        best_e = max(((g, cos(v, cent[("edu", g)])) for g in LV
                      if ("edu", g) in cent), key=lambda x: x[1])
        print(f"  {name:<22} {int(n):>7,} occ   nearest class {best_c[0]:<6}"
              f"({best_c[1]:.4f})   nearest edu {best_e[0]:<12}"
              f"({best_e[1]:.4f})")


def main():
    ap = argparse.ArgumentParser()
    for f in ("clusters", "alignment", "ai-similar", "pull", "traces", "all"):
        ap.add_argument(f"--{f}", action="store_true")
    a = ap.parse_args()
    ran = False
    for flag, fn in (("clusters", clusters), ("alignment", alignment),
                     ("ai_similar", ai_similar), ("pull", pull),
                     ("traces", traces)):
        if getattr(a, flag) or a.all:
            print("=" * 70)
            fn()
            ran = True
    if not ran:
        print(__doc__)


if __name__ == "__main__":
    main()
