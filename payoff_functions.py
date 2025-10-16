"""
Payoff Functions for Critical Network Disruption Problem (CNDP)

This module provides interchangeable payoff functions for evaluating network
disruption effectiveness. All functions follow a standard interface and can be
used with both genetic algorithm and greedy algorithm implementations.

Functions:
    - pairwise_connectivity: Original pairwise connectivity measure
    - number_of_components: Maximize number of connected components
    - largest_component_size: Minimize size of largest component

All functions increment the global fitness_count variable for performance tracking.
"""

from typing import Iterator, Set, List, Dict, Callable
import networkx as nx

# Global fitness evaluation counter (shared across algorithms)
fitness_count = 0


def pairwise_connectivity(components: Iterator[Set]) -> float:
    """
    Calculate pairwise connectivity of network components.
    
    This is the original fitness function that measures the total number of
    possible connections within all connected components. Higher values indicate
    more connectivity (worse disruption).
    
    Args:
        components: Iterator of connected components from nx.connected_components()
        
    Returns:
        float: Sum of |C|*(|C|-1)/2 for all components C (lower is better)
        
    Example:
        >>> import networkx as nx
        >>> G = nx.path_graph(4)  # 0-1-2-3
        >>> G.remove_edge(1, 2)  # Split into [0,1] and [2,3]
        >>> components = nx.connected_components(G)
        >>> fitness = pairwise_connectivity(components)
        >>> print(fitness)  # 2.0 (1 + 1 from two components of size 2)
        
    Note:
        This function increments the global fitness_count variable.
        Formula: Σ(|C| * (|C| - 1) / 2) for components C with |C| > 1
    """
    global fitness_count
    fitness_count += 1
    
    total_connectivity = 0.0
    for component in components:
        size = len(component)
        if size > 1:
            # Calculate number of possible pairs in this component
            total_connectivity += size * (size - 1) / 2
    
    return total_connectivity


def number_of_components(components: Iterator[Set]) -> float:
    """
    Count the number of connected components (negated for minimization).
    
    This function encourages network fragmentation by maximizing the number
    of separate connected components. Since optimization algorithms minimize,
    we return the negative count.
    
    Args:
        components: Iterator of connected components from nx.connected_components()
        
    Returns:
        float: Negative count of components (more negative = better disruption)
        
    Example:
        >>> import networkx as nx
        >>> G = nx.path_graph(6)  # 0-1-2-3-4-5
        >>> G.remove_edges_from([(1,2), (3,4)])  # Split into 3 components
        >>> components = nx.connected_components(G)
        >>> fitness = number_of_components(components)
        >>> print(fitness)  # -3.0 (three components)
        
    Note:
        This function increments the global fitness_count variable.
        More components = more negative value = better fitness for minimization.
    """
    global fitness_count
    fitness_count += 1
    
    # Convert iterator to list to count components
    component_list = list(components)
    
    # Return negative count (more components = better disruption)
    return -len(component_list)


def largest_component_size(components: Iterator[Set]) -> float:
    """
    Find the size of the largest connected component.
    
    This function minimizes the size of the largest remaining component,
    encouraging balanced fragmentation rather than just creating small isolates.
    
    Args:
        components: Iterator of connected components from nx.connected_components()
        
    Returns:
        float: Size of largest component (smaller is better)
        
    Example:
        >>> import networkx as nx
        >>> G = nx.star_graph(5)  # Star with center 0 and leaves 1,2,3,4,5
        >>> G.remove_node(0)     # Remove center, leaves 5 isolated nodes
        >>> components = nx.connected_components(G)
        >>> fitness = largest_component_size(components)
        >>> print(fitness)  # 1.0 (largest component has size 1)
        
    Note:
        This function increments the global fitness_count variable.
        Returns 0 if no components exist (empty graph).
    """
    global fitness_count
    fitness_count += 1
    
    # Convert iterator to list to find maximum
    component_list = list(components)
    
    if not component_list:
        return 0.0
    
    # Find the size of the largest component
    max_size = max(len(component) for component in component_list)
    
    return float(max_size)


# Function registry for easy lookup and validation
PAYOFF_FUNCTIONS: Dict[str, Callable[[Iterator[Set]], float]] = {
    'pairwise': pairwise_connectivity,
    'components': number_of_components,
    'largest': largest_component_size
}


def get_payoff_function(function_name: str) -> Callable[[Iterator[Set]], float]:
    """
    Get a payoff function by name.
    
    Args:
        function_name: Name of the payoff function ('pairwise', 'components', 'largest')
        
    Returns:
        Callable: The requested payoff function
        
    Raises:
        ValueError: If function_name is not recognized
        
    Example:
        >>> payoff_func = get_payoff_function('components')
        >>> # Use payoff_func(components) in fitness evaluation
    """
    if function_name not in PAYOFF_FUNCTIONS:
        available = ', '.join(PAYOFF_FUNCTIONS.keys())
        raise ValueError(f"Unknown payoff function '{function_name}'. Available: {available}")
    
    return PAYOFF_FUNCTIONS[function_name]


def list_payoff_functions() -> List[str]:
    """
    Get list of available payoff function names.
    
    Returns:
        List[str]: Names of available payoff functions
    """
    return list(PAYOFF_FUNCTIONS.keys())


def reset_fitness_count() -> int:
    """
    Reset the global fitness counter and return the previous value.
    
    Returns:
        int: Previous fitness count before reset
        
    Note:
        This is useful for benchmarking and performance analysis.
    """
    global fitness_count
    previous_count = fitness_count
    fitness_count = 0
    return previous_count


def get_fitness_count() -> int:
    """
    Get the current global fitness evaluation count.
    
    Returns:
        int: Number of fitness evaluations performed
    """
    global fitness_count
    return fitness_count


# Aliases for backward compatibility
pairwise = pairwise_connectivity  # For compatibility with connectivity_ga.py
f_pairwise = pairwise_connectivity  # For compatibility with connectivity_greedy.py


if __name__ == "__main__":
    """
    Demonstration and testing of payoff functions.
    """
    import networkx as nx
    
    print("=== Payoff Functions Demo ===")
    
    # Create test network
    G = nx.karate_club_graph()
    print(f"Original network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Remove some nodes to create disruption
    nodes_to_remove = [0, 33]  # Remove high-degree nodes
    G_modified = G.copy()
    G_modified.remove_nodes_from(nodes_to_remove)
    
    print(f"After removing nodes {nodes_to_remove}:")
    print(f"  Modified network: {G_modified.number_of_nodes()} nodes, {G_modified.number_of_edges()} edges")
    
    # Test all payoff functions
    components = list(nx.connected_components(G_modified))
    print(f"  Number of components: {len(components)}")
    print(f"  Component sizes: {[len(c) for c in components]}")
    
    # Reset counter for clean demo
    reset_fitness_count()
    
    for func_name, func in PAYOFF_FUNCTIONS.items():
        # Need to recreate components iterator for each function
        components_iter = nx.connected_components(G_modified)
        fitness = func(components_iter)
        print(f"  {func_name:12s}: {fitness:8.2f}")
    
    print(f"Total fitness evaluations: {get_fitness_count()}")
    
    print("\n=== Function Registry Test ===")
    print(f"Available functions: {list_payoff_functions()}")
    
    try:
        func = get_payoff_function('nonexistent')
    except ValueError as e:
        print(f"Error handling works: {e}")