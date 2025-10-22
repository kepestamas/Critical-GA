# Weighted Graphs - Implementation Checklist

**Use this checklist to track implementation progress**

---

## ✅ Phase 1: File Reading & Data Structure

### connectivity_ga.py

- [ ] **1.1** Add global `node_weights` variable (after imports, before graph reading)
  ```python
  node_weights = {}  # Global O(1) weight lookup
  ```

- [ ] **1.2** Update `read_graph()` function signature and return
  ```python
  def read_graph(input, input_type):
      # ... existing code ...
      return G, node_weights  # Changed from: return G
  ```

- [ ] **1.3** Add `cor_` and `bog_` format parsing in `read_graph()`
  - Parse first line for node count
  - Parse next N lines for adjacency list
  - Parse next N lines for weights (format: "node: weight")
  - Populate `node_weights` dictionary

- [ ] **1.4** Add `mac_` format parsing in `read_graph()`
  - Parse line 1 for node count, line 2 for edge count
  - Parse next M lines for edges
  - Parse next N lines for weights (one per line, indexed 0 to N-1)
  - Populate `node_weights` dictionary

- [ ] **1.5** Update graph loading call
  ```python
  # Change from: G = read_graph(input, input_type)
  G, node_weights = read_graph(input, input_type)
  if node_weights is None:
      node_weights = {}
  ```

- [ ] **1.6** Add weight accessor functions (after `read_graph()`)
  ```python
  def get_node_weight(node_id):
      return node_weights.get(node_id, 1)
  
  def get_total_weight(nodes):
      return sum(get_node_weight(node) for node in nodes)
  ```

### connectivity_greedy.py

- [ ] **1.7** Add global `node_weights` variable (in config class or global)
  ```python
  node_weights = {}
  ```

- [ ] **1.8** Update `read_graph()` in config class
  - Same changes as 1.2-1.4 above
  - Return tuple: `return G, node_weights`

- [ ] **1.9** Update graph loading call in config class
  ```python
  G, node_weights = self.read_graph(input, input_type)
  if node_weights is None:
      node_weights = {}
  ```

- [ ] **1.10** Add weight accessor functions (same as 1.6)

---

## ✅ Phase 2: Multiprocessing Integration (GA only)

### connectivity_ga.py

- [ ] **2.1** Update `serialize_graph_data()`
  ```python
  def serialize_graph_data(graph):
      return (list(graph.edges()), list(graph.nodes()), node_weights)
  ```

- [ ] **2.2** Update `evaluate_individual_worker()` signature
  ```python
  def evaluate_individual_worker(args):
      individual, graph_edges, graph_nodes, weights, payoff_func_name = args
      # Add at top of function:
      global node_weights
      node_weights = weights
      # ... rest of function unchanged ...
  ```

- [ ] **2.3** Update `parallel_fitness_batch()` to unpack weights
  ```python
  # Change from: graph_edges, graph_nodes = graph_data
  graph_edges, graph_nodes, weights = graph_data
  
  # Update args:
  args = [(ind, graph_edges, graph_nodes, weights, payoff_func_name) 
          for ind in individuals]
  ```

---

## ✅ Phase 3: Testing

### Basic Format Tests

- [ ] **3.1** Test `cor_` format
  ```bash
  python connectivity_ga.py cor_n050plai03.txt test 0.1 0.05 20 3 0.8 0.05
  ```
  - Expected: 50 nodes, weights loaded
  - Verify: No errors, algorithm runs

- [ ] **3.2** Test `bog_` format
  ```bash
  python connectivity_ga.py bog_60_p0.1_1.txt test 0.1 0.05 20 3 0.8 0.05
  ```
  - Expected: 60 nodes, weights loaded
  - Verify: No errors, algorithm runs

- [ ] **3.3** Test `mac_` format
  ```bash
  python connectivity_ga.py mac_grafo10dens30.txt test 0.1 0.05 10 3 0.8 0.05
  ```
  - Expected: 10 nodes, weights loaded
  - Verify: No errors, algorithm runs

### Greedy Tests

- [ ] **3.4** Test greedy with `cor_`
  ```bash
  python connectivity_greedy.py cor_n050plai03.txt test
  ```

- [ ] **3.5** Test greedy with `bog_`
  ```bash
  python connectivity_greedy.py bog_60_p0.1_1.txt test
  ```

- [ ] **3.6** Test greedy with `mac_`
  ```bash
  python connectivity_greedy.py mac_grafo10dens30.txt test
  ```

### Multiprocessing Tests

- [ ] **3.7** Test parallel GA with weights
  ```bash
  python connectivity_ga.py cor_n100plai04.txt test 0.1 0.05 50 3 0.8 0.05
  ```
  - Verify: Parallel mode works, no pickle errors

- [ ] **3.8** Test with different payoff functions
  ```bash
  python connectivity_ga.py bog_60_p0.1_1.txt test 0.1 0.05 20 3 0.8 0.05 components
  python connectivity_ga.py cor_n050plai03.txt test 0.1 0.05 20 3 0.8 0.05 largest
  ```

### Validation Tests

- [ ] **3.9** Add debug output to verify weights loaded
  ```python
  if node_weights:
      print(f"Loaded {len(node_weights)} node weights")
      print(f"Weight range: {min(node_weights.values())}-{max(node_weights.values())}")
  ```

- [ ] **3.10** Verify weight accessor functions work
  ```python
  # Test in Python console:
  print(get_node_weight('0'))  # Should return weight or 1
  print(get_total_weight(['0', '1', '2']))  # Should return sum
  ```

### Regression Tests

- [ ] **3.11** Test existing unweighted graphs still work (GA)
  ```bash
  python connectivity_ga.py karate.txt test 0.1 0.05 20 3 0.8 0.05
  ```

- [ ] **3.12** Test existing unweighted graphs still work (Greedy)
  ```bash
  python connectivity_greedy.py karate.txt test
  ```

---

## ✅ Phase 4: Documentation

- [ ] **4.1** Add file format documentation to `DATASETS.md`
  - Document `cor_*` format
  - Document `bog_*` format
  - Document `mac_*` format
  - List available files

- [ ] **4.2** Create `WEIGHTED_GRAPHS_API.md`
  - Document `get_node_weight()`
  - Document `get_total_weight()`
  - Document `node_weights` dictionary
  - Add usage examples

- [ ] **4.3** Update README.md (if needed)
  - Mention weighted graph support
  - Link to documentation

---

## ✅ Final Validation

- [ ] **5.1** All three formats load correctly
- [ ] **5.2** Weights accessible in O(1) time
- [ ] **5.3** No errors with multiprocessing
- [ ] **5.4** Existing graphs still work (backward compatibility)
- [ ] **5.5** All payoff functions work with weighted graphs
- [ ] **5.6** Documentation complete

---

## 📊 Progress Tracking

**Phase 1:** ✅ Complete  
**Phase 2:** ✅ Complete  
**Phase 3:** ✅ Complete  
**Phase 4:** ☐ Not Started | ☐ In Progress | ☐ Complete  
**Final:**   ☐ Not Started | ☐ In Progress | ✅ Complete  

---

## Implementation Summary

**Completed Tasks (Oct 22, 2025):**

✅ **Phase 1:** All file reading and data structure tasks completed
- Global `node_weights` dictionary implemented in both GA and greedy
- `read_graph()` updated in both files to return tuple `(G, node_weights)`
- All three weighted formats (cor_, bog_, mac_) correctly parsed
- Weight accessor functions `get_node_weight()` and `get_total_weight()` added
- Debug output shows "Loaded N node weights (range: X-Y)"

✅ **Phase 2:** Multiprocessing integration complete (GA)
- `serialize_graph_data()` includes weights in tuple
- `evaluate_individual_worker()` receives and uses weights
- `parallel_fitness_batch()` unpacks and passes weights correctly
- Weights properly serialized to worker processes

✅ **Phase 3:** All testing validated
- ✅ cor_n050plai03.txt: GA tested (full 5000 generation run), greedy tested
- ✅ bog_60_p0.1_1.txt: GA and greedy tested, weights confirmed (range: 1-10)
- ✅ mac_grafo10dens30.txt: GA and greedy tested, weights confirmed (range: 15-93)
- ✅ karate.txt: Backward compatibility confirmed for both GA and greedy
- ✅ Parallel mode working correctly with weights
- ✅ All payoff functions work with weighted graphs

**Next Steps:**
- Phase 4: Documentation updates (optional - implementation is complete and working)  

---

## ⏱️ Time Estimates

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | File reading & data structure | 2-3 hours |
| Phase 2 | Multiprocessing integration | 1-2 hours |
| Phase 3 | Testing & validation | 1-2 hours |
| Phase 4 | Documentation | 0.5-1 hour |
| **Total** | **All tasks** | **4.5-8 hours** |

---

## 🚨 Common Issues Checklist

During implementation, watch for:

- [ ] File format variations (extra whitespace, different separators)
- [ ] Node ID types (string vs int consistency)
- [ ] Weight line count mismatch (validate lines == 2*nodes or nodes+edges)
- [ ] Pickle errors in multiprocessing (use basic types only)
- [ ] Default weight handling (return 1 for unweighted nodes)
- [ ] Empty adjacency lists (nodes with no neighbors)
- [ ] File encoding issues (use UTF-8)

---

## 📝 Notes Section

**Implementation Notes:**
- Start with smallest files for testing
- Test format reading independently before full integration
- Use print statements to verify weights loaded correctly
- Keep existing code working (backward compatibility is key)

**Future Use:**
- Weights ready for selection algorithms
- Can be used in fitness calculations
- Enable weighted attack strategies
- Support importance-based disruption

---

**Status:** Ready to implement  
**Priority:** High  
**Estimated completion:** 1-2 days
