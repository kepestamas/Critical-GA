# Algorithm Removal Analysis: Node and Edge Deletion in CNDP Algorithms

## Executive Summary

Both the **Genetic Algorithm (GA)** and **Greedy Algorithm** implementations solve the Critical Network Disruption Problem (CNDP) by removing **k nodes** and **l edges** (where k = k_nodes and l = k_edges) from the input graph. However, they employ fundamentally different strategies:

- **GA**: Removes all k nodes and l edges **simultaneously** in each solution evaluation
- **Greedy**: Removes nodes and edges **iteratively**, one element at a time, over k+l steps

This document provides a detailed analysis of how each algorithm handles node and edge removal.

---

## 1. Problem Parameters

### Budget Constraints

Both algorithms work with the same budget constraints:

```python
# Genetic Algorithm (connectivity_ga.py, lines 31-33)
k_nodes = int(len(list(G.nodes)) * float(sys.argv[3]))  # number of nodes to remove
k_edges = int(len(list(G.edges)) * float(sys.argv[4]))  # number of edges to remove

# Greedy Algorithm (connectivity_greedy.py, lines 82-83)
self.K1 = int(len(list(self.G.nodes)) * 0.05)  # number of nodes to remove (5%)
self.K2 = int(len(list(self.G.edges)) * 0.03)  # number of edges to remove (3%)
```

**Key Observations:**
- **GA**: Budget specified as fractions (command-line arguments)
- **Greedy**: Budget hardcoded (5% nodes, 3% edges) in current implementation
- Both calculate k_nodes and k_edges based on graph size
- Total budget: K = k_nodes + k_edges elements to remove

---

## 2. Genetic Algorithm: Simultaneous Removal Strategy

### 2.1 Individual Representation

Each GA individual represents a **complete solution**:

```python
individual = (nodes_to_remove, edges_to_remove)
```

Where:
- `nodes_to_remove`: List containing exactly k_nodes node IDs
- `edges_to_remove`: List containing exactly k_edges edge tuples

**Example:**
```python
individual = (['1', '5', '12'], [('2', '3'), ('7', '9')])
# Removes 3 nodes and 2 edges simultaneously
```

### 2.2 Solution Generation

**Initial Population (lines 135-145):**
```python
def generate_one_pair():
    node_list = list(G.nodes)
    nodes = random.sample(node_list, k_nodes)  # Select k_nodes randomly
    
    edge_list = list(G.edges)
    edges = random.sample(edge_list, k_edges)  # Select k_edges randomly
    
    return (nodes, edges)
```

**Characteristics:**
- Generates complete solutions in one step
- Uses `random.sample()` → no duplicates within each list
- Each individual is a **full-budget solution** (uses all k nodes and l edges)

### 2.3 Fitness Evaluation: Batch Removal

**Serial Fitness Function (lines 148-158):**
```python
def fitness(individual):
    P : nx.Graph = copy.deepcopy(G)
    P.remove_nodes_from(individual[0])  # Remove all k nodes at once
    P.remove_edges_from(individual[1])  # Remove all l edges at once
    result = payoff_function(nx.connected_components(P))
    return result
```

**Parallel Worker Function (lines 97-106):**
```python
def evaluate_individual_worker(args):
    # Reconstruct graph
    G_worker = nx.Graph()
    G_worker.add_nodes_from(graph_nodes)
    G_worker.add_edges_from(graph_edges)
    
    # Remove all nodes and edges simultaneously
    G_worker.remove_nodes_from(individual[0])  # Batch removal of k nodes
    G_worker.remove_edges_from(individual[1])  # Batch removal of l edges
    
    # Calculate fitness on resulting graph
    payoff_func = get_payoff_function(payoff_func_name)
    result = payoff_func(nx.connected_components(G_worker))
    return (individual, result)
```

**Key Points:**
- **Simultaneous removal**: All k+l elements removed in two operations
- **NetworkX semantics**: 
  - `remove_nodes_from()` also removes all incident edges automatically
  - `remove_edges_from()` only removes specified edges
- **Order matters**: Nodes removed first (important because node removal cascades to edges)
- **Result**: One fitness evaluation per individual per generation

### 2.4 Crossover: Combining Solutions

**Tournament Crossover (lines 295-305):**
```python
def tournament_round(evaluated_population):
    current_contenders = random.sample(evaluated_population, tournament_size)
    current_contenders = find_min_from_contenders(current_contenders)
    
    # Combine two parent solutions
    united_node_list = current_contenders[0][0][0] + current_contenders[1][0][0]
    first_child_nodes, second_child_nodes = split_node_lists(united_node_list)
    
    united_edge_list = current_contenders[0][0][1] + current_contenders[1][0][1]
    first_child_edges, second_child_edges = split_edge_lists(united_edge_list)
    
    return [(first_child_nodes, first_child_edges),
            (second_child_nodes, second_child_edges)]
```

**Split Logic (lines 240-265):**
```python
def split_node_lists(united_node_list):
    first_child_nodes = []
    second_child_nodes = []
    random.shuffle(united_node_list)
    
    # Elements in both parents go to both children
    for node in united_node_list:
        if united_node_list.count(node) == 2:
            first_child_nodes.append(node)
            second_child_nodes.append(node)
            while node in united_node_list:
                united_node_list.remove(node)
    
    # Split remaining elements
    for node in united_node_list: 
        if not node in first_child_nodes and len(first_child_nodes) < k_nodes:
            first_child_nodes.append(node)
        elif not node in second_child_nodes:
            second_child_nodes.append(node)
    
    return first_child_nodes, second_child_nodes
```

**Crossover Properties:**
- Maintains solution size (k nodes, l edges)
- Preserves common elements from both parents
- Randomly distributes unique elements
- Children are immediately valid full-budget solutions

### 2.5 Mutation: Element Replacement

**Descending Mutation (lines 202-224):**
```python
def descending_mutation(individual):
    global mutation_count
    new_individual = individual[0]
    
    for _ in range(mutation_count):
        if (float(sys.argv[3]) != 0 and random.random() <= 0.5) or float(sys.argv[4]) == 0:
            # Mutate node list
            chosen_node = random.choice(new_individual[0])
            new_individual[0].remove(chosen_node)
            new_node = random.choice(list(G.nodes))
            while new_node in new_individual[0]:
                new_node = random.choice(list(G.nodes))
            new_individual[0].append(new_node)
        else:
            # Mutate edge list
            chosen_edge = random.choice(new_individual[1])
            new_individual[1].remove(chosen_edge)
            new_edge = random.choice(list(G.edges))
            while new_edge in new_individual[1]:
                new_edge = random.choice(list(G.edges))
            new_individual[1].append(new_edge)
    
    return (new_individual, fitness(new_individual))
```

**Mutation Characteristics:**
- Replaces elements rather than adding/removing
- Maintains constant solution size (k nodes, l edges)
- Multiple mutations per operation (mutation_count)
- Adaptive: `mutation_count = max(int(((k_nodes + k_edges)/4)*alfa), 1)`
- Ensures no duplicates (while loop)

### 2.6 GA Summary: Removal Pattern

| **Aspect** | **Details** |
|-----------|-------------|
| **Removal Strategy** | Simultaneous (all k+l elements at once) |
| **When Removal Occurs** | Every fitness evaluation |
| **Frequency** | pop_size × gen_count evaluations |
| **Node Removal** | `G.remove_nodes_from(k_nodes_list)` |
| **Edge Removal** | `G.remove_edges_from(k_edges_list)` |
| **Order** | Nodes first, then edges |
| **Side Effects** | Node removal auto-removes incident edges |
| **Evaluation Cost** | O(k + l) per removal, O(V + E) per fitness |

---

## 3. Greedy Algorithm: Iterative Removal Strategy

### 3.1 Main Loop Structure

**CNEP1a_2_G1 Algorithm (lines 191-232):**
```python
def CNEP1a_2_G1(config):
    S = []  # Nodes removed so far
    E = []  # Edges removed so far
    H = config.G.copy()  # Working copy of graph
    
    while len(S) + len(E) < config.K:  # K = K1 + K2 = total budget
        # Find best candidates
        [A, B] = best_nodes_edges_CNEP1A_Alg2(config, S, E, H)
        
        z1 = z2 = config.NIL
        if len(A) > 0:
            z1 = select_random(A)  # Random best node
        if len(B) > 0:
            z2 = select_random(B)  # Random best edge
        
        # Decide what to remove (node vs edge)
        if (z1 != config.NIL):
            if (z2 != config.NIL):
                if random.randint(0, 1) == 1:
                    S.append(z1)
                    H.remove_nodes_from([z1])  # Remove one node
                else:
                    E.append(z2)
                    H.remove_edges_from([z2])  # Remove one edge
            else:
                S.append(z1)
                H.remove_nodes_from([z1])
        else:
            E.append(z2)
            H.remove_edges_from([z2])
    
    return [H, S, E]
```

**Key Observations:**
- **Iterative process**: Loops K1 + K2 times
- **One element per iteration**: Removes either one node OR one edge
- **In-place modification**: Working graph H is modified incrementally
- **Budget tracking**: Stops when |S| + |E| = K

### 3.2 Candidate Selection

**best_nodes_edges_CNEP1A_Alg2 (lines 140-188):**
```python
def best_nodes_edges_CNEP1A_Alg2(config, SN, SE, GG):
    selectedEdges = []
    selectedNodes = []
    min_pw = config.INF
    
    # Create temporary graph with already-removed elements
    P = GG.copy()
    P.remove_nodes_from(SN)
    P.remove_edges_from(SE)
    node_f_orig = fitness(nx.connected_components(P))
    
    SG2 = nx.edges(config.G)
    SG1 = nx.nodes(config.G)
    
    # Evaluate all candidate nodes (if budget allows)
    if len(SN) < config.K1:
        for curr_node in SG1:
            R = P.copy()
            R.remove_nodes_from([curr_node])  # Try removing this node
            node_f = node_f_orig - fitness(nx.connected_components(R))
            
            if node_f < min_pw:
                selectedNodes.clear()
                selectedNodes.append(curr_node)
                min_pw = node_f
            elif node_f == min_pw:
                selectedNodes.append(curr_node)
    
    # Evaluate all candidate edges (if budget allows)
    if len(SE) < config.K2:
        for curr_edge in SG2:
            R = P.copy()
            R.remove_edges_from([curr_edge])  # Try removing this edge
            node_f = node_f_orig - fitness(nx.connected_components(R))
            
            if node_f < min_pw:
                selectedEdges.clear()
                selectedEdges.append(curr_edge)
                min_pw = node_f
            elif node_f == min_pw:
                selectedEdges.append(curr_edge)
    
    return [selectedNodes, selectedEdges]
```

**Evaluation Strategy:**
- **Exhaustive search**: Tests every remaining node and edge
- **Greedy criterion**: Selects element with maximum connectivity reduction
- **Delta evaluation**: Computes fitness change (node_f_orig - new_fitness)
- **Tie handling**: Keeps all elements with same best score
- **Computational cost**: O(V + E) evaluations per iteration

### 3.3 Iterative Removal Process

**Step-by-Step Example:**

```
Initial: G = (V={1,2,3,4,5}, E={(1,2),(2,3),(3,4),(4,5)})
Budget: K1=2 nodes, K2=1 edge, K=3 total

Iteration 1:
  - Evaluate all nodes: {1,2,3,4,5}
  - Evaluate all edges: {(1,2),(2,3),(3,4),(4,5)}
  - Best: Node 3 (breaks chain)
  - Remove: H.remove_nodes_from([3])
  - State: S=[3], E=[], |S|+|E|=1 < 3

Iteration 2:
  - Evaluate remaining nodes: {1,2,4,5}
  - Evaluate remaining edges: {(1,2),(4,5)} [note: (2,3),(3,4) gone with node 3]
  - Best: Edge (1,2)
  - Remove: H.remove_edges_from([(1,2)])
  - State: S=[3], E=[(1,2)], |S|+|E|=2 < 3

Iteration 3:
  - Evaluate remaining nodes: {1,2,4,5}
  - Evaluate remaining edges: {(4,5)}
  - Best: Node 4
  - Remove: H.remove_nodes_from([4])
  - State: S=[3,4], E=[(1,2)], |S|+|E|=3 = K

Stop: Budget exhausted
Result: 3 nodes {1,2,5} remain, isolated
```

### 3.4 Greedy Summary: Removal Pattern

| **Aspect** | **Details** |
|-----------|-------------|
| **Removal Strategy** | Iterative (one element per step) |
| **When Removal Occurs** | Once per main loop iteration |
| **Frequency** | K = K1 + K2 iterations total |
| **Node Removal** | `H.remove_nodes_from([single_node])` |
| **Edge Removal** | `H.remove_edges_from([single_edge])` |
| **Order** | Dynamic (best element chosen each time) |
| **Side Effects** | Node removal auto-removes incident edges |
| **Evaluation Cost** | O((V + E) × K) total evaluations |

---

## 4. Comparative Analysis

### 4.1 Removal Strategies

| **Characteristic** | **Genetic Algorithm** | **Greedy Algorithm** |
|-------------------|----------------------|---------------------|
| **Elements per removal** | k + l (all at once) | 1 (one at a time) |
| **Removal operations** | 2 per evaluation (nodes, then edges) | k + l total (1 per iteration) |
| **Graph modification** | Temporary (copy of G each time) | Incremental (working copy H) |
| **Total removals** | pop_size × gen_count × 2 operations | k + l operations |
| **Order** | Fixed (nodes first) | Adaptive (best first) |
| **Interdependencies** | Independent (each solution isolated) | Dependent (previous removals affect next choice) |

### 4.2 Computational Complexity

**Genetic Algorithm:**
```
Per generation:
  - Fitness evaluations: O(pop_size × (V + E))
  - Removals: 2 × pop_size (nodes + edges)
  
Total over run:
  - Evaluations: O(gen_count × pop_size × (V + E))
  - Typical: 5000 gens × 100 pop × (1000 nodes) = 500M operations
```

**Greedy Algorithm:**
```
Per iteration:
  - Candidate evaluations: O(V + E) tests
  - One removal: O(1)
  
Total over run:
  - Evaluations: O(K × (V + E))
  - Typical: 50 iterations × (V + E) evaluations
  - Much fewer evaluations than GA
```

### 4.3 Search Space Exploration

**Genetic Algorithm:**
- **Space size**: C(V, k) × C(E, l) ≈ (V!/(k!(V-k)!)) × (E!/(l!(E-l)!))
- **Coverage**: Explores pop_size × gen_count solutions
- **Strategy**: Population-based stochastic search
- **Optimality**: No guarantee, but good solutions found
- **Diversity**: Crossover promotes exploration

**Greedy Algorithm:**
- **Space size**: (V + E) × (V + E - 1) × ... × (V + E - K + 1) ≈ (V+E)^K
- **Coverage**: Explores one path (O(K × (V+E)) evaluations)
- **Strategy**: Greedy hill climbing
- **Optimality**: No guarantee (local optimum)
- **Diversity**: None (deterministic given random tie-breaking)

### 4.4 Solution Quality

**Genetic Algorithm Advantages:**
- Can escape local optima (through mutation)
- Explores diverse solution regions (through crossover)
- Benefits from population diversity
- Better for complex landscapes

**Greedy Algorithm Advantages:**
- Faster convergence (fewer evaluations)
- Guaranteed improvement each step
- Deterministic behavior (given seed)
- Better for smooth landscapes

### 4.5 Parallelization

**Genetic Algorithm:**
- **Parallel fitness evaluation** (lines 109-133)
- **Parallelizable**: Multiple individuals evaluated independently
- **Speedup**: Near-linear with CPU count
- **Current**: Uses multiprocessing.Pool with N_PROCESSES workers

**Greedy Algorithm:**
- **Parallel iteration execution** (lines 246-256)
- **Parallelizable**: Multiple independent runs
- **Speedup**: Linear with run count
- **Current**: Uses multiprocessing.Pool for multiple runs
- **Note**: Single run inherently sequential (each step depends on previous)

---

## 5. Node Removal Cascade Effects

### 5.1 NetworkX Semantics

Both algorithms rely on NetworkX's `remove_nodes_from()` behavior:

```python
G.remove_nodes_from(node_list)
```

**Automatic cascade:**
1. Removes specified nodes from graph
2. **Automatically removes all incident edges**
3. Updates adjacency structure

**Implication:**
- Removing k nodes can remove **more than k × degree(v)** edges
- Edge budget operates on **remaining edges** after node removals
- Order matters: nodes removed before edges in GA

### 5.2 Effective Budget

**Genetic Algorithm:**
```python
P.remove_nodes_from(individual[0])  # Removes k nodes + incident edges
P.remove_edges_from(individual[1])  # Removes l additional edges
```
- Total edges removed: incident_edges(k nodes) + l
- Edge budget applies to edges not removed by node deletions

**Greedy Algorithm:**
```python
if removing_node:
    H.remove_nodes_from([z1])  # Removes 1 node + incident edges
else:
    H.remove_edges_from([z2])  # Removes 1 edge
```
- Edge count decreases with each node removal
- Subsequent iterations see reduced edge set
- Edge budget tracked separately from node budget

### 5.3 Budget Interaction Example

```
Initial graph: 10 nodes, 20 edges
Budget: k=2 nodes, l=3 edges

Scenario 1 - GA approach (simultaneous):
  1. Remove 2 nodes (say, high-degree nodes with 5 edges each)
     → 8 nodes remain
     → ≤10 edges remain (removed 10+ edges)
  2. Remove 3 additional edges
     → Final: ≤7 edges remain
  Total removed: 2 nodes + 13+ edges

Scenario 2 - Greedy approach (iterative):
  Step 1: Remove node A (degree 5)
    → 9 nodes, ≤15 edges remain
  Step 2: Remove edge (B,C)
    → 9 nodes, ≤14 edges remain
  Step 3: Remove node D (degree 4)
    → 8 nodes, ≤10 edges remain
  Step 4: Remove edge (E,F)
    → 8 nodes, ≤9 edges remain
  Step 5: Remove edge (G,H)
    → 8 nodes, ≤8 edges remain
  Total removed: 2 nodes + 11+ edges
```

---

## 6. Algorithm Selection Guidelines

### 6.1 When to Use Genetic Algorithm

**Best for:**
- Complex, multimodal fitness landscapes
- When solution quality is priority over speed
- Problems where local optima are prevalent
- Large search spaces requiring exploration
- When parallel hardware is available

**Characteristics:**
- Higher computational cost
- Better solution quality (typically)
- More parameter tuning required
- Stochastic results (multiple runs advised)

### 6.2 When to Use Greedy Algorithm

**Best for:**
- Quick approximations needed
- Smooth, convex fitness landscapes
- Time-constrained scenarios
- Benchmarking or baseline comparisons
- When deterministic behavior desired

**Characteristics:**
- Lower computational cost
- Faster convergence
- Simpler implementation
- Deterministic results (given seed)
- Risk of local optima

### 6.3 Hybrid Approaches (Future Work)

**Potential combinations:**
1. **Greedy initialization for GA**: Use greedy solution as seed
2. **GA-guided greedy**: Use GA to identify good regions, refine with greedy
3. **Adaptive switching**: Start greedy, switch to GA if stuck
4. **Ensemble methods**: Run both, take best result

---

## 7. Implementation Details

### 7.1 Code Locations

**Genetic Algorithm (`connectivity_ga.py`):**
- Budget setup: Lines 31-33
- Individual generation: Lines 135-145
- Fitness evaluation: Lines 148-158
- Parallel evaluation: Lines 87-106
- Removal operations: Lines 100-101 (worker), 151-152 (serial)
- Crossover: Lines 295-305
- Mutation: Lines 202-224

**Greedy Algorithm (`connectivity_greedy.py`):**
- Budget setup: Lines 82-83
- Main loop: Lines 191-232
- Candidate evaluation: Lines 140-188
- Removal operations: Lines 214-230
- Single-element removal: One operation per iteration

### 7.2 Key Differences in Implementation

| **Aspect** | **GA** | **Greedy** |
|-----------|--------|-----------|
| **Graph copying** | `copy.deepcopy(G)` per evaluation | `G.copy()` once, then `H.copy()` per candidate |
| **Removal method** | Batch lists | Single-element lists |
| **Fitness calls** | Pop_size × gen_count | K × (V + E) |
| **Memory** | O(pop_size × K) | O(K) |
| **State** | Stateless (each individual independent) | Stateful (H modified incrementally) |

---

## 8. Conclusions

### 8.1 Key Findings

1. **Removal Paradigms:**
   - GA: "Select k+l, remove all, evaluate" (simultaneous)
   - Greedy: "While budget remains: find best, remove one" (iterative)

2. **Computational Trade-offs:**
   - GA: More evaluations, better exploration
   - Greedy: Fewer evaluations, faster convergence

3. **Solution Quality:**
   - GA: Typically better (but not guaranteed)
   - Greedy: Good approximations, faster

4. **Budget Interpretation:**
   - Both respect k_nodes and k_edges constraints
   - Both leverage NetworkX's automatic edge removal on node deletion
   - Effective edge removal often exceeds specified budget due to cascading

### 8.2 Algorithmic Insights

**Genetic Algorithm:**
- Treats (node set, edge set) as atomic solution
- Explores solution space through recombination
- Removal is part of fitness evaluation, not search strategy
- Population maintains diversity

**Greedy Algorithm:**
- Builds solution incrementally
- Removal sequence is the solution itself
- Each removal affects subsequent choices
- Single trajectory through search space

### 8.3 Practical Recommendations

1. **For quick experiments**: Use Greedy
2. **For best results**: Use GA with sufficient generations
3. **For large graphs**: Start with Greedy, optionally refine with GA
4. **For parameter tuning**: Use Greedy for initial exploration
5. **For publication-quality results**: Use GA with multiple runs

---

## 9. Future Research Directions

### 9.1 Algorithm Improvements

1. **Adaptive strategies:**
   - Dynamic budget allocation (node vs edge priority)
   - Hybrid removal strategies

2. **Enhanced greedy:**
   - Lookahead (remove next k elements, not just 1)
   - Beam search (maintain top-k partial solutions)

3. **GA enhancements:**
   - Better initialization (seeded with greedy solutions)
   - Local search refinement (memetic algorithm)

### 9.2 Theoretical Analysis

1. **Approximation guarantees:**
   - Worst-case analysis for greedy
   - Convergence proofs for GA

2. **Landscape characterization:**
   - Fitness landscape analysis
   - Problem difficulty metrics

3. **Budget optimization:**
   - Optimal k_nodes vs k_edges ratio
   - Diminishing returns analysis

---

## Appendix: Pseudo-Code Comparison

### A.1 Genetic Algorithm Pseudo-Code

```
GA-CNDP(G, k_nodes, k_edges, pop_size, gen_count):
    population = INITIALIZE-POPULATION(G, k_nodes, k_edges, pop_size)
    
    for generation = 1 to gen_count:
        # Evaluate all individuals
        evaluated_pop = []
        for individual in population:
            fitness = EVALUATE(G, individual)
            evaluated_pop.append((individual, fitness))
        
        # Selection and reproduction
        new_population = []
        for _ in range(pop_size // 2):
            # Tournament selection
            parent1 = TOURNAMENT-SELECT(evaluated_pop)
            parent2 = TOURNAMENT-SELECT(evaluated_pop)
            
            # Crossover
            child1, child2 = CROSSOVER(parent1, parent2)
            
            # Mutation
            if RANDOM() < mutation_prob:
                child1 = MUTATE(child1)
            if RANDOM() < mutation_prob:
                child2 = MUTATE(child2)
            
            new_population.extend([child1, child2])
        
        population = new_population
    
    return BEST-INDIVIDUAL(evaluated_pop)


EVALUATE(G, individual):
    P = COPY(G)
    P.REMOVE-NODES(individual.nodes)  # Removes k nodes + incident edges
    P.REMOVE-EDGES(individual.edges)  # Removes l edges
    return PAYOFF-FUNCTION(CONNECTED-COMPONENTS(P))
```

### A.2 Greedy Algorithm Pseudo-Code

```
GREEDY-CNDP(G, k_nodes, k_edges):
    S = []  # Removed nodes
    E = []  # Removed edges
    H = COPY(G)
    K = k_nodes + k_edges
    
    while |S| + |E| < K:
        # Find best candidates
        best_nodes = []
        best_edges = []
        min_delta = INFINITY
        
        # Evaluate all candidate nodes (if budget allows)
        if |S| < k_nodes:
            for node in H.NODES():
                H_temp = COPY(H)
                H_temp.REMOVE-NODE(node)
                delta = FITNESS(H) - FITNESS(H_temp)
                
                if delta < min_delta:
                    best_nodes = [node]
                    min_delta = delta
                elif delta == min_delta:
                    best_nodes.append(node)
        
        # Evaluate all candidate edges (if budget allows)
        if |E| < k_edges:
            for edge in H.EDGES():
                H_temp = COPY(H)
                H_temp.REMOVE-EDGE(edge)
                delta = FITNESS(H) - FITNESS(H_temp)
                
                if delta < min_delta:
                    best_edges = [edge]
                    min_delta = delta
                elif delta == min_delta:
                    best_edges.append(edge)
        
        # Select and remove best element
        if best_nodes AND best_edges:
            if RANDOM() < 0.5:
                chosen = RANDOM-CHOICE(best_nodes)
                S.append(chosen)
                H.REMOVE-NODE(chosen)
            else:
                chosen = RANDOM-CHOICE(best_edges)
                E.append(chosen)
                H.REMOVE-EDGE(chosen)
        elif best_nodes:
            chosen = RANDOM-CHOICE(best_nodes)
            S.append(chosen)
            H.REMOVE-NODE(chosen)
        else:
            chosen = RANDOM-CHOICE(best_edges)
            E.append(chosen)
            H.REMOVE-EDGE(chosen)
    
    return (H, S, E)
```

---

**Document Version:** 1.0  
**Date:** October 22, 2025  
**Author:** Analysis based on Critical-GA implementation  
**References:** `connectivity_ga.py`, `connectivity_greedy.py`, `README.md`, `docs/ALGORITHMS.md`
