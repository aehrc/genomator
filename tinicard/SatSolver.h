#ifndef _SAT_SOLVER
#define _SAT_SOLVER


#include <vector>
#include <deque>
using namespace std;

#include "IntPool.h"
#include "ImplicationExtension.h"

#define HALFLIFE 128
#define _DT 32		// RSAT phase selection threshold 

#define _NEGA 0		// variable values are negative
#define _POSI 1		// positive, or
#define _FREE 2		// free

#define SIGN(lit) 	(((lit) > 0)?_POSI:_NEGA)
#define VAR(lit)	(abs(lit))
#define NEG(lit)	(-(lit))

#define FREE(lit) 	(vars[VAR(lit)].value == _FREE)
#define SET(lit)	(vars[VAR(lit)].value == SIGN(lit))
#define RESOLVED(lit)	(vars[VAR(lit)].value == SIGN(NEG(lit)))
#define IMPLIST(lit) 	(vars[VAR(lit)].imp[SIGN(lit)]) 
#define IMPCLAUSE(lit) 	(vars[VAR(lit)].implication_clause[SIGN(lit)]) 
#define WATCH(lit)	(vars[VAR(lit)].watch[SIGN(lit)])
#define SCORE(var)	(vars[(var)].activity[0]+vars[(var)].activity[1])

#define SWAP(A,B)   {auto temp = A; A=B; B=temp;}
#define VC          (vars.size()-1)
#define ERROR(msg)  {fprintf(stderr,"ERROR: ");fprintf(stderr,msg);fprintf(stderr,"\n");exit(1);}
#define WARN(msg)   {fprintf(stderr,"WARNING: ");fprintf(stderr,msg);fprintf(stderr,"\n");}

#ifdef UPDEBUG 
	#define DB(x) x
#else 
	#define DB(x) 
#endif


struct Variable{
	bool mark = false;			// used in 1-UIP derivation
	bool phase = false;			// suggested phase for decision
	char value = _FREE;			// _POSI, _NEGA, _FREE
	unsigned dLevel = 0;		// decision level where var is set
	int *ante = NULL;			// antecedent clause if implied
	unsigned activity[2] = {0,0};		// scores for literals
	vector<int> imp[2];			// implication lists for binary clauses
	vector<int> watch[2];		// watch lists for other clauses
	int implication_clause[2][3] = {{0,0,0},{0,0,0}}; 
	Variable() {
		watch[0].clear(); watch[1].clear();
		imp[0].clear(); imp[1].clear();
	};
};

struct Luby{			// restart scheduler as proposed in 
	vector<unsigned> seq; 	// Optimal Speedup of Las Vegas Algorithms
	unsigned index; 	// Michael Luby et al, 1993
	unsigned k;
	Luby(): index(0), k(1) {}
	unsigned next(){
		if(++index == (unsigned) ((1 << k) - 1))
			seq.push_back(1 << (k++ - 1));
		else
			seq.push_back(seq[index - (1 << (k - 1))]);
		return seq.back();
	}
};



class SatSolver{
private:

	IntPool memory_pool;

	vector<int> unit_clauses;
	vector<int*> clauses;
	vector<int> cl;	// clause length
	vector<int> card;  // clause cardinality

	void debug();
	vector<Variable> vars; 		// array of variables
	vector<unsigned> varOrder;		// variables ordered by score
	vector<unsigned> varPosition;		// variable position in varOrder
	unsigned nextVar = 0;		// starting point in varOrder

	int nextClause = -1; 		// starting point to look for unsatisfied conflict clause
	int initialClauses = 0; 		// the number of initial clauses in the problem (the rest are conflict clauses)
  int rand_var_select_int = 0; // some crap to help the variable select mechanism select random variables

	int *stackTop = (int*)sizeof(int); 			// decision/implication stack
	int *zero = NULL;				// the zeroth position of the stack
	unsigned aLevel;		// assertion level
	unsigned dLevel=1; 		// decision level
	unsigned nDecisions=0; 		// num of decisions
	unsigned nConflicts=0;		// num of conflicts
	unsigned nRestarts=0;		// num of restarts
	deque<int> conflictLits;	// stores conflict literals
	deque<int> tmpConflictLits;	// ditto, temporary
	int *conflictClause;		// points to learned clause in litPool 

	int load_DIMACS(char* fname);
	int assertUnitClauses();
	int assertPureLiterals();
	void setLiteral(int lit, int *ante);	// set value, ante, level 
	bool assertLiteral(int lit, int *ante);	// set literal and perform unit propagation
	bool decide(int lit);			// increment dLevel and call assertLitreal
	void learnClause(int *firstLit);	// store learned clause in conflictLits and call addClause
	void addClause();			// add conflictLits to litPool and set up watches
	bool assertCL();			// assert literal implied by conflict clause
	void backtrack(unsigned level);		// undo assignments in levels > level 
	void scoreDecay();			// divide scores by constant
	void updateScores(int *first);		// update variable scores and positions

	unsigned nVars;		// num of variables in varOrder
	Luby luby;		// restart scheduler
	unsigned lubyUnit = 512;	// unit run length for Luby's
	unsigned nextDecay = HALFLIFE;	// next score decay point
	unsigned nextRestart;	// next restart point

	bool finalised = false; // if we are in loading clauses phase, or solving phase
	void initialiseVariableOrder();
	bool unsat = false;

	int selectLiteral();
	bool verifySolution();

public:

	ImplicationExtension* implication_extension = NULL;
  bool check_extension;
	int addImplicationExtension(ImplicationExtension* extension);
	
	int reserve_variables(int vc);
	int addClause(int* clause, int size, bool greater_than, int &cardinality, bool update_activity);
	int addImplication(int a, int b);
  int addImplication(int a, int b, int activity_increment);
	int finalise();
	bool setPhases(int* new_phases, int size);
	bool setActivities(int* new_activities, int size);
	
	SatSolver();
	SatSolver(char *fname);
	~SatSolver();
	
	int run();
	void printStats();
	void printSolution(FILE *);
	int getModel(int** buffer, int* buffer_size);
};

inline bool SatSolver::assertCL(){
	return assertLiteral(*conflictClause, conflictClause + 1);
}

inline bool SatSolver::decide(int lit){
	nDecisions++; dLevel++;
	return assertLiteral(lit, NULL);
}

inline void SatSolver::backtrack(unsigned bLevel){
	for(unsigned var; vars[var = VAR(*(stackTop - 1))].dLevel > bLevel;){
		if(vars[var].dLevel < dLevel) vars[var].phase = vars[var].value;
		vars[var].value = _FREE;
		if(varPosition[var] < nextVar) nextVar = varPosition[var];
		stackTop--;
	}
	dLevel = bLevel;
}

inline void SatSolver::scoreDecay(){
	// this may slightly disturb var order
	// e.g., (7 + 7) => (3 + 3) whereas (6 + 8) => (3 + 4)
	//   .. updated so that activity=0 only if variable sign never occurs
	for(unsigned i = 1; i <= VC; i++){
		vars[i].activity[0] = (vars[i].activity[0]!=0) | (vars[i].activity[0]>>1);
		vars[i].activity[1] = (vars[i].activity[1]!=0) | (vars[i].activity[1]>>1);
	}
}


#endif
