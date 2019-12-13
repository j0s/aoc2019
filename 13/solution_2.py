#!/usr/bin/env python
""" Intcode computer """

import sys
import math
import functools
import doctest
from collections import namedtuple

PARAM_MODE_POSITION = 0
PARAM_MODE_IMMEDIATE = 1
PARAM_MODE_RELATIVE = 2

STATE_NOT_STARTED = 0
STATE_RUNNING = 1
STATE_WAIT_FOR_INPUT = 2
STATE_TERMINATED = 3

TILE_BLACK = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_PADDLE = 3
TILE_BALL = 4
TILE_ASCII_MAP = {
    TILE_BLACK: ord('.'),
    TILE_WALL: ord('+'),
    TILE_BLOCK: ord('#'),
    TILE_PADDLE: ord('-'),
    TILE_BALL: ord('O')
}


def draw_tile(tiles, x, y, tile):
    tiles[x][y] = tile


def get_param_indices(state, modes, opcode_ix):
    """
    Get intcode index for each paremeter, given
    an array of parameter nodes and the opcode index
    """
    indices = []
    for i, mode in enumerate(modes, 1):
        if mode == PARAM_MODE_POSITION:
            indices.append(state.intcode[opcode_ix+i])
        elif mode == PARAM_MODE_IMMEDIATE:
            indices.append(opcode_ix+i)
        elif mode == PARAM_MODE_RELATIVE:
            indices.append(state.relative_base + state.intcode[opcode_ix+i])
    return indices


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
            modes = modes_list(state.intcode[state.ic] / 100)[:num_args]
            params = get_param_indices(state, modes, state.ic)
            for param_ix in params:
                while len(state.intcode) <= param_ix:
                    state.intcode += [0]
            new_ic = func(state, *params)
            if Logger.initialized():
                Logger.log(f'{func.__name__}: {params} {state}')
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
            raise Exception(f'Illegal opcode {opcode} at index {state.ic}')
        OPCODES[opcode](state)
        if state.status in [STATE_TERMINATED, STATE_WAIT_FOR_INPUT]:
            return state.status
    raise Exception('Execution continued past end of memory')


max_x = None
max_y = None


def draw(painted_coordinates, score):
    """ Output the painted coordinates as ASCII to the terminal """
    sys.stdout.buffer.write(b'score: %d\n' % score)
    global max_x
    global max_y
    max_x = max([x for x, y in painted_coordinates.keys()]) \
        if max_x is None else max_x
    max_y = max([y for x, y in painted_coordinates.keys()]) \
        if max_y is None else max_y
    output = [bytearray(b'.'*(max_x+1) + b'\n') for y in range(max_y+1)]
    for (x, y), color in painted_coordinates.items():
        output[y][x] = TILE_ASCII_MAP[color]
    for line in output:
        sys.stdout.buffer.write(line)
    sys.stdout.flush()


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    with open('input', 'r') as input_data:
        intcode = [int(x) for x in input_data.readline().split(',')]
        intcode[0] = 2

    coord = namedtuple('coordinate', ['x', 'y'])
    score = 0
    painted_coords = {}
    state = ExecutionState(intcode, [])
    while state.status != STATE_TERMINATED:
        run_intcode(state)
        while len(state.outputs) >= 3:
            x, y, param = state.outputs[0:3]
            del state.outputs[0:3]
            if x == -1 and y == 0:
                score = param
                continue
            tile = param
            if tile == TILE_BALL:
                ball_coords = coord(x, y)
            elif tile == TILE_PADDLE:
                paddle_coords = coord(x, y)
            painted_coords[coord(x, y)] = tile
        if paddle_coords.x > ball_coords.x:
            state.inputs.append(-1)
        elif paddle_coords.x < ball_coords.x:
            state.inputs.append(1)
        else:
            state.inputs.append(0)
        draw(painted_coords, score)
    assert len(state.outputs) == 0
    print('final score', score)


if __name__ == '__main__':
    main(sys.argv)
