import networkx as nx
import sys
import matplotlib.pyplot as plt
from ast import literal_eval as make_tuple
from pyvis.network import Network
from graph_io import read_graph, print_graph_summary


input = "inputs/" + sys.argv[1]
G, node_weights = read_graph(input, detect_weights=False)  # Painter doesn't need weights
print_graph_summary(G, node_weights, verbose=False)  # Silent mode for painter


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

