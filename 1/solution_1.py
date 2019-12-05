#!/usr/bin/env python

total_mass = 0
with open('input', 'r') as input:
    for line in input:
        total_mass += int(int(line) / 3) - 2

print(total_mass)
