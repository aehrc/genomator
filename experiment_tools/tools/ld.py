#!/usr/bin/env python3
#https://scikit-allel.readthedocs.io/en/stable/stats/ld.html

import click
from matplotlib import pyplot as plt
import cyvcf2
from collections import defaultdict
import math
import allel
from tqdm import tqdm
from scipy.spatial.distance import squareform
from scipy.ndimage.filters import gaussian_filter
import numpy as np
import matplotlib.image


def add_border(Z,size=20):
    Z = [[0]*len(Z[0]) for i in range(size)]+Z+[[0]*len(Z[0]) for i in range(size)]
    Z = [([0]*size)+zz+([0]*size) for zz in Z]
    return Z

@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_image', type=click.types.Path())
@click.option('--begin', type=click.INT, default=None)
@click.option('--end', type=click.INT, default=None)
def ld_analyse(input_vcf_file, output_image, begin, end):
    reader = cyvcf2.VCF(input_vcf_file)
    genotypes = []
    print("loading VCF")
    for record in tqdm(reader):
        genotypes.append([a[:-1] for a in record.genotypes])
    del reader
    print("generating genotype array")
    g = allel.GenotypeArray(genotypes,dtype='i1')
    del genotypes
    print("generating n_alt array")
    gn = g.to_n_alt(fill=-1)
    del g
    print("performing rogers_huff method")
    r = allel.rogers_huff_r(gn)
    del gn
    print("converting to squareform")
    Z = squareform(r ** 2)
    del r
    if (begin is not None) and (end is not None):
        Z = Z[begin:end,begin:end]
    Z = np.nan_to_num(Z)

    print("performing image conversion")
    #plt.imshow(Z,interpolation="nearest")
    #print("outputting")
    #plt.savefig(output_image, bbox_inches='tight')

    Z = gaussian_filter(Z,sigma=2)
    Z = 2.0/(1+np.power(Z-1,10))-1
    Z = np.array(add_border(Z.tolist()))
    

    matplotlib.image.imsave(output_image, Z, cmap='Grays', vmin=0.0, vmax=1.0)

if __name__ == '__main__':
    ld_analyse()

