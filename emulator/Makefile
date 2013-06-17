CYTHON=cython
CC=gcc
CFLAGS=-W -Wall -fpic -std=gnu99
INCLUDE=-I /usr/include/python2.7/
SRC=cpu.py
OBJ=$(SRC:.py=.o)
TARGET=cpu.so

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) -shared $^ -o $@

%.o:%.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INCLUDE)

%.c:%.py
	$(CYTHON) -o $@ $<

clean:
	rm -f $(OBJ)
	rm -f $(SRC_C)
	rm -f $(TARGET)
