#!/usr/bin/env python3

import cherts
from utils import parametrize_via_toml
from hypothesis import given
from hypothesis.strategies import tuples, floats
from pytest import approx, raises

@parametrize_via_toml('test_world.toml')
def test_player_coords(origin, heading, xyp, xyw):
    player = cherts.Player(origin, heading)
    assert xyw == player.xyw_from_xyp(xyp)
    assert xyp == player.xyp_from_xyw(xyw)

@parametrize_via_toml('test_world.toml')
@given(tuples(floats(), floats()))
def test_player_coords_inv(origin, heading, xy):
    # Make sure the round trip between the world and player coordinates frames 
    # doesn't change anything.
    player = cherts.Player(origin, heading)
    f = player.xyw_from_xyp
    g = player.xyp_from_xyw

    assert f(g(xy)).tuple == approx(xy, nan_ok=True)
    assert g(f(xy)).tuple == approx(xy, nan_ok=True)


@parametrize_via_toml('test_world.toml')
def test_xyw_paths_from_xyp_expr(origin, heading, xyw, wh, xyp_expr, xyw_paths):
    player = cherts.Player(origin, heading)
    type = cherts.PieceType(
            'dummy',
            radius=10,
            move_types=[],
            pattern_types=[],
            cooldown_sec=0,
    )
    piece = cherts.Piece(player, type, xyw)
    board = cherts.Board(*wh)

    assert xyw_paths == cherts.xyw_paths_from_xyp_expr(xyp_expr, piece, board)

@parametrize_via_toml('test_world.toml')
def test_xyw_paths_from_xyp_expr_err(xyp_expr, err_type, err_msg):
    from vecrec import VectorCastError

    player = cherts.Player((0, 0), (1, 1))
    type = cherts.PieceType(
            'dummy',
            radius=10,
            move_types=[],
            pattern_types=[],
            cooldown_sec=0,
    )
    piece = cherts.Piece(player, type, (2, 2))
    board = cherts.Board(8, 8)

    with raises(eval(err_type), match=err_msg):
        cherts.xyw_paths_from_xyp_expr(xyp_expr, piece, board)
