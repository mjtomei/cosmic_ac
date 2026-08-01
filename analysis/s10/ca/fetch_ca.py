import urllib.request, os, time, re, sys
BASE = "https://www.ourcommons.ca/Content/House/{ps}/Debates/{s:03d}/HAN{s:03d}-E.XML"
# parliaments spanning the protocol windows (2018-2022 pre, 2024-2026 post)
PARLS = [("421", 400), ("431", 60), ("432", 200), ("441", 400), ("451", 300)]
ok = skipped = miss = 0
for ps, maxs in PARLS:
    consecutive = 0
    for s in range(1, maxs + 1):
        fn = f"xml/{ps}_{s:03d}.xml"
        if os.path.exists(fn) and os.path.getsize(fn) > 20000:
            ok += 1; consecutive = 0; continue
        url = BASE.format(ps=ps, s=s)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            if len(data) < 20000:
                consecutive += 1; miss += 1
            else:
                open(fn, "wb").write(data); ok += 1; consecutive = 0
        except Exception:
            consecutive += 1; miss += 1
        if consecutive >= 12:
            print(f"{ps}: stop at sitting {s} ({consecutive} consecutive misses)", flush=True)
            break
        time.sleep(0.25)
    print(f"PARL {ps} done: ok={ok} miss={miss}", flush=True)
print(f"CA_DOWNLOAD_DONE ok={ok} miss={miss}", flush=True)
