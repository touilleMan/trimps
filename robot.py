#! /usr/bin/env python

from math import cos, sin, atan, pi, tan, copysign
import pyglet

DEGTORAD = pi /180
RADTODEG = 1.0 / DEGTORAD

class LineSensor():
    """This module detect the black line draw on the ground
       The IO (only used as a output) from io_callback is
       composed of 7 bits representing the presence of light
       (i.e. texture's pixel is not black under the sensor)
    """
    POINT = { 0xFF : pyglet.image.create(1, 1, pyglet.image.SolidColorImagePattern((255, 0, 0, 255))), \
    0x00 : pyglet.image.create(1, 1, pyglet.image.SolidColorImagePattern((0, 255, 0, 255))) }

    def __init__(self, io_callback, world, robot):
        """io_callback : callback to get/set the IO
           world : World class the sensors evolutes in
           robot : the sensors are binded to a robot and move with it
        """
        self.robot = robot
        self.world = world
        self.io_callback = io_callback
        # Compute the position (relative to the robot) of the sensors
        self.sensors = []
        # The sensors are at the end of the robot
        l = robot.sprite.width / 2
        sensor_space = float(robot.sprite.height) / 7
        w = -3 * sensor_space
        for _ in xrange(7):
            sensor = {}
            sensor['angle'] = atan(w/l)
            sensor['rayon'] = l / cos(sensor['angle'])
            self.sensors.append(sensor)
            w += sensor_space

    def update(self, dt):
        output = 0x00
        # To get back the value of the pixel under each sensor
        # we have to project the local coordinates of the sensors
        # in the coordinates the robot is
        x = self.robot.sprite.x
        y = self.robot.sprite.y
        a = self.robot.sprite.rotation * DEGTORAD
        for i in xrange(7):
            sensor = self.sensors[i]
            b = sensor['angle'] + a
            sensor_x = x + self.world.MARGIN + cos(b) * sensor['rayon']
            sensor_y = y + self.world.MARGIN - sin(b) * sensor['rayon']
            pixel = self.world.tracer_data[int(sensor_x) + self.world.tracer_width * int(sensor_y)]
            if pixel == 0xFF:
                output |= (1 << i)
            # Show where the sensor is if requested
            if self.robot.world.linesensor_printer:
                self.world.tracer.get_texture().blit_into(self.POINT[pixel], int(sensor_x), int(sensor_y), 0)
        self.io_callback(output)


class Motor():
    """Represents a simple step by step electric motor"""
    SPEED_COEF=3
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
    # Rotation is too slow compared to straight move otherwise
    ROTATION_COEF = 4

    def __init__(self, memory, world, x=50, y=50):
        self.memory = memory
        self.world = world
        self.sprite = pyglet.sprite.Sprite(self.IMAGE, x, y)
        # Motors are special builtin modules
        self.motorR = Motor(lambda : (self.memory[0x10]) & 0x0F)
        self.motorL = Motor(lambda : (self.memory[0x10] >> 4) & 0x0F)
        self.labelR = pyglet.text.Label('Right speed : 0', x=400, y=30, color=(0, 0, 0, 255))
        self.labelL = pyglet.text.Label('Left speed : 0', x=400, y=50, color=(0, 0, 0, 255))
        # Others modules are stored in a array
        self.modules = []

    def update(self, dt):
        """Update the robot physical state"""
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
        self.sprite.x += straight * cos(self.sprite.rotation * DEGTORAD) * dt
        self.sprite.y += -straight * sin(self.sprite.rotation * DEGTORAD) * dt
        self.sprite.rotation -= copysign(atan(turn/self.sprite.height), turn) * RADTODEG * dt * self.ROTATION_COEF
        self.labelR.text = 'Right speed : {}, x : {}'.format(inv_R_linear_speed, self.sprite.x)
        self.labelL.text = 'Left speed : {}, y : {}'.format(self.motorL.linear_speed, self.sprite.y)

        # Check collisions to be sure we're not out of the window
        self.sprite.x = min(self.sprite.x, self.world.window.width)
        self.sprite.x = max(self.sprite.x, 0)
        self.sprite.y = min(self.sprite.y, self.world.window.height)
        self.sprite.y = max(self.sprite.y, 0)

    def draw(self):
        """Display on screen the robot"""
        self.sprite.draw()
        self.labelR.draw()
        self.labelL.draw()
