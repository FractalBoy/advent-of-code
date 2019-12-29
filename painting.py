#!/usr/bin/env python

from collections import defaultdict, deque
from intcode import IntCodeComputer
import asyncio
import fileinput


def main():
    robot = HullPaintingRobot(fileinput.input().readline().strip().split(','))
    loop = asyncio.get_event_loop()
    painted = loop.run_until_complete(robot.run())
    print(len(painted))
    print(robot)
    loop.close()


class HullPaintingRobot():
    def __init__(self, memory):
        self.computer = IntCodeComputer(
            memory, self.get_input, self.get_output)
        self.painting = defaultdict(lambda: 0)
        self.current_coordinate = [0, 0]
        self.painting[tuple(self.current_coordinate)] = 1
        self.current_direction = 'N'
        self.painted_coordinates = set()
        self.output = deque()

    async def get_input(self):
        return self.painting[tuple(self.current_coordinate)]

    def get_output(self, value):
        self.output.append(value)

        if len(self.output) != 2:
            return

        color = int(self.output.popleft())
        direction = int(self.output.popleft())

        # Color the current coordinate
        self.painting[tuple(self.current_coordinate)] = color
        self.painted_coordinates.add(tuple(self.current_coordinate))

        direction_dispatch_table = {
            'N': {
                0: 'W',
                1: 'E'
            },
            'E': {
                0: 'N',
                1: 'S'
            },
            'S': {
                0: 'E',
                1: 'W'
            },
            'W': {
                0: 'S',
                1: 'N'
            }
        }

        # Calculate the new direction
        self.current_direction = direction_dispatch_table[self.current_direction][direction]

        move_dispatch_table = {
            'N': (0, -1),
            'E': (1, 0),
            'S': (0, 1),
            'W': (-1, 0)
        }

        # Move to the next space
        move = move_dispatch_table[self.current_direction]
        self.current_coordinate[0] = self.current_coordinate[0] + move[0]
        self.current_coordinate[1] = self.current_coordinate[1] + move[1]

    def __repr__(self):
        xs = [x for x, _ in self.painting]
        ys = [y for _, y in self.painting]
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        repr = ''

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                repr += '.' if self.painting[x,y] == 0 else '#'
            repr += '\n'

        return repr

    async def run(self):
        await self.computer.run()
        return self.painted_coordinates


if __name__ == '__main__':
    main()
