#!/usr/bin/env python3
"""(class, year, style word) counts -- for the year control and the flight test."""
import csv, glob, json, os, sys
from collections import Counter, defaultdict
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import formation_window as FW
import class_markedness as CM
style={r["word"].lower() for r in csv.DictReader(open(os.path.join(HERE,"kobak_excess_words.csv")))
       if r["type"]=="style" and r["word"].isalpha()}
cls=CM.member_class()
tot=Counter(); per=defaultdict(Counter)
for path in sorted(glob.glob(os.path.join(HERE,"provinces","segments_*.jsonl"))):
    for line in open(path):
        d=json.loads(line)
        if not d.get("scoreable"): continue
        nm=FW.norm(d.get("speaker",""))
        if not nm or FW.ROLE.match(nm): continue
        c=cls.get((d.get("prov"),nm))
        if not c: continue
        yr=d["date"][:4]
        toks=FW.TOKEN_RE.findall(d["text"].lower())
        tot[f"{c}|{yr}"]+=len(toks)
        k=per[f"{c}|{yr}"]
        for t in toks:
            if t in style: k[t]+=1
json.dump({"tot":tot,"per":{a:dict(b) for a,b in per.items()}},
          open(os.path.join(HERE,"class_word_year.json"),"w"))
print("wrote class_word_year.json:", len(tot), "class-years")

