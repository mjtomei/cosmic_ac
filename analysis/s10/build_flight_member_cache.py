#!/usr/bin/env python3
"""Member-level (member, year, style word) counts over the provinces —
the asset behind the flight decoupling checks (permutation null,
split-half) and the individual-level chase-and-flight checks (within-member
event study, lead-lag). One provincial scan; members keyed prov|norm with
their EGP class (occupation_coding join, as build_class_word_year.py) and,
where scored, their folk-ladder argmax level. Writes
flight_member_cache.json.gz: {member: {"egp":..., "lvl":..., "years":
{year: {"tot": n, "w": {word: count}}}}}."""
import csv, glob, gzip, json, os, sys
from collections import defaultdict
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import formation_window as FW
import panel_estimation as PE
style={r["word"].lower() for r in csv.DictReader(open(os.path.join(HERE,"kobak_excess_words.csv")))
       if r["type"]=="style" and r["word"].isalpha()}
code=PE.coding_maps()
egp={}
for r in PE.provincial_rows(code):
    if r["egp"]: egp["|".join(r["member"].split("|")[:2])]=r["egp"]
LVK=["lvl_FREE","lvl_BOTTOM","lvl_MIDDLE","lvl_TOP"]
lvl={}
for r in json.load(open(os.path.join(HERE,"prereg_member_table.json"))):
    if r.get("lvl_MIDDLE") is not None:
        vals=[r[k] for k in LVK]
        lvl["|".join(r["member"].split("|")[:2])]=LVK[vals.index(max(vals))].split("_")[1].lower()
out=defaultdict(lambda: {"egp":None,"lvl":None,"years":defaultdict(lambda:{"tot":0,"w":defaultdict(int)})})
for path in sorted(glob.glob(os.path.join(HERE,"provinces","segments_*.jsonl"))):
    for line in open(path):
        d=json.loads(line)
        if not d.get("scoreable"): continue
        nm=FW.norm(d.get("speaker",""))
        if not nm or FW.ROLE.match(nm): continue
        key=f"{d.get('prov')}|{nm}"
        if key not in egp and key not in lvl: continue
        yr=d["date"][:4]
        toks=FW.TOKEN_RE.findall(d["text"].lower())
        rec=out[key]; y=rec["years"][yr]
        y["tot"]+=len(toks)
        for t in toks:
            if t in style: y["w"][t]+=1
for k,rec in out.items():
    rec["egp"]=egp.get(k); rec["lvl"]=lvl.get(k)
    rec["years"]={y:{"tot":v["tot"],"w":dict(v["w"])} for y,v in rec["years"].items()}
with gzip.open(os.path.join(HERE,"flight_member_cache.json.gz"),"wt") as f:
    json.dump(dict(out), f)
print("wrote flight_member_cache.json.gz:", len(out), "members")
