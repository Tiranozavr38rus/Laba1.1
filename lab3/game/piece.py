from game.settings import *


class Piece(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 'BOARD'
        self.flipped = False

        self.drawing = {
            "WHITE": self.draw_white,
            "BLACK": self.draw_black,
            "BOARD": self.draw_board,
            "MOVE": self.draw_move}

    def draw(self):
        result = ''
        if self.state in self.drawing:
            result = self.drawing[self.state]()

        return result

    def draw_white(self):
        if self.flipped:
            return 'WF'
        else:
            return 'WW'

    def draw_black(self):
        if self.flipped:
            return 'BF'
        else:
            return 'BB'

    def draw_board(self):
        return '..'

    def draw_move(self):
        return 'MM'

    def set_black(self):
        self.state = 'BLACK'

    def set_white(self):
        self.state = 'WHITE'

    def set_move(self):
        self.state = MOVE

    def set_board(self):
        self.state = BOARD

    def get_state(self):
        return self.state

    def flip(self):
        if self.state == BLACK:
            self.state = WHITE
        elif self.state == WHITE:
            self.state = BLACK
        else:
            raise ValueError

        self.flipped = True

    def set_flipped(self):
        self.flipped = True

    def reset_flipped(self):
        self.flipped = False

    def is_flipped(self):
        return self.flipped

    def get_position(self):
        return self.x, self.y

    def __repr__(self):
        return '({0},{1})'.format(self.x, self.y)