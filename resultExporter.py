import csv
from pathlib import Path
codePath = Path.cwd()

results = {}

fileName = "BarabasiAlbert_n500m1.txt"
results1 = [50]
for testNo in range(11):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "BarabasiAlbert_n1000m1.txt"
results1 = [75]
for testNo in range(12):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "BarabasiAlbert_n2500m1.txt"
results1 = [1000]
for testNo in range(12):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "ErdosRenyi_n250.txt"
results1 = [50]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "ErdosRenyi_n500.txt"
results1 = [80]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "ErdosRenyi_n1000.txt"
results1 = [140]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "ForestFire_n250.txt"
results1 = [50]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "ForestFire_n500.txt"
results1 = [110]
for testNo in range(12):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "ForestFire_n1000.txt"
results1 = [150]
for testNo in range(12):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "WattsStrogatz_n250.txt"
results1 = [70]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "WattsStrogatz_n500.txt"
results1 = [125]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "WattsStrogatz_n1000.txt"
results1 = [200]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1



fileName = "Bovine.txt"
results1 = [3]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1


fileName = "Circuit.txt"
results1 = [25]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1


fileName = "Ecoli.txt"
results1 = [15]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1


fileName = "EU_flights.txt"
results1 = [119]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "USAir97.txt"
results1 = [33]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "Hamilton1000.txt"
results1 = [100]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "Hamilton2000.txt"
results1 = [200]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "Hamilton3000a.txt"
results1 = [300]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "humanDiseasome.txt"
results1 = [53]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
    results1.append(maxx)
results[fileName] = results1

fileName = "stocks_62_distance.net"
results1 = [3]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(30 + testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    lineNo = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
            lineNo = int(line.replace("\n","").split(" ")[0])
    results1.append(maxx)
    g =  open(codePath.as_posix() + "/results/"+ fileName + "/" + str(30 + testNo) + "_nodes.txt", "r" )
    lines = g.readlines()
    for line in lines:
        splitline = line.replace("\n","").split(" ")
        if int(splitline[0]) == lineNo:
            line = line.replace("\n","")
            splitline = line.partition(" ")
            results1.append(splitline[2])
results[fileName + str(3)] = results1

fileName = "stocks_62_distance.net"
results1 = [4]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(40 + testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    lineNo = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
            lineNo = int(line.replace("\n","").split(" ")[0])
    results1.append(maxx)
    g =  open(codePath.as_posix() + "/results/"+ fileName + "/" + str(40 + testNo) + "_nodes.txt", "r" )
    lines = g.readlines()
    for line in lines:
        splitline = line.replace("\n","").split(" ")
        if int(splitline[0]) == lineNo:
            line = line.replace("\n","")
            splitline = line.partition(" ")
            results1.append(splitline[2])
results[fileName + str(4)] = results1

fileName = "stocks_62_distance.net"
results1 = [5]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(50 + testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    lineNo = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
            lineNo = int(line.replace("\n","").split(" ")[0])
    results1.append(maxx)
    g =  open(codePath.as_posix() + "/results/"+ fileName + "/" + str(50 + testNo) + "_nodes.txt", "r" )
    lines = g.readlines()
    for line in lines:
        splitline = line.replace("\n","").split(" ")
        if int(splitline[0]) == lineNo:
            line = line.replace("\n","")
            splitline = line.partition(" ")
            results1.append(splitline[2])
results[fileName + str(5)] = results1

fileName = "stocks_62_distance.net"
results1 = [6]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(60 + testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    lineNo = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
            lineNo = int(line.replace("\n","").split(" ")[0])
    results1.append(maxx)
    g =  open(codePath.as_posix() + "/results/"+ fileName + "/" + str(60 + testNo) + "_nodes.txt", "r" )
    lines = g.readlines()
    for line in lines:
        splitline = line.replace("\n","").split(" ")
        if int(splitline[0]) == lineNo:
            line = line.replace("\n","")
            splitline = line.partition(" ")
            results1.append(splitline[2])
results[fileName + str(6)] = results1


fileName = "stocks_62_distance.net"
results1 = [7]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(70 + testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    lineNo = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
            lineNo = int(line.replace("\n","").split(" ")[0])
    results1.append(maxx)
    g =  open(codePath.as_posix() + "/results/"+ fileName + "/" + str(70 + testNo) + "_nodes.txt", "r" )
    lines = g.readlines()
    for line in lines:
        splitline = line.replace("\n","").split(" ")
        if int(splitline[0]) == lineNo:
            line = line.replace("\n","")
            splitline = line.partition(" ")
            results1.append(splitline[2])
results[fileName + str(7)] = results1

fileName = "stocks_62_distance.net"
results1 = [8]
for testNo in range(10):
    f = open(codePath.as_posix() + "/results/"+ fileName + "/" + str(80 + testNo) + ".txt", "r" )
    lines = f.readlines()
    maxx = 0
    lineNo = 0
    for line in lines:
        val = int(line.replace("\n","").split(" ")[1])
        if val > maxx:
            maxx = val
            lineNo = int(line.replace("\n","").split(" ")[0])
    results1.append(maxx)
    g =  open(codePath.as_posix() + "/results/"+ fileName + "/" + str(80 + testNo) + "_nodes.txt", "r" )
    lines = g.readlines()
    for line in lines:
        splitline = line.replace("\n","").split(" ")
        if int(splitline[0]) == lineNo:
            line = line.replace("\n","")
            splitline = line.partition(" ")
            results1.append(splitline[2])
results[fileName + str(8)] = results1



f = open(codePath.as_posix() + "/results/" + "sum.csv", "w")
with f:
    writer = csv.writer(f)
    rows = []
    row = ["Filename", "k", "test0", "test1", "test2", "test3", "test4", "test5", "test6", "test7", "test8", "test9", "test10", "test11"]
    rows.append(row)
    for fileName in results.keys():
        row = []
        row.append(fileName)
        row.extend(results[fileName])
        rows.append(row)
    writer.writerows(rows)

