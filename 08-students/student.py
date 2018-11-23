#!/usr/bin/env python3
import csv
import json
import math
import re
import sys
import datetime
from pprint import pprint

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

def regression(data, dateFormat, startDateStr='2018-9-17'):
    dates, points = [], []
    for key, value in sorted(data.items()):
        dates.append(datetime.datetime.strptime(key, dateFormat).date().toordinal())
        points.append(value)
    _prefixSum(points)
    startdate = datetime.datetime.strptime(startDateStr, '%Y-%m-%d').date().toordinal()
    dates = np.array(dates) - startdate
    reg = np.linalg.lstsq([[i] for i in dates], points, rcond=-1)[0][0]
    if False:
        try:
            import matplotlib.pyplot as plt
            y = [0] + dates
            plt.plot(y, points)
            plt.plot(y, y * reg)
            plt.show()
        except:
            pass
    reg /= 100
    return startdate, reg

def analyze(data, dateFormat='%Y-%m-%d'):
    byDate = defaultdict(lambda : 0)
    byEx = defaultdict(lambda : 0)
    for (date, ex), points in data.items():
        byDate[date] += points
        byEx[ex] += points

    startdate, reg = regression(byDate, dateFormat)

    values = list(byEx.values())
    return {'mean': np.mean(values) / 100,
            'median': np.median(values) / 100,
            'passed': np.count_nonzero(values),
            'total': np.sum(values) / 100,
            'regression slope': reg,
            'date 16': _extrapolateDate(reg, 16, startdate, dateFormat),
            'date 20': _extrapolateDate(reg, 20, startdate, dateFormat)}


def _extrapolateDate(reg, points, startdate, dateFormat):
    if reg == 0:
        return 'inf'
    return datetime.date.fromordinal(int(points / reg + startdate)).strftime(dateFormat)

def read(file):
    reader = csv.reader(file)
    deadlines = list(map(parse_exercise, list(next(reader, None)[1:])))
    rawdata = {}
    for row in reader:
        rawdata[row[0]] = [int(Decimal(v) * 100) for v in row[1:]]
    averagestudent(len(deadlines), rawdata)
    return deadlines, rawdata

def student(file, sid):
    deadlines, rawdata = read(file)
    if sid not in rawdata.keys():
        return {}
    data = defaultdict(lambda: 0)
    for deadline, points in zip(deadlines, rawdata[sid]):
        data[deadline] = max(data[deadline], points)
    return analyze(data)


def averagestudent(deadlinecount, rawdata, avgname='average'):
    avg = []
    for deadlineidx in range(deadlinecount):
        data = []
        for row in rawdata.values():
            data.append(row[deadlineidx])
        avg.append(np.average(data))
    rawdata[avgname] = avg


def main(args):
    json.dump(student(open(args[0]), args[1]), sys.stdout, indent=2)

if __name__ == '__main__':
    main(sys.argv[1:])
