# Launch (12 workers, detached tmux)
./run_tmux.sh

# Or with custom worker count
./run_tmux.sh 8

# Attach to watch progress
tmux attach -t ga_runner

# Detach: Ctrl+B, then D

# Or run directly without tmux
d