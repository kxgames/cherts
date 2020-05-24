#!/usr/bin/env python3

import kxg
from vecrec import Vector

from cherts.dummy_messages import *


class DummyReferee (kxg.Referee):

    def on_start_game(self, num_players):
        # Set up init game?
        self >> SetupDummyWorld()

        self >> CreateDummyKing(1, Vector(400, 100))
        self >> CreateDummyKing(2, Vector(400, 500))
