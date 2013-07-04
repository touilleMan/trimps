#! /usr/bin/env python

from math import cos, sin, atan, pi
import pyglet
import sys

class LineSensor():
    """This module detect the black line draw on the ground
       The IO (only used as a output) from io_callback is
       composed of 7 bits representing the presence of light
       (i.e. texture's pixel is not black under the sensor)
    """
    SENSORS_WIDTH = 5
    SENSORS_SPACE = 10

    def __init__(self, io_callback, world):
        """io_callback : callback to get/set the IO
           world : World class the sensors evoluate in
        """
        self.world = world
        self.io_callback = io_callback
        self.sensors = 0

    def update(self, dt, robot):
        # Get back the value of the pixel under the current sensor
        if self.world.tracer_data[int(robot.sprite.x) + self.world.tracer_width * int(robot.sprite.y)] == '\xff':
            self.sensors = 0xFF
        else:
            self.sensors = 0x00
        self.io_callback(self.sensors)


class Motor():
    """Represents a simple step by step electric motor"""
    MAGNET_STRENGTH = 180
    SPEED_COEF=1
    FREQUENCY_MAX=600
    FREQUENCY_MIN=50
    TIMECAP_MAX=1/FREQUENCY_MIN
    TIMECAP_MIN=1/FREQUENCY_MAX

    def __init__(self, io_callback):
        """io_callback is the function used to get/set the IO data from the memory
        """
        self.io_callback = io_callback
        # Current magnets' state of the motor
        self.magnets = [ 0, 0, 0, 0 ]
        # Linear speed of the motor
        self.linear_speed = 0
        # Time elapsed from the last magnets change
        self.lastchange = 0
        # Time the motor can keep the current speed
        self.timecap = 0

    def update(self, dt):
        """Update the physical state of the motor
        """
        # First we have to get back the current state from the IO
        io_byte = self.io_callback()
        magnets = [ (io_byte >> i) & 0x1 for i in xrange(4)]

        self.lastchange += dt
        # Now see if the magnets moved or not
        if magnets != self.magnets:
            frequency = 1 / self.lastchange

            # Verify the magnet change is valid to make the motor move
            if len([ m for m in magnets if m == 1 ]) == 1 and \
               len([ m for m in self.magnets if m == 1 ]) == 1 and \
               self.FREQUENCY_MIN < frequency < self.FREQUENCY_MAX:
                # Does the motor goes backward or not ?
                for i in [ j for j in xrange(4) if self.magnets[j] == 1 ]:
                    if magnets[(i + 1) % 4] == 1:
                        self.linear_speed = - frequency * self.SPEED_COEF
                    elif magnets[(i - 1) % 4] == 1:
                        self.linear_speed = frequency * self.SPEED_COEF  
                    else:
                        # The previous and current magnets are not contiguous,
                        # the configuration is invalid
                        self.linear_speed = 0
                self.timecap = self.lastchange
            else:
                # Bad magnet configuration, no move is possible
                self.timecap = 0
            # Finally, update the magnets state
            self.magnets = magnets
            self.lastchange = 0
        else:
            # Magnets state didn't change, check if the motor
            # still has speed
            if self.lastchange > self.timecap:
                # It's been too long since the motor has been updated
                self.linear_speed = 0


class Robot():
    """Physical representation of the robot"""
    IMAGE = pyglet.image.load("ressources/car.png")
    IMAGE.anchor_x = IMAGE.width / 2
    IMAGE.anchor_y = IMAGE.height / 2

    def __init__(self, memory, x=50, y=50):
        self.memory = memory
        self.sprite = pyglet.sprite.Sprite(self.IMAGE, x, y)
        # Motors are special builtin modules
        self.motorR = Motor(lambda : (self.memory[0x10] >> 4) & 0x0F)
        self.motorL = Motor(lambda : self.memory[0x10] & 0x0F)
        self.labelR = pyglet.text.Label('Right speed : 0', x=400, y=30, color=(0, 0, 0, 255))
        self.labelL = pyglet.text.Label('Left speed : 0', x=400, y=50, color=(0, 0, 0, 255))
        self.labelSensors = pyglet.text.Label('sensors : 0', x=400, y=70, color=(0, 0, 0, 255))
        # Others modules are stored in a array
        self.modules = []

    def update(self, dt):
        """Update the robot physical state"""
        # Update the modules
        self.motorR.update(dt)
        self.motorL.update(dt)
        for m in self.modules:
            m.update(dt, self)

        # Left motor is mounted backward, we have to invert it speed
        inv_L_linear_speed = -self.motorL.linear_speed
        # Get the total speed from motors' one
        # The two motors have different speed,
        # the difference of them creates a turn
        turn = self.motorR.linear_speed - inv_L_linear_speed
        if self.motorR.linear_speed == 0 or inv_L_linear_speed == 0 or \
           (self.motorR.linear_speed / self.motorR.linear_speed) != \
           (inv_L_linear_speed / inv_L_linear_speed):
            straight = 0
        else:
            sign = self.motorR.linear_speed / inv_L_linear_speed
            straight = sign * min([abs(self.motorR.linear_speed), abs(inv_L_linear_speed)])

        # Update the robot position
        # TODO : check colisions
        self.sprite.x += straight * cos(self.sprite.rotation * pi / 180) * dt
        self.sprite.y += -straight * sin(self.sprite.rotation * pi / 180) * dt
        self.sprite.rotation += atan(turn / self.sprite.width) * dt
        self.labelR.text = 'Right speed : {}, x : {}'.format(self.motorR.linear_speed, self.sprite.x)
        self.labelL.text = 'Left speed : {}, y : {}'.format(inv_L_linear_speed, self.sprite.y)
        self.labelSensors.text = 'sensors : {}'.format(self.modules[0].sensors)

    def draw(self):
        """Display on screen the robot"""
        self.sprite.draw()
        self.labelR.draw()
        self.labelL.draw()
        self.labelSensors.draw()
