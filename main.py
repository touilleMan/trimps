#! /usr/bin/env python

from datetime import datetime
import time

from cpu import Cpu, Memory
import emulator
from robot import Robot

def main():
    memory = Memory()
    cpu = Cpu(memory)
    robot = Robot(memory)
    cpu.program.load('tests/battle.mips')

    emulator.program_load('tests/battle.mips')
    t_old = datetime.now()
    emulator.cpu_run(12500000)
    time.sleep(1)
    emulator.cpu_stop()
#    for _ in xrange(12500000):
        # cpu clock : 12.5mHz
#        cpu.step()
#        emulator.cpu_step()

#        robot.update(dt)
    t_current = datetime.now()
    print "should be 1s : " + str(t_current - t_old)


if __name__ == '__main__':
    main()
