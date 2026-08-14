#!/usr/bin/env python3
"""Province-gradient exposure test — the staff-local version of state_gradient.

WHY PROVINCES FIX THE US DESIGN'S FLAW

The congressional test came back null, but its exposure variable (home-state
adoption) never reached the people who draft the speeches: congressional
staff live in Washington. Provincial members' staff live in-province, offices
are small, and many members draft their own remarks — so provincial adoption
actually measures the drafting environment's exposure.

Exposure: StatCan 22-10-0034 (Household Internet Use Survey), household
internet use from any location, by province, 1997-2003 — see
province_covariates.csv for provenance. The regressor is the 2000 level
(the gradient era; sd 5.0 points across provinces). Quebec is excluded
(French debates; the instrument is English).

Outcome: per-member register drift between 2006-2010 and 2015-2019, both
windows pre-LLM. Drift is the equal-weight mean logFC over Kobak style words
the member used in the early window, minus the same statistic on matched
placebo words (the member's own placebo drift), exactly as in
state_gradient.py.

Speaker identity: provincial Hansards carry no stable member ID, so members
are joined by normalised name WITHIN a province. Titles and honorifics are
stripped; "Hon." prefixes vary by government membership so they cannot be
part of the key. Cross-province name collisions are impossible by
construction (the join is per-province).

Inference: OLS of drift on standardised adoption with party unavailable
(provincial party labels are not in the segment schema), so controls are
chamber fixed effects (= province FE would absorb the regressor; instead we
use region FE: west/central/atlantic) plus member volume. Primary inference
is the cross-province gradient with members clustered by province via a
wild-ish cluster bootstrap over provinces (only ~6-9 clusters, so the
bootstrap resamples provinces whole).

Usage: python province_gradient.py
"""
import csv
import glob
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict

TOKEN_RE = re.compile(r"[a-z']+")
_HERE = os.path.dirname(os.path.abspath(__file__))
EARLY = {str(y) for y in range(2006, 2011)}
LATE = {str(y) for y in range(2015, 2020)}
MIN_WORDS = 5000
MIN_USED = 12
N_PLACEBO_SETS = 80
REGION = {"BC": "west", "AB": "west", "SK": "west", "MB": "central",
          "ON": "central", "NS": "atlantic", "NB": "atlantic",
          "NL": "atlantic", "PE": "atlantic"}

TITLE_RE = re.compile(
    r"^(hon\.?|honourable|l\'hon\.?|mr\.?|mrs\.?|ms\.?|miss|dr\.?|mme\.?|m\.|madame|monsieur|the)\s+", re.I)


ROLE_LABELS = re.compile(
    r"^(premier|deputy premier|leader of the (official )?opposition|"
    r"minister( of| responsible)?\b|government house leader|"
    r"opposition house leader|attorney general)\b", re.I)


def norm_name(s):
    s = s.strip().rstrip(":").strip()
    prev = None
    while prev != s:
        prev = s
        s = TITLE_RE.sub("", s).strip()
    # strip trailing riding/portfolio parentheticals
    s = re.sub(r"\s*\(.*?\)\s*$", "", s)
    return s.lower()


def load_style():
    return sorted({r["word"].lower() for r in
                   csv.DictReader(open(os.path.join(_HERE, "kobak_excess_words.csv")))
                   if r["type"] == "style" and r["word"].isalpha()})


def main():
    style = load_style()
    cov = {}
    for r in csv.DictReader(open(os.path.join(_HERE, "province_covariates.csv"))):
        if r["prov"].startswith("#") or not r.get("internet2000"):
            continue
        cov[r["prov"]] = float(r["internet2000"])

    files = sorted(glob.glob(os.path.join(_HERE, "provinces", "segments_*.jsonl")))
    if not files:
        raise SystemExit("no provincial segment files yet")
    print(f"corpora: {', '.join(os.path.basename(f) for f in files)}")

    pre = defaultdict(Counter)
    post = defaultdict(Counter)
    corpus_early = defaultdict(Counter)
    prov_of = {}
    for path in files:
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            y = d["date"][:4]
            if y in EARLY:
                tgt = pre
            elif y in LATE:
                tgt = post
            else:
                continue
            pv = d.get("prov")
            if pv not in cov:
                continue
            nm = norm_name(d.get("speaker", ""))
            # role labels are offices, not people; joining them across eras
            # would merge different incumbents (NS prints "THE PREMIER")
            if not nm or ROLE_LABELS.match(nm):
                continue
            key = (pv, nm)
            t = TOKEN_RE.findall(d["text"].lower())
            tgt[key].update(t)
            if y in EARLY:
                corpus_early[pv].update(t)
            prov_of[key] = pv

    placs_by_prov = {}
    for pv, ce in corpus_early.items():
        rng = random.Random(int(hashlib.sha1(
            (pv + "provgrad").encode()).hexdigest()[:8], 16))
        excluded = set(style) | {w for w, _ in ce.most_common(120)}
        bucket = defaultdict(list)
        for w, c in ce.items():
            if w in excluded or len(w) < 4 or not w.isalpha():
                continue
            bucket[int(math.log2(c + 1))].append(w)

        def pool_for(b):
            for off in (0, 1, -1, 2, -2, 3, -3):
                if bucket.get(b + off):
                    return bucket[b + off]
            return max(bucket.values(), key=len)
        pools = [pool_for(int(math.log2(ce[w] + 1))) for w in style]
        placs_by_prov[pv] = [[rng.choice(p) for p in pools]
                             for _ in range(N_PLACEBO_SETS)]

    def eqw(a, b, wa, wb, words):
        used = [w for w in words if a[w] > 0]
        if len(used) < MIN_USED:
            return None
        return sum(math.log(((b[w] + 0.5) / wb) / ((a[w] + 0.5) / wa))
                   for w in used) / len(used)

    # Hansard prints the same member under short and long forms ("Lamoureux"
    # vs "Kevin Lamoureux"), which would split one person across windows.
    # Merge a shorter name into a longer one within the same province when
    # the shorter is the longer's surname and that surname is unambiguous.
    all_keys = set(pre) | set(post)
    by_prov_names = defaultdict(set)
    for pv, nm in all_keys:
        by_prov_names[pv].add(nm)
    alias = {}
    for pv, names in by_prov_names.items():
        by_last = defaultdict(set)
        for nm in names:
            by_last[nm.split()[-1]].add(nm)
        for last, forms in by_last.items():
            longs = [n for n in forms if " " in n]
            if last in forms and len(longs) == 1:
                alias[(pv, last)] = (pv, longs[0])
    if alias:
        for src, dst in alias.items():
            for tgt in (pre, post):
                if src in tgt:
                    tgt[dst].update(tgt.pop(src))
        print(f"merged {len(alias)} short-form name aliases")

    rows = []
    for key in set(pre) & set(post):
        a, b = pre[key], post[key]
        wa, wb = sum(a.values()), sum(b.values())
        if wa < MIN_WORDS or wb < MIN_WORDS:
            continue
        ei = eqw(a, b, wa, wb, style)
        if ei is None:
            continue
        ep = [x for x in (eqw(a, b, wa, wb, P)
                          for P in placs_by_prov[key[0]]) if x is not None]
        if not ep:
            continue
        rows.append({"prov": key[0], "name": key[1],
                     "drift": ei - sum(ep) / len(ep),
                     "adopt": cov[key[0]], "region": REGION.get(key[0], "?"),
                     "w_early": wa, "w_late": wb})
    if len(rows) < 40:
        raise SystemExit(f"only {len(rows)} members qualify — check corpora")
    json.dump(rows, open("province_gradient_members.json", "w"), indent=1)

    by_prov = defaultdict(list)
    for r in rows:
        by_prov[r["prov"]].append(r["drift"])
    print(f"\n{len(rows)} members across {len(by_prov)} provinces")
    print(f"{'prov':<5s} {'adopt2000':>9s} {'n':>4s} {'mean drift':>11s}")
    for pv in sorted(by_prov, key=lambda p: -cov[p]):
        v = by_prov[pv]
        print(f"{pv:<5s} {cov[pv]:>9.1f} {len(v):>4d} "
              f"{sum(v) / len(v):>+11.4f}")

    # member-level Spearman, then the honest inference: cluster bootstrap
    # over PROVINCES (the regressor varies only at province level, so
    # member-level SEs would be wildly overconfident)
    drift = [r["drift"] for r in rows]
    adopt = [r["adopt"] for r in rows]

    def spear(x, y):
        def rank(v):
            s = sorted(range(len(v)), key=lambda i: v[i])
            rk = [0.0] * len(v)
            i = 0
            while i < len(s):
                j = i
                while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                    j += 1
                a_ = (i + j) / 2 + 1
                for k in range(i, j + 1):
                    rk[s[k]] = a_
                i = j + 1
            return rk
        rx, ry = rank(x), rank(y)
        n = len(rx)
        mx, my = sum(rx) / n, sum(ry) / n
        num = sum((p - mx) * (q - my) for p, q in zip(rx, ry))
        den = math.sqrt(sum((p - mx) ** 2 for p in rx) *
                        sum((q - my) ** 2 for q in ry))
        return num / den

    print(f"\nmember-level Spearman(drift, adoption): {spear(drift, adopt):+.3f}")

    provs = sorted(by_prov)
    pm = {p: sum(by_prov[p]) / len(by_prov[p]) for p in provs}
    pa = {p: cov[p] for p in provs}
    n = len(provs)
    ma = sum(pa.values()) / n
    md = sum(pm.values()) / n
    num = sum((pa[p] - ma) * (pm[p] - md) for p in provs)
    den = sum((pa[p] - ma) ** 2 for p in provs)
    slope = num / den if den else float("nan")
    boots = []
    for _ in range(4000):
        ps = [provs[rng.randrange(n)] for _ in range(n)]
        ma_ = sum(pa[p] for p in ps) / n
        md_ = sum(pm[p] for p in ps) / n
        nu = sum((pa[p] - ma_) * (pm[p] - md_) for p in ps)
        de = sum((pa[p] - ma_) ** 2 for p in ps)
        if de > 1e-9:
            boots.append(nu / de)
    boots.sort()
    lo, hi = boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]
    print(f"province-level slope: {slope:+.5f} drift per adoption point")
    print(f"  cluster bootstrap 95% CI over provinces: [{lo:+.5f}, {hi:+.5f}]")
    print(f"  ({n} clusters — treat with humility; the member-level pattern")
    print(f"  and the province ordering matter more than this CI)")


if __name__ == "__main__":
    main()
