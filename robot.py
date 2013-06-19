#! /usr/bin/env python

from math import cos, sin, atan, pi
import emulator
import pyglet

class Motor():
    """Represents a simple step by step electric motor"""
    MAGNET_STRENGTH = 180
    WHEEL_PERIMETER=1

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

    def synchronise(self, io_byte):
        """Synchronise the magnets state according to the given IO"""
        # io_byte store the magnets state with it first 4 bits
        for i in xrange(len(self.magnets)):
            self.magnets[i]['state'] = (io_byte >> i) & 0x1
        # Return the same io given we are only a input
        return io_byte

    def update(self, dt):
        """Update the physical state of the motor
        """
        # Compute strengths the magnets apply on the rotor
        strength = 0
        # Only the activated magnets apply force on the rotor
        for magnet in [ m for m in self.magnets if m['state'] == 1 ]:
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
        # Then we can update the rotor position and the linear speed
        self.rotor_angle += strength * dt
        self.linear_speed = strength * self.WHEEL_PERIMETER

class Robot():
    """Physical representation of the robot"""
    IMAGE = pyglet.image.load("ressources/car.png")
    IMAGE.anchor_x = IMAGE.width / 2
    IMAGE.anchor_y = IMAGE.height / 2

    def __init__(self, memory, x=50, y=50):
        self.memory = memory
        # Modules
        self.motorR = Motor()
        self.motorL = Motor()
        self.sprite = pyglet.sprite.Sprite(self.IMAGE, x, y)

        # Connect the modules' IOs in memory
        self.memory.bind(address=0x10, bitmask=0xF0,
            callback=lambda x: self.motorL.synchronise((x>>4)) << 4)
        self.memory.bind(address=0x10, bitmask=0x0F,
            callback=self.motorR.synchronise)

    def update(self, dt):
        """Update the motor physical state"""
        # First, synchronise with the real memory
        self.memory.synchronise()

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
        self.sprite.x += straight * cos(self.sprite.rotation * pi / 180) * dt
        self.sprite.y += -straight * sin(self.sprite.rotation * pi / 180) * dt
        self.sprite.rotation += atan(turn / self.sprite.width) * dt

    def draw(self):
        """Display on screen the robot"""
        self.sprite.draw()

