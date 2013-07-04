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

        # Ressources for the line tracer
        # Create a texture to store the lines drawing
        pattern = pyglet.image.SolidColorImagePattern((255, 255, 255, 255))
        self.tracer = pyglet.image.create(self.window.width, self.window.height, pattern)
        self.tracer_width = self.tracer.width
        # Get back the raw data from the texture, this is really heavy work
        # and should be down only when the texture is actualized
        self.tracer_data = [ 0xFF for _ in xrange(self.tracer.width * self.tracer.height)]

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
            pass

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            if button == pyglet.window.mouse.RIGHT:
                self.robot.sprite.x = x
                self.robot.sprite.y = y
            elif button == pyglet.window.mouse.LEFT:
                self.tracer.get_texture().blit_into(self.POINT, x, y, 0)
                w = max(x - self.POINT.anchor_x, 0)
                h = max(y - self.POINT.anchor_y, 0)
                w_max = min(x + self.POINT.anchor_x, self.tracer.width)
                h_max = min(y + self.POINT.anchor_y, self.tracer.height)
                for w_curr in xrange(w, w_max):
                    for h_curr in xrange(h, h_max):
                        self.tracer_data[h_curr * self.tracer.width + w_curr] = 0x00

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, button, modifiers):
            if button == pyglet.window.mouse.RIGHT:
                self.robot.sprite.x = x
                self.robot.sprite.y = y
            elif button == pyglet.window.mouse.LEFT:
                if self.POINT.anchor_x < x < self.window.width and \
                   self.POINT.anchor_y < y < self.window.height:
                    self.tracer.get_texture().blit_into(self.POINT, x, y, 0)
                    w = max(x - self.POINT.anchor_x, 0)
                    h = max(y - self.POINT.anchor_y, 0)
                    w_max = min(x + self.POINT.anchor_x, self.tracer.width)
                    h_max = min(y + self.POINT.anchor_y, self.tracer.height)
                    for w_curr in xrange(w, w_max):
                        for h_curr in xrange(h, h_max):
                            self.tracer_data[h_curr * self.tracer.width + w_curr] = 0x00

    def add(self, elm):
        """Add a new element to the world"""
        self.elements.append(elm)
