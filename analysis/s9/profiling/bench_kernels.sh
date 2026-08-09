#!/usr/bin/env bash
# Tier-1 kernel timing anchors on real repo data (coarse, backend-free).
# Concatenates the s10 JSON pool to a ~90MB working input, then times the
# datacenter-tax kernels on it. Output: runs/<date>_kernels/anchors.txt
set -euo pipefail
cd "$(dirname "$0")"
RUN="runs/$(date +%Y%m%d)_kernels"
mkdir -p "$RUN"
IN="$RUN/input.json"
if [ ! -f "$IN" ]; then
    for i in $(seq 20); do cat ../../s10/band_screen_pool.json; done > "$IN"
fi
SIZE=$(stat -c%s "$IN")
{
echo "input: ${SIZE} bytes (20x s10/band_screen_pool.json), $(date -Iseconds)"
echo "host: $(uname -m), $(nproc) cores"
for CMD in \
    "gzip -6 -c" \
    "gzip -9 -c" \
    "zstd -3 -c -T1" \
    "zstd -19 -c -T1" \
    "xz -6 -c -T1" \
    "sha256sum" \
    "openssl dgst -sha256" \
    "jq -cn 'inputs | length'" \
    ; do
    /usr/bin/time -f "%e s  %M KB-maxrss   $CMD" \
        bash -c "$CMD < '$IN' > /dev/null" 2>&1
done
echo "--- python json parse ---"
/usr/bin/time -f "%e s  %M KB-maxrss   python3 json.load x20" \
    python3 -c "
import json
for _ in range(20):
    with open('../../s10/band_screen_pool.json') as f: d=json.load(f)
" 2>&1
} | tee "$RUN/anchors.txt"
