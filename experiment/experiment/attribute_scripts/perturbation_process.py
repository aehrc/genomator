from matplotlib import pyplot as plt
from collections import defaultdict

#with open("results.txt",'r') as f:
#    data = f.readlines()
#data = [d.strip() for d in data]
converted_data = defaultdict(list)
#while len(data)!=0:
#    d = data[:7]
#    data = data[7:]
#    m = d[0].split("_")
#    x = float(d[1].split(" ")[1])
#    y = float(d[2].split(" ")[1])
#    converted_data[m[0]].append((x,y))
#    print(d[0],x,y-x)


with open("perturbation_experiment.txt",'r') as f:
    data = f.readlines()
data = [d.strip() for d in data]
import pdb
pdb.set_trace()
while len(data)!=0:
    d = data[:7]
    data = data[7:]
    m = d[0].split("_")
    x = float(d[1].split(" ")[1])
    y = float(d[2].split(" ")[1])
    converted_data["_".join([d[0].split("_")[i] for i in [2,3,7]])].append((x,y))
    print(d[0],x,y-x)

base_colours = ['r','b','g','m','c','k','y']*5
markers = ['.','v','s','P','*','d','X']*5
plt.figure()
for i,k in enumerate(sorted(converted_data.keys())):
    xs,ys = list(zip(*converted_data[k]))
    ys = [ys[i] - xs[i] for i in range(len(ys))]
    plt.scatter(xs,
            ys,
            s=14,
            c=[base_colours[i]],
            label=k.capitalize(),
            alpha=0.8,
            marker=markers[i])

lgnd = plt.legend(loc="upper right", scatterpoints=1, fontsize=10)
plt.xlabel("In-data distance")
plt.ylabel("Out-data distance minus In-data distance")
plt.show()
#plt.savefig("results.png", bbox_inches='tight')
