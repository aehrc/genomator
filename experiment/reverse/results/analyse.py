import glob
import matplotlib.pyplot as plt
import json
import re
import numpy as np
import math
from sklearn.neighbors import NearestNeighbors
from scipy.optimize import bisect
from math import comb
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import AutoMinorLocator
from matplotlib.ticker import PercentFormatter


files = glob.glob("./wasserstein_*")
files = sorted(files,key=lambda x: x.split("_")[::-1])
print("WASSERSTEIN")
from statistics import mean
w_dataset=[]
for f in files:
    #print(f"loading {f}")
    with open(f,'r') as f:
        data = [l for l in f.readlines() if l!="loading VCF file\n"]
    data = [float(d.strip().split(" ")[0]) for d in data]
    fname = ".".join(f.name.split(".")[:-1])
    Z = float(fname.split("_")[-1])
    batch_size = int(fname.split("_")[-2])
    val = mean(data)
    print(batch_size,end=",")
    print(Z,end=",")
    print(val)
    w_dataset.append((Z,batch_size,val))
w_dataset = sorted(w_dataset)


print("THAT THERE ARE PRIVACY VIOLATIONS")

files = glob.glob("./privacy*")
files = sorted(files)
files = [f for f in files if 'analyse' in f]
dataset=[]
for f in files:
    print(f"loading {f}")
    try:
        with open(f,'r') as f:
            analyse0 = [json.loads(ff.strip()) for ff in f.readlines()]
    except:
        print("passing")
        continue
    elements = 0
    for a in analyse0:
        for aa in a[0]+a[1]:
            if aa[0]==a[2]:
                elements += 1
                break
    n = len(analyse0)
    avg = elements*1.0/n

    Z = float(f.name.split("_")[1])
    batch_size = int(f.name.split("_")[-1].split(".")[0])
    print(Z,end=",")
    print(batch_size,end=",")
    print(n,end=',')
    print(avg,end=',')

    ##### ALL THIS STUFF CALCULATES AND PRINTS CONFIDENCE INTERVALS
    #print(n)
    # p(mu) = nCr mu^r (1-mu)^(n-r)
    # log(p(mu)/nCr) = rlog(mu) + (n-r)log(1-mu)
    l = np.log(0.95/comb(n,elements))
    ff = lambda mu: comb(n,elements)*(mu**elements)*((1-mu)**(n-elements))
    g = lambda mu: ff(mu)/ff(avg)-0.05
    if (g(avg)*g(1)<=0):
        upper = bisect(g,avg,1)
    else:
        upper = 0
    print(upper, end=",")
    if (g(avg)*g(0)<=0):
        lower = bisect(g,0,avg) 
    else:
        lower = 0
    print(lower)

    dataset.append((Z,batch_size,n,avg,upper,lower))

dataset = sorted(dataset)

labels = ["{}".format(d[0]) for d in dataset]
ys = [d[3] for d in dataset]
yerr = [[abs(d[5]-ys[i]),abs(d[4]-ys[i])] for i,d in enumerate(dataset)]
yerr = list(map(list,zip(*yerr)))
x_pos = np.arange(len(labels))

ys2 = [d[2]*100.0/1600 for d in w_dataset]
ys2_lower,ys2_upper = 1*math.floor(min(ys2)/1),1*math.ceil(max(ys2)/1)
ys2 = [(yy-ys2_lower)/(ys2_upper-ys2_lower) for yy in ys2]


# Build the plot
fig, ax = plt.subplots(figsize=(8.5,4.5))
ax.bar(x_pos, ys, yerr=yerr, align='center', alpha=0.9, ecolor='royalblue', color="lightskyblue", capsize=2, label="Exposure Risk")#, edgecolor = "black")
ax.plot(x_pos, ys2, color="black",linewidth=2, label="Wasserstein")
ax.set_ylabel('Exposure Risk that a synthetic output could be used\nto identify some individual in the population')
ax.set_xlabel('\nZ parameter')
ax.set_xticks(x_pos)
ax.set_xticklabels(labels,rotation=60,ha='right')
ax.set_title('Exposure Risk against Wasserstein distance\n')
#ax.yaxis.grid(True)

secay = ax.secondary_yaxis('right', functions=(lambda x:x*(ys2_upper-ys2_lower)+ys2_lower, lambda x:x))
secay.yaxis.set_minor_locator(AutoMinorLocator())
secay.set_ylabel('\nWasserstein Distance between Real and Synthetic Data\nas a proportion of maxium distance')
secay.get_yaxis().set_major_formatter(PercentFormatter(decimals=1))
plt.legend(loc="right")

# Save the figure and show
plt.tight_layout()
plt.savefig('bar_plot_with_error_bars.png')


