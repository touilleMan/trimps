#! /usr/bin/env python

# Check if emulator compiled version is disponible
try:
	with open("emulator.so"):
		pass
	from emulator import Cpu, Memory

# Otherwise, load the pure python version
except IOError:
	from cpu import Cpu
	from memory import Memory
