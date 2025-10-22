# Weighted Graphs - Quick Implementation Guide

## File Formats Summary

| Prefix | Format | Node Count | Weight Range | Example |
|--------|--------|------------|--------------|---------|
| `cor_` | Adj list + weights | 50-350 | 1-10 | `cor_n050plai03.txt` |
| `bog_` | Adj list + weights | 60-300 | 1-10 | `bog_60_p0.1_1.txt` |
| `mac_` | Edge list + weights | 10-30 | 15-100 | `mac_grafo10dens30.txt` |

---

## Data Structure

```python
# Global O(1) weight lookup
node_weights = {}  # {node_id: weight}

def get_node_weight(node_id):
    """O(1) weight access. Returns 1 for unweighted nodes."""
    return node_weights.get(node_id, 1)
```

---

## Implementation Checklist

### 1️⃣ Update `read_graph()` - Both Files ⏱️ 1-2 hours

**Location:** `connectivity_ga.py` and `connectivity_greedy.py`

**Pseudocode:**
```python
def read_graph(input, input_type):
    G = nx.Graph()
    node_weights = {}
    filename = sys.argv[1]
    
    if filename.startswith(('cor_', 'bog_')):
        # Format: adjacency list + weights
        lines = f.readlines()
        n = int(lines[0].strip())
        
        # Parse edges (lines 1 to n)
        for i in range(1, n + 1):
            parts = lines[i].split(':')
            node = parts[0].strip()
            neighbors = parts[1].strip().split()
            for neighbor in neighbors:
                G.add_edge(node, neighbor)
        
        # Parse weights (lines n+1 to 2n)
        for i in range(n + 1, 2*n + 1):
            parts = lines[i].split(':')
            node = parts[0].strip()
            weight = int(parts[1].strip())
            node_weights[node] = weight
    
    elif filename.startswith('mac_'):
        # Format: edge list + weights
        lines = f.readlines()
        n = int(lines[0].strip())
        m = int(lines[1].strip())
        
        # Parse edges (lines 2 to m+1)
        for i in range(2, m + 2):
            parts = lines[i].strip().split()
            G.add_edge(parts[0], parts[1])
        
        # Parse weights (lines m+2 to m+n+1)
        for i in range(m + 2, m + n + 2):
            weight = int(lines[i].strip())
            node_weights[str(i - m - 2)] = weight
    
    else:
        # Existing formats (unweighted)
        # ... existing code ...
        return G, None
    
    return G, node_weights
```

**Integration:**
```python
# Update graph loading
G, node_weights = read_graph(input, input_type)
if node_weights is None:
    node_weights = {}
```

---

### 2️⃣ Update Multiprocessing - GA Only ⏱️ 1 hour

**File:** `connectivity_ga.py`

**Step A: Update serialization**
```python
def serialize_graph_data(graph):
    """Extract picklable data from graph."""
    return (list(graph.edges()), list(graph.nodes()), node_weights)
```

**Step B: Update worker**
```python
def evaluate_individual_worker(args):
    individual, graph_edges, graph_nodes, weights, payoff_func_name = args
    
    # Make weights accessible in worker
    global node_weights
    node_weights = weights
    
    # Reconstruct and evaluate
    G_worker = nx.Graph()
    G_worker.add_nodes_from(graph_nodes)
    G_worker.add_edges_from(graph_edges)
    G_worker.remove_nodes_from(individual[0])
    G_worker.remove_edges_from(individual[1])
    
    payoff_func = get_payoff_function(payoff_func_name)
    result = payoff_func(nx.connected_components(G_worker))
    
    return (individual, result)
```

**Step C: Update batch function**
```python
def parallel_fitness_batch(individuals, graph_data, payoff_func_name):
    global PARALLEL_POOL
    
    if not USE_PARALLEL or len(individuals) < 10:
        results = []
        for ind in individuals:
            results.append((ind, fitness(ind)))
        return results
    
    if PARALLEL_POOL is None:
        PARALLEL_POOL = Pool(processes=N_PROCESSES)
    
    # Unpack graph data including weights
    graph_edges, graph_nodes, weights = graph_data
    args = [(ind, graph_edges, graph_nodes, weights, payoff_func_name) 
            for ind in individuals]
    
    results = PARALLEL_POOL.map(evaluate_individual_worker, args)
    payoff_functions.fitness_count += len(individuals)
    
    return results
```

---

### 3️⃣ Add Weight Accessors ⏱️ 15 minutes

**Both Files:** `connectivity_ga.py` and `connectivity_greedy.py`

```python
def get_node_weight(node_id):
    """
    Get weight of a node. O(1) operation.
    Returns 1 if node is unweighted (default weight).
    
    Args:
        node_id: Node identifier (string or int)
    
    Returns:
        int: Weight of the node
    """
    return node_weights.get(node_id, 1)

def get_total_weight(nodes):
    """
    Get total weight of a list of nodes. O(n) operation.
    
    Args:
        nodes: List of node identifiers
    
    Returns:
        int: Sum of weights
    """
    return sum(get_node_weight(node) for node in nodes)
```

---

### 4️⃣ Add sys.argv Detection ⏱️ 10 minutes

**Update file detection lists:**

**Before:**
```python
if sys.argv[1] in ["BarabasiAlbert_n500m1.txt", ...]:
```

**After:**
```python
# Or use prefix detection
if sys.argv[1].startswith(('cor_', 'bog_')):
    # New format
elif sys.argv[1].startswith('mac_'):
    # New format
elif sys.argv[1] in ["BarabasiAlbert_n500m1.txt", ...]:
    # Existing format
```

---

## Testing Commands

### Quick Tests (Small Files)
```bash
# Test cor_ format
python connectivity_ga.py cor_n050plai03.txt test 0.1 0.05 20 3 0.8 0.05

# Test bog_ format  
python connectivity_ga.py bog_60_p0.1_1.txt test 0.1 0.05 20 3 0.8 0.05

# Test mac_ format
python connectivity_ga.py mac_grafo10dens30.txt test 0.1 0.05 10 3 0.8 0.05

# Test greedy
python connectivity_greedy.py cor_n050plai03.txt test
python connectivity_greedy.py bog_60_p0.1_1.txt test
python connectivity_greedy.py mac_grafo10dens30.txt test
```

### Validation Tests
```bash
# Larger graphs
python connectivity_ga.py cor_n100plai04.txt test 0.1 0.05 50 3 0.8 0.05
python connectivity_ga.py bog_100_p0.1_1.txt test 0.1 0.05 50 3 0.8 0.05

# Different payoff functions
python connectivity_ga.py cor_n050plai03.txt test 0.1 0.05 20 3 0.8 0.05 components
python connectivity_ga.py bog_60_p0.1_1.txt test 0.1 0.05 20 3 0.8 0.05 largest
```

---

## Debug Output Template

```python
# Add after reading graph
if node_weights:
    print(f"✓ Loaded {len(node_weights)} node weights")
    print(f"  Weight range: {min(node_weights.values())} - {max(node_weights.values())}")
    print(f"  Sample weights: {dict(list(node_weights.items())[:5])}")
else:
    print("✓ Loaded unweighted graph")
```

---

## Common Issues & Solutions

### Issue 1: Index Out of Range
**Symptom:** Error when parsing weights  
**Cause:** File has fewer lines than expected  
**Solution:** Add validation
```python
if len(lines) < 2*n + 1:
    raise ValueError(f"Expected {2*n+1} lines, got {len(lines)}")
```

### Issue 2: Weight Not Found
**Symptom:** KeyError in get_node_weight  
**Solution:** Use `.get()` with default
```python
return node_weights.get(node_id, 1)  # Default weight = 1
```

### Issue 3: Multiprocessing Pickle Error
**Symptom:** Can't pickle node_weights  
**Solution:** Ensure weights are basic types (dict of int/str)
```python
# Weights should be: {str: int} or {int: int}
node_weights = {str(k): int(v) for k, v in node_weights.items()}
```

---

## Files to Modify

| File | Changes | Lines | Time |
|------|---------|-------|------|
| `connectivity_ga.py` | read_graph, serialization, worker | ~100 | 2h |
| `connectivity_greedy.py` | read_graph | ~50 | 1h |

**Total:** ~150 lines, 3-4 hours

---

## Next Steps After Implementation

1. ✅ Test all three formats load correctly
2. ✅ Verify weights accessible via `get_node_weight()`
3. ✅ Confirm multiprocessing works
4. ✅ Run full GA on small weighted graphs
5. 📝 Document usage in DATASETS.md
6. 🚀 Ready for weight-based selection algorithms

---

**Quick Start:** Begin with `read_graph()` updates, test with smallest files, then add multiprocessing support.
