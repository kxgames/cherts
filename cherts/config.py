#!/usr/bin/env python3

import rtoml
from pathlib import Path
from more_itertools import collapse
from .world import Board, Piece, PieceType, MoveType, PatternType

# Naming conventions
# ==================
# `config`: The dictionary loaded from `config.toml`.
# `params`: The subset of `config` relevant to a particular function.

def load_config():
    toml_path = Path(__file__).parent / 'config.toml'
    return rtoml.load(toml_path)

def load_initial_pieces(config, player, piece_types):
    pieces = []
    for params in config['setup']['pieces']:
        piece_type = piece_types[params['name']]
        position = player.to_absolute_coord(params['pos'])
        piece = Piece(player, piece_type, position)
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
            radius=params['radius'],
            move_types=list(collapse([
                move_types[k]
                for k in params['moves']
            ])),
            pattern_types={
                pattern_types[k]
                for k in params['patterns']
            },
            cooldown_sec=params['move_cooldown_sec'],
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
