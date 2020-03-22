from gui import (UctMctsAgent, RaveMctsAgent)
from gtp import GTPInterface
from tournament import tournament

game_number = 100
move_time = 1
boardsize = 11
opening_moves = []


def main():
    """
    Run a tournament between two agents and print the resulting winrate
    for the first agent.
    """
    interface1 = GTPInterface(UctMctsAgent())
    interface2 = GTPInterface(RaveMctsAgent())
    address = 'results/result.txt'
    f = open(address, 'a')
    f.write('Tournament between QB UCTRAVE , UCT \n')
    print('Tournament between QB RAVE , UCT \n')
    f.close()
    for i in range(3):
        result = tournament(interface1, interface2, game_number, move_time, boardsize, opening_moves)
        with open(address, 'a') as file:
            file.write('Result of tournament %a \n' % i)
            file.write('player 1 wins = %a games \n' % result[0])
            file.write('player 2 wins = %a games \n' % result[1])
            file.write("Simulations : \nAvg [ %a ] max = [ %a ] min = [ %a ] \n" % result[2])
            file.write("Total time : %a \n\n\n" % result[3])
            file.close()


def shutdown():
    import os
    os.system("shutdown /s /t 90")


if __name__ == "__main__":
    main()
    # shutdown()
