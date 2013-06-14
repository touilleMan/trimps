#! /usr/bin/env python

from datetime import datetime

from cpu import Cpu, Memory
from robot import Robot

def main():
    memory = Memory()
    cpu = Cpu(memory)
    robot = Robot(memory)
    cpu.program.load('tests/battle.mips')

    t_old = datetime.now()
    for i in xrange(12500000):
        # cpu clock : 12.5mHz
        cpu.step()

#        robot.update(dt)
    t_current = datetime.now()
    print "should be 1s : " + str(t_current - t_old)


if __name__ == '__main__':
    main()
