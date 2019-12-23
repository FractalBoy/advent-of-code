#!/usr/bin/env python

from functools import partial
from intcode import IntCodeComputer
from itertools import permutations
import asyncio
import fileinput
import os

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG']

output_value = None


def main():
    for line in fileinput.input():
        opcodes = line.strip().split(',')
        break
    
    results = []

    for phase_settings in permutations(range(5, 10)):
        loop = asyncio.get_event_loop()
        amp = AmplificationCircuit(opcodes, phase_settings)
        value = loop.run_until_complete(amp.run())
        results.append(value)
    
    loop.close()
    print(max(results))


class AmplificationCircuit:
    def __init__(self, opcodes, phase_settings):
        self.pipes = {0: None, 1: None, 2: None, 3: None, 4: None}
        self.input_numbers = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        self.phase_settings = phase_settings
        self.amplifiers = [
            IntCodeComputer(opcodes, self.recv_from_pipe(0),
                            self.send_to_pipe(1)),
            IntCodeComputer(opcodes, self.recv_from_pipe(1),
                            self.send_to_pipe(2)),
            IntCodeComputer(opcodes, self.recv_from_pipe(2),
                            self.send_to_pipe(3)),
            IntCodeComputer(opcodes, self.recv_from_pipe(3),
                            self.send_to_pipe(4)),
            IntCodeComputer(opcodes, self.recv_from_pipe(4),
                            self.send_to_pipe(0))
        ]

    def recv_from_pipe(self, pipe_index):
        async def closure():
            # Receive phase setting first
            if self.input_numbers[pipe_index] == 0:
                self.input_numbers[pipe_index] += 1
                value = self.phase_settings[pipe_index]
                if DEBUG:
                    print(f'received {value} from pipe {pipe_index}')
                return value
            # If this is the first pipe, we need to receive 0 after the phase setting
            elif pipe_index == 0 and self.input_numbers[pipe_index] == 1:
                self.input_numbers[pipe_index] += 1
                if DEBUG:
                    print(f'received 0 from pipe {pipe_index}')
                return 0
            # Otherwise, receive input from pipe
            else:
                if DEBUG:
                    print(f'waiting for data on pipe {pipe_index}...')
                while self.pipes[pipe_index] is None:
                    await asyncio.sleep(0)
                value = self.pipes[pipe_index]
                if DEBUG:
                    print(f'received {value} from pipe {pipe_index}')
                self.pipes[pipe_index] = None
                return value
        return closure

    def send_to_pipe(self, pipe_index):
        def closure(value):
            if DEBUG:
                print(f'placing {value} on pipe {pipe_index}')
            self.pipes[pipe_index] = value
        return closure

    async def run(self):
        await asyncio.wait(
            [amplifier.run() for amplifier in self.amplifiers],
            return_when=asyncio.ALL_COMPLETED
        )
        return self.pipes[0]


if __name__ == '__main__':
    main()
