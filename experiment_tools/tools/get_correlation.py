#!/usr/bin/env python3
#https://scikit-allel.readthedocs.io/en/stable/stats/ld.html

import click
import cyvcf2
import numpy as np
from tqdm import tqdm

# just calculates correlation of allele frequencies
@click.command()
@click.argument('input_vcf_file1', type=click.types.Path())
@click.argument('input_vcf_file2', type=click.types.Path())
@click.option('--allele_sum', type=click.types.BOOL, default=True)
def correlation_analyse(input_vcf_file1,input_vcf_file2,allele_sum):
    print("Loading VCF1")
    reader = cyvcf2.VCF(input_vcf_file1)
    genotype1 = []
    for record in tqdm(reader):
        if not allele_sum:
            genotype1 += list(zip([b[:-1] for b in record.genotypes]))
        else:
            genotype1 += [[sum(b[:-1]) for b in record.genotypes]]
    reader.close()
    genotype1 = [np.average(g) for g in tqdm(genotype1)]

    print("Loading VCF2")
    reader = cyvcf2.VCF(input_vcf_file2)
    genotype2 = []
    for record in tqdm(reader):
        if not allele_sum:
            genotype2 += list(zip([b[:-1] for b in record.genotypes]))
        else:
            genotype2 += [[sum(b[:-1]) for b in record.genotypes]]
    reader.close()
    genotype2 = [np.average(g) for g in tqdm(genotype2)]

    print(np.corrcoef(genotype1,genotype2)[0,1])
    
if __name__ == '__main__':
    correlation_analyse()

