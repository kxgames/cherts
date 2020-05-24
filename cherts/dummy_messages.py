#!/usr/bin/env python3

import kxg
from cherts.dummy_tokens import *
from cherts.dummy_map import *

class SetupDummyWorld(kxg.Message):
    """
    Set up the initial world
    """

    def __init__(self):
        self.map = DummyMap((20, 20))
        #self.player1 = DummyPlayer()
        #self.player2 = DummyPlayer()

    def tokens_to_add(self):
        yield self.map

    def on_check(self, world):
        if not self.was_sent_by_referee():
            raise kxg.MessageCheck("only the referee can initialize the game")

    def on_execute(self, world):
        world.add_map(self.map)
        world.add_player(1) # hard coding player id for now
        world.add_player(2) # hard coding player id for now


# Create pieces messages
class CreateDummyPiece(kxg.Message):
    """
    Generic create a piece
    """

    def __init__(self, player, position):
        self.player = player
        self.position = position
        self.new_piece = None

    def tokens_to_add(self):
        assert self.new_piece is not None
        yield self.new_piece

    def _do_general_checks(self, world):
        # Do general checks.
        # Check the position is on map and isn't already occupied
        pass

    def on_execute(self, world):
        """
        Create a new piece and give it to the world to store.
        """

        world.add_piece(self.player, self.new_piece)


class CreateDummyKing(CreateDummyPiece):
    def __init__(self, player, position):
        super().__init__(player, position)
        self.type = 'king'
        self.new_piece = DummyPiece(self.type, self.position)

    def on_check(self, world):
        # Do piece specific checks
        self._do_general_checks(world)

        if self.was_sent_by_referee():
            # Referee can make kings with no further checks
            # Could this be a cheating risk?
            return
        else:
            # Check that player can actually create the piece?
            raise NotImplementedError
