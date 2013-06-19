CYTHON=cython
CC=gcc
CFLAGS=-W -Wall -fpic -std=gnu99
INCLUDE=-I /usr/include/python2.7/

TARGET=emulator.so

SRC=cpumodule.c memorymodule.c emulatormodule.c
OBJ=$(SRC:.c=.o)

SRC_CYTHON=emulator.py
OBJ_CYTHON=$(SRC_CYTHON:.py=.c)

cmodule: $(OBJ)
	$(CC) -shared $^ -o $(TARGET)

cython: $(OBJ_CYTHON)
	$(CC) -shared $^ -o $(TARGET) $(INCLUDE) -fPIC

%.o:%.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INCLUDE)

%.c:%.py
	$(CYTHON) -o $@ $<

clean:
	rm -f $(OBJ)
	rm -f $(OBJ_CYTHON)
	rm -f $(TARGET)

check:
	python emulator_test.py

