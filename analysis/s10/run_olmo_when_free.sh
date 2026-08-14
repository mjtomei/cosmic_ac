#!/usr/bin/env bash
# Queue the OLMo ladder behind the running Qwen3/Mistral alignment scoring so
# the two jobs never contend for the GPU.
set -e
cd /home/matt/performance_commons/analysis/s10
# both fetches: the SFT/DPO repos ship .bin shards, not safetensors,
# so they needed a second pass with a widened allow_patterns
until [ -f OLMO_DL_DONE ] && [ -f OLMO_DL2_DONE ]; do sleep 60; done
echo "downloads complete"
while pgrep -f "[a]lign_ratio.py" >/dev/null; do sleep 60; done
echo "GPU free; starting ladder"
~/.venvs/s10/bin/python olmo_ladder.py generate --prompts 800 --new-tokens 150 --batch 48
~/.venvs/s10/bin/python olmo_ladder.py score --batch 16
touch OLMO_LADDER_DONE
echo "ladder complete"
