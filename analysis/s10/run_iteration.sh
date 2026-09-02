#!/bin/bash
# run_iteration.sh <phase> <iteration> [tmux-session]
#
# ONE workflow covering every scope, in a VISIBLE tmux window (Matthew,
# 2026-09-02). Not one headless session per scope: a single interactive
# claude-mixed session runs round2_iter_all.js, so progress is watchable in the
# pane and /workflows works against it.
set -euo pipefail
PHASE="${1:?phase}"; ITER="${2:?iteration}"; SESSION="${3:-performance-commons}"
REPO=/home/matt/performance_commons
WIN="s10-iter${ITER}"
OUT="$REPO/analysis/s10/REWRITES-round2/iter${ITER}-phase${PHASE}.json"

ARGS=$(cd "$REPO" && python3 -c "
import json
groups=json.load(open('analysis/s10/section_groups.json'))
scopes=[{'id':'full','scope':'all'}]+[{'id':g['id'],'scope':g['scope']} for g in groups]
print(json.dumps({'phase':'$PHASE','iteration':int('$ITER'),'scopes':scopes}))")

PROMPT="Call the Workflow tool with scriptPath \"analysis/s10/workflows/round2_iter_all.js\" and args $ARGS. It runs one workflow across every scope and takes a while; wait for it. When it finishes, use the Write tool to save its complete JSON result verbatim to \"$OUT\", then print the runId, the transcriptDir, and the totals line. Do not analyze, summarize, or apply anything."

tmux kill-window -t "$SESSION:$WIN" 2>/dev/null || true
tmux new-window -d -t "$SESSION" -n "$WIN" -c "$REPO"
tmux send-keys -t "$SESSION:$WIN" 'export PATH="$HOME/.local/bin:$PATH"; claude-mixed --dangerously-skip-permissions' C-m
echo "waiting for the session to come up in $SESSION:$WIN ..."
for _ in $(seq 1 60); do
  if tmux capture-pane -pt "$SESSION:$WIN" 2>/dev/null | grep -qiE 'shortcuts|bypass|welcome|>'; then break; fi
  sleep 2
done
tmux send-keys -t "$SESSION:$WIN" "$PROMPT"
sleep 2
tmux send-keys -t "$SESSION:$WIN" C-m
echo "iteration $ITER (phase $PHASE) started in tmux $SESSION:$WIN"
echo "  watch:   tmux attach -t $SESSION \; select-window -t $WIN"
echo "  result:  $OUT"
