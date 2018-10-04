#!/usr/bin/env python3

import sys

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
      parts = [j for j in [v.name, v.range] if j]
      lines.append('Voice {}: {}\n'.format(idx + 1,
                                           ', '.join(parts)))
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
           self.composition().name,
           self.composition().genre,
           self.composition().key,
           self.composition().year,
           self.edition.name,
           '; '.join(map(str, self.edition.authors)),
           voices,
           'yes' if self.partitude else 'no',
           self.composition().incipit)


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


class Person:
  def __init__(self, name, born, died):
    self.name = name
    self.born = born
    self.died = died

  def __str__(self):
    if self.born is not None and self.died is not None:
      return '{} ({}--{})'.format(self.name, self.born, self.died)
    return self.name

