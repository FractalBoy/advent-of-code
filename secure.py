#!/usr/bin/env python

import fileinput
import functools
import itertools


def main():
    for password_range in fileinput.input():
        password = Password(password_range)
        print(len(password.passwords))


class Password:
    def __init__(self, password_range):
        start, end = password_range.split('-')
        self._range = range(int(start), int(end) + 1)
        self.passwords = self.find_passwords()

    def find_passwords(self):
        return [password for password in self._range if self.valid_password(password)]

    def valid_password(self, password):
        password = str(password)
        if len(password) != 6:
            return False

        digit_count = {digit: password.count(digit) for digit in set(password)}
        if len(list(filter(lambda x: x > 1, digit_count.values()))) == 0:
            return False

        pairs = [tuple(list(password)[i: i + 2])
                 for i in range(len(password) - 1)]
        if len(list(filter(lambda x: x[0] > x[1], pairs))) != 0:
            return False

        digits = functools.reduce(chunk_consecutive, password, [[]])
        if len(list(filter(lambda x: len(x) == 2, digits))) == 0:
            return False

        return True


def chunk_consecutive(a, b):
    if len(a[-1]) == 0 or a[-1][-1] == b:
        a[-1].append(b)
    else:
        a.append([b])
    return a


if __name__ == '__main__':
    main()
