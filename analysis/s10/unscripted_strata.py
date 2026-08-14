#!/usr/bin/env python3
"""Unscripted vs prepared speech — the sharpest test of permeation available.

WHY THIS BEATS THE LENGTH PROXY

The length-band test used "short" as a stand-in for "spontaneous". That is a
proxy, and a reviewer can argue with it. Parliamentary procedure gives us the
real thing: business categories where the words CANNOT have been drafted in
advance, because nobody knew what was coming.

  UNSCRIPTED
    Canada  "Oral Questions" -- questions are not submitted in advance at
            all, and a minister answering a supplementary has no text to read
    UK      "Topical Questions" -- substantive topicals are not tabled;
            "Engagements" -- the PMQs slot where only the pro-forma opening
            question is known and every supplementary is a surprise
    Ireland "Leaders' Questions", "Questions on Policy or Legislation",
            "Questions on Promised Legislation" -- raised without notice

  PREPARED (the contrast pole)
    Canada  "Statements by Members" -- 60-second set pieces, read from a
            script, the most drafted text in the chamber
    UK/IE   everything outside the unscripted set

The prediction that separates the hypotheses:

  DRAFTING  the rise concentrates in PREPARED speech, because that is the only
            place a machine draft can physically be used
  PERMEATION the rise appears in UNSCRIPTED speech too -- people talking off
            the cuff in a register they have absorbed

Ministers answering supplementaries are the strongest single case: they are
speaking, unscripted, to a question they did not see. If their vocabulary has
drifted, nothing was drafted.

Caveat kept in view: departments prepare briefing folders, and members
rehearse lines. "Unscripted" means the specific words were not pre-written,
not that the speaker arrived unprepared.

Usage: python unscripted_strata.py   ->  then bash unscripted_run.sh
"""
import json
import os
import re

OUT = "permeation"

# (code, path, name, unscripted matcher, prepared matcher or None = complement)
SPECS = [
    ("ie", "ie/segments_ie_en.jsonl", "Dail Eireann",
     re.compile(r"leaders' questions|questions on policy or legislation|"
                r"questions on promised legislation", re.I), None),
    ("uk", "uk/segments_uk.jsonl", "UK House of Commons",
     re.compile(r"^topical questions$|^engagements$|urgent question", re.I), None),
    ("ca", "ca/segments_ca2.jsonl", "Canada House of Commons",
     re.compile(r"^oral questions$", re.I),
     re.compile(r"^statements by members$", re.I)),
]


def keep(d):
    return (d.get("scoreable") and not d.get("translated")
            and d.get("orig_frac", 1.0) > 0.5
            and (d["date"] <= "2022-12-31" or d["date"] >= "2024-01-01"))


def field(d, code):
    # Canada's rubric lives in `order`; UK/IE carry it in `section`
    return d.get("order", "") if code == "ca" else d.get("section", "")


def main():
    os.makedirs(OUT, exist_ok=True)
    cmds = []
    for code, path, name, unscr, prep in SPECS:
        if not os.path.exists(path):
            print(f"skip {code}: {path} missing")
            continue
        fh = {b: open(f"{OUT}/{code}_{b}.jsonl", "w")
              for b in ("unscripted", "prepared")}
        n = {b: [0, 0, 0, 0] for b in fh}   # [segs, words, pre_segs, post_segs]
        for line in open(path):
            d = json.loads(line)
            if not keep(d):
                continue
            f = field(d, code)
            if unscr.search(f or ""):
                b = "unscripted"
            elif prep is None or prep.search(f or ""):
                b = "prepared"
            else:
                continue
            fh[b].write(line)
            n[b][0] += 1
            n[b][1] += d["n_words"]
            n[b][2 if d["date"] <= "2022-12-31" else 3] += 1
        for f in fh.values():
            f.close()
        for b in ("unscripted", "prepared"):
            s, w, pr, po = n[b]
            print(f"  {code}_{b:<11s} {s:>8,} segs  {w:>12,} words  "
                  f"(pre {pr:,} / post {po:,})")
            if pr > 500 and po > 500:
                cmds.append(f'python3 run_protocol.py "{name} {b}" '
                            f'perm_{code}_{b} {OUT}/{code}_{b}.jsonl')
            else:
                print(f"     too few segments in one window — not run")

    with open("unscripted_run.sh", "w") as f:
        f.write("#!/usr/bin/env bash\nset -e\n" + "\n".join(cmds) + "\n")
    os.chmod("unscripted_run.sh", 0o755)
    print("\nwrote unscripted_run.sh")


if __name__ == "__main__":
    main()
