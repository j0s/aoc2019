#!/usr/bin/env python
""" Intcode computer """

import sys
import doctest
from collections import namedtuple

coord = namedtuple('coord', ['x', 'y'])

DIRECTION_UP = coord(0, -1)
DIRECTION_DOWN = coord(0, 1)
DIRECTION_LEFT = coord(-1, 0)
DIRECTION_RIGHT = coord(1, 0)

TILE_WALL = '#'
TILE_GROUND = '.'
TILE_ROBOT = '@'


class Logger:
    """ Logger class """
    logfile = None

    @classmethod
    def init(cls, filename):
        """ Initialize logger to write to given file """
        cls.logfile = open(filename, 'w')

    @classmethod
    def initialized(cls):
        return cls.logfile is not None

    @classmethod
    def log(cls, msg):
        """ Write message to log """
        if cls.logfile is not None:
            cls.logfile.write(msg+'\n')


def add_coords(c1, c2):
    return coord(c1.x + c2.x, c1.y + c2.y)


def move(state):
    new_x = state['x'] + state['dir'].x
    new_y = state['y'] + state['dir'].y
    if (new_x >= len(state.tiles[0]) or
        new_y >= len(state.tiles) or
            state.tiles[new_y][new_x] == TILE_WALL):
        return False
    state['x'] = new_x
    state['y'] = new_y


def possible_moves(pos, tiles):
    moves = []
    if pos.x > 0 and tiles[pos.y][pos.x-1] != TILE_WALL:
        moves.append(DIRECTION_LEFT)
    if pos.y > 0 and tiles[pos.y-1][pos.x] != TILE_WALL:
        moves.append(DIRECTION_UP)
    if pos.x < len(tiles[0])-1 and tiles[pos.y][pos.x+1] != TILE_WALL:
        moves.append(DIRECTION_RIGHT)
    if pos.y < len(tiles)-1 and tiles[pos.y+1][pos.x] != TILE_WALL:
        moves.append(DIRECTION_DOWN)
    return moves


class State:
    def __init__(self, tiles):
        self.pos = coord(0, 0)
        self.dir = DIRECTION_UP
        self.visited_coords = {}
        self.tiles = tiles
        self.dist = 0
        self.keys = []

    def turn_left(self):
        self.dir = coord(-self.dir.y, self.dir.x)

    def turn_right(self):
        self.dir = coord(self.dir.y, -self.dir.x)

    def move(self, ignore_doors=False):
        new_x = self.pos.x + self.dir.x
        new_y = self.pos.y + self.dir.y
        if (new_x >= len(self.tiles[0]) or
                new_y >= len(self.tiles) or
                self.tiles[new_y][new_x] == TILE_WALL):
            return False
        self.pos = coord(new_x, new_y)
        self.dist += 1
        possible_keys = 'abcdefghijklmnopqrstuvwxyz'
        if self.tiles[new_y][new_x] in list(possible_keys):
            self.keys.append(self.tiles[new_y][new_x])
        elif self.tiles[new_y][new_x] in list(possible_keys.upper()):
            if (self.tiles[new_y][new_x].lower() not in self.keys and
                    not ignore_doors):
                return False
            self.keys.append(self.tiles[new_y][new_x])
        self.visited_coords[self.pos] = self.dist


def search(pos, tiles, direction):
    if move(pos, tiles, direction):
        pass
    for direction in possible_moves(pos, tiles):
        distances[pos] = search(pos, tiles, direction)


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    tiles = []
    with open('example_1', 'r') as input_data:
        for line in input_data:
            tiles.append(list(line.strip()))

    state = State(tiles)
    for y, line in enumerate(tiles):
        for x, char in enumerate(line):
            if char == '@':
                state.pos = coord(x, y)

    search_complete = False
    distances = {}

    print(tiles)


if __name__ == '__main__':
    if '--profile' in sys.argv:
        import cProfile
        cProfile.run('main(sys.argv)')
    else:
        main(sys.argv)
