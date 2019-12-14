#!/usr/bin/env python

import fileinput
import itertools
import re
from collections import defaultdict


def main():
    grid = Grid((1, 1))
    for line in fileinput.input():
        grid.place_wire(line.strip())
    print(grid.find_shortest_distance_to_intersection())
    print(grid.follow(1))
    print(grid.follow(2))


class Grid:
    def __init__(self, central_port):
        self._grid = defaultdict(lambda: defaultdict(
            lambda: Port(is_central=False)))
        self._grid[central_port[0]][central_port[1]] = Port(is_central=True)
        self._central_port = central_port
        self._current_loc = central_port
        self._current_wire = 0

    def find_intersections(self):
        x = itertools.chain.from_iterable(
            filter(lambda x: len(x) > 0,
                   [[(x, y)
                     for y in self._grid[x].keys()
                     if self._grid[x][y].is_intersection()]
                    for x in self._grid.keys()]))
        return x

    def find_shortest_distance_to_intersection(self):
        return min([self.calculate_taxicab_distance_from_central_port(x) for x in self.find_intersections()])

    def calculate_taxicab_distance_from_central_port(self, point):
        return abs(self._central_port[0] - point[0]) + abs(self._central_port[1] - point[1])

    def follow(self, wire, length=0, prev_loc=None, curr_loc=None, visited=set(), intersections={}):
        if curr_loc is None:
            curr_loc = self._central_port

        # Possible next moves are found by looking at all non-diagonal next points
        possible_next_moves = {(curr_loc[0], curr_loc[1] - 1),
                               (curr_loc[0], curr_loc[1] + 1),
                               (curr_loc[0] - 1, curr_loc[1]),
                               (curr_loc[0] + 1, curr_loc[1])}

        # Avoid going back the spot we just came from
        if prev_loc is not None:
            possible_next_moves.remove(prev_loc)

        # If we're at a point that intersects with ourselves, we need to make sure
        # not to go back to any previously visited points, otherwise we'll go in circles
        if self._grid[curr_loc[0]][curr_loc[1]].is_self_intersection(wire):
            possible_next_moves -= visited

        for (x, y) in possible_next_moves:
            if self._grid[x][y].has_wire(wire):
                # Keep track of visited nodes, increase the length the first time we reach a node
                if (x, y) not in visited:
                    length = length + 1
                    if self._grid[x][y].is_intersection():
                        intersections[x, y] = length
                    visited.add((x, y))
                length, _ = self.follow(wire, length=length,
                                        prev_loc=curr_loc, curr_loc=(x, y), visited=visited, intersections=intersections)

        return length, intersections

    def place_wire(self, wire_spec):
        self._current_loc = self._central_port
        dispatch_table = {
            'U': lambda spots: self._go_up(spots),
            'D': lambda spots: self._go_down(spots),
            'L': lambda spots: self._go_left(spots),
            'R': lambda spots: self._go_right(spots)
        }

        self._current_wire += 1
        instructions = wire_spec.strip().split(',')
        for instruction in instructions:
            dir = instruction[0]
            spots = int(instruction[1:])
            dispatch_table[dir](spots)

    def _place_node(self, point, direction):
        self._grid[point[0]][point[1]].place(self._current_wire, direction)

    def _fix_grids(self):
        max_width = 0
        min_width = 0
        min_height = min([int(x) for x in self._grid.keys()])
        max_height = max([int(x) for x in self._grid.keys()])

        for x in range(min_height, max_height + 1):
            if len(self._grid[x].keys()):
                curr_max = max(self._grid[x].keys())
                curr_min = min(self._grid[x].keys())
                if curr_max > max_width:
                    max_width = curr_max
                if curr_min < min_width:
                    min_width = curr_min

        for x in range(min_height, max_height + 1):
            for y in range(min_width, max_width + 1):
                self._grid[x][y]

    def _go_left(self, spots):
        for y in reversed(range(self._current_loc[1] - spots, self._current_loc[1] + 1)):
            self._place_node((self._current_loc[0], y), 'H')
        self._current_loc = (
            self._current_loc[0], self._current_loc[1] - spots)

    def _go_right(self, spots):
        for y in range(self._current_loc[1], self._current_loc[1] + spots + 1):
            self._place_node((self._current_loc[0], y), 'H')
        self._current_loc = (
            self._current_loc[0], self._current_loc[1] + spots)

    def _go_up(self, spots):
        for x in range(self._current_loc[0], self._current_loc[0] + spots + 1):
            self._place_node((x, self._current_loc[1]), 'V')
        self._current_loc = (
            self._current_loc[0] + spots, self._current_loc[1])

    def _go_down(self, spots):
        for x in reversed(range(self._current_loc[0] - spots, self._current_loc[0] + 1)):
            self._place_node((x, self._current_loc[1]), 'V')
        self._current_loc = (
            self._current_loc[0] - spots, self._current_loc[1])

    def __repr__(self):
        self._fix_grids()
        repr = ''

        for x in reversed(sorted(self._grid.keys())):
            for y in sorted(self._grid[x].keys()):
                repr += ' ' + str(self._grid[x][y])
            repr += '\n'

        return repr


class Port:
    def __init__(self, is_central):
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
