CC=gcc
CFLAGS=-W -Wall -g -fpic
INCLUDE=-I /usr/include/python2.7/
SRC=emulator.c
OBJ=$(SRC:.c=.o)
TARGET=emulator.so

all: $(TARGET)

$(TARGET): $(OBJ)
	@$(CC) -shared $^ -o $@

%.o:%.c
	$(CC) -o $@ -c $< $(CFLAGS) $(INCLUDE)

clean:
	rm $(OBJ)
	rm $(TARGET)
