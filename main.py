import logging
from importlib import reload

from numpy import Infinity
reload(logging)
import logging.config
import networkx as nx
import criticalPointsWithExtremalOptimization as CPEO
import sys
import threading
from pathlib import Path

from pathlib import Path
codePath = Path.cwd()

def configureLogger():
    log_file = codePath / 'logging.conf'
    print(log_file.as_posix())
    logging.config.fileConfig(log_file.as_posix())
    loggers = {}
    loggers.update({"Main" : logging.getLogger('Main')})
    loggers.update({"EO" : logging.getLogger('EO')})
    return loggers

def readGraph(filename, fileType):
    G = nx.Graph()
    if fileType in ["hamster.txt", "football.txt", "dolphins.txt", "karate.txt", "zebra.txt", "USAir97.txt", "inf-openflights.edges", "inf-euroroad.edges", "road-minnesota.mtx"]:
        f = open(filename, "r")
        lines = f.readlines()
        for line in lines:
            splitline = line.replace("\n", "").replace(",", " ").replace("\t", " ").split(" ")
            G.add_edge(splitline[0], splitline[1])
    elif fileType == "stocks_62_distance.net":
        f = open(filename, "r")
        lines = f.readlines()
        for line in lines:
            splitline = line.replace("\n", "").replace(",", " ").replace("\t", " ").split(" ")
            if float(splitline[2]) > 1.2:
                G.add_edge(splitline[0], splitline[1])
    elif fileType in ["BarabasiAlbert_n500m1.txt","BarabasiAlbert_n1000m1.txt","ErdosRenyi_n250.txt","ErdosRenyi_n500.txt","ForestFire_n250.txt","ForestFire_n500.txt", "BarabasiAlbert_n2500m1.txt","ErdosRenyi_n1000.txt","ForestFire_n1000.txt"]:
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
    elif fileType in ["humanDiseasome.txt", "Ecoli.txt", "EU_flights.txt", "Circuit.txt", "Bovine.txt", "Treni_Roma.txt"]:
        f = open(filename, "r")
        lines = f.readlines()
        for line in lines:
            splitLine = line.replace("\n","").split(" ")
            nodeA = splitLine[0]
            neighbours = splitLine[1:-1].copy()
            for neighbour in neighbours:
                G.add_edge(nodeA, neighbour)
    return G

loggers = configureLogger()
loggers["Main"].info("Application started")



loggers["Main"].info("Reading graph")
if len(sys.argv) == 7:
    testNo = int(sys.argv[1])
    testType = int(sys.argv[2]) # 1 is normal 2 is Nash, 3 is Noisy
    initType = int(sys.argv[3]) # 1 is random 2 is by degree
    payoffType = int(sys.argv[4]) #1 is 3a, 2 is 2a, 3 is pairwise
    testName = str(sys.argv[5])
    k =  int(sys.argv[6])
else:
    testName = "humanDiseasome.txt"
    testNo = 5000
    testType = 3
    initType = 1
    payoffType = 1
    k = 52

filename = codePath / "inputs" / testName
# fileType = "minimalList"
G = readGraph(filename, testName)
Path("./pairwise_results/"+ testName + "/").mkdir(parents=True, exist_ok=True)
iterCount = 5000
threads = []

# print (G.edges)

class myThread (threading.Thread):
    def __init__(self, testNo):
        threading.Thread.__init__(self)
        self.testNo = testNo

    def run(self):
        loggers["Main"].info("Running thread: " + str(self.testNo))
        EO = CPEO.CriticalPointsExtremalOptimization(loggers["EO"], codePath, testName, testNo, initType, payoffType)
        EO.ExtremalOptimization(G.copy(), k, iterCount, testNo = self.testNo)
        loggers["Main"].info("Finishing thread: " + str(self.testNo))

# if testType == 1:
#     EO.ExtremalOptimization(G, k, iterCount)
# elif testType == 2:
#     EO.ExtremalOptimizationWithNash(G, k, iterCount)

#! run tests with "python3.8 main.py 0 1 1 3 filename k"
if testType == 1:
    for i in range(10):
        threads.append(myThread(testNo + i))
        threads[i].start()
    # EO.NoisyExtremalOptimization(G, k, iterCount, pShift=0.01, noiseCount=10, testNo = testNo)

# lst = list(G.nodes)

# result = []

# for node in lst:
#     for node2 in lst:
#         for node3 in lst:
#             if node != node2 and node2 != node3 and node3 != node:
#                 l = [node, node2, node3]
#                 result.append(l)

# EO = CPEO.CriticalPointsExtremalOptimization(loggers["EO"], codePath, testName, testNo, initType, payoffType)
# P : nx.Graph = G.copy()
# P.remove_nodes_from(['0', '2', '9'])
# print(list(nx.connected_components(P)))
# res = EO.pairwise(nx.connected_components(P))
# print(res)
# min = Infinity
# for list in result:
#     P : nx.Graph = G.copy()
#     P.remove_nodes_from(list)
#     res = EO.pairwise(nx.connected_components(P))
#     print(str(list) + " " + str(res))
#     if res < min:
#         min = res
#     if min < 300:
#         break


# print(min)

# print(EO.powerSet([1,2,3,4]))







