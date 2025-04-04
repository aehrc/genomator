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
import numpy as np
import matplotlib.image
from collections import defaultdict
from tqdm import tqdm
import random
import statistics
from resample.bootstrap import confidence_interval
from experiment_tools import *
import pickle

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]




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

def load_file_into_genotype_array(f,skipping=1):
    genotype = load_file(f)
    a1 = list(np.array(bytearray(g))[0::2*skipping].transpose() for g in genotype)
    a2 = list(np.array(bytearray(g))[1::2*skipping].transpose() for g in genotype)
    Z = np.dstack([a1,a2]).transpose([1,0,2])
    g1 = allel.GenotypeArray([[[0,0]]],dtype='i1')
    g1._values = Z
    return g1


base_colours = ['r','b','g','m','c','k','y'] 
markers = ['.','v','s','P','*','d','X']
@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('compare_vcf_file', nargs=-1, type=click.types.Path())
@click.option('--max_offset', type=click.INT, default=None)
@click.option('--max_y_limit', type=click.FLOAT, default=None)
@click.option('--chunk_size', type=click.INT, default=5)
@click.option('--output_image_file', default="LD.png")
@click.option('--skip', type=click.INT, default=1)
def ld_analyse(input_vcf_file,compare_vcf_file,max_offset,max_y_limit,chunk_size,output_image_file,skip):
    assert len(compare_vcf_file)>0, "need to supply vcf file inputs"
    print("Loading Reference VCFs")
    reader = cyvcf2.VCF(input_vcf_file)
    ref_genotype = []
    positions = []
    for i,record in enumerate(reader):
        if i%skip==0:
            ref_genotype.append([b[:-1] for b in record.genotypes])
            positions.append(record.start)
    reader.close()
    print("computing average position differences")
    average_diff_positions = []
    for i in range(len(positions)):
        A = []
        for j in range(len(positions)-i):
            A.append(positions[j+i] - positions[j])
        average_diff_positions.append(np.mean(A)/1000)

    print("generating genotype array1")
    ref_g1 = allel.GenotypeArray(ref_genotype,dtype='i1')
    del ref_genotype
    print("generating n_alt array")
    ref_gn1 = ref_g1.to_n_alt(fill=-1)
    del ref_g1
    print("performing rogers_huff method")
    ref_r1 = allel.rogers_huff_r(ref_gn1)
    del ref_gn1
    print("squaring")
    ref_r1 = np.nan_to_num(squareform(ref_r1**2))

    plt.figure()
    for index,file in tqdm(enumerate(compare_vcf_file)):
        print("processing file {}".format(file))
        g1 = load_file_into_genotype_array(file,skip)
        print("generating n_alt array")
        gn1 = g1.to_n_alt(fill=-1)
        del g1
        print("performing rogers_huff method")
        r1 = allel.rogers_huff_r(gn1)
        del gn1
        print("squaring")
        r1 = np.nan_to_num(squareform(r1**2))

        diff_data = defaultdict(list)
        for i in range(r1.shape[0]):
            for j in range(i,r1.shape[0]):
                datapoint = abs(r1[i,j] - ref_r1[i,j])**2
                diff_data[j-i].append(datapoint)
        del r1

        dx,dy = zip(*list(diff_data.items()))
        ddy = [confidence_interval(np.mean,d) for d in dy]
        dy_lower = [d[0] for d in ddy]
        dy_upper = [d[1] for d in ddy]
        dy = [np.mean(d) for d in dy]
        if max_offset is not None:
            dx = dx[:max_offset]
            dy = dy[:max_offset]
            dy_upper = dy_upper[:max_offset]
            dy_lower = dy_lower[:max_offset]
        dx = [average_diff_positions[d] for d in dx]
        dy = [statistics.mean(c) for c in chunks(dy,chunk_size)]
        dy_upper = [statistics.mean(c) for c in chunks(dy_upper,chunk_size)]
        dy_lower = [statistics.mean(c) for c in chunks(dy_lower,chunk_size)]
        dx = [statistics.mean(c) for c in chunks(dx,chunk_size)]
        plt.plot(dx, dy, c=base_colours[index],
                label=compare_vcf_file[index].split("/")[-1].split("_")[0].split(".")[0], alpha=1.0, marker=markers[index])
        plt.fill_between(dx,dy_lower,dy_upper,color=base_colours[index],alpha=0.2)
        if max_y_limit:
            plt.ylim(0,max_y_limit)
    lgnd = plt.legend(loc="upper right", scatterpoints=1, fontsize=10)
    if 'legendHandles' in dir(lgnd):
        for i in range(len(compare_vcf_file)):
            lgnd.legendHandles[i]._sizes = [30]
    else:
        for i in range(len(compare_vcf_file)):
            lgnd.legend_handles[i]._sizes = [30]
    plt.title(input_vcf_file.split("/")[-1].split("_")[0].split(".")[0].upper())
    plt.xlabel("distance between loci (kb)")
    plt.ylabel("Average Square error")
    plt.savefig(output_image_file, bbox_inches='tight')

if __name__ == '__main__':
    ld_analyse()

