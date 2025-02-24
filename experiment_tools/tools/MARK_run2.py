#!/usr/bin/env python3
from collections import defaultdict
from tqdm import tqdm
from random import choices
import pickle
import click
from experiment_tools import parse_VCF_to_genome_strings, parse_genome_strings_to_VCF

def main_MARK(df,markov_num,total_window_len):
    #markov_num  = #number of markov chain haplotypes to be generated
    #window_leng = #window length

    markov = [b'' for i in range(markov_num)]
    for i1 in tqdm(range(len(df[0]))):
        ##Window length increases from 1 till constant user provided "window_len"
        if i1 <= total_window_len:
            window_len = i1
        else:
            window_len = total_window_len

        df_sub = [d[i1-window_len:i1] for d in df] ##Cut a dataframe based on window size
        df_sub_next = [bytes([d[i1]]) for d in df] ## next elements

        witnessed_endings = defaultdict(lambda : defaultdict(int))
        for ii,m in enumerate(markov):
            continuing = False
            for k in witnessed_endings.keys():
                if m.endswith(k):
                    continuing=True
                    witnessed_k = witnessed_endings[k][0]
                    witnessed_v = witnessed_endings[k][1]
                    markov[ii] += choices(population=witnessed_k,weights=witnessed_v)[0]
                    break
            if continuing:
                continue

            found = None
            found_i = None
            for i,d in enumerate(df_sub):
                if m.endswith(d):
                    witnessed_endings[d][df_sub_next[i]]+=1
                    found = d
                    found_i = i
                    break
            for i in range(found_i+1,len(df_sub)):
                if found==df_sub[i]:
                    witnessed_endings[found][df_sub_next[i]]+=1
            witnessed_k = list(witnessed_endings[found].keys())
            witnessed_v_sum = sum(witnessed_endings[found].values())
            witnessed_v = [witnessed_endings[found][k]*1.0/witnessed_v_sum for k in witnessed_k]
            witnessed_endings[found] = (witnessed_k,witnessed_v)
            markov[ii] += choices(population=witnessed_k,weights=witnessed_v)[0]
    return markov


@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.argument('number_of_genomes', type=click.INT, default=1)
@click.option('--window_leng', type=click.INT, default=10)
def MARK_run(input_vcf_file, output_vcf_file, number_of_genomes,window_leng):
    if input_vcf_file.split(".")[-1]=="pickle":
        with open(input_vcf_file,"rb") as f:
            s,ploidy = pickle.load(f)
    else:
        s,ploidy = parse_VCF_to_genome_strings(input_vcf_file)
    ss = main_MARK(s, number_of_genomes,window_leng)
    if output_vcf_file.split(".")[-1]=="pickle" or input_vcf_file.split(".")[-1]=="pickle":
        with open(output_vcf_file, "wb") as f:
            pickle.dump(ss,f)
    else:
        parse_genome_strings_to_VCF(ss,input_vcf_file,output_vcf_file,ploidy)

if __name__ == '__main__':
    MARK_run()

