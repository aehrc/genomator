#!/usr/bin/env python3
#https://scikit-allel.readthedocs.io/en/stable/stats/ld.html

import click
import cyvcf2
import math
import allel
from tqdm import tqdm
#from scipy.stats import wasserstein_distance
import ot
import numpy as np
from sklearn.decomposition import PCA
from experiment_tools import parse_VCF_to_genome_strings

@click.command()
@click.argument('input_vcf_file1', type=click.types.Path())
@click.argument('input_vcf_file2', type=click.types.Path())
@click.option('--slices', type=click.INT, default=300)
@click.option('--samples', type=click.INT, default=200)
def wasserstein_analyse(input_vcf_file1,input_vcf_file2,slices,samples):
    genotypes1,_ = parse_VCF_to_genome_strings(input_vcf_file1)
    genotypes2,_ = parse_VCF_to_genome_strings(input_vcf_file2)
    genotypes1 = [list(g) for g in genotypes1]
    genotypes2 = [list(g) for g in genotypes2]

    genotypes1 = np.array(genotypes1)
    genotypes2 = np.array(genotypes2)
    genotypes1_balance = np.array([len(genotypes2) for i in range(len(genotypes1))])
    genotypes2_balance = np.array([len(genotypes1) for i in range(len(genotypes2))])

    pca_transform = PCA(n_components=2,svd_solver='full').fit(np.asarray(np.matrix(genotypes1)))
    genotypes1_transform = pca_transform.transform(genotypes1)
    genotypes2_transform = pca_transform.transform(genotypes2)
    
    slices = [ot.sliced_wasserstein_distance(
            genotypes1_transform,
            genotypes2_transform,
            genotypes1_balance,
            genotypes2_balance,
            slices) for i in tqdm(range(samples))]
    slice_mean = np.mean(slices)
    slice_std = np.std(slices)
    print(slice_mean,slice_std, sep='\t')


if __name__ == '__main__':
    wasserstein_analyse()
