#!/usr/bin/env python
import sys


def get_fuel_required(weight):
    """
    >>> get_fuel_required(14)
    2
    >>> get_fuel_required(1969)
    966
    >>> get_fuel_required(100756)
    50346
    """
    fuel = int(weight / 3) - 2
    if fuel <= 0:
        return 0
    else:
        return fuel + get_fuel_required(fuel)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)

    total_mass = 0
    with open('input', 'r') as input:
        for line in input:
            total_mass += get_fuel_required(int(line))

    print(total_mass)
