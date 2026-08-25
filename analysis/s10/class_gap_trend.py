#!/usr/bin/env python3
"""The second dynamic signature of chase-and-flight (Matthew, 2026-08-25):
even with the peak stationary, a WIDENING II-over-I separation across eras
would evidence flight in progress. Reads class_by_era_grouped.csv (means and
ses within chamber x period z), computes the II-I gap per half-decade and its
inverse-variance-weighted trend. Result: flat — +0.152 (1995-99) to +0.153
(2025-26), trend −0.005/half-decade (t −0.43). Both dynamic signatures (peak
migration; gap widening) are now tested and null in-window."""
import csv, math
rows=list(csv.DictReader(open("class_by_era_grouped.csv")))
by={(r["group"],r["half_decade"]):(float(r["mean_z"]),float(r["se"])) for r in rows}
bins=sorted({r["half_decade"] for r in rows})
gaps=[]
for b in bins:
    if ("II",b) in by and ("I",b) in by:
        (m2,s2),(m1,s1)=by[("II",b)],by[("I",b)]
        gaps.append((b,m2-m1,math.sqrt(s1*s1+s2*s2)))
for b,g,se in gaps: print(f"{b:12s} gap II−I {g:+.3f} (se {se:.3f})")
xs=range(len(gaps)); ys=[g for _,g,_ in gaps]; ws=[1/se**2 for _,_,se in gaps]
W=sum(ws); mx=sum(w*x for w,x in zip(ws,xs))/W; my=sum(w*y for w,y in zip(ws,ys))/W
b1=sum(w*(x-mx)*(y-my) for w,x,y in zip(ws,xs,ys))/sum(w*(x-mx)**2 for w,x in zip(ws,xs))
seb=math.sqrt(1/sum(w*(x-mx)**2 for w,x in zip(ws,xs)))
print(f"weighted trend: {b1:+.4f}/half-decade (se {seb:.4f}, t {b1/seb:+.2f})")
