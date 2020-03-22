from math import sqrt, log
from copy import deepcopy
from uct_mcstsagent import Node, UctMctsAgent
from gamestate import GameState
from meta import *


class UCB1TunedNode(Node):
    """
    Node for the MCTS. Stores the move applied to reach this node from its parent,
    stats for the associated game position, children, parent and outcome
    (outcome==none unless the position ends the game).
    """
    @property
    def value(self, explore: float = MCTSMeta.EXPLORATION) -> float:
        """
        Calculate the UCT value of this node relative to its parent, the parameter
        "explore" specifies how much the value should favor nodes that have
        yet to be thoroughly explored versus nodes that seem to have a high win
        rate.
        Currently explore is set to one.

        """
        # if the node is not visited, set the value as infinity.
        if self.N == 0:
            return 0 if explore is 0 else GameMeta.INF
        else:
            avg = self.Q / self.N
            variance = avg * (1 - avg)
            return avg + explore * sqrt(log(self.parent.N) / self.N) * min(0.25, variance + sqrt(
                2 * log(self.parent.N) / self.N))


class UCB1TunedMctsAgent(UctMctsAgent):
    """
    Implementation of an agent that preforms MCTS for hex with UCB1-Tuned evaluation.

    """
    def __init__(self, state=GameState(8)):
        self.root_state = deepcopy(state)
        self.root = UCB1TunedNode()
        self.run_time = 0
        self.node_count = 0
        self.num_rollouts = 0

    @staticmethod
    def expand(parent: Node, state: GameState) -> bool:
        """
        Generate the children of the passed "parent" node based on the available
        moves in the passed gamestate and add them to the tree. hrth

        """
        children = []
        if state.winner != GameMeta.PLAYERS['none']:
            # game is over at this node so nothing to expand
            return False

        for move in state.moves():
            children.append(UCB1TunedNode(move, parent))

        parent.add_children(children)
        return True

    def move(self, move: tuple) -> None:
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
            return

        # if for whatever reason the move is not in the children of
        # the root just throw out the tree and start over
        self.root_state.play(move)
        self.root = UCB1TunedNode()

    def set_gamestate(self, state: GameMeta) -> None:
        """
        Set the root_state of the tree to the passed gamestate, this clears all
        the information stored in the tree since none of it applies to the new
        state.

        """
        self.root_state = deepcopy(state)
        self.root = UCB1TunedNode()
