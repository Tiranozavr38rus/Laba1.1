#!/usr/bin/env python3
from game.game import Game


def main():
    players = ['random', 'ai']

    game = Game(timeout=0.1,
                display_moves=True,
                players=players)
    game.run()


if __name__ == "__main__":
    main()
