#!/usr/bin/env python

import fileinput
import re
from collections import defaultdict


def main():
    grid = Grid([1, 1])
    for line in fileinput.input():
        grid.place_wire(line.strip())
    #print(grid)
    print(list(grid.find_intersections()))
    print([Grid.calculate_taxicab_distance(grid._central_port, point) for point in grid.find_intersections()])
    print(grid.find_shortest_distance_to_intersection())


class Grid:
    def __init__(self, central_port):
        self._grid = defaultdict(lambda: defaultdict(lambda: '.'))
        self._pretty_grid = defaultdict(lambda: defaultdict(lambda: '.'))
        self._central_port = central_port
        self._place_char(central_port, 'o', '')
        self._current_dir = None
        self._current_loc = central_port.copy()
        self._current_wire = 0

    def find_intersections(self):
        for x in self._grid.keys():
            for y in self._grid[x].keys():
                if self._grid[x][y] == 'x':
                    yield [x, y]

    def find_shortest_distance_to_intersection(self):
        distances = []
        for intersection in self.find_intersections():
            distance = Grid.calculate_taxicab_distance(
                self._central_port, intersection)
            distances.append(distance)
        return min(distances)

    @staticmethod
    def calculate_taxicab_distance(point1, point2):
        return abs(point2[0] - point1[0]) + abs(point2[1] - point1[1])

    def place_wire(self, wire_spec):
        self._current_loc = self._central_port.copy()
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

    def _place_char(self, point, char, dir):
        if self._grid[point[0]][point[1]] != 'o':
            self._grid[point[0]][point[1]] = char
        if char != 'o' and char != 'x':
            if dir == 'V':
                char = '|'
            elif dir == 'H':
                char = '-'
            elif dir == '+':
                char = '+'
        if self._pretty_grid[point[0]][point[1]] != 'o':
            self._pretty_grid[point[0]][point[1]] = char

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
                self._pretty_grid[x][y]

    def _go_left(self, spots):
        if self._current_dir == 'U' or self._current_dir == 'D':
            if Grid._is_safe(self._grid[self._current_loc[0]][self._current_loc[1]], str(self._current_wire)):
                self._place_char([self._current_loc[0], self._current_loc[1]], str(
                self._current_wire), '+')
            else:
                self._place_char([self._current_loc[0], self._current_loc[1]], 'x', '+')

        col = self._grid[self._current_loc[0]]
        for y in reversed(range(self._current_loc[1] - spots, self._current_loc[1])):
            char = self._current_wire
            if not Grid._is_safe(col[y], char):
                char = 'x'
            self._place_char([self._current_loc[0], y], char, 'H')
        self._current_loc[1] = self._current_loc[1] - spots
        self._current_dir = 'L'

    def _go_right(self, spots):
        if self._current_dir == 'U' or self._current_dir == 'D':
            if Grid._is_safe(self._grid[self._current_loc[0]][self._current_loc[1]], str(self._current_wire)):
                self._place_char([self._current_loc[0], self._current_loc[1]], str(
                self._current_wire), '+')
            else:
                self._place_char([self._current_loc[0], self._current_loc[1]], 'x', '+')

        col = self._grid[self._current_loc[0]]
        for y in range(self._current_loc[1] + 1, self._current_loc[1] + spots + 1):
            char = str(self._current_wire)
            if not Grid._is_safe(col[y], char):
                char = 'x'
            self._place_char([self._current_loc[0], y], char, 'H')
        self._current_loc[1] = self._current_loc[1] + spots
        self._current_dir = 'R'

    def _go_up(self, spots):
        if self._current_dir == 'R' or self._current_dir == 'L':
            if Grid._is_safe(self._grid[self._current_loc[0]][self._current_loc[1]], str(self._current_wire)):
                self._place_char([self._current_loc[0], self._current_loc[1]], str(
                self._current_wire), '+')
            else:
                self._place_char([self._current_loc[0], self._current_loc[1]], 'x', '+')

        for x in range(self._current_loc[0] + 1, self._current_loc[0] + spots + 1):
            row = self._grid[x]
            char = str(self._current_wire)
            current_char = row[self._current_loc[1]]
            if not Grid._is_safe(current_char, char):
                char = 'x'
            self._place_char([x, self._current_loc[1]], char, 'V')
        self._current_loc[0] = self._current_loc[0] + spots
        self._current_dir = 'U'

    def _go_down(self, spots):
        if self._current_dir == 'L' or self._current_dir == 'R':
            if Grid._is_safe(self._grid[self._current_loc[0]][self._current_loc[1]], str(self._current_wire)):
                self._place_char([self._current_loc[0], self._current_loc[1]], str(
                self._current_wire), '+')
            else:
                self._place_char([self._current_loc[0], self._current_loc[1]], 'x', '+')

        for x in reversed(range(self._current_loc[0] - spots, self._current_loc[0])):
            row = self._grid[x]
            char = str(self._current_wire)
            current_char = row[self._current_loc[1]]
            if not Grid._is_safe(current_char, char):
                char = 'x'
            self._place_char([x, self._current_loc[1]], char, 'V')
        self._current_loc[0] = self._current_loc[0] - spots
        self._current_dir = 'D'

    @staticmethod
    def _is_safe(char, new_char):
        return char == '.' or char == 'o' or str(char) == str(new_char)

    def __repr__(self):
        self._fix_grids()
        repr = ''

        for x in reversed(sorted(self._pretty_grid.keys())):
            for y in sorted(self._pretty_grid[x].keys()):
                char = self._pretty_grid[x][y]
                if char is None:
                    char = '.'
                repr += ' ' + char
            repr += '\n'

        return repr


if __name__ == '__main__':
    main()
