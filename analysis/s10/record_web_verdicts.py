#!/usr/bin/env python3
"""Record dashboard verdicts for the S10 expansion and emit the next batch.

The dashboard route exists because the API balance is spent; both routes run
Pangram 4 and were verified to agree 20/20 including Mixed (api_route_check.py),
so verdicts from the two land in the same file and are directly comparable.

Reads the results panel's text on stdin, e.g.

    python record_web_verdicts.py < page.txt

The panel renders as repeating triples:

    cabctl056.rtf
    2 Credits,123 Words
    Human

Anything else on the page is ignored. Files already recorded are skipped, so
re-feeding the same page twice is harmless.

Prints the running tally, the credit spend, and the next 100 absolute paths
(the dashboard caps a batch at 100 files).
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = os.path.join(HERE, "pangram_p4_verdicts.csv")
FIELDS = ["file", "source", "chamber", "stratum", "arm", "seg_id", "date",
          "speaker", "n_words", "genre", "regime_flag", "pangram",
          "fraction_ai", "version", "prior_p3"]
DIRS = {"pangram_x_manifest.json": "pangram_x",
        "pangram_genre_manifest.json": "pangram_genre"}
BATCH = 100          # HARD CAP: the dialog warns "CSV has N rows. Only the
                     # first 100 will be processed." The 30MB file limit is
                     # not the binding constraint; 100 rows per scan is.
VERD = ("Human", "AI", "Mixed")
# two upload modes produce two label formats:
#   one RTF per segment ->  "cabctl052.rtf"
#   one CSV per batch   ->  "batch03.csv (cabctl052)"   <- the tag column
# CSV mode is the one to use: the dashboard caps a batch at 100 files but a
# CSV counts as ONE file, and the optional tag column carries the segment id
# through to the result row, which is the attribution we would otherwise
# lose. 2,827 segments go in 6 CSVs instead of 29 upload rounds.
LINE = re.compile(r"^(?:[\w.-]+\.csv \((\w+)\)|(\w+)\.rtf)$")


def main():
    man, home = {}, {}
    for mf, sub in DIRS.items():
        p = os.path.join(HERE, mf)
        if os.path.exists(p):
            got = json.load(open(p))
            man.update(got)
            home.update({k: sub for k in got})

    rows = []
    if os.path.exists(VERDICTS):
        rows = [r for r in csv.DictReader(open(VERDICTS)) if r.get("pangram")]
    have = {r["file"] for r in rows}

    raw = sys.stdin.read()
    # Compact form "n|id verdict|id verdict|..." produced by the in-page
    # extractor, which is ~2.5x cheaper to move than the rendered panel text.
    # Falls back to parsing the panel directly.
    pairs = []
    # Run-length form "aqlprev085+35:HHAHM..." — ids inside a batch are
    # consecutive, so emitting prefix+start+count+letters costs ~50 chars
    # where the pair list costs ~420. Keeps a 100-row round inside the
    # tool's ~1kB output truncation in ONE call instead of two.
    RLE = re.compile(r"([A-Za-z_]+)(\d+)\+(\d+):([HAM]+)")
    for pre, start, n, letters in RLE.findall(raw):
        w = len(start)
        for k, ch in enumerate(letters):
            pairs.append((f"{pre}{int(start) + k:0{w}d}",
                          {"H": "Human", "A": "AI", "M": "Mixed"}[ch]))
    if pairs:
        pass
    elif "|" in raw:
        for tok in raw.split("|"):
            bits = tok.strip().split()
            if len(bits) == 2:
                # single-letter form keeps each round's payload under the
                # tool's ~1kB output truncation limit
                v = {"H": "Human", "A": "AI", "M": "Mixed"}.get(bits[1],
                                                                bits[1])
                if v in VERD:
                    pairs.append((bits[0], v))
    else:
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        for i, l in enumerate(lines):
            m = LINE.match(l)
            if not m:
                continue
            v = next((x for x in lines[i + 1:i + 3] if x in VERD), None)
            if v:
                pairs.append((m.group(1) or m.group(2), v))

    added, skipped = 0, 0
    for name, v in pairs:
        if name not in man:
            continue
        if name in have:
            skipped += 1
            continue
        mm = man[name]
        rows.append({"file": name, "source": "expansion_web",
                     "chamber": mm["chamber"], "stratum": mm["stratum"],
                     "arm": mm["arm"], "seg_id": mm["seg_id"],
                     "date": mm["date"], "speaker": mm.get("speaker", ""),
                     "n_words": mm["n_words"], "genre": mm.get("genre", ""),
                     "regime_flag": mm.get("regime_flag", ""),
                     "pangram": v, "fraction_ai": "", "version": "4.0-web",
                     "prior_p3": ""})
        have.add(name)
        added += 1

    with open(VERDICTS, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["source"], r["file"])))

    todo = [n for n in sorted(man) if n not in have]
    spent = sum(-(-int(r["n_words"]) // 100) for r in rows
                if r["source"] == "expansion_web")
    print(f"added {added}, already had {skipped}")
    print(f"expansion done {len(man) - len(todo):,}/{len(man):,}  "
          f"remaining {len(todo):,}")
    print(f"dashboard credits spent so far: {spent:,} of 11,123")

    web = [r for r in rows if r["source"] == "expansion_web"]
    if web:
        t = defaultdict(Counter)
        for r in web:
            t[(r["chamber"], r["stratum"])][r["pangram"]] += 1
        fp = sum(1 for r in web
                 if r["stratum"] == "ctl" and r["pangram"] in ("AI", "Mixed"))
        nctl = sum(1 for r in web if r["stratum"] == "ctl")
        if nctl:
            print(f"control false positives: {fp}/{nctl}"
                  f"{'   <-- INVESTIGATE' if fp else '  (clean)'}")
    if todo:
        # emit the next CSV batch rather than a path list
        import csv as _csv
        sys.path.insert(0, HERE)
        from api_route_check import unrtf
        nxt = todo[:BATCH]
        out = os.path.join(HERE, "web_batches",
                           f"batch{len(man) - len(todo):06d}.csv")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", newline="") as fh:
            w = _csv.writer(fh)
            w.writerow(["id", "text"])
            for n in nxt:
                w.writerow([n, unrtf(open(os.path.join(
                    HERE, home[n], n + ".rtf")).read())])
        cred = sum(-(-man[n]["n_words"] // 100) for n in nxt)
        print(f"\nNEXT_BATCH_CSV  {out}")
        print(f"  {len(nxt)} rows, {os.path.getsize(out) / 1e6:.2f} MB, "
              f"~{cred:,} credits")


if __name__ == "__main__":
    main()
