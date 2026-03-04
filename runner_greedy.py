#!/usr/bin/env python3
"""
Runner for the greedy heuristic with final GA parameters.
- k (nodes) = 5% of |V|
- l (edges) = 3% of |E|
- weight budget B = 0.05 of total node weight (via GREEDY_WEIGHT_BUDGET)
Outputs are stored under outputs/reruns/greedy with a greedy-specific run_id
and an aggregate CSV at outputs/greedy_final/greedy_results.csv.
"""

import csv
import os
import subprocess
import time
from pathlib import Path

from graph_io import read_graph
from payoff_functions import list_payoff_functions

NODE_FRACTION = 0.05
EDGE_FRACTION = 0.03
WEIGHT_BUDGET = 0.05
PAYOFF_FUNCTIONS = list_payoff_functions()  # run all available payoff functions
TIMEOUT_SECONDS = None  # No timeout

# Large networks to run last (they take much longer)
LARGE_NETWORKS = {"cor_ip_as_network-w.txt", "cor_ip_as_network_caida-w.txt", "network-cor-forma_eu_27t.txt"}

# Very slow networks - skip these entirely
SKIP_NETWORKS = {"cor_ip_as_network-w.txt", "cor_ip_as_network_caida-w.txt", 
                 "cor_celegans_metabolic-w.txt", "cor_celegansneural-w.txt",
                 "network-cor-forma_eu_27t.txt", "cor_jazz-w.txt"}


def discover_input_files():
    root = Path("inputs/Testing")
    allowed = {".txt", ".edges", ".mtx"}
    files = [p for p in sorted(root.iterdir()) if p.is_file() and p.suffix.lower() in allowed]
    # Sort so large networks come last
    filelist = [f for f in files if f.name in {"cor_dolphins-w.txt"}]
    #normal = [f for f in files if f.name not in LARGE_NETWORKS]
    #large = [f for f in files if f.name in LARGE_NETWORKS]
    #return normal + large
    return filelist

def compute_k_values(path: Path):
    G, _ = read_graph(str(path), detect_weights=True)
    k_nodes = int(len(G.nodes) * NODE_FRACTION)
    k_edges = int(len(G.edges) * EDGE_FRACTION)
    return len(G.nodes), len(G.edges), k_nodes, k_edges


def ensure_dirs():
    Path("outputs/greedy_final").mkdir(parents=True, exist_ok=True)
    Path("outputs/reruns/greedy").mkdir(parents=True, exist_ok=True)


def extract_minval(output_path: Path):
    if not output_path.exists():
        return None
    with output_path.open("r") as handle:
        for line in handle:
            if line.startswith("MinVal achieved"):
                try:
                    return float(line.split(":", 1)[1].strip())
                except ValueError:
                    return None
    return None


def run_greedy(input_path: Path, run_id: str, payoff_function: str, iter_count: int):
    cmd = [
        "python",
        "connectivity_greedy.py",
        input_path.name,
        run_id,
        payoff_function,
    ]
    env = os.environ.copy()
    env["GREEDY_WEIGHT_BUDGET"] = str(WEIGHT_BUDGET)
    env["GREEDY_SHOW_PROGRESS"] = "1"

    # Print run info before starting
    print(f"\n  [{run_id}] {input_path.name} ({iter_count} iters): ", end="", flush=True)

    start = time.time()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        
        # Stream stdout to show progress
        while True:
            char = proc.stdout.read(1)
            if char == '' and proc.poll() is not None:
                break
            if char:
                print(char, end="", flush=True)
        
        proc.wait()
        returncode = proc.returncode
        stdout = ""  # Already printed
        stderr = proc.stderr.read()
        result = subprocess.CompletedProcess(cmd, returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise
    runtime = time.time() - start

    output_file = Path("outputs/reruns/greedy") / f"{run_id}_{input_path.name}"
    minval = extract_minval(output_file)
    
    # Print result on same line
    print(f" -> {minval} ({runtime:.1f}s)", flush=True)

    return runtime, minval, result


def should_skip_network(input_path: Path) -> bool:
    """Return True if this network should be skipped."""
    return input_path.name in SKIP_NETWORKS


def main():
    ensure_dirs()
    inputs = discover_input_files()
    if not inputs:
        print("No input files found in inputs/.")
        return
    
    # Count networks that will actually run (excluding skipped)
    active_inputs = [f for f in inputs if f.name not in SKIP_NETWORKS]
    total_runs = len(PAYOFF_FUNCTIONS) * len(active_inputs)
    
    csv_path = Path("outputs/greedy_final/greedy_results.csv")
    headers = [
        "input_file",
        "run_id",
        "payoff_function",
        "nodes",
        "edges",
        "k_nodes",
        "k_edges",
        "weight_budget",
        "min_val",
        "runtime_seconds",
        "status",
        "output_file",
    ]
    
    # Load already completed runs to skip them
    completed_runs = set()
    if csv_path.exists():
        with csv_path.open("r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                completed_runs.add(row["run_id"])
        print(f"Found {len(completed_runs)} already completed runs, will continue from there.")
    
    remaining_runs = total_runs - len(completed_runs)
    print(f"=" * 70)
    print(f"GREEDY RUNNER - {remaining_runs} runs remaining (of {total_runs} total)")
    print(f"  Payoff functions: {', '.join(PAYOFF_FUNCTIONS)}")
    print(f"  Networks: {len(active_inputs)} (skipping {len(inputs) - len(active_inputs)})")
    print(f"  Parameters: node_frac={NODE_FRACTION}, edge_frac={EDGE_FRACTION}, weight_budget={WEIGHT_BUDGET}")
    print(f"  Iteration count: (k_nodes + k_edges)^2 per network")
    print(f"=" * 70)

    # Open in append mode if file exists, otherwise write mode with header
    mode = "a" if csv_path.exists() else "w"
    with csv_path.open(mode, newline="") as csvfile:
        writer = csv.writer(csvfile)
        if mode == "w":
            writer.writerow(headers)

        run_counter = 0
        skipped_counter = 0
        for payoff in PAYOFF_FUNCTIONS:
            payoff_run_count = 0
            payoff_skipped = 0
            print(f"\n{'='*60}")
            print(f"[{payoff.upper()}] Starting payoff function ({len(active_inputs)} networks)")
            print(f"{'='*60}")
            for idx, input_path in enumerate(inputs, start=1):
                run_id = f"greedy_B005_{payoff}_{idx:03d}"
                
                # Skip very slow networks
                if should_skip_network(input_path):
                    continue
                
                # Skip already completed runs
                if run_id in completed_runs:
                    skipped_counter += 1
                    payoff_skipped += 1
                    continue
                
                run_counter += 1
                payoff_run_count += 1
                nodes, edges, k_nodes, k_edges = compute_k_values(input_path)
                iter_count = (k_nodes + k_edges) ** 2

                try:
                    runtime, minval, result = run_greedy(input_path, run_id, payoff, iter_count)
                    status = "OK" if result.returncode == 0 and minval is not None else "ERROR"
                except subprocess.TimeoutExpired:
                    runtime = TIMEOUT_SECONDS if TIMEOUT_SECONDS else 0
                    minval = None
                    status = "TIMEOUT"

                writer.writerow([
                    input_path.name,
                    run_id,
                    payoff,
                    nodes,
                    edges,
                    k_nodes,
                    k_edges,
                    WEIGHT_BUDGET,
                    minval if minval is not None else "ERROR",
                    f"{runtime:.2f}",
                    status,
                    str(Path("outputs/reruns/greedy") / f"{run_id}_{input_path.name}"),
                ])
                csvfile.flush()
            
            if payoff_skipped > 0:
                print(f"  [{payoff.upper()}] Completed {payoff_run_count} networks (skipped {payoff_skipped} already done)")
            else:
                print(f"  [{payoff.upper()}] Completed {payoff_run_count} networks")

        print(f"\n{'='*60}")
        print(f"Finished! New runs: {run_counter}, Skipped: {skipped_counter}. Results saved to {csv_path}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
