#!/usr/bin/env python3
"""Does a member's education or occupation predict their register level?

THE QUESTION, AND WHY IT IS ASKED MEMBER-LEVEL

The Canadian provinces crossed above the US House on the five-year mean in
2019, and the obvious compositional explanations -- AI prevalence, skilled
immigration, province-level post-secondary share -- all came back null at n=7.
formation_window.py found the thing that does carry: birth cohort, +1.05 per
1,000 words per decade later born, holding province and year fixed, and it
survives adding occupation and post-secondary.

This asks the composition question at the member level instead. Not "do
graduate-heavy chambers score higher", which is seven points and a prayer, but
"within one chamber, do members with more elite backgrounds use the register
more". That is n in the hundreds, holds jurisdiction fixed, absorbs the era
with year effects, and weights members by the words they actually spoke.

THE COVARIATE IS DAMAGED, AND THE DAMAGE IS THE INTERESTING PART

An eight-agent pass (2026-08-13) collected per-member education and occupation
from each legislature's own directory where one exists. Coverage on roster
rows: NS 5% · AB 26% · BC 48% · MB 48% · SK 54% · NL 60% · ON 66% · PE 81%.

Manitoba and Ontario are entirely English Wikipedia, because neither
legislature has ever published education -- verified against the official
directories and the Internet Archive, so a real absence rather than a search
failure. Those two then rank 2nd and 5th on coverage, which is the notability
artifact in plain sight: the provinces on the notability-weighted source are
the better-covered ones.

SOURCE IS THEREFORE CARRIED AS A VARIABLE, NOT APOLOGISED FOR. Every record
keeps the tier it came from, the cross-province regression is printed next to
a regression on source tier alone, and if register tracks "is this province on
Wikipedia" as well as it tracks graduate share, the printout says so in those
words. A confounder you can regress on is better than one you can only warn
about.

WITHIN-PROVINCE IS THE PRIMARY ANALYSIS, and two provinces are excluded from
the education arm by rule rather than by result:

  AB  the Assembly publishes bios only for SITTING members, so the covariate
      exists only for the 2019+ cohort while the corpus runs from 2006. A
      covariate that is a cohort marker wearing an education label would
      reproduce formation_window's birth-year finding and look like
      confirmation.
  NS  education is known for five unique people; the directory has no such
      field.

Both keep their occupation column, which is the better-covered variable
everywhere -- 33-99%, near-census in NS (99%), SK (96%), BC (92%) and ON (89%).
A legislature that will not say where someone studied will usually say what
they did.

WEIGHTING. Members are weighted by words spoken. Unweighted, a backbencher
with 9,000 words counts as much as a minister with 300,000, and a member's rate
over a few thousand words is mostly noise.

Usage:
  python covariate_study.py --build-cache   # scan the corpus once (~10 min)
  python covariate_study.py                 # the report
"""
import argparse
import csv
import glob
import json
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "member_year_rates.json")
sys.path.insert(0, HERE)
import formation_window as FW               # noqa: E402

# The tier each province's covariate came from. Carried in the data structure
# because a confounder that lives only in a comment is a confounder that gets
# forgotten.
SOURCE_TIER = {"AB": "official", "BC": "official", "MB": "wikipedia",
               "NL": "official", "NS": "official", "ON": "wikipedia",
               "PE": "official", "SK": "official"}

EDU_EXCLUDE = {"AB", "NS"}          # see the docstring; excluded by rule
MIN_WORDS = 8000                    # same floor formation_window uses
GRAD = {"graduate", "professional"}

FILES = [("AB", "provinces/ab_education_official.json", "records"),
         ("BC", "provinces/bc_member_education.json", "records"),
         ("MB", "provinces/mb_education_occupation.json", "records"),
         ("NL", "provinces/nl_education_occupation.json", None),
         ("NS", "provinces/ns_member_bios.json", None),
         ("ON", "provinces/on_member_education.json", None),
         ("PE", "provinces/pe_member_education.json", "records"),
         ("SK", "provinces/sk_legislature_bios.json", None)]


def build_cache():
    """(prov, speaker, year) -> [words, instrument hits], written to JSON."""
    style = {r["word"].lower() for r in
             csv.DictReader(open(os.path.join(HERE, "kobak_excess_words.csv")))
             if r["type"] == "style" and r["word"].isalpha()}
    cell = defaultdict(lambda: [0, 0])
    for path in sorted(glob.glob(os.path.join(HERE, "provinces",
                                              "segments_*.jsonl"))):
        for line in open(path):
            d = json.loads(line)
            if not d.get("scoreable"):
                continue
            nm = FW.norm(d.get("speaker", ""))
            if not nm or FW.ROLE.match(nm):
                continue
            t = FW.TOKEN_RE.findall(d["text"].lower())
            c = cell[f"{d['prov']}|{nm}|{d['date'][:4]}"]
            c[0] += len(t)
            c[1] += sum(1 for x in t if x in style)
    json.dump(cell, open(CACHE, "w"))
    print(f"wrote {os.path.basename(CACHE)}: {len(cell):,} member-years")


ALLSOURCE = os.path.join(HERE, "provinces", "member_allsource.json")
DEPTH = os.path.join(HERE, "provinces", "wiki_depth.json")


def load_covariates(source="official"):
    """prov -> normalised name -> {edu, occ, tier}.

    source="official"   the per-province directory scrape. Even-ish coverage,
                        low yield, and not notability-weighted except in MB and
                        ON where no official education field exists at all.
    source="allsource"  the per-member web search. Higher coverage and openly
                        notability-weighted: of 800 members with an education
                        level, only 74 have it from a non-Wikipedia source.

    Running both is the sensitivity check. If a finding holds on the official
    subset and on the all-source set with article depth controlled, it is not
    an artifact of who has a long Wikipedia article.
    """
    out = defaultdict(dict)
    if source == "allsource":
        for r in json.load(open(ALLSOURCE)):
            nm = FW.norm(r.get("name") or "")
            if not nm:
                continue
            e = (r.get("education_level") or "").strip().lower()
            o = (r.get("occupation_category") or "").strip().lower()
            tiers = r.get("evidence_tiers") or []
            out[r["prov"]][nm] = {
                "edu": e if e and e != "unknown" else None,
                "occ": o if o and o != "unknown" else None,
                # The tier is now per MEMBER, not per province: this file
                # records where each value actually came from.
                "tier": "wikipedia" if tiers == ["wikipedia"] else "mixed"}
        return out
    for prov, rel, key in FILES:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        recs = d[key] if key else d
        for r in recs:
            # Join on the file's OWN speaker key where it supplies one. BC,
            # NL and SK carry hansard_speaker_key / speaker_key / _key, and
            # joining those provinces on `name` instead matched 13-15% of
            # members and silently reduced the class test to a four-province
            # study -- BC, NL and SK each contributed about 2% of their words.
            nm = FW.norm(r.get("hansard_speaker_key") or r.get("speaker_key")
                         or r.get("_key") or r.get("name")
                         or r.get("full_name") or "")
            if not nm:
                continue
            e = (r.get("education_level") or "").strip().lower()
            o = (r.get("occupation_category") or "").strip().lower()
            out[prov][nm] = {"edu": e if e and e != "unknown" else None,
                             "occ": o if o and o != "unknown" else None,
                             "tier": SOURCE_TIER.get(prov, "?")}
    return out


def load_depth():
    """(prov, normalised name) -> Wikipedia article length in bytes.

    The notability instrument. WP:NPOL gives essentially every member an
    article, so existence says nothing; length says a great deal. Members whose
    education is known have 1.80x the median article length of those whose is
    not, so depth is the mechanism behind the missingness and belongs in the
    regression rather than in a caveat.
    """
    if not os.path.exists(DEPTH):
        return {}
    out = {}
    for k, v in json.load(open(DEPTH)).items():
        prov, _, name = k.partition("|")
        if v.get("length"):
            out[(prov, FW.norm(name))] = v["length"]
    return out


def member_rows(cov, depth=None):
    """One row per member-year with a joined covariate (and article depth)."""
    cell = json.load(open(CACHE))
    agg = defaultdict(lambda: [0, 0])
    for k, (w, h) in cell.items():
        pv, nm, yr = k.split("|")
        agg[(pv, nm, yr)][0] += w
        agg[(pv, nm, yr)][1] += h
    rows = []
    for (pv, nm, yr), (w, h) in agg.items():
        if w < MIN_WORDS:
            continue
        c = cov.get(pv, {}).get(nm)
        if not c:
            continue
        row = {"prov": pv, "name": nm, "year": int(yr), "words": w,
               "rate": h / w * 1000, "edu": c["edu"], "occ": c["occ"],
               "tier": c["tier"]}
        L = (depth or {}).get((pv, nm))
        # log, because article length spans 1.5k to 136k bytes and the
        # interesting contrast is stub-versus-substantial, not linear bytes.
        row["logdepth"] = math.log(L) if L else None
        rows.append(row)
    return rows


def wls(rows, xkey, label, extra=()):
    """Weighted OLS of rate on a covariate, with year fixed effects.

    `extra` names further columns to include, e.g. ("logdepth",) to condition
    on Wikipedia article length. Weighted by words, because a member's rate
    over a few thousand words is mostly noise.
    """
    keys = [xkey] + list(extra)
    sub = [r for r in rows if all(r.get(k) is not None for k in keys)]
    if len(sub) < 40:
        return None
    years = sorted({r["year"] for r in sub})[1:]      # first year is the base
    names = ["const", label] + list(extra) + [f"y{y}" for y in years]
    y, X = [], []
    for r in sub:
        sw = math.sqrt(r["words"])
        row = ([1.0, float(r[xkey])] + [float(r[k]) for k in extra]
               + [1.0 if r["year"] == yy else 0.0 for yy in years])
        y.append(r["rate"] * sw)
        X.append([v * sw for v in row])
    res = FW.ols(y, X, names)
    return (res, len(sub)) if res else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-cache", action="store_true")
    ap.add_argument("--source", default="official",
                    choices=("official", "allsource"))
    a = ap.parse_args()
    if a.build_cache:
        return build_cache()
    if not os.path.exists(CACHE):
        raise SystemExit("no cache; run --build-cache first")

    cov = load_covariates(a.source)
    depth = load_depth()
    print(f"COVARIATE STUDY [{a.source}] -- education and occupation vs register")
    print("=" * 68)
    print("\nCOVERAGE AND SOURCE. The Wikipedia provinces are not the")
    print("worst-covered ones, which is the notability artifact in plain view.\n")
    print(f"  {'prov':<6}{'source':<11}{'n':>5}{'edu':>6}{'  %':>6}"
          f"{'occ':>6}{'  %':>6}")
    for pv in sorted(cov):
        rs = list(cov[pv].values())
        n = len(rs)
        e = sum(1 for r in rs if r["edu"])
        o = sum(1 for r in rs if r["occ"])
        print(f"  {pv:<6}{SOURCE_TIER.get(pv,'?'):<11}{n:>5}{e:>6}"
              f"{100*e/n:>6.0f}{o:>6}{100*o/n:>6.0f}")

    rows = member_rows(cov, depth)
    for r in rows:
        r["grad"] = 1.0 if (r["edu"] in GRAD) else 0.0 if r["edu"] else None
    print(f"\n{len(rows):,} member-years joined, "
          f"{len({(r['prov'], r['name']) for r in rows}):,} members, "
          f"{len({r['prov'] for r in rows})} provinces")

    # ---------------------------------------------------------- occupation
    print("\n" + "=" * 68)
    print("OCCUPATION -- the better-covered variable, within province\n")
    print("Weighted mean register rate per 1,000 words, by prior occupation.")
    print("Read down a column, not across: levels differ between chambers.\n")
    occs = sorted({r["occ"] for r in rows if r["occ"]})
    provs = sorted({r["prov"] for r in rows})
    print(f"  {'occupation':<28}" + "".join(f"{p:>7}" for p in provs))
    for o in occs:
        cells = []
        for p in provs:
            s = [r for r in rows if r["prov"] == p and r["occ"] == o]
            w = sum(r["words"] for r in s)
            cells.append(f"{sum(r['rate']*r['words'] for r in s)/w:>7.1f}"
                         if w > 200_000 else f"{'-':>7}")
        print(f"  {o[:27]:<28}" + "".join(cells))

    # ----------------------------------------------------------- education
    print("\n" + "=" * 68)
    print("EDUCATION -- within province, graduate/professional vs not\n")
    print(f"AB and NS excluded by rule (see docstring), not by result.\n")
    print(f"  {'prov':<6}{'source':<11}{'n':>6}{'grad share':>12}"
          f"{'effect':>10}{'se':>8}{'t':>7}")
    xs, ys, tiers = [], [], []
    for pv in provs:
        if pv in EDU_EXCLUDE:
            print(f"  {pv:<6}{SOURCE_TIER.get(pv,'?'):<11}{'':>6}"
                  f"{'excluded by rule':>32}")
            continue
        sub = [r for r in rows if r["prov"] == pv and r["grad"] is not None]
        if len(sub) < 40:
            print(f"  {pv:<6}{SOURCE_TIER.get(pv,'?'):<11}{len(sub):>6}"
                  f"{'too few':>12}")
            continue
        w = sum(r["words"] for r in sub)
        share = sum(r["grad"] * r["words"] for r in sub) / w
        out = wls(sub, "grad", "grad")
        if not out:
            continue
        (res, n) = out
        b, se = res["grad"]
        print(f"  {pv:<6}{SOURCE_TIER.get(pv,'?'):<11}{n:>6}{100*share:>11.0f}%"
              f"{b:>+10.3f}{se:>8.3f}{b/se if se else 0:>7.2f}")
        xs.append(share)
        ys.append(sum(r["rate"] * r["words"] for r in sub) / w)
        tiers.append(1.0 if SOURCE_TIER.get(pv) == "wikipedia" else 0.0)

    # ------------------------------------------------------- notability arm
    print("\n" + "=" * 68)
    print("NOTABILITY -- does the register track how much has been written?\n")
    dep = [r for r in rows if r.get("logdepth") is not None]
    if len(dep) >= 40:
        out = wls(dep, "logdepth", "logdepth")
        if out:
            (res, nn) = out
            b, se = res["logdepth"]
            print(f"  register on log(article bytes), province-pooled, year FE")
            print(f"    {b:+.3f} per log-byte (se {se:.3f}, t {b/se:>+5.2f}), "
                  f"n={nn}\n")
            if abs(b / se) > 2:
                print("  Article depth PREDICTS register on its own. Since the")
                print("  education covariate is present mostly for members with")
                print("  long articles, any education effect has to be judged")
                print("  with depth in the model, not without it.\n")
            else:
                print("  Article depth does not predict register by itself,")
                print("  which is the reassuring case: the notability of a")
                print("  member is not visible in how they speak.\n")

        print("  EDUCATION EFFECT, WITH AND WITHOUT THE DEPTH CONTROL")
        print(f"  {'prov':<6}{'n':>6}{'raw':>10}{'+depth':>10}{'shift':>9}")
        for pv in sorted({r["prov"] for r in dep}):
            if pv in EDU_EXCLUDE:
                continue
            sub = [r for r in dep if r["prov"] == pv
                   and r["grad"] is not None]
            a1 = wls(sub, "grad", "grad")
            a2 = wls(sub, "grad", "grad", extra=("logdepth",))
            if not a1 or not a2:
                continue
            b1 = a1[0]["grad"][0]
            b2 = a2[0]["grad"][0]
            print(f"  {pv:<6}{a1[1]:>6}{b1:>+10.3f}{b2:>+10.3f}"
                  f"{b2-b1:>+9.3f}")
        print("\n  A coefficient that survives the depth control is not an")
        print("  artifact of who has a long article. One that collapses is.")
    else:
        print("  no depth data joined -- run wiki_depth.py")

    # ------------------------------------------------- cross-province, honest
    print("\n" + "=" * 68)
    print("CROSS-PROVINCE -- computed, with its confounder beside it\n")
    if len(xs) >= 4:
        rg = FW_spearman(xs, ys)
        rt = FW_spearman(tiers, ys)
        print(f"  register vs graduate share   rho = {rg:+.2f}   (n={len(xs)})")
        print(f"  register vs 'on Wikipedia'   rho = {rt:+.2f}   (n={len(xs)})")
        print()
        if abs(rt) >= abs(rg) - 0.15:
            print("  The source tier tracks the outcome about as well as the")
            print("  covariate does. On this data a cross-province education")
            print("  result is not separable from which source the province")
            print("  happened to have, and should not be reported as one.")
        else:
            print("  Graduate share outruns source tier here, but with this n")
            print("  that is a hint and not a finding.")
    else:
        print(f"  only {len(xs)} provinces survive the exclusions -- too few")
        print("  to correlate. That is the honest outcome, not a failure.")


def FW_spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")

    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            for k in range(i, j + 1):
                r[s[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((p - mx) * (q - my) for p, q in zip(rx, ry))
    den = math.sqrt(sum((p - mx) ** 2 for p in rx)
                    * sum((q - my) ** 2 for q in ry))
    return num / den if den else float("nan")


if __name__ == "__main__":
    main()
