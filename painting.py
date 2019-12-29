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

        # Calculate the new direction
        if self.current_direction == 'N':
            if direction == 0:
                self.current_direction = 'W'
            elif direction == 1:
                self.current_direction = 'E'
        elif self.current_direction == 'E':
            if direction == 0:
                self.current_direction = 'N'
            elif direction == 1:
                self.current_direction = 'S'
        elif self.current_direction == 'S':
            if direction == 0:
                self.current_direction = 'E'
            elif direction == 1:
                self.current_direction = 'W'
        elif self.current_direction == 'W':
            if direction == 0:
                self.current_direction = 'S'
            elif direction == 1:
                self.current_direction = 'N'

        # Move to the next space
        if self.current_direction == 'N':
            self.current_coordinate[1] -= 1
        elif self.current_direction == 'E':
            self.current_coordinate[0] += 1
        elif self.current_direction == 'S':
            self.current_coordinate[1] += 1
        elif self.current_direction == 'W':
            self.current_coordinate[0] -= 1

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
