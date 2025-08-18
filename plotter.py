import matplotlib.pyplot as plt
from pathlib import Path
codePath = Path.cwd()
filename1 = codePath / "results" / "test" / "8.txt"
filename5 = codePath / "results" / "test" / "12.txt"


f = open(filename1, "r")
lines = f.readlines()
x1 = []
y1 = []
for line in lines:
    splitline = line.replace("\n","").split(" ")
    x1.append(int(splitline[0]))
    y1.append(int(splitline[1]))

f = open(filename5, "r")
lines = f.readlines()
x5 = []
y5 = []
for line in lines:
    splitline = line.replace("\n","").split(" ")
    x5.append(int(splitline[0]))
    y5.append(int(splitline[1]))


plt.plot(x1,y1, "r")
plt.plot(x5,y5, "b")
plt.show()