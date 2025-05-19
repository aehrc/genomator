#include "PyModuleUtils.h"

#ifndef _PYTINICARD_H
#define _PYTINICARD_H



PyObject* new_solver(PyObject *self);
PyObject* del_solver(PyObject *self, PyObject *args);
PyObject* finalise(PyObject *self, PyObject *args);
PyObject* add_clause(PyObject *self, PyObject *args);
PyObject* set_phases(PyObject *self, PyObject *args);
PyObject* solve(PyObject *self, PyObject *args);
PyObject* get_model(PyObject *self, PyObject *args);
PyObject* set_activities(PyObject *self, PyObject *args);

#endif
