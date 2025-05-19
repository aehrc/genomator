#include "PyModuleUtils.h"

#include "tinicard_extensions/MemoryImplicationExtension.cpp"
#include "tinicard_extensions/MemoryCountImplicationExtension.cpp"
#include "tinicard_extensions/FastMemoryImplicationExtension.cpp"
#include "tinicard_extensions/FastRangedMemoryImplicationExtension.cpp"
#include "tinicard_extensions/FastCompactMemoryImplicationExtension.cpp"
#include "tinicard_extensions/FastCountCompactMemoryImplicationExtension.cpp"
#include "tinicard_extensions/constants.h"

#include "string.h"

PyObject* AddMemoryImplicationExtension(PyObject* self, PyObject* args) {
	PyObject *s_obj;
	PyObject *binary_queries = NULL;
	int max_size=-1;
	int not_silent=0;
	int main_thread = 1;
	if(!PyArg_ParseTuple(args, "OOi|ii", &s_obj, &binary_queries, &max_size, &not_silent, &main_thread)) {
		printf("could not parse arguments\n"); return NULL;
	}

	PyOS_sighandler_t sig_save;
	if (main_thread) {
		sig_save = PyOS_setsig(SIGINT, sigint_handler);
		if (setjmp(env) != 0) {
			PyErr_SetString(SATError, "Caught keyboard interrupt");
			return NULL;
		}
	}
	if (not_silent) printf("loading sat solver object");
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
	MemoryImplicationExtension(s, binary_queries, max_size, not_silent);

	if (main_thread)
		PyOS_setsig(SIGINT, sig_save);
	Py_RETURN_NONE;
}



PyObject* AddMemoryCountImplicationExtension(PyObject* self, PyObject* args) {
	PyObject *s_obj;
	PyObject *binary_queries = NULL;
	int max_size=-1;
	int not_silent=0;
	int main_thread = 1;
  float exception_space = 0;
	if(!PyArg_ParseTuple(args, "OOif|ii", &s_obj, &binary_queries, &max_size, &exception_space, &not_silent, &main_thread)) {
		printf("could not parse arguments\n"); return NULL;
	}

	PyOS_sighandler_t sig_save;
	if (main_thread) {
		sig_save = PyOS_setsig(SIGINT, sigint_handler);
		if (setjmp(env) != 0) {
			PyErr_SetString(SATError, "Caught keyboard interrupt");
			return NULL;
		}
	}
	if (not_silent) printf("loading sat solver object");
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
	MemoryCountImplicationExtension(s, binary_queries, max_size, exception_space, not_silent);


	if (main_thread)
		PyOS_setsig(SIGINT, sig_save);
	Py_RETURN_NONE;
}


PyObject* AddFastMemoryImplicationExtension(PyObject* self, PyObject* args) {
	PyObject *s_obj;
	PyObject *binary_queries = NULL;
	int max_size=-1;
	int index_bits=-1;
	int not_silent=0;
	int main_thread = 1;
	if(!PyArg_ParseTuple(args, "OOii|ii", &s_obj, &binary_queries, &max_size, &index_bits, &not_silent, &main_thread)) {
		printf("could not parse arguments\n"); return NULL;
	}

	PyOS_sighandler_t sig_save;
	if (main_thread) {
		sig_save = PyOS_setsig(SIGINT, sigint_handler);
		if (setjmp(env) != 0) {
			PyErr_SetString(SATError, "Caught keyboard interrupt");
			return NULL;
		}
	}
	if (not_silent) printf("loading sat solver object");
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
	FastMemoryImplicationExtension(s, binary_queries, max_size, index_bits, not_silent);

	if (main_thread)
		PyOS_setsig(SIGINT, sig_save);
	Py_RETURN_NONE;
}





PyObject* AddFastRangedMemoryImplicationExtension(PyObject* self, PyObject* args) {
	PyObject *s_obj;
	PyObject *binary_queries = NULL;
	int max_size=-1;
	int index_bits=-1;
	int not_silent=0;
	int main_thread = 1;
	if(!PyArg_ParseTuple(args, "OOii|ii", &s_obj, &binary_queries, &max_size, &index_bits, &not_silent, &main_thread)) {
		printf("could not parse arguments\n"); return NULL;
	}

	PyOS_sighandler_t sig_save;
	if (main_thread) {
		sig_save = PyOS_setsig(SIGINT, sigint_handler);
		if (setjmp(env) != 0) {
			PyErr_SetString(SATError, "Caught keyboard interrupt");
			return NULL;
		}
	}
	if (not_silent) printf("loading sat solver object");
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
	FastRangedMemoryImplicationExtension* r;
	r = new FastRangedMemoryImplicationExtension(s, binary_queries, max_size, index_bits, not_silent);
	
	if (main_thread)
		PyOS_setsig(SIGINT, sig_save);
	Py_RETURN_NONE;
}




PyObject* AddFastCompactMemoryImplicationExtension(PyObject* self, PyObject* args) {
	PyObject *s_obj;
	PyObject *binary_queries = NULL;
	int max_size=-1;
	int index_bits=-1;
	int not_silent=0;
	int main_thread = 1;
	if(!PyArg_ParseTuple(args, "OOii|ii", &s_obj, &binary_queries, &max_size, &index_bits, &not_silent, &main_thread)) {
		printf("could not parse arguments\n"); return NULL;
	}

	PyOS_sighandler_t sig_save;
	if (main_thread) {
		sig_save = PyOS_setsig(SIGINT, sigint_handler);
		if (setjmp(env) != 0) {
			PyErr_SetString(SATError, "Caught keyboard interrupt");
			return NULL;
		}
	}
	if (not_silent) printf("loading sat solver object");
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
	FastCompactMemoryImplicationExtension* r;
	r = new FastCompactMemoryImplicationExtension(s, binary_queries, max_size, index_bits, not_silent);
	
	if (main_thread)
		PyOS_setsig(SIGINT, sig_save);
	Py_RETURN_NONE;
}



PyObject* AddFastCountCompactMemoryImplicationExtension(PyObject* self, PyObject* args) {
	PyObject *s_obj;
	PyObject *binary_queries = NULL;
	int max_size=-1;
	int index_bits=-1;
	int not_silent=0;
	int main_thread = 1;
  float exception_space = 0;
  float looseness = 0;
	if(!PyArg_ParseTuple(args, "OOiiff|ii", &s_obj, &binary_queries, &max_size, &index_bits, &exception_space, &looseness, &not_silent, &main_thread)) {
		printf("could not parse arguments\n"); return NULL;
	}

	PyOS_sighandler_t sig_save;
	if (main_thread) {
		sig_save = PyOS_setsig(SIGINT, sigint_handler);
		if (setjmp(env) != 0) {
			PyErr_SetString(SATError, "Caught keyboard interrupt");
			return NULL;
		}
	}
	if (not_silent) printf("loading sat solver object");
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
  if ((exception_space<0) || (looseness!=0))
    s->check_extension=false;
	FastCountCompactMemoryImplicationExtension* r;
	r = new FastCountCompactMemoryImplicationExtension(s, binary_queries, max_size, index_bits, exception_space, looseness, not_silent);
	
	if (main_thread)
		PyOS_setsig(SIGINT, sig_save);
	Py_RETURN_NONE;
}





