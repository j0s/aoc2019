#!/usr/bin/env python

import sys


def add(intcode, ix):
    lh_ix, rh_ix, result_ix = intcode[ix+1], intcode[ix+2], intcode[ix+3]
    intcode[result_ix] = intcode[lh_ix] + intcode[rh_ix]
    return True


def multiply(intcode, ix):
    lh_ix, rh_ix, result_ix = intcode[ix+1], intcode[ix+2], intcode[ix+3]
    intcode[result_ix] = intcode[lh_ix] * intcode[rh_ix]
    return True


def quit(intcode, ix):
    return False


opcodes = {
    1: add,
    2: multiply,
    99: quit
}


def run_opcode(intcode, ix):
    opcode = intcode[ix]
    if opcode not in opcodes:
        raise Exception('Illegal opcode {}@{}'.format(opcode, ix))
    return opcodes[opcode](intcode, ix)


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
    ix = 0
    while ix < len(intcode) and run_opcode(intcode, ix):
        ix += 4


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)

    with open('input', 'r') as input:
        for line in input:
            intcode = [int(x) for x in line.split(',')]
            break

    for noun in range(100):
        for verb in range(100):
            tempcode = intcode.copy()
            tempcode[1] = noun
            tempcode[2] = verb
            run_intcode(tempcode)
            if tempcode[0] == 19690720:
                print('found noun, verb: {}, {}'.format(noun, verb))
                sys.exit(0)
