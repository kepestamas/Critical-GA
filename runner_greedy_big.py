#!/usr/bin/env python3
"""
Runner for big/slow networks that timed out or were skipped.
NO TIMEOUT - runs until completion.
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
PAYOFF_FUNCTIONS = ["largest"]  # Only largest remaining

# Networks to run (only jazz and celegans - skip ip_as and eu_27t, too slow)
BIG_NETWORKS = [
    "cor_jazz-w.txt",              # timed out
    "cor_celegansneural-w.txt",    # skipped
    "cor_celegans_metabolic-w.txt",# skipped  
]


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

    start = time.time()
    # NO TIMEOUT
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    runtime = time.time() - start

    output_file = Path("outputs/reruns/greedy") / f"{run_id}_{input_path.name}"
    minval = extract_minval(output_file)

    return runtime, minval, result


def main():
    ensure_dirs()
    
    csv_path = Path("outputs/greedy_final/greedy_results_big.csv")
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

    # Use append mode to not overwrite existing results
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(headers)

        for payoff in PAYOFF_FUNCTIONS:
            for idx, network_name in enumerate(BIG_NETWORKS, start=1):
                input_path = Path("inputs/Testing") / network_name
                if not input_path.exists():
                    print(f"WARNING: {input_path} not found, skipping")
                    continue
                    
                run_id = f"greedy_B005_BIG_{payoff}_{idx:03d}"
                
                print(f"Running greedy on {network_name} with payoff={payoff} (NO TIMEOUT)")
                nodes, edges, k_nodes, k_edges = compute_k_values(input_path)
                print(f"  -> {nodes} nodes, {edges} edges, k_nodes={k_nodes}, k_edges={k_edges}")

                runtime, minval, result = run_greedy(input_path, run_id, payoff)
                status = "OK" if result.returncode == 0 and minval is not None else "ERROR"

                writer.writerow([
                    network_name,
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
                    str(Path("outputs/reruns/greedy") / f"{run_id}_{network_name}"),
                ])
                csvfile.flush()
                print(f"  -> status={status}, min_val={minval}, runtime={runtime:.2f}s")

    print(f"\nFinished. Results saved to {csv_path}")


if __name__ == "__main__":
    main()
