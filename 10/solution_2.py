#!/usr/bin/env python

import sys
import math


def print_asteroids(input_file, asteroids, asteroids_hit, origin=None):
    with open(input_file, 'r') as input_data:
        width, height = [(len(line.strip()), i) for i, line in enumerate(input_data, 1)][-1]
    logfile = open('output', 'w')
    hit_number = 0
    lines = [['.']*width for x in range(height)]
    try:
        for (x, y) in asteroids:
            lines[y][x] = '#'
        for hit_number, (x, y) in enumerate(asteroids_hit, 1):
            lines[y][x] = f'{hit_number}'
        if origin is not None:
            lines[origin[1]][origin[0]] = 'X'
        for line in lines:
            logfile.write(''.join(line) + '\n')
    except Exception as e:
        print(f'failed to add asteroid at ({x}, {y}), len(lines) == {len(lines)}, len(lines[y]) == {len(lines[y])}')
    assert hit_number == len(asteroids_hit), f'{hit_number} != {len(asteroids_hit)}, {len(asteroids)}'


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
            output += [(x, y) for x, char in enumerate(line) if char in ['#', 'X']]
    return output


def asteroids_visible_from(asteroids, x, y):
    visible_asteroids = {}
    for asteroid_x, asteroid_y in asteroids:
        if asteroid_x == x and asteroid_y == y:
            continue
        # use negative y axis as 0, so when I sort by angle,
        # the asteroids closest to the positive y axis when
        # rotating clockwise, come first
        angle = math.atan2(x - asteroid_x, asteroid_y - y)
        if angle == math.pi:
            angle = -angle
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

    input_file = 'input'
    asteroids = parse_asteroids(input_file)

    best_spot, best_score = (0, 0), 0
    for x, y in asteroids:
        score = len(asteroids_visible_from(asteroids, x, y))
        if score > best_score:
            best_spot, best_score = (x, y), score

    print(f'best spot: {best_spot}, best score: {best_score}')
    asteroids_to_shoot = asteroids_visible_from(
        asteroids, best_spot[0], best_spot[1])
    print(asteroids_to_shoot)
    asteroids_shot = []
    while len(asteroids_to_shoot) > 0:
        for angle in sorted(asteroids_to_shoot):
            if len(asteroids_to_shoot[angle]) == 1:
                asteroids_shot.extend(asteroids_to_shoot.pop(angle))
            else:
                asteroids_shot.append(asteroids_to_shoot[angle].pop(0))
    print_asteroids(input_file, asteroids, asteroids_shot, best_spot)
    print(asteroids_shot[199])
