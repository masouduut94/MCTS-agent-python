# Monte-Carlo-Tree-Search-Agent-for-the-Game-of-HEX

## Demo:

![Demo of MCTS General Game Player](https://github.com/masouduut94/MCTS-agent-python/blob/master/resources/demo.gif) 

## Description
This code belongs to one of my paper **:link: [IMPROVING MONTE CARLO TREE SEARCH BY COMBINING
RAVE AND QUALITY-BASED REWARDS ALGORITHMS](https://www.civilica.com/Paper-CONFITC04-CONFITC04_172.html)**.

### what is Monte Carlo Tree Search(MCTS)?
MONTE Carlo Tree Search (MCTS) is a method for finding optimal decisions in a given domain by
taking random samples in the decision space and building a search tree according to the results.
It has already had a profound impact on Artificial Intelligence (AI) approaches for domains that
can be represented as trees of sequential decisions, particularly games and planning problems. 
In this project I used different simulation strategies to enhance the agent policy to explore the environment.

 from :link: [A Survey of Monte Carlo Tree Search Methods](http://ieeexplore.ieee.org/abstract/document/6145622/)





Original repo: Authored by Kenny Young [here](https://github.com/kenjyoung/mopyhex)

Contributions in this repo:
- implementing Generalized Rapid Action Value Estimation
- implementing HRAVE and GRAVE algorithms in [Comparison of rapid action value estimation variants for general game playing 2018 - Chiara F. Sironi; Mark H. M. Winands](https://ieeexplore.ieee.org/document/7860429)
- implementing Quality-based rewards in [Quality-based Rewards for Monte-Carlo Tree Search Simulations](https://dl.acm.org/doi/10.5555/3006652.3006771)
- implementing leaf-threading on basic No frills UCT.

This project is further optimized in [here](https://github.com/masouduut94/MCTS-agent-cythonized)

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
