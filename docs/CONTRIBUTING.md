# Contributing to Critical-GA

We welcome contributions to the Critical Network Disruption Problem (CNDP) project! This document provides guidelines for contributing code, documentation, datasets, and research insights.

## Table of Contents

- [Getting Started](#getting-started)
- [Types of Contributions](#types-of-contributions)
- [Development Setup](#development-setup)
- [Code Contribution Process](#code-contribution-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Standards](#documentation-standards)
- [Dataset Contributions](#dataset-contributions)
- [Research Contributions](#research-contributions)
- [Issue Reporting](#issue-reporting)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.6+ installed
- Git version control system
- Familiarity with network analysis concepts
- Basic understanding of genetic algorithms or optimization

### Quick Start

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/Critical-GA.git
   cd Critical-GA
   ```

2. **Set up development environment**
   ```bash
   python -m venv dev_env
   source dev_env/bin/activate  # On Windows: dev_env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes and test**
   ```bash
   python connectivity_ga.py karate.txt 1 0.05 0.03 50 3 0.8 0.05
   ```

## Types of Contributions

### 1. Algorithm Improvements
- **Performance optimizations**: Faster fitness evaluation, memory efficiency
- **New selection methods**: Alternative selection strategies
- **Hybrid algorithms**: Combining GA with other metaheuristics
- **Parallel implementations**: GPU acceleration, distributed computing

### 2. New Features
- **Additional algorithms**: Ant Colony Optimization, Particle Swarm Optimization
- **Multi-objective optimization**: Pareto-optimal solutions
- **Dynamic networks**: Time-varying graph analysis
- **Interactive tools**: Real-time parameter tuning

### 3. Bug Fixes
- **Correctness issues**: Logic errors, mathematical mistakes
- **Performance bugs**: Memory leaks, inefficient algorithms
- **Compatibility issues**: Python version compatibility, OS-specific problems
- **Edge cases**: Handling empty graphs, disconnected components

### 4. Documentation
- **API documentation**: Function and class descriptions
- **Tutorials**: Step-by-step guides
- **Examples**: Use case demonstrations
- **Research documentation**: Algorithm analysis, experimental results

### 5. Datasets
- **New network types**: Additional real-world networks
- **Synthetic networks**: New generative models
- **Benchmark suites**: Standardized test collections
- **Data validation**: Quality assurance tools

### 6. Testing
- **Unit tests**: Function-level testing
- **Integration tests**: End-to-end workflows
- **Performance tests**: Benchmarking and profiling
- **Regression tests**: Preventing functionality breakage

## Development Setup

### Environment Configuration

1. **Clone and setup**
   ```bash
   git clone https://github.com/kepestamas/Critical-GA.git
   cd Critical-GA
   python -m venv dev_env
   source dev_env/bin/activate
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   # Or install individual development tools:
   pip install pytest black flake8 mypy sphinx
   ```

3. **Pre-commit hooks (recommended)**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### IDE Configuration

#### VS Code Settings (`.vscode/settings.json`)
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### PyCharm Configuration
- Enable flake8 linting
- Set Black as code formatter
- Configure pytest as test runner
- Mark `inputs/` and `outputs/` as resource directories

## Code Contribution Process

### 1. Planning Phase

#### Before Writing Code
- **Check existing issues**: Look for related discussions
- **Discuss major changes**: Open an issue for significant modifications
- **Review existing code**: Understand current architecture
- **Plan testing strategy**: How will you validate your changes?

#### Design Considerations
- **Maintain compatibility**: Don't break existing functionality
- **Follow patterns**: Use established coding patterns
- **Consider performance**: Profile critical sections
- **Document decisions**: Explain complex algorithms

### 2. Implementation Phase

#### Code Organization
```
Critical-GA/
├── algorithms/          # Algorithm implementations
│   ├── genetic/        # GA variants
│   ├── greedy/         # Greedy algorithms
│   └── hybrid/         # Hybrid approaches
├── utils/              # Utility functions
│   ├── graph_io.py     # Graph input/output
│   ├── fitness.py      # Fitness functions
│   └── visualization.py # Plotting utilities
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Usage examples
```

#### Coding Standards
- **Function length**: Keep functions under 50 lines when possible
- **Variable naming**: Use descriptive names (`node_count` not `n`)
- **Comments**: Explain why, not what
- **Error handling**: Use appropriate exception handling
- **Type hints**: Add type annotations for public functions

### 3. Testing Phase

#### Required Tests
```python
# tests/test_genetic_algorithm.py
import pytest
from algorithms.genetic import GeneticAlgorithm

def test_fitness_calculation():
    """Test fitness function returns correct connectivity score."""
    # Test implementation
    pass

def test_crossover_preserves_constraints():
    """Test crossover maintains solution feasibility."""
    # Test implementation
    pass
```

#### Test Categories
- **Unit tests**: Individual function testing
- **Integration tests**: Component interaction testing
- **Performance tests**: Timing and memory usage
- **Regression tests**: Prevent previous bug recurrence

### 4. Documentation Phase

All contributions must include appropriate documentation:

#### Code Documentation
```python
def fitness(individual: Tuple[List[str], List[Tuple[str, str]]], 
           graph: nx.Graph) -> float:
    """
    Calculate the pairwise connectivity fitness of a solution.
    
    Args:
        individual: Tuple of (nodes_to_remove, edges_to_remove)
        graph: Original network graph
        
    Returns:
        Pairwise connectivity score (lower is better)
        
    Raises:
        ValueError: If individual contains invalid nodes/edges
        
    Example:
        >>> G = nx.karate_club_graph()
        >>> individual = (['0', '1'], [('2', '3')])
        >>> score = fitness(individual, G)
        >>> print(f"Fitness: {score}")
    """
```

#### Documentation Files
- Update README.md if needed
- Add to appropriate docs/ files
- Include usage examples
- Document new parameters

## Code Style Guidelines

### Python Style (PEP 8 + Project Specific)

#### Formatting
```python
# Use Black formatter (line length: 88)
# Install: pip install black
# Run: black *.py

# Good
def calculate_connectivity(graph, removed_nodes, removed_edges):
    """Calculate network connectivity after removals."""
    modified_graph = graph.copy()
    modified_graph.remove_nodes_from(removed_nodes)
    modified_graph.remove_edges_from(removed_edges)
    return sum(len(c) * (len(c) - 1) // 2 
               for c in nx.connected_components(modified_graph))

# Bad - inconsistent spacing, long line
def calculate_connectivity(graph,removed_nodes,removed_edges):
    modified_graph=graph.copy()
    modified_graph.remove_nodes_from(removed_nodes);modified_graph.remove_edges_from(removed_edges)
    return sum([len(c)*(len(c)-1)/2 for c in nx.connected_components(modified_graph)])
```

#### Naming Conventions
```python
# Variables and functions: snake_case
population_size = 100
def run_genetic_algorithm():
    pass

# Classes: PascalCase
class GeneticAlgorithm:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_GENERATIONS = 5000
DEFAULT_MUTATION_RATE = 0.05

# Private attributes: leading underscore
class Algorithm:
    def __init__(self):
        self._fitness_cache = {}
```

#### Import Organization
```python
# Standard library imports
import copy
import random
import sys
from typing import List, Tuple, Dict

# Third-party imports
import networkx as nx
import numpy as np

# Local imports
from utils.graph_io import read_graph
from algorithms.genetic import GeneticAlgorithm
```

### Algorithm-Specific Guidelines

#### Genetic Algorithm Code
```python
# Use clear variable names for GA components
def tournament_selection(population: List[Individual], 
                        tournament_size: int) -> Individual:
    """Select best individual from random tournament."""
    contestants = random.sample(population, tournament_size)
    return min(contestants, key=lambda ind: ind.fitness)

# Avoid global variables, use class-based approach
class GeneticAlgorithm:
    def __init__(self, population_size: int, mutation_rate: float):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.generation = 0
```

#### Network Analysis Code
```python
# Use NetworkX idioms
def analyze_network(graph: nx.Graph) -> Dict[str, float]:
    """Compute comprehensive network statistics."""
    return {
        'nodes': graph.number_of_nodes(),
        'edges': graph.number_of_edges(),
        'density': nx.density(graph),
        'clustering': nx.average_clustering(graph),
        'diameter': nx.diameter(graph) if nx.is_connected(graph) else float('inf')
    }
```

## Testing Guidelines

### Test Structure

#### Directory Organization
```
tests/
├── unit/               # Unit tests
│   ├── test_fitness.py
│   ├── test_selection.py
│   └── test_crossover.py
├── integration/        # Integration tests
│   ├── test_ga_workflow.py
│   └── test_greedy_workflow.py
├── performance/        # Performance tests
│   └── test_scalability.py
├── fixtures/           # Test data
│   ├── small_graphs.py
│   └── test_networks/
└── conftest.py        # Pytest configuration
```

#### Test Implementation
```python
# tests/unit/test_fitness.py
import pytest
import networkx as nx
from algorithms.fitness import calculate_pairwise_connectivity

class TestFitnessCalculation:
    """Test suite for fitness function."""
    
    def test_empty_removal(self):
        """Test fitness with no removals."""
        G = nx.karate_club_graph()
        fitness = calculate_pairwise_connectivity(G, [], [])
        expected = len(G) * (len(G) - 1) // 2  # Complete connectivity
        assert fitness == expected
    
    def test_complete_disconnection(self):
        """Test fitness when network is completely disconnected."""
        G = nx.path_graph(4)  # 0-1-2-3
        # Remove middle edges to disconnect
        removed_edges = [(1, 2)]
        fitness = calculate_pairwise_connectivity(G, [], removed_edges)
        expected = 1 + 1  # Two components of size 2 each
        assert fitness == expected
    
    @pytest.mark.parametrize("graph_generator,size", [
        (nx.karate_club_graph, None),
        (nx.erdos_renyi_graph, (50, 0.1)),
        (nx.barabasi_albert_graph, (100, 2))
    ])
    def test_various_networks(self, graph_generator, size):
        """Test fitness calculation on various network types."""
        if size is None:
            G = graph_generator()
        else:
            G = graph_generator(*size)
        
        # Test should not raise exceptions
        fitness = calculate_pairwise_connectivity(G, [], [])
        assert fitness >= 0
```

### Performance Testing
```python
# tests/performance/test_scalability.py
import time
import pytest
import networkx as nx
from algorithms.genetic import GeneticAlgorithm

class TestScalability:
    """Test algorithm performance on various network sizes."""
    
    @pytest.mark.parametrize("size", [100, 500, 1000])
    def test_ga_scalability(self, size):
        """Test GA performance scales reasonably with network size."""
        G = nx.barabasi_albert_graph(size, 2)
        ga = GeneticAlgorithm(population_size=20, max_generations=10)
        
        start_time = time.time()
        result = ga.run(G, k_nodes=size//20, k_edges=size//10)
        execution_time = time.time() - start_time
        
        # Performance should be reasonable (adjust thresholds as needed)
        assert execution_time < size * 0.1  # Linear scaling assumption
        assert result.fitness >= 0
```

### Test Data Management
```python
# tests/fixtures/small_graphs.py
import networkx as nx
import pytest

@pytest.fixture
def karate_graph():
    """Zachary's karate club graph."""
    return nx.karate_club_graph()

@pytest.fixture
def path_graph():
    """Simple path graph for testing."""
    return nx.path_graph(5)

@pytest.fixture
def disconnected_graph():
    """Graph with multiple components."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (3, 4), (4, 5)])  # Two components
    return G
```

## Documentation Standards

### Documentation Types

#### API Documentation
Use Google-style docstrings:
```python
def crossover(parent1: Individual, parent2: Individual, 
              crossover_rate: float = 0.8) -> Tuple[Individual, Individual]:
    """
    Perform crossover between two parent individuals.
    
    This function implements uniform crossover where each gene has a 50%
    chance of coming from either parent. The crossover rate determines
    the probability that crossover actually occurs.
    
    Args:
        parent1: First parent individual
        parent2: Second parent individual  
        crossover_rate: Probability of performing crossover (0.0-1.0)
        
    Returns:
        Tuple containing two offspring individuals
        
    Raises:
        ValueError: If crossover_rate is not in [0, 1]
        TypeError: If parents are not Individual instances
        
    Example:
        >>> parent1 = Individual([1, 2, 3], [(1, 2)])
        >>> parent2 = Individual([2, 3, 4], [(2, 3)])
        >>> child1, child2 = crossover(parent1, parent2, 0.8)
        >>> print(f"Child 1 nodes: {child1.nodes}")
        
    Note:
        The offspring are guaranteed to satisfy the budget constraints
        even if parents violate them.
    """
```

#### Tutorial Documentation
```markdown
# Getting Started with Genetic Algorithm

This tutorial shows how to use the genetic algorithm for network disruption.

## Basic Usage

1. **Load a network:**
   ```python
   import networkx as nx
   G = nx.karate_club_graph()
   ```

2. **Configure the algorithm:**
   ```python
   from algorithms.genetic import GeneticAlgorithm
   ga = GeneticAlgorithm(
       population_size=50,
       max_generations=1000,
       mutation_rate=0.05
   )
   ```

3. **Run optimization:**
   ```python
   result = ga.run(G, k_nodes=3, k_edges=5)
   print(f"Best fitness: {result.fitness}")
   print(f"Removed nodes: {result.removed_nodes}")
   ```
```

#### Research Documentation
```markdown
# Algorithm Performance Analysis

## Experimental Setup

We evaluated the genetic algorithm on various network types:

- **Social networks**: Karate club, dolphins, football teams
- **Synthetic networks**: Barabási-Albert, Erdős-Rényi  
- **Infrastructure**: Power grids, transportation networks

## Results

| Network Type | Avg Fitness | Std Dev | Runtime (s) |
|-------------|-------------|---------|-------------|
| Social      | 23.4        | 3.2     | 12.5        |
| Synthetic   | 45.7        | 8.1     | 18.3        |
| Infrastructure | 67.2     | 12.4    | 24.7        |

## Statistical Analysis

The genetic algorithm significantly outperformed the greedy baseline
(p < 0.001, Wilcoxon signed-rank test).
```

## Dataset Contributions

### Adding New Datasets

#### Data Requirements
- **Format**: Supported edge list or adjacency format
- **Quality**: Connected graph, no self-loops or multi-edges
- **Documentation**: Source, properties, intended use
- **Size**: Consider computational requirements

#### Contribution Process
1. **Validate the dataset**
   ```python
   import networkx as nx
   
   # Load and validate
   G = nx.read_edgelist('new_network.txt')
   assert nx.is_connected(G), "Network must be connected"
   assert G.number_of_selfloops() == 0, "No self-loops allowed"
   ```

2. **Add to appropriate directory**
   ```bash
   cp new_network.txt inputs/
   ```

3. **Update documentation**
   ```markdown
   ### New Network (`new_network.txt`)
   - **Nodes**: 150
   - **Edges**: 300  
   - **Description**: Social network of research collaborations
   - **Source**: Smith et al. (2023)
   - **Properties**: Small-world, high clustering
   ```

4. **Add parser support if needed**
   ```python
   # In read_graph function, add new format handling
   elif sys.argv[1] in ["new_network.txt"]:
       # Custom parsing logic
       pass
   ```

### Dataset Quality Standards

#### Validation Checklist
- [ ] Single connected component
- [ ] No self-loops or multi-edges
- [ ] Consistent node labeling
- [ ] Reasonable size (10-10,000 nodes)
- [ ] Clear source attribution
- [ ] Documented properties

#### Metadata Template
```yaml
# datasets/metadata/network_name.yaml
name: "Network Name"
file: "network_file.txt"
nodes: 123
edges: 456
source: "Author et al. (Year)"
description: "Brief description of the network"
properties:
  - "scale-free"
  - "small-world"
  - "modular"
domain: "social"  # social, biological, infrastructure, synthetic
format: "edge_list"  # edge_list, adjacency_list, matrix_market
```

## Research Contributions

### Algorithm Research

#### New Algorithm Implementation
1. **Literature review**: Survey existing approaches
2. **Algorithm design**: Specify pseudocode and parameters
3. **Implementation**: Follow coding standards
4. **Evaluation**: Compare against existing methods
5. **Documentation**: Theoretical analysis and empirical results

#### Experimental Studies
```python
# experiments/parameter_sensitivity.py
"""Study of GA parameter sensitivity."""

import numpy as np
from algorithms.genetic import GeneticAlgorithm
from utils.experiment_runner import run_experiment

def population_size_study():
    """Evaluate effect of population size on performance."""
    sizes = [10, 20, 50, 100, 200]
    networks = load_test_networks()
    
    results = []
    for size in sizes:
        for network in networks:
            ga = GeneticAlgorithm(population_size=size)
            result = run_experiment(ga, network, runs=10)
            results.append({
                'population_size': size,
                'network': network.name,
                'fitness_mean': np.mean(result.fitness),
                'fitness_std': np.std(result.fitness)
            })
    
    return results
```

### Theoretical Analysis

#### Complexity Analysis
```markdown
## Computational Complexity

### Time Complexity
The genetic algorithm has time complexity O(G × P × (N + E)) where:
- G = number of generations
- P = population size  
- N = number of nodes
- E = number of edges

### Space Complexity
Space complexity is O(P × K) where K is the solution size (removed elements).

### Proof Sketch
Each generation requires:
1. Fitness evaluation: O(P × (N + E)) for connected components
2. Selection: O(P log P) for sorting
3. Crossover: O(P × K) for offspring generation
4. Mutation: O(1) for random changes
```

#### Convergence Analysis
```markdown
## Theoretical Properties

### Convergence Guarantee
Under the infinite population model, the genetic algorithm converges
to the global optimum with probability 1.

**Theorem**: Let f* be the global optimum fitness. Then:
P(f_t → f* as t → ∞) = 1

**Proof outline**: 
1. Selection preserves best individuals (elitism)
2. Mutation ensures reachability of all solutions
3. Infinite time allows exploration of entire space
```

## Issue Reporting

### Bug Reports

#### Required Information
```markdown
## Bug Report Template

**Environment**
- OS: [Windows 10/macOS/Linux]
- Python version: [3.8.5]
- NetworkX version: [2.6.3]
- Critical-GA version/commit: [abc123]

**Description**
Brief description of the bug.

**Steps to Reproduce**
1. Run command: `python connectivity_ga.py ...`
2. Observe error message
3. Check output files

**Expected Behavior**
What should happen instead.

**Actual Behavior**
What actually happened (include error messages).

**Additional Context**
- Network size and type
- Parameter values used
- Any modifications to code
```

#### Bug Report Examples

##### Performance Issue
```markdown
**Title**: GA performance degrades significantly on large networks

**Description**: 
Running GA on networks >1000 nodes causes excessive memory usage
and very slow execution.

**Environment**: Windows 10, Python 3.8, 16GB RAM

**Steps to Reproduce**:
1. `python connectivity_ga.py BarabasiAlbert_n1000m1.txt 1 0.05 0.03 100 3 0.8 0.05`
2. Monitor memory usage
3. Observe >5 minute execution time

**Expected**: Should complete within 2-3 minutes with <4GB memory
**Actual**: Takes >10 minutes, uses >8GB memory

**Proposed Solution**: Implement fitness caching or reduce population size automatically
```

### Feature Requests

#### Feature Request Template
```markdown
**Title**: Add multi-objective optimization support

**Description**:
Enable optimization of multiple objectives simultaneously (e.g., minimize
connectivity while maximizing network efficiency).

**Use Case**:
Research applications where trade-offs between multiple criteria are important.

**Proposed Implementation**:
- Add Pareto-based selection
- Implement NSGA-II algorithm
- Support weighted objective functions

**Additional Context**:
Would be useful for infrastructure network analysis where both
robustness and efficiency matter.
```

## Pull Request Process

### Before Submitting

#### Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] Branch is up-to-date with main

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Breaking change

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Screenshots (if applicable)
Include before/after comparisons for visual changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

#### What Reviewers Look For
1. **Correctness**: Does the code work as intended?
2. **Style**: Does it follow project conventions?
3. **Testing**: Are changes adequately tested?
4. **Documentation**: Are changes properly documented?
5. **Performance**: Does it maintain or improve performance?
6. **Maintainability**: Is the code readable and extensible?

#### Addressing Review Comments
```bash
# Make requested changes
git add .
git commit -m "Address review comments: improve error handling"
git push origin feature/your-feature-name
```

### Merge Requirements

#### Automated Checks
- [ ] All CI tests pass
- [ ] Code coverage maintained
- [ ] No merge conflicts
- [ ] Branch protection rules satisfied

#### Manual Review
- [ ] At least one approving review
- [ ] No unresolved review comments
- [ ] Maintainer approval for significant changes

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors.

#### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information without permission
- Other conduct inappropriate in a professional setting

#### Reporting Issues
Report unacceptable behavior to project maintainers. All complaints will be reviewed confidentially.

### Communication

#### Preferred Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Request Comments**: Code-specific discussions
- **Email**: Private/sensitive matters (maintainer contacts)

#### Communication Guidelines
- **Be specific**: Provide concrete examples and details
- **Be respectful**: Assume good intentions
- **Be patient**: Maintainers are often volunteers
- **Search first**: Check if your question was already answered

### Recognition

#### Contributors
All contributors are recognized in:
- README.md contributors section
- CONTRIBUTORS.md file (if created)
- Release notes for significant contributions
- Academic papers citing contributions (where appropriate)

#### Attribution
- Code contributions: Git commit history
- Documentation: Author attribution in files
- Research contributions: Co-authorship opportunities
- Dataset contributions: Source attribution

---

## Getting Started with Your First Contribution

Ready to contribute? Here's a quick start guide:

1. **Browse open issues** labeled "good first issue" or "help wanted"
2. **Comment on the issue** to express interest and get guidance
3. **Fork the repository** and create a feature branch
4. **Make your changes** following the guidelines above
5. **Test thoroughly** and document your changes
6. **Submit a pull request** with a clear description

### Example First Contributions

#### Easy Starter Tasks
- Fix typos in documentation
- Add type hints to functions
- Improve error messages
- Add parameter validation
- Write unit tests for existing functions

#### Medium Difficulty Tasks
- Implement new selection methods
- Add support for new file formats
- Optimize performance bottlenecks
- Create visualization enhancements
- Write comprehensive examples

#### Advanced Tasks
- Design new metaheuristic algorithms
- Implement parallel processing
- Add multi-objective optimization
- Create interactive web interface
- Conduct comprehensive benchmarking studies

---

Thank you for contributing to Critical-GA! Your efforts help advance research in network analysis and optimization.