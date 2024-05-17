import os
from collections import deque
from game.board import Board
from game.controllers import PlayerController, AiController
from game.random_controller import RandomController
from game.settings import *


class Game(object):
    def __init__(self, timeout=1,
                 display_moves=True,
                 players=['ai', 'random']):

        self.board = Board()
        self.timeout = timeout
        self.ai_counter = 0
        self.list_of_colours = [BLACK, WHITE]
        self.players = players
        self.display_moves = display_moves
        self.controllers = deque([self._make_controller(c, p) for c, p in zip(self.list_of_colours, self.players)])
        self.player = self.controllers[0].get_colour()
        self.board.set_black(4, 3)
        self.board.set_black(3, 4)
        self.board.set_white(4, 4)
        self.board.set_white(3, 3)
        self.board.mark_moves(self.player)
        self.previous_move = None
        self.previous_round_passed = False

    def _make_controller(self, colour, controller_type):
        if controller_type == 'player':
            return PlayerController(colour)
        elif controller_type == 'random':
            return RandomController(colour)
        else:
            self.ai_counter += 1
            return AiController(self.ai_counter, colour, self.timeout)

    def show_info(self):
        self.player = self.controllers[0].get_colour()
        print("Играет как:       " + self.player)
        print("Отображение ходов: " + str(self.display_moves))
        print("Текущий ход:     " + str(self.controllers[0]))
        print("Количество черных:  " + str(
            len([p for p in self.board.pieces if p.get_state() == BLACK])))
        print("Количество белых:  " + str(
            len([p for p in self.board.pieces if p.get_state() == WHITE])))

    def show_board(self):
        self.board.mark_moves(self.player)
        print(self.board.draw())

    def show_commands(self):
        moves = [self.to_board_coordinates(piece.get_position()) for piece in self.board.get_move_pieces(self.player)]

        if not moves:
            raise NoMovesError

        print("Возможные ходы: ", moves)
        self.board.clear_moves()

    def run(self):
        while True:
            # os.system('clear')
            self.show_info()
            self.show_board()

            try:
                self.show_commands()
                next_move = self.controllers[0].next_move(self.board)
                self.board.make_move(next_move, self.controllers[0].get_colour())
                self.previous_round_passed = False
            except NoMovesError:
                if self.previous_round_passed:
                    print("Игра окончена")
                    blacks = len([p for p in self.board.pieces if p.get_state() == BLACK])
                    whites = len([p for p in self.board.pieces if p.get_state() == WHITE])

                    if blacks > whites:
                        print("Черные победили.")
                        exit()
                    elif blacks == whites:
                        print("Ничья.")
                        exit()
                    else:
                        print("Белые победили.")
                        exit()
                else:
                    self.previous_round_passed = True

            self.controllers.rotate()

            print("Текущий ход: ", self.to_board_coordinates(next_move))

            self.previous_move = next_move

    def to_board_coordinates(self, coordinate):
        x, y = coordinate
        return '{0}{1}'.format(chr(ord('a') + x), y + 1)
