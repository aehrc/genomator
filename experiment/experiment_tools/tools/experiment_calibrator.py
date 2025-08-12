#!/usr/bin/env python3
from experiment_tools import *
from random import shuffle,randint,random
import numpy as np
import pickle
import multiprocessing as mp
from sys import argv
from genomator import *

print("GENOMATOR_CALIBRATOR")
if len(argv)!=6:
    print("please call: experiment_calibrator.py <INPUT_VCF_FILE> <START_N> <FINISH_N> <L> <FINISH_Z>")
    print("")
    print("  where <INPUT_VCF_FILE> is the path to a genome dataset file for input")
    print("  where <START_N> is the value of N to start with (default 50)")
    print("  where <FINISH_N> is the value of N to finish with (default 250)")
    print("  where <L> is the value of L throughout the experiments (default 0.99)")
    print("  where <FINISH_Z> is the value of Z to finish with (default -2.5)")
    print("")
    print("The script runs genoamtor with the set L, starting from Z=0 and N=START_N")
    print("and in 10 equal increments runs genomator upto Z=FINISH_Z and N=FINISH_N")
    print("for each evaluating where genomator's output is about as far apart from the input dataset")
    print("as the input dataset is from itself")
    print("thereafter giving the command to generate with genomator using the resolved best parameters")
    print("")

assert len(argv)>=2

input_vcf_file1 = argv[1]
start_N = int(argv[2]) if len(argv)>2 else 50
finish_N = int(argv[3]) if len(argv)>3 else 250
L = float(argv[4]) if len(argv)>4 else 0.99
finish_Z = -float(argv[5]) if len(argv)>5 else -2.5

silent=True
def load_file(f,postpend=True):
    extension = f.split(".")[-1]
    if extension=="pickle":
        with open(f,"rb") as f:
            p = pickle.load(f)
            if (len(p)==2) and isinstance(p[1],int):
                return p[0]
            return p
    else:
        return parse_VCF_to_genome_strings(f)[0]
input_vcf_file1 = load_file(input_vcf_file1)
shuffle(input_vcf_file1)
input_vcf_file1, input_vcf_file2 = input_vcf_file1[:len(input_vcf_file1)//2], input_vcf_file1[len(input_vcf_file1)//2:]


def get_min_dist(args):
    x,dataset = args
    min_dist = float("inf")
    for d in dataset:
        dist = np.linalg.norm(x-d,ord=0)
        if dist < min_dist:
            min_dist = dist
    return min_dist*1.0/len(x)


if __name__ == '__main__':

    results_data_to_data = []
    input_vcf_file2_arrays = [np.array([hh for hh in h]) for h in input_vcf_file2]
    for g in input_vcf_file1:
        results_data_to_data.append(get_min_dist((np.array([gg for gg in g]), input_vcf_file2_arrays )))
    print("dist of data from itself")
    print(np.mean(results_data_to_data),np.median(results_data_to_data))

    target = np.median(results_data_to_data)

    breaking = False
    while not breaking:
        results = []
        for i in range(10):
            p = i*1.0/10
            Z = finish_Z*p
            N = int(start_N + (finish_N-start_N)*p)

            print(f"computation {p*100}% complete, trying N={N},Z={Z},L={L}")
            genomes = generate_genomes(
                input_vcf_file1, N, None, len(input_vcf_file1), 0, 0,
                exception_space=Z,
                looseness=L,
                solver_name="minicard", indexation_bits=10,
                difference_samples=10000,
                biasing=False,
                no_smart_clustering=False,
                cluster_information_file=None,
                max_restarts=10,
                dump_all_generated=True,
                silent=silent
            )
            if len(genomes) != len(input_vcf_file1):
                print("impossible parameters, restarting with higher N")
                break
            genomes = [np.array([gg for gg in g]) for g in genomes]
            results1 = list(map(get_min_dist, [(np.array([gg for gg in g]),genomes) for g in input_vcf_file1]))
            results2 = list(map(get_min_dist, [(np.array([gg for gg in g]),genomes) for g in input_vcf_file2]))

            #print(np.mean(results1),np.median(results1), abs(np.median(results1)-target))
            #print(np.mean(results2),np.median(results2), abs(np.median(results1)-target))
            results.append((abs(np.median(results1)-target),np.median(results1)-target, N,Z,L))
        else:
            breaking = True
        start_N += 10
        finish_N += 10

    print("ABS_OFF_TARGET,OFF_TARGET,N,Z,L")
    for r in results:
        print(','.join([str(rr) for rr in r]))
    results = sorted(results, key=lambda x:x[0])
    results = results[0]
    print(f"BEST RESULT is: N={N}, Z={Z}, L={L}")
    print(f"genomator <INPUT_VCF_FILE> <OUTPUT_VCF_FILE> <NUMBER_OF_GENOMES_TO_GENERATE> 0 0 --exception_space={Z} --sample_group_size={N} --looseness={L}")

