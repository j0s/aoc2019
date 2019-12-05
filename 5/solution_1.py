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
    >>> modes_list(123)
    [3, 2, 1]
    >>> modes_list(300)
    [0, 0, 3]
    >>> modes_list(0)
    [0, 0, 0]
    >>> modes_list(1234)
    [4, 3, 2]
    """
    return [int(modes / math.pow(10, x)) % 10 for x in range(3)]

def operator(num_args):
    def decorator_operator(func):
        @functools.wraps(func)
        def execute_operator(intcode, ix):
            modes = modes_list(intcode[ix] / 100)[:num_args]
            # print(f'executing {func} with arguments {ix}, {modes}, {get_param_indices(intcode, modes, ix)}')
            func(intcode, *get_param_indices(intcode, modes, ix))
            return 0 if num_args == 0 else num_args + 1
        return execute_operator
    return decorator_operator


@operator(num_args=3)
def add(intcode, lhs_ix, rhs_ix, result_ix):
    intcode[result_ix] = intcode[lhs_ix] + intcode[rhs_ix]

@operator(num_args=3)
def multiply(intcode, lhs_ix, rhs_ix, result_ix):
    intcode[result_ix] = intcode[lhs_ix] * intcode[rhs_ix]

@operator(num_args=1)
def store(intcode, store_ix):
    intcode[store_ix] = int(input('Enter value to store:'))

@operator(num_args=1)
def output(intcode, output_ix):
    print(intcode[output_ix], end='')

@operator(num_args=0)
def quit(intcode):
    pass

opcodes = {
    1: add,
    2: multiply,
    3: store,
    4: output,
    99: quit
}


def run_opcode(intcode, ix):
    opcode = intcode[ix] % 100
    if opcode not in opcodes:
        raise Exception(f'Illegal opcode {opcode} at index {ix}')
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
    >>> run_intcode([1002, 4, 3, 4, 33])
    [1002, 4, 3, 4, 99]
    """
    ix = 0
    while ix < len(intcode):
        offset = run_opcode(intcode, ix)
        if offset == 0:
            return intcode
        ix += offset


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)

    with open('input', 'r') as input_data:
        intcode = [int(x) for x in input_data.readline().split(',')]

    run_intcode(intcode)
