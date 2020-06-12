import kxg
from vecrec import Vector, cast_anything_to_vector, accept_anything_as_vector
from kxg import read_only

# Variable naming conventions
# ===========================
# Some of the variable names/prefixes, especially those for coordinates, use 
# abbreviated conventions that aren't intuitively meaningful.  The advantage of 
# these conventions is that they make it easy to be precise about what kind of 
# information different variables contain, which will hopefully make the code 
# easier to read and write (once you get used to the conventions).
#
# See also this article, for some of the motivation behind these conventions:
# https://www.joelonsoftware.com/2005/05/11/making-wrong-code-look-wrong/
#
# `xyp`
#   Mnemonic: "player (x, y)"
#   A vector coordinate from the perspective of a player.  Usually the player 
#   is inferred from the context, e.g.  `Piece.xyp` is from the perspective of 
#   the player controlling the piece.  In this coordinate frame, the edge of 
#   the board nearest to the player has y=0, and the edge nearest to the 
#   opponent has y=h (where h is the height of the board).  The left edge of 
#   the board is x=0 and the right edge is x=w (where w is the width of the 
#   board).
#   
# `xyw`
#   Mnemonic: "world (x, y)"
#   A vector coordinate in absolute world coordinates.  Most position variables 
#   are stored in this coordinate frame (in contrast, `xyp` and `xyg` positions 
#   are usually calculated as they are needed from `xyw` positions).  This 
#   coordinate frame is the same as the coordinate frame for player 1.
#
# `xyg`
#   Mnemonic: "GUI (x, y)":
#   A pixel coordinate in the window being displayed.  The transformations 
#   to/from this coordinate frame are defined in `gui.BoardExtension`.  In the 
#   future, different GUI implementations may define this transformation 
#   differently.  This transformation may take the player into account, such 
#   that thy player's own piece appear in front of them, but this is not 
#   required.
#
# `xyp_expr`
#   Mnemonic: "player (x, y) expressions"
#   A string containing an expression that can evaluate to:
#
#   - A coordinate from a player's perspective (i.e. `xyp`).
#   - A list of such coordinates (i.e. `xyp_path`)
#   - A list of such paths (i.e. `xyp_paths`)
#
#   `xyp_expr` variables are typically loaded from config files, and are 
#   converted to `xyp_paths` when applied to a particular piece.
#
# `path`
#   A list of coordinates meant to be traversed in order, e.g. waypoints.  
#   Paths can be in different coordinate frames, e.g. `xyp_path`, `xyw_path`, 
#   etc.

class World(kxg.World):

    def __init__(self):
        super().__init__()
        self._board = None
        self._players = []
        self._move_types = {}
        self._pattern_types = {}
        self._piece_types = {}

    @property
    def board(self):
        return self._board

    @property
    def players(self):
        return self._players

    @property
    def move_types(self):
        return self._move_types

    @property
    def pattern_types(self):
        return self._pattern_types

    @property
    def piece_types(self):
        return self._piece_types

    def setup(self, board, *, move_types, pattern_types, piece_types):
        self._board = board
        self._move_types = move_types
        self._pattern_types = pattern_types
        self._piece_types = piece_types

    def add_player(self, player):
        self._players.append(player)

    @kxg.read_only
    def find_piece(self, xyw_click):
        """
        Finds the piece at an (x, y) location.
        """
        for piece in self.iter_pieces():
            radius2 = piece.radius**2
            dist2 = xyw_click.get_distance_squared(piece.xyw)

            # Clicked on this piece.
            if dist2 < radius2:
                return piece

        # Didn't click on any piece.
        return None

    @kxg.read_only
    def iter_pieces(self):
        for player in self.players:
            yield from player.pieces

class Board(kxg.Token):

    def __init__(self, width, height):
        super().__init__()
        self._width = width
        self._height = height

    def __repr__(self):
        return super().__repr__(width=self.width, height=self.height)

    def __extend__(self):
        from . import gui
        return {
                gui.GuiActor: gui.BoardExtension,
        }

    @property
    def size(self):
        return self.width, self.height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

class Player(kxg.Token):

    @classmethod
    def from_actor(cls, actor, board):
        if actor.id == 2:
            origin = Vector(0, 0)
            heading = Vector(1, 1)
            color = 'white'
        elif actor.id == 3:
            origin = Vector(board.width - 1, board.height - 1)
            heading = Vector(-1, -1)
            color = 'black'
        else:
            # There should only be two players, and their ids should be 2 and 
            # 3.  (The referee has id 1).
            raise ValueError(f"{actor!r} has unexpected id={actor.id}")

        return cls(origin, heading, color)

    def __init__(self, origin, heading, color):
        super().__init__()
        self._origin = cast_anything_to_vector(origin)
        self._heading = cast_anything_to_vector(heading)
        self._color = color
        self._pieces = []

    def __repr__(self):
        return super().__repr__(color=self.color)

    @property
    def origin(self):
        return self._origin

    @property
    def heading(self):
        return self._heading

    @property
    def color(self):
        return self._color

    @property
    def pieces(self):
        return self._pieces

    def gain_piece(self, piece):
        assert piece.player is self
        self._pieces.append(piece)

    def gain_pieces(self, pieces):
        assert all(x.player is self for x in pieces)
        self._pieces += pieces

    def lose_piece(self, piece):
        self._pieces.remove(piece)

    def lose_pieces(self, pieces):
        for piece in pieces:
            self.lose_piece(piece)

    @read_only
    @accept_anything_as_vector
    def xyw_from_xyp(self, xyp):
        return self.origin + self.heading * Vector.from_anything(xyp)

    @read_only
    @accept_anything_as_vector
    def xyp_from_xyw(self, xyw):
        return self.heading * (xyw - self.origin)

class Piece(kxg.Token):

    # Not yet implemented:
    # - attack
    # - defense
    # - health
    # - orientation

    def __init__(self, player, type, xyw):
        super().__init__()
        self._player = player
        self._type = type
        self._xyw = cast_anything_to_vector(xyw)
        self._current_move = None
        self._current_pattern = None

    def __repr__(self):
        return super().__repr__(
                player=self.player.id,
                type=self._type.name,
                xyw=self.xyw,
        )

    def __extend__(self):
        from . import gui
        return {
                gui.GuiActor: gui.PieceExtension,
        }

    @property
    def player(self):
        return self._player

    @property
    def type(self):
        return self._type

    @property
    def xyw(self):
        return self._xyw

    @property
    def radius(self):
        return self._type.radius

    @property
    def move_types(self):
        return self._type.move_types

    @property
    def pattern_types(self):
        return self._type.pattern_types

    @read_only
    def find_possible_moves(self):
        return [
                x.make_moves(self)
                for x in self.move_types.values()
        ]

    @read_only
    def find_legal_moves(self):
        """
        Return a list of moves that the piece can legally make, accounting for 
        other pieces and patterns that must be completed.
        """
        raise NotImplementedError

    @property
    def current_move(self):
        return self._current_move

    @property
    def current_pattern(self):
        return self._current_pattern

class PieceType(kxg.Token):
    """
    Parameters for a particular piece type.

    Each `Piece` will hold a reference to a `PieceType`.  This is an 
    example of the Flyweight pattern.

    This class is meant to be read-only, because every attribute applies to 
    every instance of the piece.  To help enforce this, the public interface is 
    composed entirely of read-only properties.
    """

    def __init__(self, name, *, radius, move_types, pattern_types, cooldown_sec):
        super().__init__()
        self._name = name
        self._radius = radius
        self._cooldown_sec = cooldown_sec
        self._move_types = move_types
        self._pattern_types = pattern_types

    def __repr__(self):
        return super().__repr__(name=self.name)

    @property
    def name(self):
        return self._name

    @property
    def radius(self):
        return self._radius

    @property
    def cooldown_sec(self):
        return self._cooldown_sec

    @property
    def move_types(self):
        return self._move_types

    @property
    def pattern_types(self):
        return self._pattern_types

class Pattern(kxg.Token):

    # Need some methods to keep track of progress...

    def __init__(self, type, piece, xyw_path):
        super().__init__()
        self._type = type
        self._piece = piece
        self._xyw_path = xyw_path

    @property
    def type(self):
        return self._type

    @property
    def piece(self):
        return self._piece

    @property
    def xyw_path(self):
        return self._waypoints

class PatternType(kxg.Token):

    def __init__(self, name, *, xyp_exprs, on_complete_exprs, must_complete):
        super().__init__()
        self._name = name
        self._xyp_exprs = xyp_exprs
        self._on_complete_exprs = on_complete_exprs
        self._must_complete = must_complete

    def __repr__(self):
        return super().__repr__(name=self.name)

    @property
    def name(self):
        return self._name

    @property
    def must_complete(self):
        return self._must_complete

    @read_only
    def make_patterns(self, piece):
        xyw_paths = xyw_paths_from_xyp_exprs(
                self.xyp_exprs,
                piece,
                self.world.board,
                any_ok=True,
        )
        return [Pattern(self, piece, p) for p in xyw_paths]

    #@property
    #def make_completion_message(self):
    #    raise NotImplementedError

class Move(kxg.Token):

    def __init__(self, type, piece, xyw_path):
        super().__init__()
        self._type = type
        self._piece = piece
        self._xyw_path = xyw_path

    @property
    def type(self):
        return self._type

    @property
    def piece(self):
        return self._piece

    @property
    def xyw_path(self):
        return self._xyw_path

class MoveType(kxg.Token):

    def __init__(self, name, *, mode, xyp_exprs):
        super().__init__()
        self._name = name
        self._mode = mode
        self._xyp_exprs = xyp_exprs

    def __repr__(self):
        return super().__repr__(name=self.name)

    @property
    def name(self):
        return self._name

    @property
    def is_jump(self):
        return self._mode == 'jump'

    @property
    def is_slide(self):
        return self._mode == 'slide'

    @read_only
    def make_moves(self, piece):
        xyw_paths = xyw_paths_from_xyp_exprs(
                self.xyp_exprs,
                piece,
                self.world.board,
        )
        return [Move(self, piece, x) for x in xyw_paths]

def xyw_paths_from_xyp_exprs(xyp_exprs, piece, board, any_ok=False):
    xyw_paths = []
    for xyp_expr in xyp_exprs:
        xyw_paths += xyw_paths_from_xyp_expr(xyp_expr, piece, board, any_ok)
    return xyw_paths

def xyw_paths_from_xyp_expr(xyp_expr, piece, board, any_ok=False):
    """
    Evaluate the given expression for the given piece and board.

    Parameters:
        expr: A string containing a python expression.  The following variables 
            are available to the expression:

            x: The relative x-coordinate of the piece.
            y: The relative y-coordinate of the piece.
            w: The width of the board.
            h: The height of the board.
            any: NaN.  Used to indicate that a particular coordinate is not 
                important.  Can only be used if **any_ok** is True.

            The expression should evaluate to:

            - An relative coordinate, i.e. an (x, y) tuple.
            - A list of relative coordinates, i.e. a path.
            - A list of list of relative coordinates, i.e. multiple paths.

        piece: The piece the expression applies to.
        board: The board the piece is moving on.  
        any_ok: If true, the expression may use the 'any' variable described 
            above.

    Returns:
        A list of list of absolute coordinates.  The inner list is all of the 
        waypoints in a particular move/pattern.  The outer list is all of the 
        moves/patterns described by the expression.
    """
    player = piece.player
    any = {'any': float('nan')} if any_ok else {}
    xyp_piece = player.xyp_from_xyw(piece.xyw)
    xyp_eval = eval(xyp_expr, {}, {
            'x': xyp_piece.x,
            'y': xyp_piece.y,
            'w': board.width,
            'h': board.height,
            **any,
    })
    if isinstance(xyp_eval, tuple):
        return [[player.xyw_from_xyp(xyp_eval)]]

    if not isinstance(xyp_eval, list) or not xyp_eval:
        raise ValueError(f"{xyp_expr!r}: expected tuple or list, got {xyp_eval!r}")

    if isinstance(xyp_eval[0], tuple):
        return [[player.xyw_from_xyp(xyp) for xyp in xyp_eval]]

    if not isinstance(xyp_eval[0], list) or not xyp_eval[0]:
        raise ValueError(f"{xyp_expr!r}: expected list, got {xyp_eval[0]!r}")

    return [[player.xyw_from_xyp(xyp) for xyp in _] for _ in xyp_eval]

# Pseudo-code

class Attack:
    pass

    # - During attack
    #   - Pieces occupy same space
    #   - Deal damage to eachother until one dies or retreats
    #   - Winner stays at same position

    # - Stores:
    #     - Damage rate function
    #       (linear, nonlinear, kamikaze, group bonuses, etc.)
    #     - Orientation bonus
    #     - Ranged? Likely no

    # - calc_damage_rate(other_piece)
    #   - accounts for other piece type, orientation, position, special locations

    # - calc_self_damage_rate(other_piece)

