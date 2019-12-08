#!/usr/bin/env python

import sys
import math
import functools
import itertools

ParamModePosition = 0
ParamModeImmediate = 1


def get_param_indices(intcode, modes, ix):
    return [ix+i if mode == ParamModeImmediate else intcode[ix+i]
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
    return [int(modes / math.pow(10, x)) % 10 for x in range(3)]


class ExecutionState:
    def __init__(self, intcode, inputs=[]):
        self.intcode = intcode
        self.inputs = inputs
        self.outputs = []
        self.ic = 0


def instruction(num_args):
    def decorator_instruction(func):
        @functools.wraps(func)
        def execute_instruction(state):
            modes = modes_list(state.intcode[state.ic] / 100)[:num_args]
            retval = func(
                state, *get_param_indices(state.intcode, modes, state.ic))
            state.ic = (state.ic + num_args + 1) if retval is None else retval
        return execute_instruction
    return decorator_instruction


@instruction(num_args=3)
def add(state, lhs_ix, rhs_ix, result_ix):
    state.intcode[result_ix] = state.intcode[lhs_ix] + state.intcode[rhs_ix]


@instruction(num_args=3)
def multiply(state, lhs_ix, rhs_ix, result_ix):
    state.intcode[result_ix] = state.intcode[lhs_ix] * state.intcode[rhs_ix]


@instruction(num_args=1)
def store(state, store_ix):
    state.intcode[store_ix] = state.inputs.pop(0)


@instruction(num_args=1)
def output(state, output_ix):
    state.outputs.append(state.intcode[output_ix])


@instruction(num_args=2)
def jump_if_true(state, cond_ix, jump_ix):
    if state.intcode[cond_ix]:
        return state.intcode[jump_ix]


@instruction(num_args=2)
def jump_if_false(state, cond_ix, jump_ix):
    if not state.intcode[cond_ix]:
        return state.intcode[jump_ix]


@instruction(num_args=3)
def less_than(state, lhs_ix, rhs_ix, result_ix):
    state.intcode[result_ix] = int(
        state.intcode[lhs_ix] < state.intcode[rhs_ix])


@instruction(num_args=3)
def equals(state, lhs_ix, rhs_ix, result_ix):
    state.intcode[result_ix] = int(
        state.intcode[lhs_ix] == state.intcode[rhs_ix])


@instruction(num_args=0)
def quit(state):
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
    """
    while state.ic < len(state.intcode):
        opcode = state.intcode[state.ic] % 100
        if opcode not in opcodes:
            raise Exception(f'Illegal opcode {opcode} at index {state.ic}')
        opcodes[opcode](state)
        if state.ic == 0:
            return


def chain_executions(intcode, phase_sequence):
    """
    >>> chain_executions([3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0],
    ...                  [4,3,2,1,0])
    43210
    >>> chain_executions([3,23,3,24,1002,24,10,24,1002,23,-1,23,
    ...                   101,5,23,23,1,24,23,23,4,23,99,0,0],
    ...                  [0,1,2,3,4])
    54321
    >>> chain_executions([3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,
    ...                   1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0],
    ...                  [1,0,4,3,2])
    65210
    """

    last_output = None
    for phase in phase_sequence:
        state = ExecutionState(
            intcode.copy(), [phase, 0 if last_output is None else last_output])
        run_intcode(state)
        last_output = state.outputs[0]
    return state.outputs[0]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)
    doctest_input = None

    with open('input', 'r') as input_data:
        intcode = [int(x) for x in input_data.readline().split(',')]

    max_output = 0
    for phases in itertools.permutations([0, 1, 2, 3, 4]):
        output = chain_executions(intcode, phases)
        if output > max_output:
            max_output = output
    print(f'max_output: {max_output}')
