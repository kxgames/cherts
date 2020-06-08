#!/usr/bin/env python3

import os.path as os_path
import kxg
import pyglet

from vecrec import Vector
from .actors import BaseActor

pyglet.resource.path = [
        os_path.join(os_path.dirname(__file__), '..', 'resources'),
        ]

class Gui(BaseActor):
#    - Needs Piece type, positions, possible/legal/current moves, 
#      possible/legal/current patterns, pattern consequences
#    - Highlights available moves, patterns, etc.
#    - Display extra info on patterns

    def __init__(self):
        self.bg_color = (0.75, 0.75, 0.75, 1.0)
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


class GuiActor (BaseActor):

    def __init__(self):
        super().__init__()

        self.player = None
        self.selected_piece = None


    def on_setup_gui(self, gui):
        self.gui = gui
        self.gui.window.set_handlers(self)

    def on_draw(self):
        self.gui.on_refresh_gui()


    # User input events
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            pass

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            # Left click to select pieces
            undercursor_piece = self.world.find_piece_at_position(Vector(x, y))
            
            if undercursor_piece is None:
                if self.selected_piece is not None:
                    p = self.selected_piece
                    print(f"Unselecting p{p.player} {p.type}")
                    # Unselect a piece
                    self.selected_piece = None
                else:
                    print(f"Did not select a piece")
            else:
                # Select piece
                if self.selected_piece != undercursor_piece:
                    print(f"Piece selected p{undercursor_piece.player} {undercursor_piece.type}")
                self.selected_piece = undercursor_piece

        elif button == 2:
            # Right click to direct pieces
            pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass



class PieceExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        # Setup
        self.selected = False

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

        # Rescale the sprite image to match the piece radius
        icon_w = self.icon_sprite.width
        icon_h = self.icon_sprite.height
        icon_r = (icon_w**2 + icon_h**2)**0.5 / 2

        selected_w = self.selected_sprite.width
        selected_h = self.selected_sprite.height
        selected_r = (selected_w**2 + selected_h**2)**0.5 / 2

        piece_r = self.token.radius

        scale = piece_r / icon_r
        for sprite in self.sprites:
            sprite.scale = scale
        

    def _new_sprite(self, image_key, group_num=1, **sprite_kwargs):
        """
        Create a new sprite object with some common (but cluttering) parameters 
        prefilled. 
        'image_key' is the key for the image dict defined in the gui.
        'group_num' is the pyglet OrderedGroup number
        'sprite_kwargs' are passed directly to Sprite constructor
        """
        token_x, token_y = self.token.position
        sprite = pyglet.sprite.Sprite(
                self.actor.gui.images[image_key],
                x=token_x, y=token_y,
                batch=self.actor.gui.batch,
                group=pyglet.graphics.OrderedGroup(group_num),
                **sprite_kwargs,
        )

        return sprite

    def get_image_key(self):
        pc = self.actor.gui.piece_file_codes
        type = self.token.type.name

        if self.token.player.id == 1:
            color = 'white'
        elif self.token.player.id == 2:
            color = 'black'
        else:
            raise NotImplementedError

        image_key = f"piece_{pc[type]}{pc[color]}t"
        return image_key


    @kxg.watch_token
    def on_update_game(self, delta_t):
        for sprite in self.sprites:
            sprite.position = self.token.position

        piece = self.token
        guiactor = self.actor

        if self.selected and guiactor.selected_piece != piece:
            # Piece has been unselected
            self.selected = False
            self.selected_sprite.visible = False
            self.unselected_sprite.visible = True

        elif not self.selected and guiactor.selected_piece == piece:
            # Piece has been selected
            self.selected = True
            self.selected_sprite.visible = True
            self.unselected_sprite.visible = False
        else:
            # No change in status
            pass

    @kxg.watch_token
    def on_remove_from_world(self):
        for sprite in self.sprites:
            sprite.delete()
