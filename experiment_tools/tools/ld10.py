#!/usr/bin/env python3
#https://scikit-allel.readthedocs.io/en/stable/stats/ld.html

import click
import cyvcf2
from collections import defaultdict
import math
import allel
from tqdm import tqdm
from scipy.spatial.distance import squareform
import numpy as np
from collections import defaultdict
from tqdm import tqdm
import random


@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('compare_vcf_file', nargs=-1, type=click.types.Path())
@click.option('--max_offset', type=click.INT, default=None)
@click.option('--max_y_limit', type=click.FLOAT, default=None)
def ld_analyse(input_vcf_file,compare_vcf_file,max_offset,max_y_limit):
    assert len(compare_vcf_file)>0, "need to supply vcf file inputs"
    print("Loading Reference VCFs")
    reader = cyvcf2.VCF(input_vcf_file)
    ref_genotype = []
    positions = []
    for record in reader:
        ref_genotype.append([b[:-1] for b in record.genotypes])
        positions.append(record.start)
    reader.close()
    average_diff_positions = []
    for i in range(len(positions)):
        A = []
        for j in range(len(positions)-i):
            A.append(positions[j+i] - positions[j])
        average_diff_positions.append(np.mean(A)/1000)

    ref_g1 = allel.GenotypeArray(ref_genotype,dtype='i1')
    del ref_genotype
    ref_gn1 = ref_g1.to_n_alt(fill=-1)
    del ref_g1
    ref_r1 = allel.rogers_huff_r(ref_gn1)
    del ref_gn1
    ref_r1 = np.nan_to_num(squareform(ref_r1**2))

    for index,file in tqdm(enumerate(compare_vcf_file)):
        print("processing file {}".format(file))
        reader = cyvcf2.VCF(file)
        g = [[b[:-1] for b in record.genotypes] for record in reader]
        reader.close()
        g1 = allel.GenotypeArray(g,dtype='i1')
        del g
        gn1 = g1.to_n_alt(fill=-1)
        del g1
        r1 = allel.rogers_huff_r(gn1)
        del gn1
        r1 = np.nan_to_num(squareform(r1**2))

        diff_data = defaultdict(list)
        for i in range(r1.shape[0]):
            for j in range(i,r1.shape[0]):
                datapoint = abs(r1[i,j] - ref_r1[i,j])**2
                diff_data[j-i].append(datapoint)
        for d in diff_data.keys():
            diff_data[d] = np.mean(diff_data[d])
        print(np.mean(list(diff_data.values())))

        del r1


if __name__ == '__main__':
    ld_analyse()

