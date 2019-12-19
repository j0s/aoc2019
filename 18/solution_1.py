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


def turn_left(direction):
    return coord(-direction.y, direction.x)


def turn_right(direction):
    return coord(direction.y, -direction.x)


def move(state):
    new_x = state['x'] + state['dir'].x
    new_y = state['y'] + state['dir'].y
    if (new_x >= len(state.tiles[0]) or
        new_y >= len(state.tiles) or
        state.tiles[new_y][new_x] == TILE_WALL):
        return False
    state['x'] = new_x
    state['y'] = new_y


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    tiles = []
    with open('input', 'r') as input_data:
        for line in input_data:
            tiles.append(list(line.strip()))

    state = {
        'dir': DIRECTION_UP,
        'visited_coords': {}
    }
    for y, line in enumerate(tiles):
        for x, char in enumerate(line):
            if char == '@':
                state['x'] = x
                state['y'] = y

    search_complete = False
    while not search_complete:
        if move(state):
            direction = turn_left(direction)

    print(tiles)


if __name__ == '__main__':
    if '--profile' in sys.argv:
        import cProfile
        cProfile.run('main(sys.argv)')
    else:
        main(sys.argv)
