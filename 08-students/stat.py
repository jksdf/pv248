#!/usr/bin/env python3
import json
import re
import sys
from enum import Enum
import csv
from decimal import Decimal
from pprint import pprint

import numpy as np
from collections import defaultdict

class Mode(Enum):
    DATES = 'dates'
    DEADLINES = 'deadlines'
    EXERCISES = 'exercises'

    @classmethod
    def getMode(cls, value):
        for i in cls:
            if i.value == value:
                return i
        return None

    def getKey(self, date, num):
        if self == Mode.DATES:
            return date
        elif self == Mode.DEADLINES:
            return '{}/{}'.format(date, num)
        elif self == Mode.EXERCISES:
            return num
        else:
            raise AssertionError()

def parse_exercise(s):
    s = s.strip()
    match = re.match(r'(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<ex>[0-9]{2})', s)
    return match.group('date'), match.group('ex')


def analyze(values):
    return {'mean': np.mean(values) / 100,
            'median': np.median(values) / 100,
            'first': np.quantile(values, 0.25) / 100,
            'last': np.quantile(values, 0.75) / 100,
            'passed': np.count_nonzero(values)}


def stat(file, mode):
    reader = csv.reader(file)
    deadlines = list(map(parse_exercise, list(next(reader, None)[1:])))
    data = [[] for _ in deadlines]
    for row in reader:
        for idx, value in enumerate(row[1:]):
            data[idx].append(int(Decimal(value)*100))
    result = defaultdict(lambda: [])
    for name, points in zip(deadlines, data):
        result[mode.getKey(*name)] += points
    return {key: analyze(result[key]) for key in result.keys()}

def main(args):
    with open(args[0]) as f:
        json.dump(stat(f, Mode.getMode(args[1])), sys.stdout, indent=2)

if __name__ == '__main__':
    main(sys.argv[1:])