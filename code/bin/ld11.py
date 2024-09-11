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

# just gets average of off-axis LD
@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
def ld_analyse(input_vcf_file):
    print("Loading VCF")
    reader = cyvcf2.VCF(input_vcf_file)
    genotype = []
    for record in tqdm(reader):
        genotype.append([b[:-1] for b in record.genotypes])
    reader.close()
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
