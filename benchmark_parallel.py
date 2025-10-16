# Performance Test Script for Parallel GA
# Tests the optimized implementation vs serial mode

import subprocess
import time

def run_test(use_parallel, population_size):
    """Run GA and measure execution time."""
    # Create temporary test file
    import sys
    import os
    
    # Read connectivity_ga.py
    with open('connectivity_ga.py', 'r') as f:
        code = f.read()
    
    # Modify USE_PARALLEL setting
    if use_parallel:
        code = code.replace('USE_PARALLEL = True', 'USE_PARALLEL = True')
    else:
        code = code.replace('USE_PARALLEL = True', 'USE_PARALLEL = False')
    
    # Write temporary file
    temp_file = 'connectivity_ga_temp.py'
    with open(temp_file, 'w') as f:
        f.write(code)
    
    # Run and time
    cmd = f'python {temp_file} karate.txt benchmark 0.1 0.05 {population_size} 3 0.8 0.05'
    
    start = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    elapsed = time.time() - start
    
    # Cleanup
    os.remove(temp_file)
    
    return elapsed, result.returncode == 0

print("=" * 60)
print("GA Performance Benchmark")
print("=" * 60)
print()

# Test configurations
configs = [
    (50, "Small"),
    (100, "Medium"),
    (200, "Large"),
]

for pop_size, label in configs:
    print(f"\n{label} Population (size={pop_size}):")
    print("-" * 40)
    
    # Test serial
    print(f"  Serial mode...", end="", flush=True)
    serial_time, serial_ok = run_test(False, pop_size)
    if serial_ok:
        print(f" {serial_time:.2f}s")
    else:
        print(" FAILED")
        continue
    
    # Test parallel
    print(f"  Parallel mode...", end="", flush=True)
    parallel_time, parallel_ok = run_test(True, pop_size)
    if parallel_ok:
        print(f" {parallel_time:.2f}s")
    else:
        print(" FAILED")
        continue
    
    # Calculate speedup
    speedup = serial_time / parallel_time if parallel_time > 0 else 0
    print(f"  Speedup: {speedup:.2f}x")

print()
print("=" * 60)
