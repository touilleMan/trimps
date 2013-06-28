#! /usr/bin/env python

# Check if C++ version is compiled
try:
	from cpp_emulator import Cpu, Memory

# Otherwise, load the pure python version
except ImportError:
	from cpu import Cpu
	from memory import Memory
