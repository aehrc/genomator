import cyvcf2
import time
from tqdm import tqdm
from pysat.card import *
from collections import defaultdict
from pysat.solvers import Glucose3, Minicard
from .vcf_generate import parse_VCF_to_genome_strings
from .generate import convert_to_binary
import traceback
from random import randint, shuffle, choice
import numpy as np
from stopit import ThreadingTimeout
from contextlib import contextmanager
none_context = lambda: (contextmanager(lambda: iter([None]))())

# given a generator that produces integer numbers with bits corresponding to sets of including
# specific members
# produce a subset of thoes members which are supersets of all others
def reduce_subsume(generator):
    data_list = dict()
    set_binary = set()
    for i,data in enumerate(generator):
        g,e = data
        if g not in set_binary:
            for b in list(set_binary):
                gb = g&b
                if gb==g: #b subsumes g
                    break
                if gb==b: #g subsumes b
                    set_binary.remove(b)
                    del data_list[b]
            else:
                set_binary.add(g)
                data_list[g]=e
        if i%1000==0:
            Z = [len(z) for z in list(data_list.values())]
            print(len(set_binary),sum(Z)*1.0/len(Z))
    set_binary = list(set_binary)
    data_list = [data_list[d] for d in set_binary]
    return data_list,set_binary


# given a generator that produces integer numbers with bits corresponding to sets of including
# specific members
# produce a subset of thoes members which are supersets of all others
def reduce_subsume_2(generator):
    data_list = dict()
    set_binary = defaultdict(list)
    mask = (2**8)-1
    for counter,data in enumerate(generator):
        g,e = data
        g_mask = g&mask

        # Subsubmption check 1: check that the data is not allready subsumed by something else
        break_loop = False
        for i in range(mask,-1,-1):
            if (i&g_mask) == g_mask: # potential for stuff at index i, to subsume g
                for b in set_binary[i]:
                    if (b&g) == g: # b subsumes g
                        break_loop = True
                        break
            if break_loop:
                break
        if break_loop: # detected that g is subsumed by something, discarding g
            continue

        if len(e)<15: #True
            # Subsumption check 2: then eliminate all entries that this subsumes
            for i in range(mask+1):
                if (i&g_mask) == i: # potential for g to subsume stuff at index i
                    j = 0
                    while j < len(set_binary[i]):
                        b = set_binary[i][j]
                        if (b&g) == b: # g subsumes b
                            set_binary[i][j] = set_binary[i][-1]
                            set_binary[i].pop()
                            del data_list[b]
                        else:
                            i+=1

            # add it
            set_binary[g_mask].append(g)
        data_list[g]=e

        # diagnostics
        if counter%1000==0:
            Z = [len(z) for z in list(data_list.values())]
            print(sum([len(s) for s in set_binary.values()]),sum(Z)*1.0/len(Z),len(Z))
    data_list = list(data_list.values())
    return data_list


def side_stich_dual_iterator(size,enumerator_wrapper=None):
    if enumerator_wrapper is None:
        enumerator = range(0,2*size-1)
    else:
        enumerator = enumerator_wrapper(range(0,2*size-1))
    for index_sum in enumerator:
        for i in range(max(0,index_sum-size+1),min(index_sum+1,size)):
            yield i,(index_sum-i)

def max_0(*args):
    try:
        return max(*args)
    except Exception as e:
        print("WARNING: exception {}".format(e))
    return 0


# The first genome is generated
# the next genome is the target
# The remaining genomes are the attackers dataset
# 'N' is the size of the random clusters
def generate_genomator_indices(genomes, N, equal_constraint=True, inequality_constraint=True, diversity_requirement=0):
    assert len(genomes) > N, "not enough genomes supplied for argument N to make sense"
    transposed_genomes = list(map(tuple, zip(*genomes)))
    unique_transposed_genomes = sorted(list(set(transposed_genomes)))

    def binary_signature_generator(unique_transposed_genomes):
        for t in tqdm(unique_transposed_genomes):
            values = sorted(list(set(t))) #+ [255]
            signatures = set([tuple([tt==value for tt in t]) for value in values]+
                             [tuple([tt!=value for tt in t]) for value in values])
            for query in signatures:
                if query[0] is False:
                    yield convert_to_binary(query),query
    queries, binary_queries = reduce_subsume(binary_signature_generator(unique_transposed_genomes))
    Z = sorted(list(zip(queries,binary_queries)),key=lambda x:sum(x[0]),reverse=True)
    queries, binary_queries = zip(*Z)

    clauses = []

    def clause_generator(queries, binary_queries):
        for i,j in side_stich_dual_iterator(len(queries),tqdm):
            lits = [k for k,b in enumerate(zip(queries[i],queries[j])) if (True not in b) and (k!=0)]
            binary_lits = binary_queries[i] | binary_queries[j]
            if len(lits)==0:
                print("WARNING: TRIVIAL UNSATISFIABILITY")
                yield binary_lits,lits
                return
            else:
                yield binary_lits,lits
    clauses = reduce_subsume_2(clause_generator(queries, binary_queries))
    #clauses,_ = reduce_subsume(clause_generator(queries, binary_queries))

    variables = list(range(1,len(genomes)))
    max_variable = max(variables)
    if inequality_constraint:
        cnf_part = list(CardEnc.atmost(variables, N, max(variables), None, EncType.sortnetwrk))
        max_variable = max(max_variable,max_0([max_0([abs(cc) for cc in c]) for c in cnf_part]))
        clauses += cnf_part
        if equal_constraint:
            cnf_part = list(CardEnc.atleast(variables, N, max_variable, None, EncType.sortnetwrk))
            max_variable = max(max_variable,max_0([max_0([abs(cc) for cc in c]) for c in cnf_part]))
            clauses += cnf_part

    for i,g in enumerate(genomes[1:]):
        if sum([a!=b for a,b in zip(g,genomes[0])])<diversity_requirement:
            clauses.append([-(i+1)])

    return clauses, max_variable

def output_cnf(filename, clauses, max_variable):
    with open(filename, "w") as f:
        f.write("p cnf {} {}\n".format(max_variable, len(clauses)))
        for c in clauses:
            for cc in c:
                f.write("{} ".format(cc))
            f.write("0\n")

def sat_count(clauses,core_variables,max_variable,max_iterations=None,timeout=None):
    g = Glucose3()
    for c in clauses:
        g.add_clause(c)
    solving = True
    solutions = []
    raw_solutions = []
    print("beginning SAT model counting")
    pbar = tqdm()
    model = None
    try:
        with ThreadingTimeout(timeout) if timeout is not None else none_context() as timeout_cts:
            while solving:
                #if (model is None) or (int(time.time())%3==0):
                g.set_phases([i*(randint(0,1)*2-1) for i in range(1,max_variable+1)]) #ensure all variables loaded, and randomise solver
                #else:
                #    g.set_phases([-l for l in choice(raw_solutions)])
                solving = g.solve()
                if solving:
                    model = g.get_model()
                    raw_solutions.append(sorted([l for l in model if abs(l)<=core_variables]))
                    model = [l for l in model if l>0 and abs(l)<=core_variables]
                    solutions.append(model)
                    g.add_clause([-l for l in model])
                    pbar.update(1)
                if max_iterations is not None and len(solutions)>max_iterations:
                    break
    except KeyboardInterrupt:
        print("Detected Ctrl-C interrupt")
    except Exception as e:
        print("WARNING!: exception in generation loop {}\n emergency attempt to dump individuals already generated".format(e))
        print(traceback.format_exc())
    pbar.close()
    print("finished SAT model counting")
    return solutions

def sat_count_cmsgen(clauses,core_variables,max_variable,max_iterations=None,timeout=None):
    import pycmsgen
    g = pycmsgen.Solver(seed=int(time.time()))
    for c in clauses:
        g.add_clause(c)
    solving = True
    solutions = []
    print("beginning SAT model counting: cmsgen")
    pbar = tqdm()
    try:
        with ThreadingTimeout(timeout) if timeout is not None else none_context() as timeout_cts:
            while solving:
                sat, solution = g.solve()
                if sat:
                    model = [ii if vv else -ii for ii,vv in enumerate(solution) if vv is not None]
                    model = [l for l in model if l>0 and abs(l)<=core_variables]
                    solutions.append(model)
                    g.add_clause([-l for l in model])
                    pbar.update(1)
                if max_iterations is not None and len(solutions)>max_iterations:
                    break
    except KeyboardInterrupt:
        print("Detected Ctrl-C interrupt")
    except Exception as e:
        print("WARNING!: exception in generation loop {}\n emergency attempt to dump individuals already generated".format(e))
        print(traceback.format_exc())
    pbar.close()
    print("finished SAT model counting")
    return solutions

def sat_count_minicard(clauses,core_variables,max_variable,N,upper_exception_space=0,max_iterations=None,timeout=None,solve_timeout=None):
    if upper_exception_space<0:
        exception_space_array = list(range(int(abs(upper_exception_space))+2))
        exception_space_probability = [min(1,abs(upper_exception_space)+1-a) for a in exception_space_array]
        exception_space_probability = [a*1.0/sum(exception_space_probability) for a in exception_space_probability]
        exception_space_array = [a+1 for a in exception_space_array]
    else:
        exception_space_array = [upper_exception_space+1]
        exception_space_probability = [1.0]
    variable_list = list(range(1,max_variable+1))
    neg_variable_list = [-v for v in variable_list]
    solutions = []
    raw_solutions = []
    pbar = tqdm()
    try:
        with ThreadingTimeout(timeout) if timeout is not None else none_context() as timeout_cts:
            while True:
                # extra randomisation by shuffling lits and clauses
                shuffle(clauses)
                for c in clauses:
                    shuffle(c)
                shuffle(solutions)
                for s in solutions:
                    shuffle(s)

                solver = Minicard()
                # Add clauses with controllably randomised bound
                for c in clauses:
                    # add atleast (negate lits and invert rhs)
                    solver.add_atmost([-cc for cc in c],len(c)-int(np.random.choice(exception_space_array,p=exception_space_probability)))
                # constrain to make new solutions
                for s in solutions:
                    solver.add_clause([-ss for ss in s])
                # searching for EXACTLY <N> genomes included
                solver.add_atmost(variable_list,N)
                solver.add_atmost(neg_variable_list,len(variable_list)-N)

                # finalise, randomise phases and solve
                #if (len(raw_solutions)==0) or (int(time.time())%3==0):
                solver.set_phases([i*(randint(0,1)*2-1) for i in range(1,max_variable+1)]) #ensure all variables loaded, and randomise solver
                #else:
                #    solver.set_phases([-l for l in choice(raw_solutions)]) #bias solution away from previous solutions
                solving = False
                with ThreadingTimeout(solve_timeout) if solve_timeout is not None else none_context() as timeout_cts2:
                    solving = solver.solve()
                if solving:
                    solution = solver.get_model()
                    solutions.append([l for l in solution if l>0 and abs(l)<=core_variables])
                    raw_solutions.append(sorted([l for l in solution if abs(l)<=core_variables]))
                    pbar.update(1)
                if max_iterations is not None and len(solutions)>max_iterations:
                    break
                solver.delete()
                del solver
    except KeyboardInterrupt:
        print("Detected Ctrl-C interrupt")
    except Exception as e:
        print("WARNING!: exception in generation loop {}\n emergency attempt to dump individuals already generated".format(e))
        print(traceback.format_exc())
    pbar.close()
    print("finished SAT model counting")
    return solutions

def sat_count_tinicard(clauses,core_variables,max_variable,N,upper_exception_space=0,max_iterations=None,timeout=None):
    if upper_exception_space<0:
        exception_space_array = list(range(int(abs(upper_exception_space))+2))
        exception_space_probability = [min(1,abs(upper_exception_space)+1-a) for a in exception_space_array]
        exception_space_probability = [a*1.0/sum(exception_space_probability) for a in exception_space_probability]
        exception_space_array = [a+1 for a in exception_space_array]
    else:
        exception_space_array = [upper_exception_space+1]
        exception_space_probability = [1.0]
    import pytinicard
    solutions = []
    pbar = tqdm()
    try:
        with ThreadingTimeout(timeout) if timeout is not None else none_context() as timeout_cts:
            while True:
                # extra randomisation by shuffling lits and clauses
                shuffle(clauses)
                for c in clauses:
                    shuffle(c)
                shuffle(solutions)
                for s in solutions:
                    shuffle(s)

                solver = pytinicard.new_solver()
                # Add clauses with controllably randomised bound
                for c in clauses:
                    pytinicard.add_clause(solver,c,int(np.random.choice(exception_space_array,p=exception_space_probability)),1)
                # constrain to make new solutions
                for s in solutions:
                    pytinicard.add_clause(solver,[-ss for ss in s],1,1)
                # searching for EXACTLY <N> genomes included
                pytinicard.add_clause(solver,list(range(1,max_variable+1)),N,1)
                pytinicard.add_clause(solver,list(range(1,max_variable+1)),N,0)

                # finalise, randomise phases and solve
                pytinicard.finalise(solver)
                pytinicard.set_phases(solver,[(i+1) * (2*randint(0,1)-1) for i in range(max_variable)])
                if pytinicard.solve(solver) != 1:
                    continue
                solution = pytinicard.get_model(solver)
                solutions.append([l for l in solution if l>0 and abs(l)<=core_variables])
                pytinicard.del_solver(solver)
                pbar.update(1)
                if max_iterations is not None and len(solutions)>max_iterations:
                    break
    except KeyboardInterrupt:
        print("Detected Ctrl-C interrupt")
    except Exception as e:
        print("Exception {} detected".format(e))
        print(traceback.format_exc())
    pbar.close()
    return solutions

