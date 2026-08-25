#!/usr/bin/env python3
"""The contemporary-specificity bound from the flagged-hits audit (AL1).

Reads flagged_hits_audit.json (two-vote prepared/spontaneous classification of
all 316 estimator hits) and flagged_hits_pool.json, dissects the both-vote
spontaneous residue, and computes what the floor's transfer assumption can
cost: the headline recomputed with every both-vote-spontaneous hit treated as
a contemporary false positive (fraction-weighted, and harsher full-word).
"""
import json, os
HERE=os.path.dirname(os.path.abspath(__file__))
calls=json.load(open(os.path.join(HERE,"flagged_hits_audit.json")))
pool={e["id"]:e for e in json.load(open(os.path.join(HERE,"flagged_hits_pool.json")))}
both=[c for c in calls if c["verdict"]=="spontaneous" and c.get("second")=="spontaneous"]
n_prep=sum(1 for c in calls if c["verdict"]=="prepared")
n_uncl=sum(1 for c in calls if c["verdict"]=="unclear")
n_sp1=sum(1 for c in calls if c["verdict"]=="spontaneous")
print(f"classified {len(calls)}: prepared {n_prep}, unclear {n_uncl}, "
      f"spontaneous first-vote {n_sp1}, both votes {len(both)}")
mixed=[c for c in both if pool[c['id']]['fraction_ai']<0.9]
print(f"of the {len(both)}: {len(mixed)} are Mixed at fractions "
      f"{sorted(round(pool[c['id']]['fraction_ai'],2) for c in mixed)}; "
      f"{len(both)-len(mixed)} near-full")
TOT_W=728998; FLAG_W=65795
mw=sum(pool[c["id"]]["fraction_ai"]*pool[c["id"]]["n_words"] for c in both)
fw=sum(pool[c["id"]]["n_words"] for c in both)
print(f"machine-word weight of the {len(both)}: {mw:.0f} (fraction) / {fw} (full)")
print(f"headline 9.03% -> {(FLAG_W-mw)/TOT_W*100:.2f}% (fraction-weighted removal)")
print(f"headline 9.03% -> {(FLAG_W-fw)/TOT_W*100:.2f}% (full-word removal)")
