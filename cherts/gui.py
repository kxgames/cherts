#!/usr/bin/env python3

import kxg
import pyglet

class Gui:

    def __init__(self):
        self.window = pyglet.window.Window()
        self.window.set_visible(True)
        self.batch = pyglet.graphics.Batch()

    def on_refresh_gui(self):
        self.window.clear()
        self.batch.draw()


class GuiActor (kxg.Actor):

    def __init__(self):
        super().__init__()

    def on_setup_gui(self, gui):
        self.gui = gui
        self.gui.window.set_handlers(self)

    def on_draw(self):
        self.gui.on_refresh_gui()


