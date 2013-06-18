#! /usr/bin/env python

import pyglet

class World():
    """Physical world the robot evoluate in"""
    def __init__(self):
        self.elements = []
        self.window = pyglet.window.Window()
        # Set a white background
        pyglet.gl.glClearColor(1,1,1,0)

        @self.window.event
        def on_draw():
            self.window.clear()
            for e in self.elements:
                e.draw()

    def add(self, elm):
        """Add a new element to the world"""
        self.elements.append(elm)
