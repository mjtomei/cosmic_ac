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
  class       EGP category, baseline class I
  education   ordered academic ladder (professional excluded -- it is off the
              ladder, not a rung of it), plus a professional indicator
  prominence  log(Wikipedia article length)
  office      share of career words spoken under a rank marker ("Hon. <name>")

COVERAGE IS THE BINDING CONSTRAINT, and it differs per predictor, so the model
is reported as a ladder of nested samples rather than one number:

  full panel      cohort + class + education + prominence
  provinces only  the same, plus office -- only the eight Canadian provinces
                  mark rank in the record (UK Hansard prints ministers under
                  their own names), so office cannot enter the panel model

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
    for f in ("provinces/wiki_depth.json", "wiki_depth_t1.json"):
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


def design(rows, blocks, cats):
    """(y, X, index map) for the requested predictor blocks."""
    y, X, idx = [], [], {}
    col = 1
    for b in blocks:
        if b == "class":
            idx["class"] = list(range(col, col + len(cats["class"])))
            col += len(cats["class"])
        elif b == "edu":
            idx["edu"] = [col, col + 1]        # ladder rung + professional
            col += 2
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
                row += [float(LV.index(r["edu"]))
                        if r["edu"] != "professional" else 0.0,
                        1.0 if r["edu"] == "professional" else 0.0]
            elif b == "prominence":
                row.append(r["logdepth"])
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
            for j, nm in zip(ii, ("edu ladder/rung", "edu professional")):
                bb, se = beta[j], math.sqrt(V[j, j])
                print(f"    {nm:<16}{bb:>+8.3f}  t {bb/se:+.2f}"
                      f"{' *' if abs(bb/se) > 1.96 else ''}")
        else:
            j = ii[0]
            bb, se = beta[j], math.sqrt(V[j, j])
            print(f"    {b:<16}{bb:>+8.3f}  t {bb/se:+.2f}"
                  f"{' *' if abs(bb/se) > 1.96 else ''}")
        if len(ii) > 1:
            W, k, p = MLE.wald(beta, V, ii)
            print(f"      joint Wald chi2={W:.1f}, df={k}, p={p:.4f}")


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
    cats = {"class": [c for c in PE.EGP if c != "I"
                      and sum(1 for r in full if r["egp"] == c) > 25]}
    print(f"\n{'='*66}\nFULL PANEL — complete cases on four predictors\n{'='*66}")
    print(f"class mix: {dict(Counter(r['egp'] for r in full))}")
    for b in (["cohort"], ["class"], ["edu"], ["prominence"]):
        report(full, b, cats, f"{b[0]} ALONE (same sample)")
    report(full, ["cohort", "class", "edu", "prominence"], cats,
           "JOINT — all four")

    # ---- provinces: add office -------------------------------------------
    office = load_office()
    for r in ok:
        r["office"] = office.get(depth_key(r["member"]))
    prov = [r for r in full if r.get("office") is not None]
    if len(prov) > 80:
        catsp = {"class": [c for c in PE.EGP if c != "I"
                           and sum(1 for r in prov if r["egp"] == c) > 15]}
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
