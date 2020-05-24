#!/usr/bin/env python3

import os.path as os_path
import kxg
import pyglet

from vecrec import Vector

pyglet.resource.path = [
        os_path.join(os_path.dirname(__file__), '..', 'resources'),
        ]

class Gui:
#    - Needs Piece type, positions, possible/legal/current moves, 
#      possible/legal/current patterns, pattern consequences
#    - Highlights available moves, patterns, etc.
#    - Display extra info on patterns

    def __init__(self):
        self.window_shape = Vector(800, 600)

        self.window = pyglet.window.Window()
        self.window.set_size(*self.window_shape)
        self.window.set_visible(True)
        self.window.set_caption("Cherts")
        #self.window.set_icon(
        #        pyglet.resource.image('icon_16.png'),
        #        pyglet.resource.image('icon_32.png'),
        #        pyglet.resource.image('icon_64.png'),
        #)

        self.batch = pyglet.graphics.Batch()

        self.images = {
                'piece_kdt': pyglet.resource.image('piece_kdt45.png'),
                'piece_klt': pyglet.resource.image('piece_klt45.png'),
                'piece_qdt': pyglet.resource.image('piece_qdt45.png'),
                'piece_qlt': pyglet.resource.image('piece_qlt45.png'),
                'piece_rdt': pyglet.resource.image('piece_rdt45.png'),
                'piece_rlt': pyglet.resource.image('piece_rlt45.png'),
                'piece_bdt': pyglet.resource.image('piece_bdt45.png'),
                'piece_blt': pyglet.resource.image('piece_blt45.png'),
                'piece_ndt': pyglet.resource.image('piece_ndt45.png'),
                'piece_nlt': pyglet.resource.image('piece_nlt45.png'),
                'piece_pdt': pyglet.resource.image('piece_pdt45.png'),
                'piece_plt': pyglet.resource.image('piece_plt45.png'),
                }

        # The three letter codes are [type][color][background]
        self.piece_codes = {
                'king'   : 'k',
                'queen'  : 'q',
                'rook'   : 'r',
                'bishop' : 'b',
                'knight' : 'n',
                'pawn'   : 'p',
            
                'black'  : 'd',
                'white'  : 'l',
             
                # t = transparent background
            }


        for image in self.images.values():
            image.anchor_x = image.width / 2
            image.anchor_y = image.height / 2

    def on_refresh_gui(self):
        self.window.clear()
        self.batch.draw()



class GuiActor (kxg.Actor):

    def __init__(self):
        super().__init__()

        self.player = None


    def on_setup_gui(self, gui):
        self.gui = gui
        self.gui.window.set_handlers(self)

    def on_start_game(self, num_players):
        # Make players here or in SetupGame message?
        #self.player = tokens.Player()
        #self >> messages.CreatePlayer(self.player)
        pass

    def on_draw(self):
        self.gui.on_refresh_gui()


    # User input events
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            # Left click to select pieces
            pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass


class DummyPieceExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        self.sprite = pyglet.sprite.Sprite(
                self.actor.gui.images[self.get_image()],
                x=self.token.position[0],
                y=self.token.position[1],
                batch=self.actor.gui.batch,
                group=pyglet.graphics.OrderedGroup(1),
        )

    def get_image(self):
        pc = self.actor.gui.piece_codes
        type = self.token.type
        color = 'white' # Hard code it for now...

        image_name = f"piece_{pc[type]}{pc[color]}t"
        return image_name

    @kxg.watch_token
    def on_update_game(self, delta_t):
        self.sprite.position = self.token.position

    @kxg.watch_token
    def on_remove_from_world(self):
        self.sprite.delete()
