#!/usr/bin/env python3

import sys
import re
from collections import Counter


def _year_to_century(year):  
  c = year // 100
  return c if year % 100 == 0 else c + 1

def _parse_century(data):
  data = data.strip()
  if not data:
    return None
  match = re.match(r'^([0-9]+) ?th century$', data)
  if match:
    return int(match.group(1))
  match = re.match(r'.*([0-9]{4}).*', data)
  if match:
    return _year_to_century(int(match.group(1)))
  return None

def _century_parse(f):
  r = re.compile(r'^Composition Year: +(.+)')
  centuries = Counter()
  for line in f:
    match = r.match(line)
    if match:
      c = _parse_century(match.group(1))
      if c is not None:
        centuries[c] += 1
  return centuries


def century(f):
  res = _century_parse(f)
  for century in sorted(res.keys()):
    print('{}th century: {}'.format(century, res[century]))

def _composer_parse(f):
  r = re.compile(r'Composer: (.*)')
  composers = Counter()
  for line in f:
    match = r.match(line)
    if match:
      c = re.sub(r'\(.*?\)', '', match.group(1))
      composers += {i.strip(): 1 for i in c.split(';')}
  return composers
      

def composer(f):
  res = _composer_parse(f)
  for composer in sorted(res.keys()):
    print('{}: {}'.format(composer, res[composer]))

COMMANDS = {'composer': composer, 'century': century, }

def main():
  if len(sys.argv) != 3:
    sys.stderr.write('Usage: ./stat.py scoreboard command.\n')
    sys.exit(1)
  commandName = sys.argv[2]
  if commandName not in COMMANDS:
    sys.stderr.write('Given command "{}". '.format(commandName)
                     + 'Command has to be one of: '
                     + ', '.join(['"{}"'.format(i) for i in COMMANDS]))
    sys.exit(1)
  command = COMMANDS[commandName]
  command(open(sys.argv[1]))

if __name__ == '__main__':
  main()
