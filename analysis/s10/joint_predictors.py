#!/usr/bin/env python3
"""All the register's member-level predictors in one model.

WHY

Cohort, class, education, prominence and ministerial office have each been
estimated in their own subsection, each defended against one or two of the
others pairwise. Nobody has put them in a single regression, so "which of these
survives the others" has never been answered directly and the text has no
principled basis for how much weight to give each.

SPECIFICATION — the canonical member-level one (member_level_estimation.py):
one observation per legislator (career rate over >= 8,000 words), EQUAL weight,
register z-scored within each legislature against that chamber's full member
population, HC1 errors, joint Wald over each predictor's term block.

  cohort      birth decade, centred at 1960
  class       EGP category, baseline class I -- EVERY category present enters
              as a dummy (no small-cell fold into baseline; the SEs speak)
  education   level dummies, bachelor baseline (the education table's coding)
  prominence  log(Wikipedia article length)
  occ         the prereg occupational-derivative block: dir_middle + apex
              delta (grand model (ii)'s pair under the never-together rule)
              + Indoors, each z-scored per sd on the estimation sample
  office      share of career words spoken under a rank marker ("Hon. <name>")

COVERAGE IS THE BINDING CONSTRAINT, and it differs per predictor, so the model
is reported as a ladder of nested samples rather than one number:

  full panel      cohort + class + education + prominence
  occ panel       the same members intersected with occupational-score
                  coverage; the four-block joint refit on this sample, then
                  the occupational block added
  provinces only  the full-panel four, plus office -- only the eight Canadian
                  provinces mark rank in the record (UK Hansard prints
                  ministers under their own names), so office cannot enter
                  the panel model

Each block is also shown alone on the SAME sample as the joint fit, so an
attenuation is read against its own baseline rather than against a coefficient
estimated on a different set of members.

Usage: python joint_predictors.py
"""
import glob
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel_estimation as PE                      # noqa: E402
import member_level_estimation as MLE              # noqa: E402
import formation_window as FW                      # noqa: E402

TOKEN_RE = re.compile(r"[a-z']+")
RANK_RE = re.compile(
    r"^\s*(the\s+)?(l')?(rt\.?\s+|right\s+)?hon(ourable|orable|\.|\b)|"
    r"^\s*(premier|minister|attorney general|speaker|president of the)", re.I)
MARKING = ("ab", "bc", "mb", "nl", "ns", "on", "pe", "sk")
LV = PE.LV


def depth_key(member):
    """Both depth files key on CH|key, but tier-1 panel members carry a third
    component (CH|key|Person Name). Join on the first two either way."""
    return "|".join(member.split("|")[:2])


def load_depth():
    """CH|key -> log(article length), over both fetches."""
    out = {}
    for f in ("provinces/wiki_depth.json", "wiki_depth_t1.json",
              # the nine chambers, fetched 2026-08-17: 2,310 of 2,315 resolved
              "wiki_depth_missing9.json"):
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            continue
        for k, v in json.load(open(p)).items():
            L = v.get("length") if isinstance(v, dict) else v
            if L:
                out[depth_key(k)] = math.log(L)
    return out


def load_office():
    """member key -> share of career words spoken under a rank marker."""
    cache = os.path.join(HERE, "office_share.json")
    if os.path.exists(cache):
        return json.load(open(cache))
    tot, off = Counter(), Counter()
    files = [p for p in sorted(glob.glob(os.path.join(HERE, "provinces",
                                                      "segments_*.jsonl")))
             if os.path.basename(p).split("_", 1)[1].split(".")[0]
             .replace("_fill", "").replace("_2025", "") in MARKING]
    for path in files:
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            raw = d.get("speaker") or ""
            nm = FW.norm(raw)
            if not nm:
                continue
            k = f'{d["prov"]}|{nm}'
            n = len(TOKEN_RE.findall(d["text"].lower()))
            tot[k] += n
            if RANK_RE.match(raw):
                off[k] += n
    share = {k: off[k] / tot[k] for k in tot if tot[k] >= 5000}
    json.dump(share, open(cache, "w"))
    return share


EDU_DUM = ["secondary", "college", "graduate", "professional"]  # vs bachelor
OCC_TERMS = ["dir middle", "apex delta", "indoors"]
INDOORS_ID = "4.C.2.a.1.a"          # O*NET Work Context: Indoors, Environmentally Controlled


def load_occ():
    """member key -> (dir_middle, apex_delta, indoors) raw values.

    dir_middle and apex_delta come from the committed prereg member table;
    Indoors is the O*NET Work Context value for the member's SOC code,
    cached to indoors_by_soc.json so the model does not depend on the
    /tmp O*NET extraction surviving."""
    import csv
    cache = os.path.join(HERE, "indoors_by_soc.json")
    if os.path.exists(cache):
        val = json.load(open(cache))
    else:
        val = {}
        with open("/tmp/onet303/db_30_3_text/Work Context.txt",
                  encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["Element ID"] == INDOORS_ID and r["Scale ID"] in {"CX", "CT"}:
                    val[r["O*NET-SOC Code"]] = float(r["Data Value"])
        json.dump(val, open(cache, "w"))
    out = {}
    for r in json.load(open(os.path.join(HERE, "prereg_member_table.json"))):
        if r.get("dir_middle") is not None and r.get("apex_delta") is not None \
                and r.get("soc") in val:
            out[depth_key(r["member"])] = (
                r["dir_middle"], r["apex_delta"], val[r["soc"]])
    return out


def zscore_occ(sample):
    """attach per-sd occ columns, standardised on THIS estimation sample."""
    for i in range(3):
        v = np.array([r["occ_raw"][i] for r in sample], float)
        m, sd = v.mean(), v.std() or 1.0
        for r, x in zip(sample, v):
            r.setdefault("occ_z", [0.0] * 3)[i] = (x - m) / sd


def design(rows, blocks, cats):
    """(y, X, index map) for the requested predictor blocks."""
    y, X, idx = [], [], {}
    col = 1
    for b in blocks:
        if b == "class":
            idx["class"] = list(range(col, col + len(cats["class"])))
            col += len(cats["class"])
        elif b == "edu":
            # level dummies, bachelor baseline (review CC3: matches the
            # education table's own coding; no ordering assumption)
            idx["edu"] = list(range(col, col + len(EDU_DUM)))
            col += len(EDU_DUM)   # was += 2, a leftover of the 2-term ladder
            # coding -- it shifted every later block's index one run (the
            # misindexed joint-prominence cell corrected 2026-08-25)
        elif b == "occ":
            idx["occ"] = list(range(col, col + len(OCC_TERMS)))
            col += len(OCC_TERMS)
        else:
            idx[b] = [col]
            col += 1
    for r in rows:
        row = [1.0]
        for b in blocks:
            if b == "cohort":
                row.append(r["bd"])
            elif b == "class":
                row += [1.0 if r["egp"] == c else 0.0 for c in cats["class"]]
            elif b == "edu":
                row += [1.0 if r["edu"] == e else 0.0 for e in EDU_DUM]
            elif b == "prominence":
                row.append(r["logdepth"])
            elif b == "occ":
                row += r["occ_z"]
            elif b == "office":
                row.append(r["office"])
        X.append(row)
        y.append(r["z"])
    return y, X, idx


def report(rows, blocks, cats, label):
    y, X, idx = design(rows, blocks, cats)
    beta, V = MLE.ols_hc1(y, X)
    print(f"\n{label}   n = {len(rows):,}")
    for b in blocks:
        ii = idx[b]
        if b == "class":
            for j, c in zip(ii, cats["class"]):
                bb, se = beta[j], math.sqrt(V[j, j])
                print(f"    class {c:<10}{bb:>+8.3f}  t {bb/se:+.2f}"
                      f"{' *' if abs(bb/se) > 1.96 else ''}")
        elif b == "edu":
            for j, nm in zip(ii, [f"edu {e}" for e in EDU_DUM]):
                bb, se = beta[j], math.sqrt(V[j, j])
                print(f"    {nm:<16}{bb:>+8.3f}  t {bb/se:+.2f}"
                      f"{' *' if abs(bb/se) > 1.96 else ''}")
        elif b == "occ":
            for j, nm in zip(ii, OCC_TERMS):
                bb, se = beta[j], math.sqrt(V[j, j])
                print(f"    occ {nm:<12}{bb:>+8.3f}  t {bb/se:+.2f}"
                      f"{' *' if abs(bb/se) > 1.96 else ''}")
        else:
            j = ii[0]
            bb, se = beta[j], math.sqrt(V[j, j])
            print(f"    {b:<16}{bb:>+8.3f}  t {bb/se:+.2f}"
                  f"{' *' if abs(bb/se) > 1.96 else ''}")
        W, k, p = MLE.wald(beta, V, ii)   # every block, 1-df included
        print(f"      block Wald chi2={W:.1f}, df={k}, p={p:.4g}")


def main():
    rows = MLE.zscore(MLE.members())
    depth = load_depth()
    for r in rows:
        r["logdepth"] = depth.get(depth_key(r["member"]))
    ok = [r for r in rows
          if r["bd"] is not None and r.get("z") is not None]
    print(f"{len(ok):,} legislators with birth year and a z score, "
          f"{len({r['chamber'] for r in ok})} chambers")
    print("coverage among them: "
          f"class {sum(1 for r in ok if r['egp'] in PE.EGP_RANK):,}, "
          f"education {sum(1 for r in ok if r['edu'] in LV):,}, "
          f"prominence {sum(1 for r in ok if r['logdepth'] is not None):,}")

    # ---- full panel: cohort + class + education + prominence -------------
    full = [r for r in ok if r["egp"] in PE.EGP_RANK and r["edu"] in LV
            and r["logdepth"] is not None]
    # every class present enters as a dummy: a small-cell filter here would
    # silently fold those members into baseline class I
    cats = {"class": [c for c in PE.EGP if c != "I"
                      and any(r["egp"] == c for r in full)]}
    print(f"\n{'='*66}\nFULL PANEL — complete cases on four predictors\n{'='*66}")
    print(f"class mix: {dict(Counter(r['egp'] for r in full))}")
    print(f"edu mix:   {dict(Counter(r['edu'] for r in full))}")
    for b in (["cohort"], ["class"], ["edu"], ["prominence"]):
        report(full, b, cats, f"{b[0]} ALONE (same sample)")
    report(full, ["cohort", "class", "edu", "prominence"], cats,
           "JOINT — all four")

    # ---- occ panel: the same, intersected with occupational coverage ----
    occ = load_occ()
    for r in ok:
        r["occ_raw"] = occ.get(depth_key(r["member"]))
    occp = [r for r in full if r.get("occ_raw") is not None]
    zscore_occ(occp)
    catso = {"class": [c for c in PE.EGP if c != "I"
                       and any(r["egp"] == c for r in occp)]}
    print(f"\n{'='*66}\nOCC PANEL — intersected with occupational-score "
          f"coverage\n{'='*66}")
    print(f"class mix: {dict(Counter(r['egp'] for r in occp))}")
    print(f"edu mix:   {dict(Counter(r['edu'] for r in occp))}")
    for b in (["cohort"], ["class"], ["edu"], ["prominence"], ["occ"]):
        report(occp, b, catso, f"{b[0]} ALONE (same sample)")
    report(occp, ["cohort", "class", "edu", "prominence"], catso,
           "JOINT — four blocks (occ-panel sample)")
    report(occp, ["cohort", "class", "edu", "prominence", "occ"], catso,
           "JOINT — plus the occupational block")

    # ---- provinces: add office -------------------------------------------
    office = load_office()
    for r in ok:
        r["office"] = office.get(depth_key(r["member"]))
    prov = [r for r in full if r.get("office") is not None]
    if len(prov) > 80:
        catsp = {"class": [c for c in PE.EGP if c != "I"
                           and any(r["egp"] == c for r in prov)]}
        print(f"\n{'='*66}\nPROVINCES — the same, plus ministerial office"
              f"\n{'='*66}")
        print(f"class mix: {dict(Counter(r['egp'] for r in prov))}")
        report(prov, ["cohort", "class", "edu", "prominence"], catsp,
               "JOINT without office (same sample)")
        report(prov, ["cohort", "class", "edu", "prominence", "office"],
               catsp, "JOINT with office")
    else:
        print(f"\nprovince+office complete cases: {len(prov)} — too few")


if __name__ == "__main__":
    main()
