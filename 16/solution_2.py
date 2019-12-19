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


def gen_pattern(output_ix):
    while True:
        for n in [0, 1, 0, -1]:
            for _ in range(output_ix+1):
                yield n


def gen_offset_pattern(output_ix):
    fst = True
    for n in gen_pattern(output_ix):
        if fst:
            fst = False
        else:
            yield n


def apply_pattern(input_value):
    """
    >>> apply_pattern([1, 2, 3, 4, 5, 6, 7, 8])
    [4, 8, 2, 2, 6, 1, 5, 8]
    """
    output = []
    for i, _ in enumerate(input_value):
        s = sum([n*pattern for n, pattern in
                 zip(input_value, gen_offset_pattern(i))])
        output.append(abs(s) % 10)
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
    # Grows with the square of the input number
    inp = inp * 10
    apply_pattern_n_times(inp, 1)
    return inp[offset:offset+8]


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

    print(apply_pattern_n_times(input_value*10, 1))
    # output = get_message(input_value)
    # output = [str(o) for o in output]
    # print(''.join(output))


if __name__ == '__main__':
    if '--profile' in sys.argv:
        import cProfile
        cProfile.run('main(sys.argv)')
    else:
        main(sys.argv)
