import traceback
from random import randint, random, sample, shuffle, choice
from operator import itemgetter
from tqdm import tqdm
from collections import defaultdict
from pysat.solvers import Solver
from pysat.card import *
import numpy as np
import time
import multiprocessing as mp

class UnsatException(Exception):
    pass

print_silent = lambda s,S: print(s) if not S else None
def convert_to_binary(A):
    z = 0
    for aa in A:
        z = (z<<1) + aa
    return z

wrap_values = lambda x,N: (x+N)%(2*N+1)-N

def check_square_values(genomes,values=False):
    # sanity check that the genomes make sense
    if values:
        for i in range(len(genomes)):
            for v in genomes[i]:
                assert v in values, "genomes need to be composed of {}".format(values)
    for i in range(len(genomes)):
        for j in range(len(genomes)):
            assert len(genomes[i])==len(genomes[j]), "genomes need to be the same length"


def cluster_setup(reference_genomes, size, clustering=30, difference_samples=100, silent=False):
    length = len(reference_genomes)
    difference_samples = min(len(reference_genomes[0]),difference_samples)
    distances = [[0]*length for j in range(length)]
    indices = sample(list(range(len(reference_genomes[0]))), difference_samples)
    reference_genomes_np = [np.array(bytearray([r[i] for i in indices]),dtype=np.int8) for r in reference_genomes]
    for i in tqdm(range(len(reference_genomes_np))) if not silent else range(len(reference_genomes_np)):
        for j in range(i+1,len(reference_genomes_np)):
            distances[i][j] = np.linalg.norm(reference_genomes_np[i]-reference_genomes_np[j])**2
            distances[j][i] = distances[i][j]
    sorted_distances = [sorted(list(enumerate(d)), key=itemgetter(1)) for d in distances]
    sorted_distance_indices = [[i for i,d in dd] for dd in sorted_distances]
    partitions = length // size
    refactor_size = length // partitions 
    undershoot = length - refactor_size*partitions
    index_sets = []
    for re_run in range(clustering):
        used_set = []
        last_new_set = None
        for i in range(partitions-1):
            new_set = []
            focus = last_new_set[-1] if last_new_set is not None else choice(list(range(length)))
            ii = 0
            while len(new_set)< (refactor_size + (i<undershoot)):
                if sorted_distance_indices[focus][ii] not in used_set:
                    used_set.append(sorted_distance_indices[focus][ii])
                    new_set.append(sorted_distance_indices[focus][ii])
                ii += 1
            index_sets.append(new_set)
            last_new_set = new_set
        index_sets.append(list(set(range(length)).difference(set(used_set))))
    return index_sets 

def cluster_sample(reference_genomes,sample_group_size,index_sets):
    index_set = choice(index_sets)
    genomes = [reference_genomes[ii] for ii in index_set]
    shuffle(genomes)
    return genomes, index_set

def weighted_choice(a,p):
    pp = np.cumsum(p).tolist()
    assert abs(pp[-1]-1)<0.001
    pp[-1]=1
    def inner_():
        b = random()
        i = 0
        while (b>pp[i]):
            i += 1
        return a[i]
    return inner_

def parallel_inner( args ):
    reference_genomes, sample_group_size, basevalues, diversity_requirement, generated_diversity_requirement, no_smart_clustering, exception_space, silent, indexation_bits, biasing, solver_name, looseness, max_restarts, cluster_info, genome_number = args
    if solver_name=='tinicard':
        import pytinicard
        indexation_bits = min(indexation_bits,sample_group_size)
    if solver_name=="cmsgen":
        import pycmsgen
    bytes_mode = isinstance(reference_genomes[0],bytes)
    rootstring = b"" if bytes_mode else ""
    try:
        (1234567890).bit_count()
        bit_count_function = lambda x: x.bit_count()
    except AttributeError:
        bit_count_function = lambda x: bin(x).count("1")
    exception_space_array = list(range(int(abs(exception_space))+2))
    exception_space_probability = [min(1,abs(exception_space)+1-a) for a in exception_space_array]
    exception_space_probability = [a*1.0/sum(exception_space_probability) for a in exception_space_probability]
    exception_space_drawer = weighted_choice(exception_space_array,exception_space_probability)
    restarts = 0
    cluster_information_file = None
    solution_set = []
    while ((restarts < max_restarts) or (max_restarts<0)):
        reference_genomes, sample_group_size, basevalues, diversity_requirement, generated_diversity_requirement, no_smart_clustering, exception_space, silent, indexation_bits, biasing, solver_name, looseness, max_restarts, cluster_info, genome_number = args
        if sample_group_size>0:
            if no_smart_clustering:
                index_set = sample(list(range(len(reference_genomes))),sample_group_size)
                genomes = [reference_genomes[i] for i in index_set]
            else:
                genomes,index_set = cluster_sample(reference_genomes,sample_group_size,cluster_info)
        else:
            index_set = list(range(len(reference_genomes)))
            genomes = reference_genomes

        cluster_information_file = index_set
        transposed_genomes = list(map(tuple, zip(*genomes)))
        unique_transposed_genomes = sorted(list(set(transposed_genomes)))

        print_silent("generating query information",silent)
        # for each value, load the query of its presence/absence in each genome column
        queries = set() # binary queries across neucleotides
        clauses = set() # holding clauses prior to indexing.
        query_mapping = defaultdict(dict)
        for t in (tqdm(unique_transposed_genomes) if not silent else unique_transposed_genomes):
            if basevalues:
                values = basevalues
            else:
                values = sorted(list(set(t)))
            presence_list = [tuple(tt==value for tt in t) for value in values]
            absence_list  = [tuple(tt!=value for tt in t) for value in values]
            queries.update(presence_list)
            queries.update(absence_list)
            if bytes_mode:
                for i,q in enumerate(absence_list):
                    query_mapping[t][q] = values[i].to_bytes(1,"big")
            else:
                for i,q in enumerate(absence_list):
                    query_mapping[t][q] = values[i]
            clauses.add(frozenset(absence_list)) # one of the values must result
        queries = sorted(list(queries))
        variables = len(queries)//2
        if diversity_requirement>0:
            transposed_queries = list(map(tuple, zip(*queries)))
        index = {v:wrap_values(i+1,variables) for i,v in enumerate(queries)}
        for t in query_mapping.keys():
            query_mapping[t] = {index[a]:b for a,b in query_mapping[t].items()}
        print_silent("Problem difficulty: genomes with {} inter-diversity, generated over {} queries with depth {} with diversity {}".format(generated_diversity_requirement, len(queries), len(absence_list[0]), diversity_requirement),silent)

        # if two queries would isolate the synthetic sample, then eliminate
        print_silent("adding indistinguisability requirements",silent)
        binary_queries = [convert_to_binary(q) for q in queries]

        if solver_name=='tinicard' and biasing:
            print_silent("calculating randomisation seeds", silent)
            seeds = [1.0-sum(q)/len(q) for q in queries[:variables]]

            activities = [[0,0] for i in range(variables)]
            for i in range(len(seeds)):
                activities[i][1] = int(100*max(0.0,seeds[i]-0.8))
                activities[i][0] = int(100*max(0,-seeds[i]+1-0.8))
            activities = sum(activities,[])

        print_silent(f"GENERATING GENOME {genome_number}",silent)
        # load into SAT solver
        if solver_name=='tinicard':
            solver = pytinicard.new_solver()
        elif solver_name=='cmsgen':
            solver = pycmsgen.Solver(seed=int(time.time()))
        else:
            solver = Solver(solver_name)

        
        print_silent("Inserting indistuinguishability requirements",silent)
        if solver_name=='tinicard':
            #pytinicard.AddMemoryImplicationExtension(solver, binary_queries, len(queries[0]), 1, 1)
            #pytinicard.AddFastMemoryImplicationExtension(solver, binary_queries, len(queries[0]), indexation_bits, 1, 1)
            #pytinicard.AddFastRangedMemoryImplicationExtension(solver, binary_queries, len(queries[0]), indexation_bits, 1, 1)
            #pytinicard.AddMemoryCountImplicationExtension(solver, binary_queries, len(queries[0]), exception_space, 0)

            #if (exception_space !=0):
            #    pytinicard.AddFastCountCompactMemoryImplicationExtension(solver, binary_queries, len(queries[0]), indexation_bits, exception_space, looseness, 1 if not silent else 0, 1)
            #else:
            #    pytinicard.AddFastCompactMemoryImplicationExtension(solver, binary_queries, len(queries[0]), indexation_bits, 1 if not silent else 0, 1)
            pytinicard.AddFastCountCompactMemoryImplicationExtension(solver, binary_queries, len(queries[0]), indexation_bits, exception_space, looseness, 1 if not silent else 0, 1)
        else:
            mask = convert_to_binary([True for i in range(len(queries[0]))])
            binary_queries = [convert_to_binary(q) for q in queries]   
            query_index_to_variable = [wrap_values(i+1,variables) for i in range(len(queries))]
            if exception_space==0:
                if looseness>0:
                    for i,k1 in enumerate((tqdm(binary_queries) if not silent else binary_queries)):
                        rr = np.random.random(len(binary_queries)-i).tolist()
                        for jj,j in enumerate(range(i,len(binary_queries))):
                            if i!=j:
                                if rr[jj]<looseness:
                                    continue
                            if k1|binary_queries[j] == mask:
                                if query_index_to_variable[i]!=-query_index_to_variable[j]:
                                    solver.add_clause([ -query_index_to_variable[i],-query_index_to_variable[j] ])
                else:
                    for i,k1 in enumerate((tqdm(binary_queries) if not silent else binary_queries)):
                        for j in range(i,len(binary_queries)):
                            if k1|binary_queries[j] == mask:
                                if query_index_to_variable[i]!=-query_index_to_variable[j]:
                                    solver.add_clause([ -query_index_to_variable[i],-query_index_to_variable[j] ])
            elif exception_space<0:
                if looseness>0:
                    for i,k1 in enumerate((tqdm(binary_queries) if not silent else binary_queries)):
                        for j in range(i,len(binary_queries)):
                            if i!=j:
                                if random()<looseness:
                                    continue
                            k2 = binary_queries[j]
                            resolved_mask = ((k1|k2)&mask)^mask
                            bits_different = bit_count_function(resolved_mask)
                            #if bits_different <= np.random.choice(exception_space_array,p=exception_space_probability):
                            if bits_different <= exception_space_drawer():
                                if query_index_to_variable[i]!=-query_index_to_variable[j]:
                                    solver.add_clause([ -query_index_to_variable[i],-query_index_to_variable[j] ])
                else:
                    for i,k1 in enumerate((tqdm(binary_queries) if not silent else binary_queries)):
                        for j in range(i,len(binary_queries)):
                            k2 = binary_queries[j]
                            resolved_mask = ((k1|k2)&mask)^mask
                            bits_different = bit_count_function(resolved_mask)
                            #if bits_different <= np.random.choice(exception_space_array,p=exception_space_probability):
                            if bits_different <= exception_space_drawer():
                                if query_index_to_variable[i]!=-query_index_to_variable[j]:
                                    solver.add_clause([ -query_index_to_variable[i],-query_index_to_variable[j] ])
            else:
                if looseness>0:
                    # if two queries would isolate the synthetic sample to within <exception_space> individuals then eliminate - note that this is quantifiably stronger condition
                    for i,k1 in enumerate((tqdm(binary_queries) if not silent else binary_queries)):
                        for j in range(i,len(binary_queries)):
                            k2 = binary_queries[j]
                            resolved_mask = (k1|k2)^mask
                            bits_different = bit_count_function(resolved_mask)
                            if bits_different <= int(exception_space):
                                if query_index_to_variable[i]!=-query_index_to_variable[j]:
                                    solver.add_clause([ -query_index_to_variable[i],-query_index_to_variable[j] ])
                else:
                    # if two queries would isolate the synthetic sample to within <exception_space> individuals then eliminate - note that this is quantifiably stronger condition
                    for i,k1 in enumerate((tqdm(binary_queries) if not silent else binary_queries)):
                        for j in range(i,len(binary_queries)):
                            if i!=j:
                                if random()<looseness:
                                    continue
                            k2 = binary_queries[j]
                            resolved_mask = (k1|k2)^mask
                            bits_different = bit_count_function(resolved_mask)
                            if bits_different <= int(exception_space):
                                if query_index_to_variable[i]!=-query_index_to_variable[j]:
                                    solver.add_clause([ -query_index_to_variable[i],-query_index_to_variable[j] ])

        
        print_silent("Adding sensibility requirements",silent)
        if solver_name=="tinicard":
            for c in (tqdm(clauses) if not silent else clauses):
                pytinicard.add_clause(solver,[index[cc] for cc in c],1,1)
        else:
            for c in (tqdm(clauses) if not silent else clauses):
                solver.add_clause([index[cc] for cc in c])

        # simple diversity requirement, must be set hamming distance away from another sequence
        if diversity_requirement>0:
            print_silent("adding diversity requirements",silent)
            if solver_name=='tinicard':
                for sequence in (tqdm(transposed_queries) if not silent else transposed_queries):
                    lits = [(i+1) * (1 if a else -1) for i,a in enumerate(sequence[:variables])]
                    pytinicard.add_clause(solver,lits,diversity_requirement,1)
            else:
                assert getattr(solver,"supports_atmost",None) is not None, "Solver does not support atmost querying"
                assert solver.supports_atmost(), "Selected solver needs to support cardinality constraints"
                for sequence in (tqdm(transposed_queries) if not silent else transposed_queries):
                    lits = [(i+1) * (-1 if a else 1) for i,a in enumerate(sequence[:variables])]
                    solver.add_atmost(lits,len(lits)-diversity_requirement)

        if solver_name=='tinicard' and biasing:
            print_silent("adding solver activites",silent)
            pytinicard.set_activities(solver,activities)

        if solver_name=='tinicard':
            print_silent("Finalising solver, pure literal and implication propagation",silent)
            pytinicard.finalise(solver)
            # randomise phase information to add some randomness
            print_silent("Setting phases",silent)
            if biasing:
                pytinicard.set_phases(solver, [(i+1) * (2*(random()<seeds[i])-1) for i in range(variables)])
            else:
                pytinicard.set_phases(solver, [(i+1) * (2*randint(0,1)-1) for i in range(variables)])
        elif solver_name=='cmsgen':
            pass
        else:
            if biasing:
                #frequencies = [sum(q)/len(q) for q in queries[:variables]]
                ##e = 0.5 #https://stats.stackexchange.com/questions/214877/is-there-a-formula-for-an-s-shaped-curve-with-domain-and-range-0-1
                #extremisation_function = lambda f: 1 if f<0.4 else 0 if f>0.6 else 0.5 #lambda f: f**e/(f**e+(1-f)**e)
                #frequencies = [extremisation_function(f) for f in frequencies]
                #solver.set_phases([(i+1) * (1 if random()<frequencies[i] else -1) for i in range(variables)])
                solver.set_phases([(i+1) * (-1) for i in range(variables)])
            else:
                # randomise phase information to add some randomness
                solver.set_phases([(i+1) * (2*randint(0,1)-1) for i in range(variables)])

        # do the actual solving
        tt = time.time()
        if solver_name=='tinicard':
            if pytinicard.solve(solver) != 1:
                pytinicard.del_solver(solver)
                print_silent("detected no further possible solutions (suggest: either increase genomes, decrease genome length and/or decrease diversity requirement), proceeding to dump output",silent)
                restarts += 1
                continue
            restarts = 0
            solution = pytinicard.get_model(solver)
            pytinicard.del_solver(solver)
        elif solver_name=='cmsgen':
            sat,solution = solver.solve()
            if not sat:
                del solver
                print_silent("detected no further possible solutions (suggest: either increase genomes, decrease genome length and/or decrease diversity requirement), proceeding to dump output",silent)
                restarts += 1
                continue
            restarts = 0
            solution = [ii if vv else -ii for ii,vv in enumerate(solution) if vv is not None]
            del solver
        else:
            if solver.solve() != True:
                print_silent("detected no further possible solutions (suggest: either increase genomes, decrease genome length and/or decrease diversity requirement), proceeding to dump output",silent)
                restarts += 1
                continue
            restarts = 0
            solution = solver.get_model()
            solver.delete()
            del solver
        print_silent("SAT Solving complete in {}s".format(time.time()-tt),silent)
        
        # construct the map from dataset neucleotide combinations to synthetic neucleotide
        solution_set = set(solution)
        ret = rootstring.join([[b for a,b in query_mapping[z].items() if a in solution_set][0] for z in transposed_genomes]), cluster_information_file
        return ret
    return None, cluster_information_file



def generate_genomes(
    reference_genomes,
    sample_group_size,
    basevalues,
    number_of_genomes,
    diversity_requirement,
    generated_diversity_requirement,
    no_smart_clustering=False,
    exception_space=0, 
    silent=False,
    indexation_bits=12,
    biasing=True,
    solver_name="minicard",
    cluster_information_file=None,
    difference_samples=100,
    looseness=0,
    max_restarts=10,
    dump_all_generated=True,
    tasks=1
    ):
    
    assert sample_group_size <= len(reference_genomes), "cannot cluster group more than there are genomes"
    check_square_values(reference_genomes,basevalues)
    if cluster_information_file is not None:
        with open(cluster_information_file,"w") as f:
            f.write("CLUSTER INFORMATION FILE\n")

    genome_solutions = []

    print_silent("priming cluster method",silent)
    cluster_info = None
    if (not no_smart_clustering) and sample_group_size>=0:
        cluster_info = cluster_setup(reference_genomes, sample_group_size, silent=silent, difference_samples=difference_samples)
    print_silent("Entering the Solving process - generating genomes",silent)

    assert number_of_genomes>0
    try:
        tasks_parameters = [(
                reference_genomes, sample_group_size, basevalues,
                diversity_requirement, generated_diversity_requirement, no_smart_clustering,
                exception_space, silent, indexation_bits,
                biasing, solver_name, looseness, max_restarts, cluster_info, i
                ) for i in range(number_of_genomes)]
            
        task_count = tasks
        if task_count == -1:
            task_count = mp.cpu_count()
        if task_count > 1:
            with mp.Pool(mp.cpu_count() ) as pool:
                genome_solutions = list(pool.map(parallel_inner, tasks_parameters ))
        else:
            genome_solutions = list(map(parallel_inner,tasks_parameters))
        print_silent("Finished the Solving process",silent)

    except KeyboardInterrupt:
        print_silent("Detected Ctrl-C interrupt, proceeding to dump VCF with already generated individuals (note: double Ctrl-C to hard exit)",silent)
    except Exception as e:
        print_silent("WARNING!: exception in generation loop {}\n emergency attempt to dump individuals already generated".format(e),silent)
        print(traceback.format_exc())


    cluster_information = [g[1] for g in genome_solutions if g[0] is not None]
    if cluster_information_file is not None:
        with open(cluster_information_file,"a") as f:
            for c in cluster_information:
                f.write(str(c))
                f.write("\n")
    genome_solutions = [g[0] for g in genome_solutions if g[0] is not None]
    print_silent("{} solutions generated".format(len(genome_solutions)),silent)
    if not dump_all_generated:
        if len(genome_solutions) < number_of_genomes:
            return []
    # return generated genome string
    return genome_solutions
