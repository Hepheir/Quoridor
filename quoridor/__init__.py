from __future__ import annotations

from enum import Enum
from queue import Queue
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set


class CardinalPoint(Enum):
    WEST = 'west'
    EAST = 'east'
    NORTH = 'north'
    SOUTH = 'south'

    @classmethod
    def orthogonal_points(cls, point: CardinalPoint) -> Iterable[CardinalPoint]:
        """Orthogonal points"""

        if point in (CardinalPoint.NORTH, CardinalPoint.SOUTH):
            yield CardinalPoint.WEST
            yield CardinalPoint.EAST
        elif point in (CardinalPoint.WEST, CardinalPoint.EAST):
            yield CardinalPoint.NORTH
            yield CardinalPoint.SOUTH
        else:
            raise ValueError


class Coordinate:
    y: int
    x: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return self.column_name() + self.row_name()

    def __repr__(self) -> str:
        return self.__str__()

    def column_name(self) -> str:
        return chr(ord('a')+self.x)

    def row_name(self) -> str:
        return str(1+self.y)


class CoordinateSequence:
    def __init__(self, *args: Iterable[Coordinate]) -> None:
        self.list: List[Coordinate] = list(args[0])

    def __getitem__(self, index: int) -> Coordinate:
        self.list[index]

    def __iter__(self) -> Iterable[Coordinate]:
        self.n = 0
        return self

    def __next__(self) -> Coordinate:
        if self.n < len(self.list):
            item = self.list[self.n]
            self.n += 1
            return item
        else:
            raise StopIteration

    def __str__(self) -> str:
        return ','.join(map(str, self.list))

    def __repr__(self) -> str:
        return self.__str__()

    def __contains__(self, item: Coordinate) -> bool:
        return item in self.list


class Square(Coordinate):
    def __init__(self, game: Game, x: int, y: int) -> None:
        super().__init__(x, y)
        self.game = game
        self.has_horizontal_fence = False
        self.has_vertical_fence = False

    def __hash__(self) -> int:
        return hash(self.__str__())

    @property
    def has_pawn(self) -> bool:
        for player in self.game.players:
            if self is player.pawn:
                return True
        return False

    @property
    def west_square(self) -> Square:
        return self.game.board.get(self.y, self.x-1)

    @property
    def east_square(self) -> Square:
        return self.game.board.get(self.y, self.x+1)

    @property
    def north_square(self) -> Square:
        return self.game.board.get(self.y-1, self.x)

    @property
    def south_square(self) -> Square:
        return self.game.board.get(self.y+1, self.x)

    @property
    def west_fence(self) -> bool:
        return (
            (self.west_square and self.west_square.has_vertical_fence)
            or (self.west_square and self.west_square.north_square and self.west_square.north_square.has_vertical_fence)
        )

    @property
    def east_fence(self) -> bool:
        return (
            self.has_vertical_fence
            or (self.north_square
                and self.north_square.has_vertical_fence)
        )

    @property
    def north_fence(self) -> bool:
        return (
            (self.north_square and self.north_square.has_horizontal_fence)
            or (self.north_square and self.north_square.west_square and self.north_square.west_square.has_horizontal_fence)
        )

    @property
    def south_fence(self) -> bool:
        return (
            self.has_horizontal_fence
            or (self.west_square and self.west_square.has_horizontal_fence)
        )

    def square_at(self, point: CardinalPoint) -> Optional[Square]:
        if point == CardinalPoint.WEST:
            return self.west_square
        elif point == CardinalPoint.EAST:
            return self.east_square
        elif point == CardinalPoint.SOUTH:
            return self.south_square
        elif point == CardinalPoint.NORTH:
            return self.north_square
        else:
            raise ValueError

    def has_fence_at(self, point: CardinalPoint) -> bool:
        if point == CardinalPoint.WEST:
            return self.west_fence
        elif point == CardinalPoint.EAST:
            return self.east_fence
        elif point == CardinalPoint.SOUTH:
            return self.south_fence
        elif point == CardinalPoint.NORTH:
            return self.north_fence
        else:
            raise ValueError

    def is_connected_with_square_at(self, cardinal_point: CardinalPoint) -> bool:
        square = self.square_at(cardinal_point)
        fenced = self.has_fence_at(cardinal_point)
        return square and not fenced

    def cardinal_neighbors(self) -> Iterable[Square]:
        for cardinal_point in CardinalPoint:
            if self.is_connected_with_square_at(cardinal_point):
                yield self.square_at(cardinal_point)

    def place_horizontal_fence(self) -> None:
        self.has_horizontal_fence = True

    def place_vertical_fence(self) -> None:
        self.has_vertical_fence = True


class Board:
    def __init__(self, game: Game, width: int, height: int) -> None:
        self.game = game
        self.width = width
        self.height = height
        self.table = [[Square(game, x, y) for x in range(width)]
                      for y in range(height)]

    def __getitem__(self, coordinate: str) -> Square:
        x = ord(coordinate[0]) - ord('a')
        y = int(coordinate[1]) - 1
        return self.table[y][x]

    def get_row(self, y: int) -> CoordinateSequence:
        return CoordinateSequence(self.table[y])

    def get_column(self, x: int) -> CoordinateSequence:
        return CoordinateSequence([self.table[y][x] for y in range(self.height)])

    def get(self, y: int, x: int) -> Square | None:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.table[y][x]
        else:
            return None

    def draw(self) -> str:
        lines = []

        prefix = f'{"":4<s}'
        line = prefix
        for x in range(self.width):
            line += f' {chr(ord("a")+x):2s} '
        lines.append(line+'\n')

        for y in range(self.height):
            prefix = f'{y+1:4<d}'

            line = prefix
            for x in range(self.width):
                square = self.get(y, x)
                line += '[*]' if square.has_pawn else '[ ]'
                line += '|' if square.east_fence else ' '
            lines.append(line + '\n')

            line = prefix
            for x in range(self.width):
                square = self.get(y, x)
                line += '---' if square.south_fence else '   '

                if square.has_horizontal_fence:
                    line += '-'
                elif square.has_vertical_fence:
                    line += '|'
                else:
                    line += ' '
            lines.append(line + '\n')
        return lines


class Move:
    @classmethod
    def parse(self, game: Game, s: str) -> Move_MovePawn | Move_PlaceFenceHorizontally | Move_PlaceFenceVertically:
        coordinate = game.board[s[:2]]
        if len(s) < 3:
            move = Move_MovePawn(game, coordinate)
        elif s[2] == 'h':
            move = Move_PlaceFenceHorizontally(game, coordinate)
        elif s[2] == 'v':
            move = Move_PlaceFenceVertically(game, coordinate)
        else:
            raise ValueError
        return move

    def __init__(self, game: Game) -> None:
        self.game = game

    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__str__()

    def check_valid(self) -> bool:
        raise NotImplementedError

    def apply(self) -> None:
        raise NotImplementedError


class Move_MovePawn(Move):
    def __init__(self, game: Game, square: Square) -> None:
        super().__init__(game)
        self.square: Square = square

    def __str__(self) -> str:
        return f'move:pawn>{self.game.current_player.pawn}>{self.square}'

    def check_valid(self) -> bool:
        possible_moves: Set[Square] = set()

        square_0 = self.game.current_player.pawn
        for cardinal_point in CardinalPoint:
            if not square_0.is_connected_with_square_at(cardinal_point):
                continue
            square_1 = square_0.square_at(cardinal_point)
            if square_1.has_pawn:
                if square_1.is_connected_with_square_at(cardinal_point):
                    square_2 = square_1.square_at(cardinal_point)
                    possible_moves.add(square_2)
                    continue
                for orthogonal_point in CardinalPoint.orthogonal_points(cardinal_point):
                    if square_1.is_connected_with_square_at(orthogonal_point):
                        square_2 = square_1.square_at(orthogonal_point)
                        possible_moves.add(square_2)
            else:
                possible_moves.add(square_1)

        return self.square in possible_moves

    def apply(self) -> None:
        self.game.current_player.pawn = self.square


class Move_PlaceFenceHorizontally(Move):
    def __init__(self, game: Game, square: Square) -> None:
        super().__init__(game)
        self.square: Square = square

    def __str__(self) -> str:
        return f'move:fence>{self.square}h'

    def check_valid(self) -> bool:
        if self.square.has_horizontal_fence:
            return False
        if self.square.east_square and self.square.east_square.has_horizontal_fence:
            return False
        for player in self.game.players:
            if not self._can_player_reach_goal(player):
                return False
        return True

    def apply(self) -> None:
        self.square.place_horizontal_fence()

    def _can_player_reach_goal(self, player: Player) -> bool:
        visited: Set[Square] = set()
        queue: Queue[Square] = Queue()
        queue.put(player.pawn)
        while queue:
            width = queue.qsize()
            for w in range(width):
                square = queue.get()
                if square in player.goals:
                    return True
                if square not in visited:
                    visited.add(square)
                    for neighbor in square.cardinal_neighbors():
                        queue.put(neighbor)
        return False


class Move_PlaceFenceVertically(Move):
    def __init__(self, game: Game, square: Square) -> None:
        super().__init__(game)
        self.square: Square = square

    def __str__(self) -> str:
        return f'move:fence>{self.square}v'

    def check_valid(self) -> bool:
        if self.square.has_vertical_fence:
            return False
        if self.square.south_square and self.square.south_square.has_vertical_fence:
            return False
        for player in self.game.players:
            if not self._can_player_reach_goal(player):
                return False
        return True

    def apply(self) -> None:
        self.square.place_vertical_fence()

    def _can_player_reach_goal(self, player: Player) -> bool:
        visited: Set[Square] = set()
        queue: Queue[Square] = Queue()
        queue.put(player.pawn)
        while queue:
            width = queue.qsize()
            for w in range(width):
                square = queue.get()
                if square in player.goals:
                    return True
                if square not in visited:
                    visited.add(square)
                    for neighbor in square.cardinal_neighbors():
                        queue.put(neighbor)
        return False


class Player:
    game: Game
    remaining_fences: int
    pawn: Square
    goals: CoordinateSequence

    def __init__(self, game: Game) -> None:
        self.game = game
        self.remaining_fences = 0
        self.pawn = None
        self.goals = None

    def __str__(self) -> str:
        return f'Player@{self.pawn}'

    def __repr__(self) -> str:
        return self.__str__()


class Game:
    def __init__(self) -> None:
        self.players: List[Player] = []
        self.turn: int = None
        self.is_ingame = False

    @property
    def current_player(self) -> Player:
        index = self.turn % len(self.players)
        return self.players[index]

    def _start(self) -> None:
        self._setup()
        self.turn = 1
        self.is_ingame = True
        self._start_turn()

    def _setup(self) -> None:
        width = 9
        height = 9
        n_players = 2
        n_fences = 20

        self.board = Board(self, width, height)
        self.players = [Player(self) for i in range(n_players)]

        self.players[0].pawn = self.board['e1']
        self.players[0].goals = self.board.get_row(8)
        self.players[0].remaining_fences = n_fences//n_players

        self.players[1].pawn = self.board['e9']
        self.players[1].goals = self.board.get_row(0)
        self.players[1].remaining_fences = n_fences//n_players

    def _start_turn(self) -> None:
        print(f"Starting {self.current_player}'s turn.")

    def _end_turn(self) -> None:
        print(f"End of {self.current_player}'s turn.")
        print()

        if self.current_player.pawn in self.current_player.goals:
            self._end()
        else:
            self.turn += 1
            self._start_turn()

    def _end(self) -> None:
        winner = self.current_player
        print(f"Player {winner} has won!")
        self.is_ingame = False

    def start(self) -> None:
        return self._start()

    def move(self, s: str) -> None:
        if self.turn is None:
            raise Exception('The game has not started.')

        m = Move.parse(self, s)
        if m.check_valid():
            print(m)
            m.apply()
            self._end_turn()
        else:
            print('Invalid move.')
            self._start_turn()
