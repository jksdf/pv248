#!/usr/bin/env python3
import json
import sqlite3
import sys
from pprint import pprint


def find(print_id):
  connection = sqlite3.connect('scorelib.dat')
  lst = []
  for person in connection.execute(r'SELECT name, born, died FROM person WHERE id IN (SELECT composer FROM score_author WHERE score IN (SELECT score FROM main.edition WHERE id IN (SELECT print.edition FROM print WHERE print.id = ?)))', (print_id,)):
    name, born, died = person
    lst.append({'name': name, 'born': born, 'died': died})
  json.dump(lst, sys.stdout, indent=4)


def main(args):
  if len(args) != 1:
    sys.stderr.write('There has to be exactly one argument - a print number.\n')
  try:
    find(int(args[0]))
  except ValueError:
    sys.stderr.write('The first argument has to be a number.\n')


main(sys.argv[1:])