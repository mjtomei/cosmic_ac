#!/usr/bin/env bash
# GB10 clock-cap fix (see analysis/s10/PILOT.md, "Environment" #3).
#
# Observed: SM clock pinned at 513 of 3003 MHz in P0 under sustained load,
# ~14 W, no throttle reason -> ~23.6 TFLOPS bf16 instead of an estimated
# ~138. This script locks GPU clocks to max and verifies with a real
# benchmark, because the clock *reading* alone could be cosmetic.
#
# Usage:
#   sudo bash gpu_unlock.sh          # benchmark -> lock clocks -> benchmark
#   sudo bash gpu_unlock.sh reset    # undo the lock (-rgc)
#   bash gpu_unlock.sh bench         # benchmark only (no root needed)
#
# The lock persists until reboot, driver reload, or 'reset'. Pinning
# min=max disables idle downclocking (higher idle power) — fine for a
# wall-powered box during experiments; 'reset' when done.
set -u

VENV_PY="/home/matt/.venvs/s10/bin/python"
CACHE="CUDA_CACHE_MAXSIZE=17179869184 CUDA_CACHE_PATH=/home/matt/.nv/ComputeCache_s121"

query() {
    nvidia-smi --query-gpu=clocks.sm,clocks.max.sm,power.draw,utilization.gpu,pstate \
        --format=csv,noheader
}

bench() {
    # 12-second sustained bf16 matmul; prints TFLOPS and clocks sampled mid-run.
    [ -x "$VENV_PY" ] || { echo "(no $VENV_PY — skipping benchmark)"; return; }
    local runner=(env $CACHE "$VENV_PY")
    # run as the invoking user so we hit their warm JIT cache, not root's
    if [ "$(id -u)" = "0" ] && [ -n "${SUDO_USER:-}" ]; then
        runner=(sudo -u "$SUDO_USER" env $CACHE "$VENV_PY")
    fi
    ( sleep 6; echo "  mid-run: $(query)" ) &
    "${runner[@]}" - <<'PY'
import torch, time
a = torch.randn(8192, 8192, dtype=torch.bfloat16, device="cuda")
b = torch.randn(8192, 8192, dtype=torch.bfloat16, device="cuda")
for _ in range(5): c = a @ b
torch.cuda.synchronize(); t0 = time.perf_counter(); n = 0
while time.perf_counter() - t0 < 12: c = a @ b; n += 1
torch.cuda.synchronize(); dt = time.perf_counter() - t0
print(f"  sustained bf16 matmul: {n * 2 * 8192**3 / dt / 1e12:.1f} TFLOPS")
PY
    wait
}

echo "== state before =="
echo "  $(query)"

case "${1:-lock}" in
bench)
    bench
    ;;
reset)
    nvidia-smi -rgc || { echo "reset failed (needs root?)"; exit 1; }
    echo "== clocks unlocked (returned to driver control) =="
    echo "  $(query)"
    ;;
lock)
    if [ "$(id -u)" != "0" ]; then
        echo "Locking clocks needs root: sudo bash $0"; exit 1
    fi
    MAX=$(nvidia-smi --query-gpu=clocks.max.sm --format=csv,noheader,nounits | head -1 | tr -d ' ')
    echo "== benchmark BEFORE lock =="
    bench
    echo "== locking SM clocks to ${MAX},${MAX} MHz =="
    if ! nvidia-smi -lgc "${MAX},${MAX}"; then
        echo "-lgc refused. Likely a platform/driver limitation on GB10."
        echo "Next steps: check for DGX OS / firmware updates (known early"
        echo "DGX Spark clock-governor issues), or try: sudo nvidia-smi -pm 1"
        exit 1
    fi
    echo "== benchmark AFTER lock =="
    bench
    echo "== state after =="
    echo "  $(query)"
    echo
    echo "If TFLOPS jumped ~5-6x: cap was the clock lock, keep it during"
    echo "experiments and 'sudo bash $0 reset' when done."
    echo "If TFLOPS did NOT move despite higher reported clocks: the cap is"
    echo "below nvidia-smi (firmware/power) — collect 'nvidia-bug-report.sh'"
    echo "and check NVIDIA's DGX Spark forum for the clock-cap thread."
    ;;
*)
    echo "usage: sudo bash $0 [lock|reset|bench]"; exit 1
    ;;
esac
