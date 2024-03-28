#!/usr/bin/env python3
import click
from experiment_tools import *
from matplotlib import pyplot as plt
from random import shuffle
from tqdm import tqdm
import seaborn as sns
import numpy as np
import scipy

def get_min_dist(x, dataset):
    min_dist = float("inf")
    for d in dataset:
        dist = sum(a1!=a2 for a1,a2 in zip(x,d))
        if dist < min_dist:
            min_dist = dist
    return min_dist


@click.command()
@click.argument('original_vcf_file1', type=click.types.Path())
@click.argument('original_vcf_file2', type=click.types.Path())
@click.argument('output_vcf_file1', type=click.types.Path())
@click.argument('output_vcf_file2', type=click.types.Path())
@click.option('--sample_size', '-s', type=click.INT, default=None)
def attribute_experiment(original_vcf_file1, original_vcf_file2, output_vcf_file1, output_vcf_file2,sample_size):
    original1, _ = parse_VCF_to_genome_strings(original_vcf_file1)
    original2, _ = parse_VCF_to_genome_strings(original_vcf_file2)
    output1, _ = parse_VCF_to_genome_strings(output_vcf_file1)
    output2, _ = parse_VCF_to_genome_strings(output_vcf_file2)
    
    shuffle(original1)
    shuffle(original2)
    if sample_size is not None:
        original1 = original1[:sample_size]
        original2 = original2[:sample_size]

    results = []
    for o in tqdm(original1):
        x = get_min_dist(o,output1)*1.0/len(o)
        y = get_min_dist(o,output2)*1.0/len(o)
        results.append((x,y))
    for o in tqdm(original2):
        x = get_min_dist(o,output2)*1.0/len(o)
        y = get_min_dist(o,output1)*1.0/len(o)
        results.append((x,y))

    x_results = [x for x,y in results]
    y_results = [y for x,y in results]
    print(np.mean(x_results),np.median(x_results))
    print(np.mean(y_results),np.median(y_results))
    results_ratio = [y/x if x>0 else 9999 for x,y in results]
    print(np.mean(results_ratio))
    print(np.median(results_ratio))
    results_difference = [y-x for x,y in results]
    print(np.mean(results_difference))
    print(np.median(results_difference))


if __name__ == '__main__':
    attribute_experiment()
