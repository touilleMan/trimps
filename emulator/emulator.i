%module emulator

%include "carrays.i"
%include "std_vector.i"
%include "cdata.i"

namespace std {
   %template(vectorui) vector<unsigned int>;
};

%{
#include "memory.hpp"
#include "cpu.hpp"
%}

%include "memory.hpp"
%include "cpu.hpp"

