#!/usr/bin/env python3
"""The flight correlation, committed (review CC5): class I's relative use of
an instrument word against how much that word rose, Spearman, by volume
threshold. Reads class_word_year.json ({tot: class|year -> words,
per: class|year -> {word: count}}).

Spec (recovered exactly; reproduces the published series to the digit):
lift = (all-class pooled rate 2023-2026) / (all-class pooled rate
2006-2022); class-I relative use = I's 2023-26 rate for the word against
class II's; words enter at thresholds 100/300/800/1500 on their pooled
I+II occurrences in 2023-26. Spearman(lift, I-vs-II relative use):
-0.13 (n=119) / -0.22 (n=68) / -0.42 (n=40) / -0.46 (n=25)."""
import json, math
d=json.load(open("class_word_year.json"))
tot,per=d["tot"],d["per"]
def split(key): c,y=key.rsplit("|",1); return c,int(y)
words=set()
for e in per.values(): words|=set(e)
def rate(word, cls_pred, y0,y1):
    num=den=0
    for key,w in tot.items():
        c,y=split(key)
        if y0<=y<=y1 and cls_pred(c):
            den+=w; num+=per.get(key,{}).get(word,0)
    return (num/den*1e5 if den else None), num
def spearman(a,b):
    def rank(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
        for j,i in enumerate(s): r[i]=j
        return r
    ra,rb=rank(a),rank(b); n=len(a)
    ma,mb=sum(ra)/n,sum(rb)/n
    return sum((x-ma)*(y-mb) for x,y in zip(ra,rb))/math.sqrt(
        sum((x-ma)**2 for x in ra)*sum((y-mb)**2 for y in rb))
rows=[]
for w in sorted(words):
    pre,_=rate(w, lambda c:True, 2006,2022)
    post,n_post=rate(w, lambda c:True, 2023,2026)
    ri,_=rate(w, lambda c:c=="I", 2023,2026)
    rii,_=rate(w, lambda c:c=="II", 2023,2026)
    _,nv1=rate(w, lambda c:c=="I", 2023,2026)
    _,nv2=rate(w, lambda c:c=="II", 2023,2026)
    if pre and post and rii and ri is not None:
        rows.append((w, post/pre, ri/rii, nv1+nv2))
for th in (100,300,800,1500):
    sub=[r for r in rows if r[3]>=th]
    rho=spearman([r[1] for r in sub],[r[2] for r in sub])
    print(f"threshold {th:>5}: n={len(sub):>3}  Spearman(lift, I-relative-use) = {rho:+.2f}")
