from random import randint,choice
import sys
assert len(sys.argv)==3

f = open("cnf.cnf","w")
variables = list(range(1,int(sys.argv[1])+1))
clauses = int(sys.argv[2])
print(f"generating CNF with {variables} variables and {clauses} clauses")
f.write(f"p cnf+ {len(variables)} {clauses}\n")
for i in range(clauses):
    if (i==0):
        f.write(f"{' '.join([str(a) for a in variables])} 0\n")
        continue
    clause_type = randint(0,3)
    if clause_type==3:
        v1 = choice(variables)
        v2 = choice(variables)
        while v2==v1:
            v2 = choice(variables)
        clause = [(randint(0,1)*2-1)*v1, (randint(0,1)*2-1)*v2]
        clause = [str(a) for a in clause]
        print(clause)
        f.write(f"{' '.join(clause)} 0\n")
    else:
        clause = []
        for j in range(randint(1,7)):
            clause.append( (randint(0,1)*2-1)*choice(variables) )
        clause = [str(a) for a in clause]
        clause = list(set(clause))
        print(clause)
        if clause_type==0:
            f.write(f"{' '.join(clause)} 0\n")
        if clause_type==1:
            f.write(f"{' '.join(clause)} >= {randint(1,len(clause))}\n")
        if clause_type==2:
            f.write(f"{' '.join(clause)} <= {randint(0,len(clause))}\n")

f.close()
