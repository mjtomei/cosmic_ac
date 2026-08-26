#!/usr/bin/env python3
"""TOST equivalence tests for the study's load-bearing nulls.

A null with an MDE statement says what was detectable; an equivalence test
says what is EXCLUDED. SESOI throughout = +/-0.22 raw points — the smallest
effect the study itself treats as substantive (the low end of the stage-2
headline range, +0.22 to +0.29). Chosen once, stated here, applied to:

  A. the stage-2 dimensions the paper reads as null (AI/Mixed vs Human,
     chamber FE, HC1 — the committed column's own estimator);
  B. the evasion pairs (stage 3 original-vs-humanized, stage 4 target
     pairs): paired within-text differences per dimension;
  C. the flight battery's free-vs-middle abstention: Fisher-z TOST that
     |rho| < 0.15, the smallest deep-threshold status-top avoidance the
     battery treats as flight (executive 1500+).

TOST verdict: equivalent at 5% iff the 90% CI lies inside [-SESOI, +SESOI]
(equivalently max(p_lo, p_hi) < .05 one-sided each way).

Usage: python tost_equivalence.py
"""
import json, math, os, sys
import numpy as np

HERE=os.path.dirname(os.path.abspath(__file__))
Q=os.path.join(HERE,"quality_expansion")
DIMS=["justification","common_good","respect_groups","respect_demands",
      "respect_counterargs","constructive","evidence"]
SENT={"respect_demands","respect_counterargs"}
SESOI=0.22

def hc1(y,X):
    XtXi=np.linalg.pinv(X.T@X); b=XtXi@X.T@y
    e=y-X@b; n,k=X.shape
    V=XtXi@(X*(e**2)[:,None]).T@X@XtXi*n/max(n-k,1)
    return b,V

def norm_sf(z): return 0.5*math.erfc(z/math.sqrt(2))

def tost(b,se,sesoi=SESOI):
    p_lo=norm_sf((b-(-sesoi))/se)*0+norm_sf(-( (b+sesoi)/se ))  # H0: b<=-sesoi
    p_lo=norm_sf(-((b+sesoi)/se))
    p_hi=norm_sf((b-sesoi)/se*-1)*0 + norm_sf(((b-sesoi)/se)*-1)
    p_hi=norm_sf(-((sesoi-b)/se))
    # one-sided: reject b<=-s if (b+s)/se large; reject b>=+s if (s-b)/se large
    p1=norm_sf((b+sesoi)/se); p2=norm_sf((sesoi-b)/se)
    return max(p1,p2)

print(f"SESOI = ±{SESOI} raw points (the smallest stage-2 headline effect)\n")

print("=== A. stage-2 null dimensions (committed estimator) ===")
rows=json.load(open(os.path.join(Q,"results_stage2.json")))
chs=sorted({r["chamber"] for r in rows})[1:]
for d in DIMS:
    sub=[r for r in rows if r.get(d) is not None and not (d in SENT and r[d]==-1)]
    y=np.array([r[d] for r in sub],float)
    X=np.array([[1.0,1.0 if r["verdict"] in ("AI","Mixed") else 0.0]
                +[1.0 if r["chamber"]==c else 0.0 for c in chs] for r in sub])
    b,V=hc1(y,X); bb=b[1]; se=math.sqrt(V[1,1])
    p=tost(bb,se)
    verdict="EQUIVALENT" if p<0.05 else "not shown equivalent"
    print(f"  {d:<21s} {bb:+.3f} (se {se:.3f})  TOST p {p:.4f}  -> {verdict}")

print("\n=== B. evasion pairs, per dimension (paired within-text) ===")
for stage,gf,kf in (("stage 3",os.path.join(Q,"stage3_grades_by_id.json"),os.path.join(Q,"key3.json")),
                    ("stage 4",os.path.join(Q,"stage4_grades_by_id.json"),os.path.join(Q,"key4.json"))):
    g=json.load(open(gf)); key=json.load(open(kf))
    pairs={}
    for qid,rec in g.items():
        k=key.get(qid)
        if k: pairs.setdefault(k["seg_id"],{})[k["condition"]]=rec
    full={s:v for s,v in pairs.items() if len(v)==2}
    conds=sorted({c for v in full.values() for c in v})
    print(f"  {stage}: {len(full)} pairs, conditions {conds}")
    for d in DIMS:
        ds=[]
        for v in full.values():
            a,b_=[v[c].get(d) for c in conds]
            if a is None or b_ is None: continue
            if d in SENT and (a==-1 or b_==-1): continue
            ds.append(b_-a)
        if len(ds)<10:
            print(f"    {d:<21s} too few applicable pairs ({len(ds)})"); continue
        m=sum(ds)/len(ds)
        se=math.sqrt(sum((x-m)**2 for x in ds)/(len(ds)-1)/len(ds))
        p=tost(m,se)
        verdict="EQUIVALENT" if p<0.05 else "not shown equivalent"
        print(f"    {d:<21s} {m:+.3f} (se {se:.3f}, n {len(ds)})  TOST p {p:.4f}  -> {verdict}")

print("\n=== C. free-vs-middle abstention (Fisher-z TOST, |rho| < 0.15) ===")
for th,rho,n in ((100,-0.07,259),(300,-0.07,178),(800,-0.10,113),(1500,-0.06,77)):
    z=0.5*math.log((1+rho)/(1-rho)); zs=0.15
    z015=0.5*math.log((1+zs)/(1-zs))
    se=1/math.sqrt(n-3)
    p1=norm_sf((z+z015)/se); p2=norm_sf((z015-z)/se)
    p=max(p1,p2)
    verdict="EQUIVALENT (|rho|<0.15)" if p<0.05 else "not shown equivalent"
    print(f"  {th:>5}+  rho {rho:+.2f} (n {n})  TOST p {p:.4f}  -> {verdict}")
