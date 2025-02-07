#!/usr/bin/env python3
import click
from experiment_tools import *
from tqdm import tqdm
import statistics
from random import random

@click.command()
@click.argument('original_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.option('--noise_level', type=click.FLOAT, default=0.1)
@click.option('--silent', type=click.BOOL, default=False)
def noiser(original_vcf_file, output_vcf_file, noise_level, silent):
    original, ploidy = parse_VCF_to_genome_strings(original_vcf_file,silent=silent)

    new_genomes = []
    for o in original:
        genome = [random()+0.5 if random()<noise_level else g for i,g in enumerate(o)]
        new_genomes.append(b''.join([bytes([int(g)]) for g in genome]))

    parse_genome_strings_to_VCF(new_genomes, original_vcf_file, output_vcf_file, ploidy)

if __name__ == '__main__':
    noiser()
