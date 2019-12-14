#!/usr/bin/env python

import fileinput
from functools import reduce
import operator


def main():
    opcodes = []

    for line in fileinput.input():
        line = line.strip()
        opcodes.extend([int(x) for x in line.split(',')])

    dispatch_table = {
        1: AddOperation(opcodes),
        2: MultiplyOperation(opcodes),
        99: ExitOperation(opcodes),
    }

    pos = 0

    change_input(opcodes, 62, 55)

    while True:
        opcode = opcodes[pos]

        if opcode in dispatch_table:
            operation = dispatch_table[opcode]
        else:
            raise Exception("invalid opcode")

        if operation.should_exit:
            break

        operation.perform_operation(pos)
        pos += operation.increment_by()

    print(opcodes[0])


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

    def operation(self, *parameters):
        pass

    def get_parameters(self, pos):
        return self._opcodes[pos + 1: pos + self.num_parameters + 1]

    def perform_operation(self, pos):
        self.operation(self.get_parameters(pos))


class AddOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.num_parameters = 3

    def operation(self, parameters):
        operand1, operand2, target = parameters
        self._opcodes[target] = self._opcodes[operand1] + \
            self._opcodes[operand2]


class MultiplyOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.num_parameters = 3

    def operation(self, parameters):
        operand1, operand2, target = parameters
        self._opcodes[target] = self._opcodes[operand1] * \
            self._opcodes[operand2]


class ExitOperation(Operation):
    def __init__(self, opcodes):
        super().__init__(opcodes)
        self.should_exit = True


if __name__ == '__main__':
    main()
