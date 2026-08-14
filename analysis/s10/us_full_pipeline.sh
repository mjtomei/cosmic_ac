#!/usr/bin/env bash
# Wait for the complete-record download, then rebuild the US corpora and
# re-run both protocol versions. The sampled-corpus results it replaces are
# not comparable to the other chambers (sampling drags the placebo baseline),
# so nothing from the 330-day run should be quoted once this finishes.
set -e
cd /home/matt/performance_commons/analysis/s10/us
until [ -f ../US_FULL_DONE ]; do sleep 60; done
echo "== verifying =="
python3 verify_zips.py --dir zips --fix || true
echo "== extracting complete record =="
~/.venvs/s10/bin/python us_extract.py zips segments_us.jsonl --workers 14
python3 - <<'PY'
import json
out = {"HOUSE": open("segments_us_house.jsonl", "w"),
       "SENATE": open("segments_us_senate.jsonl", "w")}
n = {"HOUSE": 0, "SENATE": 0}
w = {"HOUSE": 0, "SENATE": 0}
for line in open("segments_us.jsonl"):
    d = json.loads(line)
    fh = out.get(d["chamber"])
    if fh:
        fh.write(line); n[d["chamber"]] += 1; w[d["chamber"]] += d["n_words"]
for f in out.values(): f.close()
print("  segments", n, "words", w)
for ch, src in (("house", "segments_us_house.jsonl"),
                ("senate", "segments_us_senate.jsonl")):
    pre, post, rows = set(), set(), []
    for line in open(src):
        d = json.loads(line)
        if not d["scoreable"] or not d["person_id"]: continue
        rows.append((d["person_id"], line))
        (pre if d["date"] <= "2022-12-31" else
         post if d["date"] >= "2024-01-01" else set()).add(d["person_id"])
    both = pre & post
    with open(f"segments_us_{ch}_within.jsonl", "w") as fh:
        k = sum(fh.write(l) > 0 for pid, l in rows if pid in both)
    print(f"   {ch} within-speaker: {len(both)} members, {k} segments")
PY
echo "== protocol v1.0 =="
for a in "US House of Representatives|us_house|segments_us_house.jsonl" \
         "US Senate|us_senate|segments_us_senate.jsonl" \
         "US House of Representatives within-speaker|us_house_within|segments_us_house_within.jsonl" \
         "US Senate within-speaker|us_senate_within|segments_us_senate_within.jsonl"; do
  IFS='|' read -r n p f <<< "$a"
  ~/.venvs/s10/bin/python ../run_protocol.py "$n" "$p" "$f"
done
echo "== protocol v1.1 =="
~/.venvs/s10/bin/python ../run_protocol_v11.py "US House of Representatives" v11_us_house segments_us_house.jsonl
~/.venvs/s10/bin/python ../run_protocol_v11.py "US Senate" v11_us_senate segments_us_senate.jsonl
echo "== formality control =="
~/.venvs/s10/bin/python ../formality_axis.py "US House of Representatives" segments_us_house.jsonl || true
~/.venvs/s10/bin/python ../formality_axis.py "US Senate" segments_us_senate.jsonl || true
touch /home/matt/performance_commons/analysis/s10/US_FULL_PIPELINE_DONE
