#!/usr/bin/env python3
"""Group-level vs individual-level register gradients, per legislature.

Matthew's design (2026-08-25): for each chamber, in ONE unit (instrument
occurrences per 100k words, per decade), compare
  T — the GROUP gradient: the chamber's word-weighted calendar trend;
  X — the INDIVIDUAL gradient: the within-year birth-year gradient among
      members (year fixed effects, word-weighted).
If X varies across legislatures in step with T, that supports generational
(cohort) organisation; if X is uniform while T diverges, that supports
age/juniority. A second, windowed cut keeps the era evidence: growth of X as
drift-formed cohorts enter is the cohort signature the unwindowed comparison
cannot see.

Panel: member-years (>=2000 words) from member_year_rates_t1.json joined to
exact birth years (covariates_tier1.json, unambiguous only), ages 21-90.
CIs: member-cluster bootstrap (300). Writes apc_chamber_decomposition.txt and
apc_gradients.png.
"""
import json, collections, random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

cells=json.load(open("member_year_rates_t1.json"))
cov=json.load(open("covariates_tier1.json"))
birth={(r["chamber"],r["key"]):int(r["birth_year"]) for r in cov
       if r.get("birth_year") and not r.get("ambiguous")}
data=collections.defaultdict(list)
for k,(w,h) in cells.items():
    ch,name,yr=k.rsplit("|",2)
    b=birth.get((ch,name))
    if b and w>=2000:
        y=int(yr)
        if 21<=y-b<=90: data[ch].append((name,y,b,w,h/w*1e5))

def wdemean(vals, keys, w):
    sw=collections.defaultdict(float); sv=collections.defaultdict(float)
    for k,v,wi in zip(keys,vals,w): sw[k]+=wi; sv[k]+=wi*v
    mu={k: sv[k]/sw[k] for k in sw}
    return np.array([v-mu[k] for k,v in zip(keys,vals)])

def grads(rows):
    y=np.array([r[1] for r in rows],float); b=np.array([r[2] for r in rows],float)
    w=np.array([r[3] for r in rows],float); r_=np.array([r[4] for r in rows],float)
    rt=wdemean(r_,[int(v) for v in y],w); bt=wdemean(b,[int(v) for v in y],w)
    X=float(np.sum(w*bt*rt)/np.sum(w*bt*bt))*10
    yt=y-np.average(y,weights=w); rc=r_-np.average(r_,weights=w)
    T=float(np.sum(w*yt*rc)/np.sum(w*yt*yt))*10
    return X,T

def boot(rows, n=300, seed=7):
    members=sorted({r[0] for r in rows})
    bym=collections.defaultdict(list)
    for r in rows: bym[r[0]].append(r)
    rng=random.Random(seed); xs=[]; ts=[]
    for _ in range(n):
        samp=[r for _ in members for r in bym[rng.choice(members)]]
        try:
            X,T=grads(samp); xs.append(X); ts.append(T)
        except Exception: pass
    xs.sort(); ts.sort()
    ci=lambda s:(s[int(.025*len(s))], s[int(.975*len(s))])
    return ci(xs), ci(ts)

CH=[("US-HOUSE","US House"),("US-SENATE","US Senate"),("UK","UK Commons"),
    ("CA-FED","CA federal"),("IE","Ireland")]
L=[]
L.append(f"{'chamber':10s}{'span':>11s}{'m-yrs':>7s}{'mean':>7s}"
         f"{'X individual/dec':>26s}{'T group/dec':>24s}")
full={}
for ch,_ in CH:
    rows=data[ch]
    X,T=grads(rows); (xlo,xhi),(tlo,thi)=boot(rows)
    W=sum(r[3] for r in rows); mean=sum(r[3]*r[4] for r in rows)/W
    span=f"{min(r[1] for r in rows)}-{max(r[1] for r in rows)}"
    full[ch]=(X,xlo,xhi,T,tlo,thi,span)
    L.append(f"{ch:10s}{span:>11s}{len(rows):>7d}{mean:>7.0f}"
             f"{X:>+12.1f} [{xlo:+.1f},{xhi:+.1f}]{T:>+12.1f} [{tlo:+.1f},{thi:+.1f}]")

L.append("")
L.append("WINDOWED individual gradients (the era evidence)")
L.append(f"{'chamber':10s}{'window':>11s}{'mean':>7s}{'X individual/dec':>26s}")
WIN=[("US-HOUSE",1994,2004),("US-HOUSE",2016,2026),
     ("US-SENATE",1994,2004),("US-SENATE",2016,2026),
     ("UK",1985,1995),("UK",2016,2026)]
win={}
for ch,y0,y1 in WIN:
    rows=[r for r in data[ch] if y0<=r[1]<=y1]
    X,_=grads(rows); (xlo,xhi),_=boot(rows,seed=11)
    Wt=sum(r[3] for r in rows); mean=sum(r[3]*r[4] for r in rows)/Wt
    win[(ch,y0)]=(X,xlo,xhi,mean)
    L.append(f"{ch:10s}{f'{y0}-{y1}':>11s}{mean:>7.0f}{X:>+12.1f} [{xlo:+.1f},{xhi:+.1f}]")
L.append("")
L.append("units: instrument occurrences per 100k words, per decade; word-weighted;")
L.append("member-cluster bootstrap CIs (300)")
txt="\n".join(L)
print(txt)
open("apc_chamber_decomposition.txt","w").write(txt+"\n")

# ---- chart: two panels, one unit ----
BLUE,ORANGE="#0072B2","#D55E00"
fig,(a1,a2)=plt.subplots(1,2,figsize=(11.6,4.9),dpi=150)
xs=np.arange(len(CH))
for i,(ch,lab) in enumerate(CH):
    X,xlo,xhi,T,tlo,thi,span=full[ch]
    a1.errorbar(i-0.13,T,yerr=[[T-tlo],[thi-T]],fmt="s",color=ORANGE,ms=8,
                capsize=3,elinewidth=1.2,markeredgecolor="white",markeredgewidth=1)
    a1.errorbar(i+0.13,X,yerr=[[X-xlo],[xhi-X]],fmt="o",color=BLUE,ms=8,
                capsize=3,elinewidth=1.2,markeredgecolor="white",markeredgewidth=1)
a1.axhline(0,color="#c7c7c7",lw=1)
a1.set_xticks(xs); a1.set_xticklabels([f"{lab}\n{full[ch][6]}" for ch,lab in CH],fontsize=8.5)
a1.set_ylabel("occurrences per 100k, per decade",fontsize=9.5)
a1.set_title("Group trends diverge; the individual gradient does not",
             fontsize=11,loc="left")
a1.errorbar([],[],fmt="s",color=ORANGE,label="group: chamber trend (T)")
a1.errorbar([],[],fmt="o",color=BLUE,label="individual: birth gradient (X)")
a1.legend(loc="upper left",frameon=False,fontsize=8.5)
for s in ("top","right"): a1.spines[s].set_visible(False)

W3=[("US-HOUSE","US House"),("US-SENATE","US Senate"),("UK","UK Commons")]
for i,(ch,lab) in enumerate(W3):
    for j,y0 in enumerate([1994 if ch!="UK" else 1985, 2016]):
        X,xlo,xhi,mean=win[(ch,y0)]
        a2.errorbar(i+(-0.14 if j==0 else 0.14),X,yerr=[[X-xlo],[xhi-X]],
                    fmt="o" if j else "^",color=BLUE if j else "#999999",ms=8,
                    capsize=3,elinewidth=1.2,markeredgecolor="white",markeredgewidth=1)
    a2.plot([i-0.14,i+0.14],[win[(ch,1994 if ch!="UK" else 1985)][0],win[(ch,2016)][0]],
            color="#bbbbbb",lw=1,zorder=1)
a2.axhline(0,color="#c7c7c7",lw=1)
a2.set_xticks(range(len(W3)))
a2.set_xticklabels([f"{lab}" for _,lab in W3],fontsize=9)
a2.set_title("…but it grew where drift-formed cohorts entered",fontsize=11,loc="left")
a2.errorbar([],[],fmt="^",color="#999999",label="early window (pre-drift cohorts)")
a2.errorbar([],[],fmt="o",color=BLUE,label="2016–2026")
a2.legend(loc="upper left",frameon=False,fontsize=8.5)
for s in ("top","right"): a2.spines[s].set_visible(False)
fig.suptitle("The individual-level birth gradient against the group-level trend, one ruler",
             fontsize=12.5,x=0.02,ha="left")
fig.tight_layout(rect=(0,0,1,0.93))
fig.savefig("apc_gradients.png",bbox_inches="tight")
print("\nwrote apc_gradients.png")
