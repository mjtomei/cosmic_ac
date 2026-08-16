#!/usr/bin/env python3
"""Wikipedia article length for the tier-1 legislators, from evidence URLs.

The tier-1 covariate records (covariates_tier1.json) carry, for 4,198 of
4,372 members, a wikipedia-tier evidence entry whose URL is the member's
article. We take the title from that URL and fetch page length (wikitext
bytes) from the MediaWiki API, exactly the notability instrument wiki_depth.py
built for the provinces via QID. Keyed by (chamber, roster key) so it joins to
member_year_rates_t1.json. Backoff on 429, same as wiki_depth.py.

Usage: python build_t1_wiki_depth.py    # writes wiki_depth_t1.json
"""
import json, os, time, urllib.parse, urllib.error, urllib.request
from collections import defaultdict
HERE=os.path.dirname(os.path.abspath(__file__))
UA="s10-legislative-register-study/1.0 (research; contact via repo)"
def get(url,tries=6):
    delay=2.0
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":UA}),timeout=60) as f:
                return json.load(f)
        except urllib.error.HTTPError as e:
            if e.code!=429 or a==tries-1: raise
            w=float(e.headers.get("Retry-After") or delay); print(f"  429; wait {w:.0f}s",flush=True)
            time.sleep(w); delay=min(delay*2,60)
def main():
    recs=json.load(open(os.path.join(HERE,"covariates_tier1.json")))
    # member -> title (first wikipedia article URL in its evidence)
    title_of={}
    for r in recs:
        for e in (r.get("evidence") or []):
            u=e.get("url","") if isinstance(e,dict) else ""
            if "en.wikipedia.org/wiki/" in u:
                t=urllib.parse.unquote(u.split("/wiki/")[-1].split("#")[0].replace("_"," "))
                title_of[(r["chamber"], r["key"])]=t; break
    titles=sorted(set(title_of.values()))
    print(f"{len(title_of)} members with an article title; {len(titles)} distinct")
    length={}
    def chunks(xs,n):
        for i in range(0,len(xs),n): yield xs[i:i+n]
    for i,batch in enumerate(chunks(titles,50)):
        url="https://en.wikipedia.org/w/api.php?action=query&prop=info&format=json&titles="+urllib.parse.quote("|".join(batch),safe="|")
        try: d=get(url)
        except Exception as ex: print(f"  batch {i}: {ex}"); continue
        norm={n["from"]:n["to"] for n in d.get("query",{}).get("normalized",[])}
        for pg in (d.get("query",{}).get("pages") or {}).values():
            if pg.get("title") and "length" in pg: length[pg["title"]]=pg["length"]
        if i%10==0: print(f"  batch {i+1}: {len(length)} lengths",flush=True)
        time.sleep(2.5)
    out={}
    for (ch,key),t in title_of.items():
        # match via normalized title if needed
        out[f"{ch}|{key}"]={"title":t,"length":length.get(t)}
    json.dump(out,open(os.path.join(HERE,"wiki_depth_t1.json"),"w"))
    got=sum(1 for v in out.values() if v.get("length"))
    print(f"wrote wiki_depth_t1.json: {got}/{len(out)} members with a length")
if __name__=="__main__": main()
