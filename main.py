#! /usr/bin/env python

from cpu import Cpu
from robot import Robot


def main():
    cpu = Cpu()
    cpu.program.load('tests/battle.mips')
    robot = Robot(cpu.memory)

    while True:
        cpu.step()
        robot.update()

if __name__ == '__main__':
    main()
