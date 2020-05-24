#!/usr/bin/env python3

import kxg

from .messages import SetupWorld, SetupPlayer
from .world import Player

class BaseActor(kxg.Actor):

    def __init__(self):
        super().__init__()
        self.player = None

    @kxg.subscribe_to_message(SetupWorld)
    def on_setup_world(self, message):
        self.player = Player.from_actor(self)
        pieces = load_initial_pieces(
                message.config,
                self.player,
                self.world.piece_types,
        )
        self.player.gain_pieces(pieces)
        self >> SetupPlayer(self.player)





