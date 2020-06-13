#!/usr/bin/env python3

import os.path as os_path
import kxg
import pyglet
from pyglet.gl import *
from nonstdlib import log, debug, info, warning, error, critical
from more_itertools import flatten, pairwise

from vecrec import Vector, accept_anything_as_vector
from .actors import BaseActor
from .messages import SetupWorld

pyglet.resource.path = [
        os_path.join(os_path.dirname(__file__), '..', 'resources'),
        ]

class Gui:
#    - Needs Piece type, positions, possible/legal/current moves, 
#      possible/legal/current patterns, pattern consequences
#    - Highlights available moves, patterns, etc.
#    - Display extra info on patterns

    def __init__(self):
        self.bg_color = (0.75, 0.75, 0.75, 1.0)
        self.window_shape = Vector(400, 400)

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

        self.load_images()

    def load_images(self):
        """
        Load the piece images and set the piece codes
        """

        pri = pyglet.resource.image # function handle
        self.images = {
                # Pieces
                'piece_kdt': pri('piece_kdt45.png'),
                'piece_klt': pri('piece_klt45.png'),
                'piece_qdt': pri('piece_qdt45.png'),
                'piece_qlt': pri('piece_qlt45.png'),
                'piece_rdt': pri('piece_rdt45.png'),
                'piece_rlt': pri('piece_rlt45.png'),
                'piece_bdt': pri('piece_bdt45.png'),
                'piece_blt': pri('piece_blt45.png'),
                'piece_ndt': pri('piece_ndt45.png'),
                'piece_nlt': pri('piece_nlt45.png'),
                'piece_pdt': pri('piece_pdt45.png'),
                'piece_plt': pri('piece_plt45.png'),

                # User interface
                'selected_circle': pri('selected_circle.png'),
                'unselected_circle': pri('unselected_circle.png'),
                }

        # The three letter codes are [type][color][background]
        self.piece_file_codes = {
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

        # Center images
        for image in self.images.values():
            image.anchor_x = image.width / 2
            image.anchor_y = image.height / 2

    def on_refresh_gui(self):
        pyglet.gl.glClearColor(*self.bg_color)
        self.window.clear()
        self.batch.draw()


class GuiActor(BaseActor):

    def __init__(self):
        super().__init__()
        self.player = None
        self.selection = None

    def on_setup_gui(self, gui):
        self.gui = gui
        self.gui.window.set_handlers(self)

    def on_draw(self):
        self.gui.on_refresh_gui()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            pass

    def on_mouse_press(self, xg, yg, button, modifiers):
        # Left click to select pieces:
        if button == 1:
            xyw = self.xyw_from_xyg((xg, yg))
            piece = self.world.find_piece(xyw)
            self.select(piece)

        # Right click to direct pieces:
        elif button == 2:
            pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def select(self, piece):
        """
        Select the given piece.

        The given piece can be None, in which case the selection is cleared.
        """
        if piece is self.selection:
            return

        self.deselect()
        self.selection = piece

        if self.selection:
            self.selection.get_extension(self).on_select()

    def deselect(self):
        """
        Clear the piece selection.

        This method can safely be called even if no piece is selected.
        """
        if self.selection:
            self.selection.get_extension(self).on_deselect()
            self.selection = None

    @accept_anything_as_vector
    def xyg_from_xyw(self, xyw):
        # Convert to player coordinates to make sure our pieces are always 
        # facing forward.
        xyp = self.player.xyp_from_xyw(xyw)
        xyp_margin = (0.5, 0.5)
        return (xyp + xyp_margin) * self.px_per_tile
        
    @accept_anything_as_vector
    def xyw_from_xyg(self, xyg):
        xyp_margin = (0.5, 0.5)
        xyp = (xyg / self.px_per_tile) - xyp_margin
        return self.player.xyw_from_xyp(xyp)

    @property
    def px_per_tile(self):
        return self.gui.window_shape.y / self.world.board.height




class BoardExtension(kxg.TokenExtension):

    @kxg.subscribe_to_message(SetupWorld)
    def on_setup_world(self, message):
        # Normally this kind of setup would happen in `on_add_to_world()`, but 
        # we can't do that here because:
        # 
        # - The board is added to the world before the players.
        # - The `xyg_from_xyw()` function needs to know what player we are.
        # 
        # We can do this setup after the SetupWorld event, because the actor 
        # creates the player earlier in the handling of that same event.

        w, h = self.token.size
        d = 0.5
        xyg_from_xyw = self.actor.xyg_from_xyw

        h_lines = [
                [xyg_from_xyw(-0.5, y-0.5), xyg_from_xyw(w+0.5, y-0.5)]
                for y in range(h+1)
        ]
        v_lines = [
                [xyg_from_xyw(x-0.5, -0.5), xyg_from_xyw(x-0.5, h+0.5)]
                for x in range(w+1)
        ]
        xygs = sum(h_lines + v_lines, [])

        n = len(xygs)
        v2f = sum((x.tuple for x in xygs), ())
        c3B = n * [0, 0, 0]

        self.border = self.actor.gui.batch.add(
                n, GL_LINES, None,
                ('v2f', v2f),
                ('c3B', c3B),
        )

    @kxg.watch_token
    def on_remove_from_world(self):
        self.border.delete()


class PieceExtension(kxg.TokenExtension):

    def get_image_key(self):
        pc = self.actor.gui.piece_file_codes
        type = self.token.type.name
        color = self.token.player.color

        image_key = f"piece_{pc[type]}{pc[color]}t"
        return image_key

    @kxg.watch_token
    def on_add_to_world(self, world):

        # Make sprites
        self.icon_sprite = self._new_sprite(self.get_image_key(), 1)
        self.selected_sprite = self._new_sprite('selected_circle', 0)
        self.selected_sprite.visible = False
        self.unselected_sprite = self._new_sprite('unselected_circle', 0)

        self.sprites = [
                self.icon_sprite,
                self.selected_sprite,
                self.unselected_sprite,
        ]

        self.move_lines = []

        # Rescale the sprite image to match the piece radius
        icon_w = self.icon_sprite.width
        icon_h = self.icon_sprite.height
        icon_r = (icon_w**2 + icon_h**2)**0.5 / 2

        selected_w = self.selected_sprite.width
        selected_h = self.selected_sprite.height
        selected_r = (selected_w**2 + selected_h**2)**0.5 / 2

        piece_r = self.actor.px_per_tile * self.token.radius

        scale = piece_r / icon_r
        for sprite in self.sprites:
            sprite.scale = scale
        
    @kxg.watch_token
    def on_update_game(self, delta_t):
        for sprite in self.sprites:
            sprite.position = self.actor.xyg_from_xyw(self.token.xyw)

    def on_select(self):
        info(f"selecting piece: {self.token}")
        self.selected_sprite.visible = True
        self.unselected_sprite.visible = False

        self.move_lines = []

        for move in self.token.find_possible_moves():
            xyw_waypoints = [self.token.xyw, *move.xyw_path]
            xygs = [
                    self.actor.xyg_from_xyw(v)
                    for v in flatten(pairwise(xyw_waypoints))
            ]

            n = len(xygs)
            v2f = sum((x.tuple for x in xygs), ())
            c3B = n * [0, 32, 73]  # navy

            line = self.actor.gui.batch.add(
                    n, GL_LINES, None,
                    ('v2f', v2f),
                    ('c3B', c3B),
            )
            self.move_lines.append(line)

    def on_deselect(self):
        info(f"deselecting piece: {self.token}")
        self.selected_sprite.visible = False
        self.unselected_sprite.visible = True

        for line in self.move_lines:
            line.delete()

    @kxg.watch_token
    def on_remove_from_world(self):
        for sprite in self.sprites:
            sprite.delete()

    def _new_sprite(self, image_key, group_num=1, **sprite_kwargs):
        """
        Create a new sprite object with some common (but cluttering) parameters 
        prefilled. 
        'image_key' is the key for the image dict defined in the gui.
        'group_num' is the pyglet OrderedGroup number
        'sprite_kwargs' are passed directly to Sprite constructor
        """

        xg, yg = self.actor.xyg_from_xyw(self.token.xyw)
        sprite = pyglet.sprite.Sprite(
                self.actor.gui.images[image_key],
                x=xg, y=yg,
                batch=self.actor.gui.batch,
                group=pyglet.graphics.OrderedGroup(group_num),
                **sprite_kwargs,
        )

        return sprite


