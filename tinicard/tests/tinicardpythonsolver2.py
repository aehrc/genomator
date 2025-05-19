import tinicard
import sys
import re

assert len(sys.argv)>2


with open(sys.argv[1], 'r') as file:
    cnf = file.read().rstrip()
normal_constraints = re.findall(r"([-\d ]+) 0", cnf)
gt_constraints = re.findall(r"([-\d ]+) >= (\d+)", cnf)
lt_constraints = re.findall(r"([-\d ]+) <= (\d+)", cnf)

normal_constraints = [[int(a) for a in aa.split(" ")] for aa in normal_constraints]
gt_constraints = [([int(a) for a in aa.split(" ")],int(bb)) for aa,bb in gt_constraints]
lt_constraints = [([int(a) for a in aa.split(" ")],int(bb)) for aa,bb in lt_constraints]

max_var = max([0]+[max([0]+[abs(aa) for aa in a]) for a in normal_constraints])
max_var = max(max_var, max([0]+[max([0]+[abs(aa) for aa in a[0]]) for a in gt_constraints]) )
max_var = max(max_var, max([0]+[max([0]+[abs(aa) for aa in a[0]]) for a in lt_constraints]) )

from collections import defaultdict

refined_normal_constraints = []
implications = defaultdict(set)
for n in normal_constraints:
    if len(n)==2 and n[0]!=n[1]:
        implications[n[0]].add(n[1])
        implications[n[1]].add(n[0])
    else:
        refined_normal_constraints.append(n)

writer = tinicard.new_writer("./temp.dat",2*max_var+1)
for a in implications.keys():
    tinicard.start_writing(writer,a)
    for b in implications[a]:
        tinicard.write_part(writer,b)
    tinicard.end_write(writer)
tinicard.del_writer(writer)

#tinicard.debugImplications("./temp.dat")

solver = tinicard.new_solver("./temp.dat")

for c in refined_normal_constraints:
    tinicard.add_clause(solver,c,1,1)
for c in gt_constraints:
    tinicard.add_clause(solver,c[0],c[1],1)
for c in lt_constraints:
    tinicard.add_clause(solver,c[0],c[1],0)

tinicard.finalise(solver)
ret = tinicard.solve(solver)
print("RETURNED {}".format(ret))
if (ret==1):
    model = " ".join([str(a) for a in tinicard.get_model(solver)])
    with open(sys.argv[2], 'w') as file:
        file.write(f"SAT\n{model} 0\n")
else:
    with open(sys.argv[2], 'w') as file:
        file.write(f"UNSAT")

tinicard.del_solver(solver)
