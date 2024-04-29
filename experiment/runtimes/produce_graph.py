import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from functools import reduce
from matplotlib.ticker import FuncFormatter

base_colours = ['r','b','g','m','c','k','y'] 

with open("runtime_results.txt","r") as f:
    data = pd.read_csv(f)
data = data.fillna(23514966)

methods = set(data["METHOD"].tolist())
methods = sorted(list(methods))
results = {m:(data[data['METHOD']==m]['TIME']*1.0/60).tolist() for m in methods}
snps = reduce(lambda a,b: a|b, [set(data[data['METHOD']==m]['SCALE'].tolist()) for m in methods] )
snps = sorted(list(snps))
snps = [s*1.0/1000 for s in snps]
results = {m:(snps[:len(results[m])],results[m]) for m in results.keys()}

plt.figure(figsize=(8.8,5.6))
for index,m in enumerate(results.keys()):
    plt.plot(results[m][0],results[m][1],color=base_colours[index], label=m, linewidth=2)
    if m!="GENOMATOR":
        plt.annotate("✕",xy=(results[m][0][-1], results[m][1][-1]), ha='center',va='center', fontsize=16)

extrapolated_x = [results['GENOMATOR'][0][-1], 64500000]
extrapolated_y = [results['GENOMATOR'][1][-1],
        results['GENOMATOR'][1][-1] + 
        (results['GENOMATOR'][1][-1] - results['GENOMATOR'][1][-2])*(1.0/(results['GENOMATOR'][0][-1] - results['GENOMATOR'][0][-2])) *
        (extrapolated_x[-1]-extrapolated_x[-2]) ]
plt.plot(extrapolated_x, extrapolated_y, linestyle=(0,(1.5,2)), color=base_colours[methods.index('GENOMATOR')], linewidth=2)

plt.loglog()
plt.title('Runtimes at Scale', pad=25)#, fontsize=15)
plt.xlabel('number of SNPs (x1000)', labelpad=17, fontsize=9)
plt.ylabel('Runtime to generate one synthetic genome (mins)', labelpad=17, fontsize=9)
plt.grid(visible=True, which='major', linewidth=0.5, linestyle='-')
plt.grid(visible=True, which='minor', linewidth=0.4, linestyle='-', axis="x")
lgnd = plt.legend(loc="center left", scatterpoints=1, fontsize=10, bbox_to_anchor=(1.05,0.5), frameon=False)
plt.axis([0.1,100000,0.01,10000])

formatter = lambda x,y: "{0:g}".format(x)
plt.gca().xaxis.set_major_formatter(FuncFormatter(formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(formatter))

plt.tight_layout()
plt.show()
