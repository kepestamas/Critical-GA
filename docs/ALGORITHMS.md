# Algorithm Details

## Problem Formulation

### Critical Network Disruption Problem (CNDP)

The Critical Network Disruption Problem is a combinatorial optimization problem that seeks to minimize network connectivity by strategically removing a limited number of network elements.

#### Mathematical Formulation

**Given:**
- Undirected graph G = (V, E) where V is the vertex set and E is the edge set
- Budget constraints: k₁ ≤ |V| (maximum nodes to remove), k₂ ≤ |E| (maximum edges to remove)

**Decision Variables:**
- S ⊆ V: Set of nodes to remove, |S| ≤ k₁
- T ⊆ E: Set of edges to remove, |T| ≤ k₂

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
- |S| ≤ k₁
- |T| ≤ k₂  
- S ⊆ V
- T ⊆ E

#### Problem Complexity

The CNDP is NP-hard, as it generalizes several known NP-hard problems:
- **Node Connectivity**: Finding minimum vertex cut
- **Edge Connectivity**: Finding minimum edge cut
- **Graph Partitioning**: Optimal graph bisection

The problem space grows exponentially: O(C(|V|,k₁) × C(|E|,k₂)) possible solutions.

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
    node_list = list(G.nodes)
    nodes = random.sample(node_list, k_nodes)
    edge_list = list(G.edges)
    edges = random.sample(edge_list, k_edges)
    return (nodes, edges)
```

**Characteristics:**
- Random sampling without replacement
- Ensures feasible solutions (no duplicates)
- Uniform distribution over search space

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

The crossover operator combines genetic material from two parents:

```python
def split_node_lists(united_node_list):
    first_child_nodes = []
    second_child_nodes = []
    random.shuffle(united_node_list)
    
    # Handle common elements (present in both parents)
    for node in united_node_list:
        if united_node_list.count(node) == 2:
            first_child_nodes.append(node)
            second_child_nodes.append(node)
            while node in united_node_list:
                united_node_list.remove(node)
    
    # Distribute unique elements
    for node in united_node_list: 
        if not node in first_child_nodes and len(first_child_nodes) < k_nodes:
            first_child_nodes.append(node)
        elif not node in second_child_nodes:
            second_child_nodes.append(node)
    
    return first_child_nodes, second_child_nodes
```

**Process:**
1. Unite parent solutions: S₁ ∪ S₂ and T₁ ∪ T₂
2. Common elements go to both children
3. Unique elements distributed randomly
4. Ensure size constraints are satisfied

**Properties:**
- Preserves good building blocks
- Maintains feasibility
- Introduces controlled randomness

### Mutation: Descending Mutation

Two mutation strategies are implemented:

#### Standard Mutation
```python
def mutate(individual):
    new_individual = individual[0]
    if random.random() <= 0.5:  # 50% chance to mutate nodes vs edges
        # Replace random node
        chosen_node = random.choice(new_individual[0])
        new_individual[0].remove(chosen_node)
        new_node = random.choice(list(G.nodes))
        while new_node in new_individual[0]:
            new_node = random.choice(list(G.nodes))
        new_individual[0].append(new_node)
    else:
        # Replace random edge (similar process)
    return (new_individual, fitness(new_individual))
```

#### Descending Mutation (Advanced)
```python
def actualize_mutation_count(current_gen, max_gen):
    global mutation_count
    half_gen = int(max_gen / 2)
    alfa = (half_gen - current_gen) / half_gen
    mutation_count = max(int(((k_nodes + k_edges)/4)*alfa), 1)

def descending_mutation(individual):
    global mutation_count
    new_individual = individual[0]
    for _ in range(mutation_count):
        # Apply multiple mutations (similar to standard)
    return (new_individual, fitness(new_individual))
```

**Key Features:**
- Mutation intensity decreases over generations
- High exploration early, exploitation later
- Prevents premature convergence

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

The greedy algorithm uses a constructive approach, iteratively selecting the single best removal at each step based on immediate impact on connectivity.

### Algorithm Structure

```python
def CNEP1a_2_G1(config):
    S = []  # Selected nodes
    E = []  # Selected edges
    H = config.G.copy()
    
    while len(S) + len(E) < config.K:
        [A, B] = best_nodes_edges_CNEP1A_Alg2(config, S, E, H)
        
        # Select best node or edge
        z1 = select_random(A) if len(A) > 0 else config.NIL
        z2 = select_random(B) if len(B) > 0 else config.NIL
        
        # Make decision
        if z1 != config.NIL:
            if z2 != config.NIL:
                if random.randint(0, 1) == 1:
                    S.append(z1)
                    H.remove_nodes_from([z1])
                else:
                    E.append(z2)
                    H.remove_edges_from([z2])
            else:
                S.append(z1)
                H.remove_nodes_from([z1])
        else:
            E.append(z2)
            H.remove_edges_from([z2])
    
    return [H, S, E]
```

### Best Element Selection

The greedy algorithm now supports configurable payoff functions:

```python
from payoff_functions import PAYOFF_FUNCTIONS

# Global payoff function set via command line
payoff_function = PAYOFF_FUNCTIONS.get(payoff_name, 
                                     PAYOFF_FUNCTIONS['pairwise_connectivity'])

def best_nodes_edges_CNEP1A_Alg2(config, SN, SE, GG):
    selectedEdges = []
    selectedNodes = []
    min_pw = config.INF
    
    P = GG.copy()
    P.remove_nodes_from(SN)
    P.remove_edges_from(SE)
    node_f_orig = f_pairwise(nx.connected_components(P))
    
    # Evaluate all possible node removals
    if len(SN) < config.K1:
        for curr_node in nx.nodes(config.G):
            R = P.copy()
            R.remove_nodes_from([curr_node])
            node_f = node_f_orig - f_pairwise(nx.connected_components(R))
            
            if node_f < min_pw:
                selectedNodes.clear()
                selectedNodes.append(curr_node)
                min_pw = node_f
            elif node_f == min_pw:
                selectedNodes.append(curr_node)
    
    # Evaluate all possible edge removals (similar process)
    
    return [selectedNodes, selectedEdges]

def f_pairwise(components_list):
    """Configurable fitness function using selected payoff function"""
    return payoff_function(components_list)
```

**Key Properties:**
- Evaluates all remaining elements
- Selects based on maximum connectivity reduction
- Handles ties by random selection
- Respects budget constraints

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