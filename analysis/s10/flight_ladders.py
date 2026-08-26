#!/usr/bin/env python3
"""Flight tests across the U-tops (review CC5, Matthew's direction): does the
top of EACH ladder avoid the words that became common, the way class I does?

For every ladder, lift is the corpus-level rise (class_word_year.json, all
classes pooled: 2023-26 rate over 2006-2022 rate — the recovered class-test
spec) and relative use is (top's 2023-26 rate) / (peak's 2023-26 rate) from
ladder_word_year.json; thresholds on top+peak 2023-26 occurrences. The class
row is the committed baseline (flight_correlation.py). Negative Spearman =
the top avoids what rose."""
import json, math
cw=json.load(open("class_word_year.json"))
lw=json.load(open("ladder_word_year.json"))
def rate_from(store, pred, y0, y1, word):
    num=den=0
    for key,w in store["tot"].items():
        g,y=key.rsplit("|",1); y=int(y)
        if y0<=y<=y1 and pred(g):
            den+=w; num+=store["per"].get(key,{}).get(word,0)
    return (num/den*1e5 if den else None), num
words=set()
for e in cw["per"].values(): words|=set(e)
lift={}
for w in words:
    pre,_=rate_from(cw, lambda g:True, 2006,2022, w)
    post,_=rate_from(cw, lambda g:True, 2023,2026, w)
    if pre and post: lift[w]=post/pre
def spearman(a,b):
    def rank(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
        for j,i in enumerate(s): r[i]=j
        return r
    ra,rb=rank(a),rank(b); n=len(a); ma,mb=sum(ra)/n,sum(rb)/n
    den=math.sqrt(sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb))
    return sum((x-ma)*(y-mb) for x,y in zip(ra,rb))/den if den else float("nan")
def battery(name, top, peak):
    rows=[]
    for w,lf in lift.items():
        rt,nt=rate_from(lw, lambda g:g==top, 2023,2026, w)
        rp,np_=rate_from(lw, lambda g:g==peak, 2023,2026, w)
        if rt is not None and rp:
            rows.append((lf, rt/rp, nt+np_))
    out=[]
    for th in (100,300,800,1500):
        sub=[r for r in rows if r[2]>=th]
        rho=spearman([r[0] for r in sub],[r[1] for r in sub]) if len(sub)>=10 else float("nan")
        out.append(f"{rho:+.2f}(n{len(sub)})" if rho==rho else f"  thin(n{len(sub)})")
    print(f"{name:38s} " + "  ".join(out))
print(f"{'ladder (top vs peak)':38s} {'100+':>12s}{'300+':>12s}{'800+':>12s}{'1500+':>12s}")
print(f"{'class I vs II (baseline, own cache)':38s} {'-0.13(n119)':>12s}{'-0.22(n68)':>12s}{'-0.42(n40)':>12s}{'-0.46(n25)':>12s}")
battery("education: professional vs bachelor", "edu_professional","edu_bachelor")
battery("education: graduate vs bachelor", "edu_graduate","edu_bachelor")
battery("occupation: executive vs middle", "rung_executive","rung_middle")
battery("office vs non-office", "office","nonoffice")
battery("folk ladder: top vs middle", "lvl_top","lvl_middle")
battery("folk ladder: free vs middle", "lvl_free","lvl_middle")
battery("folk ladder: bottom vs middle", "lvl_bottom","lvl_middle")
