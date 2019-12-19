#!/usr/bin/env python
""" Intcode computer """

import sys
import math
import functools
import doctest

PARAM_MODE_POSITION = 0
PARAM_MODE_IMMEDIATE = 1
PARAM_MODE_RELATIVE = 2

STATE_NOT_STARTED = 0
STATE_RUNNING = 1
STATE_WAIT_FOR_INPUT = 2
STATE_TERMINATED = 3


def get_param_indices(state, modes, opcode_ix):
    """
    Get intcode index for each paremeter, given
    an array of parameter nodes and the opcode index
    """
    return [state.intcode[opcode_ix+i] if mode == PARAM_MODE_POSITION else
            opcode_ix+i if mode == PARAM_MODE_IMMEDIATE else
            state.relative_base + state.intcode[opcode_ix+i]
            for i, mode in enumerate(modes, 1)]


def modes_list(modes):
    """
    >>> modes_list(300)
    [0, 0, 3]
    >>> modes_list(0)
    [0, 0, 0]
    >>> modes_list(1234)
    [4, 3, 2]
    """
    a = modes % 10
    b = (modes % 100 - a) // 10
    c = (modes % 1000 - b - a) // 100
    return [a, b, c]


class ExecutionState:  # pylint: disable=too-few-public-methods
    """ Stores the current state of intcode execution """
    def __init__(self, intcode, inputs=[]):  # pylint: disable=dangerous-default-value
        self.intcode = intcode
        self.inputs = inputs
        self.outputs = []
        self.ic = 0                         # pylint: disable=invalid-name
        self.status = STATE_NOT_STARTED
        self.relative_base = 0

    def __repr__(self):
        return (f'intcode: {self.intcode}, inputs: {self.inputs}, ' +
                f'outputs: {self.outputs}, ic: {self.ic}, ' +
                f'state: {self.status}, relative_base: {self.relative_base}')


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


def instruction(num_args):
    """
    Decorator for defining an intcode function
    taking num_args parameters
    """
    def decorator_instruction(func):
        @functools.wraps(func)
        def execute_instruction(state):
            state.status = STATE_RUNNING
            modes = modes_list(state.intcode[state.ic] // 100)[:num_args]
            params = get_param_indices(state, modes, state.ic)
            if params and len(state.intcode) <= max(params):
                state.intcode.extend([0]*(max(params) - len(state.intcode) + 1))
            new_ic = func(state, *params)
            # Logger.log(f'{func.__name__}: {params} {state}')
            if state.status != STATE_WAIT_FOR_INPUT:
                state.ic = ((state.ic + num_args + 1)
                            if new_ic is None else new_ic)
        return execute_instruction
    return decorator_instruction


@instruction(num_args=1)
def adjust_relative_base(state, relative_base_ix):
    """ Adjust relative address base with value in first argument """
    state.relative_base += state.intcode[relative_base_ix]


@instruction(num_args=3)
def add(state, lhs_ix, rhs_ix, result_ix):
    """ Add first and second arguments, store result at third argument """
    state.intcode[result_ix] = state.intcode[lhs_ix] + state.intcode[rhs_ix]


@instruction(num_args=3)
def multiply(state, lhs_ix, rhs_ix, result_ix):
    """ Multiply first and second arguments, store result at third argument """
    state.intcode[result_ix] = state.intcode[lhs_ix] * state.intcode[rhs_ix]


@instruction(num_args=1)
def store(state, store_ix):
    """ Store first input in first parameter """
    if len(state.inputs) == 0:
        state.status = STATE_WAIT_FOR_INPUT
    else:
        state.intcode[store_ix] = state.inputs.pop(0)


@instruction(num_args=1)
def output(state, output_ix):
    """ Append value at first argument to outputs """
    state.outputs.append(state.intcode[output_ix])


@instruction(num_args=2)
def jump_if_true(state, cond_ix, jump_ix):
    """ Jump to address in second parameter if first parameter is true """
    if state.intcode[cond_ix]:
        return state.intcode[jump_ix]
    return None


@instruction(num_args=2)
def jump_if_false(state, cond_ix, jump_ix):
    """ Jump to address in second parameter if first parameter is false """
    if not state.intcode[cond_ix]:
        return state.intcode[jump_ix]
    return None


@instruction(num_args=3)
def less_than(state, lhs_ix, rhs_ix, result_ix):
    """ If first parameter is less than second, store 1 at third
    parameter, otherwise store 0 """
    state.intcode[result_ix] = int(
        state.intcode[lhs_ix] < state.intcode[rhs_ix])


@instruction(num_args=3)
def equals(state, lhs_ix, rhs_ix, result_ix):
    """ Check if parameters are equal, store at third parameter """
    state.intcode[result_ix] = int(
        state.intcode[lhs_ix] == state.intcode[rhs_ix])


@instruction(num_args=0)
def terminate(state):
    """ Terminate the program"""
    state.status = STATE_TERMINATED


OPCODES = {
    1: add,
    2: multiply,
    3: store,
    4: output,
    5: jump_if_true,
    6: jump_if_false,
    7: less_than,
    8: equals,
    9: adjust_relative_base,
    99: terminate
}


def run_intcode(state):
    """
    Basic tests from previous solutions just to catch regressions

    >>> state = ExecutionState([1, 0, 0, 0, 99])
    >>> run_intcode(state)
    >>> state.intcode
    [2, 0, 0, 0, 99]
    >>> state = ExecutionState([2, 3, 0, 3, 99])
    >>> run_intcode(state)
    >>> state.intcode
    [2, 3, 0, 6, 99]
    >>> state = ExecutionState([2, 4, 4, 5, 99, 0])
    >>> run_intcode(state)
    >>> state.intcode
    [2, 4, 4, 5, 99, 9801]
    >>> state = ExecutionState([1, 1, 1, 4, 99, 5, 6, 0, 99])
    >>> run_intcode(state)
    >>> state.intcode
    [30, 1, 1, 4, 2, 5, 6, 0, 99]
    >>> state = ExecutionState([1002, 4, 3, 4, 33])
    >>> run_intcode(state)
    >>> state.intcode
    [1002, 4, 3, 4, 99]

    This program should output 1 iff input == 8 (position mode)
    >>> for i in range(7, 10):
    ...     state = ExecutionState([3,9,8,9,10,9,4,9,99,-1,8], [i])
    ...     run_intcode(state)
    ...     state.outputs
    [0]
    [1]
    [0]

    This program should output 1 if input < 8 (position mode)
    >>> for i in range(7, 10):
    ...     state = ExecutionState([3,9,7,9,10,9,4,9,99,-1,8], [i])
    ...     run_intcode(state)
    ...     state.outputs
    [1]
    [0]
    [0]

    This program should output 1 iff input == 8 (immediate mode)
    >>> for i in range(7, 10):
    ...     state = ExecutionState([3,3,1108,-1,8,3,4,3,99], [i])
    ...     run_intcode(state)
    ...     state.outputs
    [0]
    [1]
    [0]

    This program should output 1 if input < 8 (immediate mode)
    >>> for i in range(7, 10):
    ...     state = ExecutionState([3,3,1107,-1,8,3,4,3,99], [i])
    ...     run_intcode(state)
    ...     state.outputs
    [1]
    [0]
    [0]

    Jump test, should output 0 iff input is 0 (position mode)
    >>> for i in range(3):
    ...     state = ExecutionState([3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9],
    ...                            [i])
    ...     run_intcode(state)
    ...     state.outputs
    [0]
    [1]
    [1]

    This program should output 999 if input < 8, 1000 if == 8, 1001 otherwise
    >>> for i in range(7, 10):
    ...     state = ExecutionState([3,21,1008,21,8,20,1005,20,22,107,8,21,20,
    ...                             1006,20,31,1106,0,36,98,0,0,1002,21,125,20,
    ...                             4,20,1105,1,46,104,999,1105,1,46,1101,1000,
    ...                             1,20,4,20,1105,1,46,98,99], [i])
    ...     run_intcode(state)
    ...     state.outputs
    [999]
    [1000]
    [1001]

    Takes no input and should produce a copy of itself as output
    >>> state = ExecutionState([109,1,204,-1,1001,100,1,100,1008,100,16,101,
    ...                         1006,101,0,99])
    >>> run_intcode(state)
    >>> state.outputs
    [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]

    Should produce 16 digit number
    >>> state = ExecutionState([1102,34915192,34915192,7,4,7,99,0])
    >>> run_intcode(state)
    >>> len(str(state.outputs[0]))
    16

    >>> state = ExecutionState([104,1125899906842624,99])
    >>> run_intcode(state)
    >>> state.outputs[0]
    1125899906842624
    """
    while state.ic < len(state.intcode):
        opcode = state.intcode[state.ic] % 100
        if opcode not in OPCODES:
            debug_intcode = [(ix, opcode) for ix, opcode
                             in enumerate(state.intcode)]
            raise Exception(f'Illegal opcode {opcode} at index {state.ic}'
                            f'\nintcode: {debug_intcode}')

        OPCODES[opcode](state)
        if state.status in [STATE_TERMINATED, STATE_WAIT_FOR_INPUT]:
            return state.status


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    with open('input', 'r') as input_data:
        intcode = [int(x) for x in input_data.readline().split(',')]

    inputs = []
    for y in range(50):
        for x in range(50):
            inputs.append(x)
            inputs.append(y)

    outputs = []
    while inputs:
        state = ExecutionState(intcode.copy(), inputs)
        run_intcode(state)
        outputs.extend(state.outputs)

    print(outputs.count(1))


if __name__ == '__main__':
    if '--profile' in sys.argv:
        import cProfile
        cProfile.run('main(sys.argv)')
    else:
        main(sys.argv)
