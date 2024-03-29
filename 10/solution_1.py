#!/usr/bin/env python

import sys
import math
logfile = open('output', 'w')


def log(msg):
    if debug:
        logfile.write(msg+'\n')


def parse_input(filename):
    output = []
    with open(filename, 'r') as input_data:
        for line in input_data:
            output.append([1 if char == '#' else 0 for char in line])
    return output


def parse_asteroids(filename):
    output = []
    with open(filename, 'r') as input_data:
        for y, line in enumerate(input_data):
            output += [(x, y) for x, char in enumerate(line) if char == '#']
    print(output)
    return output


def num_asteroids_visible_from(asteroids, x, y):
    visible_asteroids = set()
    for asteroid_x, asteroid_y in asteroids:
        if asteroid_x == x and asteroid_y == y:
            continue
        # Asteroids blocking each other are at the same angle,
        # so just add the angle to the set
        angle = math.atan2(asteroid_x - x, asteroid_y - y)
        visible_asteroids.add(angle)

    return len(visible_asteroids)


if __name__ == '__main__':
    debug = '--debug' in sys.argv
    if '--test' in sys.argv:
        import doctest
        doctest.testmod()
        sys.exit(0)

    asteroids = parse_asteroids('input')

    print(max([num_asteroids_visible_from(asteroids, x, y)
               for (x, y) in asteroids]))
