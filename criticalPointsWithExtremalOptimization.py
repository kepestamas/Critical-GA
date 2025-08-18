import networkx as nx
import random
from itertools import chain, combinations
import math
import operator

class CriticalPointsExtremalOptimization:
    def __init__(self, logger, codePath, fileName, testNo, initType = 1, payoffType = 1):
        super().__init__()
        self.logger = logger
        self.codePath = codePath
        self.fileName = fileName
        self.nodeVals = {}
        self.listVals = {}
        self.testNo = testNo
        self.initType = initType # 1 = random 2 = greedy
        self.payoffType = payoffType # 1 = 3a, 2 = 2a
        self.noise = False

    def generateStrategy(self, G:nx.Graph, k: int):
        if self.initType == 1:
            self.logger.debug("Initializing strategies at random")
            s = random.sample(G.nodes, k)
        elif self.initType == 2:
            self.logger.debug("Initializing strategies with greedy based on degree")
            nodeList = list(G.nodes)
            nodeDegrees = {}
            for node in nodeList:
                nodeDegrees[node] = len([x for x in G.neighbors(node)])
                # self.getComponentNo(G, node)
            tmp = {k: v for k, v in sorted(nodeDegrees.items(), key=lambda item: item[1], reverse = True)}
            s = []
            i = 0
            for node in tmp.keys():
                if i >= k:
                    break
                s.append(node)
                i+=1

        return s, s.copy()

    def initOutputs(self):
        self.logger.debug("Initializing outputs")
        file_1 = self.codePath.as_posix() + "/pairwise_results/"+ self.fileName + "/shapley_allk_" + str(self.testNo) + ".txt"
        file_2 = self.codePath.as_posix() + "/pairwise_results/"+ self.fileName + "/shapley_allk_" + str(self.testNo) + "_nodes.txt"
        f = open(file_1, "w+")
        g = open(file_2, "w+")
        return f, g

    # def getComponentNo(self, G: nx.Graph, node):
    #     if not node in self.nodeVals.keys():
    #         testG = G.copy()
    #         testG.remove_node(node)
    #         compNo = nx.algorithms.number_connected_components(testG)
    #         self.nodeVals[node] = compNo
    #         testG = G.copy()
    #     else:
    #         compNo = self.nodeVals[node]
    #     return compNo

    # def getLeastCritical(self, G: nx.Graph, s, k):
    #     worst = s[0]
    #     minCompNo = self.getComponentNo(G, s[0])
    #     for node in s:
    #         compNo = self.getComponentNo(G, node)
    #         if compNo < minCompNo:
    #             minCompNo = compNo
    #             worst = node
    #     return worst

    def getPayoffWithSubtraction(self, G: nx.Graph, s, node):
        backupS = s.copy()
        res = self.payoff(G, backupS)
        backupS.remove(node)
        res -= self.payoff(G, backupS)
        return abs(res)

    def getLeastCriticalBySubtraction(self, G: nx.Graph, s, k):
        worst = s[0]
        worstValue = self.getPayoffWithSubtraction(G, s, s[0])
        for node in s:
            currentValue = self.getPayoffWithSubtraction(G, s, node)
            if currentValue < worstValue:
                worstValue = currentValue
                worst = node
            # if self.payoffType in [2, 3] and currentValue > worstValue:
            #     worstValue = currentValue
            #     worst = node
        return worst

    def powerSet(self, s):
        return  [list(j) for i in range(len(s)) for j in combinations(s, i+1)]

    def shapleyValues(self, G, s, coalitions):
        result = {}
        for node in s:
            sum = 0
            for i in range(len(s)):
                for coalition in combinations(s, i+1):
                    coalitionList = list(coalition)
                    if node not in coalitionList:
                        currentValue = (math.factorial(len(coalitionList)) * (math.factorial(len(s) - len(coalitionList) - 1))) / (math.factorial(len(s)))
                        coalitionWithNode = coalitionList.copy()
                        coalitionWithNode.append(node)
                        currentValue = currentValue * (self.payoff(G, coalitionWithNode) - self.payoff(G, coalitionList))
                        sum += currentValue
            result[node] = sum
        return result

    def __seenAll(self, seen):
        res = True
        for i in seen:
            res = res and seen[i]
        return res

    def getShapleysWithOrderings(self, G, s, k):
        strategy = s.copy()
        contributions = {}
        for i in strategy:
            contributions[i] = []

        # Random sampling with k distinct last elements
        seen = {}
        for i in strategy:
            seen[i] = False
        
        orderings = []
        random.shuffle(strategy)
        # kk = int(k / 2) #! testing with kk = k
        kk = k
        for i in range(kk):
            orderings.append(strategy.copy())
            random.shuffle(strategy)


        # #use if you want k distinct last places
        while not self.__seenAll(seen): 
            if not seen[strategy[k-1]]:
                orderings.append(strategy.copy())
                seen[strategy[k-1]] = True
            random.shuffle(strategy) # no need to check for same list, it gets filtered by the seen check

        for ordering in orderings:
            currentCoalition = []
            prevVal = 0
            for i in ordering:
                currentCoalition.append(i)
                currentVal = self.payoff(G, currentCoalition)
                contributions[i].append(currentVal - prevVal)
                prevVal = currentVal    

        shapleysWithNodes = []
        for i in contributions.keys():
            shapleysWithNodes.append((sum(contributions[i])/len(contributions[i]),i))
        
        return shapleysWithNodes

    def getLeastCriticalWithShapley(self, G: nx.Graph, s):
        shapleysWithNodes = self.getShapleysWithOrderings(G, s, len(s))
        shapleysWithNodes.sort(key = operator.itemgetter(0))
        return shapleysWithNodes[0][1]
        # worstValue = shapleysWithNodes[0][0]
        # worst = shapleysWithNodes[0][1]
        # for i in range(len(s)):
        #     if shapleysWithNodes[i][0] < worstValue:
        #         worstValue = shapleysWithNodes[i][0]
        #         worst = shapleysWithNodes[i][1]
        # return worst

    def alreadyConsidered(self, G: nx.Graph, node):
        return node in self.nodeVals.keys() and len(self.nodeVals.keys()) < G.number_of_nodes()

    def switchLeastCritical(self, G, s, worstNode):
        s.remove(worstNode)
        newNode = random.sample(G.nodes, 1)
        while newNode[0] in s or newNode[0] == worstNode: # or self.alreadyConsidered(G, newNode[0]): #only look at nodes that are not yet considered
            newNode = random.sample(G.nodes, 1)
        s.append(newNode[0])
        self.logger.debug("New node in s %s", str(newNode[0]))

    def payoff(self, G, s):
        if self.payoffType == 1:
            return self.numberOfComponentsAfterRemoval(G,s)
        elif self.payoffType == 2:
            return self.largestConnectedComponentAfterRemoval(G,s)
        elif self.payoffType == 3:
            return self.pairwiseConnectivityAfterRemoval(G,s)

    def pairwise(self, lst):
        summa = sum([len(c)*(len(c)-1)/2 if (len(c)>1) else 0 for c in lst])
        return summa

    def pairwiseConnectivityAfterRemoval(self, G, s):
        if not self.noise:
            if not str(s) in self.listVals.keys():
                P : nx.Graph = G.copy()
                P.remove_nodes_from(s)
                result = self.pairwise(nx.connected_components(P))
                self.listVals[str(s)] = result
            else:
                result = self.listVals[str(s)]
        else:
            P : nx.Graph = G.copy()
            P.remove_nodes_from(s)
            result = self.pairwise(nx.connected_components(P))
        return result

    def numberOfComponentsAfterRemoval(self, G, s): # 3a
        if not self.noise:
            if not str(s) in self.listVals.keys():
                testG = G.copy()
                testG.remove_nodes_from(s)
                res = nx.algorithms.number_connected_components(testG)
                self.listVals[str(s)] = res
            else:
                res = self.listVals[str(s)]
        else:
            testG = G.copy()
            testG.remove_nodes_from(s)
            res = nx.algorithms.number_connected_components(testG)
        return res

    def largestConnectedComponentAfterRemoval(self, G: nx.Graph, s): #2a
        if not str(s) in self.listVals.keys():
            testG = G.copy()
            testG.remove_nodes_from(s)
            comps = nx.algorithms.connected_components(testG)
            comp_sizes = [len(x) for x in comps]
            res = max(comp_sizes)
            self.listVals[str(s)] = res
        else:
            res = self.listVals[str(s)]
        return res

    def compareStrategies(self, G: nx.Graph, s1, s2):
        n1 = self.payoff(G, s1)
        n2 = self.payoff(G, s2)
        if self.payoffType == 1:
            return n1 > n2
        return n1 < n2

    def __removeEdges(self, G: nx.Graph, pShift: float):
        edgeList = [e for e in G.edges]
        random.shuffle(edgeList)
        for i in range(int(len(edgeList) * pShift)):
            G.remove_edge(edgeList[i][0], edgeList[i][1])

    def NoisyExtremalOptimization(self, G: nx.Graph, k:int, iterCount: int, pShift: float, noiseCount: int, testNo: int):
        self.testNo = testNo
        self.logger.info("Started Noisy Extremal Optimization")
        n = G.number_of_nodes()
        s, sbest = self.generateStrategy(G, k)
        f, g = self.initOutputs()
        self.noise = False
        itersSinceImprovement = 0
        itersInNoise = 0
        oldG = G.copy()
        for currentIter in range(iterCount):
            self.logger.debug("Currently at iteration %s", str(currentIter))
            self.logger.debug("Current s %s", s)
            self.logger.debug("Current s value %s", str(self.payoff(G, s)))
            self.logger.debug("Current sbest %s", sbest)
            self.logger.debug("Current sbest value %s", str(self.payoff(G, sbest)))
            if itersSinceImprovement == noiseCount:
                self.logger.debug("Noise activated")
                self.noise = True
                itersSinceImprovement = 0
                sbest = s.copy()
                self.__removeEdges(G, pShift)
            if itersInNoise == noiseCount:
                self.logger.debug("Noise de-activated")
                self.noise = False
                itersInNoise = 0
                G = oldG.copy()
            if self.noise:
                itersInNoise = itersInNoise + 1

            worstNode = self.getLeastCriticalBySubtraction(G, s, k)
            self.switchLeastCritical(G, s, worstNode)
            if self.compareStrategies(G, s, sbest):
                sbest = s.copy()
                if not self.noise:
                    itersSinceImprovement = 0
            elif not self.noise:
                itersSinceImprovement = itersSinceImprovement + 1
            if not self.noise:
                f.write(str(currentIter) + " " + str(self.payoff(G, sbest)) + "\n")
                g.write(str(currentIter) + " " + str(sbest)  + "\n")
        f.close()
        g.close()

    def ExtremalOptimization(self, G: nx.Graph, k: int, iterCount: int, testNo: int):
        self.testNo = testNo
        self.logger.info("Started Extremal Optimization")
        n = G.number_of_nodes()
        s, sbest = self.generateStrategy(G, k)
        f, g = self.initOutputs()
        for currentIter in range(iterCount):
            self.logger.debug("Currently at iteration %s", str(currentIter))
            self.logger.debug("Current s %s", s)
            self.logger.debug("Current s value %s", str(self.payoff(G, s)))
            self.logger.debug("Current sbest %s", sbest)
            self.logger.debug("Current sbest value %s", str(self.payoff(G, sbest)))
            # worstNode = self.getLeastCriticalBySubtraction(G, s, k)
            worstNode = self.getLeastCriticalWithShapley(G, s) #! shapley value introduced for pairwise results
            self.switchLeastCritical(G, s, worstNode)
            if self.compareStrategies(G, s, sbest):
                sbest = s.copy()
            f.write(str(currentIter) + " " + str(self.payoff(G, sbest)) + "\n")
        g.write(str(sbest))
        f.close()
        g.close()

    def ExtremalOptimizationWithNash(self, G: nx.Graph, k: int, iterCount: int):
        self.logger.info("Started Extremal Optimization with Nash")
        n = G.number_of_nodes()
        s, sbest = self.generateStrategy(G, k)
        f, g = self.initOutputs()
        for currentIter in range(iterCount):
            self.logger.debug("Currently at iteration %s", str(currentIter))
            self.logger.debug("Current s %s", s)
            self.logger.debug("Current s value %s", str(self.payoff(G, s)))
            self.logger.debug("Current sbest %s", sbest)
            self.logger.debug("Current sbest value %s", str(self.payoff(G, sbest)))
            worstNode = self.getLeastCriticalBySubtraction(G, s, k)
            self.switchLeastCritical(G, s, worstNode)
            if self.NashAscendancy(G, s, sbest):
                sbest = s.copy()
            f.write(str(currentIter) + " " + str(self.payoff(G, sbest)) + "\n")
        g.write(str(sbest))
        f.close()
        g.close()

    # # k(s, s') = |({i ∈ {1, ...,n}|ui(s'i, s−i) ≥ ui(s), s'i != si}|
    def calculateCardinalityOfNash(self, G: nx.Graph, s1, s2):
        card = 0
        s11 = s1.copy() 
        s22 = s2.copy()
        for i in range(len(s1)):
            if not s11[i] in s22:
                ui1 = self.payoff(G, s11)
                s11[i], s22[i] = s22[i], s11[i]
                ui2 = self.payoff(G, s11)
                if ui2 >= ui1:
                    card += 1
        return card

    # # Nash Ascendancy Procedure according to Nash Extremal Optimization and Large Cournot Games by Rodica Ioana Lung, Tudor Dan Mihoc, and D. Dumitrescu
    def NashAscendancy(self, G: nx.Graph, s1, s2): 
        cards1s2 = self.calculateCardinalityOfNash(G, s1, s2)
        cards2s1 = self.calculateCardinalityOfNash(G, s2, s1)
        # Either s1 dominates s2 (k(s1,s2) < k(s2,s1))
        return cards1s2 < cards2s1



