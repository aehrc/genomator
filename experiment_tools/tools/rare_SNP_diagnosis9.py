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

# select one that is unique from A (if you can) and return if it is unique in B
def unique_A_check_unique_B(A,B):
    Aset = set(A)
    Adict = {a:A.count(a) for a in Aset}
    Aunique = [a for a,c in Adict.items() if c==1]
    if len(Aunique)==0:
        return None
    Bcounts = [1 if B.count(a)==1 else 0 for a in Aunique]
    return Bcounts


# select one that is unique from A (if you can) and return if it is not in B
def unique_A_check_fictitious_B(A,B):
    Aset = set(A)
    Adict = {a:A.count(a) for a in Aset}
    Aunique = [a for a,c in Adict.items() if c==1]
    if len(Aunique)==0:
        return None
    Bcounts = [1 if B.count(a)==0 else 0 for a in Aunique]
    return Bcounts


base_colours = ['r','b','g','k','m','c','k','y']
markers = ['.','v','s','d','P','*','d','X']
degrees =  ["zerolet",
            "singlet",
            "doublet",
            "triplet",
            "quadruplet",
            "quintuplet",
            "sextuplet",
            "septuplet",
            "octuplet",
            "nonuplet",
            "decuplet",
            "undecuplet",
            "duodecuplet",
            "tredecuplet",
            "quattuordecuplet",
            "quindecuplet",
            "sexdecuplet",
            "septendecuplet",
            "octodecuplet",
            "novemdecuplet",
            "vigintuplet"]


def load_file(f):
    try:
        extension = f.split(".")[-1]
        if extension=="pickle":
            with open(f,"rb") as f:
                p = pickle.load(f)
                if (len(p)==2) and isinstance(p[1],int):
                    return p[0]
                return p
        else:
            return parse_VCF_to_genome_strings(f)[0]
    except Exception as e:
        print(f"Failed to load file {f}")
        raise e

@click.command()
@click.argument('input_vcf_files', nargs=-1, type=click.types.Path())
@click.option('--trials', '-t', type=click.types.INT, default=10000)
@click.option('--degree', '-d', type=click.types.INT, default=4)
@click.option('--output_image_file', default="Rare_SNP_analysis_output.png")
def Rare_SNP_analyse(input_vcf_files,trials,degree,output_image_file):
    input_vcf_files1, input_vcf_files2, dataset_files1, dataset_files2 = input_vcf_files[0::4], input_vcf_files[1::4], input_vcf_files[2::4], input_vcf_files[3::4]
    assert False not in [len(input_vcf_files1)==len(l) for l in [input_vcf_files2, dataset_files1, dataset_files2]]
    labels = {}
    for filename in dataset_files1:
        labels[filename] = filename.split("/")[-1].split("_")[0]
    label_values = sorted(list(set(labels.values())))
    label_colours = {}
    label_markers = {}
    for k in labels.keys():
        label_colours[k] = base_colours[label_values.index(labels[k])]
        label_markers[k] = markers[label_values.index(labels[k])]
    reverse_labels = defaultdict(list)
    for k,v in labels.items():
        reverse_labels[v].append(dataset_files1.index(k))
    plt.figure()
    for k in sorted(reverse_labels.keys()):
        xs = []
        ys = []
        for i in reverse_labels[k]:
            print(dataset_files1[i])
            d1 = load_file(dataset_files1[i])
            d2 = load_file(dataset_files2[i])
            d1 = list(map(tuple, zip(*d1)))
            d2 = list(map(tuple, zip(*d2)))

            transpose_ref_genome1 = load_file(input_vcf_files1[i])
            transpose_ref_genome2 = load_file(input_vcf_files1[i])
            transpose_ref_genome1 = list(map(tuple, zip(*ref_genome1)))
            transpose_ref_genome2 = list(map(tuple, zip(*ref_genome2)))
            
            in_data_response = []
            in_data_response += export_xcorr(d1, transpose_ref_genome1, degree, trials=trials, selector=unique_A_check_unique_B)
            in_data_response += export_xcorr(d2, transpose_ref_genome2, degree, trials=trials, selector=unique_A_check_unique_B)
            out_data_response = []
            out_data_response += export_xcorr(d1, transpose_ref_genome2, degree, trials=trials, selector=unique_A_check_unique_B)
            out_data_response += export_xcorr(d2, transpose_ref_genome1, degree, trials=trials, selector=unique_A_check_unique_B)

            in_data_response = sum(in_data_response,[])
            in_data_response = sum(in_data_response)/len(in_data_response)
            out_data_response = sum(out_data_response,[])
            out_data_response = sum(out_data_response)/len(out_data_response)

            print(in_data_response,out_data_response,in_data_response-out_data_response)
            xs.append(in_data_response)
            ys.append(in_data_response-out_data_response)
        plt.scatter(xs, ys, s=14, c=[label_colours[dataset_files[i]]], label=labels[dataset_files[i]], alpha=0.8, marker=label_markers[dataset_files[i]])
    lgnd = plt.legend(loc="upper left", scatterpoints=1, fontsize=10)
    #if 'legendHandles' in dir(lgnd):
    #    for i in range(len(compare_vcf_file)):
    #        lgnd.legendHandles[i]._sizes = [30]
    #else:
    #    for i in range(len(compare_vcf_file)):
    #        lgnd.legend_handles[i]._sizes = [30]
    plt.yscale("log")
    plt.xscale("log")
    plt.xlabel("Expectation of private {} occuring in input if unique in output".format(degrees[degree]))
    plt.ylabel("Expectation of fictitious {} occuring in input if unique in output".format(degrees[degree]))
    plt.savefig(output_image_file, bbox_inches='tight')

if __name__ == '__main__':
    Rare_SNP_analyse()
