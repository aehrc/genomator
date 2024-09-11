#!/usr/bin/env python3
import click
from experiment_tools import *
from matplotlib import pyplot as plt
from tqdm import tqdm
from random import shuffle
from copy import deepcopy as copy
import json

def get_min_dist(x, dataset):
    min_dist = float("inf")
    index = None
    for i,d in enumerate(dataset):
        dist = sum(a1!=a2 for a1,a2 in zip(x,d))
        if dist < min_dist:
            min_dist = dist
            index = i
    return index


@click.command()
@click.argument('input_vcf_file1', type=click.types.Path())
@click.argument('output_vcf_file1', type=click.types.Path())
@click.argument('output_vcf_file2', type=click.types.Path())
@click.option('--index_output_file', type=click.types.Path(), default=None)
def pair_splitter(input_vcf_file1, output_vcf_file1, output_vcf_file2, index_output_file):
    vcf_in, ploidy = parse_VCF_to_genome_strings(input_vcf_file1)
    if index_output_file is not None:
        backup_vcf_in = copy(vcf_in)
    shuffle(vcf_in)
    
    results1 = []
    results2 = []
    pbar = tqdm(total=len(vcf_in))
    while len(vcf_in)>0:
        results1,results2 = results2,results1
        o = vcf_in.pop()
        results1.append(o)
        pbar.update(1)
        if len(vcf_in)>0:
            p = vcf_in.pop(get_min_dist(o,vcf_in))
            results2.append(p)
            pbar.update(1)
    pbar.close()
    
    parse_genome_strings_to_VCF(results1, input_vcf_file1, output_vcf_file1, ploidy)
    parse_genome_strings_to_VCF(results2, input_vcf_file1, output_vcf_file2, ploidy)
    if index_output_file is not None:
        with open(index_output_file,'w') as f:
            f.write("VCF SPLIT INDEX FILE\n")
            f.write(json.dumps([backup_vcf_in.index(v) for v in results1]))
            f.write("\n")
            f.write(json.dumps([backup_vcf_in.index(v) for v in results2]))




if __name__ == '__main__':
    pair_splitter()
