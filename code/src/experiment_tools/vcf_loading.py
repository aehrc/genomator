import sys
import vcfpy
import os
from tqdm import tqdm
from copy import deepcopy as copy
import cyvcf2
from itertools import islice

def parse_VCF_to_genome_strings(input_vcf_file,snp_load_limit=None):
    print("loading VCF file", file=sys.stderr)
    genomes = []
    reader = cyvcf2.VCF(input_vcf_file)
    pbar = tqdm()
    count = 0
    while record_chunk := [a.genotypes for a in islice(reader,1000)]:
        ploidy = len(record_chunk[0][0])-1
        record_chunk = list(map(list,zip(*record_chunk)))
        genomes.append([bytes([gg[i] for gg in g for i in range(ploidy)]) for g in record_chunk])
        pbar.update(1000)
        count += 1000
        if (snp_load_limit is not None) and (count>snp_load_limit):
            break
    pbar.close()
    reader.close()
    genomes = [b"".join(a) for a in zip(*genomes)]
    return genomes, ploidy


def parse_genome_strings_to_VCF(s, input_vcf_file, output_vcf_file, ploidy, del_info_field = False):
    print("parsing generated genome into VCF output", file=sys.stderr)
    number_of_genomes = len(s)
    reader = vcfpy.Reader.from_path(input_vcf_file)
    output_header = copy(reader.header)
    output_header.samples = vcfpy.SamplesInfos(["GENERATEDSAMPLE{}".format(i) for i in range(number_of_genomes)])
    writer = vcfpy.Writer.from_path(output_vcf_file, output_header)
    recordset = None
    for i,record in enumerate(tqdm(reader)):
        if recordset is None:
            recordset = [copy(record.calls[0]) for genome_number in range(number_of_genomes)]
        record.calls = recordset
        if del_info_field:
            record.INFO.clear()
        for genome_number in range(number_of_genomes):
            record.calls[genome_number].sample = "GENERATEDSAMPLE{}".format(genome_number)
            genome_fragment = [s[genome_number][i*ploidy+k] for k in range(ploidy)] 
            #s[genome_number] = s[genome_number][ploidy:]
            record.calls[genome_number].set_genotype(record.calls[genome_number].gt_phase_char.join([str(ff) for ff in genome_fragment]))
        record.update_calls(record.calls)
        writer.write_record(record)