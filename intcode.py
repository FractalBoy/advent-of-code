#!/usr/bin/env python

from functools import partial
from itertools import chain
import asyncio
import fileinput
import os

DEBUG = 'DEBUG' in os.environ and os.environ['DEBUG']


def main():
    opcodes = fileinput.input().readline().strip().split(',')

    loop = asyncio.get_event_loop()
    computer = IntCodeComputer(opcodes, get_input(), print)
    loop.run_until_complete(computer.run())
    loop.close()


def get_input():
    async def closure():
        return input('Enter input: ')
    return closure


class IntCodeComputer:
    def __init__(self, memory, inp, outp):
        self._memory = memory.copy()
        self._input = inp
        self._output = outp
        self._pos = 0
        self._relative_base = 0

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
            9: AdjustRelativeBaseOperation,
            99: ExitOperation
        }

        self._pos = 0

        while True:
            pos = self._pos
            opcode = int(self._memory[pos][-2:].lstrip('0'))

            if opcode in dispatch_table:
                operation = dispatch_table[opcode]
            else:
                raise Exception(f'invalid opcode: {opcode}')

            num_parameters = operation.num_parameters()
            parameters = tuple(self._memory[pos + 1:pos + num_parameters + 1])
            modes = self._memory[pos][:-2].rjust(num_parameters, '0')
            modes = tuple(reversed(modes))
            parameters = zip(parameters, modes)
            parameters = self.get_parameters(parameters)
            operation = operation(parameters,
                                  self._input,
                                  self._output,
                                  self.set_instruction_pointer,
                                  self.adjust_relative_base)

            if DEBUG:
                print(f'performing operation: {operation.__class__.__name__}')

            if operation.should_exit:
                break

            await operation.perform_operation()

            if not operation.modified_instruction_pointer:
                if DEBUG:
                    print(
                        f'incrementing instruction pointer by {operation.increment_by()}')
                self._pos += operation.increment_by()

    def get_parameters(self, parameters):
        dispatch_table = {
            '0': self.position_mode,
            '1': self.immediate_mode,
            '2': self.relative_mode
        }

        return tuple(
            partial(dispatch_table[parameter_mode], int(parameter))
            for parameter, parameter_mode in parameters
        )

    def position_mode(self, parameter, value=None):
        if value is None:
            return self.get_memory_at_position(parameter)
        else:
            self.set_memory_at_position(parameter, value)

    def immediate_mode(self, parameter, value=None):
        if value is not None:
            raise Exception('cannot set value in immediate mode')
        return parameter

    def relative_mode(self, parameter, value=None):
        if value is None:
            return self.get_memory_at_position(self._relative_base + parameter)
        else:
            self.set_memory_at_position(self._relative_base + parameter, value)

    def set_memory_at_position(self, pos, value):
        if pos < 0:
            raise Exception('negative address is illegal')
        while pos > len(self._memory) - 1:
            self._memory.append('0')
        if DEBUG:
            print(f'placing {value} into position {pos}')
        self._memory[pos] = str(value)

    def get_memory_at_position(self, pos):
        if pos < 0:
            raise Exception('negative address is illegal')
        while pos > len(self._memory) - 1:
            self._memory.append('0')
        return self._memory[pos]

    def set_instruction_pointer(self, pos):
        if DEBUG:
            print(f'setting instruction pointer to {pos}')
        self._pos = int(pos)

    def adjust_relative_base(self, value):
        if DEBUG:
            print(f'adjusting relative base by {value}')
        self._relative_base += int(value)


class Operation:
    def __init__(self, parameters, inp, outp, set_instruction_pointer, adjust_relative_base):
        self.parameters = parameters
        self.should_exit = False
        self.modified_instruction_pointer = False

        self._input = inp
        self._output = outp
        self._set_instruction_pointer = set_instruction_pointer
        self._adjust_relative_base = adjust_relative_base

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


class AdjustRelativeBaseOperation(Operation):
    @classmethod
    def num_parameters(cls):
        return 1

    async def perform_operation(self):
        value, = self.parameters
        self._adjust_relative_base(value())


if __name__ == '__main__':
    main()
