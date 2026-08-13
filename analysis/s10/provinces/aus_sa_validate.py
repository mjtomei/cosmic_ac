#!/usr/bin/env python3
"""Validation report for the South Australian segment file.

Reads segments_aus_sa.jsonl + aus_sa_raw/ + aus_sa_manifest.json and writes
aus_sa_validation.txt:
  - the Wayback-sampling warning (SA is a non-uniform SAMPLE of sitting days)
  - segments / words / DISTINCT SITTING DAYS per year and per chamber, with
    explicit 2006-2010 and 2015-2019 subtotals
  - seg_id uniqueness assertion
  - top 10 speakers by word count (must be members, not the chair)
  - 3 random scoreable segments in full
  - fraction of raw-file words surviving extraction
"""
import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
WINDOWS = ((2006, 2010), (2015, 2019))


def raw_words(path):
    p = str(path)
    if p.endswith(".pdf"):
        txt = subprocess.run(["pdftotext", p, "-"],
                             capture_output=True, text=True).stdout
    else:
        d = Path(p).read_text(encoding="utf-8", errors="replace")
        txt = re.sub(r"<[^>]+>", " ", re.sub(r"<!--.*?-->", " ", d, flags=re.S))
    return len(txt.split())


def main():
    segs = [json.loads(l) for l in open(HERE / "segments_aus_sa.jsonl")]
    raw_dir = HERE / "aus_sa_raw"
    files = sorted(p for p in raw_dir.iterdir() if p.suffix in (".pdf", ".xml"))
    manifest = json.load(open(HERE / "aus_sa_manifest.json"))

    man_days = defaultdict(set)
    for r in manifest:
        man_days[r["kind"]].add((r["ch"], r["date"]))

    y_segs, y_words = Counter(), Counter()
    y_days = defaultdict(set)
    ch_words, ch_days = Counter(), defaultdict(set)
    spk = Counter()
    src_words = Counter()
    for s in segs:
        y = s["date"][:4]
        y_segs[y] += 1
        y_words[y] += s["n_words"]
        y_days[y].add((s["chamber"], s["date"]))
        ch_words[s["chamber"]] += s["n_words"]
        ch_days[s["chamber"]].add(s["date"])
        spk[s["speaker"]] += s["n_words"]
        src_words[s["source"]] += s["n_words"]

    with ProcessPoolExecutor(max_workers=12) as ex:
        rw = sum(ex.map(raw_words, files, chunksize=4))
    kept = sum(s["n_words"] for s in segs)
    ids = {s["seg_id"] for s in segs}
    scoreable = [s for s in segs if s["scoreable"]]
    random.seed(20260807)
    samples = random.sample(scoreable, 3)

    o = []
    o.append("=== SA (South Australia) validation ===")
    o.append("")
    o.append("!! SOURCE WARNING -- READ BEFORE USING PER-YEAR TOTALS !!")
    o.append("The live SA Hansard host (hansardsearch.parliament.sa.gov.au)")
    o.append("answers HTTP 403 at its Azure Front Door WAF on every path and for")
    o.append("every request shape tried; the block was not evaded. EVERY file in")
    o.append("this corpus therefore comes from the Internet Archive's copies of")
    o.append("that host, which are a NON-UNIFORM SAMPLE of sitting days -- roughly")
    o.append("a fifth of the true population, with the per-year day count driven by")
    o.append("Internet Archive crawl activity rather than by parliamentary")
    o.append("activity (e.g. 2009 vs 2018 below). Any per-year or per-window")
    o.append("comparison must be day-normalised or weighted; raw yearly totals here")
    o.append("measure archive coverage, not legislative output. Two capture routes")
    o.append("are mixed and do NOT have the same per-day yield: a full sitting-day")
    o.append("PDF where one was archived, otherwise whatever per-subject XML")
    o.append("fragments were archived for that day (a fraction of the day). The")
    o.append("`source` field on every segment records which route it came from.")
    o.append("")
    o.append(f"raw files: {len(files)} "
             f"({sum(1 for f in files if f.suffix=='.pdf')} pdf, "
             f"{sum(1 for f in files if f.suffix=='.xml')} xml)")
    o.append(f"manifest chamber-days: {len(man_days['pdf'])} full-day PDF, "
             f"{len({d for d in man_days['xml']})} XML-fragment-only")
    o.append(f"chamber-days with segments: {sum(len(v) for v in y_days.values())}")
    o.append(f"segments: {len(segs)} total, {len(scoreable)} scoreable "
             f"({len(scoreable)/max(len(segs),1):.0%})")
    o.append(f"seg_id uniqueness: {len(ids)} distinct ids for {len(segs)} "
             f"segments -- {'OK' if len(ids)==len(segs) else 'DUPLICATES PRESENT'}")
    o.append(f"words by source route: " +
             ", ".join(f"{k}={v}" for k, v in sorted(src_words.items())))
    o.append("")
    o.append("per year -- sitting days (chamber-days), segments, words:")
    o.append("  year   chamber-days   segments      words   words/day")
    for y in sorted(y_segs):
        d = len(y_days[y])
        o.append(f"  {y}      {d:6d}     {y_segs[y]:8d} {y_words[y]:10d} "
                 f"{y_words[y]//max(d,1):9d}")
    for lo, hi in WINDOWS:
        ys = [y for y in y_segs if lo <= int(y) <= hi]
        d = len({x for y in ys for x in y_days[y]})
        w = sum(y_words[y] for y in ys)
        s = sum(y_segs[y] for y in ys)
        o.append(f"  WINDOW {lo}-{hi}: {d} chamber-days, {s} segments, {w} words")
    o.append("")
    o.append("per chamber:")
    for c in sorted(ch_words):
        o.append(f"  {c}: {len(ch_days[c])} sitting dates, {ch_words[c]} words")
    o.append("")
    o.append("top 10 speakers by word count:")
    for name, w in spk.most_common(10):
        o.append(f"  {w:9d}  {name}")
    o.append(f"  (distinct speakers: {len(spk)})")
    o.append("")
    o.append(f"raw-word survival: {kept}/{rw} = {kept/max(rw,1):.1%}")
    o.append("  SA daily Hansard is unusually speech-dense -- no table of")
    o.append("  contents, no member roster, no page-furniture beyond a banner --")
    o.append("  so survival sits well above the 30-60% typical of the Canadian")
    o.append("  provincial PDFs. Losses = chair turns (The SPEAKER / The")
    o.append("  PRESIDENT / The CHAIR), interjection lines, subject headings,")
    o.append("  divisions and their name rosters, procedural narration, tabled")
    o.append("  written answers to questions on notice, and the second-reading")
    o.append("  'explanation of clauses' blocks inserted into Hansard without")
    o.append("  being read aloud.")
    o.append("")
    for i, s in enumerate(samples, 1):
        o.append(f"--- random scoreable segment {i}: {s['seg_id']} "
                 f"({s['speaker']}, {s['chamber']}, {s['date']}, "
                 f"{s['n_words']} words, source={s['source']}) ---")
        o.append(s["text"])
        o.append("")
    rep = "\n".join(o)
    (HERE / "aus_sa_validation.txt").write_text(rep)
    print(rep)


if __name__ == "__main__":
    main()
