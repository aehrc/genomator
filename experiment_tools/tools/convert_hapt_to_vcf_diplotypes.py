#!/usr/bin/env python3
from experiment_tools import parse_genome_strings_to_VCF
import click


header = '''##fileformat=VCFv4.2
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=AD,Number=R,Type=Integer,Description="Allelic depths for the ref and alt alleles in the order listed">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
##FORMAT=<ID=PL,Number=G,Type=Integer,Description="Normalized, Phred-scaled likelihoods for genotypes as defined in the VCF specification">
##FILTER=<ID=PASS,Description="">
'''
subheader = "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	"


@click.command()
@click.argument('input_hapt_file', type=click.types.Path())
@click.argument('input_legend_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
def convert(input_hapt_file, input_legend_file, output_vcf_file):

    print("loading HAPT file")
    with open(input_hapt_file) as f:
        data = f.readlines()
    data_ids = [d.strip().split(" ")[1] for d in data]
    data_ids = data_ids[::2]
    data_ids = [d.split("_")[0] for d in data_ids]
    data = [d.strip().split(" ")[2:] for d in data]
    data = [[int(dd) for dd in d] for d in data]
    data = list(zip(*[data[::2], data[1::2]]))
    data = [["{}|{}".format(a[i],b[i]) for i in range(len(a))] for a,b in data]
    data = list(map(list,zip(*data))) # transpose

    print("loading LEGEND file")
    with open(input_legend_file) as f:
        legend = [d.strip().split(" ") for d in f.readlines()[1:]]

    assert len(legend) == len(data)
    with open(output_vcf_file,"w") as f:
        f.write(header)
        f.write(subheader)
        f.write("\t".join(data_ids))
        f.write("\n")
        for i in range(len(data)):
            f.write("{}\t{}\trs{}\t{}\t{}\t100.00\tPASS\t.\tGT\t".format(
                legend[i][0].split(":")[0],
                legend[i][1],
                legend[i][0].split(":")[1],
                legend[i][2],
                legend[i][3]))
            f.write("\t".join([str(a) for a in data[i]]))
            f.write("\n")

if __name__ == '__main__':
    convert()

