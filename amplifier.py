#!/usr/bin/env python

from functools import partial
from intcode import IntCodeComputer
from itertools import permutations
import fileinput
import os

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG']

output_value = None


def main():
    for line in fileinput.input():
        opcodes = line.strip().split(',')
        break

    output_dict = {}

    for phase_settings in permutations(range(5)):
        amp = AmplificationCircuit(opcodes, phase_settings, partial(
            output, output_dict, phase_settings))
        amp.run()

    output_dict = {k: v for k, v in reversed(sorted(output_dict.items(), key=lambda item: item[1]))}
    print(list(output_dict.items())[0])


def output(output_dict, permutation, value):
    output_dict[permutation] = int(value)


class AmplificationCircuit:
    def __init__(self, opcodes, phase_settings, output):
        self.pipe = None
        self.input_number = 0
        self.phase_settings = phase_settings
        self.phase_index = 0
        self.amplifiers = [
            IntCodeComputer(opcodes, self.initial_input, self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, self.send_to_pipe),
            IntCodeComputer(opcodes, self.recv_from_pipe, output)
        ]

    def initial_input(self):
        if self.input_number == 0:
            self.input_number += 1
            value = self.phase_settings[self.phase_index]
            self.phase_index += 1
            return value
        else:
            return 0

    def recv_from_pipe(self):
        # Receive phase setting first, then regular input
        if self.input_number == 0:
            self.input_number += 1
            value = self.phase_settings[self.phase_index]
            self.phase_index += 1
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
