
#include <Python.h>

#include "cpumodule.h"
#include "memorymodule.h"

static PyMethodDef noddy_methods[] = {
	emulator_CpuType,
	emulator_MemoryType,
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initemulator(void)
{
    PyObject* m;

    emulator_MemoryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&emulator_MemoryType) < 0)
        return;

    emulator_CpuType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&emulator_CpuType) < 0)
        return;

    m = Py_InitModule3("emulator", emulator_methods,
                       "Example module that creates an extension type.");

    Py_INCREF(&emulator_MemoryType);
    PyModule_AddObject(m, "Memory", (PyObject *)&emulator_MemoryType);
}
