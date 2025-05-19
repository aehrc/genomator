import tinicard
import sys

assert len(sys.argv)>0


solver = tinicard.new_solver()

tinicard.add_clause(solver,[1,2,3],1,1)
tinicard.add_clause(solver,[-3,-2],1,1)

print(tinicard.finalise(solver))
print(tinicard.solve(solver))
print(tinicard.get_model(solver))

tinicard.del_solver(solver)
