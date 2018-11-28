#!/usr/bin/env python3
import os
print('')
print('BEGIN ENV:')
for key, val in os.environ.items():
    print('\"{}\": \"{}\"'.format(key, val))
print('END ENV.')