#include "PyModuleUtils.h"

#ifndef _PYTINICARDEXTENSIONS_H
#define _PYTINICARDEXTENSIONS_H


PyObject* AddMemoryImplicationExtension(PyObject* self, PyObject* args);
PyObject* AddMemoryCountImplicationExtension(PyObject* self, PyObject* args);
PyObject* AddFastMemoryImplicationExtension(PyObject* self, PyObject* args);
PyObject* AddFastRangedMemoryImplicationExtension(PyObject* self, PyObject* args);
PyObject* AddFastCompactMemoryImplicationExtension(PyObject* self, PyObject* args);
PyObject* AddFastCountCompactMemoryImplicationExtension(PyObject* self, PyObject* args);
#endif
