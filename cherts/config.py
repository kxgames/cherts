#!/usr/bin/env python3

import toml
from pathlib import Path
from more_itertools import flatten

from .world import PieceType

# Naming conventions
# ==================
# `config`: The dictionary loaded from `config.toml`.
# `params`: The subset of `config` relevant to a particular function.

def load_config():
    toml_path = Path(__file__).parent / 'config.toml'
    return toml.load(toml_path)

def load_initial_pieces(config, player, piece_types):
    pieces = []
    for k, xy in config['setup']['pieces']:
        position = player.resolve_relative_coord(xy)
        piece = Piece(player, piece_types[k], position)
        pieces.append(piece)
    return pieces

def load_board(config):
    return Board(
            width=config['board']['width'],
            height=config['board']['height'],
    )

def load_piece_types(config, move_types, pattern_types):
    return {
            name: load_piece_type(
                params,
                name,
                move_types,
                pattern_types,
            )
            for name, params in config['pieces'].items()
    }

def load_piece_type(params, name, move_types, pattern_types):
    return PieceType(
            name=name,
            move_types=list(flatten([
                move_types[k]
                for k in config['moves']
            ])),
            pattern_types={
                pattern_types[k]
                for k in config['patterns']
            },
            cooldown_sec=config['cooldown_sec'],
    )

def load_move_types(config):
    return {
            name: load_move_type(params, name)
            for name, params in config['moves'].items()
    }

def load_move_type(params, name):
    return MoveType(
            name,
            mode=params['mode'],
            waypoint_exprs=params['waypoints'],
    )

def load_pattern_types(config):
    return {
            name: load_pattern_type(params, name)
            for name, params in config['patterns'].items()
    }

def load_pattern_type(params, name):
    return PatternType(
            name,
            waypoint_exprs=params['waypoints'],
            on_complete_exprs=params['on_complete'],
            must_complete=params['must_complete'],
    )
