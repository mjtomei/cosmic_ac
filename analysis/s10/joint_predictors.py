#!/usr/bin/env python3
"""All the register's member-level predictors in one model.

WHY

Cohort, class, education, prominence and the occupational ladders have each
been estimated in their own subsection, each defended against one or two of
the others pairwise. Nobody has put them in a single regression, so "which of
these survives the others" has never been answered directly and the text has
no principled basis for how much weight to give each.

SPECIFICATION — the canonical member-level one (member_level_estimation.py):
one observation per legislator (career rate over >= 8,000 words), EQUAL weight,
register z-scored within each legislature against that chamber's full member
population, HC1 errors, block Wald over every predictor's term vector (1-df
blocks included, where it is the t test).

  cohort      birth decade, centred at 1960
  class       EGP category, baseline class I -- EVERY category present enters
              as a dummy (no small-cell fold into baseline; the SEs speak)
  education   level dummies, bachelor baseline (the education table's
              coding), with the graduate rung split by recorded degree into
              master's / doctorate / graduate-unrecorded (edu_split_graduate)
  prominence  quintiles of Wikipedia article length, Q1 baseline -- the bins,
              not a line, because the shape is not linear (Appendix D.3)
  dir ladder  the directional altitude ladder, all four levels (free, bottom,
              middle, top), each per sd on the estimation sample
  coded ladder the coded altitude ladder, all four levels likewise. NOTE
              apex_delta == lvl_MIDDLE - lvl_TOP exactly (verified corr -1.0),
              so the prereg's apex term is subsumed by this block and must
              not enter beside it
  indoors     O*NET Work Context "Indoors, Environmentally Controlled" for
              the member's SOC code, per sd
  office      share of career words spoken under a rank marker ("Hon. <name>")

COVERAGE IS THE BINDING CONSTRAINT, and it differs per predictor, so the model
is reported as a ladder of nested samples rather than one number:

  full panel      cohort + class + education + prominence
  occ panel       the same members intersected with occupational-score
                  coverage; the four-block joint refit on this sample, then
                  the two ladder blocks and indoors added
  provinces only  the full-panel four, plus office -- only the eight Canadian
                  provinces mark rank in the record (UK Hansard prints
                  ministers under their own names), so office cannot enter
                  the panel model

Each block is also shown alone on the SAME sample as the joint fit, so an
attenuation is read against its own baseline rather than against a coefficient
estimated on a different set of members.

Usage: python joint_predictors.py
"""
import csv
import glob
import json
import math
import os
import re
import sys
from collections import Counter

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

# vs bachelor; "graduate" = a graduate degree whose kind no source records
# (edu_split_graduate.py splits the rest into master's and doctorate);
# "none" enters as its own dummy -- folding its 14 members into the
# bachelor baseline would repeat the class small-cell mistake. LV_OK is
# the post-split membership filter (the split renames graduate members,
# so filtering on LV alone would silently drop them).
EDU_DUM = ["none", "secondary", "college", "master", "doctorate",
           "graduate", "professional"]
LV_OK = set(LV) | {"master", "doctorate"}
PROM_DUM = ["Q2", "Q3", "Q4", "Q5"]                              # vs Q1
DIR_KEYS = ["dir_free", "dir_bottom", "dir_middle", "dir_top"]
LVL_KEYS = ["lvl_FREE", "lvl_BOTTOM", "lvl_MIDDLE", "lvl_TOP"]
INDOORS_ID = "4.C.2.a.1.a"   # O*NET Work Context: Indoors, Env. Controlled


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


def apply_edu_split(rows):
    """refine edu == graduate into master / doctorate where a source records
    the degree (graduate_degree_split.json); the rest stay graduate."""
    p = os.path.join(HERE, "graduate_degree_split.json")
    sp = json.load(open(p))
    n = Counter()
    for r in rows:
        if r.get("edu") != "graduate":
            continue
        parts = r["member"].split("|")
        c = sp["provkey"].get("|".join(parts[:2])) or \
            (sp["t1key"].get(parts[1]) if len(parts) > 1 else None)
        if c:
            r["edu"] = c
        n[c or "unrecorded"] += 1
    print("graduate split on panel:", dict(n))


def load_occ():
    """member key -> the 8 ladder levels + indoors, raw.

    Ladder levels from the committed prereg member table; Indoors is the
    O*NET Work Context value for the member's SOC code, cached to
    indoors_by_soc.json so the model does not depend on the /tmp O*NET
    extraction surviving."""
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
        if r.get("dir_middle") is not None and r.get("soc") in val:
            out[depth_key(r["member"])] = (
                [r[k] for k in DIR_KEYS] + [r[k] for k in LVL_KEYS]
                + [val[r["soc"]]])
    return out


def zscore_occ(sample):
    """attach per-sd occ columns, standardised on THIS estimation sample."""
    for i in range(9):
        v = np.array([r["occ_raw"][i] for r in sample], float)
        m, sd = v.mean(), v.std() or 1.0
        for r, x in zip(sample, v):
            r.setdefault("occ_z", [0.0] * 9)[i] = (x - m) / sd


def assign_quintiles(sample):
    """attach r['promq'] in 0..4: quintile of logdepth on THIS sample."""
    order = sorted(range(len(sample)), key=lambda i: sample[i]["logdepth"])
    for rank, i in enumerate(order):
        sample[i]["promq"] = min(4, rank * 5 // len(sample))


def design(rows, blocks, cats):
    """(y, X, index map) for the requested predictor blocks."""
    y, X, idx = [], [], {}
    col = 1
    widths = {"class": lambda: len(cats["class"]),
              "edu": lambda: len(cats["edu"]),
              "prominence": lambda: len(PROM_DUM), "dirlad": lambda: 4,
              "codlad": lambda: 4}
    for b in blocks:
        w = widths[b]() if b in widths else 1
        idx[b] = list(range(col, col + w))
        col += w
    for r in rows:
        row = [1.0]
        for b in blocks:
            if b == "cohort":
                row.append(r["bd"])
            elif b == "class":
                row += [1.0 if r["egp"] == c else 0.0 for c in cats["class"]]
            elif b == "edu":
                row += [1.0 if r["edu"] == e else 0.0
                        for e in cats["edu"]]
            elif b == "prominence":
                row += [1.0 if r["promq"] == q else 0.0 for q in (1, 2, 3, 4)]
            elif b == "dirlad":
                row += r["occ_z"][0:4]
            elif b == "codlad":
                row += r["occ_z"][4:8]
            elif b == "indoors":
                row.append(r["occ_z"][8])
            elif b == "office":
                row.append(r["office"])
        X.append(row)
        y.append(r["z"])
    return y, X, idx


NAMES = {"class": lambda cats: [f"class {c}" for c in cats["class"]],
         "edu": lambda cats: [f"edu {e}" for e in cats["edu"]],
         "prominence": lambda cats: [f"prom {q}" for q in PROM_DUM],
         "dirlad": lambda cats: [f"dir {k.split('_')[1]}" for k in DIR_KEYS],
         "codlad": lambda cats: [f"lvl {k.split('_')[1]}" for k in LVL_KEYS]}


def report(rows, blocks, cats, label):
    y, X, idx = design(rows, blocks, cats)
    beta, V = MLE.ols_hc1(y, X)
    print(f"\n{label}   n = {len(rows):,}")
    for b in blocks:
        ii = idx[b]
        names = NAMES[b](cats) if b in NAMES else [b]
        for j, nm in zip(ii, names):
            bb, se = beta[j], math.sqrt(V[j, j])
            print(f"    {nm:<16}{bb:>+8.3f}  t {bb/se:+.2f}"
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
    apply_edu_split(ok)
    print(f"{len(ok):,} legislators with birth year and a z score, "
          f"{len({r['chamber'] for r in ok})} chambers")
    print("coverage among them: "
          f"class {sum(1 for r in ok if r['egp'] in PE.EGP_RANK):,}, "
          f"education {sum(1 for r in ok if r['edu'] in LV):,}, "
          f"prominence {sum(1 for r in ok if r['logdepth'] is not None):,}")

    # ---- full panel: cohort + class + education + prominence -------------
    full = [r for r in ok if r["egp"] in PE.EGP_RANK and r["edu"] in LV_OK
            and r["logdepth"] is not None]
    assign_quintiles(full)
    # every class present enters as a dummy: a small-cell filter here would
    # silently fold those members into baseline class I
    cats = {"class": [c for c in PE.EGP if c != "I"
                      and any(r["egp"] == c for r in full)],
            "edu": [e for e in EDU_DUM
                    if any(r["edu"] == e for r in full)]}
    print(f"\n{'='*66}\nFULL PANEL — complete cases on four predictors\n{'='*66}")
    print(f"class mix: {dict(Counter(r['egp'] for r in full))}")
    print(f"edu mix:   {dict(Counter(r['edu'] for r in full))}")
    print("prominence quintile bounds (log length): "
          + ", ".join(f"Q{q+1}<={max(r['logdepth'] for r in full if r['promq']==q):.2f}"
                      for q in range(5)))
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
    assign_quintiles(occp)
    catso = {"class": [c for c in PE.EGP if c != "I"
                       and any(r["egp"] == c for r in occp)],
             "edu": [e for e in EDU_DUM
                     if any(r["edu"] == e for r in occp)]}
    print(f"\n{'='*66}\nOCC PANEL — intersected with occupational-score "
          f"coverage\n{'='*66}")
    print(f"class mix: {dict(Counter(r['egp'] for r in occp))}")
    print(f"edu mix:   {dict(Counter(r['edu'] for r in occp))}")
    for b in (["cohort"], ["class"], ["edu"], ["prominence"],
              ["dirlad"], ["codlad"], ["indoors"]):
        report(occp, b, catso, f"{b[0]} ALONE (same sample)")
    report(occp, ["cohort", "class", "edu", "prominence"], catso,
           "JOINT — four blocks (occ-panel sample)")
    report(occp, ["cohort", "class", "edu", "prominence",
                  "dirlad", "codlad", "indoors"], catso,
           "JOINT — plus both ladders and indoors")
    # leave-one-out twins: is the surviving ladder an artifact of which twin
    # entered? and does class still die with only one ladder present?
    report(occp, ["cohort", "class", "edu", "prominence",
                  "dirlad", "indoors"], catso,
           "VARIANT — directional ladder only (coded absent)")
    report(occp, ["cohort", "class", "edu", "prominence",
                  "codlad", "indoors"], catso,
           "VARIANT — coded ladder only (directional absent)")

    # ---- provinces: add office -------------------------------------------
    office = load_office()
    for r in ok:
        r["office"] = office.get(depth_key(r["member"]))
    prov = [r for r in full if r.get("office") is not None]
    if len(prov) > 80:
        assign_quintiles(prov)
        catsp = {"class": [c for c in PE.EGP if c != "I"
                           and any(r["egp"] == c for r in prov)],
                 "edu": [e for e in EDU_DUM
                         if any(r["edu"] == e for r in prov)]}
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
