#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <algorithm>
#include <functional>
#include <set>
#include <ctype.h>

#include "SatSolver.h"
#include "utils.c"

SatSolver::SatSolver(char *fname) : memory_pool(5000,100) {
	reserve_variables(0);
  check_extension=true;
	if (load_DIMACS(fname)) ERROR("trivial unsatisfiabile constraint detected")
	if (assertUnitClauses()) ERROR("contradiction from unit clauses")
	if (assertPureLiterals()) ERROR("somehow failed to assert pure literals")
	nextRestart = luby.next()*lubyUnit;
	initialiseVariableOrder();
	finalised = true;
}

SatSolver::SatSolver() : memory_pool(5000,100) {
  check_extension=true;
	nextRestart = luby.next()*lubyUnit;
	reserve_variables(0);
}

SatSolver::~SatSolver(){
	free(zero);
}

int SatSolver::finalise() {
	finalised = true;
	if (assertUnitClauses()) {unsat=true; return 1;}
	//if (assertPureLiterals()) {unsat=true; return 2;}
	initialiseVariableOrder();
	return 0;
}

bool SatSolver::setPhases(int* new_phases, int size) {
	if (size!=int(vars.size())-1) return false;
	for (int i=0; i<size; i++)
		vars[i+1].phase = new_phases[i]>0;
	return true;
}

bool SatSolver::setActivities(int* new_activities, int size) {
	if (finalised) return 2;
	if (size>2*VC) return 1;
	for (int i=0; i<size; i++) {
		int v = ((i>>1)+1)*(1-(i&1)*2);
		if (vars[VAR(v)].activity[SIGN(v)] != 0) // NOTE: will not set activity of unknown var
			vars[VAR(v)].activity[SIGN(v)] = new_activities[i] | 1;
	}
	return 0;
}


int SatSolver::addImplicationExtension(ImplicationExtension* extension) {
	if (finalised) return 2;
	if (implication_extension != NULL) return 1;
	implication_extension = extension;
	int variablenum = implication_extension->getVariableNum();
	reserve_variables(variablenum); // add variables as nessisary
	
	for (int i=-variablenum; i<=variablenum; i++) {
		if (i==0) continue;
		vars[VAR(i)].activity[SIGN(i)] += implication_extension->getActivity(i);
	}
	return 0;
}

// function used for sorting variables in order of their score 
struct compScores : public binary_function<unsigned, unsigned, bool> {
  vector<Variable>& vars;
  compScores(vector<Variable>& myVars) : vars(myVars) {}
  bool operator()(unsigned a, unsigned b) const {
    return SCORE(a) > SCORE(b);
  }
};

void SatSolver::initialiseVariableOrder() {
	nVars = 0;
	for(unsigned i = 1; i <= VC; i++) 
		if(vars[i].value == _FREE && SCORE(i) > 0){
			varOrder[nVars++] = i;
			vars[i].phase = (vars[i].activity[_POSI] > vars[i].activity[_NEGA])?_POSI:_NEGA;
		}
	varOrder.resize(nVars);
    sort(varOrder.begin(), varOrder.end(), compScores(vars));
	for(unsigned i = 0; i < nVars; i++) varPosition[varOrder[i]] = i; 
}


// different heuristics for variable selection are go here (feel free to experiment)
int SatSolver::selectLiteral(){
  /*for (int i=0; i<vars.size(); i++) {
    vars[i].activity[0]=0;
    vars[i].activity[1]=0;
  }

	for (int v=1; v<=(int)VC; v++) for (int k=-1; k<=1; k+=2) { // checking implications
		int lit = k*v;
		if (FREE(lit))
			for (auto iit = IMPLIST(lit).begin(); iit!=IMPLIST(lit).end(); iit++)
				if (FREE(*iit)) {
          vars[VAR(lit)].activity[SIGN(lit)]++;
          vars[VAR(*iit)].activity[SIGN(*iit)]++;
        }
	}

  if (implication_extension!=NULL) {
    for (int i=0; i<1000; i++) { // draw only a sample of implication clauses and add their activities
      rand_var_select_int = (i*i+i + rand_var_select_int*10+572) ^ 47485; // some pseudorandom crap
      int lit = ((rand_var_select_int>>1)%VC) + 1;
      if (((lit)&1)==0) lit *= -1;
      if (FREE(lit)) {
        int *imp = implication_extension->getBlock(lit);
        if (imp!=NULL)
          for (int counter = 0; counter<implication_extension->getBlockSize(lit); counter++,imp++)
            if (FREE(*imp))
              vars[VAR(*imp)].activity[SIGN(*imp)]++;
      }
    }
  }

  for (int i=0; i<initialClauses; i++) {
    for (int j=0; j<cl[i]; j++)
      if (SET(clauses[i][j]))
        goto selectLiteral_continue;
    for (int j=0; j<cl[i]; j++)
      if (FREE(clauses[i][j])) {
        printf("var activity %i \n",VAR(clauses[i][j]));
        vars[VAR(clauses[i][j])].activity[SIGN(clauses[i][j])]++;
      }
    selectLiteral_continue:;
  }

  int max_index = 0;
  int max_activity = 0;
  for (int i=1; i<=VC; i++) {
    if (FREE(i)) {
      if (vars[i].activity[_POSI] > max_activity) {
        max_activity = vars[i].activity[_POSI];
        max_index = i;
      }
    }
    if (FREE(-i)) {
      if (vars[i].activity[_NEGA] > max_activity) {
        max_activity = vars[i].activity[_NEGA];
        max_index = -i;
      }
    }
  }
  if (max_index != 0) {
    return -max_index;
  }*/


  

  // // SELECTING OPPOSITE OF FIRST UNSET WATCH LITERAL
  //for (int i=0; i<clauses.size(); i++) {
  //  if (!(SET(clauses[i][0]) || SET(clauses[i][0]))) {
  //    if (FREE(clauses[i][0])){
  //      return -clauses[i][0];
  //    }
  //    if (FREE(clauses[i][1])){
  //      return -clauses[i][1];
  //    }
  //  }
  //}

/*
  rand_var_select_int = rand_var_select_int % nVars;
  int count_upto = 0;
  while (true) {
    int old_count_upto = count_upto;
    for (unsigned int i=1; i<=nVars; i++) {
      if (vars[i].value == _FREE) {
        if (count_upto == rand_var_select_int) {
          rand_var_select_int = (i*i+i + rand_var_select_int*10+572) ^ 47485; // some pseudorandom crap
          //return ((rand_var_select_int >> 1)+i)%2==1 ? i:-i;
          return i;
        }
        count_upto += 1;
      }
    }
    if (count_upto == old_count_upto) {
      return 0;
    }
  }*/



	unsigned x = 0;
  // OPPOSTIE VSIDS
	for(unsigned i = nextVar; i < nVars; i++){
		if(vars[varOrder[i]].value == _FREE){
			x = varOrder[i];
			nextVar = i + 1;
			// RSAT phase selection
			int d = vars[x].activity[_POSI] - vars[x].activity[_NEGA];
			if(d > _DT) return -x; else if(-d > _DT) return x;
			else return (vars[x].phase == _POSI)?(-x):(int)(x);
		}
	}
	/*// pick best var in unsatisfied conflict clause nearest to top of stack
	// but only search 256 clauses
	int lastClause = nextClause > 256 + initialClauses-1 ? (nextClause - 256) : initialClauses;
	for(int i = nextClause; i >= lastClause; i--){
		int *p = clauses[nextClause = i];
		// skip satisfied clauses
		bool sat = false; 
		for(; (*p); p++) if(SET(*p)){ sat = true; break; }
		if(sat) continue;
		// traverse again, find best variable of clause
		int score = -1;
		for(p = clauses[i]; (*p); p++) if(FREE(*p) && ((int) SCORE(VAR(*p))) > score){
			x = VAR(*p); score = SCORE(x);
		}
		// RSAT phase selection
		int d = vars[x].activity[_POSI] - vars[x].activity[_NEGA];
		if(d > _DT) return x; else if(-d > _DT) return -x;
		else return (vars[x].phase == _POSI)?(x):-(int)(x);
	}*/

	// fall back to VSIDS 
	for(unsigned i = nextVar; i < nVars; i++){
		if(vars[varOrder[i]].value == _FREE){
			x = varOrder[i];
			nextVar = i + 1;
			// RSAT phase selection
			int d = vars[x].activity[_POSI] - vars[x].activity[_NEGA];
			if(d > _DT) return x; else if(-d > _DT) return -x;
			else return (vars[x].phase == _POSI)?(x):-(int)(x);
		}
	}
	return 0;
}

// run the CDCL algorithm to determine a solution
//   return 0=UNSAT 1=SAT 2=INITIALISATION_NOT_COMPLETE 3=ERROR_STATE
int SatSolver::run(){
	if (!finalised) return 2;
	if (unsat) return false;
	if(dLevel == 0) return false; 		// assertUnitClauses has failed
	for(int lit; (lit = selectLiteral());){ // pick decision literal
		if(!decide(lit)) do{ 		// decision/conflict
			if(aLevel == 0) return false; // conflict has occurred in dLevel 1, unsat 
			if(nConflicts == nextDecay) {nextDecay += HALFLIFE; scoreDecay();} // score decay
			nextClause = clauses.size() - 1; // rewind to top of clause stack
			if(nConflicts == nextRestart){ // restart at dLevel 1 
				nRestarts++;
				nextRestart += luby.next() * lubyUnit;
				backtrack(1);
				if(dLevel != aLevel) break;
			// partial restart at aLevel 
			}else backtrack(aLevel);
		}while(!assertCL());		// assert conflict literal
	}
	if(!verifySolution()) return 3;
	return true;	
}

bool SatSolver::verifySolution(){
	for (int i=0; i<initialClauses; i++) { // all loaded cardinality clauses
		int clause_card = card[i];
		for (int k=0; k<cl[i]; k++) {
			if (SET(clauses[i][k])) clause_card--;
			if (clause_card<=0) goto verify_continue;
		}
		return false;
		verify_continue:;
	}
	for (int v=1; v<=(int)VC; v++) for (int k=-1; k<=1; k+=2) { // checking implications
		int lit = k*v;
		if (RESOLVED(lit))
			for (auto iit = IMPLIST(lit).begin(); iit!=IMPLIST(lit).end(); iit++)
				if (!SET(*iit)) return false;
	}

	// implications stored in file loaded access array
  if (check_extension)
    if (implication_extension!=NULL)
      for (int lit=-(int)VC; lit<=(int)VC; lit++) {
        if (lit==0) continue;
        if (RESOLVED(lit)) {
          int *imp = implication_extension->getBlock(lit);
          if (imp!=NULL)
            for (int counter = 0; counter<implication_extension->getBlockSize(lit); counter++,imp++)
              if (!SET(*imp)) return false;
        }
      }
    
	return true;
}

void SatSolver::printSolution(FILE *ofp){
	for(unsigned i = 1; i <= VC; i++)
		if(vars[i].value == _POSI) fprintf(ofp, "%d ", i);
		else if(vars[i].value == _NEGA) fprintf(ofp, "-%d ", i);
	fprintf(ofp, "0\n");
}

void SatSolver::printStats(){
	printf("c %d decisions, %d conflicts, %d restarts\n", nDecisions, nConflicts, nRestarts);
}


int SatSolver::getModel(int** buffer, int* buffer_size){
	if (*buffer_size<(int)VC) {
		*buffer = (int*)realloc(*buffer,sizeof(int)*VC);
		*buffer_size = VC;
	}
	for(unsigned i = 1; i <= VC; i++)
		if(vars[i].value == _POSI) (*buffer)[i-1]=i;
		else if(vars[i].value == _NEGA)  (*buffer)[i-1]=-i;
	return (int)VC;
}


int SatSolver::reserve_variables(int vc) {
	if (finalised) return 1;
	if (vc<=(int)VC) return 0;
	vars.resize(vc+1);
	for (int k=0; k<=(int)VC; k++) {
		IMPCLAUSE(k)[1] = k;
		IMPCLAUSE(-k)[1] =-k;
	}
	varOrder.resize(vc+1);
	varPosition.resize(vc+1);
	int *new_zero = (int*)realloc(zero, (vc+1)*sizeof(int));
	if (new_zero == NULL) ERROR("failed to resize stack")
	stackTop = new_zero + (stackTop-zero);
	zero = new_zero;
	zero[0] = 0;
	return 0;
}

int SatSolver::addClause(int* clause, int size, bool greater_than, int &cardinality, bool update_activity) {
	if (finalised) return 3;
	if (!greater_than) { // only deal with greater-than clauses
		for (int i=0; i<size; i++) clause[i]=-clause[i];
		cardinality = size - cardinality;
	}
	// purge opposite literals
	sort(clause, clause+size, abs_compare);
	for (int w=0,r=1,old_size=size; r<old_size; r++) {
		if (clause[r]==-clause[w]) {w--; cardinality--; size-=2;}
		else clause[++w]=clause[r];
	}
	
	if (cardinality<=0) return 2; // code for vacuous constraint
	if (cardinality>size) {unsat=true; return 1;} // code for trivially unsatisfiable constraint
	if (cardinality==size) { // clause is immediate binding, all literals must be set
		for (int i=0; i<size; i++) {
			unit_clauses.push_back(clause[i]);
			reserve_variables(abs(clause[i]));
		} 
		return 0;
	}
	if (size==2) { // special handling for binary variables
		int lit0=clause[0],lit1=clause[1];
		reserve_variables(abs(lit0)); reserve_variables(abs(lit1));
		IMPLIST(lit0).push_back(lit1);
		IMPLIST(lit1).push_back(lit0);
		if (update_activity) {
			vars[VAR(lit0)].activity[SIGN(lit0)]++;
			vars[VAR(lit1)].activity[SIGN(lit1)]++;
		} else {
			vars[VAR(lit0)].activity[SIGN(lit0)] |= 1;
			vars[VAR(lit1)].activity[SIGN(lit1)] |= 1;
		}
	} else { // otherwise meaningful ternary clauses
		int* new_clause = memory_pool.alloc(size+1);
		clauses.push_back(new_clause);
		cl.push_back(size);
		card.push_back(cardinality);
		int max_abs = 0;
		for (int i=0; i<size; i++)
			if (abs(clause[i])>max_abs) max_abs=abs(clause[i]);
		reserve_variables(max_abs);
		for (int i=0; i<size; i++) {
			new_clause[i] = clause[i];
			if (update_activity) {// update activities
				vars[VAR(clause[i])].activity[SIGN(clause[i])]++;
			} else {
				vars[VAR(clause[i])].activity[SIGN(clause[i])] |= 1;
			}
		}
		for (int i=0; i<=cardinality; i++)
			WATCH(clause[i]).push_back((int)clauses.size()-1); // set up watches
	} 
	nextClause = clauses.size()-1;
	initialClauses = clauses.size();
	return 0;
}

int SatSolver::addImplication(int a, int b) {
	if (finalised) return 3;
	if (a==-b) return 2; // code for vacuous constraint
	if (a==b) {unit_clauses.push_back(a);reserve_variables(abs(a)); return 0;} //unit
	reserve_variables(abs(a)); reserve_variables(abs(b));
	IMPLIST(a).push_back(b);
	IMPLIST(b).push_back(a);
	vars[VAR(a)].activity[SIGN(a)]++;
	vars[VAR(b)].activity[SIGN(b)]++;
	//vars[VAR(a)].activity[SIGN(a)] |= 1;
	//vars[VAR(b)].activity[SIGN(b)] |= 1;
	return 0;
}


int SatSolver::addImplication(int a, int b, int activity_increment) {
	if (finalised) return 3;
	if (a==-b) return 2; // code for vacuous constraint
	if (a==b) {unit_clauses.push_back(a);reserve_variables(abs(a)); return 0;} //unit
	reserve_variables(abs(a)); reserve_variables(abs(b));
	IMPLIST(a).push_back(b);
	IMPLIST(b).push_back(a);
  if (activity_increment==1) {
    vars[VAR(a)].activity[SIGN(a)]++;
    vars[VAR(b)].activity[SIGN(b)]++;
    //vars[VAR(a)].activity[SIGN(a)] |= 1;
    //vars[VAR(b)].activity[SIGN(b)] |= 1;
  }
	return 0;
}



int SatSolver::load_DIMACS(char* fname) {
	int vc, cc, max_clause_len = 1024;
	char c; bool loading_header = true; FILE* f;
	if ((f = fopen(fname, "r")) == NULL) ERROR("Cannot open file")
	int *literals = (int *) malloc(max_clause_len * sizeof(int));

	while ((c=skip_whitespace(f))!=EOF) {
		if (c=='c') {} // skipping comments
		else if (loading_header) { // parsing comments until header is reached
			if(fscanf(f, "p cnf%c %d %d", &c, &vc, &cc) == 3){
				clauses.reserve(cc);
				cl.reserve(cc);
				card.reserve(cc);
				reserve_variables(vc);
				loading_header = false;
			}
		} else { // parsing CNF body
			int len = 0, ret, cardinality=1;
			read_another:
			if (fscanf(f, "%d", &(literals[len]))) {
				if (literals[len]==0) { // check for terminating zero for normal cnf
					ret=addClause(literals, len, true, cardinality, true);
				} else {
					if(++len >= max_clause_len) // check to see if read-array needs to be resized
						literals = (int*)realloc(literals, (max_clause_len*=2) * sizeof(int));
					goto read_another;
				}
			} else if (fscanf(f, ">= %d", &cardinality))
				ret=addClause(literals, len, true, cardinality, true);
			  else if (fscanf(f, "<= %d", &cardinality))
			  	ret=addClause(literals, len, false, cardinality, true);
			  else { fprintf(stderr, "Invalid CNF line\n"); exit(0); }
			if (ret==2) WARN("vacuous clause detected")
			if (ret==1) return 1;
			cc--;
		}
		skip_to_new_line(f);
	}
	free(literals);
	fclose(f);
	if (cc!=0) WARN("clause count header wrong")
	if ((int)VC>vc) WARN("variable count header wrong")
	return 0;
}



int SatSolver::assertUnitClauses() {
	if (dLevel!=1) WARN("attempting to assert unit clauses from dlevel!=1")
	for (auto lit = unit_clauses.begin(); lit!=unit_clauses.end(); lit++) {
		if (FREE(*lit)) {
			if (!assertLiteral(*lit,zero)) {backtrack(dLevel - 1);return 1;}
		} else if(RESOLVED(*lit)) return 1;
	}
	return 0;
}

int SatSolver::assertPureLiterals() {
	for(int i = 1; i <= (int) VC; i++) if(vars[i].value == _FREE){
		// ante is NULL, as opposed to empty clause for implied literals
		if(vars[i].activity[_POSI] == 0 && vars[i].activity[_NEGA] > 0)
			{if (!assertLiteral(-i, NULL)) return 1;}
		else if(vars[i].activity[_NEGA] == 0 && vars[i].activity[_POSI] > 0)
			{if (!assertLiteral(i, NULL)) return 1;}
	}
	return 0;
}




inline void SatSolver::setLiteral(int lit, int *ante){
	DB(if (vars[VAR(lit)].value!=_FREE) WARN("setting an already set literal"))
	vars[VAR(lit)].value = SIGN(lit);
	vars[VAR(lit)].ante = ante;
	vars[VAR(lit)].dLevel = dLevel;
}

bool SatSolver::assertLiteral(int lit, int *ante){
	int *newStackTop = stackTop;
	setLiteral(*(newStackTop++) = lit, ante);
	DB(printf("%d: %d =>", dLevel, lit);)
	//DB(printf("stack size %i\n",(stackTop-zero)/sizeof(int));)
	while(stackTop < newStackTop){
		int lit = NEG(*(stackTop++)); // the literal resolved (as opposed to set)	

		// implications via binary clauses
		for (auto imp = IMPLIST(lit).begin(); imp != IMPLIST(lit).end(); imp++) {
			if(FREE(*imp)){ // implication
				DB(printf(" %d", *imp);)
				setLiteral(*(newStackTop++) = *imp, &(IMPCLAUSE(lit)[1])); 
			}else if(RESOLVED(*imp)){ // contradiction
				DB(printf(" [%d]\n", *imp);)
				nConflicts++;
				stackTop = newStackTop;
				IMPCLAUSE(lit)[0] = *imp;	// make up temporary binary clause
				learnClause(IMPCLAUSE(lit));	// for clause learning purposes
				return false;
			}
		}
		
		// implications stored in file loaded access array
		if (implication_extension!=NULL) {
      if (implication_extension->getBlockSizeNonZero(lit)) {
				int *imp = implication_extension->getBlock(lit);
				if (imp!=NULL) {
          for (int counter = 0; counter<implication_extension->getBlockSize(lit); counter++,imp++) {
					//for (; *imp; imp++) {
						if(FREE(*imp)){ // implication
							DB(printf(" %d", *imp);)
							setLiteral(*(newStackTop++) = *imp, &(IMPCLAUSE(lit)[1])); 
						}else if(RESOLVED(*imp)){ // contradiction
							DB(printf(" [%d]\n", *imp);)
							nConflicts++;
							stackTop = newStackTop;

              //TODO: cannot handle unit contradictions from implication_extension
              if (*imp == IMPCLAUSE(lit)[1]) {
                printf("WARNING: cannot handle unit contradictions from implication extension -- %i %i\n",*imp,lit);
              }
              IMPCLAUSE(lit)[0] = *imp;	// make up temporary binary clause
              learnClause(IMPCLAUSE(lit));	// for clause learning purposes
							return false;
						}
					}
				}
			}
		}
		
		// other implications
		vector<int> &watchList = WATCH(lit);
		for(vector<int>::iterator iit = watchList.begin(); iit != watchList.end(); iit++) {
			int i = *iit;
			int* w_clause = clauses[i];
			int w_card = card[i];
			int w_cl = cl[i];
			DB(if(!RESOLVED(lit)) WARN("implication does not make sense") )

			if (w_card==1) { // normal clause, special unnessisary code for speedier results (all conflict clauses are normal...)
				int position = (w_clause[1]==lit);
				DB(if(w_clause[position]!=lit) WARN("watch not in clause beginning") )
				if (SET(w_clause[!position])) continue;  // clause satisfied, no need to check further
				// othewise check for an inplace swap
				for (int k=2; k<w_cl; k++) // look for free/true literal
					if (!RESOLVED(w_clause[k])) { // found
						*(iit--) = watchList.back(); watchList.pop_back(); // unwatch watch
						SWAP(w_clause[position], w_clause[k]) // swap literals
						WATCH(w_clause[position]).push_back(i); // watch the new literal
						goto next_watch_literal;
					}
				// otherwise free/true literals not found, we either have implication or contradiction
				if (FREE(w_clause[!position])) {
					if (position==0) SWAP(w_clause[position],w_clause[1]) // move causitive variables to end of clause
					DB(printf(" %d", w_clause[0]);)
					DB(for (int k=1; k<w_cl; k++) if (!RESOLVED(w_clause[k])) WARN("Implication sense violation"))
					setLiteral(*(newStackTop++) = w_clause[0], &(w_clause[1]) );
				} else { // contradiction
					DB(printf(" [%d]\n", w_clause[!position]);)
					DB(for (int k=0; k<cl[i]; k++) if (!RESOLVED(w_clause[k])) WARN("Implication sense violation"))
					nConflicts++;
					stackTop = newStackTop;
					learnClause(w_clause);
					return false;
				}
				
			} else { // a meaningful cardinality clause
				int count_set=0; // count the number of set watches
				int position = -1;
				for (int k=0; k<=w_card; k++) {
					count_set += SET(w_clause[k]);
					if (w_clause[k]==lit) position = k; // and find the position of the lit
				}
				DB(if(position==-1) WARN("watch not in clause beginning") )
				if (count_set>=w_card) continue; // clause satisfied, no need to check further
				// othewise check for an inplace swap
				for (int k=w_card+1; k<w_cl; k++) // look for free/true literal
					if (!RESOLVED(w_clause[k])) { // found
						*(iit--) = watchList.back(); watchList.pop_back(); // unwatch watch
						SWAP(w_clause[position], w_clause[k]) // swap literals
						WATCH(w_clause[position]).push_back(i); // watch the new literal
						goto next_watch_literal;
					}
				// otherwise free/true literals not found, we either have implication or contradiction
				int index; // try and find other resolved watched literal
				for (index=0; index<=w_card; index++)
					if (index!=position && RESOLVED(w_clause[index]))
						break;
				if (index == w_card+1) { // implication
					SWAP(w_clause[position],w_clause[card[i]]) // move causitive variables to end of clause
					for (int k=0; k<w_card;k++) // string the implications
						if (FREE(w_clause[k])) {
							DB(printf(" %d", w_clause[k]);)
							setLiteral(*(newStackTop++) = w_clause[k], &(w_clause[card[i]]) );
						}
					DB(for (int k=w_card; k<w_cl; k++) if (!RESOLVED(w_clause[k])) WARN("Implication sense violation"))
				} else { // contradiction
					// do swapping to place the resolved watched literal, and resolved <index> literal last
					SWAP(w_clause[position],w_clause[card[i]]) // swap <pos> into card[i]
					SWAP(w_clause[index==w_card ? position : index],w_clause[card[i]-1]) // swap <index> into card[i]-1
					DB(printf(" [%d]\n", w_clause[card[i]-1]);)
					DB(for (int k=w_card-1; k<cl[i]; k++) if (!RESOLVED(w_clause[k])) WARN("Implication sense violation"))
					nConflicts++;
					stackTop = newStackTop;
					learnClause(&(w_clause[w_card-1]));
					return false;
				}
			}
			next_watch_literal:;
		}
	}
	DB(printf("\n");)
	return true;
}

void SatSolver::learnClause(int *first){
	if(dLevel == 1){ aLevel = 0; return; } // contradiction in level 1, instance unsat
	updateScores(first);// update var scores and positions
	conflictLits.clear(); // clear temporary storage
	unsigned curLevelLits = 0;

	// mark all literals in conflicting clause
	// push to tmpConflictLits those set prior to current dLevel
	for(tmpConflictLits.clear(); *first; first++){
		if(vars[VAR(*first)].dLevel == 1) continue; // drop known backbone literals
		if(vars[VAR(*first)].dLevel < dLevel) tmpConflictLits.push_back(*first);
		else curLevelLits++;
		vars[VAR(*first)].mark = true;
	}

	// generate 1-UIP conflict clause
	int lit; while(true){
		// pop literal from stack as in backtrack
		lit = *(--stackTop); 
		unsigned var = VAR(lit);
		vars[var].value = _FREE;
		if(!vars[var].mark){
			if(varPosition[var] < nextVar) nextVar = varPosition[var];
			continue;
		}

		// unmark
		vars[var].mark = false;
		// if not decision, update scores for the whole ante clause
		if(vars[var].ante) updateScores(vars[var].ante - 1);
		// update nextVar
		if(varPosition[var] < nextVar) nextVar = varPosition[var];
		// UIP reached
		if(curLevelLits-- == 1) break;
		// else, replace with antecedent (resolution)
		for(int *ante = vars[var].ante; *ante; ante++){
			if(vars[VAR(*ante)].mark || vars[VAR(*ante)].dLevel == 1) continue;
			if(vars[VAR(*ante)].dLevel < dLevel) tmpConflictLits.push_back(*ante);
			else curLevelLits++;
			vars[VAR(*ante)].mark = true;
		}
	}

	// conflict clause minimization
	// compute assertion level (aLevel) 
	// make sure front of conflictLits is a literal from assertion level
	aLevel = 1; 
	deque<int>::iterator it;
	for(it = tmpConflictLits.begin(); it != tmpConflictLits.end(); it++){
		bool redundant = true;
		int *ante = vars[VAR(*it)].ante;
		if(ante == NULL) redundant = false;
		else for(; *ante; ante++) if(!vars[VAR(*ante)].mark){ redundant = false; break; }
		if(!redundant){
			if(vars[VAR(*it)].dLevel > aLevel){
			       	aLevel = vars[VAR(*it)].dLevel;	
		       		conflictLits.push_front(*it);
			}else conflictLits.push_back(*it);
		}
	}

	// clear variable marks
	for(it = tmpConflictLits.begin(); it != tmpConflictLits.end(); it++)
		vars[VAR(*it)].mark = false;

	// unique lit from current dLevel pushed last
	conflictLits.push_back(-lit);

	// add clause to litPool and set up watches
	addClause();

	DB(	printf("   [aLevel: %d]", aLevel);
		for(deque<int>::iterator it = conflictLits.begin(); it != conflictLits.end(); it++)
			printf(" %d", *it);
		printf("\n");
	)
}

inline void SatSolver::addClause(){
	unsigned size = conflictLits.size();
	if(size > 1){
		conflictClause = memory_pool.alloc(size+1);
		conflictClause[0] = conflictLits.back();
		clauses.push_back(conflictClause); // add clause to list
		cl.push_back(size);
		card.push_back(1);
		conflictClause[1] = conflictLits.front(); // second literal is one from assertion level
		// set up 2 watches
		WATCH(conflictLits.back()).push_back(clauses.size()-1);
		WATCH(conflictLits.front()).push_back(clauses.size()-1);
		// copy rest of literals to litPool
		for(unsigned i = 1; i < size - 1; i++) conflictClause[i+1] = conflictLits[i];
	} else {
		conflictClause = &(IMPCLAUSE(conflictLits.back())[1]);
	}
}

void SatSolver::updateScores(int *p){
	for(; *p; p++){
		unsigned v = VAR(*p);
		vars[v].activity[SIGN(*p)]++;
		unsigned it = varPosition[v];
		
		// variable already at beginning
		if(it == 0) continue;
		unsigned score = SCORE(v);

		// order hasn't been violated
		if(score <= SCORE(varOrder[it - 1])) continue;

		// promote var up the order, using binary search from zChaff04
		int step = 0x400, q;
		for(q = ((int) it) - step; q >= 0; q -= step) 
			if(SCORE(varOrder[q]) >= score) break;
		for(q += step, step >>= 1; step > 0; step >>= 1){
			if(q - step >= 0) if(SCORE(varOrder[q - step]) < score)
				q -= step;
		}

		// swap it and q	
		varOrder[it] = varOrder[q]; varPosition[v] = q; 
		varPosition[varOrder[q]] = it; varOrder[q] = v;	
	}
}


