from random import randint,choice

f = open("cnf.cnf","w")
clauses = randint(5,15)
variables = list(range(1,11))
f.write(f"p cnf+ {len(variables)} {clauses}\n")
for i in range(clauses):
    if (i==0):
        f.write(f"{' '.join([str(a) for a in variables])} 0\n")
        continue
    clause_type = randint(0,2)
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
