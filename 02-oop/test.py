#!/usr/bin/env python3

import sys
from scorelib import load

def main(args):
  for i in load(args[0]):
    i.format()

if __name__ == '__main__':
  main(sys.argv[1:])
