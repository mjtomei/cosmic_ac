#!/usr/bin/env python3
"""Convergent and discriminant checks: the folk ladder against the
market-fitted measures (Matthew's plan, 2026-08-26; categorical throughout).

Units: occupations weighted by member count (the member-weighted view is
primary — it is the population the study measures; unweighted by
occupation reported beside it). Continuous anchors (ISEI, SIOPS, wage) are
cut to member-weighted quartiles. Level scores per occupation come from the
committed member table (element-based, constant within occupation).

  1. Cross-tabs: folk argmax level x Job Zone / edu category / ISEI
     quartile / SIOPS quartile / wage quartile — Cramer's V, with the
     occupation-level member-weighted Spearman of the underlying continuous
     scores as a companion line.
  2. Hauser-Warren: regress each level score on occupational education
     (2.D.1 modal category) + log wage; R^2 answers "is altitude the old
     ingredients recombined."
  3. Known groups: ten highest / lowest occupations per level score.
  4. FREE vs self-employment: free-argmax x EGP IVab/IVc overlap.

Usage: python market_convergence.py
"""
import csv, json, math, os
from collections import Counter, defaultdict
import numpy as np

HERE=os.path.dirname(os.path.abspath(__file__))
mj=json.load(open(os.path.join(HERE,"occupation_market_join.json")))
tab=json.load(open(os.path.join(HERE,"prereg_member_table.json")))
titles={r["O*NET-SOC Code"]: r["Title"] for r in
        csv.DictReader(open(os.path.join(HERE,"market_anchors","occupation_titles.txt")),delimiter="\t")}
LVK=["lvl_FREE","lvl_BOTTOM","lvl_MIDDLE","lvl_TOP"]

# per-SOC level scores + member counts + per-member rows
soc_scores={}; soc_members=Counter(); members=[]
for r in tab:
    soc=r.get("soc")
    if not soc or r.get("lvl_MIDDLE") is None: continue
    if soc not in soc_scores:
        soc_scores[soc]={k:r[k] for k in LVK}
    soc_members[soc]+=1
    members.append(r)
print(f"{len(soc_scores)} scored occupations, {len(members)} members")

def argmax_lvl(sc): 
    v=[sc[k] for k in LVK]; return LVK[v.index(max(v))].split("_")[1].lower()

# member-weighted quartile cuts for continuous anchors
def quartile_map(key, log=False):
    vals=[]
    for soc,n in soc_members.items():
        v=mj.get(soc,{}).get(key)
        if v is not None: vals+= [math.log(v) if log else v]*n
    vals.sort()
    cuts=[vals[int(len(vals)*q)] for q in (0.25,0.5,0.75)]
    def f(soc):
        v=mj.get(soc,{}).get(key)
        if v is None: return None
        x=math.log(v) if log else v
        return sum(x>c for c in cuts)+1
    return f
q_isei=quartile_map("isei"); q_siops=quartile_map("siops"); q_wage=quartile_map("wage",log=True)

def cramers_v(pairs):
    xs=sorted({a for a,_ in pairs}); ys=sorted({b for _,b in pairs})
    n=len(pairs)
    O=np.zeros((len(xs),len(ys)))
    for a,b in pairs: O[xs.index(a),ys.index(b)]+=1
    E=O.sum(1)[:,None]*O.sum(0)[None,:]/n
    chi2=((O-E)**2/np.where(E>0,E,1)).sum()
    k=min(len(xs),len(ys))-1
    return math.sqrt(chi2/(n*k)) if k>0 else float("nan"), n

def wspearman(key, log=False):
    """occupation-level, member-weighted, folk-TOP score? use each level? report per level"""
    out={}
    for k in LVK:
        rows=[]
        for soc,n in soc_members.items():
            v=mj.get(soc,{}).get(key)
            if v is None: continue
            rows+= [(soc_scores[soc][k], math.log(v) if log else v)]*n
        xs=[a for a,_ in rows]; ys=[b for _,b in rows]
        def rank(v):
            s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
            i=0
            while i<len(s):
                j=i
                while j+1<len(s) and v[s[j+1]]==v[s[i]]: j+=1
                for t in range(i,j+1): r[s[t]]=(i+j)/2
                i=j+1
            return r
        ra,rb=rank(xs),rank(ys)
        ra=np.array(ra,float); rb=np.array(rb,float)
        ra-=ra.mean(); rb-=rb.mean()
        out[k.split("_")[1]]=float((ra*rb).sum()/math.sqrt((ra**2).sum()*(rb**2).sum()))
    return out

print("\n=== 1. CROSS-TABS: folk argmax level x anchor (member-weighted) ===")
ANCH=[("Job Zone", lambda s: mj.get(s,{}).get("jobzone")),
      ("edu category", lambda s: mj.get(s,{}).get("edu_cat")),
      ("ISEI quartile", q_isei), ("SIOPS quartile", q_siops),
      ("wage quartile", q_wage)]
for name,f in ANCH:
    pairs=[]
    for soc,n in soc_members.items():
        a=argmax_lvl(soc_scores[soc]); b=f(soc)
        if b is not None: pairs+=[(a,b)]*n
    V,n=cramers_v(pairs)
    print(f"  {name:<14} Cramer's V = {V:.3f}  (members {n})")
print("\n  companion member-weighted Spearman of level scores vs anchors:")
for name,key,log in (("ISEI","isei",False),("SIOPS","siops",False),("wage","wage",True)):
    r=wspearman(key,log)
    print(f"  {name:<6} "+"  ".join(f"{k} {v:+.2f}" for k,v in r.items()))

print("\n=== 2. HAUSER-WARREN: level score ~ occ. education + log wage (occupation-level, member-weighted) ===")
for k in LVK:
    rows=[]
    for soc,n in soc_members.items():
        m=mj.get(soc,{})
        if m.get("edu_cat") is None or m.get("wage") is None: continue
        rows+=[(soc_scores[soc][k], m["edu_cat"], math.log(m["wage"]))]*n
    y=np.array([a for a,_,_ in rows]); X=np.column_stack([np.ones(len(rows)),
        [b for _,b,_ in rows],[c for _,_,c in rows]])
    b,res,rk,sv=np.linalg.lstsq(X,y,rcond=None)
    pred=X@b; r2=1-((y-pred)**2).sum()/((y-y.mean())**2).sum()
    print(f"  {k.split('_')[1]:<8} R^2 = {r2:.2f}")

print("\n=== 3. KNOWN GROUPS: extremes per level ===")
for k in LVK:
    ss=sorted(soc_scores, key=lambda s: soc_scores[s][k])
    lo=[titles.get(s,s) for s in ss[:6]]; hi=[titles.get(s,s) for s in ss[-6:]][::-1]
    print(f"  {k.split('_')[1]} high: "+"; ".join(hi))
    print(f"  {k.split('_')[1]}  low: "+"; ".join(lo)+"\n")

print("=== 4. FREE vs self-employment (EGP IVab/IVc) ===")
ct=Counter()
for r in members:
    if r.get("egp"):
        ct[(argmax_lvl({k:r[k] for k in LVK}), r["egp"] in ("IVab","IVc"))]+=1
free_pb=ct[("free",True)]; free_o=ct[("free",False)]
oth_pb=sum(v for (l,pb),v in ct.items() if l!="free" and pb)
oth_o=sum(v for (l,pb),v in ct.items() if l!="free" and not pb)
print(f"  free-argmax members: {free_pb} petty-bourgeois/farmer, {free_o} not "
      f"({free_pb/(free_pb+free_o):.0%} PB)")
print(f"  other levels:        {oth_pb} PB, {oth_o} not ({oth_pb/(oth_pb+oth_o):.0%} PB)")
