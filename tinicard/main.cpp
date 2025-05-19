#define VERSION "0.01"
#include <stdio.h>
#include <stdlib.h>
#ifdef _MSC_VER
#include <ctime>
double _get_cpu_time(){ 
  return (double) clock() / CLOCKS_PER_SEC;
}
#else
#include <sys/time.h>
#include <sys/resource.h>
#include <unistd.h>
double _get_cpu_time(){ 
	struct rusage usage;
  	getrusage(RUSAGE_SELF, &usage);
  	return (usage.ru_utime.tv_usec + usage.ru_stime.tv_usec) * 
	(1e-6) + (usage.ru_utime.tv_sec + usage.ru_stime.tv_sec); 
}
#endif
#include "SatSolver.h"

int main(int argc, char **argv){
	printf("c TiniCard %s\n", VERSION);
	if(argc < 2) exit(0);
	double _start_time = _get_cpu_time();

	printf("c solving %s\n", argv[1]);
	SatSolver solver(argv[1]);

	bool result = solver.run();

	if(argc > 2){
		if(result==1){ 
			FILE *ofp;
			if ((ofp = fopen(argv[2], "w")) != NULL){ 
				fprintf(ofp, "SAT\n");
				solver.printSolution(ofp);
				fclose(ofp);
			}
		}
	}else{
		if(result==1){ 
			printf("s SATISFIABLE\n");
			solver.printSolution(stdout);
		}else printf("s UNSATISFIABLE\n");
	}
	solver.printStats();
	printf("c solved in %.2fs\n", _get_cpu_time() - _start_time);
	exit(result?10:20);
}

