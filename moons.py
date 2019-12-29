#!/usr/bin/env python

from itertools import product
import fileinput
import re
import os

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG']


def main():
    system = MoonSystem()

    pattern = re.compile(r'<x=(-?\d+), y=(-?\d+), z=(-?\d+)')
    for line in fileinput.input():
        match = pattern.search(line)
        x, y, z = match.group(1, 2, 3)
        moon = Moon(int(x), int(y), int(z))
        system.add_moon(moon)
    
    system.simulate_motion(1000)
    print(system.kinetic_energy())


class Moon():
    def __init__(self, x, y, z):
        self.pos_x = x
        self.pos_y = y
        self.pos_z = z
        self.vel_x = 0
        self.vel_y = 0
        self.vel_z = 0

    def apply_gravity(self, moon):
        if self.pos_x != moon.pos_x:
            self.vel_x += 1 if self.pos_x < moon.pos_x else -1
        if self.pos_y != moon.pos_y:
            self.vel_y += 1 if self.pos_y < moon.pos_y else -1
        if self.pos_z != moon.pos_z:
            self.vel_z += 1 if self.pos_z < moon.pos_z else -1

    def apply_velocity(self):
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        self.pos_z += self.vel_z

    def kinetic_energy(self):
        return (abs(self.pos_x) + abs(self.pos_y) + abs(self.pos_z)) * \
            (abs(self.vel_x) + abs(self.vel_y) + abs(self.vel_z))

    def __repr__(self):
        return f'pos=<x={self.pos_x}, y={self.pos_y}, z={self.pos_z}>, ' \
            f'vel=<x={self.vel_x}, y={self.vel_y}, z={self.vel_z}>'


class MoonSystem():
    def __init__(self):
        self.moons = []

    def add_moon(self, moon):
        self.moons.append(moon)

    def apply_gravity(self):
        for moon_a in self.moons:
            for moon_b in (moon for moon in self.moons if moon != moon_a):
                moon_a.apply_gravity(moon_b)

    def apply_velocity(self):
        for moon in self.moons:
            moon.apply_velocity()

    def simulate_motion(self, steps):
        if DEBUG:
            print('after 0 steps:')
            print(self)

        for step in range(1, steps + 1):
            self.apply_gravity()
            self.apply_velocity()

            if DEBUG:
                print(f'after {step} steps')
                print(self)

    def kinetic_energy(self):
        return sum(moon.kinetic_energy() for moon in self.moons)

    def __repr__(self):
        repr = ''
        for moon in self.moons:
            repr += str(moon) + '\n'
        return repr


if __name__ == '__main__':
    main()
