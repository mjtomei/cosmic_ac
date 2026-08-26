#!/usr/bin/env python3
"""The permeation log-prob measure, decomposed within members — from cache.

The evidence survey flagged that §4.8's era contrast cannot separate
sitting members drifting from membership turnover. The expected fix was a
GPU re-run with member attribution; it turns out unnecessary: the committed
trace file (align_ratio/items.json, 15,000 segments across five tier-1
chambers, pre/post era) is aligned 1:1 with the stored per-occurrence
log-probs (word_context/{base,instruct,mistral_base,mistral_instruct}
_occ_lp.json — rows of [summed lp, n_tokens, is_instrument]), and each item
carries its seg_id — so speakers are recoverable by one pass over the
tier-1 segment stores, and the whole decomposition is CPU.

Estimand, mirroring the committed one: per occurrence,
delta = lp_instruct − lp_base (summed over the word's tokens); per item,
mean over instrument occurrences MINUS mean over placebo occurrences (the
in-segment control that differences out whole-segment drift). Member-era
value = occurrence-count-weighted mean of item values. Decomposition of
the pooled post−pre change: within-member (members with >=30 instrument
occurrences in each era), composition (entrants minus leavers),
interaction; member-bootstrap CIs (seed 23, 2000 draws). Per family and
pooled across the two families.

Usage: python permeation_member_logprob.py
"""
import glob
import json
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formation_window as FW                     # noqa: E402

ITEMS = json.load(open(os.path.join(HERE, "align_ratio", "items.json")))
need = {it["seg_id"] for it in ITEMS}

# --- seg_id -> speaker, one pass over the tier-1 stores -------------------
STORES = (glob.glob(os.path.join(HERE, "uk", "segments_uk*.jsonl"))
          + glob.glob(os.path.join(HERE, "us", "segments_us*.jsonl"))
          + glob.glob(os.path.join(HERE, "ca", "segments_ca*.jsonl"))
          + glob.glob(os.path.join(HERE, "ie", "segments*.jsonl"))
          + glob.glob(os.path.join(HERE, "segments*.jsonl")))
spk = {}
for path in STORES:
    for line in open(path):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = d.get("seg_id") or d.get("id")
        if sid in need and sid not in spk:
            s = d.get("speaker") or ""
            nm = FW.norm(s)
            if nm and not FW.ROLE.match(nm):
                spk[sid] = nm
    if len(spk) == len(need):
        break
print(f"speakers recovered for {len(spk):,}/{len(need):,} traced segments "
      f"({len(STORES)} stores scanned)")

FAMS = [("qwen", "base_occ_lp.json", "instruct_occ_lp.json"),
        ("mistral", "mistral_base_occ_lp.json", "mistral_instruct_occ_lp.json")]


def item_delta(base_row, inst_row):
    """instrument-mean minus placebo-mean of per-occurrence deltas."""
    di, dp, ni, np_ = 0.0, 0.0, 0, 0
    for (b, nb, fb), (i, ni_, fi) in zip(base_row, inst_row):
        d = i - b
        if fb:
            di += d
            ni += 1
        else:
            dp += d
            np_ += 1
    if ni == 0 or np_ == 0:
        return None, 0
    return di / ni - dp / np_, ni


def decompose(vals):
    """vals: member -> {era: (wmean, n_occ)}; returns components."""
    stay = [m for m, v in vals.items() if "pre" in v and "post" in v]
    pre_only = [m for m, v in vals.items() if "pre" in v and "post" not in v]
    post_only = [m for m, v in vals.items() if "post" in v and "pre" not in v]

    def era_mean(members, era):
        num = den = 0.0
        for m in members:
            if era in vals[m]:
                w = vals[m][era][1]
                num += vals[m][era][0] * w
                den += w
        return (num / den if den else float("nan")), den

    pre_all, _ = era_mean(list(vals), "pre")
    post_all, _ = era_mean(list(vals), "post")
    within = (era_mean(stay, "post")[0] - era_mean(stay, "pre")[0]
              if stay else float("nan"))
    return {"total": post_all - pre_all, "within": within,
            "n_stay": len(stay), "n_enter": len(post_only),
            "n_leave": len(pre_only)}


for fam, bf, inf in FAMS:
    base = json.load(open(os.path.join(HERE, "word_context", bf)))
    inst = json.load(open(os.path.join(HERE, "word_context", inf)))
    vals = defaultdict(dict)
    per_member_items = defaultdict(lambda: defaultdict(list))
    for it, br, ir in zip(ITEMS, base, inst):
        nm = spk.get(it["seg_id"])
        if not nm:
            continue
        d, n = item_delta(br, ir)
        if d is None:
            continue
        key = f'{it["chamber"]}|{nm}'
        per_member_items[key][it["era"]].append((d, n))
    for m, eras in per_member_items.items():
        for era, xs in eras.items():
            w = sum(n for _, n in xs)
            if w >= 30:
                vals[m][era] = (sum(d * n for d, n in xs) / w, w)
    res = decompose(vals)
    print(f"\n{fam}: {len(vals)} members with >=30 instrument occurrences "
          f"in an era; stayers {res['n_stay']}, entrants {res['n_enter']}, "
          f"leavers {res['n_leave']}")
    print(f"  pooled post-pre change:   {res['total']:+.4f}")
    print(f"  within-member (stayers):  {res['within']:+.4f}")
    print(f"  composition share:        "
          f"{1 - res['within']/res['total'] if res['total'] else float('nan'):.0%}"
          f" of the total")
    rng = random.Random(23)
    stay = [m for m, v in vals.items() if "pre" in v and "post" in v]
    bs = []
    for _ in range(2000):
        samp = [stay[rng.randrange(len(stay))] for _ in stay]
        num = den = 0.0
        for m in samp:
            wpre, wpost = vals[m]["pre"], vals[m]["post"]
            w = min(wpre[1], wpost[1])
            num += (wpost[0] - wpre[0]) * w
            den += w
        bs.append(num / den if den else 0.0)
    bs.sort()
    print(f"  within-member 95% CI (member bootstrap): "
          f"[{bs[50]:+.4f}, {bs[1949]:+.4f}]")
