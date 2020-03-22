from meta import GameMeta
import sys
import time


def print_game(game):
    for move in game:
        print(move, end=' ')
    print()


def tournament(interface1, interface2, game_number=100, movetime=10, size=8, opening_moves=[]):
    """
    Run some number of games between two agents, alternating who has first move
    each time. Return the winrate for the first of the two agents. Print games
    played along the way.
    """
    begin = time.clock()
    p1_score = 0  # score for player 1
    p2_score = 0  # score for player 2
    interface1.gtp_time([movetime])
    interface2.gtp_time([movetime])
    interface1.gtp_boardsize([size])
    interface2.gtp_boardsize([size])
    rollouts_1 = 0
    genmove_calls_1 = 0
    list_of_rollouts = []
    print('Tournament Started ...')
    print("%a games will be running between agents ..." % game_number)
    for i in range(game_number):
        interface1.gtp_clear([])
        interface2.gtp_clear([])
        turn = interface1.game.turn()
        c1 = 'w' if turn == GameMeta.PLAYERS["white"] else 'b'
        c2 = 'b' if turn == GameMeta.PLAYERS["white"] else 'w'
        game = []

        rollouts_2 = 0
        genmove_calls_2 = 0

        if i % 2 == 0:
            while interface1.gtp_winner([])[1] == "none":
                move = interface1.gtp_genmove([c1])
                rollouts_1 += move[2]
                genmove_calls_1 += 1
                list_of_rollouts.append(move[2])
                if move[0]:
                    interface2.gtp_play([c1, move[1]])
                    game.append(move[1])
                move = interface2.gtp_genmove([c2])
                rollouts_1 += move[2]
                genmove_calls_1 += 1
                list_of_rollouts.append(move[2])
                if move[0]:
                    interface1.gtp_play([c2, move[1]])
                    game.append(move[1])

            # print(interface1.gtp_show([])[1])
            if interface1.gtp_winner([])[1][0] == c1:
                p1_score += 1
                print("GAME OVER, WINNER : PLAYER 1 (" + c1 + ")\n")
                print("Games played =  [ %i   /  %g ]" % (i + 1, game_number))
                print("Wins   |  Player 1 =  [%a]  |  Player 2 = [%s]  " % (p1_score, p2_score))
            else:
                p2_score += 1
                print("GAME OVER, WINNER : PLAYER 2 (" + c2 + ")\n")
                print("Games played =  [ %i   /  %g ] " % (i + 1, game_number))
                print("Wins   |  Player 1 =  [%a] |  Player 2 = [%s]  " % (p1_score, p2_score))

        else:
            while interface1.gtp_winner([])[1] == "none":
                move = interface2.gtp_genmove([c1])
                rollouts_1 += move[2]
                genmove_calls_1 += 1
                list_of_rollouts.append(move[2])
                if move[0]:
                    interface1.gtp_play([c1, move[1]])
                    game.append(move[1])
                move = interface1.gtp_genmove([c2])
                rollouts_1 += move[2]
                genmove_calls_1 += 1
                list_of_rollouts.append(move[2])
                if move[0]:
                    interface2.gtp_play([c2, move[1]])
                    game.append(move[1])

            # print(interface1.gtp_show([])[1])
            if interface1.gtp_winner([])[1][0] == c2:
                p1_score += 1
                print("GAME OVER, WINNER : PLAYER 1 (" + c2 + ")\n")
                print("Games played =  [ %i   /  %g ] " % (i + 1, game_number))
                print("Wins   |  Player 1 =  [%a]  |  Player 2 = [%s]  " % (p1_score, p2_score))
            else:
                p2_score += 1
                print("GAME OVER, WINNER : PLAYER 2 (" + c1 + ")\n")
                print("Games played =  [ %i   /  %g ] " % (i + 1, game_number))
                print("Wins   |  Player 1 =  [%a] |  Player 2 = [%s]  " % (p1_score, p2_score))
        sys.stdout.flush()  # flush buffer so intermediate results can be viewed
    list_of_rollouts = list(filter(lambda a: a != 0, list_of_rollouts))
    p1 = (p1_score / game_number) * 100
    p2 = (p2_score / game_number) * 100
    rollouts_info = (round(sum(list_of_rollouts) / len(list_of_rollouts)),
                     max(list_of_rollouts),
                     min(list_of_rollouts))
    print('\n\n\n')
    print('player 1 wins = ', p1, ' %')
    print('player 2 wins = ', p2, ' %')
    print("Average Simulations = [ %a ] " % (rollouts_1 / genmove_calls_1))
    print('Finished in %i seconds' % (time.clock() - begin))
    return p1_score, p2_score, rollouts_info, time.clock() - begin
