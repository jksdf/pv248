#!/usr/bin/env python3

import re


def _str(val):
  return str(val) if val is not None else ''


class Print:
  def __init__(self, edition, print_id, partitude):
    self.edition = edition
    self.print_id = print_id
    self.partitude = partitude

  def composition(self):
    return self.edition.composition

  def format(self):
    print(self.__str__())

  def __str__(self):
    lines = []
    for idx, v in enumerate(self.composition().voices):
      lines.append('Voice {}: {}\n'.format(idx + 1, str(v)))
    voices = ''.join(lines)
    return """Print Number: {}
Composer: {}
Title: {}
Genre: {}
Key: {}
Composition Year: {}
Edition: {}
Editor: {}
{}Partiture: {}
Incipit: {}
""".format(self.print_id,
           '; '.join(map(str, self.composition().authors)),
           _str(self.composition().name),
           _str(self.composition().genre),
           _str(self.composition().key),
           _str(self.composition().year),
           _str(self.edition.name),
           '; '.join(map(str, self.edition.authors)),
           voices,
           'yes' if self.partitude else 'no',
           _str(self.composition().incipit))


class Edition:
  def __init__(self, composition, authors, name):
    self.composition = composition
    self.authors = authors
    self.name = name

  def format(self):
    return "{}Composer: {}\nTitle: {}\n".format(self.composition.format(),
                                                self.name,
                                                self.name)


class Composition:
  def __init__(self, name, incipit, key, genre, year, voices, authors):
    self.name = name
    self.incipit = incipit
    self.key = key
    self.genre = genre
    self.year = year
    self.voices = voices
    self.authors = authors

  def format(self):
    return "Genre: {}"


class Voice:
  def __init__(self, name, range):
    self.name = name
    self.range = range

  def __str__(self):
    return ', '.join([i for i in [self.range, self.name] if i])


class Person:
  def __init__(self, name, born, died):
    self.name = name
    self.born = born
    self.died = died

  def __str__(self):
    if self.born is not None or self.died is not None:
      return '{} ({}--{})'.format(self.name, _str(self.born) , _str(self.died))
    return self.name


def load(filename):
  prints = []
  with open(filename, encoding='utf-8') as f:
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
    val = _process_lines(lines)
    if val is not None:
      prints.append(val)
  prints.sort(key=lambda x: x.print_id)
  return prints


def _parse_bool(s):
  if s == 'yes':
    return True
  elif s == 'no':
    return False
  else:
    return False


def _parse_people(raw):
  data = [i.strip() for i in raw.split(';') if i.strip()]
  res = []
  re_year = re.compile(r'\(([0-9]{4})?--?([0-9]{4})?\)')
  re_born = re.compile(r'\(\*([0-9]{4})\)')
  re_died = re.compile(r'\(\+([0-9]{4})\)')
  for auth in data:
    year = [None, None]
    match = re_year.search(auth)
    if match:
      year = [int(i) if i else i for i in (match.group(1), match.group(2))]
    match = re_born.search(auth)
    if match:
      year[0] = int(match.group(1))
    match = re_died.search(auth)
    if match:
      year[1] = int(match.group(1))
    auth = re_year.sub('', auth)
    auth = re_born.sub('', auth)
    auth = re_died.sub('', auth)
    auth = auth.strip()
    res.append(Person(auth, year[0], year[1]))
  return res


def _parse_voice(raw):
  raw = re.sub(r'^ *[0-9]*:', '', raw)
  delimiter = ';' if ';' in raw else ','
  data = [i.strip() for i in raw.split(delimiter, 1) if i.strip()]
  if len(data) == 0:
    return Voice(None, None)
  if '--' in data[0]:
    range = data[0]
    name = data[1] if len(data) > 1 else None
  elif re.match(r'[0-9a-zA-Z]+-[0-9a-zA-Z]+', data[0]):
    range = data[0].replace('-', '--')
    name = data[1] if len(data) > 1 else None
  else:
    range = None
    name = raw.strip()
  return Voice(name, range)


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
              ('Incipit: ', 'incipit', str),)
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
