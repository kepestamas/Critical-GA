import os
from collections import Counter
import networkx as nx
import random
import copy
import sys
from multiprocessing import Pool, cpu_count


import numpy as np
import payoff_functions
from payoff_functions import get_payoff_function, list_payoff_functions
from graph_io import read_graph, get_node_weight, get_total_weight, print_graph_summary


# Global node weights dictionary for O(1) access
node_weights = {}


input = "inputs/" + sys.argv[1]
G, node_weights_loaded = read_graph(input, detect_weights=True)
node_weights = node_weights_loaded  # Always a dict now, with weight 1 for unweighted graphs
    
print_graph_summary(G, node_weights)

n = G.number_of_nodes()
m = G.number_of_edges()

# Node and edge removal parameters (count-based)
k_nodes = int(len(list(G.nodes)) * float(sys.argv[3]))  # number of nodes to remove
print(f"Nodes to remove: {k_nodes}")

k_edges = int(len(list(G.edges)) * float(sys.argv[4]))  # number of edges to remove
print(f"Edges to remove: {k_edges}")

# Weight budget constraint for nodes
total_node_weight = get_total_weight(node_weights, G.nodes())
weight_budget = float(sys.argv[5])  # budget as fraction of total weight
k_weight_budget = int(total_node_weight * weight_budget)  # maximum allowed weight sum
print(f"Total node weight: {total_node_weight}, Weight budget: {k_weight_budget} ({weight_budget*100:.1f}%)")

pop_size = int(sys.argv[6])
tournament_size = int(sys.argv[7])  # number of parents considered in crossover tournament
p_cross = float(sys.argv[8])
#not used - tournament_round_count = int(pop_size * p_cross * 0.5)  # number of rounds in tournament
mutation_chance = float(sys.argv[9])
mutation_type = int(sys.argv[12]) if len(sys.argv) > 12 else 0  # 0 for standard mutation, 1 for descending mutation
max_switch_pct = int(sys.argv[13]) if len(sys.argv) > 13 else 50  # max crossover switches as percentage of k_nodes

# Parse payoff function parameter (optional, default: 'pairwise')
if len(sys.argv) > 10:
    payoff_function_name = sys.argv[10]
else:
    payoff_function_name = 'pairwise'

# Parse generation count parameter (optional, default: 5000)
if len(sys.argv) > 11:
    gen_count = int(sys.argv[11])
else:
    gen_count = 5000

print(f"Generation count: {gen_count}")

# Validate and get payoff function
try:
    payoff_function = get_payoff_function(payoff_function_name)
    print(f"Using payoff function: {payoff_function_name}")
except ValueError as e:
    print(f"Error: {e}")
    print(f"Usage: python {sys.argv[0]} <input> <run_id> <node_frac> <edge_frac> <weight_budget> <pop_size> <tournament_size> <p_cross> <p_mut> [payoff_function] [gen_count]")
    print(f"Available payoff functions: {', '.join(list_payoff_functions())}")
    sys.exit(1)

# Synchronize fitness count with payoff functions module
payoff_functions.fitness_count = 0
mutation_count = max(int((k_nodes + k_edges) / 4), 1)  # Adaptive based on node/edge count

# Parallelization settings
#N_PROCESSES = cpu_count() - 1 if cpu_count() > 1 else 1  # Leave one core free
N_PROCESSES = cpu_count()//2 if cpu_count() > 1 else 1  # Leave half of the cores free to avoid overloading
USE_PARALLEL = True
PARALLEL_POOL = None  # Global pool to avoid recreation overhead

# max_fitness_count = 20000

# if sys.argv[1] in ["inf-USAir97.mtx", "inf-openflights.edges", "inf-euroroad.edges"]:
#     max_fitness_count = 10000000

# Extract basename from input file to avoid path separators in output filename
input_basename = os.path.basename(sys.argv[1])
# Remove file extension for cleaner output filenames
input_basename_clean = os.path.splitext(input_basename)[0]
output = "outputs/descending_mutation/ga/timing" + str(sys.argv[2]) + "_" + input_basename_clean + "_ke_" + str(k_edges) + "_kn_" + str(k_nodes) + "_wb_" + str(weight_budget) + "_" + payoff_function_name
os.makedirs(os.path.dirname(output), exist_ok=True)

# Precomputed node/edge lists for fitness evaluation (G never changes)
_G_nodes = list(G.nodes)
_G_edges = list(G.edges)

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
    Generate a random individual (node set, edge set) that respects constraints.
    - Exactly k_nodes nodes must be selected
    - Total weight of selected nodes must not exceed k_weight_budget
    """
    node_list = list(G.nodes)
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        random.shuffle(node_list)
        nodes = []
        current_weight = 0
        
        # Try to select exactly k_nodes nodes within budget
        for node in node_list:
            if len(nodes) >= k_nodes:
                break
            node_weight_val = get_node_weight(node_weights, node)
            if current_weight + node_weight_val <= k_weight_budget:
                nodes.append(node)
                current_weight += node_weight_val
        
        # Check if we successfully got k_nodes within budget
        if len(nodes) == k_nodes:
            edge_list = list(G.edges)
            edges = random.sample(edge_list, min(k_edges, len(edge_list)))
            return (nodes, edges)
    
    # Fallback: if we can't satisfy constraints, select k lightest nodes
    # This ensures we always return a valid individual
    node_list_sorted = sorted(node_list, key=lambda n: get_node_weight(node_weights, n))
    nodes = node_list_sorted[:k_nodes]
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
    P = nx.Graph()
    P.add_nodes_from(_G_nodes)
    P.add_edges_from(_G_edges)
    P.remove_nodes_from(individual[0])
    P.remove_edges_from(individual[1])
    result = payoff_function(nx.connected_components(P))
    return result

def get_second(tuple):
    return tuple[1]

def mutate_no_fitness(individual): 
    """
    Mutate an individual by replacing nodes or edges.
    For nodes: maintains k_nodes count and respects k_weight_budget constraint.
    """
    new_individual = (list(individual[0][0]), list(individual[0][1]))
    if (k_nodes > 0 and random.random() <= 0.5) or k_edges == 0: 
        print("Mutating nodes")
        # mutate node list with budget constraint
        if len(new_individual[0]) > 0:
            chosen_node = random.choice(new_individual[0])
            chosen_weight = get_node_weight(node_weights, chosen_node)
            new_individual[0].remove(chosen_node)
            
            # Calculate current weight without the removed node
            current_weight = get_total_weight(node_weights, new_individual[0])
            remaining_budget = k_weight_budget - current_weight
            
            # Try to find a replacement node that fits within budget
            node_list = list(G.nodes)
            random.shuffle(node_list)
            
            # Select a node with weight <= remaining_budget
            for new_node in node_list:
                if new_node not in new_individual[0]:
                    new_weight = get_node_weight(node_weights, new_node)
                    if new_weight <= remaining_budget:
                        new_individual[0].append(new_node)
                        break
    else:  
        print("Mutating edges")
        # mutate edge list
        if len(new_individual[1]) > 0:
            chosen_edge = random.choice(new_individual[1])
            new_individual[1].remove(chosen_edge)
            new_edge = random.choice(_G_edges)
            while new_edge in new_individual[1]:
                new_edge = random.choice(_G_edges)
            new_individual[1].append(new_edge)
    return new_individual

def mutate(individual): 
    """
    Mutate an individual by replacing nodes or edges.
    For nodes: maintains k_nodes count and respects k_weight_budget constraint.
    """
    new_individual = mutate_no_fitness(individual)
    return (new_individual, fitness(new_individual))

def actualize_mutation_count(current_gen, max_gen):
    global mutation_count
    half_gen = int(max_gen / 2)
    alfa = (half_gen - current_gen) / half_gen
    mutation_count = max(int(((k_nodes + k_edges) / 4) * alfa), 1)
    print(mutation_count)

def descending_mutation(individual):
    """
    Apply multiple mutations maintaining k_nodes count and k_weight_budget constraint.
    """
    global mutation_count
    current = individual[0]  # Extract (nodes, edges) from ((nodes, edges), fitness)
    for _ in range(mutation_count):
        current = mutate_no_fitness((current, 0))  # Wrap with dummy fitness for mutate_no_fitness
    return (current, fitness(current))

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
    Randomly distribute nodes between two children, then do 1:1 switches
    between exclusive child nodes until weight criteria is satisfied or max switches reached.
    
    Works with 3 lists: common, excl1, excl2. Switches happen only between
    exclusive lists, then joined with common at the end.
    
    Returns:
        (first_child_nodes, second_child_nodes, weight_satisfied)
    """
    # Separate common nodes (in both parents) from unique nodes
    seen = set()
    common_nodes = []
    remaining_nodes = []
    for node in united_node_list:
        if node in seen:
            common_nodes.append(node)
        else:
            seen.add(node)
            remaining_nodes.append(node)
    
    # Randomly distribute unique nodes into two exclusive lists
    random.shuffle(remaining_nodes)
    need = k_nodes - len(common_nodes)
    excl1 = remaining_nodes[:need]
    excl2 = remaining_nodes[need:need + need]
    
    common_weight = get_total_weight(node_weights, common_nodes)
    excl1_weight = get_total_weight(node_weights, excl1)
    excl2_weight = get_total_weight(node_weights, excl2)
    
    # 1:1 switches between exclusive lists to satisfy weight constraint
    max_switches = max(int(k_nodes * max_switch_pct / 100), 1)
    
    for _ in range(max_switches):
        w1 = common_weight + excl1_weight
        w2 = common_weight + excl2_weight
        
        if w1 <= k_weight_budget and w2 <= k_weight_budget:
            return common_nodes + excl1, common_nodes + excl2, True
        
        if not excl1 or not excl2:
            break
        
        # Identify overweight side
        if w1 > k_weight_budget:
            over, under = excl1, excl2
        else:
            over, under = excl2, excl1
        
        # Swap heaviest from overweight with lightest from underweight
        over.sort(key=lambda n: get_node_weight(node_weights, n), reverse=True)
        under.sort(key=lambda n: get_node_weight(node_weights, n))
        
        heavy_w = get_node_weight(node_weights, over[0])
        light_w = get_node_weight(node_weights, under[0])
        over[0], under[0] = under[0], over[0]
        
        # Incrementally update exclusive weights
        if over is excl1:
            excl1_weight = excl1_weight - heavy_w + light_w
            excl2_weight = excl2_weight - light_w + heavy_w
        else:
            excl2_weight = excl2_weight - heavy_w + light_w
            excl1_weight = excl1_weight - light_w + heavy_w
    
    # Final check using already-tracked weights
    weight_satisfied = ((common_weight + excl1_weight) <= k_weight_budget and 
                        (common_weight + excl2_weight) <= k_weight_budget)
    
    return common_nodes + excl1, common_nodes + excl2, weight_satisfied

def split_edge_lists(united_edge_list):
    first_child_edges = []
    second_child_edges = []
    
    # Separate common edges (in both parents) from unique edges using Counter - O(n)
    edge_counts = Counter(united_edge_list)
    common_edges = [e for e, c in edge_counts.items() if c >= 2]
    unique_edges = [e for e, c in edge_counts.items() if c == 1]
    
    # Common edges go to both children
    first_child_edges = list(common_edges)
    second_child_edges = list(common_edges)
    
    # Randomly distribute unique edges
    random.shuffle(unique_edges)
    for edge in unique_edges:
        if len(first_child_edges) < k_edges:
            first_child_edges.append(edge)
        elif len(second_child_edges) < k_edges:
            second_child_edges.append(edge)
    
    return first_child_edges, second_child_edges

def find_min_from_contenders(contenders):
    min_val1, min_val2 = float('inf'), float('inf')
    min1, min2 = None, None
    for contender in contenders:
        if contender[1] < min_val1:
            min2, min_val2 = min1, min_val1
            min1, min_val1 = contender, contender[1]
        elif contender[1] < min_val2:
            min2, min_val2 = contender, contender[1]
    return [min1, min2]


def tournament_round(evaluated_population):
    # print("Tournament round")
    current_contenders = random.sample(evaluated_population, tournament_size)
    # current_contenders = sorted(current_contenders, key=get_second)
    # current_contenders = current_contenders[0:2]
    current_contenders = find_min_from_contenders(current_contenders)

    parent1 = current_contenders[0]
    parent2 = current_contenders[1]

    ###### sulyproblemak ellenorzese ######
    united_node_list = parent1[0][0] + parent2[0][0]
    first_child_nodes, second_child_nodes, weight_ok = split_node_lists(united_node_list)

    united_edge_list = parent1[0][1] + parent2[0][1]
    first_child_edges, second_child_edges = split_edge_lists(united_edge_list)

    if not weight_ok:
        # Fallback: one child from lightest k_nodes, other child is a parent
        all_nodes_sorted = sorted(list(G.nodes), key=lambda n: get_node_weight(node_weights, n))
        lightest_nodes = all_nodes_sorted[:k_nodes]
        edge_list = list(G.edges)
        lightest_edges = random.sample(edge_list, min(k_edges, len(edge_list)))

        first_child = (lightest_nodes, lightest_edges)
        parent_choice = random.choice([parent1, parent2])
        second_child = copy.deepcopy(parent_choice[0])
    else:
        first_child = (first_child_nodes, first_child_edges)
        second_child = (second_child_nodes, second_child_edges)

    return first_child, second_child

def crossover_tournament(evaluated_population, graph_data=None, payoff_func_name=None):
    print("Tournament")
    
    # Generate all children first
    children = []

    ####### p_cross a veletlenszam feltetele!!!!! #######
    # EZ MAR A FOPROGRAMBAN MEGVAN!
    # if (p_cross != 0 and random.random() <= 0.5):
        #for _ in range(tournament_round_count):
    first_child, second_child = tournament_round(evaluated_population)
    children.extend([first_child, second_child])

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
        evaluated_child_population = []
        for _ in range(len(evaluated_population) // tournament_size):
            if random.random() < p_cross:
                new_children = crossover_tournament(
                    evaluated_population, graph_data, payoff_function_name
                )
                evaluated_child_population.extend(new_children)

        # print("Before mutation")
        # for pop in evaluated_population:
        #     if len(set(pop[0][0])) != 25:
        #         print("ERROR")
        if mutation_chance > 0 and evaluated_child_population:
            if mutation_type == 1:
                actualize_mutation_count(current_gen, gen_count) #! for descending mutation
            for i in range(len(evaluated_child_population)):
                if random.random() < mutation_chance:
                    idx = random.randrange(len(evaluated_child_population))
                    original_individual = evaluated_child_population[idx]
                    # 0 for standard mutation, 1 for descending mutation - sys.argv[12] is passed from runner.py to control mutation type
                    if mutation_type == 0:          
                        mutating_individual = mutate(original_individual)
                    else:
                        mutating_individual = descending_mutation(original_individual) #! for descending mutation
                    evaluated_child_population[idx] = mutating_individual

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
        
        # For components payoff function, display the actual number of components (negative of fitness)
        # This makes the output more intuitive: 3 components instead of -3.0
        if payoff_function_name == 'components':
            display_fitness = -evaluated_population[0][1]
        else:
            display_fitness = evaluated_population[0][1]
            
        print(str(current_gen) + " " + str(display_fitness) + " " + str(evaluated_population[0][0]), file=f)

        # if fitness_count > max_fitness_count:
        #     break
    
    # Cleanup parallel resources
    cleanup_parallel_pool()
    f.close()
    print(f"FINAL_FITNESS_COUNT={payoff_functions.get_fitness_count()}")


if __name__ == '__main__':
    print(list(G.nodes))
    ga()






