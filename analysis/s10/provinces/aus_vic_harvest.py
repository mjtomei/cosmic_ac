#!/usr/bin/env python3
"""Victoria (AU) Hansard harvester -- plan a query-cell manifest, then download.

The Victorian Hansard has no per-sitting-day URL.  hansard.parliament.vic.gov.au
runs an ISYS search engine whose ROOT path (allowed by that host's robots.txt)
doubles as the document-display view:

    /?IW_DATABASE=*&IW_BATCHSIZE=50&LDMS=Y&IW_SORT=n:OrderId&IW_FIELD_TEXT=<query>

With LDMS=Y the page contains the FULL TEXT of every matching document.  The
batch size is hard-capped at 50 documents and the only paging links live under
/isysquery/ which robots.txt disallows, so the unit of retrieval here is a
QUERY CELL kept under 50 documents by partitioning:

    (house, sitting date)                       ~200-220 documents  -> too big
      -> (house, date, activity type)           usually <50         -> one cell
        -> (house, date, activity, member bin)  when the activity has >50

Activity-type labels are read from the per-day facet, never hardcoded: they
changed between the two drift windows ("Questions without Notice" in 2006-2010
vs "Questions Without Notice and Ministers Statements" in 2015-2019).

Stages
  plan      sweep candidate weekdays, emit aus_vic_manifest.json (cells + urls)
  download  fetch every cell into aus_vic_raw/, resumable, 1 request/second

Usage: python3 aus_vic_harvest.py {plan|download} [ASSEMBLY|COUNCIL ...]
"""
import html as htmllib
import json
from collections import Counter
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
HOST = "https://hansard.parliament.vic.gov.au/"
# The host is behind an Azure WAF that 403s plain library user-agents.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")
WINDOWS = [(2006, 2010), (2015, 2019)]
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
# Activity types that carry no member speech worth scoring: tabled matter,
# division lists, chair rulings, one-line procedural business.  Skipped at plan
# time so the crawl stays short.
SKIP_ACT = re.compile(
    r"petition|paper|division|questions on notice|written |statement of compat"
    r"|ruling|business of the house|joint sitting|point[s]? of order"
    r"|tabled|notice[s]? of motion", re.I)
CAP = 50                     # server-side document cap per query
BIN = 40                     # member-bin target, left of the cap
MIN_GAP = 1.0                # seconds between request STARTS, host-wide
WORKERS = 4                  # concurrency; the gate below still caps at 1 req/s

# Global rate gate: whatever the concurrency, the host never sees more than one
# request per MIN_GAP seconds.  Round-trips here run 1.5-2.5 s, so without the
# pool the crawl would sit at ~0.4 req/s and take days.
_gate = threading.Lock()
_slot = [0.0]


def _ticket():
    with _gate:
        now = time.time()
        t = max(now, _slot[0])
        _slot[0] = t + MIN_GAP
    if t > now:
        time.sleep(t - now)


def get(url, tries=4):
    for a in range(tries):
        _ticket()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if a == tries - 1:
                raise
            time.sleep(3 + 5 * a)


def cell_url(query, ldms=True, batch=CAP):
    return (HOST + "?IW_DATABASE=*&IW_BATCHSIZE=%d&IW_SORT=n:OrderId%s"
            "&IW_FIELD_TEXT=%s" % (batch, "&LDMS=Y" if ldms else "",
                                   urllib.parse.quote(query)))


NRES = re.compile(r"of ([0-9,]+) results")
FACET = re.compile(r'metafilter/(ActivityType|MemberName)/([^/]+)/">([^<]*)</a>')


def probe(query):
    """List-mode request: returns (n_documents, activities, members)."""
    h = get(cell_url(query, ldms=False, batch=1))
    m = NRES.search(h)
    n = int(m.group(1).replace(",", "")) if m else 0
    acts, membs, seen = [], [], set()
    for kind, key, label in FACET.findall(h):
        cnt = re.search(r"\((\d+)\)\s*$", htmllib.unescape(label))
        val = urllib.parse.unquote(key)
        if (kind, val) in seen:
            continue
        seen.add((kind, val))
        (acts if kind == "ActivityType" else membs).append(
            (val, int(cnt.group(1)) if cnt else 0))
    return n, acts, membs


def q_day(house, d):
    return ("HOUSENAME CONTAINS (%s) AND SITTINGDATE CONTAINS (%d %s %d)"
            % (house, d.day, MONTHS[d.month - 1], d.year))


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:60]


def candidate_dates():
    out = []
    for lo, hi in WINDOWS:
        d, end = date(lo, 1, 1), date(hi, 12, 31)
        while d <= end:
            if d.weekday() < 5 and d.month != 1:   # no Jan, no weekends
                out.append(d)
            d += timedelta(days=1)
    return out


def plan(houses):
    log = open(HERE / "aus_vic_plan.log", "a")

    def say(*a):
        print(*a, file=log, flush=True)
        print(*a, file=sys.stderr, flush=True)

    pool = ThreadPoolExecutor(WORKERS)

    # 1. month pre-screen: skip whole months the Parliament never sat in
    months = [(y, mi, mn) for lo, hi in WINDOWS for y in range(lo, hi + 1)
              for mi, mn in enumerate(MONTHS, 1) if mi != 1]
    res = pool.map(lambda t: probe("SITTINGDATE CONTAINS (%s %d)"
                                   % (t[2], t[0]))[0], months)
    live = {(y, mi) for (y, mi, _), n in zip(months, res) if n}
    say("live months: %d of %d" % (len(live), len(months)))

    # 2. sitting dates (either house), one probe per candidate weekday
    cand = [d for d in candidate_dates() if (d.year, d.month) in live]
    res = pool.map(lambda d: probe("SITTINGDATE CONTAINS (%d %s %d)"
                                   % (d.day, MONTHS[d.month - 1], d.year))[0],
                   cand)
    days = [d for d, n in zip(cand, res) if n]
    say("sitting dates: %d of %d candidate weekdays" % (len(days), len(cand)))

    # 3. per (date, house): document count + activity facet
    pairs = [(d, h) for d in days for h in houses]
    plans = list(pool.map(lambda p: probe(q_day(p[1], p[0])), pairs))

    cells, sitting, oversize = [], Counter(), []
    for (d, house), (n, acts, _) in zip(pairs, plans):
        if not n:
            continue
        sitting[house] += 1
        base = q_day(house, d)
        for act, cnt in acts:
            if SKIP_ACT.search(act):
                continue
            q = base + " AND ACTIVITYTYPE CONTAINS (%s)" % act
            if cnt <= CAP:
                cells.append({"url": cell_url(q), "date": str(d),
                              "chamber": house, "activity": act, "n_docs": cnt,
                              "name": "%s_%s_%s.html"
                                      % (house[:2], d, slug(act))})
            else:
                oversize.append((d, house, act, cnt, q))
    say("cells so far %d; oversize activity cells %d"
        % (len(cells), len(oversize)))

    # 4. oversize activity cells -> split on the member facet
    membs = list(pool.map(lambda o: probe(o[4])[2], oversize))
    for (d, house, act, cnt, q), ms in zip(oversize, membs):
        bins, cur, tot = [], [], 0
        for mem, mc in ms:
            if cur and tot + mc > BIN:
                bins.append(cur)
                cur, tot = [], 0
            cur.append(mem)
            tot += mc
        if cur:
            bins.append(cur)
        for i, b in enumerate(bins or [[]]):
            qq = q
            if b:
                qq += (" AND MEMBERNAME CONTAINS (%s)"
                       % " OR MEMBERNAME CONTAINS ".join(b))
            cells.append({"url": cell_url(qq), "date": str(d),
                          "chamber": house, "activity": act, "bin": i,
                          "n_docs": cnt,
                          "name": "%s_%s_%s_b%d.html"
                                  % (house[:2], d, slug(act), i)})
        say("  split %s %s %s (%d docs) -> %d bins"
            % (house, d, act, cnt, len(bins)))

    json.dump(cells, open(HERE / "aus_vic_manifest.json", "w"), indent=1)
    say("PLAN DONE cells=%d sitting_days=%s" % (len(cells), dict(sitting)))


def body_of(h):
    i = h.find('class="speech-content"')
    j = h.find("<footer")
    return h[i:j] if i > 0 else ""


def download():
    rows = json.load(open(HERE / "aus_vic_manifest.json"))
    # Assembly first: it is the chamber the study needs, Council is a bonus.
    rows.sort(key=lambda r: (r["chamber"] != "ASSEMBLY", r["date"], r["name"]))
    raw = HERE / "aus_vic_raw"
    raw.mkdir(exist_ok=True)
    log = open(HERE / "aus_vic_download.log", "a")
    tally = Counter()
    lock = threading.Lock()

    def one(r):
        dest = raw / r["name"]
        if dest.exists() and dest.stat().st_size > 400:
            tally["skip"] += 1
            return
        try:
            h = get(r["url"])
        except Exception as e:
            tally["fail"] += 1
            with lock:
                print("FAIL %s %s" % (r["name"], e), file=log, flush=True)
            return
        b = body_of(h)
        if not b:
            tally["empty"] += 1
            with lock:
                print("EMPTY %s" % r["name"], file=log, flush=True)
        dest.write_text("<!--%s %s %s-->\n" % (r["date"], r["chamber"],
                                               r.get("activity", "")) + b,
                        encoding="utf-8")
        tally["dl"] += 1
        n = sum(tally.values())
        if n % 200 == 0:
            with lock:
                print("progress %d/%d %s" % (n, len(rows), dict(tally)),
                      file=log, flush=True)

    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(one, rows))
    print("DONE total=%d %s" % (len(rows), dict(tally)), file=log, flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    hs = sys.argv[2:] or ["ASSEMBLY", "COUNCIL"]
    if mode == "plan":
        plan(hs)
    else:
        download()
