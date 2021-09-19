# Monte-Carlo-Tree-Search-Agent-for-the-Game-of-HEX

## Demo:

![Demo of MCTS General Game Player](https://github.com/masouduut94/MCTS-agent-python/blob/master/resources/demo.gif) 

## Description
This code belongs to this paper **:link: [IMPROVING MONTE CARLO TREE SEARCH BY COMBINING
RAVE AND QUALITY-BASED REWARDS ALGORITHMS](https://github.com/masouduut94/MCTS-agent-python/blob/master/paper/CONFITC04_172.pdf)**.

### what is Monte Carlo Tree Search(MCTS)?
MONTE Carlo Tree Search (MCTS) is a method for finding optimal decisions in a given domain by
taking random samples in the decision space and building a search tree according to the results.
It has already had a profound impact on Artificial Intelligence (AI) approaches for domains that
can be represented as trees of sequential decisions, particularly games and planning problems. 
In this project I used different simulation strategies to enhance the agent policy to explore the environment.

 from :link: [A Survey of Monte Carlo Tree Search Methods](http://ieeexplore.ieee.org/abstract/document/6145622/)

### About contribution
Before you go through the details, I recommend you to get familiar with the framework reading these medium articles:
- [A simple no math included introduction to reinforcement learning](https://towardsdatascience.com/monte-carlo-tree-search-a-case-study-along-with-implementation-part-1-ebc7753a5a3b)
- [A simple introduction to Monte Carlo Tree Search](https://towardsdatascience.com/monte-carlo-tree-search-implementing-reinforcement-learning-in-real-time-game-player-25b6f6ac3b43)
- [Details of MCTS implementation on game of HEX](https://towardsdatascience.com/monte-carlo-tree-search-implementing-reinforcement-learning-in-real-time-game-player-a9c412ebeff5)

So if you are familiar with the whole concept of MCTS and UCT algorithm, you must know that in practice it suffers from 
sparse rewards. it takes so much time to warm up the tree with simple UCT algorithm. So in this case we **first implemented
the RAVE algorithm** that helps warm up tree faster. then implemented **several simulation strategy like Last Good Reply,
PoolRAVE, Decisive Move and also UCB1-Tuned**.

Then we applied **quality based rewards** in [Quality-based Rewards for Monte-Carlo Tree Search Simulations](https://dl.acm.org/doi/10.5555/3006652.3006771) 
which basically it asserts that we can apply discounted rewards by **knowing the length of simulation and the 
maximum number of actions allowed to take in environment** for each player (In some games, the game ends after limited number of moves. because there is no more movements).

After that we used **HRAVE and GRAVE in the paper [Comparison of rapid action value estimation variants for general game playing 2018 - Chiara F. Sironi; Mark H. M. Winands](https://ieeexplore.ieee.org/document/7860429)**
which basically states that we can use the **global information of the game to guide the simulations**.
We also tested the **leaf threading on UCT**.

all of above algorithms are addressed below.

### Original repo

- MopyHex: Authored by Kenny Young [here](https://github.com/kenjyoung/mopyhex)

### Contributions to the original repo:
- implementing Generalized Rapid Action Value Estimation
- implementing HRAVE and GRAVE algorithms in [Comparison of rapid action value estimation variants for general game playing 2018 - Chiara F. Sironi; Mark H. M. Winands](https://ieeexplore.ieee.org/document/7860429)
- implementing Quality-based rewards in [Quality-based Rewards for Monte-Carlo Tree Search Simulations](https://dl.acm.org/doi/10.5555/3006652.3006771)
- implementing leaf-threading on basic No frills UCT.

**This project has a further optimized version in [here](https://github.com/masouduut94/MCTS-agent-cythonized) which optimized by cython.**

### Researches have been done in **Urmia University of Technology**.
<p align="center">

<img src="https://github.com/masouduut94/MCTS-agent-python/blob/master/image/ssss.png">
    
</p>

#### Authors: 
- Masoud Masoumi Moghadam (Me :sunglasses:)
- Prof: Mohammad Pourmahmood Aghababa [profile](https://bit.ly/3dV23Be)
- Prof: Jamshid Bagherzadeh [profile](https://bit.ly/3dPX4Sc)

## What is monte carlo tree search anyway?


# Requirements
- OS: Windows  and Ubuntu
- tkinter
- Numpy

# To run it:
You can :running: (run) program using this command:

    python main.py

Also you can run tests for comparing two mcts-based algorithms against 
each other using the `playtest.py`.

## :closed_book: To know more about MCTS:

This one is highly recommended: 


## Algorithms used for boosting MCTS in this framework: 

- Upper Confidence Bounds (UCT)
- UCB1-Tuned
- Rapid Action Value Estimation (RAVE)
- Decisive Move 
- Quality Based Rewards
- Pool RAVE
- Last Good Reply


# References
- [1] A Survey of Monte Carlo Tree Search Methods, Cameron B. Browne et al, 2012 [Link to paper](https://ieeexplore.ieee.org/document/6145622)
- [2] Generalized Rapid Action Value Estimation, Tristan Cazenave,  2017 [Link to paper](https://www.ijcai.org/Proceedings/15/Papers/112.pdf)
- [3] Comparison of rapid action value estimation variants for general game playing, C. Sironi, 2018 [Link to paper](https://ieeexplore.ieee.org/document/7860429)
- [4] Quality-based Rewards for Monte-Carlo Tree Search Simulations, 2014 [Link to paper](https://dl.acm.org/doi/10.5555/3006652.3006771)
- [5] The Last-Good-Reply Policy for Monte-Carlo Go 2009 [Link to paper](https://www.semanticscholar.org/paper/The-Last-Good-Reply-Policy-for-Monte-Carlo-Go-Drake/980e6b8ef765b0fe4fc3fe8f068c79ac4169b00f) 
- [6] On the Huge Benefit of Decisive Moves in Monte-Carlo Tree Search Algorithms, Fabien Teytaud, Olivier Teytaud, 2010

