from itertools import combinations
from math import comb
from random import choice, random


# given a target genome, generated from genomes, composed of letters
# at a given depth d, compute the number of violations of indistinguishability
def compare_violation(target, genomes, values, depth, silent):
    convert_to_binary = lambda A: sum([2**i for i,aa in enumerate(A) if aa])
    # sanity check that the genomes make sense
    for i in range(len(genomes)):
        for v in genomes[i]:
            assert v in values, "genomes need to be composed of {}".format(values)
        for j in range(len(genomes)):
            assert len(genomes[i])==len(genomes[j]), "genomes need to be the same length"
    for v in target:
        assert v in values, "genomes need to be composed of {}".format(values)
    assert len(target)==len(genomes[0]), "genomes need to be the same length"
    transposed_genomes = list(map(tuple, zip(*genomes)))

    # for each value, load the query of its presence/absence in each genome column
    queries = set() # binary queries across neucleotides
    #queries = list()
    for i,t in enumerate(transposed_genomes):
        presence_list = [tuple([target[i]==value] + [tt==value for tt in t]) for value in values]
        absence_list  = [tuple([target[i]!=value] + [tt!=value for tt in t]) for value in values]

        queries.update(presence_list)
        queries.update(absence_list)
        #queries += presence_list
        #queries += absence_list
    queries = sorted(list(queries))

    
    # if two queries would isolate the synthetic sample, then eliminate
    mask = convert_to_binary([True for i in range(len(queries[0]))]) ^ 1
    binary_queries = [convert_to_binary(q) for q in queries]
    hits = 0
    for combination in combinations(list(range(len(binary_queries))), depth):
        k = 0
        for c in combination:
            k |= binary_queries[c]
        if k==mask:
            hits += 1
    combs = comb(len(binary_queries),depth)
    #print(f"{hits}/{combs}\t = {hits/combs}")
    return hits


def dumb_generate(values, number, length, perturb):
    genomes = ["".join([choice(values) for j in range(length)])]
    for i in range(number-1):
        genomes.append("".join( [gg if random()<perturb else choice(values) for gg in genomes[0]] ))
    return genomes

from genomator import *
from random import seed

dataset_size = 9
genome_lengths = 10
genome_perturb = 0.4

silent = True

values = ['A','T','G','C']

breaking = False
for dataset_size in [19,39,79,110]:
    if breaking:
        break
    for genome_lengths in [10,100,1000,10000]:
        if breaking:
            break
        for genome_perturb in [0.1,0.4]:
            if breaking:
                break
            for i in range(100):
                seed(i)
                genomes = dumb_generate(values,dataset_size,genome_lengths,genome_perturb)
                #genomes = dumb_generate(values,9,10,0.4)
                #compare_violation(genomes[-1], genomes[:-1], values, 2)

                G = generate_genomes(genomes[:], 10, values, 1, 1, 1, silent=silent, no_smart_clustering=True)
                if not silent:
                    for gg in G:
                        print(gg)
                    print("-----")
                    for gg in genomes:
                        print(gg)
                    print("-----")
                print(G)
                if len(G)==1:
                    if compare_violation(G[0], genomes[:], values, 2, silent=silent)!=0:
                        print("ERROR")
                        print(i)
                        breaking = True
                        break
