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


vert_x = converted_data['x'][0][0]
plt.gca().add_patch(patches.Rectangle((vert_x,-0.0001),-0.0,0.0027, linewidth=1, edgecolor="#67f9f8", facecolor="none"))

for i,k in enumerate(keys):
    xs,ys = list(zip(*converted_data[k]))
    ys = [ys[i] - xs[i] for i in range(len(ys))]
    plt.scatter(xs,
            ys,
            s=14,
            c=[base_colours[i]],
            label=k.capitalize(),
            alpha=0.8,
            marker=markers[i],
            linewidth=0)

# OPTIONAL FOR SHOWING REGION OF PARAMETER PERTURBATION
#plt.gca().add_patch(patches.Rectangle((0.1750,0.0006),0.015,0.0005, linewidth=1, edgecolor="black", facecolor="none"))

highlighted_points = [
(0.18132295719844357,
0.18197909514000152),
(0.22410925459678036,
0.22530708781567102),
(0.18689250019073778,
0.18754863813229572),
(0.18958571755550468,
0.18987563897154192)
]

plt.scatter([a for a,b in highlighted_points],[b-a for a,b in highlighted_points],s=58,marker='o', facecolor='none', edgecolor='black', linewidth=0.5)


lgnd = plt.legend(loc="upper right", scatterpoints=1, fontsize=10)
plt.xlabel("In-data distance")
plt.ylabel("Out-data distance minus In-data distance")

plt.xlim(0.169, 0.23) # Limit x-axis from -5 to 5
plt.ylim(-0.0001, 0.0026) # Limit y-axis from -1 to 1


#plt.show()
plt.savefig("results_attribute_experiment.png", bbox_inches='tight')
plt.savefig("results_attribute_experiment.eps", format='eps', dpi=300, bbox_inches='tight') 
