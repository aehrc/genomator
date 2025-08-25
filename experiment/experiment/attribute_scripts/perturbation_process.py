from matplotlib import pyplot as plt
from collections import defaultdict
from statistics import mean

converted_data = defaultdict(list)


with open("perturbation_experiment.txt",'r') as f:
    data = f.readlines()
data = [d.strip() for d in data]
while len(data)!=0:
    d = data[:7]
    data = data[7:]
    m = d[0].split("_")
    x = float(d[1].split(" ")[1])
    y = float(d[2].split(" ")[1])
    converted_data["_".join([d[0].split("_")[i] for i in [2,3,7]])].append((x,y-x))
    print(d[0],x,y-x)


for k in converted_data.keys():
    converted_data[k] = [[mean(values) for values in zip(*converted_data[k])]]

for k in converted_data.keys():
    print(k,end=",")
    print(",".join([str(v) for v in converted_data[k][0]]))

base_colours = ['r','b','g','m','c','k','y']*5
markers = ['.','v','s','P','*','d','X']*5
plt.figure()
#for i,k in enumerate(sorted(converted_data.keys())):
#    xs,ys = list(zip(*converted_data[k]))
#    plt.scatter(xs,
#            ys,
#            s=14,
#            c=[base_colours[i]],
#            label=k.capitalize(),
#            alpha=0.8,
#            marker=markers[i])

xs = []
ys = []
for L in [0.982,0.986,0.99,0.994]:
    k = f"150_1.5_{L}"
    xs.append(converted_data[k][0][0])
    ys.append(converted_data[k][0][1])
plt.plot(xs,ys,c = base_colours[0], marker=markers[0])
plt.annotate('decrease L', xy=(xs[0], ys[0]), xytext=(-2, 1), textcoords=("offset fontsize","offset fontsize"), c=base_colours[0])
plt.annotate('increase L', xy=(xs[-1], ys[-1]), xytext=(-4, 2.5), textcoords=("offset fontsize","offset fontsize"), c=base_colours[0])

xs = []
ys = []
for Z in [1.1,1.3,1.5,1.7,1.9]:
    k = f"150_{Z}_0.99"
    xs.append(converted_data[k][0][0])
    ys.append(converted_data[k][0][1])
plt.plot(xs,ys,c = base_colours[1], marker=markers[1])
plt.annotate('decrease Z', xy=(xs[0], ys[0]), xytext=(-2, 1), textcoords=("offset fontsize","offset fontsize"), c=base_colours[1])
plt.annotate('increase Z', xy=(xs[-1], ys[-1]), xytext=(-4, 1), textcoords=("offset fontsize","offset fontsize"), c=base_colours[1])

xs = []
ys = []
for N in [90,120,150,180]:
    k = f"{N}_1.5_0.99"
    xs.append(converted_data[k][0][0])
    ys.append(converted_data[k][0][1])
plt.plot(xs,ys,c = base_colours[2], marker=markers[2])
plt.annotate('decrease N', xy=(xs[0], ys[0]), xytext=(2, -0.5), textcoords=("offset fontsize","offset fontsize"), c=base_colours[2])
plt.annotate('increase N', xy=(xs[-1], ys[-1]), xytext=(-7, -0.5), textcoords=("offset fontsize","offset fontsize"), c=base_colours[2])



lgnd = plt.legend(loc="upper right", scatterpoints=1, fontsize=10)
plt.xlabel("In-data distance")
plt.ylabel("Out-data distance minus In-data distance")
plt.show()
#plt.savefig("results.png", bbox_inches='tight')
