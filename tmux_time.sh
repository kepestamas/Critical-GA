#!/usr/bin/env bash
# =============================================================
# Tmux run time script for Critical-GA runner
# =============================================================
#
# Usage:
#   ./tmux_time.sh               # displays running time of pane
#   ./tmux_time.sh status        # shows runner progress estimates
#   ./tmux_time.sh 0             # shows top-level process tree only
#

set -euo pipefail
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_usage() {
    echo "Usage: $0 [max_depth|status|progress]"
}

format_seconds() {
    local total_seconds="$1"
    local hours=$(( total_seconds / 3600 ))
    local minutes=$(( (total_seconds % 3600) / 60 ))
    local seconds=$(( total_seconds % 60 ))
    printf '%02dh:%02dm:%02ds' "$hours" "$minutes" "$seconds"
}

estimate_finish_time() {
    local seconds="$1"
    if [ -z "$seconds" ] || [ "$seconds" = "n/a" ]; then
        echo "n/a"
        return
    fi
    date -d "+${seconds} seconds" '+%Y-%m-%d %H:%M:%S'
}

get_generation_size() {
    local log_file="$1"
    local generation_size=""
    if [ -n "$log_file" ]; then
        generation_size="$(grep -E 'Running with [0-9]+ generations per run' "$log_file" 2>/dev/null | tail -1 | sed -E 's/.*Running with ([0-9]+) generations per run.*/\1/' || true)"
    fi
    if [ -z "$generation_size" ]; then
        generation_size="$(grep -E 'generations\s*=\s*[0-9]+' "$SCRIPT_DIR/runner.py" 2>/dev/null | head -1 | sed -E 's/.*generations\s*=\s*([0-9]+).*/\1/' || true)"
    fi
    printf '%s' "$generation_size"
}

count_completed_runs() {
    local csv_file="$1"
    if [ -f "$csv_file" ]; then
        awk 'NR > 1 {count++} END {print count + 0}' "$csv_file"
    else
        echo 0
    fi
}

show_progress_status() {
    results_csv="$SCRIPT_DIR/outputs/ga_node_weights/running/running_results.csv"
    latest_log="$(ls -1t "$SCRIPT_DIR/outputs/ga_node_weights/running"/runner_*.log 2>/dev/null | head -1 || true)"

    runner_pid="$(ps -eo pid=,args= | awk '!/awk/ && $0 ~ /runner\.py/ && $0 ~ /[[:space:]]-j([[:space:]]|$)/ {print $1; exit}')"
    if [ -n "$runner_pid" ]; then
        elapsed_seconds="$(ps -o etimes= -p "$runner_pid" 2>/dev/null | tr -d ' ' || true)"
    else
        elapsed_seconds=""
    fi

    workers="$(ps -eo pid=,args= | awk '!/awk/ && $0 ~ /runner\.py/ && $0 ~ /[[:space:]]-j([[:space:]]|$)/ {for (i=1;i<=NF;i++) if ($i == "-j") {print $(i+1); exit}}' | head -1 || true)"
    if [ -z "$workers" ] && [ -n "$latest_log" ]; then
        workers="$(grep -E 'Parallel workers:' "$latest_log" 2>/dev/null | tail -1 | sed -E 's/.*Parallel workers: ([0-9]+).*/\1/' || true)"
    fi

    generation_size="$(get_generation_size "$latest_log")"
    if [ -z "$generation_size" ]; then
        generation_size="0"
    fi

    total_runs=""
    if [ -n "$latest_log" ]; then
        total_runs="$(grep -E 'Total runs:' "$latest_log" 2>/dev/null | tail -1 | sed -E 's/.*Total runs: ([0-9]+).*/\1/' || true)"
    fi

    completed_runs="$(count_completed_runs "$results_csv")"

    unfinished_progress_sum=0
    unfinished_progress_count=0
    while IFS= read -r run_log; do
        [ -n "$run_log" ] || continue
        if [ -f "$run_log" ]; then
            line_count="$(wc -l < "$run_log" | tr -d ' ')"
            if [ "$generation_size" -gt 0 ] && [ "$line_count" -lt "$generation_size" ]; then
                unfinished_progress_sum=$(( unfinished_progress_sum + line_count ))
                unfinished_progress_count=$(( unfinished_progress_count + 1 ))
            fi
        fi
    done < <(find "$SCRIPT_DIR/outputs/descending_mutation/ga" -maxdepth 1 -type f -name 'timing*' 2>/dev/null | sort)

    progress_line=""
    if [ -n "$latest_log" ]; then
        progress_line="$(grep -E 'Progress:' "$latest_log" 2>/dev/null | tail -1 || true)"
    fi
    if [ -n "$progress_line" ]; then
        completed_runs_from_log="$(echo "$progress_line" | sed -E 's/.*Progress: ([0-9]+)\/([0-9]+) runs completed.*/\1/' || true)"
        if [ -n "$completed_runs_from_log" ]; then
            completed_runs="$completed_runs_from_log"
        fi
    fi

    if [ -z "$workers" ]; then
        workers="0"
    fi
    if [ -z "$total_runs" ]; then
        total_runs="0"
    fi
    if [ -z "$completed_runs" ]; then
        completed_runs="0"
    fi

    completed_runs=$(( completed_runs ))
    workers=$(( workers ))
    total_runs=$(( total_runs ))

    if [ "$workers" -gt 0 ]; then
        completed_rounds=$(( (completed_runs + workers - 1) / workers ))
        runs_left=$(( total_runs - completed_runs ))
        rounds_left=$(( (runs_left + workers - 1) / workers ))
    else
        completed_rounds=0
        runs_left=$(( total_runs - completed_runs ))
        rounds_left=0
    fi

    echo "Runner status"
    echo "  results csv   : $results_csv"
    if [ -n "$latest_log" ]; then
        echo "  log file      : $latest_log"
    else
        echo "  log file      : unavailable"
    fi
    echo "  workers       : $workers"
    echo "  completed     : $completed_runs/$total_runs runs"
    echo "  completed     : $completed_rounds rounds"
    echo "  remaining     : $runs_left runs / $rounds_left rounds"

    if [ "$unfinished_progress_count" -gt 0 ] && [ "$generation_size" -gt 0 ]; then
        avg_current_round=$(awk -v sum="$unfinished_progress_sum" -v count="$unfinished_progress_count" 'BEGIN { printf "%.0f", sum / count }')
        avg_percent=$(awk -v avg="$avg_current_round" -v total="$generation_size" 'BEGIN { if (total > 0) printf "%.1f", (avg / total) * 100; else print "0.0" }')
        echo "  current round : ${avg_current_round}/${generation_size} (${avg_percent}%) avg over unfinished logs"
    else
        echo "  current round : n/a"
    fi

    if [ -n "$elapsed_seconds" ] && [ "$elapsed_seconds" -gt 0 ]; then
        if [ "$completed_runs" -gt 0 ]; then
            time_per_run=$(awk -v e="$elapsed_seconds" -v c="$completed_runs" 'BEGIN { if (c>0) printf "%.2f", e/c; else print "n/a" }')
        else
            time_per_run="n/a"
        fi

        if [ "$completed_rounds" -gt 0 ]; then
            time_per_round=$(awk -v e="$elapsed_seconds" -v r="$completed_rounds" 'BEGIN { if (r>0) printf "%.2f", e/r; else print "n/a" }')
        else
            time_per_round="n/a"
        fi

        if [ "$runs_left" -gt 0 ] && [ "$time_per_run" != "n/a" ]; then
            time_left_runs=$(awk -v r="$runs_left" -v t="$time_per_run" 'BEGIN { printf "%.0f", r*t }')
        else
            time_left_runs="n/a"
        fi

        if [ "$rounds_left" -gt 0 ] && [ "$time_per_round" != "n/a" ]; then
            time_left_rounds=$(awk -v r="$rounds_left" -v t="$time_per_round" 'BEGIN { printf "%.0f", r*t }')
        else
            time_left_rounds="n/a"
        fi

        echo "  elapsed       : $(format_seconds "$elapsed_seconds")"
        if [ "$time_per_run" != "n/a" ]; then
            echo "  time/run      : ${time_per_run}s"
        else
            echo "  time/run      : n/a"
        fi
        if [ "$time_per_round" != "n/a" ]; then
            echo "  time/round    : ${time_per_round}s"
        else
            echo "  time/round    : n/a"
        fi
        if [ "$time_left_runs" != "n/a" ]; then
            echo "  time left     : $(format_seconds "$time_left_runs") based on runs"
            echo "  finish (runs) : $(estimate_finish_time "$time_left_runs")"
        else
            echo "  time left     : n/a based on runs"
            echo "  finish (runs) : n/a"
        fi
        if [ "$time_left_rounds" != "n/a" ]; then
            echo "  time left     : $(format_seconds "$time_left_rounds") based on rounds"
            echo "  finish (rounds): $(estimate_finish_time "$time_left_rounds")"
        else
            echo "  time left     : n/a based on rounds"
            echo "  finish (rounds): n/a"
        fi
    else
        echo "  elapsed       : unavailable"
        echo "  time/run      : unavailable"
        echo "  time/round    : unavailable"
        echo "  time left     : unavailable"
    fi
}

if [ "$#" -eq 0 ]; then
    max_depth=-1
elif [ "$#" -eq 1 ]; then
    case "$1" in
        status|progress)
            show_progress_status
            exit 0
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            max_depth="$1"
            ;;
    esac
else
    show_usage
    exit 1
fi

shell_pid=$(tmux display-message -p '#{pane_pid}')
fg_pgid=$(ps -o tpgid= -p "$shell_pid" | tr -d ' ')

ps -o pid=,ppid=,etime=,cmd= --forest -g "$fg_pgid" | awk -v root="$fg_pgid" -v max="$max_depth" '{id=$1;p[id]=$2;line[id]=$0;order[++n]=id} function depth(id,x){if(id==root)return 0;x=p[id];return (x in p)?depth(x)+1:0} END{for(i=1;i<=n;i++)if(max<0||depth(order[i])<=max)print line[order[i]]}'

#ps -o pid,etime,cmd --forest -g "$fg_pgid"
