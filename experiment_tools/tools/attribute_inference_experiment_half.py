#!/usr/bin/env python3
from experiment_tools import *
from random import shuffle
import numpy as np
import pickle
import multiprocessing as mp
from sys import argv


original_vcf_file1 = argv[1]
original_vcf_file2 = argv[2]
output_vcf_file1 = argv[3]

if len(argv)>5:
    sample_size=int(argv[5])
else:
    sample_size = None
silent=True

original1_extension = original_vcf_file1.split(".")[-1]
original2_extension = original_vcf_file2.split(".")[-1]
if original1_extension=="pickle":
    with open(original_vcf_file1,"rb") as f:
        original1,_ = pickle.load(f)
else:
    original1, _ = parse_VCF_to_genome_strings(original_vcf_file1,silent=silent)
if original2_extension=="pickle":
    with open(original_vcf_file2,"rb") as f:
        original2,_ = pickle.load(f)
else:
    original2, _ = parse_VCF_to_genome_strings(original_vcf_file2,silent=silent)

output1_extension = output_vcf_file1.split(".")[-1]
if output1_extension=="pickle":
    with open(output_vcf_file1,"rb") as f:
        output1 = pickle.load(f)
else:
    output1, _ = parse_VCF_to_genome_strings(output_vcf_file1,silent=silent)

shuffle(original1)
shuffle(original2)
if sample_size is not None:
    original1 = original1[:sample_size]
    original2 = original2[:sample_size]

original1 = [np.array(bytearray(r),dtype=np.int8) for r in original1]
original2 = [np.array(bytearray(r),dtype=np.int8) for r in original2]
output1 = [np.array(bytearray(r),dtype=np.int8) for r in output1]


def get_min_dist(x, dataset):
    min_dist = float("inf")
    for d in dataset:
        dist = np.linalg.norm(x-d,ord=0)
        if dist < min_dist:
            min_dist = dist
    return min_dist

def get_min_dist_pair(args):
    i,o,out = args
    if not out:
        return get_min_dist(o,original1)*1.0/len(o)
    else:
        return get_min_dist(o,original2)*1.0/len(o)

if __name__ == '__main__':
    with mp.get_context("spawn").Pool(mp.cpu_count() ) as pool:
        results_out = list(pool.imap_unordered(get_min_dist_pair, [(i,o.copy(),False) for i,o in enumerate(output1)])) 
        results_in  = list(pool.imap_unordered(get_min_dist_pair, [(i,o.copy(),True ) for i,o in enumerate(output1)])) 
        pool.close()
        pool.join()

    x_results = results_in
    y_results = results_out
    print(np.mean(x_results),np.median(x_results))
    print(np.mean(y_results),np.median(y_results))
    print(0)
    print(0)
    results_difference = [y_results[i]-x_results[i] for i in range(len(x_results))]
    print(np.mean(results_difference))
    print(np.median(results_difference))

