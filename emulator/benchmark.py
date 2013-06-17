#! /usr/bin/env python

from Emulator import Cpu

if __name__ == '__main__':
    count = DEFAULT_FREQUENCY
    datetime.now()
    cpu = Cpu()
    cpu.load("../tests/battle.mips")

    print "\t*** BENCHMARK ***"
    print "Executing {} instructions".format(count)
    print "Should take 1s on real MIPS CPU"
    tstart = datetime.now()
    cpu.step(count)
    dt = (datetime.now() - tstart).total_seconds()
    print "Took {}".format(dt)
