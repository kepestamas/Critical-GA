#!/usr/bin/env python3
"""
Runner for medium networks (excluding big ones).
NO TIMEOUT - runs until completion.
Shows iteration progress for each run.
Reorders to run cor_n300 and cor_n350 last.
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
WEIGHT_BUDGET = 1.0  # Full budget - no weight constraint
PAYOFF_FUNCTIONS = list_payoff_functions()  # pairwise, components, largest

# Networks to SKIP (too slow)
SKIP_NETWORKS = {
    "cor_jazz-w.txt",
    "cor_celegansneural-w.txt",
    "cor_celegans_metabolic-w.txt",
    "cor_ip_as_network-w.txt",
    "cor_ip_as_network_caida-w.txt",
    "network-cor-forma_eu_27t.txt",
}

# Networks to run LAST (slower than others)
LAST_NETWORKS = {
    "cor_n300plai01.txt",
    "cor_n350plai01.txt",
}


def discover_input_files():
    root = Path("inputs/Testing")
    allowed = {".txt", ".edges", ".mtx"}
    files = [p for p in sorted(root.iterdir()) if p.is_file() and p.suffix.lower() in allowed]
    
    # Filter out skipped networks
    files = [f for f in files if f.name not in SKIP_NETWORKS]
    
    # Split into normal and last
    normal = [f for f in files if f.name not in LAST_NETWORKS]
    last = [f for f in files if f.name in LAST_NETWORKS]
    
    return normal + last


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


def run_greedy(input_path: Path, run_id: str, payoff_function: str):
    cmd = [
        "python",
        "connectivity_greedy.py",
        input_path.name,
        run_id,
        payoff_function,
    ]
    env = os.environ.copy()
    env["GREEDY_WEIGHT_BUDGET"] = str(WEIGHT_BUDGET)
    env["GREEDY_SHOW_PROGRESS"] = "1"  # Enable iteration progress output

    start = time.time()
    # NO TIMEOUT - stream output in real-time
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                           text=True, env=env, bufsize=1)
    
    # Stream output line by line
    for line in proc.stdout:
        # Print progress markers [n/total] on same line
        if line.strip().startswith("[") and "/" in line:
            print(line.rstrip(), end=" ", flush=True)
    
    proc.wait()
    runtime = time.time() - start

    output_file = Path("outputs/reruns/greedy") / f"{run_id}_{input_path.name}"
    minval = extract_minval(output_file)

    return runtime, minval, proc.returncode


def main():
    ensure_dirs()
    inputs = discover_input_files()
    
    if not inputs:
        print("No input files found.")
        return
    
    print(f"Found {len(inputs)} input files (excluding big networks)")
    print(f"Skipping: {', '.join(sorted(SKIP_NETWORKS))}")
    print(f"Running last: {', '.join(sorted(LAST_NETWORKS))}")
    print()

    csv_path = Path("outputs/greedy_final/greedy_results_medium_B1.csv")
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

    # Count total runs
    total_runs = len(inputs) * len(PAYOFF_FUNCTIONS)
    current_run = 0

    with csv_path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for payoff in PAYOFF_FUNCTIONS:
            for idx, input_path in enumerate(inputs, start=1):
                current_run += 1
                run_id = f"greedy_B1_{payoff}_{idx:03d}"
                
                print(f"\n[{current_run}/{total_runs}] {input_path.name} | payoff={payoff}")
                nodes, edges, k_nodes, k_edges = compute_k_values(input_path)
                print(f"  -> {nodes} nodes, {edges} edges, k_nodes={k_nodes}, k_edges={k_edges}")
                print(f"  -> Iterations progress: ", end="", flush=True)

                runtime, minval, returncode = run_greedy(input_path, run_id, payoff)
                status = "OK" if returncode == 0 and minval is not None else "ERROR"
                
                print()  # newline after progress dots
                print(f"  -> status={status}, min_val={minval}, runtime={runtime:.2f}s")

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

    print(f"\n\nFinished. Results saved to {csv_path}")


if __name__ == "__main__":
    main()
