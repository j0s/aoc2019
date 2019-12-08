#!/usr/bin/env python

import sys

COLOR_BLACK = 0
COLOR_WHITE = 1
COLOR_TRANSPARENT = 2


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


def get_pixel_color(layers, x, y):
    colors = [layer[y][x] for layer in layers]
    for color in colors:
        if int(color) in [COLOR_BLACK, COLOR_WHITE]:
            return color
    return color


def combine_layers(layers, width, height):
    """
    >>> img = make_image('0222112222120000', 2, 2)
    >>> combine_layers(img, 2, 2)
    ['01', '10']
    """
    return [''.join([get_pixel_color(layers, x, y)
                     for x in range(width)]) for y in range(height)]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        import doctest
        doctest.testmod()
        sys.exit(0)
    doctest_input = None

    with open('input', 'r') as input_data:
        sif_input = input_data.readline()

    image = make_image(sif_input, 25, 6)
    for row in combine_layers(image, 25, 6):
        print(row)
