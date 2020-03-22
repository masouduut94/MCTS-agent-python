
class MCTSMeta:
    EXPLORATION = 0.5
    RAVE_CONST = 300
    RANDOMNESS = 0.5
    POOLRAVE_CAPACITY = 10
    K_CONST = 10
    A_CONST = 0.25
    WARMUP_ROLLOUTS = 7


class GameMeta:
    PLAYERS = {'none': 0, 'white': 1, 'black': 2}
    INF = float('inf')
    GAME_OVER = -1
    EDGE1 = 1
    EDGE2 = 2
    NEIGHBOR_PATTERNS = ((-1, 0), (0, -1), (-1, 1), (0, 1), (1, 0), (1, -1))



