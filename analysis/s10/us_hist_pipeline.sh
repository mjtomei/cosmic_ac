#!/usr/bin/env bash
# When the 2006-2017 download lands: re-extract the whole zip dir (now
# 2006-2026), re-split chambers, then run the state-gradient regression.
set -e
cd /home/matt/performance_commons/analysis/s10
until [ -f US_HIST_DONE ]; do sleep 120; done
echo "== historical download complete; verifying =="
cd us && python3 verify_zips.py --dir zips || true
echo "== extracting 2006-2026 =="
~/.venvs/s10/bin/python us_extract.py zips segments_us.jsonl --workers 14
python3 - <<'PY'
import json
out={"HOUSE":open("segments_us_house.jsonl","w"),"SENATE":open("segments_us_senate.jsonl","w")}
n={"HOUSE":0,"SENATE":0}
for line in open("segments_us.jsonl"):
    d=json.loads(line)
    f=out.get(d["chamber"])
    if f: f.write(line); n[d["chamber"]]+=1
for f in out.values(): f.close()
print("  segments:",n)
PY
cd .. && python3 state_gradient.py > state_gradient.log 2>&1
echo "== state gradient done =="
tail -20 state_gradient.log
touch STATE_GRADIENT_DONE
