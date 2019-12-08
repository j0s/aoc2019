#!/usr/bin/env python

import sys


def make_image(sif_input, width, height):
    """
    >>> make_image('123456789012', 3, 2)
    [['123', '456'], ['789', '012']]
    """
    layer_size = width*height
    row_size = width
    layers = int(len(sif_input) / layer_size)

    output = []
    for i in range(layers):
        layer_input = sif_input[i*layer_size:(i+1)*layer_size]
        layer = []
        for j in range(height):
            row_input = layer_input[j*row_size:(j+1)*row_size]
            layer.append(row_input)
        output.append(layer)
    return output


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)
    doctest_input = None

    with open('input', 'r') as input_data:
        sif_input = input_data.readline()

    image = make_image(sif_input, 25, 6)
    min_zeroes = None
    for layer in image:
        layer_zeroes = sum([row.count('0') for row in layer])
        if min_zeroes is None or layer_zeroes < min_zeroes:
            min_zeroes = layer_zeroes
            min_zeroes_layer = layer

    ones = sum([row.count('1') for row in min_zeroes_layer])
    twos = sum([row.count('2') for row in min_zeroes_layer])
    print(ones*twos)
