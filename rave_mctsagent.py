from math import sqrt, log
from copy import deepcopy
from random import choice, random
from time import time as clock

from gamestate import GameState
from uct_mcstsagent import Node, UctMctsAgent
from meta import *


class RaveNode(Node):
    def __init__(self, move=None, parent=None):
        """
        Initialize a new node with optional move and parent and initially empty
        children list and rollout statistics and unspecified outcome.

        """
        super(RaveNode, self).__init__(move, parent)

    @property
    def value(self, explore: float = MCTSMeta.EXPLORATION, rave_const: float = MCTSMeta.RAVE_CONST) -> float:
        """
        Calculate the UCT value of this node relative to its parent, the parameter
        "explore" specifies how much the value should favor nodes that have
        yet to be thoroughly explored versus nodes that seem to have a high win
        rate.
        Currently explore is set to zero when choosing the best move to play so
        that the move with the highest win_rate is always chosen. When searching
        explore is set to EXPLORATION specified above.

        """
        # unless explore is set to zero, maximally favor unexplored nodes
        if self.N == 0:
            return 0 if explore is 0 else GameMeta.INF
        else:
            # rave valuation:
            alpha = max(0, (rave_const - self.N) / rave_const)
            UCT = self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)
            AMAF = self.Q_RAVE / self.N_RAVE if self.N_RAVE is not 0 else 0
            return (1 - alpha) * UCT + alpha * AMAF


class RaveMctsAgent(UctMctsAgent):

    def __init__(self, state: GameState = GameState(8)):
        self.root_state = deepcopy(state)
        self.root = RaveNode()
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0

    def set_gamestate(self, state: GameState) -> None:
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.
        """
        self.root_state = deepcopy(state)
        self.root = RaveNode()

    def move(self, move: tuple) -> None:
        """
        Make the passed move and update the tree appropriately. It is
        designed to let the player choose an action manually (which might
        not be the best action).
        Args:
            move:
        """
        if move in self.root.children:
            child = self.root.children[move]
            child.parent = None
            self.root = child
            self.root_state.play(child.move)
            return

        # if for whatever reason the move is not in the children of
        # the root just throw out the tree and start over
        self.root_state.play(move)
        self.root = RaveNode()

    def search(self, time_budget: int) -> None:
        """
        Search and update the search tree for a specified amount of time in secounds.
        """
        start_time = clock()
        num_rollouts = 0

        # do until we exceed our time budget
        while clock() - start_time < time_budget:
            node, state = self.select_node()
            turn = state.turn()
            outcome, black_rave_pts, white_rave_pts = self.roll_out(state)
            self.backup(node, turn, outcome, black_rave_pts, white_rave_pts)
            num_rollouts += 1
        run_time = clock() - start_time
        node_count = self.tree_size()
        self.run_time = run_time
        self.node_count = node_count
        self.num_rollouts = num_rollouts

    def select_node(self) -> tuple:
        """
        Select a node in the tree to preform a single simulation from.
        """
        node = self.root
        state = deepcopy(self.root_state)

        # stop if we reach a leaf node
        while len(node.children) != 0:
            max_value = max(node.children.values(),
                            key=lambda n:
                            n.value).value
            # descend to the maximum value node, break ties at random
            max_nodes = [n for n in node.children.values() if
                         n.value == max_value]
            node = choice(max_nodes)
            state.play(node.move)

            # if some child node has not been explored select it before expanding
            # other children
            if node.N == 0:
                return node, state

        # if we reach a leaf node generate its children and return one of them
        # if the node is terminal, just return the terminal node
        if self.expand(node, state):
            node = choice(list(node.children.values()))
            state.play(node.move)
        return node, state

    @staticmethod
    def expand(parent: RaveNode, state: GameState) -> bool:
        """
        Generate the children of the passed "parent" node based on the available
        moves in the passed gamestate and add them to the tree.

        Returns:
            object:
        """
        children = []
        if state.winner != GameMeta.PLAYERS["none"]:
            # game is over at this node so nothing to expand
            return False

        for move in state.moves():
            children.append(RaveNode(move, parent))

        parent.add_children(children)
        return True

    @staticmethod
    def roll_out(state: GameState) -> tuple:
        """
        Simulate a random game except that we play all known critical
        cells first, return the winning player and record critical cells at the end.

        """
        moves = state.moves()
        while state.winner == GameMeta.PLAYERS["none"]:
            move = choice(moves)
            state.play(move)
            moves.remove(move)

        black_rave_pts = []
        white_rave_pts = []

        for x in range(state.size):
            for y in range(state.size):
                if state.board[(x, y)] == GameMeta.PLAYERS["black"]:
                    black_rave_pts.append((x, y))
                elif state.board[(x, y)] == GameMeta.PLAYERS["white"]:
                    white_rave_pts.append((x, y))

        return state.winner, black_rave_pts, white_rave_pts

    def backup(self, node: RaveNode, turn: int, outcome: int, black_rave_pts: list, white_rave_pts: list) -> None:
        """
        Update the node statistics on the path from the passed node to root to reflect
        the outcome of a randomly simulated playout.
        """
        # note that reward is calculated for player who just played
        # at the node and not the next player to play
        reward = -1 if outcome == turn else 1

        while node is not None:
            if turn == GameMeta.PLAYERS["white"]:
                for point in white_rave_pts:
                    if point in node.children:
                        node.children[point].Q_RAVE += -reward
                        node.children[point].N_RAVE += 1
            else:
                for point in black_rave_pts:
                    if point in node.children:
                        node.children[point].Q_RAVE += -reward
                        node.children[point].N_RAVE += 1

            node.N += 1
            node.Q += reward
            turn = GameMeta.PLAYERS['white'] if turn == GameMeta.PLAYERS['black'] else GameMeta.PLAYERS['black']
            reward = -reward
            node = node.parent


class DecisiveMoveMctsAgent(RaveMctsAgent):

    def roll_out(self, state: GameState) -> tuple:
        """
        Simulate a random game except that we play all known critical cells
        first, return the winning player and record critical cells at the end.
        """
        moves = state.moves()
        good_moves = moves.copy()
        good_opponent_moves = moves.copy()
        to_play = state.turn()

        while state.winner == GameMeta.PLAYERS["none"]:
            done = False
            while len(good_moves) > 0 and not done:
                move = choice(good_moves)
                good_moves.remove(move)
                if not state.would_lose(move, to_play):
                    state.play(move)
                    moves.remove(move)
                    if move in good_opponent_moves:
                        good_opponent_moves.remove(move)
                    done = True

            if not done:
                move = choice(moves)
                state.play(move)
                moves.remove(move)
                if move in good_opponent_moves:
                    good_opponent_moves.remove(move)

            good_moves, good_opponent_moves = good_opponent_moves, good_moves

        black_rave_pts = []
        white_rave_pts = []

        for x in range(state.size):
            for y in range(state.size):
                if state.board[(x, y)] == GameMeta.PLAYERS["black"]:
                    black_rave_pts.append((x, y))
                elif state.board[(x, y)] == GameMeta.PLAYERS["white"]:
                    white_rave_pts.append((x, y))

        return state.winner, black_rave_pts, white_rave_pts


class LGRMctsAgent(RaveMctsAgent):

    def __init__(self, state: GameState = GameState(8)):
        super().__init__(state)
        self.black_reply = {}
        self.white_reply = {}

    def set_gamestate(self, state: GameState) -> None:
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.
        """
        super().set_gamestate(state)
        self.white_reply = {}
        self.black_reply = {}

    def roll_out(self, state: GameState) -> tuple:
        """
        Simulate a random game except that we play all known critical
        cells first, return the winning player and record critical cells at the end.

        """
        moves = state.moves()
        first = state.turn()
        if first == GameMeta.PLAYERS["black"]:
            current_reply = self.black_reply
            other_reply = self.white_reply
        else:
            current_reply = self.white_reply
            other_reply = self.black_reply
        black_moves = []
        white_moves = []
        last_move = None
        while state.winner == GameMeta.PLAYERS["none"]:
            if last_move in current_reply:
                move = current_reply[last_move]
                if move not in moves or random() > MCTSMeta.RANDOMNESS:
                    move = choice(moves)
            else:
                move = choice(moves)
            if state.turn() == GameMeta.PLAYERS["black"]:
                black_moves.append(move)
            else:
                white_moves.append(move)
            current_reply, other_reply = other_reply, current_reply
            state.play(move)
            moves.remove(move)
            last_move = move

        black_rave_pts = []
        white_rave_pts = []

        for x in range(state.size):
            for y in range(state.size):
                if state.board[(x, y)] == GameMeta.PLAYERS["black"]:
                    black_rave_pts.append((x, y))
                elif state.board[(x, y)] == GameMeta.PLAYERS["white"]:
                    white_rave_pts.append((x, y))

        # This part of the algorithm probably deals with adjusting
        # the indices of the arrays.

        offset = 0
        skip = 0
        if state.winner == GameMeta.PLAYERS["black"]:

            if first == GameMeta.PLAYERS["black"]:
                offset = 1
            if state.turn() == GameMeta.PLAYERS["black"]:
                skip = 1
            for i in range(len(white_moves) - skip):
                self.black_reply[white_moves[i]] = black_moves[i + offset]
        else:
            if first == GameMeta.PLAYERS["white"]:
                offset = 1
            if state.turn() == GameMeta.PLAYERS["white"]:
                skip = 1
            for i in range(len(black_moves) - skip):
                self.white_reply[black_moves[i]] = white_moves[i + offset]

        return state.winner, black_rave_pts, white_rave_pts


class PoolRaveMctsAgent(RaveMctsAgent):

    def __init__(self, state: GameState = GameState(8)):
        super().__init__(state)
        self.black_rave = {}
        self.white_rave = {}

    def set_gamestate(self, state: GameState) -> None:
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.
        """
        super().set_gamestate(state)
        self.black_rave = {}
        self.white_rave = {}

    def roll_out(self, state: GameState) -> tuple:
        """
        Simulate a random game except that we play all known critical
        cells first, return the winning player and record critical cells at the end.

        """
        moves = state.moves()
        black_rave_moves = sorted(self.black_rave.keys(),
                                  key=lambda cell: self.black_rave[cell])
        white_rave_moves = sorted(self.white_rave.keys(),
                                  key=lambda cell: self.white_rave[cell])
        black_pool = []
        white_pool = []

        i = 0
        while len(black_pool) < MCTSMeta.POOLRAVE_CAPACITY and i < len(black_rave_moves):
            if black_rave_moves[i] in moves:
                black_pool.append(black_rave_moves[i])
            i += 1
        i = 0
        while len(white_pool) < MCTSMeta.POOLRAVE_CAPACITY and i < len(white_rave_moves):
            if white_rave_moves[i] in moves:
                white_pool.append(white_rave_moves[i])
            i += 1
        num_pool = 0
        while state.winner == GameMeta.PLAYERS["none"]:
            move = None
            if len(black_pool) > 0 and state.turn() == GameMeta.PLAYERS["black"]:
                move = choice(black_pool)
                num_pool += 1
            elif len(white_pool) > 0:
                move = choice(white_pool)
                num_pool += 1
            if random() > MCTSMeta.RANDOMNESS or not move or move not in moves:
                move = choice(moves)
                num_pool -= 1

            state.play(move)
            moves.remove(move)

        black_rave_pts = []
        white_rave_pts = []

        for x in range(state.size):
            for y in range(state.size):
                if state.board[(x, y)] == GameMeta.PLAYERS["black"]:
                    black_rave_pts.append((x, y))
                    if state.winner == GameMeta.PLAYERS["black"]:
                        if (x, y) in self.black_rave:
                            self.black_rave[(x, y)] += 1
                        else:
                            self.black_rave[(x, y)] = 1
                    else:
                        if (x, y) in self.black_rave:
                            self.black_rave[(x, y)] -= 1
                        else:
                            self.black_rave[(x, y)] = -1
                elif state.board[(x, y)] == GameMeta.PLAYERS["white"]:
                    white_rave_pts.append((x, y))
                    if state.winner == GameMeta.PLAYERS["white"]:
                        if (x, y) in self.white_rave:
                            self.white_rave[(x, y)] += 1
                        else:
                            self.white_rave[(x, y)] = 1
                    else:
                        if (x, y) in self.white_rave:
                            self.white_rave[(x, y)] -= 1
                        else:
                            self.white_rave[(x, y)] = -1

        return state.winner, black_rave_pts, white_rave_pts
