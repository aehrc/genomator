#!/usr/bin/env python3
from experiment_tools import parse_VCF_to_genome_strings
import click
import pickle

@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_pickle_file', type=click.types.Path())
def pickle_to_vcf(input_vcf_file,output_pickle_file):
    ss = parse_VCF_to_genome_strings(input_vcf_file)
    with open(output_pickle_file, "wb") as f:
        pickle.dump(ss,f)

if __name__ == '__main__':
    pickle_to_vcf()
