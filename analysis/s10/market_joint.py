#!/usr/bin/env python3
"""The folk ladder against the market-fitted measures, in the joint model.

The eval that feeds 8.4 its number (Matthew's plan, 2026-08-26): mirror
the committed occ-panel spec exactly — cohort, all EGP classes, all
education levels, prominence quintiles, the folk ladder per sd — and add
the market anchors as CATEGORICAL blocks (member-weighted quartile dummies,
Q1 baseline): ISEI and OES log-wage. Same member-level estimator (z within
chamber, equal weight, HC1, block Walds). Each block also alone on the
same sample. Questions: does the blind measure survive the fitted ones,
and do they survive it?

Usage: python market_joint.py
"""
import json, math, os, sys
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import joint_predictors as JP
import member_level_estimation as MLE
import panel_estimation as PE

mj=json.load(open(os.path.join(HERE,"occupation_market_join.json")))
rows=MLE.zscore(MLE.members())
depth=JP.load_depth()
for r in rows: r["logdepth"]=depth.get(JP.depth_key(r["member"]))
ok=[r for r in rows if r["bd"] is not None and r.get("z") is not None]
JP.apply_edu_split(ok)
occ=JP.load_occ()
soc={ "|".join(r["member"].split("|")[:2]): r["soc"]
      for r in json.load(open(os.path.join(HERE,"prereg_member_table.json"))) if r.get("soc")}
sample=[]
for r in ok:
    if r["egp"] not in PE.EGP_RANK or r["edu"] not in JP.LV_OK or r["logdepth"] is None: continue
    o=occ.get(JP.depth_key(r["member"]))
    sc=soc.get(JP.depth_key(r["member"]))
    m=mj.get(sc or "",{})
    if o is None or m.get("isei") is None or m.get("wage") is None: continue
    r["occ_raw"]=o; r["isei"]=m["isei"]; r["lwage"]=math.log(m["wage"])
    sample.append(r)
JP.zscore_occ(sample); JP.assign_quintiles(sample)
print(f"panel: {len(sample)} members with every block incl. ISEI and wage")

def qcuts(key):
    v=sorted(r[key] for r in sample)
    cuts=[v[int(len(v)*q)] for q in (0.25,0.5,0.75)]
    for r in sample: r[key+"_q"]=sum(r[key]>c for c in cuts)+1
qcuts("isei"); qcuts("lwage")

cats={"class":[c for c in PE.EGP if c!="I" and any(r["egp"]==c for r in sample)],
      "edu":[e for e in JP.EDU_DUM if any(r["edu"]==e for r in sample)]}

def design(rows_, blocks):
    y=[]; X=[]; idx={}; col=1
    W={"class":len(cats["class"]),"edu":len(cats["edu"]),"prominence":4,
       "folk":4,"iseiq":3,"wageq":3}
    for b in blocks:
        w=W.get(b,1); idx[b]=list(range(col,col+w)); col+=w
    for r in rows_:
        row=[1.0]
        for b in blocks:
            if b=="cohort": row.append(r["bd"])
            elif b=="class": row+=[1.0 if r["egp"]==c else 0.0 for c in cats["class"]]
            elif b=="edu": row+=[1.0 if r["edu"]==e else 0.0 for e in cats["edu"]]
            elif b=="prominence": row+=[1.0 if r["promq"]==q else 0.0 for q in (1,2,3,4)]
            elif b=="folk": row+=r["occ_z"][4:8]
            elif b=="iseiq": row+=[1.0 if r["isei_q"]==q else 0.0 for q in (2,3,4)]
            elif b=="wageq": row+=[1.0 if r["lwage_q"]==q else 0.0 for q in (2,3,4)]
        X.append(row); y.append(r["z"])
    return y,X,idx

NAMES={"class":[f"class {c}" for c in cats["class"]],
       "edu":[f"edu {e}" for e in cats["edu"]],
       "prominence":[f"prom Q{q}" for q in (2,3,4,5)],
       "folk":["folk FREE","folk BOTTOM","folk MIDDLE","folk TOP"],
       "iseiq":[f"ISEI Q{q}" for q in (2,3,4)],
       "wageq":[f"wage Q{q}" for q in (2,3,4)]}

def report(blocks,label):
    y,X,idx=design(sample,blocks)
    b,V=MLE.ols_hc1(y,X)
    print(f"\n{label}   n={len(sample):,}")
    for bl in blocks:
        for j,nm in zip(idx[bl],NAMES.get(bl,[bl])):
            se=math.sqrt(V[j,j])
            print(f"    {nm:<14}{b[j]:>+8.3f}  t {b[j]/se:+.2f}"
                  f"{' *' if abs(b[j]/se)>1.96 else ''}")
        W_,k,p=MLE.wald(b,V,idx[bl])
        print(f"      block Wald chi2={W_:.1f}, df={k}, p={p:.4g}")

for bl in (["folk"],["iseiq"],["wageq"]):
    report(bl, f"{bl[0]} ALONE (same sample)")
report(["cohort","class","edu","prominence","folk"],"JOINT — the committed five (this sample)")
report(["cohort","class","edu","prominence","iseiq","wageq"],"JOINT — market anchors instead of the folk ladder")
report(["cohort","class","edu","prominence","folk","iseiq","wageq"],"JOINT — folk ladder AND the market anchors")
