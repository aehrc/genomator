#include "PyModuleUtils.h"
#include "PyTiniCard.h"
#include "PyTiniCardExtensions.h"


char newSolver_docs[] = "Create and return a new Tinicard Solver object; no arguments, returning tinicard object";
char delSolver_docs[] = "Destroy and free a Tinicard Solver object, one argument of existing tinicard object, no return";
char addClause_docs[] = "Add a cardinality clause to the Tinicard object, arguments must be tinicard object, list of literals, the cardinality parmeter, and 0/1 flag for greater than cardinality clause type";
char finalise_docs[] = "once all clauses are added, then finalise, does some preparation in preparation for solving process";
char setPhases_docs[] = "passing in a list of ordered literals for all relevant variables, set the phases to correspond with the phase of the input literals, input as a list of literals";
char setActivities_docs[] = "passing in a list of double the number of variables, set their activites (if variables present) to that in the list of pairs. positive and negative, positive and negative, and so on.";
char solve_docs[] = "actually run the sat solver, returning 1 if SAT, 0 if UNSAT, 2 if finalise() not called before solving, 3 if error";
char getModel_docs[] = "actually return the list of the literals of the solution generated. insofar as the sat solver has successfully solved the problem";



char implication_docs[] = "processing implications";



PyMethodDef pytinicard_funcs[] = {
	{	"new_solver",
		(PyCFunction)new_solver,
		METH_NOARGS,
		newSolver_docs},
	{	"del_solver",
		(PyCFunction)del_solver,
		METH_VARARGS,
		delSolver_docs},
  {	"add_clause",
    (PyCFunction)add_clause,
    METH_VARARGS,
    addClause_docs},
  {	"finalise",
    (PyCFunction)finalise,
    METH_VARARGS,
    finalise_docs},
  {	"set_phases",
    (PyCFunction)set_phases,
    METH_VARARGS,
    setPhases_docs},
  {	"set_activities",
    (PyCFunction)set_activities,
    METH_VARARGS,
    setActivities_docs},
  {	"solve",
    (PyCFunction)solve,
    METH_VARARGS,
    solve_docs},
  {	"get_model",
    (PyCFunction)get_model,
    METH_VARARGS,
    getModel_docs},

  {	"AddMemoryImplicationExtension",
		(PyCFunction)AddMemoryImplicationExtension,
		METH_VARARGS,
		implication_docs},
  {	"AddMemoryCountImplicationExtension",
		(PyCFunction)AddMemoryCountImplicationExtension,
		METH_VARARGS,
		implication_docs},
	{	"AddFastMemoryImplicationExtension",
		(PyCFunction)AddFastMemoryImplicationExtension,
		METH_VARARGS,
		implication_docs},
	{	"AddFastRangedMemoryImplicationExtension",
		(PyCFunction)AddFastRangedMemoryImplicationExtension,
		METH_VARARGS,
		implication_docs},
	{	"AddFastCompactMemoryImplicationExtension",
		(PyCFunction)AddFastCompactMemoryImplicationExtension,
		METH_VARARGS,
		implication_docs},
	{	"AddFastCountCompactMemoryImplicationExtension",
		(PyCFunction)AddFastCountCompactMemoryImplicationExtension,
		METH_VARARGS,
		implication_docs},
		
	{	NULL}
};




char pytinicard_docs[] = "This is the PyTiniCard module.";
PyModuleDef pytinicard_mod = {
	PyModuleDef_HEAD_INIT,
	"pytinicard",
	pytinicard_docs,
	-1,
	pytinicard_funcs,
	NULL,
	NULL,
	NULL,
	NULL
};
PyMODINIT_FUNC PyInit_pytinicard(void) {
	PyObject *m = PyModule_Create(&pytinicard_mod);
	if (m == NULL)
		return NULL;
	SATError = PyErr_NewException((char *)"pysolvers.error", NULL, NULL);
	Py_INCREF(SATError);
	if (PyModule_AddObject(m, "error", SATError) < 0) {
		Py_DECREF(SATError);
		return NULL;
	}
	return m;
}


