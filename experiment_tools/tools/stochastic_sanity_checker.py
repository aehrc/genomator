#!/usr/bin/env python3
from experiment_tools import *
import click
from random import randint,choice
import numpy as np
from tqdm import tqdm

# for two vcf files, one the source of the synthetic genomes of the other
# check that these files satisfy minimum indistinguishabiliyt check across number of trials
# and also check that satisfies diversity check if specified
# sanity check that Genomator is performing correctly
@click.command()
@click.argument('source_vcf_file', type=click.types.Path())
@click.argument('synthetic_vcf_file', type=click.types.Path())
@click.option('--diversity', type=click.INT, default=0)
@click.option('--trials', type=click.INT, default=500000)
@click.option('--snp_load_limit', type=click.INT, default=10000)
def checker(source_vcf_file,synthetic_vcf_file,diversity,trials,snp_load_limit):
    print("SANITY CHECKER")
    source = parse_VCF_to_genome_strings(source_vcf_file,snp_load_limit)[0]
    synthetic = parse_VCF_to_genome_strings(synthetic_vcf_file,snp_load_limit)[0]
    if diversity>0:
        print("checking diversity")
        print("formatting")
        source_np = [bytearray(s) for s in tqdm(source)]
        source_np = [np.array(r,dtype=np.int8) for r in tqdm(source_np)]
        synthetic_np= [bytearray(s) for s in tqdm(synthetic)]
        synthetic_np = [np.array(r,dtype=np.int8) for r in tqdm(synthetic_np)]
        print("n-way distance calculating")
        for s in tqdm(synthetic_np):
            for v in source_np:
                assert np.linalg.norm(s-v)**2 >= diversity, "diversity check FAIL"

    l = len(source[0])
    print("checking indistinguishability --- (NOTE: this is stochastic checking, may pass checks when it should not)")
    for t in tqdm(range(trials)):
        i = randint(0,l-1)
        j = randint(0,l-1)
        A = [s[i] for s in source]
        B = [s[j] for s in source]
        selectA = choice(list(set(A)))
        selectB = choice(list(set(B)))
        invA = choice([True,False])
        invB = choice([True,False])
        if False not in [((A[k]==selectA)^invA) or ((B[k]==selectB)^invB) for k in range(len(source))]:
            assert False not in [((synthetic[k][i]==selectA)^invA) or ((synthetic[k][j]==selectB)^invB) for k in range(len(synthetic))], "indistinguishability check FAIL"
    print("checks succeeded")
            

if __name__ == '__main__':
    checker()

