#! /usr/bin/env python

from math import cos, sin, atan, pi, copysign
from PyQt4 import QtCore, QtGui

DEGTORAD = pi /180
RADTODEG = 1.0 / DEGTORAD

class LineSensor():
    """This module detect the black line draw on the ground
       The IO (only used as a output) from io_callback is
       composed of 7 bits representing the presence of light
       (i.e. texture's pixel is not black under the sensor)
    """
    def __init__(self, io_callback, world_map, robot):
        """io_callback : callback to get/set the IO
           world_map : image were to look for sensor input
           robot : the sensors are binded to a robot and move with it
        """
        self.robot = robot
        self.world_map = world_map
        self.io_callback = io_callback
        # Compute the position (relative to the robot) of the sensors
        self.sensors = []
        # The sensors are at the end of the robot
        l = robot.sprite.width() / 2
        sensor_space = float(robot.sprite.height()) / 7
        w = -3 * sensor_space
        for _ in xrange(7):
            sensor = {}
            sensor['angle'] = atan(w/l)
            sensor['rayon'] = l / cos(sensor['angle'])
            self.sensors.append(sensor)
            w += sensor_space

    def update(self, dt):
        """Update the sensor
        """
        output = 0x00
        # To get back the value of the pixel under each sensor
        # we have to project the local coordinates of the sensors
        # in the coordinates the robot is
        x = self.robot.pos_x
        y = self.robot.pos_y
        a = self.robot.rotation * DEGTORAD
        for i in xrange(7):
            sensor = self.sensors[i]
            b = sensor['angle'] + a
            sensor_x = x + cos(b) * sensor['rayon']
            sensor_y = y - sin(b) * sensor['rayon']
            if self.world_map.pixel(sensor_x, sensor_y) == 0xFFFFFFFF:
                output |= (1 << i)
        self.io_callback(output)


class Motor():
    """Represents a simple step by step electric motor
    """
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
    """Physical representation of the robot
    """
    # Rotation is too slow compared to straight move otherwise
    ROTATION_COEF = 4

    def __init__(self, memory, world_map, x=50, y=50):
        self.sprite = QtGui.QPixmap("ressources/car.png")
        self.memory = memory
        self.world_map = world_map
        self.pos_x = x
        self.pos_y = y
        self.half_width = self.sprite.width() / 2
        self.half_height = self.sprite.height() / 2
        self.rotation = 90
        # Motors are special builtin modules
        self.motorR = Motor(lambda : (self.memory[0x10]) & 0x0F)
        self.motorL = Motor(lambda : (self.memory[0x10] >> 4) & 0x0F)
        # Others modules are stored in a array
        self.modules = []

    # Qt image is reference according to it top left corner
    # img_* functions convert the coordinates

    def img_x(self):
        return self.pos_x - self.half_width

    def img_y(self):
        return self.pos_y - self.half_height

    def img_set_x(self, x):
        self.pos_x = x + self.half_width

    def img_set_y(self, y):
        self.pos_y = y + self.half_height


    def update(self, dt):
        """Update the robot physical state
        """
        # Update the modules
        self.motorR.update(dt)
        self.motorL.update(dt)
        for m in self.modules:
            m.update(dt)

        # Right motor is mounted backward, we have to invert it speed
        inv_R_linear_speed = -self.motorR.linear_speed
        # Get the total speed from motors' one
        # The two motors have different speed,
        # the difference of them creates a turn
        turn = float(inv_R_linear_speed) - self.motorL.linear_speed
        if inv_R_linear_speed == 0 or self.motorL.linear_speed == 0 or \
           (copysign(inv_R_linear_speed, self.motorL.linear_speed) != \
            inv_R_linear_speed):
            straight = 0
        else:
            if inv_R_linear_speed < 0:
                sign = -1
            else:
                sign = 1
            straight = sign * min(abs(inv_R_linear_speed), abs(self.motorL.linear_speed))

        # Update the robot position
        self.pos_x += straight * cos(self.rotation * DEGTORAD) * dt
        self.pos_y += -straight * sin(self.rotation * DEGTORAD) * dt
        self.rotation -= copysign(atan(turn/self.sprite.height()), turn) * RADTODEG * dt * self.ROTATION_COEF

        # Check collisions to be sure we're not out of the window
        self.pos_x = min(self.pos_x, self.world_map.width())
        self.pos_x = max(self.pos_x, 0)
        self.pos_y = min(self.pos_y, self.world_map.height())
        self.pos_y = max(self.pos_y, 0)
