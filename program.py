#! /usr/bin/env python

from emulator import Cpu, Memory
from robot import Robot, LineSensor

class Program:
    """Represent a running simulation
    """
    # Synchronise rate 1000Hz
    PROGRAM = "tests/linetracer.mips"
    # 12.5MHz CPU
    CPU_FREQ = 12500000
    SYNCHRONISE_FREQ=1000

    def __init__(self, world_map, program=PROGRAM, cpu_freq=CPU_FREQ, synchronise_freq=SYNCHRONISE_FREQ):
        self.synchronise_step = 1.0 / synchronise_freq
        self.cpu_sample = int(cpu_freq / synchronise_freq)
        memory = Memory()
        self.cpu = Cpu(memory)
        self.cpu.load(program)
        self.robot = Robot(memory, world_map)
        # Attach the robot's modules
        line_sensor = LineSensor(lambda out: memory.set_byte(0x21, out), world_map, self.robot)
        self.robot.modules.append(line_sensor)

    def update(self):
        # Make the CPU run the number of instructions between two synchronisations
        self.cpu.step(self.cpu_sample)
        # Now update the robot state
        self.robot.update(self.synchronise_step)
