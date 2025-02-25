#!/usr/bin/env python3
from experiment_tools import *
from random import shuffle
import numpy as np
import pickle
import multiprocessing as mp
from sys import argv
from scipy.stats import wasserstein_distance_nd
from sklearn.decomposition import PCA


original_vcf_file1 = argv[1]
original_vcf_file2 = argv[2]
output_vcf_file1 = argv[3]
output_vcf_file2 = argv[4]

if len(argv)>5:
    sample_size=int(argv[5])
else:
    sample_size = None
silent=True

def load_file(f,postpend=True):
    extension = f.split(".")[-1]
    if extension=="pickle":
        with open(f,"rb") as f:
            p = pickle.load(f)
            if (len(p)==2) and isinstance(p[1],int):
                return p[0]
            return p
    else:
        return parse_VCF_to_genome_strings(f)[0]

original1 = load_file(original_vcf_file1)
original2 = load_file(original_vcf_file2)
output1 = load_file(output_vcf_file1)
output2 = load_file(output_vcf_file2)

shuffle(original1)
shuffle(original2)
if sample_size is not None:
    original1 = original1[:sample_size]
    original2 = original2[:sample_size]

original1 = [np.array(bytearray(r),dtype=np.int8) for r in original1]
original2 = [np.array(bytearray(r),dtype=np.int8) for r in original2]
output1 = [np.array(bytearray(r),dtype=np.int8) for r in output1]
output2 = [np.array(bytearray(r),dtype=np.int8) for r in output2]


def get_min_dist(x, dataset):
    min_dist = float("inf")
    for d in dataset:
        dist = np.linalg.norm(x-d,ord=0)
        if dist < min_dist:
            min_dist = dist
    return min_dist

def get_min_dist_pair(args):
    i,o,reverse = args
    x = get_min_dist(o,output1)*1.0/len(o)
    y = get_min_dist(o,output2)*1.0/len(o)
    if reverse:
        x,y=y,x
    return (x,y)

def wasserstein_analyse(genotypes1, genotypes2):
    genotypes1 = np.asarray(genotypes1)
    pca_transform = PCA(n_components=2,svd_solver='full').fit(genotypes1)
    coordinates1 = pca_transform.transform(genotypes1)
    coordinates2 = pca_transform.transform(np.asarray(genotypes2))
    return wasserstein_distance_nd(coordinates1,coordinates2,None,None)

if __name__ == '__main__':
    with mp.get_context("spawn").Pool(mp.cpu_count() ) as pool:
        results = ( list(pool.imap_unordered(get_min_dist_pair, [(i,o.copy(),False) for i,o in enumerate(original1)])) +
                    list(pool.imap_unordered(get_min_dist_pair, [(i,o.copy(),True ) for i,o in enumerate(original2)])) )
        pool.close()
        pool.join()
    w1 = wasserstein_analyse(original1,output1)
    w2 = wasserstein_analyse(original2,output2)

    x_results = [x for x,y in results]
    y_results = [y for x,y in results]
    print(np.mean(x_results),np.median(x_results))
    print(np.mean(y_results),np.median(y_results))
    print(w1, w2, (w1+w2)/2 )

