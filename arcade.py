#!/usr/bin/env python

from curses import wrapper
from intcode import IntCodeComputer
import asyncio
import fileinput


def main(stdscr):
    loop = asyncio.get_event_loop()
    arcade = ArcadeCabinet(
        fileinput.input().readline().strip().split(','), stdscr)
    loop.run_until_complete(arcade.run())
    loop.close()
    stdscr.getkey()


class ArcadeCabinet():
    def __init__(self, memory, stdscr):
        self.stdscr = stdscr
        self.computer = IntCodeComputer(
            memory, self.get_input, self.get_output)
        self.output = []

    async def get_input(self):
        pass

    def get_output(self, value):
        self.output.append(value)

        if len(self.output) != 3:
            return

        x = int(self.output.pop(0))
        y = int(self.output.pop(0))
        tile_id = int(self.output.pop(0))

        if tile_id == 0:
            self.stdscr.delch(y, x)
        elif tile_id == 1:
            self.stdscr.addch(y, x, '|')
        elif tile_id == 2:
            self.stdscr.addch(y, x, u'\u2588')
        elif tile_id == 3:
            self.stdscr.addch(y, x, '_')
        elif tile_id == 4:
            self.stdscr.addch(y, x, 'o')
        else:
            raise Exception(f'invalid tile_id: {tile_id}')

    async def run(self):
        await self.computer.run()


if __name__ == '__main__':
    wrapper(main)
