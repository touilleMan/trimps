#! /usr/bin/env python

import pyglet


class World():
    """Physical world the robot evoluate in"""
    POINT=pyglet.image.create(10, 10,
        pyglet.image.SolidColorImagePattern((0, 0, 0, 255)))
    POINT.anchor_x = POINT.width / 2
    POINT.anchor_y = POINT.height / 2

    def __init__(self):
        self.elements = []
        self.window = pyglet.window.Window()
        # Create a texture for the linetracer
        pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
        self.tracer = pyglet.image.create(self.window.width, self.window.height, pattern)
        # Set a white background
        pyglet.gl.glClearColor(1,1,1,0)
        self.robot = None
        self.fps_display = pyglet.clock.ClockDisplay()

        @self.window.event
        def on_draw():
            self.window.clear()
            self.tracer.blit(0, 0)
            self.fps_display.draw()
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
                pattern = pyglet.image.SolidColorImagePattern((0, 0, 255, 255))
                self.tracer.get_texture().blit_into(self.POINT, x, y, 0)

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            if button == pyglet.window.mouse.RIGHT:
                self.robot.sprite.x = x
                self.robot.sprite.y = y
            elif button == pyglet.window.mouse.LEFT:
                if self.POINT.anchor_x < x < self.window.width and \
                   self.POINT.anchor_y < y < self.window.height:
                    self.tracer.get_texture().blit_into(self.POINT, x, y, 0)

    def add(self, elm):
        """Add a new element to the world"""
        self.elements.append(elm)
