from ast import Global
from itertools import count
from typing import Tuple
import networkx as nx
import random
import copy
import sys


from networkx.classes.function import neighbors
from numpy import infty


def read_graph(input, input_type):
    G = nx.Graph()
    f = open(input, "r")
    if sys.argv[1] in ["BarabasiAlbert_n500m1.txt","BarabasiAlbert_n1000m1.txt","ErdosRenyi_n250.txt","ErdosRenyi_n500.txt","ForestFire_n250.txt","ForestFire_n500.txt"]:
        lines = f.readlines()
        lines = lines[1:]
        split_lines = [line.replace("\n","").split(":") for line in lines]
        for line in split_lines:
            a = line[0]
            neighbors = line[1].split(" ")[1:-1]
            for neighbor in neighbors:
                G.add_edge(a,neighbor)
    elif sys.argv[1] in ["out.as20000102","ia-infect-dublin.mtx", "ia-infect-hyper.mtx","power-494-bus.mtx","power-662-bus.mtx","bn-cat-mixed-species_brain_1.edges","hamster.txt", "football.txt", "dolphins.txt", "karate.txt", "zebra.txt", "inf-USAir97.mtx", "inf-openflights.edges", "inf-euroroad.edges", "bn-mouse_visual-cortex_2.edges"]:
        lines = f.readlines()
        for line in lines:
            split_line = line.replace("\n","").replace("\t"," ").split(" ")
            G.add_edge(split_line[0],split_line[1])
    elif sys.argv[1] in ["humanDiseasome.txt", "Ecoli.txt", "Circuit.txt", "Bovine.txt"]:
        lines = f.readlines()
        split_lines = [line.replace("\n","").split(" ") for line in lines]
        for line in split_lines:
            a = line[0]
            neighbors = line[1]
            for neighbor in neighbors:
                G.add_edge(a,neighbor)
    return G


input = "inputs/" + sys.argv[1]
input_type = "split_list"
G : nx.Graph = read_graph(input, input_type)
n = G.number_of_nodes()
m = G.number_of_edges()
k_nodes = int(len(list(G.nodes)) * float(sys.argv[3])) # number of nodes to remove
print(k_nodes)
k_edges = int(len(list(G.edges)) * float(sys.argv[4])) # number of edges to remove
pop_size = int(sys.argv[5])
gen_count = 5000
tournament_size = int(sys.argv[6]) # number of parents considered in crossover tournament
p_cross = float(sys.argv[7])
tournament_round_count = int(pop_size * p_cross * 0.5) # number of rounds in tournament
mutation_chance = float(sys.argv[8])
fitness_count = 0
mutation_count = int((k_nodes + k_edges)/4)

# max_fitness_count = 20000

# if sys.argv[1] in ["inf-USAir97.mtx", "inf-openflights.edges", "inf-euroroad.edges"]:
#     max_fitness_count = 10000000

output = "outputs/descending_mutation/ga/timing" + str(sys.argv[2]) + "_" + sys.argv[1] + "_ke_" + str(k_edges) + "_kn_" + str(k_nodes)

node_dictionary = {}
for i,node in enumerate(list(G.nodes)):
    node_dictionary[i] = node

edge_dictionary = {}
for i,edge in enumerate(list(G.edges)):
    edge_dictionary[i] = edge

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


def pairwise(lst):
    global fitness_count
    fitness_count = fitness_count + 1
    summa = sum([len(c)*(len(c)-1)/2 if (len(c)>1) else 0 for c in lst])
    return summa

def fitness(individual):
    P : nx.Graph = copy.deepcopy(G)
    P.remove_nodes_from(individual[0])
    P.remove_edges_from(individual[1])
    result = pairwise(nx.connected_components(P))
    return result

def get_second(tuple):
    return tuple[1]

def mutate(individual): # randomly replace either a node or an edge from an individula
    new_individual = individual[0]
    if (float(sys.argv[3]) != 0 and random.random() <= 0.5) or float(sys.argv[4]) == 0: 
        print("Mutating nodes")
        # mutate node list
        chosen_node = random.choice(new_individual[0])
        new_individual[0].remove(chosen_node)
        new_node = random.choice(list(G.nodes))
        while new_node in new_individual[0]:
            new_node = random.choice(list(G.nodes))
        new_individual[0].append(new_node)
    else:  
        print("Mutating edges")
        # mutate edge list
        chosen_edge = random.choice(new_individual[1])
        new_individual[1].remove(chosen_edge)
        new_edge = random.choice(list(G.edges))
        while new_edge in new_individual[1]:
            new_edge = random.choice(list(G.edges))
        new_individual[1].append(new_edge)
    return (new_individual,fitness(new_individual))

def actualize_mutation_count(current_gen, max_gen):
    global mutation_count
    half_gen = int(max_gen / 2)
    alfa = (half_gen - current_gen) / half_gen
    mutation_count = max(int(((k_nodes + k_edges)/4)*alfa),1)
    print(mutation_count)

def descending_mutation(individual):
    global mutation_count
    new_individual = individual[0]
    for _ in range(mutation_count):
        if (float(sys.argv[3]) != 0 and random.random() <= 0.5) or float(sys.argv[4]) == 0: 
            print("Mutating nodes")
            # mutate node list
            chosen_node = random.choice(new_individual[0])
            new_individual[0].remove(chosen_node)
            new_node = random.choice(list(G.nodes))
            while new_node in new_individual[0]:
                new_node = random.choice(list(G.nodes))
            new_individual[0].append(new_node)
        else:  
            print("Mutating edges")
            # mutate edge list
            chosen_edge = random.choice(new_individual[1])
            new_individual[1].remove(chosen_edge)
            new_edge = random.choice(list(G.edges))
            while new_edge in new_individual[1]:
                new_edge = random.choice(list(G.edges))
            new_individual[1].append(new_edge)
    return (new_individual,fitness(new_individual))



def selection(evaluated_population):
    print("Selection")
    new_evaluated_population = evaluated_population.copy()
    # for pop in new_evaluated_population:
    #     print(len(set(pop[0][0])))

    new_evaluated_population = sorted(new_evaluated_population, key=get_second)
    new_evaluated_population = new_evaluated_population[0:pop_size]
    return new_evaluated_population

def split_node_lists(united_node_list):
    first_child_nodes = []
    second_child_nodes = []
    random.shuffle(united_node_list)
    for node in united_node_list:
        if united_node_list.count(node) == 2:
            first_child_nodes.append(node)
            second_child_nodes.append(node)
            while node in united_node_list:
                united_node_list.remove(node)    
    for node in united_node_list: 
        if not node in first_child_nodes and len(first_child_nodes) < k_nodes:
            first_child_nodes.append(node)
        elif not node in second_child_nodes:
            second_child_nodes.append(node)
    
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

def crossover_tournament(evaluated_population):
    print("Tournament")
    evaluated_child_population = []
    for _ in range(tournament_round_count):
        first_child, second_child = tournament_round(evaluated_population)
        evaluated_child_population.append((copy.deepcopy(first_child), fitness(first_child)))
        evaluated_child_population.append((copy.deepcopy(second_child), fitness(second_child)))

    return evaluated_child_population

def average_connectivity(evaluated_population):
    summa = 0
    for individual in evaluated_population:
        summa = summa + individual[1]
    return summa / len(evaluated_population)

def ga():
    print("Starting GA")
    population = generate_pop()
    evaluated_population = [(individual, fitness(individual)) for individual in population]
    print(population)
    f = open(output, "w+")
    for current_gen in range(gen_count):

        # print("Before crossover")
        # for pop in evaluated_population:
        #     if len(set(pop[0][0])) != 25:
        #         print("ERROR")
        evaluated_child_population = crossover_tournament(evaluated_population)

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
        
        print(str(current_gen) + " " + str(fitness_count))
        print(str(current_gen) + " " + str(average_connectivity(evaluated_population)))
        print(str(current_gen) + " " + str(evaluated_population[0][1]) + " " + str(evaluated_population[0][0]), file=f)

        # if fitness_count > max_fitness_count:
        #     break


print(list(G.nodes))
ga()






