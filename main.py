#! /usr/bin/env python

from datetime import datetime

from cpu import Cpu
from robot import Robot

def main():
    cpu = Cpu()
    cpu.program.load('tests/battle.mips')
    robot = Robot(cpu.memory)

    t_old = datetime.now()
    for i in xrange(12500000):
        # cpu clock : 12.5mHz
        cpu.step()

#        robot.update(dt)
    t_current = datetime.now()
    print "should be 1s : " + str(t_current - t_old)


if __name__ == '__main__':
    main()
