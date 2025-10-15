import subprocess
import time

file_list = ["ForestFire_n250.txt","ErdosRenyi_n250.txt", "ErdosRenyi_n500.txt", "ForestFire_n500.txt"]
#file_list = ["BarabasiAlbert_n500m1.txt","BarabasiAlbert_n1000m1.txt"]
# file_list = ["hamster.txt"]
#file_list = ["zebra.txt","karate.txt", "football.txt", "Ecoli.txt",  "Bovine.txt", "Circuit.txt", "dolphins.txt", "humanDiseasome.txt"]
p_nodes = 0.05 #0.05!!!, 0,05, 0   , 0.02, 0.02, 0
p_edges = 0.03 #0.03!!!, 0   , 0.03, 0.01, 0   , 0.01


pop_size = 100 # 50, 100
tournament_size = 3 # 5, 3
p_cross = 0.8 # 0.9, 0.8
p_mut = 0.05 # 0.05, 0.02

f = open("outputs/descending_mutation/timing.txt", "a")

for file in file_list:
    for i in range(10):
        start = time.time()
        list_dir = subprocess.Popen(["python3.8", "connectivity_ga.py",file,str(i),str(p_nodes),str(p_edges),str(pop_size), str(tournament_size), str(p_cross), str(p_mut)])
        list_dir.wait()
        #list_dir = subprocess.Popen(["python3.8", "connectivity_greedy.py",file,str(i)])
        #list_dir.wait()
        end = time.time()
        print(str(i) + "_" + str(file) + "_ga: " + str(end - start) + " seconds", file=f)
