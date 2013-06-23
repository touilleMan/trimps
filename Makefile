.PHONY: emulator

all: emulator

emulator:
	cd emulator && make

clean:
	cd emulator && make clean
	find . -name "*.pyc" -delete

check: all
	cd emulator && make check
