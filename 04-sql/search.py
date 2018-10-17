#!/usr/bin/env python3
import json
import sqlite3
import sys
from scorelib import *
#from .scorelib import *
from collections import defaultdict


def __map2list(mp):
  lst = [None] * max(mp.keys())
  for idx in mp.keys():
    lst[idx-1] = mp[idx]
  return lst

def __translate_keys(translation_schema):
  def f(obj):
    schema = translation_schema.get(type(obj))
    if schema is None:
      return obj.__dict__
    res = {}
    for key in obj.__dict__:
      res[schema.get(key, key)] = obj.__dict__[key]
    return res
  return f


def __to_bool(val):
  if val == 'Y':
    return True
  elif val == 'N':
    return False
  else:
    return None


def search(substr):
  connection = sqlite3.connect('scorelib.dat')
  result = defaultdict(lambda: [])
  for person_id, person_name in connection.execute(r"SELECT id, name FROM person WHERE name LIKE '%' || ? || '%'", (substr, )):
    root_composer = person_name
    for (score_id, score_name, score_genre, score_incipit, score_key, score_year) in connection.execute(r"SELECT score.id, score.name, score.genre, score.incipit, score.key, score.year FROM score JOIN score_author a on score.id = a.score WHERE a.composer = ?", (person_id, )):
      voicesMap = {}
      for voice_name, voice_range, voice_number in connection.execute(r"SELECT name, range, number FROM voice WHERE score = ?", (score_id, )):
        voicesMap[voice_number] = Voice(voice_name, voice_range)
      composers = []
      for c_name, c_born, c_died in connection.execute(r"SELECT person.name, person.born, person.died FROM score_author JOIN person ON score_author.composer = person.id WHERE score_author.score = ?", (score_id,)):
        composers.append(Person(c_name, c_born, c_died))
      composition = Composition(score_name, score_incipit, score_key, score_genre, score_year, __map2list(voicesMap), composers)
      for edition_id, edition_name, edition_year in connection.execute(r"SELECT id, name, year FROM edition WHERE score = ?", (score_id,)):
        editors = []
        for e_name, e_born, e_died in connection.execute(r"SELECT person.name, person.born, person.died FROM edition_author JOIN person ON edition_author.editor = person.id WHERE edition_author.edition = ?", (edition_id,)):
          editors.append(Person(e_name, e_born, e_died))
        edition = Edition(composition, editors, edition_name)
        for print_id, print_part in connection.execute(r"SELECT id, partiture FROM print WHERE edition = ?", (edition_id, )):
          print = Print(edition, print_id, __to_bool(print_part))
          result[root_composer].append(print)
  json.dump(result,
            sys.stdout,
            default=__translate_keys({Print: {"print_id": "Print Number", "partiture": "Partiture", "edition": "Edition"},
                                      Edition: {"authors": "Editors", "name": "Name", "composition": "Composition"},
                                      Composition: {"name": "Name", "incipit": "Incipit", "key": "Key", "genre": "Genre", "year": "Composition Year", "voices": "Voices", "authors": "Composer"},
                                      Voice: {"name": "Name", "range": "Range"},
                                      Person: {"name": "Name", "born": "Born", "died": "Died"}}),
            indent=4,
            ensure_ascii=False)
  return


def main(args):
  text = ' '.join(args).strip()
  if text == '':
    json.dump({}, sys.stdout)
    return
  search(text)


main(sys.argv[1:])