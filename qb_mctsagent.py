from random import choice
from time import clock
from gamestate import GameState
from uct_mcstsagent import UctMctsAgent, Node
from numpy.random import randint
from numpy import asarray, mean, std, exp, append
from meta import MCTSMeta, GameMeta


class QBMctsAgent(UctMctsAgent):
    """
    Basic no frills implementation of an agent that preforms MCTS for hex.

    """

    def __init__(self, state: GameState = GameState(8)):
        super(QBMctsAgent, self).__init__(state=state)
        moves_number, size = len(self.root_state.moves()), self.root_state.size
        initial_member = randint(moves_number // size, moves_number // 2)
        # initial_member = randint(divmod(moves_number, size)[0], divmod(moves_number, 2)[0])
        self.pl_list = asarray([[initial_member, initial_member]])

    def search(self, time_budget: int) -> None:
        """
        Search and update the search tree for a
        specified amount of time in seconds.

        Args:
            time_budget: How much time to think

        """
        start_time = clock()
        num_rollouts = 0

        # do until we exceed our time budget
        while clock() - start_time < time_budget:
            node, state = self.select_node()
            turn = state.turn()
            outcome = self.roll_out(state)
            self.backup(node, turn, outcome, state)
            num_rollouts += 1
        run_time = clock() - start_time
        node_count = self.tree_size()
        self.run_time = run_time
        self.node_count = node_count
        self.num_rollouts = num_rollouts

    def roll_out(self, state: GameState) -> tuple:
        """
        Simulate an entirely random game from the passed state and return the winning
        player.

        Returns:
            tuple: consists of winner of the game (either black or white)
                   and number of moves for each player

        """
        moves = state.moves()  # Get a list of all possible moves in current state of the game

        while state.winner == GameMeta.PLAYERS['none']:
            move = choice(moves)
            state.play(move)
            moves.remove(move)
        return state.winner

    def modify_reward(self, pl_length: dict) -> dict:
        """
        Takes the simulation length as the input and modifies it based on the
        Quality-Based rewards

        Args:
            pl_length:

        Returns:
            dict: Bonus added reward based on quality based rewards

        """
        mean_ = mean(self.pl_list, axis=0)
        mean_offset = asarray([mean_[0] - pl_length[0], mean_[1] - pl_length[1]])
        deviation = std(self.pl_list, axis=0)
        landa = asarray(list(map(lambda x, y: x / y if y != 0 else 0, mean_offset, deviation)))
        bonus = -1 + (2 / (1 + exp(-MCTSMeta.K_CONST * landa)))
        result = {'white': bonus[0], 'black': bonus[1]}
        return result

    def backup(self, node, turn, outcome, state: GameState):
        """
        Update the node statistics on the path from the passed node to root to reflect
        the outcome of a randomly simulated playout.

        """
        # Careful: The reward is calculated for player who just played
        # at the node and not the next player to play
        pl_length = [state.get_num_played()['white'], state.get_num_played()['black']]
        self.pl_list = append(self.pl_list, [pl_length], axis=0)
        bonus = self.modify_reward(pl_length)
        reward = -1 if outcome == turn else 1

        while node is not None:
            node.N += 1
            max_moves_played = max(state.get_num_played().values())

            if turn == GameMeta.PLAYERS['black']:
                qb_reward = reward + (reward * MCTSMeta.A_CONST * bonus['black']) \
                    if max_moves_played >= MCTSMeta.WARMUP_ROLLOUTS else reward
            else:
                qb_reward = reward + (reward * MCTSMeta.A_CONST * bonus['white']) \
                    if max_moves_played >= MCTSMeta.WARMUP_ROLLOUTS else reward

            node.Q += qb_reward
            turn = 1 if turn == 0 else 0
            node = node.parent
            reward = -reward

    def move(self, move):
        """
        Make the passed move and update the tree appropriately. It is
          designed to let the player choose an action manually (which might
          not be the best action).

        """
        if move in self.root.children:
            child = self.root.children[move]
            child.parent = None
            self.root = child
            self.root_state.play(child.move)
            moves_number, size = len(self.root_state.moves()), self.root_state.size
            initial_member = randint(moves_number // size, moves_number // 2)
            # initial_member = randint(divmod(moves_number, size)[0], divmod(moves_number, 2)[0])
            self.pl_list = asarray([[initial_member, initial_member]])
            return

        # if for whatever reason the move is not in the children of
        # the root just throw out the tree and start over
        self.root_state.play(move)
        self.root = Node()
