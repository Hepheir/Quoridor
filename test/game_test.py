import pytest

from quoridor import Game


def test_game_1():
    move_sequence = ["e8", "e2",
                     "e7", "e3",
                     "e6", "e4",
                     "e6h", "e3h",
                     "f5v", "e5h",
                     "c6h", "f4",
                     "f3v", "g6h",
                     "a6h", "e4",
                     "c5v", "d4h",
                     "d2v", "d4",
                     "d6", "d3",
                     "d5", "c3h",
                     "h4", "d2",
                     "c1h", "a2h",
                     "h7h", ]
    game = Game()
    game.start()
    for move in move_sequence:
        game.move(move)


def test_game_2():
    move_sequence = ["e8", "e2",
                     "e7", "e3",
                     "e6", "e4",
                     "e5", "e6",
                     "e4", "e7",
                     "e3", "e8",
                     "e2", "e9", ]
    game = Game()
    game.start()
    for move in move_sequence:
        game.move(move)


if __name__ == "__main__":
    test_game_1()
    test_game_2()
