import vcfpy
import os
from tqdm import tqdm
from copy import deepcopy as copy
import cyvcf2
from itertools import islice

def parse_HAPT_to_genome_strings(input_vcf_file):
    print("loading HAPT file")
    with open(input_vcf_file) as f:
        data = f.readlines()
    data = [d.strip().split(" ")[2:] for d in data]
    data = [[int(dd) for dd in d] for d in data]
    interleaved_data = []
    for i in range(0,len(data),2):
        ddata = [None]*(len(data[i])+len(data[i+1]))
        ddata[::2] = data[i]
        ddata[1::2] = data[i+1]
        interleaved_data.append(ddata)
    return [b"".join([dd.to_bytes(1,"big") for dd in d]) for d in interleaved_data]

def parse_genome_strings_to_HAPT(s, output_vcf_file):
    print("parsing generated genome into HAPT output")
    data = []
    for i,ss in enumerate(s):
        sss = [str(z) for z in list(ss)]
        data.append(["AG", f"GEN{i}_A"] + sss[ ::2])
        data.append(["AG", f"GEN{i}_B"] + sss[1::2])
    data = "\n".join([" ".join(d) for d in data])
    with open(output_vcf_file,"w") as f:
        f.write(data)

def parse_VCF_to_genome_strings(input_vcf_file):
    print("loading VCF file")
    genomes = []
    reader = cyvcf2.VCF(input_vcf_file)
    pbar = tqdm()
    while record_chunk := [a.genotypes for a in islice(reader,1000)]:
        ploidy = len(record_chunk[0][0])-1
        record_chunk = list(map(list,zip(*record_chunk)))
        genomes.append([bytes([gg[i] for gg in g for i in range(ploidy)]) for g in record_chunk])
        pbar.update(1000)
    pbar.close()
    reader.close()
    genomes = [b"".join(a) for a in zip(*genomes)]
    return genomes, ploidy


def parse_genome_strings_to_VCF(s, input_vcf_file, output_vcf_file, ploidy, del_info_field = False):
    # the genomator has returned a satisfactory set of genotype indices, now we need to reload thoes
    # back into VCF structure for export, we do this by scanning through the 
    # generated ATGC string and detecting the corresponding VCF REF/ALT.
    print("parsing generated genome into VCF output")
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
