#!/usr/bin/env python3
from functools import reduce
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


METHOD = "Method"
SCALE = "SNPs"
TIME = "Time(s)"


base_colours = ['r','b','g','m','c','k','y'] 
with open(sys.argv[1], "r") as f:
    data = pd.read_csv(f)
data = data.fillna(11757483)

methods = set(data[METHOD].tolist())
methods = sorted(list(methods))
results = {m:(data[data[METHOD]==m][TIME]*1.0/60).tolist() for m in methods}
snps = reduce(lambda a,b: a|b, [set(data[data[METHOD]==m][SCALE].tolist()) for m in methods] )
snps = sorted(list(snps))
snps = [s*1.0/1000 for s in snps]
results = {m:(snps[:len(results[m])],results[m]) for m in results.keys()}

plt.figure(figsize=(8.8,5.6))
for index,m in enumerate(results.keys()):
    plt.plot(results[m][0],results[m][1],color=base_colours[index], label=m, linewidth=2)
    if m!="GENOMATOR":
        plt.annotate("✕",xy=(results[m][0][-1], results[m][1][-1]), ha='center',va='center', fontsize=16)

plt.loglog()
plt.title('Runtimes at Scale', pad=25)
plt.xlabel('number of SNPs (x1000)', labelpad=17, fontsize=9)
plt.ylabel('Runtime to generate one synthetic genome (mins)', labelpad=17, fontsize=9)
plt.grid(visible=True, which='major', linewidth=0.5, linestyle='-')
plt.grid(visible=True, which='minor', linewidth=0.4, linestyle='-', axis="x")
lgnd = plt.legend(loc="center left", scatterpoints=1, fontsize=10, bbox_to_anchor=(1.05,0.5), frameon=False)
plt.axis([0.1,20000,0.01,1000])

formatter = lambda x,y: "{0:g}".format(x)
plt.gca().xaxis.set_major_formatter(FuncFormatter(formatter))
plt.gca().yaxis.set_major_formatter(FuncFormatter(formatter))

plt.tight_layout()
plt.savefig(sys.argv[2], bbox_inches='tight')
