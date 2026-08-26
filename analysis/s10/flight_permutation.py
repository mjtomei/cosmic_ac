#!/usr/bin/env python3
"""Permutation null, split-half, and the takeoff-window within-member check
for the (decoupled) flight correlation — evidence-standards survey rec 1,
plus Matthew's individual-level check scoped to the short horizon where it
makes sense (2026-08-27: over a thirty-year cycle careers are shorter than
the trend, so the standing claim is group-level; the within-member check
asks only about the recent takeoff window).

1. PERMUTATION NULL: hold every member's text fixed, permute the I/II
   labels among the I-and-II members within each province, recompute the
   decoupled flight rho at each volume threshold; 1,000 draws. Lift is
   fixed (computed from classes outside both strata), and the per-word
   threshold sets are fixed under permutation (the I-union-II counts do
   not move), so the null isolates the label assignment.
2. SPLIT-HALF: rho computed on the even-indexed halves of I and II members
   against the odd-indexed halves (sorted keys) — stability, not inference.
3. TAKEOFF WITHIN-MEMBER: for members with >= 2,000 style-relevant tokens
   in both windows (pre 2018-2022, post 2023-2026), the change in the
   share of their style-word usage falling on high-lift words (top tercile
   of decoupled lift), by stratum; member-bootstrap CIs. Within-member
   flight predicts the top strata's share rises LESS than the peak's.

Usage: python flight_permutation.py
"""
import gzip, json, math, random
from collections import defaultdict

random.seed(101)
cw=json.load(open("class_word_year.json"))
mc=json.load(gzip.open("flight_member_cache.json.gz","rt"))

def rate_from(pred,y0,y1,word):
    num=den=0
    for key,w in cw["tot"].items():
        g,y=key.rsplit("|",1); y=int(y)
        if y0<=y<=y1 and pred(g):
            den+=w; num+=cw["per"].get(key,{}).get(word,0)
    return (num/den*1e5 if den else None)
words=set()
for e in cw["per"].values(): words|=set(e)
REF=lambda g: g not in ("I","II")
lift={}
for w in words:
    pre=rate_from(REF,2006,2022,w); post=rate_from(REF,2023,2026,w)
    if pre and post: lift[w]=post/pre

def spearman(a,b):
    def rank(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
        for j,i in enumerate(s): r[i]=j
        return r
    ra,rb=rank(a),rank(b); n=len(a); ma,mb=sum(ra)/n,sum(rb)/n
    den=math.sqrt(sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb))
    return sum((x-ma)*(y-mb) for x,y in zip(ra,rb))/den if den else float("nan")

# member-level post-window counts for I and II members
mem=[]
for k,rec in mc.items():
    if rec.get("egp") in ("I","II"):
        tot=0; wc=defaultdict(int)
        for y,v in rec["years"].items():
            if 2023<=int(y)<=2026:
                tot+=v["tot"]
                for w,c in v["w"].items(): wc[w]+=c
        if tot>0:
            mem.append((k, k.split("|")[0], rec["egp"], tot, dict(wc)))
print(f"I/II members with 2023-26 speech: {len(mem)} "
      f"(I {sum(1 for m in mem if m[2]=='I')}, II {sum(1 for m in mem if m[2]=='II')})")

def rho_given(labels):
    agg={"I":[0,defaultdict(int)],"II":[0,defaultdict(int)]}
    for (k,pv,_,tot,wc),lab in zip(mem,labels):
        a=agg[lab]; a[0]+=tot
        for w,c in wc.items(): a[1][w]+=c
    rows=[]
    for w,lf in lift.items():
        n1=agg["I"][1].get(w,0); n2=agg["II"][1].get(w,0)
        if n2 and agg["I"][0] and agg["II"][0]:
            r1=n1/agg["I"][0]; r2=n2/agg["II"][0]
            rows.append((lf, r1/r2, n1+n2))
    out={}
    for th in (100,300,800,1500):
        sub=[r for r in rows if r[2]>=th]
        out[th]=(spearman([r[0] for r in sub],[r[1] for r in sub]), len(sub))
    return out

obs=rho_given([m[2] for m in mem])
print("\nobserved (member-aggregated, decoupled lift):")
for th,(r,n) in obs.items(): print(f"  {th:>5}+  rho {r:+.3f} (n {n})")

# permutation within province
by_pv=defaultdict(list)
for i,m in enumerate(mem): by_pv[m[1]].append(i)
B=1000
null={th:[] for th in (100,300,800,1500)}
labels0=[m[2] for m in mem]
for b in range(B):
    lab=list(labels0)
    for pv,idx in by_pv.items():
        ls=[lab[i] for i in idx]; random.shuffle(ls)
        for i,l in zip(idx,ls): lab[i]=l
    r=rho_given(lab)
    for th in null: null[th].append(r[th][0])
print(f"\npermutation null ({B} draws, labels shuffled within province):")
for th in (100,300,800,1500):
    v=sorted(x for x in null[th] if x==x)
    lo,hi=v[int(0.025*len(v))],v[int(0.975*len(v))]
    p=sum(1 for x in v if x<=obs[th][0])/len(v)
    print(f"  {th:>5}+  null 95% [{lo:+.3f},{hi:+.3f}]  mean {sum(v)/len(v):+.3f}   p(rho<=obs) = {p:.3f}")

# split-half
halves={"even":[],"odd":[]}
for i,m in enumerate(sorted(mem)): halves["even" if i%2==0 else "odd"].append(m)
for name,hs in halves.items():
    idx=[mem.index(m) for m in hs]
    labels=[m[2] for m in mem]
    # aggregate using only this half's members
    agg={"I":[0,defaultdict(int)],"II":[0,defaultdict(int)]}
    for m in hs:
        a=agg[m[2]]; a[0]+=m[3]
        for w,c in m[4].items(): a[1][w]+=c
    rows=[]
    for w,lf in lift.items():
        n1=agg["I"][1].get(w,0); n2=agg["II"][1].get(w,0)
        if n2 and agg["I"][0] and agg["II"][0]:
            rows.append((lf,(n1/agg["I"][0])/(n2/agg["II"][0]),n1+n2))
    out=[]
    for th in (100,300,800):
        sub=[r for r in rows if r[2]>=th//2]   # halves: halve the threshold
        out.append(f"{spearman([r[0] for r in sub],[r[1] for r in sub]):+.2f}(n{len(sub)})")
    print(f"split-half {name:>4}: "+"  ".join(out))

# takeoff within-member check
hi_lift={w for w,lf in sorted(lift.items(),key=lambda kv:-kv[1])[:len(lift)//3]}
def share(rec,y0,y1):
    tot=sw=0
    for y,v in rec["years"].items():
        if y0<=int(y)<=y1:
            for w,c in v["w"].items():
                sw+=c
                if w in hi_lift: tot+=c
    return (tot/sw if sw>=200 else None), sw
groups=defaultdict(list)
for k,rec in mc.items():
    pre,_=share(rec,2018,2022); post,_=share(rec,2023,2026)
    if pre is not None and post is not None:
        d=post-pre
        if rec.get("egp") in ("I","II"): groups["class "+rec["egp"]].append(d)
        if rec.get("lvl"): groups["folk "+rec["lvl"]].append(d)
print("\nTAKEOFF WITHIN-MEMBER (change in high-lift share of style usage, "
      "2018-22 -> 2023-26; members in both windows):")
for g in sorted(groups):
    v=groups[g]; m=sum(v)/len(v)
    bs=[]
    for _ in range(2000):
        s=[random.choice(v) for _ in v]; bs.append(sum(s)/len(s))
    bs.sort(); lo,hi=bs[int(0.025*len(bs))],bs[int(0.975*len(bs))]
    print(f"  {g:<12} n {len(v):>4}  Δshare {m:+.4f}  [{lo:+.4f},{hi:+.4f}]")
