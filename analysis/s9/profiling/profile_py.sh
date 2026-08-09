#!/usr/bin/env bash
# py-spy wrapper: speedscope profile + top-function table for a Python cmd.
# Usage: ./profile_py.sh <out-name> -- python3 <script> [args...]
set -euo pipefail
cd "$(dirname "$0")"
OUT="$1"; shift; [ "$1" = "--" ] && shift
RUN="runs/$(date +%Y%m%d)_${OUT}"
mkdir -p "$RUN"
PYSPY="${PYSPY:-$HOME/.local/bin/py-spy}"
"$PYSPY" record --format speedscope -o "$RUN/profile.speedscope.json" \
    --rate 200 --subprocesses -- "$@" 2> "$RUN/pyspy.log"
"$PYSPY" record --format flamegraph -o "$RUN/flame.svg" \
    --rate 200 --subprocesses -- "$@" 2>> "$RUN/pyspy.log" || true
python3 - "$RUN/profile.speedscope.json" <<'EOF' | tee "$RUN/top_functions.txt"
import json, sys, collections
d = json.load(open(sys.argv[1]))
frames = d["shared"]["frames"]
tot = collections.Counter()
for prof in d["profiles"]:
    if prof.get("type") == "sampled":
        for stack, w in zip(prof["samples"], prof["weights"]):
            if stack:
                tot[stack[-1]] += w   # leaf frame (self time)
grand = sum(tot.values()) or 1
print(f"{'self%':>7}  function (leaf)")
for idx, w in tot.most_common(25):
    f = frames[idx]
    name = f.get("name", "?"); file = f.get("file", "?")
    print(f"{100*w/grand:6.1f}%  {name}  [{file}]")
EOF
echo "run: $RUN"
