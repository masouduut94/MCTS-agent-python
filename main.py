from time import clock
import random
from math import sqrt, log
from copy import copy, deepcopy
from sys import stderr
from queue import Queue
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import numpy as np


##############################################################################
##############################################################################
##########################                             #######################
##########################           GAMESTATE         #######################
##########################                             #######################
##############################################################################
##############################################################################



class gamestate:
  """
  Stores information representing the current state of a game of hex, namely
  the board and the current turn. Also provides functions for playing the game
  """
  # dictionary associating numbers with players
  PLAYERS = {"none": 0, "white": 1, "black": 2}

  # move value of -1 indicates the game has ended so no move is possible
  GAMEOVER = -1

  # represent edges in the union find strucure for win detection
  # EDGE1 is low & EDGE2 is high
  EDGE1 = 1
  EDGE2 = 2

  neighbor_patterns = ((-1, 0), (0, -1), (-1, 1), (0, 1), (1, 0), (1, -1))

  def __init__(self, size):
    """
    Initialize the game board and give white first turn.
    Also create our union find structures for win checking.
    """
    self.size = size
    self.toplay = self.PLAYERS["white"]
    self.board = np.zeros((size, size))
    self.board = np.int_(self.board)
    self.white_played = 0
    self.black_played = 0
    self.white_groups = unionfind()
    self.black_groups = unionfind()
    self.white_groups.set_ignored_elements([self.EDGE1, self.EDGE2])
    self.black_groups.set_ignored_elements([self.EDGE1, self.EDGE2])

  def play(self, cell):
    """
    Play a stone of the current turns color in the passed cell.
    """
    if (self.toplay == self.PLAYERS["white"]):
      self.place_white(cell)
      self.toplay = self.PLAYERS["black"]
    elif (self.toplay == self.PLAYERS["black"]):
      self.place_black(cell)
      self.toplay = self.PLAYERS["white"]

  def get_num_played(self):
    return {'white': self.white_played, 'black': self.black_played}

  def get_white_groups(self):
    return self.white_groups.get_groups()

  def get_black_groups(self):
    return self.black_groups.get_groups()

  def place_white(self, cell):
    """
    Place a white stone regardless of whose turn it is.
    """
    if (self.board[cell] == self.PLAYERS["none"]):
      self.board[cell] = self.PLAYERS["white"]
      self.white_played += 1
    else:
      raise ValueError("Cell occupied")
    # if the placed cell touches a white edge connect it appropriately
    if (cell[0] == 0):
      self.white_groups.join(self.EDGE1, cell)
    if (cell[0] == self.size - 1):
      self.white_groups.join(self.EDGE2, cell)
    # join any groups connected by the new white stone
    for n in self.neighbors(cell):
      if (self.board[n] == self.PLAYERS["white"]):
        self.white_groups.join(n, cell)

  def place_black(self, cell):
    """
    Place a black stone regardless of whose turn it is.
    """
    if (self.board[cell] == self.PLAYERS["none"]):
      self.board[cell] = self.PLAYERS["black"]
      self.black_played += 1
    else:
      raise ValueError("Cell occupied")
    # if the placed cell touches a black edge connect it appropriately
    if (cell[1] == 0):
      self.black_groups.join(self.EDGE1, cell)
    if (cell[1] == self.size - 1):
      self.black_groups.join(self.EDGE2, cell)
    # join any groups connected by the new black stone
    for n in self.neighbors(cell):
      if (self.board[n] == self.PLAYERS["black"]):
        self.black_groups.join(n, cell)
  
  def would_lose(self, cell, color):
    """
    Return True is the move indicated by cell and color would lose the game,
    False otherwise.
    """
    connect1 = False
    connect2 = False
    if color == self.PLAYERS["black"]:
      if cell[1] == 0:
        connect1 = True
      elif cell[1] == self.size - 1:
        connect2 = True
      for n in self.neighbors(cell):
        if self.black_groups.connected(self.EDGE1, n):
          connect1 = True
        elif self.black_groups.connected(self.EDGE2, n):
          connect2 = True
    elif color == self.PLAYERS["white"]:
      if cell[0] == 0:
        connect1 = True
      elif cell[0] == self.size - 1:
        connect2 = True
      for n in self.neighbors(cell):
        if self.white_groups.connected(self.EDGE1, n):
          connect1 = True
        elif self.white_groups.connected(self.EDGE2, n):
          connect2 = True
      
    return connect1 and connect2

  def turn(self):
    """
    Return the player with the next move.
    """
    return self.toplay

  def set_turn(self, player):
    """
    Set the player to take the next move.
    """
    if (player in self.PLAYERS.values() and player != self.PLAYERS["none"]):
      self.toplay = player
    else:
      raise ValueError('Invalid turn: ' + str(player))

  def winner(self):
    """
    Return a number corresponding to the winning player,
    or none if the game is not over.
    """
    if (self.white_groups.connected(self.EDGE1, self.EDGE2)):
      return self.PLAYERS["white"]
    elif (self.black_groups.connected(self.EDGE1, self.EDGE2)):
      return self.PLAYERS["black"]
    else:
      return self.PLAYERS["none"]

  def neighbors(self, cell):
    """
    Return list of neighbors of the passed cell.
    """
    x = cell[0]
    y = cell[1]
    return [(n[0] + x, n[1] + y) for n in self.neighbor_patterns
            if (0 <= n[0] + x and n[0] + x < self.size and 0 <= n[1] + y and n[1] + y < self.size)]

  def moves(self):
    """
    Get a list of all moves possible on the current board.
    """
    moves = []
    for y in range(self.size):
      for x in range(self.size):
        if self.board[x, y] == self.PLAYERS["none"]:
          moves.append((x, y))
    return moves

  def __str__(self):
    """
    Print an ascii representation of the game board.
    """
    white = 'W'
    black = 'B'
    empty = '.'
    ret = '\n'
    coord_size = len(str(self.size))
    offset = 1
    ret+=' '*(offset+1)
    for x in range(self.size):
      ret+=chr(ord('A')+x)+' '*offset*2
    ret+='\n'
    for y in range(self.size):
      ret+=str(y+1)+' '*(offset*2+coord_size-len(str(y+1)))
      for x in range(self.size):
        if(self.board[x, y] == self.PLAYERS["white"]):
          ret+=white
        elif(self.board[x,y] == self.PLAYERS["black"]):
          ret+=black
        else:
          ret+=empty
        ret+=' '*offset*2
      ret+=white+"\n"+' '*offset*(y+1)
    ret+=' '*(offset*2+1)+(black+' '*offset*2)*self.size
    return ret


##############################################################################
##############################################################################
##########################                             #######################
##########################           UNIONFIND         #######################
##########################                             #######################
##############################################################################
##############################################################################



class unionfind:
  """
  Unionfind data structure specialized for finding hex connections.
  Implementation inspired by UAlberta CMPUT 275 2015 class notes.
  """
  def __init__(self):
    """
    Initialize parent and rank as empty dictionarys, we will
    lazily add items as nessesary.
    """
    self.parent = {}
    self.rank = {}
    self.groups = {}
    self.ignored = []

  def join(self, x, y):
    """
    Merge the groups of x and y if they were not already,
    return False if they were already merged, true otherwise
    """
    rep_x = self.find(x)
    rep_y = self.find(y)

    if rep_x == rep_y:
      return False
    if self.rank[rep_x] < self.rank[rep_y]:
      self.parent[rep_x] = rep_y
    
      self.groups[rep_y].extend(self.groups[rep_x])
      del self.groups[rep_x]
    elif self.rank[rep_x] >self.rank[rep_y]:
      self.parent[rep_y] = rep_x
    
      self.groups[rep_x].extend(self.groups[rep_y])
      del self.groups[rep_y]      
    else:
      self.parent[rep_x] = rep_y
      self.rank[rep_y] += 1
    
      self.groups[rep_y].extend(self.groups[rep_x])
      del self.groups[rep_x]  
  
    return True

  def find(self, x):
    """
    Get the representative element associated with the set in
    which element x resides. Uses grandparent compression to compression
    the tree on each find operation so that future find operations are faster.
    """
    if x not in self.parent:
      self.parent[x] = x
      self.rank[x] = 0
      if x in self.ignored:
        self.groups[x] = []
      else:
        self.groups[x] = [x]

    px = self.parent[x]
    if x == px: return x

    gx = self.parent[px]
    if gx==px: return px

    self.parent[x] = gx

    return self.find(gx)

  def connected(self, x, y):
    """
    Check if two elements are in the same group.
    """
    return self.find(x)==self.find(y)

  def set_ignored_elements(self, ignore):
    """
    Elements in ignored 
    """
    self.ignored = ignore

  def get_groups(self):
    return self.groups




##############################################################################
##############################################################################
##########################                             #######################
##########################             NODE            #######################
##########################                             #######################
##############################################################################
##############################################################################




inf = float('inf')


class node:
  """
  Node for the MCTS. Stores the move applied to reach this node from its parent,
  stats for the associated game position, children, parent and outcome
  (outcome==none unless the position ends the game).
  """

  def __init__(self, move=None, parent=None):
    """
    Initialize a new node with optional move and parent and initially empty
    children list and rollout statistics and unspecified outcome.

    """
    self.move = move
    self.parent = parent
    self.N = 0  # times this position was visited
    self.Q = 0  # average reward (wins-losses) from this position
    self.Q_RAVE = 0 # times this move has been critical in a rollout
    self.N_RAVE = 0 # times this move has appeared in a rollout
    self.children = {}
    self.outcome = gamestate.PLAYERS["none"]

  def add_children(self, children):
    """
    Add a list of nodes to the children of this node.

    """
    for child in children:
      self.children[child.move] = child

  def value(self, explore):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate.
    Currently explore is set to one.

    """
    # if the node is not visited, set the value as infinity.
    if (self.N == 0):
      if (explore == 0):
        return 0
      else:
        return inf  # infinity (maximum value)
    else:
      return self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)



##############################################################################
##############################################################################
################                                                  ############
################            BASIC MCTS AGENT USING UCT            ############
################                                                  ############
##############################################################################
##############################################################################



class mctsagent:
  """
  Basic no frills implementation of an agent that preforms MCTS for hex.

  """
  EXPLORATION = 0.5

  def __init__(self, state=gamestate(8)):
    self.rootstate = deepcopy(state)
    self.root = node()
    self.run_time = 0
    self.node_count = 0
    self.num_rollouts = 0

  def search(self, time_budget):
    """
    Search and update the search tree for a 
    specified amount of time in secounds.

    """
    startTime = clock()
    num_rollouts = 0

    # do until we exceed our time budget
    while (clock() - startTime < time_budget):
      node, state = self.select_node()
      turn = state.turn()
      outcome = self.roll_out(state)
      self.backup(node, turn, outcome)
      num_rollouts += 1
    run_time = clock() - startTime
    node_count = self.tree_size()
    self.run_time = run_time
    self.node_count = node_count
    self.num_rollouts = num_rollouts

  def select_node(self):
    """
    Select a node in the tree to preform a single simulation from.

    """
    node = self.root
    state = deepcopy(self.rootstate)

    #stop if we find reach a leaf node
    while(len(node.children) !=0 ):
      #decend to the maximum value node, break ties at random
      max_node = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION))
      max_value = max_node.value(self.EXPLORATION)
      max_nodes = [n for n in node.children.values() 
                   if n.value(self.EXPLORATION) == max_value]
      node = random.choice(max_nodes)
      state.play(node.move)

      #if some child node has not been explored select it before expanding
      #other children
      if node.N == 0:
        return (node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(node, state)):
      node = random.choice(list(node.children.values()))
      state.play(node.move)
    return (node, state)

  def expand(self, parent, state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.

    """
    children = []
    if (state.winner() != gamestate.PLAYERS["none"]):
      # game is over at this node so nothing to expand
      return False

    for move in state.moves():
      children.append(node(move, parent))

    parent.add_children(children)
    return True

  def roll_out(self, state):
    """
    Simulate an entirely random game from the passed state and return the winning
    player.

    """
    moves = state.moves()  # Get a list of all possible moves in current state of the game

    while (state.winner() == gamestate.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)

    return state.winner()

  def backup(self, node, turn, outcome):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.

    """
    # Careful: The reward is calculated for player who just played
    # at the node and not the next player to play
    reward = 0 if outcome == turn else 1

    while node != None:
      node.N += 1
      node.Q += reward
      node = node.parent
      reward = 0 if reward == 1 else 1

  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    if (self.rootstate.winner() != gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    # choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children.values(), key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children.values() if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move

  def move(self, move):
    """
    Make the passed move and update the tree approriately. It is 
  designed to let the player choose an action manually (which might
  not be the best action).

    """
    if move in self.root.children:
      child = self.root.children[move]
      child.parent = None
      self.root = child
      self.rootstate.play(child.move)
      return

    # if for whatever reason the move is not in the children of
    # the root just throw out the tree and start over
    self.rootstate.play(move)
    self.root = node()

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new
    state.

    """
    self.rootstate = deepcopy(state)
    self.root = node()

  def statistics(self):
    return(self.num_rollouts, self.node_count, self.run_time)

  def tree_size(self):
    """
    Count nodes in tree by BFS.
    """
    Q = Queue()
    count = 0
    Q.put(self.root)
    while not Q.empty():
      node = Q.get()
      count +=1
      for child in node.children.values():
        Q.put(child)
    return count




##############################################################################
##############################################################################
##############                                                  ##############
##############        RAPID-ACTION-VALUE-ESTIMATION NODE        ##############
##############                                                  ##############
##############################################################################
##############################################################################


class rave_node(node):
  def __init__(self, move = None, parent = None):
    """
    Initialize a new node with optional move and parent and initially empty
    children list and rollout statistics and unspecified outcome.

    """
    self.move = move
    self.parent = parent
    self.N = 0 #times this position was visited
    self.Q = 0 #average reward (wins-losses) from this position
    self.Q_RAVE = 0 # times this move has been critical in a rollout
    self.N_RAVE = 0 # times this move has appeared in a rollout
    self.children = {}

  def add_children(self, children):
    for child in children:
      self.children[child.move] = child

  def value(self, explore, rave_const):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate. 
    Currently explore is set to zero when choosing the best move to play so
    that the move with the highest winrate is always chosen. When searching
    explore is set to EXPLORATION specified above.

    """
    # unless explore is set to zero, maximally favor unexplored nodes
    if(self.N == 0):
      if(explore == 0):
          return 0
      else:
        return inf
    else:
      # rave valuation:
      alpha = max(0,(rave_const - self.N)/rave_const)
      UCT = self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)
      AMAF = self.Q_RAVE / self.N_RAVE if self.N_RAVE is not 0 else 0
      return (1-alpha) * UCT + alpha * AMAF




##############################################################################
##############################################################################
###########                                                      #############
###########          RAPID-ACTION-VALUE-ESTIMATION AGENT         #############
###########                                                      #############
##############################################################################
##############################################################################




class rave_mctsagent(mctsagent):
  RAVE_CONSTANT = 300

  def special_case(self, last_move):
    return None

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new 
    state.
    """
    self.rootstate = deepcopy(state)
    self.root = rave_node()


  def move(self, move):
    """
    Make the passed move and update the tree approriately.

    """
    if move in self.root.children:
      child = self.root.children[move]
      child.parent = None
      self.root = child
      self.rootstate.play(child.move)
      return

    # if for whatever reason the move is not in the children of
    # the root just throw out the tree and start over
    self.rootstate.play(move)
    self.root = rave_node()


  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    if(self.rootstate.winner() != gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    # choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children.values(), key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children.values() if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move


  def search(self, time_budget):
    """
    Search and update the search tree for a specified amount of time in secounds.
    """
    startTime = clock()
    num_rollouts = 0

    # do until we exceed our time budget
    while(clock() - startTime <time_budget):
      node, state = self.select_node()
      turn = state.turn()
      outcome, black_rave_pts, white_rave_pts = self.roll_out(state)
      self.backup(node, turn, outcome, black_rave_pts, white_rave_pts)
      num_rollouts += 1
    run_time = clock() - startTime
    node_count = self.tree_size()
    self.run_time = run_time
    self.node_count = node_count
    self.num_rollouts = num_rollouts

  def select_node(self):
    """
    Select a node in the tree to preform a single simulation from.
    """
    node = self.root
    state = deepcopy(self.rootstate)

    # stop if we reach a leaf node
    while(len(node.children)!= 0):
      max_value = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION, self.RAVE_CONSTANT)).value(self.EXPLORATION, self.RAVE_CONSTANT)
      # descend to the maximum value node, break ties at random
      max_nodes = [n for n in node.children.values() if n.value(self.EXPLORATION, self.RAVE_CONSTANT) == max_value]
      node = random.choice(max_nodes)
      state.play(node.move)

      #if some child node has not been explored select it before expanding
      #other children
      if node.N == 0:
        return (node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(node, state)):
      node = random.choice(list(node.children.values()))
      state.play(node.move)
    return (node, state)


  def expand(self, parent, state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.
    """
    children = []
    if(state.winner() != gamestate.PLAYERS["none"]):
      #game is over at this node so nothing to expand
      return False


    for move in state.moves():
      children.append(rave_node(move, parent))

    parent.add_children(children)
    return True


  def roll_out(self, state):
    """
    Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.

    """
    moves = state.moves()
    while(state.winner() == gamestate.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)

    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x,y)] == gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
        elif state.board[(x,y)] == gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))

    return state.winner(), black_rave_pts, white_rave_pts


  def backup(self, node, turn, outcome, black_rave_pts, white_rave_pts):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.
    """
    # note that reward is calculated for player who just played
    # at the node and not the next player to play
    reward = -1 if outcome == turn else 1

    while node!=None:
      if turn == gamestate.PLAYERS["white"]:
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
      if turn == gamestate.PLAYERS["black"]:
        turn = gamestate.PLAYERS["white"]
      else:
        turn = gamestate.PLAYERS["black"]
      reward = -reward
      node = node.parent


  def statistics(self):
    return(self.num_rollouts, self.node_count, self.run_time)


  def tree_size(self):
    """
    Count nodes in tree by BFS.
    """
    Q = Queue()
    count = 0
    Q.put(self.root)
    while not Q.empty():
      node = Q.get()
      count +=1
      for child in node.children.values():
        Q.put(child)
    return count



##############################################################################
##############################################################################
######################                                    ####################
######################         DECISIVE-MOVE AGENT        ####################
######################                                    ####################
##############################################################################
##############################################################################




class decisive_move_mctsagent(rave_mctsagent):

  def special_case(self, last_move):
    return None

  def roll_out(self, state):
    """
    Simulate a random game except that we play all known critical cells
    first, return the winning player and record critical cells at the end.
    """
    moves = state.moves()
    good_moves = moves.copy()
    good_opponent_moves = moves.copy()
    to_play = state.turn()
    
    while(state.winner() == gamestate.PLAYERS["none"]):
      done = False
      while len(good_moves) > 0 and not done:
        move = random.choice(good_moves)
        good_moves.remove(move)
        if not state.would_lose(move, to_play):
          state.play(move)
          moves.remove(move)
          if move in good_opponent_moves:
            good_opponent_moves.remove(move)
          done = True
      
      if not done:    
        move = random.choice(moves)
        state.play(move)
        moves.remove(move)
        if move in good_opponent_moves:
          good_opponent_moves.remove(move)
          
      good_moves, good_opponent_moves = good_opponent_moves, good_moves
    
    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x,y)] == gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
        elif state.board[(x,y)] == gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))

    return state.winner(), black_rave_pts, white_rave_pts



##############################################################################
##############################################################################
######################                                    ####################
######################       LAST GOOD REPLY AGENT        ####################
######################                                    ####################
##############################################################################
##############################################################################


class lgr_mctsagent(rave_mctsagent):

  def __init__(self, state=gamestate(8)):
    super().__init__(state)
    self.black_reply = {}
    self.white_reply = {}

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new 
    state.
    """
    super().set_gamestate(state)
    self.white_reply = {}
    self.black_reply = {}  

  def roll_out(self, state):
    """
    Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end.
    
    """
    moves = state.moves()
    first = state.turn()
    if first == gamestate.PLAYERS["black"]:
      current_reply = self.black_reply
      other_reply = self.white_reply
    else:
      current_reply = self.white_reply
      other_reply = self.black_reply
    black_moves = []
    white_moves = []
    last_move = None
    while(state.winner() == gamestate.PLAYERS["none"]):
      if last_move in current_reply:
        move = current_reply[last_move]
        if move not in moves or random.random() > 0.5:
          move = random.choice(moves)
      else:
        move = random.choice(moves)
      if state.turn() == gamestate.PLAYERS["black"]:
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
        if state.board[(x,y)] == gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
        elif state.board[(x,y)] == gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))
    
    # This part of the algorithm probably deals with adjusting 
    # the indeces of the arrays.
    
    offset = 0
    skip = 0          
    if state.winner() == gamestate.PLAYERS["black"]:
      
      if first == gamestate.PLAYERS["black"]:
        offset = 1
      if state.turn() == gamestate.PLAYERS["black"]:
        skip = 1
      for i in range(len(white_moves) - skip):
        self.black_reply[white_moves[i]] = black_moves[i + offset]
    else:
      if first == gamestate.PLAYERS["white"]:
        offset = 1
      if state.turn() == gamestate.PLAYERS["white"]:
        skip = 1
      for i in range(len(black_moves) - skip):
        self.white_reply[black_moves[i]] = white_moves[i + offset]

    return state.winner(), black_rave_pts, white_rave_pts
  


##############################################################################
##############################################################################
######################                                    ####################
######################           POOLRAVE AGENT           ####################
######################                                    ####################
##############################################################################
##############################################################################



class poolrave_mctsagent(rave_mctsagent):

  def __init__(self, state=gamestate(8)):
    super().__init__(state)
    self.black_rave = {}
    self.white_rave = {} 
  

  def special_case(self, last_move):
    return None


  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new 
    state.
    """
    self.rootstate = deepcopy(state)
    self.root = rave_node()
    self.white_reply = {}
    self.black_reply = {}


  def roll_out(self, state):
    """Simulate a random game except that we play all known critical
    cells first, return the winning player and record critical cells at the end."""
    moves = state.moves()
    black_rave_moves = sorted(self.black_rave.keys(),
                              key=lambda cell: self.black_rave[cell])
    white_rave_moves = sorted(self.white_rave.keys(),
                              key=lambda cell: self.white_rave[cell])
    black_pool = []
    white_pool = []

    i = 0
    while len(black_pool) < 10 and i < len(black_rave_moves):
      if black_rave_moves[i] in moves:
        black_pool.append(black_rave_moves[i])
      i += 1
    i = 0
    while len(white_pool) < 10 and i < len(white_rave_moves):
      if white_rave_moves[i] in moves:
        white_pool.append(white_rave_moves[i])
      i += 1
    num_pool = 0
    while(state.winner() == gamestate.PLAYERS["none"]):
      move = None
      if len(black_pool) > 0 and state.turn() == gamestate.PLAYERS["black"]:
        move = random.choice(black_pool)
        num_pool += 1
      elif len(white_pool) > 0:
        move = random.choice(white_pool)
        num_pool += 1
      if random.random() > 0.5 or not move or move not in moves:
        move = random.choice(moves)
        num_pool -= 1

      state.play(move)
      moves.remove(move)
    
    black_rave_pts = []
    white_rave_pts = []

    for x in range(state.size):
      for y in range(state.size):
        if state.board[(x,y)] == gamestate.PLAYERS["black"]:
          black_rave_pts.append((x,y))
          if state.winner() == gamestate.PLAYERS["black"]:
            if (x, y) in self.black_rave:
              self.black_rave[(x, y)] += 1
            else:
              self.black_rave[(x, y)] = 1
          else:
            if (x, y) in self.black_rave:
              self.black_rave[(x, y)] -= 1
            else:
              self.black_rave[(x, y)] = -1
        elif state.board[(x,y)] == gamestate.PLAYERS["white"]:
          white_rave_pts.append((x,y))
          if state.winner() == gamestate.PLAYERS["white"]:
            if (x, y) in self.white_rave:
              self.white_rave[(x, y)] += 1
            else:
              self.white_rave[(x, y)] = 1
          else:
            if (x, y) in self.white_rave:
              self.white_rave[(x, y)] -= 1
            else:
              self.white_rave[(x, y)] = -1

    return state.winner(), black_rave_pts, white_rave_pts   





##############################################################################
##############################################################################
######################                                    ####################
######################           UCB1-TUNED NODE          ####################
######################                                    ####################
##############################################################################
##############################################################################



class ucb1_node:
  """
  Node for the MCTS. Stores the move applied to reach this node from its parent,
  stats for the associated game position, children, parent and outcome
  (outcome==none unless the position ends the game).
  """

  def __init__(self, move=None, parent=None):

    """
    Initialize a new node with optional move and parent and initially empty
    children list and rollout statistics and unspecified outcome.

    """
    self.move = move
    self.parent = parent
    self.N = 0  # number of visits
    self.Q = 0  # average reward (wins-losses) from this position
    self.Q_RAVE = 0 # times this move has been critical in a rollout
    self.N_RAVE = 0 # times this move has appeared in a rollout
    self.children = {}

  def add_children(self, children):
    """
    Add a list of nodes to the children of this node.

    """
    for child in children:
      self.children[child.move] = child

  def value(self, explore):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate.
    Currently explore is set to one.

    """
    # if the node is not visited, set the value as infinity.
    if (self.N == 0):
      if (explore == 0):
        return 0
      else:
        return inf  # infinity (maximum value)
    else:
      avg = self.Q / self.N
      variance = avg * (1 - avg)
      return avg + explore * sqrt(log(self.parent.N) / self.N) \
    * min(0.25, variance + sqrt(2 * log(self.parent.N) / self.N))



##############################################################################
##############################################################################
######################                                    ####################
######################          UCB1-TUNED AGENT          ####################
######################                                    ####################
##############################################################################
##############################################################################





class ucb1_tuned_agent:
  """
  Basic no frills implementation of an agent that preforms MCTS for hex.

  """
  EXPLORATION = 0.5

  def __init__(self, state=gamestate(8)):
    self.rootstate = deepcopy(state)
    self.root = ucb1_node()
    self.run_time = 0
    self.node_count = 0
    self.num_rollouts = 0

  def search(self, time_budget):
    """
    Search and update the search tree for a 
    specified amount of time in secounds.

    """
    startTime = clock()
    num_rollouts = 0

    # do until we exceed our time budget
    while (clock() - startTime < time_budget):
      node, state = self.select_node()
      turn = state.turn()
      outcome = self.roll_out(state)
      self.backup(node, turn, outcome)
      num_rollouts += 1
    run_time = clock() - startTime
    node_count = self.tree_size()
    self.run_time = run_time
    self.node_count = node_count
    self.num_rollouts = num_rollouts

  def select_node(self):
    """
    Select a node in the tree to preform a single simulation from.

    """
    node = self.root
    state = deepcopy(self.rootstate)

    #stop if we find reach a leaf node
    while(len(node.children) !=0 ):
      #decend to the maximum value node, break ties at random
      max_node = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION))
      max_value = max_node.value(self.EXPLORATION)
      max_nodes = [n for n in node.children.values() 
                   if n.value(self.EXPLORATION) == max_value]
      node = random.choice(max_nodes)
      state.play(node.move)

      #if some child node has not been explored select it before expanding
      #other children
      if node.N == 0:
        return (node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(node, state)):
      node = random.choice(list(node.children.values()))
      state.play(node.move)
    return (node, state)

  def expand(self, parent, state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.

    """
    children = []
    if (state.winner() != gamestate.PLAYERS["none"]):
      # game is over at this node so nothing to expand
      return False

    for move in state.moves():
      children.append(ucb1_node(move, parent))

    parent.add_children(children)
    return True

  def roll_out(self, state):
    """
    Simulate an entirely random game from the passed state and return the winning
    player.

    """
    moves = state.moves()  # Get a list of all possible moves in current state of the game

    while (state.winner() == gamestate.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)

    return state.winner()

  def backup(self, node, turn, outcome):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.

    """
    # Careful: The reward is calculated for player who just played
    # at the node and not the next player to play
    reward = 0 if outcome == turn else 1

    while node != None:
      node.N += 1
      node.Q += reward
      node = node.parent
      reward = 0 if reward == 1 else 1

  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    if (self.rootstate.winner() != gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    # choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children.values(), key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children.values() if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move

  def move(self, move):
    """
    Make the passed move and update the tree approriately. It is 
  designed to let the player choose an action manually (which might
  not be the best action).

    """
    if move in self.root.children:
      child = self.root.children[move]
      child.parent = None
      self.root = child
      self.rootstate.play(child.move)
      return

    # if for whatever reason the move is not in the children of
    # the root just throw out the tree and start over
    self.rootstate.play(move)
    self.root = ucb1_node()

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new
    state.

    """
    self.rootstate = deepcopy(state)
    self.root = ucb1_node()

  def statistics(self):
    return(self.num_rollouts, self.node_count, self.run_time)

  def tree_size(self):
    """
    Count nodes in tree by BFS.
    """
    Q = Queue()
    count = 0
    Q.put(self.root)
    while not Q.empty():
      node = Q.get()
      count +=1
      for child in node.children.values():
        Q.put(child)
    return count





##############################################################################
##############################################################################
######                                                               #########
######      MOVE AVERAGE SAMPLING TECHNIQUE COMBINED WITH RAVE       #########
######                                                               #########
##############################################################################
##############################################################################



class rave_mast_mctsagent(rave_mctsagent):
  """
  Basic no frills implementation of an agent that preforms MCTS for hex.

  """
  EPSILON = 0.4
  GIBBS_MEASURE_CONSTANT = 10
  def __init__(self, state=gamestate(8)):
    super().__init__(state)
    all_moves = self.rootstate.moves()
    wins = [0 for i in range(2 * len(all_moves))]
    playout_number = [0 for i in range(2 * len(all_moves))]
    player = list(map(lambda i: 1 if i >= len(all_moves) else 2,
               [i for i in range(2 * len(all_moves))]))
    moves_stored = list(map(lambda i: all_moves[i] if divmod(i, len(all_moves))[0] != 1 \
            else all_moves[divmod(i, len(all_moves))[1]],
            [i for i in range(2 * len(all_moves))]))
    data = [moves_stored, player, wins, playout_number]
    # the main table for storing results
    self.scoreboard = np.asarray(data)

  def special_case(self, last_move):
    return None

  def roll_out(self, state):
    """
    Simulate an entirely random game from the passed state and return the winning
    player.

    """
    # Get a list of all possible moves in current state of the game
    moves = state.moves()
    state_table = self.scoreboard[:, np.array([move in moves for move in self.scoreboard[0]])]
    black_table = np.delete(state_table[:, state_table[1, :] == 2], 1, 0)
    white_table = np.delete(state_table[:, state_table[1, :] == 1], 1, 0)
    # black_table creation
    black_q = list(map(lambda x, y: np.exp((x/y) / self.GIBBS_MEASURE_CONSTANT) if y != 0 else 0, black_table[1, :], black_table[2, :]))
    black_table = np.vstack((black_table, black_q))
    # white_table creation
    white_q = list(map(lambda x, y: np.exp((x/y) / self.GIBBS_MEASURE_CONSTANT) if y != 0 else 0, white_table[1, :], white_table[2, :]))
    white_table = np.vstack((white_table, white_q))
    moves_played = []
    while (state.winner() == gamestate.PLAYERS["none"]):
      # Epsilon Greedy
      if random.random() >= self.EPSILON:
        if state.turn() == gamestate.PLAYERS["white"]:
          total = np.sum(white_table[3, :])
          length = white_table.shape[1]
          weights = white_table[3, :] / total if total != 0 else [1 / length for i in white_table[3,:]]
          move = np.random.choice(white_table[0, :], p=tuple(weights))
        else:
          total = np.sum(black_table[3, :])
          length = black_table.shape[1]
          weights = black_table[3, :] / total if total != 0 else [1 / length for i in black_table[3,:]]
          move = np.random.choice(black_table[0, :], p=tuple(weights))
      else:
        if state.turn() == gamestate.PLAYERS["white"]:
          move = np.random.choice(white_table[0, :])
        else:
          move = np.random.choice(black_table[0, :])
      # removing move from white and black table   # done
      # updating weights
      state.play(move)
      moves_played.append(move)
      white_table = white_table[:, np.array([item != move for item in white_table[0]])]
      black_table = black_table[:, np.array([item != move for item in black_table[0]])]
    
    black_moves = []
    white_moves = []

    for item in moves_played:
      if state.board[item] == gamestate.PLAYERS["black"]:
        black_moves.append(item)
      elif state.board[item] == gamestate.PLAYERS['white']:
        white_moves.append(item)

    return state.winner(), black_moves, white_moves

  def backup(self, node, turn, outcome, white_moves, black_moves):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.

    """
    # Careful: The reward is calculated for player who just played
    # at the node and not the player who is just ready to play at the turn.
    reward = -1 if outcome == turn else 1

    while node!= None:
      if turn == gamestate.PLAYERS["white"]:
        for point in white_moves:
          if point in node.children:
            node.children[point].Q_RAVE += reward
            node.children[point].N_RAVE += 1
      else:
        for point in black_moves:
          if point in node.children:
            node.children[point].Q_RAVE += reward
            node.children[point].N_RAVE += 1

      node.N += 1
      node.Q += reward
      if turn == gamestate.PLAYERS["black"]:
        turn = gamestate.PLAYERS["white"]
      else:
        turn = gamestate.PLAYERS["black"]
      reward = -reward
      node = node.parent
    
    if outcome == gamestate.PLAYERS['black']:
      for i in range(self.scoreboard.shape[1]):
        for move in black_moves:
          # if move in scoreboard matches and it was for the black player
          if self.scoreboard[0,i] == move and self.scoreboard[1,i] == gamestate.PLAYERS['black']:
            # for winner update the playouts and the wins
            self.scoreboard[3, i] += 1
            self.scoreboard[2, i] += 1

        for move in white_moves:
          if self.scoreboard[0,i] == move and self.scoreboard[1,i] == gamestate.PLAYERS['white']:
            # for loser only update the playouts
            self.scoreboard[3,i] += 1
    else:
      for i in range(self.scoreboard.shape[1]):
        for move in black_moves:
          # if move in scoreboard matches and it was for the white player
          if self.scoreboard[0,i] == move and self.scoreboard[1,i] == gamestate.PLAYERS['black']:
            # for loser only update the playouts
            self.scoreboard[3, i] += 1

        for move in white_moves:
          if self.scoreboard[0,i] == move and self.scoreboard[1,i] == gamestate.PLAYERS['white']:
            # for winner update the playouts and the wins
            self.scoreboard[3,i] += 1
            self.scoreboard[2, i] += 1

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new
    state.

    """
    super().set_gamestate(state)
    all_moves = self.rootstate.moves()
    wins = [0 for i in range(2 * len(all_moves))]
    playout_number = [0 for i in range(2 * len(all_moves))]
    player = list(map(lambda i: 1 if i >= len(all_moves) else 2,
               [i for i in range(2 * len(all_moves))]))
    moves_stored = list(map(lambda i: all_moves[i] if divmod(i, len(all_moves))[0] != 1 \
            else all_moves[divmod(i, len(all_moves))[1]],
            [i for i in range(2 * len(all_moves))]))
    data = [moves_stored, player, wins, playout_number]
    # the main table for storing results
    self.scoreboard = np.asarray(data)




##############################################################################
##############################################################################
################                                              ################
################       QUALITY-BASED REWARDS UCT NODE         ################
################                                              ################
##############################################################################
##############################################################################



class qb_node:
  """
  Node for the MCTS. Stores the move applied to reach this node from its parent,
  stats for the associated game position, children, parent and outcome
  (outcome==none unless the position ends the game).
  """

  def __init__(self, move=None, parent=None):
    """
    Initialize a new node with optional move and parent and initially empty
    children list and rollout statistics and unspecified outcome.

    """
    self.move = move
    self.parent = parent
    self.N = 0  # times this position was visited
    self.Q = 0  # average reward (wins-losses) from this position
    self.Q_RAVE = 0 # times this move has been critical in a rollout
    self.N_RAVE = 0 # times this move has appeared in a rollout
    self.children = {}

  def add_children(self, children):
    """
    Add a list of nodes to the children of this node.

    """
    for child in children:
      self.children[child.move] = child

  def value(self, explore):
    """
    Calculate the UCT value of this node relative to its parent, the parameter
    "explore" specifies how much the value should favor nodes that have
    yet to be thoroughly explored versus nodes that seem to have a high win
    rate.
    Currently explore is set to one.

    """
    # if the node is not visited, set the value as infinity.
    if (self.N == 0):
      if (explore == 0):
        return 0
      else:
        return inf  # infinity (maximum value)
    else:
      return self.Q / self.N + explore * sqrt(2 * log(self.parent.N) / self.N)



##############################################################################
##############################################################################
################                                              ################
################       QUALITY-BASED REWARDS UCT AGENT        ################
################                                              ################
##############################################################################
##############################################################################



class qb_mctsagent:
  """
  Basic no frills implementation of an agent that preforms MCTS for hex.

  """
  EXPLORATION = 0.5

  def __init__(self, state=gamestate(8)):
    self.rootstate = deepcopy(state)
    self.root = qb_node()
    self.run_time, self.node_count, self.num_rollouts, self.num_moves_played = 0, 0, 0, 0
    moves_number, size = len(self.rootstate.moves()), self.rootstate.size
    initial_member = np.random.randint(divmod(moves_number, size)[0], divmod(moves_number, 2)[0])
    self.pl_list = np.asarray([[initial_member, initial_member]])

  def search(self, time_budget):
    """
    Search and update the search tree for a 
    specified amount of time in secounds.

    """
    startTime = clock()
    num_rollouts = 0

    # do until we exceed our time budget
    while (clock() - startTime < time_budget):
      node, state = self.select_node()
      turn = state.turn()
      outcome, pl_length = self.roll_out(state)
      self.backup(node, turn, outcome, pl_length)
      num_rollouts += 1
    run_time = clock() - startTime
    node_count = self.tree_size()
    self.run_time = run_time
    self.node_count = node_count
    self.num_rollouts = num_rollouts

  def select_node(self):
    """
    Select a node in the tree to preform a single simulation from.

    """
    node = self.root
    state = deepcopy(self.rootstate)

    #stop if we find reach a leaf node
    while(len(node.children) !=0 ):
      #decend to the maximum value node, break ties at random
      max_node = max(node.children.values(), key = lambda n: n.value(self.EXPLORATION))
      max_value = max_node.value(self.EXPLORATION)
      max_nodes = [n for n in node.children.values() 
                   if n.value(self.EXPLORATION) == max_value]
      node = random.choice(max_nodes)
      state.play(node.move)
      #if some child node has not been explored select it before expanding
      #other children
      if node.N == 0:
        return (node, state)

    #if we reach a leaf node generate its children and return one of them
    #if the node is terminal, just return the terminal node
    if(self.expand(node, state)):
      node = random.choice(list(node.children.values()))
      state.play(node.move)
    return (node, state)

  def expand(self, parent, state):
    """
    Generate the children of the passed "parent" node based on the available
    moves in the passed gamestate and add them to the tree.

    """
    children = []
    if (state.winner() != gamestate.PLAYERS["none"]):
      # game is over at this node so nothing to expand
      return False

    for move in state.moves():
      children.append(qb_node(move, parent))

    parent.add_children(children)
    return True

  def roll_out(self, state):
    """
    Simulate an entirely random game from the passed state and return the winning
    player.

    """
    moves = state.moves()  # Get a list of all possible moves in current state of the game

    while (state.winner() == gamestate.PLAYERS["none"]):
      move = random.choice(moves)
      state.play(move)
      moves.remove(move)
    num_played = [state.get_num_played()['white'], state.get_num_played()['black']]
    return (state.winner(), num_played)

  def modify_reward(self, pl_length):
    """
    Takes the simulation length as the input and modifies it based on the 
    Quality-Based rewards
    
    """
    k = 10
    mean = np.mean(self.pl_list, axis=0)
    mean_offset = np.asarray([mean[0] - pl_length[0], mean[1] - pl_length[1]])
    deviation = np.std(self.pl_list, axis=0)
    landa = np.asarray(list(map(lambda x, y: x/y if y != 0 else 0, mean_offset, deviation)))
    bonus = -1 + (2 / (1 + np.exp(-k * landa)))
    a = {'white':bonus[0], 'black':bonus[1]}
    return a

  def backup(self, node, turn, outcome, pl_length):
    """
    Update the node statistics on the path from the passed node to root to reflect
    the outcome of a randomly simulated playout.

    """
    # Careful: The reward is calculated for player who just played
    # at the node and not the next player to play
    a = 0.25
    self.pl_list = np.append(self.pl_list, [pl_length], axis=0)
    bonus = self.modify_reward(pl_length)
    reward = -1 if outcome == turn else 1

    while node != None:
      node.N += 1
      if turn == gamestate.PLAYERS['black']:
        if self.num_moves_played >= 7:
          q_reward = reward + (reward * a * bonus['black'])
        else:
          q_reward = reward
      else:
        if self.num_moves_played >= 7:
          q_reward = reward + (reward * a * bonus['white'])
        else:
          q_reward = reward
      node.Q += q_reward
      turn = 1 if turn == 0 else 0
      node = node.parent
      reward = -reward

  def best_move(self):
    """
    Return the best move according to the current tree.

    """
    if (self.rootstate.winner() != gamestate.PLAYERS["none"]):
      return gamestate.GAMEOVER

    # choose the move of the most simulated node breaking ties randomly
    max_value = max(self.root.children.values(), key = lambda n: n.N).N
    max_nodes = [n for n in self.root.children.values() if n.N == max_value]
    bestchild = random.choice(max_nodes)
    return bestchild.move

  def move(self, move):
    """
    Make the passed move and update the tree approriately. It is 
	  designed to let the player choose an action manually (which might
	  not be the best action).

    """
    if move in self.root.children:
      child = self.root.children[move]
      child.parent = None
      self.root = child
      self.rootstate.play(child.move)
      self.num_moves_played += 1
      moves_number, size = len(self.rootstate.moves()), self.rootstate.size
      initial_member = np.random.randint(divmod(moves_number, size)[0], divmod(moves_number, 2)[0])
      self.pl_list = np.asarray([[initial_member, initial_member]])
      return

    # if for whatever reason the move is not in the children of
    # the root just throw out the tree and start over
    self.rootstate.play(move)
    self.root = qb_node()

  def set_gamestate(self, state):
    """
    Set the rootstate of the tree to the passed gamestate, this clears all
    the information stored in the tree since none of it applies to the new
    state.

    """
    self.rootstate = deepcopy(state)
    self.root = qb_node()

  def statistics(self):
    return(self.num_rollouts, self.node_count, self.run_time)

  def tree_size(self):
    """
    Count nodes in tree by BFS.
    """
    Q = Queue()
    count = 0
    Q.put(self.root)
    while not Q.empty():
      node = Q.get()
      count +=1
      for child in node.children.values():
        Q.put(child)
    return count




##############################################################################
##############################################################################
###############                                                  #############
###############             GRAPHICAL USER INTERFACE             #############
###############                                                  #############
##############################################################################
##############################################################################


class Gui:
  """
  This class is built to let the user have a better interaction with
  game.
  inputs =>
  root = Tk() => an object which inherits the traits of Tkinter class
  agent = an object which inherit the traits of mctsagent class.

  """

  agent_type = {1:"UCT", 2:"RAVE", 3:"LAST-GOOD-REPLY", 4:"POOLRAVE", 5:"DECISIVE-MOVE", 6:"UCB1-TUNED", 7: "RAVE-MAST"}
  AGENTS = {"UCT": mctsagent,
              "RAVE": rave_mctsagent,
              "LAST-GOOD-REPLY": lgr_mctsagent,
              "POOLRAVE": poolrave_mctsagent,
              "DECISIVE-MOVE": decisive_move_mctsagent,
              "RAVE-MAST": rave_mast_mctsagent,
              "UCB1-TUNED": ucb1_tuned_agent}

  def __init__(self, root, agent_name='UCT'):
    self.root = root
    self.root.geometry('1366x690+0+0')
    self.agent_name = agent_name
    try:
      self.agent = self.AGENTS[agent_name]()
    except KeyError:
      print("Unknown agent defaulting to basic")
      self.agent_name = "uct"
      self.agent = self.AGENTS[agent_name]()
    self.game = gamestate(8)
    self.agent.set_gamestate(self.game)
    self.time = 1
    self.root.configure(bg='#363636')
    self.colors = {'white': '#ffffff',
                   'milk': '#e9e5e5',
                   'red': '#9c0101',
                   'orange': '#ee7600',
                   'yellow': '#f4da03',
                   'green': '#00ee76',
                   'cyan': '#02adfd',
                   'blue': '#0261fd',
                   'purple': '#9c02fd',
                   'gray1': '#958989',
                   'gray2': '#3e3e3e',
                   'black': '#000000'}
    global bg
    bg = self.colors['gray2']
    self.last_move = None
    self.frame_board = Frame(self.root)  # main frame for the play board
    self.canvas = Canvas(self.frame_board, bg=bg)
    self.scroll_y = ttk.Scrollbar(self.frame_board, orient=VERTICAL)
    self.scroll_x = ttk.Scrollbar(self.frame_board, orient=HORIZONTAL)

    # the notebook frame which holds the left panel frames

    self.notebook = ttk.Notebook(self.frame_board, width=350)
    self.panel_game = Frame(self.notebook, highlightbackground=self.colors['white'])
    self.developers = Frame(self.notebook, highlightbackground=self.colors['white'])

    # Registering variables for: 

    self.game_size_value = IntVar()  # size of the board
    self.game_time_value = IntVar()  # time of CPU player
    self.game_turn_value = IntVar()  # defines whose turn is it

    self.switch_agent_value = IntVar()  # defines which agent to play against
    self.switch_agent_value.set(1)

    self.game_turn_value.set(1)
    self.turn = {1: 'white', 2: 'black'}

    self.game_size = Scale(self.panel_game)
    self.game_time = Scale(self.panel_game)
    self.game_turn = Scale(self.panel_game)
    self.generate = Button(self.panel_game)
    self.reset_board = Button(self.panel_game)

    self.switch_agent = Scale(self.panel_game)
    self.agent_show = Label(self.panel_game, font=('Calibri', 14, 'bold'), fg='white',justify=LEFT,
                            bg=bg, text='Agent Policy: ' + self.agent_name + '\n')

    self.hex_board = []
    # Holds the IDs of hexagons in the main board for implementing the click and play functions
    self.game_size_value.set(8)
    self.game_time_value.set(1)
    self.size = self.game_size_value.get()
    self.time = self.game_time_value.get()
    self.board = self.game.board
    self.board = np.int_(self.board).tolist()
    self.array_to_hex(self.board)  # building the game board
    self.logo = PhotoImage(file='image/hex.png')
    self.uut_logo = PhotoImage(file='image/uut.png')
    self.black_side()
    self.white_side()

    # Frame_content

    self.frame_board.configure(bg=bg, width=1366, height=760)
    self.frame_board.pack(fill=BOTH)
    self.notebook.add(self.panel_game, text='       Game       ')
    self.notebook.add(self.developers, text='    Developers    ')
    self.notebook.pack(side=LEFT, fill=Y)
    self.canvas.configure(width=980, bg=bg, cursor='hand2')
    self.canvas.pack(side=LEFT, fill=Y)
    self.canvas.configure(yscrollcommand=self.scroll_y.set)
    self.scroll_y.configure(command=self.canvas.yview)
    self.scroll_x.configure(command=self.canvas.xview)
    self.scroll_y.place(x=387, y=482)
    self.scroll_x.place(x=370, y=500)

    # Frame_left_panel

    """
    the left panel notebook ---->   Game

    """
    self.panel_game.configure(bg=bg)
    Label(self.panel_game, text='Board size',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg, pady=10).pack(fill=X, side=TOP)  # label ---> Board size
    self.game_size.configure(from_=3, to=20, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.game_size_value)
    self.game_size.pack(side=TOP, fill=X)
    Label(self.panel_game, text='Time',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg, pady=10).pack(side=TOP, fill=X)  # label ---> Time
    self.game_time.configure(from_=1, to=20, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.game_time_value)
    self.game_time.pack(side=TOP, fill=X)
    Label(self.panel_game, text='Player',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg, pady=10).pack(side=TOP, fill=X)  # label ---> Turn
    self.game_turn.configure(from_=1, to=2, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.game_turn_value)
    self.game_turn.pack(side=TOP)
    Label(self.panel_game, text='   ',
          font=('Calibri', 14, 'bold'),
          foreground='white', bg=bg).pack(side=TOP, fill=X)

    ################################### AGENT CONTROLS #############################

    self.agent_show.pack(fill=X, side=TOP)
    self.switch_agent.configure(from_=1, to=7, tickinterval=1, bg=bg, fg='white',
                             orient=HORIZONTAL, variable=self.switch_agent_value,)
    self.switch_agent.pack(side=TOP, fill=X)

    ################################### MOVE LABELS ################################
    self.move_label = Label(self.panel_game, font=('Calibri', 15, 'bold'),height=5, fg='white',justify=LEFT,
          bg=bg, text='PLAY : CLICK A CELL ON GAME BOARD \nMCTS BOT: CLICK GENERATE')
    self.move_label.pack(side=TOP, fill=X)

    self.reset_board.configure(text='Reset Board', pady=10,
                               cursor='hand2', width=22,
                               font=('Calibri', 12, 'bold'))
    self.reset_board.pack(side=LEFT)
    self.generate.configure(text='Generate', pady=10,
                            cursor='hand2', width=22,
                            font=('Calibri', 12, 'bold'))
    self.generate.pack(side=LEFT)
    

    """
    the left panel notebook ---> Developers

    """
    self.developers.configure(bg=bg)
    Label(self.developers,
          text= 'HEXPY',
          font=('Calibri', 18, 'bold'),
          foreground='white', bg=bg, pady=5).pack(side=TOP, fill=X)
    Label(self.developers,
          text='DEVELOPED BY:\n'
          + 'Masoud Masoumi Moghadam\n\n'
          + 'SUPERVISED BY:\n'
          + 'Dr.Pourmahmoud Aghababa\n'
          + 'Dr.Bagherzadeh\n\n'
          + 'SPECIAL THANKS TO:\n'
          + 'Nemat Rahmani\n',
          font=('Calibri', 16, 'bold'), justify=LEFT,
          foreground='white', bg=bg, pady=10).pack(side=TOP, fill=X)
    Label(self.developers, image=self.uut_logo, bg=bg).pack(side=TOP, fill=X)
    Label(self.developers, text='Summer 2016',
          font=('Calibri', 17, 'bold'), wraplength=350, justify=LEFT,
          foreground='white', bg=bg, pady=30).pack(side=TOP, fill=X)

    # Binding Actions

    """
    Binding triggers for the actions defined in the class.

    """
    self.canvas.bind('<1>', self.mouse_click)
    self.game_size.bind('<ButtonRelease>', self.set_size)
    self.game_time.bind('<ButtonRelease>', self.set_time)
    self.generate.bind('<ButtonRelease>', self.generate_move)
    self.reset_board.bind('<ButtonRelease>', self.reset)
    self.switch_agent.bind('<ButtonRelease>', self.set_agent)


  def pts(self):
    """
    Returns the points which the first hexagon has to be created based on.

    """
    return [[85, 50], [105, 65], [105, 90], [85, 105], [65, 90], [65, 65]]


  def hexagon(self, points, color):
    """
    Creates a hexagon by getting a list of points and their assigned colors
    according to the game board
    """
    if color is 0:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['gray1'], outline='black', width=2, activefill='cyan')
    elif color is 1:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['yellow'], outline='black', width=2, activefill='cyan')
    elif color is 2:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['red'], outline='black', width=2, activefill='cyan')
    elif color is 3:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['black'], outline='black', width=2)
    else:
      hx = self.canvas.create_polygon(points[0], points[1], points[2],
                                      points[3], points[4], points[5],
                                      fill=self.colors['white'], outline='black', width=2)
    return hx


  def genrow(self, points, colors):
    """
    By getting a list of points as the starting point of each row and a list of
    colors as the dedicated color for each item in row, it generates a row of
    hexagons by calling hexagon functions multiple times.
    """
    x_offset = 40
    row = []
    temp_array = []
    for i in range(len(colors)):
      for point in points:
          temp_points_x = point[0] + x_offset * i
          temp_points_y = point[1]
          temp_array.append([temp_points_x, temp_points_y])
      if colors[i] is 0:
          hx = self.hexagon(temp_array, 0)
      elif colors[i] is 1:
          hx = self.hexagon(temp_array, 4)
      else:
          hx = self.hexagon(temp_array, 3)
      row.append(hx)
      temp_array = []
    return row


  def array_to_hex(self, array):
    """
    Simply gets the gameboard and generates the hexagons by their dedicated colors.
    """
    initial_offset = 20
    y_offset = 40
    temp = []
    for i in range(len(array)):
      points = self.pts()
      for point in points:
          point[0] += initial_offset * i
          point[1] += y_offset * i
          temp.append([point[0], point[1]])
      row = self.genrow(temp, self.board[i])
      temp.clear()
      self.hex_board.append(row)


  def white_side(self):
    """
    Generates the white zones in the left and right of the board.

    """
    init_points = self.pts()
    for pt in init_points:
      pt[0] -= 40
    for pt in init_points:
      pt[0] -= 20
      pt[1] -= 40
    label_x, label_y = 0, 0
    init_offset = 20
    y_offset = 40
    temp_list = []
    for i in range(len(self.board)):
      for pt in range(len(init_points)):
          init_points[pt][0] += init_offset
          init_points[pt][1] += y_offset
          label_x += init_points[pt][0]
          label_y += init_points[pt][1]
      label_x /= 6
      label_y /= 6
      self.hexagon(init_points, 4)
      self.canvas.create_text(label_x, label_y, fill=self.colors['black'], font="Times 20 bold",
                              text=chr(ord('A') + i))
      label_x, label_y = 0, 0
      for j in init_points:
          temp_list.append([j[0] + (len(self.board) + 1) * 40, j[1]])
      self.hexagon(temp_list, 4)
      temp_list.clear()


  def black_side(self):
    """
    Generates the black zones in the top and bottom of the board.

    """
    init_points = self.pts()
    label_x, label_y = 0, 0
    temp_list = []
    for pt in init_points:
      pt[0] -= 60
      pt[1] -= 40
    for t in range(len(init_points)):
      init_points[t][0] += 40
      label_x += init_points[t][0]
      label_y += init_points[t][1]
    label_x /= 6
    label_y /= 6
    for i in range(len(self.board)):
      self.hexagon(init_points, 3)
      self.canvas.create_text(label_x, label_y, fill=self.colors['white'], font="Times 20 bold", text=i + 1)
      label_x, label_y = 0, 0
      for pt in init_points:
          temp_list.append([pt[0] + (len(self.board) + 1) * 20, pt[1] + (len(self.board) + 1) * 40])
      self.hexagon(temp_list, 3)
      temp_list.clear()
      for j in range(len(init_points)):
          init_points[j][0] += 40
          label_x += init_points[j][0]
          label_y += init_points[j][1]
      label_x /= 6
      label_y /= 6


  def mouse_click(self, event):
    """
    Whenever any of the hexagons in the board is clicked, depending
    on the player turns, it changes the color of hexagon to the player
    assigned color.

    """
    if self.winner() == 'none':
      x = self.canvas.canvasx(event.x)
      y = self.canvas.canvasy(event.y)
      idd = self.canvas.find_overlapping(x, y, x, y)
      idd = list(idd)
      if len(idd) is not 0:
        clicked_cell = idd[0]
        if any([clicked_cell in x for x in self.hex_board]):
          coordinated_cell = clicked_cell - self.hex_board[0][0]
          col = (coordinated_cell % self.size)
          turn = self.turn[self.game_turn_value.get()]
          if coordinated_cell % self.size == 0:
            row = int(coordinated_cell / self.size)
          else:
            row = int(coordinated_cell / self.size)
            cell = str(chr(65 + row)) + str(col+1)
            self.move_label.configure(text=str(turn)+' played '+cell,justify=LEFT, height=5)
          if self.board[row][col] == 0:
            self.board[row][col] = self.game_turn_value.get()
            if self.game_turn_value.get() == 1:
              self.game_turn_value.set(2)
            else:
              self.game_turn_value.set(1)
          self.refresh()
          y = row
          x = col
          if turn[0].lower() == 'w':
            self.last_move = (x, y)
            if self.game.turn() == gamestate.PLAYERS["white"]:
              self.game.play((x, y))
              self.agent.move((x, y))
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
            else:
              self.game.place_white((x, y))
              self.agent.set_gamestate(self.game)
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
          elif turn[0].lower() == 'b':
            self.last_move = (x, y)
            if self.game.turn() == gamestate.PLAYERS["black"]:
              self.game.play((x, y))
              self.agent.move((x, y))
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
            else:
              self.game.place_black((x, y))
              self.agent.set_gamestate(self.game)
              if self.winner() != 'none':
                messagebox.showinfo(" GAME OVER", " Wow, You won! \n Winner is %s" % self.winner())
              return
    else:
      messagebox.showinfo(" GAME OVER ", " The game is already over! Winner is %s" % self.winner())


  def set_size(self, event):
    """
    It changes the board size and reset the whole game.

    """
    self.canvas.delete('all')
    self.size = self.game_size_value.get()
    self.game = gamestate(self.size)
    self.agent.set_gamestate(self.game)
    self.board = self.game.board
    self.board = np.int_(self.board).tolist()
    self.last_move = None
    self.move_label.config(text='PLAY : CLICK A CELL ON GAME BOARD \nMCTS BOT: CLICK GENERATE',justify='left', height=5)
    self.refresh()


  def set_time(self, event):
    """
    It changes the time for CPU player to think and generate a move.

    """
    self.time = self.game_time_value.get()
    print('The CPU time = ', self.time, ' seconds')


  def set_agent(self, event):
    """
    It changes the time for CPU player to think and generate a move.

    """
    agent_num = self.switch_agent_value.get()
    self.agent_name = self.agent_type[agent_num]
    self.agent = self.AGENTS[self.agent_name](self.game)
    self.agent_show.config( font=('Calibri', 14, 'bold'),justify=LEFT,
        text= 'Agent Policy: ' + self.agent_name + '\n' )


  def winner(self):
    """
    Return the winner of the current game (black or white), none if undecided.

    """
    if self.game.winner() == gamestate.PLAYERS["white"]:
      return "white"
    elif self.game.winner() == gamestate.PLAYERS["black"]:
      return "black"
    else:
      return "none"


  def generate_move(self, event):
    """
    By pushing the generate button, It produces an appropriate move
    by using monte carlo tree search algorithm for the player which
    turn is his/hers! .

    """
    if self.winner() == 'none':
      # move = self.agent.special_case(self.last_move)
      move = None
      self.agent.search(self.time)
      num_rollouts, node_count, run_time = self.agent.statistics()[0], self.agent.statistics()[1], self.agent.statistics()[2]
      if move is None:
        move = self.agent.best_move()  # the move is tuple like (3, 1)
      self.game.play(move)
      self.agent.move(move)
      row, col = move[0], move[1]  # Relating the 'move' tuple with index of self.board
      self.board[col][row] = self.game_turn_value.get()
      if self.game_turn_value.get() == 1:  # change the turn of players
        self.game_turn_value.set(2)
      else:
        self.game_turn_value.set(1)
      self.refresh()
      player = self.turn[self.game_turn_value.get()]
      cell = chr(ord('A') + move[1]) + str(move[0] + 1)
      self.move_label.config( font=('Calibri', 15, 'bold'),justify='left',
        text= str(num_rollouts) + ' Game Simulations '+'\n'\
        + 'In ' + str(run_time) + ' seconds ' + '\n'\
        + 'Node Count : ' + str(node_count) + '\n'\
        + player + ' played at ' + cell, height=5 )
      print('move = ', cell)
      if self.winner() != 'none':
        messagebox.showinfo(" GAME OVER", " Oops!\n You lost! \n Winner is %s" % self.winner())
    else:
      messagebox.showinfo(" GAME OVER", " The game is already over! Winner is %s" % self.winner())


  def refresh(self):
    """
    Delete the whole world and recreate it again

    """
    self.canvas.delete('all')
    self.hex_board.clear()
    self.array_to_hex(self.board)
    self.black_side()
    self.white_side()  


  def reset(self, event):
    """
    By clicking on the Reset button game board would be cleared
    for a new game

    """
    self.game = gamestate(self.game.size)
    self.agent.set_gamestate(self.game)
    self.set_size(event)
    self.last_move = None
    self.game_turn_value.set(1)
    self.move_label.config(text='PLAY : CLICK A CELL ON GAME BOARD \nMCTS BOT: CLICK GENERATE',justify='left', height=5)



##############################################################################
##############################################################################
################                                              ################
################         GAME-TEXT-PROTOCOL INTERFACE         ################
################                                              ################
##############################################################################
##############################################################################



class gtpinterface:
  """
  Interface for using game-text-protocol to control the program
  Each implemented GTP command returns a string response for the user, along with
  a boolean indicating success or failure in executing the command.
  The interface contains an agent which decides which moves to make on request
  along with a gamestate which holds the current state of the game.

  """

  def __init__(self, agent):
    """
    Initilize the list of available commands, binding appropriate names to the
    funcitons defined in this file.
    """
    commands = {}
    commands["size"] = self.gtp_boardsize
    commands["reset"] = self.gtp_clear
    commands["play"] = self.gtp_play
    commands["genmove"] = self.gtp_genmove
    commands["print"] = self.gtp_show
    commands["set_time"] = self.gtp_time
    commands["winner"] = self.gtp_winner
    self.commands = commands
    self.game = gamestate(8)
    self.agent = agent
    self.agent.set_gamestate(self.game)
    self.move_time = 10
    self.last_move = None

  def send_command(self, command):
    """
    Parse the given command into a function name and arguments, execute it
    then return the response.

    """
    parsed_command = command.split()
    # first word specifies function to call, the rest are args
    name = parsed_command[0]
    args = parsed_command[1:]
    if (name in self.commands):
      return self.commands[name](args)
    else:
      return (False, "Unrecognized command")

  def gtp_boardsize(self, args):
    """
    Set the size of the game board (will also clear the board).

    """
    if (len(args) < 1):
      return (False, "Not enough arguments")
    try:
      size = int(args[0])
    except ValueError:
      return (False, "Argument is not a valid size")
    if size < 1:
      return (False, "Argument is not a valid size")

    self.game = gamestate(size)
    self.agent.set_gamestate(self.game)
    self.last_move = None
    return (True, "")

  def gtp_clear(self, args):
    """
    Clear the game board.

    """
    self.game = gamestate(self.game.size)
    self.agent.set_gamestate(self.game)
    return (True, "")
    self.last_move = None

  def gtp_play(self, args):
    """
    Play a stone of a given colour in a given cell.
    1st arg = colour (white/w or black/b)
    2nd arg = cell (i.e. g5)

    Note: play order is not enforced but out of order turns will cause the
    search tree to be reset

    """
    if (len(args) < 2):
      return (False, "Not enough arguments")
    try:
      x = ord(args[1][0].lower()) - ord('a')
      y = int(args[1][1:]) - 1

      if (x < 0 or y < 0 or x >= self.game.size or y >= self.game.size):
        return (False, "Cell out of bounds")

      if args[0][0].lower() == 'w':
        self.last_move = (x, y)
        if self.game.turn() == gamestate.PLAYERS["white"]:
          self.game.play((x, y))
          self.agent.move((x, y))
        else:
          self.game.place_white((x, y))
          self.agent.set_gamestate(self.game)

      elif args[0][0].lower() == 'b':
        self.last_move = (x, y)
        if self.game.turn() == gamestate.PLAYERS["black"]:
          self.game.play((x, y))
          self.agent.move((x, y))
        else:
          self.game.place_black((x, y))
          self.agent.set_gamestate(self.game)
      else:
        return (False, "Player not recognized")

    except ValueError:
      return (False, "Malformed arguments")

  def gtp_genmove(self, args):
    """
    Allow the agent to play a stone of the given colour (white/w or black/b)

    Note: play order is not enforced but out of order turns will cause the
    agents search tree to be reset

    """
    # if user specifies a player generate the appropriate move
    # otherwise just go with the current turn
    if self.gtp_winner([])[1] == 'none':
      if (len(args) > 0):
        if args[0][0].lower() == 'w':
          if self.game.turn() != gamestate.PLAYERS["white"]:
            self.game.set_turn(gamestate.PLAYERS["white"])
            self.agent.set_gamestate(self.game)

        elif args[0][0].lower() == 'b':
          if self.game.turn() != gamestate.PLAYERS["black"]:
            self.game.set_turn(gamestate.PLAYERS["black"])
            self.agent.set_gamestate(self.game)
        else:
          return (False, "Player not recognized")

      move = None
      self.agent.search(self.move_time)

      if move is None:
        move = self.agent.best_move()

      if (move == gamestate.GAMEOVER):
        return (False, "The game is already over" +
                '\n' + 'The winner is ----> ' + str(self.send_command('winner')[1]), 0)
      self.game.play(move)
      self.agent.move(move)
      return (True, chr(ord('a') + move[0]) + str(move[1] + 1), self.agent.statistics()[0])
    else:
      return(False, "The game is already over" +
            '\n' + 'The winner is ----> ' + str(self.send_command('winner')[1]), 0)

  def gtp_time(self, args):
    """
    Change the time per move allocated to the search agent (in units of secounds)

    """
    if (len(args) < 1):
      return (False, "Not enough arguments")
    try:
      time = int(args[0])
    except ValueError:
      return (False, "Argument is not a valid time limit")
    if time < 1:
      return (False, "Argument is not a valid time limit")
    self.move_time = time
    return (True, "")

  def gtp_show(self, args):
    """
    Return an ascii representation of the current state of the game board.

    """
    return (True, str(self.game))

  def gtp_winner(self, args):
    """
    Return the winner of the current game (black or white), none if undecided.

    """
    if (self.game.winner() == gamestate.PLAYERS["white"]):
      return (True, "white")
    elif (self.game.winner() == gamestate.PLAYERS["black"]):
      return (True, "black")
    else:
      return (True, "none")


def main():
  root = Tk()
  interface = Gui(root)
  root.mainloop()

if __name__ == "__main__":
  main()


