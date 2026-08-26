#!/usr/bin/env python3
"""Prevalence robustness trio (evidence-standards survey, zero-cost bundle):

1. YEAR SPLIT: the 'current speech' window pools 2025 (n=1,428) and 2026
   (n=912) segments; the two years are different regimes of a rising
   series, so the scalar headline is a blend. Report the fraction-weighted
   word rate and the binary flag rate per year with segment-bootstrap CIs,
   and name the estimand.
2. SPEAKER-CLUSTERED BOOTSTRAP: 2,340 prevalence segments come from far
   fewer speakers, and drafting is plausibly an office-level habit.
   Re-run the pooled bootstrap resampling SPEAKERS within chamber; report
   both intervals and the design effect (variance ratio).
3. RANDOM-EFFECTS ACROSS CHAMBERS: DerSimonian-Laird on the logit of the
   per-chamber word-weighted rates (delta-method variances from the
   segment bootstrap), tau, I^2, and empirical-Bayes shrunken rates —
   the honest companion to the raw elevenfold spread.

Usage: python prevalence_robustness.py
"""
import csv, hashlib, math, random, sys, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prevalence_report as PR      # the committed estimand: _frac + exclusions

FLAG = {"AI", "Mixed"}
rows=[r for r in csv.DictReader(open("pangram_p4_verdicts.csv"))
      if r.get("pangram") and r["version"] in ("4.0","4.0-web")
      and r["source"].startswith("expansion")]
allprev=[r for r in rows if r["stratum"]=="prev"]
held={c for c in {r["chamber"] for r in allprev}
      if any(x.get("regime_flag") for x in allprev if x["chamber"]==c)}
prev=[r for r in allprev if r["chamber"] not in held]
print(f"regime-flagged chambers held out (as in the headline): {sorted(held) or 'none'}")
for r in prev:
    r["n_words"]=int(r["n_words"]); r["_f"]=PR._frac(r)

def wrate(sub):
    w=sum(r["n_words"] for r in sub)
    return sum(r["_f"]*r["n_words"] for r in sub)/w if w else float("nan")
def brate(sub):
    w=sum(r["n_words"] for r in sub)
    return sum((r["pangram"] in FLAG)*r["n_words"] for r in sub)/w if w else float("nan")

def boot(sub, stat, key=None, B=2000, seed=7):
    rng=random.Random(seed)
    if key is None:
        draws=[stat([rng.choice(sub) for _ in sub]) for _ in range(B)]
    else:
        clus=defaultdict(list)
        for r in sub: clus[(r["chamber"],r[key])].append(r)
        by_ch=defaultdict(list)
        for (c,k),v in clus.items(): by_ch[c].append(v)
        draws=[]
        for _ in range(B):
            samp=[]
            for c,cl in by_ch.items():
                for _ in cl: samp+= rng.choice(cl)
            draws.append(stat(samp))
    draws.sort()
    return draws[int(0.025*B)], draws[int(0.975*B)], (
        sum((d-sum(draws)/B)**2 for d in draws)/B)

import banded_prevalence as BP
brows=BP.load(); bmeta=BP.META
bidx=[i for i,r in enumerate(brows) if r[1]=="prev"]
print("=== 0. YEAR SPLIT AT THE HEADLINE ESTIMAND (banded, all bands) ===")
for yr in ("2025","2026",None):
    ii=[i for i in bidx if yr is None or (bmeta[i].get("date") or "").startswith(yr)]
    sub=[brows[i] for i in ii]
    n,k,sr,w,wk,wr=BP.rate(sub)
    lo,hi=BP.boot_ci(sub, seed=5)
    print(f"{yr or 'pooled':>7}: n={n:>5}  {wr:6.2%}  [{lo:.2%},{hi:.2%}]")

print("\n=== RANDOM EFFECTS ON THE BANDED CHAMBER RATES ===")
from collections import defaultdict as _dd
bych=_dd(list)
for i in bidx: bych[brows[i][0]].append(brows[i])
bcells=[]
for c,sub in sorted(bych.items()):
    _,_,_,w0,_,wr=BP.rate(sub)
    lo,hi=BP.boot_ci(sub, seed=int(hashlib.sha1(c.encode()).hexdigest())%9999 if False else 9)
    v=((hi-lo)/(2*1.96))**2
    if wr>0 and v>0:
        bcells.append((c,wr,math.log(wr/(1-wr)),v/((wr*(1-wr))**2)))
wb=[1/vl for _,_,_,vl in bcells]
mu=sum(wi*l for wi,(_,_,l,_) in zip(wb,bcells))/sum(wb)
Q=sum(wi*(l-mu)**2 for wi,(_,_,l,_) in zip(wb,bcells))
df=len(bcells)-1
C=sum(wb)-sum(x*x for x in wb)/sum(wb)
tau2=max(0,(Q-df)/C); I2=max(0,(Q-df)/Q) if Q>0 else 0
raw=[wr for _,wr,_,_ in bcells]
eb=[]
for c,wr,l,vl in bcells:
    b=tau2/(tau2+vl); eb.append(1/(1+math.exp(-(mu+b*(l-mu)))))
print(f"{len(bcells)} chambers: tau={math.sqrt(tau2):.3f}, I2={I2:.2f}; "
      f"raw spread {max(raw)/min(raw):.1f}x ({min(raw):.1%}-{max(raw):.1%}); "
      f"EB-shrunken {max(eb)/min(eb):.1f}x ({min(eb):.1%}-{max(eb):.1%})")

print("\n=== 1. YEAR SPLIT, LONG BAND (companion) ===")
print("headline estimand: fraction-weighted word rate = "
      "sum(fraction_ai x n_words)/sum(n_words) over the prevalence draw;")
print("binary companion: flagged-word rate = share of words in AI/Mixed-"
      "flagged segments.\n")
for yr in ("2025","2026", None):
    sub=[r for r in prev if yr is None or r["date"][:4]==yr]
    lo,hi,_=boot(sub,wrate,seed=11)
    blo,bhi,_=boot(sub,brate,seed=12)
    lab=yr or "pooled"
    print(f"{lab:>7}: n={len(sub):>5}  fraction-weighted {wrate(sub):6.2%} "
          f"[{lo:.2%},{hi:.2%}]   binary {brate(sub):6.2%} [{blo:.2%},{bhi:.2%}]")

print("\n=== 2. SPEAKER-CLUSTERED BOOTSTRAP (pooled, fraction-weighted) ===")
spk=len({(r['chamber'],r['speaker']) for r in prev})
print(f"2,340 segments from {spk} chamber-speaker clusters")
lo1,hi1,v1=boot(prev,wrate,seed=21)
lo2,hi2,v2=boot(prev,wrate,key="speaker",seed=22)
print(f"segment-resampled: [{lo1:.2%},{hi1:.2%}]")
print(f"speaker-resampled: [{lo2:.2%},{hi2:.2%}]   design effect {v2/v1:.2f}")

print("\n=== 3. RANDOM-EFFECTS ACROSS CHAMBERS ===")
ch=defaultdict(list)
for r in prev: ch[r["chamber"]].append(r)
cells=[]
for c,sub in sorted(ch.items()):
    wr=wrate(sub)
    _,_,v=boot(sub,wrate,seed=int(hashlib.sha1(c.encode()).hexdigest(),16)%9999)
    if wr>0 and v>0:
        logit=math.log(wr/(1-wr)); vl=v/((wr*(1-wr))**2)
        cells.append((c,wr,logit,vl))
w=[1/vl for _,_,_,vl in cells]
mu=sum(wi*l for wi,(_,_,l,_) in zip(w,cells))/sum(w)
Q=sum(wi*(l-mu)**2 for wi,(_,_,l,_) in zip(w,cells))
df=len(cells)-1
C=sum(w)-sum(wi*wi for wi in w)/sum(w)
tau2=max(0,(Q-df)/C)
I2=max(0,(Q-df)/Q) if Q>0 else 0
print(f"{len(cells)} chambers; logit-scale tau = {math.sqrt(tau2):.3f}, "
      f"I^2 = {I2:.2f}, Q = {Q:.1f} (df {df})")
shr=[]
for (c,wr,l,vl) in cells:
    b=tau2/(tau2+vl)
    ls=mu+b*(l-mu)
    shr.append((c,wr,1/(1+math.exp(-ls))))
raw=[wr for _,wr,_ in shr]
eb=[s for _,_,s in shr]
print(f"raw spread   max/min: {max(raw)/min(raw):.1f}x   "
      f"({min(raw):.1%} to {max(raw):.1%})")
print(f"EB-shrunken  max/min: {max(eb)/min(eb):.1f}x   "
      f"({min(eb):.1%} to {max(eb):.1%})")
print("\nper-chamber (raw -> shrunken):")
for c,wr,s in sorted(shr,key=lambda x:-x[1]):
    print(f"  {c:<10} {wr:6.2%} -> {s:6.2%}")
