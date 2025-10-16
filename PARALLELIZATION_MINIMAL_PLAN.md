# Minimal Parallelization Plan for GA

**Goal:** Add multiprocessing to fitness evaluation with minimal code changes.

**Approach:** Simple and direct - parallelize what matters, skip the rest.

---

## 🎯 Core Strategy

**What to parallelize:**
1. Initial population fitness evaluation
2. Tournament crossover children fitness evaluation

**What NOT to parallelize:**
- Everything else (not worth the complexity)

**Configuration:**
- Global variable: `N_PROCESSES` (set once, use everywhere)
- No dynamic tuning, no decision logic

---

## 📋 Implementation Checklist

### Part 1: Setup (30 minutes)

- [ ] **1.1** Add imports at top of `connectivity_ga.py`:
  ```python
  from multiprocessing import Pool, cpu_count
  import os
  ```

- [ ] **1.2** Add global configuration (after other globals):
  ```python
  # Multiprocessing configuration
  N_PROCESSES = cpu_count() - 1  # or set to fixed number like 4
  USE_PARALLEL = True            # Easy on/off switch
  ```

### Part 2: Create Worker Function (1 hour)

- [ ] **2.1** Create picklable fitness evaluation function:
  ```python
  def evaluate_individual_worker(args):
      """Worker function for parallel fitness evaluation.
      
      Args:
          args: tuple of (individual, graph_edges, graph_nodes, payoff_func_name)
      
      Returns:
          tuple: (individual, fitness_value)
      """
      individual, graph_edges, graph_nodes, payoff_func_name = args
      
      # Reconstruct graph in worker
      G_worker = nx.Graph()
      G_worker.add_nodes_from(graph_nodes)
      G_worker.add_edges_from(graph_edges)
      
      # Get payoff function
      payoff_func = get_payoff_function(payoff_func_name)
      
      # Calculate fitness
      P = copy.deepcopy(G_worker)
      P.remove_nodes_from(individual[0])
      P.remove_edges_from(individual[1])
      result = payoff_func(nx.connected_components(P))
      
      return (individual, result)
  ```

- [ ] **2.2** Create helper to serialize graph (before worker function):
  ```python
  def serialize_graph_data(graph):
      """Extract picklable data from graph.
      
      Args:
          graph: NetworkX graph
          
      Returns:
          tuple: (edges, nodes) as lists
      """
      return (list(graph.edges()), list(graph.nodes()))
  ```

### Part 3: Create Parallel Batch Evaluator (1 hour)

- [ ] **3.1** Add main parallel evaluation function:
  ```python
  def parallel_fitness_batch(individuals, graph_data, payoff_func_name):
      """Evaluate fitness for multiple individuals in parallel.
      
      Args:
          individuals: list of individuals to evaluate
          graph_data: tuple of (edges, nodes) from serialize_graph_data()
          payoff_func_name: name of payoff function to use
          
      Returns:
          list: [(individual, fitness_value), ...]
      """
      if not USE_PARALLEL or len(individuals) < 10:
          # Fallback to serial for small batches
          results = []
          for ind in individuals:
              results.append((ind, fitness(ind)))
          return results
      
      # Prepare arguments for each worker
      graph_edges, graph_nodes = graph_data
      args = [(ind, graph_edges, graph_nodes, payoff_func_name) 
              for ind in individuals]
      
      # Parallel evaluation
      with Pool(processes=N_PROCESSES) as pool:
          results = pool.map(evaluate_individual_worker, args)
      
      return results
  ```

### Part 4: Modify Initial Population (15 minutes)

- [ ] **4.1** Find the initial population evaluation in `ga()`:
  ```python
  # OLD CODE (around line 285):
  evaluated_population = [(individual, fitness(individual)) for individual in population]
  ```

- [ ] **4.2** Replace with parallel version:
  ```python
  # NEW CODE:
  # Serialize graph data once
  graph_data = serialize_graph_data(G)
  
  # Parallel evaluation of initial population
  if USE_PARALLEL:
      evaluated_population = parallel_fitness_batch(
          population, graph_data, payoff_function_name
      )
  else:
      evaluated_population = [(individual, fitness(individual)) 
                              for individual in population]
  ```

### Part 5: Modify Tournament Crossover (30 minutes)

- [ ] **5.1** Find the crossover tournament function `crossover_tournament()`:
  ```python
  # OLD CODE (around line 267-270):
  def crossover_tournament(evaluated_population):
      print("Tournament")
      evaluated_child_population = []
      for _ in range(tournament_round_count):
          first_child, second_child = tournament_round(evaluated_population)
          evaluated_child_population.append((copy.deepcopy(first_child), fitness(first_child)))
          evaluated_child_population.append((copy.deepcopy(second_child), fitness(second_child)))
      return evaluated_child_population
  ```

- [ ] **5.2** Replace with parallel version:
  ```python
  # NEW CODE:
  def crossover_tournament(evaluated_population, graph_data=None, payoff_func_name=None):
      print("Tournament")
      
      # Generate all children first
      children = []
      for _ in range(tournament_round_count):
          first_child, second_child = tournament_round(evaluated_population)
          children.extend([copy.deepcopy(first_child), copy.deepcopy(second_child)])
      
      # Parallel evaluation of all children
      if USE_PARALLEL and graph_data is not None:
          evaluated_child_population = parallel_fitness_batch(
              children, graph_data, payoff_func_name
          )
      else:
          # Serial fallback
          evaluated_child_population = [(child, fitness(child)) for child in children]
      
      return evaluated_child_population
  ```

- [ ] **5.3** Update the call to `crossover_tournament()` in `ga()`:
  ```python
  # OLD CODE:
  evaluated_child_population = crossover_tournament(evaluated_population)
  
  # NEW CODE:
  evaluated_child_population = crossover_tournament(
      evaluated_population, graph_data, payoff_function_name
  )
  ```

### Part 6: Add Main Guard (5 minutes)

- [ ] **6.1** Wrap the execution code at the bottom:
  ```python
  # OLD CODE (at end of file):
  print(list(G.nodes))
  ga()
  
  # NEW CODE:
  if __name__ == '__main__':
      print(list(G.nodes))
      ga()
  ```

### Part 7: Handle Fitness Counter (15 minutes)

- [ ] **7.1** The fitness counter won't work correctly in parallel. Two options:

  **Option A - Disable counter in parallel mode (SIMPLE):**
  ```python
  # In parallel_fitness_batch(), add after results:
  if USE_PARALLEL:
      # Estimate fitness count (won't be exact)
      payoff_functions.fitness_count += len(individuals)
  ```

  **Option B - Collect from workers (ACCURATE but complex):**
  ```python
  # Modify worker to return count:
  def evaluate_individual_worker(args):
      # ... existing code ...
      return (individual, result, 1)  # Return count
  
  # In parallel_fitness_batch():
  results = pool.map(evaluate_individual_worker, args)
  total_count = sum(r[2] for r in results)
  payoff_functions.fitness_count += total_count
  results = [(r[0], r[1]) for r in results]  # Remove count
  ```

  **Choose Option A for simplicity.**

### Part 8: Testing (30 minutes)

- [ ] **8.1** Test with parallel enabled:
  ```bash
  python connectivity_ga.py karate.txt parallel_test 0.1 0.05 50 3 0.8 0.05
  ```

- [ ] **8.2** Test with parallel disabled:
  ```python
  # In code, temporarily set:
  USE_PARALLEL = False
  ```
  ```bash
  python connectivity_ga.py karate.txt serial_test 0.1 0.05 50 3 0.8 0.05
  ```

- [ ] **8.3** Verify results are similar (not identical due to parallel randomness)

- [ ] **8.4** Time both versions to confirm speedup:
  ```bash
  # Measure execution time
  Measure-Command { python connectivity_ga.py karate.txt test 0.1 0.05 100 3 0.8 0.05 }
  ```

---

## 🔧 Complete Code Structure

### File organization after changes:

```python
# connectivity_ga.py structure:

# 1. Imports (existing + multiprocessing)
from multiprocessing import Pool, cpu_count
import os

# 2. Configuration (existing + parallel config)
N_PROCESSES = cpu_count() - 1
USE_PARALLEL = True

# 3. Graph reading and setup (existing, unchanged)
# ... existing code ...

# 4. NEW: Helper functions
def serialize_graph_data(graph):
    # ...

def evaluate_individual_worker(args):
    # ...

def parallel_fitness_batch(individuals, graph_data, payoff_func_name):
    # ...

# 5. Existing functions (mostly unchanged)
def generate_pop():
    # ... unchanged

def fitness(individual):
    # ... unchanged

# ... other existing functions ...

def crossover_tournament(evaluated_population, graph_data=None, payoff_func_name=None):
    # ... MODIFIED (collect children, then batch evaluate)

# 6. Main GA function (modified)
def ga():
    # ... 
    graph_data = serialize_graph_data(G)  # NEW: serialize once
    
    # MODIFIED: parallel initial population
    if USE_PARALLEL:
        evaluated_population = parallel_fitness_batch(...)
    else:
        evaluated_population = [(individual, fitness(individual)) for individual in population]
    
    for current_gen in range(gen_count):
        # MODIFIED: pass graph_data to crossover
        evaluated_child_population = crossover_tournament(
            evaluated_population, graph_data, payoff_function_name
        )
        # ... rest unchanged

# 7. Main guard (NEW)
if __name__ == '__main__':
    print(list(G.nodes))
    ga()
```

---

## 📊 Expected Changes Summary

| What | Changes | Lines Added/Modified |
|------|---------|---------------------|
| Imports | Add multiprocessing imports | +2 lines |
| Config | Add N_PROCESSES, USE_PARALLEL | +3 lines |
| Worker function | New function | +25 lines |
| Serialize helper | New function | +8 lines |
| Batch evaluator | New function | +25 lines |
| Initial population | Modify evaluation | +5 lines |
| Crossover tournament | Modify to collect then batch | +10 lines |
| Main guard | Wrap execution | +2 lines |
| **TOTAL** | | **~80 lines** |

---

## ⚡ Quick Reference

### Configuration
```python
N_PROCESSES = 4              # Number of worker processes
USE_PARALLEL = True          # Enable/disable parallelization
```

### Turn parallelization on/off
```python
# Just change one line:
USE_PARALLEL = False  # Serial mode
USE_PARALLEL = True   # Parallel mode
```

### Adjust process count
```python
# Auto-detect (recommended):
N_PROCESSES = cpu_count() - 1

# Fixed number:
N_PROCESSES = 4

# Maximum:
N_PROCESSES = cpu_count()
```

---

## ✅ Testing Checklist

After implementation, verify:

- [ ] Code runs without errors (serial mode)
- [ ] Code runs without errors (parallel mode)  
- [ ] Results are reasonable in both modes
- [ ] Parallel mode is faster (for pop_size >= 50)
- [ ] No crashes or hangs
- [ ] Works on Windows (needs `if __name__ == '__main__'`)

---

## 🐛 Common Issues & Quick Fixes

### Issue 1: "Can't pickle local object"
**Fix:** Make sure all functions are defined at module level (not nested)

### Issue 2: Windows - "freeze_support" error
**Fix:** Already handled by `if __name__ == '__main__':` guard

### Issue 3: No speedup or slower
**Fix:** Increase population size or set `N_PROCESSES = 4` (not auto)

### Issue 4: Results differ between runs
**Fix:** This is normal with parallelization (random seed issues). Results should be similar, not identical.

### Issue 5: Memory errors
**Fix:** Reduce `N_PROCESSES` to 2-4

---

## 📝 Implementation Time Estimate

| Task | Time |
|------|------|
| Setup (imports, config) | 30 min |
| Worker function | 1 hour |
| Batch evaluator | 1 hour |
| Modify initial population | 15 min |
| Modify crossover | 30 min |
| Main guard | 5 min |
| Testing | 30 min |
| **TOTAL** | **~4 hours** |

---

## 🎯 Success Criteria

After implementation, you should see:

✅ Code runs in both serial and parallel modes
✅ Parallel mode shows speedup (for population >= 50)
✅ No errors or crashes
✅ Results are reasonable

**That's it!** No complex decisions, no risk analysis, just straightforward parallelization.

---

## 💡 Optional Enhancements (Not Required)

If you want to add more later:

- Add command-line flag for `--parallel` / `--serial`
- Add `--processes N` to set process count
- Add progress bar for parallel evaluation
- Better fitness counter handling

But these are NOT needed for basic parallelization to work!

---

**Ready to implement?** Start with Part 1 and work through the checklist sequentially. Each part is independent and can be tested before moving to the next.
