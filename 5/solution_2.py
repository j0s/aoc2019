#!/usr/bin/env python

import sys
import math
import functools

ParamModePosition = 0
ParamModeImmediate = 1


def get_param_indices(intcode, modes, ix):
    return [ix+i if mode == ParamModeImmediate else intcode[ix+i] for i, mode in enumerate(modes, 1)]

def modes_list(modes):
    """
    >>> modes_list(300)
    [0, 0, 3]
    >>> modes_list(0)
    [0, 0, 0]
    >>> modes_list(1234)
    [4, 3, 2]
    """
    return [int(modes / math.pow(10, x)) % 10 for x in range(3)]

def instruction(num_args):
    def decorator_instruction(func):
        @functools.wraps(func)
        def execute_instruction(intcode, ix):
            modes = modes_list(intcode[ix] / 100)[:num_args]
            retval = func(intcode, *get_param_indices(intcode, modes, ix))
            # If the instruction doesn't return a new instruction counter,
            # just jump to next instruction
            return ix + num_args + 1 if retval is None else retval
        return execute_instruction
    return decorator_instruction


@instruction(num_args=3)
def add(intcode, lhs_ix, rhs_ix, result_ix):
    intcode[result_ix] = intcode[lhs_ix] + intcode[rhs_ix]

@instruction(num_args=3)
def multiply(intcode, lhs_ix, rhs_ix, result_ix):
    intcode[result_ix] = intcode[lhs_ix] * intcode[rhs_ix]

@instruction(num_args=1)
def store(intcode, store_ix):
    if 'doctest' in sys.modules:
        intcode[store_ix] = doctest.dummy_input
    else:
        intcode[store_ix] = int(input('Input: '))

@instruction(num_args=1)
def output(intcode, output_ix):
    print(intcode[output_ix], end='')

@instruction(num_args=2)
def jump_if_true(intcode, cond_ix, jump_ix):
    if intcode[cond_ix]:
        return intcode[jump_ix]

@instruction(num_args=2)
def jump_if_false(intcode, cond_ix, jump_ix):
    if not intcode[cond_ix]:
        return intcode[jump_ix]

@instruction(num_args=3)
def less_than(intcode, lhs_ix, rhs_ix, result_ix):
    intcode[result_ix] = int(intcode[lhs_ix] < intcode[rhs_ix])

@instruction(num_args=3)
def equals(intcode, lhs_ix, rhs_ix, result_ix):
    intcode[result_ix] = int(intcode[lhs_ix] == intcode[rhs_ix])

@instruction(num_args=0)
def quit(intcode):
    # Resetting the instruction counter to 0 terminates the program
    return 0

opcodes = {
    1: add,
    2: multiply,
    3: store,
    4: output,
    5: jump_if_true,
    6: jump_if_false,
    7: less_than,
    8: equals,
    99: quit
}


def run_intcode(intcode):
    """
    Basic tests from previous solutions just to catch regressions
    >>> run_intcode([1, 0, 0, 0, 99])
    [2, 0, 0, 0, 99]
    >>> run_intcode([2, 3, 0, 3, 99])
    [2, 3, 0, 6, 99]
    >>> run_intcode([2, 4, 4, 5, 99, 0])
    [2, 4, 4, 5, 99, 9801]
    >>> run_intcode([1, 1, 1, 4, 99, 5, 6, 0, 99])
    [30, 1, 1, 4, 2, 5, 6, 0, 99]
    >>> run_intcode([1002, 4, 3, 4, 33])
    [1002, 4, 3, 4, 99]

    This program should output 1 iff input == 8 (position mode)
    >>> for i in range(7, 10):
    ...     doctest.dummy_input = i
    ...     _ = run_intcode([3,9,8,9,10,9,4,9,99,-1,8])
    010

    This program should output 1 if input < 8 (position mode)
    >>> for i in range(7, 10):
    ...     doctest.dummy_input = i
    ...     _ = run_intcode([3,9,7,9,10,9,4,9,99,-1,8])
    100

    This program should output 1 iff input == 8 (immediate mode)
    >>> for i in range(7, 10):
    ...     doctest.dummy_input = i
    ...     _ = run_intcode([3,3,1108,-1,8,3,4,3,99])
    010

    This program should output 1 if input < 8 (immediate mode)
    >>> for i in range(7, 10):
    ...     doctest.dummy_input = i
    ...     _ = run_intcode([3,3,1107,-1,8,3,4,3,99])
    100

    Jump test, should output 0 iff input is 0 (position mode)
    >>> for i in range(3):
    ...     doctest.dummy_input = i
    ...     _ = run_intcode([3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9])
    011

    This program should output 999 if input < 8, 1000 if == 8, and 1001 otherwise
    >>> for i in range(7, 10):
    ...     doctest.dummy_input = i
    ...     _ = run_intcode([3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
    ...                      1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
    ...                      999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99])
    99910001001
    """
    ix = 0
    while ix < len(intcode):
        opcode = intcode[ix] % 100
        if opcode not in opcodes:
            raise Exception(f'Illegal opcode {opcode} at index {ix}')
        ix = opcodes[opcode](intcode, ix)
        if ix == 0:
            return intcode

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)
    doctest_input = None

    with open('input', 'r') as input_data:
        intcode = [int(x) for x in input_data.readline().split(',')]

    run_intcode(intcode)
