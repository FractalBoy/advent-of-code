#!/usr/bin/env python

from math import sqrt, atan2, cos, sin
import fileinput


def main():
    map = Map(list(fileinput.input()))
    print(map.find_best_monitoring_location())


class Map:
    def __init__(self, lines):
        self.map = {(x, y): char for y, line in enumerate(lines)
                    for x, char in enumerate(line)}

    def find_best_monitoring_location(self):
        return max({
            origin: len(
                set(
                    Point.from_cartesian(
                        asteroid[0] - origin[0], asteroid[1] - origin[1]
                    ).theta
                    for asteroid in self.asteroids())
            )
            for origin in self.asteroids()
        }.items(), key=lambda item: item[1])

    def asteroids(self):
        return (coord for coord, value in self.map.items() if value == '#')

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
