# Algorithm Details

## Problem Formulation

### Critical Network Disruption Problem (CNDP)

The Critical Network Disruption Problem is a combinatorial optimization problem that seeks to minimize network connectivity by strategically removing a limited number of network elements.

#### Mathematical Formulation

**Given:**
- Undirected graph G = (V, E) where V is the vertex set and E is the edge set
- Node weights: w(v) for each v ∈ V (default w(v) = 1 for unweighted graphs)
- Total node weight: W = Σ w(v) for all v ∈ V
- Node constraints:
  - k_nodes: Exact number of nodes to remove
  - k_weight_budget: Maximum total weight of removed nodes
- Edge constraint: k_edges (maximum edges to remove)

**Decision Variables:**
- S ⊆ V: Set of nodes to remove, |S| = k_nodes and Σ w(s) ≤ k_weight_budget for s ∈ S
- T ⊆ E: Set of edges to remove, |T| ≤ k_edges

**Dual-Constraint Model:**
Solutions must satisfy BOTH:
1. **Count constraint**: Exactly k_nodes nodes must be removed
2. **Weight constraint**: Total weight Σ w(s) for s ∈ S must not exceed k_weight_budget

This is more restrictive than previous approaches where only one constraint was active.

**Objective Functions:**
Three different optimization objectives are available for the disrupted graph G' = (V\S, E\T):

1. **Pairwise Connectivity** (default):
   ```
   f₁(S,T) = Σ |Cᵢ| × (|Cᵢ| - 1) / 2
   ```
   
2. **Number of Components**:
   ```
   f₂(S,T) = -|{C₁, C₂, ..., Cₙ}|
   ```
   (Negative for minimization objective)
   
3. **Largest Component Size**:
   ```
   f₃(S,T) = max{|C₁|, |C₂|, ..., |Cₙ|}
   ```

Where {C₁, C₂, ..., Cₙ} are the connected components of G'.

**Constraints:**
- |S| = k_nodes (exact count)
- Σ w(s) ≤ k_weight_budget for s ∈ S (weight budget)
- |T| ≤ k_edges
- S ⊆ V
- T ⊆ E

#### Problem Complexity

The CNDP is NP-hard, as it generalizes several known NP-hard problems:
- **Node Connectivity**: Finding minimum vertex cut
- **Edge Connectivity**: Finding minimum edge cut
- **Graph Partitioning**: Optimal graph bisection
- **Knapsack Problem**: Selecting k_nodes items with total weight ≤ k_weight_budget

The dual-constraint model is particularly challenging as it combines:
- Exact count requirement (must select exactly k_nodes nodes)
- Knapsack-like weight constraint (total weight ≤ budget)
- Connectivity optimization objective

The problem space grows exponentially: O(C(|V|,k_nodes) × C(|E|,k_edges)) possible combinations, with additional weight constraint filtering.

## Genetic Algorithm Implementation

### Overview

The Genetic Algorithm (GA) is a metaheuristic inspired by natural evolution. It maintains a population of candidate solutions and iteratively improves them through selection, crossover, and mutation operations.

### Representation

Each individual in the population represents a solution as:
```python
individual = (nodes_to_remove, edges_to_remove)
```

Where:
- `nodes_to_remove`: List of k₁ node identifiers
- `edges_to_remove`: List of k₂ edge tuples

### Population Initialization

```python
def generate_pop():
    population = []
    for _ in range(pop_size):
        population.append(generate_one_pair())
    return population

def generate_one_pair():
    """Generate a valid solution satisfying both count and weight constraints."""
    node_list = list(G.nodes)
    
    # Try random sampling up to 1000 times
    for _ in range(1000):
        nodes = random.sample(node_list, k_nodes)
        total_weight = sum(get_node_weight(node_weights, n) for n in nodes)
        
        if total_weight <= k_weight_budget:
            # Valid solution found
            edges = random.sample(list(G.edges), k_edges)
            return (nodes, edges)
    
    # Fallback: select k_nodes lightest nodes
    sorted_nodes = sorted(node_list, key=lambda n: get_node_weight(node_weights, n))
    nodes = sorted_nodes[:k_nodes]
    edges = random.sample(list(G.edges), k_edges)
    return (nodes, edges)
```

**Characteristics:**
- Ensures exact k_nodes count
- Respects weight budget constraint
- Uses random sampling with fallback to guarantee feasibility
- Fallback strategy: selects k lightest nodes if random sampling fails
- Uniform distribution over feasible search space

### Fitness Evaluation

The fitness function supports multiple objectives through configurable payoff functions:

```python
from payoff_functions import PAYOFF_FUNCTIONS

def fitness(individual):
    P = copy.deepcopy(G)
    P.remove_nodes_from(individual[0])
    P.remove_edges_from(individual[1])
    result = payoff_function(nx.connected_components(P))
    return result
```

**Payoff Function Implementations:**

1. **Pairwise Connectivity** (default):
   ```python
   def pairwise_connectivity(components):
       return sum([len(c)*(len(c)-1)/2 if len(c)>1 else 0 for c in components])
   ```

2. **Number of Components**:
   ```python
   def number_of_components(components):
       return -len(list(components))  # Negative for minimization
   ```

3. **Largest Component Size**:
   ```python
   def largest_component_size(components):
       return max([len(c) for c in components], default=0)
   ```

**Properties:**
- All functions designed for minimization (lower fitness = better solution)
- Configurable via command-line parameter
- Consistent interface: Iterator[Set] → float
- Computationally expensive: O(V + E) per evaluation

### Selection: Tournament Selection

Tournament selection is used for parent selection:

```python
def find_min_from_contenders(contenders):
    min_val1, min_val2 = float('inf'), float('inf')
    min1, min2 = None, None
    for contender in contenders:
        if contender[1] < min_val2:
            min2 = copy.deepcopy(min1)
            min_val2 = min_val1
            min1 = copy.deepcopy(contender)
            min_val1 = contender[1]
    return [min1, min2]
```

**Algorithm:**
1. Randomly select `tournament_size` individuals
2. Choose the two best (lowest fitness)
3. Return selected parents for crossover

**Advantages:**
- Maintains selection pressure
- Preserves diversity
- Computationally efficient: O(tournament_size)

### Crossover: Union-Based Crossover

The crossover operator combines genetic material from two parents while respecting both count and weight constraints:

```python
def split_node_lists(united_node_list):
    """Distribute nodes to two children respecting k_nodes count and weight budget."""
    first_child_nodes = []
    second_child_nodes = []
    first_weight = 0
    second_weight = 0
    random.shuffle(united_node_list)
    
    # Handle common elements (present in both parents)
    for node in united_node_list:
        if united_node_list.count(node) == 2:
            node_weight = get_node_weight(node_weights, node)
            # Add to both if both have space and budget
            if (len(first_child_nodes) < k_nodes and first_weight + node_weight <= k_weight_budget and
                len(second_child_nodes) < k_nodes and second_weight + node_weight <= k_weight_budget):
                first_child_nodes.append(node)
                second_child_nodes.append(node)
                first_weight += node_weight
                second_weight += node_weight
            while node in united_node_list:
                united_node_list.remove(node)
    
    # Distribute unique elements
    for node in united_node_list:
        node_weight = get_node_weight(node_weights, node)
        
        if (len(first_child_nodes) < k_nodes and first_weight + node_weight <= k_weight_budget
            and node not in first_child_nodes):
            first_child_nodes.append(node)
            first_weight += node_weight
        elif (len(second_child_nodes) < k_nodes and second_weight + node_weight <= k_weight_budget
              and node not in second_child_nodes):
            second_child_nodes.append(node)
            second_weight += node_weight
    
    # Fill with lightest nodes if needed to reach k_nodes
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
    
    # Similar filling for second child...
    
    return first_child_nodes, second_child_nodes
```

**Process:**
1. Unite parent solutions: S₁ ∪ S₂ and T₁ ∪ T₂
2. Common elements go to both children (if constraints allow)
3. Unique elements distributed based on available space and weight budget
4. Fill with lightest nodes to reach exactly k_nodes
5. Ensure both count and weight constraints are satisfied

**Properties:**
- Preserves good building blocks
- Maintains feasibility (exact count + weight budget)
- Introduces controlled randomness
- Fallback strategy ensures valid offspring

### Mutation: Descending Mutation

Two mutation strategies are implemented, both respecting the dual-constraint model:

#### Standard Mutation
```python
def mutate(individual):
    """Replace one node while maintaining count and weight constraints."""
    new_individual = copy.deepcopy(individual)
    
    if random.random() <= 0.5:  # 50% chance to mutate nodes vs edges
        # Remove a random node
        chosen_node = random.choice(new_individual[0])
        new_individual[0].remove(chosen_node)
        
        # Calculate remaining weight budget
        current_weight = sum(get_node_weight(node_weights, n) for n in new_individual[0])
        removed_weight = get_node_weight(node_weights, chosen_node)
        remaining_budget = k_weight_budget - current_weight
        
        # Find valid replacement (within budget)
        candidates = [n for n in G.nodes if n not in new_individual[0]
                      and get_node_weight(node_weights, n) <= remaining_budget]
        
        if candidates:
            new_node = random.choice(candidates)
            new_individual[0].append(new_node)
        else:
            # No valid replacement: keep original node
            new_individual[0].append(chosen_node)
    else:
        # Replace random edge (no weight constraint on edges)
        chosen_edge = random.choice(new_individual[1])
        new_individual[1].remove(chosen_edge)
        new_edge = random.choice(list(G.edges))
        while new_edge in new_individual[1]:
            new_edge = random.choice(list(G.edges))
        new_individual[1].append(new_edge)
    
    return (new_individual, fitness(new_individual))
```

**Mutation Constraints:**
- Maintains exactly k_nodes count
- Ensures total weight ≤ k_weight_budget
- Fallback: keeps original node if no valid replacement exists

#### Descending Mutation (Advanced)
```python
def actualize_mutation_count(current_gen, max_gen):
    global mutation_count
    half_gen = int(max_gen / 2)
    alfa = (half_gen - current_gen) / half_gen
    mutation_count = max(int(((k_nodes + k_edges)/4)*alfa), 1)

def descending_mutation(individual):
    """Apply multiple mutations with decreasing intensity."""
    global mutation_count
    new_individual = copy.deepcopy(individual)
    
    for _ in range(mutation_count):
        new_individual = mutate((new_individual, 0))[0]
    
    return (new_individual, fitness(new_individual))
```

**Key Features:**
- Mutation intensity decreases over generations
- High exploration early, exploitation later
- Prevents premature convergence
- Each mutation respects dual constraints

### Population Management

```python
def selection(evaluated_population):
    new_evaluated_population = evaluated_population.copy()
    new_evaluated_population = sorted(new_evaluated_population, key=get_second)
    new_evaluated_population = new_evaluated_population[0:pop_size]
    return new_evaluated_population
```

**Strategy:**
- Combine parents and offspring
- Sort by fitness (elitism)
- Keep best `pop_size` individuals
- Ensures non-decreasing best fitness

### Main GA Loop

```python
def ga():
    population = generate_pop()
    evaluated_population = [(individual, fitness(individual)) for individual in population]
    
    for current_gen in range(gen_count):
        # Crossover
        evaluated_child_population = crossover_tournament(evaluated_population)
        
        # Mutation
        actualize_mutation_count(current_gen, gen_count)
        if random.random() < mutation_chance:
            original_individual = random.choice(evaluated_child_population)
            mutating_individual = descending_mutation(original_individual)
            evaluated_child_population.remove(original_individual)
            evaluated_child_population.append(mutating_individual)
        
        # Selection
        evaluated_population = evaluated_population + evaluated_child_population
        evaluated_population = selection(evaluated_population)
        
        # Logging
        print(f"{current_gen} {fitness_count}")
        print(f"{current_gen} {average_connectivity(evaluated_population)}")
```

## Greedy Algorithm Implementation

### Overview

The greedy algorithm uses a constructive approach with dual constraints, iteratively selecting the single best removal at each step while respecting both node count and weight budget.

### Configuration

```python
class Config:
    def __init__(self, G):
        self.G = G
        node_weights = get_node_weight_dict(G)
        total_node_weight = get_total_weight(node_weights)
        
        # Dual-constraint model
        self.K1 = int(len(list(G.nodes)) * 0.05)  # 5% of nodes (fixed count)
        self.K1_weight_budget = int(total_node_weight * 0.10)  # 10% of weight (constraint)
        self.K2 = int(len(list(G.edges)) * 0.05)  # 5% of edges
        self.K = self.K1 + self.K2  # Total budget (count-based)
```

### Algorithm Structure

```python
def CNEP1a_2_G1(config):
    S = []  # Selected nodes
    E = []  # Selected edges
    H = config.G.copy()
    current_node_weight = 0
    node_weights = get_node_weight_dict(config.G)
    
    # Loop until count constraint reached
    while len(S) < config.K1 or len(E) < config.K2:
        # Find best candidates respecting weight budget
        [A, B] = best_nodes_edges_CNEP1A_Alg2(config, S, E, H, current_node_weight, node_weights)
        
        # Select best node or edge
        z1 = select_random(A) if len(A) > 0 else config.NIL
        z2 = select_random(B) if len(B) > 0 else config.NIL
        
        # Make decision based on constraints
        if z1 != config.NIL:
            node_weight = get_node_weight(node_weights, z1)
            if z2 != config.NIL:
                # Both available: check constraints
                can_add_node = (len(S) < config.K1 and 
                              current_node_weight + node_weight <= config.K1_weight_budget)
                can_add_edge = len(E) < config.K2
                
                if can_add_node and can_add_edge:
                    if random.randint(0, 1) == 1:
                        S.append(z1)
                        current_node_weight += node_weight
                        H.remove_nodes_from([z1])
                    else:
                        E.append(z2)
                        H.remove_edges_from([z2])
                elif can_add_node:
                    S.append(z1)
                    current_node_weight += node_weight
                    H.remove_nodes_from([z1])
                elif can_add_edge:
                    E.append(z2)
                    H.remove_edges_from([z2])
                else:
                    break  # Both budgets exceeded
            else:
                # Only node available
                if (len(S) < config.K1 and 
                    current_node_weight + node_weight <= config.K1_weight_budget):
                    S.append(z1)
                    current_node_weight += node_weight
                    H.remove_nodes_from([z1])
                else:
                    break
        else:
            # Only edge available
            if len(E) < config.K2:
                E.append(z2)
                H.remove_edges_from([z2])
            else:
                break
    
    return [H, S, E]
```

**Key Features:**
- Tracks current node weight to enforce budget
- Checks both count (K1) and weight (K1_weight_budget) before adding nodes
- Terminates when either constraint cannot be satisfied
- Fixed 5% node count, 10% weight budget

### Best Element Selection

The greedy algorithm now supports configurable payoff functions:

```python
from payoff_functions import PAYOFF_FUNCTIONS

# Global payoff function set via command line
payoff_function = PAYOFF_FUNCTIONS.get(payoff_name, 
                                     PAYOFF_FUNCTIONS['pairwise'])

def best_nodes_edges_CNEP1A_Alg2(config, SN, SE, GG):
    selectedEdges = []
    selectedNodes = []
    min_pw = config.INF
    
    P = GG.copy()
    P.remove_nodes_from(SN)
    P.remove_edges_from(SE)
    node_f_orig = f_pairwise(nx.connected_components(P))
    
    # Evaluate all possible node removals respecting weight budget
    if len(SN) < config.K1:
        for curr_node in nx.nodes(config.G):
            if curr_node not in SN:
                node_weight = get_node_weight(node_weights, curr_node)
                
                # Check weight budget constraint
                if current_node_weight + node_weight <= config.K1_weight_budget:
                    R = P.copy()
                    R.remove_nodes_from([curr_node])
                    node_f = node_f_orig - f_pairwise(nx.connected_components(R))
                    
                    if node_f < min_pw:
                        selectedNodes.clear()
                        selectedNodes.append(curr_node)
                        min_pw = node_f
                    elif node_f == min_pw:
                        selectedNodes.append(curr_node)
    
    # Evaluate all possible edge removals (no weight constraint)
    # ... similar process
    
    return [selectedNodes, selectedEdges]

def f_pairwise(components_list):
    """Configurable fitness function using selected payoff function"""
    return payoff_function(components_list)
```

**Key Properties:**
- Evaluates all remaining elements that satisfy constraints
- Nodes checked against both count (K1) and weight budget (K1_weight_budget)
- Selects based on maximum connectivity reduction among valid candidates
- Handles ties by random selection
- Respects dual-constraint model

### Multiprocessing Implementation

```python
def makeCNEPRun(config, method, i):
    [R, SS, EE] = method(config)
    currVal = f_pairwise(nx.connected_components(R))
    que.put([currVal, SS, EE])

# Main execution
que = Queue()
pool = Pool(processes=mainConfig.pool_size, initializer=pool_init, initargs=(que,))
tasks = []
for i in range(mainConfig.IterationCount):
    tasks.append(pool.apply_async(makeCNEPRun, args=(mainConfig, CNEP1a_2_G1, i,)))
for t in tasks:
    t.get()
```

**Benefits:**
- Parallel execution of multiple runs
- Better exploration of greedy choices
- Improved solution quality through repetition

## Comparative Analysis

### Algorithm Comparison

| Aspect | Genetic Algorithm | Greedy Algorithm |
|--------|------------------|------------------|
| **Solution Quality** | Generally better | Good, locally optimal |
| **Computational Time** | Higher (O(G×P×N×E)) | Lower (O(K×(N+E))) |
| **Memory Usage** | Higher (population storage) | Lower (single solution) |
| **Convergence** | Gradual improvement | Fast convergence |
| **Robustness** | High (population diversity) | Lower (single trajectory) |
| **Parallelization** | Limited (generational) | Good (multiple runs) |
| **Parameter Sensitivity** | High | Low |

### When to Use Each Algorithm

**Use Genetic Algorithm when:**
- Solution quality is paramount
- Computational time is not critical
- Network size is moderate (< 1000 nodes)
- Multiple parameter configurations need exploration
- Research/analysis context

**Use Greedy Algorithm when:**
- Fast solutions are needed
- Network size is large (> 1000 nodes)
- Computational resources are limited
- Real-time or near-real-time responses required
- Practical application context

### Hybridization Opportunities

1. **Seeded GA**: Initialize GA population with greedy solutions
2. **Local Search**: Apply greedy improvement to GA solutions
3. **Multi-stage**: Use greedy for initial reduction, GA for fine-tuning
4. **Parallel Execution**: Run both algorithms simultaneously

## Performance Optimization Strategies

### Genetic Algorithm Optimizations

1. **Fitness Caching**: Store previously computed fitness values
2. **Incremental Evaluation**: Update fitness based on changes only
3. **Population Diversity**: Maintain diverse solutions to avoid local optima
4. **Adaptive Parameters**: Adjust mutation/crossover rates based on convergence

### Greedy Algorithm Optimizations

1. **Efficient Data Structures**: Use adjacency lists for faster neighbor lookup
2. **Incremental Updates**: Update connectivity without full recomputation
3. **Pruning**: Skip obviously inferior choices
4. **Memory Management**: Reuse graph objects where possible

### General Optimizations

1. **NetworkX Optimization**: Use optimized NetworkX functions
2. **Memory Management**: Minimize deep copying operations
3. **Numerical Precision**: Use appropriate numeric types
4. **I/O Optimization**: Buffer file operations

## Payoff Function Analysis

### Comparison of Optimization Objectives

The three payoff functions offer different perspectives on network disruption:

| Aspect | Pairwise Connectivity | Number of Components | Largest Component Size |
|--------|----------------------|---------------------|----------------------|
| **Focus** | Total disconnected pairs | Network fragmentation | Dominant cluster size |
| **Computation** | O(Σ\|Cᵢ\|) | O(number of components) | O(number of components) |
| **Sensitivity** | Quadratic in component size | Linear in fragmentation | Focuses on largest cluster |
| **Interpretability** | Connection-based | Structure-based | Robustness-based |

### Theoretical Properties

**Pairwise Connectivity:**
- **Range**: [0, n(n-1)/2] where n = |V|
- **Minimum**: Achieved when all nodes are isolated (complete disruption)
- **Maximum**: Achieved when network remains fully connected
- **Characteristics**: Heavily penalizes large components due to quadratic growth

**Number of Components:**
- **Range**: [-n, -1] (negative for minimization)
- **Minimum**: -n (all nodes isolated)
- **Maximum**: -1 (network remains connected)
- **Characteristics**: Linear preference for fragmentation, treats all components equally

**Largest Component Size:**
- **Range**: [1, n]
- **Minimum**: 1 (no component larger than single node)
- **Maximum**: n (network remains fully connected)
- **Characteristics**: Only considers the dominant component, ignores smaller fragments

### Strategic Implications

**Pairwise Connectivity Strategy:**
- Targets large, densely connected regions
- Prefers breaking apart major clusters
- May leave small isolated components
- Optimal for maximizing communication disruption

**Component Count Strategy:**
- Seeks maximum network fragmentation
- May sacrifice large cluster reduction for more fragments
- Creates many small isolated components
- Optimal for creating distributed failure points

**Largest Component Strategy:**
- Focuses on eliminating network backbone
- May allow medium-sized components to persist
- Targets central, high-degree nodes
- Optimal for reducing network capacity and robustness

### Empirical Behavior

**Convergence Characteristics:**
- **Pairwise**: Smooth, gradual improvement
- **Components**: Step-wise improvement (discrete component creation)
- **Largest**: Focused improvement on dominant structure

**Solution Quality:**
- **Pairwise**: Generally produces balanced disruption
- **Components**: May create uneven disruption patterns
- **Largest**: Can leave significant secondary structures intact

**Computational Efficiency:**
- **Pairwise**: Most expensive (component size summation)
- **Components**: Most efficient (simple counting)
- **Largest**: Moderate (maximum finding)

## Theoretical Analysis

### Convergence Properties

**Genetic Algorithm:**
- Convergence guaranteed for infinite population and time
- Practical convergence depends on selection pressure and diversity
- Schema theorem provides theoretical foundation

**Greedy Algorithm:**
- Converges to locally optimal solution
- Quality depends on problem structure and tie-breaking
- No guarantee of global optimality

### Approximation Quality

**Genetic Algorithm:**
- No theoretical approximation bounds
- Empirically achieves high-quality solutions
- Performance improves with population size and generations

**Greedy Algorithm:**
- Approximation ratio depends on network structure
- Better performance on networks with clear structural bottlenecks
- Fast convergence to reasonable solutions

### Scalability Analysis

**Time Complexity:**
- GA: O(G × P × (N + E) × F) where F is fitness evaluation cost
- Greedy: O(I × K × (N + E)) where I is iterations, K is removals

**Space Complexity:**
- GA: O(P × K) for population storage
- Greedy: O(N + E) for graph representation

**Network Size Impact:**
- Both algorithms scale linearly with network size for sparse graphs
- Dense networks (E ≈ N²) significantly impact performance
- Memory becomes limiting factor for very large networks

## Future Extensions

### Algorithm Improvements

1. **Hybrid Approaches**: Combine GA and greedy strategies
2. **Multi-objective Optimization**: Consider multiple criteria simultaneously
3. **Dynamic Networks**: Handle time-evolving network structures
4. **Distributed Computing**: Scale to massive networks using cluster computing

### Problem Variations

1. **Weighted Networks**: Handle edge/node weights
2. **Directed Networks**: Extend to directed graphs
3. **Multiple Objectives**: Balance connectivity vs. other metrics
4. **Budget Uncertainty**: Robust optimization under uncertain budgets

### Implementation Enhancements

1. **GPU Acceleration**: Parallelize fitness evaluations
2. **Memory Optimization**: Handle larger networks efficiently
3. **Real-time Processing**: Support streaming network updates
4. **Interactive Visualization**: Real-time algorithm visualization