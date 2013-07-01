CXX=g++
CXXFLAGS=-W -Wall -fpic -std=c++0x -pedantic
SWIG=swig
SWIGFLAGS=-c++ -python
INCLUDE=-I /usr/include/python2.7/
TARGET=_cpp_emulator.so

SRC=cpp/cpu.cpp cpp/memory.cpp
OBJ=$(SRC:.cpp=.o)
SWIG_SRC=cpp/cpp_emulator.i
SWIG_OBJ=$(SWIG_SRC:.i=_wrap.cxx)
SWIG_OBJ_PY=$(SWIG_SRC:.i=.py)


all:$(TARGET)

$(TARGET): $(OBJ) $(SWIG_OBJ)
	$(CXX) -shared $^ -o $@ $(CXXFLAGS) $(INCLUDE)

cmodule: $(OBJ)
	$(CXX) -shared $^ -o $(TARGET)

%.o:%.cpp
	$(CXX) -o $@ -c $< $(CXXFLAGS) $(INCLUDE)

%_wrap.cxx: %.i
	$(SWIG) $(SWIGFLAGS) $<
	mv $(SWIG_OBJ_PY) .

clean:
	rm -f $(OBJ)
	rm -f $(SWIG_OBJ)
	rm -f `basename $(SWIG_OBJ_PY)`
	rm -f $(TARGET)
	find . -name "*.pyc" -delete

check: all
	python emulator_test.py
