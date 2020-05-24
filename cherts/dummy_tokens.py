#!/usr/bin/env python3

import kxg

class DummyPiece(kxg.Token):

    def __init__(self, type, init_position):
        super().__init__()

        self._type = type
        self._position = init_position
        self._health = 1000
        # self._moves = All Move objects for piece type
        # self._attacks = Attack
        # self._defense = Defense
        # All Pattern objects for piece type
        # Orientation
        # Recharge time (before making next motion)

    # Attributes
    @property
    def type(self):
        return self._type

    @property
    def position(self):
        return self._position

    @property
    def health(self):
        return self._health


    # Moves and patterns
    def get_possible_moves(self):
        # returns Move object(s) that the piece could use
        raise NotImplementedError

    def get_possible_patterns(self):
        raise NotImplementedError

    def get_legal_moves(self):
        # Gets movements that account for captive patterns and other piece 
        # positions
        raise NotImplementedError

    def get_current_movement(self):
        raise NotImplementedError

    def get_current_pattern(self):
        raise NotImplementedError

    def get_possible_attacks(self):
        raise NotImplementedError


    # Extension
    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.DummyPieceExtension}
