#! /usr/bin/env python

from emulator import Cpu
from datetime import datetime

import sys
import cProfile

DEFAULT_FREQUENCY = 12500000

if __name__ == '__main__':
    count = DEFAULT_FREQUENCY
    datetime.now()
    cpu = Cpu()
    cpu.load("tests/battle.mips")

    print "\t*** BENCHMARK ***"
    print "Executing {} instructions @ {}MHz".format(count, float(count) / 1000000)
    print "Should take 1s on real MIPS CPU"
    tstart = datetime.now()

    # while True:
    #     sys.stdin.readline()
    #     cpu.step()
    #     print cpu
    cProfile.run("cpu.step(count)")

    dt = (datetime.now() - tstart).total_seconds()
    print "Took {}".format(dt)
