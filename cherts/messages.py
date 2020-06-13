#!/usr/bin/env python3

from kxg import Message, MessageCheck

from cherts.world import *
from cherts.config import (
        load_board, load_move_types, load_pattern_types, load_piece_types
)

# Think about adding an `on_receive`/`on_finalize`/`on_prepare`/`on_unpack` 
# event handler that is called once the message will no longer be sent over the 
# network.  Specifically, this would be after `on_check()` but before 
# `on_execute()`.
#
# This would be useful in SetupWorld, to create tokens from the config 
# dictionary.  Right now this has to be done in `__init__()`, which means that 
# more data is sent over the network than is necessary.

class SetupWorld(Message):

    def __init__(self, config):
        self.config = config
        self.board = load_board(self.config)
        self.move_types = load_move_types(self.config)
        self.pattern_types = load_pattern_types(self.config)
        self.piece_types = load_piece_types(
                self.config,
                self.move_types,
                self.pattern_types,
        )

    def tokens_to_add(self):
        yield self.board
        yield from self.move_types.values()
        yield from self.pattern_types.values()
        yield from self.piece_types.values()

    def on_check(self, world):
        # Make sure the world hasn't already been setup.
        if world.board:
            raise MessageCheck("board already exists.")
        if world.move_types:
            raise MessageCheck("move types already defined.")
        if world.pattern_types:
            raise MessageCheck("pattern types already defined.")
        if world.piece_types:
            raise MessageCheck("piece types already defined.")

    def on_execute(self, world):
        world.setup(
                board=self.board,
                move_types=self.move_types,
                pattern_types=self.pattern_types,
                piece_types=self.piece_types,
        )

class SetupPlayer(Message):

    def __init__(self, player):
        self.player = player

    def tokens_to_add(self):
        yield self.player
        yield from self.player.pieces

    def on_check(self, world):
        # Make sure there aren't too many players.
        if len(world.players) >= 2:
            raise MessageCheck("too many players")

    def on_execute(self, world):
        world.add_player(self.player)

class AnticipateCollision(Message):
    # The server could anticipate collision between pieces, and preemptively 
    # send out messages saying what will happen.  This might be a way to make 
    # the game more responsive, if that's a problem.
    pass

