#!/usr/bin/env python3
"""S10 bios: Manitoba Legislative Assembly MLA biographies (living + deceased).
Unlike Wikipedia these carry an explicit DOB and every general-election date,
so they close most of Manitoba's birth_year and year_first_elected gap."""
import json, re, os, urllib.request, html

UA = "PerformanceCommons-Research/1.0 (matthewtomei@gmail.com) legislator-bio-collection"
HERE = os.path.dirname(os.path.abspath(__file__))
URLS = ["https://www.gov.mb.ca/legislature/members/mla_bio_living.html",
        "https://www.gov.mb.ca/legislature/members/mla_bio_deceased.html"]


def fetch(u):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")


def to_text(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", "\n", h)
    return html.unescape(h)


NAME = re.compile(r"^([A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ'\-\. ]{1,40}),\s*(.+)$")


def main():
    recs = []
    for u in URLS:
        txt = to_text(fetch(u))
        lines = [l.strip() for l in txt.split("\n")]
        lines = [l for l in lines if l]
        cur = None
        for i, l in enumerate(lines):
            m = NAME.match(l)
            if m and len(m.group(1)) > 2 and not m.group(1).isupper() is False:
                # a surname line: "ASHTON, Steve"
                if cur:
                    recs.append(cur)
                cur = {"surname": m.group(1).strip().title(),
                       "given": m.group(2).strip(), "dob": None, "first_elected": None,
                       "party": None, "riding": None,
                       "source_url": u}
                continue
            if not cur:
                continue
            if l.startswith("DOB:"):
                y = re.search(r"\b(18\d\d|19\d\d|200\d)\b", l)
                if y:
                    cur["dob"] = int(y.group(1))
            elif l.startswith("Elected") and not cur["first_elected"]:
                y = re.search(r"\b(18\d\d|19\d\d|20[0-2]\d)\b", l)
                if y:
                    cur["first_elected"] = int(y.group(1))
            elif re.match(r"^\(.*\)\s*\(.*\)$", l) and not cur["riding"]:
                mm = re.match(r"^\((.*?)\)\s*\((.*?)\)$", l)
                cur["riding"], cur["party"] = mm.group(1), mm.group(2)
        if cur:
            recs.append(cur)
    recs = [r for r in recs if r["dob"] or r["first_elected"]]
    print("MB legislature bios parsed:", len(recs),
          "with DOB:", sum(1 for r in recs if r["dob"]),
          "with first-elected:", sum(1 for r in recs if r["first_elected"]))
    json.dump(recs, open(os.path.join(HERE, "mb_legislature_bios.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
