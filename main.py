#! /usr/bin/env python

import pyglet
from datetime import datetime
import time

from emulator import Cpu, Memory
from robot import Robot
from world import World

# 12.5MHz CPU
CPU_FREQ = 12500000
# Synchronise rate 1000Hz
SYNCHRONISE_FREQ=1000
SYNCHONISE_STEP = 1.0 / SYNCHRONISE_FREQ
CPU_SAMPLE = int(CPU_FREQ / SYNCHRONISE_FREQ)


class Program:
    def update(self, arg):
        # Make the CPU run the number of instructions between two synchronisations
        self.cpu.step(CPU_SAMPLE)
        # Now update the robot state
        self.robot.update(SYNCHONISE_STEP)

    def start(self):
        self.cpu.load('tests/linetracer.mips')
        pyglet.clock.schedule_interval(self.update, SYNCHONISE_STEP)
        pyglet.app.run()

    def __init__(self):
        self.memory = Memory()
        self.cpu = Cpu(self.memory)
        self.robot = Robot(self.memory)
        self.world = World()
        self.world.add(self.robot)

if __name__ == '__main__':
    pg = Program()
    pg.start()
