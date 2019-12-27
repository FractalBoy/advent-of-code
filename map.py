#!/usr/bin/env python

from math import sqrt, atan2, cos, sin, pi
from itertools import groupby
import fileinput


def main():
    map = Map(line.strip() for line in fileinput.input())
    print(map.find_best_monitoring_location())
    print(map.vaporize_asteroids(200))


class Map:
    def __init__(self, lines):
        self.map = {(x, y): char for y, line in enumerate(lines)
                    for x, char in enumerate(line)}

    def find_best_monitoring_location(self):
        best_monitoring_location = max({
            origin: len(
                set(
                    Point.from_cartesian(
                        asteroid[0] - origin[0], asteroid[1] - origin[1]
                    ).theta
                    for asteroid in self.asteroids())
            )
            for origin in self.asteroids()
        }.items(), key=lambda item: item[1])

        self.best_monitoring_location = best_monitoring_location[0]
        return best_monitoring_location

    def vaporize_asteroids(self, vaporized_count):
        if self.best_monitoring_location is None:
            self.find_best_monitoring_location()
        
        # Get data about all points using the best monitoring location
        # as the origin of the coordinate system.
        points = {
            asteroid: Point.from_cartesian(
                asteroid[0] - self.best_monitoring_location[0],
                asteroid[1] - self.best_monitoring_location[1]
            )
            for asteroid in self.asteroids()
            # Ignore the monitoring station
            if asteroid != self.best_monitoring_location
        }

        number = 0

        while len(points):
            def quadrant_lambda(item): return item[1].quadrant()
            def theta_lambda(item): return item[1].theta
            def r_lambda(item): return item[1].r

            # Create dictionary of form:
            # {
            #   quadrant: {
            #       angle: [list of points on that angle, sorted by distance from origin]
            #   }
            # }
            quadrants = {
                quadrant: {
                    angle:
                    sorted((asteroid for asteroid in angle_group),
                           key=r_lambda)
                    for angle, angle_group in
                    groupby(sorted(quadrant_group, key=theta_lambda),
                            key=theta_lambda)
                }
                for quadrant, quadrant_group in
                groupby(sorted(points.items(), key=quadrant_lambda),
                        key=quadrant_lambda)
            }

            # Clockwise starting at 12 o'clock means going through quadrants in order: 1, 4, 3, 2.
            # Within each quadrant, look at angles in decreasing order
            for quadrant in 1, 4, 3, 2:
                if quadrant not in quadrants:
                    continue
                quadrant_group = quadrants[quadrant]
                # Sort by angle (the key of the quadrant_group dictionary)
                for _, asteroids in sorted(quadrant_group.items(), key=lambda item: item[0], reverse=True):
                    closest_asteroid, _ = asteroids[0]
                    del points[closest_asteroid]
                    number += 1
                    if number == vaporized_count:
                        return closest_asteroid

        return None

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

    def quadrant(self):
        if self.theta >= 0 and self.theta <= pi/2:
            return 1
        if self.theta > pi/2 and self.theta <= pi:
            return 2
        if self.theta >= -pi and self.theta < -pi/2:
            return 3
        if self.theta >= -pi/2 and self.theta < 0:
            return 4

    def _calculate_cartesian(self):
        self.x = self.r * cos(self.theta)
        self.y = self.r * sin(self.theta)

    def _calculate_polar(self):
        self.r = sqrt(self.x * self.x + self.y * self.y)
        # Negative atan2 because the lower the y coordinate
        # the higher the coordinate in actual space
        self.theta = -atan2(self.y, self.x)
        self.theta = 0 if self.theta == -0 else self.theta


if __name__ == '__main__':
    main()
