CXX=g++
CXXFLAGS=-W -Wall -fpic -std=c++0x -pedantic
SWIG=swig
SWIGFLAGS=-c++ -python
INCLUDE=-I /usr/include/python2.7/
TARGET=_emulator.so

SRC=memory.cpp
OBJ=$(SRC:.cpp=.o)
SWIG_SRC=emulator.i
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

clean:
	rm -f $(OBJ)
	rm -f $(SWIG_OBJ)
	rm -f $(SWIG_OBJ_PY)
	rm -f $(TARGET)
