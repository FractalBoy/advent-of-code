#!/usr/bin/env python

import fileinput
from functools import reduce


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
        password = list(str(password))
        if len(password) != 6:
            return False

        digit_count = {digit: password.count(digit) for digit in set(password)}
        if reduce(lambda a, b: a + 1 if b > 1 else a, digit_count.values(), 0) == 0:
            return False

        pairs = [(password[i], password[i+1])
                 for i in range(len(password) - 1) if password[i] > password[i+1]]
        if len(pairs) != 0:
            return False

        digits = reduce(chunk_consecutive, password, [[]])
        if reduce(lambda a, b: a + 1 if len(b) == 2 else a, digits, 0) == 0:
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
