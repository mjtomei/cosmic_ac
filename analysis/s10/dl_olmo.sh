#!/usr/bin/env bash
set -e
for m in OLMo-2-1124-7B OLMo-2-1124-7B-SFT OLMo-2-1124-7B-DPO OLMo-2-1124-7B-Instruct; do
  echo "== $m"
  ~/.venvs/s10/bin/python - <<PY
from huggingface_hub import snapshot_download
p = snapshot_download("allenai/$m",
                      allow_patterns=["*.safetensors","*.json","*.txt","*.model"],
                      max_workers=8)
print("  ->", p)
PY
done
touch OLMO_DL_DONE
