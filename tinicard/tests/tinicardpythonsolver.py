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

solver = tinicard.new_solver()

for c in normal_constraints:
    tinicard.add_clause(solver,c,1,1)
for c in gt_constraints:
    tinicard.add_clause(solver,c[0],c[1],1)
for c in lt_constraints:
    tinicard.add_clause(solver,c[0],c[1],0)
print("FINALISE RETURNED:", tinicard.finalise(solver))
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
