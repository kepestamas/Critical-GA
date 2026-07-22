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
import sys
import argparse
import itertools
from pathlib import Path
import glob
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count


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


def run_single_ga(task):
    """
    Run a single GA experiment. Designed to be called from a process pool.
    
    Args:
        task (dict): Dictionary with all parameters for this run.
        
    Returns:
        dict: Result dictionary with fitness and runtime.
    """
    cmd = task['cmd']
    ga_timeout = task['ga_timeout']
    max_fitness_only = task['max_fitness_only']
    run_num = task['run_num']
    input_file = task['input_file']
    input_basename_clean = task['input_basename_clean']
    budget = task['budget']
    node_fraction = task['node_fraction']
    edge_fraction = task['edge_fraction']
    pop_size = task['pop_size']
    tournament_size = task['tournament_size']
    p_cross = task['p_cross']
    p_mut = task['p_mut']
    payoff = task['payoff']
    run_id = task['run_id']
    run_counter = task['run_counter']
    total_runs = task['total_runs']
    mutation_type = task['mutation_type']
    max_switch_pct = task['max_switch_pct']

    print(f"    Run {run_num}/10 (overall {run_counter}/{total_runs})")

    start_time = time.time()
    best_fitness = None
    runtime = 0.0
    result = None

    try:
        if (max_fitness_only and run_num == 1) or (not max_fitness_only):
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=ga_timeout)
        else:
            result = None

        runtime = time.time() - start_time

        if result is not None and result.returncode != 0:
            print(f"      ERROR: GA failed with return code {result.returncode}")
            print(f"      stderr: {result.stderr}")
            if result.stdout:
                print(f"      stdout: {result.stdout[:200]}...")
            best_fitness = None
        elif result is not None:
            # Calculate k_edges and k_nodes by reading the graph
            temp_cmd = [
                "python", "-c",
                f"""
import sys
sys.path.append('.')
from graph_io import read_graph
G, _ = read_graph('inputs/{input_file}', detect_weights=True)
k_nodes = int(len(list(G.nodes)) * {node_fraction})
k_edges = int(len(list(G.edges)) * {edge_fraction})
print(f'{{k_edges}}_{{k_nodes}}')
"""
            ]

            try:
                if (max_fitness_only and run_num == 1) or (not max_fitness_only):
                    temp_result = subprocess.run(temp_cmd, capture_output=True, text=True, timeout=ga_timeout)
                else:
                    temp_result = None

                if temp_result is not None and temp_result.returncode == 0:
                    k_info = temp_result.stdout.strip()
                    k_edges, k_nodes = k_info.split('_')

                    if (max_fitness_only and run_num == 1) or (not max_fitness_only):
                        output_filename = f"outputs/descending_mutation/ga/timing{run_id}_{input_basename_clean}_ke_{k_edges}_kn_{k_nodes}_wb_{budget}_{payoff}"

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
        print(f"      ERROR: GA timeout after {ga_timeout // 60} minutes")
        best_fitness = None
        runtime = ga_timeout

    print(f"      Best fitness: {best_fitness}, Runtime: {runtime:.2f}s")

    # Extract fitness counter from GA stdout
    fitness_counter = 'N/A'
    if result is not None and result.stdout:
        for line in result.stdout.strip().split('\n'):
            if line.startswith('FINAL_FITNESS_COUNT='):
                try:
                    fitness_counter = int(line.split('=')[1])
                except (ValueError, IndexError):
                    pass

    return {
        'run_id': run_id,
        'input_file': input_file,
        'budget': budget,
        'node_fraction': node_fraction,
        'edge_fraction': edge_fraction,
        'pop_size': pop_size,
        'tournament_size': tournament_size,
        'p_cross': p_cross,
        'p_mut': p_mut,
        'payoff': payoff,
        'best_fitness': best_fitness,
        'runtime': runtime,
        'mutation_type': mutation_type,
        'max_switch_pct': max_switch_pct,
        'fitness_counter': fitness_counter,
    }


def main():
    """
    Main function to run parameter tuning/final experiments.
    """

    # --- CLI argument: parallel workers ---
    parser = argparse.ArgumentParser(description="Critical-GA parameter runner")
    parser.add_argument(
        '-j', '--parallel',
        type=int,
        default=max(cpu_count() - 1, 1),
        help=f"Number of parallel workers (default: cpu_count-1 = {max(cpu_count()-1, 1)})"
    )
    args = parser.parse_args()
    parallel_workers = args.parallel
    print(f"Parallel workers: {parallel_workers} (CPUs available: {cpu_count()})")

    # Parameter combinations to run for node weights GA
    parameters = {
        'budget': [0.5],
        'node_fraction': [0.05],  # Fixed
        'edge_fraction': [0.03],  # Fixed
        'population_size': [200],
        'tournament_size': [5],
        'p_crossover': [0.8],
        'p_mutation': [0.01],
        'payoff_function': ['largest','pairwise','components'],
        'mutation_type': [0],  # 0 for standard mutation, 1 for descending mutation
        'max_switch_pct': [50]  # max crossover switches as percentage of k_nodes
    }

    # Final parameter combinations - tuning for node weights GA
    # parameters = {
    #     'budget': [0.05, 0.15, 0.25, 0.5, 1.0],
    #     'node_fraction': [0.05],  # Fixed - no moves to make
    #     'edge_fraction': [0.03],  # Fixed - no moves to make
    #     'population_size': [50,100],
    #     'tournament_size': [3,5],
    #     'p_crossover': [0.8, 0.9],
    #     'p_mutation': [0.01, 0.02],
    #     'payoff_function': ['largest','pairwise','components'],
    #     'mutation_type': [0, 1],  # 0 for standard mutation, 1 for descending mutation
    #     'max_switch_pct': [50]  # max crossover switches as percentage of k_nodes
    # }

    max_fitness_only = False # just a max_fitness value run, no moves made

    generations = 2000  # Fixed number of generations per run
    run_per_conf = 30   # runs per parameter combination (for averaging)

    ga_timeout = None #20000000  # seconds
    
    # Input files from "Tuning"
    # input_files = [
    #     "Tuning/bog_150_p0.1_2.txt",
    #     "Tuning/cor_dolphins-w.txt", 
    #     "Tuning/hos_35_r1_1.txt",
    #     "Tuning/mac_grafo20dens30.txt"
    #     # "Testing/network-cor-forma_eu_27t.txt",
    # ]
    
    # Input files from "Testing"
    input_files = [
        "Testing/network-cor-forma_eu_27t.txt",
        #"Testing/cor_ip_as_network-w.txt",
        #"Testing/cor_ip_as_network_caida-w.txt",
        #"Testing/cor_adjnoun-w.txt",
        #"Testing/cor_celegans_metabolic-w.txt",
        #"Testing/cor_celegansneural-w.txt",
        # "Testing/cor_dolphins-w.txt",
        # "Testing/cor_football-w.txt",
        # "Testing/cor_jazz-w.txt",
        # "Testing/cor_karate-w.txt",
        # "Testing/cor_lesmis-w.txt",
        # "Testing/cor_n050plai01.txt",
        # "Testing/cor_n100plai01.txt",
        # "Testing/cor_n150plai01.txt",
        # "Testing/cor_n200plai01.txt",
        # "Testing/cor_n250plai01.txt",
        # "Testing/cor_n300plai01.txt",
        # "Testing/cor_n350plai01.txt",
        # "Testing/cor_polbooks-w.txt",
        # "Testing/hos_20_r1_1.txt",
        # "Testing/hos_20_r2_1.txt",
        # "Testing/hos_25_r1_1.txt",
        # "Testing/hos_25_r2_1.txt",
        # "Testing/hos_30_r1_1.txt",
        # "Testing/hos_30_r2_1.txt",
        # "Testing/hos_35_r1_1.txt",
        # "Testing/hos_35_r2_1.txt",
        # "Testing/hos_40_r1_1.txt",
        # "Testing/hos_40_r2_1.txt",
        # "Testing/hos_45_r1_1.txt",
        # "Testing/hos_45_r2_1.txt",
        # "Testing/hos_50_r1_1.txt",
        # "Testing/hos_50_r2_1.txt",
        # "Testing/mac_grafo10dens30.txt",
        # "Testing/mac_grafo11dens30.txt",
        # "Testing/mac_grafo12dens30.txt",
        # "Testing/mac_grafo13dens30.txt",
        # "Testing/mac_grafo14dens30.txt",
        # "Testing/mac_grafo15dens30.txt",
        # "Testing/mac_grafo16dens30.txt",
        # "Testing/mac_grafo17dens30.txt",
        # "Testing/mac_grafo18dens30.txt",
        # "Testing/mac_grafo19dens30.txt",
        # "Testing/mac_grafo20dens30.txt",
        # "Testing/mac_grafo21dens30.txt",
        # "Testing/mac_grafo22dens30.txt",
        # "Testing/mac_grafo23dens30.txt",
        # "Testing/mac_grafo24dens30.txt",
        # "Testing/mac_grafo25dens30.txt",
        # "Testing/mac_grafo26dens30.txt",
        # "Testing/mac_grafo27dens30.txt",
        # "Testing/mac_grafo28dens30.txt",
        # "Testing/mac_grafo29dens30.txt",
        # "Testing/mac_grafo30dens30.txt"
    ]
    
    # Create output directory
    output_dir = "outputs/ga_node_weights/running"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create CSV file for results
    csv_file = os.path.join(output_dir, "running_results.csv")
    
    # CSV headers
    csv_headers = [
        'run_id', 'input_file', 'budget', 'node_fraction', 'edge_fraction',
        'population_size', 'tournament_size', 'p_crossover', 'p_mutation',
        'payoff_function', 'mutation_type', 'max_switch_pct',
        'best_fitness', 'runtime_seconds', 'fitness_counter'
    ]

    print("Running with "+str(generations)+" generations per run...")

    # Open CSV file for writing
    with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_headers)
            
            # Generate all parameter combinations
            param_names = ['budget', 'population_size', 'tournament_size', 'p_crossover', 'p_mutation', 'payoff_function', 'mutation_type']
            param_values = [parameters[name] for name in param_names]
            
            total_combinations = len(list(itertools.product(*param_values)))

            run_counter = 0

            # Build all tasks upfront
            tasks = []
            for combo in itertools.product(*param_values):
                budget, pop_size, tournament_size, p_cross, p_mut, payoff, mutation_type = combo

                for input_file in input_files:
                    input_basename = os.path.basename(input_file)
                    input_basename_clean = os.path.splitext(input_basename)[0]

                    for run_num in range(1, run_per_conf + 1):
                        run_counter += 1
                        run_id = f"run_{run_num}"

                        cmd = [
                            "python", "connectivity_ga_corrected.py",
                            input_file,
                            run_id,
                            str(parameters['node_fraction'][0]),
                            str(parameters['edge_fraction'][0]),
                            str(budget),
                            str(pop_size),
                            str(tournament_size),
                            str(p_cross),
                            str(p_mut),
                            str(payoff),
                            str(generations),
                            str(mutation_type),  # Pass mutation type to GA
                            str(parameters['max_switch_pct'][0])  # Pass max switch percentage to GA
                        ]

                        tasks.append({
                            'cmd': cmd,
                            'ga_timeout': ga_timeout,
                            'max_fitness_only': max_fitness_only,
                            'run_num': run_num,
                            'input_file': input_file,
                            'input_basename_clean': input_basename_clean,
                            'budget': budget,
                            'node_fraction': parameters['node_fraction'][0],
                            'edge_fraction': parameters['edge_fraction'][0],
                            'pop_size': pop_size,
                            'tournament_size': tournament_size,
                            'p_cross': p_cross,
                            'p_mut': p_mut,
                            'payoff': payoff,
                            'mutation_type': mutation_type,
                            'max_switch_pct': parameters['max_switch_pct'][0],
                            'run_id': run_id,
                            'run_counter': run_counter,
                            'total_runs': total_combinations * len(input_files) * run_per_conf,
                        })

            total_runs = len(tasks)
            print(f"Starting running with {total_combinations} combinations")
            print(f"Total runs: {total_runs} ({total_combinations} combinations × {len(input_files)} files × {run_per_conf} runs)")
            print(f"Estimated time (sequential): {total_runs * 30 / 60:.1f} min | parallel ({parallel_workers}w): ~{total_runs * 30 / 60 / parallel_workers:.1f} min")

            # Execute tasks in parallel
            completed = 0
            with ProcessPoolExecutor(max_workers=parallel_workers) as executor:
                future_to_task = {executor.submit(run_single_ga, t): t for t in tasks}

                for future in as_completed(future_to_task):
                    completed += 1
                    try:
                        res = future.result()
                    except Exception as exc:
                        task_info = future_to_task[future]
                        print(f"      EXCEPTION in {task_info['input_file']} run {task_info['run_num']}: {exc}")
                        res = {
                            'run_id': task_info['run_id'],
                            'input_file': task_info['input_file'],
                            'budget': task_info['budget'],
                            'node_fraction': task_info['node_fraction'],
                            'edge_fraction': task_info['edge_fraction'],
                            'pop_size': task_info['pop_size'],
                            'tournament_size': task_info['tournament_size'],
                            'p_cross': task_info['p_cross'],
                            'p_mut': task_info['p_mut'],
                            'payoff': task_info['payoff'],
                            'best_fitness': None,
                            'runtime': 0.0,
                            'mutation_type': task_info['mutation_type'],
                            'max_switch_pct': task_info.get('max_switch_pct', 'N/A'),
                            'fitness_counter': 'N/A'
                        }

                    csv_row = [
                        res['run_id'],
                        res['input_file'],
                        res['budget'],
                        res['node_fraction'],
                        res['edge_fraction'],
                        res['pop_size'],
                        res['tournament_size'],
                        res['p_cross'],
                        res['p_mut'],
                        res['payoff'],
                        res['mutation_type'],
                        res.get('max_switch_pct', 'N/A'),
                        res['best_fitness'] if res['best_fitness'] is not None else 'ERROR',
                        f"{res['runtime']:.2f}",
                        res.get('fitness_counter', 'N/A'),
                    ]

                    writer.writerow(csv_row)
                    csvfile.flush()

                    if completed % 10 == 0 or completed == total_runs:
                        print(f"  Progress: {completed}/{total_runs} runs completed")
    
    print(f"\nRunning completed!")
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
            f.write("Running Summary\n")
            f.write("===============\n\n")
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