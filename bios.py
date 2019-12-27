#!/usr/bin/env python

from collections import Counter, defaultdict
import fileinput


def main():
    format = SpaceImageFormat(25, 6)
    format.read_image_data(fileinput.input().readline().strip())
    image = format.full_image()
    print(format.format_image(image))


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

    def full_image(self):
        full_image = defaultdict(lambda: 2)

        for layer in self.layers:
            for coord, data in layer.items():
                if full_image[coord] == 2:
                    full_image[coord] = int(data)

        return full_image

    def format_image(self, image):
        image_string = ''
        for y in range(self.height):
            for x in range(self.width):
                if image[x, y] == 1:
                    image_string += 'X '
                else:
                    image_string += '  '
            image_string += '\n'
        return image_string

    def calculate_checksum(self):
        checksums = {idx: dict(Counter(layer.values()))
                     for idx, layer in enumerate(self.layers)}
        minimum = checksums[min(
            checksums, key=lambda key: checksums[key]['0'])]
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
