#!/usr/bin/env bash
# =============================================================
# Tmux launcher for Critical-GA runner
# =============================================================
# Starts runner.py inside a detachable tmux session.
#
# Usage:
#   ./run_tmux.sh              # uses cpu_count/2 workers
#   ./run_tmux.sh 8            # override: 8 parallel workers
#
# Tmux cheat-sheet:
#   Detach:            Ctrl+B, then D
#   Reattach:          tmux attach -t ga_runner
#   List sessions:     tmux ls
#   Kill session:      tmux kill-session -t ga_runner
# =============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_NAME="ga_runner"

# Parallel workers: argument > default (cpu_count / 2)
CPU_COUNT=$(python3 -c "import multiprocessing; print(multiprocessing.cpu_count())")
DEFAULT_WORKERS=$(( CPU_COUNT / 2 ))
WORKERS="${1:-$DEFAULT_WORKERS}"

echo "=== Critical-GA tmux launcher ==="
echo "  CPUs available : $CPU_COUNT"
echo "  Workers        : $WORKERS"
echo "  Session name   : $SESSION_NAME"
echo ""

# Kill existing session with the same name (if any)
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Start a new detached tmux session running the script
tmux new-session -d -s "$SESSION_NAME" -c "$SCRIPT_DIR" \
    "python -u runner.py -j ${WORKERS} 2>&1 | tee outputs/ga_node_weights/running/runner_\$(date +%Y%m%d_%H%M%S).log; echo ''; echo 'Run finished. Press Enter to close.'; read"

echo "Started tmux session '$SESSION_NAME'."
echo ""
echo "  Attach:   tmux attach -t $SESSION_NAME"
echo "  Detach:   Ctrl+B, then D"
echo "  Kill:     tmux kill-session -t $SESSION_NAME"
echo "  Status:   ./tmux_time.sh status"
