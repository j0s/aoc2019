#!/usr/bin/env python

import sys
import math
import doctest


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


def apply_pattern(input_value):
    """
    >>> apply_pattern([1, 2, 3, 4, 5, 6, 7, 8])
    [4, 8, 2, 2, 6, 1, 5, 8]
    """
    # Since we are at the last half, output[i]
    # is just the sum if input[i:]
    output = [0]*len(input_value)
    s = 0
    i = len(input_value) - 1
    while i >= 0:
        s += input_value[i]
        output[i] = abs(s) % 10
        i -= 1
    return output


def apply_pattern_n_times(inp, n):
    """
    >>> apply_pattern_n_times([1, 2, 3, 4, 5, 6, 7, 8], 4)
    [0, 1, 0, 2, 9, 4, 9, 8]
    """
    for _ in range(n):
        inp = apply_pattern(inp)
    return inp


def get_message(inp):
    offset = inp[0:7]
    offset.reverse()
    offset = int(sum([n*math.pow(10, i) for i, n in enumerate(offset)]))
    inp = inp * 10000
    # Since the offset is more than half of the array, the pattern
    # is only zeroes up until the digit we are calculating, so we
    # can safely discard the first offset digits
    inp = inp[offset:]
    out = apply_pattern_n_times(inp, 100)
    return out[:8]


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    with open('input', 'r') as input_data:
        for line in input_data:
            input_value = [int(c) for c in line.strip()]

    output = get_message(input_value)
    print(''.join([str(o) for o in output]))


if __name__ == '__main__':
    if '--profile' in sys.argv:
        import cProfile
        cProfile.run('main(sys.argv)')
    else:
        main(sys.argv)
