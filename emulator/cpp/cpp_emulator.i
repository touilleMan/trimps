%module cpp_emulator

%include "carrays.i"
%include "std_vector.i"
%include "cdata.i"
%include "exception.i"

namespace std {
   %template(vectorui) vector<unsigned int>;
};

%exception {
  try {
    $action
  } catch (const std::exception& e) {
    SWIG_exception(SWIG_RuntimeError, e.what());
  }
}

%{
#include "memory.hpp"
#include "cpu.hpp"
%}

%include "memory.hpp"
%include "cpu.hpp"
