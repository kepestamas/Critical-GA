import networkx as nx
import sys
import matplotlib.pyplot as plt
from ast import literal_eval as make_tuple
from pyvis.network import Network

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
    elif sys.argv[1] in ["hamster.txt", "football.txt", "dolphins.txt", "karate.txt", "zebra.txt", "inf-USAir97.mtx", "inf-openflights.edges", "inf-euroroad.edges", "road-minnesota.mtx"]:
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
G = read_graph(input)


# nx.draw_spring(G, node_size=10)
# plt.show()
# nt = Network('500px', '500px')
# # populates the nodes and edges data structures
# nt.from_nx(G)
# nt.show('nx1.html')

removed_input = "outputs/ga/1_zebra.txt_ke_3_kn_1"

f = open(removed_input, "r")
lines = f.readlines()
lastline = lines[-1]

lastline = lastline.replace("\n", "").split(" ")[2:]
lastline = ' '.join([str(elem) for elem in lastline])
lastline = make_tuple(lastline)

G.remove_nodes_from(lastline[0])
G.remove_edges_from(lastline[1])

nt = Network('500px', '500px')
# populates the nodes and edges data structures
nt.from_nx(G)
nt.show('nx3.html')

# nx.draw_spring(G, with_labels=True, node_size=10)
# plt.show()

