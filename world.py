#! /usr/bin/env python

import pyglet

class World():
    def __init__(self):
        self.elements = []
        self.window = pyglet.window.Window()

        @self.window.event
        def on_draw():
            self.window.clear()
            for e in self.elements:
                e.draw()

    def add(self, elm):
        """Add a new element to the world"""
        self.elements.append(elm)
