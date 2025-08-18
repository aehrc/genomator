import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from functools import reduce
from matplotlib.ticker import FuncFormatter

base_colours = ['r','b','g','m','c','k','y'] 
base_colours = ['#ffb840', '#E4002B', '#6d2382', '#008165']
base_colours = ['#ff0000', '#81ff00', '#00fff8', '#8100ff']
markers = ['o','o','o','o','o',]

with open("runtime_results.txt","r") as f:
    data = pd.read_csv(f)
data = data.fillna(11757483)

methods = set(data["METHOD"].tolist())
methods = sorted(list(methods))
times = {m:(data[data['METHOD']==m]['TIME']*1.0/60).tolist() for m in methods}
scales = {m:(data[data['METHOD']==m]['SCALE']).tolist() for m in methods}
results = {m:list(zip(*sorted(zip(*[scales[m],times[m]])))) for m in methods}



plt.figure(figsize=(8.8,5.6))
for index,m in enumerate(results.keys()):
    plt.plot(results[m][0],results[m][1],color=base_colours[index], label=m, linewidth=2, marker=markers[index])

plt.loglog()
plt.semilogx()
plt.title('Runtimes at Scale', pad=25)#, fontsize=15)
plt.xlabel('number of synthetic genomes generated', labelpad=17, fontsize=9)
plt.ylabel('Runtime to generate one synthetic genome (mins)', labelpad=17, fontsize=9)
plt.grid(visible=True, which='major', linewidth=0.5, linestyle='-')
plt.grid(visible=True, which='minor', linewidth=0.4, linestyle='-', axis="x")
lgnd = plt.legend(loc="center left", scatterpoints=1, fontsize=10, bbox_to_anchor=(1.05,0.5), frameon=False)
#plt.axis([0.1,20000,0.01,1000])

formatter = lambda x,y: "{0:g}".format(x)
plt.gca().xaxis.set_major_formatter(FuncFormatter(formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(formatter))

plt.tight_layout()
plt.savefig("runtime_graph.png", bbox_inches='tight')
