#!/usr/bin/env python3

import kxg
from vecrec import Vector

from cherts.dummy_tokens import *
from cherts.dummy_map import DummyMap

class DummyWorld(kxg.World):

    def __init__(self):
        
        super().__init__()

        self.map = DummyMap((20, 20)) # What is supposed to make the map??
        self.pieces = {} # player : [pieces]

    def add_map(self, map):
        self.map = map

    def add_player(self, player_id):
        self.pieces[player_id] = []

    def add_piece(self, player, new_piece):

        """
        Add a new piece to the world. Called by the create piece message
        """
        assert player in self.pieces
        self.pieces[player].append(new_piece)


    def on_update_game(self, dt):
        super().on_update_game(dt)


    @kxg.read_only
    def find_piece_at_location(self, click_location):
        """
        Finds the piece at an (x, y) location.
        """

        for player, pieces in self.pieces.items():
            for piece in pieces:
                radius = piece.radius
                offset = click_location - piece.position
                if offset.magnitude_squared < radius**2:
                    # Clicked on piece
                    return piece

        # No piece found under click location
        return None
