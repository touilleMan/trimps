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

<<<<<<< HEAD
#    while True:
#        sys.stdin.readline()
#        cpu.step()
#        print cpu
    cpu.step(count)
#    cProfile.run("cpu.step(count)")
=======
    # while True:
    #     sys.stdin.readline()
    #     cpu.step()
    #     print cpu
    cProfile.run("cpu.step(count)")
>>>>>>> a79b6a6df7737004a71567071c593a8450ffe2f9

    dt = (datetime.now() - tstart).total_seconds()
    print "Took {}".format(dt)
