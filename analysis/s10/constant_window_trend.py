#!/usr/bin/env python3
"""The constant-window register trend: 19 chambers, 2006-2026, one ruler.

Matthew's fix to the S4.5a table (2026-08-24): the old five-chamber table
mixed windows (UK/US 1994-, CA-FED 2015-, IE 2018-) and hung verdicts on
incomparable ratios. This reads occurrence_trends.json (per-chamber yearly
instrument-minus-placebo gaps, fixed instrument, fixed placebo sets) and
reports every chamber holding BOTH endpoints of the longest window most
chambers share: 2006 and 2026. Also the convergence statistic: Spearman rank
correlation between a chamber's 2006 level and its subsequent growth.

Excluded for missing an endpoint: AUS_SA (ends 2025), CA-FED (starts 2015),
IE (starts 2018). Writes constant_window_trend.csv.
"""
import csv, json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "occurrence_trends.json")))
NAME = {"UK":"UK Commons","SCOT":"Scotland","NI":"Northern Ireland","WALES":"Wales",
        "SK":"Saskatchewan","BC":"British Columbia","MB":"Manitoba","AB":"Alberta",
        "ON":"Ontario","NS":"Nova Scotia","NL":"Newfoundland & Labrador",
        "PE":"Prince Edward Island","AUS_NSW":"New South Wales","AUS_QLD":"Queensland",
        "AUS_VIC":"Victoria","AUS_WA":"Western Australia","AUS_TAS":"Tasmania",
        "US-House":"US House","US-Senate":"US Senate"}
rows=[]
for ch, ser in d.items():
    if ch.startswith("_") or ch in ("CA-FED","IE"): continue
    by={r["year"]: r for r in ser}
    if 2006 in by and 2026 in by:
        g0,g1=by[2006]["gap"],by[2026]["gap"]
        rows.append((NAME.get(ch,ch),g0,g1,g1/g0,(math.exp(math.log(g1/g0)/20)-1)*100))
rows.sort(key=lambda r:-r[4])
def rank(xs):
    s=sorted(range(len(xs)), key=lambda i: xs[i]); rk=[0.0]*len(xs)
    for j,i in enumerate(s): rk[i]=j
    return rk
xs=[r[1] for r in rows]; ys=[r[4] for r in rows]
rx,ry=rank(xs),rank(ys); n=len(rows)
mx=sum(rx)/n; my=sum(ry)/n
rho=sum((a-mx)*(b-my) for a,b in zip(rx,ry)) / math.sqrt(
    sum((a-mx)**2 for a in rx)*sum((b-my)**2 for b in ry))
with open(os.path.join(HERE,"constant_window_trend.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["chamber","gap_2006","gap_2026","change","pct_per_year"])
    for nm,g0,g1,r,p in rows: w.writerow([nm,round(g0),round(g1),round(r,2),round(p,1)])
print(f"{'chamber':24s}{'2006':>7s}{'2026':>7s}{'change':>8s}{'%/yr':>7s}")
for nm,g0,g1,r,p in rows: print(f"{nm:24s}{g0:7.0f}{g1:7.0f}{r:7.2f}x{p:+6.1f}")
print(f"\nSpearman(2006 level, growth) = {rho:+.2f}  (n={n})")
