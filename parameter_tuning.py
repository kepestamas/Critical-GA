#!/usr/bin/env python3
"""
Parameter Tuning Script for Critical-GA
========================================

This script runs the genetic algorithm with various parameter combinations
to find optimal settings for the dual-constraint CNDP problem.

It tests all combinations of the specified parameters on the networks in
"Valogatas - parameter testing" directory and generates both CSV results
and standard GA output files.
"""

import subprocess
import time
import csv
import os
import itertools
from pathlib import Path
import glob


def extract_best_fitness(output_file):
    """
    Extract the best fitness value from a GA output file.
    The format is: "generation fitness solution"
    
    Args:
        output_file (str): Path to the GA output file
        
    Returns:
        float: Best fitness value, or None if file not found/readable
    """
    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
            if lines:
                # Last line format: "generation fitness solution"
                last_line = lines[-1].strip()
                parts = last_line.split(' ', 2)  # Split into at most 3 parts
                if len(parts) >= 2:
                    return float(parts[1])  # Second field is the fitness
        return None
    except (FileNotFoundError, ValueError, IndexError):
        return None


def main():
    """
    Main function to run parameter tuning experiments.
    """
    
    # Parameter combinations to test
    parameters = {
        'budget': [0.03, 0.05, 0.08],
        'node_fraction': [0.05],  # Fixed
        'edge_fraction': [0.03],  # Fixed
        'population_size': [50, 100],
        'tournament_size': [3, 5],
        'p_crossover': [0.8, 0.9],
        'p_mutation': [0.01, 0.02],
        'payoff_function': ['largest']  # Fixed to largest
    }

    generations = 200  # Fixed number of generations per run
    
    # Input files from "Tuning"
    input_files = [
        "Tuning/bog_150_p0.1_2.txt",
        "Tuning/cor_dolphins-w.txt", 
        "Tuning/hos_35_r1_1.txt",
        "Tuning/mac_grafo20dens30.txt"
    ]
    
    # Create output directory
    output_dir = "outputs/ga_node_weights/parameter_tuning"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create CSV file for results
    csv_file = os.path.join(output_dir, "parameter_tuning_results.csv")
    
    # CSV headers
    csv_headers = [
        'run_id', 'input_file', 'budget', 'node_fraction', 'edge_fraction',
        'population_size', 'tournament_size', 'p_crossover', 'p_mutation',
        'payoff_function', 'best_fitness', 'runtime_seconds'
    ]

    print("Running parameter tuning with "+str(generations)+" generations per run...")

    # Open CSV file for writing
    with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_headers)
            
            # Generate all parameter combinations
            param_names = ['budget', 'population_size', 'tournament_size', 'p_crossover', 'p_mutation']
            param_values = [parameters[name] for name in param_names]
            
            total_combinations = len(list(itertools.product(*param_values)))
            total_runs = total_combinations * len(input_files) * 10  # 10 runs each
            
            print(f"Starting parameter tuning with {total_combinations} combinations")
            print(f"Total runs: {total_runs} ({total_combinations} combinations × {len(input_files)} files × 10 runs)")
            print(f"Estimated time: {total_runs * 30 / 60:.1f} minutes (assuming 30s per run)")
            
            run_counter = 0
            
            # Iterate through all parameter combinations
            for combo in itertools.product(*param_values):
                budget, pop_size, tournament_size, p_cross, p_mut = combo
                
                combo_desc = f"budget={budget}, pop={pop_size}, tour={tournament_size}, cross={p_cross}, mut={p_mut}"
                print(f"\nTesting combination: {combo_desc}")
                
                # Test on each input file
                for input_file in input_files:
                    input_basename = os.path.basename(input_file)
                    # Remove file extension for output filename consistency
                    input_basename_clean = os.path.splitext(input_basename)[0]
                    print(f"  Processing {input_basename}...")
                    
                    # Run 10 times with different run_ids
                    for run_num in range(1, 11):
                        run_id = f"tune_{run_num}"
                        run_counter += 1
                        
                        print(f"    Run {run_num}/10 (overall {run_counter}/{total_runs})")
                        
                        # Prepare command
                        cmd = [
                            "python", "connectivity_ga.py",
                            input_file,                    # input file
                            run_id,                        # run_id
                            str(parameters['node_fraction'][0]),  # node_fraction (0.05)
                            str(parameters['edge_fraction'][0]),  # edge_fraction (0.03) 
                            str(budget),                   # weight_budget
                            str(pop_size),                 # population_size
                            str(tournament_size),          # tournament_size
                            str(p_cross),                  # p_crossover
                            str(p_mut),                    # p_mutation
                            parameters['payoff_function'][0],  # payoff_function (components)
                            str(generations)                          # generation_count
                        ]
                        
                        # Record start time
                        start_time = time.time()
                        
                        # Run the GA
                        try:
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 min timeout
                            
                            if result.returncode != 0:
                                print(f"      ERROR: GA failed with return code {result.returncode}")
                                print(f"      stderr: {result.stderr}")
                                best_fitness = None
                            else:
                                # Calculate runtime
                                runtime = time.time() - start_time
                                
                                # Extract best fitness from output file
                                # Output filename format from connectivity_ga.py:
                                # "outputs/descending_mutation/ga/timing" + run_id + "_" + input_file + "_ke_" + k_edges + "_kn_" + k_nodes + "_wb_" + weight_budget + "_" + payoff_function
                                
                                # We need to calculate k_edges and k_nodes
                                # This requires reading the input file temporarily
                                temp_cmd = [
                                    "python", "-c",
                                    f"""
import sys
sys.path.append('.')
from graph_io import read_graph
G, _ = read_graph('inputs/{input_file}', detect_weights=True)
k_nodes = int(len(list(G.nodes)) * {parameters['node_fraction'][0]})
k_edges = int(len(list(G.edges)) * {parameters['edge_fraction'][0]})
print(f'{{k_edges}}_{{k_nodes}}')
"""
                                ]
                                
                                try:
                                    temp_result = subprocess.run(temp_cmd, capture_output=True, text=True, timeout=30)
                                    if temp_result.returncode == 0:
                                        k_info = temp_result.stdout.strip()
                                        k_edges, k_nodes = k_info.split('_')
                                        
                                        # Construct expected output filename (using clean basename without extension)
                                        output_filename = f"outputs/descending_mutation/ga/timing{run_id}_{input_basename_clean}_ke_{k_edges}_kn_{k_nodes}_wb_{budget}_{parameters['payoff_function'][0]}"
                                        
                                        best_fitness = extract_best_fitness(output_filename)
                                        
                                        if best_fitness is None:
                                            print(f"      WARNING: Could not extract fitness from {output_filename}")
                                    else:
                                        print(f"      ERROR: Could not calculate k_edges/k_nodes")
                                        best_fitness = None
                                        runtime = time.time() - start_time
                                except subprocess.TimeoutExpired:
                                    print(f"      ERROR: Timeout calculating graph parameters")
                                    best_fitness = None
                                    runtime = time.time() - start_time
                                
                        except subprocess.TimeoutExpired:
                            print(f"      ERROR: GA timeout after 5 minutes")
                            best_fitness = None
                            runtime = 300.0
                        
                        # Write result to CSV
                        csv_row = [
                            run_id,
                            input_file,
                            budget,
                            parameters['node_fraction'][0],
                            parameters['edge_fraction'][0],
                            pop_size,
                            tournament_size,
                            p_cross,
                            p_mut,
                            parameters['payoff_function'][0],
                            best_fitness if best_fitness is not None else 'ERROR',
                            f"{runtime:.2f}"
                        ]
                        
                        writer.writerow(csv_row)
                        csvfile.flush()  # Ensure data is written immediately
                        
                        print(f"      Best fitness: {best_fitness}, Runtime: {runtime:.2f}s")
    
    print(f"\nParameter tuning completed!")
    print(f"Results saved to: {csv_file}")
    print(f"GA output files saved to: outputs/descending_mutation/ga/")
    
    # Generate summary statistics
    print("\nGenerating summary...")
    
    try:
        # Read the CSV back and create summary
        summary_file = os.path.join(output_dir, "parameter_tuning_summary.txt")
        
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            results = list(reader)
        
        # Filter out error results
        valid_results = [r for r in results if r['best_fitness'] != 'ERROR']
        
        with open(summary_file, 'w') as f:
            f.write("Parameter Tuning Summary\n")
            f.write("=======================\n\n")
            f.write(f"Total runs: {len(results)}\n")
            f.write(f"Successful runs: {len(valid_results)}\n")
            f.write(f"Failed runs: {len(results) - len(valid_results)}\n\n")
            
            if valid_results:
                # Group by parameter combination
                param_combos = {}
                for result in valid_results:
                    key = (
                        result['budget'], result['population_size'], 
                        result['tournament_size'], result['p_crossover'], result['p_mutation']
                    )
                    if key not in param_combos:
                        param_combos[key] = []
                    param_combos[key].append(float(result['best_fitness']))
                
                f.write("Average fitness by parameter combination:\n")
                f.write("-" * 50 + "\n")
                
                # Sort by average fitness (ascending for minimization problems like components)
                sorted_combos = sorted(param_combos.items(), 
                                     key=lambda x: sum(x[1])/len(x[1]))
                
                for params, fitnesses in sorted_combos:
                    budget, pop_size, tour_size, p_cross, p_mut = params
                    avg_fitness = sum(fitnesses) / len(fitnesses)
                    f.write(f"Budget={budget}, Pop={pop_size}, Tour={tour_size}, Cross={p_cross}, Mut={p_mut}: "
                           f"Avg={avg_fitness:.2f} (n={len(fitnesses)})\n")
        
        print(f"Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"Error generating summary: {e}")


if __name__ == "__main__":
    main()