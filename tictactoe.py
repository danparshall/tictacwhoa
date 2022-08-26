import numpy as np
import re
import random

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
        x,y = self.current_player.give_input(self)
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

    def _check_diagonals(self, game, marker):
        win_row = np.nan
        win_col = np.nan
        dmain = game.board[(0, 1, 2), (0, 1, 2)]
        dorth = game.board[(0, 1, 2), (2, 1, 0)]
        if (np.isnan(dmain).sum() == 1) & ((dmain == marker).sum() == 2):
            # win on main diagonal
            for idx in (0,1,2):
                if np.isnan(dmain[idx]):
                    win_row = idx
                    win_col = idx
                    break
        elif (np.isnan(dorth).sum() == 1) & ((dorth == marker).sum() == 2):
            # win on counter-diagonal
            for idx in (0, 1, 2):
                if np.isnan(dorth[idx]):
                    win_row = idx
                    win_col = 2 - idx
                    break
        return win_row, win_col

    def _check_rows_and_cols(self, game, marker):
        win_row = np.nan
        win_col = np.nan

        # we need to have exactly one empty/nan space, and the other two of our marker
        nans_per_col = np.isnan(game.board).sum(axis=0)
        marks_per_col = (game.board == marker).sum(axis=0)
        poss_cols = (nans_per_col == 1) & (marks_per_col == 2)

        nans_per_row = np.isnan(game.board).sum(axis=1)
        marks_per_row = (game.board == marker).sum(axis=1)
        poss_rows = (nans_per_row == 1) & (marks_per_row == 2)

        if poss_rows.any():
            for irow, rowval in enumerate(poss_rows):
                if rowval:
                    win_row = irow
                    break
            for icol, colval in enumerate(game.board[win_row, :]):
                if np.isnan(colval):
                    # when the current col is empty, place marker there
                    win_col = icol
                    break
        elif poss_cols.any():
            for icol, colval in enumerate(poss_cols):
                if colval:
                    win_col = icol
                    break
            for irow, rowval in enumerate(game.board[:, win_col]):
                if np.isnan(rowval):
                    win_row = irow
                    break
        return win_row, win_col


    def _check_for_possible_wins(self, game, marker):
        # first check the diagonals
        win_row, win_col = self._check_diagonals(game, marker)
        if (win_row >= 0) and (win_col >= 0):
            return win_row, win_col
        # next try rows/cols
        win_row, win_col = self._check_rows_and_cols(game, marker)
        if (win_row >= 0) and (win_col >= 0):
            return win_row, win_col
        # if no potential wins
        return np.nan, np.nan

    def give_input(self, game):
        """ HeuristicBot can be set smarter or stoopider using INTELLIGENCE parameter
        At INTELLIGENCE == 0; returns a random legal move
        At INTELLIGENCE == 1; returns a win if possible, else a random legal move
        At INTELLIGENCE == 2; returns a win if possible, else a block, else a random legal move
        """
        if self.INTELLIGENCE >= 1:
        # return win if possible
            win_row, win_col = self._check_for_possible_wins(game, game.current_marker)
            if (win_row >= 0) and (win_col >= 0):
                return win_row, win_col
        if self.INTELLIGENCE >= 2:
        # return block if posible
            block_row, block_col = self._check_for_possible_wins(game, -1*game.current_marker)
            if (block_row >= 0) and (block_col >= 0):
                return block_row, block_col
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
    p1 = TttHuman("Dan")
    b1 = TttHeuristic("bot")
#    game = TttGame(p1, b1)
#    game.play()
elif True:
    # autobots
    b1 = TttHeuristic("bot1")
    b2 = TttHeuristic("bot2")
    autogames = []

    for idx in range(1000):
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
