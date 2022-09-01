import numpy as np
import random
import re


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
