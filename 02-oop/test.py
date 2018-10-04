#!/usr/bin/env python3

import sys
from scorelib import *
import re

def _parse_bool(s):
  if s == 'yes':
    return True
  elif s == 'no':
    return False
  else:
    return None

def _parse_people(raw):
  data = [i.strip() for i in raw.split(';') if i.strip()]
  res = []
  re_year = re.compile(r'\(([0-9]{4})--([0-9]{4})\)')
  for auth in data:
    year = (None, None)
    match = re_year.search(auth)
    if match:
      year = (match.group(1), match.group(2))
    auth = re_year.sub('', auth).strip()
    res.append(Person(auth, year[0], year[1]))
  return res

def _parse_voice(raw):
  data = [i.strip() for i in raw.split(',') if i]
  range = [i for i in data if '-' in i]
  range = range[0] if len(range) > 0 else None
  name = [i for i in data if '-' not in i]
  name = name[0] if len(name) > 0 else None
  return Voice(range, name)
  
  match = re.match(r'^(?:[0-9]+: )(?:([a-zA-Z0-9]+)--?([a-bA-Z0-9]+))?(?:, ([^,]+))?.*', 
                   raw)
  if not match:
    return None
  range = None
  name = None
  if len(match.groups()) in (2, 3):
    range = '{}--{}'.format(match.group(1), match.group(2))
  if len(match.groups()) == 1:
    name = match.group(1)
  if len(match.groups()) == 3:
    name = match.group(3)
  return Voice(range, name)
  
def _merge_voice(old, new):
  old = list(old) if old else list([])
  old.append(new)
  return old

def safeInt(value):
  match = re.search(r'[0-9]+', value)
  if match:
    return int(match.group(0))
  else:
    return 0

def _process_lines(lines):
  commands = (('Print Number: ', 'print', int), 
              ('Composer: ', 'composer', _parse_people), 
              ('Title: ', 'title', str), 
              ('Genre: ', 'genre', str),
              ('Key: ', 'key', str),
              ('Composition Year: ', 'comp_year', safeInt),
              ('Publication Year: ', 'pub_year', safeInt),
              ('Edition: ', 'edition', str),
              ('Editor: ', 'editor', _parse_people),
              ('Voice ', 'voices', _parse_voice, _merge_voice),
              ('Partiture: ', 'partit', _parse_bool),
              ('Incipit: ', 'incipit', str), )
  lines = [i.strip() for i in lines if i.strip()]
  processed = {}
  for line in lines:
    for c in commands:
      if line.startswith(c[0]):
        data = line[len(c[0]):].strip()
        pdata = c[2](data) if data else None
        mergeFn = c[3] if len(c) == 4 else (lambda _, x: x)
        processed[c[1]] = mergeFn(processed.get(c[1]), pdata)
  if processed == {}:
    return None
  return Print(Edition(Composition(processed.get('title'),
                                   processed.get('incipit'),
                                   processed.get('key'),
                                   processed.get('genre'),
                                   processed.get('comp_year'),
                                   processed.get('voices', []),
                                   processed.get('composer', [])),
                       processed.get('editor', []),
                       processed.get('edition')), 
               processed['print'], 
               processed.get('partit'))  

def load(filename):
  prints = []
  with open(filename) as f:
    lines = []
    for line in f:
      line = line.strip()
      if line:
        lines.append(line)
      else:
        val = _process_lines(lines)
        if val is not None:
          prints.append(val)
        lines = []
  prints.sort(key=lambda x: x.print_id)
  return prints

def main(args):
  for i in load(args[0]):
    i.format()

if __name__ == '__main__':
  main(sys.argv[1:])
