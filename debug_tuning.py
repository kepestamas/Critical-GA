#!/usr/bin/env python3
"""
Debug version of parameter tuning script to isolate the issue
"""

import subprocess
import time
import os

def main():
    # Test with just one combination
    input_file = "Tuning/bog_150_p0.1_2.txt"
    run_id = "debug_run"
    
    cmd = [
        "python", "connectivity_ga.py",
        input_file,                    # input file
        run_id,                        # run_id
        "0.05",                        # node_fraction (0.05)
        "0.03",                        # edge_fraction (0.03) 
        "0.15",                        # weight_budget
        "50",                          # population_size
        "3",                           # tournament_size
        "0.8",                         # p_crossover
        "0.01",                        # p_mutation
        "pairwise",                    # payoff_function
        "10"                           # generation_count (reduced for testing)
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Record start time
    start_time = time.time()
    
    # Run the GA
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # Calculate runtime
        runtime = time.time() - start_time
        
        print(f"Return code: {result.returncode}")
        print(f"Runtime: {runtime:.2f}s")
        print(f"Stdout length: {len(result.stdout)}")
        print(f"Stderr length: {len(result.stderr)}")
        
        if result.returncode != 0:
            print(f"ERROR: GA failed with return code {result.returncode}")
            print(f"stderr: {result.stderr}")
            if result.stdout:
                print(f"stdout (first 200 chars): {result.stdout[:200]}")
        else:
            print("GA completed successfully!")
            
            # Try to extract fitness
            from parameter_tuning import extract_best_fitness
            
            # Calculate expected output filename
            temp_cmd = [
                "python", "-c",
                f"""
import sys
sys.path.append('.')
from graph_io import read_graph
G, _ = read_graph('inputs/{input_file}', detect_weights=True)
k_nodes = int(len(list(G.nodes)) * 0.05)
k_edges = int(len(list(G.edges)) * 0.03)
print(f'{{k_edges}}_{{k_nodes}}')
"""
            ]
            
            temp_result = subprocess.run(temp_cmd, capture_output=True, text=True, timeout=30)
            if temp_result.returncode == 0:
                k_info = temp_result.stdout.strip()
                k_edges, k_nodes = k_info.split('_')
                
                input_basename_clean = os.path.splitext(os.path.basename(input_file))[0]
                output_filename = f"outputs/descending_mutation/ga/timing{run_id}_{input_basename_clean}_ke_{k_edges}_kn_{k_nodes}_wb_0.15_pairwise"
                
                print(f"Expected output file: {output_filename}")
                
                if os.path.exists(output_filename):
                    print("Output file exists!")
                    best_fitness = extract_best_fitness(output_filename)
                    print(f"Best fitness: {best_fitness}")
                else:
                    print("Output file does not exist!")
            else:
                print("Failed to calculate k_edges/k_nodes")
                
    except subprocess.TimeoutExpired:
        print("GA timed out!")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()