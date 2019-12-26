#!/usr/bin/env python

from collections import defaultdict
from math import sqrt, atan2, cos, sin
import fileinput


def main():
    lines = []
    for line in fileinput.input():
        lines.append(line.strip())

    map = Map()
    map.read_map('\n'.join(lines))
    print(map.find_best_monitoring_location())


class Map:
    def __init__(self):
        self.map = {}

    def read_map(self, text):
        y = 0

        for line in text.split('\n'):
            x = 0
            line = line.strip()
            for char in line:
                self.map[x, y] = char
                x += 1

            y += 1

    def find_best_monitoring_location(self):
        detections = defaultdict(lambda: 0)

        for origin in self.asteroids():
            angles = set()
            for ast in self.asteroids():
                if origin == ast:
                    continue
                point = Point.from_cartesian(ast[0] - origin[0], ast[1] - origin[1])
                if point.theta in angles:
                    continue
                angles.add(point.theta)
                detections[origin] += 1

        return max(detections.items(), key=lambda item: item[1])

    def asteroids(self):
        return (coord for coord, value in self.map.items() if value == '#')

    def __repr__(self):
        xs = [coord[0] for coord in self.map]
        ys = [coord[1] for coord in self.map]
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        repr = ''

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                repr += self.map[x, y]
            repr += '\n'

        return repr


class Point():
    @classmethod
    def from_cartesian(cls, x, y):
        point = cls()
        point.x = x
        point.y = y
        point._calculate_polar()
        return point

    @classmethod
    def from_polar(cls, r, theta):
        point = cls()
        point.r = r
        point.theta = theta
        point._calculate_cartesian()
        return point

    def _calculate_cartesian(self):
        self.x = self.r * cos(self.theta)
        self.y = self.r * sin(self.theta)

    def _calculate_polar(self):
        self.r = sqrt(self.x * self.x + self.y * self.y)
        self.theta = atan2(self.y, self.x)


if __name__ == '__main__':
    main()
