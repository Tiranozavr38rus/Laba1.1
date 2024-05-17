import copy
import datetime
from game.settings import *


class AlphaBetaPruner(object):
    def __init__(self, mutex, duration, pieces, first_player, second_player):
        self.mutex = mutex
        self.board = 0
        self.move = 1
        self.white = 2
        self.black = 3
        self.duration = duration
        self.lifetime = None
        self.infinity = 1.0e400
        self.first_player, self.second_player = (self.white, self.black) \
            if first_player == WHITE else (self.black, self.white)
        self.state = self.make_state(pieces)

    def make_state(self, pieces):
        results = {BOARD: self.board, MOVE: self.board, WHITE: self.white, BLACK: self.black}
        return self.first_player, [results[p.get_state()] for p in pieces]

    def alpha_beta_search(self):
        self.lifetime = datetime.datetime.now() + datetime.timedelta(seconds=self.duration)
        depth = 0
        fn = lambda action: self.min_value(depth, self.next_state(self.state, action), -self.infinity,
                                           self.infinity)
        maxfn = lambda value: value[0]
        actions = self.actions(self.state)
        moves = [(fn(action), action) for action in actions]

        if len(moves) == 0:
            raise NoMovesError

        return max(moves, key=maxfn)[1]

    def max_value(self, depth, current_state, alpha, beta):
        if self.cutoff_test(current_state, depth):
            return self.evaluation(current_state, self.first_player)

        value = -self.infinity

        actions = self.actions(current_state)
        for action in actions:
            value = max([value, self.min_value(depth + 1, self.next_state(current_state, action), alpha, beta)])
            if value >= beta:
                return value
            alpha = max(alpha, value)

        return value

    def min_value(self, depth, state, alpha, beta):
        if self.cutoff_test(state, depth):
            return self.evaluation(state, self.second_player)

        value = self.infinity

        actions = self.actions(state)
        for action in actions:
            value = min([value, self.max_value(depth + 1, self.next_state(state, action), alpha, beta)])
            if value <= alpha:
                return value
            beta = min([beta, value])

        return value

    def evaluation(self, current_state, player_to_check):
        player_state, state = current_state
        player = player_to_check
        opponent = self.opponent(player)

        moves = self.get_moves(player, opponent, state)
        player_pieces = len([p for p in state if p == player])
        opponent_pieces = len([p for p in state if p == opponent])
        count_eval = 1 if player_pieces > opponent_pieces else \
            0 if player_pieces == opponent_pieces else \
                -1

        corners_player = (state[0] == player) + \
                         (state[7] == player) + \
                         (state[56] == player) + \
                         (state[63] == player)
        corners_opponent = -1 * (state[0] == opponent) + \
                           (state[7] == opponent) + \
                           (state[56] == opponent) + \
                           (state[63] == opponent)
        corners_eval = corners_player + corners_opponent

        edges_player = len([x for x in state if state == player and (state % 8 == 0 or state % 8 == 8)]) / (
                WIDTH * HEIGHT)
        edges_opponent = -1 * len([x for x in state if state == opponent and (state % 8 == 0 or state % 8 == 8)]) / (
                WIDTH * HEIGHT)
        edges_eval = edges_player + edges_opponent

        eval = count_eval * 2 + corners_eval * 1.5 + edges_eval * 1.2

        return eval

    def actions(self, current_state):
        tmp_state = copy.deepcopy(current_state)
        player, state = tmp_state
        return self.get_moves(player, self.opponent(player), state)

    def opponent(self, player):
        return self.second_player if player is self.first_player else self.first_player

    def next_state(self, current_state, action):
        placed = action[0] + (action[1] * WIDTH)
        player = copy.copy(current_state[0])
        state = copy.copy(current_state[1])
        opponent = self.opponent(player)

        state[placed] = player
        for d in DIRECTIONS:
            if outside_board(placed, d):
                continue

            to_flip = []
            tile = placed + d
            while state[tile] == opponent and not outside_board(tile, d):
                to_flip.append(tile)
                tile += d

            if state[tile] == player:
                for piece in to_flip:
                    state[piece] = player

        return opponent, state

    def get_moves(self, player, opponent, state):
        moves = [self.mark_move(player, opponent, tile, state, d)
                 for tile in range(WIDTH * HEIGHT)
                 for d in DIRECTIONS
                 if not outside_board(tile, d) and state[tile] == player]

        return [(x, y) for found, x, y, tile in moves if found]

    def mark_move(self, player, opponent, tile, pieces, direction):
        if not outside_board(tile, direction):
            tile += direction
        else:
            return False, int(tile % WIDTH), int(tile / HEIGHT), tile

        if pieces[tile] == opponent:
            while pieces[tile] == opponent:
                if outside_board(tile, direction):
                    break
                else:
                    tile += direction

            if pieces[tile] == self.board:
                return True, int(tile % WIDTH), int(tile / HEIGHT), tile

        return False, int(tile % WIDTH), int(tile / HEIGHT), tile

    def cutoff_test(self, state, depth):
        return depth > 1000 or datetime.datetime.now() > self.lifetime
