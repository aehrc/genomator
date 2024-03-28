#!/usr/bin/env python3
from random import choice, randint, shuffle
from tqdm import tqdm

def default_selector(A,B):
    return choice(list(set(A+B)))

def export_xcorr(transpose_genomes1, transpose_genomes2, degree, trials=1000, selector=default_selector):
    datapoints = []
    pbar = tqdm(total=len(datapoints))
    while len(datapoints) < trials:
        gen1 = []
        gen2 = []
        for d in range(degree):
            i1 = randint(0,len(transpose_genomes1)-1)
            gen1.append(transpose_genomes1[i1])
            gen2.append(transpose_genomes2[i1])
        gen1_doubles = list(zip(*gen1))
        gen2_doubles = list(zip(*gen2))
        s = selector(gen1_doubles,gen2_doubles)
        if s is None:
            continue
        datapoints.append(s)
        pbar.update(1)
    pbar.close()
    return datapoints



from experiment_tools import *
import json
import click
import pickle
from itertools import product
from matplotlib import pyplot as plt
from collections import defaultdict

# select one that is unique from A (if you can) and count how often it appears in B
def select_unique_A_count_B(A,B):
    Aset = set(A)
    Adict = {a:A.count(a) for a in Aset}
    Aunique = [a for a,c in Adict.items() if c==1]
    if len(Aunique)==0:
        return None
    Bcounts = [B.count(a) for a in Aunique]
    return Bcounts

# select one that is not in A (if you can)
def select_non_A_count_B(A,B):
    elements = set(sum([list(a) for a in set(A+B)],[]))
    possibilities = set(product(elements,repeat=len(A[0])))
    Aset = set(A)
    diffset = list(possibilities.difference(Aset))
    if len(diffset) == 0:
        return None
    Bcounts = [B.count(a) for a in diffset]
    return Bcounts

base_colours = ['r','b','g','m','c','k','y'] 
markers = ['.','v','s','P','*','d','X']
@click.command()
@click.argument('input_vcf_files', nargs=-1, type=click.types.Path())
@click.option('--trials', '-t', type=click.types.INT, default=10000)
@click.option('--degree', '-d', type=click.types.INT, default=4)
@click.option('--output_image_file', default="Rare_SNP_analysis_output.png")
def Rare_SNP_analyse(input_vcf_files,trials,degree,output_image_file):
    input_vcf_files, dataset_files = input_vcf_files[1::2], input_vcf_files[::2]
    if len(dataset_files)==0:
        assert False, "you need to provide some dataset files"
    loaded_genome_files = {f:parse_VCF_to_genome_strings(f) for f in set(input_vcf_files)}
    ref_genomes = [loaded_genome_files[input_vcf_file][0] for input_vcf_file in input_vcf_files]
    datasets = []
    for f in dataset_files:
        extension = f.split(".")[-1]
        if extension=="vcf":
            datasets.append(parse_VCF_to_genome_strings(f)[0])
        elif extension=="pickle":
            with open(f,"rb") as f:
                datasets.append(pickle.load(f))
    transpose_ref_genomes = [list(map(tuple, zip(*r))) for r in ref_genomes]
    labels = {}
    for filename in dataset_files:
        labels[filename] = filename.split("/")[-1].split("_")[0]
    label_values = sorted(list(set(labels.values())))
    label_colours = {}
    label_markers = {}
    for k in labels.keys():
        label_colours[k] = base_colours[label_values.index(labels[k])]
        label_markers[k] = markers[label_values.index(labels[k])]
    reverse_labels = defaultdict(list)
    for k,v in labels.items():
        reverse_labels[v].append(dataset_files.index(k))
    plt.figure()
    for k in sorted(reverse_labels.keys()):
        xs = []
        ys = []
        for i in reverse_labels[k]:
            d = datasets[i]
            print(dataset_files[i])
            td = list(map(tuple, zip(*d)))
            unique_responses = export_xcorr(transpose_ref_genomes[i], td, degree, trials=trials, selector=select_unique_A_count_B)
            zero_responses = export_xcorr(transpose_ref_genomes[i], td, degree, trials=trials, selector=select_non_A_count_B)
            unique_responses = sum(unique_responses,[])
            zero_responses = sum(zero_responses,[])
            ratio_unique_responses_greater_than_zero = sum([a>0 for a in unique_responses])*1.0/len(unique_responses)
            ratio_zero_responses_greater_than_zero = sum([a>0 for a in zero_responses])*1.0/len(zero_responses)
            print(ratio_unique_responses_greater_than_zero,ratio_zero_responses_greater_than_zero)
            xs.append(ratio_unique_responses_greater_than_zero)
            ys.append(ratio_zero_responses_greater_than_zero)
        plt.scatter(xs, ys, s=14, c=[label_colours[dataset_files[i]]], label=labels[dataset_files[i]], alpha=0.8, marker=label_markers[dataset_files[i]])
    lgnd = plt.legend(loc="upper left", scatterpoints=1, fontsize=10)
    #for i in range(len(lgnd.legendHandles)):
    #    lgnd.legendHandles[i]._sizes = [30]
    plt.yscale("log")
    plt.xscale("log")
    plt.xlabel("Expectation of private quadruplet occuring in output")
    plt.ylabel("Expectation of fictitious quadruplet occuring in output")
    plt.savefig(output_image_file, bbox_inches='tight')

if __name__ == '__main__':
    Rare_SNP_analyse()

