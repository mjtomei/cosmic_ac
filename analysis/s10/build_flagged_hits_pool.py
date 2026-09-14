#!/usr/bin/env python3
"""Assemble every flagged prevalence segment (the estimator's own 316) with
its text, for the prepared-vs-spontaneous audit (blind-review AL1 response).

Sources: banded_prevalence.load() for the flagged set (chamber, band, id,
date); texts from the per-id RTF submission files (pangram_x/, pangram_ch/
etc.) and, for the UK/IE dashboard-rescore ids (chNNN), from the chamber
segment jsonls via the verdict CSV's seg_id. Writes flagged_hits_pool.json.
"""
import csv, glob, hashlib, json, os, re
import banded_prevalence as B

HERE=os.path.dirname(os.path.abspath(__file__))
import sys
WITH_TEXT = "--with-text" in sys.argv   # local inspection copy; never commit it
def rtf_text(path):
    s=open(path, encoding="utf-8", errors="replace").read()
    s=re.sub(r"\\par[d]?", "\n", s)
    s=re.sub(r"\\'[0-9a-f]{2}", " ", s)
    s=re.sub(r"\\[a-zA-Z]+-?\d* ?", "", s)
    s=s.replace("{","").replace("}","")
    return re.sub(r"\s+"," ", s).strip()

rows=B.load(); meta=B.META
fl=[(r,m) for r,m in zip(rows,meta) if r[1]=="prev" and r[4]]
idx={}
for d in [p for p in glob.glob(os.path.join(HERE,"pangram_*")) if os.path.isdir(p)]:
    for f in glob.glob(os.path.join(d,"*.rtf")):
        idx.setdefault(os.path.basename(f).rsplit(".",1)[0], f)

# mbNNN / shortband ids -> seg_id via their verdict CSVs
extra_seg={}
for fn in ("pangram_mb_redraw_verdicts.csv","pangram_shortband_verdicts.csv"):
    fp=os.path.join(HERE,fn)
    if os.path.exists(fp):
        for r in csv.DictReader(open(fp)):
            extra_seg[r["id"]]=r["seg_id"]

# chNNN -> seg_id -> uk/ie segment text
seg_of={}
for r in csv.DictReader(open(os.path.join(HERE,"pangram_ch_p4_verdicts.csv"))):
    seg_of[r["id"]]=(r["chamber"], r["seg_id"])
seg_text={}
need={sid for _,(chn,sid) in seg_of.items()}
need_extra={sid for sid in extra_seg.values()}
paths=["uk/segments_uk.jsonl","uk/segments_uk_2023.jsonl","uk/segments_uk_within.jsonl",
       "ie/segments_ie.jsonl","ie/segments_ie_en.jsonl","ie/segments_ie_within.jsonl"]
paths+=sorted(glob.glob(os.path.join(HERE,"provinces","segments_*.jsonl")))
if any(sid.startswith("US") for sid in need_extra):
    paths+=["us/segments_us_house.jsonl","us/segments_us_senate.jsonl","us/segments_us.jsonl"]
for path in paths:
    fp=os.path.join(HERE,path)
    if not os.path.exists(fp): continue
    for line in open(fp):
        s=json.loads(line)
        if (s.get("seg_id") in need or s.get("seg_id") in need_extra) and s["seg_id"] not in seg_text:
            seg_text[s["seg_id"]]=s["text"]

out=[]; miss=[]
for r,m in fl:
    ch,_,band,nw,_,frac=r
    t=None
    if m["id"] in idx: t=rtf_text(idx[m["id"]])
    elif m["id"] in seg_of and seg_of[m["id"]][1] in seg_text:
        t=seg_text[seg_of[m["id"]][1]]
    elif m["id"] in extra_seg and extra_seg[m["id"]] in seg_text:
        t=seg_text[extra_seg[m["id"]]]
    if t: out.append({"id":m["id"],"chamber":ch,"band":band,"date":m["date"],
                      "n_words":nw,"fraction_ai":frac,
                      # Pointer, not text. Three of the twenty chambers (BC,
                      # VIC, QLD) reserve Hansard reuse and four publish no
                      # terms, so the committed pool carries the SHA-256 of the
                      # scored string and a reader verifies against the
                      # chamber's own archive. Writing "text" here again would
                      # silently undo that on the next rebuild. Pass
                      # --with-text for a local copy, which stays untracked.
                      **({"text": t} if WITH_TEXT else
                         {"text_sha256": hashlib.sha256(t.encode("utf-8")).hexdigest(),
                          "n_chars": len(t)})})
    else: miss.append(m["id"])
print(f"assembled {len(out)} of {len(fl)}; missing {len(miss)}: {miss[:10]}")
json.dump(out, open(os.path.join(HERE,"flagged_hits_pool.json"),"w"))
