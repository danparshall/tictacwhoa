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
                forks.append(move)
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
                return forks.pop()   # no discrimination between forks
        # else return random legal move
        return random.choice(game.legal_moves)