import networkx as nx
from pathlib import Path
import csv
codePath = Path.cwd()
import networkx.algorithms.community as nx_comm
import networkx.algorithms.distance_measures as nx_dist

def readGraph(filename, fileType):
    G = nx.Graph()
    if fileType == "edges":
        f = open(filename, "r")
        lines = f.readlines()
        for line in lines:
            splitline = line.replace("\n", "").replace(",", " ").replace("\t", " ").split(" ")
    elif fileType == "list":
        f = open(filename, "r")
        lines = f.readlines()
        lines.remove(lines[0])
        for line in lines:
            splitLine = line.split(":")
            nodeA = splitLine[0]
            neighbours = splitLine[1].replace("\n","").split(" ")
            neighbours = neighbours[1:-1]
            for neighbour in neighbours:
                G.add_edge(nodeA, neighbour)
    elif fileType == "minimalList":
        f = open(filename, "r")
        lines = f.readlines()
        for line in lines:
            splitLine = line.replace("\n","").split(" ")
            nodeA = splitLine[0]
            neighbours = splitLine[1:-1].copy()
            for neighbour in neighbours:
                G.add_edge(nodeA, neighbour)
    return G


# testNames = ["Bovine.txt","Circuit.txt", "Ecoli.txt", "USAir97.txt", "humanDiseasome.txt", "Treni_Roma.txt", "facebook.txt"]
results = {}
# testNames = ["EU_flights.txt", "OClinks.txt"]
for testName in testNames:
    print("Looking at graph: ", testName)
    filename = codePath / "inputs" / testName
    fileType = "minimalList"
    G = readGraph(filename, fileType)
    Q = nx_comm.modularity(G, list(nx_comm.label_propagation_communities(G)))
    try:
        D = nx_dist.diameter(G)
    except:
        D = "infinite"
    results[testName] = [D, Q]

print(results)


# f = open(codePath.as_posix() + "/results/" + "graphStats.csv", "w")
# with f:
#     writer = csv.writer(f)
#     rows = []
#     row = ["Filename", "D", "Q"]
#     rows.append(row)
#     for filename in results.keys():
#         row = []
#         row.append(filename)
#         row.extend(results[filename])
#         rows.append(row)
#     writer.writerows(rows)