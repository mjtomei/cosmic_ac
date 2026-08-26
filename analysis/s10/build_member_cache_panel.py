#!/usr/bin/env python3
"""Member x style-word x year counts over ALL 22 panel chambers.

WHY

build_flight_member_cache.py built this asset for the eight Canadian
provinces only, and only for members already carrying an EGP class or a folk
ladder level. Three questions now need it panel-wide and unfiltered:

  peak_decomposition.py   the class profile's peak stability (§4.6b claims
                          "the peak does not migrate"), where member-level
                          and member-year aggregation disagree and the
                          disagreement has to be decomposed, not asserted;
  leadlag.py              per-WORD diffusion timing by status tier, which
                          needs each word separately rather than the pooled
                          407-word instrument;
  permeation_decompose.py the frequency-side within/composition split, which
                          is a statement about the whole panel and so cannot
                          be restricted to the coded subset.

So: one scan, every store, every speaker, all 407 style words.

STORES USED, AND WHY THESE ONES

The study's segment stores are versioned by collection round, and several
chambers have more than one file. The rule applied here is: take exactly the
set of files that covers each chamber once.

  provinces/segments_*.jsonl   (non-recursive glob, as build_flight_member_
      cache.py and covariate_study.py --build-cache both use). Seventeen
      chambers live here -- 8 Canadian provinces, 6 Australian states, and
      Scotland/Wales/Northern Ireland -- and the chamber is read off each
      row's own `prov` field rather than the file name. Each chamber has a
      base store (2006-2019), a `_fill` store (2011-2024), NI additionally a
      `_fill2` (2011-2012), and all but MB a `_2025` store (2025-2026).
      VERIFIED before this scan: for AB, MB, NI and NSW the stores share ZERO
      sitting dates and ZERO seg_ids pairwise, i.e. the fills cover dates the
      base lacks rather than re-covering them, so the union double-counts
      nothing. provinces/superseded/*_PREBUGFIX.jsonl is excluded because the
      glob is not recursive -- the same way every committed script excludes
      it.

  tier-1: exactly build_t1_cache.py's CORPORA map, unchanged, because that is
      the file set behind member_year_rates_t1.json and therefore behind the
      committed panel:
        US-HOUSE   us/segments_us_house.jsonl
        US-SENATE  us/segments_us_senate.jsonl
        UK         uk/segments_uk_deep.jsonl + uk/segments_uk_2023.jsonl
        IE         ie/segments_ie_en.jsonl
        CA-FED     ca/segments_ca2.jsonl
      The UK pair is the one non-obvious choice, so it was re-verified here:
      segments_uk_deep.jsonl spans 1985-2026 but contains NO 2023 dates at
      all, and segments_uk_2023.jsonl contains only 2023 -- the deep archive
      has a one-year hole and the second file is exactly its patch. The
      other UK stores (uk.jsonl, uk_long.jsonl, uk_within.jsonl) are earlier
      or narrower cuts of the same Hansard and would duplicate; likewise
      us/segments_us.jsonl, us_new.jsonl, *_pre_backfill.jsonl and
      *_within.jsonl on the US side, ca/segments_ca.jsonl, ca_en.jsonl,
      ca_within.jsonl on the Canadian, and ie/segments_ie.jsonl,
      ie_within.jsonl on the Irish.

  NOT included: the New Brunswick stores in the top-level directory
      (segments_all/_59th/_60th/_61s1.jsonl). NB is the DISCOVERY corpus and
      is held out of every panel estimate in this study (replication_
      protocol.md); the panel is 22 chambers without it.

FILTERS, identical to the committed builders: rows must be `scoreable`; the
speaker string is FW.norm()'d and must be non-empty and must not match
FW.ROLE (chair/minister/premier voice). Tokens are FW.TOKEN_RE over the
lower-cased text -- so `tot` here is the same word count that
member_year_rates*.json calls `words`, and sum(w.values()) is the same
quantity it calls instrument hits.

KEY. CHAMBER|normalised-speaker. For the provinces that is the panel's member
key exactly. For tier-1 the panel key is CHAMBER|norm|person-name, so the
cache key is its first two fields -- meaning a printed surname shared by two
sitting members collapses into one cache entry. That is the same compromise
build_flight_member_cache.py makes, and it is why the analyses downstream
read class from the panel rows and use the cache for word-level detail.

PRUNING. Members with fewer than 1,000 lifetime tokens AND no EGP class and
no folk level are dropped at write time: every analysis downstream has a
2,000-token floor, so they cannot enter one, and they are two thirds of the
key count.

WRITES member_cache_panel.json.gz:
  {"CH|member": {"egp": ..., "lvl": ..., "years": {year: {"tot": n,
                 "w": {word: count}}}}}

Usage: python build_member_cache_panel.py     # ~12 GB of jsonl, one pass
"""
import csv
import glob
import gzip
import json
import os
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW                      # noqa: E402
import panel_estimation as PE                      # noqa: E402

# tier-1 stores: build_t1_cache.py's CORPORA, verbatim
TIER1 = {
    "US-HOUSE": ["us/segments_us_house.jsonl"],
    "US-SENATE": ["us/segments_us_senate.jsonl"],
    "UK": ["uk/segments_uk_deep.jsonl", "uk/segments_uk_2023.jsonl"],
    "IE": ["ie/segments_ie_en.jsonl"],
    "CA-FED": ["ca/segments_ca2.jsonl"],
}
LVK = ["lvl_FREE", "lvl_BOTTOM", "lvl_MIDDLE", "lvl_TOP"]
MIN_LIFETIME = 1000


def style_words():
    return {r["word"].lower() for r in
            csv.DictReader(open(os.path.join(HERE, "kobak_excess_words.csv")))
            if r["type"] == "style" and r["word"].isalpha()}


def member_codes():
    """CH|norm -> (egp, folk level), from the committed panel + prereg table."""
    code = PE.coding_maps()
    egp = {}
    for r in PE.provincial_rows(code) + PE.tier1_rows(code)[0]:
        if r["egp"]:
            egp.setdefault("|".join(r["member"].split("|")[:2]), r["egp"])
    lvl = {}
    for r in json.load(open(os.path.join(HERE, "prereg_member_table.json"))):
        if r.get("lvl_MIDDLE") is not None:
            vals = [r[k] for k in LVK]
            lvl["|".join(r["member"].split("|")[:2])] = \
                LVK[vals.index(max(vals))].split("_")[1].lower()
    return egp, lvl


def scan(paths, chamber_of, out, canon, label):
    """One pass over `paths`, accumulating into `out`. chamber_of(row) -> str."""
    t0 = time.time()
    n_rows = n_kept = 0
    norm, role, tok = FW.norm, FW.ROLE, FW.TOKEN_RE
    for rel in paths:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p):
            print(f"  MISSING {rel}", flush=True)
            continue
        for line in open(p):
            d = json.loads(line)
            n_rows += 1
            if not d.get("scoreable", True):
                continue
            nm = norm(d.get("speaker", ""))
            if not nm or role.match(nm):
                continue
            date = d.get("date") or ""
            if len(date) < 4 or not date[:4].isdigit():
                continue
            ch = chamber_of(d)
            if not ch:
                continue
            n_kept += 1
            toks = tok.findall(d["text"].lower())
            y = out[f"{ch}|{nm}"][date[:4]]
            y[0] += len(toks)
            wd = y[1]
            for t in toks:
                c = canon.get(t)
                if c is not None:
                    wd[c] = wd.get(c, 0) + 1
    print(f"  {label:<10s} {n_rows:>9,} rows  {n_kept:>9,} kept  "
          f"{time.time() - t0:>7.1f}s", flush=True)


def main():
    style = style_words()
    canon = {w: w for w in style}                  # one shared key object/word
    print(f"style words: {len(style)}")
    egp, lvl = member_codes()
    print(f"coded members: egp {len(egp):,}  folk level {len(lvl):,}\n")

    out = defaultdict(lambda: defaultdict(lambda: [0, {}]))
    prov_paths = sorted(os.path.relpath(p, HERE) for p in
                        glob.glob(os.path.join(HERE, "provinces",
                                               "segments_*.jsonl")))
    print(f"PROVINCES: {len(prov_paths)} stores")
    scan(prov_paths, lambda d: d.get("prov"), out, canon, "provinces")
    for ch, files in TIER1.items():
        print(f"TIER-1 {ch}: {', '.join(files)}")
        scan(files, lambda d, _c=ch: _c, out, canon, ch)

    rec = {}
    dropped = 0
    for k, years in out.items():
        e, lv = egp.get(k), lvl.get(k)
        if e is None and lv is None and sum(v[0] for v in years.values()) \
                < MIN_LIFETIME:
            dropped += 1
            continue
        rec[k] = {"egp": e, "lvl": lv,
                  "years": {y: {"tot": v[0], "w": v[1]}
                            for y, v in sorted(years.items())}}
    path = os.path.join(HERE, "member_cache_panel.json.gz")
    with gzip.open(path, "wt") as f:
        json.dump(rec, f)

    chs = defaultdict(lambda: [0, 0, 0])           # chamber -> members, m-yrs, tokens
    for k, r in rec.items():
        c = chs[k.split("|")[0]]
        c[0] += 1
        c[1] += len(r["years"])
        c[2] += sum(v["tot"] for v in r["years"].values())
    print(f"\nwrote member_cache_panel.json.gz "
          f"({os.path.getsize(path) / 1e6:.1f} MB)")
    print(f"  members {len(rec):,}   (dropped {dropped:,} thin+uncoded)")
    print(f"  member-years {sum(v[1] for v in chs.values()):,}")
    print(f"  tokens {sum(v[2] for v in chs.values()) / 1e9:.2f}B")
    print(f"  chambers {len(chs)}\n")
    print(f"  {'chamber':<10}{'members':>9}{'m-years':>9}{'Mtokens':>10}"
          f"{'egp':>7}{'lvl':>7}")
    for c in sorted(chs, key=lambda c: -chs[c][2]):
        ne = sum(1 for k, r in rec.items()
                 if k.startswith(c + "|") and r["egp"])
        nl = sum(1 for k, r in rec.items()
                 if k.startswith(c + "|") and r["lvl"])
        m, my, tk = chs[c]
        print(f"  {c:<10}{m:>9,}{my:>9,}{tk / 1e6:>10.1f}{ne:>7,}{nl:>7,}")


if __name__ == "__main__":
    main()
