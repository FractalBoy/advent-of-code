#!/usr/bin/env python

from intcode import IntCodeComputer
from collections import defaultdict
from random import choice
import asyncio
import operator


def main():
    droid = Droid()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(droid.run())
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()
        print(droid.num_commands)


class Droid():
    def __init__(self):
        with open('droidcode.txt', 'r') as f:
            memory = f.readline()
        memory = memory.strip().split(',')
        self.computer = IntCodeComputer(
            memory, self.get_input, self.get_output)
        self.current_location = (0, 0)
        self.map = defaultdict(lambda: ' ')
        self.map[self.current_location] = '.'
        self.moves = []
        self.num_commands = 0
        self.halt = False

    async def get_input(self):
        unknowns = [move for move in self.enumerate_possible_moves()
                    if self.map[tuple(map(operator.add, self.current_location, move))] == ' ']

        if len(unknowns):
            next_move = unknowns[0]
            next_location = tuple(map(operator.add,
                                      self.current_location, next_move))
            self.current_location = next_location
            self.moves.append(next_move)
            self.num_commands += 1
            return self.enumerate_possible_moves()[next_move]

        next_move = tuple(map(operator.mul, (-1, -1), self.moves.pop()))
        self.current_location = tuple(map(operator.add, self.current_location, next_move))
        self.num_commands -= 1
        return self.enumerate_possible_moves()[next_move]

    def get_output(self, value):
        if value == '0':
            self.map[self.current_location] = '#'
            prev_move = tuple(map(operator.mul, (-1, -1), self.moves.pop()))
            self.current_location = tuple(
                map(operator.add, self.current_location, prev_move))
            self.num_commands -= 1
        elif value == '1':
            self.map[self.current_location] = '.'
        elif value == '2':
            self.halt = True
            raise asyncio.CancelledError("found!")

    def __repr__(self):
        xs = [x for x, _ in self.map]
        ys = [y for _, y in self.map]
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        repr = ''

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                repr += self.map[x, y]
            repr += '\n'

        return repr

    async def run(self):
        await self.computer.run()

    def enumerate_possible_moves(self):
        return {
            (0, -1): 1,
            (0, 1): 2,
            (1, 0): 3,
            (-1, 0): 4
        }


if __name__ == '__main__':
    main()
