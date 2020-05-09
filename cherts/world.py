Note:
    - Sever can anticipate collisions (battles) between pieces once moves are 
      made. Send out notifications to clients in advance.

class World:
    - stores map, pieces

class Map:
    - Stores boundaries
    - Fancier map ideas: scrabble!

    - get_boundaries() (or similar functions)

class Piece:
    - Stores:
        - Position
        - Health
        - Piece type
        - All Move objects for piece type
        - Attack
        - Defence
        - All Pattern objects for piece type
        - Orientation
        - Recharge time (before making next motion)

    - get_possible_moves()
      - returns Move object(s) that the piece could use
    - get_possible_patterns()

    - get_legal_moves()
      - Gets movements that account for captive patterns and other piece 
        positions

    - get_current_movement()
    - get_current_pattern()

    - get_possible_attacks()
    
class Attack:
    - During attack
      - Pieces occupy same space
      - Deal damage to eachother until one dies or retreats
      - Winner stays at same position

    - Stores:
        - Damage rate function
          (linear, nonlinear, kamikaze, group bonuses, etc.)
        - Orientation bonus
        - Ranged? Likely no

    - calc_damage_rate(other_piece)
      - accounts for other piece type, orientation, position, special locations

    - calc_self_damage_rate(other_piece)

class Move:
    - Move object for each permutation of motion a piece can make
      (NOT multiple inheriting class. Config file has info for all the 
      permutations, only one class type needed.)

    - Stores:
        - Speed (0 == jump, positive value is speed)
        - Relevant waypoints

    - get_relative_waypoints()
    - get_absolute_waypoints(piece)

class AbstractPattern:
    - Stores:
        - Relative waypoints
        - Start and end events if applicable
        - Is captive pattern
          (Pattern must finish before other motion is allowed. e.g. for pawns)

    - get_consequence()
      (e.g. "victory", "upgrade knight", "spawn pawn")
    - get_relative_waypoints()

class ActivePattern:
    - Stores:
        - Pattern position
        - Absolute waypoints
        - Link to abstract pattern
        - Link to piece
        - Completion metric

    - calc_time_to_complete()
    - get_absolute_waypoints()

