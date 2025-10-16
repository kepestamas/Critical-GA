# Critical Network Disruption Problem (CNDP) - Genetic Algorithm Implementation

## Project Overview

This project implements algorithms for solving the **Critical Network Disruption Problem (CNDP)**, a combinatorial optimization problem in network analysis. The goal is to find the optimal set of nodes and edges to remove from a network to minimize connectivity while adhering to resource constraints.

The project contains implementations of both **Genetic Algorithm (GA)** and **Greedy Algorithm** approaches, along with network analysis and visualization tools.

## Table of Contents

- [Problem Description](#problem-description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Algorithms](#algorithms)
- [Input Formats](#input-formats)
- [Output](#output)
- [Examples](#examples)
- [Performance](#performance)
- [Contributing](#contributing)

## Problem Description

The Critical Network Disruption Problem (CNDP) is formulated as follows:

Given:
- A network G(V, E) with vertices V and edges E
- Budget constraints: k₁ (maximum nodes to remove) and k₂ (maximum edges to remove)

Objective:
- Optimize network connectivity according to selected payoff function
- Three payoff function options available:

### Payoff Functions

1. **Pairwise Connectivity** *(default)*
   - Minimize: Σ(|C|·(|C|-1)/2) for all connected components C
   - Measures total number of pairwise connections within components
   - Original CNDP formulation

2. **Number of Components**
   - Maximize: Number of connected components in resulting network
   - Seeks to fragment network into as many isolated pieces as possible
   - Alternative perspective on network disruption

3. **Largest Component Size**
   - Minimize: Size of the largest connected component
   - Focuses on reducing the dominant cluster in the network
   - Useful for analyzing network robustness

The problem is NP-hard and requires heuristic approaches for large networks.

## Features

### Core Algorithms
- **Genetic Algorithm (GA)** with tournament selection and adaptive mutation
- **Greedy Algorithm** with multiprocessing support
- **Descending Mutation** strategy for improved convergence
- **Configurable Payoff Functions** for different optimization objectives

### Analysis Tools
- Comprehensive network property analysis
- Graph visualization (interactive HTML output)
- Performance benchmarking and timing
- Batch processing capabilities

### Supported Networks
- Social networks (Karate Club, Dolphins, Football)
- Biological networks (Brain networks, Protein interactions)
- Infrastructure networks (Power grids, Road networks, Airlines)
- Synthetic networks (Barabási-Albert, Erdős-Rényi, Watts-Strogatz)

## Installation

### Prerequisites
```bash
python >= 3.6
networkx >= 2.0
numpy
matplotlib
pyvis (for visualization)
```

### Install Dependencies
```bash
pip install networkx numpy matplotlib pyvis
```

### Clone Repository
```bash
git clone https://github.com/kepestamas/Critical-GA.git
cd Critical-GA
```

## Usage

### Genetic Algorithm

```bash
python connectivity_ga.py <input_file> <run_id> <node_fraction> <edge_fraction> <population_size> <tournament_size> <crossover_probability> <mutation_probability> [payoff_function]
```

**Parameters:**
- `input_file`: Network file from inputs/ directory
- `run_id`: Identifier for this experimental run
- `node_fraction`: Fraction of nodes to remove (0.0-1.0)
- `edge_fraction`: Fraction of edges to remove (0.0-1.0)
- `population_size`: GA population size (recommended: 50-100)
- `tournament_size`: Tournament selection size (recommended: 3-5)
- `crossover_probability`: Crossover rate (recommended: 0.8-0.9)
- `mutation_probability`: Mutation rate (recommended: 0.02-0.05)
- `payoff_function`: *(Optional)* Fitness function to use:
  - `pairwise_connectivity` *(default)*: Original pairwise connectivity measure
  - `number_of_components`: Maximize number of connected components
  - `largest_component_size`: Minimize size of largest connected component

**Examples:**
```bash
# Default pairwise connectivity
python connectivity_ga.py karate.txt 1 0.05 0.03 100 3 0.8 0.05

# Maximize connected components
python connectivity_ga.py karate.txt 1 0.05 0.03 100 3 0.8 0.05 number_of_components

# Minimize largest component
python connectivity_ga.py karate.txt 1 0.05 0.03 100 3 0.8 0.05 largest_component_size
```

### Greedy Algorithm

```bash
python connectivity_greedy.py <input_file> <run_id> [options] [payoff_function]
```

**Parameters:**
- `input_file`: Network file from inputs/ directory
- `run_id`: Identifier for this experimental run
- `payoff_function`: *(Optional)* Fitness function to use:
  - `pairwise_connectivity` *(default)*: Original pairwise connectivity measure
  - `number_of_components`: Maximize number of connected components
  - `largest_component_size`: Minimize size of largest connected component

**Examples:**
```bash
# Default pairwise connectivity
python connectivity_greedy.py karate.txt 1

# Maximize connected components
python connectivity_greedy.py karate.txt 1 -v 2 -e 2 number_of_components

# Minimize largest component
python connectivity_greedy.py karate.txt 1 -v 2 -e 2 largest_component_size
```

### Batch Processing

```bash
python connectivity_runner.py
```

This runs multiple experiments with predefined parameter sets across multiple network instances.

### Network Analysis

```bash
python network_analyzer.py <input_file>
```

Generates comprehensive network statistics including:
- Basic properties (nodes, edges, connectivity)
- Centrality measures
- Clustering coefficients
- Spectral properties
- Efficiency metrics

### Network Visualization

```bash
python network_painter.py <input_file>
```

Creates interactive HTML visualizations of networks and their disrupted versions.

## File Structure

```
Critical-GA/
├── connectivity_ga.py          # Genetic Algorithm implementation
├── connectivity_greedy.py      # Greedy Algorithm implementation  
├── connectivity_runner.py      # Batch execution script
├── payoff_functions.py         # Configurable fitness functions
├── network_analyzer.py         # Network property analysis
├── network_painter.py          # Network visualization
├── inputs/                     # Input network files
│   ├── karate.txt             # Zachary's Karate Club
│   ├── dolphins.txt           # Dolphin social network
│   ├── football.txt           # College football network
│   ├── BarabasiAlbert_*.txt   # Scale-free networks
│   ├── ErdosRenyi_*.txt       # Random networks
│   ├── ForestFire_*.txt       # Forest fire model networks
│   ├── WattsStrogatz_*.txt    # Small-world networks
│   ├── bn-*_brain_*.edges     # Brain networks
│   ├── power-*-bus.mtx        # Power grid networks
│   ├── inf-*.edges            # Infrastructure networks
│   └── ...                    # Additional network datasets
├── outputs/                    # Generated output files
├── .gitignore                 # Git ignore file
└── README.md                  # This documentation
```

## Algorithms

### Genetic Algorithm (GA)

**Key Components:**
- **Representation**: Each individual is a tuple (nodes_to_remove, edges_to_remove)
- **Selection**: Tournament selection with configurable size
- **Crossover**: Union-based crossover with random splitting
- **Mutation**: Adaptive descending mutation
- **Fitness**: Configurable payoff functions (pairwise connectivity, component count, largest component size)

**Algorithm Flow:**
1. Initialize random population
2. Evaluate fitness for all individuals
3. For each generation:
   - Perform tournament selection
   - Apply crossover to create offspring
   - Apply mutation with probability
   - Select best individuals for next generation
4. Output best solution found

**Advanced Features:**
- **Descending Mutation**: Mutation intensity decreases over generations
- **Duplicate Handling**: Ensures no duplicate nodes/edges in solutions
- **Adaptive Parameters**: Mutation count adapts based on generation

### Greedy Algorithm

**Strategy:**
- Iteratively select the node or edge whose removal causes maximum connectivity reduction
- Uses multiprocessing for parallel evaluation
- Maintains separate budgets for nodes and edges

**Algorithm Flow:**
1. Calculate baseline connectivity
2. For each remaining budget:
   - Evaluate all possible single removals
   - Select removal with maximum impact
   - Update network and continue
3. Output final solution

## Input Formats

The system supports multiple network file formats:

### Format 1: Edge List (Space/Tab Separated)
```
1 2
1 3
2 3
...
```

### Format 2: Adjacency List with Node IDs
```
nodes:edges
0: 1 2 3 
1: 0 2 4
2: 0 1 3
...
```

### Format 3: Matrix Market (.mtx)
Standard Matrix Market format for sparse matrices.

### Format 4: Custom Formats
Various biological and infrastructure network formats are supported through format-specific parsers.

## Output

### GA Output Format
```
outputs/descending_mutation/ga/timing<run_id>_<input_file>_ke_<k_edges>_kn_<k_nodes>
```

**Content:**
Each line contains: `<generation> <fitness_evaluations> <best_fitness> <solution>`

### Greedy Output Format
```
outputs/reruns/greedy/<run_id>_<input_file>
```

**Content:**
```
Nodes removed: [list_of_nodes]
Edges removed: [list_of_edges]  
MinVal achieved: <final_connectivity>
```

### Analysis Output
```
outputs/reruns/networks/<input_file>
```

Contains comprehensive network statistics and metrics.

## Examples

### Example 1: Small Network Analysis
```bash
# Analyze Karate Club network
python network_analyzer.py karate.txt

# Run GA with moderate disruption
python connectivity_ga.py karate.txt 1 0.1 0.05 50 3 0.8 0.05

# Visualize results
python network_painter.py karate.txt
```

### Example 2: Large Scale Analysis
```bash
# Run on Barabási-Albert network
python connectivity_ga.py BarabasiAlbert_n1000m1.txt 1 0.05 0.03 100 5 0.9 0.02

# Compare with greedy approach
python connectivity_greedy.py BarabasiAlbert_n1000m1.txt 1
```

### Example 3: Batch Experiments
```bash
# Run comprehensive experiments
python connectivity_runner.py
```

This will execute multiple runs across different networks and parameter configurations.

## Performance

### Computational Complexity
- **GA**: O(G × P × N × E) where G=generations, P=population, N=nodes, E=edges
- **Greedy**: O(K × (N + E)) where K=total removals

### Scalability
- **Small networks** (< 100 nodes): Both algorithms perform well
- **Medium networks** (100-1000 nodes): GA recommended for quality, Greedy for speed
- **Large networks** (> 1000 nodes): Greedy algorithm preferred

### Memory Requirements
- **GA**: O(P × K) for population storage
- **Greedy**: O(N + E) for graph representation

## Parameter Tuning Guidelines

### Genetic Algorithm Parameters

**Population Size:**
- Small networks (< 100 nodes): 50-100
- Large networks (> 500 nodes): 100-200

**Tournament Size:**
- Generally 3-5
- Larger values increase selection pressure

**Crossover Probability:**
- Recommended: 0.8-0.9
- Higher values promote exploration

**Mutation Probability:**
- Start with 0.02-0.05
- Adjust based on convergence behavior

### Budget Parameters

**Node Removal Fraction:**
- Conservative: 0.01-0.05 (1-5% of nodes)
- Aggressive: 0.1-0.2 (10-20% of nodes)

**Edge Removal Fraction:**
- Conservative: 0.01-0.03 (1-3% of edges)
- Aggressive: 0.05-0.1 (5-10% of edges)

## Network Datasets

### Included Networks

**Social Networks:**
- `karate.txt`: Zachary's Karate Club (34 nodes, 78 edges)
- `dolphins.txt`: Dolphin social network (62 nodes, 159 edges)
- `football.txt`: College football (115 nodes, 613 edges)

**Biological Networks:**
- `bn-*_brain_*.edges`: Various brain connectivity networks
- `Ecoli.txt`: E. coli metabolic network
- `humanDiseasome.txt`: Human disease network

**Infrastructure Networks:**
- `power-*-bus.mtx`: Power grid topologies
- `inf-euroroad.edges`: European road network
- `inf-openflights.edges`: Airport network

**Synthetic Networks:**
- `BarabasiAlbert_*.txt`: Scale-free networks
- `ErdosRenyi_*.txt`: Random graphs
- `WattsStrogatz_*.txt`: Small-world networks
- `ForestFire_*.txt`: Forest fire model networks

## Visualization

The `network_painter.py` script generates interactive HTML visualizations using PyVis:

**Features:**
- Interactive node manipulation
- Zoom and pan capabilities
- Highlighting of removed elements
- Component visualization
- Export capabilities

**Usage:**
```bash
python network_painter.py <network_file>
```

Outputs: `nx3.html` (interactive network visualization)

## Troubleshooting

### Common Issues

**Memory Errors:**
- Reduce population size for GA
- Use smaller networks for testing
- Increase system memory or use smaller batches

**Slow Performance:**
- Reduce generation count for GA
- Use greedy algorithm for large networks
- Enable multiprocessing where available

**File Format Errors:**
- Ensure input files are in supported formats
- Check for missing or corrupted data
- Verify file paths are correct

**Import Errors:**
- Install all required dependencies
- Check Python version compatibility
- Verify NetworkX installation

### Debug Mode

Enable debug output by modifying the debug level in the scripts:
```python
iDebug = 2  # Maximum debug output
```

## Research Applications

This implementation has been used for research in:
- **Network Robustness Analysis**: Identifying critical network components
- **Security Assessment**: Finding vulnerable network elements
- **Infrastructure Protection**: Evaluating network resilience
- **Social Network Analysis**: Understanding information spread patterns

## Citation

If you use this code in your research, please cite:

```bibtex
@software{critical_ga_2025,
  title={Critical Network Disruption Problem - Genetic Algorithm Implementation},
  author={Tamás Kálmán},
  year={2025},
  url={https://github.com/kepestamas/Critical-GA}
}
```

## License

This project is available under the MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/kepestamas/Critical-GA.git
cd Critical-GA
pip install -r requirements.txt  # (if requirements.txt exists)
```

## Acknowledgments

- NetworkX development team for the graph library
- Research communities contributing network datasets
- Open source scientific computing ecosystem

## Contact

For questions, issues, or collaboration opportunities:
- GitHub: [kepestamas](https://github.com/kepestamas)
- Project: [Critical-GA](https://github.com/kepestamas/Critical-GA)

---

*Last updated: October 2025*