#!/usr/bin/env python3

import kxg

from .messages import SetupWorld
from .config import load_config

class Referee (kxg.Referee):

    def on_start_game(self, num_players):
        config = load_config()
        self >> SetupWorld(config)
