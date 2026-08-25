#!/usr/bin/env python3
"""The pre-LLM word-context contrast, from the EXISTING scoring (review AL1+AL6).

Matthew's question made the GPU job unnecessary: every scored item carries a
full date, and the pre era spans 2018-2022. So the in-time placebo / pre-LLM
drift test reuses the committed occurrence log-probs unchanged:

  early-pre = 2018-2019   vs   late-pre = 2021-01-01 .. 2022-11-29
  (2020 dropped as a buffer; Dec 2022 dropped as post-ChatGPT)

Same estimands as word_context_delta.report(): raw = per-token
logP_instruct - logP_base at instrument-word positions; norm = raw minus the
same segment's full-trace delta. Both families. PARITY GUARD: the script
first reproduces the published pre-vs-post pooled norm (+0.0099) from the
same code path before computing the sub-era contrast. Permutation: sub-era
labels shuffled within chamber x family cells, 2,000 reps, pooled statistic.

If the late-minus-early change is positive, the register's context-permeation
was moving BEFORE any LLM existed to draft text -- carrying §4.8's
"independently of drafting" directly (no machine text is possible in either
cell) and answering the in-time-placebo demand: the instrument fires on
drift wherever drift exists, which under the paper's thesis is confirmation,
not demotion.
"""
import json, random
from collections import defaultdict

ITEMS="align_ratio/items.json"; OUT="word_context"
items=json.load(open(ITEMS))
FAM={"qwen":("base_occ_lp.json","instruct_occ_lp.json","qwen3_base_lp.json","qwen3_instruct_lp.json"),
     "mistral":("mistral_base_occ_lp.json","mistral_instruct_occ_lp.json","mistral_base_lp.json","mistral_instruct_lp.json")}

def rows_for(fam):
    b,i,fb,fi=FAM[fam]
    base=json.load(open(f"{OUT}/{b}")); inst=json.load(open(f"{OUT}/{i}"))
    FB=json.load(open(f"align_ratio/{fb}")); FI=json.load(open(f"align_ratio/{fi}"))
    out=defaultdict(list)
    for it,bo,io,(bt,bn),(itt,itn) in zip(items,base,inst,FB,FI):
        di,ni=0.0,0
        for (bl,btk,bi_),(il,itk,ii) in zip(bo,io):
            if not bi_: continue
            di+=(il-bl)/max(btk,1); ni+=1
        if not ni: continue
        full=(itt-bt)/max(min(bn,itn),1)
        out[(it["chamber"],fam)].append(
            {"era":it["era"],"date":it["date"],"norm":di/ni-full,"raw":di/ni,"turn":it["turn_id"]})
    return out

cells={}
for fam in FAM: cells.update(rows_for(fam))

def pooled(sel_a, sel_b, key="norm"):
    """equal-weight cell mean of (mean_b - mean_a); returns (pooled, ncells, npos)"""
    ch=[]
    for c,rs in cells.items():
        A=[r[key] for r in rs if sel_a(r)]; B=[r[key] for r in rs if sel_b(r)]
        if len(A)>=30 and len(B)>=30:
            ch.append((c, sum(B)/len(B)-sum(A)/len(A), len(A), len(B)))
    p=sum(x[1] for x in ch)/len(ch)
    return p, ch

# PARITY: published pre-vs-post
p0,ch0=pooled(lambda r:r["era"]=="pre", lambda r:r["era"]=="post")
print(f"parity (pre->post pooled norm): {p0:+.4f}  cells {len(ch0)}, positive {sum(1 for x in ch0 if x[1]>0)}")

EARLY=lambda r: r["era"]=="pre" and r["date"]<"2020-01-01"
LATE =lambda r: r["era"]=="pre" and "2021-01-01"<=r["date"]<"2022-11-30"
p1,ch1=pooled(EARLY,LATE)
print(f"\nPRE-LLM contrast (2018-19 -> 2021..2022-11) pooled norm: {p1:+.4f}")
for c,d,na,nb in sorted(ch1): print(f"  {c[0]:<4s} {c[1]:<7s} n={na}/{nb}  change {d:+.4f}")
print(f"positive cells: {sum(1 for x in ch1 if x[1]>0)}/{len(ch1)}")

# permutation: shuffle early/late labels within cell
rng=random.Random(23); B=2000; hits=0
prep={}
for c,rs in cells.items():
    E=[r["norm"] for r in rs if EARLY(r)]; L=[r["norm"] for r in rs if LATE(r)]
    if len(E)>=30 and len(L)>=30: prep[c]=(E,L)
obs=p1
for _ in range(B):
    tot=0
    for c,(E,L) in prep.items():
        allv=E+L; rng.shuffle(allv)
        e2,l2=allv[:len(E)],allv[len(E):]
        tot+=sum(l2)/len(l2)-sum(e2)/len(e2)
    if tot/len(prep)>=obs: hits+=1
print(f"permutation (labels shuffled within cell, {B}): p = {hits}/{B} = {hits/B:.3f}")

# raw estimand alongside
p1r,_=pooled(EARLY,LATE,key="raw")
print(f"raw-estimand pooled change: {p1r:+.4f}")
