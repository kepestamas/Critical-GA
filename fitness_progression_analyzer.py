#!/usr/bin/env python3
"""
Analysis script for parameter tuning results.

This script processes the running_results.csv file from parameter tuning
and extracts fitness progression data from corresponding generation files.
For each run, it finds when the best fitness was first achieved and outputs
the complete fitness progression.

Output format: best_fitness,generation_number,fitness_value_1,fitness_value_2,...,fitness_value_200
"""

import csv
import os
import re
import glob
import logging
from pathlib import Path


def clean_filename(filename):
    """Clean filename for use in generation file naming."""
    # Remove file extension and directory path
    name = Path(filename).name  # Get just the filename, not the full path
    name = Path(name).stem      # Remove extension
    # Replace special characters with underscores, but preserve dashes
    name = re.sub(r'[^\w-]', '_', name)
    return name


def construct_generation_filename(run_id, input_file, budget, payoff_function):
    """Construct the expected generation filename pattern."""
    input_clean = clean_filename(input_file)
    # Create a glob pattern that matches the timing file format
    # timingtune_<run_id>_<input_clean>_ke_*_kn_*_wb_<budget>_<payoff_function>
    return f"timingtune_{run_id}_{input_clean}_ke_*_kn_*_wb_{budget}_{payoff_function}"


def extract_fitness_values(generation_file_path):
    """Extract fitness values from a generation file."""
    fitness_values = []

    try:
        with open(generation_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # Split by space and take the second element (fitness value)
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            fitness = float(parts[1])
                            fitness_values.append(fitness)
                        except ValueError:
                            print(f"Warning: Could not parse fitness value from line: {line}")
                            fitness_values.append(0.0)  # Default value
    except FileNotFoundError:
        print(f"Warning: Generation file not found: {generation_file_path}")
        return None
    except Exception as e:
        print(f"Error reading generation file {generation_file_path}: {e}")
        return None

    return fitness_values


def find_first_best_generation(fitness_values, best_fitness):
    """Find the first generation where fitness equals best_fitness."""
    if fitness_values is None:
        return None

    for i, fitness in enumerate(fitness_values):
        if abs(fitness - best_fitness) < 1e-6:  # Use small epsilon for float comparison
            return i

    return None  # Best fitness never achieved


def main():
    # Paths
    csv_file = Path("outputs/ga_node_weights/running/running_results.csv")
    generation_dir = Path("outputs/descending_mutation/ga")
    output_file = Path("fitness_progression_analysis.csv")
    log_file = Path("fitness_progression_analysis.log")

    # Set up logging
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("Starting fitness progression analysis")
    logging.info(f"CSV file: {csv_file}")
    logging.info(f"Generation directory: {generation_dir}")
    logging.info(f"Output file: {output_file}")

    if not csv_file.exists():
        error_msg = f"Error: CSV file not found: {csv_file}"
        print(error_msg)
        logging.error(error_msg)
        return

    if not generation_dir.exists():
        error_msg = f"Error: Generation directory not found: {generation_dir}"
        print(error_msg)
        logging.error(error_msg)
        return

    # Read CSV and process each run
    results = []
    fieldnames = None

    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Extract run_id number from format like "tune_1"
            run_id_str = row['run_id']
            if run_id_str.startswith('tune_'):
                run_id = int(run_id_str.split('_')[1])
            else:
                run_id = int(run_id_str)

            input_file = row['input_file']
            budget = row['budget']  # Using budget field for wb_ parameter
            payoff_function = row['payoff_function']

            try:
                best_fitness = float(row['best_fitness'])
            except ValueError:
                print(f"Warning: Invalid best_fitness for run {run_id}: {row['best_fitness']}")
                continue

            # Construct generation filename pattern and find matching files
            gen_pattern = construct_generation_filename(run_id, input_file, budget, payoff_function)
            matching_files = list(generation_dir.glob(gen_pattern))

            if not matching_files:
                warning_msg = f"No generation files found matching pattern: {gen_pattern}"
                print(f"Warning: {warning_msg}")
                logging.warning(f"GENERATION_FILE_MISSING - Run: {run_id}, Input: {input_file}, "
                              f"Pattern: {gen_pattern}, Budget: {budget}, Payoff: {payoff_function}, "
                              f"CSV_Row: {row}")
                continue
            elif len(matching_files) > 1:
                info_msg = f"Multiple generation files found for run {run_id}, using first: {matching_files[0].name}"
                print(f"Warning: {info_msg}")
                logging.info(f"MULTIPLE_GENERATION_FILES - Run: {run_id}, Files: {[f.name for f in matching_files]}, "
                           f"Using: {matching_files[0].name}, Input: {input_file}, "
                           f"Budget: {budget}, Payoff: {payoff_function}, CSV_Row: {row}")

            gen_file_path = matching_files[0]

            # Extract fitness values
            fitness_values = extract_fitness_values(gen_file_path)

            if fitness_values is None:
                print(f"Skipping run {run_id}: Could not read generation file")
                continue

            # Find first generation with best fitness
            first_gen = find_first_best_generation(fitness_values, best_fitness)

            if first_gen is None:
                warning_msg = f"Best fitness {best_fitness} never achieved in run {run_id}"
                print(f"Warning: {warning_msg}")
                
                # Log detailed information
                final_fitness = fitness_values[-1] if fitness_values else 0.0
                gen_count = len(fitness_values)
                logging.warning(f"BEST_FITNESS_NOT_ACHIEVED - Run: {run_id}, Input: {input_file}, "
                              f"Expected: {best_fitness}, Achieved: {final_fitness}, "
                              f"Generations: {gen_count}, Budget: {budget}, Payoff: {payoff_function}, "
                              f"Generation_File: {gen_file_path.name}, CSV_Row: {row}")
                
                first_gen = -1  # Indicate not found

            # Check if generation count is less than 200
            gen_count = len(fitness_values)
            if gen_count < 200:
                logging.info(f"INCOMPLETE_GENERATIONS - Run: {run_id}, Input: {input_file}, "
                           f"Generations: {gen_count}/200, Best Fitness: {best_fitness}, "
                           f"Final Fitness: {fitness_values[-1] if fitness_values else 0.0}, "
                           f"Budget: {budget}, Payoff: {payoff_function}, "
                           f"Generation_File: {gen_file_path.name}, CSV_Row: {row}")

            # Prepare output row: all original columns + generation_number + fitness values
            output_row = [row[col] for col in fieldnames] + [first_gen] + fitness_values
            results.append(output_row)

    # Write output CSV
    if results:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write header: all original columns + generation_number + fitness values
            header = list(fieldnames) + ['generation_number'] + [f'fitness_value_{i+1}' for i in range(200)]
            writer.writerow(header)

            # Write data
            for row in results:
                writer.writerow(row)

        print(f"Analysis complete. Results written to {output_file}")
        print(f"Processed {len(results)} runs successfully")
        
        logging.info(f"Analysis completed successfully")
        logging.info(f"Total runs processed: {len(results)}")
        logging.info(f"Output written to: {output_file}")
        logging.info(f"Detailed log written to: {log_file}")
        
    else:
        print("No valid runs found to process")
        logging.warning("No valid runs found to process")


if __name__ == "__main__":
    main()