#!/usr/bin/env python3
import click
from experiment_tools import *
from random import shuffle
from copy import deepcopy as copy
import json


@click.command()
@click.argument('input_vcf_file1', type=click.types.Path())
@click.argument('output_vcf_file1', type=click.types.Path())
@click.argument('output_vcf_file2', type=click.types.Path())
@click.option('--index_output_file', type=click.types.Path(), default=None)
def splitter(input_vcf_file1, output_vcf_file1, output_vcf_file2, index_output_file):
    vcf_in, ploidy = parse_VCF_to_genome_strings(input_vcf_file1)
    if index_output_file is not None:
        backup_vcf_in = copy(vcf_in)
    shuffle(vcf_in)
    half_size = len(vcf_in)//2
    results1 = vcf_in[:half_size]
    results2 = vcf_in[half_size:]
    
    parse_genome_strings_to_VCF(results1, input_vcf_file1, output_vcf_file1, ploidy)
    parse_genome_strings_to_VCF(results2, input_vcf_file1, output_vcf_file2, ploidy)
    if index_output_file is not None:
        with open(index_output_file,'w') as f:
            f.write("VCF SPLIT INDEX FILE\n")
            f.write(json.dumps([backup_vcf_in.index(v) for v in results1]))
            f.write("\n")
            f.write(json.dumps([backup_vcf_in.index(v) for v in results2]))




if __name__ == '__main__':
    splitter()
