#!/usr/bin/env python3

import sys
import re
from collections import Counter


def year_to_century(year):
    c = year // 100
    return c if year % 100 == 0 else c + 1


def parse_century(data):
    data = data.strip()
    if not data:
        return None
    match = re.match(r'^([0-9]+) ?(th|st|nd) century$', data)
    if match:
        return int(match.group(1))
    match = re.match(r'.*([0-9]{4}).*', data)
    if match:
        return year_to_century(int(match.group(1)))
    return None


def century_parse(f):
    r = re.compile(r'^Composition Year: +(.+)')
    centuries = Counter()
    for line in f:
        match = r.match(line)
        if match:
            c = parse_century(match.group(1))
            if c:
                centuries[c] += 1
    return centuries


def num_suffix(n):
    if (n // 10) % 10 == 1:
        return 'th'
    if n % 10 == 1:
        return 'st'
    elif n % 10 == 2:
        return 'nd'
    else:
        return 'th'


def century(f):
    res = century_parse(f)
    for century in sorted(res.keys()):
        print('{}{} century: {}'.format(century,
                                        num_suffix(century),
                                        res[century]))


def composer_parse(f):
    r = re.compile(r'Composer: (.*)')
    composers = Counter()
    for line in f:
        match = r.match(line)
        if match:
            c = re.sub(r'\(.*?\)', '', match.group(1))
            composers += {i.strip(): 1 for i in c.split(';') if i.strip()}
    return composers


def composer(f):
    res = composer_parse(f)
    for composer in sorted(res.keys()):
        print('{}: {}'.format(composer, res[composer]))


def main():
    commands = {'composer': composer, 'century': century, }
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: ./stat.py scoreboard command.\n')
        sys.exit(1)
    commandName = sys.argv[2]
    if commandName not in commands:
        sys.stderr.write('Given command "{}". '.format(commandName)
                         + 'Command has to be one of: '
                         + ', '.join(['"{}"'.format(i) for i in commands]))
        sys.exit(1)
    command = commands[commandName]
    command(open(sys.argv[1]))


if __name__ == '__main__':
    main()
