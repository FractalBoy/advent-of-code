#!/usr/bin/env python

from functools import partial
import fileinput
import os

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG']

def main():
    opcodes = []

    for line in fileinput.input():
        line = line.strip()
        if len(line) == 0:
            break
        opcodes.extend(line.split(','))

    computer = IntCodeComputer(opcodes, partial(input, 'Enter input: '), print)
    computer.run()


class IntCodeComputer:
    def __init__(self, opcodes, inp, outp):
        self._opcodes = opcodes.copy()
        self._input = inp
        self._output = outp
        self._pos = 0

    async def run(self):
        dispatch_table = {
            1: AddOperation,
            2: MultiplyOperation,
            3: SaveOperation,
            4: LoadOperation,
            5: JumpIfTrueOperation,
            6: JumpIfFalseOperation,
            7: LessThanOperation,
            8: EqualsOperation,
            99: ExitOperation
        }

        self._pos = 0

        while True:
            pos = self._pos
            opcode = int(self._opcodes[pos][-2:].lstrip('0'))

            if opcode in dispatch_table:
                operation = dispatch_table[opcode]
            else:
                raise Exception(f'invalid opcode: {opcode}')

            num_parameters = operation.num_parameters()
            parameters = tuple(self._opcodes[pos + 1:pos + num_parameters + 1])
            modes = self._opcodes[pos][:-2].rjust(num_parameters, '0')
            modes = tuple(reversed(modes))
            parameters = zip(parameters, modes)
            parameters = self.get_parameters(parameters)
            operation = operation(parameters,
                                  self._input,
                                  self._output,
                                  self.set_instruction_pointer)

            if DEBUG:
                print(f'performing operation: {operation.__class__.__name__}')

            if operation.should_exit:
                break
            
            await operation.perform_operation()

            if not operation.modified_instruction_pointer:
                self._pos += operation.increment_by()

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
            if DEBUG:
                print(f'placing {value} into position {parameter}')
            self._opcodes[parameter] = str(value)

    def immediate_mode(self, parameter, value=None):
        if value is not None:
            raise Exception('cannot set value in immediate mode')
        return parameter

    def set_instruction_pointer(self, pos):
        if DEBUG:
            print(f'setting instruction pointer to {pos}')
        self._pos = int(pos)


class Operation:
    def __init__(self, parameters, inp, outp, set_instruction_pointer):
        self.parameters = parameters
        self.should_exit = False
        self.modified_instruction_pointer = False

        self._input = inp
        self._output = outp
        self._set_instruction_pointer = set_instruction_pointer

    @classmethod
    def num_parameters(cls):
        return 0

    @classmethod
    def increment_by(cls):
        return cls.num_parameters() + 1

    async def perform_operation(self):
        pass


class AddOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 3

    async def perform_operation(self):
        operand1, operand2, target = self.parameters
        if DEBUG:
            print(f'adding {operand1()} and {operand2()}')
        target(int(operand1()) + int(operand2()))


class MultiplyOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 3

    async def perform_operation(self):
        operand1, operand2, target = self.parameters
        if DEBUG:
            print(f'multiplying {operand1()} and {operand2()}')
        target(int(operand1()) * int(operand2()))


class SaveOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 1

    async def perform_operation(self):
        target, = self.parameters
        if DEBUG:
            print(f'getting input')
        target(await self._input())


class LoadOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 1

    async def perform_operation(self):
        target, = self.parameters
        if DEBUG:
            print(f'outputting {target()}')
        self._output(target())


class ExitOperation(Operation):
    def __init__(self, *params):
        super().__init__(*params)
        self.should_exit = True


class JumpOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 2

    def evaluate(self, value):
        pass

    async def perform_operation(self):
        self.modified_instruction_pointer = False
        value, pos = self.parameters
        if self.evaluate(value()):
            self._set_instruction_pointer(pos())
            self.modified_instruction_pointer = True


class JumpIfTrueOperation(JumpOperation):
    def evaluate(self, value):
        if DEBUG:
            print(f'evaluating {value} != 0')
        return int(value) != 0


class JumpIfFalseOperation(JumpOperation):
    def evaluate(self, value):
        if DEBUG:
            print(f'evaluating {value} == 0')
        return int(value) == 0


class CompareOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 3

    def evaluate(self, value1, value2):
        pass

    async def perform_operation(self):
        value1, value2, pos = self.parameters
        if self.evaluate(value1(), value2()):
            pos(1)
        else:
            pos(0)


class LessThanOperation(CompareOperation):
    def evaluate(self, value1, value2):
        if DEBUG:
            print(f'evaluating {value1} < {value2}')
        return int(value1) < int(value2)


class EqualsOperation(CompareOperation):
    def evaluate(self, value1, value2):
        if DEBUG:
            print(f'evaluating {value1} == {value2}')
        return int(value1) == int(value2)


if __name__ == '__main__':
    main()
