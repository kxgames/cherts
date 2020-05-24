#!/usr/bin/env python3

import kxg
import pyglet

from .actors import BaseActor


class Gui:
#    - Needs Piece type, positions, possible/legal/current moves, 
#      possible/legal/current patterns, pattern consequences
#    - Highlights available moves, patterns, etc.
#    - Display extra info on patterns


    def __init__(self):
        self.window = pyglet.window.Window()
        self.window.set_visible(True)
        self.batch = pyglet.graphics.Batch()

    def on_refresh_gui(self):
        self.window.clear()
        self.batch.draw()


class GuiActor (BaseActor):

    def __init__(self):
        super().__init__()

    def on_setup_gui(self, gui):
        self.gui = gui
        self.gui.window.set_handlers(self)

    def on_draw(self):
        self.gui.on_refresh_gui()


