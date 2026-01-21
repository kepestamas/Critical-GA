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
TIMEOUT_SECONDS = 600  # 10 minutes per run; set to None to disable timeout

# Large networks to run last (they take much longer)
LARGE_NETWORKS = {"cor_ip_as_network-w.txt", "cor_ip_as_network_caida-w.txt", "network-cor-forma_eu_27t.txt"}

# Very slow networks - only run when timeout is disabled (None)
SKIP_UNLESS_NO_TIMEOUT = {"cor_ip_as_network-w.txt", "cor_ip_as_network_caida-w.txt", 
                          "cor_celegans_metabolic-w.txt", "cor_celegansneural-w.txt",
                          "network-cor-forma_eu_27t.txt"}


def discover_input_files():
    root = Path("inputs/Testing")
    allowed = {".txt", ".edges", ".mtx"}
    files = [p for p in sorted(root.iterdir()) if p.is_file() and p.suffix.lower() in allowed]
    # Sort so large networks come last
    normal = [f for f in files if f.name not in LARGE_NETWORKS]
    large = [f for f in files if f.name in LARGE_NETWORKS]
    return normal + large


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
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        try:
            timeout = TIMEOUT_SECONDS if TIMEOUT_SECONDS is not None else None
            stdout, stderr = proc.communicate(timeout=timeout)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise
        result = subprocess.CompletedProcess(cmd, returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        raise
    runtime = time.time() - start

    output_file = Path("outputs/reruns/greedy") / f"{run_id}_{input_path.name}"
    minval = extract_minval(output_file)

    return runtime, minval, result


def should_skip_network(input_path: Path) -> bool:
    """Return True if this network should be skipped (unless timeout is disabled)."""
    if TIMEOUT_SECONDS is None:
        return False  # No timeout = run everything
    return input_path.name in SKIP_UNLESS_NO_TIMEOUT


def main():
    ensure_dirs()
    inputs = discover_input_files()
    if not inputs:
        print("No input files found in inputs/.")
        return

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

    with csv_path.open("w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for payoff in PAYOFF_FUNCTIONS:
            for idx, input_path in enumerate(inputs, start=1):
                run_id = f"greedy_B005_{payoff}_{idx:03d}"
                
                # Skip very slow networks unless timeout is disabled
                if should_skip_network(input_path):
                    print(f"SKIPPING {input_path.name} with payoff={payoff} (too slow, set TIMEOUT_SECONDS=None to run)")
                    continue
                
                print(f"Running greedy on {input_path.name} with payoff={payoff} (run_id={run_id})")
                nodes, edges, k_nodes, k_edges = compute_k_values(input_path)

                try:
                    runtime, minval, result = run_greedy(input_path, run_id, payoff)
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
                print(f"  -> status={status}, min_val={minval}, runtime={runtime:.2f}s")

    print(f"Finished. Results saved to {csv_path}")


if __name__ == "__main__":
    main()
