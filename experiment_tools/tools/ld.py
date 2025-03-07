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
from experiment_tools import *


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

def add_border(Z,size=20,fill=1):
    Z = [[fill]*len(Z[0]) for i in range(size)]+Z+[[fill]*len(Z[0]) for i in range(size)]
    Z = [([fill]*size)+zz+([fill]*size) for zz in Z]
    return Z

@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_image', type=click.types.Path())
@click.option('--begin', type=click.INT, default=None)
@click.option('--end', type=click.INT, default=None)
def ld_analyse(input_vcf_file, output_image, begin, end):
    genotypes = load_file(input_vcf_file)
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
    Z = np.array(add_border(Z.tolist(),fill=1.0))

    matplotlib.image.imsave(output_image, Z, cmap='Greys', vmin=0.0, vmax=1.0)

if __name__ == '__main__':
    ld_analyse()

