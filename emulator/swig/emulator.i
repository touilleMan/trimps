%module emulator

%include "carrays.i"
%array_class(unsigned int, intArray);

%{
#include "memory.hpp"
#include "cpu.hpp"
%}

%include "memory.hpp"
%include "cpu.hpp"
