#!/usr/bin/env python

from collections import Counter, defaultdict
import fileinput


def main():
    format = SpaceImageFormat(25, 6)
    data = ''
    for line in fileinput.input():
        data += line.strip()
    format.read_image_data(data)
    print(format.calculate_checksum())


class SpaceImageFormat():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layers = []

    def read_image_data(self, data):
        index = 0

        while index < len(data):
            layer = {}
            for y in range(self.height):
                for x in range(self.width):
                    layer[x, y] = data[index]
                    index += 1

            self.layers.append(layer)

    def calculate_checksum(self):
        checksums = {idx: dict(Counter(layer.values()))
                     for idx, layer in enumerate(self.layers)}
        minimum = checksums[min(checksums, key=lambda key: checksums[key]['0'])]
        return minimum['1'] * minimum['2']

    def __repr__(self):
        repr = ''
        for index in range(len(self.layers)):
            repr += f'Layer {index}\n'
            for y in range(self.height):
                for x in range(self.width):
                    repr += self.layers[index][x, y]
                repr += '\n'
            repr += '\n'

        return repr


if __name__ == '__main__':
    main()
