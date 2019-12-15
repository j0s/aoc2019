#!/usr/bin/env python
""" Intcode computer """

import sys
import doctest
import math


class Logger:
    """ Logger class """
    logfile = None

    @classmethod
    def init(cls, filename):
        """ Initialize logger to write to given file """
        cls.logfile = open(filename, 'w')

    @classmethod
    def initialized(cls):
        """ Return True if Logger.init() has been called, otherwise False """
        return cls.logfile is not None

    @classmethod
    def log(cls, msg):
        """ Write message to log """
        if cls.logfile is not None:
            cls.logfile.write(msg+'\n')


def parse_reactions(reactions_string):
    reactions = {}
    for reaction in reactions_string.split('\n'):
        if reaction.strip() == '':
            continue
        inputs, output = reaction.split(' => ')
        output_amount, output_chemical = output.split()
        reactions[output_chemical] = {
            'amount': int(output_amount), 'inputs': {}}
        for inp in inputs.split(','):
            input_amount, input_chemical = inp.split()
            reactions[output_chemical]['inputs'][input_chemical] = int(
                input_amount)
    return reactions


def get_ore_needed(reactions, output_chemical, output_amount=1, leftovers={}):
    '''
    >>> r = parse_reactions("""10 ORE => 10 A
    ... 1 ORE => 1 B
    ... 7 A, 1 B => 1 C
    ... 7 A, 1 C => 1 D
    ... 7 A, 1 D => 1 E
    ... 7 A, 1 E => 1 FUEL""")
    >>> get_ore_needed(r, 'FUEL')[0]
    31
    >>> r = parse_reactions("""9 ORE => 2 A
    ... 8 ORE => 3 B
    ... 7 ORE => 5 C
    ... 3 A, 4 B => 1 AB
    ... 5 B, 7 C => 1 BC
    ... 4 C, 1 A => 1 CA
    ... 2 AB, 3 BC, 4 CA => 1 FUEL""")
    >>> get_ore_needed(r, 'FUEL')[0]
    165
    >>> r = parse_reactions("""157 ORE => 5 NZVS
    ... 165 ORE => 6 DCFZ
    ... 44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
    ... 12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
    ... 179 ORE => 7 PSHF
    ... 177 ORE => 5 HKGWZ
    ... 7 DCFZ, 7 PSHF => 2 XJWVT
    ... 165 ORE => 2 GPVTF
    ... 3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT""")
    >>> get_ore_needed(r, 'FUEL')[0]
    13312
    >>> r = parse_reactions("""2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
    ... 17 NVRVD, 3 JNWZP => 8 VPVL
    ... 53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
    ... 22 VJHF, 37 MNCFX => 5 FWMGM
    ... 139 ORE => 4 NVRVD
    ... 144 ORE => 7 JNWZP
    ... 5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
    ... 5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
    ... 145 ORE => 6 MNCFX
    ... 1 NVRVD => 8 CXFTF
    ... 1 VJHF, 6 MNCFX => 4 RFSQX
    ... 176 ORE => 6 VJHF""")
    >>> get_ore_needed(r, 'FUEL')[0]
    180697
    >>> r = parse_reactions("""171 ORE => 8 CNZTR
    ... 7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
    ... 114 ORE => 4 BHXH
    ... 14 VRPVC => 6 BMBT
    ... 6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
    ... 6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
    ... 15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
    ... 13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
    ... 5 BMBT => 4 WPTQ
    ... 189 ORE => 9 KTJDG
    ... 1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
    ... 12 VRPVC, 27 CNZTR => 2 XDBXC
    ... 15 KTJDG, 12 BHXH => 5 XCVML
    ... 3 BHXH, 2 VRPVC => 7 MZWV
    ... 121 ORE => 7 VRPVC
    ... 7 XCVML => 6 RJRHP
    ... 5 BHXH, 4 VRPVC => 5 LTCX""")
    >>> get_ore_needed(r, 'FUEL')[0]
    2210736
    '''
    if output_chemical == 'ORE' or output_amount == 0:
        return output_amount, leftovers

    reactions_needed = math.ceil(
        output_amount / reactions[output_chemical]['amount'])
    output_leftover = reactions_needed * \
        reactions[output_chemical]['amount'] - output_amount
    ore_needed = 0
    for inp, inp_need in reactions[output_chemical]['inputs'].items():
        inp_need *= reactions_needed
        inp_leftover = leftovers.setdefault(inp, 0)
        if inp_leftover > inp_need:
            leftovers[inp] -= inp_need
            inp_need = 0
        else:
            inp_need -= leftovers[inp]
            leftovers[inp] = 0
        tmp_ore_needed, leftovers = get_ore_needed(
            reactions, inp, inp_need, leftovers)
        ore_needed += tmp_ore_needed
    Logger.log(
        f'amount ore needed for {output_amount} {output_chemical}: '
        f'{ore_needed} (leftovers: {leftovers})')
    leftovers[output_chemical] = output_leftover + \
        leftovers.get(output_chemical, 0)
    return ore_needed, leftovers


def main(argv):
    """ Main method """
    if '--debug' in argv:
        Logger.init('output.log')
    if '--test' in argv:
        doctest.testmod()
        sys.exit(0)

    with open('input', 'r') as input_data:
        reactions = ''.join(input_data.readlines())

    reactions = parse_reactions(reactions)

    ore_need = get_ore_needed(reactions, 'FUEL')[0]
    print(ore_need)


if __name__ == '__main__':
    main(sys.argv)
