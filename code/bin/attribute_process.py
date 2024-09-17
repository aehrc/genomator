#!/usr/bin/env python3
from matplotlib import pyplot as plt
from collections import defaultdict
import csv
import sys

reader = csv.reader(sys.stdin, delimiter='\t')
next(reader)  # Skip header
converted_data = defaultdict(list)
print(f"method\tin-data distance\tout-data distance minus in-data distance")
for method_id, median_x_str, median_y_str in reader:
    base_method = method_id.split("_")[0]
    median_x = float(median_x_str)
    difference = float(median_y_str) - median_x
    converted_data[base_method].append((median_x, difference))
    print(f"{method_id}\t{median_x}\t{difference}")

base_colours = ['r','b','g','m','c','k','y']
markers = ['.','v','s','P','*','d','X']
plt.figure()
for i,k in enumerate(sorted(converted_data.keys())):
    xs,ys = list(zip(*converted_data[k]))
    plt.scatter(xs,
            ys,
            s=14,
            c=[base_colours[i]],
            label=k,
            alpha=0.8,
            marker=markers[i])

lgnd = plt.legend(loc="upper right", scatterpoints=1, fontsize=10)
plt.xlabel("In-data distance")
plt.ylabel("Out-data distance minus In-data distance")
plt.savefig("results.png", bbox_inches='tight')
