from collections import defaultdict
from math import sqrt

with open("results.txt",'r') as f:
    data = f.readlines()
data = [d.strip() for d in data]
converted_data = defaultdict(list)
while len(data)!=0:
    d = data[:7]
    data = data[7:]
    m = d[0].split("_")
    x = float(d[1].split(" ")[1])
    y = float(d[2].split(" ")[1])
    converted_data[m[0]].append((x,y-x,d[0]))
converted_data_keys = list(converted_data.keys())
d = lambda x,y: sqrt(x**2+y**2)
for k in converted_data_keys:
    converted_data[k] = [(d(a,b),c) for a,b,c in converted_data[k]]
print("METHOD_CLASS", "DISTANCE_TO_IDEAL")
for k in converted_data_keys:
    min_instance = min(converted_data[k],key=lambda x:x[0])
    print(k,min_instance[0])

