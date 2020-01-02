#!/usr/bin/env python

from collections import defaultdict
from intcode import IntCodeComputer
import asyncio
import curses
import fileinput


def main(stdscr):
    loop = asyncio.get_event_loop()
    arcade = ArcadeCabinet(
        fileinput.input().readline().strip().split(','), stdscr)
    loop.run_until_complete(arcade.run())
    loop.close()
    stdscr.getkey()


class ArcadeCabinet():
    def __init__(self, memory, screen):
        self.screen = screen
        memory[0] = str(2)
        self.computer = IntCodeComputer(
            memory, self.get_input, self.get_output)
        self.virtual_screen = defaultdict(lambda: 0)
        self.output = []
        self.ball_x = 0
        self.paddle_x = 0

    async def get_input(self):
        if self.paddle_x > self.ball_x:
            return -1
        elif self.paddle_x < self.ball_x:
            return 1

        return 0

    def get_output(self, value):
        self.output.append(value)

        if len(self.output) != 3:
            return

        x = int(self.output.pop(0))
        y = int(self.output.pop(0))
        tile_id = int(self.output.pop(0))

        if x == -1 and y == 0:
            self.screen.addstr(0, 0, str(tile_id))
            return

        if tile_id == 0:
            self.screen.addch(y, x, ' ')
        elif tile_id == 1:
            self.screen.addch(y, x, u'\u2588')
        elif tile_id == 2:
            self.screen.addch(y, x, u'\u2585')
        elif tile_id == 3:
            self.screen.addch(y, x, '\u2581')
            self.paddle_x = x
        elif tile_id == 4:
            self.screen.addch(y, x, '\u2b24')
            self.ball_x = x
        else:
            raise Exception(f'invalid tile_id: {tile_id}')

        self.screen.refresh()
        self.virtual_screen[y, x] = tile_id

    async def run(self):
        await self.computer.run()


if __name__ == '__main__':
    curses.wrapper(main)
