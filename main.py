#! /usr/bin/env python

import pyglet
from datetime import datetime
import time

from emulator import Cpu, Memory
from robot import Robot
from world import World

def main():

    t_init = datetime.now()

    for _ in xrange(100000):
        t_old = datetime.now()
        for _ in xrange(125):
            # cpu clock : 12.5mHz
            cpu.step(1000)
        t_current = datetime.now()
        robot.update((t_current - t_old).total_seconds())

    print "should be 1s : " + str(datetime.now() - t_init)

if __name__ == '__main__':
    memory = Memory()
    cpu = Cpu(memory=memory, frequency=12500000)
    cpu.load('tests/linetracer.mips')
    robot = Robot(memory)

    world = World()
    world.add(robot)

    cpu.run()
    pyglet.clock.schedule_interval(robot.update, 0.01)
    pyglet.app.run()

    cpu.stop()
