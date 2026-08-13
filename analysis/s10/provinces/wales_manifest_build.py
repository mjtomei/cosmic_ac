#!/usr/bin/env python3
"""Build wales_pdf_manifest.json: Senedd/NAfW PLENARY Record-of-Proceedings PDFs
for 2006-01-01..2010-12-31 and 2015-01-01..2015-12-31.

Scrapes only listing pages (ModernGov/CMIS at business.senedd.wales). Does NOT
download the PDFs themselves.

Bodies (CId):
  702 = Plenary - Second Assembly  (..2007-03-28)
  701 = Plenary - Third Assembly   (2007-05-09..2011)
  153 = Plenary - Fourth Assembly  (2011-05-11..2016-04-04)
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HOST = "https://business.senedd.wales/"
UA = "performance-commons-research/1.0 (academic corpus build; matthewtomei@gmail.com)"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = "/tmp/claude-1000/-home-matt-performance-commons/90221613-745b-4ed1-89b6-bc432df3d564/scratchpad/wales_cache"
OUT = os.path.join(HERE, "wales_pdf_manifest.json")
os.makedirs(CACHE, exist_ok=True)

WINDOWS = [("2006-01-01", "2010-12-31"), ("2015-01-01", "2015-12-31")]
LAST_FETCH = [0.0]


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def fetch(url, data=None, key=None):
    """GET/POST with on-disk cache and 1s politeness delay."""
    key = key or re.sub(r"[^A-Za-z0-9._-]", "_", url)[:180]
    path = os.path.join(CACHE, key)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return open(path, encoding="utf-8", errors="replace").read()
    dt = time.time() - LAST_FETCH[0]
    if dt < 1.0:
        time.sleep(1.0 - dt)
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers={"User-Agent": UA})
    if data:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                txt = r.read().decode("utf-8", errors="replace")
            LAST_FETCH[0] = time.time()
            open(path, "w", encoding="utf-8").write(txt)
            return txt
        except Exception as e:  # noqa: BLE001
            log(f"  ! fetch fail ({attempt+1}/4) {url[:110]}: {e}")
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("giving up on " + url)


def in_window(d):
    return any(lo <= d <= hi for lo, hi in WINDOWS)


# --------------------------------------------------------------------------
# STEP 1a: 2015 via the GetMeetings web service (CId 153)
# --------------------------------------------------------------------------
def meetings_2015():
    xml = fetch(
        HOST + "mgwebservice.asmx/GetMeetings",
        data={"lCommitteeId": 153, "sFromDate": "2015-01-01", "sToDate": "2015-12-31"},
        key="ws_getmeetings_153",
    )
    out = {}
    for m in re.finditer(
        r"<meetingid>\s*(\d+)\s*</meetingid>\s*<meetingdate>\s*(\d{2})/(\d{2})/(\d{4})\s*</meetingdate>", xml
    ):
        mid, dd, mm, yyyy = m.groups()
        date = f"{yyyy}-{mm}-{dd}"
        if date.startswith("2015"):
            out[mid] = date
    log(f"[list] CId=153 web service -> {len(out)} meetings in 2015")
    return {(mid, "153"): d for mid, d in out.items()}


# --------------------------------------------------------------------------
# STEP 1b: 2006-2010 via ieListMeetings + Act=later/earlier paging (CId 702/701)
# --------------------------------------------------------------------------
MEET_RE = re.compile(r"CeListDocuments\.aspx\?CommitteeId=(\d+)&amp;MeetingId=(\d+)&amp;DF=(\d{2})%2f(\d{2})%2f(\d{4})", re.I)
PAGE_RE = re.compile(r"ieListMeetings\.aspx\?Act=(later|earlier)&amp;CId=(\d+)&amp;D=(\d{12})&amp;MD=ielistmeetings", re.I)


def _page(cid, url, found):
    """Fetch one listing page; merge its meetings into `found`; return its date span."""
    h = fetch(url)
    title = re.search(r"<title>([^<]*)</title>", h)
    title = title.group(1) if title else ""
    if "Plenary" not in title:
        log(f"  !! non-plenary listing title for {url}: {title!r}")
    dates, n_new = [], 0
    for cid2, mid, dd, mm, yyyy in MEET_RE.findall(h):
        if cid2 != str(cid):
            continue
        k = (mid, str(cid))
        if k not in found:
            n_new += 1
        found[k] = f"{yyyy}-{mm}-{dd}"
        dates.append(found[k])
    log(f"  [list] {url.split('aspx')[1][:58]:58s} rows={len(dates):3d} new={n_new:3d} "
        f"span={min(dates) if dates else '-'}..{max(dates) if dates else '-'} total={len(found)}")
    return (min(dates), max(dates)) if dates else None


def crawl_body(cid, seed_years, lo, hi):
    """Seed on Year pages, then walk the Act=later/earlier chain linearly (no branching).

    Each page's own boundary date is the D value of its next paging link, so the
    chain is deterministic. Walk stops once a page falls entirely outside [lo,hi]
    (one page of overshoot is kept deliberately, to prove the window edge is real).
    """
    found = {}
    spans = []
    for y in seed_years:
        s = _page(cid, f"{HOST}ieListMeetings.aspx?CId={cid}&Year={y}", found)
        if s:
            spans.append((y, s))
    if not spans:
        return found

    def walk(direction, start, stop):
        """Follow Act=<direction> from `start`, stopping once a page clears `stop`."""
        cur = start
        for _ in range(40):  # hard cap; pages are cached so overlap is free
            d = cur.replace("-", "") + "0000"
            url = f"{HOST}ieListMeetings.aspx?Act={direction}&CId={cid}&D={d}&MD=ielistmeetings"
            s = _page(cid, url, found)
            if not s:
                return  # end of this body's history
            if direction == "later":
                if s[0] > stop:
                    return
                cur = s[1]
            else:
                if s[1] < stop:
                    return
                cur = s[0]

    # A Year page caps at 51 rows, so each seed year usually stops around October.
    # Walk forward from EVERY seed year (not just the global max) or Nov/Dec of the
    # middle years is silently lost.
    for y, s in spans:
        walk("later", s[1], min(f"{y}-12-31", hi))
    # ...and back once from the earliest seed, to prove the window's low edge.
    walk("earlier", min(s[0] for _, s in spans), lo)
    return found


# --------------------------------------------------------------------------
# STEP 2: per-meeting document page -> Record PDF
# --------------------------------------------------------------------------
A_RE = re.compile(r"<a\b[^>]*?href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.S | re.I)
MONTHS = {m: i + 1 for i, m in enumerate(
    "January February March April May June July August September October November December".split())}


def title_date(title):
    m = re.search(r"\bon\s+\w+day,?\s+(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})", title)
    if not m:
        return None
    d, mon, y = m.groups()
    if mon not in MONTHS:
        return None
    return f"{y}-{MONTHS[mon]:02d}-{int(d):02d}"


def pdf_name(href):
    """Human filename implied by an href."""
    if "ceconvert2pdf" in href.lower():
        q = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        return urllib.parse.unquote(q.get("F", [""])[0])
    return urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(href).path))


def absolutise(href):
    p = urllib.parse.urlsplit(href)
    path = urllib.parse.quote(p.path, safe="/%")
    return urllib.parse.urljoin(HOST, urllib.parse.urlunsplit(("", "", path, p.query, "")))


# tier 0 = canonical CMIS "Record of Proceedings"; tier 1 = "The Record";
# tier 2 = Welsh-only "Cofnod".
def classify(name, text):
    s = (name + " || " + text).lower()
    if "voting record" in s or "cofnod pleidleisio" in s:
        return None
    if "answers to questions" in s or "atebion i gwestiynau" in s:
        return None
    if "votes" in s or "agenda" in s or "decisions" in s or "penderfyniad" in s:
        return None
    if re.search(r"record of proceedings", s):
        return 0
    if re.search(r"\bthe record\b|\brecord\s*\(", s):
        return 1
    if re.search(r"cofnod y trafodion|\by cofnod\b|^cofnod\b|\bcofnod\s*\(", s):
        return 2
    return None


PART_RE = re.compile(r"\bpart\s*(\d+)|\brhan\s*(\d+)|\bpm\b|\bam\b", re.I)


def records_for(mid, cid, expect_date):
    url = f"{HOST}ieListDocuments.aspx?CId={cid}&MId={mid}"
    h = fetch(url, key=f"doc_{cid}_{mid}")
    title = re.search(r"<title>([^<]*)</title>", h)
    title = html.unescape(title.group(1)) if title else ""
    tiers = {}
    for href, inner in A_RE.findall(h):
        href = html.unescape(href).strip()
        text = html.unescape(re.sub(r"<[^>]+>", " ", inner))
        text = re.sub(r"\s+", " ", text).strip()
        low = href.lower()
        if not (".pdf" in low):
            continue
        # only same-host CMIS documents; skip absolute off-host links & nav
        if low.startswith("http") and not low.startswith(HOST):
            continue
        if not (low.startswith("documents/") or "ceconvert2pdf" in low):
            continue
        name = pdf_name(href)
        t = classify(name, text)
        if t is None:
            continue
        tiers.setdefault(t, {})[absolutise(href)] = name
    return title, tiers


def main():
    # ---- meeting lists
    meetings = {}
    log("== STEP 1: meeting lists ==")
    log("[list] CId=702 (Second Assembly), seed years 2006-2007")
    meetings.update(crawl_body(702, [2006, 2007], "2006-01-01", "2007-12-31"))
    log("[list] CId=701 (Third Assembly), seed years 2007-2010")
    meetings.update(crawl_body(701, [2007, 2008, 2009, 2010], "2007-01-01", "2010-12-31"))
    meetings.update(meetings_2015())

    meetings = {k: v for k, v in meetings.items() if in_window(v)}
    log(f"[list] {len(meetings)} meetings inside target windows")

    # coverage assertion: every month of every target year present
    bymonth = {}
    for (_mid, _cid), d in meetings.items():
        bymonth.setdefault(d[:4], set()).add(d[:7])
    # Aug is summer recess and Apr/May 2007 is the dissolution/election gap: expected.
    EXPECTED_GAPS = {"2006-08", "2007-08", "2008-08", "2009-08", "2010-08", "2015-08",
                     "2007-04"}
    for y in ["2006", "2007", "2008", "2009", "2010", "2015"]:
        got = sorted(bymonth.get(y, []))
        missing = [f"{y}-{m:02d}" for m in range(1, 13) if f"{y}-{m:02d}" not in got]
        unexpected = [m for m in missing if m not in EXPECTED_GAPS]
        flag = "  <<< UNEXPECTED GAP" if unexpected else ""
        log(f"[cover] {y}: {len(got)}/12 months; missing={missing}{flag}")

    # ---- per-meeting scrape
    log("== STEP 2: document pages ==")
    rows, problems, notes = [], [], []
    items = sorted(meetings.items(), key=lambda kv: (kv[1], kv[0]))
    for i, ((mid, cid), date) in enumerate(items, 1):
        title, tiers = records_for(mid, cid, date)
        tdate = title_date(title)
        if "Plenary" not in title:
            problems.append((date, mid, cid, f"TITLE NOT PLENARY: {title!r}"))
        if tdate and tdate != date:
            problems.append((date, mid, cid, f"DATE MISMATCH title={tdate}"))
        if not tiers:
            problems.append((date, mid, cid, "NO RECORD PDF"))
            log(f"[{i}/{len(items)}] {date} m={mid} c={cid} -> NONE  ({title[:60]})")
            continue
        tier = min(tiers)
        picked = sorted(tiers[tier].items(), key=lambda kv: kv[1])
        if tier == 2:
            notes.append((date, mid, "welsh-titled only"))
        if len(picked) > 1:
            notes.append((date, mid, f"{len(picked)} record pdfs: " + " | ".join(n for _, n in picked)))
        for j, (u, name) in enumerate(picked):
            sfx = "" if j == 0 else "_" + chr(ord("b") + j - 1)
            row = {"url": u, "date": date, "meeting": mid, "body": cid,
                   "file": f"pdf_{date}_{mid}{sfx}.pdf"}
            if tier == 2:
                row["welsh_titled"] = True
            rows.append(row)
        log(f"[{i}/{len(items)}] {date} m={mid} c={cid} tier={tier} n={len(picked)}")

    rows.sort(key=lambda r: (r["date"], r["meeting"], r["file"]))
    json.dump(rows, open(OUT, "w"), indent=1)
    log(f"\n== wrote {OUT}: {len(rows)} rows ==")
    json.dump({"problems": problems, "notes": notes},
              open(os.path.join(CACHE, "issues.json"), "w"), indent=1)
    for p in problems:
        log("PROBLEM", p)
    for n in notes:
        log("NOTE", n)


if __name__ == "__main__":
    main()
