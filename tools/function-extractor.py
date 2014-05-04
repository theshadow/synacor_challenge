import os
import sys


def extract_function(offset, lines):
    func = []
    while True:
        line = lines[offset]

        if line[0] != '#':
            line = line.split('#')[0]
            func.append(line.strip())

        if line.find('ret') != -1:
            break

        offset += 1

    return func


def main():
    fh = open('../func_lines', 'r')
    line_numbers = fh.readlines()
    fh.close()

    fh = open('../challenge.txt', 'r')
    lines = fh.readlines()
    fh.close()

    fh = open('../extracted-functions.src', 'w+')

    for line_number in line_numbers:
        func = extract_function(int(line_number) - 1, lines)  # minus 1 because they're 1 based from the shell
        fh.write(('#' * 10) + "\n" + "\n".join(func) + "\n" + ('#' * 10))
        print func

    fh.close()

if __name__ == '__main__':
    main()
