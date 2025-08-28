from matplotlib import pyplot as plt
from matplotlib import patches
from collections import defaultdict


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
    converted_data[m[0]].append((x,y))
    print(d[0],x,y-x)

base_colours = ['r','b','g','m','c','k','y']*5
markers = ['.','v','s','P','*','d','X']*5
plt.figure()
keys = sorted(converted_data.keys())
keys.remove("x")
for i,k in enumerate(keys):
    xs,ys = list(zip(*converted_data[k]))
    ys = [ys[i] - xs[i] for i in range(len(ys))]
    plt.scatter(xs,
            ys,
            s=14,
            c=[base_colours[i]],
            label=k.capitalize(),
            alpha=0.8,
            marker=markers[i])

plt.gca().add_patch(patches.Rectangle((0.1750,0.0006),0.015,0.0005, linewidth=1, edgecolor="black", facecolor="none"))
vert_x = converted_data['x'][0][0]
plt.gca().add_patch(patches.Rectangle((vert_x,0.0),-0.0,0.0025, linewidth=1, edgecolor=base_colours[4], facecolor="none"))
#plt.gca().add_patch(patches.Rectangle((0.17,0.0),0.06,0.0, linewidth=1, edgecolor="black", facecolor="none"))

lgnd = plt.legend(loc="upper right", scatterpoints=1, fontsize=10)
plt.xlabel("In-data distance")
plt.ylabel("Out-data distance minus In-data distance")
plt.show()
#plt.savefig("results.png", bbox_inches='tight')
