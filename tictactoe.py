import numpy as np
import re
import random
from collections import Counter

class TttGame():
    __class__ = "Tic-tac-toe Game"   # __class__ property of an instance
    # __name__ = "Tic-tac-NAME"  # the __name__ property will be "TttGame", regardless of whether this is here

    def __init__(self, p1, p2, debug=False):
        self.__name__ = "Tic-tac-toe: {0} vs. {1}".format(p1.unique_name, p2.unique_name) # __name__ property of instance
        self.board = np.nan * np.ones((3,3))
        self.p1 = p1
        self.p2 = p2
        self.current_player = self.p1
        self.current_marker = 1
        self.winning_player = None
        self.legal_moves = [
            (0,0), (0,1), (0,2),
            (1,0), (1,1), (1,2),
            (2,0), (2,1), (2,2),
            ]
        self.history = list()
        self._DEBUG_ = debug

    def receive_input(self):
        is_waiting = True
        x,y = self.current_player.give_input(self) # the current player receives the current game as input
        if (x,y) in self.legal_moves:
            self.legal_moves.remove((x,y))
            self.board[x, y] = self.current_marker
            self.history.append((x,y))
            is_waiting = False
        else:
            print("Not a legal move")
            is_waiting = self.receive_input()
        return is_waiting

    def check_winner(self):
        """ Checks if any row, column, or diagonal has 3-in-a-row. """
        is_winner = False
        if np.any(np.abs(self.board.sum(axis=0)) == 3):
            # checks columns
            is_winner = True
        elif np.any(np.abs(self.board.sum(axis=1)) == 3):
            # checks rows
            is_winner = True
        elif np.abs(np.sum(self.board[0,0] + self.board[1,1] + self.board[2,2])) == 3:
            # checks main diagonal
            is_winner = True
        elif np.abs(np.sum(self.board[2,0] + self.board[1,1] + self.board[0,2])) == 3:
            # checks perpendicular diagonal
            is_winner = True
        if self._DEBUG_ and is_winner:
            print("The winner is {0}".format(self.current_player.unique_name))
            pass
        return is_winner

    def change_player(self):
        if self.current_player == self.p1:
            self.current_player = self.p2
        elif self.current_player == self.p2:
            self.current_player = self.p1
        if self._DEBUG_:
            print("New player is {0}".format(self.current_player.unique_name))
        self.current_marker = -1 * self.current_marker

    def play(self):
        if self.winning_player is None:   
            self.current_player.examine_board(self)
            is_waiting = True
            while is_waiting:
                is_waiting = self.receive_input()
            is_winner = self.check_winner()
            if is_winner:
                # defines the winning player.  Player objects can check for themselves if they won
                self.winning_player = self.current_player
            elif np.isnan(self.board).sum() == 0:
                # draw if all boxes filled without winner
#                print("The game was a Draw")
                self.winning_player = np.nan
            else: 
                self.change_player()
                self.play()
        else:
            print("Game has finished, start another.")



class TttPlayer():
    def __init__(self, player_name):
        self.unique_name = player_name
        print("Initializing {0}".format(self.unique_name))

    def examine_board(self, game):
        pass

    def give_input(self, game):
        return (np.nan, np.nan)

    def return_winner(self, game):
        return game.current_winner



class TttHuman(TttPlayer):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)  # inherit TttPlayer's "__init__"
        self.re_player_input = re.compile(r"^([0-2]{1})[, ]+([0-2]{1})$")
        self.__name__ = "Human Player: {0}".format(self.unique_name)

    def _make_marker(self, char):
        if char == 1:
            return "X"
        elif char == -1:
            return "O"
        else:
            return " "

    def _print_row(self, board, n_row):
        chars = [self._make_marker(c) for c in board[n_row,:]]
        print(" {0} | {1} | {2} ".format(*chars))

    def _print_board(self, game):
        print("\n")
        self._print_row(game.board, 0)
        print("-----------")
        self._print_row(game.board, 1)
        print("-----------")
        self._print_row(game.board, 2)

    def examine_board(self, game):
        self._print_board(game)

    def give_input(self, game):
        run = True
        while run:
            if game.current_player == game.p1:
                marker = "X"
            elif game.current_player == game.p2:
                marker = "O"
            else:
                marker = np.nan
                print("WTF, are you an X or an O?")

            player_input = input("Choose x,y coordinates to place marker for {0}: ".format(marker))
            player_choice = self.re_player_input.search(player_input)
            if not player_choice:
                print("Please try again; you must choose x,y coordinates from 0-2")
            else:
                # group 0 is the entire match, g1/g2 are x/y
                x = int(player_choice[1])
                y = int(player_choice[2])
                run = False
        return x,y



class TttHeuristic(TttPlayer):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)  # inherit TttPlayer's "__init__"
        self.INTELLIGENCE = 1
        self.__name__ = "Heuristic Bot (Intelligence {0}): {1}".format(self.INTELLIGENCE, self.unique_name)
        print("Starting", self.__name__)

    def _check_diag(self, board, marker, direction):
        win_row = np.nan
        win_col = np.nan
        if direction == "main":
            board_diag = board[(0, 1, 2), (0, 1, 2)]
        elif direction == "orth":
            board_diag = board[(0, 1, 2), (2, 1, 0)]
        else:
            print("What kind of diagonal is this?")

        if (np.isnan(board_diag).sum() == 1) & ((board_diag == marker).sum() == 2):
            win_row = np.where(np.isnan(board_diag))[0][0]  # we know exactly 1 of these is a nan
            if direction == "main":
                win_col = win_row
            elif direction == "orth":
                win_col = 2 - win_row
        return win_row, win_col

    def _check_row(self, board, marker, idx_row):
        win_row = np.nan
        win_col = np.nan
        check = board[idx_row, :]
        if (np.isnan(check).sum() == 1) & ((check == marker).sum() == 2):
            win_row = idx_row
            win_col = np.where(np.isnan(check))[0][0]
        return win_row, win_col

    def _check_col(self, board, marker, idx_col):
        win_row = np.nan
        win_col = np.nan
        check = board[:, idx_col]
        if (np.isnan(check).sum() == 1) & ((check == marker).sum() == 2):
            win_col = idx_col
            win_row = np.where(np.isnan(check))[0][0]
        return win_row, win_col

    def _find_winning_plays(self, board, marker):
        winning_plays = []
        for dir in ["main", "orth"]:
            (wr, wc) = self._check_diag(board, marker, dir)
            if not np.isnan(wr):
                winning_plays.append((wr,wc))
        for idx_row in (0,1,2):
            (wr, wc) = self._check_row(board, marker, idx_row)
            if not np.isnan(wr):
                winning_plays.append((wr,wc))
        for idx_col in (0,1,2):
            (wr, wc) = self._check_col(board, marker, idx_row)
            if not np.isnan(wr):
                winning_plays.append((wr,wc))
        return winning_plays

    def _check_for_possible_wins(self, board, marker):
        winning_plays = self._find_winning_plays(board, marker)
        if len(winning_plays) > 0:
            return winning_plays.pop()
        # if no potential wins
        return np.nan, np.nan

    def _check_forks(self, game, marker, legal_moves):
        """" Can have max of 1 fork when players greedily take wins. """
        board = game.board
        forks = []
        for move in legal_moves:
            possible_board = board.copy()
            possible_board[move] = marker
            winning_plays = self._find_winning_plays(possible_board, marker)
            if len(winning_plays) > 1:
#                if fork:
#                    print("WE HAVE A DOUBLE FORK!", fork, move, game.history)
                forks.append(move)
#        if fork is None:
#            fork = (np.nan, np.nan)
        return forks

    def give_input(self, game):
        """ HeuristicBot can be set smarter or stoopider using INTELLIGENCE parameter
        At INTELLIGENCE == 0; returns a random legal move
        At INTELLIGENCE == 1; returns a win if possible, else a random legal move
        At INTELLIGENCE == 2; returns a win if possible, else a block, else a random legal move
        """
        if self.INTELLIGENCE >= 1:
        # return win if possible
            win_row, win_col = self._check_for_possible_wins(game.board, game.current_marker)
            if (win_row >= 0) and (win_col >= 0):
                return win_row, win_col
        if self.INTELLIGENCE >= 2:
        # return block if posible
            block_row, block_col = self._check_for_possible_wins(game.board, -1*game.current_marker)
            if (block_row >= 0) and (block_col >= 0):
                return block_row, block_col
        if self.INTELLIGENCE >= 3:
            forks = self._check_forks(game, game.current_marker, game.legal_moves)
            if len(forks) > 0:
                return forks.pop()
#            if (fork_row >= 0) and (fork_col >= 0):
#                return fork_row, fork_col
        # else return random legal move
        return random.choice(game.legal_moves)


if False:
    p1 = TttHuman("hum1")
    p2 = TttHuman("hum2")
    game = TttGame(p1, p2)

    # make dummy board to test
    game.board[0,1] = 1
    game.board[1, 0] = 1
    game.board[1,1] = -1
    game.board[2,2] = -1

    b1 = TttHeuristic("bot");
    wr, wc = b1._check_for_possible_wins(game, 1)
    print(wr, wc)
    print(game.board)
elif False:
    p1 = TttHuman("hum1")
    b1 = TttHeuristic("bot");
    game = TttGame(p1, b1)

    # Hypothetical fork scenario
    game.board[0,0] = 1
    game.board[2,2] = -1
    game.board[2,0] = 1
    game.board[1,0] = -1
    game.legal_moves.remove((0,0))
    game.legal_moves.remove((2,2))
    game.legal_moves.remove((2,0))
    game.legal_moves.remove((1,0))
#    game.receive_input((0,0))
#    game.change_player()
#    game.receive_input((2,2))
#    game.change_player()
#    game.receive_input((2,0))
#    game.change_player()
#    game.receive_input((1,2))


elif False:
    p1 = TttHuman("Dan")
    b1 = TttHeuristic("bot")
#    game = TttGame(p1, b1)
#    game.play()
elif False:
    # autobots
    b1 = TttHeuristic("bot1")
    b2 = TttHeuristic("bot2")
    autogames = []

    for idx in range(100):
        game = TttGame(b1,b2)
        game.play()
        autogames.append(game)

    identical = 0
    tot = 0
    for idx in range(len(autogames)):
        if idx % 100 == 0:
            print(idx)
        ref = autogames[idx] 
        checks = autogames[:idx] + autogames[idx+1:] 
        for check in checks:
            tot += 1
            if (check.board == ref.board).all(): 
                identical += 1
                print("{0} out of {1} boards are identical".format(identical, idx+1))
elif True:
    # Battle bots\
    b1 = TttHeuristic("bot1")
    b2 = TttHeuristic("bot2")
    b1.INTELLIGENCE = 2
    b2.INTELLIGENCE = 3

    autogames = []
    wins_b1 = 0
    wins_b2 = 0
    for idx in range(10000):
        game = TttGame(b1, b2)
        game.play()
        autogames.append(game)
        if game.winning_player == b1:
            wins_b1 += 1
        elif game.winning_player == b2:
            wins_b2 += 1
        else:
            pass
    print(wins_b1, wins_b2)
elif True:
    # troublshoot
    b2 = TttHeuristic("bot_iq2")
    b3 = TttHeuristic("bot_iq3")
    b2.INTELLIGENCE = 2
    b3.INTELLIGENCE = 3
    game = TttGame(b2, b3)
    game.board[0,2] = 1
    game.legal_moves.remove((0,2))
    game.board[2,1] = -1
    game.legal_moves.remove((2,1))
    game.board[2,2] = 1
    game.legal_moves.remove((2,2))
    game.board[1,2] = -1
    game.legal_moves.remove((1,2))
