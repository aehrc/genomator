from genomator import *
from random import sample, seed
from itertools import combinations
from collections import defaultdict
from tqdm import tqdm

sample_group_size = 15 #25
biasing = False #True

def wrap_main_GENOMATOR(genomes,number_of_genomes):
    return generate_genomes(
            genomes, 
            sample_group_size, 
            None, 
            number_of_genomes, 
            diversity_requirement=1, 
            generated_diversity_requirement=1, 
            indexation_bits=10, 
            silent=True, 
            biasing=biasing,
            no_smart_clustering=True)


def lits_satisfy_clauses(clauses,lits):
    for c in clauses: #for each clause
        for cc in c:
            if cc in lits: #if the the clause is satisfied by some literal break out
                break
        else: #if no break point hit, then clause unsatisfied, return False
            return False
    return True

wrap_values = lambda x,N: (x+N)%(2*N+1)-N
def check_genomator_satisfy(genomes, fake_genome): 
    transposed_genomes = list(map(tuple, zip(*genomes)))
    unique_transposed_genomes = sorted(list(set(transposed_genomes)))

    # for each value, load the query of its presence/absence in each genome column
    queries = set() # binary queries across neucleotides
    clauses = set() # holding clauses prior to indexing.
    reverse_query_mapping = defaultdict(dict)
    for t in unique_transposed_genomes:
        values = sorted(list(set(t)))# + [255]
        presence_list = [tuple([tt==value for tt in t]) for value in values]
        absence_list  = [tuple([tt!=value for tt in t]) for value in values]
        queries.update(presence_list)
        queries.update(absence_list)
        for i,q in enumerate(absence_list):
            reverse_query_mapping[t][q] = values[i]#.to_bytes(1,"big")
        clauses.add(frozenset(absence_list)) # one of the values must result
    queries = sorted(list(queries))
    variables = len(queries)//2
    transposed_queries = list(map(tuple, zip(*queries)))
    index = {v:wrap_values(i+1,variables) for i,v in enumerate(queries)}
    for t in reverse_query_mapping.keys():
        reverse_query_mapping[t] = {b:index[a] for a,b in reverse_query_mapping[t].items()}

    clauses = [[index[cc] for cc in c] for c in clauses]

    # if two queries would isolate the synthetic sample, then eliminate
    mask = convert_to_binary([True for i in range(len(queries[0]))])
    binary_queries = [convert_to_binary(q) for q in queries]   

    query_index_to_variable = [wrap_values(i+1,variables) for i in range(len(queries))]
    for i,k1 in enumerate(binary_queries):
        for j in range(i,len(binary_queries)):
            if k1|binary_queries[j] == mask:
                #if query_index_to_variable[i]!=-query_index_to_variable[j]:
                clauses.append([ -query_index_to_variable[i],-query_index_to_variable[j] ])

    lits = set()  # map the fake_genome to lits relevent to CNF clauses
    for i,z in enumerate(transposed_genomes):
        rqm = reverse_query_mapping[z]
        if fake_genome[i] in rqm:
            lit = rqm[fake_genome[i]]
            if -lit not in lits:
                lits.add(rqm[fake_genome[i]])
            else:
                return False #fake_genome responds both ways to a query
        else:
            return False #fake_genome has SNP not in the dataset at specific position
    for c in clauses: #for each clause
        for cc in c:
            if cc in lits: #if the the clause is satisfied by some literal break out
                break
        else: #if no break point hit, then clause unsatisfied, return False
            return False
    return True
    return lits_satisfy_clauses(clauses,lits)
    


def check_genomator_satisfy_2(genomes, fake_genome): 
    genomes = [fake_genome]+genomes
    transposed_genomes = list(map(tuple, zip(*genomes)))
    unique_transposed_genomes = sorted(list(set(transposed_genomes)))

    for i,t1 in enumerate(unique_transposed_genomes):
        values1 = sorted(list(set(t1)))# + [255]
        signatures1 = ([tuple([tt==value for tt in t1]) for value in values1]
                    + [tuple([tt!=value for tt in t1]) for value in values1])
        for j in range(i,len(unique_transposed_genomes)):
            t2 = unique_transposed_genomes[j]
            values2 = sorted(list(set(t2)))# + [255]
            signatures2 = ([tuple([tt==value for tt in t2]) for value in values2]
                        + [tuple([tt!=value for tt in t2]) for value in values2])
            for index1,s1 in enumerate(signatures1):
                for index2,s2 in enumerate(signatures2):
                    if s1[0]==False and s2[0]==False:
                        if 0 not in [sum(a) for a in zip(s1,s2)][1:]:
                            return False
    return True





#ref_genomes_file = input("VCF file input:") #"./privacy_working_dir/pee1mark.vcf"
ref_genomes_file = "/home/bur471/Desktop/vcfs/pee1mark.vcf"
ref_genomes,ploidy = parse_VCF_to_genome_strings(ref_genomes_file)

genome_set_size = 18
genome_set_length = 950

#seed(0)
trials = 30
for trial in range(trials):
    print("BEGINNING TRIAL {}".format(trial))

    # sample a random number of genomes with a random set of SNPs
    genomes = sample(ref_genomes,genome_set_size)
    indices = sample(list(range(len(genomes[0]))), genome_set_length)
    genomes = [bytes([r[i] for i in indices]) for r in genomes]
    
    # use Genomator to make a fake genome
    fake_genome = wrap_main_GENOMATOR(genomes,1)
    if len(fake_genome)==0:
        print("WARNING: genomator couldnt make a genome, continuing")
        continue
    # simple check that the fake genome is plausible according to our evalutaion
    assert check_genomator_satisfy(genomes,fake_genome[0]), "fake genome does not satisfy set"

    # generate all SAT solutions
    clauses,max_variable = generate_genomator_indices(fake_genome + genomes,sample_group_size,equal_constraint=True)
    solutions1 = sat_count(clauses,len(genomes),max_variable)
    solutions1 = set(frozenset(s) for s in solutions1)
    clauses,max_variable = generate_genomator_indices(fake_genome + genomes,sample_group_size,False,False)
    solutions = sat_count_minicard(clauses,len(genomes),max_variable,sample_group_size)
    solutions = set(frozenset(s) for s in solutions)
    print("SOLUTION SIZE:\t{}".format(len(solutions)))
    print("SOLUTION SIZE:\t{}".format(len(solutions1)))

    # generate all SAT NON-solutions
    non_solutions = combinations(list(range(1,len(genomes))),sample_group_size)
    non_solutions = set(frozenset(s) for s in non_solutions)
    non_solutions = non_solutions.difference(solutions)
    print("NONSOLUTION SIZE:\t{}".format(len(non_solutions)))

    # verify that all the solutions satisfy genomators producing witnessed fake_genome
    for s in tqdm(solutions):
        solution_genomes = [genomes[i-1] for i in s]
        assert check_genomator_satisfy(solution_genomes,fake_genome[0]), "positive solution FAIL"

    # verify that all the NON-solutions do not satisfy genomators producing witnessed fake_genome
    non_solutions = list(non_solutions)
    for s in tqdm(non_solutions):
        solution_genomes = [genomes[i-1] for i in s]
        assert not check_genomator_satisfy(solution_genomes,fake_genome[0]), "negative solution FAIL"

