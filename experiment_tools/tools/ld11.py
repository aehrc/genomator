#!/usr/bin/env python3
#https://scikit-allel.readthedocs.io/en/stable/stats/ld.html

import click
import cyvcf2
from collections import defaultdict
import allel
from scipy.spatial.distance import squareform
import numpy as np
from collections import defaultdict
from tqdm import tqdm
from experiment_tools import *
import pickle

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

# just gets average of off-axis LD
@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
def ld_analyse(input_vcf_file):
    print("Loading VCF")
    genotype = load_file(input_vcf_file)
    genotypes = [list(zip(*[g[::2],g[1::2]])) for g in genotypes]
    g1 = allel.GenotypeArray(genotype,dtype='i1')
    del genotype
    gn1 = g1.to_n_alt(fill=-1)
    del g1
    r1 = allel.rogers_huff_r(gn1)
    del gn1
    r1 = np.nan_to_num(squareform(r1**2))

    diff_data = defaultdict(list)
    for i in tqdm(range(r1.shape[0])):
        for j in range(i,r1.shape[0]):
            datapoint = abs(r1[i,j])
            diff_data[j-i].append(datapoint)
    for d in diff_data.keys():
        diff_data[d] = np.mean(diff_data[d])
    print(np.mean(list(diff_data.values())))

if __name__ == '__main__':
    ld_analyse()

