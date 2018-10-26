#!/usr/bin/env python3

import sys
import os
import re
import numpy as np

def _linsolve(m, d):
  if len(m) == 0:
    return ('1', [])
  mrank = np.linalg.matrix_rank(m)
  augrank = np.linalg.matrix_rank([row + [dv] for row, dv in zip(m, d)])
  freevars = len(m[0])
  if mrank == augrank:
    if freevars == mrank:
      if freevars < len(m):
        for i in range(len(m)):
          r = _linsolve(m[0:i] + m[i+1:], d[0:i] + d[i+1:])
          if r[0] == '1':
            return r
      return ('1', np.linalg.solve(m, d))
    else:
      return ('inf', freevars - mrank)
  else:
    return ('0',)

def _parse(f):
  left = []
  right = []
  for line in f:
    tokens = [i for i in line.split() if i]
    if tokens[0] not in ('-', '+'):
      tokens = ['+'] + tokens
    if len(tokens) % 2 != 0:
      raise Exception('invalid equation "{}"\n'.format(line))
    tokens = list(zip(tokens[::2], tokens[1::2]))
    row = []
    for token in tokens[:-1]:
      num = re.search('[0-9]+', token[1])
      letter = re.search('[a-zA-Z]', token[1])
      num = num.group(0) if num is not None else '1'
      if token[0] == '+':
        num = int(num)
      elif token[0] == '-':
        num = -int(num)
      else:
        raise ValueError('sign has to be one of: +-')
      letter = letter.group(0)
      row.append((num, letter))
    if tokens[-1][0] != '=':
      raise Exception('= expected to be second to last token')
    right.append(int(tokens[-1][1]))
    left.append(row)
  return (left, right)


def evaluate(f):
  left, right = _parse(f)
  letters = set()
  for row in left:
    for cell in row:
      letters.add(cell[1])
  letters = list(letters)
  let2idx = {l: idx for idx, l in enumerate(letters)}
  mtx = [[0 for _ in letters] for _ in left]
  for idx, row in enumerate(left):
    for cell in row:
      mtx[idx][let2idx[cell[1]]] += cell[0]
  res = _linsolve(mtx, right)
  if res[0] == '0':
    print('no solution')
  elif res[0] == '1':
    print('solution:', ', '.join(sorted(['{} = {}'.format(letters[idx], i) for idx, i in enumerate(res[1])])))
  elif res[0] == 'inf':
    print('solution space dimension: {}'.format(res[1]))
  else:
    raise Exception()


def main(args):
  if len(args) != 1:
    sys.stderr.write('The first parameter has to be present.\n')
    return
  evaluate(sys.stdin if args[0] == '-' else open(args[0]))

if __name__ == '__main__':
  main(sys.argv[1:])
