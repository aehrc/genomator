#include "PyModuleUtils.h"

extern "C" {

PyObject *void_to_pyobj(void *ptr){ return PyCapsule_New(ptr, NULL, NULL);}
void *pyobj_to_void(PyObject *obj){ return PyCapsule_GetPointer(obj, NULL);}

bool has_registered_exit_function = false;
int* temp_array = NULL;
int temp_array_size = 0;
PyObject *SATError;
jmp_buf env;


void CleanupModule(void) {
	if (temp_array!=NULL)
		free(temp_array);
}
void sigint_handler(int signum) {longjmp(env, -1);}

int parse_python_list(PyObject* obj) {
	if (!has_registered_exit_function) {
		if (Py_AtExit(CleanupModule)) {
			PyErr_SetString(PyExc_RuntimeError,"Unable to register cleanup function.");
			return -1;
		}
		has_registered_exit_function = true;
	}
	if (!PyList_Check(obj)) {printf("second argument must be a list\n");return -1;}
	long length = PyList_Size(obj);
	if ((int)(length*sizeof(int)) > temp_array_size) {
		temp_array_size = length*sizeof(int);
		temp_array = (int*)realloc(temp_array, length*sizeof(int));
	}
	for (long i=0; i<length; i++) {
		PyObject* lit = PyList_GetItem(obj, i);
		if (!PyLong_Check(lit)) {printf("could not parse the int argument in clause\n"); return -1;}
		int elem = (int)PyLong_AsLong(lit);
		temp_array[i]=elem;	
	}
	return length;
}

}
