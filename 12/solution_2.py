#!/usr/bin/env python
""" Moon simulation """

import sys
import doctest
from functools import reduce


class Logger:
    """ Logger class """
    logfile = None

    @classmethod
    def init(cls, filename):
        """ Initialize logger to write to given file """
        cls.logfile = open(filename, 'w')

    @classmethod
    def log(cls, msg):
        """ Write message to log """
        if cls.logfile is not None:
            cls.logfile.write(msg+'\n')


def apply_acceleration(axis, moons):
    """ Update velocity fields of moons """
    for i, moon_1 in enumerate(moons, 1):
        for moon_2 in moons[i:]:
            if moon_1['pos'][axis] > moon_2['pos'][axis]:
                moon_1['vel'][axis] -= 1
                moon_2['vel'][axis] += 1
            elif moon_1['pos'][axis] < moon_2['pos'][axis]:
                moon_1['vel'][axis] += 1
                moon_2['vel'][axis] -= 1


def apply_velocity(axis, moons):
    """ Update position fields of moons """
    for moon in moons:
        moon['pos'][axis] += moon['vel'][axis]


def create_moon(x, y, z):
    return {'pos': {'x': x, 'y': y, 'z': z},
            'vel': {'x': 0, 'y': 0, 'z': 0}}


def potential_energy(moon):
    return sum([abs(val) for val in moon['pos'].values()])


def kinetic_energy(moon):
    return sum([abs(val) for val in moon['vel'].values()])


def calc_energy(moons):
    return sum([potential_energy(moon) * kinetic_energy(moon)
                for moon in moons])


def least_common_multiple(n1, n2):
    return n1 * n2 // greatest_common_denominator(n1, n2)


def greatest_common_denominator(n1, n2):
    while n2:
        n1, n2 = n2, n1 % n2
    return n1


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    # Calculate period for earch axis separately
    iterations = {}
    for axis in ['x', 'y', 'z']:
        moons = [create_moon(x=-4, y=-9, z=-3),
                 create_moon(x=-13, y=-11, z=0),
                 create_moon(x=-17, y=-7, z=15),
                 create_moon(x=-16, y=4, z=2)]

        start_coords = [moon['pos'][axis] for moon in moons]
        current_coords = []
        i = 1
        while start_coords != current_coords:
            apply_acceleration(axis, moons)
            apply_velocity(axis, moons)
            i += 1
            current_coords = [moon['pos'][axis] for moon in moons]
        iterations[axis] = i
    lcd = least_common_multiple(iterations['x'], iterations['y'])
    lcd = least_common_multiple(lcd, iterations['z'])

    print(f'total iterations: {lcd}')


if __name__ == '__main__':
    main(sys.argv)
