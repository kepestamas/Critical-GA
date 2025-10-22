# Weighted Graphs Integration Plan

**Date:** October 22, 2025  
**New Graph Types:** `cor_*`, `bog_*`, `mac_*`  
**Feature:** Vertex-weighted graphs with O(1) weight access

---

## File Format Analysis

### Format 1: `cor_*` and `bog_*` files (Adjacency List + Weights)

**Structure:**
```
<number_of_nodes>
<node_id>: <neighbor1> <neighbor2> ...
<node_id>: <neighbor1> <neighbor2> ...
...
<node_id>: <weight>
<node_id>: <weight>
...
```

**Example (cor_n050plai03.txt):**
```
50
0: 32 41 5 26 15 12
1: 3 17 37 33 27 29
...
0: 6
1: 4
...
49: 8
```

**Characteristics:**
- First line: number of nodes
- Next N lines: adjacency list (node: neighbors)
- Last N lines: weights (node: weight)
- Nodes are 0-indexed integers
- Weights are integers (typically 1-10)

### Format 2: `mac_*` files (Edge List + Weights)

**Structure:**
```
<number_of_nodes>
<number_of_edges>
<node1> <node2>
<node1> <node2>
...
<weight_node_0>
<weight_node_1>
...
```

**Example (mac_grafo10dens30.txt):**
```
10 
13 
8  3  
4  8  
...
83
86
77
...
```

**Characteristics:**
- First line: number of nodes
- Second line: number of edges
- Next M lines: edge list (space-separated pairs)
- Last N lines: weights (one per node, in order 0 to N-1)
- Weights are integers (can be larger, e.g., 15-93)

---

## Data Structure Design

### Node Weight Storage (O(1) Access)

**Global Dictionary:**
```python
node_weights = {}  # Key: node_id, Value: weight (int)
```

**Rationale:**
- O(1) lookup time using hash table
- Simple to serialize for multiprocessing
- Easy to integrate with existing code
- Minimal memory overhead

**Alternative Considered:**
- List/array indexed by node: Requires numeric node IDs in order
- NetworkX node attributes: Slower, harder to serialize
- **Decision:** Dictionary is most flexible and efficient

---

## Integration Checklist

### Part 1: Core Infrastructure (GA and Greedy)

#### ☐ 1.1 Update `read_graph()` function
**Files:** `connectivity_ga.py`, `connectivity_greedy.py`

**Changes:**
- Add detection for new file prefixes: `cor_`, `bog_`, `mac_`
- Parse adjacency list format (cor_, bog_)
- Parse edge list + count format (mac_)
- Extract weights section at end of file
- Populate `node_weights` dictionary
- **Return:** Tuple of (Graph, node_weights dict)

**Code Structure:**
```python
def read_graph(input, input_type):
    G = nx.Graph()
    node_weights = {}
    
    if sys.argv[1].startswith(('cor_', 'bog_')):
        # Parse format 1
        # ...
        return G, node_weights
    elif sys.argv[1].startswith('mac_'):
        # Parse format 2
        # ...
        return G, node_weights
    else:
        # Existing formats (unweighted)
        return G, None
```

#### ☐ 1.2 Create global `node_weights` variable
**Files:** `connectivity_ga.py`, `connectivity_greedy.py`

**Changes:**
```python
# After graph reading
G, node_weights = read_graph(input, input_type)
if node_weights is None:
    node_weights = {}  # Empty dict for unweighted graphs
```

#### ☐ 1.3 Add weight serialization for multiprocessing
**File:** `connectivity_ga.py`

**Changes:**
- Add `node_weights` to serialized data in `serialize_graph_data()`
```python
def serialize_graph_data(graph):
    """Extract picklable data from graph."""
    return (list(graph.edges()), list(graph.nodes()), node_weights)
```

- Update `evaluate_individual_worker()` to receive weights
```python
def evaluate_individual_worker(args):
    individual, graph_edges, graph_nodes, weights, payoff_func_name = args
    # Store weights globally in worker
    global node_weights
    node_weights = weights
    # ... rest of function
```

- Update `parallel_fitness_batch()` to pass weights
```python
def parallel_fitness_batch(individuals, graph_data, payoff_func_name):
    graph_edges, graph_nodes, weights = graph_data
    args = [(ind, graph_edges, graph_nodes, weights, payoff_func_name) 
            for ind in individuals]
```

---

### Part 2: Weight-Aware Selection (Future Use)

#### ☐ 2.1 Add weight accessor function
**Files:** `connectivity_ga.py`, `connectivity_greedy.py`

**Purpose:** Centralized, O(1) weight access

```python
def get_node_weight(node_id):
    """
    Get weight of a node. O(1) operation.
    Returns 1 if node is unweighted.
    """
    return node_weights.get(node_id, 1)

def get_total_weight(nodes):
    """
    Get total weight of a list of nodes. O(n) operation.
    """
    return sum(get_node_weight(node) for node in nodes)
```

#### ☐ 2.2 Document weight usage patterns
**File:** Create `WEIGHTED_SELECTION_PATTERNS.md`

**Content:**
- How to use weights in node selection (GA)
- How to use weights in greedy selection
- Probability-based selection proportional to weight
- Priority-based selection (high weight = high priority)

---

### Part 3: Testing

#### ☐ 3.1 Basic file reading tests

**Test files:**
- `cor_n050plai03.txt` (smallest cor_)
- `bog_60_p0.1_1.txt` (smallest bog_)
- `mac_grafo10dens30.txt` (smallest mac_)

**Test commands:**
```bash
# GA tests
python connectivity_ga.py cor_n050plai03.txt test 0.1 0.05 20 3 0.8 0.05
python connectivity_ga.py bog_60_p0.1_1.txt test 0.1 0.05 20 3 0.8 0.05
python connectivity_ga.py mac_grafo10dens30.txt test 0.1 0.05 10 3 0.8 0.05

# Greedy tests
python connectivity_greedy.py cor_n050plai03.txt test
python connectivity_greedy.py bog_60_p0.1_1.txt test
python connectivity_greedy.py mac_grafo10dens30.txt test
```

**Validation:**
- Verify graph loaded correctly (node count, edge count)
- Verify weights loaded (print sample weights)
- Verify algorithms run without errors
- Verify multiprocessing works with weight serialization

#### ☐ 3.2 Weight access tests

**Add debug output:**
```python
# Print sample weights after loading
print(f"Sample weights: {list(node_weights.items())[:10]}")
print(f"Total nodes with weights: {len(node_weights)}")
print(f"Weight range: {min(node_weights.values())} - {max(node_weights.values())}")
```

#### ☐ 3.3 Large graph tests

**Test with larger graphs:**
- `cor_n350plai05.txt` (350 nodes)
- `bog_300_p0.4_5.txt` (300 nodes)
- `mac_grafo30dens70.txt` (30 nodes)

---

### Part 4: Documentation

#### ☐ 4.1 Update DATASETS.md
**File:** `docs/DATASETS.md`

**Add section:**
```markdown
## Weighted Graphs

### cor_* (Correlation Networks)
- Format: Adjacency list + weights
- Sizes: 50, 100, 150, 200, 250, 300, 350 nodes
- Weight range: 1-10
- Naming: cor_n<size>plai<param>.txt

### bog_* (Bogotá Networks)
- Format: Adjacency list + weights
- Sizes: 60, 100, 150, 200, 250, 300 nodes
- Parameters: density (p0.1-p0.4), instance (1-5)
- Weight range: 1-10
- Naming: bog_<size>_p<density>_<instance>.txt

### mac_* (MAC Networks)
- Format: Edge list + weights
- Sizes: 10, 15, 20, 30 nodes
- Densities: 30%, 50%, 70%
- Weight range: 15-100 (larger values)
- Naming: mac_grafo<size>dens<density>.txt
```

#### ☐ 4.2 Create WEIGHTED_GRAPHS_API.md
**File:** `docs/WEIGHTED_GRAPHS_API.md`

**Content:**
- How to access node weights in code
- Weight accessor functions
- Integration with fitness evaluation
- Future use in selection algorithms

---

## Implementation Order

### Phase 1: Core Reading (2-3 hours)
1. Update `read_graph()` in `connectivity_ga.py`
2. Update `read_graph()` in `connectivity_greedy.py`
3. Create global `node_weights` variable in both files
4. Add weight accessor functions
5. Basic testing with small files

### Phase 2: Multiprocessing Integration (1-2 hours)
6. Update serialization functions
7. Update worker functions
8. Update batch evaluator
9. Test parallelization with weights

### Phase 3: Testing & Validation (1 hour)
10. Test all file formats
11. Verify weight loading
12. Test with all payoff functions
13. Verify multiprocessing works

### Phase 4: Documentation (1 hour)
14. Update DATASETS.md
15. Create WEIGHTED_GRAPHS_API.md
16. Add usage examples
17. Update README if needed

**Total Estimated Time:** 5-7 hours

---

## Backward Compatibility

✅ **Existing unweighted graphs:**
- Return `None` for node_weights
- Convert to empty dict `{}`
- Default weight = 1 for all nodes
- No changes to existing behavior

✅ **Existing algorithms:**
- No changes required initially
- Weights available but not mandatory
- Can be integrated gradually

---

## Future Enhancements (Not in This Phase)

### Weight-Based Selection in GA
- Modify `generate_one_pair()` to prefer high-weight nodes
- Weighted random sampling in node selection
- Priority queue based on weights

### Weight-Based Selection in Greedy
- Modify selection to consider weights
- Weighted importance scoring
- Multi-criteria optimization (connectivity + weight)

### Weight-Aware Payoff Functions
- New payoff functions that consider weights
- Weighted connectivity measures
- Weighted component sizes

---

## Risk Assessment

### Low Risk
✅ Reading formats - straightforward parsing
✅ Dictionary storage - standard Python, fast
✅ Backward compatibility - isolated changes

### Medium Risk
⚠️ Multiprocessing serialization - need to test thoroughly
⚠️ File format variations - might need edge case handling

### Mitigation
- Test with smallest files first
- Add validation for weight counts vs node counts
- Add error handling for malformed files
- Print diagnostics during development

---

## Success Criteria

✅ All three file formats load correctly
✅ Node weights accessible in O(1) time
✅ Multiprocessing works with weights
✅ No regression in existing functionality
✅ All algorithms run on new graphs
✅ Documentation complete

---

**Status:** Ready for Implementation  
**Priority:** High (enables new research datasets)  
**Complexity:** Medium (well-defined scope)
