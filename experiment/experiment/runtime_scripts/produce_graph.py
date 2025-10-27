import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from functools import reduce
from matplotlib.ticker import FuncFormatter

base_colours = ['r','b','g','m','c','k','y'] 
#base_colours = ['#ffb840', '#E4002B', '#6d2382', '#008165']
#base_colours = ['#ff0000', '#81ff00', '#00fff8', '#8100ff']

with open("runtime_results.txt","r") as f:
    data = pd.read_csv(f)
data = data.fillna(11757483)

methods = set(data["METHOD"].tolist())
methods = sorted(list(methods))
times = {m:(data[data['METHOD']==m]['TIME']*1.0/60).tolist() for m in methods}
scales = {m:(data[data['METHOD']==m]['SCALE']*1.0/1000).tolist() for m in methods}
results = {m:list(zip(*sorted(zip(*[scales[m],times[m]])))) for m in methods}



plt.figure(figsize=(8.8,5.6))
for index,m in enumerate(results.keys()):
    plt.plot(results[m][0],results[m][1],color=base_colours[index], label=m, linewidth=2)
    if m=="Wgan":
        plt.annotate("✕",xy=(results[m][0][-1], results[m][1][-1]), ha='center',va='center', fontsize=16, color=base_colours[index])

'''extrapolated_x = [results['GENOMATOR'][0][-1], 64500000/1000]
extrapolated_y = [results['GENOMATOR'][1][-1],
        results['GENOMATOR'][1][-1] + 
        (results['GENOMATOR'][1][-1] - results['GENOMATOR'][1][-2])*(1.0/(results['GENOMATOR'][0][-1] - results['GENOMATOR'][0][-2])) *
        (extrapolated_x[-1]-extrapolated_x[-2]) ]
plt.plot(extrapolated_x, extrapolated_y, linestyle=(0,(1.5,2)), color=base_colours[methods.index('GENOMATOR')], linewidth=2)
'''
plt.loglog()
plt.semilogx()
plt.title('Runtimes at Scale', pad=25)#, fontsize=15)
plt.xlabel('number of SNPs (x1000)', labelpad=17, fontsize=9)
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
plt.savefig("runtime_graph.eps", format='eps', dpi=300, bbox_inches='tight') 
