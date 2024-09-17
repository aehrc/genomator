#!/usr/bin/env python3
import click
from experiment_tools import *
from random import shuffle
from tqdm import tqdm
import numpy as np

def get_min_dist(x, dataset):
    min_dist = float("inf")
    for d in dataset:
        dist = np.linalg.norm(x-d,ord=0)
        if dist < min_dist:
            min_dist = dist
    return min_dist


@click.command()
@click.argument('original_vcf_file1', type=click.types.Path())
@click.argument('original_vcf_file2', type=click.types.Path())
@click.argument('output_vcf_file1', type=click.types.Path())
@click.argument('output_vcf_file2', type=click.types.Path())
@click.option('--sample_size', '-s', type=click.INT, default=None)
def attribute_experiment(original_vcf_file1, original_vcf_file2, output_vcf_file1, output_vcf_file2, sample_size, silent):
    original1, _ = parse_VCF_to_genome_strings(original_vcf_file1, silent=silent)
    original2, _ = parse_VCF_to_genome_strings(original_vcf_file2, silent=silent)
    output1, _ = parse_VCF_to_genome_strings(output_vcf_file1, silent=silent)
    output2, _ = parse_VCF_to_genome_strings(output_vcf_file2, silent=silent)
    if not (len(original1)>0 and len(original2)>0 and len(output1)>0 and len(output2)>0):
        if not silent:
            print("ERROR: Inputs empty")
        return
    
    shuffle(original1)
    shuffle(original2)
    if sample_size is not None:
        original1 = original1[:sample_size]
        original2 = original2[:sample_size]

    original1 = [np.array(bytearray(r),dtype=np.int8) for r in original1]
    original2 = [np.array(bytearray(r),dtype=np.int8) for r in original2]
    output1 = [np.array(bytearray(r),dtype=np.int8) for r in output1]
    output2 = [np.array(bytearray(r),dtype=np.int8) for r in output2]

    results = []
    for o in tqdm(original1) if not silent else original1:
        x = get_min_dist(o,output1)*1.0/len(o)
        y = get_min_dist(o,output2)*1.0/len(o)
        results.append((x,y))
    for o in tqdm(original2) if not silent else original2:
        x = get_min_dist(o,output2)*1.0/len(o)
        y = get_min_dist(o,output1)*1.0/len(o)
        results.append((x,y))

    x_results = [x for x,y in results]
    y_results = [y for x,y in results]
    print(np.median(x_results),np.median(y_results),sep="\t")


if __name__ == '__main__':
    attribute_experiment()
