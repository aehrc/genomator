#!/usr/bin/env python3
from collections import defaultdict
import csv
from math import sqrt
import sys


reader = csv.reader(sys.stdin, delimiter='\t')
next(reader)  # Skip header
converted_data = defaultdict(list)
for method_id, median_x_str, median_y_str in reader:
    base_method = method_id.split("_")[0]
    median_x = float(median_x_str)
    difference = float(median_y_str) - median_x
    converted_data[base_method].append((median_x, difference, method_id))

converted_data_keys = list(converted_data.keys())
d = lambda x,y: sqrt(x**2+y**2)
for k in converted_data_keys:
    converted_data[k] = [(d(a,b),c) for a,b,c in converted_data[k]]
print(f"METHOD_CLASS\tDISTANCE_TO_IDEAL")
for k in converted_data_keys:
    min_instance = min(converted_data[k],key=lambda x:x[0])
    print(f"{k}\t{min_instance[0]}")
