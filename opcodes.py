#!/usr/bin/env python

import fileinput
from functools import reduce, partial
import operator


def main():
    opcodes = []

    with open('day5.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            opcodes.extend(line.split(','))

    computer = IntCodeComputer(opcodes, partial(input, 'Enter input: '), print)
    computer.run()


class IntCodeComputer:
    def __init__(self, opcodes, inp, outp):
        self._opcodes = opcodes
        self._input = inp
        self._output = outp

    def run(self):
        dispatch_table = {
            1: AddOperation,
            2: MultiplyOperation,
            3: SaveOperation,
            4: LoadOperation,
            99: ExitOperation
        }

        pos = 0

        while True:
            opcode = int(self._opcodes[pos][-2:].lstrip('0'))

            if opcode in dispatch_table:
                operation = dispatch_table[opcode]
            else:
                raise Exception(f'invalid opcode: {opcode}')

            num_parameters = operation.num_parameters()
            parameters = tuple(self._opcodes[pos + 1:pos + num_parameters + 1])
            parameter_modes = self._opcodes[pos][:-2].rjust(num_parameters, '0')
            parameter_modes = tuple(reversed(parameter_modes))
            parameters = zip(parameters, parameter_modes)
            parameters = self.get_parameters(parameters)
            operation = operation(parameters, self._input, self._output)

            if operation.should_exit:
                break

            operation.perform_operation()
            pos += operation.increment_by()

    def get_parameters(self, parameters):
        dispatch_table = {
            '0': self.position_mode,
            '1': self.immediate_mode
        }

        return tuple(
            partial(dispatch_table[parameter_mode], int(parameter))
            for parameter, parameter_mode in parameters
        )

    def position_mode(self, parameter, value=None):
        if value is None:
            return self._opcodes[parameter]
        else:
            self._opcodes[parameter] = str(value)

    def immediate_mode(self, parameter, value=None):
        if value is not None:
            raise Exception('cannot set value in immediate mode')
        return parameter


class Operation:
    def __init__(self, parameters, inp, outp):
        self.parameters = parameters
        self._input = inp
        self._output = outp
        self.should_exit = False

    @classmethod
    def num_parameters(cls):
        return 0

    @classmethod
    def increment_by(cls):
        return cls.num_parameters() + 1

    def perform_operation(self, parameters, inp, outp):
        pass


class AddOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 3

    def perform_operation(self):
        operand1, operand2, target = self.parameters
        target(int(operand1()) + int(operand2()))


class MultiplyOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 3

    def perform_operation(self):
        operand1, operand2, target = self.parameters
        target(int(operand1()) * int(operand2()))


class SaveOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 1

    def perform_operation(self):
        target, = self.parameters
        target(self._input())


class LoadOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 1

    def perform_operation(self):
        target, = self.parameters
        self._output(target())


class ExitOperation(Operation):
    def __init__(self, parameters, inp, outp):
        super().__init__(parameters, inp, outp)
        self.should_exit = True


if __name__ == '__main__':
    main()
