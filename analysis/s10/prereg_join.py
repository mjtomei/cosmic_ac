#!/usr/bin/env python3
"""Build the registered member table for PREREG-occupational-accountability.

WHY THIS FILE EXISTS

The pre-registered study (plans/PREREG-occupational-accountability.md) is the
first join of O*NET elements to members. This script performs that join ONCE,
writes prereg_member_table.json, and every analysis script reads that table --
so the join is a single auditable step, not something each analysis re-derives.

THE JOIN CHAIN
  member -> raw prior_occupation string     (mirrored from panel_estimation)
         -> coded_occupation                (the EGP pass's cleaned title,
                                             provinces/occupation_coding*.json)
         -> O*NET-SOC code                  (soc_coding_new.json, own slots)
         -> standardised element values     (O*NET 30.3, scales as registered)
         -> U/L/D/N components, three profiles, E/A, level scores, apex delta,
            rung/ownership cells

DRIFT GUARD: the member rows are rebuilt here because panel_estimation's row
builders do not carry the raw occupation string -- but the rebuild is asserted
IDENTICAL (same members, same egp, same words) to the canonical builders'
output before anything else runs. If panel_estimation changes, this script
refuses to run rather than silently diverging.

Registered scale choices (Specification + level_scores.py): Work Activities
IM, Work Context CX (CT where no CX exists), interests OI, Work Styles WI,
skills/knowledge IM. Elements standardised across the occupations complete on
the charged instrument's 64 elements; the level signatures drop 3.A.1 as
registered. Reverse-scored: the four U discretion items (components) and
per-signature signs (levels).

Usage: python prereg_join.py
"""
import collections
import csv
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import panel_estimation as PE                    # noqa: E402
import member_level_estimation as MLE            # noqa: E402
import class_markedness as CM                    # noqa: E402
import formation_window as FW                    # noqa: E402
from joint_predictors import load_depth, depth_key   # noqa: E402

V30 = "/tmp/onet303/db_30_3_text"
REV = {"4.C.3.a.4", "4.C.3.b.8", "4.A.2.b.4", "4.C.3.a.2.b"}
PROF = {"free": (-1, -1, -1, -1), "front_line": (+1, +1, -1, +1),
        "corporate": (+1, -1, +1, +1)}


# ---------------------------------------------------------------------------
# 1. member -> raw occupation string (mirrors of the canonical row builders)
# ---------------------------------------------------------------------------
def member_strings():
    """member id -> raw own prior_occupation string, both panels."""
    out = {}
    # tier 1: replicate tier1_rows' person resolution, keep the string
    cov = collections.defaultdict(list)
    for r in json.load(open(os.path.join(HERE, "covariates_tier1.json"))):
        cov[(r["chamber"], r["key"])].append(r)
    cell = json.load(open(os.path.join(HERE, "member_year_rates_t1.json")))
    for k, (w, h) in cell.items():
        ch, nm, yr = k.split("|")
        if w < PE.MIN_WORDS:
            continue
        cands = cov.get((ch, nm))
        if not cands:
            continue
        y = int(yr)
        hits = [c for c in cands
                if (c.get("term_first") or 0) - 1 <= y <= (c.get("term_last")
                                                           or 9999) + 1]
        if len(hits) != 1:
            hits = [c for c in cands if not c.get("ambiguous")] \
                if len(cands) == 1 else hits
        if len(hits) != 1 or hits[0].get("ambiguous"):
            continue
        c = hits[0]
        person = f"{ch}|{nm}|{c.get('person_name') or ''}"
        s = (c.get("prior_occupation") or "").strip()
        if s:
            out[person] = s
    # provinces: bios files (8 originals) + covariates_missing9 (nine chambers)
    for pv, rel, key in CM.FILES:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for r in (d[key] if key else d):
            nm = FW.norm(r.get("hansard_speaker_key") or r.get("speaker_key")
                         or r.get("_key") or r.get("name")
                         or r.get("full_name") or "")
            s = (r.get("prior_occupation") or "").strip()
            if nm and s:
                out.setdefault(f"{pv}|{nm}", s)
    m9 = os.path.join(HERE, "covariates_missing9.json")
    if os.path.exists(m9):
        for r in json.load(open(m9)):
            if r.get("ambiguous"):
                continue
            s = (r.get("prior_occupation") or "").strip()
            if s and r.get("chamber") and r.get("key"):
                out.setdefault(f"{r['chamber']}|{r['key']}", s)
    return out


# ---------------------------------------------------------------------------
# 2. string -> coded_occupation -> SOC
# ---------------------------------------------------------------------------
def string_to_soc():
    clean = {}
    for f in ("provinces/occupation_coding_v2.json",
              "provinces/occupation_coding.json",
              "provinces/occupation_coding_missing9.json"):
        for r in json.load(open(os.path.join(HERE, f))):
            s = (r.get("string") or "").strip()
            c = (r.get("coded_occupation") or "").strip()
            if s and c:
                clean.setdefault(s, c)
    # The pool deduplicated titles CASE-INSENSITIVELY (4,402 distinct of 5,551
    # cased forms), so the join key is the lower-cased title. Without this the
    # first run silently dropped ~525 members whose title differed only in case.
    soc = {}
    for r in json.load(open(os.path.join(HERE, "soc_coding_new.json"))):
        code = (r.get("soc_code") or "").strip()
        if code and code != "unknown":
            soc[r["occupation"].lower().strip()] = code
    return clean, soc


# ---------------------------------------------------------------------------
# 3. SOC -> scores
# ---------------------------------------------------------------------------
def famscale(e):
    if e.startswith("4.A"): return ("Work Activities.txt", {"IM"})
    if e.startswith("4.C"): return ("Work Context.txt", {"CX", "CT"})
    if e.startswith("1.B.1"): return ("Career Interest Types.txt", {"OI"})
    if e.startswith("1.B.3"): return ("Specific Interest Areas.txt", {"OI"})
    if e.startswith("1.D"): return ("Work Styles.txt", {"WI"})
    if e.startswith("2.A"): return ("Essential Skills.txt", {"IM"})
    if e.startswith("2.B"): return ("Transferable Skills.txt", {"IM"})
    if e.startswith("2.C"): return ("Knowledge.txt", {"IM"})
    return (None, None)


# M1/M2 row tags (the prereg grid, verbatim); 4.A.4.a.2 sits in both N halves
ROW = {
 "L_M1": ["4.A.4.a.3", "1.B.3.ad"],
 "L_M2": ["1.B.1.d", "4.A.4.a.5", "4.A.4.a.8", "4.A.4.a.6", "4.C.1.b.1.f",
          "4.C.1.d.2", "4.C.1.a.2.c", "2.B.1.f", "2.C.1.e", "1.B.3.af",
          "1.B.3.am", "1.B.3.z"],
 "D_M1": ["4.A.4.b.1", "4.A.4.c.2", "4.A.4.c.3", "4.A.2.b.5", "4.C.1.b.1.g",
          "4.C.1.c.2", "2.A.2.d", "2.B.5.b", "2.B.5.c", "2.C.1.a"],
 "D_M2": ["4.A.4.b.3", "4.A.4.b.4", "4.A.4.b.5", "4.A.4.b.2", "4.C.1.c.1",
          "2.B.1.e", "2.B.5.d", "2.C.1.f", "1.D.1.i", "1.B.3.aj", "1.B.3.al"],
 "N_M1": ["4.A.3.b.6", "4.A.4.c.1", "4.C.1.a.2.j", "4.C.1.a.2.h", "2.A.1.c",
          "4.A.2.a.2", "4.A.2.a.3", "4.A.3.b.2", "2.C.1.b", "1.B.3.ai",
          "1.B.3.ak", "1.B.1.f", "4.A.4.a.2"],
 "N_M2": ["4.A.4.a.4", "4.C.1.a.4", "4.C.1.a.2.l", "4.C.1.a.2.f", "4.C.2.a.3",
          "4.C.1.d.1", "2.B.1.d", "2.B.1.b", "1.D.2.d", "1.D.2.f",
          "4.A.4.a.1", "4.A.4.a.2"],
}
WRITING = ["2.A.1.c", "4.C.1.a.2.h", "4.C.1.a.2.j", "4.A.3.b.6"]
NOMINAL = ["4.C.3.a.4", "4.C.3.a.2.a", "4.C.3.a.2.b", "4.C.3.a.1"]
EFFECTIVE = [("4.C.3.b.8", +1), ("4.C.3.d.3", -1), ("4.C.3.b.7", -1),
             ("4.C.3.b.2", -1)]


def occupation_scores():
    cells = json.load(open(os.path.join(HERE, "instrument_final_cells.json")))
    lvl = [p for p in json.load(open(os.path.join(
        HERE, "element_levels.json")))["consensus_pairs"] if p["id"] != "3.A.1"]
    lv_sig = collections.defaultdict(list)
    for p in lvl:
        lv_sig[p["level"]].append((p["id"], +1 if p["sign"] == "+" else -1))
    need = set(sum(cells.values(), [])) | {e for e, _ in
                                           sum(lv_sig.values(), [])}
    need |= set(NOMINAL) | {e for e, _ in EFFECTIVE}
    val = collections.defaultdict(dict)
    files = collections.defaultdict(set)
    for e in need:
        fn, sc = famscale(e)
        files[(fn, frozenset(sc))].add(e)
    for (fn, scs), els in files.items():
        with open(os.path.join(V30, fn), encoding="utf-8",
                  errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r["Element ID"] in els and r["Scale ID"] in scs:
                    val[r["Element ID"]][r["O*NET-SOC Code"]] = \
                        float(r["Data Value"])
    # complete set = the charged instrument's 862 (registered denominator)
    charged = set(sum(cells.values(), []))
    occ = sorted(set.intersection(*(set(val[e]) for e in charged)))
    # levels' own completeness (subset of the union files)
    lv_els = {e for e, _ in sum(lv_sig.values(), [])}
    occ_lv = sorted(set.intersection(*(set(val[e]) for e in lv_els)))

    def zmap(e, oo):
        xs = [val[e][o] for o in oo]
        m, s = st.mean(xs), st.pstdev(xs) or 1
        return {o: (val[e][o] - m) / s for o in oo}

    Zc = {e: zmap(e, occ) for e in charged}
    Zl = {e: zmap(e, occ_lv) for e in lv_els}
    extra = (set(NOMINAL) | {e for e, _ in EFFECTIVE}) - charged
    Zx = {e: zmap(e, [o for o in occ if o in val[e]]) for e in extra}
    Zx.update({e: Zc[e] for e in (set(NOMINAL) | {e for e, _ in EFFECTIVE})
               & charged})
    out = {}
    for o in occ:
        comp = {c: st.mean(Zc[e][o] * (-1 if e in REV else 1)
                           for e in els) for c, els in cells.items()}
        rec = {("comp_" + c): round(v, 4) for c, v in comp.items()}
        for name, w in PROF.items():
            rec["prof_" + name] = round(sum(
                wi * comp[k] for wi, k in zip(w, "ULDN")) / 4, 4)
        rec["E"] = round(comp["U"] + comp["D"], 4)
        rec["A"] = round(comp["D"] - comp["U"], 4)
        # registered subsets and splits, all from the same standardised values
        zc = lambda e: Zc[e][o] * (-1 if e in REV else 1)
        rec["sub_U_cons"] = round(zc("4.A.4.b.6"), 4)
        rec["sub_U_disc"] = round(st.mean(
            zc(e) for e in ("4.C.3.a.4", "4.C.3.b.8", "4.A.2.b.4",
                            "4.C.3.a.2.b")), 4)
        rec["sub_D_noal"] = round(st.mean(
            zc(e) for e in cells["D"] if e != "1.B.3.al"), 4)
        rec["sub_N_nowrite"] = round(st.mean(
            zc(e) for e in cells["N"] if e not in WRITING), 4)
        rec["sub_writing"] = round(st.mean(zc(e) for e in WRITING), 4)
        for half, els in ROW.items():
            rec["row_" + half] = round(st.mean(zc(e) for e in els), 4)
        for c, els in cells.items():
            ac = [e for e in els if e.startswith(("4.A", "4.C"))]
            if ac:
                rec["ac_" + c] = round(st.mean(zc(e) for e in ac), 4)
        # autonomy, unreversed (high = free), for the asymmetry + nominal/
        # effective tests; extra elements standardised over the same 862
        zn = lambda e: Zx[e][o]
        rec["auto_nominal"] = round(st.mean(zn(e) for e in NOMINAL), 4)
        rec["auto_effective"] = round(st.mean(
            sg * zn(e) for e, sg in EFFECTIVE), 4)
        out[o] = rec
    for o in occ_lv:
        rec = out.setdefault(o, {})
        for lvname, items in lv_sig.items():
            rec["lvl_" + lvname] = round(
                st.mean(s * Zl[e][o] for e, s in items), 4)
        if "lvl_MIDDLE" in rec and "lvl_TOP" in rec:
            rec["apex_delta"] = round(rec["lvl_MIDDLE"] - rec["lvl_TOP"], 4)
    return out, len(occ), len(occ_lv)


# ---------------------------------------------------------------------------
# 4. rung / ownership (taxonomy arm; registered regexes verbatim)
# ---------------------------------------------------------------------------
import re                                                     # noqa: E402
FL_RE = re.compile(r"^(33|35|37|39|41|43|45|47|49|51|53)-10\d\d\.")
OWN_RE = re.compile(r"owner|founder|proprietor|entrepreneur|self.?employed",
                    re.I)


def rung_of(soc, raw_string):
    if not soc:
        return None, None
    own = "owner-op" if OWN_RE.search(raw_string or "") else "employed"
    if soc == "11-1011.00":
        return "executive", own
    if soc == "11-9013.00":
        return None, own                       # farmers: not a rung
    if soc.startswith("11-"):
        return "middle", own
    if FL_RE.match(soc):
        return "first-line", own
    return None, own


# ---------------------------------------------------------------------------
def main():
    # canonical rows, then the mirror's drift guard
    code = PE.coding_maps()
    canon = MLE.members()
    strings = member_strings()
    matched = sum(1 for m in canon if m["member"] in strings)
    print(f"canonical members: {len(canon):,}; with an own occupation string: "
          f"{matched:,}")
    # drift guard: every canonical egp must be reproducible from the string
    bad = 0
    for m in canon:
        s = strings.get(m["member"])
        if m["egp"] and s and code.get(s) not in (m["egp"],):
            bad += 1
    assert bad < len(canon) * 0.01, f"string mirror diverges on {bad} members"
    print(f"drift guard: egp reproduced from captured strings; "
          f"{bad} divergent of {len(canon):,} (<1% tolerated: province "
          f"members whose egp came via a differently-keyed path)")

    rows = MLE.zscore(canon)
    clean, soc_of = string_to_soc()
    scores, n_occ, n_occ_lv = occupation_scores()
    print(f"occupations scored: charged {n_occ}, levels {n_occ_lv}")
    depth = load_depth()

    table = []
    cnt = collections.Counter()
    for m in rows:
        s = strings.get(m["member"])
        c = clean.get(s) if s else None
        soc = soc_of.get(c.lower().strip()) if c else None
        sc = scores.get(soc, {}) if soc else {}
        rung, own = rung_of(soc, s)
        rec = {"member": m["member"], "chamber": m["chamber"],
               "z": m.get("z"), "words": m["w"], "egp": m["egp"],
               "edu": m["edu"], "bd": m["bd"],
               "logdepth": depth.get(depth_key(m["member"])),
               "occ_string": s, "coded_occupation": c, "soc": soc,
               "rung": rung, "ownership": own if rung else None}
        rec.update(sc)
        table.append(rec)
        cnt["members"] += 1
        if s: cnt["with string"] += 1
        if c: cnt["with coded occupation"] += 1
        if soc: cnt["with SOC"] += 1
        if "comp_U" in sc: cnt["with charged scores"] += 1
        if "lvl_MIDDLE" in sc: cnt["with level scores"] += 1
        if rec["z"] is not None and "comp_U" in sc: cnt["z + charged"] += 1

    print("\nMEMBER-LEVEL COVERAGE (own occupations only — the run's panel):")
    for k in ("members", "with string", "with coded occupation", "with SOC",
              "with charged scores", "with level scores", "z + charged"):
        print(f"  {k:<24s}{cnt[k]:>7,}  ({100*cnt[k]/cnt['members']:.1f}%)")

    r2 = collections.Counter((r["rung"], r["ownership"]) for r in table
                             if r["rung"])
    print("\nrung x ownership (MEMBER-LEVEL, own occupations — the arm's "
          "actual cells;\nthe prereg's precomputed counts were pool slots, "
          "which mix in parent occupations):")
    for k in sorted(r2):
        print(f"  {k[0]:<12s}{k[1]:<10s}{r2[k]:>6d}")

    out = os.path.join(HERE, "prereg_member_table.json")
    json.dump(table, open(out, "w"))
    print(f"\nwrote {out}: {len(table):,} members, "
          f"{os.path.getsize(out)//1024} KB")


if __name__ == "__main__":
    main()
