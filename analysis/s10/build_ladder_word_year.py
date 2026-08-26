#!/usr/bin/env python3
"""(group, year, style word) counts for the flight tests on the OTHER U-tops
(review CC5, Matthew's direction): education (professional / graduate vs the
bachelor peak), occupational rung (executive vs the middle peak), and
ministerial office (rank-marked vs not), over the same provincial corpus as
the class flight test. Membership: prereg_member_table (edu, rung) joined on
prov|normalised-name; office from the rank-marked raw speaker form, as in
office_split.py. Lift comes from class_word_year.json (corpus-level), so
this cache only carries the group rates. Writes ladder_word_year.json."""
import csv, glob, json, os, re, sys
from collections import Counter, defaultdict
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import formation_window as FW
from office_split import RANK_RE
style={r["word"].lower() for r in csv.DictReader(open(os.path.join(HERE,"kobak_excess_words.csv")))
       if r["type"]=="style" and r["word"].isalpha()}
tab=json.load(open(os.path.join(HERE,"prereg_member_table.json")))
edu={}; rung={}; lvl={}
LVK=["lvl_FREE","lvl_BOTTOM","lvl_MIDDLE","lvl_TOP"]
for r in tab:
    if r.get("edu") in ("professional","graduate","bachelor"):
        edu[r["member"]]="edu_"+r["edu"]
    if r.get("rung") in ("executive","middle"):
        rung[r["member"]]="rung_"+r["rung"]
    if r.get("lvl_MIDDLE") is not None:
        # folk-ladder group = the member's highest-scoring level (argmax)
        vals=[r[k] for k in LVK]
        lvl[r["member"]]="lvl_"+LVK[vals.index(max(vals))].split("_")[1].lower()
tot=Counter(); per=defaultdict(Counter)
def add(group, yr, toks):
    tot[f"{group}|{yr}"]+=len(toks)
    k=per[f"{group}|{yr}"]
    for t in toks:
        if t in style: k[t]+=1
for path in sorted(glob.glob(os.path.join(HERE,"provinces","segments_*.jsonl"))):
    for line in open(path):
        d=json.loads(line)
        if not d.get("scoreable"): continue
        raw=d.get("speaker","")
        nm=FW.norm(raw)
        if not nm or FW.ROLE.match(nm): continue
        key=f"{d.get('prov')}|{nm}"
        yr=d["date"][:4]
        toks=None
        groups=[]
        if key in edu: groups.append(edu[key])
        if key in rung: groups.append(rung[key])
        if key in lvl: groups.append(lvl[key])
        groups.append("office" if RANK_RE.match(raw) else "nonoffice")
        if groups:
            toks=FW.TOKEN_RE.findall(d["text"].lower())
            for g in groups: add(g, yr, toks)
json.dump({"tot":tot,"per":{a:dict(b) for a,b in per.items()}},
          open(os.path.join(HERE,"ladder_word_year.json"),"w"))
print("wrote ladder_word_year.json:", len(tot), "group-years")
