#!/usr/bin/env python3
from random import choice, randint, shuffle
from tqdm import tqdm
import json
import click
from itertools import product
from collections import defaultdict
from genomator import parse_VCF_to_genome_strings





# takes an input VCF and a single VCF output from genomator
# then loads the information about the cluster genomator used to generate the output
# and a count file output from reverse genomator
# and and calculates (for thoes 'privacy revealed' individuals over a 50-60% threshold of counting)
# how many of their private SNP combinations are revealed.
@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.argument('cluster_file', type=click.types.Path())
@click.argument('count_file', type=click.types.Path())
@click.argument('output_file', type=click.types.Path())
@click.option('--trials', '-t', type=click.types.INT, default=10000)
@click.option('--combination_degree', '-d', type=click.types.INT, default=4)
def Rare_SNP_analyse(input_vcf_file,output_vcf_file,cluster_file,count_file,output_file,trials,combination_degree):
    with open(cluster_file,"r") as f:
        cluster_info = json.loads(f.readlines()[1].strip())
    with open(count_file,"r") as f:
        counts = json.loads(f.readlines()[0].strip())

    in_datapoints = []
    out_datapoints = []
    for i,c in enumerate(counts[1]):
        if i in cluster_info:
            in_datapoints.append((c,0))
        else:
            out_datapoints.append((c,0))
    
    with open(output_file,"a") as f:
        f.write(json.dumps([in_datapoints,out_datapoints,counts[0]]))
        f.write("\n")
    print("done")


if __name__ == '__main__':
    Rare_SNP_analyse()

