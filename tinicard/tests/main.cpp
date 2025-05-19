
#include "../SatSolver.cpp"
#include "../IntPool.cpp"
//#include "../RandomAccessArray.cpp"

int normal_clauses[7][11] = 
{{1,2,3,4,5,6,7,8,9,10,0},
 {-7,-4,5,0},
 {-3,4,-10,5,0},
 {-7,-5,-10,0},
 {-7,5,0},
 {1,2,3,4,-5,-6,7,-8,9,10,0},
 {1,2,-3,4,-5,-6,7,-8,9,10,0}};

int lt_clauses[2][2][11] = 
{{{2,8,5,0},{2}},
 {{-8,2,0},{0}}};
 
int gt_clauses[3][2][11] = 
{{{-9,1,-7,10,0},{2}},
 {{2,-7,6,-4,-10,-6,0},{4}},
 {{-1,8,6,4,5,0},{4}}};
 


int main(int argc, char **argv){
	SatSolver* solver = new SatSolver();
	int cardinality = 1;
	for (int i=0; i<7; i++) {
		int size=0;
		for (int* p=normal_clauses[i]; *p; p++) size++;
		solver->addClause(normal_clauses[i], size, true, cardinality, true);
	}
	for (int i=0; i<2; i++) {
		int size=0;
		for (int* p=lt_clauses[i][0]; *p; p++) size++;
		cardinality = lt_clauses[i][1][0];
		solver->addClause(lt_clauses[i][0], size, false, cardinality, true);
	}
	for (int i=0; i<3; i++) {
		int size=0;
		for (int* p=gt_clauses[i][0]; *p; p++) size++;
		cardinality = gt_clauses[i][1][0];
		solver->addClause(gt_clauses[i][0], size, true, cardinality, true);
	}

	//solver->addClause(int* clause, int size, bool greater_than, int &cardinality, bool update_activity);
	solver->finalise();

	int result = solver->run();

	if(result==1){ 
		printf("s SATISFIABLE\n");
		solver->printSolution(stdout);
	}else printf("s UNSATISFIABLE\n");
	solver->printStats();
	delete solver;
	return 0;
}

