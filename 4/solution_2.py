#!/usr/bin/env python

import sys


def check_password(password):
    """
    >>> check_password(112233)
    True
    >>> check_password(123444)
    False
    >>> check_password(111122)
    True
    """
    password_str = str(password)
    adjacent_digit = None
    last_digit = password_str[0]
    for digit in password_str[1:]:
        if digit == last_digit:
            if adjacent_digit != digit:
                adjacent = True
                adjacent_digit = digit
            adjacent = not adjacent
        if digit < last_digit:
            return False
        last_digit = digit
    return adjacent


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)

    num_passwords = 0
    for password in range(240920, 789857+1):
        if check_password(password):
            num_passwords += 1
    print(num_passwords)
