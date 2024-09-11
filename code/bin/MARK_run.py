#!/usr/bin/env python3
#generating code adapted from:
#https://gitlab.inria.fr/ml_genetics/public/artificial_genomes
import numpy as np
import pandas as pd
import sys
from tqdm import tqdm
from random import choice
import pickle

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import click
from experiment_tools import parse_VCF_to_genome_strings, parse_genome_strings_to_VCF

def main_MARK(inpt,markov_num,window_leng):
    #markov_num  = #number of markov chain haplotypes to be generated
    #window_leng = #window length

    df1 = pd.DataFrame([list(a) for a in inpt])

    ##Takes a dataframe, calculates frequency of "0" based on the last column for the combined values in the columns except the last one.
    ##Based on this frequency, "0" or "1" would be picked by probability at a given position.
    def mark_calc0(df_sub,combs):
        if len(df_sub.columns) == 2:
            temp = df_sub.iloc[:,0].astype(str)
        else:
            temp = df_sub.iloc[:,0].astype(str).str.cat(df_sub.iloc[:,1:-1].astype(str))
        df_sub["comb"] = temp

        ret_dict = {}
        df_sub = df_sub[df_sub.comb.isin(combs)]
        for A in df_sub.groupby("comb"):
            if A[0] not in combs:
                continue
            Z = A[1]
            Z = Z[df_sub.columns[-2]].value_counts().to_dict()
            sumZ = sum(Z.values())
            for k in Z.keys():
                Z[k] *= 1.0/sumZ
            ret_dict[A[0]] = Z
        return ret_dict

    ##Cut a dataframe based on window size
    def cutter(df, window_size, i):
        sub_df = df[:,i-window_size:i+1]
        sub_df = pd.DataFrame(sub_df)
        return sub_df

    ##Function for creating a single markov chain given the dataframe and window length
    def markover(df, window_len, markov_num):
        markov = [list() for i in range(markov_num)]
        window_len_temp = window_len
        df = df.values
        for i1 in tqdm(range(len(df[0,:]))):
            ##Put 1 or 0 based solely on frequency for the 1st index
            if i1 == 0:
                first_elements = list(df[:,i1])
                for i in range(markov_num):
                    markov[i].append(choice(first_elements))
                continue
            ##Window length increases from 1 till constant user provided "window_len"
            if i1 <= window_len_temp:
                window_len = i1
            else:
                window_len = window_len_temp
            sub_df = cutter(df, window_len, i1)
            combs = [''.join(str(e) for e in markov[i][(i1-window_len):i1]) for i in range(markov_num)]
            prob0_dict = mark_calc0(sub_df,combs) #frequency of "0" at the position is calculated for the given window
            for i,comb in enumerate(combs):
                choice_data = prob0_dict[comb]
                choice_data_keys = list(choice_data.keys())
                markov[i].append(np.random.choice(choice_data_keys,p=[choice_data[k] for k in choice_data_keys]))
        return markov

    ##Create a data frame of "markov_num" number of markov chain haplotypes
    markovs = markover(df1, window_leng,markov_num)
    return [bytes(m) for m in markovs]






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
