#!/usr/bin/env python

import fileinput
from collections import defaultdict


def main():
    lines = [line.strip() for line in fileinput.input()]
    grid = Grid((1, 1), lines)
    # print(grid)
    # print(grid.find_shortest_taxicab_distance_to_intersection())
    print(grid.find_shortest_path_distance_to_intersection())


class Grid:
    def __init__(self, central_port, wire_specs):
        self._grid = defaultdict(lambda: Port())
        self._grid[central_port] = Port(is_central=True)
        self._central_port = central_port
        self._current_loc = central_port
        self._current_wire = 0
        self._wires = set()
        self._intersections = defaultdict(dict)
        self._current_length = 0
        self._instructions = None
        self._wire_specs = wire_specs
        self.place_wires()

    def find_intersections(self):
        return [point for point in self._grid if self._grid[point].is_intersection()]

    def find_shortest_taxicab_distance_to_intersection(self):
        return min([self.calculate_taxicab_distance_from_central_port(x) for x in self.find_intersections()])

    def calculate_taxicab_distance_from_central_port(self, point):
        return abs(self._central_port[0] - point[0]) + abs(self._central_port[1] - point[1])

    def find_shortest_path_distance_to_intersection(self):
        self.place_wires(follow_only=True)
        lengths = [[self._intersections[key][point] for point in sorted(self._intersections[key].keys())]
                   for key in self._intersections]
        return min([sum(l) for l in zip(*lengths)])

    def place_wires(self, follow_only=False):
        dispatch_table = {
            'U': self._go_up,
            'D': self._go_down,
            'L': self._go_left,
            'R': self._go_right
        }

        self._current_wire = 0

        for wire_spec in self._wire_specs:
            self._current_loc = self._central_port
            self._current_wire += 1
            self._current_length = 0
            if not follow_only:
                self._wires.add(self._current_wire)
            instructions = wire_spec.split(',')
            for instruction in instructions:
                dir = instruction[0]
                spots = int(instruction[1:])
                dispatch_table[dir](spots, follow_only)

    def _place_node(self, point, direction):
        self._grid[point].place(self._current_wire, direction)

    def _fix_grid(self):
        xs = [x for (x, _) in self._grid]
        ys = [y for (_, y) in self._grid]
        for x in range(min(xs), max(xs) + 1):
            for y in range(min(ys), max(ys) + 1):
                self._grid[x, y]

    def _go_left(self, spots, follow_only=False):
        self._go_horizontal(-spots, follow_only)

    def _go_right(self, spots, follow_only=False):
        self._go_horizontal(spots, follow_only)

    def _go_up(self, spots, follow_only=False):
        self._go_vertical(spots, follow_only)

    def _go_down(self, spots, follow_only=False):
        self._go_vertical(-spots, follow_only)

    def _go_horizontal(self, spots, follow_only=False):
        direction = int(spots / abs(spots))
        for _ in range(0, abs(spots)):
            if not follow_only:
                self._place_node(self._current_loc, 'H')
            self._current_loc = (
                self._current_loc[0] + direction, self._current_loc[1])
            self._current_length += 1
            if self._grid[self._current_loc].is_intersection():
                self._intersections[self._current_wire][self._current_loc] = self._current_length

    def _go_vertical(self, spots, follow_only=False):
        direction = int(spots / abs(spots))
        for _ in range(0, abs(spots)):
            if not follow_only:
                self._place_node(self._current_loc, 'V')
            self._current_loc = (
                self._current_loc[0], self._current_loc[1] + direction)
            self._current_length += 1
            if self._grid[self._current_loc].is_intersection():
                self._intersections[self._current_wire][self._current_loc] = self._current_length

    def __repr__(self):
        self._fix_grid()
        repr = ''

        for y in reversed(sorted(list(set([y for _, y in self._grid])))):
            for x in sorted(list(set([x for x, _ in self._grid]))):
                repr += ' ' + str(self._grid[x, y])
            repr += '\n'

        return repr


class Port:
    def __init__(self, is_central=False):
        self._is_central = is_central
        self._wires = set()
        self._directions = set()
        self._count = defaultdict(lambda: 0)

    def is_intersection(self):
        return not self._is_central and len(self._wires) > 1

    def is_self_intersection(self, wire):
        return self._count[wire] > 1

    def place(self, wire, direction):
        self._wires.add(wire)
        self._count[wire] += 1
        self._directions.update([direction])

    def has_wire(self, wire):
        return wire in self._wires

    def __repr__(self):
        if self._is_central:
            return 'o'
        elif self.is_intersection():
            return 'x'
        elif len(self._directions) > 0:
            if 'H' in self._directions and 'V' in self._directions:
                return '+'
            elif 'H' in self._directions:
                return '-'
            elif 'V' in self._directions:
                return '|'
        else:
            return '.'


if __name__ == '__main__':
    main()
