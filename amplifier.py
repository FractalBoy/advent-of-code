#!/usr/bin/env python

from functools import partial
from intcode import IntCodeComputer
import fileinput
import os

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG']

def main():
    for line in fileinput.input():
        opcodes = line.strip().split(',')
        break
    amp = AmplificationCircuit(opcodes)
    amp.run()


class AmplificationCircuit:
    def __init__(self, opcodes):
        self.pipe = None
        self.input_number = 0
        self.amplifiers = [
            IntCodeComputer(opcodes, partial(
                input, 'Enter input: '), self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, print)
        ]

    def recv_from_pipe(self):
        if self.input_number == 0:
            self.input_number += 1
            value = input('Enter input: ')
            if DEBUG:
                print(f'outputted {value} from user')
            return value
        else:
            if DEBUG:
                print(f'outputted {self.pipe} from pipe')
            return self.pipe

    def send_to_pipe(self, value):
        if DEBUG:
            print(f'set pipe to {value}')
        self.pipe = value

    def run(self):
        for amplifier in self.amplifiers:
            self.input_number = 0
            amplifier.run()


if __name__ == '__main__':
    main()
