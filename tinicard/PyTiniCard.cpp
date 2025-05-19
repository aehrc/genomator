#include "PyModuleUtils.h"
#include "PyTiniCard.h"

PyObject* new_solver(PyObject *self) {
	SatSolver *s = new SatSolver();
	if (s == NULL) {
		PyErr_SetString(PyExc_RuntimeError,"Cannot create a new solver.");
		return NULL;
	}
	return void_to_pyobj((void *)s);
}


PyObject* del_solver(PyObject *self, PyObject *args) {
	PyObject *s_obj;
	if (!PyArg_ParseTuple(args, "O", &s_obj))
		return NULL;
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
	if (s->implication_extension != NULL)
		delete s->implication_extension;
	delete s;
	Py_RETURN_NONE;
}


PyObject* finalise(PyObject *self, PyObject *args) {
	PyObject *s_obj;
	if (!PyArg_ParseTuple(args, "O", &s_obj))
		return NULL;
	SatSolver *s = (SatSolver*)pyobj_to_void(s_obj);
	return PyLong_FromLong(s->finalise());
}



PyObject* add_clause(PyObject *self, PyObject *args) {
	PyObject *s_obj;
	PyObject *c_obj;
	int rhs;
	int gt;
	if (!PyArg_ParseTuple(args, "OOii", &s_obj, &c_obj, &rhs,&gt))
		return NULL;
	// get pointer to solver
	SatSolver* s = (SatSolver*)pyobj_to_void(s_obj);
	int clause_size = parse_python_list(c_obj);
	if (clause_size==-1) return NULL;
	int res = s->addClause(temp_array, clause_size, gt/*bool greater_than*/, rhs, false);//true);
	PyObject *ret = PyBool_FromLong((long)res);
	return ret;
}



PyObject* set_phases(PyObject *self, PyObject *args) {
	PyObject *s_obj;
	PyObject *p_obj;
	if (!PyArg_ParseTuple(args, "OO", &s_obj, &p_obj))
		return NULL;
	// get pointer to solver
	SatSolver* s = (SatSolver*)pyobj_to_void(s_obj);
	int list_size = parse_python_list(p_obj);
	if (list_size==-1) return NULL;
	int res = s->setPhases(temp_array, list_size);
	PyObject *ret = PyBool_FromLong((long)res);
	return ret;
}




PyObject* set_activities(PyObject *self, PyObject *args) {
	PyObject *s_obj;
	PyObject *p_obj;
	if (!PyArg_ParseTuple(args, "OO", &s_obj, &p_obj))
		return NULL;
	// get pointer to solver
	SatSolver* s = (SatSolver*)pyobj_to_void(s_obj);
	int list_size = parse_python_list(p_obj);
	if (list_size==-1) return NULL;
	int res = s->setActivities(temp_array, list_size);
	PyObject *ret = PyBool_FromLong((long)res);
	return ret;
}



PyObject* solve(PyObject *self, PyObject *args) {
	PyObject *s_obj;
	int main_thread = 1;
	if (!PyArg_ParseTuple(args, "O|i", &s_obj, &main_thread))
		return NULL;
	// get pointer to solver
	SatSolver* s = (SatSolver*)pyobj_to_void(s_obj);
	PyOS_sighandler_t sig_save;
	if (main_thread) {
		sig_save = PyOS_setsig(SIGINT, sigint_handler);
		if (setjmp(env) != 0) {
			PyErr_SetString(SATError, "Caught keyboard interrupt");
			return NULL;
		}
	}
	int res = s->run();
	if (main_thread)
		PyOS_setsig(SIGINT, sig_save);
	if (res==2) {PyErr_SetString(PyExc_RuntimeError,"solve called without finalise");return NULL;}
	if (res==3) {PyErr_SetString(PyExc_RuntimeError,"solve resulted in bad solution");return NULL;}
	PyObject *ret = PyLong_FromLong((long)res);
	return ret;
}


PyObject* get_model(PyObject *self, PyObject *args) {
	if (!has_registered_exit_function) {
		if (Py_AtExit(CleanupModule)) {
			PyErr_SetString(PyExc_RuntimeError,"Unable to register cleanup function.");
			return NULL;
		}
		has_registered_exit_function = true;
	}
	PyObject *s_obj;
	if (!PyArg_ParseTuple(args, "O", &s_obj))
		return NULL;
	// get pointer to solver
	SatSolver* s = (SatSolver*)pyobj_to_void(s_obj);
	int solution_size = s->getModel(&temp_array,&temp_array_size);
	PyObject *model = PyList_New(solution_size);
	for (int i = 0; i < solution_size; i++) {
		PyObject *lit = PyLong_FromLong(temp_array[i]);
		PyList_SetItem(model, i, lit);
	}
	PyObject *ret = Py_BuildValue("O", model);
	Py_DECREF(model);
	return ret;
}


