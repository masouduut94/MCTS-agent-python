from numpy import zeros, int_
from unionfind import UnionFind
from meta import GameMeta


class GameState:
    """
    Stores information representing the current state of a game of hex, namely
    the board and the current turn. Also provides functions for playing game.
    """
    # dictionary associating numbers with players
    # PLAYERS = {"none": 0, "white": 1, "black": 2}

    # move value of -1 indicates the game has ended so no move is possible
    # GAME_OVER = -1

    # represent edges in the union find structure for detecting the connection
    # for player 1 Edge1 is high and EDGE2 is low
    # for player 2 Edge1 is left and EDGE2 is right

    # neighbor_patterns = ((-1, 0), (0, -1), (-1, 1), (0, 1), (1, 0), (1, -1))

    def __init__(self, size):
        """
        Initialize the game board and give white first turn.
        Also create our union find structures for win checking.

        Args:
            size (int): The board size
        """
        self.size = size
        self.to_play = GameMeta.PLAYERS['white']
        self.board = zeros((size, size))
        self.board = int_(self.board)
        self.white_played = 0
        self.black_played = 0
        self.white_groups = UnionFind()
        self.black_groups = UnionFind()
        self.white_groups.set_ignored_elements([GameMeta.EDGE1, GameMeta.EDGE2])
        self.black_groups.set_ignored_elements([GameMeta.EDGE1, GameMeta.EDGE2])

    def play(self, cell: tuple) -> None:
        """
        Play a stone of the player that owns the current turn in input cell.
        Args:
            cell (tuple): row and column of the cell
        """
        if self.to_play == GameMeta.PLAYERS['white']:
            self.place_white(cell)
            self.to_play = GameMeta.PLAYERS['black']
        elif self.to_play == GameMeta.PLAYERS['black']:
            self.place_black(cell)
            self.to_play = GameMeta.PLAYERS['white']

    def get_num_played(self) -> dict:
        return {'white': self.white_played, 'black': self.black_played}

    def get_white_groups(self) -> dict:
        """

        Returns (dict): group of white groups for unionfind check

        """
        return self.white_groups.get_groups()

    def get_black_groups(self) -> dict:
        """

        Returns (dict): group of white groups for unionfind check

        """
        return self.black_groups.get_groups()

    def place_white(self, cell: tuple) -> None:
        """
        Place a white stone regardless of whose turn it is.

        Args:
            cell (tuple): row and column of the cell
        """
        if self.board[cell] == GameMeta.PLAYERS['none']:
            self.board[cell] = GameMeta.PLAYERS['white']
            self.white_played += 1
        else:
            raise ValueError("Cell occupied")
        # if the placed cell touches a white edge connect it appropriately
        if cell[0] == 0:
            self.white_groups.join(GameMeta.EDGE1, cell)
        if cell[0] == self.size - 1:
            self.white_groups.join(GameMeta.EDGE2, cell)
        # join any groups connected by the new white stone
        for n in self.neighbors(cell):
            if self.board[n] == GameMeta.PLAYERS['white']:
                self.white_groups.join(n, cell)

    def place_black(self, cell: tuple) -> None:
        """
        Place a black stone regardless of whose turn it is.

        Args:
            cell (tuple): row and column of the cell
        """
        if self.board[cell] == GameMeta.PLAYERS['none']:
            self.board[cell] = GameMeta.PLAYERS['black']
            self.black_played += 1
        else:
            raise ValueError("Cell occupied")
        # if the placed cell touches a black edge connect it appropriately
        if cell[1] == 0:
            self.black_groups.join(GameMeta.EDGE1, cell)
        if cell[1] == self.size - 1:
            self.black_groups.join(GameMeta.EDGE2, cell)
        # join any groups connected by the new black stone
        for n in self.neighbors(cell):
            if self.board[n] == GameMeta.PLAYERS['black']:
                self.black_groups.join(n, cell)

    def would_lose(self, cell: tuple, color: int) -> bool:
        """
        Return True is the move indicated by cell and color would lose the game,
        False otherwise.
        """
        connect1 = False
        connect2 = False
        if color == GameMeta.PLAYERS['black']:
            if cell[1] == 0:
                connect1 = True
            elif cell[1] == self.size - 1:
                connect2 = True
            for n in self.neighbors(cell):
                if self.black_groups.connected(GameMeta.EDGE1, n):
                    connect1 = True
                elif self.black_groups.connected(GameMeta.EDGE2, n):
                    connect2 = True
        elif color == GameMeta.PLAYERS['white']:
            if cell[0] == 0:
                connect1 = True
            elif cell[0] == self.size - 1:
                connect2 = True
            for n in self.neighbors(cell):
                if self.white_groups.connected(GameMeta.EDGE1, n):
                    connect1 = True
                elif self.white_groups.connected(GameMeta.EDGE2, n):
                    connect2 = True

        return connect1 and connect2

    def turn(self) -> int:
        """
        Return the player with the next move.
        """
        return self.to_play

    def set_turn(self, player: int) -> None:
        """
        Set the player to take the next move.
        Raises:
            ValueError if player turn is not 1 or 2
        """
        if player in GameMeta.PLAYERS.values() and player != GameMeta.PLAYERS['none']:
            self.to_play = player
        else:
            raise ValueError('Invalid turn: ' + str(player))

    @property
    def winner(self) -> int:
        """
        Return a number corresponding to the winning player,
        or none if the game is not over.
        """
        if self.white_groups.connected(GameMeta.EDGE1, GameMeta.EDGE2):
            return GameMeta.PLAYERS['white']
        elif self.black_groups.connected(GameMeta.EDGE1, GameMeta.EDGE2):
            return GameMeta.PLAYERS['black']
        else:
            return GameMeta.PLAYERS['none']

    def neighbors(self, cell: tuple) -> list:
        """
        Return list of neighbors of the passed cell.

        Args:
            cell tuple):
        """
        x = cell[0]
        y = cell[1]
        return [(n[0] + x, n[1] + y) for n in GameMeta.NEIGHBOR_PATTERNS
                if (0 <= n[0] + x < self.size and 0 <= n[1] + y < self.size)]

    def moves(self) -> list:
        """
        Get a list of all moves possible on the current board.
        """
        moves = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[x, y] == GameMeta.PLAYERS['none']:
                    moves.append((x, y))
        return moves

    def __str__(self):
        """
        Print an ascii representation of the game board.
        Notes:
            Used for gtp interface
        """
        white = 'W'
        black = 'B'
        empty = '.'
        ret = '\n'
        coord_size = len(str(self.size))
        offset = 1
        ret += ' ' * (offset + 1)
        for x in range(self.size):
            ret += chr(ord('A') + x) + ' ' * offset * 2
        ret += '\n'
        for y in range(self.size):
            ret += str(y + 1) + ' ' * (offset * 2 + coord_size - len(str(y + 1)))
            for x in range(self.size):
                if self.board[x, y] == GameMeta.PLAYERS['white']:
                    ret += white
                elif self.board[x, y] == GameMeta.PLAYERS['black']:
                    ret += black
                else:
                    ret += empty
                ret += ' ' * offset * 2
            ret += white + "\n" + ' ' * offset * (y + 1)
        ret += ' ' * (offset * 2 + 1) + (black + ' ' * offset * 2) * self.size
        return ret
