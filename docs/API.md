# API Documentation

## Core Functions and Classes

### connectivity_ga.py

#### Main Functions

##### `read_graph(input, input_type)`
Parses network files in various formats and creates NetworkX Graph objects.

**Parameters:**
- `input` (str): Path to the input file
- `input_type` (str): Type of input format (currently unused, auto-detected)

**Returns:**
- `nx.Graph`: NetworkX graph object

**Supported Formats:**
- Adjacency list format (BarabasiAlbert, ErdosRenyi, ForestFire, WattsStrogatz)
- Edge list format (most biological and infrastructure networks)
- Custom formats for specific datasets

##### `generate_pop()`
Generates initial population for the genetic algorithm.

**Returns:**
- `list`: Population of (nodes, edges) tuples

##### `generate_one_pair()`
Creates a single individual (solution candidate).

**Returns:**
- `tuple`: (nodes_to_remove, edges_to_remove)

##### `fitness(individual)`
Evaluates the fitness of an individual solution.

**Parameters:**
- `individual` (tuple): (nodes_to_remove, edges_to_remove)

**Returns:**
- `float`: Pairwise connectivity score (lower is better)

**Implementation:**
```python
def fitness(individual):
    P = copy.deepcopy(G)
    P.remove_nodes_from(individual[0])
    P.remove_edges_from(individual[1])
    result = pairwise(nx.connected_components(P))
    return result
```

##### `pairwise(components_list)` - DEPRECATED
Calculates pairwise connectivity from connected components.

**Parameters:**
- `components_list`: Iterator of connected components from NetworkX

**Returns:**
- `float`: Sum of C*(C-1)/2 for all components C

**Note:** This function is being replaced by configurable payoff functions in `payoff_functions.py`.

##### `selection(evaluated_population)`
Performs selection to maintain population size.

**Parameters:**
- `evaluated_population` (list): List of (individual, fitness) tuples

**Returns:**
- `list`: Selected individuals for next generation

##### `crossover_tournament(evaluated_population)`
Performs tournament-based crossover to generate offspring.

**Parameters:**
- `evaluated_population` (list): Current population with fitness values

**Returns:**
- `list`: New offspring population

##### `tournament_round(evaluated_population)`
Executes a single tournament round.

**Parameters:**
- `evaluated_population` (list): Population to select from

**Returns:**
- `tuple`: Two offspring individuals

##### `mutate(individual)` / `descending_mutation(individual)`
Applies mutation operators to individuals.

**Parameters:**
- `individual` (tuple): Individual to mutate

**Returns:**
- `tuple`: (mutated_individual, fitness_score)

**Mutation Types:**
- `mutate()`: Single random replacement
- `descending_mutation()`: Multiple replacements with decreasing intensity

##### `actualize_mutation_count(current_gen, max_gen)`
Updates mutation intensity based on current generation.

**Parameters:**
- `current_gen` (int): Current generation number
- `max_gen` (int): Maximum generations

**Side Effects:**
- Updates global `mutation_count` variable

#### Global Variables

- `G`: Main graph object (NetworkX Graph)
- `n`: Number of nodes
- `m`: Number of edges  
- `k_nodes`: Number of nodes to remove
- `k_edges`: Number of edges to remove
- `pop_size`: Population size
- `gen_count`: Maximum generations (default: 5000)
- `tournament_size`: Tournament selection size
- `p_cross`: Crossover probability
- `mutation_chance`: Mutation probability
- `fitness_count`: Global fitness evaluation counter
- `payoff_function`: Current payoff function (from payoff_functions module)

### payoff_functions.py

#### Configurable Fitness Functions

The `payoff_functions.py` module provides three different optimization objectives for the CNDP problem.

##### `pairwise_connectivity(components)`
Default payoff function implementing original CNDP objective.

**Parameters:**
- `components` (Iterator[Set]): Connected components from NetworkX

**Returns:**
- `float`: Sum of C*(C-1)/2 for all components C

**Implementation:**
```python
def pairwise_connectivity(components: Iterator[Set]) -> float:
    global fitness_count
    fitness_count += 1
    
    score = 0.0
    for component in components:
        size = len(component)
        if size > 1:
            score += size * (size - 1) / 2
    
    return score
```

##### `number_of_components(components)`
Alternative objective maximizing network fragmentation.

**Parameters:**
- `components` (Iterator[Set]): Connected components from NetworkX

**Returns:**
- `float`: Negative number of components (for minimization)

**Rationale:**
- More components = better network disruption
- Returns negative value to work with minimization algorithms
- Encourages solutions that fragment the network into many small pieces

##### `largest_component_size(components)`
Alternative objective minimizing dominant cluster size.

**Parameters:**
- `components` (Iterator[Set]): Connected components from NetworkX

**Returns:**
- `float`: Size of largest connected component

**Rationale:**
- Smaller largest component = reduced network functionality
- Directly minimizes the size of the dominant cluster
- Useful for analyzing network robustness and cascading failures

#### Function Registry

##### `PAYOFF_FUNCTIONS`
Dictionary mapping function names to implementations.

```python
PAYOFF_FUNCTIONS = {
    'pairwise_connectivity': pairwise_connectivity,
    'number_of_components': number_of_components,
    'largest_component_size': largest_component_size
}
```

#### Usage Examples

##### In Genetic Algorithm:
```python
from payoff_functions import PAYOFF_FUNCTIONS

# Set payoff function based on command line argument
payoff_function = PAYOFF_FUNCTIONS.get(payoff_name, 
                                     PAYOFF_FUNCTIONS['pairwise_connectivity'])

# Use in fitness evaluation
def fitness(individual):
    P = copy.deepcopy(G)
    P.remove_nodes_from(individual[0])
    P.remove_edges_from(individual[1])
    result = payoff_function(nx.connected_components(P))
    return result
```

##### In Greedy Algorithm:
```python
from payoff_functions import PAYOFF_FUNCTIONS

# Set global payoff function
payoff_function = PAYOFF_FUNCTIONS.get(payoff_name, 
                                     PAYOFF_FUNCTIONS['pairwise_connectivity'])

def f_pairwise(components_list):
    return payoff_function(components_list)
```

### connectivity_greedy.py

#### Classes

##### `config`
Configuration and setup class for greedy algorithm.

**Attributes:**
- `inputFile`: Path to input network file
- `G`: NetworkX graph object
- `K1`: Number of nodes to remove
- `K2`: Number of edges to remove
- `K`: Total removals (K1 + K2)
- `INF`: Large number for infinity representation
- `IterationCount`: Number of greedy iterations
- `pool_size`: Number of CPU processes
- `iDebug`: Debug level (0-2)

**Methods:**

###### `__init__(input_file, iterCount, iK1, iK2, iDebug=2)`
Initialize configuration object.

###### `read_graph(input, input_type)`
Parse input network file (similar to GA version).

#### Core Functions

##### `best_nodes_edges_CNEP1A_Alg2(config, SN, SE, GG)`
Finds best nodes/edges to remove in current iteration.

**Parameters:**
- `config`: Configuration object
- `SN`: Currently selected nodes
- `SE`: Currently selected edges  
- `GG`: Current graph state

**Returns:**
- `list`: [best_nodes, best_edges] candidates

##### `CNEP1a_2_G1(config)`
Main greedy algorithm implementation.

**Parameters:**
- `config`: Configuration object

**Returns:**
- `list`: [final_graph, removed_nodes, removed_edges]

##### `makeCNEPRun(config, method, i)`
Executes single greedy run (for multiprocessing).

**Parameters:**
- `config`: Configuration object
- `method`: Algorithm function to run
- `i`: Run identifier

#### Utility Functions

##### `f_pairwise(components_list)`
Configurable fitness function that uses the selected payoff function from `payoff_functions.py`. 

**Note:** Name is historical - now supports all payoff functions, not just pairwise connectivity.

##### `select_random(lst)`
Selects random element from list.

##### `print_config(mainConfig)`
Prints current configuration settings.

##### `print_usage()`
Displays command-line usage information.

### network_analyzer.py

#### Main Analysis Function

The script performs comprehensive network analysis when run as main program.

#### Computed Metrics

##### Basic Properties
- `V`: Number of vertices
- `E`: Number of edges
- `k`: Graph connectivity (boolean)
- `k_v`: Node connectivity 
- `k_e`: Edge connectivity
- `delta_min`: Minimum degree

##### Distance Metrics  
- `d`: Network diameter
- `d_avg`: Average shortest path length
- `eff`: Global efficiency

##### Centrality Metrics
- `b_max`: Maximum edge betweenness
- `b_v`: Average vertex betweenness  
- `b_e`: Average edge betweenness

##### Clustering
- `C`: Average clustering coefficient

##### Spectral Properties
- `l_eig`: Laplacian eigenvalues (sorted)
- Algebraic connectivity (λ₂)
- `eps`: Number of spanning trees
- `R`: Effective graph resistance (Kirchhoff index)

#### Implementation Details

##### Laplacian Matrix Construction
```python
L = np.arange(len(node_list) * len(node_list))
L.shape = (len(node_list), len(node_list))

for i in range(len(node_list)):
    for j in range(len(node_list)):
        if node_list[j] in G.neighbors(node_list[i]):
            L[i, j] = -1
        elif i == j:
            L[i, j] = G.degree(node_list[i])
        else:
            L[i, j] = 0
```

### network_painter.py

#### Visualization Functions

##### `read_graph(input)`
Similar to other modules, parses network files.

#### Main Workflow
1. Load original network
2. Read solution file with removed elements
3. Apply removals to create modified network
4. Generate interactive HTML visualization using PyVis

#### Output
- `nx3.html`: Interactive network visualization

### connectivity_runner.py

#### Batch Processing Script

##### Configuration Variables
- `file_list`: Networks to process
- `p_nodes`: Fraction of nodes to remove
- `p_edges`: Fraction of edges to remove
- `pop_size`: GA population size
- `tournament_size`: Tournament selection size
- `p_cross`: Crossover probability
- `p_mut`: Mutation probability

##### Execution Loop
Runs multiple algorithm instances with timing measurements and logs results.

## Error Handling

### Common Exceptions

##### `FileNotFoundError`
- **Cause**: Input file not found
- **Solution**: Verify file path and existence

##### `KeyError` 
- **Cause**: Unsupported file format
- **Solution**: Add format to supported file list

##### `MemoryError`
- **Cause**: Large networks with high population sizes
- **Solution**: Reduce population size or use greedy algorithm

##### `NetworkXError`
- **Cause**: Invalid graph operations
- **Solution**: Check graph connectivity and node/edge existence

## Performance Optimization

### Memory Management
- Use `copy.deepcopy()` sparingly
- Implement in-place modifications where possible
- Clear unused variables in loops

### Computational Efficiency
- Cache fitness evaluations
- Use efficient data structures (sets for lookups)
- Leverage NetworkX optimized algorithms

### Multiprocessing
- Greedy algorithm supports multiprocessing
- GA is inherently sequential due to evolutionary nature
- Consider parallel fitness evaluation for GA

## Extension Points

### Adding New File Formats
1. Add format detection logic in `read_graph()`
2. Implement parser for new format
3. Test with sample files

### Custom Fitness Functions
1. Replace `pairwise()` function
2. Ensure minimization objective
3. Update selection logic if needed

### Alternative Algorithms
1. Implement new algorithm following existing interface
2. Add configuration parameters
3. Integrate with runner script

### Visualization Enhancements
1. Extend PyVis configuration options
2. Add custom styling and layouts
3. Implement export functionality

## Dependencies

### Required Libraries
```python
import networkx as nx      # Graph algorithms and data structures
import numpy as np         # Numerical computations
import random             # Random number generation
import copy               # Deep copying of objects  
import sys                # System parameters and functions
import time               # Timing functions
import math               # Mathematical functions
import subprocess         # Process management
import multiprocessing    # Parallel processing
import matplotlib.pyplot as plt  # Plotting (optional)
from pyvis.network import Network  # Interactive visualization
```

### Version Requirements
- Python >= 3.6
- NetworkX >= 2.0
- NumPy >= 1.15
- Matplotlib >= 3.0 (optional)
- PyVis >= 0.1.8 (for visualization)

## Configuration Files

### Future Enhancements
Consider creating configuration files for:
- Algorithm parameters
- File format specifications  
- Output formatting options
- Visualization settings

### Example Configuration (JSON)
```json
{
  "ga_params": {
    "population_size": 100,
    "max_generations": 5000,
    "tournament_size": 3,
    "crossover_prob": 0.8,
    "mutation_prob": 0.05
  },
  "problem_params": {
    "node_removal_fraction": 0.05,
    "edge_removal_fraction": 0.03
  },
  "output": {
    "directory": "outputs/",
    "timing_enabled": true,
    "debug_level": 1
  }
}
```