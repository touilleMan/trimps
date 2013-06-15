#! /usr/bin/env python

from datetime import datetime
import time

import emulator
#from robot import Robot

def pmodule():
    memory = emulator.Memory()
    cpu = emulator.Cpu(memory)
#    robot = Robot(memory)
    cpu.load('tests/battle.mips')
    for _ in xrange(12500000):
        # cpu clock : 12.5mHz
        cpu.step()


def cmodule():
    emulator.program_load('tests/battle.mips')
    emulator.cpu_run(12500000)
    time.sleep(1)
    emulator.cpu_stop()

def main():
    t_old = datetime.now()
    pmodule()
#    cmodule()
    t_current = datetime.now()
    print "should be 1s : " + str(t_current - t_old)



if __name__ == '__main__':
    main()
