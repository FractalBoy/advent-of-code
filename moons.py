#!/usr/bin/env python

from itertools import product
from math import gcd
import fileinput
import re
import operator
import os

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG']


def main():
    system = MoonSystem()

    pattern = re.compile(r'<x=(-?\d+), y=(-?\d+), z=(-?\d+)>')
    for line in fileinput.input():
        match = pattern.search(line)
        x, y, z = match.group(1, 2, 3)
        moon = Moon(int(x), int(y), int(z))
        system.add_moon(moon)

    for _ in range(1000):
        system.simulate_one_step()

    print(system)
    print(system.kinetic_energy())

    for value in system.simulate_until_repeat():
        print(value)


class Moon():
    def __init__(self, x, y, z):
        self.set_position_vector((x, y, z))
        self.set_velocity_vector((0, 0, 0))

    def apply_gravity(self, moon):
        self.set_velocity_vector(
            map(operator.add, self.get_velocity_vector(),
                map(sign, moon - self)))

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
        self.x_initial_state = None
        self.y_initial_state = None
        self.z_initial_state = None

    def add_moon(self, moon):
        self.moons.append(moon)

    def apply_gravity(self):
        for moon_a in self.moons:
            for moon_b in self.moons:
                moon_a.apply_gravity(moon_b)

    def apply_velocity(self):
        for moon in self.moons:
            moon.apply_velocity()

    def get_states(self):
        pos_vel = [moon.get_position_vector() + moon.get_velocity_vector()
                   for moon in self.moons]

        return (tuple((pos_x, vel_x) for pos_x, _, _, vel_x, _, _ in pos_vel),
        tuple((pos_y, vel_y) for _, pos_y, _, _, vel_y, _ in pos_vel),
        tuple((pos_z, vel_z) for _, _, pos_z, _, _, vel_z in pos_vel))

    def determine_initial_states(self):
        (self.x_initial_state,
        self.y_initial_state,
        self.z_initial_state) = self.get_states()
    
    def check_for_cycle(self):
        (x_state, y_state, z_state) = self.get_states()
        found_x, found_y, found_z = False, False, False

        if x_state == self.x_initial_state:
            found_x = True
        if y_state == self.y_initial_state:
            found_y = True
        if z_state == self.z_initial_state:
            found_z = True

        return found_x, found_y, found_z

    def simulate_one_step(self):
        self.apply_gravity()
        self.apply_velocity()
        return self.check_for_cycle()

    def simulate_until_repeat(self):
        self.determine_initial_states()

        count = 0
        count_x, count_y, count_z = 0, 0, 0

        while count_x == 0 or count_y == 0 or count_z == 0:
            count += 1
            found_x, found_y, found_z = self.simulate_one_step()
            if found_x and count_x == 0:
                count_x = count
                yield count_x, count_y, count_z
            if found_y and count_y == 0:
                count_y = count
                yield count_x, count_y, count_z
            if found_z and count_z == 0:
                count_z = count
                yield count_x, count_y, count_z

        yield lcm(count_x, count_y, count_z)

    def kinetic_energy(self):
        return sum(moon.kinetic_energy() for moon in self.moons)

    def __repr__(self):
        repr = ''
        for moon in self.moons:
            repr += str(moon) + '\n'
        return repr


def lcm(*iterable):
    answer = iterable[0]

    for value in iterable[1:]:
        answer = value * answer // gcd(value, answer)

    return answer

def sign(x):
    if x < 0:
        return -1
    if x == 0:
        return 0
    if x > 0:
        return 1




if __name__ == '__main__':
    main()
