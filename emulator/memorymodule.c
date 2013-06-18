#include <Python.h>

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
} emulator_MemoryObject;

static PyTypeObject emulator_MemoryType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "emulator.Memory",             /*tp_name*/
    sizeof(emulator_MemoryObject), /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Memory objects",           /* tp_doc */
};

static PyMethodDef emulator_methods[] = {
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

    m = Py_InitModule3("emulator", emulator_methods,
                       "Example module that creates an extension type.");

    Py_INCREF(&emulator_MemoryType);
    PyModule_AddObject(m, "Memory", (PyObject *)&emulator_MemoryType);
}
