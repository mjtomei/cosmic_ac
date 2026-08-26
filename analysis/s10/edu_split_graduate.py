#!/usr/bin/env python3
"""Split the "graduate" education level into master's vs doctorate.

Matthew's ask (2026-08-25): the education ladder's graduate rung lumps two
different credentials. Every source that coded a member "graduate" carries
its raw evidence — quotes, education_field, full_name — so the degree is
recoverable by marker for most members. Members whose evidence names no
specific degree stay "graduate" (unrecorded): they remain in the model as
their own level rather than being dropped or guessed.

Markers (honorary-degree sentences stripped first): doctorate = PhD/DPhil/
EdD/ScD/ThD/doctoral/doctorate; master's = MA/MSc/MS/MBA/MEd/MPA/MPP/MSW/
MPhil/LLM/MDiv/STM/"master of/in/'s degree". Doctorate wins when both
appear (highest attained). JD is NOT a doctorate here — law belongs to the
professional level, not the graduate rung.

Writes graduate_degree_split.json: {"provkey": {"PV|nm": lvl}, "t1key":
{raw tier-1 key: lvl}} with lvl in {master, doctorate}.

Usage: python edu_split_graduate.py
"""
import json
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))

DOC = re.compile(r"\b(ph\.?\s?d|d\.?\s?phil|doctorate|doctoral|ed\.?d\b|"
                 r"sc\.?d\b|d\.?sc\b|th\.?d)(?![a-z])", re.I)
MAS = re.compile(r"\b(m\.?\s?a\.|m\.a\b|m\.?sc\b|m\.s\.|m\.s\b|mba\b|"
                 r"m\.?b\.?a\.|m\.?ed\b|m\.ed\.|mpa\b|mpp\b|msw\b|"
                 r"m\.?phil\b|ll\.?m\b|m\.?div\b|s\.?t\.?m\b|"
                 r"master(?:'s|s)?\s+(?:degree|of|in)|master of)(?![a-z])",
                 re.I)
HON = re.compile(r"honorary|honoris causa", re.I)


def strip_hon(t):
    return " ".join(s for s in re.split(r"(?<=[.;])\s+", t)
                    if not HON.search(s))


def classify(blob):
    b = strip_hon(blob)
    if DOC.search(b):
        return "doctorate"
    if MAS.search(b):
        return "master"
    return None


def blob_of(rec):
    parts = [rec.get("full_name") or "", rec.get("education_field") or ""]
    for ev in rec.get("evidence") or []:
        parts.append(str(ev.get("value") or ""))
        parts.append(ev.get("quote") or "")
    return " | ".join(parts)


def main():
    import sys
    sys.path.insert(0, HERE)
    import formation_window as FW
    provkey, t1key = {}, {}
    tally = Counter()

    for r in json.load(open(os.path.join(HERE, "provinces",
                                         "member_allsource.json"))):
        if (r.get("education_level") or "").lower() != "graduate":
            continue
        c = classify(blob_of(r))
        tally[f"prov:{c}"] += 1
        if c:
            provkey[f'{r["prov"]}|{FW.norm(r["name"])}'] = c

    for r in json.load(open(os.path.join(HERE, "covariates_tier1.json"))):
        if (r.get("education_level") or "").lower() != "graduate" \
                or r.get("ambiguous"):
            continue
        c = classify(blob_of(r))
        tally[f"t1:{c}"] += 1
        if c:
            t1key[r["key"]] = c

    for r in json.load(open(os.path.join(HERE, "covariates_missing9.json"))):
        if (r.get("education_level") or "").lower() != "graduate" \
                or r.get("ambiguous"):
            continue
        c = classify(blob_of(r))
        tally[f"m9:{c}"] += 1
        if c:
            provkey[f'{r["chamber"]}|{r["key"]}'] = c

    out = {"provkey": provkey, "t1key": t1key}
    json.dump(out, open(os.path.join(HERE, "graduate_degree_split.json"), "w"))
    for k, v in sorted(tally.items()):
        print(f"{k:<16}{v}")
    n_split = sum(v for k, v in tally.items() if not k.endswith("None"))
    n_all = sum(tally.values())
    print(f"\nsplit {n_split}/{n_all} graduate codings "
          f"({n_split/n_all:.0%}); the rest stay graduate (unrecorded)")

    # ---- the education table, refined: spec A (z, bd control, HC1),
    # bachelor baseline — the same estimator behind the draft's table ----
    import math
    import member_level_estimation as MLE
    rows = MLE.zscore(MLE.members())
    ok = [r for r in rows if r["bd"] is not None and r.get("z") is not None
          and r["edu"] in MLE.LV]
    import joint_predictors as JP
    JP.apply_edu_split(ok)
    cats = ["none", "secondary", "college", "master", "doctorate",
            "graduate", "professional"]
    y, X = [], []
    for r in ok:
        y.append(r["z"])
        X.append([1.0] + [1.0 if r["edu"] == c else 0.0 for c in cats]
                 + [r["bd"]])
    beta, V = MLE.ols_hc1(y, X)
    print(f"\nEDUCATION, refined — z within legislature, birth-decade "
          f"controlled   n={len(ok):,} (baseline bachelor)")
    from collections import defaultdict
    mz, nn = defaultdict(float), Counter()
    for r in ok:
        mz[r["edu"]] += r["z"]; nn[r["edu"]] += 1
    for lvl in ["none", "secondary", "college", "bachelor"] + cats[3:]:
        m = mz[lvl] / nn[lvl]
        if lvl == "bachelor":
            print(f"  {lvl:<22}mean z {m:+.3f}  n {nn[lvl]:>5}  baseline")
            continue
        j = cats.index(lvl) + 1
        b, se = beta[j], math.sqrt(V[j, j])
        print(f"  {lvl:<22}mean z {m:+.3f}  n {nn[lvl]:>5}  "
              f"vs bachelor {b:+.3f} (t {b/se:+.2f})")
    W, k, pv = MLE.wald(beta, V, list(range(1, len(cats) + 1)))
    print(f"  block Wald: chi2={W:.1f}, df={k}, p={pv:.4g}")


if __name__ == "__main__":
    main()
