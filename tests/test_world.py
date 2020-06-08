#!/usr/bin/env python3

import cherts
from utils import parametrize_via_toml
from hypothesis import given
from hypothesis.strategies import tuples, floats
from pytest import approx, raises

@parametrize_via_toml('test_world.toml')
def test_player_coords(origin, heading, rel_coord, abs_coord):
    player = cherts.Player(origin, heading)
    assert player.to_absolute_coord(rel_coord) == abs_coord
    assert player.to_relative_coord(abs_coord) == rel_coord

@parametrize_via_toml('test_world.toml')
@given(tuples(floats(), floats()))
def test_player_coords_inv(origin, heading, xy):
    player = cherts.Player(origin, heading)
    f = player.to_relative_coord
    g = player.to_absolute_coord

    assert f(g(xy)).tuple == approx(xy, nan_ok=True)
    assert g(f(xy)).tuple == approx(xy, nan_ok=True)




@parametrize_via_toml('test_world.toml')
def test_eval_waypoint_expr(origin, heading, x, y, w, h, expr, expected):
    player = cherts.Player(origin, heading)
    type = cherts.PieceType(
            'dummy',
            move_types=[],
            pattern_types=[],
            cooldown_sec=0,
    )
    piece = cherts.Piece(player, type, (x, y))
    board = cherts.Board(w, h)

    assert cherts.eval_waypoint_expr(expr, piece, board) == expected

@parametrize_via_toml('test_world.toml')
def test_eval_waypoint_expr_err(expr, err_type, err_msg):
    from vecrec import VectorCastError

    player = cherts.Player((0, 0), (1, 1))
    type = cherts.PieceType(
            'dummy',
            move_types=[],
            pattern_types=[],
            cooldown_sec=0,
    )
    piece = cherts.Piece(player, type, (2, 2))
    board = cherts.Board(8, 8)

    with raises(eval(err_type), match=err_msg):
        cherts.eval_waypoint_expr(expr, piece, board)
