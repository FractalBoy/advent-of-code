#!/usr/bin/env python

from itertools import product
import fileinput
import re
import operator
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
        self.set_position_vector((x, y, z))
        self.set_velocity_vector((0, 0, 0))

    def apply_gravity(self, moon):
        def sign(x):
            if x < 0:
                return -1
            if x == 0:
                return 0
            if x > 0:
                return 1

        self.set_velocity_vector(
            map(operator.add, self.get_velocity_vector(),
                map(sign, self - moon)))

    def apply_velocity(self):
        self.set_position_vector(
            map(operator.add, self, self.get_velocity_vector()))

    def kinetic_energy(self):
        return sum(map(abs, self.get_position_vector()))  \
            * sum(map(abs, self.get_velocity_vector()))

    def __repr__(self):
        return f'pos=<x={self.pos_x}, y={self.pos_y}, z={self.pos_z}>, ' \
            f'vel=<x={self.vel_x}, y={self.vel_y}, z={self.vel_z}>'

    def get_velocity_vector(self):
        return (self.vel_x, self.vel_y, self.vel_z)

    def set_velocity_vector(self, vector):
        self.vel_x, self.vel_y, self.vel_z = vector

    def set_position_vector(self, vector):
        self.pos_x, self.pos_y, self.pos_z = vector
    
    def get_position_vector(self):
        return (self.pos_x, self.pos_y, self.pos_z)

    def __sub__(self, value):
        return map(operator.sub, self, value)

    def __getitem__(self, index):
        return self.get_position_vector()[index]

    def __len__(self):
        return 3


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
