#! /usr/bin/env python

from math import cos, sin, atan, pi

class Motor():
    """Represents a simple step by step electric motor"""
    MAGNET_STRENGTH = 180
    WHEEL_PERIMETER=10
    def __init__(self):
        # Current magnets' state of the motor
        self.magnets = [ {'angle' : i * 90, 'state' : 0} for i in xrange(4) ]
        # Position of the rotor's head (i.e. magnet-sensitive part)
        self.rotor_angle = 0
        self.linear_speed = 0

    def getter(self):
        """Returns the state of the motor's magnets"""
        state = 0x0
        for i in xrange(len(self.magnets)):
            state |= self.magnets[i]['state'] << i
        return state

    def setter(self, state):
        """Set the motor's magnets"""
        # Copy the given magnets' state
        for i in xrange(len(self.magnets)):
            self.magnets[i]['state'] = state & (1 << i)

    def update(self):
        """Update the physical state of the motor"""
        # Compute strengths the magnets apply on the rotor
        strength = 0
        for magnet in filter(lambda m: m['state'] == 1, self.magnets):
            # Retreive the angle distance between the magnet an the rotor
            dangle = magnet['angle'] - self.rotor_angle
            if dangle > 180:
                dangle -= 180
            # The closer the magnet is, the bigger the strength
            if -1 < dangle < 1:
                strength += self.MAGNET_STRENGTH
            else:
                strength += (1 / dangle) * self.MAGNET_STRENGTH
        # To cut simple, we consider this strength is an angular speed
        # Then we can update the linear speed
        self.linear_speed = strength * self.WHEEL_PERIMETER

class Robot():
    WIDTH = 10
    LENGTH = 10
    def __init__(self, memory):
        self.memory = memory
        # Physical position
        self.x = 0
        self.y = 0
        self.angle = 0
        # Modules
        self.motorR = Motor()
        self.motorL = Motor()

        # Connect the modules' IOs in memory
        self.memory.bind(address='0x10', bitmask=0x0000FF00,
                        getter=lambda : self.motorL.getter() << 16,
                        setter=lambda val: self.motorL.setter(val >> 16))
        self.memory.bind(address='0x10', bitmask=0x000000FF,
                        getter=lambda : self.motorR.getter(),
                        setter=lambda val: self.motorR.setter(val))

    def update(self, dt):
        """Update the motor physical state"""
        # Update the modules
        self.motorR.update(dt)
        self.motorL.update(dt)

        # Get the total speed from motors' one
        # The two motors have different speed,
        # the difference of them creates a turn
        turn = self.motorR.linear_speed - self.motorL.linear_speed
        if self.motorR.linear_speed == 0 or self.motorL.linear_speed == 0 or \
           (self.motorR.linear_speed / self.motorR.linear_speed) != \
           (self.motorL.linear_speed / self.motorL.linear_speed):
           straight = 0
        else:
            sign = self.motorR.linear_speed / self.motorR.linear_speed
            straight = sign * min([abs(self.motorR.linear_speed), abs(self.motorL.linear_speed)])

        # Update the robot position
        # TODO : check colisions
        self.x = straight * cos(self.angle * pi / 180) * dt
        self.y = -straight * sin(self.angle * pi / 180) * dt
        self.angle = atan(turn / self.WIDTH) * dt

        print "x : {}, y : {}, angle : {}".format(self.x, self.y, self.angle)
