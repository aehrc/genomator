#!/usr/bin/env python3
from experiment_tools import *
import click
import pickle


@click.command()
@click.argument('input_pickle_file', type=click.types.Path())
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.option('--ploidy', type=click.INT, default=2)
def pickle_to_vcf(input_pickle_file,input_vcf_file,output_vcf_file,ploidy):
    with open(input_pickle_file,"rb") as f:
        s = pickle.load(f)
    parse_genome_strings_to_VCF(s, input_vcf_file, output_vcf_file, ploidy, False)

if __name__ == '__main__':
    pickle_to_vcf()
