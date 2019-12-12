#!/usr/bin/env python
""" Moon simulation """

import sys
import doctest


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


def apply_acceleration(moons):
    """ Update velocity fields of moons """
    for i, moon_1 in enumerate(moons, 1):
        for moon_2 in moons[i:]:
            for axis in ['x', 'y', 'z']:
                if moon_1['pos'][axis] > moon_2['pos'][axis]:
                    moon_1['vel'][axis] -= 1
                    moon_2['vel'][axis] += 1
                elif moon_1['pos'][axis] < moon_2['pos'][axis]:
                    moon_1['vel'][axis] += 1
                    moon_2['vel'][axis] -= 1


def apply_velocity(moons):
    """ Update position fields of moons """
    for moon in moons:
        for axis, value in moon['vel'].items():
            moon['pos'][axis] += value


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


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    # moons = [create_moon(x=-8, y=-10, z=0),
    #          create_moon(x=5, y=5, z=10),
    #          create_moon(x=2, y=-7, z=3),
    #          create_moon(x=9, y=-8, z=-3)]
    # moons = [create_moon(-1, 0, 2),
    #          create_moon(2, -10, -7),
    #          create_moon(4, -8, 8),
    #          create_moon(3, 5, -1)]
    moons = [create_moon(x=-4, y=-9, z=-3),
             create_moon(x=-13, y=-11, z=0),
             create_moon(x=-17, y=-7, z=15),
             create_moon(x=-16, y=4, z=2)]

    for i in range(1000):
        print(i)
        for moon in moons:
            print(moon)
        apply_acceleration(moons)
        apply_velocity(moons)
        print('energy:', calc_energy(moons))

    for moon in moons:
        print(moon)
    print('energy:', calc_energy(moons))


if __name__ == '__main__':
    main(sys.argv)
