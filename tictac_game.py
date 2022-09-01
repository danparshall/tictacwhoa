import numpy as np

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
                # game is a draw if all boxes filled without winner
#                print("The game was a Draw")
                pass # winning_player remains None
            else: 
                self.change_player()
                self.play()
        else:
            print("Game has finished, start another.")
