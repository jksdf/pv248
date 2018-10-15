#!/usr/bin/env python3

import sys
import re
import sqlite3
import scorelib
from collections import defaultdict

INIT_SCRIPT = 'scorelib.sql'

def loadPeople(prints: [scorelib.Print]):
  people = defaultdict(lambda : [])
  for p in prints:
    for person in p.edition.authors:
      people[person.name].append(person)
    for person in p.composition().authors:
      people[person.name].append(person)
  peopleset = set()
  for personname in people.keys():
    born, died = None, None
    for p in people[personname]:
      if p.born:
        born = p.born
      if p.died:
        died = p.died
    peopleset.add(scorelib.Person(personname, born, died))
  return peopleset

def storePeople(connection, people, ids):
  cursor = connection.cursor()
  for p in people:
    cursor.execute('INSERT INTO person (name, born, died) VALUES (?, ?, ?)', (p.name, p.born, p.died))
    ids[p] = cursor.lastrowid


def loadCompositions(prints):
  return [p.composition() for p in prints]


def storeCompositions(connection, compositions, ids):
  cursor = connection.cursor()
  mp = defaultdict(lambda : [])
  for c in compositions:
    mp[c.pub_key()].append(c)
  for key in mp.keys():
    c = mp[key][0]
    cursor.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)', (c.name, c.genre, c.key, c.incipit, c.year))
    for c in mp[key]:
      ids[c] = cursor.lastrowid

  for c in compositions:
    for idx, v in enumerate(c.voices):
      cursor.execute('INSERT INTO voice (score, number, range, name) VALUES (?, ?, ?, ?)', (ids[c], idx + 1, v.range, v.name))

def loadEditions(prints):
  return [p.edition for p in prints]


def storeEditions(connection, editions, ids):
  cursor = connection.cursor()
  mp = defaultdict(lambda : [])
  for e in editions:
    score_id = ids[e.composition]
    mp[e.pub_key()].append((e, score_id))
  for key in mp.keys():
    e, score_id = mp[key][0]
    cursor.execute('INSERT INTO edition (name, score) VALUES (?, ?)', (e.name, score_id))
    for e, _ in mp[key]:
      ids[e] = cursor.lastrowid


def storePrints(connection, prints, ids):
  cursor = connection.cursor()
  unique = set()
  for p in prints:
    edition_id = ids[p.edition]
    unique.add((p.print_id, 'Y' if p.partiture else 'N', edition_id))
  for key in unique:
    cursor.execute('INSERT INTO print (id, partiture, edition) VALUES (?, ?, ?)', key)


def loadEditorLinks(prints):
  x = []
  for p in prints:
    for editor in p.edition.authors:
       x.append((p.edition, editor))
  return x


def storeEditorLinks(connection, links, ids):
  cursor = connection.cursor()
  keys = set(((ids[link[0]], ids[link[1]]) for link in links))
  for key in keys:
    cursor.execute('INSERT INTO edition_author (edition, editor) VALUES (?, ?)', key)

def loadComposerLinks(prints):
  x = []
  for p in prints:
    for author in p.composition().authors:
       x.append((p.composition(), author))
  return x

def storeComposerLinks(connection, links, ids):
  cursor = connection.cursor()
  keys = set(((ids[link[0]], ids[link[1]]) for link in links))
  for key in keys:
    cursor.execute('INSERT INTO score_author (score, composer) VALUES (?, ?)', key)


def main(args):
  prints = scorelib.load(args[0])
  ids = {}
  connection = sqlite3.connect(args[1])
  connection.cursor().executescript(open(args[2] if len(args) > 2 else INIT_SCRIPT).read())
  storePeople(connection, loadPeople(prints), ids)
  storeCompositions(connection, loadCompositions(prints), ids)
  storeEditions(connection, loadEditions(prints), ids)
  storePrints(connection, prints, ids)
  storeEditorLinks(connection, loadEditorLinks(prints), ids)
  storeComposerLinks(connection, loadComposerLinks(prints), ids)
  connection.commit()


if __name__ == '__main__':
  main(sys.argv[1:])