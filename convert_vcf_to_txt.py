
import click
import json
import os
from tqdm import tqdm
from copy import deepcopy as copy
import cyvcf2
from itertools import islice



def parse_VCF_to_genome_strings(input_vcf_file):
    print("loading VCF file")
    genomes = []
    reader = cyvcf2.VCF(input_vcf_file)
    samples = reader.samples
    variant_names = []
    pbar = tqdm()
    while record_chunk := list(islice(reader,1000)):
        variant_names += [r.ID for r in record_chunk]
        record_chunk = [a.genotypes for a in record_chunk]
        ploidy = len(record_chunk[0][0])-1
        record_chunk = list(map(list,zip(*record_chunk)))
        genomes.append([  bytes([ sum([gg[i] for i in range(ploidy)]) for gg in g])  for g in record_chunk])
        pbar.update(1000)
    pbar.close()
    reader.close()
    genomes = [b"".join(a) for a in zip(*genomes)]
    return genomes, ploidy, samples, variant_names

@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_txt_file', type=click.types.Path())
def main_method(input_vcf_file, output_txt_file):
    genomes,ploidy,samples,variant_names = parse_VCF_to_genome_strings(input_vcf_file)
    with open(output_txt_file,'w') as f:
        f.write("id discard "+" ".join(variant_names)+"\n")
        for i in range(len(genomes)):
            f.write(samples[i]+" no "+" ".join([str(g) for g in genomes[i]])+"\n")


if __name__ == '__main__':
	main_method()


