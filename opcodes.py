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

    dispatch_table = {
        1: AddOperation(opcodes),
        2: MultiplyOperation(opcodes),
        3: SaveOperation(opcodes),
        4: LoadOperation(opcodes),
        99: ExitOperation(opcodes)
    }

    pos = 0

    #change_input(opcodes, 62, 55)

    while True:
        opcode = int(opcodes[pos][-2:].lstrip('0'))

        if opcode in dispatch_table:
            operation = dispatch_table[opcode]
        else:
            raise Exception(f'invalid opcode: {opcode}')

        parameter_modes = list(reversed(
            opcodes[pos][-5:-2].rjust(operation.num_parameters, '0')))

        if operation.should_exit:
            break

        operation.perform_operation(
            parameter_modes, pos, partial(input, 'Enter input: '), print)
        pos += operation.increment_by()


def change_input(opcodes, pos1, pos2):
    opcodes[1] = pos1
    opcodes[2] = pos2


class Operation:
    def __init__(self, opcodes):
        self._opcodes = opcodes
        self.num_parameters = 0
        self.should_exit = False

    def increment_by(self):
        return self.num_parameters + 1

    def operation(self, parameters, inp, outp):
        pass

    def get_parameters(self, pos, parameter_modes):
        dispatch_table = {
            '0': self.position_mode,
            '1': self.immediate_mode
        }
        return tuple(
            partial(dispatch_table[parameter_modes[i]],
                    int(self._opcodes[pos + 1 + i]))
            for i in range(0, self.num_parameters)
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

    def perform_operation(self, parameter_modes, pos, inp, outp):
        self.operation(self.get_parameters(pos, parameter_modes), inp, outp)


class AddOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.num_parameters = 3

    def operation(self, parameters, inp, outp):
        operand1, operand2, target = parameters
        target(int(operand1()) + int(operand2()))


class MultiplyOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.num_parameters = 3

    def operation(self, parameters, inp, outp):
        operand1, operand2, target = parameters
        target(int(operand1()) * int(operand2()))


class SaveOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.num_parameters = 1

    def operation(self, parameters, inp, outp):
        target, = parameters
        target(inp())


class LoadOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.num_parameters = 1

    def operation(self, parameters, inp, outp):
        target, = parameters
        outp(target())


class ExitOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.should_exit = True
        self.num_parameters = 0


if __name__ == '__main__':
    main()
