from vecrec import Vector
from kxg import Token, read_only

# Coordinate frames
# =================
# There are two coordinate frames:
#
# - "absolute": Real positions, independent of the player.  Most coordinate 
#   variables are absolute, and you should assume that a coordinate is absolute 
#   unless it is labeled otherwise.

# - "relative": Positions from the perspective of the player.  In this frame, 
#   the edge of the board nearest to the player has y=0, and the edge nearest 
#   to the opponent has y=h (where h is the height of the board).  The left 
#   edge of the board is x=0 and the right edge is x=w (where w is the width of 
#   the board).  The "waypoint expressions" loaded from the config file are in 
#   relative coordinates, but are converted to absolute coordinates as soon as 
#   possible (e.g. when they are evaluated for a particular piece).

class World(World):

    def __init__(self):
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

class Board(Token):

    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def size(self):
        return self.width, self.height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

class Player(Token):

    @classmethod
    def from_actor(cls, actor, board):
        if self.id == 1:
            origin = Vector(0, 0)
            heading = Vector(1, 1)
        elif self.id == 2:
            origin = Vector(board.width, board.height)
            heading = Vector(-1, -1)
        else:
            # There should only be two players, and their ids should be 1 and 
            # 2.  (The referee has id 0).
            raise ValueError(f"{self!r} has unexpected id={self.id}")

        return cls(origin, heading)

    def __init__(self, origin, heading):
        self._origin = origin
        self._heading = heading  # -1 or +1
        self._pieces = []

    @property
    def origin(self):
        return self._origin

    @property
    def heading(self):
        return self._heading

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
    def to_absolute_coord(self, xy):
        return self.origin + self.heading * Vector.from_anything(xy)

    @readonly
    def to_relative_coord(self, xy):
        return self.heading * (xy - self.origin)

class Piece(Token):

    # Not yet implemented:
    # - attack
    # - defense
    # - health
    # - orientation

    def __init__(self, player, type, position):
        self._player = player
        self._type = type
        self._position = position
        self._current_move = None
        self._current_pattern = None

    @property
    def player(self):
        return self._player

    @property
    def position(self):
        return self._position

    @property
    def move_types():
        return self.type.move_types

    @property
    def pattern_types(self):
        return self.type.pattern_types

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

class PieceType(Token):
    """
    Parameters for a particular piece type.

    Each `Piece` will hold a reference to a `PieceType`.  This is an 
    example of the Flyweight pattern.

    This class is meant to be read-only, because every attribute applies to 
    every instance of the piece.  To help enforce this, the public interface is 
    composed entirely of read-only properties.
    """

    def __init__(self, name, *, move_types, pattern_types, cooldown_sec):
        self._name = name
        self._cooldown_sec = cooldown_sec
        self._move_types = move_types
        self._pattern_types = pattern_types

    @property
    def name(self):
        return self._name

    @property
    def cooldown_sec(self):
        return self._cooldown_sec

    @property
    def move_types(self):
        return self._move_types

    @property
    def pattern_types(self):
        return self._pattern_types

class Pattern(Token):

    # Need some methods to keep track of progress...

    def __init__(self, type, piece, waypoints):
        self._type = type
        self._piece = piece
        self._waypoints = waypoints

    @property
    def type(self):
        return self._type

    @property
    def piece(self):
        return self._piece

    @property
    def waypoints(self):
        return self._waypoints

class PatternType(Token):

    def __init__(self, name, *, waypoint_exprs, on_complete_exprs, must_complete):
        self._name = name
        self._waypoint_exprs = waypoint_exprs
        self._on_complete_exprs = on_complete_exprs
        self._must_complete = must_complete

    @property
    def must_complete(self):
        return self._must_complete

    @read_only
    def make_patterns(self, piece):
        waypoints = eval_waypoint_exprs(
                self.waypoint_exprs,
                piece,
                self.world.board,
                any_ok=True,
        )
        return [Pattern(self, piece, x) for x in waypoints]

    @property
    def make_completion_message(self):
        raise NotImplementedError

class Move(Token):

    def __init__(self, type, piece, waypoints):
        self._type = type
        self._piece = piece
        self._waypoints = waypoints

    @property
    def type(self):
        return self._type

    @property
    def piece(self):
        return self._piece

    @property
    def waypoints(self):
        return self._waypoints

class MoveType(Token):

    def __init__(self, name, *, mode, waypoint_exprs):
        self._name = name
        self._mode = mode
        self._waypoint_exprs = waypoint_exprs

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
        waypoints = eval_waypoint_exprs(
                self.waypoint_exprs,
                piece,
                self.world.board,
        )
        return [Move(self, piece, x) for x in waypoints]

def eval_waypoint_exprs(exprs, piece, board, any_ok=False):
    waypoints = []
    for expr in exprs:
        waypoints += eval_waypoint_expr(expr, piece, board, any_ok)
    return waypoints

def eval_waypoint_expr(expr, piece, board, any_ok=False):
    player = piece.player
    rel = player.to_relative_coord(piece.position)
    any = {'any': float('nan')} if any_ok else {}
    waypoints = eval(expr, {}, {
            'x': rel.x,
            'y': rel.y,
            'w': board.width,
            'h': board.height,
            **any,
    })
    if isinstance(xy := waypoints, tuple):
        return [[player.to_absolute_coords(xy)]]

    if not isintance(waypoints, list) or not waypoints:
        raise ValueError(f"{expr!r}: expected list, got {waypoints!r}")

    if isinstance(waypoints[0], tuple):
        return [[player.to_absolute_coords(xy) for xy in waypoints]]

    if not isintance(waypoints[0], list) or not waypoints[0]:
        raise ValueError(f"{expr!r}: expected list, got {waypoints[0]!r}")

    return [[player.to_absolute_coords(xy) for xy in w] for w in waypoints]

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

