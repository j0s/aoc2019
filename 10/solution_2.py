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
    return output


def asteroids_visible_from(asteroids, x, y):
    visible_asteroids = {}
    for asteroid_x, asteroid_y in asteroids:
        if asteroid_x == x and asteroid_y == y:
            continue
        # use negative y axis as 0, so when I sort by angle,
        # the asteroids closest to the positive y axis when
        # rotating clockwise, come first
        angle = -math.atan2(asteroid_x - x, y - asteroid_y)
        #angle = math.atan2(asteroid_y - y, asteroid_x - x)
        visible_asteroids.setdefault(
            angle, []).append((asteroid_x, asteroid_y))

    for angle in visible_asteroids.keys():
        visible_asteroids[angle].sort(key=lambda asteroid: math.sqrt(
            math.pow(asteroid[0] - x, 2) + math.pow(asteroid[1] - y, 2)))
    return visible_asteroids


if __name__ == '__main__':
    debug = '--debug' in sys.argv
    if '--test' in sys.argv:
        import doctest
        doctest.testmod()
        sys.exit(0)

    asteroids = parse_asteroids('input')

    best_spot = (0, 0, 0)
    for x, y in asteroids:
        score = len(asteroids_visible_from(asteroids, x, y))
        if score > best_spot[0]:
            best_spot = (score, x, y)

    print(f'best spot: {best_spot}')
    asteroids_to_shoot = asteroids_visible_from(
        asteroids, best_spot[1], best_spot[2])
    print(asteroids_to_shoot)
    asteroids_shot = []
    while len(asteroids_shot) < 200:
        for angle in sorted(asteroids_to_shoot):
            if len(asteroids_to_shoot[angle]) == 1:
                asteroids_shot.append(asteroids_to_shoot.pop(angle)[0])
            else:
                asteroids_shot.append(asteroids_to_shoot[angle].pop(0))
    print(asteroids_shot)
