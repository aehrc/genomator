#!/usr/bin/env python3
import click
from random import shuffle
from experiment_tools import parse_VCF_to_genome_strings
import vcfpy
from copy import deepcopy as copy
from tqdm import tqdm


def parse_genome_strings_to_VCF(s, input_vcf_file, output_vcf_file, ploidy):
    number_of_genomes = len(s)
    number_of_snps = len(s[0])//ploidy
    reader = vcfpy.Reader.from_path(input_vcf_file)
    output_header = copy(reader.header)
    output_header.samples = vcfpy.SamplesInfos(["GENERATEDSAMPLE{}".format(i) for i in range(number_of_genomes)])
    writer = vcfpy.Writer.from_path(output_vcf_file, output_header)
    recordset = None
    for i,record in enumerate(tqdm(reader)):
        if i<number_of_snps:
            if recordset is None:
                recordset = [copy(record.calls[0]) for genome_number in range(number_of_genomes)]
            record.calls = recordset
            for genome_number in range(number_of_genomes):
                record.calls[genome_number].sample = "GENERATEDSAMPLE{}".format(genome_number)
                genome_fragment = [s[genome_number][i*ploidy+k] for k in range(ploidy)] 
                #s[genome_number] = s[genome_number][ploidy:]
                record.calls[genome_number].set_genotype(record.calls[genome_number].gt_phase_char.join([str(ff) for ff in genome_fragment]))
            record.update_calls(record.calls)
            writer.write_record(record)



@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.argument('samples', type=click.INT)
@click.argument('snps', type=click.INT)
def vcf_trimmer(input_vcf_file,output_vcf_file,samples,snps):
    vcf_in, ploidy = parse_VCF_to_genome_strings(input_vcf_file)
    dataset_snps = len(vcf_in[0])
    assert dataset_snps >= snps, "ERROR: cannot trim to number of SNPs more than there are SNPs in the VCF input"
    indices = list(range(dataset_snps))
    shuffle(indices)
    indices = indices[:snps]
    vcf_in = [bytes([v[i] for i in indices]) for v in vcf_in]
    assert len(vcf_in)>= samples, "ERROR: cannot trim to samples more than there are samples in the VCF input"
    shuffle(vcf_in)
    vcf_in = vcf_in[:samples]
    parse_genome_strings_to_VCF(vcf_in, input_vcf_file, output_vcf_file, ploidy)

if __name__ == '__main__':
    vcf_trimmer()
