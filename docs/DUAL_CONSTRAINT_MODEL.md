# Dual-Constraint Model Implementation

## Overview

The dual-constraint model enforces two simultaneous constraints on node removal:

1. **Count Constraint**: Exactly `k_nodes` nodes must be removed
2. **Weight Constraint**: Total weight of removed nodes must not exceed `k_weight_budget`

This approach provides more fine-grained control compared to previous single-constraint models (weight-only or count-only).

## Motivation

### Previous Approaches

**Count-Only Model** (original):
- Removes exactly k nodes
- Problem: In weighted graphs, may remove very heavy or very light nodes
- No control over total weight impact

**Weight-Only Model** (October 22, 2025):
- Removes nodes until total weight reaches target
- Problem: Variable number of nodes removed (could be 1 heavy node or many light nodes)
- Less predictable structural impact

### Dual-Constraint Model (October 28, 2025)

**Advantages**:
- **Predictable structure**: Always removes exactly k_nodes nodes
- **Weight control**: Total weight bounded by budget
- **Flexibility**: For unweighted graphs, equivalent to count-only (all weights = 1)
- **Challenge**: More restrictive - not all k_nodes combinations are valid

## Mathematical Formulation

Given graph G = (V, E) with node weights w(v):

### Parameters
- `node_fraction` ∈ [0,1]: Fraction of nodes determining count
- `weight_budget` ∈ [0,1]: Fraction of total weight determining budget
- Total weight: W = Σ w(v) for all v ∈ V

### Constraints
- **Count**: |S| = k_nodes where k_nodes = ⌊|V| × node_fraction⌋
- **Weight**: Σ w(s) ≤ k_weight_budget where k_weight_budget = ⌊W × weight_budget⌋ for s ∈ S

### Feasibility

A solution S is **feasible** if and only if:
1. |S| = k_nodes (exact count)
2. Σ w(s) ≤ k_weight_budget for s ∈ S (weight bound)
3. S ⊆ V (valid nodes)

**NP-Hard Subproblem**: Finding feasible solutions is related to the knapsack problem.

## Implementation Details

### Genetic Algorithm

#### Population Initialization

```python
def generate_one_pair():
    """Generate feasible solution with fallback strategy."""
    node_list = list(G.nodes)
    
    # Attempt random sampling (1000 tries)
    for _ in range(1000):
        nodes = random.sample(node_list, k_nodes)
        total_weight = sum(get_node_weight(node_weights, n) for n in nodes)
        
        if total_weight <= k_weight_budget:
            edges = random.sample(list(G.edges), k_edges)
            return (nodes, edges)
    
    # Fallback: select k_nodes lightest nodes
    sorted_nodes = sorted(node_list, key=lambda n: get_node_weight(node_weights, n))
    nodes = sorted_nodes[:k_nodes]
    edges = random.sample(list(G.edges), k_edges)
    return (nodes, edges)
```

**Fallback Strategy**: Ensures every generation produces valid solutions by selecting the k lightest nodes if random sampling fails.

#### Mutation

```python
def mutate(individual):
    """Replace one node maintaining both constraints."""
    new_individual = copy.deepcopy(individual)
    
    # Remove random node
    chosen_node = random.choice(new_individual[0])
    new_individual[0].remove(chosen_node)
    
    # Calculate remaining budget
    current_weight = sum(get_node_weight(node_weights, n) 
                        for n in new_individual[0])
    remaining_budget = k_weight_budget - current_weight
    
    # Find valid replacements
    candidates = [n for n in G.nodes 
                  if n not in new_individual[0] 
                  and get_node_weight(node_weights, n) <= remaining_budget]
    
    if candidates:
        new_node = random.choice(candidates)
        new_individual[0].append(new_node)
    else:
        # No valid replacement: keep original
        new_individual[0].append(chosen_node)
    
    return (new_individual, fitness(new_individual))
```

**Constraint Preservation**:
- Always maintains exactly k_nodes nodes
- Only accepts replacements within weight budget
- Fallback keeps original node if no valid replacement exists

#### Crossover

```python
def split_node_lists(united_node_list):
    """Distribute nodes to children respecting both constraints."""
    first_child_nodes = []
    second_child_nodes = []
    first_weight = 0
    second_weight = 0
    
    # Distribute nodes checking both constraints
    for node in united_node_list:
        node_weight = get_node_weight(node_weights, node)
        
        if (len(first_child_nodes) < k_nodes and 
            first_weight + node_weight <= k_weight_budget):
            first_child_nodes.append(node)
            first_weight += node_weight
        elif (len(second_child_nodes) < k_nodes and 
              second_weight + node_weight <= k_weight_budget):
            second_child_nodes.append(node)
            second_weight += node_weight
    
    # Fill with lightest nodes to reach k_nodes
    if len(first_child_nodes) < k_nodes:
        candidates = sorted([n for n in G.nodes if n not in first_child_nodes],
                          key=lambda n: get_node_weight(node_weights, n))
        for node in candidates:
            if len(first_child_nodes) >= k_nodes:
                break
            node_weight = get_node_weight(node_weights, node)
            if first_weight + node_weight <= k_weight_budget:
                first_child_nodes.append(node)
                first_weight += node_weight
    
    # Similar for second child...
    
    return first_child_nodes, second_child_nodes
```

**Features**:
- Distributes nodes based on available space and weight budget
- Fills with lightest nodes to guarantee exactly k_nodes
- Both children satisfy both constraints

### Greedy Algorithm

#### Configuration

```python
class Config:
    def __init__(self, G):
        self.G = G
        node_weights = get_node_weight_dict(G)
        total_node_weight = get_total_weight(node_weights)
        
        # Fixed: 5% nodes, 10% weight budget
        self.K1 = int(len(list(G.nodes)) * 0.05)
        self.K1_weight_budget = int(total_node_weight * 0.10)
        self.K2 = int(len(list(G.edges)) * 0.05)
```

**Design Choice**: Greedy uses fixed 5% node count and 10% weight budget, providing more weight budget than node percentage to accommodate variation in node weights.

#### Main Loop

```python
def CNEP1a_2_G1(config):
    S = []
    E = []
    H = config.G.copy()
    current_node_weight = 0
    
    while len(S) < config.K1 or len(E) < config.K2:
        [A, B] = best_nodes_edges_CNEP1A_Alg2(config, S, E, H, 
                                              current_node_weight, node_weights)
        
        z1 = select_random(A) if len(A) > 0 else config.NIL
        z2 = select_random(B) if len(B) > 0 else config.NIL
        
        # Decision logic checking both constraints
        if z1 != config.NIL:
            node_weight = get_node_weight(node_weights, z1)
            can_add = (len(S) < config.K1 and 
                      current_node_weight + node_weight <= config.K1_weight_budget)
            
            if can_add:
                S.append(z1)
                current_node_weight += node_weight
                H.remove_nodes_from([z1])
            # ... edge handling
        
        # Break if constraints cannot be satisfied
        if len(S) >= config.K1 and len(E) >= config.K2:
            break
    
    return [H, S, E]
```

#### Candidate Selection

```python
def best_nodes_edges_CNEP1A_Alg2(config, SN, SE, GG, current_node_weight, node_weights):
    selectedNodes = []
    
    if len(SN) < config.K1:
        for curr_node in nx.nodes(config.G):
            if curr_node not in SN:
                node_weight = get_node_weight(node_weights, curr_node)
                
                # Check weight budget
                if current_node_weight + node_weight <= config.K1_weight_budget:
                    # Evaluate this node
                    R = P.copy()
                    R.remove_nodes_from([curr_node])
                    node_f = node_f_orig - f_pairwise(nx.connected_components(R))
                    
                    if node_f < min_pw:
                        selectedNodes.clear()
                        selectedNodes.append(curr_node)
                        min_pw = node_f
                    elif node_f == min_pw:
                        selectedNodes.append(curr_node)
    
    return [selectedNodes, selectedEdges]
```

**Key**: Only evaluates nodes that would satisfy the weight budget if added.

## Command Line Interface

### Genetic Algorithm

```bash
python connectivity_ga.py <input> <run_id> <node_frac> <edge_frac> <weight_budget> \
                          <pop_size> <tournament_size> <p_cross> <p_mut> [payoff]
```

**Parameters**:
- `node_frac`: Determines k_nodes (count constraint)
- `weight_budget`: Determines k_weight_budget (weight constraint)

**Example**:
```bash
# Remove 5% nodes (count), max 10% total weight
python connectivity_ga.py karate.txt 1 0.05 0.03 0.10 50 3 0.8 0.05
```

### Greedy Algorithm

```bash
python connectivity_greedy.py <input> <run_id> [options] [payoff]
```

**Fixed constraints**: 5% nodes, 10% weight budget (hardcoded in Config class).

## Output Format

### Genetic Algorithm

**Filename**: `timing<run_id>_<input>_ke_<k_edges>_kn_<k_nodes>_wb_<weight_budget>`

**Example**: `timing1_karate.txt_ke_3_kn_2_wb_4`
- Removes 3 edges
- Removes 2 nodes (exact count)
- Weight budget: 4 (max total weight)

**Content**: Each line shows generation, evaluations, best fitness, and solution.

### Greedy Algorithm

**Filename**: `<run_id>_<input>`

**Content**:
```
Nodes removed: [node_list]
Edges removed: [edge_list]
MinVal achieved: <fitness_value>
```

## Parameter Tuning Guidelines

### Unweighted Graphs

For graphs where all nodes have weight 1:
- Set `weight_budget` ≥ `node_fraction` (e.g., 0.05 nodes → 0.10 weight budget)
- Larger budget provides more flexibility in node selection
- Budget = node_fraction gives tightest constraint (only k_nodes combinations work)

### Weighted Graphs

**Light variation** (weights differ by factor < 3):
- Set `weight_budget` = 1.5 × `node_fraction`
- Example: 0.05 nodes → 0.075 weight budget

**Heavy variation** (weights differ by factor > 3):
- Set `weight_budget` = 2-3 × `node_fraction`
- Example: 0.05 nodes → 0.10-0.15 weight budget
- Provides room to select heavier nodes

**Very heavy-tailed** (few very heavy nodes):
- Set `weight_budget` = 3-5 × `node_fraction`
- Example: 0.05 nodes → 0.15-0.25 weight budget

### Infeasibility Warning

If weight_budget < node_fraction × min_avg_weight, no feasible solutions may exist!

**Example**: 
- 100 nodes, all with weight ≥ 3
- node_fraction = 0.05 → k_nodes = 5
- Minimum total weight = 5 × 3 = 15
- Need weight_budget ≥ 0.15 (15% of total 100)

## Comparison with Previous Models

| Aspect | Count-Only | Weight-Only | Dual-Constraint |
|--------|-----------|-------------|-----------------|
| Node count | Fixed | Variable | **Fixed** |
| Total weight | Unbounded | Fixed | **Bounded** |
| Control | Structure only | Weight only | **Both** |
| Flexibility | High | High | **Medium** |
| Feasibility | Always | Always | **May require fallback** |
| Best for | Unweighted graphs | Weight-focused | **Weighted graphs with structure control** |

## Future Extensions

### Adaptive Budget

Automatically adjust weight_budget based on weight distribution:

```python
def adaptive_budget(G, node_fraction):
    weights = [get_node_weight(node_weights, n) for n in G.nodes]
    k_nodes = int(len(G.nodes) * node_fraction)
    
    # Sort and estimate: take average of k lightest nodes
    sorted_weights = sorted(weights)
    avg_light_weight = sum(sorted_weights[:k_nodes]) / k_nodes
    
    # Set budget at 1.5× average light weight
    total_weight = sum(weights)
    suggested_fraction = (avg_light_weight * k_nodes * 1.5) / total_weight
    
    return max(node_fraction, suggested_fraction)
```

### Soft Constraints

Allow weight budget violation with penalty:

```python
def fitness_with_penalty(individual):
    base_fitness = compute_connectivity_fitness(individual)
    
    total_weight = sum(get_node_weight(node_weights, n) for n in individual[0])
    if total_weight > k_weight_budget:
        penalty = (total_weight - k_weight_budget) * penalty_coefficient
        return base_fitness + penalty
    
    return base_fitness
```

### Multi-Objective Optimization

Treat count and weight as separate objectives:

```python
def pareto_dominates(sol1, sol2):
    """Check if sol1 Pareto-dominates sol2."""
    fitness1 = compute_connectivity_fitness(sol1)
    fitness2 = compute_connectivity_fitness(sol2)
    weight1 = sum(get_node_weight(node_weights, n) for n in sol1[0])
    weight2 = sum(get_node_weight(node_weights, n) for n in sol2[0])
    
    return (fitness1 <= fitness2 and weight1 <= weight2 and
            (fitness1 < fitness2 or weight1 < weight2))
```

## References

- Original CNDP: Count-only constraint (pre-October 2025)
- Weight-based removal: Weight-only constraint (October 22, 2025)
- Dual-constraint model: Count + weight constraints (October 28, 2025)

## Implementation Files

- `connectivity_ga.py`: Genetic algorithm with dual constraints
- `connectivity_greedy.py`: Greedy algorithm with dual constraints
- `graph_io.py`: Weight handling utilities (get_node_weight, get_total_weight)
- `payoff_functions.py`: Fitness functions (unchanged)

---

*Last updated: October 28, 2025*
