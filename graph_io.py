"""
Graph I/O utilities for Critical-GA project.

This module provides centralized graph reading functionality with support for:
- Weighted graph formats (cor_*, bog_*, mac_*)
- Standard unweighted formats
- Node weight management

All graph I/O operations should use this module for consistency.
"""

import networkx as nx
import os
import sys
from typing import Tuple, Dict, Optional


def read_graph(input_path: str, detect_weights: bool = True) -> Tuple[nx.Graph, Dict]:
    """
    Read graph from file with automatic format detection.
    
    Supported weighted formats:
    - cor_* files: Line 0: n nodes, Lines 1-n: "node: neighbors", Lines n+1-2n: "node: weight"
    - bog_* files: Same format as cor_*
    - mac_* files: Line 0: n nodes, Line 1: m edges, Lines 2-m+1: edges, Lines m+2-m+n+1: weights
    
    Supported unweighted formats:
    - BarabasiAlbert, ErdosRenyi, ForestFire: Adjacency list with node count header
    - Standard edge lists: tab or space separated
    - Character-based adjacency lists
    
    For unweighted graphs, all nodes are assigned weight 1 by default.
    
    Args:
        input_path: Full path to graph file
        detect_weights: Whether to parse and return node weights (default: True)
    
    Returns:
        tuple: (Graph, node_weights_dict) where node_weights_dict always contains weights.
               For unweighted graphs, all nodes have weight 1.
               If detect_weights=False, returns empty dict {}.
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        IOError: If file cannot be read
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Graph file not found: {input_path}")
    
    G = nx.Graph()
    node_weights = {} if detect_weights else None
    filename = os.path.basename(input_path)
    
    # Read file
    with open(input_path, "r") as f:
        lines = f.readlines()
    
    # Weighted graph formats: cor_*, bog_*, hos_*, mac_*
    if detect_weights and (filename.startswith('cor_') or filename.startswith('bog_') or filename.startswith('hos_')):
        # Format: adjacency list + weights
        # Line 0: number of nodes
        # Lines 1 to n: node: neighbor1 neighbor2 ...
        # Lines n+1 to 2n: node: weight
        n = int(lines[0].strip())
        
        # Parse adjacency list (lines 1 to n)
        for i in range(1, n + 1):
            if i < len(lines) and ':' in lines[i]:
                parts = lines[i].split(':')
                node = parts[0].strip()
                if len(parts) > 1 and parts[1].strip():
                    neighbors = parts[1].strip().split()
                    for neighbor in neighbors:
                        G.add_edge(node, neighbor)
        
        # Parse weights (lines n+1 to 2n)
        for i in range(n + 1, 2*n + 1):
            if i < len(lines) and ':' in lines[i]:
                parts = lines[i].split(':')
                node = parts[0].strip()
                weight = int(parts[1].strip())
                node_weights[node] = weight
        
        return G, node_weights
    
    elif detect_weights and filename.startswith('mac_'):
        # Format: edge list + weights
        # Line 0: number of nodes
        # Line 1: number of edges
        # Lines 2 to m+1: node1 node2
        # Lines m+2 to m+n+1: weight (one per node, indexed 0 to n-1)
        n = int(lines[0].strip())
        m = int(lines[1].strip())
        
        # Parse edges (lines 2 to m+1)
        for i in range(2, m + 2):
            if i < len(lines):
                parts = lines[i].strip().split()
                if len(parts) >= 2:
                    G.add_edge(parts[0].strip(), parts[1].strip())
        
        # Parse weights (lines m+2 to m+n+1)
        for i in range(m + 2, m + n + 2):
            if i < len(lines):
                weight = int(lines[i].strip())
                node_id = str(i - m - 2)
                node_weights[node_id] = weight
        
        return G, node_weights
    
    # Unweighted graph formats
    if filename in ["BarabasiAlbert_n500m1.txt", "BarabasiAlbert_n1000m1.txt", 
                    "ErdosRenyi_n250.txt", "ErdosRenyi_n500.txt", 
                    "ForestFire_n250.txt", "ForestFire_n500.txt", 
                    "WattsStrogatz_n250.txt", "WattsStrogatz_n500.txt"]:
        # Skip first line (node count), then parse adjacency list
        lines = lines[1:]
        split_lines = [line.replace("\n", "").split(":") for line in lines]
        for line in split_lines:
            if len(line) >= 2:
                a = line[0]
                neighbors = line[1].split(" ")[1:-1]
                for neighbor in neighbors:
                    if neighbor:  # Skip empty strings
                        G.add_edge(a, neighbor)
    
    elif filename in ["out.as20000102", "ia-infect-dublin.mtx", "ia-infect-hyper.mtx",
                     "power-494-bus.mtx", "power-662-bus.mtx", 
                     "bn-cat-mixed-species_brain_1.edges", "bn-fly-drosophila_medulla_1.edges",
                     "bn-mouse_retina_1.edges", "bn-mouse_visual-cortex_2.edges",
                     "hamster.txt", "football.txt", "dolphins.txt", "karate.txt", "zebra.txt",
                     "inf-USAir97.mtx", "inf-openflights.edges", "inf-euroroad.edges",
                     "eco-foodweb-baywet.edges", "road-minnesota.mtx", "out.loc-brightkite_edges"]:
        # Standard edge list format: space or tab separated
        for line in lines:
            split_line = line.replace("\n", "").replace("\t", " ").split(" ")
            if len(split_line) >= 2:
                node1, node2 = split_line[0], split_line[1]
                if node1 and node2:  # Skip empty strings
                    G.add_edge(node1, node2)
    
    elif filename in ["humanDiseasome.txt", "Ecoli.txt", "Circuit.txt", "Bovine.txt"]:
        # Character-based adjacency list
        split_lines = [line.replace("\n", "").split(" ") for line in lines]
        for line in split_lines:
            if len(line) >= 2:
                a = line[0]
                neighbors = line[1]
                for neighbor in neighbors:
                    if neighbor:  # Skip empty strings
                        G.add_edge(a, neighbor)
    
    else:
        # Generic fallback: try edge list format
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                G.add_edge(parts[0], parts[1])
    
    # For unweighted graphs, assign weight 1 to all nodes
    if detect_weights and len(node_weights) == 0:
        for node in G.nodes():
            node_weights[node] = 1
    
    # Return weights dictionary (empty if detect_weights=False, populated otherwise)
    return G, node_weights


def get_node_weight(node_weights: Optional[Dict], node_id, default: int = 1) -> int:
    """
    Get weight of a node. O(1) operation.
    
    Args:
        node_weights: Dictionary of node weights (can be None or empty)
        node_id: Node identifier (string or int)
        default: Default weight for unweighted nodes (default: 1)
    
    Returns:
        int: Weight of the node, or default if not found
    
    Example:
        >>> weights = {'0': 5, '1': 3}
        >>> get_node_weight(weights, '0')
        5
        >>> get_node_weight(weights, '2')
        1
        >>> get_node_weight(None, '0')
        1
        >>> get_node_weight({}, '0')
        1
    """
    if node_weights is None or len(node_weights) == 0:
        return default
    return node_weights.get(node_id, default)


def get_total_weight(node_weights: Optional[Dict], nodes, default: int = 1) -> int:
    """
    Get total weight of a collection of nodes. O(n) operation.
    
    Args:
        node_weights: Dictionary of node weights (can be None or empty)
        nodes: Iterable of node identifiers
        default: Default weight for unweighted nodes (default: 1)
    
    Returns:
        int: Sum of weights for all nodes
    
    Example:
        >>> weights = {'0': 5, '1': 3, '2': 2}
        >>> get_total_weight(weights, ['0', '1'])
        8
        >>> get_total_weight(None, ['0', '1', '2'])
        3
        >>> get_total_weight({}, ['0', '1', '2'])
        3
    """
    if node_weights is None or len(node_weights) == 0:
        # For unweighted graphs, return count of nodes
        return len(list(nodes)) * default
    
    return sum(get_node_weight(node_weights, node, default) for node in nodes)


def print_graph_summary(G: nx.Graph, node_weights: Optional[Dict] = None, verbose: bool = True) -> None:
    """
    Print summary information about loaded graph.
    
    Args:
        G: NetworkX graph
        node_weights: Optional node weights dictionary
        verbose: Whether to print detailed information (default: True)
    
    Example output:
        Loaded 34 nodes, 78 edges
        Loaded unweighted graph (all nodes weight 1)
        
        OR
        
        Loaded 50 nodes, 120 edges
        Loaded 50 node weights (range: 1-10)
    """
    if not verbose:
        return
    
    if node_weights and len(node_weights) > 0:
        weight_values = list(node_weights.values())
        weight_min = min(weight_values)
        weight_max = max(weight_values)
        
        # Check if all weights are 1 (unweighted graph with default weights)
        if weight_min == 1 and weight_max == 1:
            print("Loaded unweighted graph (all nodes weight 1)")
        else:
            print(f"Loaded {len(node_weights)} node weights (range: {weight_min}-{weight_max})")
    else:
        print("Loaded unweighted graph")


# Backward compatibility: module-level node_weights for legacy code
# NOTE: This will be deprecated in future versions
# New code should pass node_weights as parameters instead of using global state
_legacy_node_weights = {}


def get_legacy_node_weight(node_id, default: int = 1) -> int:
    """
    Legacy function for backward compatibility.
    Uses module-level _legacy_node_weights dictionary.
    
    DEPRECATED: Use get_node_weight(node_weights, node_id) instead.
    """
    return get_node_weight(_legacy_node_weights, node_id, default)


def get_legacy_total_weight(nodes, default: int = 1) -> int:
    """
    Legacy function for backward compatibility.
    Uses module-level _legacy_node_weights dictionary.
    
    DEPRECATED: Use get_total_weight(node_weights, nodes) instead.
    """
    return get_total_weight(_legacy_node_weights, nodes, default)
