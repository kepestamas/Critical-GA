# GA Parallelization - Quick Checklist

**Simple step-by-step checklist for adding parallelization to connectivity_ga.py**

**Total time: ~4 hours | Lines to add: ~80**

---

## ☑️ Step-by-Step Checklist

### ✅ Step 1: Add Imports (2 minutes)
At top of file, after existing imports:
```python
from multiprocessing import Pool, cpu_count
```

---

### ✅ Step 2: Add Configuration (2 minutes)
After global variable definitions (around line 70):
```python
# Parallelization settings
N_PROCESSES = cpu_count() - 1  # or set to 4
USE_PARALLEL = True
```

---

### ✅ Step 3: Add Helper Function (5 minutes)
Before `generate_pop()` function:
```python
def serialize_graph_data(graph):
    """Extract picklable data from graph."""
    return (list(graph.edges()), list(graph.nodes()))
```

---

### ✅ Step 4: Add Worker Function (15 minutes)
After helper function:
```python
def evaluate_individual_worker(args):
    """Worker function for parallel fitness evaluation."""
    individual, graph_edges, graph_nodes, payoff_func_name = args
    
    # Reconstruct graph
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

---

### ✅ Step 5: Add Batch Evaluator (20 minutes)
After worker function:
```python
def parallel_fitness_batch(individuals, graph_data, payoff_func_name):
    """Evaluate multiple individuals in parallel."""
    if not USE_PARALLEL or len(individuals) < 10:
        # Serial fallback
        results = []
        for ind in individuals:
            results.append((ind, fitness(ind)))
        return results
    
    # Prepare arguments
    graph_edges, graph_nodes = graph_data
    args = [(ind, graph_edges, graph_nodes, payoff_func_name) 
            for ind in individuals]
    
    # Parallel evaluation
    with Pool(processes=N_PROCESSES) as pool:
        results = pool.map(evaluate_individual_worker, args)
    
    # Update fitness counter (approximate)
    payoff_functions.fitness_count += len(individuals)
    
    return results
```

---

### ✅ Step 6: Modify `crossover_tournament()` (15 minutes)

**Find this function** (around line 265):
```python
def crossover_tournament(evaluated_population):
    print("Tournament")
    evaluated_child_population = []
    for _ in range(tournament_round_count):
        first_child, second_child = tournament_round(evaluated_population)
        evaluated_child_population.append((copy.deepcopy(first_child), fitness(first_child)))
        evaluated_child_population.append((copy.deepcopy(second_child), fitness(second_child)))
    return evaluated_child_population
```

**Replace with:**
```python
def crossover_tournament(evaluated_population, graph_data=None, payoff_func_name=None):
    print("Tournament")
    
    # Generate all children first
    children = []
    for _ in range(tournament_round_count):
        first_child, second_child = tournament_round(evaluated_population)
        children.extend([copy.deepcopy(first_child), copy.deepcopy(second_child)])
    
    # Parallel evaluation
    if USE_PARALLEL and graph_data is not None:
        evaluated_child_population = parallel_fitness_batch(
            children, graph_data, payoff_func_name
        )
    else:
        evaluated_child_population = [(child, fitness(child)) for child in children]
    
    return evaluated_child_population
```

---

### ✅ Step 7: Modify `ga()` Function - Initial Population (10 minutes)

**Find this code** (around line 285):
```python
def ga():
    print("Starting GA")
    population = generate_pop()
    evaluated_population = [(individual, fitness(individual)) for individual in population]
```

**Replace the evaluation line with:**
```python
def ga():
    print("Starting GA")
    population = generate_pop()
    
    # Serialize graph data once for parallel evaluation
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

---

### ✅ Step 8: Modify `ga()` Function - Crossover Call (5 minutes)

**Find this line** (inside the `for current_gen in range(gen_count):` loop):
```python
evaluated_child_population = crossover_tournament(evaluated_population)
```

**Replace with:**
```python
evaluated_child_population = crossover_tournament(
    evaluated_population, graph_data, payoff_function_name
)
```

---

### ✅ Step 9: Add Main Guard (2 minutes)

**Find the code at the bottom** of the file:
```python
print(list(G.nodes))
ga()
```

**Replace with:**
```python
if __name__ == '__main__':
    print(list(G.nodes))
    ga()
```

---

### ✅ Step 10: Test (30 minutes)

**Test 1 - Basic run:**
```bash
python connectivity_ga.py karate.txt test 0.1 0.05 50 3 0.8 0.05
```
✅ Should run without errors

**Test 2 - Verify speedup:**
```bash
# Time it
Measure-Command { python connectivity_ga.py karate.txt test 0.1 0.05 100 3 0.8 0.05 }
```
✅ Should be faster than before (for population >= 50)

**Test 3 - Serial mode (fallback test):**
Edit code temporarily:
```python
USE_PARALLEL = False
```
Run again, should work.

---

## 🎯 Quick Configuration Reference

### Enable/Disable Parallelization
```python
USE_PARALLEL = True   # Parallel mode
USE_PARALLEL = False  # Serial mode (for debugging)
```

### Adjust Process Count
```python
N_PROCESSES = cpu_count() - 1  # Auto (recommended)
N_PROCESSES = 4                # Fixed number
```

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| **Functions added** | 3 (serialize, worker, batch evaluator) |
| **Functions modified** | 2 (crossover_tournament, ga) |
| **Lines added** | ~80 |
| **Time required** | ~4 hours |
| **Expected speedup** | 2-6x (depending on cores and population) |

---

## ✅ Completion Checklist

Mark off as you complete each step:

- [ ] Step 1: Imports added
- [ ] Step 2: Configuration added
- [ ] Step 3: Helper function added
- [ ] Step 4: Worker function added
- [ ] Step 5: Batch evaluator added
- [ ] Step 6: `crossover_tournament()` modified
- [ ] Step 7: `ga()` initial population modified
- [ ] Step 8: `ga()` crossover call modified
- [ ] Step 9: Main guard added
- [ ] Step 10: Tested and working

---

## 🐛 Troubleshooting

**Error: "Can't pickle"**
→ All functions must be at module level (not nested)

**Error: Slower than before**
→ Try `N_PROCESSES = 4` instead of auto-detect

**Error: Different results**
→ Normal with parallelization, results should be similar not identical

**Error on Windows**
→ Make sure you added `if __name__ == '__main__':` guard

---

**That's it!** Follow the 10 steps in order and you're done.

**For full details:** See PARALLELIZATION_MINIMAL_PLAN.md
