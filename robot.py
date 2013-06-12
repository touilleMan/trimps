#! /usr/bin/env python

class Motor():
    def __init__(self, robot):
        self.robot = robot
        # Eache magnet is connected in the memory with an IO
        self.io = [ { 'address' : 0x10, 'mask' : 0x1 }, { 'address' : 0x10, 'mask' : 0x2 },  { 'address' : 0x10, 'mask' : 0x4 }, { 'address' : 0x10, 'mask' : 0x8 } ]
        # Current magnets' state of the motor
        self.m = [ 0 for _ in xrange(4) ]

    def update(self):
        # Get back state of each magnet
        for i in len(self.m):
            mem = self.robot.memory[self.io[i]['address']]
            self.m[i] = mem & self.io[i]['mask']
            # Todo : finish this !


class Robot():
    def __init__(self, memory):
        self.memory = memory
        self.motor1 = Motor(self)
        self.motor2 = Motor(self)

    def update(self):
        pass
