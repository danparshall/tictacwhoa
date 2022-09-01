import numpy as np

import tictac_game as ttg
import tictac_players as ttp

from importlib import reload
reload(ttg)
reload(ttp)



if False:
    p1 = ttp.TttHuman("hum1")
    p2 = ttp.TttHuman("hum2")
    game = ttg.TttGame(p1, p2)

    # make dummy board to test
    game.board[0,1] = 1
    game.board[1, 0] = 1
    game.board[1,1] = -1
    game.board[2,2] = -1

    b1 = ttp.TttHeuristic("bot");
    wr, wc = b1._check_for_possible_wins(game, 1)
    print(wr, wc)
    print(game.board)
elif False:
    p1 = ttp.TttHuman("Dan")
    b1 = ttp.TttHeuristic("bot")
#    game = ttg.TttGame(p1, b1)
#    game.play()
elif False:
    # TODO: bug in counting; N boards means N**2 comparisons, also using "==", which means NaN won't come out the same
    # autobots
    b1 = ttp.TttHeuristic("bot1")
    b2 = ttp.TttHeuristic("bot2")
    autogames = []

    for idx in range(1000):
        game = ttg.TttGame(b1,b2)
        game.play()
        autogames.append(game)

    identical = 0
    tot = 0
    for idx in range(len(autogames)):
        if idx % 100 == 0:
            print(idx)
        ref = autogames[idx]
        checks = autogames[idx+1:] # compare to all the boards we haven't seen yet
        for check in checks:
            tot += 1
            if (check.board == ref.board).all(): 
                identical += 1
                print("{0} out of {1} boards are identical".format(identical, idx+1))
    print("{0} out of {1} boards are identical".format(identical, idx+1))
elif True:
    # autobots
    b1 = ttp.TttHeuristic("bot_x")
    b2 = ttp.TttHeuristic("bot_o")

    intelligence = range(4)
    n_int = len(intelligence)
    xwins = np.zeros((n_int, n_int))
    owins = np.zeros((n_int, n_int))
    draws = np.zeros((n_int, n_int))
    for int_x in intelligence:
        print("Setting X intelligence to", int_x)
        b1.INTELLIGENCE = int_x
        for int_o in intelligence:
            print("Setting O intelligence to", int_o)
            b2.INTELLIGENCE = int_o

            xtmp = 0
            otmp = 0
            dtmp = 0
            for idx in range(1000):
                game = ttg.TttGame(b1,b2)
                game.play()

                if game.winning_player == b1:
                    xtmp += 1
                elif game.winning_player == b2:
                    otmp += 1
                elif game.winning_player is None:
                    dtmp += 1
                else:
                    raise ValueError("Who won the game?")
            xwins[int_x, int_o] = xtmp
            owins[int_x, int_o] = otmp
            draws[int_x, int_o] = dtmp
