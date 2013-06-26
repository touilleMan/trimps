#! /usr/bin/env python

import pyglet

class Camera(object):
    MAX_ZOOM=3
    MIN_ZOOM=0.8
    def __init__(self, win, zoom=1.0):
        self.win = win
        self.zoom = zoom

    def worldProjection(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        widthRatio = self.win.width / self.win.height
        pyglet.gl.gluOrtho2D(
            -self.zoom * widthRatio,
            self.zoom * widthRatio,
            -self.zoom,
            self.zoom)

    def hudProjection(self):
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.gluOrtho2D(0, self.win.width, 0, self.win.height)


class World():
    """Physical world the robot evoluates in"""
    POINT=pyglet.image.create(10, 10,
        pyglet.image.SolidColorImagePattern((0, 0, 0, 255)))
    POINT.anchor_x = POINT.width / 2
    POINT.anchor_y = POINT.height / 2

    def __init__(self):
        self.elements = []
        self.window = pyglet.window.Window()
        # Set a white background
        pyglet.gl.glClearColor(1,1,1,1)
        pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 0))
        self.tracer = pyglet.image.create(self.window.width, self.window.height, pattern)
        self.camera = Camera(self.window)
        self.robot = None

        @self.window.event
        def on_draw():
            self.window.clear()
            self.tracer.blit(0, 0)
#            self.camera.hudProjection()
            for e in self.elements:
                e.draw()

        @self.window.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            self.camera.zoom += scroll_y * 0.1
            if self.camera.zoom > self.camera.MAX_ZOOM:
                self.camera.zoom = self.camera.MAX_ZOOM
            elif self.camera.zoom < self.camera.MIN_ZOOM:
                self.camera.zoom = self.camera.MIN_ZOOM

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            if button == pyglet.window.mouse.RIGHT:
                self.robot.sprite.x = x
                self.robot.sprite.y = y
            elif button == pyglet.window.mouse.LEFT:
                self.tracer.blit_into(self.POINT, x, y, 0)

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            if button == pyglet.window.mouse.RIGHT:
                self.robot.sprite.x = x
                self.robot.sprite.y = y
            elif button == pyglet.window.mouse.LEFT:
                self.tracer.blit_into(self.POINT, x, y, 0)

    def add(self, elm):
        """Add a new element to the world"""
        self.elements.append(elm)
