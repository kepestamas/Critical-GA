from ast import Global
from itertools import count
from typing import Tuple
import networkx as nx
import random
import copy
import sys
from multiprocessing import Pool, cpu_count


from networkx.classes.function import neighbors
import numpy as np
import payoff_functions
from payoff_functions import get_payoff_function, list_payoff_functions
from graph_io import read_graph, get_node_weight, get_total_weight, print_graph_summary


# Global node weights dictionary for O(1) access
node_weights = {}


input = "inputs/" + sys.argv[1]
input_type = "split_list"
G, node_weights_loaded = read_graph(input, detect_weights=True)
node_weights = node_weights_loaded  # Always a dict now, with weight 1 for unweighted graphs
    
print_graph_summary(G, node_weights)

n = G.number_of_nodes()
m = G.number_of_edges()

# Calculate total weight budget for nodes
total_node_weight = get_total_weight(node_weights, G.nodes())
k_weight = int(total_node_weight * float(sys.argv[3]))  # total weight of nodes to remove
print(f"Total node weight: {total_node_weight}, Target weight to remove: {k_weight}")

k_edges = int(len(list(G.edges)) * float(sys.argv[4])) # number of edges to remove
pop_size = int(sys.argv[5])
gen_count = 5000
tournament_size = int(sys.argv[6]) # number of parents considered in crossover tournament
p_cross = float(sys.argv[7])
tournament_round_count = int(pop_size * p_cross * 0.5) # number of rounds in tournament
mutation_chance = float(sys.argv[8])

# Parse payoff function parameter (optional, default: 'pairwise')
if len(sys.argv) > 9:
    payoff_function_name = sys.argv[9]
else:
    payoff_function_name = 'pairwise'

# Validate and get payoff function
try:
    payoff_function = get_payoff_function(payoff_function_name)
    print(f"Using payoff function: {payoff_function_name}")
except ValueError as e:
    print(f"Error: {e}")
    print(f"Usage: python {sys.argv[0]} <input> <run_id> <node_frac> <edge_frac> <pop_size> <tournament_size> <p_cross> <p_mut> [payoff_function]")
    print(f"Available payoff functions: {', '.join(list_payoff_functions())}")
    sys.exit(1)

# Synchronize fitness count with payoff functions module
payoff_functions.fitness_count = 0
fitness_count = 0
mutation_count = max(int(k_weight / 10), 1)  # Adaptive based on weight budget

# Parallelization settings
N_PROCESSES = cpu_count() - 1 if cpu_count() > 1 else 1  # Leave one core free
USE_PARALLEL = True
PARALLEL_POOL = None  # Global pool to avoid recreation overhead

# max_fitness_count = 20000

# if sys.argv[1] in ["inf-USAir97.mtx", "inf-openflights.edges", "inf-euroroad.edges"]:
#     max_fitness_count = 10000000

output = "outputs/descending_mutation/ga/timing" + str(sys.argv[2]) + "_" + sys.argv[1] + "_ke_" + str(k_edges) + "_kw_" + str(k_weight) + "_" + payoff_function_name

node_dictionary = {}
for i,node in enumerate(list(G.nodes)):
    node_dictionary[i] = node

edge_dictionary = {}
for i,edge in enumerate(list(G.edges)):
    edge_dictionary[i] = edge

def serialize_graph_data(graph):
    """Extract picklable data from graph including node weights."""
    return (list(graph.edges()), list(graph.nodes()), node_weights)

def evaluate_individual_worker(args):
    """Worker function for parallel fitness evaluation."""
    individual, graph_edges, graph_nodes, weights, payoff_func_name = args
    
    # Make weights accessible in worker process
    global node_weights
    node_weights = weights
    
    # Reconstruct graph once (avoid deepcopy)
    G_worker = nx.Graph()
    G_worker.add_nodes_from(graph_nodes)
    G_worker.add_edges_from(graph_edges)
    
    # Remove nodes and edges directly (no deepcopy needed)
    G_worker.remove_nodes_from(individual[0])
    G_worker.remove_edges_from(individual[1])
    
    # Get payoff function and calculate
    payoff_func = get_payoff_function(payoff_func_name)
    result = payoff_func(nx.connected_components(G_worker))
    
    return (individual, result)

def parallel_fitness_batch(individuals, graph_data, payoff_func_name):
    """Evaluate multiple individuals in parallel."""
    global PARALLEL_POOL
    
    if not USE_PARALLEL or len(individuals) < 10:
        # Serial fallback for small batches
        results = []
        for ind in individuals:
            results.append((ind, fitness(ind)))
        return results
    
    # Create pool once if not exists
    if PARALLEL_POOL is None:
        PARALLEL_POOL = Pool(processes=N_PROCESSES)
    
    # Prepare arguments including weights
    graph_edges, graph_nodes, weights = graph_data
    args = [(ind, graph_edges, graph_nodes, weights, payoff_func_name) 
            for ind in individuals]
    
    # Parallel evaluation using persistent pool
    results = PARALLEL_POOL.map(evaluate_individual_worker, args)
    
    # Update fitness counter (approximate)
    payoff_functions.fitness_count += len(individuals)
    
    return results

def generate_pop():
    population = []
    for _ in range(pop_size):
        population.append(generate_one_pair())
    return population


def generate_one_pair():
    """
    Generate a random individual (node set, edge set) that respects weight constraints.
    Nodes are selected to have total weight close to k_weight (ideally exactly k_weight).
    """
    node_list = list(G.nodes)
    random.shuffle(node_list)
    
    # Select nodes with weight sum close to k_weight
    nodes = []
    current_weight = 0
    
    for node in node_list:
        node_weight_val = get_node_weight(node_weights, node)
        if current_weight + node_weight_val <= k_weight:
            nodes.append(node)
            current_weight += node_weight_val
            if current_weight == k_weight:
                break
    
    # If we haven't reached k_weight exactly, try to get closer
    # by replacing nodes if possible (greedy improvement)
    if current_weight < k_weight:
        remaining_budget = k_weight - current_weight
        available_nodes = [n for n in node_list if n not in nodes]
        for node in available_nodes:
            node_weight_val = get_node_weight(node_weights, node)
            if node_weight_val == remaining_budget:
                nodes.append(node)
                current_weight += node_weight_val
                break
            elif node_weight_val < remaining_budget:
                nodes.append(node)
                current_weight += node_weight_val
                remaining_budget = k_weight - current_weight

    edge_list = list(G.edges)
    edges = random.sample(edge_list, min(k_edges, len(edge_list)))

    return (nodes, edges)


def fitness(individual):
    """
    Evaluate fitness of an individual using the selected payoff function.
    
    Args:
        individual: Tuple of (nodes_to_remove, edges_to_remove)
        
    Returns:
        float: Fitness score (lower is better for all payoff functions)
    """
    P : nx.Graph = copy.deepcopy(G)
    P.remove_nodes_from(individual[0])
    P.remove_edges_from(individual[1])
    result = payoff_function(nx.connected_components(P))
    return result

def get_second(tuple):
    return tuple[1]

def mutate(individual): 
    """
    Mutate an individual by replacing nodes or edges.
    For nodes: maintains weight constraint (total weight ≈ k_weight).
    """
    new_individual = individual[0]
    if (float(sys.argv[3]) != 0 and random.random() <= 0.5) or float(sys.argv[4]) == 0: 
        print("Mutating nodes")
        # mutate node list with weight constraint
        if len(new_individual[0]) > 0:
            chosen_node = random.choice(new_individual[0])
            chosen_weight = get_node_weight(node_weights, chosen_node)
            new_individual[0].remove(chosen_node)
            
            # Try to find a replacement node with similar weight
            node_list = list(G.nodes)
            random.shuffle(node_list)
            
            # First try: exact weight match
            for new_node in node_list:
                if new_node not in new_individual[0]:
                    if get_node_weight(node_weights, new_node) == chosen_weight:
                        new_individual[0].append(new_node)
                        break
            
            # Second try: any available node (may change total weight slightly)
            if len(new_individual[0]) == len(individual[0]) - 1:  # Still missing a node
                for new_node in node_list:
                    if new_node not in new_individual[0]:
                        new_individual[0].append(new_node)
                        break
    else:  
        print("Mutating edges")
        # mutate edge list
        if len(new_individual[1]) > 0:
            chosen_edge = random.choice(new_individual[1])
            new_individual[1].remove(chosen_edge)
            new_edge = random.choice(list(G.edges))
            while new_edge in new_individual[1]:
                new_edge = random.choice(list(G.edges))
            new_individual[1].append(new_edge)
    return (new_individual, fitness(new_individual))

def actualize_mutation_count(current_gen, max_gen):
    global mutation_count
    half_gen = int(max_gen / 2)
    alfa = (half_gen - current_gen) / half_gen
    mutation_count = max(int((k_weight / 10) * alfa), 1)
    print(mutation_count)

def descending_mutation(individual):
    """
    Apply multiple mutations with weight-aware node replacement.
    """
    global mutation_count
    new_individual = individual[0]
    for _ in range(mutation_count):
        if (float(sys.argv[3]) != 0 and random.random() <= 0.5) or float(sys.argv[4]) == 0: 
            print("Mutating nodes")
            # mutate node list with weight constraint
            if len(new_individual[0]) > 0:
                chosen_node = random.choice(new_individual[0])
                chosen_weight = get_node_weight(node_weights, chosen_node)
                new_individual[0].remove(chosen_node)
                
                # Try to find replacement with similar weight
                node_list = list(G.nodes)
                random.shuffle(node_list)
                
                for new_node in node_list:
                    if new_node not in new_individual[0]:
                        if get_node_weight(node_weights, new_node) == chosen_weight:
                            new_individual[0].append(new_node)
                            break
                
                # Fallback: any node
                if len(new_individual[0]) < len(individual[0][0]):
                    for new_node in node_list:
                        if new_node not in new_individual[0]:
                            new_individual[0].append(new_node)
                            break
        else:  
            print("Mutating edges")
            # mutate edge list
            if len(new_individual[1]) > 0:
                chosen_edge = random.choice(new_individual[1])
                new_individual[1].remove(chosen_edge)
                new_edge = random.choice(list(G.edges))
                while new_edge in new_individual[1]:
                    new_edge = random.choice(list(G.edges))
                new_individual[1].append(new_edge)
    return (new_individual, fitness(new_individual))



def selection(evaluated_population):
    print("Selection")
    new_evaluated_population = evaluated_population.copy()
    # for pop in new_evaluated_population:
    #     print(len(set(pop[0][0])))

    new_evaluated_population = sorted(new_evaluated_population, key=get_second)
    new_evaluated_population = new_evaluated_population[0:pop_size]
    return new_evaluated_population

def split_node_lists(united_node_list):
    """
    Split united node list into two children, respecting weight constraints.
    Each child should have total weight close to k_weight.
    """
    first_child_nodes = []
    second_child_nodes = []
    random.shuffle(united_node_list)
    
    # First pass: assign nodes that appear twice to both children
    for node in united_node_list[:]:  # Use slice to avoid modification during iteration
        if united_node_list.count(node) == 2:
            first_child_nodes.append(node)
            second_child_nodes.append(node)
            while node in united_node_list:
                united_node_list.remove(node)
    
    # Second pass: distribute remaining nodes based on weight constraints
    first_weight = get_total_weight(node_weights, first_child_nodes)
    second_weight = get_total_weight(node_weights, second_child_nodes)
    
    for node in united_node_list:
        node_weight_val = get_node_weight(node_weights, node)
        
        # Assign to child that needs more weight (closer to k_weight)
        if first_weight + node_weight_val <= k_weight and (first_weight <= second_weight):
            first_child_nodes.append(node)
            first_weight += node_weight_val
        elif second_weight + node_weight_val <= k_weight:
            second_child_nodes.append(node)
            second_weight += node_weight_val
        else:
            # If neither can fit exactly, choose the one closer to target
            if abs((first_weight + node_weight_val) - k_weight) < abs((second_weight + node_weight_val) - k_weight):
                if first_weight + node_weight_val <= k_weight * 1.2:  # Allow 20% overflow
                    first_child_nodes.append(node)
                    first_weight += node_weight_val
            else:
                if second_weight + node_weight_val <= k_weight * 1.2:  # Allow 20% overflow
                    second_child_nodes.append(node)
                    second_weight += node_weight_val
    
    return first_child_nodes, second_child_nodes

def split_edge_lists(united_edge_list):
    first_child_edges = []
    second_child_edges = []
    random.shuffle(united_edge_list)
    for edge in united_edge_list:
        if united_edge_list.count(edge) == 2:
            first_child_edges.append(edge)
            second_child_edges.append(edge)
            while edge in united_edge_list:
                united_edge_list.remove(edge)    
    for edge in united_edge_list: 
        if True:
            if not edge in first_child_edges and len(first_child_edges) < k_edges:
                first_child_edges.append(edge)
            elif not edge in second_child_edges:
                second_child_edges.append(edge)

    
    return first_child_edges, second_child_edges

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


def tournament_round(evaluated_population):
    # print("Tournament round")
    current_contenders = random.sample(evaluated_population, tournament_size)
    # current_contenders = sorted(current_contenders, key=get_second)
    # current_contenders = current_contenders[0:2]
    current_contenders = find_min_from_contenders(current_contenders)


    united_node_list = current_contenders[0][0][0] + current_contenders[1][0][0]
    first_child_nodes, second_child_nodes = split_node_lists(united_node_list)

    united_edge_list = current_contenders[0][0][1] + current_contenders[1][0][1]
    first_child_edges, second_child_edges = split_edge_lists(united_edge_list)

    first_child = (first_child_nodes, first_child_edges)
    second_child = (second_child_nodes, second_child_edges)
    return first_child, second_child

def crossover_tournament(evaluated_population, graph_data=None, payoff_func_name=None):
    print("Tournament")
    
    # Generate all children first
    children = []
    for _ in range(tournament_round_count):
        first_child, second_child = tournament_round(evaluated_population)
        children.extend([copy.deepcopy(first_child), copy.deepcopy(second_child)])
    
    # Parallel evaluation
    if USE_PARALLEL and graph_data is not None:
        evaluated_child_population = parallel_fitness_batch(
            children, graph_data, payoff_func_name
        )
    else:
        evaluated_child_population = [(child, fitness(child)) for child in children]
    
    return evaluated_child_population

def average_connectivity(evaluated_population):
    summa = 0
    for individual in evaluated_population:
        summa = summa + individual[1]
    return summa / len(evaluated_population)

def cleanup_parallel_pool():
    """Close the parallel pool to free resources."""
    global PARALLEL_POOL
    if PARALLEL_POOL is not None:
        PARALLEL_POOL.close()
        PARALLEL_POOL.join()
        PARALLEL_POOL = None

def ga():
    print("Starting GA")
    population = generate_pop()
    
    # Serialize graph data once for parallel evaluation
    graph_data = serialize_graph_data(G)
    
    # Parallel evaluation of initial population
    if USE_PARALLEL:
        evaluated_population = parallel_fitness_batch(
            population, graph_data, payoff_function_name
        )
    else:
        evaluated_population = [(individual, fitness(individual)) 
                                for individual in population]
    
    print(population)
    f = open(output, "w+")
    for current_gen in range(gen_count):

        # print("Before crossover")
        # for pop in evaluated_population:
        #     if len(set(pop[0][0])) != 25:
        #         print("ERROR")
        evaluated_child_population = crossover_tournament(
            evaluated_population, graph_data, payoff_function_name
        )

        # print("Before mutation")
        # for pop in evaluated_population:
        #     if len(set(pop[0][0])) != 25:
        #         print("ERROR")
        actualize_mutation_count(current_gen, gen_count) #! for descending mutation
        if random.random() < mutation_chance:
            original_individual = random.choice(evaluated_child_population)
            # mutating_individual = mutate(original_individual)
            mutating_individual = descending_mutation(original_individual) #! for descending mutation
            evaluated_child_population.remove(original_individual)
            evaluated_child_population.append(mutating_individual)

        evaluated_population = evaluated_population + evaluated_child_population
        # print("Before selection")
        # for pop in evaluated_population:
        #     if len(set(pop[0][0])) != 25:
        #         print("ERROR")

        evaluated_population = selection(evaluated_population)
        # if current_gen % 10 == 0:
        # print("After all")
        # for pop in evaluated_population:
        #     if len(set(pop[0][0])) != 25:
        #         print("ERROR")
        
        print(str(current_gen) + " " + str(payoff_functions.get_fitness_count()))
        print(str(current_gen) + " " + str(average_connectivity(evaluated_population)))
        print(str(current_gen) + " " + str(evaluated_population[0][1]) + " " + str(evaluated_population[0][0]), file=f)

        # if fitness_count > max_fitness_count:
        #     break
    
    # Cleanup parallel resources
    cleanup_parallel_pool()


if __name__ == '__main__':
    print(list(G.nodes))
    ga()






