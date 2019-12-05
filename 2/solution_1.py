#!/usr/bin/env python

import sys


def add(intcode, ix):
    lh_ix, rh_ix, result_ix = intcode[ix+1], intcode[ix+2], intcode[ix+3]
    intcode[result_ix] = intcode[lh_ix] + intcode[rh_ix]
    return intcode, False


def multiply(intcode, ix):
    lh_ix, rh_ix, result_ix = intcode[ix+1], intcode[ix+2], intcode[ix+3]
    intcode[result_ix] = intcode[lh_ix] * intcode[rh_ix]
    return intcode, False


def quit(intcode, ix):
    return intcode, True


def run_intcode(intcode):
    """
    >>> run_intcode([1, 0, 0, 0, 99])
    [2, 0, 0, 0, 99]
    >>> run_intcode([2, 3, 0, 3, 99])
    [2, 3, 0, 6, 99]
    >>> run_intcode([2, 4, 4, 5, 99, 0])
    [2, 4, 4, 5, 99, 9801]
    >>> run_intcode([1, 1, 1, 4, 99, 5, 6, 0, 99])
    [30, 1, 1, 4, 2, 5, 6, 0, 99]
    """
    opcodes = {
        99: quit,
        1: add,
        2: multiply
    }
    ix = 0
    while ix < len(intcode):
        code = intcode[ix]
        if code not in opcodes:
            raise Exception('Illegal opcode {}@{}'.format(code, ix))
        intcode, halt = opcodes[code](intcode, ix)
        if halt:
            return intcode
        ix += 4


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)

    with open('input', 'r') as input:
        for line in input:
            intcode = [int(x) for x in line.split(',')]
            intcode[1] = 12
            intcode[2] = 2
            intcode = run_intcode(intcode)
            print(intcode)
