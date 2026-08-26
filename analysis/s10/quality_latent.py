#!/usr/bin/env python3
"""Does the AI-vs-human quality contrast depend on the equal-weight composite?

Evidence-standards bundle item: the seven-dimension composite is asserted,
not derived. This script derives a data-driven weighting — the first
principal factor of the dimensions' Spearman correlation matrix (pairwise
complete, sentinel -1s treated as missing) — and re-runs the stage-1 and
stage-2 AI-vs-human contrasts on the factor-weighted latent score beside
the equal-weight composite, same estimator as the committed columns
(chamber FE where the stage has chambers, HC1). A full polychoric/IRT
graded-response fit needs scipy (absent in this environment); the
principal-factor weighting answers the substantive question — do the
conclusions survive non-equal weights? — and the upgrade is noted as
nice-to-have.

Usage: python quality_latent.py
"""
import json, math, os
import numpy as np

HERE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"quality_expansion")
DIMS=["justification","common_good","respect_groups","respect_demands",
      "respect_counterargs","constructive","evidence"]
SENT={"respect_demands","respect_counterargs"}

def spearman_pairwise(rows):
    def vals(d):
        return [ (None if (r.get(d) is None or (d in SENT and r[d]==-1)) else float(r[d])) for r in rows ]
    cols={d:vals(d) for d in DIMS}
    def rank(v):
        idx=[i for i,x in enumerate(v) if x is not None]
        s=sorted(idx,key=lambda i:v[i]); r={}
        i=0
        while i<len(s):
            j=i
            while j+1<len(s) and v[s[j+1]]==v[s[i]]: j+=1
            for k in range(i,j+1): r[s[k]]=(i+j)/2
            i=j+1
        return r
    C=np.eye(len(DIMS))
    for a in range(len(DIMS)):
        for b in range(a+1,len(DIMS)):
            va,vb=cols[DIMS[a]],cols[DIMS[b]]
            idx=[i for i in range(len(rows)) if va[i] is not None and vb[i] is not None]
            ra=rank([va[i] if i in set(idx) else None for i in range(len(rows))])
            rb=rank([vb[i] if i in set(idx) else None for i in range(len(rows))])
            xs=np.array([ra[i] for i in idx]); ys=np.array([rb[i] for i in idx])
            xs=(xs-xs.mean()); ys=(ys-ys.mean())
            den=math.sqrt((xs**2).sum()*(ys**2).sum())
            C[a,b]=C[b,a]=float((xs*ys).sum()/den) if den else 0.0
    return C, cols

def hc1(y,X):
    XtXi=np.linalg.pinv(X.T@X); b=XtXi@X.T@y
    e=y-X@b; n,k=X.shape
    V=XtXi@(X*(e**2)[:,None]).T@X@XtXi*n/max(n-k,1)
    return b,V

def contrast(rows, score, chfe, reg):
    ok=[i for i,r in enumerate(rows) if score[i] is not None and reg(rows[i]) is not None]
    y=np.array([score[i] for i in ok])
    x=np.array([reg(rows[i]) for i in ok],float)
    if set(np.unique(x)) - {0.0, 1.0} and x.std():   # standardise continuous only
        x=(x-x.mean())/x.std()
    chs=sorted({rows[i]["chamber"] for i in ok})[1:] if chfe else []
    X=np.array([[1.0, xi]+[1.0 if rows[i]["chamber"]==c else 0.0 for c in chs]
                for i,xi in zip(ok,x)])
    b,V=hc1(y,X)
    return b[1], b[1]/math.sqrt(V[1,1]), len(ok)

REGS={"stage 1": (lambda r: r.get("ai"), "per sd of screen score"),
      "stage 2": (lambda r: 1.0 if r["verdict"] in ("AI","Mixed") else 0.0,
                  "AI/Mixed vs Human")}
for stage,fn,chfe in (("stage 1","results_stage1.json",False),
                      ("stage 2","results_stage2.json",True)):
    p=os.path.join(HERE,fn)
    if not os.path.exists(p):
        print(f"{stage}: {fn} not found — skipped"); continue
    rows=json.load(open(p))
    C,cols=spearman_pairwise(rows)
    w,v=np.linalg.eigh(C)
    load=v[:,-1]
    if load.sum()<0: load=-load
    share=w[-1]/len(DIMS)
    print(f"\n{stage}: first factor explains {share:.0%} of the Spearman matrix")
    print("  loadings: "+", ".join(f"{d} {l:+.2f}" for d,l in zip(DIMS,load)))
    # z-score each dim over applicable, latent = loading-weighted mean of available z's
    zs={}
    for d in DIMS:
        v_=[x for x in cols[d] if x is not None]
        m,s=float(np.mean(v_)),float(np.std(v_)) or 1.0
        zs[d]=[(None if x is None else (x-m)/s) for x in cols[d]]
    latent=[]; equal=[]
    for i in range(len(rows)):
        num=den=0.0; ne=de=0.0
        for j,d in enumerate(DIMS):
            z=zs[d][i]
            if z is not None:
                num+=load[j]*z; den+=abs(load[j]); ne+=z; de+=1
        latent.append(num/den if den else None)
        equal.append(ne/de if de else None)
    reg,rlab=REGS[stage]
    for name,score in (("equal-weight composite",equal),("factor-weighted latent",latent)):
        b,t,n=contrast(rows,score,chfe,reg)
        print(f"  {rlab} on {name:<24s} {b:+.3f}  t {t:+.2f}  (n {n})")
