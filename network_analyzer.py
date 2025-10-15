import networkx as nx
import sys
import numpy as np
import math
from numpy.linalg import eig

def read_graph(input):
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

def get_second(input):
    return input[1]

def avg(x):
    return sum(x) / len(x)

input = "inputs/" + sys.argv[1]
G = read_graph(input)


output = open("outputs/reruns/networks/"+sys.argv[1], "w")


V = len(list(G.nodes)) # number of nodes
print("V: " + str(V))
E = len(list(G.edges)) # number of edges
print("E: " + str(E))
k = nx.is_connected(G) # connectivity
print("k: " + str(k))
k_v = nx.node_connectivity(G) # node connectivity
print("k_v: " + str(k_v))
k_e = nx.edge_connectivity(G) # edge connectivity
print("k_e: " + str(k_e))
delta_min = min(list(nx.degree(G)), key=get_second)[1] # minimum degree of Graph
print("delta_min: " + str(delta_min))
d = nx.diameter(G) # diameter
print("diameter (d): " + str(d))
d_avg = nx.average_shortest_path_length(G) # avarage_distance
print("avarage_distance (d-): " + str(d_avg))
eff = nx.global_efficiency(G) # average global efficiency
print("average efficiency (E): " + str(eff))
b_max = max(nx.edge_betweenness(G).values()) # maximum edge betweenness
print("maximum edge betweenness (b_e_max): " + str(b_max))
b_v = (1/2) * (V-1) * (d_avg + 1) # average vertex betweenness according to paper
print("average vertex betweenness (b_v): " + str(b_v))
b_e = ((V * (V-1)) / (2 * E)) * (d_avg) # average edge betweenness according to paper
print("average edge betweenness (b_e): " + str(b_e))


C = avg(list(nx.clustering(G).values())) # average clustering coefficient
print("average clustering coefficient (C): " + str(C))

# !Reliability polinomial may be too slow

# Laplacian matrix:
node_list = list(G.nodes)
L = np.arange(len(node_list) * len(node_list))
L.shape = (len(node_list), len(node_list))

for i in range(len(node_list)):
    for j  in range(len(node_list)):
        if node_list[j] in G.neighbors(node_list[i]):
            L[i, j] = -1
        elif i == j:
            L[i, j] = G.degree(node_list[i])
        else:
            L[i, j] = 0
        j += 1
    i += 1


l_eig, _ = eig(L)
l_eig = np.real(l_eig)
l_eig = list(l_eig)
l_eig.sort() # Laplacian eighen values sorted


print("Algebraic connectivity (lambda_2): " + str(l_eig[1])) # Algebraic connectivity using laplacian eighen values

eps = (1/V) * np.prod(l_eig[1:]) # Number of spanning trees using laplacian eighen values
print("Number of spanning trees (epsilon): " + str(eps))

R = V * sum([1/a for a in l_eig[1:]]) # Effective graph resistance (Kirchhoff index) using laplacian eighen values
print("Effective graph resistance (Kirchhoff index) (R): " + str(R))




# d = sum([node[1] for node in list(G.degree)]) / len([node[1] for node in list(G.degree)]) 


# ro = (2*E) / (V * (V-1))



# Floyd Warshall Algorithm in python


# # The number of vertices
# nV = 4

# INF = 999999999


# Algorithm implementation
# def floyd_warshall(G):
#     distance = list(map(lambda i: list(map(lambda j: j, i)), G))

#     # Adding vertices individually
#     for k in range(V):
#         for i in range(V):
#             for j in range(V):
#                 distance[i][j] = min(distance[i][j], distance[i][k] + distance[k][j])
#     return distance



# G1 = []
# G_list = list(G.nodes)

# for i in range(V):
#     G1.append([])
#     for j in range(V):
#         if (G_list[j] in G.neighbors(G_list[i])):
#             G1[i].append(1)
#         elif i == j:
#             G1[i].append(0)
#         else:
#             G1[i].append(INF)
# # print(G1)
# distance = floyd_warshall(G1)
# for i in range(V):
#     for j in range(V):
#         if (distance[i][j] == INF):
#             distance[i][j] = 0

# sum = 0
# for i in range(V):
#     for j in range(V):
#         if i != j:
#             sum += distance[i][j]
# l_G = sum / (V * (V-1))
# print("$" + str(V) + "$ & $" + str(E) + "$ & $" + str("{:.4f}".format(d)) + "$ & $" + str("{:.4f}".format(ro)) + "$ & $" + str("{:.4f}".format(l_G)) + "$ ")