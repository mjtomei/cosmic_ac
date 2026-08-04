#!/usr/bin/env bash
# Regenerate all five figures and the two-column PDF.
# Run from anywhere; operates on the project root (the parent of build/).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
for s in fig1_effort fig2_coordination fig3_demand fig4_phase fig5_trend fig_tapeout fig_embargo fig_insurance; do
  echo "  [fig] $s"; python3 "build/$s.py"
done
echo "  [pdf] render_twocol"
python3 build/render_twocol.py the-performance-commons.md the-performance-commons-2col.pdf
echo "done -> $ROOT/the-performance-commons-2col.pdf"
