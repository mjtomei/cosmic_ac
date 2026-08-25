#!/usr/bin/env python3
"""The register as a detector, tested directly (review CE2; Matthew's cuts).

A simple threshold on the register score — occurrences of the 407 Kobak style
words per 100k words, the study's own instrument — evaluated as a classifier
by AUC on four label sets:

  A. all segments Pangram scored that we can text-resolve (legislative
     prevalence + controls + the CA-FED genre arm + the 292 final-run bypass
     variants), label = Pangram flag (AI/Mixed vs Human);
  B. legislative segments only (no LLM-generated text), label = Pangram flag;
  C. ground truth: known LLM-generated text (the final-run bypass variants,
     Opus rewrites) vs known human (the pre-2022 controls);
  D. the hard case: 2025-26 legislative prevalence segments only — both
     classes drifted contemporary speech, label = Pangram flag.

Register scores use the same word list and boundary rule as the instrument.
AUC = Mann-Whitney. Writes register_auc_check.txt.
"""
import csv, glob, json, os, re
import banded_prevalence as B

HERE=os.path.dirname(os.path.abspath(__file__))
STYLE=[r["word"].lower() for r in csv.DictReader(open("kobak_excess_words.csv"))
       if r["type"]=="style" and r["word"].isalpha()]
RX=re.compile(r"\b(" + "|".join(sorted(STYLE,key=len,reverse=True)) + r")\b", re.I)
TOK=re.compile(r"[a-z']+")

def rtf_text(path):
    s=open(path,encoding="utf-8",errors="replace").read()
    s=re.sub(r"\\par[d]?","\n",s); s=re.sub(r"\\'[0-9a-f]{2}"," ",s)
    s=re.sub(r"\\[a-zA-Z]+-?\d* ?","",s); s=s.replace("{","").replace("}","")
    return re.sub(r"\s+"," ",s).strip()

def score(text):
    n=len(TOK.findall(text.lower()))
    return (len(RX.findall(text))/n*1e5, n) if n else (None,0)

# --- resolve texts for every estimator row + genre rows (ids like the flagged builder) ---
idx={}
for d in [p for p in glob.glob(os.path.join(HERE,"pangram_*")) if os.path.isdir(p)]:
    for f in glob.glob(os.path.join(d,"*.rtf")):
        idx.setdefault(os.path.basename(f).rsplit(".",1)[0], f)
seg_need={}
for fn,idc,segc in [("pangram_ch_p4_verdicts.csv","id","seg_id"),
                    ("pangram_mb_redraw_verdicts.csv","id","seg_id"),
                    ("pangram_shortband_verdicts.csv","id","seg_id")]:
    for r in csv.DictReader(open(fn)): seg_need[r[idc]]=r[segc]
seg_text={}
need=set(seg_need.values())
paths=(["uk/segments_uk.jsonl","uk/segments_uk_2023.jsonl","uk/segments_uk_within.jsonl",
        "ie/segments_ie.jsonl","ie/segments_ie_en.jsonl","ie/segments_ie_within.jsonl"]
       + sorted(glob.glob("provinces/segments_*.jsonl"))
       + ["us/segments_us_house.jsonl","us/segments_us_senate.jsonl","us/segments_us.jsonl"])
for path in paths:
    if not os.path.exists(path): continue
    for line in open(path):
        s=json.loads(line)
        if s.get("seg_id") in need and s["seg_id"] not in seg_text:
            seg_text[s["seg_id"]]=s["text"]

def text_of(i):
    if i in idx: return rtf_text(idx[i])
    if i in seg_need and seg_need[i] in seg_text: return seg_text[seg_need[i]]
    return None

rows=B.load(); meta=B.META
leg=[]; miss=0
for r,m in zip(rows,meta):
    t=text_of(m["id"])
    if not t: miss+=1; continue
    sc,_=score(t)
    if sc is None: continue
    leg.append({"set":"est","role":r[1],"flag":r[4],"score":sc})
# genre-arm rows (CA-FED, arm=genre)
for r in csv.DictReader(open("pangram_p4_verdicts.csv")):
    if r.get("arm")=="genre" and r.get("pangram"):
        t=text_of(r["file"].split(".")[0])
        if not t: miss+=1; continue
        sc,_=score(t)
        if sc is None: continue
        leg.append({"set":"genre","role":r["stratum"],"flag":r["pangram"] in ("AI","Mixed"),"score":sc})
print(f"legislative rows scored: {len(leg)} (unresolved {miss})")

llm=[]
for f in ("bypass_text/bypass_v3_text.json","bypass_text/gov_bypass_v3_text.json"):
    for k,t in json.load(open(f)).items():
        sc,_=score(t)
        if sc is not None: llm.append({"score":sc})
print(f"known-LLM variants scored: {len(llm)}")

def auc(pos,neg):
    import bisect
    neg_s=sorted(neg); n=len(pos)*len(neg); w=0.0
    for p in pos:
        lo=bisect.bisect_left(neg_s,p); hi=bisect.bisect_right(neg_s,p)
        w+=lo+(hi-lo)/2
    return w/n

L=[]
def rep(name,pos,neg):
    a=auc(pos,neg)
    L.append(f"{name:55s} AUC {a:.3f}   (n+ {len(pos)}, n- {len(neg)})")
    print(L[-1])

ctl=[x["score"] for x in leg if x["role"]=="ctl"]
prev=[x for x in leg if x["role"]=="prev"]
flag_leg=[x["score"] for x in leg if x["flag"]]
noflag_leg=[x["score"] for x in leg if not x["flag"]]
rep("B. legislative only (flagged vs not, incl. controls)", flag_leg, noflag_leg)
rep("D. 2025-26 prevalence only (flagged vs not)", [x["score"] for x in prev if x["flag"]],
    [x["score"] for x in prev if not x["flag"]])
rep("C. ground truth: LLM variants vs pre-2022 controls", [x["score"] for x in llm], ctl)
rep("A. everything (leg flagged+LLM vs leg unflagged)", flag_leg+[x["score"] for x in llm], noflag_leg)
import statistics as st
L.append(f"medians per 100k: controls {st.median(ctl):.0f}, unflagged prev "
         f"{st.median([x['score'] for x in prev if not x['flag']]):.0f}, flagged prev "
         f"{st.median([x['score'] for x in prev if x['flag']]):.0f}, LLM variants {st.median([x['score'] for x in llm]):.0f}")
print(L[-1])
open("register_auc_check.txt","w").write("\n".join(L)+"\n")
