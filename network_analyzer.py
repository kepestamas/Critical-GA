import networkx as nx
import sys
import numpy as np
import math
from numpy.linalg import eig
from graph_io import read_graph, print_graph_summary

def get_second(input):
    return input[1]

def avg(x):
    return sum(x) / len(x)

input = "inputs/" + sys.argv[1]
G, node_weights = read_graph(input, detect_weights=False)  # Analyzer doesn't need weights
print_graph_summary(G, node_weights, verbose=False)  # Silent mode for analyzer


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