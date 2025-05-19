#include <stdio.h>
#include <Python.h>
#include <csetjmp>
#include <signal.h>
#include "SatSolver.h"


#ifndef _PYMODULE_UTILS
#define _PYMODULE_UTILS

extern "C" {

PyObject *void_to_pyobj(void *ptr);
void *pyobj_to_void(PyObject *obj);

extern bool has_registered_exit_function;
extern int* temp_array;
extern int temp_array_size;
extern PyObject *SATError;
extern jmp_buf env;

void CleanupModule();
void sigint_handler(int signum);
int parse_python_list(PyObject* obj);

}
#endif
