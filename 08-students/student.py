#!/usr/bin/env python3
import csv
import json
import math
import re
import sys
import datetime

import numpy as np
from collections import defaultdict
from decimal import Decimal


def parse_exercise(s):
    s = s.strip()
    match = re.match(r'(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<ex>[0-9]{2})', s)
    return match.group('date'), match.group('ex')


def _prefixSum(l):
    for i in range(1,len(l)):
        l[i] = l[i-1] + l[i]

def analyze(data, dateFormat='%Y-%m-%d'):
    dates, points = [], []
    for key, value in sorted(data.items()):
        dates.append(datetime.datetime.strptime(key, dateFormat).date().toordinal())
        points.append(value)
    _prefixSum(points)
    startdate = np.min(dates)
    dates = np.array(dates) - startdate
    reg = np.linalg.lstsq([[i] for i in dates], points, rcond=-1)[0][0]
    if False:
        try:
            import matplotlib.pyplot as plt
            y = dates
            plt.plot(y, points)
            plt.plot(y, y * reg)
            plt.show()
        except:
            pass
    reg /= 100
    values = list(data.values())
    return {'mean': np.mean(values) / 100,
            'median': np.median(values) / 100,
            'passed': np.count_nonzero(values),
            'total': np.sum(values) / 100,
            'regression slope': reg,
            'date 16': _extrapolateDate(reg, 16, startdate).strftime(dateFormat),
            'date 20': _extrapolateDate(reg, 20, startdate).strftime(dateFormat)}


def _extrapolateDate(reg, points, startdate):
    return datetime.date.fromordinal(math.ceil(points / reg + startdate))

def student(file, id):
    reader = csv.reader(file)
    deadlines = list(map(parse_exercise, list(next(reader, None)[1:])))
    rawdata = None
    for row in reader:
        if int(row[0]) == id:
            rawdata = [int(Decimal(v) * 100) for v in row[1:]]
            break
    if rawdata is None:
        raise ValueError()
    data = defaultdict(lambda: 0)
    for (date, _), points in zip(deadlines, rawdata):
        data[date] = max(data[date], points)
    return analyze(data)

def main(args):
    json.dump(student(open(args[0]), int(args[1])), sys.stdout, indent=2)

if __name__ == '__main__':
    main(sys.argv[1:])