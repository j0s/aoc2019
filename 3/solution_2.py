#!/usr/bin/env python

import sys

movements = {
    'U': lambda x, y, l: (x, y+l),
    'D': lambda x, y, l: (x, y-l),
    'R': lambda x, y, l: (x+l, y),
    'L': lambda x, y, l: (x-l, y),
}

def make_movement(from_x, from_y, start_distance, movement):
    direction = movement[0]
    length = int(movement[1:])
    if direction not in movements:
        raise Exception('Encountered invalid direction {}'.format(direction))
    movement_coords = {}
    return {movements[direction](from_x, from_y, l): start_distance+l for l in range(1, length+1)}, \
            start_distance + length, \
            movements[direction](from_x, from_y, length)

def calculate_path(wire):
    x, y = 0, 0
    total_distance = 0
    path_coords = {}
    for movement in wire:
        move_coords, total_distance, (x, y) = make_movement(x, y, total_distance, movement)
        # If a coordinate already exists in the path, we shall keep the
        # distance from before, so update move_coords with coords from path_coords
        move_coords.update(path_coords)
        path_coords = move_coords
    return path_coords

def path_intersections(wire_1_path, wire_2_path):
    wire_1_coords = set([coord for coord, _ in wire_1_path.items()])
    wire_2_coords = set([coord for coord, _ in wire_2_path.items()])
    return wire_1_coords & wire_2_coords

def get_closest_intersection_distance(wire_1, wire_2):
    """
    >>> get_closest_intersection_distance('R75,D30,R83,U83,L12,D49,R71,U7,L72', 'U62,R66,U55,R34,D71,R55,D58,R83')
    610
    >>> get_closest_intersection_distance('R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51', 'U98,R91,D20,R16,D67,R40,U7,R15,U6,R7')
    410
    """
    wire_1, wire_2 = wire_1.split(','), wire_2.split(',')
    wire_1_path, wire_2_path = calculate_path(wire_1), calculate_path(wire_2)
    intersections = path_intersections(wire_1_path, wire_2_path)
    return min([wire_1_path[coord] + wire_2_path[coord] for coord in intersections])

if len(sys.argv) > 1 and sys.argv[1] == '--test':
    import doctest
    doctest.testmod()
    sys.exit(0)

if __name__ == '__main__':
    with open('input', 'r') as input:
        wire_1 = input.readline()
        wire_2 = input.readline()
        print(get_closest_intersection_distance(wire_1, wire_2))
