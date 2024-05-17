import datetime
import os
import queue
import threading
import sys
from game.ai import AlphaBetaPruner
from game.brain import Brain
from game.settings import *


class Controller(object):
    def next_move(self, pieces):
        pass

    def get_colour(self):
        pass


class PlayerController(Controller):

    def __init__(self, colour):
        self.colour = colour

    def next_move(self, board):
        result = None
        while result is None:
            event = input('Введите координаты, к примеру: c3, или нажмите Ctrl+D для выхода: ')
            try:
                if len(event) != 2:
                    raise ValueError
                x, y = event[0], event[1]
                result = self._parse_coordinates(x, y)
                found_moves = [p.get_position() for p in board.get_move_pieces(self.get_colour())]

                if not found_moves:
                    raise NoMovesError

                if result not in found_moves:
                    raise TypeError

            except (TypeError, ValueError):
                result = None
                print("Неверные координаты, попробуйте снова.")

        return result

    def get_colour(self):
        return self.colour

    def __str__(self):
        return "Player"

    def __repr__(self):
        return "PlayerController"

    @staticmethod
    def _parse_coordinates(x, y):
        return ord(x) - ord('a'), ord(y) - ord('0') - 1


stdoutmutex = threading.Lock()
workQueue = queue.Queue(1)
threads = []


class AiController(Controller):

    def __init__(self, id, colour, duration):
        self.id = id
        self.colour = colour
        self.duration = duration

    def next_move(self, board):
        brain = Brain(self.duration, stdoutmutex, workQueue, board.pieces, self.colour,
                      BLACK if self.colour is WHITE else WHITE)
        brain.start()

        threads.append(brain)

        update_step_duration = datetime.timedelta(microseconds=10000)
        goal_time = datetime.datetime.now() + update_step_duration
        accumulated_time = datetime.datetime.now()

        while workQueue.empty():
            if accumulated_time >= goal_time:
                print('.', end='')
                goal_time = datetime.datetime.now() + update_step_duration
                sys.stdout.flush()

            accumulated_time = datetime.datetime.now()

        print()

        for thread in threads:
            thread.join()

        return workQueue.get()

    def get_colour(self):
        return self.colour

    def __str__(self):
        return "Ai"

    def __repr__(self):
        return "AiController[" + self.id + "]"